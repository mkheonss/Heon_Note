define('o9.NSCM.JS_MtrlHrchy', ['o9/data/query', 'o9/data/cellset', 'o9.NSCM.commonLib'], function () {
    const programName = "o9.NSCM.JS_MtrlHrchy";

    var fn_add = function(o9Params){
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
        var fbMtrlHrcyL3 = parsedParams.fbMtrlHrcyL3;
        var fbMtrlHrcyL4 = parsedParams.fbMtrlHrcyL4;
        var fbMtrlHrcyL5 = parsedParams.fbMtrlHrcyL5;
        var fbMtrlHrcyL1Order = parsedParams.fbMtrlHrcyL1Order;
        var fbMtrlHrcyL2Order = parsedParams.fbMtrlHrcyL2Order;
        var fbMtrlHrcyL3Order = parsedParams.fbMtrlHrcyL3Order;
        var fbMtrlHrcyL4Order = parsedParams.fbMtrlHrcyL4Order;
        var fbMtrlHrcyL5Order = parsedParams.fbMtrlHrcyL5Order;
        var fbScmMaterial = parsedParams.fbScmMaterial;

        if ( fbMtrlHrcyL4 == null ) {
            fbMtrlHrcyL4 = "";
        }
        if ( fbMtrlHrcyL5 == null ) {
            fbMtrlHrcyL5 = "";
        }

        if ( fbMtrlHrcyL4 == "" && fbMtrlHrcyL5 != "" ) {
            RuleOutputToUI = { Status : 'Error', Message : "Please enter Level 4" };
            return;
        }
        if ( !vdUtil.fn_isInt(fbMtrlHrcyL1Order) ) {
            RuleOutputToUI = { Status : 'Error', Message : "Please enter an integer(Level 1 Order)" };
            return;
        }
        if ( !vdUtil.fn_isInt(fbMtrlHrcyL2Order) ) {
            RuleOutputToUI = { Status : 'Error', Message : "Please enter an integer(Level 2 Order)" };
            return;
        }
        if ( !vdUtil.fn_isInt(fbMtrlHrcyL3Order) ) {
            RuleOutputToUI = { Status : 'Error', Message : "Please enter an integer(Level 3 Order)" };
            return;
        }
        if ( fbMtrlHrcyL4Order != null && !vdUtil.fn_isInt(fbMtrlHrcyL4Order) ) {
            RuleOutputToUI = { Status : 'Error', Message : "Please enter an integer(Level 4 Order)" };
            return;
        }
        if ( fbMtrlHrcyL5Order != null && !vdUtil.fn_isInt(fbMtrlHrcyL5Order) ) {
            RuleOutputToUI = { Status : 'Error', Message : "Please enter an integer(Level 5 Order)" };
            return;
        }

        vdCommon.printStep("Rule No Max");
        // Hierarchy Max 값을 구한다.
        var result = vdCommon.selectList(["[Rule].[Rule No].filter(#.Name != \"-\")"],
                                            [],
                                            "",
                                            "orderby [Rule].[Rule No].Key desc",
                                            "limit 1");
        var ruleNo = vdUtil.fn_lpad((parseInt(result.cs.row(0).cell(result.cs.memberColumnIndex("Rule", "Rule No")).Name) + 1) + "", 4, "0");

        // Member 를 추가한다.
        if ( !vdCommon.existMember("[Rule].[Rule No]", ruleNo) ) {
            vdCommon.createMember("[Rule].[Rule No]", ruleNo);
        }
        /*
        var l1Order = 99;
        var l2Order = 99;
        var l3Order = 99;
        vdCommon.printStep("Measure Add");
        // Level별 정렬값을 구한다.
        result = vdCommon.selectList(["[Version].[Version Name].[CWV_MP]",
                                            "[Rule].[Rule No]",
                                            "[Hrcy Type].[Hrcy Type].[" + fbHrcyType + "]"],
                                        ["Measure.[Mtrl Hrchy_L1 Order]"],
                                        'where {Measure.[Mtrl Hrchy_L1 Name] == "' + fbMtrlHrcyL1 + '"} ',
                                        "",
                                        "limit 1");
        if ( result.cs.rowCount > 0 ) {
            l1Order = result.cs.row(0).cell(result.cs.measureColumnIndex("Mtrl Hrchy_L1 Order"));
        }
        result = vdCommon.selectList(["[Version].[Version Name].[CWV_MP]",
                                            "[Rule].[Rule No]",
                                            "[Hrcy Type].[Hrcy Type].[" + fbHrcyType + "]"],
                                        ["Measure.[Mtrl Hrchy_L2 Order]"],
                                        'where {Measure.[Mtrl Hrchy_L1 Name] == "' + fbMtrlHrcyL1 + '", Measure.[Mtrl Hrchy_L2 Name] == "' + fbMtrlHrcyL2 + '"}',
                                        "",
                                        "limit 1");
        if ( result.cs.rowCount > 0 ) {
            l2Order = result.cs.row(0).cell(result.cs.measureColumnIndex("Mtrl Hrchy_L2 Order"));
        }
        */

        // Measure 가 등록되어 있는지를 체크해서 넣어준다.
        if ( !vdCommon.existMeasure(["[Version].[Version Name].[CWV_MP]",
                                            "[Rule].[Rule No]",
                                            "[Hrcy Type].[Hrcy Type].[" + fbHrcyType + "]"],
                                    ["Measure.[Mtrl Hrchy_L1 Name]"],
                                    'where {Measure.[Mtrl Hrchy_L1 Name] == "' + fbMtrlHrcyL1 + '", ' +
                                        'Measure.[Mtrl Hrchy_L2 Name] == "' + fbMtrlHrcyL2 + '", ' +
                                        'Measure.[Mtrl Hrchy_L3 Name] == "' + fbMtrlHrcyL3 + '", ' +
                                        'coalesce(Measure.[Mtrl Hrchy_L4 Name], "") == "' + fbMtrlHrcyL4 + '", ' +
                                        'coalesce(Measure.[Mtrl Hrchy_L5 Name], "") == "' + fbMtrlHrcyL5 + '"}') ) {
            var granularity = [];
            granularity.push("[Version].[Version Name]");
            granularity.push("[Rule].[Rule No]");
            granularity.push("[Hrcy Type].[Hrcy Type]");
            var granularityValues = [];
            granularityValues.push("CWV_MP");
            granularityValues.push(ruleNo);
            granularityValues.push(fbHrcyType);

            vdCommon.createMeasure(vdCommon.makeDimension(granularity, granularityValues),
                        ['Measure.[Mtrl Hrchy_L1 Name] = "' + fbMtrlHrcyL1 + '";',
                        'Measure.[Mtrl Hrchy_L1 Order] = ' + fbMtrlHrcyL1Order + ';',
                        'Measure.[Mtrl Hrchy_L2 Name] = "' + fbMtrlHrcyL2 + '";',
                        'Measure.[Mtrl Hrchy_L2 Order] = ' + fbMtrlHrcyL2Order + ';',
                        'Measure.[Mtrl Hrchy_L3 Name] = "' + fbMtrlHrcyL3 + '";',
                        'Measure.[Mtrl Hrchy_L3 Order] = ' + fbMtrlHrcyL3Order + ';',
                        'Measure.[Mtrl Hrchy_L4 Name] = "' + fbMtrlHrcyL4 + '";',
                        'Measure.[Mtrl Hrchy_L4 Order] = ' + fbMtrlHrcyL4Order + ';',
                        'Measure.[Mtrl Hrchy_L5 Name] = "' + fbMtrlHrcyL5 + '";',
                        'Measure.[Mtrl Hrchy_L5 Order] = ' + fbMtrlHrcyL5Order + ';',
                        'Measure.[Mtrl Hrchy_SCM Material] = ' + fbScmMaterial + ';',
                        'Measure.[Mtrl Hrchy_Update Time] = now();',
                        'Measure.[Mtrl Hrchy_Updated By] = CurrentUser().Name;',
                        'Measure.[Mtrl Hrchy_Delete Flag] = "N";']);
        } else {
            RuleOutputToUI = { Status : 'Error', Message : "This Data has already been registered." };
            return;
        }

        vdCommon.programEnd();
    };

    var fn_level1 = function(o9Params){
        const commonLib = require('o9.NSCM.commonLib');
        const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
        const vdUtil = new commonLib.VdUtil();

        vdCommon.setLogLevel("Debug");
        vdCommon.printParams(o9Params);

        // 파라미터 가져오기
        var parsedParams = JSON.parse(o9Params);
        var fbHrcyType = parsedParams.fbHrcyType;

        var result = vdCommon.selectList(["[Version].[Version Name].[CWV_MP]",
                                            "[Rule].[Rule No]",
                                            "[Hrcy Type].[Hrcy Type].[" + fbHrcyType + "]"],
                                         ["Measure.[Mtrl Hrchy_L1 Name]", "Measure.[Mtrl Hrchy_L1 Order]"],
                                         'where { isnull(Measure.[Mtrl Hrchy_Deleted By]) }',
                                         "orderby Measure.[Mtrl Hrchy_L1 Order]",
                                         "");
        vdCommon.printCsData(result, 3);

        var comboList = vdCommon.fn_makeCombo(result, {MeasureName : "Mtrl Hrchy_L1 Name"});
        vdCommon.debug("ComboData : " + JSON.stringify(comboList));

        vdCommon.programEnd();

        return comboList;
    };

    var fn_level2 = function(o9Params){
        const commonLib = require('o9.NSCM.commonLib');
        const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
        const vdUtil = new commonLib.VdUtil();

        vdCommon.setLogLevel("Debug");
        vdCommon.printParams(o9Params);

        // 파라미터 가져오기
        var parsedParams = JSON.parse(o9Params);
        var fbHrcyType = parsedParams.fbHrcyType;
        var fbMtrlHrcyL1 = parsedParams.fbMtrlHrcyL1;

        var result = vdCommon.selectList(["[Version].[Version Name].[CWV_MP]",
                                            "[Rule].[Rule No]",
                                            "[Hrcy Type].[Hrcy Type].[" + fbHrcyType + "]"],
                                         ["Measure.[Mtrl Hrchy_L2 Name]", "Measure.[Mtrl Hrchy_L2 Order]"],
                                         'where { Measure.[Mtrl Hrchy_L1 Name] == "' + fbMtrlHrcyL1 + '", ' +
                                            'isnull(Measure.[Mtrl Hrchy_Deleted By]) }',
                                         "orderby Measure.[Mtrl Hrchy_L2 Order]",
                                         "");
        //vdCommon.printCsData(result, 3);

        var comboList = vdCommon.fn_makeCombo(result, {MeasureName : "Mtrl Hrchy_L2 Name"});
        vdCommon.debug("ComboData : " + JSON.stringify(comboList));

        vdCommon.programEnd();

        return comboList;
    };

    var fn_level3 = function(o9Params){
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

        var result = vdCommon.selectList(["[Version].[Version Name].[CWV_MP]",
                                            "[Rule].[Rule No]",
                                            "[Hrcy Type].[Hrcy Type].[" + fbHrcyType + "]"],
                                         ["Measure.[Mtrl Hrchy_L3 Name]", "Measure.[Mtrl Hrchy_L3 Order]"],
                                         'where {Measure.[Mtrl Hrchy_L1 Name] == "' + fbMtrlHrcyL1 + '", ' +
                                            'Measure.[Mtrl Hrchy_L2 Name] == "' + fbMtrlHrcyL2 + '", ' +
                                            'isnull(Measure.[Mtrl Hrchy_Deleted By]) }',
                                         "orderby Measure.[Mtrl Hrchy_L3 Order]",
                                         "");
        //vdCommon.printCsData(result, 3);

        var comboList = vdCommon.fn_makeCombo(result, {MeasureName : "Mtrl Hrchy_L3 Name"});
        vdCommon.debug("ComboData : " + JSON.stringify(comboList));

        vdCommon.programEnd();

        return comboList;
    };

    var fn_level4 = function(o9Params){
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
        var fbMtrlHrcyL3 = parsedParams.fbMtrlHrcyL3;

        var result = vdCommon.selectList(["[Version].[Version Name].[CWV_MP]",
                                            "[Rule].[Rule No]",
                                            "[Hrcy Type].[Hrcy Type].[" + fbHrcyType + "]"],
                                         ["Measure.[Mtrl Hrchy_L4 Name]", "Measure.[Mtrl Hrchy_L4 Order]"],
                                         'where {Measure.[Mtrl Hrchy_L1 Name] == "' + fbMtrlHrcyL1 + '", ' +
                                            'Measure.[Mtrl Hrchy_L2 Name] == "' + fbMtrlHrcyL2 + '", ' +
                                            'Measure.[Mtrl Hrchy_L3 Name] == "' + fbMtrlHrcyL3 + '", ' +
                                            'isnull(Measure.[Mtrl Hrchy_Deleted By]) }',
                                         "orderby Measure.[Mtrl Hrchy_L4 Order]",
                                         "");
        //vdCommon.printCsData(result, 3);

        var comboList = vdCommon.fn_makeCombo(result, {MeasureName : "Mtrl Hrchy_L4 Name"});
        vdCommon.debug("ComboData : " + JSON.stringify(comboList));

        vdCommon.programEnd();

        return comboList;
    };

    var fn_level5 = function(o9Params){
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
        var fbMtrlHrcyL3 = parsedParams.fbMtrlHrcyL3;
        var fbMtrlHrcyL4 = parsedParams.fbMtrlHrcyL4;

        var result = vdCommon.selectList(["[Version].[Version Name].[CWV_MP]",
                                            "[Rule].[Rule No]",
                                            "[Hrcy Type].[Hrcy Type].[" + fbHrcyType + "]"],
                                         ["Measure.[Mtrl Hrchy_L5 Name]", "Measure.[Mtrl Hrchy_L5 Order]"],
                                         'where {Measure.[Mtrl Hrchy_L1 Name] == "' + fbMtrlHrcyL1 + '", ' +
                                            'Measure.[Mtrl Hrchy_L2 Name] == "' + fbMtrlHrcyL2 + '", ' +
                                            'Measure.[Mtrl Hrchy_L3 Name] == "' + fbMtrlHrcyL3 + '", ' +
                                            'Measure.[Mtrl Hrchy_L4 Name] == "' + fbMtrlHrcyL4 + '", ' +
                                            'isnull(Measure.[Mtrl Hrchy_Deleted By]) }',
                                         "orderby Measure.[Mtrl Hrchy_L5 Order]",
                                         "");
        //vdCommon.printCsData(result, 3);

        var comboList = vdCommon.fn_makeCombo(result, {MeasureName : "Mtrl Hrchy_L5 Name"});
        vdCommon.debug("ComboData : " + JSON.stringify(comboList));

        vdCommon.programEnd();

        return comboList;
    };

    var fn_delete = function(o9Params){
        const commonLib = require('o9.NSCM.commonLib');
        const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
        const vdUtil = new commonLib.VdUtil();

        vdCommon.setLogLevel("Debug");
        vdCommon.printParams(o9Params);

        // 파라미터 가져오기
        var parsedParams = JSON.parse(o9Params);
        var fbHrcyType = parsedParams.fbHrcyType;
        var fbSelect = parsedParams.fbSelect;

        var granularity = [];
        granularity.push("[Version].[Version Name]");
        granularity.push("[Rule].[Rule No]");
        granularity.push("[Hrcy Type].[Hrcy Type]");

        for ( var i = 0; i < fbSelect.length; i++ ) {
            var row = fbSelect[i];

            var result = vdCommon.selectList(
                                ["&CWVUI",
                                    "[Rule].[Rule No].[" + row.RuleNo.Value + "]",
                                    "[Hrcy Type].[Hrcy Type].[" + fbHrcyType + "]"],
                                ["Measure.[Mtrl Hrchy_Delete Flag]"],
                                "",
                                "",
                                "");
            if ( result.cs.rowCount > 0 && result.cs.row(0).cell(result.cs.measureColumnIndex("Mtrl Hrchy_Delete Flag")) == "N" ) {
                var granularityValues = [];
                granularityValues.push("CWV_MP");
                granularityValues.push(row.RuleNo.Value);
                granularityValues.push(fbHrcyType);
                vdCommon.updateMeasure(vdCommon.makeDimension(granularity, granularityValues),
                                        ['Measure.[Mtrl Hrchy_Delete Time] = now();',
                                        'Measure.[Mtrl Hrchy_Deleted By] = CurrentUser().Name;',
                                        'Measure.[Mtrl Hrchy_Delete Flag] = "Y";']);
            }
        }

        vdCommon.programEnd();
    };

    var fn_restore = function(o9Params){
        // 데이타를 어제일로 남기고 지운다.
        const commonLib = require('o9.NSCM.commonLib');
        const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
        const vdUtil = new commonLib.VdUtil();

        vdCommon.setLogLevel("Debug");
        vdCommon.printParams(o9Params);

        // 파라미터 가져오기
        var parsedParams = JSON.parse(o9Params);
        var fbHrcyType = parsedParams.fbHrcyType;
        var fbSelect = parsedParams.fbSelect;

        var granularity = [];
        granularity.push("[Version].[Version Name]");
        granularity.push("[Rule].[Rule No]");
        granularity.push("[Hrcy Type].[Hrcy Type]");

        for ( var i = 0; i < fbSelect.length; i++ ) {
            var row = fbSelect[i];

            var result = vdCommon.selectList(
                                ["&CWVUI",
                                    "[Rule].[Rule No].[" + row.RuleNo.Value + "]",
                                    "[Hrcy Type].[Hrcy Type].[" + fbHrcyType + "]"],
                                ["Measure.[Mtrl Hrchy_Delete Flag]"],
                                "",
                                "",
                                "");
            if ( result.cs.rowCount > 0 && result.cs.row(0).cell(result.cs.measureColumnIndex("Mtrl Hrchy_Delete Flag")) == "Y" ) {
                var granularityValues = [];
                granularityValues.push("CWV_MP");
                granularityValues.push(row.RuleNo.Value);
                granularityValues.push(fbHrcyType);
                vdCommon.updateMeasure(vdCommon.makeDimension(granularity, granularityValues),
                                        ['Measure.[Mtrl Hrchy_Delete Time] = Null;',
                                        'Measure.[Mtrl Hrchy_Deleted By] = "";',
                                        'Measure.[Mtrl Hrchy_Delete Flag] = "N";']);
            }
        }

        vdCommon.programEnd();
    };

    var fn_level1Order = function(o9Params){
        const commonLib = require('o9.NSCM.commonLib');
        const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
        const vdUtil = new commonLib.VdUtil();

        vdCommon.setLogLevel("Debug");
        vdCommon.printParams(o9Params);

        // 파라미터 가져오기
        var parsedParams = JSON.parse(o9Params);
        var fbHrcyType = parsedParams.fbHrcyType;
        var fbMtrlHrcyL1 = parsedParams.fbMtrlHrcyL1;

        var result = vdCommon.selectList(["[Rule].[Rule No]"],
                                         ["Measure.[Mtrl Hrchy_L1 Order]"],
                                         'where { [Version].[Version Name].[CWV_MP], [Hrcy Type].[Hrcy Type].[' + fbHrcyType + '], ' +
                                            ' Measure.[Mtrl Hrchy_L1 Name] == "' + fbMtrlHrcyL1 + '", ' +
                                            'isnull(Measure.[Mtrl Hrchy_Deleted By])  }',
                                         "",
                                         "");
        var comboList = vdCommon.fn_makeCombo(result, {MeasureName : "Mtrl Hrchy_L1 Order"});
        if ( comboList.length == 0 ) {
            result = vdCommon.selectList(["[Rule].[Rule No]"],
                                         ["Measure.[Mtrl Hrchy_L1 Order]"],
                                         'where { [Version].[Version Name].[CWV_MP], [Hrcy Type].[Hrcy Type].[' + fbHrcyType + '], ' +
                                            'isnull(Measure.[Mtrl Hrchy_Deleted By])  }',
                                         "orderby Measure.[Mtrl Hrchy_L1 Order] desc",
                                         "limit 1");
            comboList = vdCommon.fn_makeCombo(result, {MeasureName : "Mtrl Hrchy_L1 Order"});
            if ( comboList.length == 0 ) {
                comboList[0] = {Name : "1", DisplayName : "1"};
            } else {
                var maxSeq = parseInt(comboList[0].Name) + 1;
                comboList[0].Name = maxSeq;
                comboList[0].DisplayName = maxSeq;
            }
        }
        vdCommon.debug("ComboData : " + JSON.stringify(comboList));

        vdCommon.programEnd();

        return comboList;
    };

    var fn_level2Order = function(o9Params){
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

        var result = vdCommon.selectList(["[Rule].[Rule No]"],
                                         ["Measure.[Mtrl Hrchy_L2 Order]"],
                                         'where { [Version].[Version Name].[CWV_MP], [Hrcy Type].[Hrcy Type].[' + fbHrcyType + '], ' +
                                            ' Measure.[Mtrl Hrchy_L1 Name] == "' + fbMtrlHrcyL1 + '", ' +
                                            ' Measure.[Mtrl Hrchy_L2 Name] == "' + fbMtrlHrcyL2 + '", ' +
                                            'isnull(Measure.[Mtrl Hrchy_Deleted By])  }',
                                         "",
                                         "");
        var comboList = vdCommon.fn_makeCombo(result, {MeasureName : "Mtrl Hrchy_L2 Order"});
        if ( comboList.length == 0 ) {
            result = vdCommon.selectList(["[Rule].[Rule No]"],
                                         ["Measure.[Mtrl Hrchy_L2 Order]"],
                                         'where { [Version].[Version Name].[CWV_MP], [Hrcy Type].[Hrcy Type].[' + fbHrcyType + '], ' +
                                            ' Measure.[Mtrl Hrchy_L1 Name] == "' + fbMtrlHrcyL1 + '", ' +
                                            'isnull(Measure.[Mtrl Hrchy_Deleted By])  }',
                                         "orderby Measure.[Mtrl Hrchy_L2 Order] desc",
                                         "limit 1");
            comboList = vdCommon.fn_makeCombo(result, {MeasureName : "Mtrl Hrchy_L2 Order"});
            if ( comboList.length == 0 ) {
                comboList[0] = {Name : "1", DisplayName : "1"};
            } else {
                var maxSeq = parseInt(comboList[0].Name) + 1;
                comboList[0].Name = maxSeq;
                comboList[0].DisplayName = maxSeq;
            }
        }
        vdCommon.debug("ComboData : " + JSON.stringify(comboList));

        vdCommon.programEnd();

        return comboList;
    };

    var fn_level3Order = function(o9Params){
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
        var fbMtrlHrcyL3 = parsedParams.fbMtrlHrcyL3;

        var result = vdCommon.selectList(["[Rule].[Rule No]"],
                                         ["Measure.[Mtrl Hrchy_L3 Order]"],
                                         'where { [Version].[Version Name].[CWV_MP], [Hrcy Type].[Hrcy Type].[' + fbHrcyType + '], ' +
                                            ' Measure.[Mtrl Hrchy_L1 Name] == "' + fbMtrlHrcyL1 + '", ' +
                                            ' Measure.[Mtrl Hrchy_L2 Name] == "' + fbMtrlHrcyL2 + '", ' +
                                            ' Measure.[Mtrl Hrchy_L3 Name] == "' + fbMtrlHrcyL3 + '", ' +
                                            'isnull(Measure.[Mtrl Hrchy_Deleted By])  }',
                                         "",
                                         "");
        var comboList = vdCommon.fn_makeCombo(result, {MeasureName : "Mtrl Hrchy_L3 Order"});
        if ( comboList.length == 0 ) {
            result = vdCommon.selectList(["[Rule].[Rule No]"],
                                         ["Measure.[Mtrl Hrchy_L3 Order]"],
                                         'where { [Version].[Version Name].[CWV_MP], [Hrcy Type].[Hrcy Type].[' + fbHrcyType + '], ' +
                                            ' Measure.[Mtrl Hrchy_L1 Name] == "' + fbMtrlHrcyL1 + '", ' +
                                            ' Measure.[Mtrl Hrchy_L2 Name] == "' + fbMtrlHrcyL2 + '", ' +
                                            'isnull(Measure.[Mtrl Hrchy_Deleted By])  }',
                                         "orderby Measure.[Mtrl Hrchy_L3 Order] desc",
                                         "limit 1");
            comboList = vdCommon.fn_makeCombo(result, {MeasureName : "Mtrl Hrchy_L3 Order"});
            if ( comboList.length == 0 ) {
                comboList[0] = {Name : "1", DisplayName : "1"};
            } else {
                var maxSeq = parseInt(comboList[0].Name) + 1;
                comboList[0].Name = maxSeq;
                comboList[0].DisplayName = maxSeq;
            }
        }
        vdCommon.debug("ComboData : " + JSON.stringify(comboList));

        vdCommon.programEnd();

        return comboList;
    };

    var fn_level4Order = function(o9Params){
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
        var fbMtrlHrcyL3 = parsedParams.fbMtrlHrcyL3;
        var fbMtrlHrcyL4 = parsedParams.fbMtrlHrcyL4;

        var result = vdCommon.selectList(["[Rule].[Rule No]"],
                                         ["Measure.[Mtrl Hrchy_L4 Order]"],
                                         'where { [Version].[Version Name].[CWV_MP], [Hrcy Type].[Hrcy Type].[' + fbHrcyType + '], ' +
                                            ' Measure.[Mtrl Hrchy_L1 Name] == "' + fbMtrlHrcyL1 + '", ' +
                                            ' Measure.[Mtrl Hrchy_L2 Name] == "' + fbMtrlHrcyL2 + '", ' +
                                            ' Measure.[Mtrl Hrchy_L3 Name] == "' + fbMtrlHrcyL3 + '", ' +
                                            ' Measure.[Mtrl Hrchy_L4 Name] == "' + fbMtrlHrcyL4 + '", ' +
                                            'isnull(Measure.[Mtrl Hrchy_Deleted By])  }',
                                         "",
                                         "");
        var comboList = vdCommon.fn_makeCombo(result, {MeasureName : "Mtrl Hrchy_L4 Order"});
        if ( comboList.length == 0 ) {
            result = vdCommon.selectList(["[Rule].[Rule No]"],
                                         ["Measure.[Mtrl Hrchy_L4 Order]"],
                                         'where { [Version].[Version Name].[CWV_MP], [Hrcy Type].[Hrcy Type].[' + fbHrcyType + '], ' +
                                            ' Measure.[Mtrl Hrchy_L1 Name] == "' + fbMtrlHrcyL1 + '", ' +
                                            ' Measure.[Mtrl Hrchy_L2 Name] == "' + fbMtrlHrcyL2 + '", ' +
                                            ' Measure.[Mtrl Hrchy_L3 Name] == "' + fbMtrlHrcyL3 + '", ' +
                                            'isnull(Measure.[Mtrl Hrchy_Deleted By])  }',
                                         "orderby Measure.[Mtrl Hrchy_L4 Order] desc",
                                         "limit 1");
            comboList = vdCommon.fn_makeCombo(result, {MeasureName : "Mtrl Hrchy_L4 Order"});
            if ( comboList.length == 0 ) {
                comboList[0] = {Name : "1", DisplayName : "1"};
            } else {
                var maxSeq = parseInt(comboList[0].Name) + 1;
                comboList[0].Name = maxSeq;
                comboList[0].DisplayName = maxSeq;
            }
        }
        vdCommon.debug("ComboData : " + JSON.stringify(comboList));

        vdCommon.programEnd();

        return comboList;
    };

    var fn_level5Order = function(o9Params){
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
        var fbMtrlHrcyL3 = parsedParams.fbMtrlHrcyL3;
        var fbMtrlHrcyL4 = parsedParams.fbMtrlHrcyL4;
        var fbMtrlHrcyL5 = parsedParams.fbMtrlHrcyL5;

        var result = vdCommon.selectList(["[Rule].[Rule No]"],
                                         ["Measure.[Mtrl Hrchy_L5 Order]"],
                                         'where { [Version].[Version Name].[CWV_MP], [Hrcy Type].[Hrcy Type].[' + fbHrcyType + '], ' +
                                            ' Measure.[Mtrl Hrchy_L1 Name] == "' + fbMtrlHrcyL1 + '", ' +
                                            ' Measure.[Mtrl Hrchy_L2 Name] == "' + fbMtrlHrcyL2 + '", ' +
                                            ' Measure.[Mtrl Hrchy_L3 Name] == "' + fbMtrlHrcyL3 + '", ' +
                                            ' Measure.[Mtrl Hrchy_L4 Name] == "' + fbMtrlHrcyL4 + '", ' +
                                            ' Measure.[Mtrl Hrchy_L5 Name] == "' + fbMtrlHrcyL5 + '", ' +
                                            'isnull(Measure.[Mtrl Hrchy_Deleted By])  }',
                                         "",
                                         "");
        var comboList = vdCommon.fn_makeCombo(result, {MeasureName : "Mtrl Hrchy_L5 Order"});
        if ( comboList.length == 0 ) {
            result = vdCommon.selectList(["[Rule].[Rule No]"],
                                         ["Measure.[Mtrl Hrchy_L5 Order]"],
                                         'where { [Version].[Version Name].[CWV_MP], [Hrcy Type].[Hrcy Type].[' + fbHrcyType + '], ' +
                                            ' Measure.[Mtrl Hrchy_L1 Name] == "' + fbMtrlHrcyL1 + '", ' +
                                            ' Measure.[Mtrl Hrchy_L2 Name] == "' + fbMtrlHrcyL2 + '", ' +
                                            ' Measure.[Mtrl Hrchy_L3 Name] == "' + fbMtrlHrcyL3 + '", ' +
                                            ' Measure.[Mtrl Hrchy_L4 Name] == "' + fbMtrlHrcyL4 + '", ' +
                                            'isnull(Measure.[Mtrl Hrchy_Deleted By])  }',
                                         "orderby Measure.[Mtrl Hrchy_L5 Order] desc",
                                         "limit 1");
            comboList = vdCommon.fn_makeCombo(result, {MeasureName : "Mtrl Hrchy_L5 Order"});
            if ( comboList.length == 0 ) {
                comboList[0] = {Name : "1", DisplayName : "1"};
            } else {
                var maxSeq = parseInt(comboList[0].Name) + 1;
                comboList[0].Name = maxSeq;
                comboList[0].DisplayName = maxSeq;
            }
        }
        vdCommon.debug("ComboData : " + JSON.stringify(comboList));

        vdCommon.programEnd();

        return comboList;
    };

    return {
        fn_add : fn_add,
        fn_level1 : fn_level1,
        fn_level2 : fn_level2,
        fn_level3 : fn_level3,
        fn_level4 : fn_level4,
        fn_level5 : fn_level5,
        fn_delete : fn_delete,
        fn_restore : fn_restore,
        fn_level1Order : fn_level1Order,
        fn_level2Order : fn_level2Order,
        fn_level3Order : fn_level3Order,
        fn_level4Order : fn_level4Order,
        fn_level5Order : fn_level5Order
    };
});

/**************************** o9.NSCM.JS_MtrlHrchy ****************************
    2025-2-24 : Version Name 을 CWV_MP 로 변경
    2025-2-26 : Add 시 전체를 선택하도록 변경
*********************************************************************/