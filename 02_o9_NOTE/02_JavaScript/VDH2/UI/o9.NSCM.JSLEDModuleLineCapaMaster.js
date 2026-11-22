define('o9.NSCM.JSLEDModuleLineCapaMaster', ['o9/data/query', 'o9/data/cellset', 'o9.NSCM.commonLib'], function () {

    const programName = "o9.NSCM.JSLEDModuleLineCapaMaster";

    var fn_save = function(o9Params) {
        try {
            const commonLib = require('o9.NSCM.commonLib');
            const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
            const vdUtil = new commonLib.VdUtil();
            
            vdCommon.setLogLevel("Debug");
            vdCommon.printParams(o9Params);

            // 파라미터 가져오기
            var parsedParams = JSON.parse(o9Params);

            /* Validation 호출 (PY_UI_LED_ModuleLineConsumeItem) */
            var execQuery = 'EXEC plugin instance [PY_UI_LED_ModuleLineConsumeItem] ' +
                            'for measures {[Module Line Capa Master LED_Capa Consume Item]} ' +
                            'using scope ( &MPV ) ' +
                            'using arguments {(ExecutionMode, "MediumWeight"), ("IncludeNullRows", "False"), (paramOutVersion , "CWV_MP"), (MaxSliceTableCells, 200000000), (MaxConcurrency, 1), ([Param.o9_sys_log_level], "DEBUG")};  ';
        
            vdCommon.debug("execQuery: " + JSON.stringify(execQuery));
            vdCommon.executeQuery("fn_save : PY_UI_LED_ModuleLineConsumeItem Run", execQuery);

            vdCommon.programEnd();
        } catch ( e ) {
            RuleOutputToUI = { Status : 'Error', Message : "Js Logic Error : " + e.message };
            return;
        }
    };

    return {
        fn_save : fn_save,
    };
});