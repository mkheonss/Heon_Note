define('o9.NSCM.JSIntransitMtrl', ['o9/data/query', 'o9/data/cellset', 'o9.NSCM.commonLibVD'], function () {

/**************************************************************************************
    프로그램명  : o9.NSCM.JSIntransitMtrl
    화면명     : Intransit (Material)
    API 개발자 : sungmin0.lim
    최초생성   : 2026.03.06
**************************************************************************************/

    // fn_cLib 를 통해서 commonLib 를 생성
    var fn_cLib = function(name) {
        return new commonLib.VdCommon(name);
    }
    var fn_cUtil = function() {
        return new commonLib.VdUtil();
    }

    const programName = "o9.NSCM.JSIntransitMtrl";
    const commonLib = require('o9.NSCM.commonLibVD');
    const cUtil = fn_cUtil();

	var fn_scenarioVersionInfo = function(o9Params){
        const cLib = fn_cLib(programName + "." + arguments.callee.name);
        cLib.setLogLevel("Debug");

	    try {
            var p = JSON.parse(o9Params);

            cLib.printParams(o9Params);

            var info = cLib.fn_scenarioInfo(p.fbVersion);
            var comboList = [{"Name" : info["VersionInfo"]}];

            cLib.programEnd();

            return comboList;
        } catch ( e ) {
            cLib.error(e.message);
            RuleOutputToUI = { Status : 'Error', Message : "Js Logic Error : " + e.message };
        }
    };

	var fn_mergeValidation = function(o9Params){
        const cLib = fn_cLib(programName + "." + arguments.callee.name);
        cLib.setLogLevel("Debug");

        var rtn = 0;

	    try {
            var p = JSON.parse(o9Params);

            cLib.printParams(o9Params);

            var info = cLib.fn_scenarioInfo(p.fbVersion);
            if ( info["IsScenario"] == "N" ) {
                RuleOutputToUI = { Status : 'Error', Message : "Only scenario Version can be modified." };
                rtn = 1;
                return;
            }

            cLib.programEnd();

            return rtn;
        } catch ( e ) {
            cLib.error(e.message);
            RuleOutputToUI = { Status : 'Error', Message : "Js Logic Error : " + e.message };
            return 1;
        }
    };

    var fn_merge = function(o9Params){
        const cLib = fn_cLib(programName + "." + arguments.callee.name);
        cLib.setLogLevel("Debug");

	    try {
            var p = JSON.parse(o9Params);

            cLib.printParams(o9Params);

            var fbVersionName = "[Version].[Version Name].[CWV_MP]";
		    var fbVersion = p.fbVersion;

            var name = cLib.selectResult('CurrentUser().Name');
            var userName = cLib.selectResult('CurrentUser().[User Name]');

            // merge 가 전체일 경우 null 로 넘어온다.
            var rows = p.fbSelect;

            if ( rows == null ) {
                rows = [];

                var where = 'where { Measure.[Intransit Mtrl_Updated By] == "' + name + '" || Measure.[Intransit Mtrl_Updated By] == "' + userName + '"}';

                // 전체이면 내가 수정한 것만 가져와서 배열을 생성
                var result = cLib.selectList(["[Version].[Version Name].[" + fbVersion + "]"
                                                    ,"[Location].[Location]"
                                                    ,"[Sequence].[Sequence]"
                                                    ,"[Sub Location].[Sub Location]"
                                                    ,"[Item Material].[Item Material]"]
                                             ,["Measure.[Intransit Mtrl_Updated By]"]
                                             ,where, "", "");
                for ( var i = 0; i < result.cs.rowCount; i++ ) {
                    var query = "UpdateScenario ( [Version].[Version Name].[CWV_MP] " +
                                    ",[Version].[Version Name].[" + fbVersion + "] " +
                                    ",false " +
                                    ",for model [Intransit Mtrl] using scope ( " +
                                    "         [Location].[Location].[" + cUtil.fn_getDimValue(result, i, "Location", "Location") + "] " +
                                    "           * [Sequence].[Sequence].[" + cUtil.fn_getDimValue(result, i, "Sequence", "Sequence") + "] " +
                                    "           * [Sub Location].[Sub Location].[" + cUtil.fn_getDimValue(result, i, "Sub Location", "Sub Location") + "] " +
                                    "           * [Item Material].[Item Material].[" + cUtil.fn_getDimValue(result, i, "Item Material", "Item Material") + "] " +
                                    "));";
                    cLib.executeQuery("merge", query);

                    var dimensions = [];
                    dimensions.push(fbVersionName);
                    dimensions.push("[Location].[Location].[" + cUtil.fn_getDimValue(result, i, "Location", "Location") + "]");
                    dimensions.push("[Sequence].[Sequence].[" + cUtil.fn_getDimValue(result, i, "Sequence", "Sequence") + "]");
                    dimensions.push("[Sub Location].[Sub Location].[" + cUtil.fn_getDimValue(result, i, "Sub Location", "Sub Location") + "]");
                    dimensions.push("[Item Material].[Item Material].[" + cUtil.fn_getDimValue(result, i, "Item Material", "Item Material") + "]");
                    var measures = [];
                    measures.push(cUtil.fn_qMeaUpdateTime("Measure.[Intransit Mtrl_Update Time]"));
                    measures.push(cLib.fn_mergeUser("Measure.[Intransit Mtrl_Updated By]", fbVersion));
                    cLib.updateBlockMeasure(dimensions, measures);
                }
            } else {
                for ( var i = 0; i < rows.length; i++ ) {
                    var row = rows[i];

                    var query = "UpdateScenario ( [Version].[Version Name].[CWV_MP] " +
                                    ",[Version].[Version Name].[" + fbVersion + "] " +
                                    ",false " +
                                    ",for model [Intransit Mtrl] using scope ( " +
                                    "         [Location].[Location].[" + row.Location.Value + "] " +
                                    "           * [Sequence].[Sequence].[" + row.Sequence.Value + "] " +
                                    "           * [Sub Location].[Sub Location].[" + row.SubLocation.Value + "] " +
                                    "           * [Item Material].[Item Material].[" + row.ItemMaterial.Value + "] " +
                                    "));";
                    cLib.executeQuery("merge", query);

                    var dimensions = [];
                    dimensions.push(fbVersionName);
                    dimensions.push("[Location].[Location].[" + row.Location.Value + "]");
                    dimensions.push("[Sequence].[Sequence].[" + row.Sequence.Value + "]");
                    dimensions.push("[Sub Location].[Sub Location].[" + row.SubLocation.Value + "]");
                    dimensions.push("[Item Material].[Item Material].[" + row.ItemMaterial.Value + "]");
                    var measures = [];
                    measures.push(cUtil.fn_qMeaUpdateTime("Measure.[Intransit Mtrl_Update Time]"));
                    measures.push(cLib.fn_mergeUser("Measure.[Intransit Mtrl_Updated By]", fbVersion));
                    cLib.updateBlockMeasure(dimensions, measures);
                }
            }

            cLib.programEnd();
        } catch ( e ) {
            cLib.error(e.message);
            RuleOutputToUI = { Status : 'Error', Message : "Js Logic Error : " + e.message };
        }
    };

    var fn_kindCombo = function(o9Params){
        const cLib = fn_cLib(programName + "." + arguments.callee.name);
        cLib.setLogLevel("Debug");

        try {
            var comboList = cLib.fn_makeCombo(null, {ComboCodes : ["1","2","3"], ComboValues : ["Increase week","Decrease week","Select week"]});
            cLib.debug("ComboData : " + JSON.stringify(comboList));

            cLib.programEnd();

            return comboList;
        } catch ( e ) {
            cLib.error(e.message);
            RuleOutputToUI = { Status : 'Error', Message : "Js Logic Error : " + e.message };
            return;
        }
    };

    var fn_kindSubCombo = function(o9Params){
        const cLib = fn_cLib(programName + "." + arguments.callee.name);
        cLib.setLogLevel("Debug");

        try {
            var p = JSON.parse(o9Params);

            cLib.printParams(o9Params);

            var comboList = [];
            if ( p.fbKind == "1" ) {
                var arr = ["1", "2", "3", "4", "5", "6", "7", "8", "9", "10"];
                comboList = cLib.fn_makeCombo(null, {ComboCodes : arr, ComboValues : arr});
            } else if ( p.fbKind == "2" ) {
                var arr = ["-1", "-2", "-3", "-4", "-5", "-6", "-7", "-8", "-9", "-10"];
                comboList = cLib.fn_makeCombo(null, {ComboCodes : arr, ComboValues : arr});
            } else {
                var result = cLib.selectList(["&MPHorizon"], [], "", "", "");
                comboList = cLib.fn_makeCombo(result, {DimName : "Time", DimAttbName : "Week"});
            }

            cLib.debug("ComboData : " + JSON.stringify(comboList));

            cLib.programEnd();

            return comboList;
        } catch ( e ) {
            cLib.error(e.message);
            RuleOutputToUI = { Status : 'Error', Message : "Js Logic Error : " + e.message };
            return;
        }
    };

    var fn_update = function(o9Params){
        const cLib = fn_cLib(programName + "." + arguments.callee.name);
        cLib.setLogLevel("Debug");

	    try {
            var p = JSON.parse(o9Params);

            cLib.printParams(o9Params);

            var hm = {};
            for ( var i = 0; i < p.fbSelect.length; i++ ) {
                var row = p.fbSelect[i];

                if ( p.fbKind != "3" ) {
                    var result = cLib.selectList(["[Version].[Version Name].[" + p.fbVersion + "]"
                                                        ,"[Location].[Location].[" + row.Location.Value + "]"
                                                        ,"[Sequence].[Sequence].[" + row.Sequence.Value + "]"
                                                        ,"[Sub Location].[Sub Location].[" + row.SubLocation.Value + "]"
                                                        ,"[Item Material].[Item Material].[" + row.ItemMaterial.Value + "]"]
                                                 ,["Measure.[Intransit Mtrl_Avail Week]"]
                                                 ,"", "", "");
                    var availWeek = cUtil.fn_getMeaValue(result, 0, "Intransit Mtrl_Avail Week");

                    if ( hm[availWeek] == undefined ) {
                        hm[availWeek] = cLib.selectResult('Time.Week.filter(#.Name == "' + availWeek + '").element(0).LeadOffset(' + p.fbValue + ').Name');
                    }
                }

                var dimensions = [];
                dimensions.push("[Version].[Version Name].[" + p.fbVersion + "]");
                dimensions.push("[Location].[Location].[" + row.Location.Value + "]");
                dimensions.push("[Sequence].[Sequence].[" + row.Sequence.Value + "]");
                dimensions.push("[Sub Location].[Sub Location].[" + row.SubLocation.Value + "]");
                dimensions.push("[Item Material].[Item Material].[" + row.ItemMaterial.Value + "]");
                var measures = [];
                if ( p.fbKind != "3" ) {
                    measures.push(cUtil.fn_qMeaStr(null, "Measure.[Intransit Mtrl_Avail Week]", hm[availWeek]));
                } else {
                    measures.push(cUtil.fn_qMeaStr(null, "Measure.[Intransit Mtrl_Avail Week]", p.fbValue));
                }
                measures.push(cUtil.fn_qMeaUpdateUserName("Measure.[Intransit Mtrl_Updated By]"));
                measures.push(cUtil.fn_qMeaUpdateTime("Measure.[Intransit Mtrl_Update Time]"));
                if ( p.fbQty != "" ) {
                    measures.push(cUtil.fn_qMeaInt(null, "Measure.[Intransit Mtrl_Qty]", p.fbQty));
                }
                cLib.updateBlockMeasure(dimensions, measures);
            }

            cLib.programEnd();
        } catch ( e ) {
            cLib.error(e.message);
            RuleOutputToUI = { Status : 'Error', Message : "Js Logic Error : " + e.message };
        }
    };
	
    return {
        fn_scenarioVersionInfo : fn_scenarioVersionInfo
        ,fn_mergeValidation : fn_mergeValidation
        ,fn_merge : fn_merge
        ,fn_kindCombo : fn_kindCombo
        ,fn_kindSubCombo : fn_kindSubCombo
        ,fn_update : fn_update
    };
});

/**********************************************************************************************************


- o9.NSCM.JSIntransitMtrl
**********************************************************************************************************/