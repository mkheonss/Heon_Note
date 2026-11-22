define('o9.NSCM.JSScenarioCreation', ['o9/data/query', 'o9/data/cellset', 'o9.NSCM.commonLib'], function () {
    const programName = "o9.NSCM.JSScenarioCreation";

	var scenarioCreation = function(o9Params){
        try {
	        const commonLib = require('o9.NSCM.commonLib');
            const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
            const vdUtil = new commonLib.VdUtil();

            vdCommon.setLogLevel("Debug");
            vdCommon.printParams(o9Params);

            var parsedParams = JSON.parse(o9Params);
            var fbSourceVersion = parsedParams.fbSourceVersion;
            var fbPlanType = parsedParams.fbPlanType;
            var fbDescription = parsedParams.Description;

            var CurrentWeek = vdCommon.selectResult('&CurrentWeek.element(0).DisplayName');
            // 당주인지 체크
            if ( CurrentWeek != fbSourceVersion.substr(0,6) ) {
                RuleOutputToUI = { Status : 'Error', Message : "화요일 오후 1시 이후부터 시나리오 생성이 가능합니다." };
                return;
            }

            var SourceKey = vdCommon.selectResult('Version.[Version Name].filter(#.DisplayName == "' + fbSourceVersion + '").element(0).Key');
            var SourceName = vdCommon.selectResult('Version.[Version Name].filter(#.DisplayName == "' + fbSourceVersion + '").element(0).Name');            
            var UserId = vdCommon.selectResult('CurrentUser().[User Name]');
            // Max 값을 구한다.
            var SeqMax = vdCommon.selectList(['&Sim.filter(#.DisplayName startswith "' + CurrentWeek + '")'],
                                             [],
                                             "",
                                             "orderby [Version].[Version Name].DisplayName desc",
                                             "limit 1");
            var Seq = "1";
            if ( SeqMax.cs.rowCount > 0 ) {
                Seq = vdUtil.fn_lpad((parseInt(SeqMax.cs.row(0).cell(SeqMax.cs.memberColumnIndex("Version", "Version Name")).Name.substr(11)) + 1) + "", 2, "0");
            }

            Seq = String(Seq).padStart(2, '0');

            vdCommon.debug("CurrentWeek : " + CurrentWeek +
                                " , SourceKey : " + SourceKey +
                                " , SourceName : " + SourceName +
                                " , UserId : " + UserId +
                                " , Seq : " + Seq);

            var TargetName = '';
            var SortingOrder = '';
            var ScenarioType = '';

            if ( fbPlanType == "MP-Simulation" ) {
                TargetName = CurrentWeek + '_WI_' + Seq;
                SortingOrder = CurrentWeek + '04';
                ScenarioType = 'Simulation';
            }

            if (Seq === "01") {
            vdCommon.updateMeasure(["[Version].[Version Name].[" + SourceName + "]"]
                        ,['Measure.[W Demand Quantity to SCS backup] = Measure.[W Demand Quantity to SCS];'
                            ,'Measure.[W Resource Base Capacity backup Sim] = Measure.[W Resource Base Capacity];'
                            ,'Measure.[W Flex Capacity Band1 backup Sim] = Measure.[W Flex Capacity Band1];'
                            ,'Measure.[W Flex Capacity Band2 backup Sim] = Measure.[W Flex Capacity Band2];'
                            ,'Measure.[W Demand Build Ahead Limit backup] = Measure.[W Demand Build Ahead Limit];'
                            ]);
            }

            vdCommon.executeQuery("Delete Version", 'deleteversion("' + TargetName + '");');

            vdCommon.executeQuery("Create Scenario" , 'createscenario(' + SourceKey + ',"' + TargetName + '");');

            vdCommon.executeQuery("Update Scenario Name" , 'updatemember(Version.[Version Name]={,"' + TargetName + '"},' +
                                                                '[Version].[Version Name$DisplayName]={"' + TargetName + '",}, ' +
                                                                '[Version].[Plan Type]={"' + fbPlanType + '",},' +
                                                                '[Version].[Description]={"' + TargetName + " (" + fbDescription + ")" +'",},' +
                                                                '[Version].[Version Name Sorting Order]={"' + SortingOrder + '",},' +
                                                                '[Version].[Version Status]={"Active",},' +
                                                                '[Version].[Version Expiry Date]={dateadd(Now(),3,"week"),},' +
                                                                '[Version].[ScenarioType]={"' + ScenarioType + '",});');

            vdCommon.createMeasure(["[Version].[Version Name].[" + TargetName + "]"]
                        ,['Measure.[Scenario Master_Scenario Description] = "' + fbDescription +'";'
                            ,'Measure.[Scenario Master_Objective_Group] = "Regular Plan";'
                            ,'Measure.[Scenario Master_Source Scenario Name] = Version.[Version Name].filter(#.DisplayName == "' + fbSourceVersion + '").element(0).DisplayName;'
                            ,'Measure.[Scenario Master_Scenario Type] = "What-If";'
                            ,'Measure.[Scenario Master_Scenario Status] = "Editable";'
                            ,'Measure.[Scenario Master_Plan Status] = "Not Started";'
                            ,'Measure.[Scenario Master_Scenario Expiry Date] = dateadd(Now(),3,"week");'
                            ,'Measure.[Scenario Master_Created By] = CurrentUser().[User Name];'
                            ,'Measure.[Scenario Master_Updated By] = CurrentUser().[User Name];'
                            ,'Measure.[Scenario Master_Creation Time] = Now();'
                            ,'Measure.[Scenario Master_Update Time] = Now();'
                            ]);

            vdCommon.programEnd();
        } catch ( e ) {
            RuleOutputToUI = { Status : 'Error', Message : "Js Logic Error : " + e.message };
            return;
        }
    };
	
    return {
        scenarioCreation : scenarioCreation
    };
});

/**************************** o9.NSCM.JSScenarioCreation ****************************
    2025-09-16 : ...
*********************************************************************/