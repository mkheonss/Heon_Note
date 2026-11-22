define('o9.NSCM.JSLcmItemAttr', ['o9/data/query', 'o9/data/cellset', 'o9.NSCM.commonLib'], function () {
    const programName = "o9.NSCM.JSLcmItemAttr";
    
    var fn_publish = function(o9Params){
        try {
            const commonLib = require('o9.NSCM.commonLib');
            const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
            vdCommon.setLogLevel("Debug");

            vdCommon.printParams(o9Params);

            // 파라미터 가져오기
            var parsedParams = JSON.parse(o9Params);
            var fbVersionName = parsedParams.fbVersionName;

            // IBPL 실행
            var execQuery = 'createMember(  ' +
                                '[Item].[Item]={,Item.#.Name},  ' +
                                '[Item].[Inch] = {,Measure.[Lcm Item Attr_Inch]},  ' +
                                '[Item].[Series] = {,Measure.[Lcm Item Attr_Series]},  ' +
                                '[Item].[SET Item] = {,Measure.[Lcm Item Attr_SET Item]},  ' +
                                '[Item].[Definition] = {,Measure.[Lcm Item Attr_Definition]},  ' +
                                '[Item].[Strategy] = {,Measure.[Lcm Item Attr_Strategy]},  ' +
                                '[Item].[Hz] = {,Measure.[Lcm Item Attr_Hz]},  ' +
                                '[Item].[Open Cell] = {,Measure.[Lcm Item Attr_Open Cell]},  ' +
                                '[Item].[CY Code] = {,Measure.[Lcm Item Attr_CY Code]},  ' +
                                '[Item].[DP Code] = {,Measure.[Lcm Item Attr_DP Code]},  ' +
                                '[Item].[Project] = {,Measure.[Lcm Item Attr_Project]},  ' +
                                '[Item].[Cell Vendor] = {,Measure.[Lcm Item Attr_Cell Vendor]},  ' +
                                '[Item].[Mini LED] = {,Measure.[Lcm Item Attr_Mini LED]},  ' +
                                '[Item].[Bonding] = {,Measure.[Lcm Item Attr_Bonding]},  ' +
                                '[Item].[3in1] = {,Measure.[Lcm Item Attr_3in1]},  ' +
                                '[Item].[Year] = {,Measure.[Lcm Item Attr_Year]}  ' +
                                ') using scope ([Version].[Version Name].[' + fbVersionName + '] * &LCMItem.relatedmembers([Item])) ;  ';
            vdCommon.executeQuery("Py Run", execQuery);

            vdCommon.programEnd();
        } catch ( e ) {
            RuleOutputToUI = { Status : 'Error', Message : "Js Logic Error : " + e.message };
            return;
        }
    };

    return {
        fn_publish : fn_publish
    };
});

/**************************** o9.NSCM.JSLcmItemAttr ****************************
    2025-1-6 : ...
*********************************************************************/