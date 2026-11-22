define('o9.NSCM.JSEWSETFrozenPeriodDetail', ['o9/data/query', 'o9/data/cellset', 'o9.NSCM.commonLib'], function () {

/**************************************************************************************
    프로그램명  : o9.NSCM.JSEWSETFrozenPeriodDetail
    화면명     : SET Frozen Period(Detail)
    화면 개발자 : 김동수 프로
    API 개발자 : sungmin0.lim
    최초생성   : 2025.08.4
**************************************************************************************/

	const programName = "o9.NSCM.JSEWSETFrozenPeriodDetail";
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
{ "rowstatus":"C","rowindex":"0","[Location].[Location]":"P306","[Item].[Item]":"VG-LFF55SWG/ZA","Measure.[SET Frozen Period Detail_Release]":"4" },
{ "rowstatus":"C","rowindex":"1","[Location].[Location]":"P306","[Item].[Item]":"VG-LFF55SDG/ZA","Measure.[SET Frozen Period Detail_Release]":"5" }
                  ] }

- 수정 테스트
{ "fbFuncName" : "fn_save", "fbParams" : { "[Version].[Version Name]" : "CWV_MP" },
  "fbGridRows" : [
{ "rowstatus":"U","rowindex":"1","[Location].[Location]":"P306","[Item].[Item]":"VG-LFF55SWG/ZA","Measure.[SET Frozen Period Detail_Release]":"6" }
                  ] }

- 삭제 테스트
{ "fbFuncName" : "fn_save", "fbParams" : { "[Version].[Version Name]" : "CWV_MP" },
  "fbGridRows" : [
{ "rowstatus":"D","rowindex":"1","[Location].[Location]":"P306","[Item].[Item]":"VG-LFF55SWG/ZA","Measure.[SET Frozen Period Detail_Release]":"7" }
                  ] }
    */
    var fn_save = function(parsedParams){
        const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
        vdCommon.setLogLevel("Debug");

		try {
		    var fbVersion = parsedParams.fbParams["[Version].[Version Name]"];

		    // Validation 체크 : 등록 체크
            var validation = [];
            for ( var i = 0; i < parsedParams.fbGridRows.length; i++ ) {
                var row = parsedParams.fbGridRows[i];
                var rowstatus = row["rowstatus"];
                var rowindex = row["rowindex"];

                var count = 0;
                if ( rowstatus == "C" ) {
                    var dimensions = [];
                    dimensions.push("[Version].[Version Name].[" + fbVersion + "]");
                    dimensions.push("[Location].[Location].[" + row["[Location].[Location]"] + "]");
                    dimensions.push("[Item].[Item].[" + row["[Item].[Item]"] + "]");

                    // 등록 여부 체크
                    var count = vdCommon.selectListCount(dimensions, ["Measure.[SET Frozen Period Detail_Release]"], "");
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
                    dimensions.push("[Version].[Version Name].[" + fbVersion + "]");
                    dimensions.push("[Location].[Location].[" + row["[Location].[Location]"] + "]");
                    dimensions.push("[Item].[Item].[" + row["[Item].[Item]"] + "]");

                    var measures = [];
                    measures.push('Measure.[SET Frozen Period Detail_Release] = "' + row["Measure.[SET Frozen Period Detail_Release]"] + '";');
                    measures.push(vdUtil.fn_qMeaUpdateUserName("Measure.[SET Frozen Period Detail_Init By]"));
                    measures.push(vdUtil.fn_qMeaUpdateTime("Measure.[SET Frozen Period Detail_Init Time]"));

                    vdCommon.createMeasure(dimensions, measures);
                } else if ( rowstatus == "U" ) {
                    var dimensions = [];
                    dimensions.push("[Version].[Version Name].[" + fbVersion + "]");
                    dimensions.push("[Location].[Location].[" + row["[Location].[Location]"] + "]");
                    dimensions.push("[Item].[Item].[" + row["[Item].[Item]"] + "]");

                    var measures = [];
                    measures.push('Measure.[SET Frozen Period Detail_Release] = "' + row["Measure.[SET Frozen Period Detail_Release]"] + '";');
                    measures.push(vdUtil.fn_qMeaUpdateUserName("Measure.[SET Frozen Period Detail_Update By]"));
                    measures.push(vdUtil.fn_qMeaUpdateTime("Measure.[SET Frozen Period Detail_Update Time]"));

                    vdCommon.updateBlockMeasure(dimensions, measures);
                } else if ( rowstatus == "D" ) {
                    var where = [];
                    where.push("[Version].[Version Name].[" + fbVersion + "]");
                    where.push("[Location].[Location].[" + row["[Location].[Location]"] + "]");
                    where.push("[Item].[Item].[" + row["[Item].[Item]"] + "]");

                    vdCommon.deleteMeasure(where, "SET Frozen Period Detail");
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
        "fn_save" : fn_save
    };

    return {
        fn_loadFunction : fn_loadFunction
    };
});

/**************************** o9.NSCM.JSEWSETFrozenPeriodDetail ****************************
**************************************************************************************/

/*

Select ([Version].[Version Name].[CWV_MP] * [Location].[Location] * [Item].[Item] ) on row, ({Measure.[SET Frozen Period Detail_Init By], Measure.[SET Frozen Period Detail_Init Time], Measure.[SET Frozen Period Detail_Release], Measure.[SET Frozen Period Detail_Update By], Measure.[SET Frozen Period Detail_Update Time]}) on column;

*/