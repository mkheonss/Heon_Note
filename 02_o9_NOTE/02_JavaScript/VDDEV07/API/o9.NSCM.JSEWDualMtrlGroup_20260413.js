define('o9.NSCM.JSEWDualMtrlGroup', ['o9/data/query', 'o9/data/cellset', 'o9.NSCM.commonLib'], function () {

/**************************************************************************************
    프로그램명  : o9.NSCM.JSEWDualMtrlGroup
    화면명     : Dual Mtrl Group
    화면 개발자 : 강정원 프로
    API 개발자 : sungmin0.lim
    최초생성   : 2025.9.17
**************************************************************************************/

	const programName = "o9.NSCM.JSEWDualMtrlGroup";
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
{"fbFuncName":"fn_filter_groupNameOverride","fbParams":
{ "FilterMtrlItem" : "B", "FilterSETItem" : "L",
"filters":{
    "[Version].[Version Name]":{"SelectedMembers":["CWV_MP"],"MemberFilter":"&CWVUI"},
    "[Location].[Site Group3]":{"SelectedMembers":["MF_EUROPE_SEH","MF_EUROPE_SESK","MF_CHINA_SEHZ","MF_KOREA_SEC","MF_LATIN_AMERICA_SEDA","MF_NORTH_AMERICA_SAMEX","MF_MIDDLE EAST_SEEG","MF_ETC_ETC","MF_S.E ASIA_SEHC"],"MemberFilter":"&NSUISiteGrp3MFView"},
    "[Location].[Location]":{"SelectedMembers":[],"MemberFilter":"&NSUILocationMFMtrlView"},
    "[Item Material].[MSL1]":{"SelectedMembers":[],"MemberFilter":"&NSUIMtrlMSL1View"},
    "[Item Material].[MSL2]":{"SelectedMembers":[],"MemberFilter":"&NSUIMtrlMSL2View"},
    "[Item Material].[MSL3]":{"SelectedMembers":[],"MemberFilter":"&NSUIMtrlMSL3View"},
    "[Item Material].[MSL4]":{"SelectedMembers":[],"MemberFilter":"&NSUIMtrlMSL4View"},
    "[Item Material].[MSL5]":{"SelectedMembers":[],"MemberFilter":"&NSUIMtrlMSL5View"},
    "[Item].[Item Std1]":{"SelectedMembers":["MONITOR","AV"],"MemberFilter":""},
    "[Item].[Item Std2]":{"SelectedMembers":["MONITOR_LCD_MONITOR"],"MemberFilter":""},
    "[Item].[Item Std3]":{"SelectedMembers":["MONITOR_LCD_MONITOR_NON-SMART"],"MemberFilter":""},
    "[Item].[Item Std4]":{"SelectedMembers":["MONITOR_LCD_MONITOR_NON-SMART_22"],"MemberFilter":""},
    "[Category].[Category]":{"SelectedMembers":["Dualized Mtrl Group-Master"],"MemberFilter":""}
}}}
    */
    var fn_filter_groupNameOverride = function(parsedParams){
        const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
        vdCommon.setLogLevel("Debug");

		try {
		    var dims = ["[Group].[Group ID]"];

		    var category = vdUtil.fn_getFilterValue(parsedParams, "[Category].[Category]");
		    var meas = [];
		    if ( category[0] == "Dualized Mtrl Group-Master" ) {
		        meas.push("Measure.[Dual Mtrl Anl Mst_Flag]");
		    } else {
		        meas.push("Measure.[Dual Mtrl Anl_Qty]");
		    }

		    // where 절에 필터값을 적용
            var wheres = [];
            var fq = "";
            fq = vdUtil.fn_getFilterQuery2(parsedParams, "[Version].[Version Name]");  if ( fq != "" ) wheres.push(fq);
            fq = vdUtil.fn_getFilterQuery2(parsedParams, "[Item Material].[MSL1]");  if ( fq != "" ) wheres.push(fq);
            fq = vdUtil.fn_getFilterQuery2(parsedParams, "[Item Material].[MSL2]");  if ( fq != "" ) wheres.push(fq);
            fq = vdUtil.fn_getFilterQuery2(parsedParams, "[Item Material].[MSL3]");  if ( fq != "" ) wheres.push(fq);
            fq = vdUtil.fn_getFilterQuery2(parsedParams, "[Item Material].[MSL4]");  if ( fq != "" ) wheres.push(fq);
            fq = vdUtil.fn_getFilterQuery2(parsedParams, "[Item Material].[MSL5]");  if ( fq != "" ) wheres.push(fq);
            fq = vdUtil.fn_getFilterQuery2(parsedParams, "[Location].[Site Group3]");  if ( fq != "" ) wheres.push(fq);
            fq = vdUtil.fn_getFilterQuery2(parsedParams, "[Location].[Location]");  if ( fq != "" ) wheres.push(fq);
            fq = vdUtil.fn_getFilterQuery2(parsedParams, "[Item].[Item Std1]");  if ( fq != "" ) wheres.push(fq);
            fq = vdUtil.fn_getFilterQuery2(parsedParams, "[Item].[Item Std2]");  if ( fq != "" ) wheres.push(fq);
            fq = vdUtil.fn_getFilterQuery2(parsedParams, "[Item].[Item Std3]");  if ( fq != "" ) wheres.push(fq);
            fq = vdUtil.fn_getFilterQuery2(parsedParams, "[Item].[Item Std4]");  if ( fq != "" ) wheres.push(fq);
            fq = vdUtil.fn_getFilterQuery2(parsedParams, "[Category].[Category]");  if ( fq != "" ) wheres.push(fq);
            fq = vdUtil.fn_getFilterQuery2(parsedParams, "[Time].[Week]");  if ( fq != "" ) wheres.push(fq);

            var item = vdUtil.fn_getParam(parsedParams, "FilterSETItem");
            if ( item != "" ) wheres.push("[Item].[Item]" + vdUtil.fn_filterStr(item + "%"));
            var itemMaterial = vdUtil.fn_getParam(parsedParams, "FilterMtrlItem");
            if ( itemMaterial != "" ) wheres.push("[Item Material].[Item Material]" + vdUtil.fn_filterStr(itemMaterial + "%"));

            var where = ( wheres.length == 0 ? "" : "where { " + wheres.join(", ") + " } ");

            var result = vdCommon.selectList(dims, meas, where, "", "limit 3000");
            var comboList = vdCommon.fn_makeCombo(result, {DimName : "Group", DimAttbName : "Group ID", Sort : "DisplayName"});
            vdCommon.debug("ComboData : " + JSON.stringify(comboList.slice(0,3)));

            vdCommon.programEnd();

            return { "Code" : 0, "Msg" : "", "Rows" : comboList };
        } catch ( e ) {
            vdCommon.error(e.message);
            return { "Code" : -1, "Msg" : e.message };
        }
    };


/************************************************* util logic *************************************************/

/************************************************* Mapping logic **********************************************/
    // Mapping 함수 정의, 마지막에 선언을 해야 함수를 정상적으로 인식함
    const functionMap = {
        "fn_filter_groupNameOverride" : fn_filter_groupNameOverride
    };

    return {
        fn_loadFunction : fn_loadFunction
    };
});

/**************************** o9.NSCM.JSEWDualMtrlGroup ****************************
**************************************************************************************/