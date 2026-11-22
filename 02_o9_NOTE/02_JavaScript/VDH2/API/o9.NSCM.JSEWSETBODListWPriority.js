define('o9.NSCM.JSEWSETBODListWPriority', ['o9/data/query', 'o9/data/cellset', 'o9.NSCM.commonLib'], function(){

    /*--------------------------------------------------------------------------------------------------*/
    /* 프로그램명 : o9.NSCM.JSEWSETBODListWPriority                                                     */
    /* 화면명 : SET BOD List W Priority (EW)                                                            */
    /* Action Button : EWSETBODListWPriority                                                            */
    /* 최초생성 : 2025.06.20 / syif1380.lee                                                             */
    /*--------------------------------------------------------------------------------------------------*/

    const programName = "o9.NSCM.JSEWSETBODListWPriority";
    const commonLib = require('o9.NSCM.commonLib');
    const vdUtil = new commonLib.VdUtil();

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

            var rtn = functionMap[fbFuncName](parsedParams);

            vdCommon.programEnd();
            return rtn;
        } catch ( e ) {
            vdCommon.error(e.message);
            return { "Code" : -1, "Msg" : e.message };
        }
	};

    /**
     * Reload Master
     * 배치 실행 프로그램
     * @param {*} o9Params 
     * @returns 
     */
    var fn_execution = function(parsedParams){
        const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
        vdCommon.setLogLevel("Debug");

        try {
            vdCommon.debug("parsedParams :: "+JSON.stringify(parsedParams));

            // Reload Master, Supply Type, Validation 실행
            // EXEC procedure PR_UI_BODListWSET_Daily;
            var execQuery = 'EXEC procedure PR_UI_BODListWSET_Daily;';
            vdCommon.debug("execQuery: " + JSON.stringify(execQuery));
            vdCommon.executeQuery("procedure Reload Master : PR_UI_BODListWSET_Daily Run", execQuery);

            vdCommon.programEnd();

            return { "Code" : 0, "Msg" : "", "Rows" : "" };

        } catch ( e ) {
            vdCommon.error(e.message);
            return { "Code" : -1, "Msg" : e.message };
        }
    };

    // Mapping 함수 정의, 마지막에 선언을 해야 함수를 정상적으로 인식함
    const functionMap = {
        "fn_execution" : fn_execution
    };

    return {
        fn_loadFunction : fn_loadFunction
    };

});


/*--------------------------------------------------------------------------------------------------*/
/* 프로그램명 : o9.NSCM.JSEWSETBODListWPriority
   화면명 : SET BOD List W Priority (EW)
   Action Button : EWSETBODListWPriority
   [history]
   2025.06.20 | syif1380.lee | fn_execution 이름변경

*/
/*--------------------------------------------------------------------------------------------------*/