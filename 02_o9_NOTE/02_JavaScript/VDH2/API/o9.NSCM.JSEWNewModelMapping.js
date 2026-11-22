define('o9.NSCM.JSEWNewModelMapping', ['o9/data/query', 'o9/data/cellset', 'o9.NSCM.commonLib'], function () {

/**************************************************************************************
    프로그램명  : o9.NSCM.JSEWSNewModelMapping
    화면명     : New Model Mapping
    화면 개발자 : 정형철 프로
    API 개발자 : sungmin0.lim
    최초생성   : 2025.07.1
**************************************************************************************/

	const programName = "o9.NSCM.JSEWNewModelMapping";
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
    // { "fbFuncName" : "fn_cb_newModelMapBuyer", "fbParams" : { "[Item Material].[Item Material]" : "1107-002224" } }
    var fn_cb_newModelMapBuyer = function(parsedParams){
        const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
        vdCommon.setLogLevel("Debug");

		try {
		    var comboList = [];

		    // Item Material 의 MSL3 을 가져온다.
		    var where = "where { [Item Material].[Item Material]" + vdUtil.fn_filterStr(parsedParams.fbParams["[Item Material].[Item Material]"]) + " } ";
		    var result = vdCommon.selectList(["[Item Material].[MSL3]"], [], where, "", "limit 1");
            if ( result.cs.rowCount > 0 ) {
                var msl3 = result.cs.row(0).cell(result.cs.memberColumnIndex("Item Material", "MSL3")).Name;

                // MSL3 의 Mtrl Master MSL3_Buyer Group 을 가져온다.
                result = vdCommon.selectList(["[Item Material].[MSL3]" + vdUtil.fn_filterStr(msl3)], ["Measure.[Mtrl Master MSL3_Buyer Group]"], "where { &CWVUI } ", "", "");
                if ( result.cs.rowCount > 0 ) {
                    var buyerGroup = result.cs.row(0).cell(result.cs.measureColumnIndex("Mtrl Master MSL3_Buyer Group"));

                    var where = "where { &CWVUI, [Category].[Category]" + vdUtil.fn_filterStr(buyerGroup) + " } ";
                    result = vdCommon.selectList(["[Item].[Buyer]"], ["Measure.[Buyer Group Mapping_Buyer Group]"], where, "", "");
                    comboList = vdCommon.fn_makeCombo(result, {MeasureName : "Buyer Group Mapping_Buyer Group", Sort : "DisplayName", "existAll" : true});
                    vdCommon.debug("ComboData : " + JSON.stringify(comboList.slice(0,3)));
                } else {
                    comboList = vdCommon.fn_makeCombo(null, {ComboCodes : ["All"], ComboValues : ["All"]});
                }
            }

            vdCommon.programEnd();

            return { "Code" : 0, "Msg" : "", "Rows" : comboList };
        } catch ( e ) {
            vdCommon.error(e.message);
            return { "Code" : -1, "Msg" : e.message };
        }
    };

    /* { "fbFuncName" : "fn_save", "fbParams" : { "[Version].[Version Name]" : "CWV_MP" },
           "fbGridRows" : [{ "rowStatus" : "C", "[Item].[Item]" : "All", "[Project].[Project]" : "S95DA", "[Item Material].[Item Material]" : "1105-003132", "[Rule].[Rule No]" : "0003",
                                "[Inch].[Inch]" : "55", "[Buyer Group].[Buyer Group]" : "EUROPE", "[Basic Name].[Basic Name]" : "QS-F55S95D/EU",
                                "Measure.[New Model Map_BOM Type]" : "SOP Assy", "Measure.[New Model Map_Base Qty]" : "1", "Measure.[New Model Map_User Spec]" : "Spec1"}
                           ,{ "rowStatus" : "C", "[Item].[Item]" : "All", "[Project].[Project]" : "S95DA", "[Item Material].[Item Material]" : "1105-003132", "[Rule].[Rule No]" : "0003",
                                "[Inch].[Inch]" : "65", "[Buyer Group].[Buyer Group]" : "EUROPE", "[Basic Name].[Basic Name]" : "QS-F55S95D/EU",
                                "Measure.[New Model Map_BOM Type]" : "SET", "Measure.[New Model Map_Base Qty]" : "2", "Measure.[New Model Map_User Spec]" : "Spec2"}
                           ,{ "rowStatus" : "C", "[Item].[Item]" : "All", "[Project].[Project]" : "S95DA", "[Item Material].[Item Material]" : "1105-003132", "[Rule].[Rule No]" : "0004",
                                "[Inch].[Inch]" : "55", "[Buyer Group].[Buyer Group]" : "EUROPE", "[Basic Name].[Basic Name]" : "QS-F55S95D/EU",
                                "Measure.[New Model Map_BOM Type]" : "ExportAssy", "Measure.[New Model Map_Base Qty]" : "3", "Measure.[New Model Map_User Spec]" : "Spec3"}]
                            }

    */

    var fn_save = function(parsedParams){
        const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
        vdCommon.setLogLevel("Debug");

		try {
		    var fbVersion = parsedParams.fbParams["[Version].[Version Name]"];
            var ruleNoHm = {};
            for ( var i = 0; i < parsedParams.fbGridRows.length; i++ ) {
                var row = parsedParams.fbGridRows[i];
                var rowstatus = row["rowstatus"];

                if ( rowstatus == "C" ) {
                    var dimensions = [];
                    dimensions.push("[Version].[Version Name].[" + fbVersion + "]");
                    dimensions.push("[Item].[Item].[" + row["[Item].[Item]"] + "]");
                    dimensions.push("[Project].[Project].[" + row["[Project].[Project]"] + "]");
                    dimensions.push("[Item Material].[Item Material].[" + row["[Item Material].[Item Material]"] + "]");
                    dimensions.push("[Inch].[Inch].[" + row["[Inch].[Inch]"] + "]");
                    dimensions.push("[Buyer Group].[Buyer Group].[" + row["[Buyer Group].[Buyer Group]"] + "]");
                    dimensions.push("[Basic Name].[Basic Name].[" + row["[Basic Name].[Basic Name]"] + "]");

                    var ruleNo = row["[Rule].[Rule No]"];
                    if ( ruleNoHm[ruleNo] == undefined ) {
                        var measures = ["Measure.[New Model Map_BOM Type]", "Measure.[New Model Map_Base Qty]", "Measure.[New Model Map_User Spec]", "Measure.[Dummy]"];
                        var where = "where {&CWVUI, [Item].[Item], [Project].[Project], [Item Material].[Item Material], [Inch].[Inch], [Buyer Group].[Buyer Group], [Basic Name].[Basic Name] }";
		                var result = vdCommon.selectList(["[Rule].[Rule No]"], measures, where, "orderby [Rule].[Rule No].Key desc", "limit 1");
		                var newRuleNo = "0001";
                        if ( result.cs.rowCount > 0 ) {
                            newRuleNo = (parseInt(result.cs.row(0).cell(result.cs.memberColumnIndex("Rule", "Rule No")).Name) + 1) + "";
                        }
                        newRuleNo = vdUtil.fn_lpad(newRuleNo, 4, "0");
                        vdCommon.debug("newRuleNo : " + newRuleNo);

                        // Member 생성
                        if ( !vdCommon.existMember('[Rule].[Rule No]', newRuleNo) ) {
                            vdCommon.createMember('[Rule].[Rule No]', newRuleNo);
                        }

                        ruleNoHm[ruleNo] = newRuleNo;
                    }
                    dimensions.push("[Rule].[Rule No].[" + ruleNoHm[ruleNo] + "]");
                    row["[Rule].[Rule No]"] = ruleNoHm[ruleNo];

                    var measures = [];
                    measures.push('Measure.[New Model Map_BOM Type] = "' + row["Measure.[New Model Map_BOM Type]"] + '";');
                    measures.push('Measure.[New Model Map_Base Qty] = "' + row["Measure.[New Model Map_Base Qty]"] + '";');
                    measures.push('Measure.[New Model Map_User Spec] = "' + row["Measure.[New Model Map_User Spec]"] + '";');
                    measures.push(vdUtil.fn_qMeaUpdateUserName("Measure.[New Model Map_Created By]"));
                    measures.push(vdUtil.fn_qMeaUpdateTime("Measure.[New Model Map_Creation Time]"));

                    vdCommon.createMeasure(dimensions, measures);

                    // Filter 용으로 등록
                    var fDimensions = [];
                    fDimensions.push("[Version].[Version Name].[" + fbVersion + "]");
                    fDimensions.push("[Project].[Project].[" + row["[Project].[Project]"] + "]");
                    fDimensions.push("[Inch].[Inch].[" + row["[Inch].[Inch]"] + "]");
                    fDimensions.push("[Basic Name].[Basic Name].[" + row["[Basic Name].[Basic Name]"] + "]");
                    fDimensions.push("[Buyer Group].[Buyer Group].[" + row["[Buyer Group].[Buyer Group]"] + "]");
                    if ( !vdCommon.existMeasure(fDimensions, ['Measure.[New Model Map Filter_Asn]']) ) {
                        vdCommon.createMeasure(fDimensions, ['Measure.[New Model Map Filter_Asn] = 1;']);
                    }
                } else if ( rowstatus == "U" ) {
                    var dimensions = [];
                    dimensions.push("[Version].[Version Name].[" + fbVersion + "]");
                    dimensions.push("[Item].[Item].[" + row["[Item].[Item]"] + "]");
                    dimensions.push("[Project].[Project].[" + row["[Project].[Project]"] + "]");
                    dimensions.push("[Item Material].[Item Material].[" + row["[Item Material].[Item Material]"] + "]");
                    dimensions.push("[Inch].[Inch].[" + row["[Inch].[Inch]"] + "]");
                    dimensions.push("[Buyer Group].[Buyer Group].[" + row["[Buyer Group].[Buyer Group]"] + "]");
                    dimensions.push("[Basic Name].[Basic Name].[" + row["[Basic Name].[Basic Name]"] + "]");
                    dimensions.push("[Rule].[Rule No].[" + row["[Rule].[Rule No]"] + "]");

                    var measures = [];
                    measures.push('Measure.[New Model Map_BOM Type] = "' + row["Measure.[New Model Map_BOM Type]"] + '";');
                    measures.push('Measure.[New Model Map_Base Qty] = "' + row["Measure.[New Model Map_Base Qty]"] + '";');
                    measures.push('Measure.[New Model Map_User Spec] = "' + row["Measure.[New Model Map_User Spec]"] + '";');
                    measures.push(vdUtil.fn_qMeaUpdateUserName("Measure.[New Model Map_Updated By]"));
                    measures.push(vdUtil.fn_qMeaUpdateTime("Measure.[New Model Map_Update Time]"));

                    vdCommon.updateMeasure(dimensions, measures);
                } else if ( rowstatus == "D" ) {
                    var dimensions = [];
                    dimensions.push("[Version].[Version Name]" + vdUtil.fn_filterStr(fbVersion));
                    dimensions.push("[Item].[Item]" + vdUtil.fn_filterStr(row["[Item].[Item]"]));
                    dimensions.push("[Project].[Project]" + vdUtil.fn_filterStr(row["[Project].[Project]"]));
                    dimensions.push("[Item Material].[Item Material]" + vdUtil.fn_filterStr(row["[Item Material].[Item Material]"]));
                    dimensions.push("[Inch].[Inch]" + vdUtil.fn_filterStr(row["[Inch].[Inch]"]));
                    dimensions.push("[Buyer Group].[Buyer Group]" + vdUtil.fn_filterStr(row["[Buyer Group].[Buyer Group]"]));
                    dimensions.push("[Basic Name].[Basic Name]" + vdUtil.fn_filterStr(row["[Basic Name].[Basic Name]"]));
                    dimensions.push("[Rule].[Rule No]" + vdUtil.fn_filterStr(row["[Rule].[Rule No]"]));

                    vdCommon.deleteMeasure(dimensions, "New Model Map");
                }
            }

            // New Model Map BOM 을 재구성 해준다.
            var ruleNos = [];
            for ( var i = 0; i < parsedParams.fbGridRows.length; i++ ) {
                var row = parsedParams.fbGridRows[i];
                var ruleNo = row["[Rule].[Rule No]"];

                if ( !ruleNos.includes(ruleNo) ) {
                    ruleNos.push(ruleNo);
                }
            }
            // Measure 삭제
            var dimensions = [];
            dimensions.push("[Version].[Version Name]" + vdUtil.fn_filterStr(fbVersion));
            dimensions.push("[Rule].[Rule No]" + vdUtil.fn_filterStr(ruleNos));
            vdCommon.deleteMeasure(dimensions, "New Model Map BOM");
            // 26.1.20 추가
            vdCommon.deleteMeasure(dimensions, "New Model Map Monitor");
            vdCommon.deleteMeasure(dimensions, "New Model Map BOM Monitor");

            // Python 실행
            var execQuery = 'EXEC plugin instance [PY_UI_NewModelMap] ' +
                            'for measures {[New Model Map BOM_BOM Type]} ' +
                            'using scope ( [Version].[Version Name]' + vdUtil.fn_filterStr(fbVersion) + ' * [Rule].[Rule No]' + vdUtil.fn_filterStr(ruleNos) + ' ) ' +
                            'using arguments {(ExecutionMode, "MediumWeight"), (MaxSliceTableCells, 200000000), (MaxConcurrency, 1 )};'
            vdCommon.executePython("PY_UI_NewModelMap", execQuery);

            vdCommon.programEnd();

            return { "Code" : 0, "Msg" : "" };
        } catch ( e ) {
            vdCommon.error(e.message);
            return { "Code" : -1, "Msg" : e.message };
        }
    };


/************************************************* util logic *************************************************/

/************************************************* Mapping logic **********************************************/
    // Mapping 함수 정의, 마지막에 선언을 해야 함수를 정상적으로 인식함
    const functionMap = {
        "fn_cb_newModelMapBuyer" : fn_cb_newModelMapBuyer
        ,"fn_save" : fn_save
    };

    return {
        fn_loadFunction : fn_loadFunction
    };
});

/**************************** o9.NSCM.JSEWNewModelMapping ****************************
2025-12-04 : 신규 추가시 Filter 를 위해서 New Model Map Filter 에 데이타 넣기
2026-01-20 : 삭제시 New Model Map Monitor, New Model Map BOM Monitor 도 같이 삭제하도록 수정
**************************************************************************************/