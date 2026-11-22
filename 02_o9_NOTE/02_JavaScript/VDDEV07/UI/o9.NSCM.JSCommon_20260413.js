define('o9.NSCM.JSCommon', ['o9/data/query', 'o9/data/cellset', 'o9.NSCM.commonLib'], function () {
    const programName = "o9.NSCM.JSCommon";

    var gfn_dummyCombo = function(o9Params){
        try {
            const commonLib = require('o9.NSCM.commonLib');
            const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
            vdCommon.setLogLevel("Debug");

            var comboList = [];
            comboList.push({ Name : "-", DisplayName : "-"});

            vdCommon.programEnd();

            return comboList;
        } catch ( e ) {
            vdCommon.error(e.message);
            RuleOutputToUI = { Status : 'Error', Message : "Js Logic Error : " + e.message };
            return;
        }
    };

    var gfn_filterWeekCombo = function(o9Params){
        try {
            const commonLib = require('o9.NSCM.commonLib');
            const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
            vdCommon.setLogLevel("Debug");

            vdCommon.printParams(o9Params);

            // 파라미터 가져오기
            var parsedParams = JSON.parse(o9Params);
            var fbWeek = parsedParams.fbWeek.split(",");

            var comboList = [];
            for ( var i = 0; i < fbWeek.length; i++ ) {
                comboList.push({ Name : fbWeek[i], DisplayName : fbWeek[i] });
            }
            vdCommon.debug("ComboData : " + JSON.stringify(comboList));

            vdCommon.programEnd();

            return comboList;
        } catch ( e ) {
            vdCommon.error(e.message);
            RuleOutputToUI = { Status : 'Error', Message : "Js Logic Error : " + e.message };
            return;
        }
    };

    return {
        gfn_dummyCombo : gfn_dummyCombo,
        gfn_filterWeekCombo : gfn_filterWeekCombo
    };
});

/**************************** o9.NSCM.JSCommon ****************************
    gfn_dummyCombo
        - 기능 : filter 의 값을 가지고 ds를 호출하기 위해 임시 Combo로 만들어서 cascadeFrom 에 연결해서 사용함
    gfn_filterWeekCombo
        - 기능 : filter 에 있는 Week 로 Week Combo 를 만든다.
        - 파라미터 : fbWeek
*********************************************************************/