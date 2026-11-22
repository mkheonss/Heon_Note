define('o9.NSCM.JSSetSopFrozen', ['o9/data/query', 'o9/data/cellset', 'o9.NSCM.commonLib'], function () {
    const programName = "o9.NSCM.JSSetSopFrozen";

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
                                                'Measure.[BOD List_BOD Valid] == "Y",  ' +
                                                'coalesce(Measure.[BOD List_Eff Startdate],DATEADD(Now(),-1,"Day")) < now(),  ' +
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
                                                 ["Measure.[BOD List_BOD Valid]",
                                                    "Measure.[BOD List_Eff Enddate]",
                                                    "Measure.[BOD List_Eff Startdate]"],
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

    var fn_itemCombo = function(o9Params){
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
            var fbProductGroup = parsedParams.fbProductGroup;
            var fbProduct = parsedParams.fbProduct;
            var fbScmType = parsedParams.fbScmType;
            var fbInch = parsedParams.fbInch;
            var fbDefinition = parsedParams.fbDefinition;
            var fbYear = parsedParams.fbYear;
            var fbMarketingName = parsedParams.fbMarketingName;

            var toSite = ( "-,All".indexOf(fbToSite) > -1 ? "" : ".[" + fbToSite + "]" );
/*
            var dims = [];
            dims.push("&CWVUI");
            dims.push("[Location].[Location].[" + fbFromSite + "]");
            dims.push("[Sub Location].[Sub Location]" + toSite);
            dims.push("[Trans Mode].[Trans Mode]");
            if ( fbProductGroup != "All" )  dims.push("Item.[Product Group]" + vdUtil.fn_filterStr(fbProductGroup));
            if ( fbProduct != "All" )  dims.push("Item.[Product]" + vdUtil.fn_filterStr(fbProduct));
            if ( fbScmType != "All" )  dims.push("Item.[SCM Type]" + vdUtil.fn_filterStr(fbScmType));
            if ( fbInch != "All" )  dims.push("Item.[Inch]" + vdUtil.fn_filterStr(fbInch));
            if ( fbDefinition != "All" )  dims.push("Item.[Definition]" + vdUtil.fn_filterStr(fbDefinition));
            if ( fbYear != "All" )  dims.push("Item.[Year]" + vdUtil.fn_filterStr(fbYear));
            if ( fbMarketingName != "All" )  dims.push("Item.[Marketing Name]" + vdUtil.fn_filterStr(fbMarketingName));
            dims.push("Item.[Item]");

            var result = vdCommon.selectList(dims,
                                             ["Measure.[BOD Item_BOD LT]",
                                                "Measure.[BOD Item_BOD LT_Inherit]"],
                                             '',
                                             "",
                                             "limit 1000");
            vdCommon.printCsData(result, 3);
*/
            var where = [];
            where.push("&CWVUI");
            where.push("[Location].[Location].[" + fbFromSite + "]");
            where.push("[Sub Location].[Sub Location]" + toSite);
            where.push("[Trans Mode].[Trans Mode]");
            if ( fbProductGroup != "All" )  where.push("Item.[Product Group]" + vdUtil.fn_filterStr(fbProductGroup));
            if ( fbProduct != "All" )  where.push("Item.[Product]" + vdUtil.fn_filterStr(fbProduct));
            if ( fbScmType != "All" )  where.push("Item.[SCM Type]" + vdUtil.fn_filterStr(fbScmType));
            if ( fbInch != "All" )  where.push("Item.[Inch]" + vdUtil.fn_filterStr(fbInch));
            if ( fbDefinition != "All" )  where.push("Item.[Definition]" + vdUtil.fn_filterStr(fbDefinition));
            if ( fbYear != "All" )  where.push("Item.[Year]" + vdUtil.fn_filterStr(fbYear));
            if ( fbMarketingName != "All" )  where.push("Item.[Marketing Name]" + vdUtil.fn_filterStr(fbMarketingName));

            var result = vdCommon.selectList(["Item.[Item]"],
                                             ["Measure.[BOD Item_BOD LT]",
                                                "Measure.[BOD Item_BOD LT_Inherit]"],
                                             'where {' + where.join(", ") + ', coalesce(Measure.[BOD Item_Eff Startdate],DATEADD(Now(),-1,"Day")) < now(), coalesce(Measure.[BOD Item_Eff Enddate],DATEADD(Now(),1,"Day")) > now(), ~isnull(Measure.[BOD Item_BOD LT])}',
                                             "",
                                             "limit 1000");
            vdCommon.printCsData(result, 3);

            var comboList = vdCommon.fn_makeCombo(result, {DimName : "Item", DimAttbName : "Item", existAll : true, Sort : "DisplayName"});
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
            var fbItem = parsedParams.fbItem;
            var fbExceptItem = parsedParams.fbExceptItem;

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

            fbItem = fbItem.join("^");
            if ( fbExceptItem != null ) {
                fbExceptItem = fbExceptItem.join("^");
            } else {
                fbExceptItem = "";
            }

            var whereSql = 'where { Measure.[SOP Frozen_From Site] == "' + fbFromSite + '",' +
                            'Measure.[SOP Frozen_To Site] == "' + fbToSite + '",' +
                            'Measure.[SOP Frozen_Prod Grp] == "' + fbProductGroup + '",' +
                            'Measure.[SOP Frozen_Product] == "' + fbProduct + '",' +
                            'Measure.[SOP Frozen_SCM Type] == "' + fbScmType + '",' +
                            'Measure.[SOP Frozen_Inch] == "' + fbInch + '",' +
                            'Measure.[SOP Frozen_Definition] == "' + fbDefinition + '",' +
                            'Measure.[SOP Frozen_Year] == "' + fbYear + '",' +
                            'Measure.[SOP Frozen_Mkt Name] == "' + fbMarketingName + '",' +
                            'Measure.[SOP Frozen_Item] == "' + fbItem + '",' +
                            'Measure.[SOP Frozen_Ecp Item] == "' + fbExceptItem + '" }';
            if ( vdCommon.existMeasure(["&CWVUI","[Group].[Group ID]"], ["Measure.[SOP Frozen_Ctg]"], whereSql) ) {
                RuleOutputToUI = { Status : 'Error', Message : "The data is contained under the same conditions except for Category." };
                return;
            }

            vdCommon.printStep("Measure Add");
            vdCommon.createMeasure(["&CWVUI",
                                    "[Group].[Group ID].[" + groupId + "]"],
                                    ['Measure.[SOP Frozen_From Site] = "' + fbFromSite + '";',
                                    'Measure.[SOP Frozen_From Site Name] = "' + vdCommon.fn_getCodeName("Location", fbFromSite) + '";',
                                    'Measure.[SOP Frozen_Ctg] = "' + fbCategory + '";',
                                    'Measure.[SOP Frozen_To Site] = "' + fbToSite + '";',
                                    'Measure.[SOP Frozen_To Site Name] = "' + vdCommon.fn_getCodeName("Location", fbToSite) + '";',
                                    'Measure.[SOP Frozen_Prod Grp] = "' + fbProductGroup + '";',
                                    'Measure.[SOP Frozen_Product] = "' + fbProduct + '";',
                                    'Measure.[SOP Frozen_SCM Type] = "' + fbScmType + '";',
                                    'Measure.[SOP Frozen_Inch] = "' + fbInch + '";',
                                    'Measure.[SOP Frozen_Definition] = "' + fbDefinition + '";',
                                    'Measure.[SOP Frozen_Year] = "' + fbYear + '";',
                                    'Measure.[SOP Frozen_Mkt Name] = "' + fbMarketingName + '";',
                                    'Measure.[SOP Frozen_Item] = "' + fbItem + '";',
                                    'Measure.[SOP Frozen_Ecp Item] = "' + fbExceptItem + '";',
                                    'Measure.[SOP Frozen_Total Flag] = "N";',
                                    'Measure.[SOP Frozen_Valid Flag] = "Y";']);

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
                                ( fbItem != "All" ? 'Item.[Item]' + vdUtil.fn_filterStr(parsedParams.fbItem) + ' * ' : "" ) +
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
            var fbItem = parsedParams.fbItem;
            var fbExceptItem = parsedParams.fbExceptItem;

            vdCommon.createMeasure(["&CWVUI",
                                    "[Group].[Group ID].[" + fbGroupId + "]"],
                                    ['Measure.[SOP Frozen_From Site] = "' + fbFromSite + '";',
                                    'Measure.[SOP Frozen_From Site Name] = "' + vdCommon.fn_getCodeName("Location", fbFromSite) + '";',
                                    'Measure.[SOP Frozen_Ctg] = "' + fbCategory + '";',
                                    'Measure.[SOP Frozen_To Site] = "' + fbToSite + '";',
                                    'Measure.[SOP Frozen_To Site Name] = "' + vdCommon.fn_getCodeName("Location", fbToSite) + '";',
                                    'Measure.[SOP Frozen_Prod Grp] = "' + fbProductGroup + '";',
                                    'Measure.[SOP Frozen_Product] = "' + fbProduct + '";',
                                    'Measure.[SOP Frozen_SCM Type] = "' + fbScmType + '";',
                                    'Measure.[SOP Frozen_Inch] = "' + fbInch + '";',
                                    'Measure.[SOP Frozen_Definition] = "' + fbDefinition + '";',
                                    'Measure.[SOP Frozen_Year] = "' + fbYear + '";',
                                    'Measure.[SOP Frozen_Mkt Name] = "' + fbMarketingName + '";',
                                    'Measure.[SOP Frozen_Item] = "' + fbItem + '";',
                                    'Measure.[SOP Frozen_Ecp Item] = "' + fbExceptItem + '";']);

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

                vdCommon.deleteMeasure(["&CWVUI", "[Group].[Group ID].[" + row.GroupId.Value + "]"], "SOP Frozen");
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
        fn_itemCombo : fn_itemCombo,
        fn_add : fn_add,
        fn_change : fn_change,
        fn_delete : fn_delete
    };
});

/**************************** o9.NSCM.JSSetSopFrozen ****************************
    2025-02-25 : 속도개선으로 쿼리 변경
    2025-04-30 : fn_delete : 멀티 선택으로 수정
*********************************************************************/