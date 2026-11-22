define('o9.NSCM.JSEWQuotaMtrl', ['o9/data/query', 'o9/data/cellset', 'o9.NSCM.commonLib'], function () {

/**************************************************************************************
    프로그램명  : o9.NSCM.JSEWQuotaMtrl
    화면명     : Quota Mtrl
    화면 설계자 : 이재연 프로
    화면 개발자 : 박승하 프로
    API 개발자 : sungmin0.lim
    최초생성   : 2025.09.09
**************************************************************************************/

	const programName = "o9.NSCM.JSEWQuotaMtrl";
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

            var rtn = functionMap[fbFuncName](parsedParams);

            vdCommon.programEnd();
            return rtn;
        } catch ( e ) {
            return { "Code" : -1, "Msg" : e.message };
        }
	};

/************************************************* common logic *************************************************/
    /*
- 수정 테스트
{ "fbFuncName" : "fn_saveTop", "fbParams" : { "[Version].[Version Name]" : "CWV_MP" },
  "fbGridRows" : [
{ "rowstatus":"U","rowindex":"0","[Version].[Version Name]":"CWV_MP","[Item Material].[Item Material]":"BN44-01110C","[Sub Location].[Sub Location]":"G2902355","[Group].[Group ID]":"SMPS1000003","Measure.[Global Quota Mtrl_Status]":"REQ","Measure.[Global Quota Mtrl Sub_Group Name]":"AAA","Measure.[Global Quota Mtrl W_Portion]" : ["202515^1","202516^2","202517^3","202518^4"] },
{ "rowstatus":"U","rowindex":"1","[Version].[Version Name]":"CWV_MP","[Item Material].[Item Material]":"BN44-01110C","[Sub Location].[Sub Location]":"G1115625","[Group].[Group ID]":"SMPS1000003","Measure.[Global Quota Mtrl_Status]":"CONFIRM","Measure.[Global Quota Mtrl Sub_Group Name]":"BBB","Measure.[Global Quota Mtrl W_Portion]" : ["202515^1","202516^2","202517^3","202518^4"] }
                  ] }
    */

    var fn_saveTop = function(parsedParams){
        const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
        vdCommon.setLogLevel("Debug");

		try {
            // 저장
            for ( var i = 0; i < parsedParams.fbGridRows.length; i++ ) {
                var row = parsedParams.fbGridRows[i];
                var rowstatus = row["rowstatus"];

                if ( rowstatus == "U" ) {
                    var status = row["Measure.[Global Quota Mtrl_Status]"];
                    if ( status != "CONFIRM" ) {
                        // Global Quota Mtrl_Status 변경
                        var dimensions = [];
                        dimensions.push(vdUtil.fn_qDimVersionName(parsedParams));
                        dimensions.push(vdUtil.fn_qDim(row, "[Item Material].[Item Material]"));
                        dimensions.push(vdUtil.fn_qDim(row, "[Sub Location].[Sub Location]"));
                        dimensions.push(vdUtil.fn_qDim(row, "[Group].[Group ID]"));

                        var measures = [];
                        measures.push(vdUtil.fn_qMeaStr(null, "Measure.[Global Quota Mtrl_Status]", "CONFIRM"));
                        measures.push(vdUtil.fn_qMeaUpdateUser("Measure.[Global Quota Mtrl_Updated By]"));
                        measures.push(vdUtil.fn_qMeaUpdateTime("Measure.[Global Quota Mtrl_Update Time]"));

                        vdCommon.updateBlockMeasure(dimensions, measures);
                    } else {
                        // 수정일자 반영
                        var dimensions = [];
                        dimensions.push(vdUtil.fn_qDimVersionName(parsedParams));
                        dimensions.push(vdUtil.fn_qDim(row, "[Item Material].[Item Material]"));
                        dimensions.push(vdUtil.fn_qDim(row, "[Sub Location].[Sub Location]"));
                        dimensions.push(vdUtil.fn_qDim(row, "[Group].[Group ID]"));

                        var measures = [];
                        measures.push(vdUtil.fn_qMeaUpdateUser("Measure.[Global Quota Mtrl_Updated By]"));
                        measures.push(vdUtil.fn_qMeaUpdateTime("Measure.[Global Quota Mtrl_Update Time]"));

                        vdCommon.updateBlockMeasure(dimensions, measures);
                    }

                    // Global Quota Mtrl Sub_Group Name 변경
                    var dimensions = [];
                    dimensions.push(vdUtil.fn_qDimVersionName(parsedParams));
                    dimensions.push(vdUtil.fn_qDim(row, "[Group].[Group ID]"));

                    var measures = [];
                    measures.push(vdUtil.fn_qMeaStr(row, "Measure.[Global Quota Mtrl Sub_Group Name]"));

                    vdCommon.updateBlockMeasure(dimensions, measures);

                    // 주차 수정
                    var weekList = row["Measure.[Global Quota Mtrl W_Portion]"];
                    var queryStr = "";
                    for ( var m = 0; m < weekList.length; m++ ) {
                        var subDimensions = [];
                        subDimensions.push(vdUtil.fn_qDimVersionName(parsedParams));
                        subDimensions.push(vdUtil.fn_qDim(row, "[Item Material].[Item Material]"));
                        subDimensions.push(vdUtil.fn_qDim(row, "[Sub Location].[Sub Location]"));
                        subDimensions.push(vdUtil.fn_qDim(row, "[Group].[Group ID]"));
                        subDimensions.push("[Time].[Week].[" + weekList[m].split("^")[0] + "]");

                        var subMeasures = [];
                        subMeasures.push(vdUtil.fn_qMeaStr(row, "Measure.[Global Quota Mtrl W_Portion]", weekList[m].split("^")[1]));

                        queryStr += vdCommon.updateMeasureQuery(subDimensions, subMeasures);
                    }
                    if ( queryStr != "" ) {
                        vdCommon.executeQuery("Global Quota Mtrl W", queryStr);
                    }
                }
            }

            vdCommon.programEnd();

            return { "Code" : 0, "Msg" : "It was saved successfully." };
        } catch ( e ) {
            vdCommon.error(e.message);
            return { "Code" : -1, "Msg" : e.message };
        }
    };

  /*
- 추가 테스트
{ "fbFuncName" : "fn_saveBottom", "fbParams" : { "[Version].[Version Name]" : "CWV_MP" },
  "fbGridRows" : [
{ "rowstatus":"C","rowindex":"0","[Version].[Version Name]":"CWV_MP","[Item Material].[Item Material]":"BN44-01110C","[Sub Location].[Sub Location]":"G2902355","[Group].[Group ID]":"SMPS1000003","[Location].[Location]":"P401^P306^P701","Measure.[Plant Quota Mtrl W_Portion]" : ["202520^1","202521^2","202522^3","202523^4"] },
{ "rowstatus":"C","rowindex":"1","[Version].[Version Name]":"CWV_MP","[Item Material].[Item Material]":"BN44-01110A","[Sub Location].[Sub Location]":"G1115625","[Group].[Group ID]":"SMPS1000003","[Location].[Location]":"P401^P306^P701","Measure.[Plant Quota Mtrl W_Portion]" : ["202520^1","202521^2","202522^3","202523^4"] }
                  ] }

- 수정 테스트
{ "fbFuncName" : "fn_saveBottom", "fbParams" : { "[Version].[Version Name]" : "CWV_MP" },
  "fbGridRows" : [
{ "rowstatus":"U","rowindex":"2","[Version].[Version Name]":"CWV_MP","[Item Material].[Item Material]":"BN44-01110C","[Sub Location].[Sub Location]":"G2902355","[Group].[Group ID]":"SMPS1000003","[Location].[Location]":"P306","Measure.[Plant Quota Mtrl W_Portion]" : ["202515^11","202516^22","202517^33","202518^44"] }
                  ] }

- 삭제 테스트
{ "fbFuncName" : "fn_saveBottom", "fbParams" : { "[Version].[Version Name]" : "CWV_MP" },
  "fbGridRows" : [
{ "rowstatus":"D","rowindex":"4","[Version].[Version Name]":"CWV_MP","[Item Material].[Item Material]":"BN44-01110C","[Sub Location].[Sub Location]":"G2902355","[Group].[Group ID]":"SMPS1000003","[Location].[Location]":"P401","Measure.[Plant Quota Mtrl W_Portion]" : ["202520^1","202521^2","202522^3","202523^4"] },
{ "rowstatus":"D","rowindex":"5","[Version].[Version Name]":"CWV_MP","[Item Material].[Item Material]":"BN44-01110C","[Sub Location].[Sub Location]":"G2902355","[Group].[Group ID]":"SMPS1000003","[Location].[Location]":"P306","Measure.[Plant Quota Mtrl W_Portion]" : ["202520^1","202521^2","202522^3","202523^4"] },
{ "rowstatus":"D","rowindex":"6","[Version].[Version Name]":"CWV_MP","[Item Material].[Item Material]":"BN44-01110C","[Sub Location].[Sub Location]":"G2902355","[Group].[Group ID]":"SMPS1000003","[Location].[Location]":"P701","Measure.[Plant Quota Mtrl W_Portion]" : ["202520^1","202521^2","202522^3","202523^4"] },
{ "rowstatus":"D","rowindex":"7","[Version].[Version Name]":"CWV_MP","[Item Material].[Item Material]":"BN44-01110A","[Sub Location].[Sub Location]":"G1115625","[Group].[Group ID]":"SMPS1000003","[Location].[Location]":"P401","Measure.[Plant Quota Mtrl W_Portion]" : ["202520^1","202521^2","202522^3","202523^4"] },
{ "rowstatus":"D","rowindex":"8","[Version].[Version Name]":"CWV_MP","[Item Material].[Item Material]":"BN44-01110A","[Sub Location].[Sub Location]":"G1115625","[Group].[Group ID]":"SMPS1000003","[Location].[Location]":"P306","Measure.[Plant Quota Mtrl W_Portion]" : ["202520^1","202521^2","202522^3","202523^4"] },
{ "rowstatus":"D","rowindex":"9","[Version].[Version Name]":"CWV_MP","[Item Material].[Item Material]":"BN44-01110A","[Sub Location].[Sub Location]":"G1115625","[Group].[Group ID]":"SMPS1000003","[Location].[Location]":"P701","Measure.[Plant Quota Mtrl W_Portion]" : ["202520^1","202521^2","202522^3","202523^4"] }
                  ] }
    */

    var fn_saveBottom = function(parsedParams){
        const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
        vdCommon.setLogLevel("Debug");

		try {
		    // Validation 체크 : 등록 체크
            var validation = [];
            for ( var i = 0; i < parsedParams.fbGridRows.length; i++ ) {
                var row = parsedParams.fbGridRows[i];
                var rowstatus = row["rowstatus"];
                var rowindex = row["rowindex"];

                var count = 0;
                if ( rowstatus == "C" ) {
                    var dimensions = [];
                    dimensions.push(vdUtil.fn_qDimVersionName(parsedParams));
                    dimensions.push(vdUtil.fn_qDim(row, "[Item Material].[Item Material]"));
                    dimensions.push(vdUtil.fn_qDim(row, "[Sub Location].[Sub Location]"));
                    dimensions.push(vdUtil.fn_qDim(row, "[Group].[Group ID]"));
                    dimensions.push(vdUtil.fn_qDim(null, "[Time].[Week]", ""));
                    dimensions.push(vdUtil.fn_qDim(row, "[Location].[Location]", row["[Location].[Location]"].split("^")));

                    // 등록 여부 체크
                    var count = vdCommon.selectListCount(dimensions, ["Measure.[Plant Quota Mtrl W_Portion]"], "");
                    if ( count > 0 ) {
                        validation.push(rowindex + "^" + "This is registered data.")
                    }
                }
            }

            if ( validation.length > 0 ) {
                return { "Code" : 1, "Msg" : validation };
            }

            // 저장
            for ( var i = 0; i < parsedParams.fbGridRows.length; i++ ) {
                var row = parsedParams.fbGridRows[i];
                var rowstatus = row["rowstatus"];

                if ( rowstatus == "C" ) {
                    // 배치에서 데이타 생성을 위한 구분자로 Flag 를 세팅한다.
                    var dimensions = [];
                    dimensions.push(vdUtil.fn_qDimVersionName(parsedParams));
                    dimensions.push(vdUtil.fn_qDim(row, "[Group].[Group ID]"));

                    var measures = [];
                    measures.push(vdUtil.fn_qMeaInt(null, "Measure.[Global Quota Mtrl Sub_Plant Mgmt Flag]", "1"));

                    vdCommon.createMeasureQuery(dimensions, measures);

                    // 생성일자(수정일자) 변경
                    dimensions = [];
                    dimensions.push(vdUtil.fn_qDimVersionName(parsedParams));
                    dimensions.push(vdUtil.fn_qDim(row, "[Item Material].[Item Material]"));
                    dimensions.push(vdUtil.fn_qDim(row, "[Sub Location].[Sub Location]"));
                    dimensions.push(vdUtil.fn_qDim(row, "[Group].[Group ID]"));
                    dimensions.push(vdUtil.fn_qDim(null, "[Location].[Location]", row["[Location].[Location]"].split("^")));

                    measures = [];
                    measures.push(vdUtil.fn_qMeaUpdateUser("Measure.[Plant Quota Mtrl_Updated By]"));
                    measures.push(vdUtil.fn_qMeaUpdateTime("Measure.[Plant Quota Mtrl_Update Time]"));

                    vdCommon.createMeasure(dimensions, measures);

                    // Week 데이타 생성
                    vdCommon.createMeasure([vdUtil.fn_qDimVersionName(parsedParams),
                                                vdUtil.fn_qDim(row, "[Item Material].[Item Material]"),
                                                vdUtil.fn_qDim(row, "[Sub Location].[Sub Location]"),
                                                vdUtil.fn_qDim(row, "[Group].[Group ID]"),
                                                vdUtil.fn_qDim(row, "[Location].[Location]", row["[Location].[Location]"].split("^")),
                                                "&MPHroizon"],
                                            ['Measure.[Plant Quota Mtrl W_Portion] = 0;']);

                    var weekList = row["Measure.[Plant Quota Mtrl W_Portion]"];
                    var queryStr = "";
                    for ( var m = 0; m < weekList.length; m++ ) {
                        var subDimensions = [];
                        subDimensions.push(vdUtil.fn_qDimVersionName(parsedParams));
                        subDimensions.push(vdUtil.fn_qDim(row, "[Item Material].[Item Material]"));
                        subDimensions.push(vdUtil.fn_qDim(row, "[Sub Location].[Sub Location]"));
                        subDimensions.push(vdUtil.fn_qDim(row, "[Group].[Group ID]"));
                        subDimensions.push(vdUtil.fn_qDim(null, "[Location].[Location]", row["[Location].[Location]"].split("^")));
                        subDimensions.push("[Time].[Week].[" + weekList[m].split("^")[0] + "]");

                        var subMeasures = [];
                        subMeasures.push(vdUtil.fn_qMeaStr(row, "Measure.[Plant Quota Mtrl W_Portion]", weekList[m].split("^")[1]));

                        queryStr += vdCommon.updateMeasureQuery(subDimensions, subMeasures);
                    }
                    if ( queryStr != "" ) {
                        vdCommon.executeQuery("Plant Quota Mtrl W", queryStr);
                    }
                } else if ( rowstatus == "U" ) {
                    // 수정일자 변경
                    var dimensions = [];
                    dimensions.push(vdUtil.fn_qDimVersionName(parsedParams));
                    dimensions.push(vdUtil.fn_qDim(row, "[Item Material].[Item Material]"));
                    dimensions.push(vdUtil.fn_qDim(row, "[Sub Location].[Sub Location]"));
                    dimensions.push(vdUtil.fn_qDim(row, "[Group].[Group ID]"));
                    dimensions.push(vdUtil.fn_qDim(row, "[Location].[Location]"));

                    var measures = [];
                    measures.push(vdUtil.fn_qMeaUpdateUser("Measure.[Plant Quota Mtrl_Updated By]"));
                    measures.push(vdUtil.fn_qMeaUpdateTime("Measure.[Plant Quota Mtrl_Update Time]"));

                    vdCommon.createMeasure(dimensions, measures);

                    // 주차 수정
                    var weekList = row["Measure.[Plant Quota Mtrl W_Portion]"];
                    var queryStr = "";
                    for ( var m = 0; m < weekList.length; m++ ) {
                        var subDimensions = [];
                        subDimensions.push(vdUtil.fn_qDimVersionName(parsedParams));
                        subDimensions.push(vdUtil.fn_qDim(row, "[Item Material].[Item Material]"));
                        subDimensions.push(vdUtil.fn_qDim(row, "[Sub Location].[Sub Location]"));
                        subDimensions.push(vdUtil.fn_qDim(row, "[Group].[Group ID]"));
                        subDimensions.push(vdUtil.fn_qDim(row, "[Location].[Location]"));
                        subDimensions.push("[Time].[Week].[" + weekList[m].split("^")[0] + "]");

                        var subMeasures = [];
                        subMeasures.push(vdUtil.fn_qMeaStr(row, "Measure.[Plant Quota Mtrl W_Portion]", weekList[m].split("^")[1]));

                        queryStr += vdCommon.updateMeasureQuery(subDimensions, subMeasures);
                    }
                    if ( queryStr != "" ) {
                        vdCommon.executeQuery("Plant Quota Mtrl W", queryStr);
                    }
                } else if ( rowstatus == "D" ) {
                    var where = [];
                    where.push(vdUtil.fn_qDimVersionName(parsedParams));
                    where.push(vdUtil.fn_qDim(row, "[Item Material].[Item Material]"));
                    where.push(vdUtil.fn_qDim(row, "[Sub Location].[Sub Location]"));
                    where.push(vdUtil.fn_qDim(row, "[Group].[Group ID]"));
                    where.push(vdUtil.fn_qDim(row, "[Location].[Location]"));

                    vdCommon.deleteMeasure(where, "Plant Quota Mtrl W");
                }
            }

            vdCommon.programEnd();

            return { "Code" : 0, "Msg" : "It was saved successfully." };
        } catch ( e ) {
            vdCommon.error(e.message);
            return { "Code" : -1, "Msg" : e.message };
        }
    };

    /*
{ "fbFuncName" : "fn_cb_plant", "fbParams" : { "[Group].[Group ID]" : "SMPS1000003" } }
    */
    var fn_cb_plant = function(parsedParams){
        const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
        vdCommon.setLogLevel("Debug");

        try {
            // 파라미터 가져오기
            var fbVersion = parsedParams.fbVersion;

            // Location 을 찾는다.
            result = vdCommon.selectList(["&NSUILocationMFMtrlView", "Location.[Site Group3]"], [], "", "", "");

            var comboList = vdCommon.fn_makeCombo(result, {DimName : "Location", DimAttbName : "Location", isDisplayNameWithCode : true, Sort : "Name"
                                                                ,"includeOtherProperty" : "Location:Location:DisplayName:FromSite,Location:Site Group3:DisplayAlias:Factory"});
            vdCommon.debug("ComboData : " + JSON.stringify(comboList));

            vdCommon.programEnd();

            return comboList;
        } catch ( e ) {
            vdCommon.error(e.message);
            RuleOutputToUI = { Status : 'Error', Message : "Js Logic Error : " + e.message };
            return;
        }
    };

    /*
{"fbFuncName":"fn_filter_groupId","fbParams":
{"filters":{
    "[Version].[Version Name]":{"SelectedMembers":["CWV_MP"],"MemberFilter":"&CWVUI"},
    "[Item Material].[MSL1]":{"SelectedMembers":[],"MemberFilter":"&NSUIMtrlMSL1View"},
    "[Item Material].[MSL2]":{"SelectedMembers":[],"MemberFilter":"&NSUIMtrlMSL2View"},
    "[Item Material].[MSL3]":{"SelectedMembers":[],"MemberFilter":"&NSUIMtrlMSL3View"},
    "[Item Material].[MSL4]":{"SelectedMembers":[],"MemberFilter":"&NSUIMtrlMSL4View"},
    "[Item Material].[MSL5]":{"SelectedMembers":[],"MemberFilter":"&NSUIMtrlMSL5View"}
}
,"FilterMtrlItem" : "BN44-012"
}}
    */
    var fn_filter_groupId = function(parsedParams){
        const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
        vdCommon.setLogLevel("Debug");

		try {
		    var dims = ["[Group].[Group ID]"];
		    var meas = ["Measure.[Global Quota Group Mtrl Asn_Asn]"];

		    // where 절에 필터값을 적용
            var wheres = [];
            var fq = "";
            fq = vdUtil.fn_getFilterQuery2(parsedParams, "[Version].[Version Name]");  if ( fq != "" ) wheres.push(fq);
            fq = vdUtil.fn_getFilterQuery2(parsedParams, "[Item Material].[MSL1]");  if ( fq != "" ) wheres.push(fq);
            fq = vdUtil.fn_getFilterQuery2(parsedParams, "[Item Material].[MSL2]");  if ( fq != "" ) wheres.push(fq);
            fq = vdUtil.fn_getFilterQuery2(parsedParams, "[Item Material].[MSL3]");  if ( fq != "" ) wheres.push(fq);
            fq = vdUtil.fn_getFilterQuery2(parsedParams, "[Item Material].[MSL4]");  if ( fq != "" ) wheres.push(fq);
            fq = vdUtil.fn_getFilterQuery2(parsedParams, "[Item Material].[MSL5]");  if ( fq != "" ) wheres.push(fq);
            fq = vdUtil.fn_getFilterQuery2(parsedParams, "[Time].[Week]");  if ( fq != "" ) wheres.push(fq);

            //2025.9.24 조건 추가
            var itemMaterial = vdUtil.fn_getParam(parsedParams, "FilterMtrlItem");
            if ( itemMaterial != "" ) wheres.push("[Item Material].[Item Material]" + vdUtil.fn_filterStr(itemMaterial + "%"));

            var where = ( wheres.length == 0 ? "" : "where { " + wheres.join(", ") + " } ");

            var result = vdCommon.selectList(dims, meas, where, "", "limit 3000");
            //vdCommon.printCsData(result, 3);
            var comboList = vdCommon.fn_makeCombo(result, {DimName : "Group", DimAttbName : "Group ID", Sort : "DisplayName"});
            vdCommon.debug("ComboData : " + JSON.stringify(comboList.slice(0,3)));

            vdCommon.programEnd();

            return { "Code" : 0, "Msg" : "", "Rows" : comboList };
        } catch ( e ) {
            vdCommon.error(e.message);
            return { "Code" : -1, "Msg" : e.message };
        }
    };

   /*
- 파라미터
{ "fbFuncName" : "fn_merge"
    ,"fbParams" : { "commitType" : "1", "grid" : "Top"
                    ,"filters" : { "[Version].[Version Name]" : {"SelectedMembers" : ["202605_P_WI_01"], "MemberFilter" : ""} }
                    }
    ,"fbGridRows" : [
        { "rowstatus":"U","rowindex":"0","[Version].[Version Name]":"CWV_MP","[Item Material].[Item Material]":"BN44-01110C","[Sub Location].[Sub Location]":"G2902355","[Group].[Group ID]":"SMPS1000003" }
                  ] }

{ "fbFuncName" : "fn_merge"
    ,"fbParams" : { "commitType" : "1", "grid" : "Bottom"
                    ,"filters" : { "[Version].[Version Name]" : {"SelectedMembers" : ["202605_P_WI_01"], "MemberFilter" : ""} }
                    }
    ,"fbGridRows" : [
        { "rowstatus":"C","rowindex":"0","[Version].[Version Name]":"CWV_MP","[Item Material].[Item Material]":"BN44-01110C","[Sub Location].[Sub Location]":"G2902355","[Group].[Group ID]":"SMPS1000003","[Location].[Location]":"P401" }
                  ] }
    */
    var fn_merge = function(parsedParams){
        const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
        vdCommon.setLogLevel("Debug");

		try {
		    var fbVersionName = "[Version].[Version Name].[CWV_MP]";
		    var fbVersion = vdUtil.fn_getDimensionValue(vdUtil.fn_getFilterVersion(parsedParams));

            var name = vdCommon.selectResult('CurrentUser().Name');
            var userName = vdCommon.selectResult('CurrentUser().[User Name]');

		    if ( parsedParams.fbParams.grid == "Top" ) {
		        var where = 'where { Measure.[Global Quota Mtrl_Updated By] == "' + name + '" || Measure.[Global Quota Mtrl_Updated By] == "' + userName + '"}';

                if ( ( parsedParams.fbParams.commitType + "" ) == "0" ) {
                    // 전체이면 내가 수정한 것만 가져와서 배열을 생성
                    var result = vdCommon.selectList(["[Version].[Version Name].[" + fbVersion + "]"
                                                            ,"[Item Material].[Item Material]"
                                                            ,"[Sub Location].[Sub Location]"
                                                            ,"[Group].[Group ID]"]
                                                     ,["Measure.[Global Quota Mtrl_Status]"]
                                                     ,where, "", "");
                    for ( var i = 0; i < result.cs.rowCount; i++ ) {
                        parsedParams.fbGridRows.push({ "[Item Material].[Item Material]" : vdUtil.fn_getDimValue(result, i, "Item Material", "Item Material")
                                                        ,"[Sub Location].[Sub Location]" : vdUtil.fn_getDimValue(result, i, "Sub Location", "Sub Location")
                                                        ,"[Group].[Group ID]" : vdUtil.fn_getDimValue(result, i, "Group", "Group ID") });
                    }
                }

                for ( var i = 0; i < parsedParams.fbGridRows.length; i++ ) {
                    var row = parsedParams.fbGridRows[i];

                    var dimensions = [];
                    dimensions.push(fbVersionName);
                    dimensions.push(vdUtil.fn_qDim(row, "[Item Material].[Item Material]"));
                    dimensions.push(vdUtil.fn_qDim(row, "[Sub Location].[Sub Location]"));
                    dimensions.push(vdUtil.fn_qDim(row, "[Group].[Group ID]"));
                    var measures = [];
                    measures.push(vdUtil.fn_qMeaForMerge("Measure.[Global Quota Mtrl_Status]", fbVersion));
                    measures.push(vdUtil.fn_qMeaUpdateTime("Measure.[Global Quota Mtrl_Update Time]"));
                    measures.push(vdCommon.fn_mergeUser("Measure.[Global Quota Mtrl_Updated By]", fbVersion));
                    vdCommon.createMeasure(dimensions, measures);

                    // Global Quota Mtrl Sub_Group Name 변경
                    dimensions = [];
                    dimensions.push(fbVersionName);
                    dimensions.push(vdUtil.fn_qDim(row, "[Group].[Group ID]"));
                    measures = [];
                    measures.push(vdUtil.fn_qMeaForMerge("Measure.[Global Quota Mtrl Sub_Group Name]", fbVersion));
                    vdCommon.createMeasure(dimensions, measures);

                    dimensions = [];
                    dimensions.push(fbVersionName);
                    dimensions.push(vdUtil.fn_qDim(row, "[Item Material].[Item Material]"));
                    dimensions.push(vdUtil.fn_qDim(row, "[Sub Location].[Sub Location]"));
                    dimensions.push(vdUtil.fn_qDim(row, "[Group].[Group ID]"));
                    dimensions.push("&MPHroizon");
                    measures = [];
                    measures.push(vdUtil.fn_qMeaForMerge("Measure.[Global Quota Mtrl W_Portion]", fbVersion));
                    vdCommon.createMeasure(dimensions, measures);
                }
            } else if ( parsedParams.fbParams.grid == "Bottom" ) {
		        var where = 'where { Measure.[Plant Quota Mtrl_Updated By] == "' + name + '" || Measure.[Plant Quota Mtrl_Updated By] == "' + userName + '"}';

                if ( ( parsedParams.fbParams.commitType + "" ) == "0" ) {
                    // 전체이면 내가 수정한 것만 가져와서 배열을 생성
                    var result = vdCommon.selectList(["[Version].[Version Name].[" + fbVersion + "]"
                                                            ,"[Item Material].[Item Material]"
                                                            ,"[Sub Location].[Sub Location]"
                                                            ,"[Group].[Group ID]"
                                                            ,"[Location].[Location]"]
                                                     ,["Measure.[Plant Quota Mtrl_Updated By]"]
                                                     ,where, "", "");
                    for ( var i = 0; i < result.cs.rowCount; i++ ) {
                        parsedParams.fbGridRows.push({ "[Item Material].[Item Material]" : vdUtil.fn_getDimValue(result, i, "Item Material", "Item Material")
                                                        ,"[Sub Location].[Sub Location]" : vdUtil.fn_getDimValue(result, i, "Sub Location", "Sub Location")
                                                        ,"[Group].[Group ID]" : vdUtil.fn_getDimValue(result, i, "Group", "Group ID")
                                                        ,"[Location].[Location]" : vdUtil.fn_getDimValue(result, i, "Location", "Location") });
                    }
                }

                for ( var i = 0; i < parsedParams.fbGridRows.length; i++ ) {
                    var row = parsedParams.fbGridRows[i];

                    var dimensions = [];
                    dimensions.push(fbVersionName);
                    dimensions.push(vdUtil.fn_qDim(row, "[Item Material].[Item Material]"));
                    dimensions.push(vdUtil.fn_qDim(row, "[Sub Location].[Sub Location]"));
                    dimensions.push(vdUtil.fn_qDim(row, "[Group].[Group ID]"));
                    dimensions.push(vdUtil.fn_qDim(row, "[Location].[Location]"));
                    var measures = [];
                    measures.push(vdUtil.fn_qMeaUpdateTime("Measure.[Plant Quota Mtrl_Update Time]"));
                    measures.push(vdCommon.fn_mergeUser("Measure.[Plant Quota Mtrl_Updated By]", fbVersion));
                    vdCommon.createMeasure(dimensions, measures);

                    // 배치에서 데이타 생성을 위한 구분자로 Flag 를 세팅한다.
                    dimensions = [];
                    dimensions.push(fbVersionName);
                    dimensions.push(vdUtil.fn_qDim(row, "[Group].[Group ID]"));
                    measures = [];
                    measures.push(vdUtil.fn_qMeaForMerge("Measure.[Global Quota Mtrl Sub_Plant Mgmt Flag]", fbVersion));
                    vdCommon.createMeasure(dimensions, measures);

                    // Week 데이타 생성
                    dimensions = [];
                    dimensions.push(fbVersionName);
                    dimensions.push(vdUtil.fn_qDim(row, "[Item Material].[Item Material]"));
                    dimensions.push(vdUtil.fn_qDim(row, "[Sub Location].[Sub Location]"));
                    dimensions.push(vdUtil.fn_qDim(row, "[Group].[Group ID]"));
                    dimensions.push(vdUtil.fn_qDim(row, "[Location].[Location]"));
                    dimensions.push("&MPHroizon");
                    measures = [];
                    measures.push(vdUtil.fn_qMeaForMerge("Measure.[Plant Quota Mtrl W_Portion]", fbVersion));
                    vdCommon.createMeasure(dimensions, measures);
                }
            }

            vdCommon.programEnd();

            return { "Code" : 0, "Msg" : "It was saved successfully." };
        } catch ( e ) {
            vdCommon.error(e.message);
            return { "Code" : -1, "Msg" : e.message };
        }
    };


/************************************************* util logic *************************************************/

/************************************************* Mapping logic **********************************************/
    // Mapping 함수 정의, 마지막에 선언을 해야 함수를 정상적으로 인식함
    const functionMap = {
        "fn_saveTop" : fn_saveTop
        ,"fn_saveBottom" : fn_saveBottom
        ,"fn_cb_plant" : fn_cb_plant
        ,"fn_filter_groupId" : fn_filter_groupId
        ,"fn_merge" : fn_merge
    };

    return {
        fn_loadFunction : fn_loadFunction
    };
});

/************************************** o9.NSCM.JSEWQuotaMtrl **************************************
25.11.27 : 수정일자, 수정자 기록 남기도록 수정
25.12.02 : fn_cb_plant 에서 &NSUILocationPlant 로만 가져오도록 수정
26.02.06 : Measure.[Global Quota Mtrl Sub_Group Name] 수정은 REQ 일때만에서 무조건으로 변경
26.03.04 : fn_merge 추가
************************************** o9.NSCM.JSEWQuotaMtrl **************************************/