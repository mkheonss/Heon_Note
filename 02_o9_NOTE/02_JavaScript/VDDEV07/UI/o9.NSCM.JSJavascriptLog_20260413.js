define('o9.NSCM.JSJavascriptLog', ['o9/data/query', 'o9/data/cellset', 'o9.NSCM.commonLib'], function () {

/**************************************************************************************
    프로그램명  : o9.NSCM.JSJavascriptLog
    화면명     : Javascript 로그를 분리하는 소스
    API 개발자 : sungmin0.lim
    최초생성   : 2026.03.05
**************************************************************************************/

    // fn_cLib 를 통해서 commonLib 를 생성
    var fn_cLib = function(name) {
        return new commonLib.VdCommon(name);
    }
    var fn_cUtil = function() {
        return new commonLib.VdUtil();
    }

    const programName = "o9.NSCM.JSJavascriptLog";
    const commonLib = require('o9.NSCM.commonLib');
    const cUtil = fn_cUtil();

	var fn_makeLog = function(o9Params){
        const cLib = fn_cLib(programName + "." + arguments.callee.name);
        cLib.setLogLevel("Debug");

	    try {
            cLib.printParams(o9Params);

            // 파이썬 호출
            var execQuery = 'EXEC plugin instance [PY_JavascriptLog] ' +
                            'for measures {[Javascript Run Log_Full]} ' +
                            'using scope ( [Version].[Version Name].[CurrentWorkingView] ) ' +
                            'using arguments {(pVersionName, "CurrentWorkingView"), (ExecutionMode, "MediumWeight"), (MaxSliceTableCells, 200000000), (MaxConcurrency, 1 )};'
            cLib.executePython("PY_JavascriptLog", execQuery);

            cLib.programEnd();
        } catch ( e ) {
            cLib.error(e.message);
            RuleOutputToUI = { Status : 'Error', Message : "Js Logic Error : " + e.message };
            return;
        }
    };
	
    return {
        fn_makeLog : fn_makeLog
    };
});

/*************************************************************************************************************
26.03.11 - Javascript 로그는 CurrentWorkingView에 남기기로 함. 파이썬 로그도 CurrentWorkingView 로 남기게됨
****************************************** o9.NSCM.JSJavascriptLog ******************************************/