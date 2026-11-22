define('o9.NSCM.JSEWAdditionPanelMaster', ['o9/data/query', 'o9/data/cellset', 'o9.NSCM.commonLibVD'], function(){

    /*--------------------------------------------------------------------------------------------------*/
    // 프로그램명 : o9.NSCM.JSEWAdditionPanelMaster
    // 화면명 : Addition Panel Master (EW)
    // UI 설명: 이원화 GRP별 패널확정구간 (로직 기반 자동 구성) / SOP 제안 주차 (실행주차 마스터 참고하여 구성)
    // Action Button : EWAdditionPanelMaster
    // 최초생성 : 2026.04.09 / syif1380.lee
    /*--------------------------------------------------------------------------------------------------*/

    // fn_cLib 를 통해서 commonLib 를 생성 // 2026.03.26 공통적용변경
    var fn_cLib = function(name) {
        return new commonLib.VdCommon(name);
    }
    var fn_cUtil = function() {
        return new commonLib.VdUtil();
    }
        
    const commonLib = require('o9.NSCM.commonLibVD');
    const cUtil = fn_cUtil();

    const programName = "o9.NSCM.JSEWAdditionPanelMaster";
    // const Horizon = "&MPHorizon";

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

            var rtn = functionMap[fbFuncName](parsedParams);

            cLib.programEnd();
            return rtn;
        } catch ( e ) {
            cLib.error(e.message);
            return { "Code" : -1, "Msg" : e.message };
        }
	};

    /**
     * fn_save : 저장
     * 하단 그리드 저장 : Addition Panel Suggestion Master
     *  - 상단 그리드 : 조회용 (I/F Data)
     * 
     * @param {*} o9Params 
     * @returns 
     */
    var fn_save = function(parsedParams){
        const cLib = fn_cLib(programName + "." + arguments.callee.name);
        cLib.setLogLevel("Debug");

        try {
            cLib.debug("parsedParams :: "+JSON.stringify(parsedParams));
            for ( var i=0; i<parsedParams.fbGridRows.length; i++){

                let row = parsedParams.fbGridRows[i];
                let rowstatus = row["rowstatus"];

                // dimension 정의
                let dimension = [];
                dimension.push(cUtil.fn_qDimVersionName(parsedParams));
                dimension.push(cUtil.fn_qDim(row, "[Location].[Location]"));
                dimension.push(cUtil.fn_qDim(row, "[Group].[Group ID]"));

                let measure = [];
                measure.push(cUtil.fn_qMeaInt(row, "Measure.[Add Panel Sgst Mst_ADD Sgst]"));	        // Integer
                measure.push(cUtil.fn_qMeaStr(row, "Measure.[Add Panel Sgst Mst_Min Max Flag]"));
                measure.push(cUtil.fn_qMeaStr(row, "Measure.[Add Panel Sgst Mst_Valid Flag]"));
                measure.push(cUtil.fn_qMeaUpdateUserName("Measure.[Add Panel Sgst Mst_Updated by]"));
                measure.push(cUtil.fn_qMeaUpdateTime("Measure.[Add Panel Sgst Mst_Update time]"));

                if ( rowstatus == "U" ) {
                    cLib.updateMeasure(dimension, measure);
                }
            }

            cLib.programEnd();

            return { "Code" : 0, "Msg" : "", "Rows" : ""};  // 오류 dataset Return

        } catch ( e ) {
            cLib.error(e.message);
            return { "Code" : -1, "Msg" : e.message };
        }
    };


    // Mapping 함수 정의, 마지막에 선언을 해야 함수를 정상적으로 인식함
    const functionMap = {
        "fn_save"       : fn_save
    };

    return {
        fn_loadFunction : fn_loadFunction
    };

});

/*--------------------------------------------------------------------------------------------------*/
/* 
    프로그램명 : o9.NSCM.JSEWAdditionPanelMaster
    화면명 : Addition Panel Master (EW)
    Action Button : EWAdditionPanelMaster
    [history]

*/
/*--------------------------------------------------------------------------------------------------*/