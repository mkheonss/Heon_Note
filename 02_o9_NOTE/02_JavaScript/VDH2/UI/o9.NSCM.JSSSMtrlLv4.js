define('o9.NSCM.JSSSMtrlLv4', ['o9/data/query', 'o9/data/cellset', 'o9.NSCM.commonLib'], function () {
    const programName = "o9.NSCM.JSSSMtrlLv4";

    var fn_addCombo = function(o9Params){
        const commonLib = require('o9.NSCM.commonLib');
        const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
        vdCommon.setLogLevel("Debug");

        try {
            vdCommon.printParams(o9Params);

            // 파라미터 가져오기
            var parsedParams = JSON.parse(o9Params);

            // MSL4 에 있는 데이타를 가져온다.
            var rExistMsl4 = vdCommon.selectList(
                                ["&CWVUI",
                                    "[Item Material].[MSL4]",
                                    "[Location].[Location]"],
                                ["Measure.[SS Mtrl L4_Source]"],
                                "",
                                "",
                                "");
            var validHm = {};
            for ( var i = 0; i < rExistMsl4.cs.rowCount; i++ ) {
                msl4 = rExistMsl4.cs.row(i).cell(rExistMsl4.cs.memberColumnIndex("Item Material", "MSL4")).Name;

                if ( validHm[msl4] == undefined ) {
                    validHm[msl4] = msl4;
                }
            }
            vdCommon.debug("validHm : " + JSON.stringify(validHm));

            // 등록되지 않은 MSL4의 데이타로 콤보를 구성한다.
            var comboList = [];
            var rMsl3 = vdCommon.selectList(
                                ["&CWVUI",
                                    "[Item Material].[MSL3]"],
                                ["Measure.[SS Mtrl L3_Sub Set]"],
                                'where {Measure.[SS Mtrl L3_Sub Set] == "Lv4"}',
                                "",
                                "");
            var msl3s = "";
            for ( var i = 0; i < rMsl3.cs.rowCount; i++ ) {
                msl = rMsl3.cs.row(i).cell(rMsl3.cs.memberColumnIndex("Item Material", "MSL3")).Name;

                if ( i == 0 ) {
                    msl3s = '"' + msl + '"';
                } else {
                    msl3s += ',"' + msl + '"';
                }
            }

            var rMSL4 = vdCommon.selectList(
                            ['[Item Material].[MSL3].filter(#.Name in {' + msl3s + '})',
                                "&NSUIMtrlMSL4View"],
                            [],
                            "",
                            "",
                            "");
            for ( var m = 0; m < rMSL4.cs.rowCount; m++ ) {
                MSL4 = rMSL4.cs.row(m).cell(rMSL4.cs.memberColumnIndex("Item Material", "MSL4")).Name;
                if ( validHm[MSL4] == undefined ) {
                    comboList.push({ Name : MSL4, DisplayName : MSL4});
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

    var fn_add = function(o9Params){
        const commonLib = require('o9.NSCM.commonLib');
        const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
        vdCommon.setLogLevel("Debug");

        try {
            vdCommon.printParams(o9Params);

            // 파라미터 가져오기
            var parsedParams = JSON.parse(o9Params);
            var fbMSL4 = parsedParams.fbMSL4;

            var result = vdCommon.selectList(
                                        ["&NSUILocationMFMtrlView"],
                                        [],
                                        //'where { &CWVUI, [Item Material].[MSL4].[' + fbMSL4 + '], Measure.[Item Mtrl Site Asn_Cur Status] in {"ACTIVE","PLANNED"} }',
                                        "",
                                        "",
                                        "");
            var locations = "";
            for ( var i = 0; i < result.cs.rowCount; i++ ) {
                location = result.cs.row(i).cell(result.cs.memberColumnIndex("Location", "Location")).Name;
                if ( i == 0 ) {
                    locations = '"' + location + '"';
                } else {
                    locations += ',"' + location + '"';
                }
            }

            if ( locations == "" ) {
                RuleOutputToUI = { Status : 'Error', Message : "There is no location information." };
                rtn = 1;
            } else {
                vdCommon.createMeasure(["&CWVUI",
                                            "[Item Material].[MSL4].[" + fbMSL4 + "]",
                                            '[Location].[Location].filter(#.Name in {' + locations + '})'],
                                        ['Measure.[SS Mtrl L4_Source] = "NSCM";',
                                            'Measure.[SS Mtrl L4_ECP Flag] = "off";',
                                            'Measure.[SS Mtrl L4_Time Varying Flag] = "Y";']);

                vdCommon.createMeasure(["&CWVUI",
                                            "[Item Material].[MSL4].[" + fbMSL4 + "]",
                                            '[Location].[Location].filter(#.Name in {' + locations + '})',
                                            "&MDMHorizon"],
                                        ['Measure.[SS Mtrl L4 W_Time] = Null;']);
            }

            vdCommon.programEnd();
        } catch ( e ) {
            vdCommon.error(e.message);
            RuleOutputToUI = { Status : 'Error', Message : "Js Logic Error : " + e.message };
            return;
        }
    };

    var fn_sourceErpValidation = function(o9Params){
        var rtn = 0; // 에러 없음

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

                var result = vdCommon.selectList(
                                    ["&CWVUI",
                                        "[Item Material].[MSL4].[" + row.MSL4.Value + "]",
                                        "[Location].[Location].[" + row.Location.Value + "]"],
                                    ["Measure.[SS Mtrl L4_Source]",
                                    "Measure.[SS Mtrl L4_Time Varying Flag]"],
                                    "",
                                    "",
                                    "");

                if ( result.cs.row(0).cell(result.cs.measureColumnIndex("SS Mtrl L4_Source")) == "ERP" ) {
                    RuleOutputToUI = { Status : 'Error', Message : "Select the Source value of NSCM" };
                    rtn = 1;
                    break;
                } else if ( result.cs.row(0).cell(result.cs.measureColumnIndex("SS Mtrl L4_Time Varying Flag")) == "Y" ) {
                    RuleOutputToUI = { Status : 'Error', Message : "Change Time Varying to N first" };
                    rtn = 1;
                    break;
                }
            }

            vdCommon.programEnd();
        } catch ( e ) {
            RuleOutputToUI = { Status : 'Error', Message : "Js Logic Error : " + e.message };
            return;
        }

        return rtn;
    };

    var fn_sourceNscmValidation = function(o9Params){
        var rtn = 0; // 에러 없음

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

                var result = vdCommon.selectList(
                                    ["&CWVUI",
                                        "[Item Material].[MSL4].[" + row.MSL4.Value + "]",
                                        "[Location].[Location].[" + row.Location.Value + "]"],
                                    ["Measure.[SS Mtrl L4_Source]",
                                    "Measure.[SS Mtrl L4_Time Varying Flag]"],
                                    "",
                                    "",
                                    "");

                if ( result.cs.row(0).cell(result.cs.measureColumnIndex("SS Mtrl L4_Source")) == "NSCM" ) {
                    RuleOutputToUI = { Status : 'Error', Message : "Select the Source value of ERP" };
                    rtn = 1;
                    break;
                } else if ( result.cs.row(0).cell(result.cs.measureColumnIndex("SS Mtrl L4_Time Varying Flag")) == "Y" ) {
                    RuleOutputToUI = { Status : 'Error', Message : "Change Time Varying to N first" };
                    rtn = 1;
                    break;
                }
            }

            vdCommon.programEnd();
        } catch ( e ) {
            RuleOutputToUI = { Status : 'Error', Message : "Js Logic Error : " + e.message };
            return;
        }

        return rtn;
    };

    var fn_sourceEcpOnValidation = function(o9Params){
        var rtn = 0; // 에러 없음

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

                var result = vdCommon.selectList(
                                    ["&CWVUI",
                                        "[Item Material].[MSL4].[" + row.MSL4.Value + "]",
                                        "[Location].[Location].[" + row.Location.Value + "]"],
                                    ["Measure.[SS Mtrl L4_Source]",
                                    "Measure.[SS Mtrl L4_ECP Flag]"],
                                    "",
                                    "",
                                    "");

                if ( result.cs.row(0).cell(result.cs.measureColumnIndex("SS Mtrl L4_ECP Flag")) == "on" ) {
                    RuleOutputToUI = { Status : 'Error', Message : "Select the ECP value of off" };
                    rtn = 1;
                    break;
                }
            }

            vdCommon.programEnd();
        } catch ( e ) {
            RuleOutputToUI = { Status : 'Error', Message : "Js Logic Error : " + e.message };
            return;
        }

        return rtn;
    };

    var fn_sourceEcpOffValidation = function(o9Params){
        var rtn = 0; // 에러 없음

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

                var result = vdCommon.selectList(
                                    ["&CWVUI",
                                        "[Item Material].[MSL4].[" + row.MSL4.Value + "]",
                                        "[Location].[Location].[" + row.Location.Value + "]"],
                                    ["Measure.[SS Mtrl L4_Source]",
                                    "Measure.[SS Mtrl L4_ECP Flag]"],
                                    "",
                                    "",
                                    "");

                if ( result.cs.row(0).cell(result.cs.measureColumnIndex("SS Mtrl L4_ECP Flag")) == "off" ) {
                    RuleOutputToUI = { Status : 'Error', Message : "Select the ECP value of on" };
                    rtn = 1;
                    break;
                }
            }

            vdCommon.programEnd();
        } catch ( e ) {
            RuleOutputToUI = { Status : 'Error', Message : "Js Logic Error : " + e.message };
            return;
        }

        return rtn;
    };

    var fn_sourceTimeYValidation = function(o9Params){
        var rtn = 0; // 에러 없음

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

                var result = vdCommon.selectList(
                                    ["&CWVUI",
                                        "[Item Material].[MSL4].[" + row.MSL4.Value + "]",
                                        "[Location].[Location].[" + row.Location.Value + "]"],
                                    ["Measure.[SS Mtrl L4_Source]",
                                    "Measure.[SS Mtrl L4_Time Varying Flag]"],
                                    "",
                                    "",
                                    "");

                if ( result.cs.row(0).cell(result.cs.measureColumnIndex("SS Mtrl L4_Time Varying Flag")) == "Y" ) {
                    RuleOutputToUI = { Status : 'Error', Message : "Select the Time Varying value of N" };
                    rtn = 1;
                    break;
                } else if ( result.cs.row(0).cell(result.cs.measureColumnIndex("SS Mtrl L4_Source")) == "ERP" ) {
                    RuleOutputToUI = { Status : 'Error', Message : "Time Varying cannot be modified for data whose source is ERP." };
                    rtn = 1;
                    break;
                }
            }

            vdCommon.programEnd();
        } catch ( e ) {
            RuleOutputToUI = { Status : 'Error', Message : "Js Logic Error : " + e.message };
            return;
        }

        return rtn;
    };

    var fn_sourceTimeNValidation = function(o9Params){
        var rtn = 0; // 에러 없음

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

                var result = vdCommon.selectList(
                                    ["&CWVUI",
                                        "[Item Material].[MSL4].[" + row.MSL4.Value + "]",
                                        "[Location].[Location].[" + row.Location.Value + "]"],
                                    ["Measure.[SS Mtrl L4_Source]",
                                    "Measure.[SS Mtrl L4_Time Varying Flag]"],
                                    "",
                                    "",
                                    "");

                if ( result.cs.row(0).cell(result.cs.measureColumnIndex("SS Mtrl L4_Time Varying Flag")) == "N" ) {
                    RuleOutputToUI = { Status : 'Error', Message : "Select the Time Varying value of Y" };
                    rtn = 1;
                    break;
                } else if ( result.cs.row(0).cell(result.cs.measureColumnIndex("SS Mtrl L4_Source")) == "ERP" ) {
                    RuleOutputToUI = { Status : 'Error', Message : "Time Varying cannot be modified for data whose source is ERP." };
                    rtn = 1;
                    break;
                }
            }

            vdCommon.programEnd();
        } catch ( e ) {
            RuleOutputToUI = { Status : 'Error', Message : "Js Logic Error : " + e.message };
            return;
        }

        return rtn;
    };

    var fn_sourceNscmChange = function(o9Params){
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

                var result = vdCommon.selectList(
                                    ["&CWVUI",
                                        "[Item Material].[MSL4].[" + row.MSL4.Value + "]",
                                        "[Location].[Location].[" + row.Location.Value + "]"],
                                    ["Measure.[SS Mtrl L4_Source]"],
                                    "",
                                    "",
                                    "");
                if ( result.cs.rowCount > 0 && result.cs.row(0).cell(result.cs.measureColumnIndex("SS Mtrl L4_Source")) == "ERP" ) {
                    vdCommon.updateMeasure(["&CWVUI",
                                                "[Item Material].[MSL4].[" + row.MSL4.Value + "]",
                                                "[Location].[Location].[" + row.Location.Value + "]"],
                                            ['Measure.[SS Mtrl L4_Source] = "NSCM";',
                                                'Measure.[SS Mtrl L4_Time Varying Flag] = "N";']);

                    vdCommon.createMeasure(["&CWVUI",
                                                "[Item Material].[MSL4].[" + row.MSL4.Value + "]",
                                                "[Location].[Location].[" + row.Location.Value + "]",
                                                "[Time].[Week].filter(#.Key == &CurrentWeek.element(0).Key)"],
                                            ['Measure.[SS Mtrl L4 W_Time.Lock] = False;']);

                    vdCommon.createMeasure(["&CWVUI",
                                                "[Item Material].[MSL4].[" + row.MSL4.Value + "]",
                                                "[Location].[Location].[" + row.Location.Value + "]",
                                                "&MDMHorizon.filter(#.Key > &CurrentWeek.element(0).Key)"],
                                            ['Measure.[SS Mtrl L4 W_Time.Lock] = True;',
                                                'Measure.[SS Mtrl L4 W_Time] = Null;']);
                }
            }

            vdCommon.programEnd();
        } catch ( e ) {
            vdCommon.error(e.message);
            RuleOutputToUI = { Status : 'Error', Message : "Js Logic Error : " + e.message };
            return;
        }
    };

    var fn_sourceErpChange = function(o9Params){
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

                var result = vdCommon.selectList(
                                    ["&CWVUI",
                                        "[Item Material].[MSL4].[" + row.MSL4.Value + "]",
                                        "[Location].[Location].[" + row.Location.Value + "]"],
                                    ["Measure.[SS Mtrl L4_Source]"],
                                    "",
                                    "",
                                    "");
                if ( result.cs.rowCount > 0 && result.cs.row(0).cell(result.cs.measureColumnIndex("SS Mtrl L4_Source")) == "NSCM" ) {
                    vdCommon.createMeasure(["&CWVUI",
                                                "[Item Material].[MSL4].[" + row.MSL4.Value + "]",
                                                "[Location].[Location].[" + row.Location.Value + "]"],
                                            ['Measure.[SS Mtrl L4_Source] = "ERP";',
                                                'Measure.[SS Mtrl L4_Time Varying Flag] = "N";']);

                    vdCommon.createMeasure(["&CWVUI",
                                                "[Item Material].[MSL4].[" + row.MSL4.Value + "]",
                                                "[Location].[Location].[" + row.Location.Value + "]",
                                                "&MDMHorizon"],
                                            ['Measure.[SS Mtrl L4 W_Time.Lock] = True;',
                                                'Measure.[SS Mtrl L4 W_Time] = Null;']);
                }
            }

            vdCommon.programEnd();
        } catch ( e ) {
            vdCommon.error(e.message);
            RuleOutputToUI = { Status : 'Error', Message : "Js Logic Error : " + e.message };
            return;
        }
    };

    var fn_sourceTimeYChange = function(o9Params){
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

                vdCommon.updateMeasure(["&CWVUI",
                                            "[Item Material].[MSL4].[" + row.MSL4.Value + "]",
                                            "[Location].[Location].[" + row.Location.Value + "]"],
                                        ['Measure.[SS Mtrl L4_Time Varying Flag] = "Y";']);

                vdCommon.createMeasure(["&CWVUI",
                                            "[Item Material].[MSL4].[" + row.MSL4.Value + "]",
                                            "[Location].[Location].[" + row.Location.Value + "]",
                                            "&MDMHorizon"],
                                        ['Measure.[SS Mtrl L4 W_Time.Lock] = True;']);
            }

            vdCommon.programEnd();
        } catch ( e ) {
            vdCommon.error(e.message);
            RuleOutputToUI = { Status : 'Error', Message : "Js Logic Error : " + e.message };
            return;
        }
    };

    var fn_sourceTimeNChange = function(o9Params){
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

                vdCommon.updateMeasure(["&CWVUI",
                                            "[Item Material].[MSL4].[" + row.MSL4.Value + "]",
                                            "[Location].[Location].[" + row.Location.Value + "]"],
                                        ['Measure.[SS Mtrl L4_Time Varying Flag] = "N";']);

                vdCommon.createMeasure(["&CWVUI",
                                            "[Item Material].[MSL4].[" + row.MSL4.Value + "]",
                                            "[Location].[Location].[" + row.Location.Value + "]",
                                            "[Time].[Week].filter(#.Key == &CurrentWeek.element(0).Key)"],
                                        ['Measure.[SS Mtrl L4 W_Time.Lock] = False;']);

                vdCommon.createMeasure(["&CWVUI",
                                            "[Item Material].[MSL4].[" + row.MSL4.Value + "]",
                                            "[Location].[Location].[" + row.Location.Value + "]",
                                            "&MDMHorizon.filter(#.Key > &CurrentWeek.element(0).Key)"],
                                        ['Measure.[SS Mtrl L4 W_Time.Lock] = True;',
                                            'Measure.[SS Mtrl L4 W_Time] = Null;']);
            }

            vdCommon.programEnd();
        } catch ( e ) {
            vdCommon.error(e.message);
            RuleOutputToUI = { Status : 'Error', Message : "Js Logic Error : " + e.message };
            return;
        }
    };

    var fn_sourceEcpOnChange = function(o9Params){
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

                vdCommon.updateMeasure(["&CWVUI",
                                            "[Item Material].[MSL4].[" + row.MSL4.Value + "]",
                                            "[Location].[Location].[" + row.Location.Value + "]"],
                                        ['Measure.[SS Mtrl L4_ECP Flag] = "on";']);
            }

            vdCommon.programEnd();
        } catch ( e ) {
            vdCommon.error(e.message);
            RuleOutputToUI = { Status : 'Error', Message : "Js Logic Error : " + e.message };
            return;
        }
    };

    var fn_sourceEcpOffChange = function(o9Params){
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

                vdCommon.updateMeasure(["&CWVUI",
                                            "[Item Material].[MSL4].[" + row.MSL4.Value + "]",
                                            "[Location].[Location].[" + row.Location.Value + "]"],
                                        ['Measure.[SS Mtrl L4_ECP Flag] = "off";']);
            }

            vdCommon.programEnd();
        } catch ( e ) {
            vdCommon.error(e.message);
            RuleOutputToUI = { Status : 'Error', Message : "Js Logic Error : " + e.message };
            return;
        }
    };

    var fn_ditto = function(o9Params){
        const commonLib = require('o9.NSCM.commonLib');
        const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
        const vdUtil = new commonLib.VdUtil();

        try {
            vdCommon.setLogLevel("Debug");

            vdCommon.printParams(o9Params);

            // 파라미터 가져오기
            var parsedParams = JSON.parse(o9Params);
            var fbSelect = parsedParams.fbSelect;

            for ( var i = 0; i < fbSelect.length; i++ ) {
                var row = fbSelect[i];

                // 들어 있는 데이타로 HashMap 을 만든다.
                var result = vdCommon.selectList(
                                    ["&CWVUI",
                                        "[Location].[Location].[" + row.Location.Value + "]",
                                        "[Item Material].[MSL4].[" + row.MSL4.Value + "]",
                                        "&MDMHorizon"],
                                    ["Measure.[SS Mtrl L4 W_Time]",
                                        "Measure.[SS Mtrl L4_Source]",
                                        "Measure.[SS Mtrl L4_Time Varying Flag]"],
                                    "",
                                    "orderby Time.[Week].DisplayName",
                                    "");
                vdCommon.printCsData(result, 3);

                if ( result.cs.rowCount > 0 &&
                        result.cs.row(0).cell(result.cs.measureColumnIndex("SS Mtrl L4_Source")) == "NSCM" &&
                        result.cs.row(0).cell(result.cs.measureColumnIndex("SS Mtrl L4_Time Varying Flag")) == "Y" ) {
                    // 주차별 hm 데이타를 만든다.
                    var hm = {}
                    var value = 0;
                    var week = "";
                    for ( var m = 0; m < result.cs.rowCount; m++ ) {
                        week = result.cs.row(m).cell(result.cs.memberColumnIndex("Time", "Week")).Name;
                        value = result.cs.row(m).cell(result.cs.measureColumnIndex("SS Mtrl L4 W_Time"));

                        hm[week] = value;
                    }
                    vdCommon.debug("ComboData : " + JSON.stringify(hm));

                    // 주차를 기준으로 ditto 를 수행한다.
                    result = vdCommon.selectList(["&MDMHorizon"], [], "", "", "");
                    var lastValue = 0;
                    var queryStr = "";
                    for ( var m = 0; m < result.cs.rowCount; m++ ) {
                        week = result.cs.row(m).cell(result.cs.memberColumnIndex("Time", "Week")).Name;

                        if ( hm[week] == undefined ) {
                            value = 0;
                        } else {
                            value = hm[week];
                        }

                        if ( m == 0 ) {
                            lastValue = value;
                        } else if ( value == 0 || value == undefined ) {
                            queryStr += vdCommon.createMeasureQuery(["&CWVUI",
                                                                        "[Location].[Location].[" + row.Location.Value + "]",
                                                                        "[Time].[Week].[" + week + "]",
                                                                        "[Item Material].[MSL4].[" + row.MSL4.Value + "]"],
                                                                     ['Measure.[SS Mtrl L4 W_Time] = ' + lastValue + ';']);
                        } else {
                            lastValue = value;
                        }
                    }

                    if ( queryStr != "" ) {
                        vdCommon.executeQuery("Batch Query" , queryStr);
                    }
                }
            }

            vdCommon.programEnd();
        } catch ( e ) {
            RuleOutputToUI = { Status : 'Error', Message : "Js Logic Error : " + e.message };
            return;
        }
    };

    var fn_sourceCombo = function(o9Params){
        const commonLib = require('o9.NSCM.commonLib');
        const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
        vdCommon.setLogLevel("Debug");

        try {
            var comboList = vdCommon.fn_makeCombo(null, {ComboCodes : ["ERP","NSCM"], ComboValues : ["ERP","NSCM"]});
            vdCommon.debug("ComboData : " + JSON.stringify(comboList));

            vdCommon.programEnd();

            return comboList;
        } catch ( e ) {
            vdCommon.error(e.message);
            RuleOutputToUI = { Status : 'Error', Message : "Js Logic Error : " + e.message };
            return;
        }
    };

    var fn_ecpCombo = function(o9Params){
        const commonLib = require('o9.NSCM.commonLib');
        const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
        vdCommon.setLogLevel("Debug");

        try {
            var comboList = vdCommon.fn_makeCombo(null, {ComboCodes : ["on","off"], ComboValues : ["on","off"]});
            vdCommon.debug("ComboData : " + JSON.stringify(comboList));

            vdCommon.programEnd();

            return comboList;
        } catch ( e ) {
            vdCommon.error(e.message);
            RuleOutputToUI = { Status : 'Error', Message : "Js Logic Error : " + e.message };
            return;
        }
    };

    var fn_timeVaryingCombo = function(o9Params){
        const commonLib = require('o9.NSCM.commonLib');
        const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
        vdCommon.setLogLevel("Debug");

        try {
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

    var fn_sourceChange = function(o9Params){
        const commonLib = require('o9.NSCM.commonLib');
        const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
        vdCommon.setLogLevel("Debug");

        try {
            vdCommon.printParams(o9Params);

            // 파라미터 가져오기
            var parsedParams = JSON.parse(o9Params);
            var fbSelect = parsedParams.fbSelect;
            var fbFlag = parsedParams.fbFlag;
            var fbQty = parsedParams.fbQty;
            var flag = "";

            for ( var i = 0; i < fbSelect.length; i++ ) {
                var row = fbSelect[i];

                var result = vdCommon.selectList(
                                    ["&CWVUI",
                                        "[Item Material].[MSL4].[" + row.MSL4.Value + "]",
                                        "[Location].[Location].[" + row.Location.Value + "]"],
                                    ["Measure.[SS Mtrl L4_Source]"],
                                    "",
                                    "",
                                    "");
                if ( result.cs.rowCount > 0 ) {
                    flag = result.cs.row(0).cell(result.cs.measureColumnIndex("SS Mtrl L4_Source"));
                    vdCommon.debug("flag : " + flag);

                    if ( fbFlag == "NSCM" && flag != "NSCM" ) {
                        vdCommon.updateMeasure(["&CWVUI",
                                                    "[Item Material].[MSL4].[" + row.MSL4.Value + "]",
                                                    "[Location].[Location].[" + row.Location.Value + "]"],
                                                ['Measure.[SS Mtrl L4_Source] = "NSCM";',
                                                    'Measure.[SS Mtrl L4_Time Varying Flag] = "Y";']);

                        vdCommon.createMeasure(["&CWVUI",
                                                    "[Item Material].[MSL4].[" + row.MSL4.Value + "]",
                                                    "[Location].[Location].[" + row.Location.Value + "]",
                                                    "&MDMHorizon"],
                                                ['Measure.[SS Mtrl L4 W_Time.Lock] = False;',
                                                    'Measure.[SS Mtrl L4 W_Time] = ' + fbQty + ';']);
                    } else if ( fbFlag == "ERP" && flag != "ERP" ) {
                        vdCommon.updateMeasure(["&CWVUI",
                                                    "[Item Material].[MSL4].[" + row.MSL4.Value + "]",
                                                    "[Location].[Location].[" + row.Location.Value + "]"],
                                                ['Measure.[SS Mtrl L4_Source] = "ERP";',
                                                    'Measure.[SS Mtrl L4_Time Varying Flag] = "N";']);

                        vdCommon.createMeasure(["&CWVUI",
                                                    "[Item Material].[MSL4].[" + row.MSL4.Value + "]",
                                                    "[Location].[Location].[" + row.Location.Value + "]",
                                                    "&MDMHorizon"],
                                                ['Measure.[SS Mtrl L4 W_Time.Lock] = False;',
                                                    'Measure.[SS Mtrl L4 W_Time] = Null;']);
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

    var fn_ecpChange = function(o9Params){
        const commonLib = require('o9.NSCM.commonLib');
        const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
        vdCommon.setLogLevel("Debug");

        try {
            vdCommon.printParams(o9Params);

            // 파라미터 가져오기
            var parsedParams = JSON.parse(o9Params);
            var fbSelect = parsedParams.fbSelect;
            var fbFlag = parsedParams.fbFlag;
            var flag = "";

            for ( var i = 0; i < fbSelect.length; i++ ) {
                var row = fbSelect[i];

                var result = vdCommon.selectList(
                                    ["&CWVUI",
                                        "[Item Material].[MSL4].[" + row.MSL4.Value + "]",
                                        "[Location].[Location].[" + row.Location.Value + "]"],
                                    ["Measure.[SS Mtrl L4_ECP Flag]"],
                                    "",
                                    "",
                                    "");
                if ( result.cs.rowCount > 0 ) {
                    flag = result.cs.row(0).cell(result.cs.measureColumnIndex("SS Mtrl L4_ECP Flag"));
                    vdCommon.debug("flag : " + flag);

                    if ( fbFlag == "on" && flag != "on" ) {
                        vdCommon.updateMeasure(["&CWVUI",
                                                    "[Item Material].[MSL4].[" + row.MSL4.Value + "]",
                                                    "[Location].[Location].[" + row.Location.Value + "]"],
                                                ['Measure.[SS Mtrl L4_ECP Flag] = "on";']);
                    } else if ( fbFlag == "off" && flag != "off" ) {
                        vdCommon.updateMeasure(["&CWVUI",
                                                    "[Item Material].[MSL4].[" + row.MSL4.Value + "]",
                                                    "[Location].[Location].[" + row.Location.Value + "]"],
                                                ['Measure.[SS Mtrl L4_ECP Flag] = "off";']);
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

    var fn_timeVaryingChange = function(o9Params){
        const commonLib = require('o9.NSCM.commonLib');
        const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
        vdCommon.setLogLevel("Debug");

        try {
            vdCommon.printParams(o9Params);

            // 파라미터 가져오기
            var parsedParams = JSON.parse(o9Params);
            var fbSelect = parsedParams.fbSelect;
            var fbFlag = parsedParams.fbFlag;
            var flag = "";
            var source = "";

            for ( var i = 0; i < fbSelect.length; i++ ) {
                var row = fbSelect[i];

                var result = vdCommon.selectList(
                                    ["&CWVUI",
                                        "[Item Material].[MSL4].[" + row.MSL4.Value + "]",
                                        "[Location].[Location].[" + row.Location.Value + "]"],
                                    ["Measure.[SS Mtrl L4_Time Varying Flag]",
                                        "Measure.[SS Mtrl L4_Source]"],
                                    "",
                                    "",
                                    "");
                if ( result.cs.rowCount > 0 ) {
                    flag = result.cs.row(0).cell(result.cs.measureColumnIndex("SS Mtrl L4_Time Varying Flag"));
                    source = result.cs.row(0).cell(result.cs.measureColumnIndex("SS Mtrl L4_Source"));
                    vdCommon.debug("flag : " + flag + ", source : " + source);

                    if ( source == "NSCM" && fbFlag == "Y" && flag != "Y" ) {
                        vdCommon.createMeasure(["&CWVUI",
                                                    "[Item Material].[MSL4].[" + row.MSL4.Value + "]",
                                                    "[Location].[Location].[" + row.Location.Value + "]"],
                                                ['Measure.[SS Mtrl L4_Time Varying Flag] = "Y";']);

                        var qty = null;
                        var resultFirst = vdCommon.selectList(["&CWVUI",
                                                                    "[Item Material].[MSL4].[" + row.MSL4.Value + "]",
                                                                    "[Location].[Location].[" + row.Location.Value + "]",
                                                                    "[Time].[Week].filter(#.Key == &CurrentWeek.element(0).Key)"],
                                                              ["Measure.[SS Mtrl L4 W_Time]"],
                                                              "",
                                                              "",
                                                              "");
                        if ( resultFirst.cs.rowCount > 0 ) {
                            qty = resultFirst.cs.row(0).cell(resultFirst.cs.measureColumnIndex("SS Mtrl L4 W_Time"));
                        }

                        vdCommon.createMeasure(["&CWVUI",
                                                    "[Item Material].[MSL4].[" + row.MSL4.Value + "]",
                                                    "[Location].[Location].[" + row.Location.Value + "]",
                                                    "&MDMHorizon"],
                                                ['Measure.[SS Mtrl L4 W_Time.Lock] = False;',
                                                    'Measure.[SS Mtrl L4 W_Time] = ' + qty + ';']);
                    } else if ( source == "NSCM" && fbFlag == "N" && flag != "N" ) {
                        vdCommon.createMeasure(["&CWVUI",
                                                    "[Item Material].[MSL4].[" + row.MSL4.Value + "]",
                                                    "[Location].[Location].[" + row.Location.Value + "]"],
                                                ['Measure.[SS Mtrl L4_Time Varying Flag] = "N";']);

                        vdCommon.createMeasure(["&CWVUI",
                                                    "[Item Material].[MSL4].[" + row.MSL4.Value + "]",
                                                    "[Location].[Location].[" + row.Location.Value + "]",
                                                    '&MDMHorizon.filter(#.Key > &CurrentWeek.element(0).Key)'],
                                                ['Measure.[SS Mtrl L4 W_Time.Lock] = False;',
                                                    'Measure.[SS Mtrl L4 W_Time] = Null;']);
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

    var fn_ditto_V2 = function(o9Params){
        // 2025.4.16 : Ditto 기능 수정
        const commonLib = require('o9.NSCM.commonLib');
        const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
        const vdUtil = new commonLib.VdUtil();
        vdCommon.setLogLevel("Debug");

        try {
            vdCommon.printParams(o9Params);

            // 파라미터 가져오기
            var parsedParams = JSON.parse(o9Params);
            var fbSelect = parsedParams.fbSelect;
            var fbWeek = parsedParams.fbWeek.split(",");
            var fbFromWeek = parsedParams.fbFromWeek;
            var fbToWeek = parsedParams.fbToWeek;
            var fbValue = parsedParams.fbValue;

            for ( var i = 0; i < fbSelect.length; i++ ) {
                var row = fbSelect[i];

                // 들어 있는 데이타로 HashMap 을 만든다.
                var result = vdCommon.selectList(
                                    ["&CWVUI",
                                        "[Location].[Location].[" + row.Location.Value + "]",
                                        "[Item Material].[MSL4].[" + row.MSL4.Value + "]",
                                        '[Time].[Week].filter(#.Name >= "' + fbFromWeek + '" && #.Name <= "' + fbToWeek + '")'],
                                    ["Measure.[SS Mtrl L4 W_Time]",
                                        "Measure.[SS Mtrl L4 W_Time.Lock]",
                                        "Measure.[SS Mtrl L4_Source]",
                                        "Measure.[SS Mtrl L4_Time Varying Flag]"],
                                    "",
                                    "orderby Time.[Week].DisplayName",
                                    "");
                vdCommon.printCsData(result, 3);

                if ( result.cs.rowCount > 0 &&
                        result.cs.row(0).cell(result.cs.measureColumnIndex("SS Mtrl L4_Source")) == "NSCM" &&
                        result.cs.row(0).cell(result.cs.measureColumnIndex("SS Mtrl L4_Time Varying Flag")) == "Y" ) {
                    var queryStr = vdCommon.createMeasureQuery(["&CWVUI",
                                                                    "[Location].[Location].[" + row.Location.Value + "]",
                                                                    "[Item Material].[MSL4].[" + row.MSL4.Value + "]",
                                                                    '[Time].[Week].filter(#.Name >= "' + fbFromWeek + '" && #.Name <= "' + fbToWeek + '")'],
                                                                 ['Measure.[SS Mtrl L4 W_Time] = ' + fbValue + ';']);
                    vdCommon.executeQuery("Batch Query" , queryStr);
                } else if ( result.cs.rowCount > 0 &&
                        result.cs.row(0).cell(result.cs.measureColumnIndex("SS Mtrl L4_Source")) == "NSCM" &&
                        result.cs.row(0).cell(result.cs.measureColumnIndex("SS Mtrl L4_Time Varying Flag")) == "N" &&
                        result.cs.row(0).cell(result.cs.measureColumnIndex("SS Mtrl L4 W_Time.Lock")) != true ) {
                    var queryStr = vdCommon.createMeasureQuery(["&CWVUI",
                                                                    "[Location].[Location].[" + row.Location.Value + "]",
                                                                    "[Item Material].[MSL4].[" + row.MSL4.Value + "]",
                                                                    '[Time].[Week].[' + result.cs.row(0).cell(result.cs.memberColumnIndex("Time", "Week")).Name + ']'],
                                                                 ['Measure.[SS Mtrl L4 W_Time] = ' + fbValue + ';']);
                    vdCommon.executeQuery("Batch Query" , queryStr);
                }
            }

            vdCommon.programEnd();
        } catch ( e ) {
            RuleOutputToUI = { Status : 'Error', Message : "Js Logic Error : " + e.message };
            return;
        }
    };

    var fn_ditto_V2 = function(o9Params){
        // 2025.4.16 : Ditto 기능 수정
        const commonLib = require('o9.NSCM.commonLib');
        const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
        const vdUtil = new commonLib.VdUtil();

        try {
            vdCommon.setLogLevel("Debug");

            vdCommon.printParams(o9Params);

            // 파라미터 가져오기
            var parsedParams = JSON.parse(o9Params);
            var fbSelect = parsedParams.fbSelect;
            var fbWeek = parsedParams.fbWeek.split(",");
            var fbFromWeek = parsedParams.fbFromWeek;
            var fbToWeek = parsedParams.fbToWeek;
            var fbValue = parsedParams.fbValue;

            if ( fbToWeek == null ) {
                fbToWeek = fbWeek[fbWeek.length - 1];
            }

            for ( var i = 0; i < fbSelect.length; i++ ) {
                var row = fbSelect[i];

                // 들어 있는 데이타로 HashMap 을 만든다.
                var result = vdCommon.selectList(
                                    ["&CWVUI",
                                        "[Location].[Location].[" + row.Location.Value + "]",
                                        "[Item Material].[MSL4].[" + row.MSL4.Value + "]",
                                        '[Time].[Week].filter(#.Name >= "' + fbFromWeek + '" && #.Name <= "' + fbToWeek + '")'],
                                    ["Measure.[SS Mtrl L4 W_Time]",
                                        "Measure.[SS Mtrl L4 W_Time.Lock]",
                                        "Measure.[SS Mtrl L4_Source]",
                                        "Measure.[SS Mtrl L4_Time Varying Flag]"],
                                    "",
                                    "orderby Time.[Week].DisplayName",
                                    "");
                //vdCommon.printCsData(result, 3);

                if ( result.cs.rowCount > 0 &&
                        result.cs.row(0).cell(result.cs.measureColumnIndex("SS Mtrl L4_Source")) == "NSCM" &&
                        result.cs.row(0).cell(result.cs.measureColumnIndex("SS Mtrl L4_Time Varying Flag")) == "Y" ) {
                    var queryStr = vdCommon.createMeasureQuery(["&CWVUI",
                                                                    "[Location].[Location].[" + row.Location.Value + "]",
                                                                    "[Item Material].[MSL4].[" + row.MSL4.Value + "]",
                                                                    '[Time].[Week].filter(#.Name >= "' + fbFromWeek + '" && #.Name <= "' + fbToWeek + '")'],
                                                                 ['Measure.[SS Mtrl L4 W_Time] = ' + fbValue + ';']);
                    vdCommon.executeQuery("Batch Query" , queryStr);
                } else if ( result.cs.rowCount > 0 &&
                        result.cs.row(0).cell(result.cs.measureColumnIndex("SS Mtrl L4_Source")) == "NSCM" &&
                        result.cs.row(0).cell(result.cs.measureColumnIndex("SS Mtrl L4_Time Varying Flag")) == "N" &&
                        result.cs.row(0).cell(result.cs.measureColumnIndex("SS Mtrl L4 W_Time.Lock")) != true ) {
                    var queryStr = vdCommon.createMeasureQuery(["&CWVUI",
                                                                    "[Location].[Location].[" + row.Location.Value + "]",
                                                                    "[Item Material].[MSL4].[" + row.MSL4.Value + "]",
                                                                    '[Time].[Week].[' + result.cs.row(0).cell(result.cs.memberColumnIndex("Time", "Week")).Name + ']'],
                                                                 ['Measure.[SS Mtrl L4 W_Time] = ' + fbValue + ';']);
                    vdCommon.executeQuery("Batch Query" , queryStr);
                }
            }

            vdCommon.programEnd();
        } catch ( e ) {
            RuleOutputToUI = { Status : 'Error', Message : "Js Logic Error : " + e.message };
            return;
        }
    };

    return {
        fn_addCombo : fn_addCombo,
        fn_add : fn_add,
        //fn_sourceErpValidation : fn_sourceErpValidation,
        //fn_sourceNscmValidation, fn_sourceNscmValidation,
        //fn_sourceTimeYValidation : fn_sourceTimeYValidation,
        //fn_sourceTimeNValidation : fn_sourceTimeNValidation,
        //fn_sourceEcpOnValidation : fn_sourceEcpOnValidation,
        //fn_sourceEcpOffValidation : fn_sourceEcpOffValidation,
        //fn_sourceNscmChange : fn_sourceNscmChange,
        //fn_sourceErpChange : fn_sourceErpChange,
        //fn_sourceTimeYChange : fn_sourceTimeYChange,
        //fn_sourceTimeNChange : fn_sourceTimeNChange,
        //fn_sourceEcpOnChange : fn_sourceEcpOnChange,
        //fn_sourceEcpOffChange : fn_sourceEcpOffChange,
        fn_ditto : fn_ditto,
        fn_sourceCombo : fn_sourceCombo,
        fn_ecpCombo : fn_ecpCombo,
        fn_timeVaryingCombo : fn_timeVaryingCombo,
        fn_sourceChange : fn_sourceChange,
        fn_ecpChange : fn_ecpChange,
        fn_timeVaryingChange : fn_timeVaryingChange,
        fn_ditto_V2 : fn_ditto_V2
    };
});

/**************************** o9.NSCM.JSSSMtrlLv4 ****************************
    2025-3-28 : fn_ditto 기능 추가
    2025-04-14 : fn_sourceChange, fn_ecpChange, fn_timeVaryingChange 기능 추가
    2025-04-16 : fn_ditto_V2 기능 추가
*********************************************************************/