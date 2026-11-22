define('o9.NSCM.JSPlanCycleRollingUpdate', ['o9/data/query', 'o9/data/cellset', 'o9.NSCM.commonLib'], function () {
    const programName = "o9.NSCM.JSPlanCycleRollingUpdate";

	var planCycleRollingUpdate = function(o9Params){
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
            //var ArchivedVersionName = '';
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
                SortingOrder = CurrentWeek + '01';
            } else if ( fbPlanType == "MP-Main" ) {
                ScenarioName = CurrentWeek + '_M';
                SortingOrder = CurrentWeek + '02';
            //} else if ( fbPlanType == "MP-Sync1" ) {
            //    ScenarioName = CurrentWeek + '_S';
            //    SortingOrder = CurrentWeek + '03';
            //} else if ( fbPlanType == "MP-Sync2" ) {
            //    ScenarioName = CurrentWeek;
            //    SortingOrder = CurrentWeek + '04';
            } else if ( fbPlanType == "MP-Sync" ) {
                ScenarioName = CurrentWeek;
                SortingOrder = CurrentWeek + '03';
            } else if ( fbPlanType == "MP-Test" ) {
                ScenarioName = CurrentWeek + '_A';
                SortingOrder = CurrentWeek + '04';
            //    SortingOrder = CurrentWeek + '05';
            }

            //vdCommon.executeQuery("Change Plan", 'disable plan;');

            // CWV_MP 에서만 상태를 바꾼다. 아니면 이전 버전에서 복구를 하는 케이스임
            var UpdateScenarioName = 'updatemember(Version.[Version Name]={,"' + fbVersionName + '"},' +
                                        '[Version].[Version Name$DisplayName]={"' + ScenarioName + '",}, ' +
                                        '[Version].[Version Name$DisplayAlias]={"' + ScenarioName + '",}, ' +
                                        'Version.[Plan Type]={"' + fbPlanType + '",},' +
                                        '[Version].[Version Name Sorting Order]={"' + SortingOrder + '",},' +
                                        '[Version].[Current Version Flag]={NULL,});';
            vdCommon.executeQuery("Update Scenario Name", UpdateScenarioName);

            //vdCommon.executeQuery("Change Plan", 'enable plan;');

            vdCommon.programEnd();
        } catch ( e ) {
            RuleOutputToUI = { Status : 'Error', Message : "Js Logic Error : " + e.message };
            return;
        }
    };
	
    return {
        planCycleRollingUpdate : planCycleRollingUpdate
    };
});

/**************************** o9.NSCM.JSPlanCycleRollingUpdate ****************************
    2025-06-17 : ...
    2026-03-13 : enable plan, disable plan 삭제
    2026-03-19 : Plan Version이 Sync1, Sync2로 변경, DisplayAlias도 수정
*********************************************************************/