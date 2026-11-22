define('o9.NSCM.JSExcelUploadMapFunc', ['o9/data/query', 'o9/data/cellset', 'o9.NSCM.commonLib'], function () {
    const programName = "o9.NSCM.JSExcelUploadMapFunc";

    var fn_vendorCombo = function(o9Params){
        try {
            const commonLib = require('o9.NSCM.commonLib');
            const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
            vdCommon.setLogLevel("Debug");

            vdCommon.printParams(o9Params);

            // 파라미터 가져오기
            var parsedParams = JSON.parse(o9Params);
            var fbProductGroup = parsedParams.fbProductGroup;

            var result = vdCommon.selectList(["&VendorHQLocation"],
                                             [],
                                             "",
                                             "",
                                             "");
            vdCommon.printCsData(result, 3);

            var comboList = vdCommon.fn_makeCombo(result, {DimName : "Location", DimAttbName : "Location", isNameWithDisplayName : true, isDisplayNameWithCode : true, Sort : "DisplayName"});
            vdCommon.debug("ComboData : " + JSON.stringify(comboList));

            vdCommon.programEnd();

            return comboList;
        } catch ( e ) {
            RuleOutputToUI = { Status : 'Error', Message : "Js Logic Error : " + e.message };
            return;
        }
    };

    var fn_newVendorAdd = function(o9Params){
        try {
            const commonLib = require('o9.NSCM.commonLib');
            const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
            const vdUtil = new commonLib.VdUtil();

            vdCommon.setLogLevel("Debug");

            vdCommon.printParams(o9Params);

            // 파라미터 가져오기
            var parsedParams = JSON.parse(o9Params);
            var fbHeader = parsedParams.fbHeader;
            var fbSequence = parsedParams.fbSequence;
            var fbVendor = parsedParams.fbVendor;

            vdCommon.updateMeasure(["&VD",
                                        "[Header].[Header].[" + fbHeader + "]",
                                        "[Sequence].[Sequence].[" + fbSequence + "]"],
                                    ['Measure.[Excel Map_Value Conv] = "' + fbVendor.split(":")[0] + '";',
                                        'Measure.[Excel Map_Value Conv Desc] = "' + fbVendor.split(":")[1] + '";',
                                        'Measure.[Excel Map_Value Status] = null;']);

            vdCommon.programEnd();
        } catch ( e ) {
            RuleOutputToUI = { Status : 'Error', Message : "Js Logic Error : " + e.message };
            return;
        }
    };

    var fn_vendorUpdate = function(o9Params){
        try {
            const commonLib = require('o9.NSCM.commonLib');
            const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
            const vdUtil = new commonLib.VdUtil();

            vdCommon.setLogLevel("Debug");

            vdCommon.printParams(o9Params);

            // 파라미터 가져오기
            var parsedParams = JSON.parse(o9Params);
            var fbHeader = parsedParams.fbHeader;
            var fbSequence = parsedParams.fbSequence;
            var fbVendor = parsedParams.fbVendor;

            vdCommon.updateMeasure(["&VD",
                                        "[Header].[Header].[" + fbHeader + "]",
                                        "[Sequence].[Sequence].[" + fbSequence + "]"],
                                    ['Measure.[Excel Map_Value Conv] = "' + fbVendor.split(":")[0] + '";',
                                        'Measure.[Excel Map_Value Conv Desc] = "' + fbVendor.split(":")[1] + '";']);

            vdCommon.programEnd();
        } catch ( e ) {
            RuleOutputToUI = { Status : 'Error', Message : "Js Logic Error : " + e.message };
            return;
        }
    };

    var fn_newDataTypeAdd = function(o9Params){
        try {
            const commonLib = require('o9.NSCM.commonLib');
            const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
            const vdUtil = new commonLib.VdUtil();

            vdCommon.setLogLevel("Debug");

            vdCommon.printParams(o9Params);

            // 파라미터 가져오기
            var parsedParams = JSON.parse(o9Params);
            var fbHeader = parsedParams.fbHeader;
            var fbSequence = parsedParams.fbSequence;
            var fbValueConv = parsedParams.fbValueConv;
            var fbStatus = parsedParams.fbStatus;

            vdCommon.updateMeasure(["&VD",
                                        "[Header].[Header].[" + fbHeader + "]",
                                        "[Sequence].[Sequence].[" + fbSequence + "]"],
                                    ['Measure.[Excel Map_Value Conv] = "' + fbValueConv + '";',
                                        'Measure.[Excel Map_Value Status] = "' + fbStatus + '";']);

            vdCommon.programEnd();
        } catch ( e ) {
            RuleOutputToUI = { Status : 'Error', Message : "Js Logic Error : " + e.message };
            return;
        }
    };

    var fn_plantCombo = function(o9Params){
        try {
            const commonLib = require('o9.NSCM.commonLib');
            const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
            vdCommon.setLogLevel("Debug");

            vdCommon.printParams(o9Params);

            // 파라미터 가져오기
            var parsedParams = JSON.parse(o9Params);
            var fbProductGroup = parsedParams.fbProductGroup;

            var result = vdCommon.selectList(["&NSUISubLocationMFMtrlView"],
                                             [],
                                             "",
                                             "",
                                             "");
            vdCommon.printCsData(result, 3);

            var comboList = vdCommon.fn_makeCombo(result, {DimName : "Sub Location", DimAttbName : "Sub Location", isNameWithDisplayName : true, isDisplayNameWithCode : true, Sort : "DisplayName"});
            vdCommon.debug("ComboData : " + JSON.stringify(comboList));

            vdCommon.programEnd();

            return comboList;
        } catch ( e ) {
            RuleOutputToUI = { Status : 'Error', Message : "Js Logic Error : " + e.message };
            return;
        }
    };

    var fn_newPlantAdd = function(o9Params){
        try {
            const commonLib = require('o9.NSCM.commonLib');
            const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
            const vdUtil = new commonLib.VdUtil();

            vdCommon.setLogLevel("Debug");

            vdCommon.printParams(o9Params);

            // 파라미터 가져오기
            var parsedParams = JSON.parse(o9Params);
            var fbHeader = parsedParams.fbHeader;
            var fbSequence = parsedParams.fbSequence;
            var fbPlant = parsedParams.fbPlant;

            vdCommon.updateMeasure(["&VD",
                                        "[Header].[Header].[" + fbHeader + "]",
                                        "[Sequence].[Sequence].[" + fbSequence + "]"],
                                    ['Measure.[Excel Map_Value Conv] = "' + fbPlant.split(":")[0] + '";',
                                        'Measure.[Excel Map_Value Conv Desc] = "' + fbPlant.split(":")[1] + '";',
                                        'Measure.[Excel Map_Value Status] = null;']);

            vdCommon.programEnd();
        } catch ( e ) {
            RuleOutputToUI = { Status : 'Error', Message : "Js Logic Error : " + e.message };
            return;
        }
    };

    var fn_plantUpdate = function(o9Params){
        try {
            const commonLib = require('o9.NSCM.commonLib');
            const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
            const vdUtil = new commonLib.VdUtil();

            vdCommon.setLogLevel("Debug");

            vdCommon.printParams(o9Params);

            // 파라미터 가져오기
            var parsedParams = JSON.parse(o9Params);
            var fbHeader = parsedParams.fbHeader;
            var fbSequence = parsedParams.fbSequence;
            var fbPlant = parsedParams.fbPlant;

            vdCommon.updateMeasure(["&VD",
                                        "[Header].[Header].[" + fbHeader + "]",
                                        "[Sequence].[Sequence].[" + fbSequence + "]"],
                                    ['Measure.[Excel Map_Value Conv] = "' + fbPlant.split(":")[0] + '";',
                                        'Measure.[Excel Map_Value Conv Desc] = "' + fbPlant.split(":")[1] + '";',
                                        'Measure.[Excel Map_Value Status] = null;']);

            vdCommon.programEnd();
        } catch ( e ) {
            RuleOutputToUI = { Status : 'Error', Message : "Js Logic Error : " + e.message };
            return;
        }
    };

    var fn_vendorDelete = function(o9Params){
        try {
            const commonLib = require('o9.NSCM.commonLib');
            const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
            vdCommon.setLogLevel("Debug");

            vdCommon.printParams(o9Params);

            // 파라미터 가져오기
            var parsedParams = JSON.parse(o9Params);
            var fbSelect = parsedParams.fbSelect;

            for ( var i = 0; i < fbSelect.length; i++ ) {
                var row = fbSelect[i];

                var where = [];
                where.push("&VD");
                where.push("[Header].[Header].[Vendor]");
                where.push("[Sequence].[Sequence].[" + row.Sequence.Value + "]");

                vdCommon.deleteMeasure(where, "Excel Map");
            }

            vdCommon.programEnd();
        } catch ( e ) {
            RuleOutputToUI = { Status : 'Error', Message : "Js Logic Error : " + e.message };
            return;
        }
    };

    var fn_plantDelete = function(o9Params){
        try {
            const commonLib = require('o9.NSCM.commonLib');
            const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
            vdCommon.setLogLevel("Debug");

            vdCommon.printParams(o9Params);

            // 파라미터 가져오기
            var parsedParams = JSON.parse(o9Params);
            var fbSelect = parsedParams.fbSelect;
            var fbVersion = parsedParams.fbVersion;

            for ( var i = 0; i < fbSelect.length; i++ ) {
                var row = fbSelect[i];

                var where = [];
                where.push("&VD");
                where.push("[Header].[Header].[Plant]");
                where.push("[Sequence].[Sequence].[" + row.Sequence.Value + "]");

                vdCommon.deleteMeasure(where, "Excel Map");
            }

            vdCommon.programEnd();
        } catch ( e ) {
            RuleOutputToUI = { Status : 'Error', Message : "Js Logic Error : " + e.message };
            return;
        }
    };



    var fn_seqmentAdd = function(o9Params){
        try {
            const commonLib = require('o9.NSCM.commonLib');
            const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
            vdCommon.setLogLevel("Debug");

            vdCommon.printParams(o9Params);

            // 파라미터 가져오기
            var parsedParams = JSON.parse(o9Params);
            var fbValueOrg = parsedParams.fbValueOrg;
            var fbVendor = parsedParams.fbVendor;

            var result = vdCommon.selectList(["&VD",
                                                "[Header].[Header].[Vendor]",
                                                "[Sequence].[Sequence]"],
                                            [],
                                            'where { Measure.[Excel Map_Value Org] == "' + fbValueOrg + '" }',
                                            "",
                                            "");
            if ( result.cs.rowCount > 0 ) {
                RuleOutputToUI = { Status : 'Error', Message : "Data is already registered" };
                return;
            } else {
                result = vdCommon.selectList(["&VD",
                                                "[Header].[Header].[Vendor]",
                                                "[Sequence].[Sequence]"],
                                                ["Measure.[Excel Map_Value Conv]"],
                                                "",
                                                "orderby [Sequence].[Sequence].Key desc",
                                                "limit 1");
                var maxSequence = 1;
                if ( result.cs.rowCount > 0 ) {
                    maxSequence = parseInt(result.cs.row(0).cell(result.cs.memberColumnIndex("Sequence", "Sequence")).Name) + 1;
                }

                vdCommon.createMeasure(["&VD",
                                            "[Header].[Header].[Vendor]",
                                            "[Sequence].[Sequence].[" + maxSequence + "]"],
                                        ['Measure.[Excel Map_Value Org] = "' + fbValueOrg + '";',
                                            'Measure.[Excel Map_Value Conv] = "' + fbVendor.split(":")[0] + '";',
                                            'Measure.[Excel Map_Value Conv Desc] = "' + fbVendor.split(":")[1] + '";',
                                            'Measure.[Excel Map_Value Status] = null;']);

                if ( !vdCommon.existMember("[Seg].[Seg]", fbValueOrg) ) {
                    vdCommon.createMember("[Seg].[Seg]", fbValueOrg);
                }
            }

            vdCommon.programEnd();
        } catch ( e ) {
            RuleOutputToUI = { Status : 'Error', Message : "Js Logic Error : " + e.message };
            return;
        }
    };

    var fn_dataTypeStatusCombo = function(o9Params){
        try {
            const commonLib = require('o9.NSCM.commonLib');
            const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
            vdCommon.setLogLevel("Debug");

            var comboList = vdCommon.fn_makeCombo(null, {ComboCodes : ["Apply","Ignore"], ComboValues : ["Apply","Ignore"]});
            vdCommon.debug("ComboData : " + JSON.stringify(comboList));

            vdCommon.programEnd();

            return comboList;
        } catch ( e ) {
            RuleOutputToUI = { Status : 'Error', Message : "Js Logic Error : " + e.message };
            return;
        }
    };

    var fn_dataTypeConvCombo = function(o9Params){
        try {
            const commonLib = require('o9.NSCM.commonLib');
            const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
            vdCommon.setLogLevel("Debug");

            vdCommon.printParams(o9Params);

            // 파라미터 가져오기
            var parsedParams = JSON.parse(o9Params);
            var fbValueOrg = parsedParams.fbValueOrg;
            var fbStatus = parsedParams.fbStatus;

            var comboList = null;
            if ( fbStatus == "Apply") {
                //comboList = vdCommon.fn_makeCombo(null, {ComboCodes : ["AIR","EXPRESS","RAIL","TRUCK","VSL","VSL1"], ComboValues : ["AIR","EXPRESS","RAIL","TRUCK","VSL","VSL1"]});
                comboList = vdCommon.fn_makeCombo(null, {ComboCodes : ["AIR","VSL"], ComboValues : ["AIR","VSL"]});
            } else {
                comboList = vdCommon.fn_makeCombo(null, {ComboCodes : [fbValueOrg], ComboValues : [fbValueOrg]});
            }
            vdCommon.debug("ComboData : " + JSON.stringify(comboList));

            vdCommon.programEnd();

            return comboList;
        } catch ( e ) {
            RuleOutputToUI = { Status : 'Error', Message : "Js Logic Error : " + e.message };
            return;
        }
    };

    var fn_dataTypeUpdate = function(o9Params){
        try {
            const commonLib = require('o9.NSCM.commonLib');
            const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
            const vdUtil = new commonLib.VdUtil();

            vdCommon.setLogLevel("Debug");

            vdCommon.printParams(o9Params);

            // 파라미터 가져오기
            var parsedParams = JSON.parse(o9Params);
            var fbHeader = parsedParams.fbHeader;
            var fbSequence = parsedParams.fbSequence;
            var fbValueConv = parsedParams.fbValueConv;
            var fbStatus = parsedParams.fbStatus;

            vdCommon.updateMeasure(["&VD",
                                        "[Header].[Header].[" + fbHeader + "]",
                                        "[Sequence].[Sequence].[" + fbSequence + "]"],
                                    ['Measure.[Excel Map_Value Conv] = "' + fbValueConv + '";',
                                        'Measure.[Excel Map_Value Status] = "' + fbStatus + '";']);

            vdCommon.programEnd();
        } catch ( e ) {
            RuleOutputToUI = { Status : 'Error', Message : "Js Logic Error : " + e.message };
            return;
        }
    };

    var fn_dataTypeDelete = function(o9Params){
        try {
            const commonLib = require('o9.NSCM.commonLib');
            const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
            vdCommon.setLogLevel("Debug");

            vdCommon.printParams(o9Params);

            // 파라미터 가져오기
            var parsedParams = JSON.parse(o9Params);
            var fbSelect = parsedParams.fbSelect;

            for ( var i = 0; i < fbSelect.length; i++ ) {
                var row = fbSelect[i];

                var where = [];
                where.push("&VD");
                where.push("[Header].[Header].[Data type]");
                where.push("[Sequence].[Sequence].[" + row.Sequence.Value + "]");

                vdCommon.deleteMeasure(where, "Excel Map");
            }

            vdCommon.programEnd();
        } catch ( e ) {
            RuleOutputToUI = { Status : 'Error', Message : "Js Logic Error : " + e.message };
            return;
        }
    };

    return {
        fn_vendorCombo : fn_vendorCombo,
        fn_newVendorAdd : fn_newVendorAdd,
        fn_vendorUpdate : fn_vendorUpdate,
        fn_newDataTypeAdd : fn_newDataTypeAdd,
        fn_plantCombo : fn_plantCombo,
        fn_newPlantAdd : fn_newPlantAdd,
        fn_plantUpdate : fn_plantUpdate,
        fn_vendorDelete : fn_vendorDelete,
        fn_plantDelete : fn_plantDelete,
        fn_seqmentAdd : fn_seqmentAdd,
        fn_dataTypeStatusCombo : fn_dataTypeStatusCombo,
        fn_dataTypeConvCombo : fn_dataTypeConvCombo,
        fn_dataTypeUpdate : fn_dataTypeUpdate,
        fn_dataTypeDelete : fn_dataTypeDelete
    };
});

/**************************** o9.NSCM.JSExcelUploadMapFunc ****************************
    2025-02-24 : fn_vendorDelete, fn_vendorDelete, fn_seqmentAdd 기능 추가
    2025-02-28 : fn_useCombo, fn_dataTypeCombo 추가
*********************************************************************/