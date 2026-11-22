define('o9.NSCM.JSLEDPurchasingProposalVendor', ['o9/data/query', 'o9/data/cellset', 'o9.NSCM.commonLib'], function () {

    const programName = "o9.NSCM.JSLEDPurchasingProposalVendor";

    var fn_vendor = function() {
        try {            
            const commonLib = require('o9.NSCM.commonLib');
            const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
            vdCommon.setLogLevel("Debug");

            const result = vdCommon.selectList(["[Vendor].[Vendor]", "[Vendor].[Vendor Name]"], [], "", "", "");
            vdCommon.printCsData(result, 3);

            const dimension = result.columns.dimension;
            const comboList = [];
            for (let i = 0; i < result.cs.rowCount; i++) {
                const combo = {};
                for (let idx = 0; idx < dimension.length; idx++) {
                    const attributeName = dimension[idx].split(".")[1];
                    const memberObject = result.cs.row(i).cell(result.cs.memberColumnIndex(dimension[idx].split(".")[0], attributeName));
                    if (attributeName === "Vendor") {
                        combo["Name"] = memberObject.Name;
                    } else {
                        combo["DisplayName"] = `${combo["Name"]}(${memberObject.Name})`;
                    }
                }
                comboList.push(combo);
            }

            vdCommon.debug("ComboData : " + JSON.stringify(comboList));
            vdCommon.programEnd();

            return comboList;
        } catch ( e ) {
            RuleOutputToUI = { Status : 'Error', Message : "Js Logic Error : " + e.message };
            return;
        }
    };

    var fn_location = function() {
        try {            
            const commonLib = require('o9.NSCM.commonLib');
            const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
            vdCommon.setLogLevel("Debug");

            const result = vdCommon.selectList(["[Location].[Location Type].[MF].relatedmembers([Location])"], [], "", "", "limit 1000");
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

    var fn_subLocation = function() {
        try {            
            const commonLib = require('o9.NSCM.commonLib');
            const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
            vdCommon.setLogLevel("Debug");

            const result = vdCommon.selectList(["[Sub Location].[Sub Location Type].[DC].relatedmembers([Sub Location])"], [], "", "", "limit 1000");
            vdCommon.printCsData(result, 3);

            const comboList = vdCommon.fn_makeCombo(result, {DimName : "Sub Location", DimAttbName : "Sub Location", Sort : "DisplayName", existAll : false, isDisplayNameWithCode : true});
            vdCommon.debug("ComboData : " + JSON.stringify(comboList));

            vdCommon.programEnd();

            return comboList;
        } catch ( e ) {
            RuleOutputToUI = { Status : 'Error', Message : "Js Logic Error : " + e.message };
            return;
        }
    };

    var fn_productGroup = function() {
        try {            
            const commonLib = require('o9.NSCM.commonLib');
            const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
            vdCommon.setLogLevel("Debug");

            const result = vdCommon.selectList(["[Product].[Product Group]"], [], "", "", "");
            vdCommon.printCsData(result, 3);

            const comboList = vdCommon.fn_makeCombo(result, {DimName : "Product", DimAttbName : "Product Group", Sort : "DisplayName", existAll : false, isDisplayNameWithCode : true});
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
            const fbVendor = parsedParams.fbVendor;
            const fbLocation = parsedParams.fbLocation;
            const fbSubLocation = parsedParams.fbSubLocation;
            const fbProductGroup = parsedParams.fbProductGroup;
            const fbINCO1 = parsedParams.fbINCO1;

            const dimension = ["&CWVUI"
                        , `[Vendor].[Vendor].[${fbVendor}]`
                        , `[Location].[Location].[${fbLocation}]`
                        , `[Sub Location].[Sub Location].[${fbSubLocation}]`
                        , `[Product].[Product Group].[${fbProductGroup}]`];

            if (!vdCommon.existDimension(dimension)) {
                vdCommon.createDimension(['[Vendor].[Vendor]', '[Location].[Location]', '[Sub Location].[Sub Location]', '[Product].[Product Group]'],
                     [fbVendor, fbLocation, fbSubLocation, fbProductGroup]);
            }

            const measure = [`Measure.[Purchasing Proposal Vendor_INCO1]=${fbINCO1};`];
            
            vdCommon.createMeasure(dimension, measure);

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
            const fbVendor = parsedParams.fbVendor;
            const fbLocation = parsedParams.fbLocation;
            const fbSubLocation = parsedParams.fbSubLocation;
            const fbProductGroup = parsedParams.fbProductGroup;
            const fbINCO1 = parsedParams.fbINCO1;

            const dimension = ["&CWVUI"
                        , `[Vendor].[Vendor].[${fbVendor}]`
                        , `[Location].[Location].[${fbLocation}]`
                        , `[Sub Location].[Sub Location].[${fbSubLocation}]`
                        , `[Product].[Product Group].[${fbProductGroup}]`];

            const measure = [`Measure.[Purchasing Proposal Vendor_INCO1]=${fbINCO1};`];
            
            vdCommon.updateMeasure(dimension, measure);
    
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

            const parsedParams = JSON.parse(o9Params);
            const fbVendor = parsedParams.fbVendor;
            const fbLocation = parsedParams.fbLocation;
            const fbSubLocation = parsedParams.fbSubLocation;
            const fbProductGroup = parsedParams.fbProductGroup;

            const dimension = ["&CWVUI"
                        , `[Vendor].[Vendor].[${fbVendor}]`
                        , `[Location].[Location].[${fbLocation}]`
                        , `[Sub Location].[Sub Location].[${fbSubLocation}]`
                        , `[Product].[Product Group].[${fbProductGroup}]`];

            vdCommon.deleteMeasure(dimension, "Purchasing Proposal Vendor");

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
            const vdUtil = new commonLib.VdUtil();

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

            if (fbActionBtnType == "edit" || fbActionBtnType == "delete") {
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
        fn_vendor : fn_vendor,
        fn_location : fn_location,
        fn_subLocation : fn_subLocation,
        fn_productGroup : fn_productGroup,
        fn_add : fn_add,
        fn_update : fn_update,
        fn_delete : fn_delete,
        fn_validate : fn_validate
    };
});