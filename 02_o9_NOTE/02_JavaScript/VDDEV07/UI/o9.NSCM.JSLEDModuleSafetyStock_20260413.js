define('o9.NSCM.JSLEDModuleSafetyStock', ['o9/data/query', 'o9/data/cellset', 'o9.NSCM.commonLib'], function () {

    const programName = "o9.NSCM.JSLEDModuleSafetyStock";
    
    var fn_version = function() {
        try {            
            const commonLib = require('o9.NSCM.commonLib');
            const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
            vdCommon.setLogLevel("Debug");

            const versionDisplayName = vdCommon.selectResult('Version.[Version Name].[CWV_MP].DisplayName');
            vdCommon.debug("Version Name : " + JSON.stringify(versionDisplayName));

            vdCommon.programEnd();

            return { Name : versionDisplayName, DisplayName : versionDisplayName };
        } catch ( e ) {
            RuleOutputToUI = { Status : 'Error', Message : "Js Logic Error : " + e.message };
            return;
        }
    };

    var fn_locationCombo = function() {
        try {            
            const commonLib = require('o9.NSCM.commonLib');
            const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
            vdCommon.setLogLevel("Debug");

            const where = 'where {&CWVUI, [Location].[Site Stage].filter(#.Name contains "SET"), [Location].[Location Type].[MF], &LEDStrategy, Measure.[Item Site Asn_Cur Status] in {"PLANNED", "ACTIVE"}}';
            const result = vdCommon.selectList(["[Location].[Location]"], [], where, "", "");
            vdCommon.printCsData(result, 3);

            const comboList = vdCommon.fn_makeCombo(result, {DimName : "Location", DimAttbName : "Location", Sort : "DisplayName", existAll : false, isDisplayNameWithCode : true});
            vdCommon.debug("ComboData : " + JSON.stringify(comboList));

            vdCommon.programEnd();

            return comboList;
        } catch ( e ) {
            RuleOutputToUI = { Status : 'Error', Message : "Js Logic Error : " + e.message };
            return;
        }
    };

    var fn_itemCombo = function() {
        try {            
            const commonLib = require('o9.NSCM.commonLib');
            const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
            vdCommon.setLogLevel("Debug");

            const where = 'where {[Version].[Version Name].[CWV_MP], [Item].[Item Stage].[LED_MODULE], [Item].[Product Code].[90CD], [Location].[Location Type].[MF], Measure.[Item Site Asn_Cur Status] in {"PLANNED", "ACTIVE"}}';
            const result = vdCommon.selectList(["[Item].[Item]"], [], where, "", "");
            vdCommon.printCsData(result, 3);

            const comboList = vdCommon.fn_makeCombo(result, {DimName : "Item", DimAttbName : "Item", Sort : "DisplayName", existAll : false, isDisplayNameWithCode : true});
            vdCommon.debug("ComboData : " + JSON.stringify(comboList));

            vdCommon.programEnd();

            return comboList;
        } catch ( e ) {
            RuleOutputToUI = { Status : 'Error', Message : "Js Logic Error : " + e.message };
            return;
        }
    };

    var fn_weekCombo = function() {
        try {            
            const commonLib = require('o9.NSCM.commonLib');
            const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
            vdCommon.setLogLevel("Debug");

            const result = vdCommon.selectList(["[Time].[Week].filter(#.Key >= &CurrentWeek.element(0).LeadOffset(0).Key && #.Key <= &CurrentWeek.element(0).LeadOffset(52).Key)"], [], "", "", "");
            vdCommon.printCsData(result, 3);

            const comboList = vdCommon.fn_makeCombo(result, {DimName : "Time", DimAttbName : "Week", Sort : "DisplayName", existAll : false, isDisplayNameWithCode : true});
            vdCommon.debug("ComboData : " + JSON.stringify(comboList));

            vdCommon.programEnd();

            return comboList;
        } catch ( e ) {
            RuleOutputToUI = { Status : 'Error', Message : "Js Logic Error : " + e.message };
            return;
        }
    };

    var fn_add = function(o9Params) {
        try {
            const commonLib = require('o9.NSCM.commonLib');
            const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
            
            vdCommon.setLogLevel("Debug");
            vdCommon.printParams(o9Params);

            const parsedParams = JSON.parse(o9Params);
            const fbLocation = parsedParams.fbLocation;
            const fbItem = parsedParams.fbItem;

            const dim = ["&CWVUI"
                        , `[Location].[Location].[${fbLocation}]`
                        , `[Item].[Item].[${fbItem}]`];

            if (!vdCommon.existDimension([`[Location].[Location].[${fbLocation}]`, `[Item].[Item].[${fbItem}]`])) {
                vdCommon.createDimension(['[Location].[Location]', '[Item].[Item]'], [fbLocation, fbItem]);
            }

            vdCommon.createMeasure(dim
                                    ,['Measure.[Module SS LED_Type]="MIN_ONHAND";'
                                    , `Measure.[Module SS LED_Calendar]="MO_${fbItem}@${fbLocation}";`
                                    , `Measure.[Module SS LED_Rank]="${parsedParams.fbRank}";`
                                    , `Measure.[Module SS LED_Black Rank]="${parsedParams.fbBlackRank}";`
                                    , `Measure.[Module SS LED_Min Same Rank Qty]=${parsedParams.fbMinRankQty};`
                                    , `Measure.[Module SS LED_Min Qty Multiple Lot Size]=${parsedParams.fbMultifulLotSize};`
                                    , 'Measure.[Module SS LED_Valid]="Y";']);

            dim.push("[Time].[Week].filter(#.Key >= &CurrentWeek.element(0).LeadOffset(0).Key && #.Key <= &CurrentWeek.element(0).LeadOffset(52).Key)");
            
            vdCommon.createMeasure(dim, [`Measure.[Module SS W LED_Qty]=${parsedParams.fbStaticValue};`]);

            vdCommon.programEnd();
        } catch ( e ) {
            RuleOutputToUI = { Status : 'Error', Message : "Js Logic Error : " + e.message };
            return;
        }
    };

    var fn_update = function(o9Params) {
        try {
            const commonLib = require('o9.NSCM.commonLib');
            const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
            
            vdCommon.setLogLevel("Debug");
            vdCommon.printParams(o9Params);

            const parsedParams = JSON.parse(o9Params);
            const fbLocation = parsedParams.fbLocation;
            const fbItem = parsedParams.fbItem;
            const fbWeek = parsedParams.fbWeek;

            const dimension = ["&CWVUI"
                            ,`[Location].[Location].[${fbLocation}]`
                            ,`[Item].[Item].[${fbItem}]`
                            ,`[Time].[Week].filter(#.Name >= "${fbWeek}")`];

            vdCommon.updateMeasure(dimension, [`Measure.[Module SS W LED_Qty]=${parsedParams.fbStaticValue};`]);
    
            vdCommon.programEnd();
        } catch ( e ) {
            RuleOutputToUI = { Status : 'Error', Message : "Js Logic Error : " + e.message };
            return;
        }
    };

    var fn_delete = function(o9Params) {
        try {
            const commonLib = require('o9.NSCM.commonLib');
            const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);

            vdCommon.setLogLevel("Debug");
            vdCommon.printParams(o9Params);

            // 파라미터 가져오기
            const parsedParams = JSON.parse(o9Params);
            const fbLocation = parsedParams.fbLocation;
            const fbItem = parsedParams.fbItem;

            const dim = ["&CWVUI"
                    , `[Location].[Location].[${fbLocation}]`
                    , `[Item].[Item].[${fbItem}]`];

            vdCommon.deleteMeasure(dim, "Module SS LED");

            dim.push("[Time].[Week].filter(#.Key >= &CurrentWeek.element(0).LeadOffset(0).Key && #.Key <= &CurrentWeek.element(0).LeadOffset(52).Key)");
            
            vdCommon.deleteMeasure(dim, "Module SS W LED");

            vdCommon.programEnd();
        } catch ( e ) {
            RuleOutputToUI = { Status : 'Error', Message : "Js Logic Error : " + e.message };
            return;
        }
    };

    var fn_validate = function(o9Params) {
        try {
            const commonLib = require('o9.NSCM.commonLib');
            const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);

            vdCommon.setLogLevel("Debug");
            vdCommon.printParams(o9Params);

            const parsedParams = JSON.parse(o9Params);

            const fbTupleList = parsedParams.fbTupleList;
            const tupleListSize = parsedParams.fbTupleList.length;
            const fbActionBtnType = parsedParams.fbActionBtnType;
            let returnValue = 0;    // 0: 정상, 1: 오류메세지
            let errMsg = "";

            vdCommon.debug("tupleListSize size =======>" + tupleListSize);

            if (fbActionBtnType == null || fbActionBtnType === "") {
                errMsg = "Action Button 이 정의되지 않았습니다.";
                RuleOutputToUI = { Status : 'Error', Message : errMsg };
                returnValue = 1;
                return returnValue;
            }

            if (fbActionBtnType == "ditto" || fbActionBtnType == "delete") {
                if (tupleListSize == 0) {
                    errMsg = "1개의 행을 선택하세요.";
                    RuleOutputToUI = { Status : 'Error', Message : errMsg };
                    returnValue = 1;
                    return returnValue;
                } else if (tupleListSize > 1) {
                    errMsg = "1건만 선택할 수 있습니다.";
                    RuleOutputToUI = { Status : 'Error', Message : errMsg };
                    returnValue = 1;
                    return returnValue;
                }
            }
            
            vdCommon.programEnd();
            return returnValue;
        } catch ( e ) {
            RuleOutputToUI = { Status : 'Error', Message : "Js Logic Error : " + e.message };
            return;
        }
    };

    return {
        fn_version : fn_version,
        fn_locationCombo : fn_locationCombo,
        fn_itemCombo : fn_itemCombo,
        fn_weekCombo : fn_weekCombo,
        fn_add : fn_add,
        fn_update : fn_update,
        fn_delete : fn_delete,
        fn_validate : fn_validate
    };
});