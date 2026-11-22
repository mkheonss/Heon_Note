define('o9.vd.zz1ClassCategoryAttbRun', ['o9/data/query', 'o9/data/cellset', 'o9.vd.zz1CommonLib'], function () {

    var callJs = function(o9Params){
        var commonLib = require('o9.vd.zz1CommonLib');

        var programName = "o9.vd.zz1ClassCategoryAttbRun";
        vdCommon = new commonLib.VdCommon(programName);
        vdCommon.setLogLevel("Debug");

        vdCommon.printParams(o9Params);

        // 파라미터 가져오기
        var parsedParams = JSON.parse(o9Params);
        var fbProduct = parsedParams.fbProduct;
        var fbClassCategory = fbClassCategory = parsedParams.fbClassCategory;

        vdCommon.printStep("Class Category 의 Attb No 생성");
        dimension = ['Version.[Version Name].[CurrentWorkingView]',
                            '[zz1Item Product].[Product].[' + fbProduct + ']',
                            '[zz1Item Attb].[Attb No].[' + 'ATTB01' + ']',
                            '[Item].[Class Category].[' + fbClassCategory + ']',
                            '[zz1Item Attb Rule].[Rule No].[' + fbClassCategory + '_ATTB01_01' + ']'];
        if ( !vdCommon.existMeasure(dimension, ['Measure.[Item Attb Ref Attb Id]']) ) {
            var fbAttbNo = "ATTB01,ATTB02,ATTB03,ATTB04,ATTB05,ATTB06,ATTB07,ATTB08,ATTB09,ATTB10,ATTB11,ATTB12,ATTB13,ATTB14,ATTB15";
            var arrAttbNo = fbAttbNo.split(",");
            for ( const attbNo of arrAttbNo ) {
                vdCommon.debug("attbNo" + " : " + attbNo);

                ruleNo = fbClassCategory + '_' + attbNo + '_01';

                var dimension = ['Version.[Version Name].[CurrentWorkingView]',
                                    '[zz1Item Product].[Product].[' + fbProduct + ']',
                                    '[zz1Item Attb].[Attb No].[' + attbNo + ']',
                                    '[Item].[Class Category].[' + fbClassCategory + ']',
                                    '[zz1Item Attb Rule].[Rule No].[' + ruleNo + ']'];
                vdCommon.createMember('[zz1Item Attb Rule].[Rule No]', ruleNo);
                vdCommon.createMeasure(dimension,
                            ['Measure.[Item Attb Ref Attb Id] = "-";',
                            'Measure.[Item Rule Seq] = 1;']);
            }
        } else {
            RuleOutputToUI = { Status : 'Error', Message : "This Data has already been registered." };
            return;
        }

        vdCommon.programEnd();
    };

    return {
        zz1ClassCategoryAttbRun : callJs
    };
});