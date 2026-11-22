define('o9.NSCM.JSEWLCMPOSend', ['o9/data/query', 'o9/data/cellset', 'o9.NSCM.commonLibVD'], function(){

    /*--------------------------------------------------------------------------------------------------*/
    // 프로그램명 : o9.NSCM.JSEWLCMPOSend
    // 화면명 : LCM PO Send (EW)
    // UI 설명: LCM PO Send 에 따라 ERP PO 정보 I/F 진행, 수출향 물량 PO 발행 및 관리를 위한 운영 UI
    // Action Button : EWLCMPOSend
    // 최초생성 : 2026.02.19 / syif1380.lee
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

    const programName = "o9.NSCM.JSEWLCMPOSend";
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

                // dimension 정의
                let dimension = [];
                dimension.push(cUtil.fn_qDimVersionName(parsedParams));
                dimension.push(cUtil.fn_qDim(row, "[Location].[Location]"));
                dimension.push(cUtil.fn_qDim(row, "[To Item].[To Item]"));
                dimension.push(cUtil.fn_qDim(row, "[Item].[Item]"));
                dimension.push(cUtil.fn_qDim(row, "[Sub Location].[Sub Location]"));
                dimension.push(cUtil.fn_qDim(row, "[Trans Mode].[Trans Mode]"));
                dimension.push(cUtil.fn_qDim(row, "[Vendor].[Vendor]"));
                dimension.push(cUtil.fn_qDim(row, "[Sequence].[Sequence]"));

                let measure = [];
                measure.push(cUtil.fn_qMeaStr(row, "Measure.[LCM PO Send_Currency]"));
                measure.push(cUtil.fn_qMeaStr(row, "Measure.[LCM PO Send_DOMEXP]"));
                measure.push(cUtil.fn_qMeaStr(row, "Measure.[LCM PO Send_ETA Week]"));
                measure.push(cUtil.fn_qMeaStr(row, "Measure.[LCM PO Send_ETD Week]"));
                measure.push(cUtil.fn_qMeaStr(row, "Measure.[LCM PO Send_Incoterms1]"));
                measure.push(cUtil.fn_qMeaStr(row, "Measure.[LCM PO Send_Incoterms2]"));
                measure.push(cUtil.fn_qMeaStr(row, "Measure.[LCM PO Send_Lot Size]"));
                measure.push(cUtil.fn_qMeaStr(row, "Measure.[LCM PO Send_MFG Week]"));
                measure.push(cUtil.fn_qMeaStr(row, "Measure.[LCM PO Send_Mst Check]"));
                measure.push(cUtil.fn_qMeaStr(row, "Measure.[LCM PO Send_Org Vendor]"));
                measure.push(cUtil.fn_qMeaStr(row, "Measure.[LCM PO Send_PO Item]"));
                measure.push(cUtil.fn_qMeaStr(row, "Measure.[LCM PO Send_PO No]"));
                measure.push(cUtil.fn_qMeaStr(row, "Measure.[LCM PO Send_PO Status]"));
                measure.push(cUtil.fn_qMeaInt(row, "Measure.[LCM PO Send_POP ID]"));			// Integer
                measure.push(cUtil.fn_qMeaInt(row, "Measure.[LCM PO Send_POP Qty]"));		    // Integer
                measure.push(cUtil.fn_qMeaStr(row, "Measure.[LCM PO Send_Plant]"));
                measure.push(cUtil.fn_qMeaInt(row, "Measure.[LCM PO Send_Price]"));			// Number
                measure.push(cUtil.fn_qMeaStr(row, "Measure.[LCM PO Send_Pur Grp]"));
                measure.push(cUtil.fn_qMeaStr(row, "Measure.[LCM PO Send_Pur Org]"));
                measure.push(cUtil.fn_qMeaStr(row, "Measure.[LCM PO Send_SLoc]"));
                measure.push(cUtil.fn_qMeaInt(row, "Measure.[LCM PO Send_SOP Qty]"));	        // Integer
                measure.push(cUtil.fn_qMeaStr(row, "Measure.[LCM PO Send_Status]"));

                // add 없음 I/F Data
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
        "fn_save"    : fn_save
    };

    return {
        fn_loadFunction : fn_loadFunction
    };

});

/*--------------------------------------------------------------------------------------------------*/
/* 
    프로그램명 : o9.NSCM.JSEWLCMPOSend
    화면명 : LCM PO Send (EW)
    Action Button : EWLCMPOSend
    [history]
    2026.03.26 : commonLib 선언 부분 변경 및 공통함수 이름 변경
*/
/*--------------------------------------------------------------------------------------------------*/