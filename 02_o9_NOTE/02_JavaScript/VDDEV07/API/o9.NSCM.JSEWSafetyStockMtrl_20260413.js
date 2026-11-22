define('o9.NSCM.JSEWSafetyStockMtrl', ['o9/data/query', 'o9/data/cellset', 'o9.NSCM.commonLibVD'], function () {

/**************************************************************************************
    프로그램명  : o9.NSCM.JSEWSafetyStockMtrl
    화면명     : Safety Stock Material
    화면 개발자 : 김종진 프로
    API 개발자 : sungmin0.lim
    최초생성   : 2025.08.27
**************************************************************************************/

	const programName = "o9.NSCM.JSEWSafetyStockMtrl";
    const commonLib = require('o9.NSCM.commonLibVD');
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
            var comboList = vdCommon.fn_makeCombo(null, {ComboCodes : ["Lv4","Lv5","-"], ComboValues : ["Lv4","Lv5","-"]});
            vdCommon.debug("ComboData : " + JSON.stringify(comboList.slice(0,3)));

            vdCommon.programEnd();

            return { "Code" : 0, "Msg" : "", "Rows" : comboList };
        } catch ( e ) {
            vdCommon.error(e.message);
            return { "Code" : -1, "Msg" : e.message };
        }
    };

    // { "fbFuncName" : "fn_cb_ecp" }
	var fn_cb_ecp = function(parsedParams){
        const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
        vdCommon.setLogLevel("Debug");

		try {
            var comboList = vdCommon.fn_makeCombo(null, {ComboCodes : ["on","off"], ComboValues : ["on","off"]});
            vdCommon.debug("ComboData : " + JSON.stringify(comboList.slice(0,3)));

            vdCommon.programEnd();

            return { "Code" : 0, "Msg" : "", "Rows" : comboList };
        } catch ( e ) {
            vdCommon.error(e.message);
            return { "Code" : -1, "Msg" : e.message };
        }
    };

    // { "fbFuncName" : "fn_cb_source" }
	var fn_cb_source = function(parsedParams){
        const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
        vdCommon.setLogLevel("Debug");

		try {
            var comboList = vdCommon.fn_makeCombo(null, {ComboCodes : ["ERP","NSCM"], ComboValues : ["ERP","NSCM"]});
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

    // { "fbFuncName" : "fn_cb_lv4Add" }
	var fn_cb_lv4Add = function(parsedParams){
        const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
        vdCommon.setLogLevel("Debug");

		try {
            // MSL4 에 있는 데이타를 가져온다.
            var rExistMsl4 = vdCommon.selectList( ["&CWVUI", "[Item Material].[MSL4]", "[Location].[Location]"],
                                                    ["Measure.[SS Mtrl L4_Source]"],
                                                    "", "", "");
            var validHm = {};
            for ( var i = 0; i < rExistMsl4.cs.rowCount; i++ ) {
                msl4 = rExistMsl4.cs.row(i).cell(rExistMsl4.cs.memberColumnIndex("Item Material", "MSL4")).Name;

                if ( validHm[msl4] == undefined ) {
                    validHm[msl4] = msl4;
                }
            }
            //vdCommon.debug("validHm : " + JSON.stringify(validHm));

            // MSL3 데이타를 가져온다.
            var comboList = [];
            var rMsl3 = vdCommon.selectList(["&CWVUI", "[Item Material].[MSL3]"],
                                            ["Measure.[SS Mtrl L3_Sub Set]"],
                                            'where {Measure.[SS Mtrl L3_Sub Set] == "Lv4"}', "", "");
            var msl3s = "";
            for ( var i = 0; i < rMsl3.cs.rowCount; i++ ) {
                msl = rMsl3.cs.row(i).cell(rMsl3.cs.memberColumnIndex("Item Material", "MSL3")).Name;

                if ( i == 0 ) {
                    msl3s = '"' + msl + '"';
                } else {
                    msl3s += ',"' + msl + '"';
                }
            }

            // 등록되지 않은 MSL4의 데이타로 콤보를 구성한다.
            var rMSL4 = vdCommon.selectList(['[Item Material].[MSL3].filter(#.Name in {' + msl3s + '})', "&NSUIMtrlMSL4View"],
                                            [],
                                            "", "", "");
            for ( var m = 0; m < rMSL4.cs.rowCount; m++ ) {
                MSL4 = rMSL4.cs.row(m).cell(rMSL4.cs.memberColumnIndex("Item Material", "MSL4")).Name;
                if ( validHm[MSL4] == undefined ) {
                    comboList.push({ Name : MSL4, DisplayName : MSL4});
                }
            }

            // 정렬
            comboList.sort((a, b) => {
                    if ( a.Name < b.Name ) return -1;
                    if ( a.Name > b.Name ) return 1;
                    return 0;
                });

            vdCommon.programEnd();

            return { "Code" : 0, "Msg" : "", "Rows" : comboList };
        } catch ( e ) {
            vdCommon.error(e.message);
            return { "Code" : -1, "Msg" : e.message };
        }
    }

    // { "fbFuncName" : "fn_cb_lv5Add" }
	var fn_cb_lv5Add = function(parsedParams){
        const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
        vdCommon.setLogLevel("Debug");

		try {
            // MSL5 에 있는 데이타를 가져온다.
            var rExistMSL5 = vdCommon.selectList(["&CWVUI", "[Item Material].[MSL5]", "[Location].[Location]"],
                                                    ["Measure.[SS Mtrl L5_Source]"],
                                                    "", "", "");
            var validHm = {};
            for ( var i = 0; i < rExistMSL5.cs.rowCount; i++ ) {
                MSL5 = rExistMSL5.cs.row(i).cell(rExistMSL5.cs.memberColumnIndex("Item Material", "MSL5")).Name;

                if ( validHm[MSL5] == undefined ) {
                    validHm[MSL5] = MSL5;
                }
            }
            //vdCommon.debug("validHm : " + JSON.stringify(validHm));

            // MSL3 데이타를 가져온다.
            var comboList = [];
            var rMsl3 = vdCommon.selectList(["&CWVUI", "[Item Material].[MSL3]"],
                                            ["Measure.[SS Mtrl L3_Sub Set]"],
                                            'where {Measure.[SS Mtrl L3_Sub Set] == "Lv5"}', "", "");
            var msl3s = "";
            for ( var i = 0; i < rMsl3.cs.rowCount; i++ ) {
                msl = rMsl3.cs.row(i).cell(rMsl3.cs.memberColumnIndex("Item Material", "MSL3")).Name;

                if ( i == 0 ) {
                    msl3s = '"' + msl + '"';
                } else {
                    msl3s += ',"' + msl + '"';
                }
            }

            // 등록되지 않은 MSL5의 데이타로 콤보를 구성한다.
            var rMSL5 = vdCommon.selectList(['[Item Material].[MSL3].filter(#.Name in {' + msl3s + '})', "&NSUIMtrlMSL4View", "&NSUIMtrlMSL5View"],
                                            [],
                                            "", "", "");
            for ( var m = 0; m < rMSL5.cs.rowCount; m++ ) {
                MSL5 = rMSL5.cs.row(m).cell(rMSL5.cs.memberColumnIndex("Item Material", "MSL5")).Name;
                if ( validHm[MSL5] == undefined ) {
                    comboList.push({ Name : MSL5, DisplayName : MSL5});
                }
            }

            // 정렬
            comboList.sort((a, b) => {
                    if ( a.Name < b.Name ) return -1;
                    if ( a.Name > b.Name ) return 1;
                    return 0;
                });

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
            var comboList = vdCommon.fn_makeCombo(result, {DimName : "Location", DimAttbName : "Location", Sort : "Name", isDisplayNameWithCode : true});
            vdCommon.debug("ComboData : " + JSON.stringify(comboList.slice(0,3)));

            vdCommon.programEnd();

            return { "Code" : 0, "Msg" : "", "Rows" : comboList };
        } catch ( e ) {
            vdCommon.error(e.message);
            return { "Code" : -1, "Msg" : e.message };
        }
    };

    // { "fbFuncName" : "fn_cb_item", "fbParams" : { "[Item Material].[MSL3]" : "Panel>EB Panel>EB 완Panel", "[Item Material].[MSL4]" : "Panel>EB Panel>EB 완Panel>40~54" } }
	var fn_cb_item = function(parsedParams){
        const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
        vdCommon.setLogLevel("Debug");

		try {
            var msl3 = vdUtil.fn_getParam(parsedParams, "[Item Material].[MSL3]");
            var msl4 = vdUtil.fn_getParam(parsedParams, "[Item Material].[MSL4]");
            var msl5 = vdUtil.fn_getParam(parsedParams, "[Item Material].[MSL5]");

            // 등록된 데이타를 가져온다.
            var rExistItem = vdCommon.selectList(["&CWVUI",
                                                    "[Item Material].[MSL3]" + vdUtil.fn_filterStr(msl3),
                                                    "[Item Material].[MSL4]" + ( msl4 == "All" ? "" : vdUtil.fn_filterStr(msl4) ),
                                                    "[Item Material].[MSL5]" + ( msl5 == "All" ? "" : vdUtil.fn_filterStr(msl5) ),
                                                    "[Item Material].[Item Material]",
                                                    "[Location].[Location]"],
                                                ["Measure.[SS Mtrl Item_Source]"],
                                                "", "", "");

            var validHm = {};
            for ( var i = 0; i < rExistItem.cs.rowCount; i++ ) {
                item = vdCommon.getMember(rExistItem.cs, i, "Item Material", "Item Material").Name;

                if ( validHm[item] == undefined ) {
                    validHm[item] = item;
                }
            }
            //vdCommon.debug("validHm : " + JSON.stringify(validHm));

            var comboList = [];
            var rItem = vdCommon.selectList(["[Item Material].[MSL3]" + vdUtil.fn_filterStr(msl3),
                                                "[Item Material].[MSL4]" + ( msl4 == "All" ? "" : vdUtil.fn_filterStr(msl4) ),
                                                "[Item Material].[MSL5]" + ( msl5 == "All" ? "" : vdUtil.fn_filterStr(msl5) ),
                                                "[Item Material].[Item Material]"],
                                            [],
                                            "", "", "");
            for ( var i = 0; i < rItem.cs.rowCount; i++ ) {
                item = rItem.cs.row(i).cell(rItem.cs.memberColumnIndex("Item Material", "Item Material")).Name;

                if ( validHm[item] == undefined ) {
                    comboList.push({ Name : item, DisplayName : item});
                }
            }

            // 정렬
            comboList.sort((a, b) => {
                    if ( a.Name < b.Name ) return -1;
                    if ( a.Name > b.Name ) return 1;
                    return 0;
                });

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
{ "rowstatus":"U","rowindex":"0","[Version].[Version Name]":"CWV_DP","[Location].[Location]":"P551","[Item Material].[MSL3]":"Semicon.>Semicon.>Non Memory","Measure.[SS Mtrl L3_ECP Flag]":"on","Measure.[SS Mtrl L3_Source]":"NSCM","Measure.[SS Mtrl L3_Time Varying Flag]":"Y","Measure.[SS Mtrl L3_Sub Set]":"-","Measure.[SS Mtrl L3 W_Time]" : ["202520^1","202521^2","202522^3","202523^4"] }
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
                    measures.push(vdUtil.fn_qMeaStr(row, "Measure.[SS Mtrl L3_Sub Set]"));
                    vdCommon.updateMeasure(dimensions, measures);

                    dimensions = [];
                    dimensions.push(vdUtil.fn_qDimVersionName(parsedParams));
                    dimensions.push(vdUtil.fn_qDim(row, "[Location].[Location]"));
                    dimensions.push(vdUtil.fn_qDim(row, "[Item Material].[MSL3]"));
                    measures = [];
                    measures.push(vdUtil.fn_qMeaStr(row, "Measure.[SS Mtrl L3_ECP Flag]"));
                    measures.push(vdUtil.fn_qMeaStr(row, "Measure.[SS Mtrl L3_Source]"));
                    measures.push(vdUtil.fn_qMeaStr(row, "Measure.[SS Mtrl L3_Time Varying Flag]"));
                    measures.push(vdUtil.fn_qMeaUpdateUser("Measure.[SS Mtrl L3_Updated By]"));
                    measures.push(vdUtil.fn_qMeaUpdateTime("Measure.[SS Mtrl L3_Update Time]"));
                    vdCommon.updateMeasure(dimensions, measures);

                    // 주차 수정
                    var weekList = row["Measure.[SS Mtrl L3 W_Time]"];
                    var queryStr = "";
                    for ( var m = 0; m < weekList.length; m++ ) {
                        var subDimensions = [];
                        subDimensions.push(vdUtil.fn_qDimVersionName(parsedParams));
                        subDimensions.push(vdUtil.fn_qDim(row, "[Location].[Location]"));
                        subDimensions.push(vdUtil.fn_qDim(row, "[Item Material].[MSL3]"));
                        subDimensions.push("[Time].[Week].[" + weekList[m].split("^")[0] + "]");

                        var subMeasures = [];
                        subMeasures.push(vdUtil.fn_qMeaNotStr(row, "Measure.[SS Mtrl L3 W_Time]", weekList[m].split("^")[1]));

                        queryStr += vdCommon.createMeasureQuery(subDimensions, subMeasures);
                    }
                    if ( queryStr != "" ) {
                        vdCommon.executeQuery("SS Mtrl L3 W", queryStr);
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
{ "rowstatus":"C","rowindex":"0","[Version].[Version Name]":"CWV_MP","[Location].[Location]":"P105^P306","[Item Material].[MSL4]":"Elec.>Elec.>SMPS>Adaptor","Measure.[SS Mtrl L4_ECP Flag]":"on","Measure.[SS Mtrl L4_Source]":"NSCM","Measure.[SS Mtrl L4_Time Varying Flag]":"Y","Measure.[SS Mtrl L4 W_Time]" : ["202520^1","202521^2","202522^3","202523^4"] }
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
                    var location = "";
                    if ( vdUtil.fn_getString(row["[Location].[Location]"]) == "" ) {
                        location = "&NSUILocationMFMtrlView";
                    } else {
                        location = "[Location].[Location]" + vdUtil.fn_filterStr(row["[Location].[Location]"].split("^"));
                    }

                    var dimensions = [];
                    dimensions.push(vdUtil.fn_qDimVersionName(parsedParams));
                    dimensions.push(location);
                    dimensions.push(vdUtil.fn_qDim(row, "[Item Material].[MSL4]"));

                    // 등록 여부 체크
                    var count = vdCommon.selectListCount(dimensions, ["Measure.[SS Mtrl L4_ECP Flag]"], "");
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
                    var location = "";
                    if ( vdUtil.fn_getString(row["[Location].[Location]"]) == "" ) {
                        location = "&NSUILocationMFMtrlView";
                    } else {
                        location = "[Location].[Location]" + vdUtil.fn_filterStr(row["[Location].[Location]"].split("^"));
                    }

                    var dimensions = [];
                    dimensions.push(vdUtil.fn_qDimVersionName(parsedParams));
                    dimensions.push(location);
                    dimensions.push(vdUtil.fn_qDim(row, "[Item Material].[MSL4]"));

                    var measures = [];
                    measures.push(vdUtil.fn_qMeaStr(row, "Measure.[SS Mtrl L4_ECP Flag]"));
                    measures.push(vdUtil.fn_qMeaStr(row, "Measure.[SS Mtrl L4_Source]"));
                    measures.push(vdUtil.fn_qMeaStr(row, "Measure.[SS Mtrl L4_Time Varying Flag]"));
                    measures.push(vdUtil.fn_qMeaUpdateUser("Measure.[SS Mtrl L4_Created By]"));
                    measures.push(vdUtil.fn_qMeaUpdateTime("Measure.[SS Mtrl L4_Creation Time]"));

                    vdCommon.createMeasure(dimensions, measures);

                    // Week 데이타 생성
                    vdCommon.createMeasure([vdUtil.fn_qDimVersionName(parsedParams),
                                                location,
                                                vdUtil.fn_qDim(row, "[Item Material].[MSL4]"),
                                                "&MDMHorizon"],
                                            ['Measure.[SS Mtrl L4 W_Time] = 0;']);

                    var weekList = row["Measure.[SS Mtrl L4 W_Time]"];
                    var queryStr = "";
                    for ( var m = 0; m < weekList.length; m++ ) {
                        var subDimensions = [];
                        subDimensions.push(vdUtil.fn_qDimVersionName(parsedParams));
                        subDimensions.push(location);
                        subDimensions.push(vdUtil.fn_qDim(row, "[Item Material].[MSL4]"));
                        subDimensions.push("[Time].[Week].[" + weekList[m].split("^")[0] + "]");

                        var subMeasures = [];
                        subMeasures.push(vdUtil.fn_qMeaNotStr(row, "Measure.[SS Mtrl L4 W_Time]", weekList[m].split("^")[1]));

                        queryStr += vdCommon.updateMeasureQuery(subDimensions, subMeasures);
                    }
                    if ( queryStr != "" ) {
                        vdCommon.executeQuery("SS Mtrl L4 W", queryStr);
                    }
                } else if ( rowstatus == "U" ) {
                    var dimensions = [];
                    dimensions.push(vdUtil.fn_qDimVersionName(parsedParams));
                    dimensions.push(vdUtil.fn_qDim(row, "[Location].[Location]"));
                    dimensions.push(vdUtil.fn_qDim(row, "[Item Material].[MSL4]"));

                    var measures = [];
                    measures.push(vdUtil.fn_qMeaStr(row, "Measure.[SS Mtrl L4_ECP Flag]"));
                    measures.push(vdUtil.fn_qMeaStr(row, "Measure.[SS Mtrl L4_Source]"));
                    measures.push(vdUtil.fn_qMeaStr(row, "Measure.[SS Mtrl L4_Time Varying Flag]"));
                    measures.push(vdUtil.fn_qMeaUpdateUser("Measure.[SS Mtrl L4_Updated By]"));
                    measures.push(vdUtil.fn_qMeaUpdateTime("Measure.[SS Mtrl L4_Update Time]"));

                    vdCommon.updateBlockMeasure(dimensions, measures);

                    // 주차 수정
                    var weekList = row["Measure.[SS Mtrl L4 W_Time]"];
                    var queryStr = "";
                    for ( var m = 0; m < weekList.length; m++ ) {
                        var subDimensions = [];
                        subDimensions.push(vdUtil.fn_qDimVersionName(parsedParams));
                        subDimensions.push(vdUtil.fn_qDim(row, "[Location].[Location]"));
                        subDimensions.push(vdUtil.fn_qDim(row, "[Item Material].[MSL4]"));
                        subDimensions.push("[Time].[Week].[" + weekList[m].split("^")[0] + "]");

                        var subMeasures = [];
                        subMeasures.push(vdUtil.fn_qMeaNotStr(row, "Measure.[SS Mtrl L4 W_Time]", weekList[m].split("^")[1]));

                        queryStr += vdCommon.updateMeasureQuery(subDimensions, subMeasures);
                    }
                    if ( queryStr != "" ) {
                        vdCommon.executeQuery("SS Mtrl L4 W", queryStr);
                    }
                } else if ( rowstatus == "D" ) {
                    var where = [];
                    where.push(vdUtil.fn_qDimVersionName(parsedParams));
                    where.push(vdUtil.fn_qDim(row, "[Location].[Location]"));
                    where.push(vdUtil.fn_qDim(row, "[Item Material].[MSL4]"));

                    vdCommon.deleteMeasure(where, "SS Mtrl L4");
                    vdCommon.deleteMeasure(where, "SS Mtrl L4 W");
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
{ "rowstatus":"C","rowindex":"0","[Version].[Version Name]":"CWV_MP","[Location].[Location]":"P105^P306","[Item Material].[MSL5]":"Optics>Optics>Sheet>Complex>*","Measure.[SS Mtrl L5_ECP Flag]":"on","Measure.[SS Mtrl L5_Source]":"NSCM","Measure.[SS Mtrl L5_Time Varying Flag]":"Y","Measure.[SS Mtrl L5 W_Time]" : ["202520^1","202521^2","202522^3","202523^4"] }
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
                    var location = "";
                    if ( vdUtil.fn_getString(row["[Location].[Location]"]) == "" ) {
                        location = "&NSUILocationMFMtrlView";
                    } else {
                        location = "[Location].[Location]" + vdUtil.fn_filterStr(row["[Location].[Location]"].split("^"));
                    }

                    var dimensions = [];
                    dimensions.push(vdUtil.fn_qDimVersionName(parsedParams));
                    dimensions.push(location);
                    dimensions.push(vdUtil.fn_qDim(row, "[Item Material].[MSL5]"));

                    // 등록 여부 체크
                    var count = vdCommon.selectListCount(dimensions, ["Measure.[SS Mtrl L5_ECP Flag]"], "");
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
                    var location = "";
                    if ( vdUtil.fn_getString(row["[Location].[Location]"]) == "" ) {
                        location = "&NSUILocationMFMtrlView";
                    } else {
                        location = "[Location].[Location]" + vdUtil.fn_filterStr(row["[Location].[Location]"].split("^"));
                    }

                    var dimensions = [];
                    dimensions.push(vdUtil.fn_qDimVersionName(parsedParams));
                    dimensions.push(location);
                    dimensions.push(vdUtil.fn_qDim(row, "[Item Material].[MSL5]"));

                    var measures = [];
                    measures.push(vdUtil.fn_qMeaStr(row, "Measure.[SS Mtrl L5_ECP Flag]"));
                    measures.push(vdUtil.fn_qMeaStr(row, "Measure.[SS Mtrl L5_Source]"));
                    measures.push(vdUtil.fn_qMeaStr(row, "Measure.[SS Mtrl L5_Time Varying Flag]"));
                    measures.push(vdUtil.fn_qMeaUpdateUser("Measure.[SS Mtrl L5_Created By]"));
                    measures.push(vdUtil.fn_qMeaUpdateTime("Measure.[SS Mtrl L5_Creation Time]"));

                    vdCommon.createMeasure(dimensions, measures);

                    // Week 데이타 생성
                    vdCommon.createMeasure([vdUtil.fn_qDimVersionName(parsedParams),
                                                location,
                                                vdUtil.fn_qDim(row, "[Item Material].[MSL5]"),
                                                "&MDMHorizon"],
                                            ['Measure.[SS Mtrl L5 W_Time] = 0;']);

                    var weekList = row["Measure.[SS Mtrl L5 W_Time]"];
                    var queryStr = "";
                    for ( var m = 0; m < weekList.length; m++ ) {
                        var subDimensions = [];
                        subDimensions.push(vdUtil.fn_qDimVersionName(parsedParams));
                        subDimensions.push(location);
                        subDimensions.push(vdUtil.fn_qDim(row, "[Item Material].[MSL5]"));
                        subDimensions.push("[Time].[Week].[" + weekList[m].split("^")[0] + "]");

                        var subMeasures = [];
                        subMeasures.push(vdUtil.fn_qMeaNotStr(row, "Measure.[SS Mtrl L5 W_Time]", weekList[m].split("^")[1]));

                        queryStr += vdCommon.updateMeasureQuery(subDimensions, subMeasures);
                    }
                    if ( queryStr != "" ) {
                        vdCommon.executeQuery("SS Mtrl L5 W", queryStr);
                    }
                } else if ( rowstatus == "U" ) {
                    var dimensions = [];
                    dimensions.push(vdUtil.fn_qDimVersionName(parsedParams));
                    dimensions.push(vdUtil.fn_qDim(row, "[Location].[Location]"));
                    dimensions.push(vdUtil.fn_qDim(row, "[Item Material].[MSL5]"));

                    var measures = [];
                    measures.push(vdUtil.fn_qMeaStr(row, "Measure.[SS Mtrl L5_ECP Flag]"));
                    measures.push(vdUtil.fn_qMeaStr(row, "Measure.[SS Mtrl L5_Source]"));
                    measures.push(vdUtil.fn_qMeaStr(row, "Measure.[SS Mtrl L5_Time Varying Flag]"));
                    measures.push(vdUtil.fn_qMeaUpdateUser("Measure.[SS Mtrl L5_Updated By]"));
                    measures.push(vdUtil.fn_qMeaUpdateTime("Measure.[SS Mtrl L5_Update Time]"));

                    vdCommon.updateBlockMeasure(dimensions, measures);

                    // 주차 수정
                    var weekList = row["Measure.[SS Mtrl L5 W_Time]"];
                    var queryStr = "";
                    for ( var m = 0; m < weekList.length; m++ ) {
                        var subDimensions = [];
                        subDimensions.push(vdUtil.fn_qDimVersionName(parsedParams));
                        subDimensions.push(vdUtil.fn_qDim(row, "[Location].[Location]"));
                        subDimensions.push(vdUtil.fn_qDim(row, "[Item Material].[MSL5]"));
                        subDimensions.push("[Time].[Week].[" + weekList[m].split("^")[0] + "]");

                        var subMeasures = [];
                        subMeasures.push(vdUtil.fn_qMeaNotStr(row, "Measure.[SS Mtrl L5 W_Time]", weekList[m].split("^")[1]));

                        queryStr += vdCommon.updateMeasureQuery(subDimensions, subMeasures);
                    }
                    if ( queryStr != "" ) {
                        vdCommon.executeQuery("SS Mtrl L5 W", queryStr);
                    }
                } else if ( rowstatus == "D" ) {
                    var where = [];
                    where.push(vdUtil.fn_qDimVersionName(parsedParams));
                    where.push(vdUtil.fn_qDim(row, "[Location].[Location]"));
                    where.push(vdUtil.fn_qDim(row, "[Item Material].[MSL5]"));

                    vdCommon.deleteMeasure(where, "SS Mtrl L5");
                    vdCommon.deleteMeasure(where, "SS Mtrl L5 W");
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
{ "rowstatus":"C","rowindex":"1","[Version].[Version Name]":"CWV_MP","[Location].[Location]":"P551","[Item Material].[Item Material]":"BN96-56470A","Measure.[SS Mtrl Item_ECP Flag]":"off","Measure.[SS Mtrl Item_Source]":"ERP","Measure.[SS Mtrl Item_Time Varying Flag]":"N","Measure.[SS Mtrl Item W_Time]" : ["202520^1","202521^2","202522^3","202523^4"] },
{ "rowstatus":"C","rowindex":"2","[Version].[Version Name]":"CWV_MP","[Location].[Location]":"P551^P721^P406","[Item Material].[Item Material]":"BN96-60407A^BN96-50510A^BN96-12878A","Measure.[SS Mtrl Item_ECP Flag]":"on","Measure.[SS Mtrl Item_Source]":"NSCM","Measure.[SS Mtrl Item_Time Varying Flag]":"Y","Measure.[SS Mtrl Item W_Time]" : ["202520^1","202521^2","202522^3","202523^4"] }
                  ] }

- 수정 테스트
{ "fbFuncName" : "fn_saveItem", "fbParams" : { "[Version].[Version Name]" : "CWV_MP" },
  "fbGridRows" : [
{ "rowstatus":"U","rowindex":"0","[Version].[Version Name]":"CWV_MP","[Location].[Location]":"P551","[Item Material].[Item Material]":"BN96-50510A","Measure.[SS Mtrl Item_ECP Flag]":"on","Measure.[SS Mtrl Item_Source]":"NSCM","Measure.[SS Mtrl Item_Time Varying Flag]":"Y","Measure.[SS Mtrl Item W_Time]" : ["202520^1","202521^2","202522^3","202523^4"] }
                  ] }

- 삭제 테스트
{ "fbFuncName" : "fn_saveItem", "fbParams" : { "[Version].[Version Name]" : "CWV_MP" },
  "fbGridRows" : [
{ "rowstatus":"D","rowindex":"0","[Version].[Version Name]":"CWV_MP","[Location].[Location]":"P551","[Item Material].[Item Material]":"BN96-56470A","Measure.[SS Mtrl Item_ECP Flag]":"on","Measure.[SS Mtrl Item_Source]":"NSCM","Measure.[SS Mtrl Item_Time Varying Flag]":"Y","Measure.[SS Mtrl Item W_Time]" : ["202520^1","202521^2","202522^3","202523^4"] },
{ "rowstatus":"D","rowindex":"0","[Version].[Version Name]":"CWV_MP","[Location].[Location]":"P551","[Item Material].[Item Material]":"BN96-60407A","Measure.[SS Mtrl Item_ECP Flag]":"on","Measure.[SS Mtrl Item_Source]":"NSCM","Measure.[SS Mtrl Item_Time Varying Flag]":"Y","Measure.[SS Mtrl Item W_Time]" : ["202520^1","202521^2","202522^3","202523^4"] },
{ "rowstatus":"D","rowindex":"0","[Version].[Version Name]":"CWV_MP","[Location].[Location]":"P551","[Item Material].[Item Material]":"BN96-50510A","Measure.[SS Mtrl Item_ECP Flag]":"on","Measure.[SS Mtrl Item_Source]":"NSCM","Measure.[SS Mtrl Item_Time Varying Flag]":"Y","Measure.[SS Mtrl Item W_Time]" : ["202520^1","202521^2","202522^3","202523^4"] },
{ "rowstatus":"D","rowindex":"0","[Version].[Version Name]":"CWV_MP","[Location].[Location]":"P551","[Item Material].[Item Material]":"BN96-12878A","Measure.[SS Mtrl Item_ECP Flag]":"on","Measure.[SS Mtrl Item_Source]":"NSCM","Measure.[SS Mtrl Item_Time Varying Flag]":"Y","Measure.[SS Mtrl Item W_Time]" : ["202520^1","202521^2","202522^3","202523^4"] },
{ "rowstatus":"D","rowindex":"0","[Version].[Version Name]":"CWV_MP","[Location].[Location]":"P721","[Item Material].[Item Material]":"BN96-60407A","Measure.[SS Mtrl Item_ECP Flag]":"on","Measure.[SS Mtrl Item_Source]":"NSCM","Measure.[SS Mtrl Item_Time Varying Flag]":"Y","Measure.[SS Mtrl Item W_Time]" : ["202520^1","202521^2","202522^3","202523^4"] },
{ "rowstatus":"D","rowindex":"0","[Version].[Version Name]":"CWV_MP","[Location].[Location]":"P721","[Item Material].[Item Material]":"BN96-50510A","Measure.[SS Mtrl Item_ECP Flag]":"on","Measure.[SS Mtrl Item_Source]":"NSCM","Measure.[SS Mtrl Item_Time Varying Flag]":"Y","Measure.[SS Mtrl Item W_Time]" : ["202520^1","202521^2","202522^3","202523^4"] },
{ "rowstatus":"D","rowindex":"0","[Version].[Version Name]":"CWV_MP","[Location].[Location]":"P721","[Item Material].[Item Material]":"BN96-12878A","Measure.[SS Mtrl Item_ECP Flag]":"on","Measure.[SS Mtrl Item_Source]":"NSCM","Measure.[SS Mtrl Item_Time Varying Flag]":"Y","Measure.[SS Mtrl Item W_Time]" : ["202520^1","202521^2","202522^3","202523^4"] },
{ "rowstatus":"D","rowindex":"0","[Version].[Version Name]":"CWV_MP","[Location].[Location]":"P406","[Item Material].[Item Material]":"BN96-60407A","Measure.[SS Mtrl Item_ECP Flag]":"on","Measure.[SS Mtrl Item_Source]":"NSCM","Measure.[SS Mtrl Item_Time Varying Flag]":"Y","Measure.[SS Mtrl Item W_Time]" : ["202520^1","202521^2","202522^3","202523^4"] },
{ "rowstatus":"D","rowindex":"0","[Version].[Version Name]":"CWV_MP","[Location].[Location]":"P406","[Item Material].[Item Material]":"BN96-50510A","Measure.[SS Mtrl Item_ECP Flag]":"on","Measure.[SS Mtrl Item_Source]":"NSCM","Measure.[SS Mtrl Item_Time Varying Flag]":"Y","Measure.[SS Mtrl Item W_Time]" : ["202520^1","202521^2","202522^3","202523^4"] },
{ "rowstatus":"D","rowindex":"0","[Version].[Version Name]":"CWV_MP","[Location].[Location]":"P406","[Item Material].[Item Material]":"BN96-12878A","Measure.[SS Mtrl Item_ECP Flag]":"on","Measure.[SS Mtrl Item_Source]":"NSCM","Measure.[SS Mtrl Item_Time Varying Flag]":"Y","Measure.[SS Mtrl Item W_Time]" : ["202520^1","202521^2","202522^3","202523^4"] }
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
                    var count = vdCommon.selectListCount(dimensions, ["Measure.[SS Mtrl Item_ECP Flag]"], "");
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
                    measures.push(vdUtil.fn_qMeaStr(row, "Measure.[SS Mtrl Item_ECP Flag]"));
                    measures.push(vdUtil.fn_qMeaStr(row, "Measure.[SS Mtrl Item_Source]"));
                    measures.push(vdUtil.fn_qMeaStr(row, "Measure.[SS Mtrl Item_Time Varying Flag]"));
                    measures.push(vdUtil.fn_qMeaUpdateUser("Measure.[SS Mtrl Item_Created By]"));
                    measures.push(vdUtil.fn_qMeaUpdateTime("Measure.[SS Mtrl Item_Creation Time]"));

                    vdCommon.createMeasure(dimensions, measures);

                    // Week 데이타 생성
                    vdCommon.createMeasure([vdUtil.fn_qDimVersionName(parsedParams),
                                                "[Location].[Location]" + vdUtil.fn_filterStr(location.split("^")),
                                                "[Item Material].[Item Material]" + vdUtil.fn_filterStr(itemMaterial.split("^")),
                                                "&MDMHorizon"],
                                            ['Measure.[SS Mtrl Item W_Time] = 0;']);

                    var weekList = row["Measure.[SS Mtrl Item W_Time]"];
                    var queryStr = "";
                    for ( var m = 0; m < weekList.length; m++ ) {
                        var subDimensions = [];
                        subDimensions.push(vdUtil.fn_qDimVersionName(parsedParams));
                        subDimensions.push("[Location].[Location]" + vdUtil.fn_filterStr(location.split("^")));
                        subDimensions.push("[Item Material].[Item Material]" + vdUtil.fn_filterStr(itemMaterial.split("^")));
                        subDimensions.push("[Time].[Week].[" + weekList[m].split("^")[0] + "]");

                        var subMeasures = [];
                        subMeasures.push(vdUtil.fn_qMeaNotStr(row, "Measure.[SS Mtrl Item W_Time]", weekList[m].split("^")[1]));

                        queryStr += vdCommon.updateMeasureQuery(subDimensions, subMeasures);
                    }
                    if ( queryStr != "" ) {
                        vdCommon.executeQuery("SS Mtrl Item W", queryStr);
                    }
                } else if ( rowstatus == "U" ) {
                    var dimensions = [];
                    dimensions.push(vdUtil.fn_qDimVersionName(parsedParams));
                    dimensions.push(vdUtil.fn_qDim(row, "[Location].[Location]"));
                    dimensions.push(vdUtil.fn_qDim(row, "[Item Material].[Item Material]"));

                    var measures = [];
                    measures.push(vdUtil.fn_qMeaStr(row, "Measure.[SS Mtrl Item_ECP Flag]"));
                    measures.push(vdUtil.fn_qMeaStr(row, "Measure.[SS Mtrl Item_Source]"));
                    measures.push(vdUtil.fn_qMeaStr(row, "Measure.[SS Mtrl Item_Time Varying Flag]"));
                    measures.push(vdUtil.fn_qMeaUpdateUser("Measure.[SS Mtrl Item_Updated By]"));
                    measures.push(vdUtil.fn_qMeaUpdateTime("Measure.[SS Mtrl Item_Update Time]"));

                    vdCommon.updateBlockMeasure(dimensions, measures);

                    // 주차 수정
                    var weekList = row["Measure.[SS Mtrl Item W_Time]"];
                    var queryStr = "";
                    for ( var m = 0; m < weekList.length; m++ ) {
                        var subDimensions = [];
                        subDimensions.push(vdUtil.fn_qDimVersionName(parsedParams));
                        subDimensions.push(vdUtil.fn_qDim(row, "[Location].[Location]"));
                        subDimensions.push(vdUtil.fn_qDim(row, "[Item Material].[Item Material]"));
                        subDimensions.push("[Time].[Week].[" + weekList[m].split("^")[0] + "]");

                        var subMeasures = [];
                        subMeasures.push(vdUtil.fn_qMeaNotStr(row, "Measure.[SS Mtrl Item W_Time]", weekList[m].split("^")[1]));

                        queryStr += vdCommon.createMeasureQuery(subDimensions, subMeasures);
                    }
                    if ( queryStr != "" ) {
                        vdCommon.executeQuery("SS Mtrl Item W", queryStr);
                    }
                } else if ( rowstatus == "D" ) {
                    var where = [];
                    where.push(vdUtil.fn_qDimVersionName(parsedParams));
                    where.push(vdUtil.fn_qDim(row, "[Location].[Location]"));
                    where.push(vdUtil.fn_qDim(row, "[Item Material].[Item Material]"));

                    vdCommon.deleteMeasure(where, "SS Mtrl Item");
                    vdCommon.deleteMeasure(where, "SS Mtrl Item W");
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
        { "rowstatus":"C","[Location].[Location]":"P551","[Item Material].[MSL3]":"Semicon.>Semicon.>Non Memory" }
                  ] }

{ "fbFuncName" : "fn_merge"
    ,"fbParams" : { "commitType" : "1", "grid" : "Lv4"
                    ,"filters" : { "[Version].[Version Name]" : {"SelectedMembers" : ["202605_P_WI_01"], "MemberFilter" : ""} }
                    }
    ,"fbGridRows" : [
        { "rowstatus":"C","[Location].[Location]":"P551","[Item Material].[MSL4]":"Elec.>Elec.>SMPS>Adapto" }
                  ] }

{ "fbFuncName" : "fn_merge"
    ,"fbParams" : { "commitType" : "1", "grid" : "Lv5"
                    ,"filters" : { "[Version].[Version Name]" : {"SelectedMembers" : ["202605_P_WI_01"], "MemberFilter" : ""} }
                    }
    ,"fbGridRows" : [
        { "rowstatus":"C","[Location].[Location]":"P551","[Item Material].[MSL5]":"Optics>Optics>Sheet>Complex>*" }
                  ] }

{ "fbFuncName" : "fn_merge"
    ,"fbParams" : { "commitType" : "1", "grid" : "Item"
                    ,"filters" : { "[Version].[Version Name]" : {"SelectedMembers" : ["202605_P_WI_01"], "MemberFilter" : ""} }
                    }
    ,"fbGridRows" : [
        { "rowstatus":"C","[Location].[Location]":"P551","[Item Material].[Item Material]":"BN96-56470A" }
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
		        var where = 'where { Measure.[SS Mtrl L3_Updated By] == "' + name + '" || Measure.[SS Mtrl L3_Updated By] == "' + userName + '"}';

                if ( ( parsedParams.fbParams.commitType + "" ) == "0" ) {
                    // 전체이면 내가 수정한 것만 가져와서 배열을 생성
                    var result = vdCommon.selectList(["[Version].[Version Name].[" + fbVersion + "]"
                                                            ,"[Location].[Location]"
                                                            ,"[Item Material].[MSL3]"]
                                                     ,["Measure.[SS Mtrl L3_ECP Flag]"]
                                                     ,where, "", "");
                    for ( var i = 0; i < result.cs.rowCount; i++ ) {
                        parsedParams.fbGridRows.push({ "[Location].[Location]" : vdUtil.fn_getDimValue(result, i, "Location", "Location")
                                                        ,"[Item Material].[MSL3]" : vdUtil.fn_getDimValue(result, i, "Item Material", "MSL3") });
                    }
                }

                for ( var i = 0; i < parsedParams.fbGridRows.length; i++ ) {
                    var row = parsedParams.fbGridRows[i];

                    var dimensions = [];
                    dimensions.push(fbVersionName);
                    dimensions.push(vdUtil.fn_qDim(row, "[Location].[Location]"));
                    dimensions.push(vdUtil.fn_qDim(row, "[Item Material].[MSL3]"));
                    var measures = [];
                    measures.push(vdUtil.fn_qMeaForMerge("Measure.[SS Mtrl L3_ECP Flag]", fbVersion));
                    measures.push(vdUtil.fn_qMeaForMerge("Measure.[SS Mtrl L3_Source]", fbVersion));
                    measures.push(vdUtil.fn_qMeaForMerge("Measure.[SS Mtrl L3_Time Varying Flag]", fbVersion));
                    measures.push(vdUtil.fn_qMeaUpdateTime("Measure.[SS Mtrl L3_Update Time]"));
                    measures.push(vdCommon.fn_mergeUser("Measure.[SS Mtrl L3_Updated By]", fbVersion));
                    vdCommon.createMeasure(dimensions, measures);

                    dimensions = [];
                    dimensions.push(fbVersionName);
                    dimensions.push(vdUtil.fn_qDim(row, "[Item Material].[MSL3]"));
                    measures = [];
                    measures.push(vdUtil.fn_qMeaForMerge("Measure.[SS Mtrl L3_Sub Set]", fbVersion));
                    vdCommon.createMeasure(dimensions, measures);

                    dimensions = [];
                    dimensions.push(fbVersionName);
                    dimensions.push(vdUtil.fn_qDim(row, "[Location].[Location]"));
                    dimensions.push("&MDMHorizon");
                    dimensions.push(vdUtil.fn_qDim(row, "[Item Material].[MSL3]"));
                    measures = [];
                    measures.push(vdUtil.fn_qMeaForMerge("Measure.[SS Mtrl L3 W_Time]", fbVersion));
                    vdCommon.createMeasure(dimensions, measures);
                }
            } else if ( parsedParams.fbParams.grid == "Lv4" ) {
		        var where = 'where { Measure.[SS Mtrl L4_Updated By] == "' + name + '" || Measure.[SS Mtrl L4_Updated By] == "' + userName + '"}';

                if ( ( parsedParams.fbParams.commitType + "" ) == "0" ) {
                    // 전체이면 내가 수정한 것만 가져와서 배열을 생성
                    var result = vdCommon.selectList(["[Version].[Version Name].[" + fbVersion + "]"
                                                            ,"[Location].[Location]"
                                                            ,"[Item Material].[MSL4]"]
                                                     ,["Measure.[SS Mtrl L4_ECP Flag]"]
                                                     ,where, "", "");
                    for ( var i = 0; i < result.cs.rowCount; i++ ) {
                        parsedParams.fbGridRows.push({ "[Location].[Location]" : vdUtil.fn_getDimValue(result, i, "Location", "Location")
                                                        ,"[Item Material].[MSL4]" : vdUtil.fn_getDimValue(result, i, "Item Material", "MSL4") });
                    }
                }

                for ( var i = 0; i < parsedParams.fbGridRows.length; i++ ) {
                    var row = parsedParams.fbGridRows[i];

                    var dimensions = [];
                    dimensions.push(fbVersionName);
                    dimensions.push(vdUtil.fn_qDim(row, "[Location].[Location]"));
                    dimensions.push(vdUtil.fn_qDim(row, "[Item Material].[MSL4]"));
                    var measures = [];
                    measures.push(vdUtil.fn_qMeaForMerge("Measure.[SS Mtrl L4_ECP Flag]", fbVersion));
                    measures.push(vdUtil.fn_qMeaForMerge("Measure.[SS Mtrl L4_Source]", fbVersion));
                    measures.push(vdUtil.fn_qMeaForMerge("Measure.[SS Mtrl L4_Time Varying Flag]", fbVersion));
                    measures.push(vdUtil.fn_qMeaUpdateTime("Measure.[SS Mtrl L4_Update Time]"));
                    measures.push(vdCommon.fn_mergeUser("Measure.[SS Mtrl L4_Updated By]", fbVersion));
                    vdCommon.createMeasure(dimensions, measures);

                    dimensions = [];
                    dimensions.push(fbVersionName);
                    dimensions.push(vdUtil.fn_qDim(row, "[Location].[Location]"));
                    dimensions.push("&MDMHorizon");
                    dimensions.push(vdUtil.fn_qDim(row, "[Item Material].[MSL4]"));
                    measures = [];
                    measures.push(vdUtil.fn_qMeaForMerge("Measure.[SS Mtrl L4 W_Time]", fbVersion));
                    vdCommon.createMeasure(dimensions, measures);
                }
            } else if ( parsedParams.fbParams.grid == "Lv5" ) {
		        var where = 'where { Measure.[SS Mtrl L5_Updated By] == "' + name + '" || Measure.[SS Mtrl L5_Updated By] == "' + userName + '"}';

                if ( ( parsedParams.fbParams.commitType + "" ) == "0" ) {
                    // 전체이면 내가 수정한 것만 가져와서 배열을 생성
                    var result = vdCommon.selectList(["[Version].[Version Name].[" + fbVersion + "]"
                                                            ,"[Location].[Location]"
                                                            ,"[Item Material].[MSL5]"]
                                                     ,["Measure.[SS Mtrl L5_ECP Flag]"]
                                                     ,where, "", "");
                    for ( var i = 0; i < result.cs.rowCount; i++ ) {
                        parsedParams.fbGridRows.push({ "[Location].[Location]" : vdUtil.fn_getDimValue(result, i, "Location", "Location")
                                                        ,"[Item Material].[MSL5]" : vdUtil.fn_getDimValue(result, i, "Item Material", "MSL5") });
                    }
                }

                for ( var i = 0; i < parsedParams.fbGridRows.length; i++ ) {
                    var row = parsedParams.fbGridRows[i];

                    var dimensions = [];
                    dimensions.push(fbVersionName);
                    dimensions.push(vdUtil.fn_qDim(row, "[Location].[Location]"));
                    dimensions.push(vdUtil.fn_qDim(row, "[Item Material].[MSL5]"));
                    var measures = [];
                    measures.push(vdUtil.fn_qMeaForMerge("Measure.[SS Mtrl L5_ECP Flag]", fbVersion));
                    measures.push(vdUtil.fn_qMeaForMerge("Measure.[SS Mtrl L5_Source]", fbVersion));
                    measures.push(vdUtil.fn_qMeaForMerge("Measure.[SS Mtrl L5_Time Varying Flag]", fbVersion));
                    measures.push(vdUtil.fn_qMeaUpdateTime("Measure.[SS Mtrl L5_Update Time]"));
                    measures.push(vdCommon.fn_mergeUser("Measure.[SS Mtrl L5_Updated By]", fbVersion));
                    vdCommon.createMeasure(dimensions, measures);

                    dimensions = [];
                    dimensions.push(fbVersionName);
                    dimensions.push(vdUtil.fn_qDim(row, "[Location].[Location]"));
                    dimensions.push("&MDMHorizon");
                    dimensions.push(vdUtil.fn_qDim(row, "[Item Material].[MSL5]"));
                    measures = [];
                    measures.push(vdUtil.fn_qMeaForMerge("Measure.[SS Mtrl L5 W_Time]", fbVersion));
                    vdCommon.createMeasure(dimensions, measures);
                }
            } else if ( parsedParams.fbParams.grid == "Item" ) {
		        var where = 'where { Measure.[SS Mtrl Item_Updated By] == "' + name + '" || Measure.[SS Mtrl Item_Updated By] == "' + userName + '"}';

                if ( ( parsedParams.fbParams.commitType + "" ) == "0" ) {
                    // 전체이면 내가 수정한 것만 가져와서 배열을 생성
                    var result = vdCommon.selectList(["[Version].[Version Name].[" + fbVersion + "]"
                                                            ,"[Location].[Location]"
                                                            ,"[Item Material].[Item Material]"]
                                                     ,["Measure.[SS Mtrl Item_ECP Flag]"]
                                                     ,where, "", "");
                    for ( var i = 0; i < result.cs.rowCount; i++ ) {
                        parsedParams.fbGridRows.push({ "[Location].[Location]" : vdUtil.fn_getDimValue(result, i, "Location", "Location")
                                                        ,"[Item Material].[Item Material]" : vdUtil.fn_getDimValue(result, i, "Item Material", "Item Material") });
                    }
                }

                for ( var i = 0; i < parsedParams.fbGridRows.length; i++ ) {
                    var row = parsedParams.fbGridRows[i];

                    var dimensions = [];
                    dimensions.push(fbVersionName);
                    dimensions.push(vdUtil.fn_qDim(row, "[Location].[Location]"));
                    dimensions.push(vdUtil.fn_qDim(row, "[Item Material].[Item Material]"));
                    var measures = [];
                    measures.push(vdUtil.fn_qMeaForMerge("Measure.[SS Mtrl Item_ECP Flag]", fbVersion));
                    measures.push(vdUtil.fn_qMeaForMerge("Measure.[SS Mtrl Item_Source]", fbVersion));
                    measures.push(vdUtil.fn_qMeaForMerge("Measure.[SS Mtrl Item_Time Varying Flag]", fbVersion));
                    measures.push(vdUtil.fn_qMeaUpdateTime("Measure.[SS Mtrl Item_Update Time]"));
                    measures.push(vdCommon.fn_mergeUser("Measure.[SS Mtrl Item_Updated By]", fbVersion));
                    vdCommon.createMeasure(dimensions, measures);

                    dimensions = [];
                    dimensions.push(fbVersionName);
                    dimensions.push(vdUtil.fn_qDim(row, "[Location].[Location]"));
                    dimensions.push("&MDMHorizon");
                    dimensions.push(vdUtil.fn_qDim(row, "[Item Material].[Item Material]"));
                    measures = [];
                    measures.push(vdUtil.fn_qMeaForMerge("Measure.[SS Mtrl Item W_Time]", fbVersion));
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
        ,"fn_cb_ecp" :  fn_cb_ecp
        ,"fn_cb_source" : fn_cb_source
        ,"fn_cb_timeVarying" : fn_cb_timeVarying
        ,"fn_cb_lv4Add" : fn_cb_lv4Add
        ,"fn_cb_lv5Add" : fn_cb_lv5Add
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

/**************************** o9.NSCM.JSEWSafetyStockMtrl ****************************
26.02.02 : Plant 가 멀티로 들어가도록 수정
26.02.04 : fn_cb_plant 에서 옵션 변경
26.02.26 : fn_merge 추가
**************************** o9.NSCM.JSEWSafetyStockMtrl ****************************/