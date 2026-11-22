define('o9.NSCM.JSEWCompareDashBoard', ['o9.NSCM.commonLibDA'], function (commonLib) {
	const programName = "o9.NSCM.JSEWCompareDashBoard";
   /* setting  */
    let daCommon = new commonLib.DACommon(programName);
    daCommon.setLogLevel("Debug")
    let daUtil = new commonLib.DAUtil();

/************************************************* UI Call Common Logic *************************************************/
	var fn_loadFunction = function(o9Params){
		try {
            // 파라메타 가져오기
            var parsedParams = JSON.parse(o9Params);
            var fbFuncName = parsedParams.fbFuncName;
        //    Log.Info(`##########################JSEWCompareDashBoard`);
           var rtn = functionMap[fbFuncName](parsedParams);
           return rtn;
        } catch ( e ) {
            return { "Code" : -1, "Msg" : e.message };
        }
	};

/************************************************* combo logic *************************************************/
    // { "fbFuncName" : "fn_cb_planWeek" }
    // { "fbFuncName" : "fn_setItem", "fbParams" : { "[Item].[Product Group]" : "TV", "[Item].[Definition]" : "ACCESSORY", "[Item].[Item]" : "PSN42%" } }
    let fn_cb_planWeek = function(parsedParams){
		try {
            /* 설계서상에 Benchmark Plan 당주~2주전 까지의 Time.Week */
            let resultSet = QueryCommon.selectPlanWeek();
            /*  DisplayName(Code)  combo return */
            let comboList = daCommon.fn_makeCombo(resultSet, {DimName : "Time", DimAttbName : "Week", isDisplayNameWithCode : false});
            return { "Code" : 0, "Msg" : "", "Rows" : comboList };
        } catch ( e ) {
            daCommon.error("fn_cb_planWeek Error");
            return { "Code" : -1, "Msg" : e.message };
        }
    };

    let fn_cb_planWeek_version = function(parsedParams){
        try{
            let resultSet;
            let currentWeek = "";
            if(daUtil.fn_getString(parsedParams.fbParams.planWeek) == ""){
                resultSet = QueryCommon.selectCurrentWeek(parsedParams);
                parsedParams.fbParams.planWeek = daCommon.getMember(resultSet.cs, 0, "Time", "Week").Name;
            }
            //Benchmark Plan week param으로 받아 PlanWeek에 대한 Version을 가져온다.
            resultSet = QueryCommon.selectPlanWeekVersion(parsedParams);
            /*  DisplayName(Code)  combo return */
            let comboList = daCommon.fn_makeCombo(resultSet, {DimName : "Version", DimAttbName : "Version Name", Sort : "DisplayName", isDisplayNameWithCode : false});
            return { "Code" : 0, "Msg" : "", "Rows" : comboList };
        }catch(e){
            daCommon.error("fn_cb_planWeek_version Error");
            return { "Code" : -1, "Msg" : "fn_cb_planWeek_version" };
        }
    }

/************************************************* Mapping logic *************************************************/
    // Mapping 함수 정의, 마지막에 선언을 해야 함수를 정상적으로 인식함
    const functionMap = {
        "fn_cb_planWeek" : fn_cb_planWeek,
        "fn_cb_planWeek_version" : fn_cb_planWeek_version,
    };

    class QueryCommon {
        static selectPlanWeek(){
            let query = `
                select (&AllWeeks.Filter(#.Key >= &CurrentWeek.element(0).LeadOffset(-2).Key && #.Key <= &CurrentWeek.element(0).LeadOffset(0).Key)) on row orderby Time.Week.Key desc;
            `;
            return daCommon.selectQueryList('selectPlanWeek', query);
        }

        static selectCurrentWeek(params){
            let query = `
                select (&CurrentWeek);
            `;
            return daCommon.selectQueryList('selectCurrentWeek', query);
        }
        //select (&CurrentWeek);

        static selectPlanWeekVersion(params){
            let query = `
                select (&NSMPVersionsForSimulUI.filter(#.[Plan Week] == "${params.fbParams.planWeek}"));
            `;
            return daCommon.selectQueryList('selectPlanWeek', query);
        }
    }

    return {
        fn_loadFunction : fn_loadFunction
    };
});