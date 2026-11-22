define('o9.NSCM.JSEWAccountPricePlan', ['o9/data/query', 'o9/data/cellset', 'o9.NSCM.commonLibVD'], function(){

    /*--------------------------------------------------------------------------------------------------*/
    // 프로그램명 : o9.NSCM.JSEWAccountPricePlan
    // 화면명 : Account Price Plan(EW)
    // UI 설명: 
    // Action Button : EWAccountPricePlan
    // 최초생성 : 2026.03.23 / syif1380.lee
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

    const programName = "o9.NSCM.JSEWAccountPricePlan";
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
     * {"fbFuncName" : "fn_save", 
        "fbParams" : {"filters":{"[Version].[Version Name]":{"SelectedMembers":["CWV_MP"],"MemberFilter":"&CWVUI"}}}
        ,"fbGridRows":[
        {"rowstatus":"U"
        ,"groupkey":"0,0,0,0,0"
        ,"[Sales Domain].[Ship To]":"226"
        ,"[Item].[Item]":"HW-B650F/ZD"
        ,"Measure.[Account Price PL_Valid]":"N"
        ,"Measure.[Account Price PL_Start Dttm]":"2026-03-13 05:35:42"
        ,"Measure.[Account Price PL_End Dttm]":"2026-03-13 05:35:46"
        } ]
        }
     * @param {*} o9Params 
     * @returns 
     */
    var fn_save = function(parsedParams){
        const cLib = fn_cLib(programName + "." + arguments.callee.name);
        cLib.setLogLevel("Debug");

        try {
            cLib.debug("parsedParams :: "+JSON.stringify(parsedParams));

            cLib.debug("fn_getFilterValue >> "+cUtil.fn_getFilterValue(parsedParams, "[Version].[Version Name]"));
            cLib.debug("fn_qDimVersionName >> "+cUtil.fn_qDimVersionName(parsedParams));

            for ( var i=0; i<parsedParams.fbGridRows.length; i++){

                let row = parsedParams.fbGridRows[i];
                let rowstatus = row["rowstatus"];

                // dimension 정의
                let dimension = [];
                // dimension.push(cUtil.fn_qDimVersionName(parsedParams));
                dimension.push(cUtil.fn_qDim(null, "[Version].[Version Name]", cUtil.fn_getFilterValue(parsedParams, "[Version].[Version Name]")));
                dimension.push(cUtil.fn_qDim(row, "[Sales Domain].[Ship To]"));
                dimension.push(cUtil.fn_qDim(row, "[Item].[Item]"));

                let measure = [];
                measure.push(cUtil.fn_qMeaStr(row, "Measure.[Account Price PL_Valid]"));
                measure.push(cUtil.fn_qMeaStr(row, "Measure.[Account Price PL_Start Dttm]"));
                measure.push(cUtil.fn_qMeaStr(row, "Measure.[Account Price PL_End Dttm]"));
                measure.push(cUtil.fn_qMeaUpdateUserName("Measure.[Account Price PL_Updated By]"));
                measure.push(cUtil.fn_qMeaUpdateTime("Measure.[Account Price PL_Update Time]"));

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
    프로그램명 : o9.NSCM.JSEWAccountPricePlan
    화면명 : Account Price Plan(EW)
    Action Button : EWAccountPricePlan
    [history]
    2026.03.26 : commonLib 선언 부분 변경 및 공통함수 이름 변경
*/
/*--------------------------------------------------------------------------------------------------*/