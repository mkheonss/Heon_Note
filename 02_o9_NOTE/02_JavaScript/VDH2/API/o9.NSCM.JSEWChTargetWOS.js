define('o9.NSCM.JSEWChTargetWOS', ['o9/data/query', 'o9/data/cellset', 'o9.NSCM.commonLibVD'], function(){

    /*--------------------------------------------------------------------------------------------------*/
    // 프로그램명 : o9.NSCM.JSEWChTargetWOS
    // 화면명 : Ch Target WOS (EW)
    // Action Button : EWChTargetWOS
    // 최초생성 : 2026.01.29 / syif1380.lee
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

    const programName = "o9.NSCM.JSEWChTargetWOS";
    const Horizon = "&MPHorizon";

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
     * 
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
                let w_AdjWOS = row["Measure.[Ch Target WOS W_Adj WOS]"];    // "Measure.[Ch Target WOS W_Adj WOS]":["202601^1","202602^2","202603^3"]

                // BOD Item 의 dimension 정의
                let dimension = [];
                dimension.push(cUtil.fn_qDimVersionName(parsedParams));
                dimension.push(cUtil.fn_qDim(row, "[Sales Domain].[Ship To]"));
                dimension.push(cUtil.fn_qDim(row, "[Item].[Segment]"));
                // dimension.push(cUtil.fn_qDim(row, "[Time].[Week]"));

                let dimensionDel = [];
                dimensionDel.push(cUtil.fn_qDimVersionName(parsedParams));
                dimensionDel.push(cUtil.fn_qDim(row, "[Sales Domain].[Ship To]"));
                dimensionDel.push(cUtil.fn_qDim(row, "[Item].[Segment]"));
                dimensionDel.push(Horizon);

                let measure = [];
                measure.push(cUtil.fn_qMeaUpdateUserName("Measure.[Ch Target WOS W_Updated By]"));
                measure.push(cUtil.fn_qMeaUpdateTime("Measure.[Ch Target WOS W_Update Time]"));

                let measureChk = ["Measure.[Ch Target WOS W_Adj WOS]", "Measure.[Ch Target WOS W_WOS]", "Measure.[Ch Target WOS W_Qty]", "Measure.[Ch Target WOS W_Create Time]", "Measure.[Ch Target WOS W_Update Time]"];

                // rowstatus == "C" 없음 : 배치 Data 생성

                if ( rowstatus == "U" ) {
                    for ( var k=0; k < w_AdjWOS.length; k++){

                        let value = w_AdjWOS[k].split("^"); // ["202601^1","202602^2","202603^3"]

                        let dimensionW = [...dimension];
                        dimensionW.push(cUtil.fn_qDim(null, "[Time].[Week]", value[0]));

                        let measureUpdate = [...measure];
                        measureUpdate.push(cUtil.fn_qMeaInt(null, "Measure.[Ch Target WOS W_Adj WOS]", value[1]));
                        measureUpdate.push("Measure.[Ch Target WOS W_Del Flag] = 0;");
                        measureUpdate.push("Measure.[Ch Target WOS W_Exist Flag] = 1;");

                        cLib.debug(" #### Update : dimensionW >> "+JSON.stringify(dimensionW));
                        cLib.debug(" #### Update : measureUpdate >> "+JSON.stringify(measureUpdate));

                        if ( !cLib.existMeasure(dimensionW, measureChk, "")) {
                            cLib.createMeasure(dimensionW, measureUpdate);
                        } else {
                            cLib.updateMeasure(dimensionW, measureUpdate);
                        }
                    }
                    
                }else if ( rowstatus == "D" ) {
                    cLib.debug(" #### Delete : dimensionDel >> "+JSON.stringify(dimensionDel));

                    let measureDelete = [...measure];
                    measureDelete.push("Measure.[Ch Target WOS W_Adj WOS] = null;");
                    measureDelete.push("Measure.[Ch Target WOS W_Del Flag] = 1;");
                    cLib.updateMeasure(dimensionDel, measureDelete);

                    // cLib.deleteMeasure(dimensionDel, "Ch Target WOS W");
                }
            }

            cLib.programEnd();

            //  정상 저장 후 리턴 값?? Warn 종류는 저장은 되고, 화면으로 메세지 리턴해줘야 함
            return { "Code" : 0, "Msg" : "", "Rows" : ""};  // 오류 dataset Return

        } catch ( e ) {
            cLib.error(e.message);
            return { "Code" : -1, "Msg" : e.message };
        }
    };

    // Mapping 함수 정의, 마지막에 선언을 해야 함수를 정상적으로 인식함
    const functionMap = {
        "fn_save"    : fn_save
    };

    return {
        fn_loadFunction : fn_loadFunction
    };

});

/*--------------------------------------------------------------------------------------------------*/
/* 
    프로그램명 : o9.NSCM.JSEWChTargetWOS
    화면명 : Channel Target WOS (EW)
    Action Button : EWChTargetWOS
    [history]
    2026.01.30 : Delete 기능 W_Del Flag, W_Adj WOS = null 로 변경
    2026.03.26 : commonLib 선언 부분 변경 및 공통함수 이름 변경
*/
/*--------------------------------------------------------------------------------------------------*/