define('o9.NSCM.JSSimulationManagement', ['o9/data/query', 'o9/data/cellset', 'o9.NSCM.commonLibVD'], function () {
	const programName = "o9.NSCM.JSSimulationManagement";
    const commonLib = require('o9.NSCM.commonLib');
    const vdUtil = new commonLib.VdUtil();
    const log = new commonLib.VdCommon(programName);
    log.setLogLevel("Debug");

    var fn_validation = function(o9Params){
        const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
        vdCommon.setLogLevel("Debug");
        vdCommon.printParams(o9Params);

        var rtn = 0;

        try {
            // 파라미터 가져오기
            var p = JSON.parse(o9Params);

            if ( p.Version.length > 1 ) {
                RuleOutputToUI = { Status : 'Error', Message : "Plan을 하나만 선택하세요." };
                return 1;
            } else {
                var CurrentWeek = vdCommon.selectResult('&CurrentWeek.element(0).DisplayName');
                vdCommon.debug("CurrentWeek : " + CurrentWeek);

                // 당주인지 체크
                if ( CurrentWeek != p.Version[0].substr(0,6) ) {
                    RuleOutputToUI = { Status : 'Error', Message : "당주 Plan으로 다시 선택하세요." };
                    return 1;
                }

                // Rerun인지 체크
                var result = vdCommon.selectList(["[Version].[Version Name]" + vdUtil.fn_filterStr(p.Version)],
                                                 ["Measure.[Scenario Master_Plan Status]"],
                                                 "", "", "");
                var planStatus = vdUtil.fn_getMeaValue(result, 0, "Scenario Master_Plan Status");
                vdCommon.debug("Plan Status : " + planStatus);
                if ( planStatus == "Completed") {
                    RuleOutputToUI = { Status : 'Error', Message : "해당 Plan으로 ReRun은 불가능합니다." };
                    return 1;
                }

                // 동일 주차에 실행이 있는지 체크
                
                var result = vdCommon.selectList(["&Sim" + vdUtil.fn_filterStr(CurrentWeek + "%")],
                                                 ["Measure.[Scenario Master_Plan Status]"],
                                                 'where { Measure.[Scenario Master_Plan Status] == "Running" }', "", "");
                if ( result.cs.rowCount > 0 ) {
                    RuleOutputToUI = { Status : 'Error', Message : "현재 Running 중인 Plan이 있습니다." };
                    return 1;
                }
                

                // Objective Set이 있는지 체크
                var result = vdCommon.selectList(["[Version].[Version Name]" + vdUtil.fn_filterStr(p.Version)],
                                                 ["Measure.[Scenario Master_Objective_Group]"],
                                                 "", "", "");
                                                 
                var planGroup = result.cs.row(0).cell(result.cs.measureColumnIndex("Scenario Master_Objective_Group"));
                vdCommon.debug("Plan Group : " + planGroup);
                
                if (typeof planGroup == 'undefined'){
                    RuleOutputToUI = { Status : 'Error', Message : "해당 Plan은 Objective Set이 지정되지 않았습니다." };
                    return 1;
                }
                
            }

            vdCommon.programEnd();
        } catch ( e ) {
            RuleOutputToUI = { Status : 'Error', Message : "Js Logic Error : " + e.message };
            return 1;
        }

        return rtn;
    };



    var fn_validation_edit = function(o9Params){
        const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
        vdCommon.setLogLevel("Debug");
        vdCommon.printParams(o9Params);

        var rtn = 0;

        try {
            // 파라미터 가져오기
            var p = JSON.parse(o9Params);

            var CurrentWeek = vdCommon.selectResult('&CurrentWeek.element(0).DisplayName');
            vdCommon.debug("CurrentWeek : " + CurrentWeek);

            if ( p.Version.length > 1 ) {
                RuleOutputToUI = { Status : 'Error', Message : "Plan을 하나만 선택하세요." };
                return 1;
            } else {
                // 당주인지 체크
                if ( CurrentWeek != p.Version[0].substr(0,6) ) {
                    RuleOutputToUI = { Status : 'Error', Message : "당주 Plan으로 다시 선택하세요." };
                    return 1;
                }
            }

            vdCommon.programEnd();
        } catch ( e ) {
            RuleOutputToUI = { Status : 'Error', Message : "Js Logic Error : " + e.message };
            return 1;
        }

        return rtn;
    };



    return {
        fn_validation : fn_validation,
        fn_validation_edit : fn_validation_edit
    };
});

/**************************************************************************************
프로그램명  : o9.NSCM.JSSimulationManagement
화면명     : Simulation Management
개발자     : sungmin0.lim
최초생성   : 2025.10.21
AB        : PlanRun
**************************************************************************************/