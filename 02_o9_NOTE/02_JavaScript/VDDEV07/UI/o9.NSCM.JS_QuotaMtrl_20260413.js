define('o9.NSCM.JS_QuotaMtrl', ['o9/data/query', 'o9/data/cellset', 'o9.NSCM.commonLib'], function () {
    var fn_validation = function(o9Params){
        try {
            var commonLib = require('o9.NSCM.commonLib');

            var programName = "o9.NSCM.JS_QuotaMtrl ============> fn_validation";

            vdUtil = new commonLib.VdUtil();
            vdCommon = new commonLib.VdCommon(programName);
            vdCommon.setLogLevel("Debug");

            vdCommon.printParams(o9Params);

            // 파라미터 가져오기
            var parsedParams = JSON.parse(o9Params);
            var GroupID = parsedParams.GroupID;
            var GroupName = parsedParams.GroupName;

            var rtn = 0;
            var result = vdCommon.selectList(
                                ["[Group].[Group ID]",
                                    "[Group].[Group Name].[" + GroupName + "]",
                                    "[Group].[Group Type].[Quota]"],
                                [], "", "", "");
            if ( result.cs.rowCount > 0 ) {
                RuleOutputToUI = { Status : 'Error', Message : "This Data has already been registered." };
                rtn = 1;
                return;
            }

            vdCommon.programEnd();

            return rtn;
        } catch ( e ) {
            RuleOutputToUI = { Status : 'Error', Message : "Js Logic Error : " + e.message };
            return 1;
        }
    };

    var fn_plantAdd = function(o9Params){
        try {
            var commonLib = require('o9.NSCM.commonLib');

            var programName = "o9.NSCM.JS_QuotaMtrl ============> fn_plantAdd";

            vdUtil = new commonLib.VdUtil();
            vdCommon = new commonLib.VdCommon(programName);
            vdCommon.setLogLevel("Debug");

            vdCommon.printParams(o9Params);

            // 파라미터 가져오기
            var parsedParams = JSON.parse(o9Params);
            var fbGroupID = parsedParams.fbGroupID;
            var fbLocation = parsedParams.fbLocation;

            for ( var i = 0; i < fbGroupID.length; i++ ) {
                vdCommon.debug("fbGroupID : " + fbGroupID[i]);

                // Item 목록을 만든다.
                var items = [];
                var result = vdCommon.selectList(
                                            ["&CWV",
                                                "[Group].[Group ID].[" + fbGroupID[i] + "]",
                                                "[Item Material].[Item Material]"],
                                            ["Measure.[Global Quota Mtrl W_Portion]",
                                                "Measure.[Global Quota Mtrl W_Quota Sync]"],
                                            "",
                                            "",
                                            "");
                vdCommon.printCsData(result, 3);
                for ( var k = 0; k < result.cs.rowCount; k++ ) {
                    items.push(result.cs.row(k).cell(result.cs.memberColumnIndex("Item Material", "Item Material")).Name);
                }
                vdCommon.debug("items : " + items.join(","));

                var queryStr = "";
                for ( var m = 0; m < fbLocation.length; m++ ) {
                    vdCommon.debug("fbLocation : " + fbLocation[m]);
                    for ( var q = 0; q < items.length; q++ ) {
                        // 값이 0인 기준 데이타 생성
                        queryStr += vdCommon.createMeasureQuery(
                                        ["&CWV",
                                            "[Group].[Group ID].[" + fbGroupID[i] + "]",
                                            "[Location].[Location].[" + fbLocation[m] + "]",
                                            "[Item Material].[Item Material].[" + items[q] + "]",
                                            "&AllWeeks.Filter(#.Key >= &CurrentWeek.element(0).LeadOffset(0).Key && #.Key <= &CurrentWeek.element(0).LeadOffset(34).Key)"],
                                        ["Measure.[Plant Quota Mtrl W_Portion] = 0;"]);

                        // Group Quota 값으로 세팅
                        queryStr += vdCommon.createMeasureQuery(
                                        ["&CWV",
                                            "[Group].[Group ID].[" + fbGroupID[i] + "]",
                                            "[Location].[Location].[" + fbLocation[m] + "]",
                                            "[Item Material].[Item Material].[" + items[q] + "]",
                                            "&AllWeeks.Filter(#.Key >= &CurrentWeek.element(0).LeadOffset(0).Key && #.Key <= &CurrentWeek.element(0).LeadOffset(34).Key)"],
                                        ["Measure.[Plant Quota Mtrl W_Portion] = Measure.[Global Quota Mtrl W_Portion];"]);
                    }
                }

                vdCommon.executeQuery("Batch Query" , queryStr);
            }

            vdCommon.programEnd();
        } catch ( e ) {
            RuleOutputToUI = { Status : 'Error', Message : "Js Logic Error : " + e.message };
            return;
        }
    };

    var fn_plantAdd_combo = function(o9Params){
        try {

            var commonLib = require('o9.NSCM.commonLib');

            var programName = "o9.NSCM.JS_QuotaMtrl ============> fn_plantAdd_combo";
            vdCommon = new commonLib.VdCommon(programName);
            vdCommon.setLogLevel("Debug");

            vdCommon.printParams(o9Params);

            // 파라미터 가져오기
            var parsedParams = JSON.parse(o9Params);

            vdCommon.printStep("Combo Data Get");
            var result = vdCommon.selectList(['Location.[Location].filter(#.[Site Type] == "MF")'],
                                             [],
                                             "",
                                             "orderby Location.[Location].DisplayName asc",
                                             "");
            vdCommon.printCsData(result, 3);

            var comboList = [];
            for ( var i = 0; i < result.cs.rowCount; i++ ) {
                comboList.push({
                        Name : result.cs.row(i).cell(result.cs.memberColumnIndex("Location", "Location")).Name,
                        DisplayName : result.cs.row(i).cell(result.cs.memberColumnIndex("Location", "Location")).DisplayName
                    });
            }

            vdCommon.programEnd();

            return comboList;
        } catch ( e ) {
            RuleOutputToUI = { Status : 'Error', Message : "Js Logic Error : " + e.message };
            return;
        }
    };

    return {
        fn_validation : fn_validation,
        fn_plantAdd : fn_plantAdd,
        fn_plantAdd_combo : fn_plantAdd_combo
    };
}); 
//JS_QuotaMtrl