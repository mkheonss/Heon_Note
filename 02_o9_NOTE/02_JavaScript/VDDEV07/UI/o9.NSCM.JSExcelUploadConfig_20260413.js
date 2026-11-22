define('o9.NSCM.JSExcelUploadConfig', ['o9/data/query', 'o9/data/cellset', 'o9.NSCM.commonLib'], function () {
    const programName = "o9.NSCM.JSExcelUploadConfig";

    var fn_layoutClassCombo = function(o9Params){
        try {
            const commonLib = require('o9.NSCM.commonLib');
            const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
            vdCommon.setLogLevel("Debug");

            var result = vdCommon.selectList(["[Layout].[Layout Class]"],
                                             [],
                                             "",
                                             "",
                                             "");
            vdCommon.printCsData(result, 3);

            var comboList = vdCommon.fn_makeCombo(result, {DimName : "Layout", DimAttbName : "Layout Class", Sort : "DisplayName"});
            vdCommon.debug("ComboData : " + JSON.stringify(comboList));

            vdCommon.programEnd();

            return comboList;
        } catch ( e ) {
            RuleOutputToUI = { Status : 'Error', Message : "Js Logic Error : " + e.message };
            return;
        }
    };

    var fn_layoutAdd = function(o9Params){
        try {
            const commonLib = require('o9.NSCM.commonLib');
            const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
            vdCommon.setLogLevel("Debug");

            // 파라미터 가져오기
            var parsedParams = JSON.parse(o9Params);
            var fbLayoutClass = parsedParams.fbLayoutClass;
            var fbLayout = parsedParams.fbLayout;

            var result = vdCommon.selectList(
                                ["Version.[Version Name].[CurrentWorkingView]",
                                    "[Layout].[Layout].[" + fbLayout + "]",
                                    "[Sequence].[Sequence].[1]"],
                                ["Measure.[Excel Header Cfg_Header]"],
                                "",
                                "",
                                "");
            if ( result.cs.rowCount > 0 ) {
                RuleOutputToUI = { Status : 'Error', Message : "Layout Data is registered." };
                return;
            } else {
                if ( !vdCommon.existMember('[Layout].[Layout]', fbLayout) ) {
                    vdCommon.createDimension(['[Layout].[Layout Class]','[Layout].[Layout]'], ['"' + fbLayoutClass + '"', '"' + fbLayout + '"']);
                }

                vdCommon.createMeasure(['Version.[Version Name].[CurrentWorkingView]',
                                '[Layout].[Layout].[' + fbLayout + ']',
                                '[Sequence].[Sequence].[1]'],
                            ['Measure.[Excel Header Cfg_Header] = "-";']);
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
            const vdUtil = new commonLib.VdUtil();

            vdCommon.setLogLevel("Debug");

            vdCommon.printParams(o9Params);

            // 파라미터 가져오기
            var parsedParams = JSON.parse(o9Params);
            var fbLayout = parsedParams.fbLayout;
            var fbCount = parsedParams.fbCount;

            vdCommon.printStep("Group ID Max");

            // Max 값을 구한다.
            var result = vdCommon.selectList(["&CWV","[Layout].[Layout].[" + fbLayout + "]","[Sequence].[Sequence]"],
                                                ["Measure.[Excel Header Cfg_Header]"],
                                                "",
                                                "orderby [Sequence].[Sequence].Key desc",
                                                "limit 1");
            var sequence = parseInt(result.cs.row(0).cell(result.cs.memberColumnIndex("Sequence", "Sequence")).Name);

            for ( var m = 1; m <= fbCount; m++ ) {
                sequence++;

                var dimension = [];
                dimension.push('Version.[Version Name].[CurrentWorkingView]');
                dimension.push("[Layout].[Layout].[" + fbLayout + "]");
                dimension.push("[Sequence].[Sequence].[" + sequence + "]");

                var measure = [];
                measure.push('Measure.[Excel Header Cfg_Header] = "-";');

                vdCommon.createMeasure(dimension, measure);
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
            const vdUtil = new commonLib.VdUtil();

            vdCommon.setLogLevel("Debug");

            vdCommon.printParams(o9Params);

             // 파라미터 가져오기
            var parsedParams = JSON.parse(o9Params);
            var fbSelect = parsedParams.fbSelect;

            for ( var i = 0; i < fbSelect.length; i++ ) {
                var row = fbSelect[i];

                var where = [];
                where.push('Version.[Version Name].[CurrentWorkingView]');
                where.push("[Layout].[Layout].[" + row.Layout.Value + "]");
                where.push("[Sequence].[Sequence].[" + row.Sequence.Value + "]");

                vdCommon.deleteMeasure(where, "Excel Header Cfg");
            }

            vdCommon.programEnd();
        } catch ( e ) {
            RuleOutputToUI = { Status : 'Error', Message : "Js Logic Error : " + e.message };
            return;
        }
    };

    return {
        fn_layoutClassCombo : fn_layoutClassCombo,
        fn_layoutAdd : fn_layoutAdd,
        fn_add : fn_add,
        fn_delete : fn_delete
    };
});