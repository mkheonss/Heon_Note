define('o9.NSCM.JSConstraintTypeItem', ['o9/data/query', 'o9/data/cellset', 'o9.NSCM.commonLib'], function () {
    const programName = "o9.NSCM.JSConstraintTypeItem";

    var fn_addL3Combo = function(o9Params){
        try {
            const commonLib = require('o9.NSCM.commonLib');
            const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
            vdCommon.setLogLevel("Debug");

            vdCommon.printParams(o9Params);

            // 파라미터 가져오기
            var parsedParams = JSON.parse(o9Params);


            var comboList = [];
            var result = vdCommon.selectList(["&NSUIMtrlMSL3View"],
                                            [],
                                            '',
                                            "",
                                            "");
            var comboList = vdCommon.fn_makeCombo(result, {DimName : "Item Material", DimAttbName : "MSL3", Sort : "Name", isOnlyName : true});
            vdCommon.debug("ComboData : " + JSON.stringify(comboList));

            vdCommon.programEnd();

            return comboList;
        } catch ( e ) {
            vdCommon.error(e.message);
            RuleOutputToUI = { Status : 'Error', Message : "Js Logic Error : " + e.message };
            return;
        }
    };

    var fn_addL5Combo = function(o9Params){
        try {
            const commonLib = require('o9.NSCM.commonLib');
            const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
            vdCommon.setLogLevel("Debug");

            vdCommon.printParams(o9Params);

            // 파라미터 가져오기
            var parsedParams = JSON.parse(o9Params);
            var fbVersion = parsedParams.fbVersion;
            var fbMSL3 = parsedParams.fbMSL3;

            var comboList = [];
            var result = vdCommon.selectList(["&NSUIMtrlMSL3View.[" + fbMSL3 + "]",
                                                "&NSUIMtrlMSL5View"],
                                            [],
                                            "",
                                            "",
                                            "");
            var comboList = vdCommon.fn_makeCombo(result, {DimName : "Item Material", DimAttbName : "MSL5", Sort : "Name", isOnlyName : true});
            vdCommon.debug("ComboData : " + JSON.stringify(comboList));

            vdCommon.programEnd();

            return comboList;
        } catch ( e ) {
            vdCommon.error(e.message);
            RuleOutputToUI = { Status : 'Error', Message : "Js Logic Error : " + e.message };
            return;
        }
    };

    var fn_addItemCombo = function(o9Params){
        try {
            const commonLib = require('o9.NSCM.commonLib');
            const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
            vdCommon.setLogLevel("Debug");

            vdCommon.printParams(o9Params);

            // 파라미터 가져오기
            var parsedParams = JSON.parse(o9Params);
            var fbVersion = parsedParams.fbVersion;
            var fbMSL5 = parsedParams.fbMSL5;

            var comboList = [];
            var result = vdCommon.selectList(["&NSUIMtrlMSL5View.[" + fbMSL5 + "]",
                                                "[Item Material].[Item Material]"],
                                            [],
                                            "",
                                            "",
                                            "");
            var comboList = vdCommon.fn_makeCombo(result, {DimName : "Item Material", DimAttbName : "Item Material", Sort : "DisplayName"});
            vdCommon.debug("ComboData : " + JSON.stringify(comboList));

            vdCommon.programEnd();

            return comboList;
        } catch ( e ) {
            vdCommon.error(e.message);
            RuleOutputToUI = { Status : 'Error', Message : "Js Logic Error : " + e.message };
            return;
        }
    };

    var fn_addLocationCombo = function(o9Params){
        try {
            const commonLib = require('o9.NSCM.commonLib');
            const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
            vdCommon.setLogLevel("Debug");

            vdCommon.printParams(o9Params);

            // 파라미터 가져오기
            var parsedParams = JSON.parse(o9Params);
            var fbVersion = parsedParams.fbVersion;
            var fbItem = parsedParams.fbItem;

            var comboList = [];
            var result = vdCommon.selectList(["&NSUILocationMFMtrlView"],
                                            [],
                                            'where { [Version].[Version Name].[' + fbVersion + '], [Item Material].[Item Material].[' + fbItem + '], Measure.[Item Mtrl Site Asn_Cur Status] in {"ACTIVE","PLANNED"} }',
                                            "",
                                            "");
            var comboList = vdCommon.fn_makeCombo(result, {DimName : "Location", DimAttbName : "Location", Sort : "DisplayName", isDisplayNameWithCode : true});
            vdCommon.debug("ComboData : " + JSON.stringify(comboList));

            vdCommon.programEnd();

            return comboList;
        } catch ( e ) {
            vdCommon.error(e.message);
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
            var fbVersion = parsedParams.fbVersion;
            var fbItem = parsedParams.fbItem;
            var fbLocation = parsedParams.fbLocation;

            for ( var i = 0; i < fbLocation.length; i++ ) {
                vdCommon.createMeasure(["[Version].[Version Name].[" + fbVersion + "]",
                                            "[Item Material].[Item Material].[" + fbItem + "]",
                                            "[Location].[Location].[" + fbLocation[i] + "]"],
                                        ['Measure.[Mtrl Const Type Item_ETDETA] = "ETA";',
                                            'Measure.[Mtrl Const Type Item_Time Varying Flag] = "Y";']);

                vdCommon.createMeasure(["[Version].[Version Name].[" + fbVersion + "]",
                                            "[Item Material].[Item Material].[" + fbItem + "]",
                                            "[Location].[Location].[" + fbLocation[i] + "]",
                                            "[Relative Week].[Relative Week]"],
                                        ['Measure.[Mtrl Const Type Item W_Type] = "Soft";',
                                            'Measure.[Mtrl Const Type Item W_Type.Lock] = False;']);
            }

            vdCommon.programEnd();
        } catch ( e ) {
            vdCommon.error(e.message);
            RuleOutputToUI = { Status : 'Error', Message : "Js Logic Error : " + e.message };
            return;
        }
    };

    var fn_timeVaryingYValidate = function(o9Params){
        var rtn = 0; // 에러 없음

        try {
            const commonLib = require('o9.NSCM.commonLib');
            const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
            vdCommon.setLogLevel("Debug");

            vdCommon.printParams(o9Params);

            // 파라미터 가져오기
            var parsedParams = JSON.parse(o9Params);
            var fbVersion = parsedParams.fbVersion;
            var fbSelect = parsedParams.fbSelect;

            for ( var i = 0; i < fbSelect.length; i++ ) {
                var row = fbSelect[i];

                var result = vdCommon.selectList(
                                    ["[Version].[Version Name].[" + fbVersion + "]",
                                        "[Item Material].[Item Material].[" + row.Item.Value + "]",
                                        "[Location].[Location].[" + row.Location.Value + "]"],
                                    ["Measure.[Mtrl Const Type Item_Time Varying Flag]"],
                                    "",
                                    "",
                                    "");

                if ( result.cs.rowCount > 0 && result.cs.row(0).cell(result.cs.measureColumnIndex("Mtrl Const Type Item_Time Varying Flag")) == "Y" ) {
                    RuleOutputToUI = { Status : 'Error', Message : "Select the Time Varying value of N" };
                    rtn = 1;
                    break;
                }
            }

            vdCommon.programEnd();
        } catch ( e ) {
            vdCommon.error(e.message);
            RuleOutputToUI = { Status : 'Error', Message : "Js Logic Error : " + e.message };
            return;
        }

        return rtn;
    };

    var fn_timeVaryingYChange = function(o9Params){
        try {
            const commonLib = require('o9.NSCM.commonLib');
            const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
            vdCommon.setLogLevel("Debug");

            vdCommon.printParams(o9Params);

            // 파라미터 가져오기
            var parsedParams = JSON.parse(o9Params);
            var fbVersion = parsedParams.fbVersion;
            var fbSelect = parsedParams.fbSelect;

            for ( var i = 0; i < fbSelect.length; i++ ) {
                var row = fbSelect[i];

                vdCommon.updateMeasure(["[Version].[Version Name].[" + fbVersion + "]",
                                            "[Item Material].[Item Material].[" + row.Item.Value + "]",
                                            "[Location].[Location].[" + row.Location.Value + "]"],
                                        ['Measure.[Mtrl Const Type Item_Time Varying Flag] = "Y";']);

                vdCommon.updateMeasure(["[Version].[Version Name].[" + fbVersion + "]",
                                            "[Item Material].[Item Material].[" + row.Item.Value + "]",
                                            "[Location].[Location].[" + row.Location.Value + "]",
                                            "[Relative Week].[Relative Week]"],
                                        ['Measure.[Mtrl Const Type Item W_Type.Lock] = False;',
                                            'Measure.[Mtrl Const Type Item W_Type] = "Soft";']);
            }

            vdCommon.programEnd();
        } catch ( e ) {
            vdCommon.error(e.message);
            RuleOutputToUI = { Status : 'Error', Message : "Js Logic Error : " + e.message };
            return;
        }
    };

    var fn_timeVaryingNValidate = function(o9Params){
        var rtn = 0; // 에러 없음

        try {
            const commonLib = require('o9.NSCM.commonLib');
            const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
            vdCommon.setLogLevel("Debug");

            vdCommon.printParams(o9Params);

            // 파라미터 가져오기
            var parsedParams = JSON.parse(o9Params);
            var fbVersion = parsedParams.fbVersion;
            var fbSelect = parsedParams.fbSelect;

            for ( var i = 0; i < fbSelect.length; i++ ) {
                var row = fbSelect[i];

                var result = vdCommon.selectList(
                                    ["[Version].[Version Name].[" + fbVersion + "]",
                                        "[Item Material].[Item Material].[" + row.Item.Value + "]",
                                        "[Location].[Location].[" + row.Location.Value + "]"],
                                    ["Measure.[Mtrl Const Type Item_Time Varying Flag]"],
                                    "",
                                    "",
                                    "");

                if ( result.cs.rowCount > 0 && result.cs.row(0).cell(result.cs.measureColumnIndex("Mtrl Const Type Item_Time Varying Flag")) == "N" ) {
                    RuleOutputToUI = { Status : 'Error', Message : "Select the Time Varying value of Y" };
                    rtn = 1;
                    break;
                }
            }

            vdCommon.programEnd();
        } catch ( e ) {
            vdCommon.error(e.message);
            RuleOutputToUI = { Status : 'Error', Message : "Js Logic Error : " + e.message };
            return;
        }

        return rtn;
    };

    var fn_timeVaryingNChange = function(o9Params){
        try {
            const commonLib = require('o9.NSCM.commonLib');
            const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
            vdCommon.setLogLevel("Debug");

            vdCommon.printParams(o9Params);

            // 파라미터 가져오기
            var parsedParams = JSON.parse(o9Params);
            var fbVersion = parsedParams.fbVersion;
            var fbSelect = parsedParams.fbSelect;

            for ( var i = 0; i < fbSelect.length; i++ ) {
                var row = fbSelect[i];

                vdCommon.updateMeasure(["[Version].[Version Name].[" + fbVersion + "]",
                                            "[Item Material].[Item Material].[" + row.Item.Value + "]",
                                            "[Location].[Location].[" + row.Location.Value + "]"],
                                        ['Measure.[Mtrl Const Type Item_Time Varying Flag] = "N";']);

                vdCommon.updateMeasure(["[Version].[Version Name].[" + fbVersion + "]",
                                            "[Item Material].[Item Material].[" + row.Item.Value + "]",
                                            "[Location].[Location].[" + row.Location.Value + "]",
                                            "[Relative Week].[Relative Week].[W01]"],
                                        ['Measure.[Mtrl Const Type Item W_Type.Lock] = False;']);

                vdCommon.updateMeasure(["[Version].[Version Name].[" + fbVersion + "]",
                                            "[Item Material].[Item Material].[" + row.Item.Value + "]",
                                            "[Location].[Location].[" + row.Location.Value + "]",
                                            '[Relative Week].[Relative Week].filter(#.Name != "W01")'],
                                        ['Measure.[Mtrl Const Type Item W_Type.Lock] = True;',
                                            'Measure.[Mtrl Const Type Item W_Type] = "-";']);
            }

            vdCommon.programEnd();
        } catch ( e ) {
            vdCommon.error(e.message);
            RuleOutputToUI = { Status : 'Error', Message : "Js Logic Error : " + e.message };
            return;
        }
    };

    var fn_etdValidate = function(o9Params){
        var rtn = 0; // 에러 없음

        try {
            const commonLib = require('o9.NSCM.commonLib');
            const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
            vdCommon.setLogLevel("Debug");

            vdCommon.printParams(o9Params);

            // 파라미터 가져오기
            var parsedParams = JSON.parse(o9Params);
            var fbVersion = parsedParams.fbVersion;
            var fbSelect = parsedParams.fbSelect;

            for ( var i = 0; i < fbSelect.length; i++ ) {
                var row = fbSelect[i];

                var result = vdCommon.selectList(
                                    ["[Version].[Version Name].[" + fbVersion + "]",
                                        "[Item Material].[Item Material].[" + row.Item.Value + "]",
                                        "[Location].[Location].[" + row.Location.Value + "]"],
                                    ["Measure.[Mtrl Const Type Item_ETDETA]"],
                                    "",
                                    "",
                                    "");

                if ( result.cs.rowCount > 0 && result.cs.row(0).cell(result.cs.measureColumnIndex("Mtrl Const Type Item_ETDETA")) == "ETD" ) {
                    RuleOutputToUI = { Status : 'Error', Message : "Select the ETD/ETA value of ETA" };
                    rtn = 1;
                    break;
                }
            }

            vdCommon.programEnd();
        } catch ( e ) {
            vdCommon.error(e.message);
            RuleOutputToUI = { Status : 'Error', Message : "Js Logic Error : " + e.message };
            return;
        }

        return rtn;
    };

    var fn_etdChange = function(o9Params){
        try {
            const commonLib = require('o9.NSCM.commonLib');
            const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
            vdCommon.setLogLevel("Debug");

            vdCommon.printParams(o9Params);

            // 파라미터 가져오기
            var parsedParams = JSON.parse(o9Params);
            var fbVersion = parsedParams.fbVersion;
            var fbSelect = parsedParams.fbSelect;

            for ( var i = 0; i < fbSelect.length; i++ ) {
                var row = fbSelect[i];
                vdCommon.updateMeasure(["[Version].[Version Name].[" + fbVersion + "]",
                                            "[Item Material].[Item Material].[" + row.Item.Value + "]",
                                            "[Location].[Location].[" + row.Location.Value + "]"],
                                        ['Measure.[Mtrl Const Type Item_ETDETA] = "ETD";']);
            }

            vdCommon.programEnd();
        } catch ( e ) {
            vdCommon.error(e.message);
            RuleOutputToUI = { Status : 'Error', Message : "Js Logic Error : " + e.message };
            return;
        }
    };

    var fn_etaValidate = function(o9Params){
        var rtn = 0; // 에러 없음

        try {
            const commonLib = require('o9.NSCM.commonLib');
            const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
            vdCommon.setLogLevel("Debug");

            vdCommon.printParams(o9Params);

            // 파라미터 가져오기
            var parsedParams = JSON.parse(o9Params);
            var fbVersion = parsedParams.fbVersion;
            var fbSelect = parsedParams.fbSelect;

            for ( var i = 0; i < fbSelect.length; i++ ) {
                var row = fbSelect[i];

                var result = vdCommon.selectList(
                                    ["[Version].[Version Name].[" + fbVersion + "]",
                                        "[Item Material].[Item Material].[" + row.Item.Value + "]",
                                        "[Location].[Location].[" + row.Location.Value + "]"],
                                    ["Measure.[Mtrl Const Type Item_ETDETA]"],
                                    "",
                                    "",
                                    "");

                if ( result.cs.rowCount > 0 && result.cs.row(0).cell(result.cs.measureColumnIndex("Mtrl Const Type Item_ETDETA")) == "ETA" ) {
                    RuleOutputToUI = { Status : 'Error', Message : "Select the ETD/ETA value of ETD" };
                    rtn = 1;
                    break;
                }
            }

            vdCommon.programEnd();
        } catch ( e ) {
            vdCommon.error(e.message);
            RuleOutputToUI = { Status : 'Error', Message : "Js Logic Error : " + e.message };
            return;
        }

        return rtn;
    };

    var fn_etaChange = function(o9Params){
        try {
            const commonLib = require('o9.NSCM.commonLib');
            const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
            vdCommon.setLogLevel("Debug");

            vdCommon.printParams(o9Params);

            // 파라미터 가져오기
            var parsedParams = JSON.parse(o9Params);
            var fbVersion = parsedParams.fbVersion;
            var fbSelect = parsedParams.fbSelect;

            for ( var i = 0; i < fbSelect.length; i++ ) {
                var row = fbSelect[i];

                vdCommon.updateMeasure(["[Version].[Version Name].[" + fbVersion + "]",
                                            "[Item Material].[Item Material].[" + row.Item.Value + "]",
                                            "[Location].[Location].[" + row.Location.Value + "]"],
                                        ['Measure.[Mtrl Const Type Item_ETDETA] = "ETA";']);
            }

            vdCommon.programEnd();
        } catch ( e ) {
            vdCommon.error(e.message);
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
            var fbSelect = parsedParams.fbSelect;
            var fbVersion = parsedParams.fbVersion;

            for ( var i = 0; i < fbSelect.length; i++ ) {
                var row = fbSelect[i];

                var where = [];
                where.push("[Version].[Version Name].[" + fbVersion + "]");
                where.push("[Item Material].[Item Material].[" + row.Item.Value + "]");
                where.push("[Location].[Location].[" + row.Location.Value + "]");

                vdCommon.deleteMeasure(where, "Mtrl Const Type Item");
                vdCommon.deleteMeasure(where, "Mtrl Const Type Item W");
            }

            vdCommon.programEnd();
        } catch ( e ) {
            RuleOutputToUI = { Status : 'Error', Message : "Js Logic Error : " + e.message };
            return;
        }
    };

    var fn_timeVaryingChange = function(o9Params){
        try {
            const commonLib = require('o9.NSCM.commonLib');
            const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
            vdCommon.setLogLevel("Debug");

            vdCommon.printParams(o9Params);

            // 파라미터 가져오기
            var parsedParams = JSON.parse(o9Params);
            var fbVersion = parsedParams.fbVersion;
            var fbSelect = parsedParams.fbSelect;
            var fbFlag = parsedParams.fbFlag;

            for ( var i = 0; i < fbSelect.length; i++ ) {
                var row = fbSelect[i];

                var result = vdCommon.selectList(
                                    ["[Version].[Version Name].[" + fbVersion + "]",
                                        "[Item Material].[Item Material].[" + row.Item.Value + "]",
                                        "[Location].[Location].[" + row.Location.Value + "]"],
                                    ["Measure.[Mtrl Const Type Item_Time Varying Flag]",
                                        "Measure.[Mtrl Const Type Item_ETDETA]"],
                                    "",
                                    "",
                                    "");
                if ( result.cs.rowCount > 0 ) {
                    flag = result.cs.row(0).cell(result.cs.measureColumnIndex("Mtrl Const Type Item_Time Varying Flag"));
                    vdCommon.debug("flag : " + flag);

                    if ( fbFlag == "Y" && flag != "Y" ) {
                        vdCommon.createMeasure(["[Version].[Version Name].[" + fbVersion + "]",
                                                    "[Item Material].[Item Material].[" + row.Item.Value + "]",
                                                    "[Location].[Location].[" + row.Location.Value + "]"],
                                                ['Measure.[Mtrl Const Type Item_Time Varying Flag] = "Y";']);

                        vdCommon.createMeasure(["[Version].[Version Name].[" + fbVersion + "]",
                                                    "[Item Material].[Item Material].[" + row.Item.Value + "]",
                                                    "[Location].[Location].[" + row.Location.Value + "]",
                                                    "[Relative Week].[Relative Week]"],
                                                ['Measure.[Mtrl Const Type Item W_Type.Lock] = False;',
                                                    'Measure.[Mtrl Const Type Item W_Type] = "Soft";']);
                    } else if ( fbFlag == "N" && flag != "N" ) {
                        vdCommon.createMeasure(["[Version].[Version Name].[" + fbVersion + "]",
                                                    "[Item Material].[Item Material].[" + row.Item.Value + "]",
                                                    "[Location].[Location].[" + row.Location.Value + "]"],
                                                ['Measure.[Mtrl Const Type Item_Time Varying Flag] = "N";']);

                        vdCommon.createMeasure(["[Version].[Version Name].[" + fbVersion + "]",
                                                    "[Item Material].[Item Material].[" + row.Item.Value + "]",
                                                    "[Location].[Location].[" + row.Location.Value + "]",
                                                    "[Relative Week].[Relative Week].[W01]"],
                                                ['Measure.[Mtrl Const Type Item W_Type.Lock] = False;']);

                        vdCommon.createMeasure(["[Version].[Version Name].[" + fbVersion + "]",
                                                    "[Item Material].[Item Material].[" + row.Item.Value + "]",
                                                    "[Location].[Location].[" + row.Location.Value + "]",
                                                    '[Relative Week].[Relative Week].filter(#.Name != "W01")'],
                                                ['Measure.[Mtrl Const Type Item W_Type.Lock] = True;',
                                                    'Measure.[Mtrl Const Type Item W_Type] = "-";']);
                    }
                }
            }

            vdCommon.programEnd();
        } catch ( e ) {
            vdCommon.error(e.message);
            RuleOutputToUI = { Status : 'Error', Message : "Js Logic Error : " + e.message };
            return;
        }
    };

    var fn_etdEtaChange = function(o9Params){
        try {
            const commonLib = require('o9.NSCM.commonLib');
            const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
            vdCommon.setLogLevel("Debug");

            vdCommon.printParams(o9Params);

            // 파라미터 가져오기
            var parsedParams = JSON.parse(o9Params);
            var fbVersion = parsedParams.fbVersion;
            var fbSelect = parsedParams.fbSelect;
            var fbFlag = parsedParams.fbFlag;

            for ( var i = 0; i < fbSelect.length; i++ ) {
                var row = fbSelect[i];

                var result = vdCommon.selectList(
                                    ["[Version].[Version Name].[" + fbVersion + "]",
                                        "[Item Material].[Item Material].[" + row.Item.Value + "]",
                                        "[Location].[Location].[" + row.Location.Value + "]"],
                                    ["Measure.[Mtrl Const Type Item_Time Varying Flag]",
                                        "Measure.[Mtrl Const Type Item_ETDETA]"],
                                    "",
                                    "",
                                    "");
                if ( result.cs.rowCount > 0 ) {
                    flag = result.cs.row(0).cell(result.cs.measureColumnIndex("Mtrl Const Type Item_ETDETA"));
                    vdCommon.debug("flag : " + flag);

                    if ( fbFlag == "ETD" && flag != "ETD" ) {
                        vdCommon.createMeasure(["[Version].[Version Name].[" + fbVersion + "]",
                                                    "[Item Material].[Item Material].[" + row.Item.Value + "]",
                                                    "[Location].[Location].[" + row.Location.Value + "]"],
                                                ['Measure.[Mtrl Const Type Item_ETDETA] = "ETD";']);
                    } else if ( fbFlag == "ETA" && flag != "ETA" ) {
                        vdCommon.createMeasure(["[Version].[Version Name].[" + fbVersion + "]",
                                                    "[Item Material].[Item Material].[" + row.Item.Value + "]",
                                                    "[Location].[Location].[" + row.Location.Value + "]"],
                                                ['Measure.[Mtrl Const Type Item_ETDETA] = "ETA";']);
                    }
                }
            }

            vdCommon.programEnd();
        } catch ( e ) {
            vdCommon.error(e.message);
            RuleOutputToUI = { Status : 'Error', Message : "Js Logic Error : " + e.message };
            return;
        }
    };

    return {
        fn_addL3Combo : fn_addL3Combo,
        fn_addL5Combo : fn_addL5Combo,
        fn_addItemCombo : fn_addItemCombo,
        fn_addLocationCombo : fn_addLocationCombo,
        fn_add : fn_add,
        fn_timeVaryingYValidate : fn_timeVaryingYValidate,
        fn_timeVaryingYChange : fn_timeVaryingYChange,
        fn_timeVaryingNValidate : fn_timeVaryingNValidate,
        fn_timeVaryingNChange : fn_timeVaryingNChange,
        fn_etdValidate : fn_etdValidate,
        fn_etdChange : fn_etdChange,
        fn_etaValidate, fn_etaValidate,
        fn_etaChange : fn_etaChange,
        fn_delete : fn_delete,
        fn_timeVaryingChange : fn_timeVaryingChange,
        fn_etdEtaChange : fn_etdEtaChange
    };
});

/**************************** o9.NSCM.JSConstraintTypeItem ****************************
    2024-12-18 : ...

*********************************************************************/