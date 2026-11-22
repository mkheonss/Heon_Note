define('o9.NSCM.JSEWCOFixedPlan', ['o9/data/query', 'o9/data/cellset', 'o9.NSCM.commonLib', 'o9.NSCM.JSEWCommonCO'], function() {	
    /*-------------------------------------------------------------------------------------------------------*/
    // 프로그램명 : o9.NSCM.JSEWCOFixedPlan
    // Action Button : EWFixedPlan
    // 화면명 : Fixed Plan
    // 2025.12.16 최초 생성                                                                         / gs9.kim */
    // 2026.02.03 그레인 변경으로 [Product Group].[Product Group] > [Item].[Product Group] 수정      / gs9.kim */
    /*-------------------------------------------------------------------------------------------------------*/

    const programName = "o9.NSCM.JSEWCOFixedPlan";
	const commonLib = require('o9.NSCM.commonLibCO');
    const coUtil = new commonLib.COUtil();
    const coCommon = new commonLib.COCommon(programName + "." + arguments.callee.name);
	
    var fn_loadFunction = function(o9Params) {
		try {
            coCommon.setLogLevel("Debug");
            coCommon.printParams(o9Params);

            // 파라메타 가져오기
            const parsedParams = JSON.parse(o9Params);
			const fbFuncName = parsedParams.fbFuncName;
            
			if ( functionMap[fbFuncName] == undefined ) {
                return { "Code" : 1, "Msg" : "No Function" };
            }

            if ( parsedParams["fbParams"] == undefined ) {
                parsedParams["fbParams"] = {};
            }
            if ( parsedParams.fbParams["includeField"] == undefined ) {
                parsedParams.fbParams["includeField"] = "";
            }
            // 조회시 기본 limit 지정( 3000개 )
            if ( parsedParams.fbParams["limit"] == undefined ) {
                parsedParams.fbParams["limit"] = "limit 3000";
            } else if ( parsedParams.fbParams["limit"] == -1 ) {
                parsedParams.fbParams["limit"] = "";    
            } else {
                parsedParams.fbParams["limit"] = "limit " + parsedParams.fbParams.limit;
            }
            // 콤보에 All 추가
            if ( parsedParams.fbParams["existAll"] == undefined ) {
                parsedParams.fbParams["existAll"] = false;
            }
            // where 조건 추가
            if ( parsedParams.fbParams["where"] == undefined ) {
                parsedParams.fbParams["where"] = {};
            }
            
            const rtn = functionMap[fbFuncName](parsedParams);
            return rtn;
        } catch ( e ) {
            return { "Code" : -1, "Msg" : e.message };
        } finally {
            coCommon.programEnd();
        }
	};

    var fn_save = function(parsedParams) {
        coCommon.debug("parsedParams :: " + JSON.stringify(parsedParams));

		try {
            const versionName = coUtil.fn_qDimVersionName(parsedParams);
            const funcName = parsedParams.fbFuncName;

            parsedParams.fbGridRows.forEach(row => {
                const rowstatus = row["rowstatus"];

                if (rowstatus == "U") {
                    fn_update(row, versionName, funcName);
                }
            });

            return { "Code" : 0, "Msg" : "It was saved successfully." };
        } catch ( e ) {
            coCommon.error(e.message);
            return { "Code" : -1, "Msg" : e.message };
        }
    };

    /*
    {	"fbFuncName" : "fn_FixedPlanWeekSave",
        "fbParams" : { "[Version].[Version Name]" : "CurrentWorkingView" },
        "fbGridRows" : [
        {
            "rowstatus":"U",
            "rowindex":"1",
            "[Sub Location].[Sub Location]":"A100",
            "[Time].[Week]":"202526",
            "[Item].[Product Group]":"MOBILE",
            "Measure.[Fixed Plan Week_ADD Week]":"15.00"
        }]
    }

    {	"fbFuncName" : "fn_FixedPlanDefaultSave",
        "fbParams" : { "[Version].[Version Name]" : "CurrentWorkingView" },
        "fbGridRows" : [
        {
            "rowstatus":"U",
            "rowindex":"1",
            "[Sub Location].[Sub Location]":"P651",
            "[Item].[Product Group]":"MOBILE",
            "Measure.[Fixed Plan Default_ORG ADD Week]":"11.00"
        }]
    }
    */
    var fn_update = function(row, versionName, funcName) {
        coCommon.debug("update row: " + JSON.stringify(row));

        const dimensions = [];
        dimensions.push(versionName);
        Object.keys(row)
          .filter(
            (key) =>
              key.startsWith("[Time].[Week]") ||
              key.startsWith("[Item].[Product Group]") ||
              key.startsWith("[Sub Location].[Sub Location]")
          )
          .forEach((key) => dimensions.push(coUtil.fn_qDim(row, key)));
        
        const measures = [];
        Object.keys(row).filter(key => key.startsWith("Measure.")).forEach(key => measures.push(coUtil.fn_qMeaStr(row, key)));

        measures.push(coUtil.fn_qMeaUpdateTime(`Measure.[Fixed Plan ${funcName === "fn_FixedPlanWeekSave" ? "Week" : "Default"}_Update time]`));
        measures.push(`Measure.[Fixed Plan ${funcName === "fn_FixedPlanWeekSave" ? "Week" : "Default"}_Updated by]=CurrentUser().[User Name];`);

        coCommon.updateMeasure(dimensions, measures);
    }

    const functionMap = {
        "fn_FixedPlanWeekSave" : fn_save,
        "fn_FixedPlanDefaultSave" : fn_save
    };

    return {
        fn_loadFunction : fn_loadFunction
    };    
});