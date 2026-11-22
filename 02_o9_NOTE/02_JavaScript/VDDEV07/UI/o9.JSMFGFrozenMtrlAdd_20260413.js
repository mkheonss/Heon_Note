define('o9.JSMFGFrozenMtrlAdd', ['o9/data/query', 'o9/data/cellset', 'o9.ap.webservice.cliet'], function () {
    //gets all dimensions defined

    var FrozenValidate2 = function (o9Params) {
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

        //var GlobalTop = 'Select ([Version].[Version Name].[CWV_MP] * [Global Top].[GT Name Fix].['+ parsedParams.Vendor +'] * [Trans Mode].[Trans Mode].['+ parsedParams.TPMode +'] * [Location].[Location].['+ parsedParams.Plant +'] * [Time].[Week] * [Item Material].[MSL1].['+ parsedParams.SCMLevel1 +'] * [Item Material].[MSL2].['+ parsedParams.SCMLevel2 +'] * [Item Material].[MSL3].['+ parsedParams.SCMLevel3 +'] * {Measure.[BOD Item Mtrl W_Factory Out], Measure.[BOD Item Mtrl W_GR LT], Measure.[BOD Item Mtrl W_Intransit LT], Measure.[BOD Item Mtrl W_Port To Port], Measure.[BOD Item Mtrl W_Supplier]});';
        
        Log.Info('O9 data ----------*********************--------------');
        var GlobalTop = 'Select ([Version].[Version Name].[CWV_MP] * [Time].[Week]  * [Item Material].[MSL1].['+ parsedParams.L1 +'] * [Item Material].[MSL2].['+ parsedParams.L2 +'] * [Item Material].[MSL3].['+ parsedParams.L3 +'] * [Item Material].[MSL5].['+ parsedParams.Inch +']* [Item Material].[Item Material].['+ parsedParams.ItemMaterial +'] * [Location].[Location].['+ parsedParams.FromSite +'] * {Measure.[Supply Frozen Mtrl Item W_Fix Range]});';
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

    return {
        FrozenValidate2: FrozenValidate2
    };
});