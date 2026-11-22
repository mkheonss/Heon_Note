define('o9.MaterilBODAddDisplayAlias', ['o9/data/query', 'o9/data/cellset', 'o9.ap.webservice.cliet'], function () {
   
    var fn_MSL1= function(o9Params){

        var queryModule = require('o9/data/query');
        var cellsetModule = require('o9/data/cellset');

        let parsedParams = JSON.parse(o9Params);

        var comboList = [];
        
        let queryMSL1 = 'select ([Item Material].[MSL1].Filter(#.Name in {"Panel", "Semicon."}));';
        let queryMSL1Table = cellsetModule.createCellSet(queryModule.select(queryMSL1)); 
        let queryMSL1Row = queryMSL1Table.rowCount;
        for(let i=0;i<queryMSL1Row;i++)
        {
            let ffLev1 = queryMSL1Table.row(i).cell(queryMSL1Table.memberColumnIndex("Item Material","MSL1")).Name;
            let ffLev1DN = queryMSL1Table.row(i).cell(queryMSL1Table.memberColumnIndex("Item Material","MSL1")).DisplayName;
            let ffLev1DA = queryMSL1Table.row(i).cell(queryMSL1Table.memberColumnIndex("Item Material","MSL1")).DisplayAlias;   
            comboList.push({Name : ffLev1, DisplayName : ffLev1DA });
        }

        Log.Info("ComboList MSL1: "+ JSON.stringify(comboList));
        return comboList;
    };

    var fn_MSL2= function(o9Params){

        var queryModule = require('o9/data/query');
        var cellsetModule = require('o9/data/cellset');

        let parsedParams = JSON.parse(o9Params);
        var L1 = parsedParams.SCMLevel1;

        var comboList = [];
        
        let queryMSL2 = 'select ([Item Material].[MSL1].['+L1+']*&NSUIMtrlMSL2View);';
        let queryMSL2Table = cellsetModule.createCellSet(queryModule.select(queryMSL2)); 
        let queryMSL2Row = queryMSL2Table.rowCount;
        for(let i=0;i<queryMSL2Row;i++)
        {
            let ffLev2 = queryMSL2Table.row(i).cell(queryMSL2Table.memberColumnIndex("Item Material","MSL2")).Name;
            let ffLev2DN = queryMSL2Table.row(i).cell(queryMSL2Table.memberColumnIndex("Item Material","MSL2")).DisplayName;
            let ffLev2DA = queryMSL2Table.row(i).cell(queryMSL2Table.memberColumnIndex("Item Material","MSL2")).DisplayAlias;   
            comboList.push({Name : ffLev2, DisplayName : ffLev2DA });
        }
        Log.Info("ComboList MSL2: "+ JSON.stringify(comboList));
        return comboList;
    };

    var fn_MSL3= function(o9Params){

        var queryModule = require('o9/data/query');
        var cellsetModule = require('o9/data/cellset');

        let parsedParams = JSON.parse(o9Params);
        var L2 = parsedParams.SCMLevel2;

        var comboList = [];

        let queryMSL3 = 'select (&NSUIMtrlMSL2View.['+L2+']*&NSUIMtrlMSL3View);';
        let queryMSL3Table = cellsetModule.createCellSet(queryModule.select(queryMSL3));
        let queryMSL3Row = queryMSL3Table.rowCount;
        for(let i=0;i<queryMSL3Row;i++)
        { 
            let ffLev3 = queryMSL3Table.row(i).cell(queryMSL3Table.memberColumnIndex("Item Material","MSL3")).Name;
            let ffLev3DN = queryMSL3Table.row(i).cell(queryMSL3Table.memberColumnIndex("Item Material","MSL3")).DisplayName;
            let ffLev3DA = queryMSL3Table.row(i).cell(queryMSL3Table.memberColumnIndex("Item Material","MSL3")).DisplayAlias;   
            comboList.push({Name : ffLev3, DisplayName : ffLev3DA });
        }
        Log.Info("ComboList MSL3: "+ JSON.stringify(comboList));
        return comboList;
    };

    return {
        fn_MSL1 : fn_MSL1,
        fn_MSL2 : fn_MSL2,
        fn_MSL3 : fn_MSL3
    };
});