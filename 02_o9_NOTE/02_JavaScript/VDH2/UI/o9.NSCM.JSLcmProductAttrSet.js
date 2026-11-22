define('o9.NSCM.JSLcmProductAttrSet', ['o9/data/query', 'o9/data/cellset', 'o9.NSCM.commonLib'], function () {
    const programName = "o9.NSCM.JSLcmProductAttrSet";

    var fn_add = function(o9Params){
        try {
            var commonLib = require('o9.NSCM.commonLib');
            var vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
            vdCommon.setLogLevel("Debug");

            vdCommon.printParams(o9Params);

            // 파라미터 가져오기
            var parsedParams = JSON.parse(o9Params);
            var fbProductGroup = parsedParams.fbProductGroup;
            var fbProduct = parsedParams.fbProduct;
            var fbVersionName = parsedParams.fbVersionName || "CWV_MP";

            vdCommon.printStep("[Item].[Product Group] Validation Check");
            if ( vdCommon.existMember('[Item].[Product Group]', fbProductGroup) ) {
                vdCommon.printStep("[Product].[Product Group] Member Check");
                if ( !vdCommon.existMember('[Product].[Product Group]', fbProductGroup) ) {
                    vdCommon.createMember('[Product].[Product Group]', fbProductGroup);
                }
            } else {
                RuleOutputToUI = { Status : 'Error', Message : "The data (" + fbProductGroup + ") does not exist in [Item].[Product Group]." };
                return;
            }

            vdCommon.printStep("[Item].[Product] Validation Check");
            if ( vdCommon.existMember('[Item].[Product]', fbProduct) ) {
                vdCommon.printStep("[Product].[Product] Member Check");
                if ( !vdCommon.existMember('[Product].[Product]', fbProduct) ) {
                    vdCommon.createMember('[Product].[Product]', fbProduct);
                }
            } else {
                RuleOutputToUI = { Status : 'Error', Message : "The data (" + fbProduct + ")  does not exist in [Item].[Product]." };
                return;
            }

            vdCommon.printStep("Product Dimension Check");
            if ( !vdCommon.existDimension(['[Product].[Product Group].[' + fbProductGroup + ']', '[Product].[Product].[' + fbProduct + ']']) ) {
                vdCommon.createDimension(['[Product].[Product Group]','[Product].[Product]'], ['"' + fbProductGroup + '"', '"' + fbProduct + '"']);
            }

            vdCommon.printStep("Lcm Product Attr Set Measure Add");
            var dimension = ["[Version].[Version Name].[" + fbVersionName + "]",
                                '[Product].[Product].[' + fbProduct + ']'];
            if ( !vdCommon.existMeasure(dimension, ['Measure.[Lcm Prod Attr Set_Attr01 Name]']) ) {
                vdCommon.createMeasure(dimension,
                            ['Measure.[Lcm Prod Attr Set_Attr01 Name] = "";',
                            'Measure.[Lcm Prod Attr Set_Attr02 Name] = "";',
                            'Measure.[Lcm Prod Attr Set_Attr03 Name] = "";',
                            'Measure.[Lcm Prod Attr Set_Attr04 Name] = "";',
                            'Measure.[Lcm Prod Attr Set_Attr05 Name] = "";',
                            'Measure.[Lcm Prod Attr Set_Attr06 Name] = "";',
                            'Measure.[Lcm Prod Attr Set_Attr07 Name] = "";',
                            'Measure.[Lcm Prod Attr Set_Attr08 Name] = "";',
                            'Measure.[Lcm Prod Attr Set_Attr09 Name] = "";',
                            'Measure.[Lcm Prod Attr Set_Attr10 Name] = "";',
                            'Measure.[Lcm Prod Attr Set_Attr11 Name] = "";',
                            'Measure.[Lcm Prod Attr Set_Attr12 Name] = "";',
                            'Measure.[Lcm Prod Attr Set_Attr13 Name] = "";',
                            'Measure.[Lcm Prod Attr Set_Attr14 Name] = "";',
                            'Measure.[Lcm Prod Attr Set_Attr15 Name] = "";']);
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

    var fn_delete = function(o9Params){
        try {
            var commonLib = require('o9.NSCM.commonLib');
            var vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
            vdCommon.setLogLevel("Debug");

            vdCommon.printParams(o9Params);

            // 파라미터 가져오기
            var parsedParams = JSON.parse(o9Params);
            var fbProductGroup = parsedParams.fbProductGroup;
            var fbProduct = parsedParams.fbProduct;
            var fbVersionName = parsedParams.fbVersionName || "CWV_MP";

            var result = vdCommon.selectList(
                                ["[Version].[Version Name].[" + fbVersionName + "]",
                                    "[Product].[Product].[" + fbProduct + "]",
                                    "[Item].[Class Category]",
                                    "[Attr No].[Attr No].[ATTB01]",
                                    "[Sequence].[Sequence]"],
                                ["Measure.[Lcm Item Attr Map_RuleNo]"],
                                "",
                                "",
                                "");
            if ( result.cs.rowCount > 0 ) {
                RuleOutputToUI = { Status : 'Error', Message : "Class Category Data is registered." };
                return;
            } else {
                var where = [];
                where.push("[Version].[Version Name].[" + fbVersionName + "]");
                where.push("[Product].[Product].[" + fbProduct + "]");

                vdCommon.printStep("Product Attr Set Measure Delete");
                vdCommon.deleteMeasure(where, "Lcm Product Attr Set");
            }

            vdCommon.programEnd();
        } catch ( e ) {
            RuleOutputToUI = { Status : 'Error', Message : "Js Logic Error : " + e.message };
            return;
        }
    };

    var fn_apply = function(o9Params){
        try {
            var commonLib = require('o9.NSCM.commonLib');
            var vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
            var vdUtil = new commonLib.VdUtil();
            vdCommon.setLogLevel("Debug");

            vdCommon.printParams(o9Params);

            // 파라미터 가져오기
            var parsedParams = JSON.parse(o9Params);
            var fbVersionName = parsedParams.fbVersionName || "CWV_MP";

            var result = vdCommon.selectList(["[Version].[Version Name].[" + fbVersionName + "]",
                                                "[Product].[Product Group]",
                                                "[Product].[Product]"],
                                             ["Measure.[Lcm Prod Attr Set_Attr01 Name]",
                                             "Measure.[Lcm Prod Attr Set_Attr02 Name]",
                                             "Measure.[Lcm Prod Attr Set_Attr03 Name]",
                                             "Measure.[Lcm Prod Attr Set_Attr04 Name]",
                                             "Measure.[Lcm Prod Attr Set_Attr05 Name]",
                                             "Measure.[Lcm Prod Attr Set_Attr06 Name]",
                                             "Measure.[Lcm Prod Attr Set_Attr07 Name]",
                                             "Measure.[Lcm Prod Attr Set_Attr08 Name]",
                                             "Measure.[Lcm Prod Attr Set_Attr09 Name]",
                                             "Measure.[Lcm Prod Attr Set_Attr10 Name]",
                                             "Measure.[Lcm Prod Attr Set_Attr11 Name]",
                                             "Measure.[Lcm Prod Attr Set_Attr12 Name]",
                                             "Measure.[Lcm Prod Attr Set_Attr13 Name]",
                                             "Measure.[Lcm Prod Attr Set_Attr14 Name]",
                                             "Measure.[Lcm Prod Attr Set_Attr15 Name]"],
                                             "",
                                             "",
                                             "");
            vdCommon.printCsData(result, 3);

            for ( var i = 0; i < result.cs.rowCount; i++ ) {
                var product = vdUtil.fn_getString(result.cs.row(i).cell(result.cs.memberColumnIndex("Product", "Product")).Name);

                var queryStr = "";

                var attbNos = "01,02,03,04,05,06,07,08,09,10,11,12,13,14,15".split(",");
                for ( const attbNo of attbNos ) {
                    var attrName = vdUtil.fn_getString(result.cs.row(i).cell(result.cs.measureColumnIndex("Lcm Prod Attr Set_Attr" + attbNo + " Name")));

                    var dimension = [];
                    dimension.push("[Version].[Version Name].[" + fbVersionName + "]");
                    dimension.push("[Product].[Product].[" + product + "]");
                    dimension.push("[Attr No].[Attr No].[ATTB" + attbNo + "]");

                    var measure = [];
                    measure.push('Measure.[Lcm Prod Attr_Attr Name] = "' + attrName + '";');

                    queryStr += vdCommon.createMeasureQuery(dimension, measure);
                }

                vdCommon.executeQuery("Batch Query" , queryStr);
            }

            vdCommon.programEnd();
        } catch ( e ) {
            RuleOutputToUI = { Status : 'Error', Message : "Js Logic Error : " + e.message };
            return;
        }
    };

    return {
        fn_add : fn_add,
        fn_delete : fn_delete,
        fn_apply : fn_apply
    };
});

/**************************** Modify Log ****************************
    2024-11-13 : ...
*********************************************************************/