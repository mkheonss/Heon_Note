define('o9.NSCM.JSEWConstraintTypeMtrl', ['o9/data/query', 'o9/data/cellset', 'o9.NSCM.commonLib'], function () {

/**************************************************************************************
    프로그램명  : o9.NSCM.JSEWConstraintTypeMtrl
    화면명     : Constraint Type Material
    화면 개발자 : 김종진 프로
    API 개발자 : sungmin0.lim
    최초생성   : 2025.08.29
**************************************************************************************/

	const programName = "o9.NSCM.JSEWConstraintTypeMtrl";
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
    // { "fbFuncName" : "fn_cb_subSet" }
	var fn_cb_subSet = function(parsedParams){
        const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
        vdCommon.setLogLevel("Debug");

		try {
            var comboList = vdCommon.fn_makeCombo(null, {ComboCodes : ["LV4","LV5","-"], ComboValues : ["LV4","LV5","-"]});
            vdCommon.debug("ComboData : " + JSON.stringify(comboList.slice(0,3)));

            vdCommon.programEnd();

            return { "Code" : 0, "Msg" : "", "Rows" : comboList };
        } catch ( e ) {
            vdCommon.error(e.message);
            return { "Code" : -1, "Msg" : e.message };
        }
    };

    // { "fbFuncName" : "fn_cb_etdEta" }
	var fn_cb_etdEta = function(parsedParams){
        const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
        vdCommon.setLogLevel("Debug");

		try {
            var comboList = vdCommon.fn_makeCombo(null, {ComboCodes : ["ETD","ETA"], ComboValues : ["ETD","ETA"]});
            vdCommon.debug("ComboData : " + JSON.stringify(comboList.slice(0,3)));

            vdCommon.programEnd();

            return { "Code" : 0, "Msg" : "", "Rows" : comboList };
        } catch ( e ) {
            vdCommon.error(e.message);
            return { "Code" : -1, "Msg" : e.message };
        }
    };

    // { "fbFuncName" : "fn_cb_timeVarying" }
	var fn_cb_timeVarying = function(parsedParams){
        const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
        vdCommon.setLogLevel("Debug");

		try {
            var comboList = vdCommon.fn_makeCombo(null, {ComboCodes : ["Y","N"], ComboValues : ["Y","N"]});
            vdCommon.debug("ComboData : " + JSON.stringify(comboList.slice(0,3)));

            vdCommon.programEnd();

            return { "Code" : 0, "Msg" : "", "Rows" : comboList };
        } catch ( e ) {
            vdCommon.error(e.message);
            return { "Code" : -1, "Msg" : e.message };
        }
    };

    // { "fbFuncName" : "fn_cb_msl1" }
	var fn_cb_msl1 = function(parsedParams){
        const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
        vdCommon.setLogLevel("Debug");

		try {
            var result = vdCommon.selectList(["&NSUIMtrlMSL1View"],
                                            [],
                                            "", "orderby [Item Material].[MSL1].[MSL1 Sorting Order]", "");
            var comboList = vdCommon.fn_makeCombo(result, {DimName : "Item Material", DimAttbName : "MSL1"});
            vdCommon.debug("ComboData : " + JSON.stringify(comboList.slice(0,3)));

            vdCommon.programEnd();

            return { "Code" : 0, "Msg" : "", "Rows" : comboList };
        } catch ( e ) {
            vdCommon.error(e.message);
            return { "Code" : -1, "Msg" : e.message };
        }
    };

    // { "fbFuncName" : "fn_cb_msl12" }
	var fn_cb_msl12 = function(parsedParams){
        const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
        vdCommon.setLogLevel("Debug");

		try {
            var result = vdCommon.selectList(["&NSUIMtrlMSL1View", "&NSUIMtrlMSL2View"],
                                            [],
                                            "", "orderby [Item Material].[MSL2].[MSL2 Sorting Order]", "");
            var comboList = vdCommon.fn_makeCombo(result, {DimName : "Item Material", DimAttbName : "MSL2", includeField : "Item Material:MSL1:MSL1"});
            vdCommon.debug("ComboData : " + JSON.stringify(comboList.slice(0,3)));

            vdCommon.programEnd();

            return { "Code" : 0, "Msg" : "", "Rows" : comboList };
        } catch ( e ) {
            vdCommon.error(e.message);
            return { "Code" : -1, "Msg" : e.message };
        }
    };

    // { "fbFuncName" : "fn_cb_msl23" }
	var fn_cb_msl23 = function(parsedParams){
        const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
        vdCommon.setLogLevel("Debug");

		try {
            var result = vdCommon.selectList(["&NSUIMtrlMSL2View", "&NSUIMtrlMSL3View"],
                                            [],
                                            "", "orderby [Item Material].[MSL3].[MSL3 Sorting Order]", "");
            var comboList = vdCommon.fn_makeCombo(result, {DimName : "Item Material", DimAttbName : "MSL3", includeField : "Item Material:MSL2:MSL2"});
            vdCommon.debug("ComboData : " + JSON.stringify(comboList.slice(0,3)));

            vdCommon.programEnd();

            return { "Code" : 0, "Msg" : "", "Rows" : comboList };
        } catch ( e ) {
            vdCommon.error(e.message);
            return { "Code" : -1, "Msg" : e.message };
        }
    };

    // { "fbFuncName" : "fn_cb_msl34" }
	var fn_cb_msl34 = function(parsedParams){
        const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
        vdCommon.setLogLevel("Debug");

		try {
            var result = vdCommon.selectList(["&NSUIMtrlMSL3View", "&NSUIMtrlMSL4View"],
                                            [],
                                            "", "orderby [Item Material].[MSL4].[MSL4 Sorting Order]", "");
            var comboList = vdCommon.fn_makeCombo(result, {DimName : "Item Material", DimAttbName : "MSL4", includeField : "Item Material:MSL3:MSL3"});
            vdCommon.debug("ComboData : " + JSON.stringify(comboList.slice(0,3)));

            // All 추가
            comboList.unshift({Name : "All", DisplayName : "All", MSL3 : "All", MSL3_DisplayName : "All", MSL3_DisplayAlias : "All"});

            vdCommon.programEnd();

            return { "Code" : 0, "Msg" : "", "Rows" : comboList };
        } catch ( e ) {
            vdCommon.error(e.message);
            return { "Code" : -1, "Msg" : e.message };
        }
    };

    // { "fbFuncName" : "fn_cb_msl345" }
	var fn_cb_msl345 = function(parsedParams){
        const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
        vdCommon.setLogLevel("Debug");

		try {
            var result = vdCommon.selectList(["&NSUIMtrlMSL3View", "&NSUIMtrlMSL4View", "&NSUIMtrlMSL5View"],
                                            [],
                                            "", "orderby [Item Material].[MSL5].[MSL5 Sorting Order]", "");
            var comboList = vdCommon.fn_makeCombo(result, {DimName : "Item Material", DimAttbName : "MSL5", includeField : "Item Material:MSL3:MSL3,Item Material:MSL4:MSL4"});
            vdCommon.debug("ComboData : " + JSON.stringify(comboList.slice(0,3)));

            // All 추가
            comboList.unshift({Name : "All", DisplayName : "All", MSL3 : "All", MSL3_DisplayName : "All", MSL3_DisplayAlias : "All", MSL4 : "All", MSL4_DisplayName : "All", MSL4_DisplayAlias : "All"});

            vdCommon.programEnd();

            return { "Code" : 0, "Msg" : "", "Rows" : comboList };
        } catch ( e ) {
            vdCommon.error(e.message);
            return { "Code" : -1, "Msg" : e.message };
        }
    };

    // { "fbFuncName" : "fn_cb_plant" }
	var fn_cb_plant = function(parsedParams){
        const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
        vdCommon.setLogLevel("Debug");

		try {
            var result = vdCommon.selectList(["&NSUILocationMFMtrlView"],
                                            [],
                                            "", "", "");
            var comboList = vdCommon.fn_makeCombo(result, {DimName : "Location", DimAttbName : "Location"});
            vdCommon.debug("ComboData : " + JSON.stringify(comboList.slice(0,3)));

            vdCommon.programEnd();

            return { "Code" : 0, "Msg" : "", "Rows" : comboList };
        } catch ( e ) {
            vdCommon.error(e.message);
            return { "Code" : -1, "Msg" : e.message };
        }
    };

    // { "fbFuncName" : "fn_cb_item", "fbParams" : { "[Item Material].[MSL5]" : "Panel>TV Panel>TV OpenCell>37~43>40" } }
	var fn_cb_item = function(parsedParams){
        const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
        vdCommon.setLogLevel("Debug");

		try {
            var msl3 = vdUtil.fn_getParam(parsedParams, "[Item Material].[MSL3]");
            var msl4 = vdUtil.fn_getParam(parsedParams, "[Item Material].[MSL4]");
            var msl5 = vdUtil.fn_getParam(parsedParams, "[Item Material].[MSL5]");

            var version = vdUtil.fn_getFilterQuery(parsedParams, "[Version].[Version Name]");

            var comboList = [];
            var result = vdCommon.selectList(["[Item Material].[MSL3]" + vdUtil.fn_filterStr(msl3),
                                                "[Item Material].[MSL4]" + ( msl4 == "All" ? "" : vdUtil.fn_filterStr(msl4) ),
                                                "[Item Material].[MSL5]" + ( msl5 == "All" ? "" : vdUtil.fn_filterStr(msl5) ),
                                                "[Item Material].[Item Material]"],
                                            [],
                                            'where {' + version + ', Measure.[Item Mtrl Site Asn_Cur Status] in {"ACTIVE","PLANNED"}}',
                                            "", "");
            var comboList = vdCommon.fn_makeCombo(result, {DimName : "Item Material", DimAttbName : "Item Material"});
            vdCommon.debug("ComboData : " + JSON.stringify(comboList.slice(0,3)));

            vdCommon.programEnd();

            return { "Code" : 0, "Msg" : "", "Rows" : comboList };
        } catch ( e ) {
            vdCommon.error(e.message);
            return { "Code" : -1, "Msg" : e.message };
        }
    };


    /*
- 수정 테스트
{ "fbFuncName" : "fn_save3", "fbParams" : { "[Version].[Version Name]" : "CWV_MP" },
  "fbGridRows" : [
{ "rowstatus":"U","rowindex":"0","[Version].[Version Name]":"CWV_MP","[Item Material].[MSL3]":"Panel>EB Panel>EB OpenCell","Measure.[Mtrl Const Type L3_ETDETA]":"ETD","Measure.[Mtrl Const Type L3_Time Varying Flag]":"Y","Measure.[Mtrl Const Type L3 W_Type]" : ["202520^Un","202521^Hard","202522^Soft","202523^Un"] }
                  ] }
    */
    var fn_save3 = function(parsedParams){
        const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
        vdCommon.setLogLevel("Debug");

		try {
            // 저장
            for ( var i = 0; i < parsedParams.fbGridRows.length; i++ ) {
                var row = parsedParams.fbGridRows[i];
                var rowstatus = row["rowstatus"];

            if ( rowstatus == "U" ) {
                    var dimensions = [];
                    dimensions.push(vdUtil.fn_qDimVersionName(parsedParams));
                    dimensions.push(vdUtil.fn_qDim(row, "[Item Material].[MSL3]"));
                    var measures = [];
                    measures.push(vdUtil.fn_qMeaStr(row, "Measure.[Mtrl Const Type L3_Sub Set]"));
                    measures.push(vdUtil.fn_qMeaStr(row, "Measure.[Mtrl Const Type L3_ETDETA]"));
                    measures.push(vdUtil.fn_qMeaStr(row, "Measure.[Mtrl Const Type L3_Time Varying Flag]"));
                    measures.push(vdUtil.fn_qMeaUpdateUser("Measure.[Mtrl Const Type L3_Updated By]"));
                    measures.push(vdUtil.fn_qMeaUpdateTime("Measure.[Mtrl Const Type L3_Update Time]"));
                    vdCommon.updateMeasure(dimensions, measures);

                    // 주차 수정
                    var weekList = row["Measure.[Mtrl Const Type L3 W_Type]"];
                    var queryStr = "";
                    for ( var m = 0; m < weekList.length; m++ ) {
                        var subDimensions = [];
                        subDimensions.push(vdUtil.fn_qDimVersionName(parsedParams));
                        subDimensions.push(vdUtil.fn_qDim(row, "[Item Material].[MSL3]"));
                        subDimensions.push("[Relative Week].[Relative Week].[" + weekList[m].split("^")[0] + "]");

                        var subMeasures = [];
                        subMeasures.push(vdUtil.fn_qMeaStr(row, "Measure.[Mtrl Const Type L3 W_Type]", weekList[m].split("^")[1]));

                        queryStr += vdCommon.createMeasureQuery(subDimensions, subMeasures);
                    }
                    if ( queryStr != "" ) {
                        vdCommon.executeQuery("Mtrl Const Type L3 W", queryStr);
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
{ "fbFuncName" : "fn_save4", "fbParams" : { "[Version].[Version Name]" : "CWV_MP" },
  "fbGridRows" : [
{ "rowstatus":"C","rowindex":"0","[Location].[Location]":"P551","[Item Material].[MSL4]":"Panel>TV Panel>TV OpenCell>60~70","Measure.[Mtrl Const Type L4_ETDETA]":"ETD","Measure.[Mtrl Const Type L4_Time Varying Flag]":"Y","Measure.[Mtrl Const Type L4 W_Type]" : ["202520^Un","202521^Hard","202522^Soft","202523^Un"] }
                  ] }

- 수정 테스트
{ "fbFuncName" : "fn_save4", "fbParams" : { "[Version].[Version Name]" : "CWV_MP" },
  "fbGridRows" : [
{ "rowstatus":"U","rowindex":"0","[Location].[Location]":"P551","[Item Material].[MSL4]":"Panel>TV Panel>TV OpenCell>60~70","Measure.[Mtrl Const Type L4_ETDETA]":"ETD","Measure.[Mtrl Const Type L4_Time Varying Flag]":"Y","Measure.[Mtrl Const Type L4 W_Type]" : ["202520^Un","202521^Hard","202522^Soft","202523^Un"] }
                  ] }

- 삭제 테스트
{ "fbFuncName" : "fn_save4", "fbParams" : { "[Version].[Version Name]" : "CWV_MP" },
  "fbGridRows" : [
{ "rowstatus":"D","rowindex":"0","[Location].[Location]":"P551","[Item Material].[MSL4]":"Panel>TV Panel>TV OpenCell>60~70","Measure.[Mtrl Const Type L4_ETDETA]":"ETD","Measure.[Mtrl Const Type L4_Time Varying Flag]":"Y","Measure.[Mtrl Const Type L4 W_Type]" : ["202520^Un","202521^Hard","202522^Soft","202523^Un"] }
                  ] }

    */

    var fn_save4 = function(parsedParams){
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
                    dimensions.push(vdUtil.fn_qDim(row, "[Item Material].[MSL4]"));

                    // 등록 여부 체크
                    var count = vdCommon.selectListCount(dimensions, ["Measure.[Mtrl Const Type L4_ETDETA]"], "");
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
                    var dimensions = [];
                    dimensions.push(vdUtil.fn_qDimVersionName(parsedParams));
                    dimensions.push(vdUtil.fn_qDim(row, "[Item Material].[MSL4]"));

                    var measures = [];
                    measures.push(vdUtil.fn_qMeaStr(row, "Measure.[Mtrl Const Type L4_ETDETA]"));
                    measures.push(vdUtil.fn_qMeaStr(row, "Measure.[Mtrl Const Type L4_Time Varying Flag]"));
                    measures.push(vdUtil.fn_qMeaUpdateUser("Measure.[Mtrl Const Type L4_Created By]"));
                    measures.push(vdUtil.fn_qMeaUpdateTime("Measure.[Mtrl Const Type L4_Creation Time]"));

                    vdCommon.createMeasure(dimensions, measures);

                    // Week 데이타 생성
                    vdCommon.createMeasure([vdUtil.fn_qDimVersionName(parsedParams),
                                                vdUtil.fn_qDim(row, "[Item Material].[MSL4]"),
                                                "[Relative Week].[Relative Week]"],
                                            ['Measure.[Mtrl Const Type L4 W_Type] = "Soft";']);

                    var weekList = row["Measure.[Mtrl Const Type L4 W_Type]"];
                    var queryStr = "";
                    for ( var m = 0; m < weekList.length; m++ ) {
                        var subDimensions = [];
                        subDimensions.push(vdUtil.fn_qDimVersionName(parsedParams));
                        subDimensions.push(vdUtil.fn_qDim(row, "[Item Material].[MSL4]"));
                        subDimensions.push("[Relative Week].[Relative Week].[" + weekList[m].split("^")[0] + "]");

                        var subMeasures = [];
                        subMeasures.push(vdUtil.fn_qMeaStr(row, "Measure.[Mtrl Const Type L4 W_Type]", weekList[m].split("^")[1]));

                        queryStr += vdCommon.updateMeasureQuery(subDimensions, subMeasures);
                    }
                    if ( queryStr != "" ) {
                        vdCommon.executeQuery("Mtrl Const Type L4 W", queryStr);
                    }
                } else if ( rowstatus == "U" ) {
                    var dimensions = [];
                    dimensions.push(vdUtil.fn_qDimVersionName(parsedParams));
                    dimensions.push(vdUtil.fn_qDim(row, "[Item Material].[MSL4]"));

                    var measures = [];
                    measures.push(vdUtil.fn_qMeaStr(row, "Measure.[Mtrl Const Type L4_ETDETA]"));
                    measures.push(vdUtil.fn_qMeaStr(row, "Measure.[Mtrl Const Type L4_Time Varying Flag]"));
                    measures.push(vdUtil.fn_qMeaUpdateUser("Measure.[Mtrl Const Type L4_Updated By]"));
                    measures.push(vdUtil.fn_qMeaUpdateTime("Measure.[Mtrl Const Type L4_Update Time]"));

                    vdCommon.updateBlockMeasure(dimensions, measures);

                    // 주차 수정
                    var weekList = row["Measure.[Mtrl Const Type L4 W_Type]"];
                    var queryStr = "";
                    for ( var m = 0; m < weekList.length; m++ ) {
                        var subDimensions = [];
                        subDimensions.push(vdUtil.fn_qDimVersionName(parsedParams));
                        subDimensions.push(vdUtil.fn_qDim(row, "[Item Material].[MSL4]"));
                        subDimensions.push("[Relative Week].[Relative Week].[" + weekList[m].split("^")[0] + "]");

                        var subMeasures = [];
                        subMeasures.push(vdUtil.fn_qMeaStr(row, "Measure.[Mtrl Const Type L4 W_Type]", weekList[m].split("^")[1]));

                        queryStr += vdCommon.updateMeasureQuery(subDimensions, subMeasures);
                    }
                    if ( queryStr != "" ) {
                        vdCommon.executeQuery("Mtrl Const Type L4 W", queryStr);
                    }
                } else if ( rowstatus == "D" ) {
                    var where = [];
                    where.push(vdUtil.fn_qDimVersionName(parsedParams));
                    where.push(vdUtil.fn_qDim(row, "[Item Material].[MSL4]"));

                    vdCommon.deleteMeasure(where, "Mtrl Const Type L4");
                    vdCommon.deleteMeasure(where, "Mtrl Const Type L4 W");
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
{ "fbFuncName" : "fn_save5", "fbParams" : { "[Version].[Version Name]" : "CWV_MP" },
  "fbGridRows" : [
{ "rowstatus":"C","rowindex":"0","[Version].[Version Name]":"CWV_MP","[Item Material].[MSL5]":"Panel>TV Panel>TV OpenCell>75↑>75","Measure.[Mtrl Const Type L5_ETDETA]":"ETD","Measure.[Mtrl Const Type L5_Time Varying Flag]":"Y","Measure.[Mtrl Const Type L5 W_Type]" : ["202520^Un","202521^Hard","202522^Soft","202523^Un"] }
                  ] }

- 수정 테스트
{ "fbFuncName" : "fn_save5", "fbParams" : { "[Version].[Version Name]" : "CWV_MP" },
  "fbGridRows" : [
{ "rowstatus":"U","rowindex":"0","[Version].[Version Name]":"CWV_MP","[Item Material].[MSL5]":"Panel>TV Panel>TV OpenCell>75↑>75","Measure.[Mtrl Const Type L5_ETDETA]":"ETD","Measure.[Mtrl Const Type L5_Time Varying Flag]":"Y","Measure.[Mtrl Const Type L5 W_Type]" : ["202520^Un","202521^Hard","202522^Soft","202523^Un"] }
                  ] }

- 삭제 테스트
{ "fbFuncName" : "fn_save5", "fbParams" : { "[Version].[Version Name]" : "CWV_MP" },
  "fbGridRows" : [
{ "rowstatus":"D","rowindex":"0","[Version].[Version Name]":"CWV_MP","[Item Material].[MSL5]":"Panel>TV Panel>TV OpenCell>75↑>75","Measure.[Mtrl Const Type L5_ETDETA]":"ETD","Measure.[Mtrl Const Type L5_Time Varying Flag]":"Y","Measure.[Mtrl Const Type L5 W_Type]" : ["202520^Un","202521^Hard","202522^Soft","202523^Un"] }
                  ] }


    */

    var fn_save5 = function(parsedParams){
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
                    dimensions.push(vdUtil.fn_qDim(row, "[Item Material].[MSL5]"));

                    // 등록 여부 체크
                    var count = vdCommon.selectListCount(dimensions, ["Measure.[Mtrl Const Type L5_ETDETA]"], "");
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
                    var dimensions = [];
                    dimensions.push(vdUtil.fn_qDimVersionName(parsedParams));
                    dimensions.push(vdUtil.fn_qDim(row, "[Item Material].[MSL5]"));

                    var measures = [];
                    measures.push(vdUtil.fn_qMeaStr(row, "Measure.[Mtrl Const Type L5_ETDETA]"));
                    measures.push(vdUtil.fn_qMeaStr(row, "Measure.[Mtrl Const Type L5_Time Varying Flag]"));
                    measures.push(vdUtil.fn_qMeaUpdateUser("Measure.[Mtrl Const Type L5_Created By]"));
                    measures.push(vdUtil.fn_qMeaUpdateTime("Measure.[Mtrl Const Type L5_Creation Time]"));

                    vdCommon.createMeasure(dimensions, measures);

                    // Week 데이타 생성
                    vdCommon.createMeasure([vdUtil.fn_qDimVersionName(parsedParams),
                                                vdUtil.fn_qDim(row, "[Item Material].[MSL5]"),
                                                "[Relative Week].[Relative Week]"],
                                            ['Measure.[Mtrl Const Type L5 W_Type] = "Soft";']);

                    var weekList = row["Measure.[Mtrl Const Type L5 W_Type]"];
                    var queryStr = "";
                    for ( var m = 0; m < weekList.length; m++ ) {
                        var subDimensions = [];
                        subDimensions.push(vdUtil.fn_qDimVersionName(parsedParams));
                        subDimensions.push(vdUtil.fn_qDim(row, "[Item Material].[MSL5]"));
                        subDimensions.push("[Relative Week].[Relative Week].[" + weekList[m].split("^")[0] + "]");

                        var subMeasures = [];
                        subMeasures.push(vdUtil.fn_qMeaStr(row, "Measure.[Mtrl Const Type L5 W_Type]", weekList[m].split("^")[1]));

                        queryStr += vdCommon.updateMeasureQuery(subDimensions, subMeasures);
                    }
                    if ( queryStr != "" ) {
                        vdCommon.executeQuery("Mtrl Const Type L5 W", queryStr);
                    }
                } else if ( rowstatus == "U" ) {
                    var dimensions = [];
                    dimensions.push(vdUtil.fn_qDimVersionName(parsedParams));
                    dimensions.push(vdUtil.fn_qDim(row, "[Item Material].[MSL5]"));

                    var measures = [];
                    measures.push(vdUtil.fn_qMeaStr(row, "Measure.[Mtrl Const Type L5_ETDETA]"));
                    measures.push(vdUtil.fn_qMeaStr(row, "Measure.[Mtrl Const Type L5_Time Varying Flag]"));
                    measures.push(vdUtil.fn_qMeaUpdateUser("Measure.[Mtrl Const Type L5_Updated By]"));
                    measures.push(vdUtil.fn_qMeaUpdateTime("Measure.[Mtrl Const Type L5_Update Time]"));

                    vdCommon.updateBlockMeasure(dimensions, measures);

                    // 주차 수정
                    var weekList = row["Measure.[Mtrl Const Type L5 W_Type]"];
                    var queryStr = "";
                    for ( var m = 0; m < weekList.length; m++ ) {
                        var subDimensions = [];
                        subDimensions.push(vdUtil.fn_qDimVersionName(parsedParams));
                        subDimensions.push(vdUtil.fn_qDim(row, "[Item Material].[MSL5]"));
                        subDimensions.push("[Relative Week].[Relative Week].[" + weekList[m].split("^")[0] + "]");

                        var subMeasures = [];
                        subMeasures.push(vdUtil.fn_qMeaStr(row, "Measure.[Mtrl Const Type L5 W_Type]", weekList[m].split("^")[1]));

                        queryStr += vdCommon.updateMeasureQuery(subDimensions, subMeasures);
                    }
                    if ( queryStr != "" ) {
                        vdCommon.executeQuery("Mtrl Const Type L5 W", queryStr);
                    }
                } else if ( rowstatus == "D" ) {
                    var where = [];
                    where.push(vdUtil.fn_qDimVersionName(parsedParams));
                    where.push(vdUtil.fn_qDim(row, "[Item Material].[MSL5]"));

                    vdCommon.deleteMeasure(where, "Mtrl Const Type L5");
                    vdCommon.deleteMeasure(where, "Mtrl Const Type L5 W");
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
{ "fbFuncName" : "fn_saveItem", "fbParams" : { "[Version].[Version Name]" : "CWV_MP" },
  "fbGridRows" : [
{ "rowstatus":"C","rowindex":"1","[Version].[Version Name]":"CWV_MP","[Location].[Location]":"P551^P721","[Item Material].[Item Material]":"BN96-60407A^BN96-50510A","Measure.[Mtrl Const Type Item_ETDETA]":"ETA","Measure.[Mtrl Const Type Item_Time Varying Flag]":"N","Measure.[Mtrl Const Type Item W_Type]" : ["202520^Un","202521^Hard","202522^Soft","202523^Un"] }
                  ] }

- 수정 테스트
{ "fbFuncName" : "fn_saveItem", "fbParams" : { "[Version].[Version Name]" : "CWV_MP" },
  "fbGridRows" : [
{ "rowstatus":"U","rowindex":"2","[Version].[Version Name]":"CWV_MP","[Location].[Location]":"P551","[Item Material].[Item Material]":"BN96-60407A","Measure.[Mtrl Const Type Item_ETDETA]":"ETD","Measure.[Mtrl Const Type Item_Time Varying Flag]":"Y","Measure.[Mtrl Const Type Item W_Type]" : ["202520^Un","202521^Hard","202522^Soft","202523^Un"] }
                  ] }

- 삭제 테스트
{ "fbFuncName" : "fn_saveItem", "fbParams" : { "[Version].[Version Name]" : "CWV_MP" },
  "fbGridRows" : [
{ "rowstatus":"D","rowindex":"2","[Version].[Version Name]":"CWV_MP","[Location].[Location]":"P551","[Item Material].[Item Material]":"BN96-60407A","Measure.[Mtrl Const Type Item_ETDETA]":"ETD","Measure.[Mtrl Const Type Item_Time Varying Flag]":"Y","Measure.[Mtrl Const Type Item W_Type]" : ["202520^Un","202521^Hard","202522^Soft","202523^Un"] },
{ "rowstatus":"D","rowindex":"2","[Version].[Version Name]":"CWV_MP","[Location].[Location]":"P551","[Item Material].[Item Material]":"BN96-50510A","Measure.[Mtrl Const Type Item_ETDETA]":"ETD","Measure.[Mtrl Const Type Item_Time Varying Flag]":"Y","Measure.[Mtrl Const Type Item W_Type]" : ["202520^Un","202521^Hard","202522^Soft","202523^Un"] },
{ "rowstatus":"D","rowindex":"2","[Version].[Version Name]":"CWV_MP","[Location].[Location]":"P721","[Item Material].[Item Material]":"BN96-60407A","Measure.[Mtrl Const Type Item_ETDETA]":"ETD","Measure.[Mtrl Const Type Item_Time Varying Flag]":"Y","Measure.[Mtrl Const Type Item W_Type]" : ["202520^Un","202521^Hard","202522^Soft","202523^Un"] },
{ "rowstatus":"D","rowindex":"2","[Version].[Version Name]":"CWV_MP","[Location].[Location]":"P721","[Item Material].[Item Material]":"BN96-50510A","Measure.[Mtrl Const Type Item_ETDETA]":"ETD","Measure.[Mtrl Const Type Item_Time Varying Flag]":"Y","Measure.[Mtrl Const Type Item W_Type]" : ["202520^Un","202521^Hard","202522^Soft","202523^Un"] }
                  ] }
    */

    var fn_saveItem = function(parsedParams){
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
                    var location = row["[Location].[Location]"];
                    var itemMaterial = row["[Item Material].[Item Material]"];

                    var dimensions = [];
                    dimensions.push(vdUtil.fn_qDimVersionName(parsedParams));
                    dimensions.push("[Location].[Location]" + vdUtil.fn_filterStr(location.split("^")));
                    dimensions.push("[Item Material].[Item Material]" + vdUtil.fn_filterStr(itemMaterial.split("^")));

                    // 등록 여부 체크
                    var count = vdCommon.selectListCount(dimensions, ["Measure.[Mtrl Const Type Item_ETDETA]"], "");
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
                    var location = row["[Location].[Location]"];
                    var itemMaterial = row["[Item Material].[Item Material]"];

                    var dimensions = [];
                    dimensions.push(vdUtil.fn_qDimVersionName(parsedParams));
                    dimensions.push("[Location].[Location]" + vdUtil.fn_filterStr(location.split("^")));
                    dimensions.push("[Item Material].[Item Material]" + vdUtil.fn_filterStr(itemMaterial.split("^")));

                    var measures = [];
                    measures.push(vdUtil.fn_qMeaStr(row, "Measure.[Mtrl Const Type Item_ETDETA]"));
                    measures.push(vdUtil.fn_qMeaStr(row, "Measure.[Mtrl Const Type Item_Time Varying Flag]"));
                    measures.push(vdUtil.fn_qMeaUpdateUser("Measure.[Mtrl Const Type Item_Created By]"));
                    measures.push(vdUtil.fn_qMeaUpdateTime("Measure.[Mtrl Const Type Item_Creation Time]"));

                    vdCommon.createMeasure(dimensions, measures);

                    // Week 데이타 생성
                    vdCommon.createMeasure([vdUtil.fn_qDimVersionName(parsedParams),
                                                "[Location].[Location]" + vdUtil.fn_filterStr(location.split("^")),
                                                "[Item Material].[Item Material]" + vdUtil.fn_filterStr(itemMaterial.split("^")),
                                                "[Relative Week].[Relative Week]"],
                                            ['Measure.[Mtrl Const Type Item W_Type] = 0;']);

                    var weekList = row["Measure.[Mtrl Const Type Item W_Type]"];
                    var queryStr = "";
                    for ( var m = 0; m < weekList.length; m++ ) {
                        var subDimensions = [];
                        subDimensions.push(vdUtil.fn_qDimVersionName(parsedParams));
                        subDimensions.push("[Location].[Location]" + vdUtil.fn_filterStr(location.split("^")));
                        subDimensions.push("[Item Material].[Item Material]" + vdUtil.fn_filterStr(itemMaterial.split("^")));
                        subDimensions.push("[Relative Week].[Relative Week].[" + weekList[m].split("^")[0] + "]");

                        var subMeasures = [];
                        subMeasures.push(vdUtil.fn_qMeaStr(row, "Measure.[Mtrl Const Type Item W_Type]", weekList[m].split("^")[1]));

                        queryStr += vdCommon.updateMeasureQuery(subDimensions, subMeasures);
                    }
                    if ( queryStr != "" ) {
                        vdCommon.executeQuery("Mtrl Const Type Item W", queryStr);
                    }
                } else if ( rowstatus == "U" ) {
                    var dimensions = [];
                    dimensions.push(vdUtil.fn_qDimVersionName(parsedParams));
                    dimensions.push(vdUtil.fn_qDim(row, "[Location].[Location]"));
                    dimensions.push(vdUtil.fn_qDim(row, "[Item Material].[Item Material]"));

                    var measures = [];
                    measures.push(vdUtil.fn_qMeaStr(row, "Measure.[Mtrl Const Type Item_ETDETA]"));
                    measures.push(vdUtil.fn_qMeaStr(row, "Measure.[Mtrl Const Type Item_Time Varying Flag]"));
                    measures.push(vdUtil.fn_qMeaUpdateUser("Measure.[Mtrl Const Type Item_Updated By]"));
                    measures.push(vdUtil.fn_qMeaUpdateTime("Measure.[Mtrl Const Type Item_Update Time]"));

                    vdCommon.updateBlockMeasure(dimensions, measures);

                    // 주차 수정
                    var weekList = row["Measure.[Mtrl Const Type Item W_Type]"];
                    var queryStr = "";
                    for ( var m = 0; m < weekList.length; m++ ) {
                        var subDimensions = [];
                        subDimensions.push(vdUtil.fn_qDimVersionName(parsedParams));
                        subDimensions.push(vdUtil.fn_qDim(row, "[Location].[Location]"));
                        subDimensions.push(vdUtil.fn_qDim(row, "[Item Material].[Item Material]"));
                        subDimensions.push("[Relative Week].[Relative Week].[" + weekList[m].split("^")[0] + "]");

                        var subMeasures = [];
                        subMeasures.push(vdUtil.fn_qMeaStr(row, "Measure.[Mtrl Const Type Item W_Type]", weekList[m].split("^")[1]));

                        queryStr += vdCommon.createMeasureQuery(subDimensions, subMeasures);
                    }
                    if ( queryStr != "" ) {
                        vdCommon.executeQuery("Mtrl Const Type Item W", queryStr);
                    }
                } else if ( rowstatus == "D" ) {
                    var where = [];
                    where.push(vdUtil.fn_qDimVersionName(parsedParams));
                    where.push(vdUtil.fn_qDim(row, "[Location].[Location]"));
                    where.push(vdUtil.fn_qDim(row, "[Item Material].[Item Material]"));

                    vdCommon.deleteMeasure(where, "Mtrl Const Type Item");
                    vdCommon.deleteMeasure(where, "Mtrl Const Type Item W");
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
- 파라미터
{ "fbFuncName" : "fn_merge"
    ,"fbParams" : { "commitType" : "1", "grid" : "Lv3"
                    ,"filters" : { "[Version].[Version Name]" : {"SelectedMembers" : ["202605_P_WI_01"], "MemberFilter" : ""} }
                   }
    ,"fbGridRows" : [
        { "rowstatus":"C","[Item Material].[MSL3]":"Semicon.>Semicon.>Non Memory" }
                  ] }

{ "fbFuncName" : "fn_merge"
    ,"fbParams" : { "commitType" : "1", "grid" : "Lv4"
                    ,"filters" : { "[Version].[Version Name]" : {"SelectedMembers" : ["202605_P_WI_01"], "MemberFilter" : ""} }
                   }
    ,"fbGridRows" : [
        { "rowstatus":"C","[Item Material].[MSL4]":"Elec.>Elec.>SMPS>Adapto" }
                  ] }

{ "fbFuncName" : "fn_merge"
    ,"fbParams" : { "commitType" : "1", "grid" : "Lv5"
                    ,"filters" : { "[Version].[Version Name]" : {"SelectedMembers" : ["202605_P_WI_01"], "MemberFilter" : ""} }
                   }
    ,"fbGridRows" : [
        { "rowstatus":"C","[Item Material].[MSL5]":"Optics>Optics>Sheet>Complex>*" }
                  ] }

{ "fbFuncName" : "fn_merge"
    ,"fbParams" : { "commitType" : "1", "grid" : "Item"
                    ,"filters" : { "[Version].[Version Name]" : {"SelectedMembers" : ["202605_P_WI_01"], "MemberFilter" : ""} }
                   }
    ,"fbGridRows" : [
        { "rowstatus":"C","[Item Material].[Item Material]":"BN96-56470A" }
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

		    if ( parsedParams.fbParams.grid == "Lv3" ) {
		        var where = 'where { Measure.[Mtrl Const Type L3_Updated By] == "' + name + '" || Measure.[Mtrl Const Type L3_Updated By] == "' + userName + '"}';

                if ( ( parsedParams.fbParams.commitType + "" ) == "0" ) {
                    // 전체이면 내가 수정한 것만 가져와서 배열을 생성
                    var result = vdCommon.selectList(["[Version].[Version Name].[" + fbVersion + "]"
                                                            ,"[Item Material].[MSL3]"]
                                                     ,["Measure.[Mtrl Const Type L3_ETDETA]"]
                                                     ,where, "", "");
                    for ( var i = 0; i < result.cs.rowCount; i++ ) {
                        parsedParams.fbGridRows.push({ "[Item Material].[MSL3]" : vdUtil.fn_getDimValue(result, i, "Item Material", "MSL3") });
                    }
                }

                for ( var i = 0; i < parsedParams.fbGridRows.length; i++ ) {
                    var row = parsedParams.fbGridRows[i];

                    var dimensions = [];
                    dimensions.push(fbVersionName);
                    dimensions.push(vdUtil.fn_qDim(row, "[Item Material].[MSL3]"));
                    var measures = [];
                    measures.push(vdUtil.fn_qMeaForMerge("Measure.[Mtrl Const Type L3_Sub Set]", fbVersion));
                    measures.push(vdUtil.fn_qMeaForMerge("Measure.[Mtrl Const Type L3_ETDETA]", fbVersion));
                    measures.push(vdUtil.fn_qMeaForMerge("Measure.[Mtrl Const Type L3_Time Varying Flag]", fbVersion));
                    measures.push(vdUtil.fn_qMeaUpdateTime("Measure.[Mtrl Const Type L3_Update Time]"));
                    measures.push(vdCommon.fn_mergeUser("Measure.[Mtrl Const Type L3_Updated By]", fbVersion));
                    vdCommon.createMeasure(dimensions, measures);

                    dimensions = [];
                    dimensions.push(fbVersionName);
                    dimensions.push(vdUtil.fn_qDim(row, "[Item Material].[MSL3]"));
                    measures = [];
                    measures.push(vdUtil.fn_qMeaForMerge("Measure.[Mtrl Const Type L3_Sub Set]", fbVersion));
                    vdCommon.createMeasure(dimensions, measures);

                    dimensions = [];
                    dimensions.push(fbVersionName);
                    dimensions.push("&MDMHorizon");
                    dimensions.push(vdUtil.fn_qDim(row, "[Item Material].[MSL3]"));
                    measures = [];
                    measures.push(vdUtil.fn_qMeaForMerge("Measure.[Mtrl Const Type L3 W_Type]", fbVersion));
                    vdCommon.createMeasure(dimensions, measures);
                }
            } else if ( parsedParams.fbParams.grid == "Lv4" ) {
		        var where = 'where { Measure.[Mtrl Const Type L4_Updated By] == "' + name + '" || Measure.[Mtrl Const Type L4_Updated By] == "' + userName + '"}';

                if ( ( parsedParams.fbParams.commitType + "" ) == "0" ) {
                    // 전체이면 내가 수정한 것만 가져와서 배열을 생성
                    var result = vdCommon.selectList(["[Version].[Version Name].[" + fbVersion + "]"
                                                            ,"[Item Material].[MSL4]"]
                                                     ,["Measure.[Mtrl Const Type L4_ETDETA]"]
                                                     ,where, "", "");
                    for ( var i = 0; i < result.cs.rowCount; i++ ) {
                        parsedParams.fbGridRows.push({ "[Item Material].[MSL4]" : vdUtil.fn_getDimValue(result, i, "Item Material", "MSL4") });
                    }
                }

                for ( var i = 0; i < parsedParams.fbGridRows.length; i++ ) {
                    var row = parsedParams.fbGridRows[i];

                    var dimensions = [];
                    dimensions.push(fbVersionName);
                    dimensions.push(vdUtil.fn_qDim(row, "[Item Material].[MSL4]"));
                    var measures = [];

                    measures.push(vdUtil.fn_qMeaForMerge("Measure.[Mtrl Const Type L4_ETDETA]", fbVersion));
                    measures.push(vdUtil.fn_qMeaForMerge("Measure.[Mtrl Const Type L4_Time Varying Flag]", fbVersion));
                    measures.push(vdUtil.fn_qMeaUpdateTime("Measure.[Mtrl Const Type L4_Update Time]"));
                    measures.push(vdCommon.fn_mergeUser("Measure.[Mtrl Const Type L4_Updated By]", fbVersion));
                    vdCommon.createMeasure(dimensions, measures);

                    dimensions = [];
                    dimensions.push(fbVersionName);
                    dimensions.push("&MDMHorizon");
                    dimensions.push(vdUtil.fn_qDim(row, "[Item Material].[MSL4]"));
                    measures = [];
                    measures.push(vdUtil.fn_qMeaForMerge("Measure.[Mtrl Const Type L4 W_Type]", fbVersion));
                    vdCommon.createMeasure(dimensions, measures);
                }
            } else if ( parsedParams.fbParams.grid == "Lv5" ) {
		        var where = 'where { Measure.[Mtrl Const Type L5_Updated By] == "' + name + '" || Measure.[Mtrl Const Type L5_Updated By] == "' + userName + '"}';

                if ( ( parsedParams.fbParams.commitType + "" ) == "0" ) {
                    // 전체이면 내가 수정한 것만 가져와서 배열을 생성
                    var result = vdCommon.selectList(["[Version].[Version Name].[" + fbVersion + "]"
                                                            ,"[Item Material].[MSL5]"]
                                                     ,["Measure.[Mtrl Const Type L5_ETDETA]"]
                                                     ,where, "", "");
                    for ( var i = 0; i < result.cs.rowCount; i++ ) {
                        parsedParams.fbGridRows.push({ "[Item Material].[MSL5]" : vdUtil.fn_getDimValue(result, i, "Item Material", "MSL5") });
                    }
                }

                for ( var i = 0; i < parsedParams.fbGridRows.length; i++ ) {
                    var row = parsedParams.fbGridRows[i];

                    var dimensions = [];
                    dimensions.push(fbVersionName);
                    dimensions.push(vdUtil.fn_qDim(row, "[Item Material].[MSL5]"));
                    var measures = [];

                    measures.push(vdUtil.fn_qMeaForMerge("Measure.[Mtrl Const Type L5_ETDETA]", fbVersion));
                    measures.push(vdUtil.fn_qMeaForMerge("Measure.[Mtrl Const Type L5_Time Varying Flag]", fbVersion));
                    measures.push(vdUtil.fn_qMeaUpdateTime("Measure.[Mtrl Const Type L5_Update Time]"));
                    measures.push(vdCommon.fn_mergeUser("Measure.[Mtrl Const Type L5_Updated By]", fbVersion));
                    vdCommon.createMeasure(dimensions, measures);

                    dimensions = [];
                    dimensions.push(fbVersionName);
                    dimensions.push("&MDMHorizon");
                    dimensions.push(vdUtil.fn_qDim(row, "[Item Material].[MSL5]"));
                    measures = [];
                    measures.push(vdUtil.fn_qMeaForMerge("Measure.[Mtrl Const Type L5 W_Type]", fbVersion));
                    vdCommon.createMeasure(dimensions, measures);
                }
            } else if ( parsedParams.fbParams.grid == "Item" ) {
		        var where = 'where { Measure.[Mtrl Const Type Item_Updated By] == "' + name + '" || Measure.[Mtrl Const Type Item_Updated By] == "' + userName + '"}';

                if ( ( parsedParams.fbParams.commitType + "" ) == "0" ) {
                    // 전체이면 내가 수정한 것만 가져와서 배열을 생성
                    var result = vdCommon.selectList(["[Version].[Version Name].[" + fbVersion + "]"
                                                            ,"[Item Material].[Item Material]"]
                                                     ,["Measure.[Mtrl Const Type Item_ETDETA]"]
                                                     ,where, "", "");
                    for ( var i = 0; i < result.cs.rowCount; i++ ) {
                        parsedParams.fbGridRows.push({ "[Item Material].[Item Material]" : vdUtil.fn_getDimValue(result, i, "Item Material", "Item Material") });
                    }
                }

                for ( var i = 0; i < parsedParams.fbGridRows.length; i++ ) {
                    var row = parsedParams.fbGridRows[i];

                    var dimensions = [];
                    dimensions.push(fbVersionName);
                    dimensions.push(vdUtil.fn_qDim(row, "[Item Material].[Item Material]"));
                    var measures = [];

                    measures.push(vdUtil.fn_qMeaForMerge("Measure.[Mtrl Const Type L3_ETDETA]", fbVersion));
                    measures.push(vdUtil.fn_qMeaForMerge("Measure.[Mtrl Const Type L3_Time Varying Flag]", fbVersion));
                    measures.push(vdUtil.fn_qMeaUpdateTime("Measure.[Mtrl Const Type Item_Update Time]"));
                    measures.push(vdCommon.fn_mergeUser("Measure.[Mtrl Const Type Item_Updated By]", fbVersion));
                    vdCommon.createMeasure(dimensions, measures);

                    dimensions = [];
                    dimensions.push(fbVersionName);
                    dimensions.push("&MDMHorizon");
                    dimensions.push(vdUtil.fn_qDim(row, "[Item Material].[Item Material]"));
                    measures = [];
                    measures.push(vdUtil.fn_qMeaForMerge("Measure.[Mtrl Const Type Item W_Type]", fbVersion));
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
        "fn_save3" : fn_save3
        ,"fn_save4" : fn_save4
        ,"fn_save5" : fn_save5
        ,"fn_saveItem" : fn_saveItem
        ,"fn_cb_subSet" : fn_cb_subSet
        ,"fn_cb_etdEta" :  fn_cb_etdEta
        ,"fn_cb_timeVarying" : fn_cb_timeVarying
        ,"fn_cb_msl1" : fn_cb_msl1
        ,"fn_cb_msl12" : fn_cb_msl12
        ,"fn_cb_msl23" : fn_cb_msl23
        ,"fn_cb_msl34" : fn_cb_msl34
        ,"fn_cb_msl345" : fn_cb_msl345
        ,"fn_cb_item" : fn_cb_item
        ,"fn_cb_plant" : fn_cb_plant
        ,"fn_merge" : fn_merge
    };

    return {
        fn_loadFunction : fn_loadFunction
    };
});

/**************************** o9.NSCM.JSEWConstraintTypeMtrl ****************************
26.02.26 : fn_merge 추가
**************************************************************************************/