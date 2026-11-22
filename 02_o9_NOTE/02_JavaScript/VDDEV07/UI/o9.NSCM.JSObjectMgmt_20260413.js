define('o9.NSCM.JSObjectMgmt', ['o9/data/query', 'o9/data/cellset', 'o9.NSCM.commonLib'], function () {
    const programName = "o9.NSCM.JSObjectMgmt";
	var CreateBackupVersion = function(o9Params){
	    try {
            const commonLib = require('o9.NSCM.commonLib');
            const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
            const vdUtil = new commonLib.VdUtil();

            vdCommon.setLogLevel("Debug");
            vdCommon.printParams(o9Params);

            var p = JSON.parse(o9Params);
            var query = "";
            var sVersion = "CWV_MP";

            // CreateBackupVersion MG List
            var result = vdCommon.selectList(['[Seq].[Seq]'], ['Measure.[CreateBkup List_Condition], Measure.[CreateBkup List_LeadOffSet], Measure.[CreateBkup List_Object], Measure.[CreateBkup List_Type], Measure.[CreateBkup List_User Defined]']
                                                ,"where {[Version].[Version Name].[" + sVersion +"], Measure.[CreateBkup List_Skip] != true } "
                                                ,"", "");

            // Delete Object Process
            query = query + 'exec parallel begin  ';
            for ( var i = 0; i < result.cs.rowCount; i++ ) {
                var Seq = vdUtil.fn_getDimValue(result, i, "Seq", "Seq");
                var DataObject = vdUtil.fn_getString(result.cs.row(i).cell(result.cs.measureColumnIndex("CreateBkup List_Object")));
                var Type = vdUtil.fn_getString(result.cs.row(i).cell(result.cs.measureColumnIndex("CreateBkup List_Type")));
                //var Condition = vdUtil.fn_getString(result.cs.row(i).cell(result.cs.measureColumnIndex("CreateBkup List_Condition")));
                //var LeadOffSet = vdUtil.fn_getString(result.cs.row(i).cell(result.cs.measureColumnIndex("CreateBkup List_LeadOffSet")));
                //var UserDefined = vdUtil.fn_getString(result.cs.row(i).cell(result.cs.measureColumnIndex("CreateBkup List_User Defined")));

                query = query + 'block begin  ';
                if (Type == "Measure Group"){
                    query = query + 'DELETE DATA FOR MODEL ['  +  DataObject  +  '] ';
                }
                else if (Type == "Graph"){
                    query = query + 'DELETE DATA FOR GRAPH ['  +  DataObject  +  '] ';
                }
                query = query + 'where {[Version].[Version Name].['  +  p.TargetScenario  +  ']};  ';
                query = query + 'end  ';
            }
            query = query + 'end;';

            vdCommon.debug("Query : " + query);
            vdCommon.executeQuery("Execute Result", query);

            // Create "CWV_MP_INI" Scenario
            vdCommon.executeQuery("Create CWV_MP_INI", 'createscenario(Version.[Version Name].[CWV_MP] , "CWV_MP_INI"); ');

            // Update Object Process
            query = 'exec parallel begin  ';
            for ( var i = 0; i < result.cs.rowCount; i++ ) {
                var Seq = vdUtil.fn_getDimValue(result, i, "Seq", "Seq");
                var DataObject = vdUtil.fn_getString(result.cs.row(i).cell(result.cs.measureColumnIndex("CreateBkup List_Object")));
                //var Type = vdUtil.fn_getString(result.cs.row(i).cell(result.cs.measureColumnIndex("CreateBkup List_Type")));
                var Condition = vdUtil.fn_getString(result.cs.row(i).cell(result.cs.measureColumnIndex("CreateBkup List_Condition")));
                var LeadOffSet = vdUtil.fn_getString(result.cs.row(i).cell(result.cs.measureColumnIndex("CreateBkup List_LeadOffSet")));
                var UserDefined = vdUtil.fn_getString(result.cs.row(i).cell(result.cs.measureColumnIndex("CreateBkup List_User Defined")));

                query = query + 'block begin  ';
                query = query + 'UpdateScenario(['  +  p.TargetScenario  +  '], CWV_MP_INI, false, true ';
                query = query + ', for Model ['  +  DataObject  +  '] ';
                if (Condition == "Day"){
                    query = query + 'using scope (Time.Day.filter(#.Key >= &CurrentWeek.element(' + LeadOffSet  + ').Key))';
                }
                else if (Condition == "Week"){
                    query = query + 'using scope (Time.Week.filter(#.Key >= &CurrentWeek.element(' + LeadOffSet  + ').Key))';
                }
                else if (Condition == "Month"){
                    query = query + 'using scope (Time.Month.filter(#.Key >= &CurrentWeek.element(' + LeadOffSet  + ').Key))';
                }
                else if (Condition == "User Defined"){
                    query = query + 'using scope ('  +  UserDefined  +  ')';
                }
                query = query + ');    end  ';
            }
            query = query + 'end;';

            vdCommon.debug("Query : " + query);
            vdCommon.executeQuery("Execute Result", query);

            // Delete "CWV_MP_INI" Scenario
            vdCommon.executeQuery("Delete CWV_MP_INI", 'deleteversion ("CWV_MP_INI"); ');


            // Init Dttm, Init By, Up Dttm, Up By Cleansing Process
            var result = vdCommon.selectList(['[Seq].[Seq]'], ['Measure.[CreateBkup Cleansing List_Object]']
                                                ,"where {[Version].[Version Name].[" + sVersion +"], Measure.[CreateBkup Cleansing List_Skip] != true } "
                                                ,"", "");

            query = 'scope: ( [Version].[Version Name].['  +  p.TargetScenario  +  '] );  ';
            for ( var i = 0; i < result.cs.rowCount; i++ ) {
                var Seq = vdUtil.fn_getDimValue(result, i, "Seq", "Seq");
                var DataObject = vdUtil.fn_getString(result.cs.row(i).cell(result.cs.measureColumnIndex("CreateBkup Cleansing List_Object")));
                query = query + 'Measure.['  +  DataObject  +  '] = Null;  ';
            }
            query = query + 'end scope;';

            vdCommon.debug("Query : " + query);
            vdCommon.executeQuery("Execute Result", query);

            vdCommon.programEnd();
        } catch ( e ) {
            RuleOutputToUI = { Status : 'Error', Message : "Js Logic Error : " + e.message };
            return;
        }
    };



	var UpdateBackupVersion = function(o9Params){
	    try {
            const commonLib = require('o9.NSCM.commonLib');
            const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
            const vdUtil = new commonLib.VdUtil();

            vdCommon.setLogLevel("Debug");
            vdCommon.printParams(o9Params);

            var p = JSON.parse(o9Params);
            var query = "";
            var sVersion = "CWV_MP";

            // UpdateBackupVersion MG List
            var result = vdCommon.selectList(['[Seq].[Seq]'], ['Measure.[UpdateBkup List_Condition], Measure.[UpdateBkup List_LeadOffSet], Measure.[UpdateBkup List_Object], Measure.[UpdateBkup List_Type], Measure.[UpdateBkup List_User Defined]']
                                                ,"where {[Version].[Version Name].[" + sVersion +"], Measure.[UpdateBkup List_Skip] != true } "
                                                ,"", "");

            // Delete Object Process
            query = query + 'exec parallel begin  ';
            for ( var i = 0; i < result.cs.rowCount; i++ ) {
                var Seq = vdUtil.fn_getDimValue(result, i, "Seq", "Seq");
                var DataObject = vdUtil.fn_getString(result.cs.row(i).cell(result.cs.measureColumnIndex("UpdateBkup List_Object")));
                var Type = vdUtil.fn_getString(result.cs.row(i).cell(result.cs.measureColumnIndex("UpdateBkup List_Type")));
                //var Condition = vdUtil.fn_getString(result.cs.row(i).cell(result.cs.measureColumnIndex("UpdateBkup List_Condition")));
                //var LeadOffSet = vdUtil.fn_getString(result.cs.row(i).cell(result.cs.measureColumnIndex("UpdateBkup List_LeadOffSet")));
                //var UserDefined = vdUtil.fn_getString(result.cs.row(i).cell(result.cs.measureColumnIndex("UpdateBkup List_User Defined")));

                query = query + 'block begin  ';
                if (Type == "Measure Group"){
                    query = query + 'DELETE DATA FOR MODEL ['  +  DataObject  +  '] ';
                }
                else if (Type == "Graph"){
                    query = query + 'DELETE DATA FOR GRAPH ['  +  DataObject  +  '] ';
                }
                query = query + 'where {[Version].[Version Name].['  +  p.TargetScenario  +  ']};  ';
                query = query + 'end  ';
            }
            query = query + 'end;';

            vdCommon.debug("Query : " + query);
            vdCommon.executeQuery("Execute Result", query);

            // Update Object Process
            query = 'exec parallel begin  ';
            for ( var i = 0; i < result.cs.rowCount; i++ ) {
                var Seq = vdUtil.fn_getDimValue(result, i, "Seq", "Seq");
                var DataObject = vdUtil.fn_getString(result.cs.row(i).cell(result.cs.measureColumnIndex("UpdateBkup List_Object")));
                //var Type = vdUtil.fn_getString(result.cs.row(i).cell(result.cs.measureColumnIndex("UpdateBkup List_Type")));
                var Condition = vdUtil.fn_getString(result.cs.row(i).cell(result.cs.measureColumnIndex("UpdateBkup List_Condition")));
                var LeadOffSet = vdUtil.fn_getString(result.cs.row(i).cell(result.cs.measureColumnIndex("UpdateBkup List_LeadOffSet")));
                var UserDefined = vdUtil.fn_getString(result.cs.row(i).cell(result.cs.measureColumnIndex("UpdateBkup List_User Defined")));

                query = query + 'block begin  ';
                query = query + 'UpdateScenario(['  +  p.TargetScenario  +  '], CWV_MP, false, true ';
                query = query + ', for Model ['  +  DataObject  +  '] ';
                if (Condition == "Day"){
                    query = query + 'using scope (Time.Day.filter(#.Key >= &CurrentWeek.element(' + LeadOffSet  + ').Key))';
                }
                else if (Condition == "Week"){
                    query = query + 'using scope (Time.Week.filter(#.Key >= &CurrentWeek.element(' + LeadOffSet  + ').Key))';
                }
                else if (Condition == "Month"){
                    query = query + 'using scope (Time.Month.filter(#.Key >= &CurrentWeek.element(' + LeadOffSet  + ').Key))';
                }
                else if (Condition == "User Defined"){
                    query = query + 'using scope ('  +  UserDefined  +  ')';
                }
                query = query + ');    end  ';
            }
            query = query + 'end;';

            vdCommon.debug("Query : " + query);
            vdCommon.executeQuery("Execute Result", query);

            vdCommon.programEnd();
        } catch ( e ) {
            RuleOutputToUI = { Status : 'Error', Message : "Js Logic Error : " + e.message };
            return;
        }
    };




	var CreateLWScenario = function(o9Params){
	    try {
            const commonLib = require('o9.NSCM.commonLib');
            const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
            const vdUtil = new commonLib.VdUtil();

            vdCommon.setLogLevel("Debug");
            vdCommon.printParams(o9Params);

            var p = JSON.parse(o9Params);
            var query = "";
            var sVersion = "CWV_MP";
            var sVersionKey = vdCommon.selectResult('Version.[Version Name].[CWV_MP].Key');

            // CreateLWScenario MG List
            var result = vdCommon.selectList(['[Seq].[Seq]'], ['Measure.[LW Scenario List_Condition], Measure.[LW Scenario List_LeadOffSet], Measure.[LW Scenario List_Object], Measure.[LW Scenario List_Type], Measure.[LW Scenario List_User Defined]']
                                                ,"where {[Version].[Version Name].[" + sVersion +"], Measure.[LW Scenario List_Skip] != true } "
                                                ,"", "");

            var rowCount = result.cs.rowCount;

            // CreateLWScenario
            query = 'createlwscenario(' + sVersionKey + ', "' + p.TargetScenario + '")  ';
            for ( var i = 0; i < rowCount; i++ ) {
                var Seq = vdUtil.fn_getDimValue(result, i, "Seq", "Seq");
                var DataObject = vdUtil.fn_getString(result.cs.row(i).cell(result.cs.measureColumnIndex("LW Scenario List_Object")));
                //var Type = vdUtil.fn_getString(result.cs.row(i).cell(result.cs.measureColumnIndex("LW Scenario List_Type")));
                var Condition = vdUtil.fn_getString(result.cs.row(i).cell(result.cs.measureColumnIndex("LW Scenario List_Condition")));
                var LeadOffSet = vdUtil.fn_getString(result.cs.row(i).cell(result.cs.measureColumnIndex("LW Scenario List_LeadOffSet")));
                var UserDefined = vdUtil.fn_getString(result.cs.row(i).cell(result.cs.measureColumnIndex("LW Scenario List_User Defined")));

                query = query + 'Initialize model {[' + DataObject + ']} to parent';
                if (Condition == "Day"){
                    query = query + '  using scope (Time.Day.filter(#.Key >= &CurrentWeek.element(' + LeadOffSet  + ').Key))';
                }
                else if (Condition == "Week"){
                    query = query + '  using scope (Time.Week.filter(#.Key >= &CurrentWeek.element(' + LeadOffSet  + ').Key))';
                }
                else if (Condition == "Month"){
                    query = query + '  using scope (Time.Month.filter(#.Key >= &CurrentWeek.element(' + LeadOffSet  + ').Key))';
                }
                else if (Condition == "User Defined"){
                    query = query + '  using scope ('  +  UserDefined  +  ')';
                }

                if ( i == rowCount - 1 ){
                    query = query + ';';
                }
                else {
                    query = query + ',  ';
                }
            }

            vdCommon.debug("Query : " + query);
            vdCommon.executeQuery("Execute Result", query);

            vdCommon.programEnd();
        } catch ( e ) {
            RuleOutputToUI = { Status : 'Error', Message : "Js Logic Error : " + e.message };
            return;
        }
    };




	var UpdateLWScenario = function(o9Params){
	    try {
            const commonLib = require('o9.NSCM.commonLib');
            const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
            const vdUtil = new commonLib.VdUtil();

            vdCommon.setLogLevel("Debug");
            vdCommon.printParams(o9Params);

            var p = JSON.parse(o9Params);
            var query = "";
            var fbVersion = p.Version;
            var fbPlanType = p.PlanType;
            var TargetVersion = "";
            var SourceVersion = p.Version + '_INI';
            var CurrentWeek = vdCommon.selectResult('&CurrentWeek.element(0).DisplayName');

            if ( fbPlanType == "MP-Pre" ) {
                TargetVersion = CurrentWeek + '_P';
                SourceVersion = SourceVersion + '_PRE';
            } else if ( fbPlanType == "MP-Main" ) {
                TargetVersion = CurrentWeek + '_M';
                SourceVersion = SourceVersion + '_MAIN';
            //} else if ( fbPlanType == "MP-Sync1" ) {
            //    TargetVersion = CurrentWeek + '_S';
            //    SourceVersion = SourceVersion + '_SYNC1';
            //} else if ( fbPlanType == "MP-Sync2" ) {
            //    TargetVersion = CurrentWeek;
            //    SourceVersion = SourceVersion + '_SYNC2';
            } else if ( fbPlanType == "MP-Sync" ) {
                TargetVersion = CurrentWeek;
                SourceVersion = SourceVersion + '_SYNC';
            } else if ( fbPlanType == "MP-Test" ) {
                TargetVersion = CurrentWeek + '_A';
                SourceVersion = SourceVersion + '_TEST';
            }

            // Update LW Scenario MG List
            var result = vdCommon.selectList(['[Seq].[Seq]'], ['Measure.[UpdateLWScenario List_Condition], Measure.[UpdateLWScenario List_LeadOffSet], Measure.[UpdateLWScenario List_Object], Measure.[UpdateLWScenario List_Type], Measure.[UpdateLWScenario List_User Defined]']
                                                ,"where {[Version].[Version Name].[" + fbVersion +"], Measure.[UpdateLWScenario List_Skip] != true } "
                                                ,"", "");


            // Delete Object Process
            query = query + 'exec parallel begin  ';
            for ( var i = 0; i < result.cs.rowCount; i++ ) {
                var Seq = vdUtil.fn_getDimValue(result, i, "Seq", "Seq");
                var DataObject = vdUtil.fn_getString(result.cs.row(i).cell(result.cs.measureColumnIndex("UpdateLWScenario List_Object")));
                var Type = vdUtil.fn_getString(result.cs.row(i).cell(result.cs.measureColumnIndex("UpdateLWScenario List_Type")));
                //var Condition = vdUtil.fn_getString(result.cs.row(i).cell(result.cs.measureColumnIndex("UpdateLWScenario List_Condition")));
                //var LeadOffSet = vdUtil.fn_getString(result.cs.row(i).cell(result.cs.measureColumnIndex("UpdateLWScenario List_LeadOffSet")));
                //var UserDefined = vdUtil.fn_getString(result.cs.row(i).cell(result.cs.measureColumnIndex("UpdateLWScenario List_User Defined")));

                query = query + 'block begin  ';
                if (Type == "Measure Group"){
                    query = query + 'DELETE DATA FOR MODEL ['  +  DataObject  +  '] ';
                }
                else if (Type == "Graph"){
                    query = query + 'DELETE DATA FOR GRAPH ['  +  DataObject  +  '] ';
                }
                query = query + 'where {[Version].[Version Name].['  +  TargetVersion  +  ']};  ';
                query = query + 'end  ';
            }
            query = query + 'end;';

            vdCommon.debug("Query : " + query);
            vdCommon.executeQuery("Execute Result", query);

            // Update Object Process
            query = 'exec parallel begin  ';
            for ( var i = 0; i < result.cs.rowCount; i++ ) {
                var Seq = vdUtil.fn_getDimValue(result, i, "Seq", "Seq");
                var DataObject = vdUtil.fn_getString(result.cs.row(i).cell(result.cs.measureColumnIndex("UpdateLWScenario List_Object")));
                //var Type = vdUtil.fn_getString(result.cs.row(i).cell(result.cs.measureColumnIndex("UpdateLWScenario List_Type")));
                var Condition = vdUtil.fn_getString(result.cs.row(i).cell(result.cs.measureColumnIndex("UpdateLWScenario List_Condition")));
                var LeadOffSet = vdUtil.fn_getString(result.cs.row(i).cell(result.cs.measureColumnIndex("UpdateLWScenario List_LeadOffSet")));
                var UserDefined = vdUtil.fn_getString(result.cs.row(i).cell(result.cs.measureColumnIndex("UpdateLWScenario List_User Defined")));

                query = query + 'block begin  ';
                query = query + 'UpdateScenario(['  +  TargetVersion  +  '], '  +  SourceVersion  +  ', false, true ';
                query = query + ', for Model ['  +  DataObject  +  '] ';
                if (Condition == "Day"){
                    query = query + 'using scope (Time.Day.filter(#.Key >= &CurrentWeek.element(' + LeadOffSet  + ').Key))';
                }
                else if (Condition == "Week"){
                    query = query + 'using scope (Time.Week.filter(#.Key >= &CurrentWeek.element(' + LeadOffSet  + ').Key))';
                }
                else if (Condition == "Month"){
                    query = query + 'using scope (Time.Month.filter(#.Key >= &CurrentWeek.element(' + LeadOffSet  + ').Key))';
                }
                else if (Condition == "User Defined"){
                    query = query + 'using scope ('  +  UserDefined  +  ')';
                }
                query = query + ');    end  ';
            }
            query = query + 'end;';

            vdCommon.debug("Query : " + query);
            vdCommon.executeQuery("Execute Result", query);

            vdCommon.programEnd();
        } catch ( e ) {
            RuleOutputToUI = { Status : 'Error', Message : "Js Logic Error : " + e.message };
            return;
        }
    };



	var planCycleRollingLW = function(o9Params){
	    try {
            const commonLib = require('o9.NSCM.commonLib');
            const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
            const vdUtil = new commonLib.VdUtil();

            vdCommon.setLogLevel("Debug");
            vdCommon.printParams(o9Params);

            var p = JSON.parse(o9Params);
            var fbVersionName = p.Version;
            var fbPlanType = p.PlanType;
            var fbTargetVersionName = p.TargetVersion;

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
            //} else if ( fbPlanType == "MP-Sync1" ) {
            //    ArchivedVersionName = CurrentWeek + '_S';
            //    SortingOrder = CurrentWeek + '04';
            //    expiryDate = dayAfter12W;
            //} else if ( fbPlanType == "MP-Sync2" ) {
            //    ArchivedVersionName = CurrentWeek;
            //    SortingOrder = CurrentWeek + '01';
            //    expiryDate = dayAfter3Y;
            } else if ( fbPlanType == "MP-Sync" ) {
                ArchivedVersionName = CurrentWeek;
                SortingOrder = CurrentWeek + '01';
                expiryDate = dayAfter3Y;
            } else if ( fbPlanType == "MP-Test" ) {
                ArchivedVersionName = CurrentWeek + '_A';
            //    SortingOrder = CurrentWeek + '05';
                SortingOrder = CurrentWeek + '04';
                expiryDate = dayAfter12W;
            }

            vdCommon.debug("expiryDate : " + expiryDate + " , dayAfter3Y : " + dayAfter3Y + " , dayAfter12W : " + dayAfter12W);

            // CWV_MP로 변경 -> Name$DisplayName 중복으로 ...(1) 이 생성이 되어서..
            var UpdateArchivedScenarioName = 'updatemember(Version.[Version Name]={,"CWV_MP"},' +
                                                '[Version].[Version Name$DisplayName]={"CWV_MP",});';
            vdCommon.executeQuery("CWV_MP 의 이름을 CWV_MP 로 변경", UpdateArchivedScenarioName);

            vdCommon.executeQuery("Delete Archived", 'deleteversion("' + ArchivedVersionName + '");');


            // Create Archived LW Scenario
            var query = "";

            var result = vdCommon.selectList(['[Seq].[Seq]'], ['Measure.[LW Scenario List_Condition], Measure.[LW Scenario List_LeadOffSet], Measure.[LW Scenario List_Object], Measure.[LW Scenario List_Type], Measure.[LW Scenario List_User Defined]']
                                                ,"where {[Version].[Version Name].[" + fbVersionName +"], Measure.[LW Scenario List_Skip] != true } "
                                                ,"", "");

            var rowCount = result.cs.rowCount;

            query = 'createlwscenario(' + ArchivedSourceKey + ', "' + ArchivedVersionName + '")  ';
            for ( var i = 0; i < rowCount; i++ ) {
                var Seq = vdUtil.fn_getDimValue(result, i, "Seq", "Seq");
                var DataObject = vdUtil.fn_getString(result.cs.row(i).cell(result.cs.measureColumnIndex("LW Scenario List_Object")));
                //var Type = vdUtil.fn_getString(result.cs.row(i).cell(result.cs.measureColumnIndex("LW Scenario List_Type")));
                var Condition = vdUtil.fn_getString(result.cs.row(i).cell(result.cs.measureColumnIndex("LW Scenario List_Condition")));
                var LeadOffSet = vdUtil.fn_getString(result.cs.row(i).cell(result.cs.measureColumnIndex("LW Scenario List_LeadOffSet")));
                var UserDefined = vdUtil.fn_getString(result.cs.row(i).cell(result.cs.measureColumnIndex("LW Scenario List_User Defined")));

                query = query + 'Initialize model {[' + DataObject + ']} to parent';
                if (Condition == "Day"){
                    query = query + '  using scope (Time.Day.filter(#.Key >= &CurrentWeek.element(' + LeadOffSet  + ').Key))';
                }
                else if (Condition == "Week"){
                    query = query + '  using scope (Time.Week.filter(#.Key >= &CurrentWeek.element(' + LeadOffSet  + ').Key))';
                }
                else if (Condition == "Month"){
                    query = query + '  using scope (Time.Month.filter(#.Key >= &CurrentWeek.element(' + LeadOffSet  + ').Key))';
                }
                else if (Condition == "User Defined"){
                    query = query + '  using scope ('  +  UserDefined  +  ')';
                }

                if ( i == rowCount - 1 ){
                    query = query + ';';
                }
                else {
                    query = query + ',  ';
                }
            }

            vdCommon.debug("Query : " + query);
            vdCommon.executeQuery("Execute Result", query);


            // Update Archived LW Scenario
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

            vdCommon.programEnd();
        } catch ( e ) {
            RuleOutputToUI = { Status : 'Error', Message : "Js Logic Error : " + e.message };
            return;
        }
    };







	var DeleteAllBeforePlan = function(o9Params){
	    try {
            const commonLib = require('o9.NSCM.commonLib');
            const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
            const vdUtil = new commonLib.VdUtil();

            vdCommon.setLogLevel("Debug");
            vdCommon.printParams(o9Params);

            var p = JSON.parse(o9Params);
            var query = "";
            var sVersion = "CWV_MP";
            var TargetVersion = p.Version;

            // CreateBackupVersion MG List
            var result = vdCommon.selectList(['[Seq].[Seq]'], ['Measure.[DeleteAllBeforePlan List_Condition], Measure.[DeleteAllBeforePlan List_LeadOffSet], Measure.[DeleteAllBeforePlan List_Object], Measure.[DeleteAllBeforePlan List_Type], Measure.[DeleteAllBeforePlan List_User Defined]']
                                                ,"where {[Version].[Version Name].[" + sVersion +"], Measure.[DeleteAllBeforePlan List_Skip] != true } "
                                                ,"", "");

            // Delete Object Process
            query = query + 'exec parallel begin  ';
            for ( var i = 0; i < result.cs.rowCount; i++ ) {
                var Seq = vdUtil.fn_getDimValue(result, i, "Seq", "Seq");
                var DataObject = vdUtil.fn_getString(result.cs.row(i).cell(result.cs.measureColumnIndex("DeleteAllBeforePlan List_Object")));
                var Type = vdUtil.fn_getString(result.cs.row(i).cell(result.cs.measureColumnIndex("DeleteAllBeforePlan List_Type")));
                var Condition = vdUtil.fn_getString(result.cs.row(i).cell(result.cs.measureColumnIndex("DeleteAllBeforePlan List_Condition")));
                var LeadOffSet = vdUtil.fn_getString(result.cs.row(i).cell(result.cs.measureColumnIndex("DeleteAllBeforePlan List_LeadOffSet")));
                var UserDefined = vdUtil.fn_getString(result.cs.row(i).cell(result.cs.measureColumnIndex("DeleteAllBeforePlan List_User Defined")));

                query = query + 'block begin  ';
                if (Type == "Measure"){
                    if (Condition == "Day"){
                        query = query + 'scope:([Version].[Version Name].['  +  TargetVersion  +  '] * [Time].[Day].filter(#.Key >= &CurrentWeek.element('  +  LeadOffSet  +  ').Key));  ';
                    }
                    else if (Condition == "Week"){
                        query = query + 'scope:([Version].[Version Name].['  +  TargetVersion  +  '] * [Time].[Week].filter(#.Key >= &CurrentWeek.element('  +  LeadOffSet  +  ').Key));  ';
                    }
                    else if (Condition == "Month"){
                        query = query + 'scope:([Version].[Version Name].['  +  TargetVersion  +  '] * [Time].[Month].filter(#.Key >= &CurrentWeek.element('  +  LeadOffSet  +  ').Key));  ';
                    }
                    else if (Condition == "User Defined"){
                        query = query + 'scope:([Version].[Version Name].['  +  TargetVersion  +  '] * '  +  UserDefined  +  ');  ';
                    }
                    else {
                        query = query + 'scope:([Version].[Version Name].['  +  TargetVersion  +  ']);  ';
                    }
                    query = query + 'Measure.['  +  DataObject  +  '] = null;  ';
                    query = query + 'end scope;  ';
                }
                else {
                    if (Type == "Measure Group"){
                        query = query + 'DELETE DATA FOR MODEL ['  +  DataObject  +  '] ';
                    }
                    else if (Type == "Graph"){
                        query = query + 'DELETE DATA FOR GRAPH ['  +  DataObject  +  '] ';
                    }

                    if (Condition == "Day"){
                        query = query + 'where {[Version].[Version Name].['  +  TargetVersion  +  '] * [Time].[Day].filter(#.Key >= &CurrentWeek.element('  +  LeadOffSet  +  ').Key)};  ';
                    }
                    else if (Condition == "Week"){
                        query = query + 'where {[Version].[Version Name].['  +  TargetVersion  +  '] * [Time].[Week].filter(#.Key >= &CurrentWeek.element('  +  LeadOffSet  +  ').Key)};  ';
                    }
                    else if (Condition == "Month"){
                        query = query + 'where {[Version].[Version Name].['  +  TargetVersion  +  '] * [Time].[Month].filter(#.Key >= &CurrentWeek.element('  +  LeadOffSet  +  ').Key)};  ';
                    }
                    else if (Condition == "User Defined"){
                        query = query + 'where {[Version].[Version Name].['  +  TargetVersion  +  '] * '  +  UserDefined  +  '};  ';
                    }
                    else {
                        query = query + 'where {[Version].[Version Name].['  +  TargetVersion  +  ']};  ';
                    }
                }
                query = query + 'end  ';
            }
            query = query + 'end;';

            vdCommon.debug("Query : " + query);
            vdCommon.executeQuery("Execute Result", query);

            vdCommon.programEnd();
        } catch ( e ) {
            RuleOutputToUI = { Status : 'Error', Message : "Js Logic Error : " + e.message };
            return;
        }
    };


	
    return {
        CreateBackupVersion : CreateBackupVersion,
        UpdateBackupVersion : UpdateBackupVersion,
        CreateLWScenario : CreateLWScenario,
        UpdateLWScenario : UpdateLWScenario,
        planCycleRollingLW : planCycleRollingLW,
        DeleteAllBeforePlan : DeleteAllBeforePlan
    };
});

/**************************** o9.NSCM.JSObjectMgmt *********************************
    2026-03-10 : 최초 작성
    2026-03-13 : Skip, Type, Condition, LeadOffSet, UserDefined 필드 반영
    2026-03-16 : CreateLWScenario 신규 생성,   CreateBackupVersion에서 Init Dttm/By, Up Dttm/By Cleansing 기능 추가
    2026-03-19 : planCycleRollingLW, UpdateLWScenario 신규 생성
    2026-03-23 : DeleteAllBeforePlan 신규 생성
******************************************************************************************/