define('o9.NSCM.JSSSMtrlLv3', ['o9/data/query', 'o9/data/cellset', 'o9.NSCM.commonLib'], function () {
    const programName = "o9.NSCM.JSSSMtrlLv3";

    var fn_subSetCombo = function(o9Params){
        const commonLib = require('o9.NSCM.commonLib');
        const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
        vdCommon.setLogLevel("Debug");

        try {
            vdCommon.printParams(o9Params);

            // 파라미터 가져오기
            var parsedParams = JSON.parse(o9Params);

            var comboList = [];
            comboList.push({ Name : "Lv4", DisplayName : "Lv4"});
            comboList.push({ Name : "Lv5", DisplayName : "Lv5"});
            comboList.push({ Name : "-", DisplayName : "-"});

            vdCommon.programEnd();

            return comboList;
        } catch ( e ) {
            vdCommon.error(e.message);
            RuleOutputToUI = { Status : 'Error', Message : "Js Logic Error : " + e.message };
            return;
        }
    };

    var fn_subSetChange = function(o9Params){
        const commonLib = require('o9.NSCM.commonLib');
        const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
        vdCommon.setLogLevel("Debug");

        try {
            vdCommon.printParams(o9Params);

            // 파라미터 가져오기
            var parsedParams = JSON.parse(o9Params);
            var fbMSL3 = parsedParams.fbMSL3;
            var fbSubSet = parsedParams.fbSubSet;

            vdCommon.updateMeasure(["&CWVUI",
                                        "[Item Material].[MSL3].[" + fbMSL3 + "]"],
                                    ['Measure.[SS Mtrl L3_Sub Set] = "' + fbSubSet + '";']);

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
                                        "[Item Material].[MSL3].[" + row.MSL3.Value + "]",
                                        "[Location].[Location].[" + row.Location.Value + "]"],
                                    ["Measure.[SS Mtrl L3_Source]",
                                    "Measure.[SS Mtrl L3_Time Varying Flag]"],
                                    "",
                                    "",
                                    "");

                if ( result.cs.row(0).cell(result.cs.measureColumnIndex("SS Mtrl L3_Source")) == "ERP" ) {
                    RuleOutputToUI = { Status : 'Error', Message : "Select the Source value of NSCM" };
                    rtn = 1;
                    break;
                } else if ( result.cs.row(0).cell(result.cs.measureColumnIndex("SS Mtrl L3_Time Varying Flag")) == "Y" ) {
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
                                        "[Item Material].[MSL3].[" + row.MSL3.Value + "]",
                                        "[Location].[Location].[" + row.Location.Value + "]"],
                                    ["Measure.[SS Mtrl L3_Source]",
                                    "Measure.[SS Mtrl L3_Time Varying Flag]"],
                                    "",
                                    "",
                                    "");

                if ( result.cs.row(0).cell(result.cs.measureColumnIndex("SS Mtrl L3_Source")) == "NSCM" ) {
                    RuleOutputToUI = { Status : 'Error', Message : "Select the Source value of ERP" };
                    rtn = 1;
                    break;
                } else if ( result.cs.row(0).cell(result.cs.measureColumnIndex("SS Mtrl L3_Time Varying Flag")) == "Y" ) {
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
                                        "[Item Material].[MSL3].[" + row.MSL3.Value + "]",
                                        "[Location].[Location].[" + row.Location.Value + "]"],
                                    ["Measure.[SS Mtrl L3_Source]",
                                    "Measure.[SS Mtrl L3_ECP Flag]"],
                                    "",
                                    "",
                                    "");

                if ( result.cs.row(0).cell(result.cs.measureColumnIndex("SS Mtrl L3_ECP Flag")) == "on" ) {
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
                                        "[Item Material].[MSL3].[" + row.MSL3.Value + "]",
                                        "[Location].[Location].[" + row.Location.Value + "]"],
                                    ["Measure.[SS Mtrl L3_Source]",
                                    "Measure.[SS Mtrl L3_ECP Flag]"],
                                    "",
                                    "",
                                    "");

                if ( result.cs.row(0).cell(result.cs.measureColumnIndex("SS Mtrl L3_ECP Flag")) == "off" ) {
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
                                        "[Item Material].[MSL3].[" + row.MSL3.Value + "]",
                                        "[Location].[Location].[" + row.Location.Value + "]"],
                                    ["Measure.[SS Mtrl L3_Source]",
                                    "Measure.[SS Mtrl L3_Time Varying Flag]"],
                                    "",
                                    "",
                                    "");

                if ( result.cs.row(0).cell(result.cs.measureColumnIndex("SS Mtrl L3_Time Varying Flag")) == "Y" ) {
                    RuleOutputToUI = { Status : 'Error', Message : "Select the Time Varying value of N" };
                    rtn = 1;
                    break;
                } else if ( result.cs.row(0).cell(result.cs.measureColumnIndex("SS Mtrl L3_Source")) == "ERP" ) {
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
                                        "[Item Material].[MSL3].[" + row.MSL3.Value + "]",
                                        "[Location].[Location].[" + row.Location.Value + "]"],
                                    ["Measure.[SS Mtrl L3_Source]",
                                    "Measure.[SS Mtrl L3_Time Varying Flag]"],
                                    "",
                                    "",
                                    "");

                if ( result.cs.row(0).cell(result.cs.measureColumnIndex("SS Mtrl L3_Time Varying Flag")) == "N" ) {
                    RuleOutputToUI = { Status : 'Error', Message : "Select the Time Varying value of Y" };
                    rtn = 1;
                    break;
                } else if ( result.cs.row(0).cell(result.cs.measureColumnIndex("SS Mtrl L3_Source")) == "ERP" ) {
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
                                        "[Item Material].[MSL3].[" + row.MSL3.Value + "]",
                                        "[Location].[Location].[" + row.Location.Value + "]"],
                                    ["Measure.[SS Mtrl L3_Source]"],
                                    "",
                                    "",
                                    "");
                if ( result.cs.rowCount > 0 && result.cs.row(0).cell(result.cs.measureColumnIndex("SS Mtrl L3_Source")) == "ERP" ) {
                    vdCommon.updateMeasure(["&CWVUI",
                                                "[Item Material].[MSL3].[" + row.MSL3.Value + "]",
                                                "[Location].[Location].[" + row.Location.Value + "]"],
                                            ['Measure.[SS Mtrl L3_Source] = "NSCM";',
                                                'Measure.[SS Mtrl L3_Time Varying Flag] = "N";']);

                    vdCommon.createMeasure(["&CWVUI",
                                                "[Item Material].[MSL3].[" + row.MSL3.Value + "]",
                                                "[Location].[Location].[" + row.Location.Value + "]",
                                                "[Time].[Week].filter(#.Key == &CurrentWeek.element(0).Key)"],
                                            ['Measure.[SS Mtrl L3 W_Time.Lock] = False;']);

                    vdCommon.createMeasure(["&CWVUI",
                                                "[Item Material].[MSL3].[" + row.MSL3.Value + "]",
                                                "[Location].[Location].[" + row.Location.Value + "]",
                                                "&MDMHorizon.filter(#.Key > &CurrentWeek.element(0).Key)"],
                                            ['Measure.[SS Mtrl L3 W_Time.Lock] = True;',
                                                'Measure.[SS Mtrl L3 W_Time] = Null;']);
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
                                        "[Item Material].[MSL3].[" + row.MSL3.Value + "]",
                                        "[Location].[Location].[" + row.Location.Value + "]"],
                                    ["Measure.[SS Mtrl L3_Source]"],
                                    "",
                                    "",
                                    "");
                if ( result.cs.rowCount > 0 && result.cs.row(0).cell(result.cs.measureColumnIndex("SS Mtrl L3_Source")) == "NSCM" ) {
                    vdCommon.updateMeasure(["&CWVUI",
                                                "[Item Material].[MSL3].[" + row.MSL3.Value + "]",
                                                "[Location].[Location].[" + row.Location.Value + "]"],
                                            ['Measure.[SS Mtrl L3_Source] = "ERP";',
                                                'Measure.[SS Mtrl L3_Time Varying Flag] = "N";']);

                    vdCommon.createMeasure(["&CWVUI",
                                                "[Item Material].[MSL3].[" + row.MSL3.Value + "]",
                                                "[Location].[Location].[" + row.Location.Value + "]",
                                                "&MDMHorizon"],
                                            ['Measure.[SS Mtrl L3 W_Time.Lock] = True;',
                                                'Measure.[SS Mtrl L3 W_Time] = Null;']);
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
                                            "[Item Material].[MSL3].[" + row.MSL3.Value + "]",
                                            "[Location].[Location].[" + row.Location.Value + "]"],
                                        ['Measure.[SS Mtrl L3_Time Varying Flag] = "Y";']);

                vdCommon.createMeasure(["&CWVUI",
                                            "[Item Material].[MSL3].[" + row.MSL3.Value + "]",
                                            "[Location].[Location].[" + row.Location.Value + "]",
                                            "&MDMHorizon"],
                                        ['Measure.[SS Mtrl L3 W_Time.Lock] = True;']);
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
                                            "[Item Material].[MSL3].[" + row.MSL3.Value + "]",
                                            "[Location].[Location].[" + row.Location.Value + "]"],
                                        ['Measure.[SS Mtrl L3_Time Varying Flag] = "N";']);

                vdCommon.createMeasure(["&CWVUI",
                                            "[Item Material].[MSL3].[" + row.MSL3.Value + "]",
                                            "[Location].[Location].[" + row.Location.Value + "]",
                                            "[Time].[Week].filter(#.Key == &CurrentWeek.element(0).Key)"],
                                        ['Measure.[SS Mtrl L3 W_Time.Lock] = False;']);

                vdCommon.createMeasure(["&CWVUI",
                                            "[Item Material].[MSL3].[" + row.MSL3.Value + "]",
                                            "[Location].[Location].[" + row.Location.Value + "]",
                                            "&MDMHorizon.filter(#.Key > &CurrentWeek.element(0).Key)"],
                                        ['Measure.[SS Mtrl L3 W_Time.Lock] = True;',
                                            'Measure.[SS Mtrl L3 W_Time] = Null;']);
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
                                            "[Item Material].[MSL3].[" + row.MSL3.Value + "]",
                                            "[Location].[Location].[" + row.Location.Value + "]"],
                                        ['Measure.[SS Mtrl L3_ECP Flag] = "on";']);
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
                                            "[Item Material].[MSL3].[" + row.MSL3.Value + "]",
                                            "[Location].[Location].[" + row.Location.Value + "]"],
                                        ['Measure.[SS Mtrl L3_ECP Flag] = "off";']);
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
                                        "[Item Material].[MSL3].[" + row.MSL3.Value + "]",
                                        "&MDMHorizon"],
                                    ["Measure.[SS Mtrl L3 W_Time]",
                                        "Measure.[SS Mtrl L3_Source]",
                                        "Measure.[SS Mtrl L3_Time Varying Flag]"],
                                    "",
                                    "orderby Time.[Week].DisplayName",
                                    "");
                vdCommon.printCsData(result, 3);

                if ( result.cs.rowCount > 0 &&
                        result.cs.row(0).cell(result.cs.measureColumnIndex("SS Mtrl L3_Source")) == "NSCM" &&
                        result.cs.row(0).cell(result.cs.measureColumnIndex("SS Mtrl L3_Time Varying Flag")) == "Y" ) {
                    // 주차별 hm 데이타를 만든다.
                    var hm = {}
                    var value = 0;
                    var week = "";
                    for ( var m = 0; m < result.cs.rowCount; m++ ) {
                        week = result.cs.row(m).cell(result.cs.memberColumnIndex("Time", "Week")).Name;
                        value = result.cs.row(m).cell(result.cs.measureColumnIndex("SS Mtrl L3 W_Time"));

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
                                                                        "[Item Material].[MSL3].[" + row.MSL3.Value + "]"],
                                                                     ['Measure.[SS Mtrl L3 W_Time] = ' + lastValue + ';']);
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
                                        "[Item Material].[MSL3].[" + row.MSL3.Value + "]",
                                        "[Location].[Location].[" + row.Location.Value + "]"],
                                    ["Measure.[SS Mtrl L3_Source]"],
                                    "",
                                    "",
                                    "");
                if ( result.cs.rowCount > 0 ) {
                    flag = result.cs.row(0).cell(result.cs.measureColumnIndex("SS Mtrl L3_Source"));
                    vdCommon.debug("flag : " + flag);

                    if ( fbFlag == "NSCM" && flag != "NSCM" ) {
                        vdCommon.updateMeasure(["&CWVUI",
                                                    "[Item Material].[MSL3].[" + row.MSL3.Value + "]",
                                                    "[Location].[Location].[" + row.Location.Value + "]"],
                                                ['Measure.[SS Mtrl L3_Source] = "NSCM";',
                                                    'Measure.[SS Mtrl L3_Time Varying Flag] = "Y";']);

                        vdCommon.createMeasure(["&CWVUI",
                                                    "[Item Material].[MSL3].[" + row.MSL3.Value + "]",
                                                    "[Location].[Location].[" + row.Location.Value + "]",
                                                    "&MDMHorizon"],
                                                ['Measure.[SS Mtrl L3 W_Time.Lock] = False;',
                                                    'Measure.[SS Mtrl L3 W_Time] = ' + fbQty + ';']);
                    } else if ( fbFlag == "ERP" && flag != "ERP" ) {
                        vdCommon.updateMeasure(["&CWVUI",
                                                    "[Item Material].[MSL3].[" + row.MSL3.Value + "]",
                                                    "[Location].[Location].[" + row.Location.Value + "]"],
                                                ['Measure.[SS Mtrl L3_Source] = "ERP";',
                                                    'Measure.[SS Mtrl L3_Time Varying Flag] = "N";']);

                        vdCommon.createMeasure(["&CWVUI",
                                                    "[Item Material].[MSL3].[" + row.MSL3.Value + "]",
                                                    "[Location].[Location].[" + row.Location.Value + "]",
                                                    "&MDMHorizon"],
                                                ['Measure.[SS Mtrl L3 W_Time.Lock] = False;',
                                                    'Measure.[SS Mtrl L3 W_Time] = Null;']);
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
                                        "[Item Material].[MSL3].[" + row.MSL3.Value + "]",
                                        "[Location].[Location].[" + row.Location.Value + "]"],
                                    ["Measure.[SS Mtrl L3_ECP Flag]"],
                                    "",
                                    "",
                                    "");
                if ( result.cs.rowCount > 0 ) {
                    flag = result.cs.row(0).cell(result.cs.measureColumnIndex("SS Mtrl L3_ECP Flag"));
                    vdCommon.debug("flag : " + flag);

                    if ( fbFlag == "on" && flag != "on" ) {
                        vdCommon.updateMeasure(["&CWVUI",
                                                    "[Item Material].[MSL3].[" + row.MSL3.Value + "]",
                                                    "[Location].[Location].[" + row.Location.Value + "]"],
                                                ['Measure.[SS Mtrl L3_ECP Flag] = "on";']);
                    } else if ( fbFlag == "off" && flag != "off" ) {
                        vdCommon.updateMeasure(["&CWVUI",
                                                    "[Item Material].[MSL3].[" + row.MSL3.Value + "]",
                                                    "[Location].[Location].[" + row.Location.Value + "]"],
                                                ['Measure.[SS Mtrl L3_ECP Flag] = "off";']);
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
                                        "[Item Material].[MSL3].[" + row.MSL3.Value + "]",
                                        "[Location].[Location].[" + row.Location.Value + "]"],
                                    ["Measure.[SS Mtrl L3_Time Varying Flag]",
                                        "Measure.[SS Mtrl L3_Source]"],
                                    "",
                                    "",
                                    "");
                if ( result.cs.rowCount > 0 ) {
                    flag = result.cs.row(0).cell(result.cs.measureColumnIndex("SS Mtrl L3_Time Varying Flag"));
                    source = result.cs.row(0).cell(result.cs.measureColumnIndex("SS Mtrl L3_Source"));
                    vdCommon.debug("flag : " + flag + ", source : " + source);

                    if ( source == "NSCM" && fbFlag == "Y" && flag != "Y" ) {
                        vdCommon.createMeasure(["&CWVUI",
                                                    "[Item Material].[MSL3].[" + row.MSL3.Value + "]",
                                                    "[Location].[Location].[" + row.Location.Value + "]"],
                                                ['Measure.[SS Mtrl L3_Time Varying Flag] = "Y";']);

                        var qty = null;
                        var resultFirst = vdCommon.selectList(["&CWVUI",
                                                                    "[Item Material].[MSL3].[" + row.MSL3.Value + "]",
                                                                    "[Location].[Location].[" + row.Location.Value + "]",
                                                                    "[Time].[Week].filter(#.Key == &CurrentWeek.element(0).Key)"],
                                                              ["Measure.[SS Mtrl L3 W_Time]"],
                                                              "",
                                                              "",
                                                              "");
                        if ( resultFirst.cs.rowCount > 0 ) {
                            qty = resultFirst.cs.row(0).cell(resultFirst.cs.measureColumnIndex("SS Mtrl L3 W_Time"));
                        }

                        vdCommon.createMeasure(["&CWVUI",
                                                    "[Item Material].[MSL3].[" + row.MSL3.Value + "]",
                                                    "[Location].[Location].[" + row.Location.Value + "]",
                                                    "&MDMHorizon"],
                                                ['Measure.[SS Mtrl L3 W_Time.Lock] = False;',
                                                    'Measure.[SS Mtrl L3 W_Time] = ' + qty + ';']);
                    } else if ( source == "NSCM" && fbFlag == "N" && flag != "N" ) {
                        vdCommon.createMeasure(["&CWVUI",
                                                    "[Item Material].[MSL3].[" + row.MSL3.Value + "]",
                                                    "[Location].[Location].[" + row.Location.Value + "]"],
                                                ['Measure.[SS Mtrl L3_Time Varying Flag] = "N";']);

                        vdCommon.createMeasure(["&CWVUI",
                                                    "[Item Material].[MSL3].[" + row.MSL3.Value + "]",
                                                    "[Location].[Location].[" + row.Location.Value + "]",
                                                    '&MDMHorizon.filter(#.Key > &CurrentWeek.element(0).Key)'],
                                                ['Measure.[SS Mtrl L3 W_Time.Lock] = False;',
                                                    'Measure.[SS Mtrl L3 W_Time] = Null;']);
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
                                        "[Item Material].[MSL3].[" + row.MSL3.Value + "]",
                                        '[Time].[Week].filter(#.Name >= "' + fbFromWeek + '" && #.Name <= "' + fbToWeek + '")'],
                                    ["Measure.[SS Mtrl L3 W_Time]",
                                        "Measure.[SS Mtrl L3 W_Time.Lock]",
                                        "Measure.[SS Mtrl L3_Source]",
                                        "Measure.[SS Mtrl L3_Time Varying Flag]"],
                                    "",
                                    "orderby Time.[Week].DisplayName",
                                    "");
                vdCommon.printCsData(result, 3);

                if ( result.cs.rowCount > 0 &&
                        result.cs.row(0).cell(result.cs.measureColumnIndex("SS Mtrl L3_Source")) == "NSCM" &&
                        result.cs.row(0).cell(result.cs.measureColumnIndex("SS Mtrl L3_Time Varying Flag")) == "Y" ) {
                    var queryStr = vdCommon.createMeasureQuery(["&CWVUI",
                                                                    "[Location].[Location].[" + row.Location.Value + "]",
                                                                    "[Item Material].[MSL3].[" + row.MSL3.Value + "]",
                                                                    '[Time].[Week].filter(#.Name >= "' + fbFromWeek + '" && #.Name <= "' + fbToWeek + '")'],
                                                                 ['Measure.[SS Mtrl L3 W_Time] = ' + fbValue + ';']);
                    vdCommon.executeQuery("Batch Query" , queryStr);
                } else if ( result.cs.rowCount > 0 &&
                        result.cs.row(0).cell(result.cs.measureColumnIndex("SS Mtrl L3_Source")) == "NSCM" &&
                        result.cs.row(0).cell(result.cs.measureColumnIndex("SS Mtrl L3_Time Varying Flag")) == "N" &&
                        result.cs.row(0).cell(result.cs.measureColumnIndex("SS Mtrl L3 W_Time.Lock")) != true ) {
                    var queryStr = vdCommon.createMeasureQuery(["&CWVUI",
                                                                    "[Location].[Location].[" + row.Location.Value + "]",
                                                                    "[Item Material].[MSL3].[" + row.MSL3.Value + "]",
                                                                    '[Time].[Week].[' + result.cs.row(0).cell(result.cs.memberColumnIndex("Time", "Week")).Name + ']'],
                                                                 ['Measure.[SS Mtrl L3 W_Time] = ' + fbValue + ';']);
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
                                        "[Item Material].[MSL3].[" + row.MSL3.Value + "]",
                                        '[Time].[Week].filter(#.Name >= "' + fbFromWeek + '" && #.Name <= "' + fbToWeek + '")'],
                                    ["Measure.[SS Mtrl L3 W_Time]",
                                        "Measure.[SS Mtrl L3 W_Time.Lock]",
                                        "Measure.[SS Mtrl L3_Source]",
                                        "Measure.[SS Mtrl L3_Time Varying Flag]"],
                                    "",
                                    "orderby Time.[Week].DisplayName",
                                    "");
                //vdCommon.printCsData(result, 3);

                if ( result.cs.rowCount > 0 &&
                        result.cs.row(0).cell(result.cs.measureColumnIndex("SS Mtrl L3_Source")) == "NSCM" &&
                        result.cs.row(0).cell(result.cs.measureColumnIndex("SS Mtrl L3_Time Varying Flag")) == "Y" ) {
                    var queryStr = vdCommon.createMeasureQuery(["&CWVUI",
                                                                    "[Location].[Location].[" + row.Location.Value + "]",
                                                                    "[Item Material].[MSL3].[" + row.MSL3.Value + "]",
                                                                    '[Time].[Week].filter(#.Name >= "' + fbFromWeek + '" && #.Name <= "' + fbToWeek + '")'],
                                                                 ['Measure.[SS Mtrl L3 W_Time] = ' + fbValue + ';']);
                    vdCommon.executeQuery("Batch Query" , queryStr);
                } else if ( result.cs.rowCount > 0 &&
                        result.cs.row(0).cell(result.cs.measureColumnIndex("SS Mtrl L3_Source")) == "NSCM" &&
                        result.cs.row(0).cell(result.cs.measureColumnIndex("SS Mtrl L3_Time Varying Flag")) == "N" &&
                        result.cs.row(0).cell(result.cs.measureColumnIndex("SS Mtrl L3 W_Time.Lock")) != true ) {
                    var queryStr = vdCommon.createMeasureQuery(["&CWVUI",
                                                                    "[Location].[Location].[" + row.Location.Value + "]",
                                                                    "[Item Material].[MSL3].[" + row.MSL3.Value + "]",
                                                                    '[Time].[Week].[' + result.cs.row(0).cell(result.cs.memberColumnIndex("Time", "Week")).Name + ']'],
                                                                 ['Measure.[SS Mtrl L3 W_Time] = ' + fbValue + ';']);
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
        fn_subSetCombo : fn_subSetCombo,
        fn_subSetChange : fn_subSetChange,
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

/**************************** o9.NSCM.JSSSMtrlLv3 ****************************
    2025-3-28 : fn_ditto 기능 추가
    2025-04-14 : fn_sourceChange, fn_ecpChange, fn_timeVaryingChange 기능 추가
    2025-04-16 : fn_ditto_V2 기능 추가
*********************************************************************/