define('o9.NSCM.JSWhatIfScenario', ['o9/data/query', 'o9/data/cellset', 'o9.NSCM.commonLib', 'o9.NSCM.commonLibVD'], function () {
    const programName = "o9.NSCM.JSWhatIfScenario";
    const commonLib = require('o9.NSCM.commonLib');
    const vdUtil = new commonLib.VdUtil();
    const log = new commonLib.VdCommon(programName);
    log.setLogLevel("Debug");


	var fn_creation = function(o9Params){
        const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);

        try {
            vdCommon.printParams(o9Params);

            var p = JSON.parse(o9Params);
            
            var planType = "";
            if ( p.fbVersion.indexOf("_P") > -1 ) {
                planType = "PRE"
            } else if ( p.fbVersion.indexOf("_M") > -1 ) {
                planType = "MAIN"
            }

            if ( planType != "" ) {
                var currentWeek = vdCommon.selectResult('&CurrentWeek.element(0).DisplayName');
                var sVersion = "";
                var nVersion = "";
                var scenarioType = "";
                var scenarioType_Input = "";
                if ( planType == "PRE" ) {
                    sVersion = "CWV_MP_INI_PRE";
                    nVersion = currentWeek + "_P_WI_";
                    scenarioType = "What-If Pre";
                    scenarioType_Input = "What-If AllocPur Pre";
                } else if ( planType == "MAIN" ) {
                    sVersion = "CWV_MP_INI_MAIN";
                    nVersion = currentWeek + "_M_WI_";
                    scenarioType = "What-If Main";
                    scenarioType_Input = "What-If AllocPur Main";
                }

                var seq = "01";
                var result = vdCommon.selectList(['[Version].[Version Name].filter(#.Name startswith "' + nVersion + '")'], [], "", "orderby [Version].[Version Name].Name desc", "limit 1");
                if ( result.cs.rowCount == 1 ) {
                    var lVersion = vdUtil.fn_getDimValue(result, 0, "Version", "Version Name");
                    seq = vdUtil.fn_lpad((parseInt(lVersion.substr(-2)) + 1) + "", 2, "0");
                }
                nVersion += seq;

                vdCommon.debug("currentWeek : " + currentWeek +
                                    " , planType : " + planType +
                                    " , sVersion : " + sVersion +
                                    " , nVersion : " + nVersion +
                                    " , scenarioType : " + scenarioType);

                // 25-12-26 : Demand Modification을 위한 초기화
                //if (seq === "01") {
                //vdCommon.updateMeasure(["[Version].[Version Name].[" + sVersion + "]"]
                //            ,['Measure.[W Demand Quantity to SCS backup] = Measure.[W Demand Quantity to SCS];'
                //                ,'Measure.[W Demand Build Ahead Limit backup] = Measure.[W Demand Build Ahead Limit];'
                //                ]);
                //}

                var SourceKey = vdCommon.selectResult('Version.[Version Name].[' + sVersion + '].Key');
                vdCommon.executeQuery("Create Scenario" , 'createscenario(' + SourceKey + ',"' + nVersion + '");');

                // 25-12-17 : Current Running Flag 업데이트
                var result = vdCommon.selectList(['[Version].[Version Name].filter(#.[Plan Type] == "What-If" && #.[Current Running Flag] == true)'], [], "", "", "");
                for ( var i = 0; i < result.cs.rowCount; i++ ) {
                    var versionName = vdUtil.fn_getDimValue(result, i, "Version", "Version Name");

                    vdCommon.executeQuery("Current Running Flag = false", 'updatemember( Version.[Version Name]={,"' + versionName + '"}, ' +
                                                                            ' [Version].[Current Running Flag]={false,});');
                }

                vdCommon.executeQuery("Update Scenario Name" , 'updatemember(Version.[Version Name]={,"' + nVersion + '"},' +
                                                                    '[Version].[Version Name$DisplayName]={"' + nVersion + '",}, ' +
                                                                    '[Version].[Plan Type]={"What-If",},' +
                                                                    //'Version.[Current Running Flag]={true,},' +
								                                    '[Version].[Description]={"' + nVersion + " (" + p.Description + ")" +'",},' +
								                                    '[Version].[Version Expiry Date]={dateadd(Now(),12,"week"),},' +
                                                                    '[Version].[ScenarioType]={"' + scenarioType + '",});');

                vdCommon.executeQuery("Create Scenario" , 'createscenario(' + SourceKey + ',"Input_' + nVersion + '") include models [Alloc Pur Sum], [Alloc Pur];');

                // 26-02-26 : Plan Type, ScenarioType Update
                vdCommon.executeQuery("Update Scenario Name" , 'updatemember(Version.[Version Name]={,"Input_' + nVersion + '"},' +
                                                                    '[Version].[Version Name$DisplayName]={"Input_' + nVersion + '",}, ' +
                                                                    '[Version].[Plan Type]={"What-If AllocPur",},' +
								    '[Version].[Version Expiry Date]={dateadd(Now(),12,"week"),},' +
                                                                    '[Version].[ScenarioType]={"' + scenarioType_Input + '",});');

                // 25-12-26 : Scenario Masater에 Update
                vdCommon.createMeasure(["[Version].[Version Name].[" + nVersion + "]"]
                            ,['Measure.[Scenario Master_Scenario Description] = "' + p.Description +'";'
                                ,'Measure.[Scenario Master_Objective_Group] = "Regular Plan";'
                                ,'Measure.[Scenario Master_Source Scenario Name] = Version.[Version Name].[' + p.fbVersion + '].DisplayName;'
                                ,'Measure.[Scenario Master_Scenario Type] = "What-If";'
                                ,'Measure.[Scenario Master_Scenario Status] = "Editable";'
                                ,'Measure.[Scenario Master_Plan Status] = "Not Started";'
                                ,'Measure.[Scenario Master_PlanGroup] = "All";'
                                ,'Measure.[Scenario Master_Scenario Expiry Date] = dateadd(Now(),12,"week");'
                                ,'Measure.[Scenario Master_Created By] = CurrentUser().[User Name];'
                                ,'Measure.[Scenario Master_Updated By] = CurrentUser().[User Name];'
                                ,'Measure.[Scenario Master_Creation Time] = Now();'
                                ,'Measure.[Scenario Master_Update Time] = Now();'
                                ]);
            }
            vdCommon.programEnd();
        } catch ( e ) {
            vdCommon.error(e.message);
            RuleOutputToUI = { Status : 'Error', Message : "Js Logic Error : " + e.message };
            return;
        }
    };


	var fn_deletion = function(o9Params){
        const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);

        try {
            vdCommon.printParams(o9Params);

            var p = JSON.parse(o9Params);

            vdCommon.executeQuery("Delete Scenario" , 'deleteversion("' + p.fbVersion + '");');
            vdCommon.executeQuery("Delete Scenario" , 'deleteversion("Input_' + p.fbVersion + '");');

            vdCommon.programEnd();
        } catch ( e ) {
            vdCommon.error(e.message);
            RuleOutputToUI = { Status : 'Error', Message : "Js Logic Error : " + e.message };
            return;
        }
    };


    var fn_validation = function(o9Params){
        const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
        vdCommon.setLogLevel("Debug");
        vdCommon.printParams(o9Params);

        var rtn = 0;

        try {
            // 파라미터 가져오기
            var p = JSON.parse(o9Params);

            var CurrentWeek = vdCommon.selectResult('&CurrentWeek.element(0).DisplayName');
            vdCommon.debug("CurrentWeek : " + CurrentWeek);

            if ( p.fbVersion.length > 1 ) {
                RuleOutputToUI = { Status : 'Error', Message : "Plan을 하나만 선택하세요." };
                return 1;
            } else {
                // 당주인지 체크
                if ( CurrentWeek != p.fbVersion[0].substr(0,6) ) {
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

    var fn_validation_editplangroup = function(o9Params){
        const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
        vdCommon.setLogLevel("Debug");
        vdCommon.printParams(o9Params);

        var rtn = 0;

        try {
            // 파라미터 가져오기
            var p = JSON.parse(o9Params);

            vdCommon.debug("Version Name : " + p.fbVersion);

            if ( p.fbVersion.length > 1 ) {
                RuleOutputToUI = { Status : 'Error', Message : "Plan을 하나만 선택하세요." };
                return 1;
            } else {
                // 차주인지 체크
                if ( p.fbVersion[0].substr(0,7) != "CWV_OBJ" ) {
                    RuleOutputToUI = { Status : 'Error', Message : "PlanGroup을 수정할 수 없는 Version입니다." };
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

    var fn_validation_planrun = function(o9Params){
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
                //if ( CurrentWeek != p.Version[0].substr(0,6) ) {
                //    RuleOutputToUI = { Status : 'Error', Message : "당주 Plan으로 다시 선택하세요." };
                //    return 1;
                //}

                // Rerun인지 체크
                //var result = vdCommon.selectList(["[Version].[Version Name]" + vdUtil.fn_filterStr(p.Version)],
                //                                 ["Measure.[Scenario Master_Plan Status]"],
                //                                 "", "", "");
                //var planStatus = vdUtil.fn_getMeaValue(result, 0, "Scenario Master_Plan Status");
                //vdCommon.debug("Plan Status : " + planStatus);
                //if ( planStatus == "Completed") {
                //    RuleOutputToUI = { Status : 'Error', Message : "해당 Plan으로 ReRun은 불가능합니다." };
                //    return 1;
                //}

                // 동일 주차에 실행이 있는지 체크
                
                var result = vdCommon.selectList(["&Sim" + vdUtil.fn_filterStr(CurrentWeek + "%")],
                                                 ["Measure.[Scenario Master_Plan Status]"],
                                                 'where { Measure.[Scenario Master_Plan Status] == "Running" }', "", "");
                if ( result.cs.rowCount > 0 ) {
                    RuleOutputToUI = { Status : 'Error', Message : "현재 Running 중인 Plan이 있습니다." };
                    return 1;
                }
                

                // Objective Set이 있는지 체크
                //var result = vdCommon.selectList(["[Version].[Version Name]" + vdUtil.fn_filterStr(p.Version)],
                //                                 ["Measure.[Scenario Master_Objective_Group]"],
                //                                 "", "", "");
                                                 
                //var planGroup = result.cs.row(0).cell(result.cs.measureColumnIndex("Scenario Master_Objective_Group"));
                //vdCommon.debug("Plan Group : " + planGroup);
                
                //if (typeof planGroup == 'undefined'){
                //    RuleOutputToUI = { Status : 'Error', Message : "해당 Plan은 Objective Set이 지정되지 않았습니다." };
                //    return 1;
                //}
                
            }

            vdCommon.programEnd();
        } catch ( e ) {
            RuleOutputToUI = { Status : 'Error', Message : "Js Logic Error : " + e.message };
            return 1;
        }

        return rtn;
    };


    var fn_whatif_creation = function(o9Params){
        const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);

        try {
            vdCommon.printParams(o9Params);

            var p = JSON.parse(o9Params);
            
            var planType = "";
            if ( p.Version.indexOf("_P") > -1 ) {
                planType = "PRE"
            } else if ( p.Version.indexOf("_M") > -1 ) {
                planType = "MAIN"
            }

            if ( planType != "" ) {
                var currentWeek = vdCommon.selectResult('&CurrentWeek.element(0).DisplayName');
                var sVersion = "";
                var nVersion = "";
                var scenarioType = "";
                if ( planType == "PRE" ) {
                    sVersion = "CWV_MP_INI_PRE";
                    scenarioType = "What-If Pre";
                } else if ( planType == "MAIN" ) {
                    sVersion = "CWV_MP_INI_MAIN";
                    scenarioType = "What-If Main";
                }

                nVersion = p.Version
                var SourceKey = vdCommon.selectResult('Version.[Version Name].[' + sVersion + '].Key');

                // 26-03-11 : Current Running Flag 업데이트
                var result = vdCommon.selectList(['[Version].[Version Name].filter(#.[Plan Type] == "What-If" && #.[Current Running Flag] == true)'], [], "", "", "");
                for ( var i = 0; i < result.cs.rowCount; i++ ) {
                    var versionName = vdUtil.fn_getDimValue(result, i, "Version", "Version Name");

                    vdCommon.executeQuery("Current Running Flag = false", 'updatemember( Version.[Version Name]={,"' + versionName + '"}, ' +
                                                                            ' [Version].[Current Running Flag]={false,});');
                }

                vdCommon.executeQuery("Delete Scenario", 'deleteversion("' + nVersion + '");');
                vdCommon.executeQuery("Create Scenario" , 'createscenario(' + SourceKey + ',"' + nVersion + '");');
                vdCommon.executeQuery("Update Scenario Name" , 'updatemember(Version.[Version Name]={,"' + nVersion + '"},' +
                                                                    '[Version].[Version Name$DisplayName]={"' + nVersion + '",}, ' +
                                                                    'Version.[Plan Type]={"What-If",},' +
                                                                    'Version.[Current Running Flag]={true,},' +
								                                    '[Version].[Version Expiry Date]={dateadd(Now(),12,"week"),},' +
                                                                    '[Version].[ScenarioType]={"' + scenarioType + '",});');

            }


            vdCommon.programEnd();
        } catch ( e ) {
            vdCommon.error(e.message);
            RuleOutputToUI = { Status : 'Error', Message : "Js Logic Error : " + e.message };
            return;
        }
    };


    return {
        fn_creation : fn_creation,
        fn_deletion : fn_deletion,
        fn_validation : fn_validation,
        fn_validation_planrun : fn_validation_planrun,
        fn_validation_editplangroup : fn_validation_editplangroup,
        fn_whatif_creation : fn_whatif_creation
    };
});

/**************************** o9.NSCM.JSWhatIfScenario *******************************
    2025-12-26 : 최초 생성
    2025-12-29 : fn_creation 수정 (Description과 Expiry date 추가, Plan Group Default = "All")
    2026-01-30 : fn_validation_editplangroup 신규 생성
    2026-02-11:  fn_creation running flag=true로 만드는 작업 제거
    2026-02-11:  fn_whatif_creation 신규 생성
    2026-02-23:  expiry date 3주 -> 12주로 수정
    2026-02-26:  fn_creation에서 Input 시나리오의 Plan Type, Scenario Type Property도 Update하는 로직 추가
    2026-03-11:  fn_whatif_creation에서 기존 시나리오의 current running flag = false로 Update
*******************************************************************************************/