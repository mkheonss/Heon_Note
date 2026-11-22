define('o9.JSMFGFrozenLv5Add', ['o9/data/query', 'o9/data/cellset', 'o9.ap.webservice.cliet'], function () {
    //gets all dimensions defined
    var FrozenValidate = function (o9Params) {
        Log.Info('----------------------Start  queryForCoverage -----------------------');

        var queryModule = require('o9/data/query');
        var cellsetModule = require('o9/data/cellset');

        var parsedParams = JSON.parse(o9Params);
        Log.Info('O9 parsedParams   ---' + JSON.stringify(parsedParams));
        Log.Info('----------------------Start  queryForCoverage -----------------------');

        // var queryForAll = 'Select ([Version].[Version Name].[CWV_MP] * [Global Top].[GT Code]);';
        // Log.Info('queryForAll ---' + queryForAll);
        // var data = cellsetModule.createCellSet(queryModule.select(queryForAll));
        // Log.Info('O9 data ---' + JSON.stringify(data));

        var GlobalTop = 'select ([Version].[Version Name].[CWV_MP] * &MPHorizon * [Item Material].[MSL1].['+ parsedParams.L1 +'] * [Item Material].[MSL2].['+ parsedParams.L2 +'] * [Item Material].[MSL3].['+ parsedParams.L3 +'] * [Item Material].[MSL5].['+ parsedParams.Inch +'] * {Measure.[Supply Frozen Mtrl L5 W_Fix Range]} );';
        var data = cellsetModule.createCellSet(queryModule.select(GlobalTop));
        Log.Info('O9 data ----------*********************--------------' + JSON.stringify(data));
        Log.Info('O9 data ---' + JSON.stringify(data.rowCount));
        // queryModule.update(data);
        
        Log.Info(' ------------------------------------ERROR--------------------------------------  ' + typeof(data.rowCount));
        // Log.Info(' er00000  ' + err);
        if (data.rowCount > 0) {
            RuleOutputToUI = {
                Status: 'Error',
                Message: 'Duplicate Record found:'
            };
            return;
        }

    };

    var fn_MSL1= function(o9Params){

        var queryModule = require('o9/data/query');
        var cellsetModule = require('o9/data/cellset');

        let parsedParams = JSON.parse(o9Params);

        var comboList = [];
        
        let queryMSL1 = 'select (&NSUIMtrlMSL1View);';
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
        var L1 = parsedParams.L1;

        var comboList = [];
        
        let queryMSL2 = 'select (&NSUIMtrlMSL1View.['+L1+']*&NSUIMtrlMSL2View);';
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
        var L2 = parsedParams.L2;

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

    var fn_MSL5= function(o9Params){

        var queryModule = require('o9/data/query');
        var cellsetModule = require('o9/data/cellset');

        let parsedParams = JSON.parse(o9Params);
        var L3 = parsedParams.L3;

        var comboList = [];

        let queryMSL5 = 'select (&NSUIMtrlMSL3View.['+L3+']*&NSUIMtrlMSL5View);';
        let queryMSL5Table = cellsetModule.createCellSet(queryModule.select(queryMSL5));
        let queryMSL5Row = queryMSL5Table.rowCount;
        for(let i=0;i<queryMSL5Row;i++)
        {
            let ffLev5 = queryMSL5Table.row(i).cell(queryMSL5Table.memberColumnIndex("Item Material","MSL5")).Name;
            let ffLev5DN = queryMSL5Table.row(i).cell(queryMSL5Table.memberColumnIndex("Item Material","MSL5")).DisplayName;
            let ffLev5DA = queryMSL5Table.row(i).cell(queryMSL5Table.memberColumnIndex("Item Material","MSL5")).DisplayAlias; 
            comboList.push({Name : ffLev5, DisplayName : ffLev5DA });
        }  
        
        Log.Info("ComboList MSL5: "+ JSON.stringify(comboList));
        return comboList;
    };


    return {
        fn_MSL1 : fn_MSL1,
        fn_MSL2 : fn_MSL2,
        fn_MSL3 : fn_MSL3,
        fn_MSL5 : fn_MSL5,
        FrozenValidate: FrozenValidate,
    };
});