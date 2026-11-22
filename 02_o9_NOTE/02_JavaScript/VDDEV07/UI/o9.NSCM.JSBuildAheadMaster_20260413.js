define('o9.NSCM.JSBuildAheadMaster', ['o9/data/query', 'o9/data/cellset', 'o9.NSCM.commonLib'], function () {
    const programName = "o9.NSCM.JSBuildAheadMaster";

    var fn_locationCombo = function(o9Params){
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
                                             'where {&CWVUI, [Sub Location].[Sub Location], [Trans Mode].[Trans Mode], ' +
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

    var fn_subLocationCombo = function(o9Params){
        try {
            const commonLib = require('o9.NSCM.commonLib');
            const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
            vdCommon.setLogLevel("Debug");

            vdCommon.printParams(o9Params);

            var parsedParams = JSON.parse(o9Params);
            var fbLocation = parsedParams.fbLocation;

            /* 25.2.25 : 속도개선으로 쿼리 변경
            var result = vdCommon.selectList(["&CWVUI",
                                                "[Location].[Location].[" + fbLocation + "]",
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
                                             'where { &CWVUI, [Location].[Location].[' + fbLocation + '], [Trans Mode].[Trans Mode], ' +
                                                'Measure.[BOD List_BOD Valid] == "Y", ' +
                                                'coalesce(Measure.[BOD List_Eff Startdate],DATEADD(Now(),-1,"Day")) < now(), ' +
                                                'coalesce(Measure.[BOD List_Eff Enddate],DATEADD(Now(),1,"Day")) > now()}',
                                             "",
                                             "");
            vdCommon.printCsData(result, 3);

            var comboList = vdCommon.fn_makeCombo(result, {DimName : "Sub Location", DimAttbName : "Sub Location", Sort : "DisplayName", isDisplayNameWithCode : true});
            vdCommon.debug("ComboData : " + JSON.stringify(comboList));

            vdCommon.programEnd();

            return comboList;
        } catch ( e ) {
            RuleOutputToUI = { Status : 'Error', Message : "Js Logic Error : " + e.message };
            return;
        }
    };

    var fn_subLocationAllCombo = function(o9Params){
        try {
            const commonLib = require('o9.NSCM.commonLib');
            const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
            vdCommon.setLogLevel("Debug");

            vdCommon.printParams(o9Params);

            var parsedParams = JSON.parse(o9Params);
            var fbLocation = parsedParams.fbLocation;

            var result = vdCommon.selectList(["&NSUISubLocationDC"],
                                             ["Measure.[BOD List_BOD Valid]"],
                                             'where {&CWVUI, [Location].[Location].[' + fbLocation + '], [Trans Mode].[Trans Mode], ' +
                                                'Measure.[BOD List_BOD Valid] == "Y", coalesce(Measure.[BOD List_Eff Startdate],DATEADD(Now(),-1,"Day")) < now(), ' +
                                                'coalesce(Measure.[BOD List_Eff Enddate],DATEADD(Now(),1,"Day")) > now()}',
                                             "",
                                             "");
            vdCommon.printCsData(result, 3);

            var comboList = vdCommon.fn_makeCombo(result, {DimName : "Sub Location", DimAttbName : "Sub Location", Sort : "DisplayName", isDisplayNameWithCode : true, existAll : true});
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

    var fn_productGroupAllCombo = function(o9Params){
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

            var comboList = vdCommon.fn_makeCombo(result, {DimName : "Item", DimAttbName : "Product Group", Sort : "DisplayName", existAll : true});
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

            var result = vdCommon.selectList([(fbProductGroup == "All" ? '&SETItem.relatedmembers([Product Group])' : "&SETItem.relatedmembers([Product Group]).[" + fbProductGroup + "]"),
                                                "&SETItem.relatedmembers([Definition])"],
                                             [],
                                             "",
                                             "",
                                             "");
            vdCommon.printCsData(result, 3);

            var comboList = vdCommon.fn_makeCombo(result, {DimName : "Item", DimAttbName : "Definition", Sort : "DisplayName", existAll : true});
            vdCommon.debug("ComboData : " + JSON.stringify(comboList));

            vdCommon.programEnd();

            return comboList;
        } catch ( e ) {
            RuleOutputToUI = { Status : 'Error', Message : "Js Logic Error : " + e.message };
            return;
        }
    };

    var fn_projectCombo = function(o9Params){
        try {
            const commonLib = require('o9.NSCM.commonLib');
            const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
            vdCommon.setLogLevel("Debug");

            vdCommon.printParams(o9Params);

            // 파라미터 가져오기
            var parsedParams = JSON.parse(o9Params);
            var fbProductGroup = parsedParams.fbProductGroup;
            var fbDefinition = parsedParams.fbDefinition;

            var result = vdCommon.selectList([(fbProductGroup == "All" ? '&SETItem.relatedmembers([Product Group])' : "&SETItem.relatedmembers([Product Group]).[" + fbProductGroup + "]"),
                                                (fbDefinition == "All" ? '&SETItem.relatedmembers([Definition])' : "&SETItem.relatedmembers([Definition]).[" + fbDefinition + "]"),
                                                "&SETItem.relatedmembers([Project])"],
                                             [],
                                             "",
                                             "",
                                             "");
            vdCommon.printCsData(result, 3);

            var comboList = vdCommon.fn_makeCombo(result, {DimName : "Item", DimAttbName : "Project", Sort : "DisplayName", existAll : true});
            vdCommon.debug("ComboData : " + JSON.stringify(comboList));

            vdCommon.programEnd();

            return comboList;
        } catch ( e ) {
            RuleOutputToUI = { Status : 'Error', Message : "Js Logic Error : " + e.message };
            return;
        }
    };

    var fn_mktNameCombo = function(o9Params){
        try {
            const commonLib = require('o9.NSCM.commonLib');
            const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
            vdCommon.setLogLevel("Debug");

            vdCommon.printParams(o9Params);

            // 파라미터 가져오기
            var parsedParams = JSON.parse(o9Params);

            var result = vdCommon.selectList(["&SETItem.relatedmembers([Marketing Name])"],
                                             [],
                                             "",
                                             "",
                                             "");
            vdCommon.printCsData(result, 3);

            var comboList = vdCommon.fn_makeCombo(result, {DimName : "Item", DimAttbName : "Marketing Name", Sort : "DisplayName", existAll : true});
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

            var result = vdCommon.selectList(["&SETItem.relatedmembers([Inch])"],
                                             [],
                                             "",
                                             "",
                                             "");
            vdCommon.printCsData(result, 3);

            var comboList = vdCommon.fn_makeCombo(result, {DimName : "Item", DimAttbName : "Inch", Sort : "DisplayName", existAll : true});
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

            var result = vdCommon.selectList(["&SETItem.relatedmembers([Year]).intersectwith(&NSUIItemYearComboView)"],
                                             [],
                                             "",
                                             "",
                                             "");
            vdCommon.printCsData(result, 3);

            var comboList = vdCommon.fn_makeCombo(result, {DimName : "Item", DimAttbName : "Year", Sort : "DisplayName", existAll : true});
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
            var fbLocation = parsedParams.fbLocation;
            var fbSubLocation = parsedParams.fbSubLocation;
            var fbProductGroup = parsedParams.fbProductGroup;
            var fbDefinition = parsedParams.fbDefinition;
            var fbProject = parsedParams.fbProject;
            var fbMktName = parsedParams.fbMktName;
            var fbInch = parsedParams.fbInch;
            var fbYear = parsedParams.fbYear;

            var dims = [];
            dims.push("&CWVUI");
            dims.push("Location.[Location].[" + fbLocation + "]");
            if ( fbSubLocation != "All" )   dims.push("[Sub Location].[Sub Location].[" + fbSubLocation + "]");
            if ( fbProductGroup != "All" )   dims.push("Item.[Product Group].[" + fbProductGroup + "]");
            if ( fbDefinition != "All" )  dims.push("Item.[Definition]" + vdUtil.fn_filterStr(fbDefinition));
            if ( fbProject != "All" )  dims.push("Item.[Project]" + vdUtil.fn_filterStr(fbProject));
            if ( fbMktName != "All" )  dims.push("Item.[Marketing Name]" + vdUtil.fn_filterStr(fbMktName));
            if ( fbInch != "All" )  dims.push("Item.[Inch]" + vdUtil.fn_filterStr(fbInch));
            if ( fbYear != "All" )  dims.push("Item.[Year]" + vdUtil.fn_filterStr(fbYear));
            dims.push("Item.[Item]");

            var result = vdCommon.selectList( dims,
                                             ["Measure.[BOD Item_BOD Frozen]",
                                                "Measure.[BOD Item_BOD LT]",
                                                "Measure.[BOD Item_BOD LT_Inherit]",
                                                "Measure.[BOD Item_Cur Status]",
                                                "Measure.[BOD Item_Eff Enddate]",
                                                "Measure.[BOD Item_Eff Startdate]",
                                                "Measure.[BOD Item_Lock Flag]",
                                                "Measure.[BOD Item_Min Lot Qty]",
                                                "Measure.[BOD Item_Multi Lot Qty]",
                                                "Measure.[BOD Item_Need Check]",
                                                "Measure.[BOD Item_Period SET Detail]",
                                                "Measure.[BOD Item_Period1]",
                                                "Measure.[BOD Item_Period2]",
                                                "Measure.[BOD Item_Period3]",
                                                "Measure.[BOD Item_Priority]",
                                                "Measure.[BOD Item_Priority_Inherit]",
                                                "Measure.[BOD Item_Prod Item]",
                                                "Measure.[BOD Item_Shipment LT]",
                                                "Measure.[BOD Item_Shipment LT_Inherit]",
                                                "Measure.[BOD Item_Time Phased BOD]",
                                                "Measure.[BOD Item_Time Phased Prty]",
                                                "Measure.[BOD Item_Time Phased Shipment]",
                                                "Measure.[BOD Item_To Item]"],
                                             'where {coalesce(Measure.[BOD Item_Eff Startdate],DATEADD(Now(),-1,"Day")) < now(), coalesce(Measure.[BOD Item_Eff Enddate],DATEADD(Now(),1,"Day")) > now()}',
                                             "",
                                             "limit 1000");
            vdCommon.printCsData(result, 3);

            var comboList = vdCommon.fn_makeCombo(result, {DimName : "Item", DimAttbName : "Item", Sort : "DisplayName", existAll : true});
            vdCommon.debug("ComboData : " + JSON.stringify(comboList));

            vdCommon.programEnd();

            return comboList;
        } catch ( e ) {
            RuleOutputToUI = { Status : 'Error', Message : "Js Logic Error : " + e.message };
            return;
        }
    };

    var fn_validCombo = function(o9Params){
        try {
            const commonLib = require('o9.NSCM.commonLib');
            const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
            vdCommon.setLogLevel("Debug");

            var comboList = vdCommon.fn_makeCombo(null, {ComboCodes : ["Y","N"], ComboValues : ["Y","N"]});
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
            var fbLocation = parsedParams.fbLocation;
            var fbSubLocation = parsedParams.fbSubLocation;
            var fbProductGroup = parsedParams.fbProductGroup;
            var fbValid = parsedParams.fbValid;
            var fbAll = parsedParams.fbAll;

            if ( fbAll != "-" && !vdUtil.fn_isInt(fbAll) ) {
                RuleOutputToUI = { Status : 'Error', Message : "Please enter only numbers and -" };
                return;
            }

            // 필터용 데이타 Group ID = "-" 데이타 생성
            if ( !vdCommon.existDimension(['[Group].[Group Type].[BAL]','[Group].[Group ID].[-]']) ) {
                vdCommon.createDimension(['[Group].[Group Type]','[Group].[Group Name]','[Group].[Group ID]'], ["BAL", '"-"', '"-"']);
            }

            for ( var i = 0; i < fbSubLocation.length; i++ ) {
                // 중복체크
                if ( vdCommon.existMeasure(["&CWVUI",
                                                "Location.[Location].[" + fbLocation + "]",
                                                "[Sub Location].[Sub Location].[" + fbSubLocation[i] + "]",
                                                "Item.[Product Group].[" + fbProductGroup + "]"],
                                            ["Measure.[Build Ahead Prod_Valid]"],
                                            "") ) {
                    continue;
                }

                vdCommon.createMeasure(["&CWVUI",
                                            "Location.[Location].[" + fbLocation + "]",
                                            "[Sub Location].[Sub Location].[" + fbSubLocation[i] + "]",
                                            "Item.[Product Group].[" + fbProductGroup + "]"],
                                        ['Measure.[Build Ahead Prod_Creation time] = now();',
                                            'Measure.[Build Ahead Prod_Created by] = CurrentUser().Name;',
                                            'Measure.[Build Ahead Prod_Valid] = "' + fbValid + '";',
                                            'Measure.[Build Ahead Prod_ALL] = "' + fbAll + '";']);

                var measures = [];
                if ( fbAll == "-" ) {
                    measures.push('Measure.[Build Ahead Prod W_Period] = null;');
                    //measures[1] = 'Measure.[Build Ahead Prod W_Period.Lock] = false;';
                } else {
                    measures.push('Measure.[Build Ahead Prod W_Period] = ' + fbAll + ';') ;
                    //measures[1] = 'Measure.[Build Ahead Prod W_Period.Lock] = true;';
                }
                vdCommon.createMeasure(["&CWVUI",
                                            "Location.[Location].[" + fbLocation + "]",
                                            "[Sub Location].[Sub Location].[" + fbSubLocation[i] + "]",
                                            "Item.[Product Group].[" + fbProductGroup + "]",
                                            "&MPHorizon"],
                                        measures);

                // 필터용 데이타 생성
                vdCommon.createMeasure(["&CWVUI",
                                            "Location.[Location].[" + fbLocation + "]",
                                            "[Sub Location].[Sub Location].[" + fbSubLocation[i] + "]",
                                            "Item.[Product Group].[" + fbProductGroup + "]",
                                            "[Group].[Group ID].[-]"],
                                        ['Measure.[Build Ahead Group_Asn] = 1;']);
            }

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
            var fbSelect = parsedParams.fbSelect;

            for ( var i = 0; i < fbSelect.length; i++ ) {
                var row = fbSelect[i];

                vdCommon.deleteMeasure(["&CWVUI",
                                            "Location.[Location].[" + row.Location.Value + "]",
                                            "[Sub Location].[Sub Location].[" + row.SubLocation.Value + "]",
                                            "Item.[Product Group].[" + row.ProductGroup.Value + "]"],
                                        "Build Ahead Prod");

                vdCommon.deleteMeasure(["&CWVUI",
                                            "Location.[Location].[" + row.Location.Value + "]",
                                            "[Sub Location].[Sub Location].[" + row.SubLocation.Value + "]",
                                            "Item.[Product Group].[" + row.ProductGroup.Value + "]"],
                                        "Build Ahead Prod W");
            }

            vdCommon.programEnd();
        } catch ( e ) {
            RuleOutputToUI = { Status : 'Error', Message : "Js Logic Error : " + e.message };
            return;
        }
    };

    var fn_updateValid = function(o9Params){
        try {
            const commonLib = require('o9.NSCM.commonLib');
            const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
            const vdUtil = new commonLib.VdUtil();

            vdCommon.setLogLevel("Debug");

            vdCommon.printParams(o9Params);

            // 파라미터 가져오기
            var parsedParams = JSON.parse(o9Params);
            var fbValid = parsedParams.fbValid;
            var fbSelect = parsedParams.fbSelect;

            for ( var i = 0; i < fbSelect.length; i++ ) {
                var row = fbSelect[i];

                vdCommon.updateMeasure(["&CWVUI",
                                            "Location.[Location].[" + row.Location.Value + "]",
                                            "[Sub Location].[Sub Location].[" + row.SubLocation.Value + "]",
                                            "Item.[Product Group].[" + row.ProductGroup.Value + "]"],
                                        ['Measure.[Build Ahead Prod_Update time] = now();',
                                            'Measure.[Build Ahead Prod_Updated by] = CurrentUser().Name;',
                                            'Measure.[Build Ahead Prod_Valid] = "' + fbValid + '";']);
            }

            vdCommon.programEnd();
        } catch ( e ) {
            RuleOutputToUI = { Status : 'Error', Message : "Js Logic Error : " + e.message };
            return;
        }
    };

    var fn_updateAll = function(o9Params){
        try {
            const commonLib = require('o9.NSCM.commonLib');
            const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
            const vdUtil = new commonLib.VdUtil();

            vdCommon.setLogLevel("Debug");

            vdCommon.printParams(o9Params);

            // 파라미터 가져오기
            var parsedParams = JSON.parse(o9Params);
            var fbAll = parsedParams.fbAll;
            var fbSelect = parsedParams.fbSelect;

            if ( fbAll != "-" && !vdUtil.fn_isInt(fbAll) ) {
                RuleOutputToUI = { Status : 'Error', Message : "Please enter only numbers and -" };
                return;
            }

            for ( var i = 0; i < fbSelect.length; i++ ) {
                var row = fbSelect[i];

                vdCommon.createMeasure(["&CWVUI",
                                            "Location.[Location].[" + row.Location.Value + "]",
                                            "[Sub Location].[Sub Location].[" + row.SubLocation.Value + "]",
                                            "Item.[Product Group].[" + row.ProductGroup.Value + "]"],
                                        ['Measure.[Build Ahead Prod_Update time] = now();',
                                            'Measure.[Build Ahead Prod_Updated by] = CurrentUser().Name;',
                                            'Measure.[Build Ahead Prod_ALL] = "' + fbAll + '";']);

                var measures = [];
                if ( fbAll == "-" ) {
                    measures.push('Measure.[Build Ahead Prod W_Period] = null;');
                    measures.push('Measure.[Build Ahead Prod W_Period.Lock] = false;');
                } else {
                    measures.push('Measure.[Build Ahead Prod W_Period.Lock] = false;');
                    measures.push('Measure.[Build Ahead Prod W_Period] = ' + fbAll + ';');
                    measures.push('Measure.[Build Ahead Prod W_Period.Lock] = true;');
                }
                vdCommon.createMeasure(["&CWVUI",
                                            "Location.[Location].[" + row.Location.Value + "]",
                                            "[Sub Location].[Sub Location].[" + row.SubLocation.Value + "]",
                                            "Item.[Product Group].[" + row.ProductGroup.Value + "]",
                                            "&MPHorizon"],
                                        measures);
            }

            vdCommon.programEnd();
        } catch ( e ) {
            RuleOutputToUI = { Status : 'Error', Message : "Js Logic Error : " + e.message };
            return;
        }
    };

    var fn_addMiddle = function(o9Params){
        try {
            const commonLib = require('o9.NSCM.commonLib');
            const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
            const vdUtil = new commonLib.VdUtil();

            vdCommon.setLogLevel("Debug");

            vdCommon.printParams(o9Params);

            // 파라미터 가져오기
            var parsedParams = JSON.parse(o9Params);
            var fbLocation = parsedParams.fbLocation;
            var fbSubLocation = parsedParams.fbSubLocation;
            var fbProductGroup = parsedParams.fbProductGroup;
            var fbDefinition = parsedParams.fbDefinition;
            var fbProject = parsedParams.fbProject;
            var fbMktName = parsedParams.fbMktName;
            var fbInch = parsedParams.fbInch;
            var fbYear = parsedParams.fbYear;
            var fbItem = parsedParams.fbItem;
            var fbPeriod = parsedParams.fbPeriod;

            if ( !vdUtil.fn_isInt(fbPeriod) ) {
                RuleOutputToUI = { Status : 'Error', Message : "Please enter only numbers. (Period)" };
                return;
            }

            vdCommon.printStep("Group ID Max");

            // Max 값을 구한다.
            var result = vdCommon.selectList(["&CWVUI",
                                                "[Group].[Group ID].filter(#.Name startswith([BAL_]))"],
                                            ["Measure.[Build Ahead Item_From Site]"],
                                            "",
                                            "orderby [Group].[Group ID].Name desc",
                                            "limit 1");
            vdCommon.printCsData(result, 3);
            var groupId = "";
            if ( result.cs.rowCount == 0 ) {
                groupId = "BAL_" + vdUtil.fn_lpad("1", 5, "0");
            } else {
                groupId = "BAL_" + vdUtil.fn_lpad((parseInt(result.cs.row(0).cell(result.cs.memberColumnIndex("Group", "Group ID")).Name.substr(4)) + 1) + "", 5, "0");
            }
            // Dimension 을  추가한다.
            if ( !vdCommon.existDimension(['[Group].[Group Type].[BAL]','[Group].[Group ID].[' + groupId + ']']) ) {
                vdCommon.createDimension(['[Group].[Group Type]','[Group].[Group Name]','[Group].[Group ID]'], ["BAL", groupId, groupId]);
            }

            // 메인 데이타 생성
            vdCommon.createMeasure(["&CWVUI",
                                        "[Group].[Group ID].[" + groupId + "]"],
                                    ['Measure.[Build Ahead Item_Creation time] = now();',
                                        'Measure.[Build Ahead Item_Created by] = CurrentUser().Name;',
                                        'Measure.[Build Ahead Item_Category] = "Item Group";',
                                        'Measure.[Build Ahead Item_From Site] = "' + fbLocation + '";',
                                        'Measure.[Build Ahead Item_To Site] = "' + fbSubLocation + '";',
                                        'Measure.[Build Ahead Item_Product Group] = "' + fbProductGroup + '";',
                                        'Measure.[Build Ahead Item_Definition] = "' + fbDefinition + '";',
                                        'Measure.[Build Ahead Item_Project] = "' + fbProject + '";',
                                        'Measure.[Build Ahead Item_MKT Name] = "' + fbMktName + '";',
                                        'Measure.[Build Ahead Item_Inch] = "' + fbInch + '";',
                                        'Measure.[Build Ahead Item_Year] = "' + fbYear + '";',
                                        'Measure.[Build Ahead Item_Item] = "' + fbItem + '";']);

            // Week 데이타 생성
            vdCommon.createMeasure(["&CWVUI",
                                        "[Group].[Group ID].[" + groupId + "]",
                                        "&MPHorizon"],
                                    ['Measure.[Build Ahead Item W_Period] = ' + fbPeriod + ';']);

            // 필터용 데이타 생성
            if ( fbSubLocation == "All" ) {
                var fbSubLocations = [];
                var result = vdCommon.selectList(["&CWVUI",
                                                    "Location.[Location].[" + fbLocation + "]",
                                                    "[Sub Location].[Sub Location]"],
                                                    ["Measure.[BOD Item_BOD LT]",
                                                        "Measure.[Dummy]"],
                                                    "",
                                                    "",
                                                    "");
                for ( var i = 0; i < result.cs.rowCount; i++ ) {
                    fbSubLocations.push(vdUtil.fn_getString(result.cs.row(i).cell(result.cs.memberColumnIndex("Sub Location", "Sub Location")).Name));
                }

                vdCommon.createMeasure(["&CWVUI",
                                            "Location.[Location].[" + fbLocation + "]",
                                            "[Sub Location].[Sub Location]" + vdUtil.fn_filterStr(fbSubLocations),
                                            ( fbProductGroup == "All" ? 'Item.[Product Group].filter(#.Name in {"TV","MONITOR","AV"})' : "Item.[Product Group].[" + fbProductGroup + "]" ),
                                            "[Group].[Group ID].[" + groupId + "]"],
                                        ['Measure.[Build Ahead Group_Asn] = 1;']);
            } else {
                vdCommon.createMeasure(["&CWVUI",
                                            "Location.[Location].[" + fbLocation + "]",
                                            "[Sub Location].[Sub Location].[" + fbSubLocation + "]",
                                            ( fbProductGroup == "All" ? 'Item.[Product Group].filter(#.Name in {"TV","MONITOR","AV"})' : "Item.[Product Group].[" + fbProductGroup + "]" ),
                                            "[Group].[Group ID].[" + groupId + "]"],
                                        ['Measure.[Build Ahead Group_Asn] = 1;']);
            }

            // 데이타 초기화
            //vdCommon.deleteMeasure(["&CWVUI", "[Group].[Group ID].[" + groupId + "]"], "Build Ahead Item Ecp");

            // 파이썬 실행
            var execQuery = 'EXEC plugin instance [PY_UI_BuildAheadMaster] ' +
                            'for measures {[Build Ahead Item Ecp_Flag]} ' +
                            'using scope ( &CWVUI * ' +
                                ( fbProductGroup != "All" ? 'Item.[Product Group]' + vdUtil.fn_filterStr(fbProductGroup) + ' * ' : "" ) +
                                ( fbDefinition != "All" ? 'Item.[Definition]' + vdUtil.fn_filterStr(fbDefinition) + ' * ' : "" ) +
                                ( fbProject != "All" ? 'Item.[Project]' + vdUtil.fn_filterStr(fbProject) + ' * ' : "" ) +
                                ( fbMktName != "All" ? 'Item.[Marketing Name]' + vdUtil.fn_filterStr(fbMktName) + ' * ' : "" ) +
                                ( fbInch != "All" ? 'Item.[Inch]' + vdUtil.fn_filterStr(fbInch) + ' * ' : "" ) +
                                ( fbYear != "All" ? 'Item.[Year]' + vdUtil.fn_filterStr(fbYear) + ' * ' : "" ) +
                                ( fbItem != "All" ? 'Item.[Item]' + vdUtil.fn_filterStr(fbItem) + ' * ' : "" ) +
                                '[Group].[Group ID].[' + groupId + '] * ' +
                                '[Location].[Location].[' + fbLocation + '] * ' +
                                '[Sub Location].[Sub Location].[' + fbSubLocation + '] ) ' +
                            'using arguments {(RunID, "Run_1"),(ExecutionMode, "MediumWeight"), (MaxSliceTableCells, 200000000), (MaxConcurrency, 1 )};'
            vdCommon.executeQuery("Py Run", execQuery);

            vdCommon.programEnd();
        } catch ( e ) {
            RuleOutputToUI = { Status : 'Error', Message : "Js Logic Error : " + e.message };
            return;
        }
    };

    var fn_deleteMiddle = function(o9Params){
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
                                            "Group.[Group ID].[" + row.GroupID.Value + "]"],
                                        "Build Ahead Item");

                vdCommon.deleteMeasure(["&CWVUI",
                                            "Group.[Group ID].[" + row.GroupID.Value + "]"],
                                        "Build Ahead Item W");

                vdCommon.deleteMeasure(["&CWVUI",
                                            "Group.[Group ID].[" + row.GroupID.Value + "]"],
                                        "Build Ahead Item Ecp");
            }

            vdCommon.programEnd();
        } catch ( e ) {
            RuleOutputToUI = { Status : 'Error', Message : "Js Logic Error : " + e.message };
            return;
        }
    };

    var fn_shipmentTypeCombo = function(o9Params){
        try {
            const commonLib = require('o9.NSCM.commonLib');
            const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
            vdCommon.setLogLevel("Debug");

            var comboList = comboList = vdCommon.fn_makeCombo(null, {ComboCodes : ["All","DIR_S","INDIR"], ComboValues : ["All","DIR_S","INDIR"]});
            vdCommon.debug("ComboData : " + JSON.stringify(comboList));

            vdCommon.programEnd();

            return comboList;
        } catch ( e ) {
            RuleOutputToUI = { Status : 'Error', Message : "Js Logic Error : " + e.message };
            return;
        }
    };

    var fn_subLocationForShipmentTypeCombo = function(o9Params){
        try {
            const commonLib = require('o9.NSCM.commonLib');
            const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
            vdCommon.setLogLevel("Debug");

            vdCommon.printParams(o9Params);

            var parsedParams = JSON.parse(o9Params);
            var fbLocation = parsedParams.fbLocation;
            var fbShipmentType = parsedParams.fbShipmentType;

            // 등록 데이타 제외한다.
            var result = vdCommon.selectList(["&NSUISubLocationDC",
                                                "[Sub Location].[Sub Location Shipment Type]" + (fbShipmentType == "All" ? "" : ".[" + fbShipmentType + "]")],
                                             ["Measure.[BOD List_BOD Valid]"],
                                             'where { &CWVUI, [Location].[Location].[' + fbLocation + '], [Trans Mode].[Trans Mode], ' +
                                                'Measure.[BOD List_BOD Valid] == "Y", ' +
                                                'coalesce(Measure.[BOD List_Eff Startdate],DATEADD(Now(),-1,"Day")) < now(), ' +
                                                'coalesce(Measure.[BOD List_Eff Enddate],DATEADD(Now(),1,"Day")) > now()}',
                                             "",
                                             "");
            //vdCommon.printCsData(result, 3);
            var comboList = vdCommon.fn_makeCombo(result, {DimName : "Sub Location", DimAttbName : "Sub Location", Sort : "DisplayName", isDisplayNameWithCode : true});
            vdCommon.debug("ComboData : " + JSON.stringify(comboList));

            vdCommon.programEnd();

            return comboList;
        } catch ( e ) {
            RuleOutputToUI = { Status : 'Error', Message : "Js Logic Error : " + e.message };
            return;
        }
    };

    return {
        fn_locationCombo : fn_locationCombo,
        fn_subLocationCombo : fn_subLocationCombo,
        fn_subLocationAllCombo : fn_subLocationAllCombo,
        fn_productGroupCombo : fn_productGroupCombo,
        fn_productGroupAllCombo : fn_productGroupAllCombo,
        fn_definitionCombo : fn_definitionCombo,
        fn_projectCombo : fn_projectCombo,
        fn_mktNameCombo : fn_mktNameCombo,
        fn_inchCombo : fn_inchCombo,
        fn_yearCombo : fn_yearCombo,
        fn_itemCombo : fn_itemCombo,
        fn_validCombo : fn_validCombo,
        fn_add : fn_add,
        fn_delete : fn_delete,
        fn_updateValid : fn_updateValid,
        fn_updateAll : fn_updateAll,
        fn_addMiddle : fn_addMiddle,
        fn_deleteMiddle : fn_deleteMiddle,
        fn_shipmentTypeCombo : fn_shipmentTypeCombo,
        fn_subLocationForShipmentTypeCombo : fn_subLocationForShipmentTypeCombo
    };
});

/**************************** o9.NSCM.JSBuildAheadMaster ****************************
    2025-1-13 :
        fn_subLocationAllCombo 추가
        추가할 때 Build Ahead Group_Asn 데이타 생성 로직 반영
    2025-02-25 : 속도개선으로 쿼리 변경
    2025-04-23 : fn_updateAll : All 적용시 데이타 수정이 없다는 요구로 updateMeasure -> createMeasure 로 변경( 주차 데이타가 없어서 생성으로 변경 )
    2025-04-24 : to site 를 가져올때 Shipment Type Combo 를 사용해서 가져오고, 멀티 선택이 가능하도록 수정

*********************************************************************/