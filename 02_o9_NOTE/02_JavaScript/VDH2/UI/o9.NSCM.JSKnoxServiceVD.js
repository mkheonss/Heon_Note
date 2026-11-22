define('o9.NSCM.JSKnoxServiceVD', ['o9/data/query', 'o9/data/cellset', 'o9.NSCM.commonLibVD'], function () {

/**************************************************************************************
    프로그램명  : o9.NSCM.JSKnoxServiceVD
    화면명     : Knox 후처리 서비스 ( 모듈별로 정의 필요 )
    API 개발자 : sungmin0.lim
    최초생성   : 2026.02.09
**************************************************************************************/

    // fn_cLib 를 통해서 commonLib 를 생성
    var fn_cLib = function(name) {
        return new commonLib.VdCommon(name);
    }
    var fn_cUtil = function() {
        return new commonLib.VdUtil();
    }

	const programName = "o9.NSCM.JSKnoxServiceVD";
    const commonLib = require('o9.NSCM.commonLibVD');
    const cUtil = fn_cUtil();

/************************************************* common logic *************************************************/
/*
    ... 서비스
*/
    var fn_knoxTest = function(status, o9Params){
        const cLib = fn_cLib(programName + "." + arguments.callee.name);
        cLib.setLogLevel("Debug");
        var rtnMsg = "";
		try {
		    var p = JSON.parse(o9Params);

            cLib.printParams(o9Params);

            // 결재를 올린 대상들의 상태를 업데이트 한다.
            for ( var i = 0; i < p.approvalList.length; i++ ) {
                var row = p.approvalList[i];

                var dimensions = [];
                dimensions.push(cUtil.fn_qDim(row, "[Version].[Version Name]"));
                dimensions.push(cUtil.fn_qDim(row, "[Location].[Location]"));
                dimensions.push(cUtil.fn_qDim(row, "[Seq].[Seq]"));

                var measures = [];
                measures.push(cUtil.fn_qMeaStr(null, "Measure.[Knox Test_Status]", status));

                // 완결(2) 이면 후처리 실행
                if ( status == "2" ) {
                    measures.push(cUtil.fn_qMeaStr(null, "Measure.[Knox Test_Post Process Result]", "처리 했어요...."));
                }
                cLib.updateMeasure(dimensions, measures);
            }

            cLib.programEnd();
        } catch ( e ) {
            cLib.error(e.message);
            rtnMsg = e.message;
        }

        return rtnMsg;
    };

/*
    var fn_service1 = function(o9Params){
        const cLib = fn_cLib(programName + "." + arguments.callee.name);
        cLib.setLogLevel("Debug");

        var rtnMsg = "1111111111";

		try {
            cLib.debug("파라미터 : " + o9Params);

            cLib.printParams(o9Params);

		    var p = JSON.parse(o9Params);

            cLib.programEnd();
        } catch ( e ) {
            cLib.error(e.message);
            rtnMsg = e.message;
        }

        return rtnMsg;
    };

    var fn_service2 = function(o9Params){
        const cLib = fn_cLib(programName + "." + arguments.callee.name);
        cLib.setLogLevel("Debug");

        var rtnMsg = "2222222";

		try {
            cLib.debug("파라미터 : " + o9Params);

            cLib.printParams(o9Params);

		    var p = JSON.parse(o9Params);

            cLib.programEnd();
        } catch ( e ) {
            cLib.error(e.message);
            rtnMsg = e.message;
        }

        return rtnMsg;
    };
*/

    return {
        fn_knoxTest : fn_knoxTest
    };
});

/************************************************* o9.NSCM.JSKnoxServiceVD *************************************************
************************************************* o9.NSCM.JSKnoxServiceVD *************************************************/