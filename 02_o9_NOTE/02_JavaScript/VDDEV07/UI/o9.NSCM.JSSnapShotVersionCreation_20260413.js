define('o9.NSCM.JSSnapShotVersionCreation', ['o9/data/query', 'o9/data/cellset', 'o9.NSCM.commonLib'], function () {
    const programName = "o9.NSCM.JSSnapShotVersionCreation";

	var snapShotVersionCreation = function(o9Params){
	    try {
            const commonLib = require('o9.NSCM.commonLib');
            const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
            const vdUtil = new commonLib.VdUtil();

            vdCommon.setLogLevel("Debug");
            vdCommon.printParams(o9Params);

            var parsedParams = JSON.parse(o9Params);
            var fbVersionName = parsedParams.Version;

            var SourceKey = vdCommon.selectResult('Version.[Version Name].[' + fbVersionName + '].Key');
            var SnapshotVersionPlanType = vdCommon.selectResult('Version.[Version Name].[' + fbVersionName + '].[Plan Type]');
            var SnapshotDisplay = vdCommon.selectResult('Version.[Version Name].[' + fbVersionName + '].DisplayName');
            var SnapshotVersionSortingOrder = vdCommon.selectResult('Version.[Version Name].[' + fbVersionName + '].[Version Name Sorting Order]');
            var Prefix = SnapshotDisplay.split("_")[0];
            var CurrentTime = vdCommon.selectResult('Time.[Week].filter(#.DisplayName == "' + Prefix + '").first.Key');
            var SnapshotVersionName = '';
            var VersionFlag = true;

            vdCommon.debug("SourceKey : " + SourceKey +
                                " , SnapshotVersionPlanType : " + SnapshotVersionPlanType +
                                " , SnapshotDisplay : " + SnapshotDisplay +
                                " , SnapshotVersionSortingOrder : " + SnapshotVersionSortingOrder +
                                " , Prefix : " + Prefix +
                                " , CurrentTime : " + CurrentTime);

            if ( SnapshotVersionPlanType == "MP-Pre" ) {
                SnapshotVersionName = Prefix + '_P';
            } else if ( SnapshotVersionPlanType == "MP-Main" ) {
                SnapshotVersionName = Prefix + '_M';
            } else if ( SnapshotVersionPlanType == "MP-Sync" ) {
                SnapshotVersionName = Prefix;
            } else if ( SnapshotVersionPlanType == "MP-Test" ) {
                SnapshotVersionName = Prefix + '_T';
                VersionFlag = null;
            }

            vdCommon.executeQuery("Change Plan", 'disable plan;');

            vdCommon.executeQuery("Update Scenario Name", 'updatemember(Version.[Version Name]={,"' + fbVersionName + '"},' +
                                                            '[Version].[Version Name$DisplayName]={"' + SnapshotDisplay + '_Temp",});');

            vdCommon.executeQuery("Delete Version", 'deleteversion("' + SnapshotVersionName + '");');

            vdCommon.executeQuery("Create Snapshot Version", 'createscenario(' + SourceKey + ',"' + SnapshotVersionName + '");');

            vdCommon.executeQuery("Update Snapshot VersionName", 'updatemember(Version.[Version Name]={,"' + SnapshotVersionName + '"},' +
                                                                    '[Version].[Version Name$DisplayName]={"' + SnapshotDisplay + '",}, ' +
                                                                    'Version.[Plan Type]={"' + SnapshotVersionPlanType + '",},' +
                                                                    '[Version].[Version Name Sorting Order]={"' + SnapshotVersionSortingOrder + '",},' +
                                                                    '[Version].[Version Status]={"Finished",},' +
                                                                    '[Version].[ScenarioType]={"Snapshot Version",},' +
                                                                    '[Version].[Current Version Flag]={' + VersionFlag + ',} , ' +
                                                                    '[Version].[Current Time For Version] = {todatetime("' + CurrentTime + '"),});');

            vdCommon.executeQuery("Change Plan", 'enable plan;');

            vdCommon.programEnd();
        } catch ( e ) {
            RuleOutputToUI = { Status : 'Error', Message : "Js Logic Error : " + e.message };
            return;
        }
    };
	
    return {
    	snapShotVersionCreation : snapShotVersionCreation
	};
});

/**************************** o9.NSCM.JSSnapShotVersionCreation ****************************
    2024-11-13 : ...
*********************************************************************/