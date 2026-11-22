define('o9.NSCM.JSItemMaterialAttrMap', ['o9/data/query', 'o9/data/cellset', 'o9.NSCM.commonLib'], function () {
    const programName = "o9.NSCM.JSItemMaterialAttrMap";

    var fn_levelDataCombo = function(o9Params){
        try {
            const commonLib = require('o9.NSCM.commonLib');
            const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
            vdCommon.setLogLevel("Debug");

            vdCommon.printParams(o9Params);

            // 파라미터 가져오기
            var parsedParams = JSON.parse(o9Params);
            var fbVersionName = parsedParams.fbVersionName;

            var comboList = [];

            // 기존에 등록된 Hrcy Level Data 데이타를 가져온다
            var existMap = {};
            var result = vdCommon.selectList(["[Version].[Version Name].[" + fbVersionName + "]",
                                                "[Hrcy Level Data].[Hrcy Level]",
                                                "[Hrcy Level Data].[Hrcy Level Data]",
                                                "[Attr No].[Attr No].[S_ATTB01]",
                                                "[Sequence].[Sequence].[1]"],
                                             ["Measure.[Item Material Attr Map_RuleNo]"],
                                             "",
                                             "",
                                             "");
            vdCommon.printCsData(result, 3);
            for ( var i = 0; i < result.cs.rowCount; i++ ) {
                levelData = result.cs.row(i).cell(result.cs.memberColumnIndex("Hrcy Level Data", "Hrcy Level")).Name + "," +
                                result.cs.row(i).cell(result.cs.memberColumnIndex("Hrcy Level Data", "Hrcy Level Data")).Name;

                if ( existMap[levelData] == undefined ) {
                    existMap[levelData] = levelData;
                }
            }

            // LV1 데이타를 가져온다.
            result = vdCommon.selectList(["[Version].[Version Name].[" + fbVersionName + "]",
                                                "[Rule].[Rule No]",
                                                "[Hrcy Type].[Hrcy Type]"],
                                             ["Measure.[Mtrl Hrchy_L1 Name]"],
                                             'where { Measure.[Mtrl Hrchy_Attb Make Level] == "LV1" }',
                                             "",
                                             "");
            vdCommon.printCsData(result, 3);
            for ( var i = 0; i < result.cs.rowCount; i++ ) {
                l1Name = result.cs.row(i).cell(result.cs.measureColumnIndex("Mtrl Hrchy_L1 Name"));

                if ( existMap["LV1" + "," + l1Name] == undefined ) {
                    comboList.push({ Name : "LV1" + "," + l1Name, DisplayName : l1Name + " (LV1)"});
                }
            }

            // LV2 데이타를 가져온다.
            result = vdCommon.selectList(["[Version].[Version Name].[" + fbVersionName + "]",
                                                "[Rule].[Rule No]",
                                                "[Hrcy Type].[Hrcy Type]"],
                                             ["Measure.[Mtrl Hrchy_L2 Name]"],
                                             'where { Measure.[Mtrl Hrchy_Attb Make Level] == "LV2" }',
                                             "",
                                             "");
            vdCommon.printCsData(result, 3);
            for ( var i = 0; i < result.cs.rowCount; i++ ) {
                l1Name = result.cs.row(i).cell(result.cs.measureColumnIndex("Mtrl Hrchy_L2 Name"));

                if ( existMap["LV2" + "," + l1Name] == undefined ) {
                    comboList.push({ Name : "LV2" + "," + l1Name, DisplayName : l1Name + " (LV2)"});
                }
            }

            // LV3 데이타를 가져온다.
            result = vdCommon.selectList(["[Version].[Version Name].[" + fbVersionName + "]",
                                                "[Rule].[Rule No]",
                                                "[Hrcy Type].[Hrcy Type]"],
                                             ["Measure.[Mtrl Hrchy_L3 Name]"],
                                             'where { Measure.[Mtrl Hrchy_Attb Make Level] == "LV3" }',
                                             "",
                                             "");
            vdCommon.printCsData(result, 3);
            for ( var i = 0; i < result.cs.rowCount; i++ ) {
                l1Name = result.cs.row(i).cell(result.cs.measureColumnIndex("Mtrl Hrchy_L3 Name"));

                if ( existMap["LV3" + "," + l1Name] == undefined ) {
                    comboList.push({ Name : "LV3" + "," + l1Name, DisplayName : l1Name + " (LV3)"});
                }
            }

            vdCommon.debug("ComboData : " + JSON.stringify(comboList));

            vdCommon.programEnd();

            return comboList;
        } catch ( e ) {
            RuleOutputToUI = { Status : 'Error', Message : "Js Logic Error : " + e.message };
            return;
        }
    };

    var fn_levelDataAdd = function(o9Params){
        try {
            const commonLib = require('o9.NSCM.commonLib');
            const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
            vdCommon.setLogLevel("Debug");

            vdCommon.printParams(o9Params);

            // 파라미터 가져오기
            var parsedParams = JSON.parse(o9Params);
            var fbVersionName = parsedParams.fbVersionName;
            var fbLevelData = parsedParams.fbLevelData.split(",");

            // 공통 속성 추가
            if ( !vdCommon.existDimension(['[Hrcy Level Data].[Hrcy Level].[Common]',
                                                '[Hrcy Level Data].[Hrcy Level Data].[Common]']) ) {
                vdCommon.createDimension(['[Hrcy Level Data].[Hrcy Level]','[Hrcy Level Data].[Hrcy Level Data]'],
                                                ["Common", "Common"]);
            }
            if ( !vdCommon.existMeasure(
                        ["[Version].[Version Name].[" + fbVersionName + "]",
                            "[Hrcy Level Data].[Hrcy Level Data].[Common]",
                            "[Attr No].[Attr No].[C_ATTB01]",
                            "[Sequence].[Sequence].[1]"],
                        ['Measure.[Item Material Attr Map_RuleNo]']) ) {
                var queryStr = "";

                var attbNos = "01,02,03,04,05,06,07,08,09,10".split(",");
                for ( const attbNo of attbNos ) {
                    var dimension = [];
                    dimension.push("[Version].[Version Name].[" + fbVersionName + "]");
                    dimension.push("[Hrcy Level Data].[Hrcy Level Data].[Common]");
                    dimension.push("[Attr No].[Attr No].[C_ATTB" + attbNo + "]");
                    dimension.push("[Sequence].[Sequence].[1]");

                    var measure = [];
                    measure.push('Measure.[Item Material Attr Map_RuleNo] = "Common_C_ATTB' + attbNo + '_1";');
                    measure.push('Measure.[Item Material Attr Map_Rule Seq] = 1;');

                    queryStr += vdCommon.createMeasureQuery(dimension, measure);
                }

                vdCommon.executeQuery("Batch Query" , queryStr);
            }

            // Level Data 를 Dimension 에 등록
            if ( !vdCommon.existDimension(['[Hrcy Level Data].[Hrcy Level].[' + fbLevelData[0] + ']',
                                                '[Hrcy Level Data].[Hrcy Level Data].[' + fbLevelData[1] + ']']) ) {
                vdCommon.createDimension(['[Hrcy Level Data].[Hrcy Level]','[Hrcy Level Data].[Hrcy Level Data]'],
                                                [fbLevelData[0], fbLevelData[1]]);
            }

            // Level Data 속성을 등록
            if ( !vdCommon.existMeasure(
                        ["[Version].[Version Name].[" + fbVersionName + "]",
                            "[Hrcy Level Data].[Hrcy Level Data].[" + fbLevelData[1] + "]",
                            "[Attr No].[Attr No].[S_ATTB01]",
                            "[Sequence].[Sequence].[1]"],
                        ['Measure.[Item Material Attr Map_RuleNo]']) ) {
                var queryStr = "";

                var attbNos = "01,02,03,04,05,06,07,08,09,10,11,12,13,14,15".split(",");
                for ( const attbNo of attbNos ) {
                    var dimension = [];
                    dimension.push("[Version].[Version Name].[" + fbVersionName + "]");
                    dimension.push("[Hrcy Level Data].[Hrcy Level Data].[" + fbLevelData[1] + "]");
                    dimension.push("[Attr No].[Attr No].[S_ATTB" + attbNo + "]");
                    dimension.push("[Sequence].[Sequence].[1]");

                    var measure = [];
                    measure.push('Measure.[Item Material Attr Map_RuleNo] = "' + fbLevelData[1] + "_S_ATTB" + attbNo + '_1";');
                    measure.push('Measure.[Item Material Attr Map_Rule Seq] = 1;');

                    queryStr += vdCommon.createMeasureQuery(dimension, measure);
                }

                vdCommon.executeQuery("Batch Query" , queryStr);
            } else {
                RuleOutputToUI = { Status : 'Error', Message : "This Data has already been registered." };
                return;
            }

            vdCommon.programEnd();
        } catch ( e ) {
            RuleOutputToUI = { Status : 'Error', Message : "Js Logic Error : " + e.message };
            return;
        }
    };

    var fn_add = function(o9Params){
        try {
            const commonLib = require('o9.NSCM.commonLib');
            const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
            vdCommon.setLogLevel("Debug");

            vdCommon.printParams(o9Params);

            // 파라미터 가져오기
            var parsedParams = JSON.parse(o9Params);
            var fbVersionName = parsedParams.fbVersionName;
            var fbSelect = parsedParams.fbSelect;
            var fbCount = parsedParams.fbCount;

            for ( var i = 0; i < fbSelect.length; i++ ) {
                var row = fbSelect[i];

                var result = vdCommon.selectList(
                                    ["[Version].[Version Name].[" + fbVersionName + "]",
                                        "[Hrcy Level Data].[Hrcy Level Data].[" + row.LevelData.Value + "]",
                                        "[Attr No].[Attr No].[" + row.AttrNo.Value + "]",
                                        "[Sequence].[Sequence]"],
                                    ["Measure.[Item Material Attr Map_RuleNo]"],
                                    "",
                                    "orderby [Sequence].[Sequence].Key desc",
                                    "");

                var sequence = parseInt(result.cs.row(0).cell(result.cs.memberColumnIndex("Sequence", "Sequence")).Name);

                for ( var m = 1; m <= fbCount; m++ ) {
                    sequence++;

                    var dimension = [];
                    dimension.push("[Version].[Version Name].[" + fbVersionName + "]");
                    dimension.push("[Hrcy Level Data].[Hrcy Level Data].[" + row.LevelData.Value + "]");
                    dimension.push("[Attr No].[Attr No].[" + row.AttrNo.Value + "]");
                    dimension.push("[Sequence].[Sequence].[" + sequence + "]");

                    var measure = [];
                    measure.push('Measure.[Item Material Attr Map_RuleNo] = "' + row.LevelData.Value + '_' + row.AttrNo.Value + '_' + sequence + '";');
                    measure.push('Measure.[Item Material Attr Map_Rule Seq] = ' + sequence + ';');

                    vdCommon.createMeasure(dimension, measure);
                }
            }

            vdCommon.programEnd();
        } catch ( e ) {
            RuleOutputToUI = { Status : 'Error', Message : "Js Logic Error : " + e.message };
            return;
        }
    };

    var fn_delete = function(o9Params){
        try {
            const commonLib = require('o9.NSCM.commonLib');
            const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
            vdCommon.setLogLevel("Debug");

            vdCommon.printParams(o9Params);

            // 파라미터 가져오기
            var parsedParams = JSON.parse(o9Params);
            var fbVersionName = parsedParams.fbVersionName;
            var fbSelect = parsedParams.fbSelect;

            // Sequence 가 1인건 삭제를 못함
            for ( var i = 0; i < fbSelect.length; i++ ) {
                var row = fbSelect[i];

                if ( row.Sequence.Value == "1" ) {
                    RuleOutputToUI = { Status : 'Error', Message : "Data with a Sequence of 1 cannot be deleted." };
                    return;
                }
            }

            for ( var i = 0; i < fbSelect.length; i++ ) {
                var row = fbSelect[i];

                var where = [];
                where.push("[Version].[Version Name].[" + fbVersionName + "]");
                where.push("[Hrcy Level Data].[Hrcy Level Data].[" + row.LevelData.Value + "]");
                where.push("[Attr No].[Attr No].[" + row.AttrNo.Value + "]");
                where.push("[Sequence].[Sequence].[" + row.Sequence.Value + "]");

                vdCommon.deleteMeasure(where, "Item Material Attr Map");
            }

            vdCommon.programEnd();
        } catch ( e ) {
            RuleOutputToUI = { Status : 'Error', Message : "Js Logic Error : " + e.message };
            return;
        }
    };

    var fn_apply = function(o9Params){
        try {
            const commonLib = require('o9.NSCM.commonLib');
            const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
            vdCommon.setLogLevel("Debug");

            vdCommon.printParams(o9Params);

            // 파라미터 가져오기
            var parsedParams = JSON.parse(o9Params);
            var fbVersionName = parsedParams.fbVersionName;
            var fbLevelData = parsedParams.fbLevelData;

            vdCommon.deleteMeasure(["[Version].[Version Name].[" + fbVersionName + "]",
                                            'Measure.[Item Material_Level Data] == "' + fbLevelData + '"'],
                                        "Item Material");

            // 파이썬 실행
            var execQuery = 'EXEC plugin instance [PY_UI_ItemMaterialAttrMap] ' +
                            'for measures {[Item Material_Level Data]} ' +
                            'using scope ( Version.[Version Name].[' + fbVersionName + '] * [Hrcy Level Data].[Hrcy Level Data].filter(#.Name in {"Common","' + fbLevelData + '"}) ) ' +
                            'using arguments {(pDetailLogFlag, "N"), (RunID, "Run_1"), ("IncludeNullRows", "False"), (ExecutionMode, "MediumWeight"), (MaxSliceTableCells, 200000000), (MaxConcurrency, 1 )};'
            vdCommon.executeQuery("Py Run", execQuery);

            vdCommon.programEnd();
        } catch ( e ) {
            RuleOutputToUI = { Status : 'Error', Message : "Js Logic Error : " + e.message };
            return;
        }
    };

    var fn_applyLevelDataCombo = function(o9Params){
        try {
            const commonLib = require('o9.NSCM.commonLib');
            const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
            vdCommon.setLogLevel("Debug");

            vdCommon.printParams(o9Params);

            // 파라미터 가져오기
            var parsedParams = JSON.parse(o9Params);
            var fbVersionName = parsedParams.fbVersionName;

            var comboList = [];

            var result = vdCommon.selectList(["[Version].[Version Name].[" + fbVersionName + "]",
                                                "[Hrcy Level Data].[Hrcy Level]",
                                                "[Hrcy Level Data].[Hrcy Level Data]",
                                                "[Attr No].[Attr No].[S_ATTB01]",
                                                "[Sequence].[Sequence].[1]"],
                                             ["Measure.[Item Material Attr Map_RuleNo]"],
                                             "",
                                             "",
                                             "");
            vdCommon.printCsData(result, 3);
            for ( var i = 0; i < result.cs.rowCount; i++ ) {
                level = result.cs.row(i).cell(result.cs.memberColumnIndex("Hrcy Level Data", "Hrcy Level")).Name;
                levelData = result.cs.row(i).cell(result.cs.memberColumnIndex("Hrcy Level Data", "Hrcy Level Data")).Name;

                comboList.push({ Name : levelData, DisplayName : levelData + " (" + level + ")"});
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
        fn_levelDataCombo : fn_levelDataCombo,
        fn_levelDataAdd : fn_levelDataAdd,
        fn_add : fn_add,
        fn_delete : fn_delete,
        fn_apply : fn_apply,
        fn_applyLevelDataCombo : fn_applyLevelDataCombo
    };
});

/**************************** o9.NSCM.JSItemMaterialAttrMap ****************************
    2024-11-26 : ...
*********************************************************************/