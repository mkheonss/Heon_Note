define('o9.JS_Material BOD Item_Delete-Validation', ['o9/data/query', 'o9/data/cellset', 'o9.ap.webservice.cliet'], function () {
    //Code Reviewed
    //By - Amit Kumar
    //Date: 28 Nov 2024
    var Delete = function (props) {
        Log.Info('----------------------Start  queryForCoverage -----------------------');

        var queryModule = require('o9/data/query');
        var cellsetModule = require('o9/data/cellset');


        Log.Info('----------------------Start  queryForCoverage -----------------------');


        var queryForTime = 'Select ([Version].[Version Name].[CWV_MP] * [Time].[Week].filter(#.Key >= &CurrentWeek.element(0).Key && #.Key <= &CurrentWeek.element(0).LeadOffset(12).Key));';

        var time = cellsetModule.createCellSet(queryModule.select(queryForTime));
        Log.Info('O9 data ---' + JSON.stringify(time));

        var timeArr = [];

        for (let i = 0; i < time.rowCount; i++) {
            var value = time.row(i).cell(time.memberColumnIndex('Time', 'Week')).Name;
            Log.Info('----------------------------------------------------' + value);
            timeArr.push(time.row(i).cell(time.memberColumnIndex('Time', 'Week')).Name);
        }

        Log.Info('-----------------------------------' + timeArr);

        Log.Info('-----------------------------------' + timeArr.length);

        var parsedParams = JSON.parse(props);

        Log.Info('-------------------------' + parsedParams);

        Log.Info('---------------------' + JSON.stringify(parsedParams));

        Log.Info('---------------------' + parsedParams.DeleteTuple);

        Log.Info('---------------------' + JSON.stringify(parsedParams.DeleteTuple));

        Log.Info('---------------------' + JSON.stringify(parsedParams.DeleteTuple.SubLoc));

        Log.Info('---------------------' + JSON.stringify(parsedParams.DeleteTuple[0].SubLoc));

        Log.Info('---------------------' + JSON.stringify(parsedParams.DeleteTuple[0].SubLoc.Value));

        Log.Info('---------------------' + parsedParams.DeleteTuple.length);


        for (var i = 0; i < parsedParams.DeleteTuple.length; i++) {
            var curr = parsedParams.DeleteTuple[i];

            Log.Info('---------------------' + JSON.stringify(curr.SubLoc.Value));
            Log.Info('---------------------' + JSON.stringify(curr.BODTransport.Value));
            Log.Info('---------------------' + JSON.stringify(curr.Loc.Value));
            Log.Info('---------------------' + JSON.stringify(curr.Item.Value));

            var k = 0;

            for (let i = 0; i < timeArr.length; i++) {

                var query = 'Select ([Version].[Version Name].[CWV_MP] * [Location].[Location].[' + curr.Loc.Value + '] * [Trans Mode].[Trans Mode].[' + curr.BODTransport.Value + '] * [Sub Location].[Sub Location].[' + curr.SubLoc.Value + '] * [Time].[Week].[' + timeArr[i] + '] * [Item Material].[Item Material].[' + curr.Item.Value + '] * {Measure.[BOD Item Mtrl W_Factory Out], Measure.[BOD Item Mtrl W_GR LT], Measure.[BOD Item Mtrl W_Intransit LT], Measure.[BOD Item Mtrl W_Port To Port], Measure.[BOD Item Mtrl W_Supplier], Measure.[BOD Item Mtrl W_Total LT], Measure.[BOD Item Mtrl_Lock Flag]});';

                var d = cellsetModule.createCellSet(queryModule.select(query));

                var v1 = d.row(0).cell(d.measureColumnIndex('BOD Item Mtrl W_Total LT'));

                if (v1 == 0 || v1 == null) {
                    k++;
                }
            }
            Log.Info('-----------------------------------------------------------------' + k);
            let state = 'delete data for model [BOD Item Mtrl W] where {Version.[Version Name].[CWV_MP], [Location].[Location].[' + curr.Loc.Value + '], [Trans Mode].[Trans Mode].[' + curr.BODTransport.Value + '], [Sub Location].[Sub Location].[' + curr.SubLoc.Value + '], [Item Material].[Item Material].[' + curr.Item.Value + ']};';
                    queryModule.update(state);
            
            /*
            var del = d.row(0).cell(d.measureColumnIndex('BOD Item Mtrl_Lock Flag'));

            Log.Info('-----------------------------------------------------------------' + del);
            
            if (k == timeArr.length) {
                if (del == 'Y') {
                    RuleOutputToUI = {
                        Status: 'Error',
                        Message: 'Some cells are locked. Unlock then try again'
                    };
                }
                else {
                    Log.Info('--------------------------------Delete Command ----------------------');

                    let state = 'delete data for model [BOD Item Mtrl W] where {Version.[Version Name].[CWV_MP], [Location].[Location].[' + curr.Loc.Value + '], [Trans Mode].[Trans Mode].[' + curr.BODTransport.Value + '], [Sub Location].[Sub Location].[' + curr.SubLoc.Value + '], [Item Material].[Item Material].[' + curr.Item.Value + ']};';
                    queryModule.update(state);
                }
            }
            else {
                RuleOutputToUI = {
                    Status: 'Error',
                    Message: 'There is some data available in SOP Quantity. You can not delete it.'
                };
            }
        */
        }

    };

    return {
        Delete: Delete
    };
});