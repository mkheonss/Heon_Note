define('o9.NSCM.JSBuildAheadCalendar', ['o9/data/query', 'o9/data/cellset', 'o9.NSCM.commonLib'], function () {
    const programName = "o9.NSCM.JSBuildAheadCalendar";

    var fn_mustCombo = function(o9Params){
        try {
            const commonLib = require('o9.NSCM.commonLib');
            const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
            vdCommon.setLogLevel("Debug");

            var comboList = vdCommon.fn_makeCombo(null, {ComboCodes : ["Y","N","-"], ComboValues : ["Y","N","Null"]});
            vdCommon.debug("ComboData : " + JSON.stringify(comboList));

            vdCommon.programEnd();

            return comboList;
        } catch ( e ) {
            RuleOutputToUI = { Status : 'Error', Message : "Js Logic Error : " + e.message };
            return;
        }
    };

    var fn_update = function(o9Params){
        try {
            const commonLib = require('o9.NSCM.commonLib');
            const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
            const vdUtil = new commonLib.VdUtil();

            vdCommon.setLogLevel("Debug");

            vdCommon.printParams(o9Params);

            // 파라미터 가져오기
            var parsedParams = JSON.parse(o9Params);
            var fbMust = parsedParams.fbMust;
            var fbSelect = parsedParams.fbSelect;

            for ( var i = 0; i < fbSelect.length; i++ ) {
                var row = fbSelect[i];

                if ( fbMust == "-" ) {
                    vdCommon.updateMeasure(["&CWVUI",
                                                "[Sales Domain].[AP2].[" + row.Ap2.Value + "]",
                                                "Location.[Location].[" + row.Location.Value + "]",
                                                "[Sub Location].[Sub Location].[" + row.SubLocation.Value + "]",
                                                "Item.[Item].[" + row.Item.Value + "]"],
                                            ['Measure.[Build Ahead Item_Valid] = Measure.[Build Ahead Item_Valid Org];',
                                                vdUtil.fn_qMeaStr(null, "Measure.[Build Ahead Item_Must]", ""),
                                                vdUtil.fn_qMeaUpdateTime("Measure.[Build Ahead Item_Update time]"),
                                                vdUtil.fn_qMeaUpdateUserName("Measure.[Build Ahead Item_Updated by]")]);
                } else {
                    vdCommon.updateMeasure(["&CWVUI",
                                                "[Sales Domain].[AP2].[" + row.Ap2.Value + "]",
                                                "Location.[Location].[" + row.Location.Value + "]",
                                                "[Sub Location].[Sub Location].[" + row.SubLocation.Value + "]",
                                                "Item.[Item].[" + row.Item.Value + "]"],
                                            [vdUtil.fn_qMeaStr(null, "Measure.[Build Ahead Item_Valid]", fbMust),
                                                vdUtil.fn_qMeaStr(null, "Measure.[Build Ahead Item_Must]", fbMust),
                                                vdUtil.fn_qMeaUpdateTime("Measure.[Build Ahead Item_Update time]"),
                                                vdUtil.fn_qMeaUpdateUserName("Measure.[Build Ahead Item_Updated by]")]);
                }
            }

            vdCommon.programEnd();
        } catch ( e ) {
            RuleOutputToUI = { Status : 'Error', Message : "Js Logic Error : " + e.message };
            return;
        }
    };

    return {
        fn_mustCombo : fn_mustCombo,
        fn_update : fn_update
    };
});

/**************************** Modify Log ****************************
    20254-11-19 : MG 를 "Build Ahead Cal" 에서 "Build Ahead Item" 로 변경
*********************************************************************/