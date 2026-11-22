define('o9.NSCM.JSExcelUploadSeg', ['o9/data/query', 'o9/data/cellset', 'o9.NSCM.commonLib'], function () {
    const programName = "o9.NSCM.JSExcelUploadSeg";

    var fn_add = function(o9Params){
        try {
            const commonLib = require('o9.NSCM.commonLib');
            const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
            vdCommon.setLogLevel("Debug");

            // 파라미터 가져오기
            var parsedParams = JSON.parse(o9Params);
            var fbSeg = parsedParams.fbSeg;

            var result = vdCommon.selectList(
                                ["&CWV",
                                    "[Seg].[Seg].[" + fbSeg + "]"],
                                ["Measure.[Excel Seg_Updated By]"],
                                "",
                                "",
                                "");
            if ( result.cs.rowCount > 0 ) {
                RuleOutputToUI = { Status : 'Error', Message : "Seg is registered." };
                return;
            } else {
                if ( !vdCommon.existMember('[Seg].[Seg]', fbSeg) ) {
                    vdCommon.createDimension(['[Seg].[Seg]'], ['"' + fbSeg + '"']);
                }

                vdCommon.createMeasure(['&CWV', '[Seg].[Seg].[' + fbSeg + ']'], ['Measure.[Excel Seg_Updated By] = Currentuser().[User Name];']);
            }

            vdCommon.programEnd();
        } catch ( e ) {
            RuleOutputToUI = { Status : 'Error', Message : "Js Logic Error : " + e.message };
            return;
        }
    };

    var fn_delete = function(o9Params){
        try {
            const commonLib = require('o9.NSCM.commonLib');
            const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
            const vdUtil = new commonLib.VdUtil();

            vdCommon.setLogLevel("Debug");

            vdCommon.printParams(o9Params);

             // 파라미터 가져오기
            var parsedParams = JSON.parse(o9Params);
            var fbSeg = parsedParams.fbSeg;

            vdCommon.deleteMeasure(["&CWV", "[Seg].[Seg].[" + fbSeg + "]"], "Excel Seg");
            vdCommon.deleteMember("[Seg].[Seg]", fbSeg);

            vdCommon.programEnd();
        } catch ( e ) {
            RuleOutputToUI = { Status : 'Error', Message : "Js Logic Error : " + e.message };
            return;
        }
    };

    return {
        fn_add : fn_add,
        fn_delete : fn_delete
    };
});