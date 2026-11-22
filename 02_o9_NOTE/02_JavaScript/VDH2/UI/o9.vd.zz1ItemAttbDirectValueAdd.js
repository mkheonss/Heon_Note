define('o9.vd.zz1ItemAttbDirectValueAdd', ['o9/data/query', 'o9/data/cellset', 'o9.vd.zz1CommonLib'], function () {

    var callJs = function(o9Params){
        var commonLib = require('o9.vd.zz1CommonLib');

        var programName = "o9.vd.zz1ItemAttbDirectValueAdd";
        vdCommon = new commonLib.VdCommon(programName);
        vdCommon.setLogLevel("Debug");

        vdCommon.printParams(o9Params);

        // 파라미터 가져오기
        var parsedParams = JSON.parse(o9Params);
        var fbItem = parsedParams.fbItem;

        if ( !vdCommon.existMember('[Item].[Item]', fbItem) ) {
            RuleOutputToUI = { Status : 'Error', Message : "Item not exist." };
            return;
        }


        var dimension = ['Version.[Version Name].[CurrentWorkingView]',
                            '[Item].[Item].[' + fbItem + ']'];
        if ( !vdCommon.existMeasure(dimension, ['Measure.[Item Attb Direct 01]']) ) {
            vdCommon.createMeasure(dimension,
                        ['Measure.[Item Attb Direct 01] = "-";',
                        'Measure.[Item Attb Direct 02] = "-";',
                        'Measure.[Item Attb Direct 03] = "-";',
                        'Measure.[Item Attb Direct 04] = "-";',
                        'Measure.[Item Attb Direct 05] = "-";',
                        'Measure.[Item Attb Direct 06] = "-";',
                        'Measure.[Item Attb Direct 07] = "-";',
                        'Measure.[Item Attb Direct 08] = "-";',
                        'Measure.[Item Attb Direct 09] = "-";',
                        'Measure.[Item Attb Direct 10] = "-";',
                        'Measure.[Item Attb Direct 11] = "-";',
                        'Measure.[Item Attb Direct 12] = "-";',
                        'Measure.[Item Attb Direct 13] = "-";',
                        'Measure.[Item Attb Direct 14] = "-";',
                        'Measure.[Item Attb Direct 15] = "-";']);
        } else {
            RuleOutputToUI = { Status : 'Error', Message : "This Data has already been registered." };
            return;
        }

        vdCommon.programEnd();
    };

    return {
        zz1ItemAttbDirectValueAdd : callJs
    };
});