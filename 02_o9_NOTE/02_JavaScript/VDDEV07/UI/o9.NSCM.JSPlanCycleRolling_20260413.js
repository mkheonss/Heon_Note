define('o9.NSCM.JSPlanCycleRolling', ['o9/data/query', 'o9/data/cellset', 'o9.NSCM.commonLib'], function () {
    const programName = "o9.NSCM.JSPlanCycleRolling";

	var planCycleRolling = function(o9Params){
	    try {
            const commonLib = require('o9.NSCM.commonLib');
            const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
            const vdUtil = new commonLib.VdUtil();

            vdCommon.setLogLevel("Debug");
            vdCommon.printParams(o9Params);

            var parsedParams = JSON.parse(o9Params);
            //var fbVersionName = parsedParams.fbVersionName;
            //var fbPlanType = parsedParams.fbPlanType;
            //var fbTargetVersionName = parsedParams.fbTargetVersionName;
            var fbVersionName = parsedParams.Version;
            var fbPlanType = parsedParams.PlanType;
            var fbTargetVersionName = parsedParams.TargetVersion;

            var ScenarioName = '';
            var ArchivedVersionName = '';
            var SortingOrder = '';

            var CurrentWeekKey = vdCommon.selectResult('&CurrentWeek.element(0).Key');
            var CurrentWeek = vdCommon.selectResult('&CurrentWeek.element(0).DisplayName');
            var LastWeek = vdCommon.selectResult('&LastWeek.element(0).DisplayName');
            var ArchivedSourceKey = vdCommon.selectResult('Version.[Version Name].[' + fbVersionName + '].Key');
            var ArchivedType = vdCommon.selectResult('Version.[Version Name].[' + fbVersionName + '].[Plan Type]');
            var ArchivedSortingOrder = vdCommon.selectResult('Version.[Version Name].[' + fbVersionName + '].[Version Name Sorting Order]');

            if ( vdUtil.fn_getString(fbTargetVersionName) != "" ) {
                CurrentWeek = fbTargetVersionName;
                LastWeek = vdCommon.selectResult('&AllWeeks.Filter(#.Key == [Time].[Week].filter(#.Name == "' + fbTargetVersionName + '").element(0).LeadOffset(-1).Key).element(0).DisplayName');
            }

            if ( vdUtil.fn_getString(fbPlanType) == "" ) {
                var result = vdCommon.selectList(['Version.[Version Name].[' + fbVersionName + ']'], ["Measure.[W Plan Type]"], "", "", "");
                if ( result.cs.rowCount > 0 ) {
                    fbPlanType = result.cs.row(0).cell(result.cs.measureColumnIndex("W Plan Type"));
                } else {
                    fbPlanType = "MP-Pre";
                }
            }

            vdCommon.debug("CurrentWeekKey : " + CurrentWeekKey +
                                " , CurrentWeek : " + CurrentWeek +
                                " , LastWeek : " + LastWeek +
                                " , ArchivedSourceKey : " + ArchivedSourceKey +
                                " , ArchivedType : " + ArchivedType +
                                " , ArchivedSortingOrder : " + ArchivedSortingOrder);

            if ( fbPlanType == "MP-Pre" ) {
                ScenarioName = CurrentWeek + '_P';
                ArchivedVersionName = LastWeek;
                SortingOrder = CurrentWeek + '01';
            } else if ( fbPlanType == "MP-Main" ) {
                ScenarioName = CurrentWeek + '_M';
                ArchivedVersionName = CurrentWeek + '_P';
                SortingOrder = CurrentWeek + '02';
            } else if ( fbPlanType == "MP-Sync" ) {
                ScenarioName = CurrentWeek;
                ArchivedVersionName = CurrentWeek + '_M';
                SortingOrder = CurrentWeek + '03';
            } else if ( fbPlanType == "MP-Test" ) {
                ScenarioName = CurrentWeek;
                ArchivedVersionName = CurrentWeek + '_T';
                SortingOrder = CurrentWeek + '04';
            }

            vdCommon.executeQuery("Change Plan", 'disable plan;');

            vdCommon.executeQuery("Delete Archived", 'deleteversion("' + ArchivedVersionName + '");');

            vdCommon.executeQuery("Create Archived", 'createscenario(' + ArchivedSourceKey + ',"' + ArchivedVersionName + '");');

            // CWV_MP 에서만 상태를 바꾼다. 아니면 이전 버번에서 복구를 하는 케이스임
            var UpdateScenarioName = 'updatemember(Version.[Version Name]={,"' + fbVersionName + '"},' +
                                        '[Version].[Version Name$DisplayName]={"' + ScenarioName + '",}, ' +
                                        'Version.[Plan Type]={"' + fbPlanType + '",},' +
                                        '[Version].[Version Name Sorting Order]={"' + SortingOrder + '",},' +
                                        '[Version].[Current Version Flag]={NULL,});';
            vdCommon.executeQuery("Update Scenario Name", UpdateScenarioName);

            var UpdateArchivedScenarioName = 'updatemember(Version.[Version Name]={,"' + ArchivedVersionName + '"},' +
                                                '[Version].[Version Name$DisplayName]={"' + ArchivedVersionName + '",}, ' +
                                                'Version.[Plan Type]={"' + ArchivedType + '",},' +
                                                '[Version].[Version Name Sorting Order]={"' + ArchivedSortingOrder + '",},' +
                                                '[Version].[Version Status]={"Archived",},' +
                                                '[Version].[ScenarioType]={"Archiving Version",},' +
                                                '[Version].[Current Version Flag]={true,} , ' +
                                                '[Version].[Current Time For Version] = {todatetime("' + CurrentWeekKey + '"),});';
            vdCommon.executeQuery("Update Archived Scenario Name", UpdateArchivedScenarioName);

            vdCommon.executeQuery("Change Plan", 'enable plan;');

            vdCommon.programEnd();
        } catch ( e ) {
            RuleOutputToUI = { Status : 'Error', Message : "Js Logic Error : " + e.message };
            return;
        }
    };
	
    return {
        planCycleRolling : planCycleRolling
    };
});

/**************************** o9.NSCM.JSPlanCycleRolling ****************************
    2024-11-13 : ...
*********************************************************************/