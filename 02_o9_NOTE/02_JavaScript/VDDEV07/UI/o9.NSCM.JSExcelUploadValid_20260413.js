define('o9.NSCM.JSExcelUploadValid', ['o9/data/query', 'o9/data/cellset', 'o9.NSCM.commonLib'], function () {
    const programName = "o9.NSCM.JSExcelUploadValid";

    var fn_headerAdd = function(o9Params){
        try {
            const commonLib = require('o9.NSCM.commonLib');
            const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
            vdCommon.setLogLevel("Debug");

            // 파라미터 가져오기
            var parsedParams = JSON.parse(o9Params);
            var fbHeader = parsedParams.fbHeader;

            var result = vdCommon.selectList(
                                ["&VD",
                                    "[Header].[Header].[" + fbHeader + "]",
                                    "[Sequence].[Sequence]"],
                                ["Measure.[Excel Valid_Value]"],
                                "",
                                "",
                                "");
            if ( result.cs.rowCount > 0 ) {
                RuleOutputToUI = { Status : 'Error', Message : "Header is registered." };
                return;
            } else {
                if ( !vdCommon.existMember('[Header].[Header]', fbHeader) ) {
                    vdCommon.createDimension(['[Header].[Auto Yn]','[Header].[Header]'], ['"N"', '"' + fbHeader + '"']);
                }

                vdCommon.createMeasure(['&VD',
                                '[Header].[Header].[' + fbHeader + ']',
                                '[Sequence].[Sequence].[1]'],
                            ['Measure.[Excel Valid_Value] = "-";']);
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
            var fbHeader = parsedParams.fbHeader;
            var fbCount = parsedParams.fbCount;

            vdCommon.printStep("Group ID Max");

            // Max 값을 구한다.
            var result = vdCommon.selectList(["&VD","[Header].[Header].[" + fbHeader + "]","[Sequence].[Sequence]"],
                                                ["Measure.[Excel Valid_Value]"],
                                                "",
                                                "orderby [Sequence].[Sequence].Key desc",
                                                "limit 1");
            var sequence = parseInt(result.cs.row(0).cell(result.cs.memberColumnIndex("Sequence", "Sequence")).Name);

            for ( var m = 1; m <= fbCount; m++ ) {
                sequence++;

                var dimension = [];
                dimension.push('&VD');
                dimension.push("[Header].[Header].[" + fbHeader + "]");
                dimension.push("[Sequence].[Sequence].[" + sequence + "]");

                var measure = [];
                measure.push('Measure.[Excel Valid_Value] = "-";');

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
                where.push('&VD');
                where.push("[Header].[Header].[" + row.Header.Value + "]");
                where.push("[Sequence].[Sequence].[" + row.Sequence.Value + "]");

                vdCommon.deleteMeasure(where, "Excel Valid");
            }

            vdCommon.programEnd();
        } catch ( e ) {
            RuleOutputToUI = { Status : 'Error', Message : "Js Logic Error : " + e.message };
            return;
        }
    };

    return {
        fn_headerAdd : fn_headerAdd,
        fn_add : fn_add,
        fn_delete : fn_delete
    };
});

/**************************** o9.NSCM.JSExcelUploadValid ****************************
    2024-11-13 : ...
*********************************************************************/