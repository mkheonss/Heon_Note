define('o9.NSCM.JSEWBomVersionMgmt', ['o9/data/query', 'o9/data/cellset', 'o9.NSCM.commonLibVD'], function () {

/**************************************************************************************
    프로그램명  : o9.NSCM.JSEWBomVersionMgmt
    화면명     : Bom Version Mgmt
    화면 설계자 : 임재민 프로
    화면 개발자 :
    API 개발자 : sungmin0.lim
    최초생성   : 2026.03.23
**************************************************************************************/


    // fn_cLib 를 통해서 commonLib 를 생성
    var fn_cLib = function(name) {
        return new commonLib.VdCommon(name);
    }
    var fn_cUtil = function() {
        return new commonLib.VdUtil();
    }

    const programName = "o9.NSCM.JSEWBomVersionMgmt";
    const commonLib = require('o9.NSCM.commonLibVD');
    const cUtil = fn_cUtil();

/************************************************* UI Call Common Logic *************************************************/
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

            if ( parsedParams["fbParams"] == undefined ) {
                parsedParams["fbParams"] = {};
            }

            var rtn = functionMap[fbFuncName](parsedParams);

            cLib.programEnd();
            return rtn;
        } catch ( e ) {
            cLib.error(e.message);
            return { "Code" : -1, "Msg" : e.message };
        }
	};

/************************************************* common logic *************************************************/
   /*
- 파라미터
{ "fbFuncName" : "fn_save"
    ,"fbParams" : { "filters" : { "[Version].[Version Name]" : {"SelectedMembers" : ["202605_P_WI_01"], "MemberFilter" : ""} }
                    }
    ,"fbGridRows" : {
        "mtrl" : [
                    { "rowstatus":"U"
                        ,"[Location].[Location]":"P406"
                        ,"[Item Material].[Item Material]":"BN96-54530A"
                        ,"Measure.[Mtrl Usage_Comment]" : "aaaa"
                        ,"Measure.[Mtrl Usage Prty W_Prty]" : ["202547^1","202548^2","202549^3","202550^4"]}
                 ]
        ,"mtrlset" : [
                    { "rowstatus":"U"
                        ,"[Location].[Location]":"P406"
                        ,"[Item].[Item]":"QE43QN92DATXXH"
                        ,"[Item Material].[Item Material]":"1105-003132"
                        ,"[Item Component].[Item Component]":"BN95-10953A"
                        ,"[BOM Info].[BOM Version]":"AA01"
                         ,"Measure.[BOM Version Prty W_Prty]" : ["202547^1","202548^2","202549^3","202550^4"]}
                 ]
        }
}
    */
    var fn_save = function(parsedParams){
        const cLib = fn_cLib(programName + "." + arguments.callee.name);
        cLib.setLogLevel("Debug");

		try {
		    cLib.printParams(parsedParams);

		    var fbVersionName = "[Version].[Version Name].[CWV_MP]";
		    var fbVersion = cUtil.fn_getDimensionValue(cUtil.fn_getFilterVersion(parsedParams));

            var name = cLib.selectResult('CurrentUser().Name');
            var userName = cLib.selectResult('CurrentUser().[User Name]');

		    if ( parsedParams.fbGridRows["mtrl"] != undefined && parsedParams.fbGridRows["mtrl"].length > 0   ) {
                for ( var i = 0; i < parsedParams.fbGridRows.mtrl.length; i++ ) {
                    var row = parsedParams.fbGridRows.mtrl[i];
                    var rowstatus = row["rowstatus"];

                    if ( rowstatus == "U" ) {
                        var dimensions = [];
                        dimensions.push(fbVersionName);
                        dimensions.push(cUtil.fn_qDim(row, "[Location].[Location]"));
                        dimensions.push(cUtil.fn_qDim(row, "[Item Material].[Item Material]"));
                        var measures = [];
                        measures.push(cUtil.fn_qMeaStr("Measure.[Mtrl Usage_Comment]"));
                        measures.push(cUtil.fn_qMeaUpdateTime("Measure.[Mtrl Usage_Update Time]"));
                        measures.push(cUtil.fn_qMeaUpdateUserName("Measure.[Mtrl Usage_Updated By]"));
                        cLib.updateMeasure(dimensions, measures);

                        var weekList = row["Measure.[Mtrl Usage Prty W_Prty]"];
                        var queryStr = "";
                        for ( var m = 0; m < weekList.length; m++ ) {
                            dimensions = [];
                            dimensions.push(fbVersionName);
                            dimensions.push(cUtil.fn_qDim(row, "[Location].[Location]"));
                            dimensions.push(cUtil.fn_qDim(row, "[Item Material].[Item Material]"));
                            dimensions.push("[Time].[Week].[" + weekList[m].split("^")[0] + "]");
                            measures = [];
                            measures.push(cUtil.fn_qMeaNotStr(null, "Measure.[Mtrl Usage Prty W_Prty]", weekList[m].split("^")[1]));

                            queryStr += cLib.updateMeasureQuery(dimensions, measures);
                        }

                        if ( queryStr != "" ) {
                            cLib.executeQuery("Mtrl Usage Prty W", queryStr);
                        }
                    }
                }
            }

            if ( parsedParams.fbGridRows["mtrlset"] != undefined && parsedParams.fbGridRows["mtrlset"].length > 0   ) {
                for ( var i = 0; i < parsedParams.fbGridRows.mtrlset.length; i++ ) {
                    var row = parsedParams.fbGridRows.mtrlset[i];
                    var rowstatus = row["rowstatus"];

                    if ( rowstatus == "U" ) {
                        var dimensions = [];
                        dimensions.push(fbVersionName);
                        dimensions.push(cUtil.fn_qDim(row, "[Location].[Location]"));
                        dimensions.push(cUtil.fn_qDim(row, "[Item].[Item]"));
                        dimensions.push(cUtil.fn_qDim(row, "[Item Material].[Item Material]"));
                        dimensions.push(cUtil.fn_qDim(row, "[Item Component].[Item Component]"));
                        dimensions.push(cUtil.fn_qDim(row, "[BOM Info].[BOM Version]"));
                        var measures = [];
                        measures.push(cUtil.fn_qMeaStr("Measure.[BOM Version_Comment]"));
                        measures.push(cUtil.fn_qMeaStr("Measure.[BOM Version_Fix Flag]"));
                        measures.push(cUtil.fn_qMeaStr("Measure.[BOM Version_Prty]"));
                        measures.push(cUtil.fn_qMeaUpdateTime("Measure.[BOM Version_Update Time]"));
                        measures.push(cUtil.fn_qMeaUpdateUserName("Measure.[BOM Version_Updated By]"));
                        cLib.updateMeasure(dimensions, measures);

                        var weekList = row["Measure.[BOM Version Prty W_Prty]"];
                        var queryStr = "";
                        for ( var m = 0; m < weekList.length; m++ ) {
                            dimensions = [];
                            dimensions.push(fbVersionName);
                            dimensions.push(cUtil.fn_qDim(row, "[Location].[Location]"));
                            dimensions.push(cUtil.fn_qDim(row, "[Item].[Item]"));
                            dimensions.push(cUtil.fn_qDim(row, "[Item Material].[Item Material]"));
                            dimensions.push(cUtil.fn_qDim(row, "[Item Component].[Item Component]"));
                            dimensions.push(cUtil.fn_qDim(row, "[BOM Info].[BOM Version]"));
                            dimensions.push("[Time].[Week].[" + weekList[m].split("^")[0] + "]");
                            measures = [];
                            measures.push(cUtil.fn_qMeaNotStr(null, "Measure.[BOM Version Prty W_Prty]", weekList[m].split("^")[1]));

                            queryStr += cLib.updateMeasureQuery(dimensions, measures);
                        }

                        if ( queryStr != "" ) {
                            cLib.executeQuery("BOM Version Prty W_Prty", queryStr);
                        }
                    }
                }
            }

            cLib.programEnd();

            return { "Code" : 0, "Msg" : "It was saved successfully." };
        } catch ( e ) {
            cLib.error(e.message);
            return { "Code" : -1, "Msg" : e.message };
        }
    };

   /*
- 파라미터
{ "fbFuncName" : "fn_merge"
    ,"fbParams" : { "filters" : { "[Version].[Version Name]" : {"SelectedMembers" : ["202605_P_WI_01"], "MemberFilter" : ""} }
                    }
    ,"fbGridRows" : {
        "mtrl" : [
                    { "[Location].[Location]":"P406"
                        ,"[Item Material].[Item Material]":"BN96-54530A" }
                 ]
        ,"mtrlset" : [
                    { "[Location].[Location]":"P406"
                        ,"[Item].[Item]":"QE43QN92DATXXH"
                        ,"[Item Material].[Item Material]":"1105-003132"
                        ,"[Item Component].[Item Component]":"BN95-10953A"
                        ,"[BOM Info].[BOM Version]":"AA01" }
                 ]
        }
}
    */
    var fn_merge = function(parsedParams){
        const cLib = fn_cLib(programName + "." + arguments.callee.name);
        cLib.setLogLevel("Debug");

		try {
		    cLib.printParams(parsedParams);

		    var fbVersionName = "[Version].[Version Name].[CWV_MP]";
		    var fbVersion = cUtil.fn_getDimensionValue(cUtil.fn_getFilterVersion(parsedParams));

            var name = cLib.selectResult('CurrentUser().Name');
            var userName = cLib.selectResult('CurrentUser().[User Name]');

		    if ( parsedParams.fbGridRows["mtrl"] != undefined && parsedParams.fbGridRows["mtrl"].length > 0   ) {
                for ( var i = 0; i < parsedParams.fbGridRows.mtrl.length; i++ ) {
                    var row = parsedParams.fbGridRows.mtrl[i];

                    var dimensions = [];
                    dimensions.push(fbVersionName);
                    dimensions.push(cUtil.fn_qDim(row, "[Location].[Location]"));
                    dimensions.push(cUtil.fn_qDim(row, "[Item Material].[Item Material]"));
                    var measures = [];
                    measures.push(cUtil.fn_qMeaForMerge("Measure.[Mtrl Usage_Comment]", fbVersion));
                    measures.push(cUtil.fn_qMeaForMerge("Measure.[Mtrl Usage_Model Cnt]", fbVersion));
                    measures.push(cUtil.fn_qMeaUpdateTime("Measure.[Mtrl Usage_Update Time]"));
                    measures.push(cLib.fn_mergeUser("Measure.[Mtrl Usage_Updated By]", fbVersion));
                    cLib.createMeasure(dimensions, measures);

                    dimensions = [];
                    dimensions.push(fbVersionName);
                    dimensions.push(cUtil.fn_qDim(row, "[Location].[Location]"));
                    dimensions.push(cUtil.fn_qDim(row, "[Item Material].[Item Material]"));
                    dimensions.push("&MDMHorizon");
                    measures = [];
                    measures.push(cUtil.fn_qMeaForMerge("Measure.[Mtrl Usage Prty W_Prty]", fbVersion));
                    //measures.push(cUtil.fn_qMeaForMerge("Measure.[BOM Diff Mgmt W_Priority]", fbVersion));
                    cLib.createMeasure(dimensions, measures);
                }
            }

            if ( parsedParams.fbGridRows["mtrlset"] != undefined && parsedParams.fbGridRows["mtrlset"].length > 0   ) {
                for ( var i = 0; i < parsedParams.fbGridRows.mtrlset.length; i++ ) {
                    var row = parsedParams.fbGridRows.mtrlset[i];

                    var dimensions = [];
                    dimensions.push(fbVersionName);
                    dimensions.push(cUtil.fn_qDim(row, "[Location].[Location]"));
                    dimensions.push(cUtil.fn_qDim(row, "[Item].[Item]"));
                    dimensions.push(cUtil.fn_qDim(row, "[Item Material].[Item Material]"));
                    dimensions.push(cUtil.fn_qDim(row, "[Item Component].[Item Component]"));
                    dimensions.push(cUtil.fn_qDim(row, "[BOM Info].[BOM Version]"));
                    var measures = [];
                    measures.push(cUtil.fn_qMeaForMerge("Measure.[BOM Version_Comment]", fbVersion));
                    measures.push(cUtil.fn_qMeaForMerge("Measure.[BOM Version_Fix Flag]", fbVersion));
                    measures.push(cUtil.fn_qMeaForMerge("Measure.[BOM Version_Prty]", fbVersion));
                    measures.push(cUtil.fn_qMeaUpdateTime("Measure.[BOM Version_Update Time]"));
                    measures.push(cLib.fn_mergeUser("Measure.[BOM Version_Updated By]", fbVersion));
                    cLib.createMeasure(dimensions, measures);

                    dimensions = [];
                    dimensions.push(fbVersionName);
                    dimensions.push(cUtil.fn_qDim(row, "[Location].[Location]"));
                    dimensions.push(cUtil.fn_qDim(row, "[Item].[Item]"));
                    dimensions.push(cUtil.fn_qDim(row, "[Item Material].[Item Material]"));
                    dimensions.push(cUtil.fn_qDim(row, "[Item Component].[Item Component]"));
                    dimensions.push(cUtil.fn_qDim(row, "[BOM Info].[BOM Version]"));
                    dimensions.push("&MDMHorizon");
                    measures = [];
                    measures.push(cUtil.fn_qMeaForMerge("Measure.[BOM Version Prty W_Prty]", fbVersion));
                    //measures.push(cUtil.fn_qMeaForMerge("Measure.[BOM Version Prty W_Alert]", fbVersion));
                    //measures.push(cUtil.fn_qMeaForMerge("Measure.[BOM Version Prty W_Horizon Ancestor]", fbVersion));
                    //measures.push(cUtil.fn_qMeaForMerge("Measure.[BOM Version Prty W_Horizon Asn]", fbVersion));
                    //measures.push(cUtil.fn_qMeaForMerge("Measure.[BOM Version Prty W_Horizon Fix]", fbVersion));
                    //measures.push(cUtil.fn_qMeaForMerge("Measure.[BOM Version Prty W_OC]", fbVersion));
                    cLib.createMeasure(dimensions, measures);
                }
            }

            cLib.programEnd();

            return { "Code" : 0, "Msg" : "It was saved successfully." };
        } catch ( e ) {
            cLib.error(e.message);
            return { "Code" : -1, "Msg" : e.message };
        }
    };

/************************************************* util logic *************************************************/

/************************************************* Mapping logic **********************************************/
    // Mapping 함수 정의, 마지막에 선언을 해야 함수를 정상적으로 인식함
    const functionMap = {
        "fn_merge" : fn_merge
        ,"fn_save" : fn_save
    };

    return {
        fn_loadFunction : fn_loadFunction
    };
});

/**************************************************************************************************************


**************************************** o9.NSCM.JSEWBomVersionMgmt *******************************************/