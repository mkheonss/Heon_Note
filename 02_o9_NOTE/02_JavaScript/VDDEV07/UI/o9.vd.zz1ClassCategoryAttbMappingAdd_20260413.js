define('o9.vd.zz1ClassCategoryAttbMappingAdd', ['o9/data/query', 'o9/data/cellset', 'o9.vd.zz1CommonLib'], function () {

    var callJs = function(o9Params){
        var commonLib = require('o9.vd.zz1CommonLib');

        var programName = "o9.vd.zz1ClassCategoryAttbMappingAdd";
        vdCommon = new commonLib.VdCommon(programName);
        vdCommon.setLogLevel("Debug");

        vdCommon.printParams(o9Params);

        // 파라미터 가져오기
        var parsedParams = JSON.parse(o9Params);
        var fbProduct = parsedParams.fbProduct;
        var fbAttbNo = parsedParams.fbAttbNo;
        var fbClassCategory = parsedParams.fbClassCategory;
        var fbItemRuleSeq = parsedParams.fbItemRuleSeq;

        itemRuleSeq = parseInt(fbItemRuleSeq);
        if ( itemRuleSeq > 99 ) {
            RuleOutputToUI = { Status : 'Error', Message : "Rule Seq under 100" };
            return;
        }

        var ruleNo = fbClassCategory + '_' + fbAttbNo + '_' + (itemRuleSeq < 10 ? '0' : '') + itemRuleSeq;

        if ( !vdCommon.existMember('[zz1Item Attb Rule].[Rule No]', ruleNo) ) {
            vdCommon.createMember('[zz1Item Attb Rule].[Rule No]', ruleNo);
        }


        var dimension = ['Version.[Version Name].[CurrentWorkingView]',
                            '[zz1Item Product].[Product].[' + fbProduct + ']',
                            '[zz1Item Attb].[Attb No].[' + fbAttbNo + ']',
                            '[Item].[Class Category].[' + fbClassCategory + ']',
                            '[zz1Item Attb Rule].[Rule No].[' + ruleNo + ']'];
        if ( !vdCommon.existMeasure(dimension, ['Measure.[Item Attb Ref Attb Id]']) ) {
            vdCommon.createMeasure(dimension,
                        ['Measure.[Item Attb Ref Attb Id] = "-";',
                        'Measure.[Item Rule Seq] = ' + itemRuleSeq + ';']);
        } else {
            RuleOutputToUI = { Status : 'Error', Message : "This Data has already been registered." };
            return;
        }

        vdCommon.programEnd();
    };

    return {
        zz1ClassCategoryAttbMappingAdd : callJs
    };
});