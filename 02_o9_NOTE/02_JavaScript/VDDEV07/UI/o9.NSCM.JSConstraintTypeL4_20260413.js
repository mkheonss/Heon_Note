define('o9.NSCM.JSConstraintTypeL4', ['o9/data/query', 'o9/data/cellset', 'o9.NSCM.commonLib'], function () {
    const programName = "o9.NSCM.JSConstraintTypeL4";

    var fn_addL3Combo = function(o9Params){
        try {
            const commonLib = require('o9.NSCM.commonLib');
            const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
            vdCommon.setLogLevel("Debug");

            vdCommon.printParams(o9Params);

            // 파라미터 가져오기
            var parsedParams = JSON.parse(o9Params);
            var fbVersion = parsedParams.fbVersion;

            var comboList = [];
            var rMsl = vdCommon.selectList(
                                ["[Version].[Version Name].[" + fbVersion + "]",
                                    "&NSUIMtrlMSL3View"],
                                ["Measure.[Mtrl Const Type L3_Sub Set]"],
                                'where {Measure.[Mtrl Const Type L3_Sub Set] == "LV4"}',
                                "",
                                "");
            for ( var i = 0; i < rMsl.cs.rowCount; i++ ) {
                msl = rMsl.cs.row(i).cell(rMsl.cs.memberColumnIndex("Item Material", "MSL3")).Name;

                comboList.push({ Name : msl, DisplayName : msl});
            }

            // 정렬
            comboList.sort((a, b) => {
                    if ( a.Name < b.Name ) return -1;
                    if ( a.Name > b.Name ) return 1;
                    return 0;
                });

            vdCommon.programEnd();

            return comboList;
        } catch ( e ) {
            vdCommon.error(e.message);
            RuleOutputToUI = { Status : 'Error', Message : "Js Logic Error : " + e.message };
            return;
        }
    };

    var fn_addL4Combo = function(o9Params){
        try {
            const commonLib = require('o9.NSCM.commonLib');
            const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
            vdCommon.setLogLevel("Debug");

            vdCommon.printParams(o9Params);

            // 파라미터 가져오기
            var parsedParams = JSON.parse(o9Params);
            var fbVersion = parsedParams.fbVersion;
            var fbMSL3 = parsedParams.fbMSL3;

            // MSL4 에 있는 데이타를 가져온다.
            var rExistMsl = vdCommon.selectList(
                                ["[Version].[Version Name].[" + fbVersion + "]",
                                    "[Item Material].[MSL3].[" + fbMSL3 + "]",
                                    "&NSUIMtrlMSL4View"],
                                ["Measure.[Mtrl Const Type L4_ETDETA]"],
                                "",
                                "",
                                "");
            var validHm = {};
            for ( var i = 0; i < rExistMsl.cs.rowCount; i++ ) {
                msl = rExistMsl.cs.row(i).cell(rExistMsl.cs.memberColumnIndex("Item Material", "MSL4")).Name;

                if ( validHm[msl] == undefined ) {
                    validHm[msl] = msl;
                }
            }
            vdCommon.debug("validHm : " + JSON.stringify(validHm));

            // 등록되지 않은 MSL3의 데이타로 콤보를 구성한다.
            var comboList = [];
            var rMsl = vdCommon.selectList(
                            ["[Item Material].[MSL3].[" + fbMSL3 + "]",
                                "&NSUIMtrlMSL4View"],
                            [],
                            "",
                            "",
                            "");
            for ( var m = 0; m < rMsl.cs.rowCount; m++ ) {
                msl = rMsl.cs.row(m).cell(rMsl.cs.memberColumnIndex("Item Material", "MSL4")).Name;
                if ( validHm[msl] == undefined ) {
                    comboList.push({ Name : msl, DisplayName : msl});
                }
            }

            // 정렬
            comboList.sort((a, b) => {
                    if ( a.Name < b.Name ) return -1;
                    if ( a.Name > b.Name ) return 1;
                    return 0;
                });

            vdCommon.programEnd();

            return comboList;
        } catch ( e ) {
            vdCommon.error(e.message);
            RuleOutputToUI = { Status : 'Error', Message : "Js Logic Error : " + e.message };
            return;
        }
    };

    var fn_addEtdEtaCombo = function(o9Params){
        try {
            const commonLib = require('o9.NSCM.commonLib');
            const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
            vdCommon.setLogLevel("Debug");

            var comboList = vdCommon.fn_makeCombo(null, {ComboCodes : ["ETD","ETA"], ComboValues : ["ETD","ETA"]});
            vdCommon.debug("ComboData : " + JSON.stringify(comboList));

            vdCommon.programEnd();

            return comboList;
        } catch ( e ) {
            vdCommon.error(e.message);
            RuleOutputToUI = { Status : 'Error', Message : "Js Logic Error : " + e.message };
            return;
        }
    };

    var fn_addTimeVaryingCombo = function(o9Params){
        try {
            const commonLib = require('o9.NSCM.commonLib');
            const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
            vdCommon.setLogLevel("Debug");

            var comboList = vdCommon.fn_makeCombo(null, {ComboCodes : ["Y","N"], ComboValues : ["Y","N"]});
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
            var fbMSL4 = parsedParams.fbMSL4;
            var fbEtdEta = parsedParams.fbEtdEta;
            var fbTimeVarying = parsedParams.fbTimeVarying;
            var fbConstType = parsedParams.fbConstType;

            vdCommon.createMeasure(["[Version].[Version Name].[" + fbVersion + "]",
                                        "[Item Material].[MSL4].[" + fbMSL4 + "]"],
                                    ['Measure.[Mtrl Const Type L4_ETDETA] = "' + fbEtdEta + '";',
                                        'Measure.[Mtrl Const Type L4_Time Varying Flag] = "' + fbTimeVarying + '";']);

            if ( fbTimeVarying == "Y" ) {
                vdCommon.createMeasure(["[Version].[Version Name].[" + fbVersion + "]",
                                            "[Item Material].[MSL4].[" + fbMSL4 + "]",
                                            "[Relative Week].[Relative Week]"],
                                        ['Measure.[Mtrl Const Type L4 W_Type] = "' + fbConstType + '";',
                                            'Measure.[Mtrl Const Type L4 W_Type.Lock] = False;']);
            } else {
                vdCommon.createMeasure(["[Version].[Version Name].[" + fbVersion + "]",
                                            "[Item Material].[MSL4].[" + fbMSL4 + "]",
                                            "[Relative Week].[Relative Week].[W01]"],
                                        ['Measure.[Mtrl Const Type L4 W_Type] = "' + fbConstType + '";',
                                            'Measure.[Mtrl Const Type L4 W_Type.Lock] = False;']);

                vdCommon.createMeasure(["[Version].[Version Name].[" + fbVersion + "]",
                                            "[Item Material].[MSL4].[" + fbMSL4 + "]",
                                            '[Relative Week].[Relative Week].filter(#.Name != "W01")'],
                                        ['Measure.[Mtrl Const Type L4 W_Type] = "-";',
                                            'Measure.[Mtrl Const Type L4 W_Type.Lock] = True;']);
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
                                        "[Item Material].[MSL4].[" + row.MSL4.Value + "]"],
                                    ["Measure.[Mtrl Const Type L4_Time Varying Flag]"],
                                    "",
                                    "",
                                    "");

                if ( result.cs.rowCount > 0 && result.cs.row(0).cell(result.cs.measureColumnIndex("Mtrl Const Type L4_Time Varying Flag")) == "Y" ) {
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
                                            "[Item Material].[MSL4].[" + row.MSL4.Value + "]"],
                                        ['Measure.[Mtrl Const Type L4_Time Varying Flag] = "Y";']);

                vdCommon.updateMeasure(["[Version].[Version Name].[" + fbVersion + "]",
                                            "[Item Material].[MSL4].[" + row.MSL4.Value + "]",
                                            "[Relative Week].[Relative Week]"],
                                        ['Measure.[Mtrl Const Type L4 W_Type.Lock] = False;',
                                            'Measure.[Mtrl Const Type L4 W_Type] = "Soft";']);
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
                                        "[Item Material].[MSL4].[" + row.MSL4.Value + "]"],
                                    ["Measure.[Mtrl Const Type L4_Time Varying Flag]"],
                                    "",
                                    "",
                                    "");

                if ( result.cs.rowCount > 0 && result.cs.row(0).cell(result.cs.measureColumnIndex("Mtrl Const Type L4_Time Varying Flag")) == "N" ) {
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
                                            "[Item Material].[MSL4].[" + row.MSL4.Value + "]"],
                                        ['Measure.[Mtrl Const Type L4_Time Varying Flag] = "N";']);

                vdCommon.updateMeasure(["[Version].[Version Name].[" + fbVersion + "]",
                                            "[Item Material].[MSL4].[" + row.MSL4.Value + "]",
                                            "[Relative Week].[Relative Week].[W01]"],
                                        ['Measure.[Mtrl Const Type L4 W_Type.Lock] = False;']);

                vdCommon.updateMeasure(["[Version].[Version Name].[" + fbVersion + "]",
                                            "[Item Material].[MSL4].[" + row.MSL4.Value + "]",
                                            '[Relative Week].[Relative Week].filter(#.Name != "W01")'],
                                        ['Measure.[Mtrl Const Type L4 W_Type.Lock] = True;',
                                            'Measure.[Mtrl Const Type L4 W_Type] = "-";']);
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
                                        "[Item Material].[MSL4].[" + row.MSL4.Value + "]"],
                                    ["Measure.[Mtrl Const Type L4_ETDETA]"],
                                    "",
                                    "",
                                    "");

                if ( result.cs.rowCount > 0 && result.cs.row(0).cell(result.cs.measureColumnIndex("Mtrl Const Type L4_ETDETA")) == "ETD" ) {
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
                                            "[Item Material].[MSL4].[" + row.MSL4.Value + "]"],
                                        ['Measure.[Mtrl Const Type L4_ETDETA] = "ETD";']);
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
                                        "[Item Material].[MSL4].[" + row.MSL4.Value + "]"],
                                    ["Measure.[Mtrl Const Type L4_ETDETA]"],
                                    "",
                                    "",
                                    "");

                if ( result.cs.rowCount > 0 && result.cs.row(0).cell(result.cs.measureColumnIndex("Mtrl Const Type L4_ETDETA")) == "ETA" ) {
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
                                            "[Item Material].[MSL4].[" + row.MSL4.Value + "]"],
                                        ['Measure.[Mtrl Const Type L4_ETDETA] = "ETA";']);
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
                where.push("[Item Material].[MSL4].[" + row.MSL4.Value + "]");

                vdCommon.deleteMeasure(where, "Mtrl Const Type L4");
                vdCommon.deleteMeasure(where, "Mtrl Const Type L4 W");
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
                                        "[Item Material].[MSL4].[" + row.MSL4.Value + "]"],
                                    ["Measure.[Mtrl Const Type L4_Time Varying Flag]",
                                        "Measure.[Mtrl Const Type L4_ETDETA]"],
                                    "",
                                    "",
                                    "");
                if ( result.cs.rowCount > 0 ) {
                    flag = result.cs.row(0).cell(result.cs.measureColumnIndex("Mtrl Const Type L4_Time Varying Flag"));
                    vdCommon.debug("flag : " + flag);

                    if ( fbFlag == "Y" && flag != "Y" ) {
                        vdCommon.createMeasure(["[Version].[Version Name].[" + fbVersion + "]",
                                                    "[Item Material].[MSL4].[" + row.MSL4.Value + "]"],
                                                ['Measure.[Mtrl Const Type L4_Time Varying Flag] = "Y";']);

                        vdCommon.createMeasure(["[Version].[Version Name].[" + fbVersion + "]",
                                                    "[Item Material].[MSL4].[" + row.MSL4.Value + "]",
                                                    "[Relative Week].[Relative Week]"],
                                                ['Measure.[Mtrl Const Type L4 W_Type.Lock] = False;',
                                                    'Measure.[Mtrl Const Type L4 W_Type] = "Soft";']);
                    } else if ( fbFlag == "N" && flag != "N" ) {
                        vdCommon.createMeasure(["[Version].[Version Name].[" + fbVersion + "]",
                                                    "[Item Material].[MSL4].[" + row.MSL4.Value + "]"],
                                                ['Measure.[Mtrl Const Type L4_Time Varying Flag] = "N";']);

                        vdCommon.createMeasure(["[Version].[Version Name].[" + fbVersion + "]",
                                                    "[Item Material].[MSL4].[" + row.MSL4.Value + "]",
                                                    "[Relative Week].[Relative Week].[W01]"],
                                                ['Measure.[Mtrl Const Type L4 W_Type.Lock] = False;']);

                        vdCommon.createMeasure(["[Version].[Version Name].[" + fbVersion + "]",
                                                    "[Item Material].[MSL4].[" + row.MSL4.Value + "]",
                                                    '[Relative Week].[Relative Week].filter(#.Name != "W01")'],
                                                ['Measure.[Mtrl Const Type L4 W_Type.Lock] = True;',
                                                    'Measure.[Mtrl Const Type L4 W_Type] = "-";']);
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
                                        "[Item Material].[MSL4].[" + row.MSL4.Value + "]"],
                                    ["Measure.[Mtrl Const Type L4_Time Varying Flag]",
                                        "Measure.[Mtrl Const Type L4_ETDETA]"],
                                    "",
                                    "",
                                    "");
                if ( result.cs.rowCount > 0 ) {
                    flag = result.cs.row(0).cell(result.cs.measureColumnIndex("Mtrl Const Type L4_ETDETA"));
                    vdCommon.debug("flag : " + flag);

                    if ( fbFlag == "ETD" && flag != "ETD" ) {
                        vdCommon.createMeasure(["[Version].[Version Name].[" + fbVersion + "]",
                                                    "[Item Material].[MSL4].[" + row.MSL4.Value + "]"],
                                                ['Measure.[Mtrl Const Type L4_ETDETA] = "ETD";']);
                    } else if ( fbFlag == "ETA" && flag != "ETA" ) {
                        vdCommon.createMeasure(["[Version].[Version Name].[" + fbVersion + "]",
                                                    "[Item Material].[MSL4].[" + row.MSL4.Value + "]"],
                                                ['Measure.[Mtrl Const Type L4_ETDETA] = "ETA";']);
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
        fn_addL4Combo : fn_addL4Combo,
        fn_addEtdEtaCombo : fn_addEtdEtaCombo,
        fn_addTimeVaryingCombo : fn_addTimeVaryingCombo,
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

/**************************** o9.NSCM.JSConstraintTypeL4 ****************************
    2024-12-18 : ...

*********************************************************************/