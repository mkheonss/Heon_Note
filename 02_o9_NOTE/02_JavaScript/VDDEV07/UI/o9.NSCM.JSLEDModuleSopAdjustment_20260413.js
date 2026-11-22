define('o9.NSCM.JSLEDModuleSopAdjustment', ['o9/data/query', 'o9/data/cellset', 'o9.NSCM.commonLib'], function () {

    const programName = "o9.NSCM.JSLEDModuleSopAdjustment";
    const commonLib = require('o9.NSCM.commonLib');
    const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
    const vdUtil = new commonLib.VdUtil();
    
    var fn_add = function(o9Params) {
        try {
            vdCommon.setLogLevel("Debug");
            vdCommon.printParams(o9Params);

            const parsedParams = JSON.parse(o9Params);
            
            const dimension = [];
            dimension.push(`&CWVUI`);
            dimension.push(`[Location].[Location].[${parsedParams.fbLocation}]`);
            dimension.push(`[Belongings].[Belongings].[${parsedParams.fbBelongings}]`);
            dimension.push(`[Item].[Item].[${parsedParams.fbItem}]`);
            dimension.push(`[To Item].[To Item].[${parsedParams.fbToItem}]`);
            dimension.push(`[BOM Info].[BOM Version].[${parsedParams.fbBomVersion}]`);
            dimension.push(`[LED Rank].[LED Rank].[${parsedParams.fbRank}]`);
            dimension.push(`[LED Black Rank].[LED Black Rank].[${parsedParams.fbBlackRank}]`);

            // if (!vdCommon.existDimension([`[Location].[Location].[${fbLocation}]`, `[Item].[Item].[${fbItem}]`])) {
            //     vdCommon.createDimension(['[Location].[Location]', '[Item].[Item]'], [fbLocation, fbItem]);
            // }

            const measure = [];
            measure.push(`Measure.[Module SOP ADJ Module LED_Category]="";`);
            measure.push(`Measure.[Module SOP ADJ Module LED_SOP Week]="${parsedParams.fbSopWeek}";`);
            measure.push(`Measure.[Module SOP ADJ Module LED_MFG Week]="${parsedParams.fbMfgWeek}";`);
            measure.push(`Measure.[Module SOP ADJ Module LED_SOP Qty]="${parsedParams.fbSopQty}";`);
            measure.push(`Measure.[Module SOP ADJ Module LED_CHG Qty]="${parsedParams.fbChgQty}";`);
            measure.push(`Measure.[Module SOP ADJ Module LED_Change Reason]="${parsedParams.fbChangeReason}";`);
            measure.push(`Measure.[Module SOP ADJ Module LED_Short Reason]="${parsedParams.fbShortReason}";`);
            measure.push(`Measure.[Module SOP ADJ Module LED_BOD Name]="${parsedParams.fbBodName}";`);
            measure.push(`Measure.[Module SOP ADJ Module LED_SOP ID]="${parsedParams.fbSopId}";`);
            
            // vdCommon.createMeasure(dimension, measure);

            vdCommon.programEnd();
        } catch ( e ) {
            RuleOutputToUI = { Status : 'Error', Message : "Js Logic Error : " + e.message };
            return;
        }
    };

    var fn_delete = function(o9Params) {
        try {

            vdCommon.setLogLevel("Debug");
            vdCommon.printParams(o9Params);

            // 파라미터 가져오기
            const parsedParams = JSON.parse(o9Params);

            const dimension = [];
            dimension.push(`&CWVUI`);
            dimension.push(`[Location].[Location].[${parsedParams.fbLocation}]`);
            dimension.push(`[Belongings].[Belongings].[${parsedParams.fbBelongings}]`);
            dimension.push(`[Item].[Item].[${parsedParams.fbItem}]`);
            dimension.push(`[To Item].[To Item].[${parsedParams.fbToItem}]`);
            dimension.push(`[BOM Info].[BOM Version].[${parsedParams.fbBomVersion}]`);
            dimension.push(`[LED Rank].[LED Rank].[${parsedParams.fbRank}]`);
            dimension.push(`[LED Black Rank].[LED Black Rank].[${parsedParams.fbBlackRank}]`);

            vdCommon.programEnd();
        } catch ( e ) {
            RuleOutputToUI = { Status : 'Error', Message : "Js Logic Error : " + e.message };
            return;
        }
    };

    return {
        fn_add : fn_add,
        fn_delete : fn_delete
    };
});