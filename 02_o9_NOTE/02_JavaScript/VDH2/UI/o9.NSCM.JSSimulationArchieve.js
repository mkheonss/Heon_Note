define('o9.NSCM.JSSimulationArchieve', ['o9/data/query', 'o9/data/cellset', 'o9.NSCM.commonLibVD'], function () {
	const programName = "o9.NSCM.JSSimulationArchieve";
    const commonLib = require('o9.NSCM.commonLib');
    const vdUtil = new commonLib.VdUtil();
    const log = new commonLib.VdCommon(programName);
    log.setLogLevel("Debug");

    var fn_archieve = function(o9Params){
        const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
        vdCommon.setLogLevel("Debug");
        vdCommon.printParams(o9Params);

        try {
            // 파라미터 가져오기
            var p = JSON.parse(o9Params);

            var CurrentWeek = vdCommon.selectResult('&CurrentWeek.element(0).DisplayName');
            vdCommon.debug("CurrentWeek : " + CurrentWeek);

            var result = vdCommon.selectList(['[Version].[Version Name].filter(#.ScenarioType == "Simulation")'],
                                             ["Measure.[Scenario Master_Scenario Type]"],
                                             'where {Measure.[Scenario Master_Scenario Type] == "What-If", Measure.[Scenario Master_Scenario Status] == "Editable"}', "", "");
            for ( var i = 0; i < result.cs.rowCount; i++ ) {
                var name = result.cs.row(i).cell(result.cs.memberColumnIndex("Version", "Version Name")).Name;
                var key = result.cs.row(i).cell(result.cs.memberColumnIndex("Version", "Version Name")).Key;

                if ( name.substr(0,6) < CurrentWeek ) {
                    vdCommon.debug("name : " + name + " , key : " + key);
                    vdCommon.executeQuery("Create Version", 'CreateVersion(' + key + ',"' + name + '_Archived", false, false);');
                    vdCommon.executeQuery("Delete Version", 'DeleteVersion("' + name + '");');
                    vdCommon.executeQuery("Update Member", 'updatemember(Version.[Version Name]={,"' + name + '_Archived"},Version.[ScenarioType]={"Simulation",});');

                    vdCommon.updateMeasure(["[Version].[Version Name].[" + name + "]"],
                                            ['Measure.[Scenario Master_Scenario Status] = "Uneditable";']);
                }
            }

            vdCommon.programEnd();
        } catch ( e ) {
            RuleOutputToUI = { Status : 'Error', Message : "Js Logic Error : " + e.message };
        }
    };

    return {
        fn_archieve : fn_archieve
    };
});

/**************************************************************************************
프로그램명  : o9.NSCM.JSSimulationArchieve
화면명     : Simulation Archieve
개발자     : sungmin0.lim
최초생성   : 2025.10.28
AB        : ABSimulationArchieve
**************************************************************************************/