define('o9.NSCM.JSPreConfiguredScenario', ['o9/data/query', 'o9/data/cellset', 'o9.NSCM.commonLib'], function () {
    const programName = "o9.NSCM.JSPreConfiguredScenario";

	var PreConfiguredScenario = function(o9Params){
	    try {
            const commonLib = require('o9.NSCM.commonLib');
            const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
            const vdUtil = new commonLib.VdUtil();

            vdCommon.setLogLevel("Debug");
            vdCommon.printParams(o9Params);

            var p = JSON.parse(o9Params);

            var currentWeek = vdCommon.selectResult('&CurrentWeek.element(0).DisplayName');
            var nextWeek = vdCommon.selectResult('&NextWeek.element(0).DisplayName');

            var sVersionKey = "";
            var nVersion = "";
            var sVersion = "";
            var planType = "Pre-Configured";
            var scenarioType = "";
            if ( p.ScenarioType == "Pre-Configured Pre" ) {
                sVersionKey = vdCommon.selectResult('Version.[Version Name].[CWV_MP_INI_PRE].Key');
                sVersion = currentWeek + '_P';
                nVersion = currentWeek + '_P_PC_01';
                scenarioType = "Pre-Configured Pre";
            } 

            vdCommon.debug("sVersionKey : " + sVersionKey + " , nVersion : " + nVersion + " , planType : " + planType + " , scenarioType : " + scenarioType);

            if ( p.ScenarioType == "Pre-Configured Pre" ) {
                // Current Running Flag 업데이트
                var result = vdCommon.selectList(['[Version].[Version Name].filter(#.[Plan Type] == "Pre-Configured" && #.[Current Running Flag] == true)'], [], "", "", "");
                for ( var i = 0; i < result.cs.rowCount; i++ ) {
                    var versionName = vdUtil.fn_getDimValue(result, i, "Version", "Version Name");

                    vdCommon.executeQuery("Current Running Flag = false", 'updatemember( Version.[Version Name]={,"' + versionName + '"}, ' +
                                                                            ' [Version].[Current Running Flag]={false,});');
                }

                // CWV_MP_INI_PRE를 소스로 현재주차 PC버전 생성.
                vdCommon.executeQuery("Delete Scenario", 'deleteversion("' + nVersion + '");');
                vdCommon.executeQuery("Create Scenario", 'createscenario(' + sVersionKey + ',"' + nVersion + '");');
                vdCommon.executeQuery("Update Scenario", 'updatemember(Version.[Version Name]={,"' + nVersion + '"},' +
                                                            '[Version].[Plan Type]={"' + planType + '",}, ' +
                                                            '[Version].[Version Expiry Date]={dateadd(Now(),12,"week"),},' +
                                                            '[Version].[ScenarioType]={"' + scenarioType + '",}, ' +
                                                            '[Version].[Current Running Flag]={true,} ' +
                                                            ');');


                // 26-01-30 : Scenario Masater에 Create & Update
                vdCommon.createMeasure(["[Version].[Version Name].[" + nVersion + "]"]
                            ,['Measure.[Scenario Master_Source Scenario Name] = Version.[Version Name].[' + sVersion + '].DisplayName;'
                                ,'Measure.[Scenario Master_Scenario Status] = "Editable";'
                                ,'Measure.[Scenario Master_Plan Status] = "Not Started";'
                                ,'Measure.[Scenario Master_Scenario Expiry Date] = dateadd(Now(),12,"week");'
                                ,'Measure.[Scenario Master_Creation Time] = Now();'
                                ,'Measure.[Scenario Master_Update Time] = Now();'
                                ]);
                vdCommon.updateMeasure(["[Version].[Version Name].[" + nVersion + "]"]
                            ,['Measure.[Scenario Master_Objective_Group] = Measure.[Scenario Master_Objective_Group]@([Version].[Version Name].[CWV_OBJ_PRE]);'
                                ,'Measure.[Scenario Master_PlanGroup] = Measure.[Scenario Master_PlanGroup]@([Version].[Version Name].[CWV_OBJ_PRE]);'
                                ,'Measure.[Scenario Master_Objective_Group Description] = Measure.[Scenario Master_Objective_Group Description]@([Version].[Version Name].[CWV_OBJ_PRE]);'
                                ,'Measure.[Scenario Master_Source Scenario Name] = "' + currentWeek + '_P' + '";'
                                ,'Measure.[Scenario Master_Scenario Type] = "' + scenarioType + '";'
                                ]);
                vdCommon.updateMeasure(["[Version].[Version Name].[CWV_OBJ_PRE]"]
                            ,['Measure.[Scenario Master_Source Scenario Name] = "' + nextWeek + '_P' +'";'
                                ]);

                // 26-03-05 : SDX LPS Active Group Picklist에 Create
                vdCommon.createMeasure(["[Version].[Version Name].[" + nVersion + "]"]
                                ,['Measure.[SDX LPS Active Group Picklist] = Null;'
                                    ]);
                vdCommon.updateMeasure(["[Version].[Version Name].[" + nVersion + "]"]
                                ,['Measure.[SDX LPS Active Group Picklist] = Measure.[Scenario Master_Objective_Group]@([Version].[Version Name].[CWV_OBJ_PRE]);'
                                    ]);

                // 25.12.31 DisplayName, DisplayAlias 변경 로직 추가
                vdCommon.executeQuery("Update Version", 'updatemember(Version.[Version Name]={,"CWV_OBJ_PRE"},' +
                                                            '[Version].[Version Name$DisplayName]={"' + nextWeek + '_P_PC_01",}, ' +
                                                            '[Version].[Version Name$DisplayAlias]={"' + nextWeek + '_P_PC_01",} ' +
                                                            ');');
                vdCommon.executeQuery("Update Version", 'updatemember(Version.[Version Name]={,"' + nVersion + '"},' +
                                                            '[Version].[Version Name$DisplayName]={"' + currentWeek + '_P_PC_01",}, ' +
                                                            '[Version].[Version Name$DisplayAlias]={"' + currentWeek + '_P_PC_01",} ' +
                                                            ');');
            }

            vdCommon.programEnd();
        } catch ( e ) {
            RuleOutputToUI = { Status : 'Error', Message : "Js Logic Error : " + e.message };
            return;
        }
    };
	
    return {
        PreConfiguredScenario : PreConfiguredScenario
    };
});

/**************************** o9.NSCM.JSPreConfiguredScenario***************************
    2025-12-03 : 최초 작성
    2025-12-31 : DisplayName, DisplayAlias 변경 로직 추가
    2026-01-30 : Scenario Master에 Update하는 로직 추가
    2026-02-10 : SDX LPS Active Group Picklist 업데이트
    2026-02-23 : expiry date 3주 -> 12주로 변경
    2026-03-05 : SDX LPS Active Group Picklist를 Null로 업데이트, Main, Sync, Test에 돌아도 문제 없도록 수정.
    2026-03-19 : Pre-Configured Main 삭제
***************************************************************************************/