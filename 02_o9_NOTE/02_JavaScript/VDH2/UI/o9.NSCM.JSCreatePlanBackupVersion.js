define('o9.NSCM.JSCreatePlanBackupVersion', ['o9/data/query', 'o9/data/cellset', 'o9.NSCM.commonLib'], function () {
    const programName = "o9.NSCM.JSCreatePlanBackupVersion";

	var CreatePlanBackupVersion = function(o9Params){
	    try {
            const commonLib = require('o9.NSCM.commonLib');
            const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
            const vdUtil = new commonLib.VdUtil();

            vdCommon.setLogLevel("Debug");
            vdCommon.printParams(o9Params);

            var parsedParams = JSON.parse(o9Params);
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

            var currentDay = vdCommon.selectResult('&CurrentDay.element(0).Name');
            var dayAfter12W = vdUtil.fn_dateAdd(currentDay, "week", 12);
            var dayAfter3Y = vdUtil.fn_dateAdd(currentDay, "year", 3);
            var expiryDate = "";

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
                ArchivedVersionName = CurrentWeek + '_P';
                SortingOrder = CurrentWeek + '02';
                expiryDate = dayAfter12W;
            } else if ( fbPlanType == "MP-Main" ) {
                ArchivedVersionName = CurrentWeek + '_M';
                SortingOrder = CurrentWeek + '03';
                expiryDate = dayAfter12W;
            } else if ( fbPlanType == "MP-Sync" ) {
                ArchivedVersionName = CurrentWeek;
                SortingOrder = CurrentWeek + '01';
                expiryDate = dayAfter3Y;
            } else if ( fbPlanType == "MP-Test" ) {
                ArchivedVersionName = CurrentWeek + '_A';
                SortingOrder = CurrentWeek + '04';
                expiryDate = dayAfter12W;
            }

            vdCommon.debug("expiryDate : " + expiryDate + " , dayAfter3Y : " + dayAfter3Y + " , dayAfter12W : " + dayAfter12W);

            vdCommon.executeQuery("Change Plan", 'disable plan;');

            // CWV_MP로 변경 -> Name$DisplayName 중복으로 ...(1) 이 생성이 되어서..
            var UpdateArchivedScenarioName = 'updatemember(Version.[Version Name]={,"CWV_MP"},' +
                                                '[Version].[Version Name$DisplayName]={"CWV_MP",});';
            vdCommon.executeQuery("CWV_MP 의 이름을 CWV_MP 로 변경", UpdateArchivedScenarioName);

            vdCommon.executeQuery("Delete Archived", 'deleteversion("' + ArchivedVersionName + '");');
            vdCommon.executeQuery("Create Archived", 'createscenario(' + ArchivedSourceKey + ',"' + ArchivedVersionName + '");');
            var UpdateArchivedScenarioName = 'updatemember(Version.[Version Name]={,"' + ArchivedVersionName + '"},' +
                                                '[Version].[Version Name$DisplayName]={"' + ArchivedVersionName + '",}, ' +
                                                '[Version].[Version Name$DisplayAlias]={"' + ArchivedVersionName + '",}, ' +
                                                'Version.[Plan Type]={"' + ArchivedType + '",},' +
                                                '[Version].[Version Expiry Date]={"' + expiryDate + '",},' +
                                                '[Version].[Version Name Sorting Order]={"' + ArchivedSortingOrder + '",},' +
                                                '[Version].[Version Status]={"Archived",},' +
                                                '[Version].[ScenarioType]={"Archiving Version",},' +
                                                '[Version].[Current Version Flag]={true,} , ' +
                                                '[Version].[Current Time For Version] = {todatetime("' + CurrentWeekKey + '"),});';
            vdCommon.executeQuery("Update Archived Scenario Name", UpdateArchivedScenarioName);

            // CWV_MP 의 Name$DisplayName 를 다시 변경
            var UpdateArchivedScenarioName = 'updatemember(Version.[Version Name]={,"CWV_MP"},' +
                                                '[Version].[Version Name$DisplayName]={"' + ArchivedVersionName + '",}, ' +
                                                '[Version].[Version Name$DisplayAlias]={"' + ArchivedVersionName + '",});';
            vdCommon.executeQuery("CWV_MP 의 이름을 주차명으로 변경", UpdateArchivedScenarioName);

            vdCommon.executeQuery("Change Plan", 'enable plan;');

            vdCommon.programEnd();
        } catch ( e ) {
            RuleOutputToUI = { Status : 'Error', Message : "Js Logic Error : " + e.message };
            return;
        }
    };
	
    return {
        CreatePlanBackupVersion : CreatePlanBackupVersion
    };
});

/**************************** o9.NSCM.JSCreatePlanBackupVersion ****************************
    2026-02-11 : o9.NSCM.JSPlanCycleRollingAdd를 소스로 신규 생성
***************************************************************************************************/