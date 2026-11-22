define('o9.NSCM.JS_MtrlHrchyMappingRule', ['o9/data/query', 'o9/data/cellset', 'o9.NSCM.commonLib'], function () {
    const programName = "o9.NSCM.JS_MtrlHrchyMappingRule";

    var fn_add = function(o9Params){
        var commonLib = require('o9.NSCM.commonLib');

        var programName = "o9.NSCM.JS_MtrlHrchyMappingRule ============> fn_add";

        vdUtil = new commonLib.VdUtil();
        vdCommon = new commonLib.VdCommon(programName);
        vdCommon.setLogLevel("Debug");

        vdCommon.printParams(o9Params);

        // 파라미터 가져오기
        var parsedParams = JSON.parse(o9Params);
        var fbHrcyType = parsedParams.fbHrcyType;
        var fbMtrlHrchyMapRulePriority = parsedParams.fbMtrlHrchyMapRulePriority;
        var fbMtrlHrchyMapRuleCode = parsedParams.fbMtrlHrchyMapRuleCode;
        var fbMtrlHrchyMapRuleDesc = parsedParams.fbMtrlHrchyMapRuleDesc;
        var fbMtrlHrchyMapRuleLongDesc = parsedParams.fbMtrlHrchyMapRuleLongDesc;
        var fbMtrlHrchyMapRuleGrp = parsedParams.fbMtrlHrchyMapRuleGrp;
        var fbRuleNo = parsedParams.fbMtrlHrcyL3;

        if ( fbRuleNo == "-" ) {
            RuleOutputToUI = { Status : 'Error', Message : "Please select  a level info." };
            return;
        }

        vdCommon.printStep("Rule No Max");
        // Hierarchy Max 값을 구한다.
        var result = vdCommon.selectList(["[Group].[Group ID].filter(#.Name startswith([#]))"],
                                            [],
                                            "",
                                            "orderby [Group].[Group ID].Key desc",
                                            "limit 1");
        var groupId = "#" + vdUtil.fn_lpad((parseInt(result.cs.row(0).cell(result.cs.memberColumnIndex("Group", "Group ID")).Name.substr(1)) + 1) + "", 4, "0");

        // Member 를 추가한다.
        if ( !vdCommon.existMember("[Group].[Group ID]", groupId) ) {
            vdCommon.createMember("[Group].[Group ID]", groupId);
        }

        vdCommon.printStep("Measure Add");
        vdCommon.createMeasure(["[Version].[Version Name].[CWV_MP]",
                                "[Rule].[Rule No].[" + fbRuleNo + "]",
                                "[Group].[Group ID].[" + groupId + "]",
                                "[Hrcy Type].[Hrcy Type].[" + fbHrcyType + "]"],
                                ['Measure.[Mtrl Hrchy Map Rule_Priority] = "' + fbMtrlHrchyMapRulePriority + '";',
                                'Measure.[Mtrl Hrchy Map Rule_Code] = "' + vdUtil.fn_getString(fbMtrlHrchyMapRuleCode) + '";',
                                'Measure.[Mtrl Hrchy Map Rule_Desc] = "' + vdUtil.fn_getString(fbMtrlHrchyMapRuleDesc) + '";',
                                'Measure.[Mtrl Hrchy Map Rule_Long Desc] = "' + vdUtil.fn_getString(fbMtrlHrchyMapRuleLongDesc) + '";',
                                'Measure.[Mtrl Hrchy Map Rule_Grp] = "' + vdUtil.fn_getString(fbMtrlHrchyMapRuleGrp) + '";',
                                'Measure.[Mtrl Hrchy Map Rule_Apply Flag] = True;',
                                'Measure.[Mtrl Hrchy Map Rule_Status] = "Confirm";',
                                'Measure.[Mtrl Hrchy Map Rule_Update Time] = now();',
                                'Measure.[Mtrl Hrchy Map Rule_Updated By] = CurrentUser().Name;']);

        vdCommon.programEnd();
    };

    var fn_ruleNo = function(o9Params){
        var commonLib = require('o9.NSCM.commonLib');

        var programName = "o9.NSCM.JS_MtrlHrchyMappingRule ============> fn_ruleNo";

        vdUtil = new commonLib.VdUtil();
        vdCommon = new commonLib.VdCommon(programName);
        vdCommon.setLogLevel("Debug");

        vdCommon.printParams(o9Params);

        // 파라미터 가져오기
        var parsedParams = JSON.parse(o9Params);
        var fbHrcyType = parsedParams.fbHrcyType;

        var result = vdCommon.selectList(["[Version].[Version Name].[CWV_MP]",
                                            "[Rule].[Rule No]",
                                            "[Hrcy Type].[Hrcy Type].[" + fbHrcyType + "]"],
                                         ["Measure.[Mtrl Hrchy_L1 Name]", "Measure.[Mtrl Hrchy_L1 Order]",
                                         "Measure.[Mtrl Hrchy_L2 Name]", "Measure.[Mtrl Hrchy_L2 Order]",
                                         "Measure.[Mtrl Hrchy_L3 Name]", "Measure.[Mtrl Hrchy_L3 Order]",
                                         "Measure.[Mtrl Hrchy_L4 Name]", "Measure.[Mtrl Hrchy_L4 Order]", "Measure.[Mtrl Hrchy_L4 Rule]",
                                         "Measure.[Mtrl Hrchy_L5 Name]", "Measure.[Mtrl Hrchy_L5 Order]", "Measure.[Mtrl Hrchy_L5 Rule]",
                                         ],
                                         'where {coalesce(Measure.[Mtrl Hrchy_Delete Flag], "N") == "N", coalesce(Measure.[Mtrl Hrchy_Validation], "") == ""}',
                                         "orderby Measure.[Mtrl Hrchy_L1 Order], Measure.[Mtrl Hrchy_L2 Order], Measure.[Mtrl Hrchy_L3 Order]",
                                         "");
        vdCommon.printCsData(result, 3);

        var comboList = [];
        comboList.push({ Name : "-", DisplayName : "-"});
        for ( var i = 0; i < result.cs.rowCount; i++ ) {
            name = vdUtil.fn_getString(result.cs.row(i).cell(result.cs.memberColumnIndex("Rule", "Rule No")).Name);
            displayName = vdUtil.fn_getString(result.cs.row(i).cell(result.cs.measureColumnIndex("Mtrl Hrchy_L1 Name"))) + "-" +
                            vdUtil.fn_getString(result.cs.row(i).cell(result.cs.measureColumnIndex("Mtrl Hrchy_L2 Name"))) + "-" +
                            vdUtil.fn_getString(result.cs.row(i).cell(result.cs.measureColumnIndex("Mtrl Hrchy_L3 Name"))) + "-" +
                            vdUtil.fn_nvl(vdUtil.fn_nvl(vdUtil.fn_getString(result.cs.row(i).cell(result.cs.measureColumnIndex("Mtrl Hrchy_L4 Name"))), vdUtil.fn_getString(result.cs.row(i).cell(result.cs.measureColumnIndex("Mtrl Hrchy_L4 Rule")))), "*") + "-" +
                            vdUtil.fn_nvl(vdUtil.fn_nvl(vdUtil.fn_getString(result.cs.row(i).cell(result.cs.measureColumnIndex("Mtrl Hrchy_L5 Name"))), vdUtil.fn_getString(result.cs.row(i).cell(result.cs.measureColumnIndex("Mtrl Hrchy_L5 Rule")))), "*");

            comboList.push({ Name : name, DisplayName : displayName});
        }

        vdCommon.debug("ComboData : " + JSON.stringify(comboList));

        vdCommon.programEnd();

        return comboList;
    };

    var fn_change = function(o9Params){
        var commonLib = require('o9.NSCM.commonLib');

        var programName = "o9.NSCM.JS_MtrlHrchyMappingRule ============> fn_change";

        vdUtil = new commonLib.VdUtil();
        vdCommon = new commonLib.VdCommon(programName);
        vdCommon.setLogLevel("Debug");

        vdCommon.printParams(o9Params);

         // 파라미터 가져오기
        var parsedParams = JSON.parse(o9Params);
        var fbHrcyType = parsedParams.fbHrcyType;
        var fbRuleNo = parsedParams.fbRuleNo;
        var fbGroupId = parsedParams.fbGroupId;
        var fbMtrlHrchyMapRulePriority = parsedParams.fbMtrlHrchyMapRulePriority;
        var fbMtrlHrchyMapRuleSort3 = parsedParams.fbMtrlHrchyMapRuleSort3;
        var fbMtrlHrchyMapRuleCode = parsedParams.fbMtrlHrchyMapRuleCode;
        var fbMtrlHrchyMapRuleDesc = parsedParams.fbMtrlHrchyMapRuleDesc;
        var fbMtrlHrchyMapRuleLongDesc = parsedParams.fbMtrlHrchyMapRuleLongDesc;
        var fbMtrlHrchyMapRuleGrp = parsedParams.fbMtrlHrchyMapRuleGrp;
        var fbChangeRuleNo = parsedParams.fbMtrlHrcyL3;

        vdCommon.printStep("Measure Add");
        vdCommon.createMeasure(["[Version].[Version Name].[CWV_MP]",
                                    "[Rule].[Rule No].[" + fbChangeRuleNo + "]",
                                    "[Group].[Group ID].[" + fbGroupId + "]",
                                    "[Hrcy Type].[Hrcy Type].[" + fbHrcyType + "]"],
                                ['Measure.[Mtrl Hrchy Map Rule_Priority] = "' + fbMtrlHrchyMapRulePriority + '";',
                                    'Measure.[Mtrl Hrchy Map Rule_SORT3] = "' + vdUtil.fn_getString(fbMtrlHrchyMapRuleSort3) + '";',
                                    'Measure.[Mtrl Hrchy Map Rule_Code] = "' + vdUtil.fn_getString(fbMtrlHrchyMapRuleCode) + '";',
                                    'Measure.[Mtrl Hrchy Map Rule_Desc] = "' + vdUtil.fn_getString(fbMtrlHrchyMapRuleDesc) + '";',
                                    'Measure.[Mtrl Hrchy Map Rule_Long Desc] = "' + vdUtil.fn_getString(fbMtrlHrchyMapRuleLongDesc) + '";',
                                    'Measure.[Mtrl Hrchy Map Rule_Grp] = "' + vdUtil.fn_getString(fbMtrlHrchyMapRuleGrp) + '";',
                                    'Measure.[Mtrl Hrchy Map Rule_Status] = "Confirm";',
                                    'Measure.[Mtrl Hrchy Map Rule_Update Time] = now();',
                                    'Measure.[Mtrl Hrchy Map Rule_Updated By] = CurrentUser().Name;']);

        vdCommon.deleteMeasure(["[Version].[Version Name].[CWV_MP]",
                                    "[Rule].[Rule No].[" + fbRuleNo + "]",
                                    "[Group].[Group ID].[" + fbGroupId + "]",
                                    "[Hrcy Type].[Hrcy Type].[" + fbHrcyType + "]"],
                               "Mtrl Hrchy Map Rule");

        vdCommon.programEnd();
    };

    var fn_changeValidate = function(o9Params){
        var commonLib = require('o9.NSCM.commonLib');

        var programName = "o9.NSCM.JS_MtrlHrchyMappingRule ============> fn_changeValidate";

        vdUtil = new commonLib.VdUtil();
        vdCommon = new commonLib.VdCommon(programName);
        vdCommon.setLogLevel("Debug");

        vdCommon.printParams(o9Params);

         // 파라미터 가져오기
        var parsedParams = JSON.parse(o9Params);
        var fbHrcyType = parsedParams.fbHrcyType;
        var fbRuleNo = parsedParams.fbRuleNo;
        var fbGroupId = parsedParams.fbGroupId;

        vdCommon.programEnd();

        return (fbGroupId.substring(0,1) == "#" ? 0 : 1);
    };

    var fn_delete = function(o9Params){
        try {
            var commonLib = require('o9.NSCM.commonLib');

            var programName = "o9.NSCM.JS_MtrlHrchyMappingRule ============> fn_delete";

            vdUtil = new commonLib.VdUtil();
            vdCommon = new commonLib.VdCommon(programName);
            vdCommon.setLogLevel("Debug");

            vdCommon.printParams(o9Params);

             // 파라미터 가져오기
            var parsedParams = JSON.parse(o9Params);
            var fbSelect = parsedParams.fbSelect;
            var fbHrcyType = parsedParams.fbHrcyType;

            for ( var i = 0; i < fbSelect.length; i++ ) {
                var row = fbSelect[i];
                vdCommon.deleteMeasure(["[Version].[Version Name].[CWV_MP]",
                                            "[Rule].[Rule No].[" + row.RuleNo.Value + "]",
                                            "[Group].[Group ID].[" + row.GroupId.Value + "]",
                                            "[Hrcy Type].[Hrcy Type].[" + fbHrcyType + "]"],
                                       "Mtrl Hrchy Map Rule");
            }

            vdCommon.programEnd();
        } catch ( e ) {
            RuleOutputToUI = { Status : 'Error', Message : "Js Logic Error : " + e.message };
            return;
        }
    };

    var fn_reqConfirm = function(o9Params){
        var commonLib = require('o9.NSCM.commonLib');

        var programName = "o9.NSCM.JS_MtrlHrchyMappingRule ============> fn_reqConfirm";

        vdUtil = new commonLib.VdUtil();
        vdCommon = new commonLib.VdCommon(programName);
        vdCommon.setLogLevel("Debug");

        vdCommon.printParams(o9Params);

         // 파라미터 가져오기
        var parsedParams = JSON.parse(o9Params);
        var fbHrcyType = parsedParams.fbHrcyType;
        var fbRuleNo = parsedParams.fbRuleNo;
        var fbGroupId = parsedParams.fbGroupId;
        var fbMtrlHrchyMapRulePriority = parsedParams.fbMtrlHrchyMapRulePriority;
        var fbMtrlHrchyMapRuleSort3 = parsedParams.fbMtrlHrchyMapRuleSort3;
        var fbMtrlHrchyMapRuleCode = parsedParams.fbMtrlHrchyMapRuleCode;
        var fbMtrlHrchyMapRuleDesc = parsedParams.fbMtrlHrchyMapRuleDesc;
        var fbMtrlHrchyMapRuleLongDesc = parsedParams.fbMtrlHrchyMapRuleLongDesc;
        var fbMtrlHrchyMapRuleGrp = parsedParams.fbMtrlHrchyMapRuleGrp;
        var fbChangeRuleNo = parsedParams.fbMtrlHrcyL3;

        var result = vdCommon.selectList(["[Group].[Group ID].filter(#.Name startswith([#]))"],
                                            [],
                                            "",
                                            "orderby [Group].[Group ID].Key desc",
                                            "limit 1");
        var groupId = "#" + vdUtil.fn_lpad((parseInt(result.cs.row(0).cell(result.cs.memberColumnIndex("Group", "Group ID")).Name.substr(1)) + 1) + "", 4, "0");
        // Member 를 추가한다.
        if ( !vdCommon.existMember("[Group].[Group ID]", groupId) ) {
            vdCommon.createMember("[Group].[Group ID]", groupId);
        }

        vdCommon.printStep("Measure Add");
        vdCommon.createMeasure(["[Version].[Version Name].[CWV_MP]",
                                    "[Rule].[Rule No].[" + fbChangeRuleNo + "]",
                                    "[Group].[Group ID].[" + groupId + "]",
                                    "[Hrcy Type].[Hrcy Type].[" + fbHrcyType + "]"],
                                ['Measure.[Mtrl Hrchy Map Rule_Priority] = "' + fbMtrlHrchyMapRulePriority + '";',
                                    'Measure.[Mtrl Hrchy Map Rule_SORT3] = "' + vdUtil.fn_getString(fbMtrlHrchyMapRuleSort3) + '";',
                                    'Measure.[Mtrl Hrchy Map Rule_Code] = "' + vdUtil.fn_getString(fbMtrlHrchyMapRuleCode) + '";',
                                    'Measure.[Mtrl Hrchy Map Rule_Desc] = "' + vdUtil.fn_getString(fbMtrlHrchyMapRuleDesc) + '";',
                                    'Measure.[Mtrl Hrchy Map Rule_Long Desc] = "' + vdUtil.fn_getString(fbMtrlHrchyMapRuleLongDesc) + '";',
                                    'Measure.[Mtrl Hrchy Map Rule_Grp] = "' + vdUtil.fn_getString(fbMtrlHrchyMapRuleGrp) + '";',
                                    'Measure.[Mtrl Hrchy Map Rule_Apply Flag] = True;',
                                    'Measure.[Mtrl Hrchy Map Rule_Status] = "Confirm";',
                                    'Measure.[Mtrl Hrchy Map Rule_Update Time] = now();',
                                    'Measure.[Mtrl Hrchy Map Rule_Updated By] = CurrentUser().Name;']);

        vdCommon.deleteMeasure(["[Version].[Version Name].[CWV_MP]",
                                    "[Rule].[Rule No].[" + fbRuleNo + "]",
                                    "[Group].[Group ID].[" + fbGroupId + "]",
                                    "[Hrcy Type].[Hrcy Type].[" + fbHrcyType + "]"],
                               "Mtrl Hrchy Map Rule");

        vdCommon.programEnd();
    };

    var fn_reqConfirmValidate = function(o9Params){
        var commonLib = require('o9.NSCM.commonLib');

        var programName = "o9.NSCM.JS_MtrlHrchyMappingRule ============> fn_reqConfirmValidate";

        vdUtil = new commonLib.VdUtil();
        vdCommon = new commonLib.VdCommon(programName);
        vdCommon.setLogLevel("Debug");

        vdCommon.printParams(o9Params);

         // 파라미터 가져오기
        var parsedParams = JSON.parse(o9Params);
        var fbHrcyType = parsedParams.fbHrcyType;
        var fbRuleNo = parsedParams.fbRuleNo;
        var fbGroupId = parsedParams.fbGroupId;

        vdCommon.programEnd();

        return (fbGroupId.substring(0,1) == "R" ? 0 : 1);
    };

    var fn_level1 = function(o9Params){
        try {
	        const commonLib = require('o9.NSCM.commonLib');
            const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
            const vdUtil = new commonLib.VdUtil();

            vdCommon.setLogLevel("Debug");
            vdCommon.printParams(o9Params);

            // 파라미터 가져오기
            var parsedParams = JSON.parse(o9Params);
            var fbHrcyType = parsedParams.fbHrcyType;

            vdCommon.printStep("Combo Data Get");
            var result = vdCommon.selectList(["[Version].[Version Name].[CWV_MP]",
                                                "[Rule].[Rule No]",
                                                "[Hrcy Type].[Hrcy Type].[" + fbHrcyType + "]"],
                                             ["Measure.[Mtrl Hrchy_L1 Name]", "Measure.[Mtrl Hrchy_L1 Order]"],
                                             'where {Measure.[Mtrl Hrchy_Delete Flag] == "N"}',
                                             "orderby Measure.[Mtrl Hrchy_L1 Order]",
                                             "");
            vdCommon.printCsData(result, 3);

            var comboList = [];
            var validHashMap = {};
            for ( var i = 0; i < result.cs.rowCount; i++ ) {
                comboData = result.cs.row(i).cell(result.cs.measureColumnIndex("Mtrl Hrchy_L1 Name"));

                if ( validHashMap[comboData] == undefined ) {
                    comboList.push({ Name : comboData, DisplayName : comboData});
                    validHashMap[comboData] = comboData;
                }
            }
            vdCommon.debug("ComboData : " + JSON.stringify(validHashMap));

            vdCommon.programEnd();

            return comboList;
        } catch ( e ) {
            RuleOutputToUI = { Status : 'Error', Message : "Js Logic Error : " + e.message };
            return;
        }
    };

    var fn_level2 = function(o9Params){
	    try {
	        const commonLib = require('o9.NSCM.commonLib');
            const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
            const vdUtil = new commonLib.VdUtil();

            vdCommon.setLogLevel("Debug");
            vdCommon.printParams(o9Params);

            // 파라미터 가져오기
            var parsedParams = JSON.parse(o9Params);
            var fbHrcyType = parsedParams.fbHrcyType;
            var fbMtrlHrcyL1 = parsedParams.fbMtrlHrcyL1;

            vdCommon.printStep("Combo Data Get");
            var result = vdCommon.selectList(["[Version].[Version Name].[CWV_MP]",
                                                "[Rule].[Rule No]",
                                                "[Hrcy Type].[Hrcy Type].[" + fbHrcyType + "]"],
                                             ["Measure.[Mtrl Hrchy_L2 Name]",
                                                "Measure.[Mtrl Hrchy_L2 Order]",
                                                "Measure.[Mtrl Hrchy_L2 Rule]"],
                                             'where { Measure.[Mtrl Hrchy_L1 Name] == "' + fbMtrlHrcyL1 + '", Measure.[Mtrl Hrchy_Delete Flag] == "N" }',
                                             "orderby Measure.[Mtrl Hrchy_L2 Order]",
                                             "");
            vdCommon.printCsData(result, 3);

            var comboList = [];
            var validHashMap = {};
            for ( var i = 0; i < result.cs.rowCount; i++ ) {
                comboData = vdUtil.fn_getString(result.cs.row(i).cell(result.cs.measureColumnIndex("Mtrl Hrchy_L2 Name")));

                kind = "Name:";
                if ( comboData == "" ) {
                    kind = "Rule:";
                    comboData = result.cs.row(i).cell(result.cs.measureColumnIndex("Mtrl Hrchy_L2 Rule"));
                }

                if ( validHashMap[comboData] == undefined ) {
                    comboList.push({ Name : kind + comboData, DisplayName : comboData});
                    validHashMap[comboData] = comboData;
                }
            }
            vdCommon.debug("ComboData : " + JSON.stringify(validHashMap));

            vdCommon.programEnd();

            return comboList;
        } catch ( e ) {
            RuleOutputToUI = { Status : 'Error', Message : "Js Logic Error : " + e.message };
            return;
        }
    };

    var fn_level3 = function(o9Params){
	    try {
	        const commonLib = require('o9.NSCM.commonLib');
            const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
            const vdUtil = new commonLib.VdUtil();

            vdCommon.setLogLevel("Debug");
            vdCommon.printParams(o9Params);

            // 파라미터 가져오기
            var parsedParams = JSON.parse(o9Params);
            var fbHrcyType = parsedParams.fbHrcyType;
            var fbMtrlHrcyL1 = parsedParams.fbMtrlHrcyL1;
            var fbMtrlHrcyL2 = parsedParams.fbMtrlHrcyL2;

            var whereQuery = ""
            if ( fbMtrlHrcyL2.split(":")[0] == "Name" ) {
                whereQuery = 'where { Measure.[Mtrl Hrchy_L1 Name] == "' + fbMtrlHrcyL1 + '", Measure.[Mtrl Hrchy_L2 Name] == "' + fbMtrlHrcyL2.split(":")[1] + '", Measure.[Mtrl Hrchy_Delete Flag] == "N" }';
            } else {
                whereQuery = 'where { Measure.[Mtrl Hrchy_L1 Name] == "' + fbMtrlHrcyL1 + '", Measure.[Mtrl Hrchy_L2 Rule] == "' + fbMtrlHrcyL2.split(":")[1] + '", Measure.[Mtrl Hrchy_Delete Flag] == "N" }';
            }
            vdCommon.printStep("Combo Data Get");
            var result = vdCommon.selectList(["[Version].[Version Name].[CWV_MP]",
                                                "[Rule].[Rule No]",
                                                "[Hrcy Type].[Hrcy Type].[" + fbHrcyType + "]"],
                                             ["Measure.[Mtrl Hrchy_L3 Name]", "Measure.[Mtrl Hrchy_L3 Order]", "Measure.[Mtrl Hrchy_L3 Rule]",
                                             "Measure.[Mtrl Hrchy_L4 Name]", "Measure.[Mtrl Hrchy_L4 Order]", "Measure.[Mtrl Hrchy_L4 Rule]",
                                             "Measure.[Mtrl Hrchy_L5 Name]", "Measure.[Mtrl Hrchy_L5 Order]", "Measure.[Mtrl Hrchy_L5 Rule]"],
                                             whereQuery,
                                             "orderby Measure.[Mtrl Hrchy_L3 Order]",
                                             "");
            vdCommon.printCsData(result, 3);

            var comboList = [];
            for ( var i = 0; i < result.cs.rowCount; i++ ) {
                name = vdUtil.fn_getString(result.cs.row(i).cell(result.cs.memberColumnIndex("Rule", "Rule No")).Name);
                displayName = vdUtil.fn_nvl(vdUtil.fn_getString(result.cs.row(i).cell(result.cs.measureColumnIndex("Mtrl Hrchy_L3 Name"))), vdUtil.fn_getString(result.cs.row(i).cell(result.cs.measureColumnIndex("Mtrl Hrchy_L3 Rule")))) + " - " +
                                vdUtil.fn_nvl(vdUtil.fn_nvl(vdUtil.fn_getString(result.cs.row(i).cell(result.cs.measureColumnIndex("Mtrl Hrchy_L4 Name"))), vdUtil.fn_getString(result.cs.row(i).cell(result.cs.measureColumnIndex("Mtrl Hrchy_L4 Rule")))), "*") + " - " +
                                vdUtil.fn_nvl(vdUtil.fn_nvl(vdUtil.fn_getString(result.cs.row(i).cell(result.cs.measureColumnIndex("Mtrl Hrchy_L5 Name"))), vdUtil.fn_getString(result.cs.row(i).cell(result.cs.measureColumnIndex("Mtrl Hrchy_L5 Rule")))), "*");

                comboList.push({ Name : name, DisplayName : displayName});
            }
            vdCommon.debug("ComboData : " + JSON.stringify(comboList));

            vdCommon.programEnd();

            return comboList;
        } catch ( e ) {
            RuleOutputToUI = { Status : 'Error', Message : "Js Logic Error : " + e.message };
            return;
        }
    };

    return {
        fn_add : fn_add,
        fn_change : fn_change,
        fn_ruleNo : fn_ruleNo,
        fn_changeValidate : fn_changeValidate,
        fn_delete : fn_delete,
        fn_reqConfirm : fn_reqConfirm,
        fn_reqConfirmValidate : fn_reqConfirmValidate,
        fn_level1 : fn_level1,
        fn_level2 : fn_level2,
        fn_level3 : fn_level3
    };
});

/**************************** o9.NSCM.JS_MtrlHrchyMappingRule ****************************
    2025-2-24 : Version Name 을 CWV_MP 로 변경
*********************************************************************/