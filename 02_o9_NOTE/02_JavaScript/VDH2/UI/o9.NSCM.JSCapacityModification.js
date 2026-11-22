define('o9.NSCM.JSCapacityModification', ['o9/data/query', 'o9/data/cellset', 'o9.NSCM.commonLibVD'], function () {
	const programName = "o9.NSCM.JSCapacityModification";
    const commonLib = require('o9.NSCM.commonLib');
    const vdUtil = new commonLib.VdUtil();
    const log = new commonLib.VdCommon(programName);
    log.setLogLevel("Debug");

    var fn_cb_location = function(o9Params){
        const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
        vdCommon.setLogLevel("Debug");
        vdCommon.printParams(o9Params);

        try {
            // 파라메타 가져오기
            let parsedParams = JSON.parse(o9Params);

            var result = vdCommon.selectList(["[Location].[Location]"], ["Measure.[W Resource Base Capacity backup Sim]"]
                                                ,"where { Version.[Version Name]" + vdUtil.fn_filterStr(parsedParams.fb_Version) +
                                                    ", Measure.[W Resource Base Capacity backup Sim] > 0 } "
                                                ,"", "");
            var comboList = vdCommon.fn_makeCombo(result, {DimName : "Location", DimAttbName : "Location"
                                                            ,Sort : "DisplayName"
                                                            ,isDisplayNameWithCode : true
                                                            ,existAll : true});

            vdCommon.debug("ComboData : " + JSON.stringify(comboList.slice(0,3)));

            vdCommon.programEnd();

            return comboList;
        } catch ( e ) {
            RuleOutputToUI = { Status : 'Error', Message : "Js Logic Error : " + e.message };
            return;
        }
    };

    var fn_cb_resourceline = function(o9Params){
        const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
        vdCommon.setLogLevel("Debug");
        vdCommon.printParams(o9Params);

        try {
            // 파라메타 가져오기
            let parsedParams = JSON.parse(o9Params);

            var result = vdCommon.selectList(["[Resource].[Resource Line]"], ["Measure.[W Resource Base Capacity backup Sim]"]
                                                ,"where { Version.[Version Name]" + vdUtil.fn_filterStr(parsedParams.fb_Version) +
                                                    ", Measure.[W Resource Base Capacity backup Sim] > 0 } "
                                                ,"", "");
            var comboList = vdCommon.fn_makeCombo(result, {DimName : "Resource", DimAttbName : "Resource Line"
                                                            ,Sort : "DisplayName"
                                                            ,isDisplayNameWithCode : true
                                                            ,existAll : true});

            vdCommon.debug("ComboData : " + JSON.stringify(comboList.slice(0,3)));

            vdCommon.programEnd();

            return comboList;
        } catch ( e ) {
            RuleOutputToUI = { Status : 'Error', Message : "Js Logic Error : " + e.message };
            return;
        }
    };

    var fn_addIndex = function(o9Params){
        const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
        vdCommon.setLogLevel("Debug");
        vdCommon.printParams(o9Params);

        try{
            // 파라메타 가져오기
            let parsedParams = JSON.parse(o9Params);

            // Max 값을 구한다.
            var result = vdCommon.selectList(["[Version].[Version Name]" + vdUtil.fn_filterStr(parsedParams.fb_Version),
                                                '[Seq].[Seq]'],
                                             ["Measure.[Scenario Capacity Mod_Created By]"],
                                             "",
                                             "orderby [Seq].[Seq].Key desc",
                                             "limit 1");
            var seq = "A1";
            if ( result.cs.rowCount > 0 ) {
                seq = "A" + (parseInt(result.cs.row(0).cell(result.cs.memberColumnIndex("Seq", "Seq")).Name.substr(1)) + 1);
            }

            var dimensions = [];
            dimensions.push(vdUtil.fn_qDim(null, "[Version].[Version Name]", parsedParams.fb_Version));
            dimensions.push(vdUtil.fn_qDim(null, "[Seq].[Seq]", seq));

            var measures = [];
            measures.push(vdUtil.fn_qMeaStr(null, "Measure.[Scenario Capacity Mod_Location]", fn_convertMultiValue(parsedParams.fb_Location)));
            measures.push(vdUtil.fn_qMeaStr(null, "Measure.[Scenario Capacity Mod_Resource Line]", fn_convertMultiValue(parsedParams.fb_ResourceLine)));
            measures.push('Measure.[Scenario Capacity Mod_Override Seq] = 99;');
            measures.push('Measure.[Scenario Capacity Mod_Created By] = CurrentUser().[User Name];');
            measures.push(vdUtil.fn_qMeaUpdateTime("Measure.[Scenario Capacity Mod_Created Time]"));
            measures.push('Measure.[Scenario Capacity Mod_Updated By] = CurrentUser().[User Name];');
            measures.push(vdUtil.fn_qMeaUpdateTime("Measure.[Scenario Capacity Mod_Update Time]"));

            vdCommon.createMeasure(dimensions, measures);

            vdCommon.programEnd();
        }catch ( e ) {
            RuleOutputToUI = { Status : 'Error', Message : "Js Logic Error : " + e.message };
            return;
        }
    }

    var fn_editValidation = function(o9Params){
        const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
        vdCommon.setLogLevel("Debug");
        vdCommon.printParams(o9Params);

        var rtn = 0;

        try {
            // 파라미터 가져오기
            var parsedParams = JSON.parse(o9Params);

            vdCommon.debug(parsedParams.VersionSeq.length);
            if ( parsedParams.VersionSeq.length > 1 ) {
                RuleOutputToUI = { Status : 'Error', Message : "수정 할 row 하나만 선택 해주세요." };
                rtn = 1;
            } else{
                var CurrentWeek = vdCommon.selectResult('&CurrentWeek.element(0).DisplayName');
                vdCommon.debug("CurrentWeek : " + CurrentWeek);
                vdCommon.debug(parsedParams.VersionSeq[0]["Version"].Value.substr(0,6));
                // 당주인지 체크
                if ( CurrentWeek != parsedParams.VersionSeq[0]["Version"].Value.substr(0,6) ) {
                    RuleOutputToUI = { Status : 'Error', Message : "당주 Plan으로 다시 선택하세요." };
                    rtn = 1;
                }
            }

            vdCommon.programEnd();
        } catch ( e ) {
            RuleOutputToUI = { Status : 'Error', Message : "Js Logic Error : " + e.message };
            return 1;
        }

        return rtn;
    };

    var fn_copyValidation = function(o9Params){
        const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
        vdCommon.setLogLevel("Debug");
        vdCommon.printParams(o9Params);

        var rtn = 0;

        try {
            // 파라미터 가져오기
            var parsedParams = JSON.parse(o9Params);

            vdCommon.debug(parsedParams.VersionSeq.length);
            if ( parsedParams.VersionSeq.length > 1 ) {
                RuleOutputToUI = { Status : 'Error', Message : "복사 할 row 하나만 선택 해주세요." };
                rtn = 1;
            }

            vdCommon.programEnd();
        } catch ( e ) {
            RuleOutputToUI = { Status : 'Error', Message : "Js Logic Error : " + e.message };
            return 1;
        }

        return rtn;
    };

    var fn_applyValidation = function(o9Params){
        const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
        vdCommon.setLogLevel("Debug");
        vdCommon.printParams(o9Params);

        var rtn = 0;

        try {
            // 파라미터 가져오기
            var parsedParams = JSON.parse(o9Params);

            vdCommon.debug(parsedParams.Version.length);
            if ( parsedParams.Version.length > 1 ) {
                RuleOutputToUI = { Status : 'Error', Message : "Plan을 하나만 선택해주세요." };
                rtn = 1;
            } else {
                var CurrentWeek = vdCommon.selectResult('&CurrentWeek.element(0).DisplayName');
                vdCommon.debug("CurrentWeek : " + CurrentWeek);
                // 당주인지 체크
                if ( CurrentWeek != parsedParams.Version[0].substr(0,6) ) {
                    RuleOutputToUI = { Status : 'Error', Message : "당주 Plan으로 다시 선택하세요." };
                    rtn = 1;
                }
            }

            vdCommon.programEnd();
        } catch ( e ) {
            RuleOutputToUI = { Status : 'Error', Message : "Js Logic Error : " + e.message };
            return 1;
        }

        return rtn;
    };

    var fn_editIndex = function(o9Params){
        const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
        vdCommon.setLogLevel("Debug");
        vdCommon.printParams(o9Params);

        try{
            // 파라메타 가져오기
            let parsedParams = JSON.parse(o9Params);

            var dimensions = [];
            dimensions.push("[Version].[Version Name]" + vdUtil.fn_filterStr(parsedParams.fb_Version));
            dimensions.push("[Seq].[Seq]" + vdUtil.fn_filterStrForDN(parsedParams.fb_Seq));

            var measures = [];
            measures.push(vdUtil.fn_qMeaStr(null, "Measure.[Scenario Capacity Mod_Location]", fn_convertMultiValue(parsedParams.fb_Location)));
            measures.push(vdUtil.fn_qMeaStr(null, "Measure.[Scenario Capacity Mod_Resource Line]", fn_convertMultiValue(parsedParams.fb_ResourceLine)));
            measures.push('Measure.[Scenario Capacity Mod_Updated By] = CurrentUser().[User Name];');
            measures.push(vdUtil.fn_qMeaUpdateTime("Measure.[Scenario Capacity Mod_Update Time]"));

            vdCommon.updateMeasure(dimensions, measures);

            vdCommon.programEnd();
        }catch ( e ) {
            RuleOutputToUI = { Status : 'Error', Message : "Js Logic Error : " + e.message };
            return;
        }
    }

    var fn_copyIndex = function(o9Params){
        const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
        vdCommon.setLogLevel("Debug");
        vdCommon.printParams(o9Params);

        try{
            // 파라메타 가져오기
            let parsedParams = JSON.parse(o9Params);

            // Max 값을 구한다.
            var result = vdCommon.selectList(["[Version].[Version Name]" + vdUtil.fn_filterStr(parsedParams.fb_TargetVersion),
                                                '[Seq].[Seq]'],
                                             ["Measure.[Scenario Capacity Mod_Created By]"],
                                             "",
                                             "orderby [Seq].[Seq].Key desc",
                                             "limit 1");
            var seq = "A0";
            if ( result.cs.rowCount > 0 ) {
                seq = result.cs.row(0).cell(result.cs.memberColumnIndex("Seq", "Seq")).Name;
            }

            result = vdCommon.selectList(["[Version].[Version Name]" + vdUtil.fn_filterStr(parsedParams.fb_Version),
                                            '[Seq].[Seq]' + vdUtil.fn_filterStrForDN(parsedParams.fb_Seq)],
                                         ["Measure.[Scenario Capacity Mod_Location]",
                                            "Measure.[Scenario Capacity Mod_Resource Line]",
                                            "Measure.[Scenario Capacity Mod_Description]",
                                            "Measure.[Scenario Capacity Mod_From Week]",
                                            "Measure.[Scenario Capacity Mod_To Week]",
                                            "Measure.[Scenario Capacity Mod_Base Rate]",
                                            "Measure.[Scenario Capacity Mod_Flex1 Rate]",
                                            "Measure.[Scenario Capacity Mod_Flex2 Rate]"],
                                         "",
                                         "",
                                         "");
            for ( var i = 0; i < result.cs.rowCount; i++ ) {
                // seq 증가
                seq = "A" + (parseInt(seq.substr(1)) + 1);

                var dimensions = [];
                dimensions.push(vdUtil.fn_qDim(null, "[Version].[Version Name]", parsedParams.fb_TargetVersion));
                dimensions.push(vdUtil.fn_qDim(null, "[Seq].[Seq]", seq));

		value = vdUtil.fn_getString(result.cs.row(i).cell(result.cs.measureColumnIndex("Scenario Capacity Mod_Description")));

		if ( value === "" ) {
		    RuleOutputToUI = { Status : 'Error', Message : "Please enter the description"};
                    return;
		}

                value1 = vdUtil.fn_getString(result.cs.row(i).cell(result.cs.measureColumnIndex("Scenario Capacity Mod_From Week")));
                value2 = vdUtil.fn_getString(result.cs.row(i).cell(result.cs.measureColumnIndex("Scenario Capacity Mod_To Week")));
                value3 = vdUtil.fn_getString(result.cs.row(i).cell(result.cs.measureColumnIndex("Scenario Capacity Mod_Base Rate")));
                value4 = vdUtil.fn_getString(result.cs.row(i).cell(result.cs.measureColumnIndex("Scenario Capacity Mod_Flex1 Rate")));
                value5 = vdUtil.fn_getString(result.cs.row(i).cell(result.cs.measureColumnIndex("Scenario Capacity Mod_Flex2 Rate")));

		if ( value1 === "" || value2 === "" || value3 === "" || value4 === "" || value5 === "" ) {
		    RuleOutputToUI = { Status : 'Error', Message : "Please enter From Week, To Week, Base, Flex1, and Flex2 Rate"};
                    return;
		}

                var measures = [];
                measures.push(vdUtil.fn_qMeaStr(null, "Measure.[Scenario Capacity Mod_Location]", result.cs.row(i).cell(result.cs.measureColumnIndex("Scenario Capacity Mod_Location"))));
                measures.push(vdUtil.fn_qMeaStr(null, "Measure.[Scenario Capacity Mod_Resource Line]", result.cs.row(i).cell(result.cs.measureColumnIndex("Scenario Capacity Mod_Resource Line"))));
                measures.push('Measure.[Scenario Capacity Mod_Override Seq] = 99;');
                measures.push('Measure.[Scenario Capacity Mod_From Week] = ' + vdUtil.fn_getString(vdUtil.fn_getMeaValue(result, i, "Scenario Capacity Mod_From Week")) + ';');
                measures.push('Measure.[Scenario Capacity Mod_To Week] = ' + vdUtil.fn_getString(vdUtil.fn_getMeaValue(result, i, "Scenario Capacity Mod_To Week")) + ';');
                measures.push('Measure.[Scenario Capacity Mod_Base Rate] = ' + vdUtil.fn_getString(vdUtil.fn_getMeaValue(result, i, "Scenario Capacity Mod_Base Rate")) + ';');
                measures.push('Measure.[Scenario Capacity Mod_Flex1 Rate] = ' + vdUtil.fn_getString(vdUtil.fn_getMeaValue(result, i, "Scenario Capacity Mod_Flex1 Rate")) + ';');
                measures.push('Measure.[Scenario Capacity Mod_Flex2 Rate] = ' + vdUtil.fn_getString(vdUtil.fn_getMeaValue(result, i, "Scenario Capacity Mod_Flex2 Rate")) + ';');
                measures.push('Measure.[Scenario Capacity Mod_Created By] = CurrentUser().[User Name];');
                measures.push('Measure.[Scenario Capacity Mod_Updated By] = CurrentUser().[User Name];');
                measures.push(vdUtil.fn_qMeaUpdateTime("Measure.[Scenario Capacity Mod_Created Time]"));
                measures.push(vdUtil.fn_qMeaUpdateTime("Measure.[Scenario Capacity Mod_Update Time]"));
                measures.push(vdUtil.fn_qMeaStr(null, "Measure.[Scenario Capacity Mod_Description]", result.cs.row(i).cell(result.cs.measureColumnIndex("Scenario Capacity Mod_Description"))));

                vdCommon.createMeasure(dimensions, measures);
            }

            vdCommon.programEnd();
        }catch ( e ) {
            RuleOutputToUI = { Status : 'Error', Message : "Js Logic Error : " + e.message };
            return;
        }
    }

    var fn_deleteIndex = function(o9Params){
        try {
            const commonLib = require('o9.NSCM.commonLib');
            const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
            const vdUtil = new commonLib.VdUtil();

            vdCommon.setLogLevel("Debug");

            vdCommon.printParams(o9Params);

            // 파라미터 가져오기
            var parsedParams = JSON.parse(o9Params);

            vdCommon.deleteMeasure(["[Version].[Version Name]" + vdUtil.fn_filterStr(parsedParams.fb_Version),
                                        "[Seq].[Seq]" + vdUtil.fn_filterStrForDN(parsedParams.fb_Seq)],
                                    "Scenario Capacity Modification");

            vdCommon.programEnd();
        } catch ( e ) {
            RuleOutputToUI = { Status : 'Error', Message : "Js Logic Error : " + e.message };
            return;
        }
    };

    var fn_apply = function(o9Params){
        const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
        vdCommon.setLogLevel("Debug");
        vdCommon.printParams(o9Params);

        try{
            // 파라메타 가져오기
            let parsedParams = JSON.parse(o9Params);

            var value = "";
            var result = vdCommon.selectList(["[Version].[Version Name]" + vdUtil.fn_filterStr(parsedParams.fb_Version),
                                                '[Seq].[Seq]'],
                                             ["Measure.[Scenario Capacity Mod_Location]", "Measure.[Scenario Capacity Mod_Resource Line]",
                                                "Measure.[Scenario Capacity Mod_From Week]", "Measure.[Scenario Capacity Mod_To Week]",
                                                "Measure.[Scenario Capacity Mod_Base Rate]", "Measure.[Scenario Capacity Mod_Flex1 Rate]",
                                                "Measure.[Scenario Capacity Mod_Flex2 Rate]", "Measure.[Scenario Capacity Mod_Override Seq]"],
                                             "",
                                             "orderby Measure.[Scenario Capacity Mod_Override Seq] desc, Seq.Seq.Key desc",
                                             "");
            for ( var i = 0; i < result.cs.rowCount; i++ ) {
                value = vdUtil.fn_getString(vdUtil.fn_getMeaValue(result, i, "Scenario Capacity Mod_Base Rate"));
                value1 = vdUtil.fn_getString(vdUtil.fn_getMeaValue(result, i, "Scenario Capacity Mod_Flex1 Rate"));
                value2 = vdUtil.fn_getString(vdUtil.fn_getMeaValue(result, i, "Scenario Capacity Mod_Flex2 Rate"));

                if ( value === "" ) {
                    RuleOutputToUI = { Status : 'Error', Message : "Please enter the Base Rate value"};
                    return;
                }
                if ( value1 === "" ) {
                    RuleOutputToUI = { Status : 'Error', Message : "Please enter the Flex1 Rate value"};
                    return;
                }
                if ( value2 === "" ) {
                    RuleOutputToUI = { Status : 'Error', Message : "Please enter the Flex2 Rate value"};
                    return;
                }
            }

            vdCommon.updateMeasure(["[Version].[Version Name]" + vdUtil.fn_filterStr(parsedParams.fb_Version)]
                        ,['Measure.[W Resource Base Capacity] = Measure.[W Resource Base Capacity backup Sim];'
                            ,'Measure.[W Flex Capacity Band1] = Measure.[W Flex Capacity Band1 backup Sim];'
                            ,'Measure.[W Flex Capacity Band2] = Measure.[W Flex Capacity Band2 backup Sim];'
                            ]);

            for ( var i = 0; i < result.cs.rowCount; i++ ) {
                var dimensions = [];
                dimensions.push(vdUtil.fn_qDim(null, "[Version].[Version Name]", parsedParams.fb_Version));

                value = vdUtil.fn_getString(vdUtil.fn_getMeaValue(result, i, "Scenario Capacity Mod_Location"));
                    dimensions.push("[Location].[Location]" + ( value == "All" ? "" : vdUtil.fn_filterStr(value.split("^"))));
                value = vdUtil.fn_getString(vdUtil.fn_getMeaValue(result, i, "Scenario Capacity Mod_Resource Line"));
                    dimensions.push("[Resource].[Resource Line]" + ( value == "All" ? "" : vdUtil.fn_filterStr(value.split("^"))) + ".relatedmembers([Resource])");

                // 주차 설정
                var from = vdUtil.fn_getString(vdUtil.fn_getMeaValue(result, i, "Scenario Capacity Mod_From Week"));
                var to = vdUtil.fn_getString(vdUtil.fn_getMeaValue(result, i, "Scenario Capacity Mod_To Week"));

                // 주차 로직 걸기
                if ( from != "" && to != "" ) {
                    dimensions.push('[Time].[Week].filter(#.Name >= "' + from + '" && #.Name <= "' + to + '")');
                } else if ( from != "" && to == "" ) {
                    dimensions.push('[Time].[Week].filter(#.Name >= "' + from + '")');
                } else if ( from == "" && to != "" ) {
                    dimensions.push('[Time].[Week].filter(#.Name <= "' + to + '")');
                }

                var measures = [];
                value = vdUtil.fn_getMeaValue(result, i, "Scenario Capacity Mod_Base Rate");
                measures.push('Measure.[W Resource Base Capacity] = round(Measure.[W Resource Base Capacity backup Sim] * ' + value + ');');
                value = vdUtil.fn_getMeaValue(result, i, "Scenario Capacity Mod_Flex1 Rate");
                measures.push('Measure.[W Flex Capacity Band1] = round(Measure.[W Flex Capacity Band1 backup Sim] * ' + value + ');');
                value = vdUtil.fn_getMeaValue(result, i, "Scenario Capacity Mod_Flex2 Rate");
                measures.push('Measure.[W Flex Capacity Band2] = round(Measure.[W Flex Capacity Band2 backup Sim] * ' + value + ');');

                vdCommon.updateMeasure(dimensions, measures);
            }

            vdCommon.programEnd();
        }catch ( e ) {
            RuleOutputToUI = { Status : 'Error', Message : "Js Logic Error : " + e.message };
            return;
        }
    }

    var fn_convertMultiValue = function(val){
        if ( val === null ) {
            return "All";
        } else if ( typeof(val) == "string" ) {
            return val;
        } else {
            if ( val.includes("All") ) {
                return "All";
            } else {
                return val.join("^");
            }
        }
    }

    // All 과 다른것을 같이 멀티로 선택할 경우 공통을 타면 문제가 있어 따로 만듬
    var fn_localFilter = function(val) {
        if ( val.includes("All") ) {
            return "";
        } else {
            return vdUtil.fn_filterStr(val);
        }
    }

    return {
        fn_cb_location : fn_cb_location,
        fn_cb_resourceline : fn_cb_resourceline,
        fn_addIndex : fn_addIndex,
        fn_editValidation : fn_editValidation,
        fn_copyValidation : fn_copyValidation,
        fn_applyValidation : fn_applyValidation,
        fn_editIndex : fn_editIndex,
        fn_copyIndex : fn_copyIndex,
        fn_deleteIndex : fn_deleteIndex,
        fn_apply : fn_apply
    };
});

/**************************************************************************************
프로그램명  : o9.NSCM.JSCapacityModification
화면명     : Capacity Modification
개발자     : sungmin0.lim
최초생성   : 2025.09.23
**************************************************************************************/