define('o9.NSCM.JSItemAttrDistribute', ['o9/data/query', 'o9/data/cellset', 'o9.NSCM.commonLib'], function () {
    const programName = "o9.NSCM.JSItemAttrDistribute";

    var fn_classCategoryCombo = function(o9Params){
        try {
            const commonLib = require('o9.NSCM.commonLib');
            const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
            vdCommon.setLogLevel("Debug");

            var result = vdCommon.selectList(["[Item].[Product Group]", "[Item].[Product]", "&SETItem.relatedmembers([Class Category])"],
                                             [],
                                             "",
                                             "",
                                             "");
            vdCommon.printCsData(result, 3);

            var comboList = [];
            for ( var i = 0; i < result.cs.rowCount; i++ ) {
                name = result.cs.row(i).cell(result.cs.memberColumnIndex("Item", "Class Category")).Name;
                displayName = result.cs.row(i).cell(result.cs.memberColumnIndex("Item", "Class Category")).Name +
                                " ( " + result.cs.row(i).cell(result.cs.memberColumnIndex("Item", "Product Group")).Name +
                                " - " + result.cs.row(i).cell(result.cs.memberColumnIndex("Item", "Product")).Name + " )";

                comboList.push({ Name : name, DisplayName : displayName});
            }
            comboList.sort((a, b) =>{
                    if ( a.DisplayName < b.DisplayName ) return -1;
                    if ( a.DisplayName > b.DisplayName ) return 1;
                    return 0;
                });

            comboList.unshift({ Name : "All", DisplayName : "All"});

            vdCommon.programEnd();

            return comboList;
        } catch ( e ) {
            RuleOutputToUI = { Status : 'Error', Message : "Js Logic Error : " + e.message };
            return;
        }
    };

    var fn_apply = function(o9Params){
        try {
            const commonLib = require('o9.NSCM.commonLib');
            const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
            vdCommon.setLogLevel("Debug");

            vdCommon.printParams(o9Params);

            // 파라미터 가져오기
            var parsedParams = JSON.parse(o9Params);
            var fbClassCategory = parsedParams.fbClassCategory;
            var fbVersionName = parsedParams.fbVersionName;

            // 파이썬 실행
            if ( fbClassCategory == "All" ) {
                var execQuery = 'EXEC plugin instance [PY_UI_ItemAttrDistribute]  ' +
                                'for measures {[Item Attr_JDM]}  ' +
                                'using scope ([Version].[Version Name].[' + fbVersionName + ']) ' +
                                'using arguments {(createdBy, CurrentUser().Name), (outVersionName, "' + fbVersionName + '"), (ExecutionMode, "MediumWeight"), (MaxSliceTableCells, 200000000), (MaxConcurrency, 1 )};'
                vdCommon.executeQuery("Py Run", execQuery);
            } else {
                var execQuery = 'EXEC plugin instance [PY_UI_ItemAttrDistribute]  ' +
                                'for measures {[Item Attr_JDM]}  ' +
                                'using scope ( [Version].[Version Name].[' + fbVersionName + '] * [Item].[Class Category].[' + fbClassCategory + '] ) ' +
                                'using arguments {(createdBy, CurrentUser().Name), (outVersionName, "' + fbVersionName + '"), (ExecutionMode, "MediumWeight"), (MaxSliceTableCells, 200000000), (MaxConcurrency, 1 )};'
                vdCommon.executeQuery("Py Run", execQuery);
            }

            vdCommon.programEnd();
        } catch ( e ) {
            RuleOutputToUI = { Status : 'Error', Message : "Js Logic Error : " + e.message };
            return;
        }
    };

    var fn_publish = function(o9Params){
        try {
            const commonLib = require('o9.NSCM.commonLib');
            const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
            vdCommon.setLogLevel("Debug");

            vdCommon.printParams(o9Params);

            // 파라미터 가져오기
            var parsedParams = JSON.parse(o9Params);
            var fbClassCategory = parsedParams.fbClassCategory;
            var fbVersionName = parsedParams.fbVersionName;

            // IBPL 실행
            var execQuery = 'createMember(  ' +
                                '[Item].[Item]={,Item.#.Name},  ' +
                                '[Item].[B2B/B2C] = {,Measure.[Item Attr_B2B/B2C]},  ' +
                                '[Item].[Basic Name] = {,Measure.[Item Attr_Basic Name]},  ' +
                                '[Item].[Channel] = {,Measure.[Item Attr_Channel]},  ' +
                                '[Item].[CTN] = {,Measure.[Item Attr_CTN]},  ' +
                                '[Item].[Curved] = {,Measure.[Item Attr_Curved]},  ' +
                                '[Item].[Definition] = {,Measure.[Item Attr_Definition]},  ' +
                                '[Item].[Feature] = {,Measure.[Item Attr_Feature]},  ' +
                                '[Item].[Fixed] = {,Measure.[Item Attr_Fixed]},  ' +
                                '[Item].[Grade] = {,Measure.[Item Attr_Grade]},  ' +
                                '[Item].[Inch] = {,Measure.[Item Attr_Inch]},  ' +
                                '[Item].[Inch Group] = {,Measure.[Item Attr_Inch Group]},  ' +
                                '[Item].[Inch(Int)] = {,Measure.[Item Attr_Inch(Int)]},  ' +
                                '[Item].[JDM] = {,Measure.[Item Attr_JDM]},  ' +
                                '[Item].[Key Parts] = {,Measure.[Item Attr_Key Parts]},  ' +
                                '[Item].[KPI] = {,Measure.[Item Attr_KPI]},  ' +
                                '[Item].[Marketing Name] = {,Measure.[Item Attr_Marketing Name]},  ' +
                                '[Item].[Marketing Name2] = {,Measure.[Item Attr_Marketing Name2]},  ' +
                                '[Item].[Model Name] = {,Measure.[Item Attr_Model Name]},  ' +
                                '[Item].[Neo OLED] = {,Measure.[Item Attr_Neo OLED]},  ' +
                                '[Item].[OLED] = {,Measure.[Item Attr_OLED]},  ' +
                                '[Item].[Option] = {,Measure.[Item Attr_Option]},  ' +
                                '[Item].[Pet Name] = {,Measure.[Item Attr_Pet Name]},  ' +
                                '[Item].[Pitch] = {,Measure.[Item Attr_Pitch]},  ' +
                                '[Item].[Resolution] = {,Measure.[Item Attr_Resolution]},  ' +
                                '[Item].[Series] = {,Measure.[Item Attr_Series]},  ' +
                                '[Item].[Series Name] = {,Measure.[Item Attr_Series Name]},  ' +
                                '[Item].[Smart] = {,Measure.[Item Attr_Smart]},  ' +
                                '[Item].[Strategy] = {,Measure.[Item Attr_Strategy]},  ' +
                                '[Item].[Sub Product] = {,Measure.[Item Attr_Sub Product]},  ' +
                                '[Item].[Tuner] = {,Measure.[Item Attr_Tuner]},  ' +
                                '[Item].[WiFi] = {,Measure.[Item Attr_WiFi]},  ' +
                                '[Item].[Year] = {,Measure.[Item Attr_Year]},  ' +
                                '[Item].[Year Alphabet] = {,Measure.[Item Attr_Year Alphabet]}  ';

            if ( fbClassCategory == "All" ) {
                execQuery += ') using scope ([Version].[Version Name].[' + fbVersionName + '] * &SETItem.relatedmembers([Item])) ;  ';

                vdCommon.executeQuery("Py Run", execQuery);
            } else {
                execQuery += ') using scope ([Version].[Version Name].[' + fbVersionName + '] * [Item].[Class Category].[' + fbClassCategory + '].relatedmembers([Item])) ;  ';

                vdCommon.executeQuery("Py Run", execQuery);
            }

            vdCommon.programEnd();
        } catch ( e ) {
            RuleOutputToUI = { Status : 'Error', Message : "Js Logic Error : " + e.message };
            return;
        }
    };

    return {
        fn_classCategoryCombo : fn_classCategoryCombo,
        fn_apply : fn_apply,
        fn_publish : fn_publish
    };
});