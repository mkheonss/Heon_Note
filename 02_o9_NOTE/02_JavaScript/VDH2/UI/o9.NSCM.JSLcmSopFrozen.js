define('o9.NSCM.JSLcmSopFrozen', ['o9/data/query', 'o9/data/cellset', 'o9.NSCM.commonLib'], function () {
    const programName = "o9.NSCM.JSLcmSopFrozen";

    var fn_fromSiteNameCombo = function(o9Params){
        try {
            const commonLib = require('o9.NSCM.commonLib');
            const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
            vdCommon.setLogLevel("Debug");

            /* 25.2.25 : 속도개선으로 쿼리 변경
            var result = vdCommon.selectList(["&CWVUI", "&LCMLocation", "[Sub Location].[Sub Location]", "[Trans Mode].[Trans Mode]"],
                                             ["Measure.[BOD List_BOD Valid]",
                                                "Measure.[BOD List_Eff Enddate]",
                                                "Measure.[BOD List_Eff Startdate]"],
                                             'where {Measure.[BOD List_BOD Valid] == "Y", coalesce(Measure.[BOD List_Eff Startdate],DATEADD(Now(),-1,"Day")) < now(), coalesce(Measure.[BOD List_Eff Enddate],DATEADD(Now(),1,"Day")) > now()}',
                                             "",
                                             "");
            */
            var result = vdCommon.selectList(["&LCMLocation"],
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
                                                    "[Sub Location].[Sub Location]",
                                                    "[Trans Mode].[Trans Mode]"],
                                                 ["Measure.[BOD List_BOD Valid]",
                                                    "Measure.[BOD List_Eff Enddate]",
                                                    "Measure.[BOD List_Eff Startdate]"],
                                                 'where {Measure.[BOD List_BOD Valid] == "Y", coalesce(Measure.[BOD List_Eff Startdate],DATEADD(Now(),-1,"Day")) < now(), coalesce(Measure.[BOD List_Eff Enddate],DATEADD(Now(),1,"Day")) > now()}',
                                                 "",
                                                 "");
                */
                var result = vdCommon.selectList(["[Sub Location].[Sub Location]"],
                                                 ["Measure.[BOD List_BOD Valid]"],
                                                 'where {&CWVUI, [Location].[Location].[' + fbFromSite + '], [Trans Mode].[Trans Mode], ' +
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

            var result = vdCommon.selectList(["&LCMItem.relatedmembers([Product Group])"],
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

            var toSite = ( "-,All".indexOf(fbToSite) > -1 ? "" : ".[" + fbToSite + "]" );
            /*
            var result = vdCommon.selectList(["&CWVUI",
                                                "[Location].[Location].[" + fbFromSite + "]",
                                                "[Sub Location].[Sub Location]" + toSite,
                                                "[Trans Mode].[Trans Mode]",
                                                "Item.[Product Group]" + (fbProductGroup == "All" ? "" : ".[" + fbProductGroup + "]"),
                                                "Item.[Item]"],
                                         ["Measure.[BOD Item_BOD LT]",
                                                "Measure.[BOD Item_BOD LT_Inherit]"],
                                         "",
                                         "",
                                         "limit 1000");
            */
            var where = [];
            where.push("&CWVUI");
            where.push("[Location].[Location].[" + fbFromSite + "]");
            where.push("[Sub Location].[Sub Location]" + toSite);
            where.push("[Trans Mode].[Trans Mode]");
            if ( fbProductGroup != "All" )  where.push("Item.[Product Group]" + vdUtil.fn_filterStr(fbProductGroup));

            var result = vdCommon.selectList(["&LCMItem"],
                                             ["Measure.[BOD Item_BOD LT]",
                                                    "Measure.[BOD Item_BOD LT_Inherit]"],
                                             'where {' + where.join(", ") + ', coalesce(Measure.[BOD Item_Eff Startdate],DATEADD(Now(),-1,"Day")) < now(), coalesce(Measure.[BOD Item_Eff Enddate],DATEADD(Now(),1,"Day")) > now(), ~isnull(Measure.[BOD Item_BOD LT])}',
                                             "",
                                             "limit 1000");
            vdCommon.printCsData(result, 3);

            var comboList = vdCommon.fn_makeCombo(result, {DimName : "Item", DimAttbName : "Item", Sort : "DisplayName"});
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
            var fbProductGroup = parsedParams.fbProductGroup;
            var fbItem = parsedParams.fbItem;

            vdCommon.printStep("Group ID Max");

            // Max 값을 구한다.
            var result = vdCommon.selectList(["&CWVUI * [Group].[Group Type].[MFF_L] * [Group].[Group ID].filter(#.Name startswith([MFF_L_]))"],
                                                ["Measure.[SOP Frozen_From Site]"],
                                                "",
                                                "orderby [Group].[Group ID].Key desc",
                                                "limit 1");
            var groupId = "";
            if ( result.cs.rowCount == 0 ) {
                groupId = "MFF_L_" + vdUtil.fn_lpad("1", 5, "0");
            } else {
                groupId = "MFF_L_" + vdUtil.fn_lpad((parseInt(result.cs.row(0).cell(result.cs.memberColumnIndex("Group", "Group ID")).Name.substr(6)) + 1) + "", 5, "0");
            }
            // Dimension 을  추가한다.
            if ( !vdCommon.existDimension(['[Group].[Group Type].[MFF_L]','[Group].[Group ID].[' + groupId + ']']) ) {
                vdCommon.createDimension(['[Group].[Group Type]','[Group].[Group Name]','[Group].[Group ID]'], ["MFF_L", groupId, groupId]);
            }

            fbItem = fbItem.join("^");

            vdCommon.printStep("Measure Add");
            vdCommon.createMeasure(["&CWVUI",
                                    "[Group].[Group ID].[" + groupId + "]"],
                                    ['Measure.[SOP Frozen_From Site] = "' + fbFromSite + '";',
                                    'Measure.[SOP Frozen_From Site Name] = "' + vdCommon.fn_getCodeName("Location", fbFromSite) + '";',
                                    'Measure.[SOP Frozen_To Site] = "' + fbToSite + '";',
                                    'Measure.[SOP Frozen_To Site Name] = "' + vdCommon.fn_getCodeName("Location", fbToSite) + '";',
                                    'Measure.[SOP Frozen_Prod Grp] = "' + fbProductGroup + '";',
                                    'Measure.[SOP Frozen_Item] = "' + fbItem + '";',
                                    'Measure.[SOP Frozen_Valid Flag] = "Y";']);

            vdCommon.programEnd();
        } catch ( e ) {
            RuleOutputToUI = { Status : 'Error', Message : "Js Logic Error : " + e.message };
            return;
        }
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
            var fbGroupId = parsedParams.fbGroupId;

            vdCommon.deleteMeasure(["&CWVUI",
                                        "[Group].[Group ID].[" + fbGroupId + "]"],
                                    "SOP Frozen");

            vdCommon.programEnd();
        } catch ( e ) {
            RuleOutputToUI = { Status : 'Error', Message : "Js Logic Error : " + e.message };
            return;
        }
    };

    return {
        fn_fromSiteNameCombo : fn_fromSiteNameCombo,
        fn_toSiteNameCombo : fn_toSiteNameCombo,
        fn_productGroupCombo : fn_productGroupCombo,
        fn_itemCombo : fn_itemCombo,
        fn_add : fn_add,
        fn_delete : fn_delete
    };
});

/**************************** o9.NSCM.JSLcmSopFrozen ****************************
    2024-11-13 : ...
    2025-01-29 : Item 에서 All 제거
                 Add 시 파이썬 호출 제거
    2025-02-25 : 속도개선으로 쿼리 변경
*********************************************************************/