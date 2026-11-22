define('o9.NSCM.JSEWBuildAheadMaster', ['o9/data/query', 'o9/data/cellset', 'o9.NSCM.commonLib'], function () {

/**************************************************************************************
    프로그램명  : o9.NSCM.JSEWBuildAheadMaster
    화면명     : Build Ahead Master
    화면 개발자 : 박승하 프로
    API 개발자 : sungmin0.lim
    최초생성   : 2025.08.4
**************************************************************************************/

	const programName = "o9.NSCM.JSEWBuildAheadMaster";
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
- 추가 테스트
{ "fbFuncName" : "fn_save", "fbParams" : { "[Version].[Version Name]" : "CWV_MP" },
  "fbGridRows" : [
{ "rowstatus":"C","[Group].[Group ID]":"","Measure.[Build Ahead Group_Category]":"Item Group","Measure.[Build Ahead Group_From Site]":"P306","Measure.[Build Ahead Group_Shipment Type]":"INDIR","Measure.[Build Ahead Group_To Site]":"S356","Measure.[Build Ahead Group_Product Group]":"MONITOR","Measure.[Build Ahead Group_Definition]":"All","Measure.[Build Ahead Group_Project]":"All","Measure.[Build Ahead Group_MKT Name]":"All","Measure.[Build Ahead Group_Inch]":"All","Measure.[Build Ahead Group_Year]":"All","Measure.[Build Ahead Group_Item]":"All","Measure.[Build Ahead Group_Description]":"A_B_C_D","Measure.[Build Ahead Group_Valid]":"Y","Measure.[Build Ahead Group_ALL]":"ALL_1","Measure.[Build Ahead Group W_Period]" : ["202508^5","202509^9","202510^10"] },
{ "rowstatus":"C","[Group].[Group ID]":"","Measure.[Build Ahead Group_Category]":"Item Group","Measure.[Build Ahead Group_From Site]":"P306","Measure.[Build Ahead Group_Shipment Type]":"INDIR","Measure.[Build Ahead Group_To Site]":"All","Measure.[Build Ahead Group_Product Group]":"All","Measure.[Build Ahead Group_Definition]":"All","Measure.[Build Ahead Group_Project]":"All","Measure.[Build Ahead Group_MKT Name]":"All","Measure.[Build Ahead Group_Inch]":"All","Measure.[Build Ahead Group_Year]":"2023","Measure.[Build Ahead Group_Item]":"QN%","Measure.[Build Ahead Group_Description]":"A_B_C_D","Measure.[Build Ahead Group_Valid]":"N","Measure.[Build Ahead Group_ALL]":"ALL_2","Measure.[Build Ahead Group W_Period]" : ["202508^5","202509^9","202510^10"] }
                  ] }

{ "fbFuncName" : "fn_save", "fbParams" : { "[Version].[Version Name]" : "CWV_MP" },
  "fbGridRows" : [
{ "rowstatus":"C","[Group].[Group ID]":"","Measure.[Build Ahead Group_Category]":"Item Group","Measure.[Build Ahead Group_From Site]":"P551","Measure.[Build Ahead Group_Shipment Type]":"INDIR","Measure.[Build Ahead Group_To Site]":"L5S0","Measure.[Build Ahead Group_Product Group]":"MONITOR^AV","Measure.[Build Ahead Group_Definition]":"All","Measure.[Build Ahead Group_Project]":"All","Measure.[Build Ahead Group_MKT Name]":"All","Measure.[Build Ahead Group_Inch]":"All","Measure.[Build Ahead Group_Year]":"All","Measure.[Build Ahead Group_Item]":"LS22D304GAWXXL","Measure.[Build Ahead Group_Description]":"A_B_C_D","Measure.[Build Ahead Group_Valid]":"Y","Measure.[Build Ahead Group_ALL]":"ALL_1","Measure.[Build Ahead Group W_Period]" : ["202508^5","202509^9","202510^10"] }
                  ] }


- 수정 테스트
{ "fbFuncName" : "fn_save", "fbParams" : { "[Version].[Version Name]" : "CWV_MP" },
  "fbGridRows" : [
{ "rowstatus":"U","[Group].[Group ID]":"BAL_0000","Measure.[Build Ahead Group_Category]":"Item Group","Measure.[Build Ahead Group_From Site]":"P306","Measure.[Build Ahead Group_Shipment Type]":"INDIR","Measure.[Build Ahead Group_To Site]":"P306","Measure.[Build Ahead Group_Product Group]":"TV","Measure.[Build Ahead Group_Definition]":"All","Measure.[Build Ahead Group_Project]":"59SCA","Measure.[Build Ahead Group_MKT Name]":"Micro","Measure.[Build Ahead Group_Inch]":"65","Measure.[Build Ahead Group_Year]":"2023","Measure.[Build Ahead Group_Item]":"QN6565C%","Measure.[Build Ahead Group_Description]":"A_B_C_D","Measure.[Build Ahead Group_Valid]":"","Measure.[Build Ahead Group_ALL]":"","Measure.[Build Ahead Group W_Period]" : ["202508^5","202509^9","202510^10"] }
                  ] }

- 삭제 테스트
{ "fbFuncName" : "fn_save", "fbParams" : { "[Version].[Version Name]" : "CWV_MP" },
  "fbGridRows" : [
{ "rowstatus":"D","[Group].[Group ID]":"BAL_00003","Measure.[Build Ahead Group_Category]":"Item Group","Measure.[Build Ahead Group_From Site]":"P306","Measure.[Build Ahead Group_Shipment Type]":"INDIR","Measure.[Build Ahead Group_To Site]":"P306","Measure.[Build Ahead Group_Product Group]":"TV","Measure.[Build Ahead Group_Definition]":"All","Measure.[Build Ahead Group_Project]":"59SCA","Measure.[Build Ahead Group_MKT Name]":"Micro","Measure.[Build Ahead Group_Inch]":"65","Measure.[Build Ahead Group_Year]":"2023","Measure.[Build Ahead Group_Item]":"QN6565C%","Measure.[Build Ahead Group_Description]":"A_B_C_D","Measure.[Build Ahead Group_Valid]":"","Measure.[Build Ahead Group_ALL]":"","Measure.[Build Ahead Group W_Period]" : ["202508^5","202509^9","202510^10"] }
                  ] }
    */
    var fn_save = function(parsedParams){
        const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
        vdCommon.setLogLevel("Debug");

		try {
		    var fbVersion = parsedParams.fbParams["[Version].[Version Name]"];
            for ( var i = 0; i < parsedParams.fbGridRows.length; i++ ) {
                var row = parsedParams.fbGridRows[i];
                var rowstatus = row["rowstatus"];

                if ( rowstatus == "C" ) {
                    // Max 값을 구한다.
                    var result = vdCommon.selectList(["[Version].[Version Name].[" + fbVersion + "]",
                                                        "[Group].[Group ID].filter(#.Name startswith([BAL_]))"],
                                                    ["Measure.[Build Ahead Group_From Site]"],
                                                    "",
                                                    "orderby [Group].[Group ID].Name desc",
                                                    "limit 1");
                    var groupId = "BAL_00001";
                    if ( result.cs.rowCount > 0 ) {
                        groupId = "BAL_" + vdUtil.fn_lpad((parseInt(result.cs.row(0).cell(result.cs.memberColumnIndex("Group", "Group ID")).Name.substr(4)) + 1) + "", 5, "0");
                    }
                    // Dimension 을  추가한다.
                    if ( !vdCommon.existDimension(['[Group].[Group Type].[BAL]','[Group].[Group ID].[' + groupId + ']']) ) {
                        vdCommon.createDimension(['[Group].[Group Type]','[Group].[Group Name]','[Group].[Group ID]','[Group].[All Group]'], ["BAL", groupId, groupId, 'All']);
                    }

                    var dimensions = [];
                    dimensions.push("[Version].[Version Name].[" + fbVersion + "]");
                    dimensions.push("[Group].[Group ID].[" + groupId + "]");

                    var measures = [];
                    measures.push(vdUtil.fn_qMeaStr(row, "Measure.[Build Ahead Group_Category]"));
                    measures.push(vdUtil.fn_qMeaStr(row, "Measure.[Build Ahead Group_From Site]"));
                    measures.push(vdUtil.fn_qMeaStr(row, "Measure.[Build Ahead Group_Shipment Type]"));
                    measures.push(vdUtil.fn_qMeaStr(row, "Measure.[Build Ahead Group_To Site]"));
                    measures.push(vdUtil.fn_qMeaStr(row, "Measure.[Build Ahead Group_Product Group]"));
                    measures.push(vdUtil.fn_qMeaStr(row, "Measure.[Build Ahead Group_Definition]"));
                    measures.push(vdUtil.fn_qMeaStr(row, "Measure.[Build Ahead Group_Project]"));
                    measures.push(vdUtil.fn_qMeaStr(row, "Measure.[Build Ahead Group_MKT Name]"));
                    measures.push(vdUtil.fn_qMeaStr(row, "Measure.[Build Ahead Group_Inch]"));
                    measures.push(vdUtil.fn_qMeaStr(row, "Measure.[Build Ahead Group_Year]"));
                    measures.push(vdUtil.fn_qMeaStr(row, "Measure.[Build Ahead Group_Item]"));
                    measures.push(vdUtil.fn_qMeaStr(row, "Measure.[Build Ahead Group_Description]"));
                    measures.push(vdUtil.fn_qMeaStr(row, "Measure.[Build Ahead Group_Valid]"));
                    measures.push(vdUtil.fn_qMeaStr(row, "Measure.[Build Ahead Group_ALL]"));
                    measures.push(vdUtil.fn_qMeaUpdateUserName("Measure.[Build Ahead Group_Created By]"));
                    measures.push(vdUtil.fn_qMeaUpdateTime("Measure.[Build Ahead Group_Creation Time]"));

                    vdCommon.createMeasure(dimensions, measures);

                    if ( row["Measure.[Build Ahead Group_ALL]"] == "Default" ) {
                        // Week 데이타 생성
                        vdCommon.createMeasure(["[Version].[Version Name].[" + fbVersion + "]",
                                                    "[Group].[Group ID].[" + groupId + "]",
                                                    "&MPHorizon"],
                                                ['Measure.[Build Ahead Group W_Period] = 0;']);

                        var weekList = row["Measure.[Build Ahead Group W_Period]"];
                        var queryStr = "";
                        for ( var m = 0; m < weekList.length; m++ ) {
                            var subDimensions = [];
                            subDimensions.push("[Version].[Version Name].[" + fbVersion + "]");
                            subDimensions.push("[Group].[Group ID].[" + groupId + "]");
                            subDimensions.push("[Time].[Week].[" + weekList[m].split("^")[0] + "]");

                            var subMeasures = [];
                            subMeasures.push(vdUtil.fn_qMeaNotStr(null, "Measure.[Build Ahead Group W_Period]", vdUtil.fn_undefinedNull(weekList[m].split("^")[1])));

                            queryStr += vdCommon.updateMeasureQuery(subDimensions, subMeasures);
                        }
                        if ( queryStr != "" ) {
                            vdCommon.executeQuery("Build Ahead Group W", queryStr);
                        }
                    } else {
                        var subDimensions = [];
                        subDimensions.push("[Version].[Version Name].[" + fbVersion + "]");
                        subDimensions.push("[Group].[Group ID].[" + groupId + "]");
                        subDimensions.push("&MPHorizon");

                        var subMeasures = [];
                        subMeasures.push(vdUtil.fn_qMeaNotStr(null, "Measure.[Build Ahead Group W_Period]", row["Measure.[Build Ahead Group_ALL]"].substring(4,5)));
                        vdCommon.createMeasure(subDimensions, subMeasures);
                    }

                    // 필터용 데이타 생성
                    var fbLocation = row["Measure.[Build Ahead Group_From Site]"];
                    var fbSubLocation = row["Measure.[Build Ahead Group_To Site]"];
                    var fbProductGroup = row["Measure.[Build Ahead Group_Product Group]"];
                    var fbDefinition = row["Measure.[Build Ahead Group_Definition]"];
                    var fbProject = row["Measure.[Build Ahead Group_Project]"];
                    var fbMktName = row["Measure.[Build Ahead Group_MKT Name]"];
                    var fbInch = row["Measure.[Build Ahead Group_Inch]"];
                    var fbYear = row["Measure.[Build Ahead Group_Year]"];
                    var fbItem = row["Measure.[Build Ahead Group_Item]"];

                    if ( fbSubLocation == "All" ) {
                        var subLocations = [];
                        var result = vdCommon.selectList(["[Version].[Version Name].[" + fbVersion + "]",
                                                            "Location.[Location].[" + fbLocation + "]",
                                                            "[Sub Location].[Sub Location]"],
                                                            ["Measure.[BOD Item_BOD LT]",
                                                                "Measure.[Dummy]"],
                                                            "",
                                                            "",
                                                            "");
                        for ( var i = 0; i < result.cs.rowCount; i++ ) {
                            subLocations.push(vdUtil.fn_getString(result.cs.row(i).cell(result.cs.memberColumnIndex("Sub Location", "Sub Location")).Name));
                        }

                        vdCommon.createMeasure(["[Version].[Version Name].[" + fbVersion + "]",
                                                    "Location.[Location].[" + fbLocation + "]",
                                                    "[Sub Location].[Sub Location]" + vdUtil.fn_filterStr(subLocations),
                                                    ( fbProductGroup == "All" ? 'Item.[Product Group].filter(#.Name in {"TV","MONITOR","AV"})' : "Item.[Product Group]" + vdUtil.fn_filterStr(fbProductGroup.split("^")) ),
                                                    "[Group].[Group ID].[" + groupId + "]"],
                                                ['Measure.[Build Ahead Asn_Asn] = 1;']);
                    } else {
                        vdCommon.createMeasure(["[Version].[Version Name].[" + fbVersion + "]",
                                                    "Location.[Location].[" + fbLocation + "]",
                                                    "[Sub Location].[Sub Location].[" + fbSubLocation + "]",
                                                    ( fbProductGroup == "All" ? 'Item.[Product Group].filter(#.Name in {"TV","MONITOR","AV"})' : "Item.[Product Group]" + vdUtil.fn_filterStr(fbProductGroup.split("^")) ),
                                                    "[Group].[Group ID].[" + groupId + "]"],
                                                ['Measure.[Build Ahead Asn_Asn] = 1;']);
                    }

                    // 파이썬 실행
                    // Item 의 경우 데이타가 0건이면 scope 반영시 오류가 발생을 하여 갯수를 한번 체크하여 실행을 해준다.
                    var itemDimensions = [];
                    if ( fbProductGroup != "All" )
                        itemDimensions.push('Item.[Product Group]' + vdUtil.fn_filterStr(fbProductGroup.split("^")));
                    if ( fbDefinition != "All" )
                        itemDimensions.push('Item.[Definition]' + vdUtil.fn_filterStr(fbDefinition.split("^")));
                    if ( fbProject != "All" )
                        itemDimensions.push('Item.[Project]' + vdUtil.fn_filterStr(fbProject.split("^")));
                    if ( fbMktName != "All" )
                        itemDimensions.push('Item.[Marketing Name]' + vdUtil.fn_filterStr(fbMktName.split("^")));
                    if ( fbInch != "All" )
                        itemDimensions.push('Item.[Inch]' + vdUtil.fn_filterStr(fbInch.split("^")));
                    if ( fbYear != "All" )
                        itemDimensions.push('Item.[Year]' + vdUtil.fn_filterStr(fbYear.split("^")));
                    if ( fbItem != "All" )
                        itemDimensions.push('Item.[Item]' + vdUtil.fn_filterStr(fbItem.split("^")));
                    var seq = vdCommon.selectListCount(itemDimensions, [], "");
                    if ( seq > 0 ) {
                        var execQuery = 'EXEC plugin instance [PY_UI_BuildAheadMaster] ' +
                                        'for measures {[Build Ahead Group Ecp_Flag]} ' +
                                        'using scope ( &CWVUI * ' +
                                            ( fbProductGroup != "All" ? 'Item.[Product Group]' + vdUtil.fn_filterStr(fbProductGroup.split("^")) + ' * ' : "" ) +
                                            ( fbDefinition != "All" ? 'Item.[Definition]' + vdUtil.fn_filterStr(fbDefinition.split("^")) + ' * ' : "" ) +
                                            ( fbProject != "All" ? 'Item.[Project]' + vdUtil.fn_filterStr(fbProject.split("^")) + ' * ' : "" ) +
                                            ( fbMktName != "All" ? 'Item.[Marketing Name]' + vdUtil.fn_filterStr(fbMktName.split("^")) + ' * ' : "" ) +
                                            ( fbInch != "All" ? 'Item.[Inch]' + vdUtil.fn_filterStr(fbInch.split("^")) + ' * ' : "" ) +
                                            ( fbYear != "All" ? 'Item.[Year]' + vdUtil.fn_filterStr(fbYear.split("^")) + ' * ' : "" ) +
                                            ( fbItem != "All" ? 'Item.[Item]' + vdUtil.fn_filterStr(fbItem.split("^")) + ' * ' : "" ) +
                                            '[Group].[Group ID].[' + groupId + '] * ' +
                                            '[Location].[Location].[' + fbLocation + '] * ' +
                                            '[Sub Location].[Sub Location]' + ( fbSubLocation != "All" ? vdUtil.fn_filterStr(fbSubLocation) : "" ) + ' ) ' +
                                        'using arguments {(RunID, "Run_1"),(ExecutionMode, "MediumWeight"), (MaxSliceTableCells, 200000000), (MaxConcurrency, 1 )};'
                        vdCommon.executeQuery("Py Run", execQuery);
                    }
                } else if ( rowstatus == "U" ) {
                    var dimensions = [];
                    dimensions.push("[Version].[Version Name].[" + fbVersion + "]");
                    dimensions.push("[Group].[Group ID].[" + row["[Group].[Group ID]"] + "]");

                    var measures = [];
                    measures.push(vdUtil.fn_qMeaStr(row, "Measure.[Build Ahead Group_Valid]"));
                    measures.push(vdUtil.fn_qMeaStr(row, "Measure.[Build Ahead Group_ALL]"));
                    measures.push(vdUtil.fn_qMeaUpdateUserName("Measure.[Build Ahead Group_Updated By]"));
                    measures.push(vdUtil.fn_qMeaUpdateTime("Measure.[Build Ahead Group_Update Time]"));

                    vdCommon.updateBlockMeasure(dimensions, measures);

                    if ( row["Measure.[Build Ahead Group_ALL]"] == "Default" ) {
                        // 주차 수정
                        var weekList = row["Measure.[Build Ahead Group W_Period]"];
                        var queryStr = "";
                        for ( var m = 0; m < weekList.length; m++ ) {
                            var subDimensions = [];
                            subDimensions.push("[Version].[Version Name].[" + fbVersion + "]");
                            subDimensions.push("[Group].[Group ID].[" + row["[Group].[Group ID]"] + "]");
                            subDimensions.push("[Time].[Week].[" + weekList[m].split("^")[0] + "]");

                            var subMeasures = [];
                            subMeasures.push(vdUtil.fn_qMeaNotStr(null, "Measure.[Build Ahead Group W_Period]", vdUtil.fn_undefinedNull(weekList[m].split("^")[1])));

                            queryStr += vdCommon.updateMeasureQuery(subDimensions, subMeasures);
                        }
                        if ( queryStr != "" ) {
                            vdCommon.executeQuery("Build Ahead Group W", queryStr);
                        }
                    } else {
                        var subDimensions = [];
                        subDimensions.push("[Version].[Version Name].[" + fbVersion + "]");
                        subDimensions.push("[Group].[Group ID].[" + row["[Group].[Group ID]"] + "]");
                        subDimensions.push("&MPHorizon");

                        var subMeasures = [];
                        subMeasures.push(vdUtil.fn_qMeaNotStr(null, "Measure.[Build Ahead Group W_Period]", row["Measure.[Build Ahead Group_ALL]"].substring(4,5)));
                        vdCommon.updateMeasure(subDimensions, subMeasures);
                    }
                } else if ( rowstatus == "D" ) {
                    var where = [];
                    where.push("[Version].[Version Name].[" + fbVersion + "]");
                    where.push("[Group].[Group ID].[" + row["[Group].[Group ID]"] + "]");

                    vdCommon.deleteMeasure(where, "Build Ahead Group");
                    vdCommon.deleteMeasure(where, "Build Ahead Group W");
                    vdCommon.deleteMeasure(where, "Build Ahead Group Ecp");
                    vdCommon.deleteMeasure(where, "Build Ahead Asn");
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
- 시나리오 찾기
    select ([Version].[Version Name].filter(#.[Plan Type] == "What-If"));
- 데이타 삭제
    DELETE DATA FOR MODEL [Build Ahead Group] where { &CWVUI, [Group].[Group ID].filter(#.Name in {"BAL_00004","BAL_00005","BAL_00006","BAL_00332"}) };
    DELETE DATA FOR MODEL [Build Ahead Group W] where { &CWVUI, [Group].[Group ID].filter(#.Name in {"BAL_00004","BAL_00005","BAL_00006","BAL_00332"}) };
    DELETE DATA FOR MODEL [Build Ahead Group Ecp] where { &CWVUI, [Group].[Group ID].filter(#.Name in {"BAL_00004","BAL_00005","BAL_00006","BAL_00332"}) };
    DELETE DATA FOR MODEL [Build Ahead Asn] where { &CWVUI, [Group].[Group ID].filter(#.Name in {"BAL_00004","BAL_00005","BAL_00006","BAL_00332"}) };

    cartesian scope : ( [Version].[Version Name].[202605_P_WI_01] * [Group].[Group ID].[BAL_00003] );
        Measure.[Build Ahead Group_Updated By] = "sungmin0.lim@partner.samsung.com";
    end scope;

- 파라미터
{ "fbFuncName" : "fn_merge"
    ,"fbParams" : { "commitType" : "1"
                    ,"filters" : { "[Version].[Version Name]" : {"SelectedMembers" : ["202605_P_WI_01"], "MemberFilter" : ""} }
                   }
    ,"fbGridRows" : [
        { "rowstatus":"C","[Group].[Group ID]":"BAL_00004" },
        { "rowstatus":"C","[Group].[Group ID]":"BAL_00005" },
        { "rowstatus":"C","[Group].[Group ID]":"BAL_00006" },
        { "rowstatus":"C","[Group].[Group ID]":"BAL_00332" }
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

		    if ( ( parsedParams.fbParams.commitType + "" ) == "0" ) {
                // 전체이면 내가 수정한 것만 가져와서 배열을 생성
		        var name = vdCommon.selectResult('CurrentUser().Name');
                var userName = vdCommon.selectResult('CurrentUser().[User Name]');

                var where = 'where { Measure.[Build Ahead Group_Updated By] == "' + name + '" || Measure.[Build Ahead Group_Updated By] == "' + userName + '"}';
                var result = vdCommon.selectList(["[Version].[Version Name].[" + fbVersion + "]"
                                                        ,"[Group].[Group ID]"]
                                                 ,["Measure.[Build Ahead Group_From Site]"]
                                                 ,where, "", "");
                for ( var i = 0; i < result.cs.rowCount; i++ ) {
                    parsedParams.fbGridRows.push({ "[Group].[Group ID]" : vdUtil.fn_getDimValue(result, i, "Group", "Group ID") });
                }
            }

            var groupIds = [];
            for ( var i = 0; i < parsedParams.fbGridRows.length; i++ ) {
                var row = parsedParams.fbGridRows[i];

                groupIds.push(row["[Group].[Group ID]"]);
            }

            // Build Ahead Group : Merge
            var dimensions = [];
            dimensions.push("[Version].[Version Name].[CWV_MP]");
            dimensions.push("[Group].[Group ID]" + vdUtil.fn_filterStr(groupIds));
            var measures = [];
            measures.push(vdUtil.fn_qMeaForMerge("Measure.[Build Ahead Group_ALL]", fbVersion));
            measures.push(vdUtil.fn_qMeaForMerge("Measure.[Build Ahead Group_Category]", fbVersion));
            measures.push(vdUtil.fn_qMeaForMerge("Measure.[Build Ahead Group_Definition]", fbVersion));
            measures.push(vdUtil.fn_qMeaForMerge("Measure.[Build Ahead Group_Description]", fbVersion));
            measures.push(vdUtil.fn_qMeaForMerge("Measure.[Build Ahead Group_From Site]", fbVersion));
            measures.push(vdUtil.fn_qMeaForMerge("Measure.[Build Ahead Group_Inch]", fbVersion));
            measures.push(vdUtil.fn_qMeaForMerge("Measure.[Build Ahead Group_Item]", fbVersion));
            measures.push(vdUtil.fn_qMeaForMerge("Measure.[Build Ahead Group_MKT Name]", fbVersion));
            measures.push(vdUtil.fn_qMeaForMerge("Measure.[Build Ahead Group_Product Group]", fbVersion));
            measures.push(vdUtil.fn_qMeaForMerge("Measure.[Build Ahead Group_Project]", fbVersion));
            measures.push(vdUtil.fn_qMeaForMerge("Measure.[Build Ahead Group_Shipment Type]", fbVersion));
            measures.push(vdUtil.fn_qMeaForMerge("Measure.[Build Ahead Group_To Site]", fbVersion));
            measures.push(vdUtil.fn_qMeaForMerge("Measure.[Build Ahead Group_Valid]", fbVersion));
            measures.push(vdUtil.fn_qMeaForMerge("Measure.[Build Ahead Group_Year]", fbVersion));
            measures.push(vdUtil.fn_qMeaUpdateTime("Measure.[Build Ahead Group_Update Time]"));
            measures.push(vdCommon.fn_mergeUser("Measure.[Build Ahead Group_Updated By]", fbVersion));
            vdCommon.createMeasure(dimensions, measures);

            // Build Ahead Group W : Merge
            dimensions = [];
            dimensions.push("[Version].[Version Name].[CWV_MP]");
            dimensions.push("[Group].[Group ID]" + vdUtil.fn_filterStr(groupIds));
            dimensions.push("&MPHorizon");
            measures = [];
            measures.push(vdUtil.fn_qMeaForMerge("Measure.[Build Ahead Group W_Period]", fbVersion));
            vdCommon.createMeasure(dimensions, measures);

            // Build Ahead Group Ecp : Merge
            dimensions = [];
            dimensions.push("[Version].[Version Name].[CWV_MP]");
            dimensions.push("[Group].[Group ID]" + vdUtil.fn_filterStr(groupIds));
            dimensions.push("[Item].[Item]");
            measures = [];
            measures.push(vdUtil.fn_qMeaForMerge("Measure.[Build Ahead Group Ecp_Flag]", fbVersion));
            vdCommon.createMeasure(dimensions, measures);

            // Build Ahead Asn : Merge
            dimensions = [];
            dimensions.push("[Version].[Version Name].[CWV_MP]");
            dimensions.push("[Location].[Location]");
            dimensions.push("[Group].[Group ID]" + vdUtil.fn_filterStr(groupIds));
            dimensions.push("[Item].[Product Group]");
            dimensions.push("[Sub Location].[Sub Location]");
            measures = [];
            measures.push(vdUtil.fn_qMeaForMerge("Measure.[Build Ahead Asn_Asn]", fbVersion));
            vdCommon.createMeasure(dimensions, measures);

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
        "fn_save" : fn_save
        ,"fn_merge" : fn_merge
    };

    return {
        fn_loadFunction : fn_loadFunction
    };
});

/**************************** o9.NSCM.JSEWBuildAheadMaster ****************************
2025-11-19 : MG 를 "Build Ahead Item" 에서 "Build Ahead Group" 로 변경
2025-12-10 : PY_UI_BuildAheadMaster 호출시 파라미터를 배열 형태로 변경해서 호출
2026-01-26 : Group Dimension 생성시 "All Group" 추가
2026-02-05 : Item 도 ^로 멀티등록이 가능하게 수정
2026-02-26 : merge 기능 추가
**************************** o9.NSCM.JSEWBuildAheadMaster ****************************/