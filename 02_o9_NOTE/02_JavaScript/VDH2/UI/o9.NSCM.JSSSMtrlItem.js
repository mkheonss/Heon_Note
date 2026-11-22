define('o9.NSCM.JSSSMtrlItem', ['o9/data/query', 'o9/data/cellset', 'o9.NSCM.commonLib'], function () {
    const programName = "o9.NSCM.JSSSMtrlItem";

    var fn_addCombo1 = function(o9Params){
        var commonLib = require('o9.NSCM.commonLib');

        var programName = "o9.NSCM.JSSSMtrlItem ============> fn_addCombo1";
        vdCommon = new commonLib.VdCommon(programName);
        vdCommon.setLogLevel("Debug");

        vdCommon.printParams(o9Params);

        // 파라미터 가져오기
        var parsedParams = JSON.parse(o9Params);

        var rMsl1 = vdCommon.selectList(
                            ["&NSUIMtrlMSL1View"],
                            [],
                            "",
                            "orderby [Item Material].[MSL1].[MSL1 Sorting Order]",
                            "");
        var comboList = vdCommon.fn_makeCombo(rMsl1, {DimName : "Item Material", DimAttbName : "MSL1", isDisplayNameWithCode : true});
        vdCommon.debug("ComboData : " + JSON.stringify(comboList));

        vdCommon.programEnd();

        return comboList;
    };

    var fn_addCombo2 = function(o9Params){
        var commonLib = require('o9.NSCM.commonLib');

        var programName = "o9.NSCM.JSSSMtrlItem ============> fn_addCombo2";
        vdCommon = new commonLib.VdCommon(programName);
        vdCommon.setLogLevel("Debug");

        vdCommon.printParams(o9Params);

        // 파라미터 가져오기
        var parsedParams = JSON.parse(o9Params);
        var msl1 = parsedParams.fbMSL1;

        var rMsl2 = vdCommon.selectList(
                            ["&NSUIMtrlMSL1View.[" + msl1 + "]",
                                "&NSUIMtrlMSL2View"],
                            [],
                            "",
                            "orderby [Item Material].[MSL2].[MSL2 Sorting Order]",
                            "");
        var comboList = vdCommon.fn_makeCombo(rMsl2, {DimName : "Item Material", DimAttbName : "MSL2", isDisplayNameWithCode : true});
        vdCommon.debug("ComboData : " + JSON.stringify(comboList));

        vdCommon.programEnd();

        return comboList;
    };

    var fn_addCombo3 = function(o9Params){
        var commonLib = require('o9.NSCM.commonLib');

        var programName = "o9.NSCM.JSSSMtrlItem ============> fn_addCombo3";
        vdCommon = new commonLib.VdCommon(programName);
        vdCommon.setLogLevel("Debug");

        vdCommon.printParams(o9Params);

        // 파라미터 가져오기
        var parsedParams = JSON.parse(o9Params);
        var msl2 = parsedParams.fbMSL2;

        var rMsl3 = vdCommon.selectList(
                            ["&NSUIMtrlMSL2View.[" + msl2 + "]",
                                "&NSUIMtrlMSL3View"],
                            [],
                            "",
                            "orderby [Item Material].[MSL3].[MSL3 Sorting Order]",
                            "");
        var comboList = vdCommon.fn_makeCombo(rMsl3, {DimName : "Item Material", DimAttbName : "MSL3", isDisplayNameWithCode : true});
        vdCommon.debug("ComboData : " + JSON.stringify(comboList));

        vdCommon.programEnd();

        return comboList;
    };

    var fn_addCombo4 = function(o9Params){
        var commonLib = require('o9.NSCM.commonLib');

        var programName = "o9.NSCM.JSSSMtrlItem ============> fn_addCombo4";
        vdCommon = new commonLib.VdCommon(programName);
        vdCommon.setLogLevel("Debug");

        vdCommon.printParams(o9Params);

        // 파라미터 가져오기
        var parsedParams = JSON.parse(o9Params);
        var msl3 = parsedParams.fbMSL3;

        var result = vdCommon.selectList(
                            ["&NSUIMtrlMSL3View.[" + msl3 + "]",
                                "&NSUIMtrlMSL4View"],
                            [],
                            "",
                            "orderby [Item Material].[MSL4].[MSL4 Sorting Order]",
                            "");
        var comboList = vdCommon.fn_makeCombo(result, {DimName : "Item Material", DimAttbName : "MSL4", isDisplayNameWithCode : true, existAll : true});
        vdCommon.debug("ComboData : " + JSON.stringify(comboList));

        vdCommon.programEnd();

        return comboList;
    };

    var fn_addCombo5 = function(o9Params){
        var commonLib = require('o9.NSCM.commonLib');

        var programName = "o9.NSCM.JSSSMtrlItem ============> fn_addCombo5";
        vdCommon = new commonLib.VdCommon(programName);
        vdCommon.setLogLevel("Debug");

        vdCommon.printParams(o9Params);

        // 파라미터 가져오기
        var parsedParams = JSON.parse(o9Params);
        var msl3 = parsedParams.fbMSL3;
        var msl4 = parsedParams.fbMSL4;

        var comboList = [];
        var result = vdCommon.selectList(
                            ["&NSUIMtrlMSL3View.[" + msl3 + "]",
                                "&NSUIMtrlMSL4View" + ( msl4 == "All" ? "" : ".[" + msl4 + "]"),
                                "&NSUIMtrlMSL5View"],
                            [],
                            "",
                            "orderby [Item Material].[MSL5].[MSL5 Sorting Order]",
                            "");
        var comboList = vdCommon.fn_makeCombo(result, {DimName : "Item Material", DimAttbName : "MSL5", isDisplayNameWithCode : true, existAll : true});
        vdCommon.debug("ComboData : " + JSON.stringify(comboList));

        vdCommon.programEnd();

        return comboList;
    };

    var fn_addComboItem = function(o9Params){
        var commonLib = require('o9.NSCM.commonLib');

        var programName = "o9.NSCM.JSSSMtrlItem ============> fn_addComboItem";
        vdCommon = new commonLib.VdCommon(programName);
        vdCommon.setLogLevel("Debug");

        vdCommon.printParams(o9Params);

        // 파라미터 가져오기
        var parsedParams = JSON.parse(o9Params);
        var msl3 = parsedParams.fbMSL3;
        var msl4 = parsedParams.fbMSL4;
        var msl5 = parsedParams.fbMSL5;

        // 등록된 데이타를 가져온다.
        var rExistItem = vdCommon.selectList(
                            ["&CWVUI",
                                "[Item Material].[MSL3].[" + msl3 + "]",
                                "[Item Material].[MSL4]" + ( msl4 == "All" ? "" : ".[" + msl4 + "]" ),
                                "[Item Material].[MSL5]" + ( msl5 == "All" ? "" : ".[" + msl5 + "]" ),
                                "[Item Material].[Item Material]",
                                "[Location].[Location]"],
                            ["Measure.[SS Mtrl Item_Source]"],
                            "",
                            "",
                            "limit 2000");

        var validHm = {};
        for ( var i = 0; i < rExistItem.cs.rowCount; i++ ) {
            item = vdCommon.getMember(rExistItem.cs, i, "Item Material", "Item Material").Name;

            if ( validHm[item] == undefined ) {
                validHm[item] = item;
            }
        }
        vdCommon.debug("validHm : " + JSON.stringify(validHm));

        var comboList = [];
        var rItem = vdCommon.selectList(
                            ["[Item Material].[MSL3].[" + msl3 + "]",
                                "[Item Material].[MSL4]" + ( msl4 == "All" ? "" : ".[" + msl4 + "]" ),
                                "[Item Material].[MSL5]" + ( msl5 == "All" ? "" : ".[" + msl5 + "]" ),
                                "[Item Material].[Item Material]"],
                            [],
                            "",
                            "",
                            "");
        for ( var i = 0; i < rItem.cs.rowCount; i++ ) {
            item = rItem.cs.row(i).cell(rItem.cs.memberColumnIndex("Item Material", "Item Material")).Name;

            if ( validHm[item] == undefined ) {
                comboList.push({ Name : item, DisplayName : item});
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
    };

    var fn_add = function(o9Params){
        const commonLib = require('o9.NSCM.commonLib');
        const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
        vdCommon.setLogLevel("Debug");

        try {
            vdCommon.printParams(o9Params);

            // 파라미터 가져오기
            var parsedParams = JSON.parse(o9Params);
            var fbMSL5 = parsedParams.fbMSL5;
            var fbItem = parsedParams.fbItem;
            var fbPlant = parsedParams.fbPlant;

            var locations = "";
            if ( fbPlant != "All" ) {
                locations = fbPlant.join(",");
            } else {
                var msl5 = "";
                if ( fbMSL5 != "All" ) {
                    msl5 = ".[" + fbMSL5 + "]";
                }
                var result = vdCommon.selectList(
                                            ["&NSUILocationMFMtrlView"],
                                            [],
                                            'where { &CWVUI, [Item Material].[MSL5]' + msl5 + ', Measure.[Item Mtrl Site Asn_Cur Status] in {"ACTIVE","PLANNED"} }',
                                            "",
                                            "",
                                            "");
                for ( var i = 0; i < result.cs.rowCount; i++ ) {
                    location = result.cs.row(i).cell(result.cs.memberColumnIndex("Location", "Location")).Name;
                    if ( i == 0 ) {
                        locations = '"' + location + '"';
                    } else {
                        locations += ',"' + location + '"';
                    }
                }
            }

            if ( locations == "" ) {
                RuleOutputToUI = { Status : 'Error', Message : "Location does not exist." };
                return;
            } else {
                for ( var i = 0; i < fbItem.length; i++ ) {
                    vdCommon.createMeasure(["&CWVUI",
                                                "[Item Material].[Item Material].[" + fbItem[i] + "]",
                                                '[Location].[Location].filter(#.Name in {' + locations + '})'],
                                            ['Measure.[SS Mtrl Item_Source] = "NSCM";',
                                                'Measure.[SS Mtrl Item_ECP Flag] = "off";',
                                                'Measure.[SS Mtrl Item_Time Varying Flag] = "Y";']);

                    vdCommon.createMeasure(["&CWVUI",
                                                "[Item Material].[Item Material].[" + fbItem[i] + "]",
                                                '[Location].[Location].filter(#.Name in {' + locations + '})',
                                                "&MDMHorizon"],
                                            ['Measure.[SS Mtrl Item W_Time] = Null;']);
                }
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
            var commonLib = require('o9.NSCM.commonLib');

            var programName = "o9.NSCM.JSSSMtrlItem ============> fn_sourceErpValidation";

            vdUtil = new commonLib.VdUtil();
            vdCommon = new commonLib.VdCommon(programName);
            vdCommon.setLogLevel("Debug");

            vdCommon.printParams(o9Params);

            // 파라미터 가져오기
            var parsedParams = JSON.parse(o9Params);
            var fbSelect = parsedParams.fbSelect;

            for ( var i = 0; i < fbSelect.length; i++ ) {
                var row = fbSelect[i];

                var result = vdCommon.selectList(
                                    ["&CWVUI",
                                        "[Item Material].[Item Material].[" + row.Item.Value + "]",
                                        "[Location].[Location].[" + row.Location.Value + "]"],
                                    ["Measure.[SS Mtrl Item_Source]",
                                    "Measure.[SS Mtrl Item_Time Varying Flag]"],
                                    "",
                                    "",
                                    "");

                if ( result.cs.row(0).cell(result.cs.measureColumnIndex("SS Mtrl Item_Source")) == "ERP" ) {
                    RuleOutputToUI = { Status : 'Error', Message : "Select the Source value of NSCM" };
                    rtn = 1;
                    break;
                } else if ( result.cs.row(0).cell(result.cs.measureColumnIndex("SS Mtrl Item_Time Varying Flag")) == "Y" ) {
                    RuleOutputToUI = { Status : 'Error', Message : "Change Time Varying to N first" };
                    rtn = 1;
                    break;
                }
            }
        } catch ( e ) {
            RuleOutputToUI = { Status : 'Error', Message : "Js Logic Error : " + e.message };
            return;
        }

        vdCommon.programEnd();

        return rtn;
    };

    var fn_sourceNscmValidation = function(o9Params){
        var rtn = 0; // 에러 없음

        try {
            var commonLib = require('o9.NSCM.commonLib');

            var programName = "o9.NSCM.JSSSMtrlItem ============> fn_sourceNscmValidation";

            vdUtil = new commonLib.VdUtil();
            vdCommon = new commonLib.VdCommon(programName);
            vdCommon.setLogLevel("Debug");

            vdCommon.printParams(o9Params);

            // 파라미터 가져오기
            var parsedParams = JSON.parse(o9Params);
            var fbSelect = parsedParams.fbSelect;

            for ( var i = 0; i < fbSelect.length; i++ ) {
                var row = fbSelect[i];

                var result = vdCommon.selectList(
                                    ["&CWVUI",
                                        "[Item Material].[Item Material].[" + row.Item.Value + "]",
                                        "[Location].[Location].[" + row.Location.Value + "]"],
                                    ["Measure.[SS Mtrl Item_Source]",
                                    "Measure.[SS Mtrl Item_Time Varying Flag]"],
                                    "",
                                    "",
                                    "");

                if ( result.cs.row(0).cell(result.cs.measureColumnIndex("SS Mtrl Item_Source")) == "NSCM" ) {
                    RuleOutputToUI = { Status : 'Error', Message : "Select the Source value of ERP" };
                    rtn = 1;
                    break;
                } else if ( result.cs.row(0).cell(result.cs.measureColumnIndex("SS Mtrl Item_Time Varying Flag")) == "Y" ) {
                    RuleOutputToUI = { Status : 'Error', Message : "Change Time Varying to N first" };
                    rtn = 1;
                    break;
                }
            }
        } catch ( e ) {
            RuleOutputToUI = { Status : 'Error', Message : "Js Logic Error : " + e.message };
            return;
        }

        vdCommon.programEnd();

        return rtn;
    };

    var fn_sourceEcpOnValidation = function(o9Params){
        var rtn = 0; // 에러 없음

        try {
            var commonLib = require('o9.NSCM.commonLib');

            var programName = "o9.NSCM.JSSSMtrlItem ============> fn_sourceEcpOnValidation";

            vdUtil = new commonLib.VdUtil();
            vdCommon = new commonLib.VdCommon(programName);
            vdCommon.setLogLevel("Debug");

            vdCommon.printParams(o9Params);

            // 파라미터 가져오기
            var parsedParams = JSON.parse(o9Params);
            var fbSelect = parsedParams.fbSelect;

            for ( var i = 0; i < fbSelect.length; i++ ) {
                var row = fbSelect[i];

                var result = vdCommon.selectList(
                                    ["&CWVUI",
                                        "[Item Material].[Item Material].[" + row.Item.Value + "]",
                                        "[Location].[Location].[" + row.Location.Value + "]"],
                                    ["Measure.[SS Mtrl Item_Source]",
                                    "Measure.[SS Mtrl Item_ECP Flag]"],
                                    "",
                                    "",
                                    "");

                if ( result.cs.row(0).cell(result.cs.measureColumnIndex("SS Mtrl Item_ECP Flag")) == "on" ) {
                    RuleOutputToUI = { Status : 'Error', Message : "Select the ECP value of off" };
                    rtn = 1;
                    break;
                }
            }
        } catch ( e ) {
            RuleOutputToUI = { Status : 'Error', Message : "Js Logic Error : " + e.message };
            return;
        }

        vdCommon.programEnd();

        return rtn;
    };

    var fn_sourceEcpOffValidation = function(o9Params){
        var rtn = 0; // 에러 없음

        try {
            var commonLib = require('o9.NSCM.commonLib');

            var programName = "o9.NSCM.JSSSMtrlItem ============> fn_sourceEcpOffValidation";

            vdUtil = new commonLib.VdUtil();
            vdCommon = new commonLib.VdCommon(programName);
            vdCommon.setLogLevel("Debug");

            vdCommon.printParams(o9Params);

            // 파라미터 가져오기
            var parsedParams = JSON.parse(o9Params);
            var fbSelect = parsedParams.fbSelect;

            for ( var i = 0; i < fbSelect.length; i++ ) {
                var row = fbSelect[i];

                var result = vdCommon.selectList(
                                    ["&CWVUI",
                                        "[Item Material].[Item Material].[" + row.Item.Value + "]",
                                        "[Location].[Location].[" + row.Location.Value + "]"],
                                    ["Measure.[SS Mtrl Item_Source]",
                                    "Measure.[SS Mtrl Item_ECP Flag]"],
                                    "",
                                    "",
                                    "");

                if ( result.cs.row(0).cell(result.cs.measureColumnIndex("SS Mtrl Item_ECP Flag")) == "off" ) {
                    RuleOutputToUI = { Status : 'Error', Message : "Select the ECP value of on" };
                    rtn = 1;
                    break;
                }
            }
        } catch ( e ) {
            RuleOutputToUI = { Status : 'Error', Message : "Js Logic Error : " + e.message };
            return;
        }

        vdCommon.programEnd();

        return rtn;
    };

    var fn_sourceTimeYValidation = function(o9Params){
        var rtn = 0; // 에러 없음

        try {
            var commonLib = require('o9.NSCM.commonLib');

            var programName = "o9.NSCM.JSSSMtrlItem ============> fn_sourceTimeYValidation";

            vdUtil = new commonLib.VdUtil();
            vdCommon = new commonLib.VdCommon(programName);
            vdCommon.setLogLevel("Debug");

            vdCommon.printParams(o9Params);

            // 파라미터 가져오기
            var parsedParams = JSON.parse(o9Params);
            var fbSelect = parsedParams.fbSelect;

            for ( var i = 0; i < fbSelect.length; i++ ) {
                var row = fbSelect[i];

                var result = vdCommon.selectList(
                                    ["&CWVUI",
                                        "[Item Material].[Item Material].[" + row.Item.Value + "]",
                                        "[Location].[Location].[" + row.Location.Value + "]"],
                                    ["Measure.[SS Mtrl Item_Source]",
                                    "Measure.[SS Mtrl Item_Time Varying Flag]"],
                                    "",
                                    "",
                                    "");

                if ( result.cs.row(0).cell(result.cs.measureColumnIndex("SS Mtrl Item_Time Varying Flag")) == "Y" ) {
                    RuleOutputToUI = { Status : 'Error', Message : "Select the Time Varying value of N" };
                    rtn = 1;
                    break;
                } else if ( result.cs.row(0).cell(result.cs.measureColumnIndex("SS Mtrl Item_Source")) == "ERP" ) {
                    RuleOutputToUI = { Status : 'Error', Message : "Time Varying cannot be modified for data whose source is ERP." };
                    rtn = 1;
                    break;
                }
            }
        } catch ( e ) {
            RuleOutputToUI = { Status : 'Error', Message : "Js Logic Error : " + e.message };
            return;
        }

        vdCommon.programEnd();

        return rtn;
    };

    var fn_sourceTimeNValidation = function(o9Params){
        var rtn = 0; // 에러 없음

        try {
            var commonLib = require('o9.NSCM.commonLib');

            var programName = "o9.NSCM.JSSSMtrlItem ============> fn_sourceTimeNValidation";

            vdUtil = new commonLib.VdUtil();
            vdCommon = new commonLib.VdCommon(programName);
            vdCommon.setLogLevel("Debug");

            vdCommon.printParams(o9Params);

            // 파라미터 가져오기
            var parsedParams = JSON.parse(o9Params);
            var fbSelect = parsedParams.fbSelect;

            for ( var i = 0; i < fbSelect.length; i++ ) {
                var row = fbSelect[i];

                var result = vdCommon.selectList(
                                    ["&CWVUI",
                                        "[Item Material].[Item Material].[" + row.Item.Value + "]",
                                        "[Location].[Location].[" + row.Location.Value + "]"],
                                    ["Measure.[SS Mtrl Item_Source]",
                                    "Measure.[SS Mtrl Item_Time Varying Flag]"],
                                    "",
                                    "",
                                    "");

                if ( result.cs.row(0).cell(result.cs.measureColumnIndex("SS Mtrl Item_Time Varying Flag")) == "N" ) {
                    RuleOutputToUI = { Status : 'Error', Message : "Select the Time Varying value of Y" };
                    rtn = 1;
                    break;
                } else if ( result.cs.row(0).cell(result.cs.measureColumnIndex("SS Mtrl Item_Source")) == "ERP" ) {
                    RuleOutputToUI = { Status : 'Error', Message : "Time Varying cannot be modified for data whose source is ERP." };
                    rtn = 1;
                    break;
                }
            }
        } catch ( e ) {
            RuleOutputToUI = { Status : 'Error', Message : "Js Logic Error : " + e.message };
            return;
        }

        vdCommon.programEnd();

        return rtn;
    };

    var fn_ditto = function(o9Params){
        const commonLib = require('o9.NSCM.commonLib');
        const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
        const vdUtil = new commonLib.VdUtil();
        vdCommon.setLogLevel("Debug");

        try {

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
                                        "[Item Material].[Item Material].[" + row.Item.Value + "]",
                                        "&MDMHorizon"],
                                    ["Measure.[SS Mtrl Item W_Time]",
                                        "Measure.[SS Mtrl Item_Source]",
                                        "Measure.[SS Mtrl Item_Time Varying Flag]"],
                                    "",
                                    "orderby Time.[Week].DisplayName",
                                    "");
                vdCommon.printCsData(result, 3);

                if ( result.cs.rowCount > 0 &&
                        result.cs.row(0).cell(result.cs.measureColumnIndex("SS Mtrl Item_Source")) == "NSCM" &&
                        result.cs.row(0).cell(result.cs.measureColumnIndex("SS Mtrl Item_Time Varying Flag")) == "Y" ) {
                    // 주차별 hm 데이타를 만든다.
                    var hm = {}
                    var value = 0;
                    var week = "";
                    for ( var m = 0; m < result.cs.rowCount; m++ ) {
                        week = result.cs.row(m).cell(result.cs.memberColumnIndex("Time", "Week")).Name;
                        value = result.cs.row(m).cell(result.cs.measureColumnIndex("SS Mtrl Item W_Time"));

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
                                                                        "[Item Material].[Item Material].[" + row.Item.Value + "]"],
                                                                     ['Measure.[SS Mtrl Item W_Time] = ' + lastValue + ';']);
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
                                        "[Item Material].[Item Material].[" + row.Item.Value + "]",
                                        "[Location].[Location].[" + row.Location.Value + "]"],
                                    ["Measure.[SS Mtrl Item_Source]"],
                                    "",
                                    "",
                                    "");
                if ( result.cs.rowCount > 0 ) {
                    flag = result.cs.row(0).cell(result.cs.measureColumnIndex("SS Mtrl Item_Source"));
                    vdCommon.debug("flag : " + flag);

                    if ( fbFlag == "NSCM" && flag != "NSCM" ) {
                        vdCommon.updateMeasure(["&CWVUI",
                                                    "[Item Material].[Item Material].[" + row.Item.Value + "]",
                                                    "[Location].[Location].[" + row.Location.Value + "]"],
                                                ['Measure.[SS Mtrl Item_Source] = "NSCM";',
                                                    'Measure.[SS Mtrl Item_Time Varying Flag] = "Y";']);

                        vdCommon.createMeasure(["&CWVUI",
                                                    "[Item Material].[Item Material].[" + row.Item.Value + "]",
                                                    "[Location].[Location].[" + row.Location.Value + "]",
                                                    "&MDMHorizon"],
                                                ['Measure.[SS Mtrl Item W_Time.Lock] = False;',
                                                    'Measure.[SS Mtrl Item W_Time] = ' + fbQty + ';']);
                    } else if ( fbFlag == "ERP" && flag != "ERP" ) {
                        vdCommon.updateMeasure(["&CWVUI",
                                                    "[Item Material].[Item Material].[" + row.Item.Value + "]",
                                                    "[Location].[Location].[" + row.Location.Value + "]"],
                                                ['Measure.[SS Mtrl Item_Source] = "ERP";',
                                                    'Measure.[SS Mtrl Item_Time Varying Flag] = "N";']);

                        vdCommon.createMeasure(["&CWVUI",
                                                    "[Item Material].[Item Material].[" + row.Item.Value + "]",
                                                    "[Location].[Location].[" + row.Location.Value + "]",
                                                    "&MDMHorizon"],
                                                ['Measure.[SS Mtrl Item W_Time.Lock] = False;',
                                                    'Measure.[SS Mtrl Item W_Time] = Null;']);
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
                                        "[Item Material].[Item Material].[" + row.Item.Value + "]",
                                        "[Location].[Location].[" + row.Location.Value + "]"],
                                    ["Measure.[SS Mtrl Item_ECP Flag]"],
                                    "",
                                    "",
                                    "");
                if ( result.cs.rowCount > 0 ) {
                    flag = result.cs.row(0).cell(result.cs.measureColumnIndex("SS Mtrl Item_ECP Flag"));
                    vdCommon.debug("flag : " + flag);

                    if ( fbFlag == "on" && flag != "on" ) {
                        vdCommon.updateMeasure(["&CWVUI",
                                                    "[Item Material].[Item Material].[" + row.Item.Value + "]",
                                                    "[Location].[Location].[" + row.Location.Value + "]"],
                                                ['Measure.[SS Mtrl Item_ECP Flag] = "on";']);
                    } else if ( fbFlag == "off" && flag != "off" ) {
                        vdCommon.updateMeasure(["&CWVUI",
                                                    "[Item Material].[Item Material].[" + row.Item.Value + "]",
                                                    "[Location].[Location].[" + row.Location.Value + "]"],
                                                ['Measure.[SS Mtrl Item_ECP Flag] = "off";']);
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
                                        "[Item Material].[Item Material].[" + row.Item.Value + "]",
                                        "[Location].[Location].[" + row.Location.Value + "]"],
                                    ["Measure.[SS Mtrl Item_Time Varying Flag]",
                                        "Measure.[SS Mtrl Item_Source]"],
                                    "",
                                    "",
                                    "");
                if ( result.cs.rowCount > 0 ) {
                    flag = result.cs.row(0).cell(result.cs.measureColumnIndex("SS Mtrl Item_Time Varying Flag"));
                    source = result.cs.row(0).cell(result.cs.measureColumnIndex("SS Mtrl Item_Source"));
                    vdCommon.debug("flag : " + flag + ", source : " + source);

                    if ( source == "NSCM" && fbFlag == "Y" && flag != "Y" ) {
                        vdCommon.createMeasure(["&CWVUI",
                                                    "[Item Material].[Item Material].[" + row.Item.Value + "]",
                                                    "[Location].[Location].[" + row.Location.Value + "]"],
                                                ['Measure.[SS Mtrl Item_Time Varying Flag] = "Y";']);

                        var qty = null;
                        var resultFirst = vdCommon.selectList(["&CWVUI",
                                                                    "[Item Material].[Item Material].[" + row.Item.Value + "]",
                                                                    "[Location].[Location].[" + row.Location.Value + "]",
                                                                    "[Time].[Week].filter(#.Key == &CurrentWeek.element(0).Key)"],
                                                              ["Measure.[SS Mtrl Item W_Time]"],
                                                              "",
                                                              "",
                                                              "");
                        if ( resultFirst.cs.rowCount > 0 ) {
                            qty = resultFirst.cs.row(0).cell(resultFirst.cs.measureColumnIndex("SS Mtrl Item W_Time"));
                        }

                        vdCommon.createMeasure(["&CWVUI",
                                                    "[Item Material].[Item Material].[" + row.Item.Value + "]",
                                                    "[Location].[Location].[" + row.Location.Value + "]",
                                                    "&MDMHorizon"],
                                                ['Measure.[SS Mtrl Item W_Time.Lock] = False;',
                                                    'Measure.[SS Mtrl Item W_Time] = ' + qty + ';']);
                    } else if ( source == "NSCM" && fbFlag == "N" && flag != "N" ) {
                        vdCommon.createMeasure(["&CWVUI",
                                                    "[Item Material].[Item Material].[" + row.Item.Value + "]",
                                                    "[Location].[Location].[" + row.Location.Value + "]"],
                                                ['Measure.[SS Mtrl Item_Time Varying Flag] = "N";']);

                        vdCommon.createMeasure(["&CWVUI",
                                                    "[Item Material].[Item Material].[" + row.Item.Value + "]",
                                                    "[Location].[Location].[" + row.Location.Value + "]",
                                                    '&MDMHorizon.filter(#.Key > &CurrentWeek.element(0).Key)'],
                                                ['Measure.[SS Mtrl Item W_Time.Lock] = False;',
                                                    'Measure.[SS Mtrl Item W_Time] = Null;']);
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
                                        "[Item Material].[Item Material].[" + row.Item.Value + "]",
                                        '[Time].[Week].filter(#.Name >= "' + fbFromWeek + '" && #.Name <= "' + fbToWeek + '")'],
                                    ["Measure.[SS Mtrl Item W_Time]",
                                        "Measure.[SS Mtrl Item W_Time.Lock]",
                                        "Measure.[SS Mtrl Item_Source]",
                                        "Measure.[SS Mtrl Item_Time Varying Flag]"],
                                    "",
                                    "orderby Time.[Week].DisplayName",
                                    "");
                //vdCommon.printCsData(result, 3);

                if ( result.cs.rowCount > 0 &&
                        result.cs.row(0).cell(result.cs.measureColumnIndex("SS Mtrl Item_Source")) == "NSCM" &&
                        result.cs.row(0).cell(result.cs.measureColumnIndex("SS Mtrl Item_Time Varying Flag")) == "Y" ) {
                    var queryStr = vdCommon.createMeasureQuery(["&CWVUI",
                                                                    "[Location].[Location].[" + row.Location.Value + "]",
                                                                    "[Item Material].[Item Material].[" + row.Item.Value + "]",
                                                                    '[Time].[Week].filter(#.Name >= "' + fbFromWeek + '" && #.Name <= "' + fbToWeek + '")'],
                                                                 ['Measure.[SS Mtrl Item W_Time] = ' + fbValue + ';']);
                    vdCommon.executeQuery("Batch Query" , queryStr);
                } else if ( result.cs.rowCount > 0 &&
                        result.cs.row(0).cell(result.cs.measureColumnIndex("SS Mtrl Item_Source")) == "NSCM" &&
                        result.cs.row(0).cell(result.cs.measureColumnIndex("SS Mtrl Item_Time Varying Flag")) == "N" &&
                        result.cs.row(0).cell(result.cs.measureColumnIndex("SS Mtrl Item W_Time.Lock")) != true ) {
                    var queryStr = vdCommon.createMeasureQuery(["&CWVUI",
                                                                    "[Location].[Location].[" + row.Location.Value + "]",
                                                                    "[Item Material].[Item Material].[" + row.Item.Value + "]",
                                                                    '[Time].[Week].[' + result.cs.row(0).cell(result.cs.memberColumnIndex("Time", "Week")).Name + ']'],
                                                                 ['Measure.[SS Mtrl Item W_Time] = ' + fbValue + ';']);
                    vdCommon.executeQuery("Batch Query" , queryStr);
                }
            }

            vdCommon.programEnd();
        } catch ( e ) {
            RuleOutputToUI = { Status : 'Error', Message : "Js Logic Error : " + e.message };
            return;
        }
    };

    var fn_addPlantCombo = function(o9Params){
        const commonLib = require('o9.NSCM.commonLib');
        const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
        const vdUtil = new commonLib.VdUtil();
        vdCommon.setLogLevel("Debug");

        vdCommon.printParams(o9Params);

        // 파라미터 가져오기
        var parsedParams = JSON.parse(o9Params);
        var fbMSL5 = parsedParams.fbMSL5;

        var msl5 = "";
        if ( fbMSL5 != "All" ) {
            msl5 = ".[" + fbMSL5 + "]";
        }

        var comboList = [];
        var result = vdCommon.selectList(["&NSUILocationMFMtrlView"],
                                         [],
                                         'where { &CWVUI, [Item Material].[MSL5]' + msl5 + ', Measure.[Item Mtrl Site Asn_Cur Status] in {"ACTIVE","PLANNED"} }',
                                         "",
                                         "");
        var comboList = vdCommon.fn_makeCombo(result, {DimName : "Location", DimAttbName : "Location", isDisplayNameWithCode : true, existAll : true});
        vdCommon.debug("ComboData : " + JSON.stringify(comboList));

        vdCommon.programEnd();

        return comboList;
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

                vdCommon.deleteMeasure(["&CWVUI",
                                            "Location.[Location].[" + row.Location.Value + "]",
                                            "[Item Material].[Item Material].[" + row.Item.Value + "]"],
                                        "SS Mtrl Item");

                vdCommon.deleteMeasure(["&CWVUI",
                                            "Location.[Location].[" + row.Location.Value + "]",
                                            "[Item Material].[Item Material].[" + row.Item.Value + "]"],
                                        "SS Mtrl Item W");
            }

            vdCommon.programEnd();
        } catch ( e ) {
            RuleOutputToUI = { Status : 'Error', Message : "Js Logic Error : " + e.message };
            return;
        }
    };

    return {
        fn_addCombo1 : fn_addCombo1,
        fn_addCombo2 : fn_addCombo2,
        fn_addCombo3 : fn_addCombo3,
        fn_addCombo4 : fn_addCombo4,
        fn_addCombo5 : fn_addCombo5,
        fn_addComboItem : fn_addComboItem,
        fn_add : fn_add,
        //fn_sourceErpValidation : fn_sourceErpValidation,
        //fn_sourceNscmValidation, fn_sourceNscmValidation,
        //fn_sourceTimeYValidation : fn_sourceTimeYValidation,
        //fn_sourceTimeNValidation : fn_sourceTimeNValidation,
        //fn_sourceEcpOnValidation : fn_sourceEcpOnValidation,
        //fn_sourceEcpOffValidation : fn_sourceEcpOffValidation,
        fn_ditto : fn_ditto,
        fn_sourceCombo : fn_sourceCombo,
        fn_ecpCombo : fn_ecpCombo,
        fn_timeVaryingCombo : fn_timeVaryingCombo,
        fn_sourceChange : fn_sourceChange,
        fn_ecpChange : fn_ecpChange,
        fn_timeVaryingChange : fn_timeVaryingChange,
        fn_ditto_V2 : fn_ditto_V2,
        fn_addPlantCombo : fn_addPlantCombo,
        fn_delete : fn_delete
    };
});

/**************************** o9.NSCM.JSSSMtrlItem ****************************
    2025-03-28 : fn_ditto 기능 추가
    2025-04-08 : fn_addCombo4 추가
    2025-04-14 : fn_sourceChange, fn_ecpChange, fn_timeVaryingChange 기능 추가
    2025-04-16 : fn_ditto_V2 기능 추가
    2025-04-24 : Item 영역에서 추가시 Location 도 선택 가능하게 하고, 삭제 기능도 추가
                    fn_addPlantCombo, fn_delete 추가
                    fn_add 수정
*********************************************************************/