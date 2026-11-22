define('o9.NSCM.JSTargetEOHMustFlagUpdate', ['o9/data/query', 'o9/data/cellset', 'o9.NSCM.commonLibVD'], function () {
	const programName = "o9.NSCM.JSTargetEOHMustFlagUpdate";
    const commonLib = require('o9.NSCM.commonLib');
    const vdUtil = new commonLib.VdUtil();
    const log = new commonLib.VdCommon(programName);
    log.setLogLevel("Debug");

    var fn_cb_ynh = function(o9Params){
        const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
        vdCommon.setLogLevel("Debug");
        vdCommon.printParams(o9Params);

        try {
            var comboList = vdCommon.fn_makeCombo(null, {ComboCodes : ["Y","N"], ComboValues : ["Y","N"]});
            vdCommon.debug("ComboData : " + JSON.stringify(comboList));

            vdCommon.programEnd();

            return comboList;
        } catch ( e ) {
            RuleOutputToUI = { Status : 'Error', Message : "Js Logic Error : " + e.message };
            return;
        }
    };

    var fn_save1 = function(o9Params){
        const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
        vdCommon.setLogLevel("Debug");
        vdCommon.printParams(o9Params);

        try{
            // 파라메타 가져오기
            let p = JSON.parse(o9Params);

            var queryStr = "";
            for ( var i = 0; i < p.fbSelect.length; i++ ) {
                var row = p.fbSelect[i];

                var dimensions = ["&CWVUI"];
                if ( row.GC.Value != "All")
                    dimensions.push("[Sales Domain].[GC].[" + row.GC.Value + "]");
                if ( row.AP2.Value != "All")
                    dimensions.push("[Sales Domain].[AP2].[" + row.AP2.Value + "]");
                dimensions.push("[Item].[Segment].[" + row.Segment.Value + "]");
                queryStr += vdCommon.updateMeasureQuery(dimensions,
//                                                        ['Measure.[Target Ecp Set_SS Must] = ' + ( p.fb1SS == "Y" ? '"Y"' : "null") + ';']);
                                                        ['Measure.[Target Ecp Set_SS Must] = ' + ( p.fb1SS == "Y" ? '"Y"' : '"N"') + ';']);

                dimensions = ["&CWVUI"];
                if ( row.GC.Value != "All")
                    dimensions.push("[Sales Domain].[GC].[" + row.GC.Value + "]");
                if ( row.AP2.Value != "All")
                    dimensions.push("[Sales Domain].[AP2].[" + row.AP2.Value + "]");
                dimensions.push("[Item].[Segment].[" + row.Segment.Value + "].relatedmembers([Item])");
                queryStr += vdCommon.updateMeasureQuery(dimensions,
                                                        ['Measure.[SS_Must Flag] = ' + ( p.fb1SS == "Y" ? '"Y"' : "null") + ';',
                                                            vdUtil.fn_qMeaUpdateUser('Measure.[SS_Updated By]'),
                                                            vdUtil.fn_qMeaUpdateTime('Measure.[SS_Update Time]')]);
            }
            vdCommon.executeQuery("Batch Query 1" , queryStr);

            RuleOutputToUI = { Status : 'Success', Message : 'Bulk Update "Safety Stock" Successfully' };

            vdCommon.programEnd();
        }catch ( e ) {
            RuleOutputToUI = { Status : 'Error', Message : "Js Logic Error : " + e.message };
            return;
        }
    }

    var fn_save2 = function(o9Params){
        const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
        vdCommon.setLogLevel("Debug");
        vdCommon.printParams(o9Params);

        try{
            // 파라메타 가져오기
            let p = JSON.parse(o9Params);

            var queryStr = "";
            for ( var i = 0; i < p.fbSelect.length; i++ ) {
                var row = p.fbSelect[i];

                var dimensions = ["&CWVUI"];
                if ( row.GC.Value != "All")
                    dimensions.push("[Sales Domain].[GC].[" + row.GC.Value + "]");
                if ( row.AP2.Value != "All")
                    dimensions.push("[Sales Domain].[AP2].[" + row.AP2.Value + "]");
                dimensions.push("[Item].[Segment].[" + row.Segment.Value + "]");
                queryStr += vdCommon.updateMeasureQuery(dimensions,
//                                                        ['Measure.[Target Ecp Set_Build Ahead Must] = ' + ( p.fb2BAL == "Y" ? '"Y"' : "null") + ';']);
                                                        ['Measure.[Target Ecp Set_Build Ahead Must] = ' + ( p.fb2BAL == "Y" ? '"Y"' : '"N"') + ';']);

                dimensions = ["&CWVUI"];
                if ( row.GC.Value != "All")
                    dimensions.push("[Sales Domain].[GC].[" + row.GC.Value + "]");
                if ( row.AP2.Value != "All")
                    dimensions.push("[Sales Domain].[AP2].[" + row.AP2.Value + "]");
                dimensions.push("[Item].[Segment].[" + row.Segment.Value + "].relatedmembers([Item])");
                queryStr += vdCommon.updateMeasureQuery(dimensions,
                                                        ['Measure.[Build Ahead Cal_Must] = ' + ( p.fb2BAL == "Y" ? '"Y"' : "null") + ';',
                                                            vdUtil.fn_qMeaUpdateUser('Measure.[Build Ahead Cal_Updated By]'),
                                                            vdUtil.fn_qMeaUpdateTime('Measure.[Build Ahead Cal_Update Time]')]);
            }
            vdCommon.executeQuery("Batch Query 2" , queryStr);

            RuleOutputToUI = { Status : 'Success', Message : 'Bulk Update "Build Ahead Calendar" Successfully' };

            vdCommon.programEnd();
        }catch ( e ) {
            RuleOutputToUI = { Status : 'Error', Message : "Js Logic Error : " + e.message };
            return;
        }
    }

    return {
        fn_cb_ynh : fn_cb_ynh,
        fn_save1 : fn_save1,
        fn_save2 : fn_save2
    };
});

/**************************************************************************************
프로그램명  : o9.NSCM.JSTargetEOHMustFlagUpdate
화면명     : T.EOH Setting
개발자     : sungmin0.lim
최초생성   : 2025.10.22
AB        : ABTargetEOHMustFlagUpdate
**************************************************************************************/