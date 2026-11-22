define('o9.NSCM.JS_MtrlHrcy', ['o9/data/query', 'o9/data/cellset', 'o9.NSCM.commonLib'], function () {
    var fn_add = function(o9Params){
        var commonLib = require('o9.NSCM.commonLib');

        var programName = "o9.NSCM.JS_MtrlHrcy ============> fn_add";
        vdCommon = new commonLib.VdCommon(programName);
        vdCommon.setLogLevel("Debug");

        vdCommon.printParams(o9Params);

        // 파라미터 가져오기
        var parsedParams = JSON.parse(o9Params);
        var fbMtrlHrcyType = parsedParams.fbMtrlHrcyType;
        var fbMtrlHrcyStatus = "Latest";
        var fbMtrlHrcyL1 = parsedParams.fbMtrlHrcyL1;
        var fbMtrlHrcyL2 = parsedParams.fbMtrlHrcyL2;
        var fbMtrlHrcyL3 = parsedParams.fbMtrlHrcyL3;

        vdCommon.printStep("[Mtrl Hrcy No].[Mtrl Hrcy No] Add");
        // Hierarchy Max 값을 구한다.
        var result = vdCommon.selectList(["[Mtrl Hrcy No].[Mtrl Hrcy No].filter(#.Name != \"REQ\")"],
                                            [],
                                            "",
                                            "orderby [Mtrl Hrcy No].[Mtrl Hrcy No].Key desc",
                                            "limit 1");

        var mtrlHrcyNo = (parseInt(result.cs.row(0).cell(result.cs.memberColumnIndex("Mtrl Hrcy No", "Mtrl Hrcy No")).Name) + 1) + "";

        // Member 를 추가한다.
        if ( !vdCommon.existMember("[Mtrl Hrcy No].[Mtrl Hrcy No]", mtrlHrcyNo) ) {
            vdCommon.createMember("[Mtrl Hrcy No].[Mtrl Hrcy No]", mtrlHrcyNo);
        }

        vdCommon.printStep("Dimension (Granularity) Add");

        // Dimension 이 등록되어 있는지를 체크해서 넣어준다.
        var granularity = [];
        granularity.push("[Version].[Version Name]");
        granularity.push("[Mtrl Hrcy Type].[Mtrl Hrcy Type]");
        granularity.push("[Mtrl Hrcy Status].[Mtrl Hrcy Status]");
        granularity.push("[Mtrl Hrcy No].[Mtrl Hrcy No]");
        var granularityValues = [];
        granularityValues.push("CurrentWorkingView");
        granularityValues.push(fbMtrlHrcyType);
        granularityValues.push(fbMtrlHrcyStatus);
        granularityValues.push(mtrlHrcyNo);
        if ( !vdCommon.existDimension(vdCommon.makeDimension(granularity, granularityValues)) ) {
            vdCommon.createDimension(granularity, granularityValues);
        }

        vdCommon.printStep("Measure Add");
        // Level별 정렬값을 구한다.
        result = vdCommon.selectList(["[Version].[Version Name].[CurrentWorkingView]",
                                            "[Mtrl Hrcy Type].[Mtrl Hrcy Type].[" + fbMtrlHrcyType + "]",
                                            "[Mtrl Hrcy Status].[Mtrl Hrcy Status]",
                                            "[Mtrl Hrcy No].[Mtrl Hrcy No]"],
                                        ["Measure.[Mtrl Hrcy_L1 Order]"],
                                        'where {Measure.[Mtrl Hrcy_L1 Name] == "' + fbMtrlHrcyL1 + '"} ',
                                        "",
                                        "limit 1");
        var l1Order = result.cs.row(0).cell(result.cs.measureColumnIndex("Mtrl Hrcy_L1 Order"));
        result = vdCommon.selectList(["[Version].[Version Name].[CurrentWorkingView]",
                                            "[Mtrl Hrcy Type].[Mtrl Hrcy Type].[" + fbMtrlHrcyType + "]",
                                            "[Mtrl Hrcy Status].[Mtrl Hrcy Status]",
                                            "[Mtrl Hrcy No].[Mtrl Hrcy No]"],
                                        ["Measure.[Mtrl Hrcy_L2 Order]"],
                                        'where {Measure.[Mtrl Hrcy_L1 Name] == "' + fbMtrlHrcyL1 + '", Measure.[Mtrl Hrcy_L2 Name] == "' + fbMtrlHrcyL2 + '"}',
                                        "",
                                        "limit 1");
        var l2Order = result.cs.row(0).cell(result.cs.measureColumnIndex("Mtrl Hrcy_L2 Order"));
        var l3Order = "99";

        // Measure 가 등록되어 있는지를 체크해서 넣어준다.
        if ( !vdCommon.existMeasure(["[Version].[Version Name].[CurrentWorkingView]",
                                            "[Mtrl Hrcy Type].[Mtrl Hrcy Type].[" + fbMtrlHrcyType + "]",
                                            "[Mtrl Hrcy Status].[Mtrl Hrcy Status]",
                                            "[Mtrl Hrcy No].[Mtrl Hrcy No]"],
                                    ["Measure.[Mtrl Hrcy_L1 Name]"],
                                    'where {Measure.[Mtrl Hrcy_L1 Name] == "' + fbMtrlHrcyL1 + '", Measure.[Mtrl Hrcy_L2 Name] == "' + fbMtrlHrcyL2 + '", Measure.[Mtrl Hrcy_L3 Name] == "' + fbMtrlHrcyL3 + '"}') ) {
            vdCommon.createMeasure(vdCommon.makeDimension(granularity, granularityValues),
                        ['Measure.[Mtrl Hrcy_L1 Name] = "' + fbMtrlHrcyL1 + '";',
                        'Measure.[Mtrl Hrcy_L1 Order] = ' + l1Order + ';',
                        'Measure.[Mtrl Hrcy_L2 Name] = "' + fbMtrlHrcyL2 + '";',
                        'Measure.[Mtrl Hrcy_L2 Order] = ' + l2Order + ';',
                        'Measure.[Mtrl Hrcy_L3 Name] = "' + fbMtrlHrcyL3 + '";',
                        'Measure.[Mtrl Hrcy_L3 Order] = ' + l3Order + ';',
                        'Measure.[Mtrl Hrcy_Update Time] = now();',
                        'Measure.[Mtrl Hrcy_Updated By] = CurrentUser().Name;',
                        'Measure.[zzMtrl Hrcy_SCM Material] = "N";']);
        } else {
            RuleOutputToUI = { Status : 'Error', Message : "This Data has already been registered." };
            return;
        }

        vdCommon.programEnd();
    };

    var fn_level1 = function(o9Params){
        var commonLib = require('o9.NSCM.commonLib');

        var programName = "o9.NSCM.JS_MtrlHrcy ============> fn_level1";
        vdCommon = new commonLib.VdCommon(programName);
        vdCommon.setLogLevel("Debug");

        vdCommon.printParams(o9Params);

        // 파라미터 가져오기
        var parsedParams = JSON.parse(o9Params);
        var fbMtrlHrcyType = parsedParams.fbMtrlHrcyType;

        vdCommon.printStep("[Mtrl Hrcy No].[Mtrl Hrcy No] Add");
        var result = vdCommon.selectList(["[Version].[Version Name].[CurrentWorkingView]",
                                            "[Mtrl Hrcy Type].[Mtrl Hrcy Type].[" + fbMtrlHrcyType + "]",
                                            "[Mtrl Hrcy Status].[Mtrl Hrcy Status]",
                                            "[Mtrl Hrcy No].[Mtrl Hrcy No]"],
                                         ["Measure.[Mtrl Hrcy_L1 Name]", "Measure.[Mtrl Hrcy_L1 Order]"],
                                         "",
                                         "orderby Measure.[Mtrl Hrcy_L1 Order]",
                                         "");
        //vdCommon.printCsData(result, 3);

        var comboList = [];
        var validHashMap = {};
        for ( var i = 0; i < result.cs.rowCount; i++ ) {
            comboData = result.cs.row(i).cell(result.cs.measureColumnIndex("Mtrl Hrcy_L1 Name"));

            if ( validHashMap[comboData] == undefined ) {
                comboList.push({ Name : comboData, DisplayName : comboData});
                validHashMap[comboData] = comboData;
            }
        }
        vdCommon.debug("ComboData : " + JSON.stringify(validHashMap));

        vdCommon.programEnd();

        return comboList;
    };

    var fn_level2 = function(o9Params){
        var commonLib = require('o9.NSCM.commonLib');

        var programName = "o9.NSCM.JS_MtrlHrcy ============> fn_level2";
        vdCommon = new commonLib.VdCommon(programName);
        vdCommon.setLogLevel("Debug");

        vdCommon.printParams(o9Params);

        // 파라미터 가져오기
        var parsedParams = JSON.parse(o9Params);
        var fbMtrlHrcyType = parsedParams.fbMtrlHrcyType;
        var fbMtrlHrcyL1 = parsedParams.fbMtrlHrcyL1;

        vdCommon.printStep("[Mtrl Hrcy No].[Mtrl Hrcy No] Add");
        var result = vdCommon.selectList(["[Version].[Version Name].[CurrentWorkingView]",
                                            "[Mtrl Hrcy Type].[Mtrl Hrcy Type].[" + fbMtrlHrcyType + "]",
                                            "[Mtrl Hrcy Status].[Mtrl Hrcy Status]",
                                            "[Mtrl Hrcy No].[Mtrl Hrcy No]"],
                                         ["Measure.[Mtrl Hrcy_L2 Name]", "Measure.[Mtrl Hrcy_L2 Order]"],
                                         'where {Measure.[Mtrl Hrcy_L1 Name] == "' + fbMtrlHrcyL1 + '"}',
                                         "orderby Measure.[Mtrl Hrcy_L2 Order]",
                                         "");
        //vdCommon.printCsData(result, 3);

        var comboList = [];
        var validHashMap = {};
        for ( var i = 0; i < result.cs.rowCount; i++ ) {
            comboData = result.cs.row(i).cell(result.cs.measureColumnIndex("Mtrl Hrcy_L2 Name"));

            if ( validHashMap[comboData] == undefined ) {
                comboList.push({ Name : comboData, DisplayName : comboData});
                validHashMap[comboData] = comboData;
            }
        }
        vdCommon.debug("ComboData : " + JSON.stringify(validHashMap));

        vdCommon.programEnd();

        return comboList;
    };

    var fn_level3 = function(o9Params){
        var commonLib = require('o9.NSCM.commonLib');

        var programName = "o9.NSCM.JS_MtrlHrcy ============> fn_level3";
        vdCommon = new commonLib.VdCommon(programName);
        vdCommon.setLogLevel("Debug");

        vdCommon.printParams(o9Params);

        // 파라미터 가져오기
        var parsedParams = JSON.parse(o9Params);
        var fbMtrlHrcyType = parsedParams.fbMtrlHrcyType;
        var fbMtrlHrcyL1 = parsedParams.fbMtrlHrcyL1;
        var fbMtrlHrcyL2 = parsedParams.fbMtrlHrcyL2;

        vdCommon.printStep("[Mtrl Hrcy No].[Mtrl Hrcy No] Add");
        var result = vdCommon.selectList(["[Version].[Version Name].[CurrentWorkingView]",
                                            "[Mtrl Hrcy Type].[Mtrl Hrcy Type].[" + fbMtrlHrcyType + "]",
                                            "[Mtrl Hrcy Status].[Mtrl Hrcy Status]",
                                            "[Mtrl Hrcy No].[Mtrl Hrcy No]"],
                                         ["Measure.[Mtrl Hrcy_L3 Name]", "Measure.[Mtrl Hrcy_L3 Order]"],
                                         'where {Measure.[Mtrl Hrcy_L1 Name] == "' + fbMtrlHrcyL1 + '", Measure.[Mtrl Hrcy_L2 Name] == "' + fbMtrlHrcyL2 + '"}',
                                         "orderby Measure.[Mtrl Hrcy_L3 Order]",
                                         "");
        //vdCommon.printCsData(result, 3);

        var comboList = [];
        var validHashMap = {};
        for ( var i = 0; i < result.cs.rowCount; i++ ) {
            comboData = result.cs.row(i).cell(result.cs.measureColumnIndex("Mtrl Hrcy_L3 Name"));

            if ( validHashMap[comboData] == undefined ) {
                comboList.push({ Name : comboData, DisplayName : comboData});
                validHashMap[comboData] = comboData;
            }
        }
        vdCommon.debug("ComboData : " + JSON.stringify(validHashMap));

        vdCommon.programEnd();

        return comboList;
    };

    var fn_delete = function(o9Params){
        var commonLib = require('o9.NSCM.commonLib');

        var programName = "o9.NSCM.JS_MtrlHrcy ============> fn_add";
        vdCommon = new commonLib.VdCommon(programName);
        vdCommon.setLogLevel("Debug");

        vdCommon.printParams(o9Params);

        // 파라미터 가져오기
        var parsedParams = JSON.parse(o9Params);
        var fbMtrlHrcyType = parsedParams.fbMtrlHrcyType;
        var fbMtrlHrcyStatus = parsedParams.fbMtrlHrcyStatus;
        var fbMtrlHrcyNo = parsedParams.fbMtrlHrcyNo;

        var granularity = [];
        granularity.push("[Version].[Version Name]");
        granularity.push("[Mtrl Hrcy Type].[Mtrl Hrcy Type]");
        granularity.push("[Mtrl Hrcy Status].[Mtrl Hrcy Status]");
        granularity.push("[Mtrl Hrcy No].[Mtrl Hrcy No]");
        var granularityValues = [];
        granularityValues.push("CurrentWorkingView");
        granularityValues.push(fbMtrlHrcyType);
        granularityValues.push(fbMtrlHrcyStatus);
        granularityValues.push(fbMtrlHrcyNo);

        vdCommon.createMeasure(vdCommon.makeDimension(granularity, granularityValues),
                                ['Measure.[Mtrl Hrcy_Delete Flag] = "Y";',
                                'Measure.[Mtrl Hrcy_L1 Name.Lock] = true;',
                                'Measure.[Mtrl Hrcy_L1 Order.Lock] = true;',
                                'Measure.[Mtrl Hrcy_L1 Type.Lock] = true;',
                                'Measure.[zzMtrl Hrcy_L1 Rule.Lock] = true;',
                                'Measure.[Mtrl Hrcy_L2 Name.Lock] = true;',
                                'Measure.[Mtrl Hrcy_L2 Order.Lock] = true;',
                                'Measure.[Mtrl Hrcy_L2 Type.Lock] = true;',
                                'Measure.[zzMtrl Hrcy_L2 Rule.Lock] = true;',
                                'Measure.[Mtrl Hrcy_L3 Name.Lock] = true;',
                                'Measure.[Mtrl Hrcy_L3 Order.Lock] = true;',
                                'Measure.[Mtrl Hrcy_L3 Type.Lock] = true;',
                                'Measure.[zzMtrl Hrcy_L3 Rule.Lock] = true;',
                                'Measure.[Mtrl Hrcy_L4 Name.Lock] = true;',
                                'Measure.[Mtrl Hrcy_L4 Order.Lock] = true;',
                                'Measure.[Mtrl Hrcy_L4 Type.Lock] = true;',
                                'Measure.[zzMtrl Hrcy_L4 Rule.Lock] = true;',
                                'Measure.[Mtrl Hrcy_L5 Name.Lock] = true;',
                                'Measure.[Mtrl Hrcy_L5 Order.Lock] = true;',
                                'Measure.[Mtrl Hrcy_L5 Type.Lock] = true;',
                                'Measure.[zzMtrl Hrcy_L5 Rule.Lock] = true;',
                                'Measure.[zzMtrl Hrcy_SCM Material.Lock] = true;']);

        vdCommon.programEnd();
    };

    return {
        fn_add : fn_add,
        fn_level1 : fn_level1,
        fn_level2 : fn_level2,
        fn_level3 : fn_level3,
        fn_delete : fn_delete
    };
});