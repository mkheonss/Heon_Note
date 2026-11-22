define('o9.NSCM.JSConstraintTypeL3', ['o9/data/query', 'o9/data/cellset', 'o9.NSCM.commonLib'], function () {
    const programName = "o9.NSCM.JSConstraintTypeL3";

    var fn_subSetChange = function(o9Params){
        try {
            const commonLib = require('o9.NSCM.commonLib');
            const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
            vdCommon.setLogLevel("Debug");

            vdCommon.printParams(o9Params);

            // 파라미터 가져오기
            var parsedParams = JSON.parse(o9Params);
            var fbVersion = parsedParams.fbVersion;
            var fbMSL3 = parsedParams.fbMSL3;
            var fbSubSetLevel = parsedParams.fbSubSetLevel;

            vdCommon.updateMeasure(["[Version].[Version Name].[" + fbVersion + "]",
                                        "[Item Material].[MSL3].[" + fbMSL3 + "]"],
                                    ['Measure.[Mtrl Const Type L3_Sub Set] = "' + fbSubSetLevel + '";']);

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
                                        "[Item Material].[MSL3].[" + row.MSL3.Value + "]"],
                                    ["Measure.[Mtrl Const Type L3_Time Varying Flag]"],
                                    "",
                                    "",
                                    "");

                if ( result.cs.rowCount > 0 && result.cs.row(0).cell(result.cs.measureColumnIndex("Mtrl Const Type L3_Time Varying Flag")) == "Y" ) {
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
                                            "[Item Material].[MSL3].[" + row.MSL3.Value + "]"],
                                        ['Measure.[Mtrl Const Type L3_Time Varying Flag] = "Y";']);

                vdCommon.updateMeasure(["[Version].[Version Name].[" + fbVersion + "]",
                                            "[Item Material].[MSL3].[" + row.MSL3.Value + "]",
                                            "[Relative Week].[Relative Week]"],
                                        ['Measure.[Mtrl Const Type L3 W_Type.Lock] = False;',
                                            'Measure.[Mtrl Const Type L3 W_Type] = "Soft";']);
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
                                        "[Item Material].[MSL3].[" + row.MSL3.Value + "]"],
                                    ["Measure.[Mtrl Const Type L3_Time Varying Flag]"],
                                    "",
                                    "",
                                    "");

                if ( result.cs.rowCount > 0 && result.cs.row(0).cell(result.cs.measureColumnIndex("Mtrl Const Type L3_Time Varying Flag")) == "N" ) {
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
                                            "[Item Material].[MSL3].[" + row.MSL3.Value + "]"],
                                        ['Measure.[Mtrl Const Type L3_Time Varying Flag] = "N";']);

                vdCommon.updateMeasure(["[Version].[Version Name].[" + fbVersion + "]",
                                            "[Item Material].[MSL3].[" + row.MSL3.Value + "]",
                                            "[Relative Week].[Relative Week].[W01]"],
                                        ['Measure.[Mtrl Const Type L3 W_Type.Lock] = False;']);

                vdCommon.updateMeasure(["[Version].[Version Name].[" + fbVersion + "]",
                                            "[Item Material].[MSL3].[" + row.MSL3.Value + "]",
                                            '[Relative Week].[Relative Week].filter(#.Name != "W01")'],
                                        ['Measure.[Mtrl Const Type L3 W_Type.Lock] = True;',
                                            'Measure.[Mtrl Const Type L3 W_Type] = "-";']);
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
                                        "[Item Material].[MSL3].[" + row.MSL3.Value + "]"],
                                    ["Measure.[Mtrl Const Type L3_ETDETA]"],
                                    "",
                                    "",
                                    "");

                if ( result.cs.rowCount > 0 && result.cs.row(0).cell(result.cs.measureColumnIndex("Mtrl Const Type L3_ETDETA")) == "ETD" ) {
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
                                            "[Item Material].[MSL3].[" + row.MSL3.Value + "]"],
                                        ['Measure.[Mtrl Const Type L3_ETDETA] = "ETD";']);
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
                                        "[Item Material].[MSL3].[" + row.MSL3.Value + "]"],
                                    ["Measure.[Mtrl Const Type L3_ETDETA]"],
                                    "",
                                    "",
                                    "");

                if ( result.cs.rowCount > 0 && result.cs.row(0).cell(result.cs.measureColumnIndex("Mtrl Const Type L3_ETDETA")) == "ETA" ) {
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
                                            "[Item Material].[MSL3].[" + row.MSL3.Value + "]"],
                                        ['Measure.[Mtrl Const Type L3_ETDETA] = "ETA";']);
            }

            vdCommon.programEnd();
        } catch ( e ) {
            vdCommon.error(e.message);
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
                                        "[Item Material].[MSL3].[" + row.MSL3.Value + "]"],
                                    ["Measure.[Mtrl Const Type L3_Time Varying Flag]",
                                        "Measure.[Mtrl Const Type L3_ETDETA]"],
                                    "",
                                    "",
                                    "");
                if ( result.cs.rowCount > 0 ) {
                    flag = result.cs.row(0).cell(result.cs.measureColumnIndex("Mtrl Const Type L3_Time Varying Flag"));
                    vdCommon.debug("flag : " + flag);

                    if ( fbFlag == "Y" && flag != "Y" ) {
                        vdCommon.createMeasure(["[Version].[Version Name].[" + fbVersion + "]",
                                                    "[Item Material].[MSL3].[" + row.MSL3.Value + "]"],
                                                ['Measure.[Mtrl Const Type L3_Time Varying Flag] = "Y";']);

                        vdCommon.createMeasure(["[Version].[Version Name].[" + fbVersion + "]",
                                                    "[Item Material].[MSL3].[" + row.MSL3.Value + "]",
                                                    "[Relative Week].[Relative Week]"],
                                                ['Measure.[Mtrl Const Type L3 W_Type.Lock] = False;',
                                                    'Measure.[Mtrl Const Type L3 W_Type] = "Soft";']);
                    } else if ( fbFlag == "N" && flag != "N" ) {
                        vdCommon.createMeasure(["[Version].[Version Name].[" + fbVersion + "]",
                                                    "[Item Material].[MSL3].[" + row.MSL3.Value + "]"],
                                                ['Measure.[Mtrl Const Type L3_Time Varying Flag] = "N";']);

                        vdCommon.createMeasure(["[Version].[Version Name].[" + fbVersion + "]",
                                                    "[Item Material].[MSL3].[" + row.MSL3.Value + "]",
                                                    "[Relative Week].[Relative Week].[W01]"],
                                                ['Measure.[Mtrl Const Type L3 W_Type.Lock] = False;']);

                        vdCommon.createMeasure(["[Version].[Version Name].[" + fbVersion + "]",
                                                    "[Item Material].[MSL3].[" + row.MSL3.Value + "]",
                                                    '[Relative Week].[Relative Week].filter(#.Name != "W01")'],
                                                ['Measure.[Mtrl Const Type L3 W_Type.Lock] = True;',
                                                    'Measure.[Mtrl Const Type L3 W_Type] = "-";']);
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
                                        "[Item Material].[MSL3].[" + row.MSL3.Value + "]"],
                                    ["Measure.[Mtrl Const Type L3_Time Varying Flag]",
                                        "Measure.[Mtrl Const Type L3_ETDETA]"],
                                    "",
                                    "",
                                    "");
                if ( result.cs.rowCount > 0 ) {
                    flag = result.cs.row(0).cell(result.cs.measureColumnIndex("Mtrl Const Type L3_ETDETA"));
                    vdCommon.debug("flag : " + flag);

                    if ( fbFlag == "ETD" && flag != "ETD" ) {
                        vdCommon.createMeasure(["[Version].[Version Name].[" + fbVersion + "]",
                                                    "[Item Material].[MSL3].[" + row.MSL3.Value + "]"],
                                                ['Measure.[Mtrl Const Type L3_ETDETA] = "ETD";']);
                    } else if ( fbFlag == "ETA" && flag != "ETA" ) {
                        vdCommon.createMeasure(["[Version].[Version Name].[" + fbVersion + "]",
                                                    "[Item Material].[MSL3].[" + row.MSL3.Value + "]"],
                                                ['Measure.[Mtrl Const Type L3_ETDETA] = "ETA";']);
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
        fn_subSetChange : fn_subSetChange,
        fn_timeVaryingYValidate : fn_timeVaryingYValidate,
        fn_timeVaryingYChange : fn_timeVaryingYChange,
        fn_timeVaryingNValidate : fn_timeVaryingNValidate,
        fn_timeVaryingNChange : fn_timeVaryingNChange,
        fn_etdValidate : fn_etdValidate,
        fn_etdChange : fn_etdChange,
        fn_etaValidate, fn_etaValidate,
        fn_etaChange : fn_etaChange,
        fn_timeVaryingChange : fn_timeVaryingChange,
        fn_etdEtaChange : fn_etdEtaChange
    };
});

/**************************** o9.NSCM.JSConstraintTypeL3 ****************************
    2024-12-18 : ...
    2025-02-11 : fn_timeVaryingChange, fn_etdEtaChange 기능 구현
*********************************************************************/