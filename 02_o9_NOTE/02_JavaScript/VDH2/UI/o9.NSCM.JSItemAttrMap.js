define('o9.NSCM.JSItemAttrMap', ['o9/data/query', 'o9/data/cellset', 'o9.NSCM.commonLib'], function () {

    var fn_classCategoryAdd = function(o9Params){
        try {
            var commonLib = require('o9.NSCM.commonLib');

            var programName = "o9.NSCM.JSItemAttrMap.fn_classCategoryAdd";

            vdUtil = new commonLib.VdUtil();
            vdCommon = new commonLib.VdCommon(programName);
            vdCommon.setLogLevel("Debug");

            vdCommon.printParams(o9Params);

            // 파라미터 가져오기
            var parsedParams = JSON.parse(o9Params);
            var fbProduct = parsedParams.fbProduct;
            var fbClassCategory = parsedParams.fbClassCategory;
            var fbVersionName = parsedParams.fbVersionName;

            if ( !vdCommon.existMeasure(
                        ["[Version].[Version Name].[" + fbVersionName + "]",
                            "[Product].[Product].[" + fbProduct + "]",
                            "[Item].[Class Category].[" + fbClassCategory + "]",
                            "[Attr No].[Attr No].[ATTB01]",
                            "[Sequence].[Sequence].[1]"],
                        ['Measure.[Item Attr Map_RuleNo]']) ) {
                var queryStr = "";

                var attbNos = "01,02,03,04,05,06,07,08,09,10,11,12,13,14,15".split(",");
                for ( const attbNo of attbNos ) {
                    var dimension = [];
                    dimension.push("[Version].[Version Name].[" + fbVersionName + "]");
                    dimension.push("[Product].[Product].[" + fbProduct + "]");
                    dimension.push("[Item].[Class Category].[" + fbClassCategory + "]");
                    dimension.push("[Attr No].[Attr No].[ATTB" + attbNo + "]");
                    dimension.push("[Sequence].[Sequence].[1]");

                    var measure = [];
                    measure.push('Measure.[Item Attr Map_RuleNo] = "' + fbClassCategory + "_ATTB" + attbNo + '_1";');
                    measure.push('Measure.[Item Attr Map_Rule Seq] = 1;');

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
            var commonLib = require('o9.NSCM.commonLib');

            var programName = "o9.NSCM.JSItemAttrMap.fn_add";
            vdCommon = new commonLib.VdCommon(programName);
            vdCommon.setLogLevel("Debug");

            vdCommon.printParams(o9Params);

            // 파라미터 가져오기
            var parsedParams = JSON.parse(o9Params);
            var fbSelect = parsedParams.fbSelect;
            var fbCount = parsedParams.fbCount;
            var fbVersionName = parsedParams.fbVersionName;

            for ( var i = 0; i < fbSelect.length; i++ ) {
                var row = fbSelect[i];

                var result = vdCommon.selectList(
                                    ["[Version].[Version Name].[" + fbVersionName + "]",
                                        "[Product].[Product].[" + row.Product.Value + "]",
                                        "[Item].[Class Category].[" + row.ClassCategory.Value + "]",
                                        "[Attr No].[Attr No].[" + row.AttrNo.Value + "]",
                                        "[Sequence].[Sequence]"],
                                    ["Measure.[Item Attr Map_RuleNo]"],
                                    "",
                                    "orderby [Sequence].[Sequence].Key desc",
                                    "");

                var sequence = parseInt(result.cs.row(0).cell(result.cs.memberColumnIndex("Sequence", "Sequence")).Name);

                for ( var m = 1; m <= fbCount; m++ ) {
                    sequence++;

                    var dimension = [];
                    dimension.push("[Version].[Version Name].[" + fbVersionName + "]");
                    dimension.push("[Product].[Product].[" + row.Product.Value + "]");
                    dimension.push("[Item].[Class Category].[" + row.ClassCategory.Value + "]");
                    dimension.push("[Attr No].[Attr No].[" + row.AttrNo.Value + "]");
                    dimension.push("[Sequence].[Sequence].[" + sequence + "]");

                    var measure = [];
                    measure.push('Measure.[Item Attr Map_RuleNo] = "' + row.ClassCategory.Value + '_' + row.AttrNo.Value + '_' + sequence + '";');
                    measure.push('Measure.[Item Attr Map_Rule Seq] = ' + sequence + ';');

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
            var commonLib = require('o9.NSCM.commonLib');

            var programName = "o9.NSCM.JSItemAttrMap.fn_delete";
            vdCommon = new commonLib.VdCommon(programName);
            vdCommon.setLogLevel("Debug");

            vdCommon.printParams(o9Params);

            // 파라미터 가져오기
            var parsedParams = JSON.parse(o9Params);
            var fbSelect = parsedParams.fbSelect;
            var fbVersionName = parsedParams.fbVersionName;

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
                where.push("[Product].[Product].[" + row.Product.Value + "]");
                where.push("[Item].[Class Category].[" + row.ClassCategory.Value + "]");
                where.push("[Attr No].[Attr No].[" + row.AttrNo.Value + "]");
                where.push("[Sequence].[Sequence].[" + row.Sequence.Value + "]");

                vdCommon.deleteMeasure(where, "Item Attr Map");
            }

            vdCommon.programEnd();
        } catch ( e ) {
            RuleOutputToUI = { Status : 'Error', Message : "Js Logic Error : " + e.message };
            return;
        }
    };

    return {
        fn_classCategoryAdd : fn_classCategoryAdd,
        fn_add : fn_add,
        fn_delete : fn_delete
    };
});