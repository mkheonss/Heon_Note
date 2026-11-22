define('o9.NSCM.JSMtrlSupplyPlanExcelUpload', ['o9/data/query', 'o9/data/cellset', 'o9.NSCM.commonLib'], function () {
    const programName = "o9.NSCM.JSMtrlSupplyPlanExcelUpload";

    var fn_segCombo = function(o9Params){
        try {
            const commonLib = require('o9.NSCM.commonLib');
            const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
            vdCommon.setLogLevel("Debug");

            var result = vdCommon.selectList(["&CWVUI"],
                                             ["Measure.[Mtrl Supply Plan Sub_Xls Seg]"],
                                             'where { Measure.[Mtrl Supply Plan Sub_Xls Updated By] == currentuser().Name }',
                                             "",
                                             "");

            var comboList = [];
            if ( result.cs.rowCount > 0 ) {
                var segs = result.cs.row(0).cell(result.cs.measureColumnIndex("Mtrl Supply Plan Sub_Xls Seg"));

                comboList = vdCommon.fn_makeCombo(null, {ComboCodes : segs.split(","), ComboValues : segs.split(",")});
            }
            vdCommon.debug("ComboData : " + JSON.stringify(comboList));

            vdCommon.programEnd();

            return comboList;
        } catch ( e ) {
            RuleOutputToUI = { Status : 'Error', Message : "Js Logic Error : " + e.message };
            return;
        }
    };

    var fn_delete = function(o9Params){
        const commonLib = require('o9.NSCM.commonLib');
        const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
        const vdUtil = new commonLib.VdUtil();

        try {
            vdCommon.setLogLevel("Debug");

            vdCommon.printParams(o9Params);

            // 파라미터 가져오기
            var parsedParams = JSON.parse(o9Params);
            var fbSegs = parsedParams.fbSeg;

            for ( var i = 0; i < fbSegs.length; i++ ) {
                vdCommon.deleteMeasure(["&CWVUI", 'Measure.[Mtrl Supply Plan Sub_Xls Seg] == "' + fbSegs[i] + '"'], "Mtrl Supply Plan Sub");
            }

            vdCommon.programEnd();
        } catch ( e ) {
            RuleOutputToUI = { Status : 'Error', Message : "Js Logic Error : " + e.message };
            return;
        }
    };

    return {
        fn_segCombo : fn_segCombo
        ,fn_delete : fn_delete
    };
});

/**************************** o9.NSCM.JSMtrlSupplyPlanExcelUpload ****************************
    2025-07-18 : 신규 생성
*********************************************************************/