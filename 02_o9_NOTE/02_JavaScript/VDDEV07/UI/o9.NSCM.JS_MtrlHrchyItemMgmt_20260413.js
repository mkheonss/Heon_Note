define('o9.NSCM.JS_MtrlHrchyItemMgmt', ['o9/data/query', 'o9/data/cellset', 'o9.NSCM.commonLib'], function () {
    const programName = "o9.NSCM.JS_MtrlHrchyItemMgmt";

    var fn_publish = function(o9Params){
        try {
            const commonLib = require('o9.NSCM.commonLib');
            const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
            const vdUtil = new commonLib.VdUtil();

            vdCommon.setLogLevel("Debug");

            vdCommon.printParams(o9Params);

            // 파라미터 가져오기
            var parsedParams = JSON.parse(o9Params);
            var fbVersion = parsedParams.fbVersion;
            var fbItemMaterial = parsedParams.fbItemMaterial;

            vdCommon.printStep("createMember");
            vdCommon.createDimension(["[Item Material].[Item Material]",
                                    "[Item Material].[MSL1]",
                                    "[Item Material].[MSL2]",
                                    "[Item Material].[MSL3]",
                                    "[Item Material].[MSL4]",
                                    "[Item Material].[MSL5]",
                                    "[Item Material].[MSL1$DisplayAlias]",
                                    "[Item Material].[MSL2$DisplayAlias]",
                                    "[Item Material].[MSL3$DisplayAlias]",
                                    "[Item Material].[MSL4$DisplayAlias]",
                                    "[Item Material].[MSL5$DisplayAlias]",
                                    "[Item Material].[MSL1 Sorting Order]",
                                    "[Item Material].[MSL2 Sorting Order]",
                                    "[Item Material].[MSL3 Sorting Order]",
                                    "[Item Material].[MSL4 Sorting Order]",
                                    "[Item Material].[MSL5 Sorting Order]"],
                                    ['[Item Material].#.Name',
                                    'Measure.[Item Material_MSL1_Apply]',
                                    'Measure.[Item Material_MSL2_Apply]',
                                    'Measure.[Item Material_MSL3_Apply]',
                                    'Measure.[Item Material_MSL4_Apply]',
                                    'Measure.[Item Material_MSL5_Apply]',
                                    'P Measure.[Item Material_MSL1_Display]',
                                    'P Measure.[Item Material_MSL2_Display]',
                                    'P Measure.[Item Material_MSL3_Display]',
                                    'P Measure.[Item Material_MSL4_Display]',
                                    'P Measure.[Item Material_MSL5_Display]',
                                    'P Measure.[Item Material_MSL1_Order]',
                                    'P Measure.[Item Material_MSL2_Order]',
                                    'P Measure.[Item Material_MSL3_Order]',
                                    'P Measure.[Item Material_MSL4_Order]',
                                    'P Measure.[Item Material_MSL5_Order]'],
                                    'using scope ([Version].[Version Name].[' + fbVersion + '] * [Item Material].[Item Material].[' + fbItemMaterial + '])',
                                    'where { ~isnull(Measure.[Item Material_MSL Group ID]) }');

            vdCommon.programEnd();
        } catch ( e ) {
            RuleOutputToUI = { Status : 'Error', Message : "Js Logic Error : " + e.message };
            return;
        }
    };

    var fn_allPublish = function(o9Params){
        try {
            const commonLib = require('o9.NSCM.commonLib');
            const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
            const vdUtil = new commonLib.VdUtil();

            vdCommon.setLogLevel("Debug");

            vdCommon.printParams(o9Params);

            // 파라미터 가져오기
            var parsedParams = JSON.parse(o9Params);
            var fbVersion = parsedParams.fbVersion;

            vdCommon.printStep("createMember");
            vdCommon.createDimension(["[Item Material].[Item Material]",
                                    "[Item Material].[MSL1]",
                                    "[Item Material].[MSL2]",
                                    "[Item Material].[MSL3]",
                                    "[Item Material].[MSL4]",
                                    "[Item Material].[MSL5]",
                                    "[Item Material].[MSL1$DisplayAlias]",
                                    "[Item Material].[MSL2$DisplayAlias]",
                                    "[Item Material].[MSL3$DisplayAlias]",
                                    "[Item Material].[MSL4$DisplayAlias]",
                                    "[Item Material].[MSL5$DisplayAlias]",
                                    "[Item Material].[MSL1 Sorting Order]",
                                    "[Item Material].[MSL2 Sorting Order]",
                                    "[Item Material].[MSL3 Sorting Order]",
                                    "[Item Material].[MSL4 Sorting Order]",
                                    "[Item Material].[MSL5 Sorting Order]"],
                                    ['[Item Material].#.Name',
                                    'Measure.[Item Material_MSL1_Apply]',
                                    'Measure.[Item Material_MSL2_Apply]',
                                    'Measure.[Item Material_MSL3_Apply]',
                                    'Measure.[Item Material_MSL4_Apply]',
                                    'Measure.[Item Material_MSL5_Apply]',
                                    'P Measure.[Item Material_MSL1_Display]',
                                    'P Measure.[Item Material_MSL2_Display]',
                                    'P Measure.[Item Material_MSL3_Display]',
                                    'P Measure.[Item Material_MSL4_Display]',
                                    'P Measure.[Item Material_MSL5_Display]',
                                    'P Measure.[Item Material_MSL1_Order]',
                                    'P Measure.[Item Material_MSL2_Order]',
                                    'P Measure.[Item Material_MSL3_Order]',
                                    'P Measure.[Item Material_MSL4_Order]',
                                    'P Measure.[Item Material_MSL5_Order]'],
                                    'using scope ([Version].[Version Name].[' + fbVersion + '] * [Item Material].[Item Material])',
                                    'where { ~isnull(Measure.[Item Material_MSL Group ID]) }');

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
            const vdUtil = new commonLib.VdUtil();

            vdCommon.setLogLevel("Debug");

            vdCommon.printParams(o9Params);

            // 파라미터 가져오기
            var parsedParams = JSON.parse(o9Params);
            var fbVersionName = parsedParams.fbVersionName;
            var fbHrcyType = parsedParams.fbHrcyType;

            vdCommon.updateMeasure(["[Version].[Version Name].[" + fbVersionName + "]"],
                                    ['Measure.[Item Material_MSL1] = "-";',
                                        'Measure.[Item Material_MSL2] = "-";',
                                        'Measure.[Item Material_MSL3] = "-";',
                                        'Measure.[Item Material_MSL4] = "-";',
                                        'Measure.[Item Material_MSL5] = "-";',
                                        'Measure.[Item Material_MSL1_Apply] = "-";',
                                        'Measure.[Item Material_MSL2_Apply] = "-";',
                                        'Measure.[Item Material_MSL3_Apply] = "-";',
                                        'Measure.[Item Material_MSL4_Apply] = "-";',
                                        'Measure.[Item Material_MSL5_Apply] = "-";',
                                        'Measure.[Item Material_MSL1_Display] = "-";',
                                        'Measure.[Item Material_MSL2_Display] = "-";',
                                        'Measure.[Item Material_MSL3_Display] = "-";',
                                        'Measure.[Item Material_MSL4_Display] = "-";',
                                        'Measure.[Item Material_MSL5_Display] = "-";',
                                        'Measure.[Item Material_MSL1_Order] = "0";',
                                        'Measure.[Item Material_MSL2_Order] = "0";',
                                        'Measure.[Item Material_MSL3_Order] = "0";',
                                        'Measure.[Item Material_MSL4_Order] = "0";',
                                        'Measure.[Item Material_MSL5_Order] = "0";']);

            // 파이썬 실행
            var execQuery = 'EXEC plugin instance [PY_UI_MtrlHrchyMapRule] ' +
                            'for measures {[Item Material_MSL1]} ' +
                            'using scope ( Version.[Version Name].[' + fbVersionName + '] * [Hrcy Type].[Hrcy Type].[' + fbHrcyType + '] ) ' +
                            'using arguments {(pDetailLogFlag, "N"), (RunID, "Run_1"), ("IncludeNullRows", "False"), (ExecutionMode, "MediumWeight"), (MaxSliceTableCells, 200000000), (MaxConcurrency, 1 )};'
            vdCommon.executeQuery("Py Run", execQuery);

            vdCommon.programEnd();
        } catch ( e ) {
            RuleOutputToUI = { Status : 'Error', Message : "Js Logic Error : " + e.message };
            return;
        }
    };

    return {
        fn_apply : fn_apply,
        fn_publish : fn_publish,
        fn_allPublish : fn_allPublish
    };
});

/**************************** o9.NSCM.JS_MtrlHrchyItemMgmt ****************************
    2024-11-13 : ...
    2024-12-20 : fn_allPublish 추가
*********************************************************************/