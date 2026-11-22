define('o9.NSCM.JSEWProblemList', ['o9/data/query', 'o9/data/cellset', 'o9.NSCM.commonLibVD'], function () {

/**************************************************************************************
    프로그램명  : o9.NSCM.JSEWProblemList
    화면명     : Problem List
    화면 설계자 : 정현석 프로
    화면 개발자 :
    API 개발자 : sungmin0.lim
    최초생성   : 2026.03.04
**************************************************************************************/


    // fn_cLib 를 통해서 commonLib 를 생성
    var fn_cLib = function(name) {
        return new commonLib.VdCommon(name);
    }
    var fn_cUtil = function() {
        return new commonLib.VdUtil();
    }

    const programName = "o9.NSCM.JSEWProblemList";
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
{ "fbFuncName" : "fn_summary"
    ,"fbParams" : { "filters" : {"[Version].[Version Name]" : {"SelectedMembers" : ["CWV_MP"], "MemberFilter" : "" }
                                   ,"[Sales Domain].[Sales Std1]" : {"SelectedMembers" : ["1111"], "MemberFilter" : "" }
                                }
                  }
}
*/
    var fn_summary = function(parsedParams){
        const cLib = fn_cLib(programName + "." + arguments.callee.name);
        cLib.setLogLevel("Debug");

		try {
            cLib.printParams(parsedParams);

		    var version = cUtil.fn_getFilterVersion(parsedParams);

            var summary = { "version" : cUtil.fn_getDimensionValue(version), demandQty : 0, shortQty : 0, shortRatio : 0};

            // 필터조건 추가
            var where = [];
            var query = cUtil.fn_getFilterQuery2(parsedParams, "[Sales Domain].[Sales Std1]");
            if ( query != "" ) where.push(query);
            var query = cUtil.fn_getFilterQuery2(parsedParams, "[Sales Domain].[Sales Std2]");
            if ( query != "" ) where.push(query);
            var query = cUtil.fn_getFilterQuery2(parsedParams, "[Sales Domain].[Sales Std3]");
            if ( query != "" ) where.push(query);
            var query = cUtil.fn_getFilterQuery2(parsedParams, "[Sales Domain].[Sales Std4]");
            if ( query != "" ) where.push(query);
            var query = cUtil.fn_getFilterQuery2(parsedParams, "[Item].[Item Std1]");
            if ( query != "" ) where.push(query);
            var query = cUtil.fn_getFilterQuery2(parsedParams, "[Item].[Item Std2]");
            if ( query != "" ) where.push(query);
            var query = cUtil.fn_getFilterQuery2(parsedParams, "[Item].[Item Std3]");
            if ( query != "" ) where.push(query);
            var query = cUtil.fn_getFilterQuery2(parsedParams, "[Item].[Item Std4]");
            if ( query != "" ) where.push(query);
            var query = cUtil.fn_getFilterQuery2(parsedParams, "[Location].[Site Group1]");
            if ( query != "" ) where.push(query);
            var query = cUtil.fn_getFilterQuery2(parsedParams, "[Location].[Site Group2]");
            if ( query != "" ) where.push(query);
            var query = cUtil.fn_getFilterQuery2(parsedParams, "[Location].[Site Group3]");
            if ( query != "" ) where.push(query);
            var query = cUtil.fn_getFilterQuery2(parsedParams, "[Location].[Site Group4]");
            if ( query != "" ) where.push(query);
            var query = cUtil.fn_getFilterQuery2(parsedParams, "[Problem Type].[Short Reason]");
            if ( query != "" ) where.push(query);
            var query = cUtil.fn_getFilterQuery2(parsedParams, "[FCST Type].[FCST Type]");
            if ( query != "" ) where.push(query);
            var query = cUtil.fn_getFilterQuery2(parsedParams, "[AIR Idx].[AIR Idx]");
            if ( query != "" ) where.push(query);
            var query = cUtil.fn_getFilterQuery2(parsedParams, "[Time].[Week]");
            if ( query != "" ) where.push(query);

            var whereStr = "";
            if ( where.length > 0 ) {
                whereStr = 'where { ' + where.join(", ") + ' }';
            }

            var result = cLib.selectList([version]
                                             ,["Measure.[Problem Anl_Needed Qty]"
                                                ,"Measure.[Problem Anl_Short Qty]"]
                                             ,whereStr, "", "");
            if ( result.cs.rowCount > 0 ) {
                summary.demandQty = cUtil.fn_getMeaValue(result, 0, "Problem Anl_Needed Qty");
                summary.shortQty = cUtil.fn_getMeaValue(result, 0, "Problem Anl_Short Qty");
                summary.shortRatio = ((summary.shortQty / summary.demandQty) * 100).toFixed(1);
            }

            return { "Code" : 0, "Rows" : summary };
        } catch ( e ) {
            cLib.error(e.message);
            return { "Code" : -1, "Msg" : e.message };
        } finally {
            cLib.programEnd();
        }
    };


/************************************************* util logic *************************************************/

/************************************************* Mapping logic **********************************************/
    // Mapping 함수 정의, 마지막에 선언을 해야 함수를 정상적으로 인식함
    const functionMap = {
        "fn_summary" : fn_summary
    };

    return {
        fn_loadFunction : fn_loadFunction
    };
});

/***********************************************************************************************************


**************************************** o9.NSCM.JSEWProblemList *******************************************/