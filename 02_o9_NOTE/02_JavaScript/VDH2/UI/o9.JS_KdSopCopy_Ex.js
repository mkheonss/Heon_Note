define('o9.JS_KdSopCopy_Ex', ['o9/data/query', 'o9/data/cellset', 'o9.NSCM.commonLib'], function () {

    const programName = "o9.JS_KdSopCopy_Ex ============>";
    const commonLib = require('o9.NSCM.commonLib');
    const queryModule = require('o9/data/query');
    const cellsetModule = require('o9/data/cellset');
    vdCommon = new commonLib.VdCommon(programName);    
    

    var fn_Excluder1 = function(o9Params){ 
        vdUtil = new commonLib.VdUtil();

        vdCommon.setLogLevel("Debug");

        vdCommon.printParams(o9Params);
        
        let checkQuery = 'Select ([Version].[Version Name].[CWV_MP]* [Item].[Item]*[Item].[ProductType].filter(#.Name in {"SKD","CKD"})  ) on row,({Measure.[BOD Item_Asn]}) on column;';
        var checkQueryResult = cellsetModule.createCellSet(queryModule.select(checkQuery));
        var checkQueryResultRow = checkQueryResult.rowCount;

        var diffArray = [];
        for (let i = 0; i < checkQueryResultRow; i++) {
            var checkItem = checkQueryResult.row(i).cell(checkQueryResult.memberColumnIndex("Item","Item")).Name;
                diffArray.push({Name : checkItem,DisplayName : checkItem});
            }
        vdCommon.debug("ShowRow-: " + diffArray);
                
        return diffArray;
        
    };

    var fn_Excluder2 = function(o9Params){ 
        vdUtil = new commonLib.VdUtil();

        vdCommon.setLogLevel("Debug");

        vdCommon.printParams(o9Params);
        
        let checkQuery = 'Select ([Version].[Version Name].[CWV_MP]* [Item].[Item]*[Item].[ProductType].filter(#.Name in {"SKD","CKD","CRT"})  ) on row,({Measure.[BOD Item_Asn]}) on column;';
        var checkQueryResult = cellsetModule.createCellSet(queryModule.select(checkQuery));
        var checkQueryResultRow = checkQueryResult.rowCount;

        var diffArray = [];
        for (let i = 0; i < checkQueryResultRow; i++) {
            var checkItem = checkQueryResult.row(i).cell(checkQueryResult.memberColumnIndex("Item","Item")).Name;
                diffArray.push({Name : checkItem,DisplayName : checkItem});
            }
        vdCommon.debug("ShowRow-: " + diffArray);
                
        return diffArray;
        
    };

    return {
        fn_Excluder1 : fn_Excluder1,
        fn_Excluder2 : fn_Excluder2
    };

});