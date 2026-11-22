define('o9.NSCM.JSSetGroupFrozen', ['o9/data/query', 'o9/data/cellset', 'o9.NSCM.commonLib'], function () {
    const programName = "o9.NSCM.JSSetGroupFrozen";

    var fn_fromSiteNameCombo = function(o9Params){
        try {
            const commonLib = require('o9.NSCM.commonLib');
            const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
            vdCommon.setLogLevel("Debug");

            /* 25.2.25 : 속도개선으로 쿼리 변경
            var result = vdCommon.selectList(["&CWVUI", "&SETLocation", "[Sub Location].[Sub Location]", "[Trans Mode].[Trans Mode]"],
                                             ["Measure.[BOD List_BOD Valid]",
                                                "Measure.[BOD List_Eff Enddate]",
                                                "Measure.[BOD List_Eff Startdate]"],
                                             'where {Measure.[BOD List_BOD Valid] == "Y", coalesce(Measure.[BOD List_Eff Startdate],DATEADD(Now(),-1,"Day")) < now(), coalesce(Measure.[BOD List_Eff Enddate],DATEADD(Now(),1,"Day")) > now()}',
                                             "",
                                             "");
            */
            var result = vdCommon.selectList(["&SETLocation"],
                                             ["Measure.[BOD List_BOD Valid]"],
                                             'where { &CWVUI, [Sub Location].[Sub Location], [Trans Mode].[Trans Mode], ' +
                                                'Measure.[BOD List_BOD Valid] == "Y", ' +
                                                'coalesce(Measure.[BOD List_Eff Startdate],DATEADD(Now(),-1,"Day")) < now(), ' +
                                                'coalesce(Measure.[BOD List_Eff Enddate],DATEADD(Now(),1,"Day")) > now()}',
                                             "",
                                             "");
            vdCommon.printCsData(result, 3);

            var comboList = vdCommon.fn_makeCombo(result, {DimName : "Location", DimAttbName : "Location", Sort : "DisplayName", isDisplayNameWithCode : true});
            vdCommon.debug("ComboData : " + JSON.stringify(comboList));


            vdCommon.programEnd();

            return comboList;
        } catch ( e ) {
            RuleOutputToUI = { Status : 'Error', Message : "Js Logic Error : " + e.message };
            return;
        }
    };

    var fn_categoryCombo = function(o9Params){
        try {
            const commonLib = require('o9.NSCM.commonLib');
            const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
            vdCommon.setLogLevel("Debug");

            var comboList = vdCommon.fn_makeCombo(null, {ComboCodes : ["P Fix","P&SOP Fix"], ComboValues : ["P Fix","P&SOP Fix"]});
            vdCommon.debug("ComboData : " + JSON.stringify(comboList));

            vdCommon.programEnd();

            return comboList;
        } catch ( e ) {
            RuleOutputToUI = { Status : 'Error', Message : "Js Logic Error : " + e.message };
            return;
        }
    };

    var fn_toSiteNameCombo = function(o9Params){
        try {
            const commonLib = require('o9.NSCM.commonLib');
            const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
            vdCommon.setLogLevel("Debug");

            vdCommon.printParams(o9Params);

            // 파라미터 가져오기
            var parsedParams = JSON.parse(o9Params);
            var fbCategory = parsedParams.fbCategory;
            var fbFromSite = parsedParams.fbFromSite;

            if ( fbCategory == "P Fix" ) {
                var comboList = [];
                comboList.push({ Name : "-", DisplayName : "-"});
            } else {
                /* 25.2.25 : 속도개선으로 쿼리 변경
                var result = vdCommon.selectList(["&CWVUI",
                                                    "[Location].[Location].[" + fbFromSite + "]",
                                                    "&NSUISubLocationDC",
                                                    "[Trans Mode].[Trans Mode]"],
                                                 ["Measure.[BOD List_BOD Valid]",
                                                    "Measure.[BOD List_Eff Enddate]",
                                                    "Measure.[BOD List_Eff Startdate]"],
                                                 'where {Measure.[BOD List_BOD Valid] == "Y", coalesce(Measure.[BOD List_Eff Startdate],DATEADD(Now(),-1,"Day")) < now(), coalesce(Measure.[BOD List_Eff Enddate],DATEADD(Now(),1,"Day")) > now()}',
                                                 "",
                                                 "");
                */
                var result = vdCommon.selectList(["&NSUISubLocationDC"],
                                                 ["Measure.[BOD List_BOD Valid]"],
                                                 'where { &CWVUI, [Location].[Location].[' + fbFromSite + '], [Trans Mode].[Trans Mode], ' +
                                                    'Measure.[BOD List_BOD Valid] == "Y", ' +
                                                    'coalesce(Measure.[BOD List_Eff Startdate],DATEADD(Now(),-1,"Day")) < now(), ' +
                                                    'coalesce(Measure.[BOD List_Eff Enddate],DATEADD(Now(),1,"Day")) > now()}',
                                                 "",
                                                 "");
                vdCommon.printCsData(result, 3);

                var comboList = vdCommon.fn_makeCombo(result, {DimName : "Sub Location", DimAttbName : "Sub Location", existAll : true, Sort : "DisplayName", isDisplayNameWithCode : true});
            }

            vdCommon.debug("ComboData : " + JSON.stringify(comboList));

            vdCommon.programEnd();

            return comboList;
        } catch ( e ) {
            RuleOutputToUI = { Status : 'Error', Message : "Js Logic Error : " + e.message };
            return;
        }
    };

    var fn_productGroupCombo = function(o9Params){
        try {
            const commonLib = require('o9.NSCM.commonLib');
            const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
            vdCommon.setLogLevel("Debug");

            var result = vdCommon.selectList(["&SETItem.relatedmembers([Product Group])"],
                                             [],
                                             "",
                                             "",
                                             "");
            vdCommon.printCsData(result, 3);

            var comboList = vdCommon.fn_makeCombo(result, {DimName : "Item", DimAttbName : "Product Group", Sort : "DisplayName"});
            vdCommon.debug("ComboData : " + JSON.stringify(comboList));

            vdCommon.programEnd();

            return comboList;
        } catch ( e ) {
            RuleOutputToUI = { Status : 'Error', Message : "Js Logic Error : " + e.message };
            return;
        }
    };

    var fn_productCombo = function(o9Params){
        try {
            const commonLib = require('o9.NSCM.commonLib');
            const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
            vdCommon.setLogLevel("Debug");

            vdCommon.printParams(o9Params);

            // 파라미터 가져오기
            var parsedParams = JSON.parse(o9Params);
            var fbProductGroup = parsedParams.fbProductGroup;

            var result = vdCommon.selectList(["Item.[Product Group].[" + fbProductGroup + "]",
                                                "&SETItem.relatedmembers([Product])"],
                                             [],
                                             "",
                                             "",
                                             "");
            vdCommon.printCsData(result, 3);

            var comboList = vdCommon.fn_makeCombo(result, {DimName : "Item", DimAttbName : "Product", existAll : true, Sort : "DisplayName"});
            vdCommon.debug("ComboData : " + JSON.stringify(comboList));

            vdCommon.programEnd();

            return comboList;
        } catch ( e ) {
            RuleOutputToUI = { Status : 'Error', Message : "Js Logic Error : " + e.message };
            return;
        }
    };

    var fn_scmTypeCombo = function(o9Params){
        try {
            const commonLib = require('o9.NSCM.commonLib');
            const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
            vdCommon.setLogLevel("Debug");

            var comboList = vdCommon.fn_makeCombo(null, {ComboCodes : ["SET","OPTION"], ComboValues : ["SET","OPTION"]});
            vdCommon.debug("ComboData : " + JSON.stringify(comboList));

            vdCommon.programEnd();

            return comboList;
        } catch ( e ) {
            RuleOutputToUI = { Status : 'Error', Message : "Js Logic Error : " + e.message };
            return;
        }
    };

    var fn_inchCombo = function(o9Params){
        try {
            const commonLib = require('o9.NSCM.commonLib');
            const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
            vdCommon.setLogLevel("Debug");

            vdCommon.printParams(o9Params);

            // 파라미터 가져오기
            var parsedParams = JSON.parse(o9Params);
            var fbProductGroup = parsedParams.fbProductGroup;

            var result = vdCommon.selectList(["Item.[Product Group].[" + fbProductGroup + "]",
                                                "&SETItem.relatedmembers([Inch])"],
                                             [],
                                             "",
                                             "",
                                             "");
            vdCommon.printCsData(result, 3);

            var comboList = vdCommon.fn_makeCombo(result, {DimName : "Item", DimAttbName : "Inch", existAll : true, Sort : "DisplayName"});
            vdCommon.debug("ComboData : " + JSON.stringify(comboList));

            vdCommon.programEnd();

            return comboList;
        } catch ( e ) {
            RuleOutputToUI = { Status : 'Error', Message : "Js Logic Error : " + e.message };
            return;
        }
    };

    var fn_definitionCombo = function(o9Params){
        try {
            const commonLib = require('o9.NSCM.commonLib');
            const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
            vdCommon.setLogLevel("Debug");

            vdCommon.printParams(o9Params);

            // 파라미터 가져오기
            var parsedParams = JSON.parse(o9Params);
            var fbProductGroup = parsedParams.fbProductGroup;

            var result = vdCommon.selectList(["Item.[Product Group].[" + fbProductGroup + "]",
                                                "&SETItem.relatedmembers([Definition])"],
                                             [],
                                             "",
                                             "",
                                             "");
            vdCommon.printCsData(result, 3);

            var comboList = vdCommon.fn_makeCombo(result, {DimName : "Item", DimAttbName : "Definition", existAll : true, Sort : "DisplayName"});
            vdCommon.debug("ComboData : " + JSON.stringify(comboList));

            vdCommon.programEnd();

            return comboList;
        } catch ( e ) {
            RuleOutputToUI = { Status : 'Error', Message : "Js Logic Error : " + e.message };
            return;
        }
    };

    var fn_yearCombo = function(o9Params){
        try {
            const commonLib = require('o9.NSCM.commonLib');
            const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
            vdCommon.setLogLevel("Debug");

            vdCommon.printParams(o9Params);

            // 파라미터 가져오기
            var parsedParams = JSON.parse(o9Params);
            var fbProductGroup = parsedParams.fbProductGroup;

            var result = vdCommon.selectList(["&SETItem.relatedmembers([Year]).intersectwith(&NSUIItemYearComboView)"],
                                             [],
                                             "",
                                             "",
                                             "");
            vdCommon.printCsData(result, 3);

            var comboList = vdCommon.fn_makeCombo(result, {DimName : "Item", DimAttbName : "Year", existAll : true, Sort : "DisplayName"});
            vdCommon.debug("ComboData : " + JSON.stringify(comboList));

            vdCommon.programEnd();

            return comboList;
        } catch ( e ) {
            RuleOutputToUI = { Status : 'Error', Message : "Js Logic Error : " + e.message };
            return;
        }
    };

    var fn_marketingNameCombo = function(o9Params){
        try {
            const commonLib = require('o9.NSCM.commonLib');
            const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
            vdCommon.setLogLevel("Debug");

            vdCommon.printParams(o9Params);

            // 파라미터 가져오기
            var parsedParams = JSON.parse(o9Params);
            var fbProductGroup = parsedParams.fbProductGroup;

            var result = vdCommon.selectList(["Item.[Product Group].[" + fbProductGroup + "]",
                                                "&SETItem.relatedmembers([Marketing Name])"],
                                             [],
                                             "",
                                             "",
                                             "");
            vdCommon.printCsData(result, 3);

            var comboList = vdCommon.fn_makeCombo(result, {DimName : "Item", DimAttbName : "Marketing Name", existAll : true, Sort : "DisplayName"});
            vdCommon.debug("ComboData : " + JSON.stringify(comboList));

            vdCommon.programEnd();

            return comboList;
        } catch ( e ) {
            RuleOutputToUI = { Status : 'Error', Message : "Js Logic Error : " + e.message };
            return;
        }
    };

    var fn_digitCombo = function(o9Params){
        try {
            const commonLib = require('o9.NSCM.commonLib');
            const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
            vdCommon.setLogLevel("Debug");

            var comboList = vdCommon.fn_makeCombo(null, {ComboCodes : ["1","2","3","4","5","6","7","8","9","10","11","12","13","14"], ComboValues : ["1","2","3","4","5","6","7","8","9","10","11","12","13","14"], existAll : true});
            vdCommon.debug("ComboData : " + JSON.stringify(comboList));

            vdCommon.programEnd();

            return comboList;
        } catch ( e ) {
            RuleOutputToUI = { Status : 'Error', Message : "Js Logic Error : " + e.message };
            return;
        }
    };

    var fn_add = function(o9Params){
        try {
            const commonLib = require('o9.NSCM.commonLib');
            const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
            const vdUtil = new commonLib.VdUtil();

            vdCommon.setLogLevel("Debug");

            vdCommon.printParams(o9Params);

            // 파라미터 가져오기
            var parsedParams = JSON.parse(o9Params);
            var fbFromSite = parsedParams.fbFromSite;
            var fbToSite = parsedParams.fbToSite;
            var fbCategory = parsedParams.fbCategory;
            var fbProductGroup = parsedParams.fbProductGroup;
            var fbProduct = parsedParams.fbProduct;
            var fbScmType = parsedParams.fbScmType;
            var fbInch = parsedParams.fbInch;
            var fbDefinition = parsedParams.fbDefinition;
            var fbYear = parsedParams.fbYear;
            var fbMarketingName = parsedParams.fbMarketingName;
            var fbDigit = parsedParams.fbDigit;

            vdCommon.printStep("Group ID Max");

            // Max 값을 구한다.
            var result = vdCommon.selectList(["[Group].[Group Type].[MFF_S] * [Group].[Group ID].filter(#.Name startswith([MFF_S_]))"],
                                                [],
                                                "",
                                                "orderby [Group].[Group ID].Name desc",
                                                "limit 1");
            var groupId = "";
            if ( result.cs.rowCount == 0 ) {
                groupId = "MFF_S_" + vdUtil.fn_lpad("1", 5, "0");
            } else {
                groupId = "MFF_S_" + vdUtil.fn_lpad((parseInt(result.cs.row(0).cell(result.cs.memberColumnIndex("Group", "Group ID")).Name.substr(6)) + 1) + "", 5, "0");
            }
            /* 필요없는 로직
            // Member 를 추가한다.
            if ( !vdCommon.existMember("[Group].[Group ID]", groupId) ) {
                vdCommon.createMember("[Group].[Group ID]", groupId);
            }
            */
            // Dimension 을  추가한다.
            if ( !vdCommon.existDimension(['[Group].[Group Type].[MFF_S]','[Group].[Group ID].[' + groupId + ']']) ) {
                vdCommon.createDimension(['[Group].[Group Type]','[Group].[Group Name]','[Group].[Group ID]'], ["MFF_S", groupId, groupId]);
            }

            vdCommon.printStep("Measure Add");
            vdCommon.createMeasure(["&CWVUI",
                                    "[Group].[Group ID].[" + groupId + "]"],
                                    ['Measure.[SOP Frozen Grp SET_From Site] = "' + fbFromSite + '";',
                                    'Measure.[SOP Frozen Grp SET_From Site Name] = "' + vdCommon.fn_getCodeName("Location", fbFromSite) + '";',
                                    'Measure.[SOP Frozen Grp SET_Ctg] = "' + fbCategory + '";',
                                    'Measure.[SOP Frozen Grp SET_To Site] = "' + fbToSite + '";',
                                    'Measure.[SOP Frozen Grp SET_To Site Name] = "' + vdCommon.fn_getCodeName("Location", fbToSite) + '";',
                                    'Measure.[SOP Frozen Grp SET_Prod Grp] = "' + fbProductGroup + '";',
                                    'Measure.[SOP Frozen Grp SET_Product] = "' + fbProduct + '";',
                                    'Measure.[SOP Frozen Grp SET_SCM Type] = "' + fbScmType + '";',
                                    'Measure.[SOP Frozen Grp SET_Inch] = "' + fbInch + '";',
                                    'Measure.[SOP Frozen Grp SET_Definition] = "' + fbDefinition + '";',
                                    'Measure.[SOP Frozen Grp SET_Year] = "' + fbYear + '";',
                                    'Measure.[SOP Frozen Grp SET_Mkt Name] = "' + fbMarketingName + '";',
                                    'Measure.[SOP Frozen Grp SET_Digit] = "' + fbDigit + '";',
                                    'Measure.[SOP Frozen Grp SET_Total Flag] = "N";',
                                    'Measure.[SOP Frozen Grp SET_Valid Flag] = "Y";']);

            // 파이썬 실행
            var execQuery = 'EXEC plugin instance [PY_MG_SOPFrozenList] ' +
                            'for measures {[SOP Frozen List_Ctg]} ' +
                            'using scope ( &MPV * ' +
                                ( fbProductGroup != "All" ? 'Item.[Product Group]' + vdUtil.fn_filterStr(fbProductGroup) + ' * ' : "" ) +
                                ( fbProduct != "All" ? 'Item.[Product]' + vdUtil.fn_filterStr(fbProduct) + ' * ' : "" ) +
                                ( fbScmType != "All" ? 'Item.[SCM Type]' + vdUtil.fn_filterStr(fbScmType) + ' * ' : "" ) +
                                ( fbInch != "All" ? 'Item.[Inch]' + vdUtil.fn_filterStr(fbInch) + ' * ' : "" ) +
                                ( fbDefinition != "All" ? 'Item.[Definition]' + vdUtil.fn_filterStr(fbDefinition) + ' * ' : "" ) +
                                ( fbYear != "All" ? 'Item.[Year]' + vdUtil.fn_filterStr(fbYear) + ' * ' : "" ) +
                                ( fbMarketingName != "All" ? 'Item.[Marketing Name]' + vdUtil.fn_filterStr(fbMarketingName) + ' * ' : "" ) +
                                '[Group].[Group ID].[' + groupId + '] * ' +
                                '[Location].[Location].[' + fbFromSite + '] ) ' +
                            'using arguments {("IncludeNullRows", "False"), (ParamOutVersion, "CWV_MP"),(ExecutionMode, "MediumWeight"), (MaxSliceTableCells, 200000000), (MaxConcurrency, 1 )};'
            vdCommon.executeQuery("Py Run", execQuery);

            //EXEC plugin instance [PY_MG_SOPFrozenList]
            //for measures {[SOP Frozen List_Ctg]}
            //using scope ( &MPV * Group.[Group Type].[MFF_S].relatedmembers([Group ID]) )
            //using arguments {("IncludeNullRows", "False"), (ParamOutVersion, "CWV_MP"), (pLogInfo, "CWV_MP;PY_MG_SOPFrozenList;5"), (ExecutionMode, "MediumWeight"), (MaxSliceTableCells, 200000000), (MaxConcurrency, 1 )};

            vdCommon.programEnd();
        } catch ( e ) {
            RuleOutputToUI = { Status : 'Error', Message : "Js Logic Error : " + e.message };
            return;
        }
    };

    var fn_change = function(o9Params){
        try {
            const commonLib = require('o9.NSCM.commonLib');
            const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
            const vdUtil = new commonLib.VdUtil();

            vdCommon.setLogLevel("Debug");

            vdCommon.printParams(o9Params);

            // 파라미터 가져오기
            var parsedParams = JSON.parse(o9Params);
            var fbGroupId = parsedParams.fbGroupId;
            var fbFromSite = parsedParams.fbFromSite;
            var fbToSite = parsedParams.fbToSite;
            var fbCategory = parsedParams.fbCategory;
            var fbProductGroup = parsedParams.fbProductGroup;
            var fbProduct = parsedParams.fbProduct;
            var fbScmType = parsedParams.fbScmType;
            var fbInch = parsedParams.fbInch;
            var fbDefinition = parsedParams.fbDefinition;
            var fbYear = parsedParams.fbYear;
            var fbMarketingName = parsedParams.fbMarketingName;
            var fbDigit = parsedParams.fbDigit;

            vdCommon.createMeasure(["&CWVUI",
                                    "[Group].[Group ID].[" + fbGroupId + "]"],
                                    ['Measure.[SOP Frozen Grp SET_From Site] = "' + fbFromSite + '";',
                                    'Measure.[SOP Frozen Grp SET_From Site Name] = "' + vdCommon.fn_getCodeName("Location", fbFromSite) + '";',
                                    'Measure.[SOP Frozen Grp SET_Ctg] = "' + fbCategory + '";',
                                    'Measure.[SOP Frozen Grp SET_To Site] = "' + fbToSite + '";',
                                    'Measure.[SOP Frozen Grp SET_To Site Name] = "' + vdCommon.fn_getCodeName("Location", fbToSite) + '";',
                                    'Measure.[SOP Frozen Grp SET_Prod Grp] = "' + fbProductGroup + '";',
                                    'Measure.[SOP Frozen Grp SET_Product] = "' + fbProduct + '";',
                                    'Measure.[SOP Frozen Grp SET_SCM Type] = "' + fbScmType + '";',
                                    'Measure.[SOP Frozen Grp SET_Inch] = "' + fbInch + '";',
                                    'Measure.[SOP Frozen Grp SET_Definition] = "' + fbDefinition + '";',
                                    'Measure.[SOP Frozen Grp SET_Year] = "' + fbYear + '";',
                                    'Measure.[SOP Frozen Grp SET_Mkt Name] = "' + fbMarketingName + '";',
                                    'Measure.[SOP Frozen Grp SET_Digit] = "' + fbDigit + '";']);

            vdCommon.programEnd();
        } catch ( e ) {
            RuleOutputToUI = { Status : 'Error', Message : "Js Logic Error : " + e.message };
            return;
        }
    };

    var fn_delete = function(o9Params){
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

                vdCommon.deleteMeasure(["&CWVUI", "[Group].[Group ID].[" + row.GroupId.Value + "]"], "SOP Frozen Grp SET");
                vdCommon.deleteMeasure(["&CWVUI", "[Group].[Group ID].[" + row.GroupId.Value + "]"], "SOP Frozen List");
            }

            vdCommon.programEnd();
        } catch ( e ) {
            RuleOutputToUI = { Status : 'Error', Message : "Js Logic Error : " + e.message };
            return;
        }
    };

    return {
        fn_fromSiteNameCombo : fn_fromSiteNameCombo,
        fn_toSiteNameCombo : fn_toSiteNameCombo,
        fn_categoryCombo : fn_categoryCombo,
        fn_productGroupCombo : fn_productGroupCombo,
        fn_productCombo : fn_productCombo,
        fn_scmTypeCombo : fn_scmTypeCombo,
        fn_inchCombo : fn_inchCombo,
        fn_definitionCombo : fn_definitionCombo,
        fn_yearCombo : fn_yearCombo,
        fn_marketingNameCombo : fn_marketingNameCombo,
        fn_digitCombo : fn_digitCombo,
        fn_add : fn_add,
        fn_change : fn_change,
        fn_delete : fn_delete
    };
});

/**************************** o9.NSCM.JSSetGroupFrozen ****************************
    2025-02-25 : 속도개선으로 쿼리 변경
    2025-04-30 : fn_delete : 멀티 선택으로 수정
*********************************************************************/