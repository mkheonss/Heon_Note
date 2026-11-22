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

    var fn_delete = function(o9Params){
        const cLib = fn_cLib(programName + "." + arguments.callee.name);
        cLib.setLogLevel("Debug");

	    try {
            cLib.printParams(o9Params);

            var p = JSON.parse(o9Params);

            var where = [];
            where.push("[Version].[Version Name].[CurrentWorkingView]");

            if ( p.fbDay != "All" ) {
                var nowTime = new Date();
                nowTime.setHours(nowTime.getHours() + 9);
                var day = nowTime.getFullYear() + "-"
                            + cUtil.fn_lpad((nowTime.getMonth() + 1) + "", 2, "0") + "-"
                            + cUtil.fn_lpad(nowTime.getDate() + "", 2, "0");

                var result = cLib.selectList(['&AllDays.filter(#.Key == &AllDays.filter(#.Name == "' + day + '").element(0).LeadOffset(' + p.fbDay + ').Key)'], [], "", "", "");
                if ( result.cs.rowCount > 0 ) {
                    where.push('[Time].[Day].filter(#.Name <= "' + cUtil.fn_getDimValue(result, 0, "Time", "Day") + '")');
                }
            }

            cLib.deleteMeasure(where, "Javascript Run Log");
            cLib.deleteMeasure(where, "Javascript Error Log");

            cLib.programEnd();
        } catch ( e ) {
            cLib.error(e.message);
            RuleOutputToUI = { Status : 'Error', Message : "Js Logic Error : " + e.message };
            return;
        }
    };

    var fn_dayCombo = function(o9Params){
        const cLib = fn_cLib(programName + "." + arguments.callee.name);
        cLib.setLogLevel("Debug");

        try {
            var comboList = cLib.fn_makeCombo(null, {ComboCodes : ["All","-5","-10","-15","-20","-25","-30"], ComboValues : ["All","-5","-10","-15","-20","-25","-30"]});
            cLib.debug("ComboData : " + JSON.stringify(comboList.slice(0,3)));

            cLib.programEnd();

            return comboList;
        } catch ( e ) {
            cLib.error(e.message);
            RuleOutputToUI = { Status : 'Error', Message : "Js Logic Error : " + e.message };
            return;
        }
    };

    return {
        fn_makeLog : fn_makeLog
        ,fn_dayCombo : fn_dayCombo
        ,fn_delete : fn_delete
    };
});

/*************************************************************************************************************
26.03.11 - Javascript 로그는 CurrentWorkingView에 남기기로 함. 파이썬 로그도 CurrentWorkingView 로 남기게됨
26.04.02 - fn_dayCombo, fn_delete 추가
****************************************** o9.NSCM.JSJavascriptLog ******************************************/