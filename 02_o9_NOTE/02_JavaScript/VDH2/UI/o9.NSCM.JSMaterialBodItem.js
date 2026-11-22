define('o9.NSCM.JSMaterialBodItem', ['o9/data/query', 'o9/data/cellset', 'o9.NSCM.commonLib'], function () {
    const programName = "o9.NSCM.JSMaterialBodItem";

    var fn_ditto = function(o9Params){
        const commonLib = require('o9.NSCM.commonLib');
        const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
        const vdUtil = new commonLib.VdUtil();

        try {
            vdCommon.setLogLevel("Debug");

            vdCommon.printParams(o9Params);

            // 파라미터 가져오기
            var parsedParams = JSON.parse(o9Params);
            var fbSelect = parsedParams.fbSelect;
            var fbWeek = parsedParams.fbWeek.split(",");
            var fbFromWeek = parsedParams.fbFromWeek;
            var fbToWeek = parsedParams.fbToWeek;
            var fbFactoryOut = parsedParams.fbFactoryOut;
            var fbPorttoPortLT = parsedParams.fbPorttoPortLT;
            var fbGrLT = parsedParams.fbGrLT;

            if ( fbToWeek == null ) {
                fbToWeek = fbWeek[fbWeek.length - 1];
            }
            vdCommon.debug("fbFactoryOut : " + fbFactoryOut + " , fbPorttoPortLT : " + fbPorttoPortLT + " , fbGrLT : " + fbGrLT)

            if ( fbFactoryOut == null && fbPorttoPortLT == null && fbGrLT == null ) {
                RuleOutputToUI = { Status : 'Error', Message : "You must enter at least one piece of data." };
                return;
            }

            for ( var i = 0; i < fbSelect.length; i++ ) {
                var row = fbSelect[i];

                var measures = [];
                if ( fbFactoryOut != null ) {
                    measures.push('Measure.[BOD Item Mtrl W_Factory Out] = ' + fbFactoryOut + ';');
                }
                if ( fbPorttoPortLT != null ) {
                    measures.push('Measure.[BOD Item Mtrl W_Port To Port] = ' + fbPorttoPortLT + ';');
                }
                if ( fbGrLT != null ) {
                    measures.push('Measure.[BOD Item Mtrl W_GR LT] = ' + fbGrLT + ';');
                }
                var queryStr = vdCommon.createMeasureQuery(["&CWVUI",
                                                                "[Location].[Location].[" + row.Location.Value + "]",
                                                                "[Item Material].[Item Material].[" + row.Item.Value + "]",
                                                                "[Trans Mode].[Trans Mode].[" + row.TransMode.Value + "]",
                                                                "[Sub Location].[Sub Location].[" + row.SubLocation.Value + "]",
                                                                '[Time].[Week].filter(#.Name >= "' + fbFromWeek + '" && #.Name <= "' + fbToWeek + '")'],
                                                             measures);
                vdCommon.executeQuery("Batch Query" , queryStr);
            }

            vdCommon.programEnd();
        } catch ( e ) {
            RuleOutputToUI = { Status : 'Error', Message : "Js Logic Error : " + e.message };
            return;
        }
    };

    return {
        fn_ditto : fn_ditto
    };
});

/**************************** o9.NSCM.JSMaterialBodItem ****************************
    2025-04-25 : 신규 생성
*********************************************************************/