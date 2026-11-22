define('o9.NSCM.JSEWTest', ['o9/data/query', 'o9/data/cellset', 'o9.NSCM.commonLibVD'], function () {
	const programName = "o9.NSCM.JSEWTest";
    const commonLib = require('o9.NSCM.commonLibVD');

    const util = new commonLib.VDUtil();

/************************************************* UI Call Common Logic *************************************************/
	var fn_loadFunction = function(o9Params){
        const common = new commonLib.VDCommon(programName + "." + arguments.callee.name);
        common.setLogLevel("Debug");

		try {
            let returnData = {};
            let obj = this;

            common.printParams(o9Params);

            // 파라메타 가져오기
            var parsedParams = JSON.parse(o9Params);
			var fbFuncName = parsedParams.fbFuncName;

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
            
            var rtn = functionMap[fbFuncName](parsedParams);

            common.programEnd();
            return rtn;
        } catch ( e ) {
            return { "Code" : -1, "Msg" : e.message };
        }
	};

/************************************************* combo logic *************************************************/
    // { "fbFuncName" : "fn_cb_jdm" }
	var fn_cb_jdm = function(parsedParams){
        const common = new commonLib.VDCommon(programName + "." + arguments.callee.name);
        common.setLogLevel("Debug");

		try {
            var comboList = common.fn_makeCombo(null, {ComboCodes : ["Y","-"], ComboValues : ["Y","-"]});
            common.debug("ComboData : " + JSON.stringify(comboList.slice(0,3)));

            common.debug("UserId : " + common.fn_getUserName());

            let result = common.selectQueryList("fn_groupID Select", "select (&NSUILocationMFMtrlView * Location.[Company]) where { Location.[All Location].[All] } limit 10;");
            common.debug("ComboData : " + JSON.stringify(result));

            common.programEnd();

            return { "Code" : 0, "Msg" : "", "Rows" : comboList };
        } catch ( e ) {
            common.error(e.message);
            return { "Code" : -1, "Msg" : e.message };
        }
    };

    // { "fbFuncName" : "fn_cb_setInch" }
    // { "fbFuncName" : "fn_cb_setInch", "fbParams" : { "includeField" : "Item:Project:Project,Item:Basic Name:Basic Name" } }
    // { "fbFuncName" : "fn_cb_setInch", "fbParams" : { "where" : { "[Item].[Project]" : "QAQ60G", "[Item].[Basic Name]" : "QTV-F55Q60A/EU" } } }
    var fn_cb_setInch = function(parsedParams){
        const common = new commonLib.VDCommon(programName + "." + arguments.callee.name);
        common.setLogLevel("Debug");

		try {
		    var dims = ['[Item].[Inch].filter(#.Name != "-").relatedmembers([Inch])'];

            var result = common.selectList(dims, [], "", "", "");
            //vdCommon.printCsData(result, 3);
            var comboList = common.fn_makeCombo(result, {DimName : "Item", DimAttbName : "Inch", Sort : "DisplayName" });
            common.debug("ComboData : " + JSON.stringify(comboList.slice(0,3)));

            common.programEnd();

            return { "Code" : 0, "Msg" : "", "Rows" : comboList };
        } catch ( e ) {
            common.error(e.message);
            return { "Code" : -1, "Msg" : e.message };
        }
    };

/************************************************* Mapping logic *************************************************/
    const functionMap = {
        "fn_cb_jdm" : fn_cb_jdm
        ,"fn_cb_setInch" : fn_cb_setInch
    };

    return {
        fn_loadFunction : fn_loadFunction
    };
});


/**************************** o9.NSCM.JSEWTest ****************************

*********************************************************************/