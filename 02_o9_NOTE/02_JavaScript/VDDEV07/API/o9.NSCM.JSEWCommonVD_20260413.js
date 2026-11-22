define('o9.NSCM.JSEWCommonVD', ['o9/data/query', 'o9/data/cellset', 'o9.NSCM.commonLibVD'], function () {
	const programName = "o9.NSCM.JSEWCommonVD";
    const commonLib = require('o9.NSCM.commonLibVD');
    const vdUtil = new commonLib.VdUtil();

    // Log 를 위해서 선언
    const commonLog = new commonLib.VdCommon(programName + ".Log");
    commonLog.setLogLevel("Debug");

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

/************************************************* combo logic *************************************************/
    // 여러개의 콤보를 한번에 가져올때
    // { "fbFuncName" : "fn_cb_common", "fbParams" : { "codes" : ["jdm", "mfSiteStageForMF", "subsidiaryForMF", "siteMF", "siteDC", "tpmodeGO"] } }
	var fn_cb_common = function(parsedParams){
        const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
        vdCommon.setLogLevel("Debug");

		try {
            vdCommon.printParams(parsedParams);

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
            vdCommon.printParams(parsedParams);

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
            vdCommon.printParams(parsedParams);

		    var dims = ['[Location].[MF Site Stage].filter(~(#.Name =="-"))'];

		    // Casecade 를 위해서 Dimension 추가
		    dims = vdUtil.fn_addIncludeField(dims, parsedParams);

            // where절 세팅
            parsedParams.fbParams.where["[Location].[Location Type]"] = "MF";

            var result = vdCommon.selectList(dims, [], vdUtil.fn_makeWhere(parsedParams), "", parsedParams.fbParams.limit);
            //vdCommon.printCsData(result, 3);
            var comboList = vdCommon.fn_makeCombo(result, {DimName : "Location", DimAttbName : "MF Site Stage", Sort : "DisplayName",
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

    // { "fbFuncName" : "fn_cb_subsidiaryForMF" }
	var fn_cb_subsidiaryForMF = function(parsedParams){
        const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
        vdCommon.setLogLevel("Debug");

		try {
            vdCommon.printParams(parsedParams);

		    var dims = ['[Location].[Subsidiary].filter(~(#.Name =="-"))'];

		    // Casecade 를 위해서 Dimension 추가
		    dims = vdUtil.fn_addIncludeField(dims, parsedParams);

            // where절 세팅
            parsedParams.fbParams.where["[Location].[Location Type]"] = "MF";

            var result = vdCommon.selectList(dims, [], vdUtil.fn_makeWhere(parsedParams), "", parsedParams.fbParams.limit);
            //vdCommon.printCsData(result, 3);
            var comboList = vdCommon.fn_makeCombo(result, {DimName : "Location", DimAttbName : "Subsidiary", Sort : "DisplayName",
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

    // { "fbFuncName" : "fn_cb_siteMF" }
	var fn_cb_siteMF = function(parsedParams){
        const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
        vdCommon.setLogLevel("Debug");

		try {
            vdCommon.printParams(parsedParams);

		    var dims = ['&MFStageSETLocation'];

            // filter를 적용할 Dimension 설정
            if ( parsedParams.fbParams["filterDimension"] == undefined ) {
                parsedParams.fbParams["filterDimension"] = ["[Location]"];
            }

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

    // { "fbFuncName" : "fn_cb_siteDC" }
    var fn_cb_siteDC = function(parsedParams){
        const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
        vdCommon.setLogLevel("Debug");

		try {
            vdCommon.printParams(parsedParams);

		    var dims = ['&NSUIToLocationDC'];

            // filter를 적용할 Dimension 설정
            if ( parsedParams.fbParams["filterDimension"] == undefined ) {
                parsedParams.fbParams["filterDimension"] = ["[To Location]"];
            }

		    // Casecade 를 위해서 Dimension 추가
		    dims = vdUtil.fn_addIncludeField(dims, parsedParams);

            var result = vdCommon.selectList(dims, [], vdUtil.fn_makeWhere(parsedParams), "", parsedParams.fbParams.limit);
            //vdCommon.printCsData(result, 3);
            var comboList = vdCommon.fn_makeCombo(result, {DimName : "To Location", DimAttbName : "To Location", Sort : "DisplayName",
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

    // { "fbFuncName" : "fn_cb_siteMFDC" }
	var fn_cb_siteMFDC = function(parsedParams){
        const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
        vdCommon.setLogLevel("Debug");

		try {
            vdCommon.printParams(parsedParams);

		    var dims = ['&MFStageSETLocation.unionwith(&NSUILocationDC)'];

            // filter를 적용할 Dimension 설정
            if ( parsedParams.fbParams["filterDimension"] == undefined ) {
                parsedParams.fbParams["filterDimension"] = ["[Location]"];
            }

		    // Casecade 를 위해서 Dimension 추가
		    dims = vdUtil.fn_addIncludeField(dims, parsedParams);

            var result = vdCommon.selectList(dims, [], vdUtil.fn_makeWhere(parsedParams), "", parsedParams.fbParams.limit);
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

    // { "fbFuncName" : "fn_cb_tpmodeGO" }
    var fn_cb_tpmodeGO = function(parsedParams){
        const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
        vdCommon.setLogLevel("Debug");

		try {
            vdCommon.printParams(parsedParams);

		    var dims = ['&NSUITransModeView'];

		    // Casecade 를 위해서 Dimension 추가
		    dims = vdUtil.fn_addIncludeField(dims, parsedParams);

            var result = vdCommon.selectList(dims, [], "", "", parsedParams.fbParams.limit);
            //vdCommon.printCsData(result, 3);
            var comboList = vdCommon.fn_makeCombo(result, {DimName : "Trans Mode", DimAttbName : "Trans Mode", Sort : "DisplayName",
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

    // { "fbFuncName" : "fn_cb_MPHorizon" }
    var fn_cb_MPHorizon = function(parsedParams){
        const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
        vdCommon.setLogLevel("Debug");

		try {
            vdCommon.printParams(parsedParams);

		    var dims = ['&MPHorizon'];

		    // Casecade 를 위해서 Dimension 추가
		    dims = vdUtil.fn_addIncludeField(dims, parsedParams);

            var result = vdCommon.selectList(dims, [], "", "", parsedParams.fbParams.limit);
            //vdCommon.printCsData(result, 3);
            var comboList = vdCommon.fn_makeCombo(result, {DimName : "Time", DimAttbName : "Week", Sort : "DisplayName",
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

    // { "fbFuncName" : "fn_cb_SETItem_BODValid_csiteMF_csiteDC", "fbParams" : { "[Location].[Location]" : "P105", "[Sub Location].[Sub Location]" : "S356", "filters" : { "[Version].[Version Name]" : {"SelectedMembers" : ["CWV_MP"], "MemberFilter" : ""} } } }
    var fn_cb_SETItem_BODValid_csiteMF_csiteDC = function(parsedParams){
        const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
        vdCommon.setLogLevel("Debug");

		try {
            vdCommon.printParams(parsedParams);

		    var dims = ['&SETItem'];

		    // Casecade 를 위해서 Dimension 추가
		    dims = vdUtil.fn_addIncludeField(dims, parsedParams);

            var version = vdUtil.fn_getFilterQuery(parsedParams, "[Version].[Version Name]");

            var where = 'where { ' + version + ', Measure.[BOD List_BOD Valid] == "Y", ' +
                            '&nsuilocationplant.[' + parsedParams.fbParams["[Location].[Location]"] + '], ' +
                            '&nsuisublocationdc.[' + parsedParams.fbParams["[Sub Location].[Sub Location]"] + '], ' +
                            'Measure.[BOD Item_Asn]==1 }';
            var result = vdCommon.selectList(dims, ["Measure.[BOD Item_Asn]"], where, "orderby Item.Item.DisplayName", parsedParams.fbParams.limit);
            //vdCommon.printCsData(result, 3);
            var comboList = vdCommon.fn_makeCombo(result, {DimName : "Item", DimAttbName : "Item", Sort : "DisplayName",
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

    // { "fbFuncName" : "fn_cb_inch", "fbParams" : { "includeField" : "Item:Product Group:UI Product Group,Item:Product:UI Product" } }
    // { "fbFuncName" : "fn_cb_inch", "fbParams" : { "includeField" : "Item:Product:UI Product" } }
	var fn_cb_inch = function(parsedParams){
        const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
        vdCommon.setLogLevel("Debug");

		try {
            vdCommon.printParams(parsedParams);

		    var dims = ['&NSUIItemInchView.filter(#.Name >= "0" && #.Name <= "9")'];

		    // Casecade 를 위해서 Dimension 추가
		    dims = vdUtil.fn_addIncludeField(dims, parsedParams);

            var result = vdCommon.selectList(dims, [], vdUtil.fn_makeWhere(parsedParams), "", parsedParams.fbParams.limit);
            //vdCommon.printCsData(result, 3);
            var comboList = vdCommon.fn_makeCombo(result, {DimName : "Item", DimAttbName : "Inch", Sort : "DisplayName",
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

    // { "fbFuncName" : "fn_cb_project" }
    var fn_cb_project = function(parsedParams){
        const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
        vdCommon.setLogLevel("Debug");

		try {
            vdCommon.printParams(parsedParams);

		    var dims = ['[Item].[Project].filter(#.Name != "-").relatedmembers([Project])'];

		    // Casecade 를 위해서 Dimension 추가
		    dims = vdUtil.fn_addIncludeField(dims, parsedParams);

            var result = vdCommon.selectList(dims, [], vdUtil.fn_makeWhere(parsedParams), "", parsedParams.fbParams.limit);
            //vdCommon.printCsData(result, 3);
            var comboList = vdCommon.fn_makeCombo(result, {DimName : "Item", DimAttbName : "Project", Sort : "DisplayName",
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

    // { "fbFuncName" : "fn_cb_setProject" }
    var fn_cb_setProject = function(parsedParams){
        const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
        vdCommon.setLogLevel("Debug");

		try {
            vdCommon.printParams(parsedParams);

            var dims = ['[Item].[Project].filter(#.Name != "-").relatedmembers([Project])'];

		    // Casecade 를 위해서 Dimension 추가
		    dims = vdUtil.fn_addIncludeField(dims, parsedParams);

            // where절 세팅
            parsedParams.fbParams.where["[Item].[Item Stage]"] = "SET";

            var result = vdCommon.selectList(dims, [], vdUtil.fn_makeWhere(parsedParams), "", parsedParams.fbParams.limit);
            //vdCommon.printCsData(result, 3);
            var comboList = vdCommon.fn_makeCombo(result, {DimName : "Item", DimAttbName : "Project", Sort : "DisplayName",
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

    // { "fbFuncName" : "fn_cb_setBasic", "fbParams" : { "includeField" : "Item:Project:Project" } }
    // { "fbFuncName" : "fn_cb_setBasic", "fbParams" : { "where" : { "[Item].[Project]" : "QAQ60G"} } }
    var fn_cb_setBasic = function(parsedParams){
        const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
        vdCommon.setLogLevel("Debug");

		try {
            vdCommon.printParams(parsedParams);

		    var dims = ['[Item].[Basic Name].filter(#.Name != "-").relatedmembers([Basic Name])'];

		    // Casecade 를 위해서 Dimension 추가
		    dims = vdUtil.fn_addIncludeField(dims, parsedParams);

            // where절 세팅
            parsedParams.fbParams.where["[Item].[Item Stage]"] = "SET";

            var result = vdCommon.selectList(dims, [], vdUtil.fn_makeWhere(parsedParams), "", parsedParams.fbParams.limit);
            //vdCommon.printCsData(result, 3);
            var comboList = vdCommon.fn_makeCombo(result, {DimName : "Item", DimAttbName : "Basic Name", Sort : "DisplayName",
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

    // { "fbFuncName" : "fn_cb_setInch", "fbParams" : { "includeField" : "Item:Project:Project,Item:Basic Name:Basic Name" } }
    // { "fbFuncName" : "fn_cb_setInch", "fbParams" : { "where" : { "[Item].[Project]" : "QAQ60G", "[Item].[Basic Name]" : "QTV-F55Q60A/EU" } } }
    var fn_cb_setInch = function(parsedParams){
        const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
        vdCommon.setLogLevel("Debug");

		try {
            vdCommon.printParams(parsedParams);

		    var dims = ['&NSUIItemInchView.filter(#.Name >= "0" && #.Name <= "9")'];

		    // Casecade 를 위해서 Dimension 추가
		    dims = vdUtil.fn_addIncludeField(dims, parsedParams);

            // where절 세팅
            parsedParams.fbParams.where["[Item].[Item Stage]"] = "SET";

            var result = vdCommon.selectList(dims, [], vdUtil.fn_makeWhere(parsedParams), "orderby [Item].[Inch].[Inch Sorting Order]", parsedParams.fbParams.limit);
            //vdCommon.printCsData(result, 3);
            var comboList = vdCommon.fn_makeCombo(result, {DimName : "Item", DimAttbName : "Inch",
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
            vdCommon.printParams(parsedParams);

		    var dims = ['[Item].[Item]'];

		    // Casecade 를 위해서 Dimension 추가
		    dims = vdUtil.fn_addIncludeField(dims, parsedParams);

            // where절 세팅
            parsedParams.fbParams.where["[Item].[Item Stage]"] = "SET";

            var result = vdCommon.selectList(dims, [], vdUtil.fn_makeWhere(parsedParams), "", parsedParams.fbParams.limit);
            //vdCommon.printCsData(result, 3);
            var comboList = vdCommon.fn_makeCombo(result, {DimName : "Item", DimAttbName : "Item", Sort : "DisplayName",
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

    // { "fbFuncName" : "fn_cb_materialWithDesc" }
    // 26.2.11 : 신승호 : 쿼리 변경 요청
    //          Select ( [Item Material].[Item Material].filter(#.[Item Material$InActive]!=True) * [Item Material].[Description] ) on row where {&CWVUI, &NSUIMtrlMSL1View, Measure.[Item Mtrl Site Asn_Cur Status] in {"ACTIVE","PLANNED"}  };

    var fn_cb_materialWithDesc = function(parsedParams){
        const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
        vdCommon.setLogLevel("Debug");

		try {
            vdCommon.printParams(parsedParams);

		    var dims = ["[Item Material].[Item Material].filter(#.[Item Material$InActive] != True)", "[Item Material].[Description]"];

		    // Casecade 를 위해서 Dimension 추가
		    dims = vdUtil.fn_addIncludeField(dims, parsedParams);

            var otherWhere = ["&CWVUI"
                                ,'&NSUIMtrlMSL1View'
                                ,'Measure.[Item Mtrl Site Asn_Cur Status] in {"ACTIVE","PLANNED"}'];
            var result = vdCommon.selectList(dims, [], vdUtil.fn_makeWhere(parsedParams, otherWhere), "", parsedParams.fbParams.limit);
            //vdCommon.printCsData(result, 3);
            var comboList = vdCommon.fn_makeCombo(result, {DimName : "Item Material", DimAttbName : "Item Material", DimDescAttbName : "Description", Sort : "DisplayName",
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

    // { "fbFuncName" : "fn_cb_setYear", "fbParams" : { "includeField" : "Item:Product Group:ProductGroup,Item:Definition:Definition,Item:Project:Project,Item:Marketing Name:MarketingName" } }
    var fn_cb_setYear = function(parsedParams){
        const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
        vdCommon.setLogLevel("Debug");

		try {
            vdCommon.printParams(parsedParams);

		    var dims = ['&NSUIItemYearView.filter(#.Name >= "0" && #.Name <= "9")'];

		    // Casecade 를 위해서 Dimension 추가
		    dims = vdUtil.fn_addIncludeField(dims, parsedParams);

            // where절 세팅
            parsedParams.fbParams.where["[Item].[Item Stage]"] = "SET";

            var result = vdCommon.selectList(dims, [], vdUtil.fn_makeWhere(parsedParams), "orderby [Item].[Year].[Year Sorting Order] desc", parsedParams.fbParams.limit);
            //vdCommon.printCsData(result, 3);
            var comboList = vdCommon.fn_makeCombo(result, {DimName : "Item", DimAttbName : "Year",
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

    // { "fbFuncName" : "fn_cb_setDefinition", "fbParams" : { "includeField" : "Item:Product Group:ProductGroup,Item:Project:Project,Item:Marketing Name:MarketingName" } }
    var fn_cb_setDefinition = function(parsedParams){
        const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
        vdCommon.setLogLevel("Debug");

		try {
            vdCommon.printParams(parsedParams);

		    var dims = ['[Item].[Definition].filter(#.Name != "-").relatedmembers([Definition])'];

		    // Casecade 를 위해서 Dimension 추가
		    dims = vdUtil.fn_addIncludeField(dims, parsedParams);

            // where절 세팅
            parsedParams.fbParams.where["[Item].[Item Stage]"] = "SET";

            var result = vdCommon.selectList(dims, [], vdUtil.fn_makeWhere(parsedParams), "", parsedParams.fbParams.limit);
            //vdCommon.printCsData(result, 3);
            var comboList = vdCommon.fn_makeCombo(result, {DimName : "Item", DimAttbName : "Definition", Sort : "DisplayName",
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

    // { "fbFuncName" : "fn_cb_setMarketingName", "fbParams" : { "includeField" : "Item:Product Group:ProductGroup,Item:Definition:Definition,Item:Project:Project" } }
    var fn_cb_setMarketingName = function(parsedParams){
        const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
        vdCommon.setLogLevel("Debug");

		try {
            vdCommon.printParams(parsedParams);

		    var dims = ['[Item].[Marketing Name].filter(#.Name != "-").relatedmembers([Marketing Name])'];

		    // Casecade 를 위해서 Dimension 추가
		    dims = vdUtil.fn_addIncludeField(dims, parsedParams);

            // where절 세팅
            parsedParams.fbParams.where["[Item].[Item Stage]"] = "SET";

            var result = vdCommon.selectList(dims, [], vdUtil.fn_makeWhere(parsedParams), "", parsedParams.fbParams.limit);
            //vdCommon.printCsData(result, 3);
            var comboList = vdCommon.fn_makeCombo(result, {DimName : "Item", DimAttbName : "Marketing Name", Sort : "DisplayName",
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

    // { "fbFuncName" : "fn_cb_productGroup" }
    var fn_cb_productGroup = function(parsedParams){
        const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
        vdCommon.setLogLevel("Debug");

		try {
            vdCommon.printParams(parsedParams);

		    var dims = ['[Item].[Product Group].filter(#.Name != "-").relatedmembers([Product Group])'];

		    // Casecade 를 위해서 Dimension 추가
		    dims = vdUtil.fn_addIncludeField(dims, parsedParams);

            var result = vdCommon.selectList(dims, [], vdUtil.fn_makeWhere(parsedParams), "", parsedParams.fbParams.limit);
            //vdCommon.printCsData(result, 3);
            var comboList = vdCommon.fn_makeCombo(result, {DimName : "Item", DimAttbName : "Product Group", Sort : "DisplayName",
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

    // { "fbFuncName" : "fn_cb_setProductGroup" }
    var fn_cb_setProductGroup = function(parsedParams){
        const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
        vdCommon.setLogLevel("Debug");

		try {
            vdCommon.printParams(parsedParams);

		    var dims = ['[Item].[Product Group].filter(#.Name != "-").relatedmembers([Product Group])'];

		    // Casecade 를 위해서 Dimension 추가
		    dims = vdUtil.fn_addIncludeField(dims, parsedParams);

            // where절 세팅
            parsedParams.fbParams.where["[Item].[Item Stage]"] = "SET";

            var result = vdCommon.selectList(dims, [], vdUtil.fn_makeWhere(parsedParams), "", parsedParams.fbParams.limit);
            //vdCommon.printCsData(result, 3);
            var comboList = vdCommon.fn_makeCombo(result, {DimName : "Item", DimAttbName : "Product Group", Sort : "Product Group Sorting Order",
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

    // { "fbFuncName" : "fn_cb_siteMFMtrl" }
    // { "fbFuncName" : "fn_cb_siteMFMtrl","fbParams" : {"includeField" : "Location:Company:Company" ,"where" : { "Location.[All Location]" : "All" }, "limit" : 10 ,"existAll" : true} }
    var fn_cb_siteMFMtrl = function(parsedParams){
        const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
        vdCommon.setLogLevel("Debug");

		try {
            vdCommon.printParams(parsedParams);

		    var dims = ['&NSUILocationMFMtrlView'];

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

    // { "fbFuncName" : "fn_cb_siteFrom",  "fbParams" : { "filters" : { "[Version].[Version Name]" : {"SelectedMembers" : ["CWV_MP"], "MemberFilter" : ""} } } }
    var fn_cb_siteFrom = function(parsedParams){
        const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
        vdCommon.setLogLevel("Debug");

        try {
            vdCommon.printParams(parsedParams);

		    var dims = ['&NSUILocationPlant'];

		    // Casecade 를 위해서 Dimension 추가
		    dims = vdUtil.fn_addIncludeField(dims, parsedParams);

            var version = vdUtil.fn_getFilterQuery(parsedParams, "[Version].[Version Name]");

            var result = vdCommon.selectList(dims, ["Measure.[BOD List_BOD Valid]"],
                                             'where { ' + version + ', [Sub Location].[Sub Location], [Trans Mode].[Trans Mode], ' +
                                                'Measure.[BOD List_BOD Valid] == "Y", ' +
                                                'coalesce(Measure.[BOD List_Eff Startdate],DATEADD(Now(),-1,"Day")) < now(), ' +
                                                'coalesce(Measure.[BOD List_Eff Enddate],DATEADD(Now(),1,"Day")) > now()}',
                                             "",
                                             "");

            var comboList = vdCommon.fn_makeCombo(result, {DimName : "Location", DimAttbName : "Location", Sort : "DisplayName",
                                                    includeField : parsedParams.fbParams.includeField,
                                                    includeProperty : parsedParams.fbParams.includeProperty,
                                                    existAll : parsedParams.fbParams.existAll,
                                                    existBlank : parsedParams.fbParams.existBlank,
                                                    existHyphen : parsedParams.fbParams.existHyphen,
                                                    isDisplayNameWithCode : parsedParams.fbParams.isDisplayNameWithCode});
            vdCommon.debug("ComboData : " + JSON.stringify(comboList.slice(0,3)));

            vdCommon.programEnd();

            return comboList;
        } catch ( e ) {
            RuleOutputToUI = { Status : 'Error', Message : "Js Logic Error : " + e.message };
            return;
        }
    };

    // { "fbFuncName" : "fn_cb_siteTo","fbParams" : { "Location.[Location]" : ["P306","P54A"], "filters" : { "[Version].[Version Name]" : {"SelectedMembers" : ["CWV_MP"], "MemberFilter" : ""} } } }
    var fn_cb_siteTo = function(parsedParams){
        const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
        vdCommon.setLogLevel("Debug");

        try {
            vdCommon.printParams(parsedParams);

            var fbLocation = parsedParams.fbParams["Location.[Location]"];

            var dims = ['&NSUISubLocationDC'];

		    // Casecade 를 위해서 Dimension 추가
		    dims = vdUtil.fn_addIncludeField(dims, parsedParams);

            var version = vdUtil.fn_getFilterQuery(parsedParams, "[Version].[Version Name]");

            var result = vdCommon.selectList(dims, ["Measure.[BOD List_BOD Valid]"],
                                             'where { ' + version + ', [Location].[Location]' + vdUtil.fn_filterStr(fbLocation) + ', [Trans Mode].[Trans Mode], ' +
                                                'Measure.[BOD List_BOD Valid] == "Y", ' +
                                                'coalesce(Measure.[BOD List_Eff Startdate],DATEADD(Now(),-1,"Day")) < now(), ' +
                                                'coalesce(Measure.[BOD List_Eff Enddate],DATEADD(Now(),1,"Day")) > now()}',
                                             "",
                                             "");

            var comboList = vdCommon.fn_makeCombo(result, {DimName : "Sub Location", DimAttbName : "Sub Location", Sort : "DisplayName",
                                                    includeField : parsedParams.fbParams.includeField,
                                                    includeProperty : parsedParams.fbParams.includeProperty,
                                                    existAll : parsedParams.fbParams.existAll,
                                                    existBlank : parsedParams.fbParams.existBlank,
                                                    existHyphen : parsedParams.fbParams.existHyphen,
                                                    isDisplayNameWithCode : parsedParams.fbParams.isDisplayNameWithCode});
            vdCommon.debug("ComboData : " + JSON.stringify(comboList.slice(0,3)));

            vdCommon.programEnd();

            return comboList;
        } catch ( e ) {
            RuleOutputToUI = { Status : 'Error', Message : "Js Logic Error : " + e.message };
            return;
        }
    };

    // { "fbFuncName" : "fn_cb_shipmentType" }
	var fn_cb_shipmentType = function(parsedParams){
        const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
        vdCommon.setLogLevel("Debug");

		try {
            vdCommon.printParams(parsedParams);

            var comboList = vdCommon.fn_makeCombo(null, {ComboCodes : ["INDIR","DIR_D","DIR_S"], ComboValues : ["INDIR","DIR_D","DIR_S"],
                                                    existAll : parsedParams.fbParams.existAll,
                                                    existBlank : parsedParams.fbParams.existBlank,
                                                    existHyphen : parsedParams.fbParams.existHyphen});

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
            vdCommon.printParams(parsedParams);

            var comboList = vdCommon.fn_makeCombo(null, {ComboCodes : ["Y","N","-"], ComboValues : ["Y","N","-"],
                                                    existAll : parsedParams.fbParams.existAll,
                                                    existBlank : parsedParams.fbParams.existBlank,
                                                    existHyphen : parsedParams.fbParams.existHyphen});

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
            vdCommon.printParams(parsedParams);

            var comboList = vdCommon.fn_makeCombo(null, {ComboCodes : ["Y","N"], ComboValues : ["Y","N"],
                                                    existAll : parsedParams.fbParams.existAll,
                                                    existBlank : parsedParams.fbParams.existBlank,
                                                    existHyphen : parsedParams.fbParams.existHyphen});

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
            vdCommon.printParams(parsedParams);

		    var dims = ['Item.[Plan Group]'];

		    // Casecade 를 위해서 Dimension 추가
		    dims = vdUtil.fn_addIncludeField(dims, parsedParams);

            var result = vdCommon.selectList(dims, [], vdUtil.fn_makeWhere(parsedParams), "", parsedParams.fbParams.limit);
            //vdCommon.printCsData(result, 3);
            var comboList = vdCommon.fn_makeCombo(result, {DimName : "Item", DimAttbName : "Plan Group", Sort : "DisplayName",
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

    // { "fbFuncName" : "fn_cb_locationJdmType" }
    var fn_cb_locationJdmType = function(parsedParams){
        const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
        vdCommon.setLogLevel("Debug");

		try {
            vdCommon.printParams(parsedParams);

		    var comboList = vdCommon.fn_makeCombo(null, {ComboCodes : ["JDM","Nomal"], ComboValues : ["JDM","Nomal"],
                                                    existAll : parsedParams.fbParams.existAll,
                                                    existBlank : parsedParams.fbParams.existBlank,
                                                    existHyphen : parsedParams.fbParams.existHyphen});

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
            vdCommon.printParams(parsedParams);

		    var dims = ['Item.[SCM Type].filter(~(#.Name =="-"))'];

		    // Casecade 를 위해서 Dimension 추가
		    dims = vdUtil.fn_addIncludeField(dims, parsedParams);

            var result = vdCommon.selectList(dims, [], vdUtil.fn_makeWhere(parsedParams), "", parsedParams.fbParams.limit);
            //vdCommon.printCsData(result, 3);
            var comboList = vdCommon.fn_makeCombo(result, {DimName : "Item", DimAttbName : "SCM Type", Sort : "DisplayName",
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

    // { "fbFuncName" : "fn_cb_confirm" }
    var fn_cb_confirm = function(parsedParams){
        const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
        vdCommon.setLogLevel("Debug");

		try {
            vdCommon.printParams(parsedParams);

		    var comboList = vdCommon.fn_makeCombo(null, {ComboCodes : ["REQ","CON"], ComboValues : ["REQ","CON"],
                                                    existAll : parsedParams.fbParams.existAll,
                                                    existBlank : parsedParams.fbParams.existBlank,
                                                    existHyphen : parsedParams.fbParams.existHyphen});

            vdCommon.programEnd();

            return { "Code" : 0, "Msg" : "", "Rows" : comboList };
        } catch ( e ) {
            vdCommon.error(e.message);
            return { "Code" : -1, "Msg" : e.message };
        }
    };

    // { "fbFuncName" : "fn_cb_siteMfValidBod", "fbParams" : { "filters" : { "[Version].[Version Name]" : {"SelectedMembers" : ["CWV_MP"], "MemberFilter" : ""} } } }
    var fn_cb_siteMfValidBod = function(parsedParams){
        const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
        vdCommon.setLogLevel("Debug");

		try {
            vdCommon.printParams(parsedParams);

		    var dims = ['[Location].[Location]'];

		    // Casecade 를 위해서 Dimension 추가
		    dims = vdUtil.fn_addIncludeField(dims, parsedParams);

            var version = vdUtil.fn_getFilterQuery(parsedParams, "[Version].[Version Name]");

            var where = 'where { ' + version + ', Measure.[BOD List_BOD Valid] == "Y", Measure.[BOD Item_Asn]==1 }';
            var result = vdCommon.selectList(dims, ["Measure.[BOD Item_Asn]"], where, "orderby [Location].[Location].DisplayName", parsedParams.fbParams.limit);
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

    // { "fbFuncName" : "fn_cb_siteMfDcValidBod", "fbParams" : { "[Location].[Location]" : "P105", "filters" : { "[Version].[Version Name]" : {"SelectedMembers" : ["CWV_MP"], "MemberFilter" : ""} } } }
    var fn_cb_siteMfDcValidBod = function(parsedParams){
        const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
        vdCommon.setLogLevel("Debug");

		try {
            vdCommon.printParams(parsedParams);

		    var dims = ['[Sub Location].[Sub Location]',
		                    '[Location].[Location]' + vdUtil.fn_filterStr(parsedParams.fbParams["[Location].[Location]"])];

		    // Casecade 를 위해서 Dimension 추가
		    dims = vdUtil.fn_addIncludeField(dims, parsedParams);

            parsedParams.fbParams.includeField += ( parsedParams.fbParams.includeField == "" ? "" : "," ) + "Location:Location:Location";

            var version = vdUtil.fn_getFilterQuery(parsedParams, "[Version].[Version Name]");

            var where = 'where { ' + version + ', Measure.[BOD List_BOD Valid] == "Y", Measure.[BOD Item_Asn]==1 }';
            var result = vdCommon.selectList(dims, ["Measure.[BOD Item_Asn]"], where, "orderby [Sub Location].[Sub Location].DisplayName", parsedParams.fbParams.limit);
            var comboList = vdCommon.fn_makeCombo(result, {DimName : "Sub Location", DimAttbName : "Sub Location", Sort : "DisplayName",
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

    // { "fbFuncName" : "fn_cb_setItemValidBod", "fbParams" : { "[Location].[Location]" : "P105", "[Sub Location].[Sub Location]" : "S356" , "filters" : { "[Version].[Version Name]" : {"SelectedMembers" : ["CWV_MP"], "MemberFilter" : ""} } } }
    var fn_cb_setItemValidBod = function(parsedParams){
        const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
        vdCommon.setLogLevel("Debug");

		try {
            vdCommon.printParams(parsedParams);

		    var dims = ['&SETItem'];

		    // Casecade 를 위해서 Dimension 추가
		    dims = vdUtil.fn_addIncludeField(dims, parsedParams);

            var version = vdUtil.fn_getFilterQuery(parsedParams, "[Version].[Version Name]");

            var where = 'where { ' + version + ', Measure.[BOD List_BOD Valid] == "Y", ';
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

    // { "fbFuncName" : "fn_cb_siteMfLcm" }
	var fn_cb_siteMfLcm = function(parsedParams){
        const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
        vdCommon.setLogLevel("Debug");

		try {
            vdCommon.printParams(parsedParams);

		    var dims = ['&MFStageLCMLocation'];

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

    // { "fbFuncName" : "fn_cb_company" }
	var fn_cb_company = function(parsedParams){
        const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
        vdCommon.setLogLevel("Debug");

		try {
            vdCommon.printParams(parsedParams);

		    var dims = ['Company.[Company]'];

		    // Casecade 를 위해서 Dimension 추가
		    dims = vdUtil.fn_addIncludeField(dims, parsedParams);

            var result = vdCommon.selectList(dims, [], vdUtil.fn_makeWhere(parsedParams), "", parsedParams.fbParams.limit);
            //vdCommon.printCsData(result, 3);
            var comboList = vdCommon.fn_makeCombo(result, {DimName : "Company", DimAttbName : "Company", Sort : "DisplayName",
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

    // { "fbFuncName" : "fn_cb_country" }
	var fn_cb_country = function(parsedParams){
        const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
        vdCommon.setLogLevel("Debug");

		try {
            vdCommon.printParams(parsedParams);

		    var dims = ['Country.[Country]'];

		    // Casecade 를 위해서 Dimension 추가
		    dims = vdUtil.fn_addIncludeField(dims, parsedParams);

            var result = vdCommon.selectList(dims, [], vdUtil.fn_makeWhere(parsedParams), "", parsedParams.fbParams.limit);
            //vdCommon.printCsData(result, 3);
            var comboList = vdCommon.fn_makeCombo(result, {DimName : "Country", DimAttbName : "Country", Sort : "DisplayName",
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

    /*
        {   "fbFuncName" : "fn_cb_locationSiteGroup3",
            "fbParams" : { "includeField" : "Location:Site Group1:group1,Location:Site Group2:group2"
                            ,"[Location].[Site Group1]" : ["MF"]
                            ,"[Location].[Site Group2]" : ["MF_S.W ASIA","MF_LATIN_AMERICA"]
                            ,"[Location].[Site Group3]" : ["MF_S.W ASIA_SIEL"]
                         }
        }
    */
	var fn_cb_locationSiteGroup3 = function(parsedParams){
        const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
        vdCommon.setLogLevel("Debug");

		try {
            vdCommon.printParams(parsedParams);

		    // 필터값이 있는지 체크하여 Dims 에 추가
		    var filter = "";
            if ( parsedParams.fbParams["[Location].[Site Group3]"] != undefined ) {
                filter = vdUtil.fn_filterStr(parsedParams.fbParams["[Location].[Site Group3]"]);
            }
		    var dims = ['[Location].[Site Group3].filter(#.[Site Group3 View Flag] == true)' + filter];

		    // Casecade 를 위해서 Dimension 추가
		    dims = vdUtil.fn_addIncludeField(dims, parsedParams);

            var result = vdCommon.selectList(dims, [], vdUtil.fn_makeWhere(parsedParams), "", parsedParams.fbParams.limit);
            //vdCommon.printCsData(result, 3);
            var comboList = vdCommon.fn_makeCombo(result, {DimName : "Location", DimAttbName : "Site Group3", Sort : "DisplayName",
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

    /*
        {   "fbFuncName" : "fn_cb_locationSiteGroup123_filter",
            "fbParams" : { "filters" : {
                                        "[Location].[Site Group1]" : {"SelectedMembers" : ["MF"], "MemberFilter" : ""}
                                        ,"[Location].[Site Group2]" : {"SelectedMembers" : ["MF_S.W ASIA","MF_LATIN_AMERICA"], "MemberFilter" : ""}
                                        ,"[Location].[Site Group3]" : {"SelectedMembers" : ["MF_S.W ASIA_SIEL"], "MemberFilter" : ""}
                                    }
                         }
        }
    */
	var fn_cb_locationSiteGroup123_filter = function(parsedParams){
        const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
        vdCommon.setLogLevel("Debug");

		try {
            vdCommon.printParams(parsedParams);

		    var siteGroup1 = parsedParams.fbParams.filters["[Location].[Site Group1]"];
		    var siteGroup2 = parsedParams.fbParams.filters["[Location].[Site Group2]"];
		    var siteGroup3 = parsedParams.fbParams.filters["[Location].[Site Group3]"];
		    var dims = [];
		    if ( siteGroup1 == undefined ) {
		        dims.push("[Location].[Site Group1]" + ".filter(#.[Site Group1 View Flag] == true)")
		    } else {
		        if ( siteGroup1["MemberFilter"] == "" ) {
		            dims.push("[Location].[Site Group1]" + vdUtil.fn_filterStr(siteGroup1["SelectedMembers"]) + ".filter(#.[Site Group1 View Flag] == true)");
		        } else {
		            dims.push(siteGroup1["MemberFilter"] + vdUtil.fn_filterStr(siteGroup1["SelectedMembers"]));
		        }
		    }
		    if ( siteGroup2 == undefined ) {
		        dims.push("[Location].[Site Group2]" + ".filter(#.[Site Group2 View Flag] == true)")
		    } else {
		        if ( siteGroup2["MemberFilter"] == "" ) {
		            dims.push("[Location].[Site Group2]" + vdUtil.fn_filterStr(siteGroup2["SelectedMembers"]) + ".filter(#.[Site Group2 View Flag] == true)");
		        } else {
		            dims.push(siteGroup2["MemberFilter"] + vdUtil.fn_filterStr(siteGroup2["SelectedMembers"]));
		        }
		    }
		    if ( siteGroup3 == undefined ) {
		        dims.push("[Location].[Site Group3]" + ".filter(#.[Site Group3 View Flag] == true)")
		    } else {
		        if ( siteGroup3["MemberFilter"] == "" ) {
		            dims.push("[Location].[Site Group3]" + vdUtil.fn_filterStr(siteGroup3["SelectedMembers"]) + ".filter(#.[Site Group3 View Flag] == true)");
		        } else {
		            dims.push(siteGroup3["MemberFilter"] + vdUtil.fn_filterStr(siteGroup3["SelectedMembers"]));
		        }
		    }

            parsedParams.fbParams["includeField"] = "Location:Site Group1:group1,Location:Site Group2:group2";

            var result = vdCommon.selectList(dims, [], vdUtil.fn_makeWhere(parsedParams), "", parsedParams.fbParams.limit);
            //vdCommon.printCsData(result, 3);
            var comboList = vdCommon.fn_makeCombo(result, {DimName : "Location", DimAttbName : "Site Group3", Sort : "DisplayName",
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

    // { "fbFuncName" : "fn_cb_lcmProductGroup" }
    var fn_cb_lcmProductGroup = function(parsedParams){
        const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
        vdCommon.setLogLevel("Debug");

		try {
            vdCommon.printParams(parsedParams);

		    var dims = ['[Item].[Product Group].filter(#.Name != "-").relatedmembers([Product Group])'];

		    // Casecade 를 위해서 Dimension 추가
		    dims = vdUtil.fn_addIncludeField(dims, parsedParams);

            // where절 세팅
            parsedParams.fbParams.where["[Item].[Item Stage]"] = "LCM";

            var result = vdCommon.selectList(dims, [], vdUtil.fn_makeWhere(parsedParams), "", parsedParams.fbParams.limit);
            //vdCommon.printCsData(result, 3);
            var comboList = vdCommon.fn_makeCombo(result, {DimName : "Item", DimAttbName : "Product Group", Sort : "DisplayName",
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

    // 2025.08.29 Append
    // { "fbFuncName" : "fn_cb_lcmItemValidBod", "fbParams" : { "[Location].[Location]" : "P105", "[Sub Location].[Sub Location]" : "S356","filters" : { "[Version].[Version Name]" : {"SelectedMembers" : ["CWV_MP"], "MemberFilter" : ""} } } }
    var fn_cb_lcmItemValidBod = function(parsedParams){
        const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
        vdCommon.setLogLevel("Debug");

		try {
            vdCommon.printParams(parsedParams);

		    var dims = ['&LCMItem'];

		    // Casecade 를 위해서 Dimension 추가
		    dims = vdUtil.fn_addIncludeField(dims, parsedParams);

            var version = vdUtil.fn_getFilterQuery(parsedParams, "[Version].[Version Name]");

            var where = 'where { ' + version + ', Measure.[BOD List_BOD Valid] == "Y", ';
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

    // 25.12.15 함수 추가
    // { "fbFuncName" : "fn_currentWeek" }
	var fn_currentWeek = function(parsedParams){
        const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
        vdCommon.setLogLevel("Debug");

		try {
            vdCommon.printParams(parsedParams);

		    var currentWeek = vdCommon.selectResult('&CurrentWeek.element(0).DisplayName');

            vdCommon.programEnd();

            return { "Code" : 0, "Msg" : "", "CurrentWeek" : currentWeek };
        } catch ( e ) {
            vdCommon.error(e.message);
            return { "Code" : -1, "Msg" : e.message };
        }
    };

    // 25.12.31 함수 추가
    // { "fbFuncName" : "fn_timeInfo" }
    var fn_timeInfo = function(parsedParams){
        const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
        vdCommon.setLogLevel("Debug");

		try {
            vdCommon.printParams(parsedParams);

		    var CurrentDay = vdCommon.selectResult('&CurrentDay.element(0).Name');

		    var LastWeek = vdCommon.selectResult('&LastWeek.element(0).DisplayName');
		    var CurrentWeek = vdCommon.selectResult('&CurrentWeek.element(0).DisplayName');
		    var NextWeek = vdCommon.selectResult('&NextWeek.element(0).DisplayName');

		    var LastWeek = vdCommon.selectResult('&LastWeek.element(0).DisplayName');
		    var CurrentWeek = vdCommon.selectResult('&CurrentWeek.element(0).DisplayName');
		    var NextWeek = vdCommon.selectResult('&NextWeek.element(0).DisplayName');

		    var CurrentPartialWeek = vdCommon.selectResult('&CurrentPartialWeek.element(0).DisplayName');

		    var LastMonth = vdCommon.selectResult('&LastMonth.element(0).DisplayName');
		    var CurrentMonth = vdCommon.selectResult('&CurrentMonth.element(0).DisplayName');
		    var NextMonth = vdCommon.selectResult('&NextMonth.element(0).DisplayName');

		    var LastYear = vdCommon.selectResult('&LastYear.element(0).DisplayName');
		    var CurrentYear = vdCommon.selectResult('&CurrentYear.element(0).DisplayName');
		    var NextYear = vdCommon.selectResult('&NextYear.element(0).DisplayName');

            var nowTime = new Date();
            nowTime.setHours(nowTime.getHours() + 9);
            var CurrentTime = nowTime.getFullYear() + "-"
                                + vdUtil.fn_lpad((nowTime.getMonth() + 1) + "", 2, "0") + "-"
                                + vdUtil.fn_lpad(nowTime.getDate() + "", 2, "0") + " "
                                + vdUtil.fn_lpad(nowTime.getHours() + "", 2, "0") + ":"
                                + vdUtil.fn_lpad(nowTime.getMinutes() + "", 2, "0") + ":"
                                + vdUtil.fn_lpad(nowTime.getSeconds() + "", 2, "0");
            vdCommon.programEnd();

            return { "Code" : 0, "Msg" : ""
                        ,"CurrentDay" : CurrentDay
                        ,"LastWeek" : LastWeek, "CurrentWeek" : CurrentWeek, "NextWeek" : NextWeek
                        ,"CurrentPartialWeek" : CurrentPartialWeek
                        ,"LastMonth" : LastMonth, "CurrentMonth" : CurrentMonth, "NextMonth" : NextMonth
                        ,"LastYear" : LastYear, "CurrentYear" : CurrentYear, "NextYear" : NextYear
                        ,"CurrentTime" : CurrentTime
                         };
        } catch ( e ) {
            vdCommon.error(e.message);
            return { "Code" : -1, "Msg" : e.message };
        }
    };

    /*
        26.1.19 추가
        {   "fbFuncName" : "fn_cb_setItemForBodItem"
            ,"fbParams" : {
                "where" : { "[Item].[Product Group]" : "TV", "[Location].[Location]" : "P105", "[Sub Location].[Sub Location]" : "S356" }
                ,"filters" : {   "[Version].[Version Name]" : {"SelectedMembers" : ["CWV_MP"], "MemberFilter" : "" } }
            }
        }
    */
    var fn_cb_setItemForBodItem = function(parsedParams){
        const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
        vdCommon.setLogLevel("Debug");

		try {
            vdCommon.printParams(parsedParams);

		    var dims = ['&SETItem'];

		    // Casecade 를 위해서 Dimension 추가
		    dims = vdUtil.fn_addIncludeField(dims, parsedParams);

            var otherWhere = [vdUtil.fn_getFilterQuery(parsedParams, "[Version].[Version Name]")
                                ,'coalesce(Measure.[BOD Item_Eff Startdate],DATEADD(Now(),-1,"Day")) < now()'
                                ,'coalesce(Measure.[BOD Item_Eff Enddate],DATEADD(Now(),1,"Day")) > now()'];
            var whereFilter = 'Measure.[Item Site Asn_Cur Status] startswith "ACTIVE" || Measure.[Item Site Asn_Cur Status] contains ",ACTIVE" || ' +
                                'Measure.[Item Site Asn_Cur Status] startswith "PLANNED" || Measure.[Item Site Asn_Cur Status] contains ",PLANNED"';
            var result = vdCommon.selectList(dims, ["Measure.[BOD Item_BOD LT]"], vdUtil.fn_makeWhere(parsedParams, otherWhere), "", parsedParams.fbParams.limit, whereFilter);
            //vdCommon.printCsData(result, 3);
            var comboList = vdCommon.fn_makeCombo(result, {DimName : "Item", DimAttbName : "Item", Sort : "DisplayName",
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

    /*
        26.1.21 추가
        {   "fbFuncName" : "fn_cb_subLocationForLcmBodList"
            ,"fbParams" : {
                "where" : { "[Location].[Location]" : "P306SP" }
                ,"filters" : {   "[Version].[Version Name]" : {"SelectedMembers" : ["CWV_MP"], "MemberFilter" : "" } }
            }
        }
    */
    var fn_cb_subLocationForLcmBodList = function(parsedParams){
        const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
        vdCommon.setLogLevel("Debug");

		try {
            vdCommon.printParams(parsedParams);

		    var dims = ['&MFStageSETSubLocation.unionwith(&MFStageKDSubLocation)'];

		    // Casecade 를 위해서 Dimension 추가
		    dims = vdUtil.fn_addIncludeField(dims, parsedParams);

            var otherWhere = [vdUtil.fn_getFilterQuery(parsedParams, "[Version].[Version Name]")
                                ,'Measure.[LCM BOD List_BOD Valid] == "Y"'
                                ,'coalesce(Measure.[LCM BOD List_Eff Startdate],DATEADD(Now(),-1,"Day")) < now()'
                                ,'coalesce(Measure.[LCM BOD List_Eff Enddate],DATEADD(Now(),1,"Day")) > now()'];
            var result = vdCommon.selectList(dims, ["Measure.[LCM BOD List_BOD Valid]"], vdUtil.fn_makeWhere(parsedParams, otherWhere), "", parsedParams.fbParams.limit);
            //vdCommon.printCsData(result, 3);
            var comboList = vdCommon.fn_makeCombo(result, {DimName : "Sub Location", DimAttbName : "Sub Location", Sort : "DisplayName",
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

    // { "fbFuncName" : "fn_cb_lotSizingRemain" }
	var fn_cb_lotSizingRemain = function(parsedParams){
        const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
        vdCommon.setLogLevel("Debug");

		try {
            vdCommon.printParams(parsedParams);

            var comboList = vdCommon.fn_makeCombo(null, {ComboCodes : ["Down","Keep"], ComboValues : ["Down","Keep"]});
            vdCommon.debug("ComboData : " + JSON.stringify(comboList.slice(0,3)));

            vdCommon.programEnd();

            return { "Code" : 0, "Msg" : "", "Rows" : comboList };
        } catch ( e ) {
            vdCommon.error(e.message);
            return { "Code" : -1, "Msg" : e.message };
        }
    };

    /*
        26.2.25 추가
        {   "fbFuncName" : "fn_defaultInfo"
            ,"fbParams" : {
                "filters" : {   "[Version].[Version Name]" : {"SelectedMembers" : ["202605_M_WI_01"], "MemberFilter" : "" } }
            }
        }

        대상 : select (Version.[Version Name].filter(#.[Plan Type] == "What-If"));
    */
    var fn_defaultInfo = function(parsedParams){
        const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
        vdCommon.setLogLevel("Debug");

		try {
            vdCommon.printParams(parsedParams);

            var planType = "";
            var description = "";

            var result = vdCommon.selectList([vdUtil.fn_getFilterVersion(parsedParams)], [], "", "", "");
            if ( result.cs.rowCount > 0 ) {
                planType = vdUtil.fn_getDimPropertyValue(result, 0, "Version", "Version Name", "Plan Type");
                description = vdUtil.fn_getDimPropertyValue(result, 0, "Version", "Version Name", "Description");
            }

            vdCommon.programEnd();

            return { "Code" : 0, "Msg" : ""
                        ,"IsScenario" : ( planType == "What-If" ? "Y" : "N")
                        ,"VersionInfo" : ( planType == "What-If" ? "This data is currently being edited in the scenario version. (" + description + ")" : "")
                   };
        } catch ( e ) {
            vdCommon.error(e.message);
            return { "Code" : -1, "Msg" : e.message };
        }
    };

    /*
        26.3.3 추가 : Item 의 상세정보를 가져온다.
        {   "fbFuncName" : "fn_itemInfo", "fbParams" : { "[Item].[Item]" : "UA58AU7000UCAB" } }
    */
    var fn_itemInfo = function(parsedParams){
        const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
        vdCommon.setLogLevel("Debug");

		try {
            vdCommon.printParams(parsedParams);

            var rtn = { "Code" : 0, "Msg" : "" };
            var result = vdCommon.selectList(["[Item].[Item].[" + parsedParams.fbParams["[Item].[Item]"] + "]"
                                                ,"[Item].[Product Group]"
                                                ,"[Item].[Product]"]
                                             ,[], "", "", "");
            if ( result.cs.rowCount > 0 ) {
                rtn["Is Hero"] = vdUtil.fn_getString(vdUtil.fn_getDimPropertyValue(result, 0, "Item", "Item", "Is Hero"));
                rtn["Product Group"] = vdUtil.fn_getDimValue(result, 0, "Item", "Product Group");
                rtn["Product"] = vdUtil.fn_getDimValue(result, 0, "Item", "Product");
            }

            vdCommon.programEnd();

            return rtn;
        } catch ( e ) {
            vdCommon.error(e.message);
            return { "Code" : -1, "Msg" : e.message };
        }
    };

    // { "fbFuncName" : "fn_updateInfo", "fbParams" : { "version" : "CWV_MP", "measureList" : ["Measure.[VersionInfo_Time Phased BOD Master Update User]", "Measure.[VersionInfo_Time Phased BOD Master Update Time]"] } }
    var fn_updateInfo = function(parsedParams){
        const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
        vdCommon.setLogLevel("Debug");

		try {
            vdCommon.printParams(parsedParams);

            var result = vdCommon.selectList(["[Version].[Version Name].[" + parsedParams.fbParams.version + "]"], parsedParams.fbParams.measureList, "", "", "");
            var rtn = { "Code" : 0, "Msg" : "" };
            for ( var i = 0; i < result.cs.rowCount; i++ ) {
                for ( var m = 0; m < parsedParams.fbParams.measureList.length; m++ ) {
                    var measure = parsedParams.fbParams.measureList[m];
                    rtn[measure] = result.cs.row(i).cell(result.cs.measureColumnIndex(vdUtil.fn_getMeasureName(measure)));
                }
            }

            vdCommon.programEnd();

            return rtn;
        } catch ( e ) {
            vdCommon.error(e.message);
            return { "Code" : -1, "Msg" : e.message };
        }
    };

    // 26.3.11 : { "fbFuncName" : "fn_cb_siteDCwithKD" }
    var fn_cb_siteDCwithKD = function(parsedParams){
        const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
        vdCommon.setLogLevel("Debug");

		try {
            vdCommon.printParams(parsedParams);

		    var dims = ['&NSUIToLocationDC.unionwith(&NSUIToLocationwithKD)'];

            // filter를 적용할 Dimension 설정
            if ( parsedParams.fbParams["filterDimension"] == undefined ) {
                parsedParams.fbParams["filterDimension"] = ["[To Location]"];
            }

		    // Casecade 를 위해서 Dimension 추가
		    dims = vdUtil.fn_addIncludeField(dims, parsedParams);

            var result = vdCommon.selectList(dims, [], vdUtil.fn_makeWhere(parsedParams), "", parsedParams.fbParams.limit);
            //vdCommon.printCsData(result, 3);
            var comboList = vdCommon.fn_makeCombo(result, {DimName : "To Location", DimAttbName : "To Location", Sort : "DisplayName",
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
        ,"fn_cb_shipmentType" : fn_cb_shipmentType
        ,"fn_cb_setYNH" : fn_cb_setYNH
        ,"fn_cb_setYN" : fn_cb_setYN
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
        ,"fn_cb_locationSiteGroup3" : fn_cb_locationSiteGroup3
        ,"fn_cb_locationSiteGroup123_filter" : fn_cb_locationSiteGroup123_filter
        ,"fn_cb_lcmProductGroup" : fn_cb_lcmProductGroup
        ,"fn_cb_lcmItemValidBod" : fn_cb_lcmItemValidBod
        ,"fn_cb_siteMFDC" : fn_cb_siteMFDC
        ,"fn_currentWeek" : fn_currentWeek
        ,"fn_timeInfo" : fn_timeInfo
        ,"fn_cb_setItemForBodItem" : fn_cb_setItemForBodItem
        ,"fn_cb_subLocationForLcmBodList" : fn_cb_subLocationForLcmBodList
        ,"fn_cb_lotSizingRemain" : fn_cb_lotSizingRemain
        ,"fn_defaultInfo" : fn_defaultInfo
        ,"fn_itemInfo" : fn_itemInfo
        ,"fn_cb_siteDCwithKD" : fn_cb_siteDCwithKD
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
        ,"includeProperty" : "To Location Site ID,To Location Site Location" => Property 를 포함 할때
        ,"where" : { "[Item].[Project]" : "QAQ60G", "[Item].[Basic Name]" : "QTV-F55Q60A/EU" } => 조건을 걸 때
        ,"limit" : 10 => 갯수를 제한할 때
        ,"existAll" : true => 상단에 All 을 추가할 때
        ,"existBlank" : true => 상단에 Blank 을 추가할 때(선택을 안할 경우에 사용)
        ,"existHyphen" : true => 상단에 - 을 추가할 때 (2025-11-25 추가)
        ,"[Item].[Project]" : "QAQ60G" => 파라미터를 넘길 때
        ,"measureList" : ["Measure.[VersionInfo_Time Phased BOD Master Update User]", "Measure.[VersionInfo_Time Phased BOD Master Update Time]"] => 마지막 수정자, 수정일자 Measure 정보만 가져올때
        ,"filters" : { "[Location].[Site Group1]" : {"SelectedMembers" : ["MF"], "MemberFilter" : ""} => 화면 필터값을 넘길 때
        ,"filterDimension" => 정의 안하면 로직의 Default 값으로 가고, ["[Location]"] 로 정의하면 필터를 적용한다. [] 로 넘기면 적용을 안한다.
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

/*
Call Test

     {   "fbFuncName" : "fn_cb_locationSiteGroup3",
                "fbParams" : { "includeField" : "Location:Site Group1:group1,Location:Site Group2:group2"
                                ,"[Location].[Site Group1]" : ["MF"], "[Location].[Site Group2]" : ["MF_S.W ASIA","MF_LATIN_AMERICA"]
                                ,"existAll" : true
                                ,"existBlank" : true
                                ,"existHyphen" : true
                                ,"limit" : 10
                                 } }

    { "fbFuncName" : "fn_cb_setInch", "fbParams" : { "where" : { "[Item].[Project]" : "QAQ60G", "[Item].[Basic Name]" : "QTV-F55Q60A/EU" } } }

    { "fbFuncName" : "fn_cb_setItem", "fbParams" : { "where" : { "[Item].[Project]" : "QAQ60G", "[Item].[Basic Name]" : "QTV-F55Q60A/EU", "[Item].[Inch]" : "50" } } }
    { "fbFuncName" : "fn_cb_setItem", "fbParams" : { "where" : { "[Item].[Project]" : "QAQ60G" } } }
    { "fbFuncName" : "fn_cb_setItem", "fbParams" : { "where" : { "[Item].[Project]" : "QAQ%" } } }
    { "fbFuncName" : "fn_cb_setItem", "fbParams" : { "where" : { "[Item].[Project]" : "%60G" } } }
    { "fbFuncName" : "fn_cb_setItem", "fbParams" : { "where" : { "[Item].[Project]" : "%AQ60%" } } }
    { "fbFuncName" : "fn_cb_setItem", "fbParams" : { "where" : { "[Item].[Project]" : ["QAQ60G", "QTQ60F"] } } }

    { "fbFuncName" : "fn_cb_siteMFMtrl","fbParams" : {"includeField" : "Location:Company:Company" ,"where" : { "Location.[All Location]" : "All" }, "limit" : 10 ,"existAll" : true} }

* 2025-11-25 테스트
    { "fbFuncName" : "fn_cb_scmType", "fbParams" : { "existHyphen" : true } }
*/


/**************************** o9.NSCM.JSEWCommonVD ****************************
    2025-06-17 : 신규 생성
    2025-06-23 : 콤보 데이타 조회시 갯수 제한 ( 3,000 개 )
    2025-06-24 : 콤보 구성시 existAll 파라미터 추가
    2025-07-03 : 콤보 구성시 existBlank 파라미터 추가
    2025-11-24 : vdUtil.fn_addIncludeField 에서
                    attribute 에 attribute^property 형태로 넣은 경우 로직 추가
    2025-11-25 : fn_makeCombo 호출시 existHyphen 옵션 기능 추가
    2025-12-09 : fn_cb_siteMFDC 추가
    2025-12-09 : 해당 Dimension 의 Property 를 가져오는 옵션 추가
                    { "fbFuncName" : "fn_cb_siteDC", "fbParams" : { "includeProperty" : "To Location Site ID,To Location Site Location" } }
    2025-12-11 : filter 적용 로직을 공통으로 반영
    2025-12-15 : fn_currentWeek 추가
    2025-12-31 : fn_timeInfo 추가
    2026-01-05 : fn_addIncludeField, fn_getMeasureName, fn_makeWhere, fn_makeFilterWhere 함수를 commonLib 로 옮김
    2026-01-19 : fn_cb_setItemForBodItem 추가
    2026-01-21 : fn_cb_subLocationForLcmBodList 추가
    2026-01-29 : fn_cb_lotSizingRemain 추가
    2026-02-25 : fn_defaultInfo 추가
    2026-03-03 : fn_itemInfo 추가
    2026-03-11 : fn_cb_siteDCwithKD 추가
**************************** o9.NSCM.JSEWCommonVD ****************************/