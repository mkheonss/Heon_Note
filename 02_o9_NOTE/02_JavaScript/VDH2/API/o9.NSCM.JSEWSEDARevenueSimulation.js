define('o9.NSCM.JSEWSEDARevenueSimulation', ['o9/data/query', 'o9/data/cellset', 'o9.NSCM.commonLibVD'], function(){

    /*--------------------------------------------------------------------------------------------------*/
    // 프로그램명 : o9.NSCM.JSEWSEDARevenueSimulation
    // 화면명 : SEDA Revenue Simulation (EW)
    // Action Button : EWSEDARevenueSimulation
    // EW 개발자 : 미정
    // 최초생성 : 2026.01.23 / syif1380.lee
    /*--------------------------------------------------------------------------------------------------*/

    // fn_cLib 를 통해서 commonLib 를 생성 // 2026.03.26 공통적용변경
    var fn_cLib = function(name) {
        return new commonLib.VdCommon(name);
    }
    var fn_cUtil = function() {
        return new commonLib.VdUtil();
    }
        
    const commonLib = require('o9.NSCM.commonLibVD');   // 2026.03.26 공통적용변경
    const cUtil = fn_cUtil();                           // 2026.03.26 공통적용변경

    const programName = "o9.NSCM.JSEWSEDARevenueSimulation";

    //================================= 공통 콤보 사용 ===============================//
    // Action Button : EWCommonVD
    //================================================================================//

	var fn_loadFunction = function(o9Params){
        const cLib = fn_cLib(programName + "." + arguments.callee.name);
        cLib.setLogLevel("Debug");

		try {
            cLib.printParams(o9Params);

            // 파라메타 가져오기
            var parsedParams = JSON.parse(o9Params);
			var fbFuncName = parsedParams.fbFuncName;

            if ( functionMap[fbFuncName] == undefined ) {
                return { "Code" : 1, "Msg" : "No Function" };
            }

            var rtn = functionMap[fbFuncName](parsedParams);

            cLib.programEnd();
            return rtn;
        } catch ( e ) {
            cLib.error(e.message);
            return { "Code" : -1, "Msg" : e.message };
        }
	};

    /**
     * Period Setting
     * 
     * @param {*} o9Params 
     * @returns 
     */
    var fn_savePeriod = function(parsedParams){
        const cLib = fn_cLib(programName + "." + arguments.callee.name);
        cLib.setLogLevel("Debug");

        try {
            cLib.debug("parsedParams :: "+JSON.stringify(parsedParams));

            for ( var i=0; i<parsedParams.fbGridRows.length; i++){

                var row = parsedParams.fbGridRows[i];
                var rowstatus = row["rowstatus"];

                let dimension = [];
                dimension.push(cUtil.fn_qDimVersionName(parsedParams));
                // dimension.push(cUtil.fn_qDim(row, "[Version].[Version Name]"));
                dimension.push(cUtil.fn_qDim(row, "[Category].[Category]"));

                let measure = [];
                measure.push(cUtil.fn_qMeaInt(row, "Measure.[LT Ratio Master_Period]"));

                if ( !cLib.existMeasure(dimension,["Measure.[LT Ratio Master_Period]"], "")){
                    cLib.createMeasure(dimension, measure);
                }else{
                    cLib.updateMeasure(dimension, measure);
                }
            } // end for

            if( parsedParams.fbGridRows.length > 0){
                fn_callPyUIRevenueSimulation(parsedParams);
            }

            cLib.programEnd();
            
            return { "Code" : 0, "Msg" : "", "Rows" : "" };

        } catch ( e ) {
            cLib.error(e.message);
            return { "Code" : -1, "Msg" : e.message };
        }
    };

    /**
     * PY 호출 : PY_UI_RevenueSimulation
     * 
     * @param {*} parsedParams 
     * @returns 
     */
    var fn_callPyUIRevenueSimulation = function(parsedParams){
        const cLib = fn_cLib(programName + "." + arguments.callee.name);
        cLib.setLogLevel("Debug");

        try {
            cLib.debug("PY_UI_RevenueSimulation ==========================================================>");

            let fbCategory = [...new Set(parsedParams.fbGridRows.map(row => row["[Category].[Category]"]))];

            var execQuery = 'EXEC plugin instance [PY_UI_RevenueSimulation] for measures {[LT Ratio Rslt W_GIBLLT Qty]}'
                            +' using scope ( &MPV '
                            +' * [Category].[Category]'+cUtil.fn_filterStr(fbCategory)
                            +' ) '
                            +' using arguments {(ExecutionMode, "MediumWeight"), ("IncludeNullRows", "False"), (paramOutVersion , "CWV_MP"), (MaxSliceTableCells, 200000000), (MaxConcurrency, 1), ([Param.o9_sys_log_level], "DEBUG")}; ';

                cLib.debug("execQuery: " + JSON.stringify(execQuery));
                cLib.executeQuery("PY_UI_RevenueSimulation Run", execQuery);

        } catch ( e ) {
            cLib.error(e.message);
            return { "Code" : -1, "Msg" : e.message };
        }
    };

    const functionMap = {
        "fn_savePeriod"    : fn_savePeriod
    };

    return {
        fn_loadFunction : fn_loadFunction
    };

});

/*--------------------------------------------------------------------------------------------------*/
/* 
    프로그램명 : o9.NSCM.JSEWSEDARevenueSimulation
    화면명 : SEDA Revenue Simulation (EW)
    Action Button : EWSEDARevenueSimulation
    [history]
    2026.03.26 : commonLib 선언 부분 변경 및 공통함수 이름 변경
*/
/*--------------------------------------------------------------------------------------------------*/