define('o9.vd.zz1ClassCategoryAttbMappingDelete', ['o9/data/query', 'o9/data/cellset', 'o9.vd.zz1CommonLib'], function () {

    var callJs = function(o9Params){
        var commonLib = require('o9.vd.zz1CommonLib');

        var programName = "o9.vd.zz1ClassCategoryAttbMappingDelete";
        vdCommon = new commonLib.VdCommon(programName);
        vdCommon.setLogLevel("Debug");

        vdCommon.printParams(o9Params);

        // 파라미터 가져오기
        var parsedParams = JSON.parse(o9Params);
        var fbProduct = parsedParams.fbProduct;
        var fbAttbNo = parsedParams.fbAttbNo;
        var fbClassCategory = parsedParams.fbClassCategory;
        var fbRuleNo = parsedParams.fbRuleNo;

        var no = fbRuleNo.substring(fbRuleNo.length - 2, fbRuleNo.length);
        vdCommon.debug("no : " + no);
        if ( no == "01" ) {
            RuleOutputToUI = { Status : 'Error', Message : "It cannot be deleted." };
            return;
        } else {
            var dimension = ['Version.[Version Name].[CurrentWorkingView]',
                                '[zz1Item Product].[Product].[' + fbProduct + ']',
                                '[zz1Item Attb].[Attb No].[' + fbAttbNo + ']',
                                '[Item].[Class Category].[' + fbClassCategory + ']',
                                '[zz1Item Attb Rule].[Rule No].[' + fbRuleNo + ']'];
            vdCommon.deleteMeasure(dimension, "zz1ClassCategory Attb Mapping");
        }

        vdCommon.programEnd();
    };

    return {
        zz1ClassCategoryAttbMappingDelete : callJs
    };
});