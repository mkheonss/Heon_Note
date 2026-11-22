define('o9.JS_Material BOD Ditto', ['o9/data/query', 'o9/data/cellset', 'o9.ap.webservice.cliet'], function () {
    //gets all dimensions defined
    const Ditto = function (props) {
        try {
            const queryModule = require('o9/data/query');
            const cellsetModule = require('o9/data/cellset');

            var queryForTime = 'Select ([Version].[Version Name].[CWV_MP] * [Time].[Week].filter(#.Key >= &CurrentWeek.element(0).Key && #.Key <= &CurrentWeek.element(0).LeadOffset(34).Key));';

            var time = cellsetModule.createCellSet(queryModule.select(queryForTime));
            Log.Info('O9 Time data ---' + JSON.stringify(time));

            var timeArr = [];

            for (let i = 0; i < time.rowCount; i++) {
                var value = time.row(i).cell(time.memberColumnIndex('Time', 'Week')).Name;
                timeArr.push(value);
            }

            var parsedParams = JSON.parse(props);

            for (var j = 0; j < parsedParams.DittoTuple.length; j++) {
                var curr = parsedParams.DittoTuple[j];

                var factory_out = Number.MIN_SAFE_INTEGER;
                var gr_lt = Number.MIN_SAFE_INTEGER;
                var port_to_port = Number.MIN_SAFE_INTEGER;

                //Query for the current week
                var query = 'Select ([Version].[Version Name].[CWV_MP] * [Location].[Location].[' + curr.Loc.Value + '] * [Trans Mode].[Trans Mode].[' + curr.BODTransport.Value + '] * [Sub Location].[Sub Location].[' + curr.SubLoc.Value + '] * [Time].[Week].[' + timeArr[0] + '] * [Item Material].[MSL3].[' + curr.Item.Value + '] * {Measure.[BOD List Mtrl W_Factory Out], Measure.[BOD List Mtrl W_GR LT], Measure.[BOD List Mtrl W_Port To Port]});';

                query = cellsetModule.createCellSet(queryModule.select(query));

                var currWeek = timeArr[0];
                var prevWeeek = currWeek - 1;

                Log.Info("------------------------------------------------------------Current Weeek : " + currWeek);
                Log.Info("------------------------------------------------------------Current Weeek : " + prevWeeek);

                //fetching and checking if the measure value is null
                var v1 = query.row(0).cell(query.measureColumnIndex('BOD List Mtrl W_Factory Out'));
                if (v1 == undefined) {
                    var prevQuery = 'Select ([Version].[Version Name].[CWV_MP] * [Location].[Location].[' + curr.Loc.Value + '] * [Trans Mode].[Trans Mode].[' + curr.BODTransport.Value + '] * [Sub Location].[Sub Location].[' + curr.SubLoc.Value + '] * [Time].[Week].[' + prevWeeek + '] * [Item Material].[MSL3].[' + curr.Item.Value + '] * {Measure.[BOD List Mtrl W_Factory Out], Measure.[BOD List Mtrl W_GR LT], Measure.[BOD List Mtrl W_Port To Port]});';

                    prevQuery = cellsetModule.createCellSet(queryModule.select(prevQuery));

                    var v = prevQuery.row(0).cell(prevQuery.measureColumnIndex('BOD List Mtrl W_Factory Out'));

                    if (v != undefined) {
                        factory_out = v;
                    }
                }

                var v2 = query.row(0).cell(query.measureColumnIndex('BOD List Mtrl W_GR LT'));
                if (v2 == undefined) {
                    var prevQuery = 'Select ([Version].[Version Name].[CWV_MP] * [Location].[Location].[' + curr.Loc.Value + '] * [Trans Mode].[Trans Mode].[' + curr.BODTransport.Value + '] * [Sub Location].[Sub Location].[' + curr.SubLoc.Value + '] * [Time].[Week].[' + prevWeeek + '] * [Item Material].[MSL3].[' + curr.Item.Value + '] * {Measure.[BOD List Mtrl W_Factory Out], Measure.[BOD List Mtrl W_GR LT], Measure.[BOD List Mtrl W_Port To Port]});';

                    prevQuery = cellsetModule.createCellSet(queryModule.select(prevQuery));

                    var v = prevQuery.row(0).cell(prevQuery.measureColumnIndex('BOD List Mtrl W_GR LT'));

                    if (v != undefined) {
                        gr_lt = v;
                    }
                }

                var v3 = query.row(0).cell(query.measureColumnIndex('BOD List Mtrl W_Port To Port'));
                if (v3 == undefined) {
                    var prevQuery = 'Select ([Version].[Version Name].[CWV_MP] * [Location].[Location].[' + curr.Loc.Value + '] * [Trans Mode].[Trans Mode].[' + curr.BODTransport.Value + '] * [Sub Location].[Sub Location].[' + curr.SubLoc.Value + '] * [Time].[Week].[' + prevWeeek + '] * [Item Material].[MSL3].[' + curr.Item.Value + '] * {Measure.[BOD List Mtrl W_Factory Out], Measure.[BOD List Mtrl W_GR LT], Measure.[BOD List Mtrl W_Port To Port]});';

                    prevQuery = cellsetModule.createCellSet(queryModule.select(prevQuery));

                    var v = prevQuery.row(0).cell(prevQuery.measureColumnIndex('BOD List Mtrl W_Port To Port'));

                    if (v != undefined) {
                        port_to_port = v;
                    }
                } 

                for (let i = 0; i < timeArr.length; i++) {
                    query = 'Select ([Version].[Version Name].[CWV_MP] * [Location].[Location].[' + curr.Loc.Value + '] * [Trans Mode].[Trans Mode].[' + curr.BODTransport.Value + '] * [Sub Location].[Sub Location].[' + curr.SubLoc.Value + '] * [Time].[Week].[' + timeArr[i] + '] * [Item Material].[MSL3].[' + curr.Item.Value + '] * {Measure.[BOD List Mtrl W_Factory Out], Measure.[BOD List Mtrl W_GR LT], Measure.[BOD List Mtrl W_Port To Port]});';

                    query = cellsetModule.createCellSet(queryModule.select(query));

                    v1 = query.row(0).cell(query.measureColumnIndex('BOD List Mtrl W_Factory Out'));
                    if (v1 == undefined) {
                        if (factory_out != Number.MIN_SAFE_INTEGER) {
                            var updateQuery = 'cartesian scope: ([Version].[Version Name].[CWV_MP] * [Location].[Location].[' + curr.Loc.Value + '] * [Trans Mode].[Trans Mode].[' + curr.BODTransport.Value + '] * [Sub Location].[Sub Location].[' + curr.SubLoc.Value + '] * [Time].[Week].[' + timeArr[i] + '] * [Item Material].[MSL3].[' + curr.Item.Value + ']); Measure.[BOD List Mtrl W_Factory Out]=' + factory_out + '; end scope;';
                            queryModule.update(updateQuery);
                        }
                    }
                    else {
                        factory_out = v1;
                    }

                    v2 = query.row(0).cell(query.measureColumnIndex('BOD List Mtrl W_GR LT'));
                    if (v2 == undefined) {
                        if (gr_lt != Number.MIN_SAFE_INTEGER) {
                            var updateQuery = 'cartesian scope: ([Version].[Version Name].[CWV_MP] * [Location].[Location].[' + curr.Loc.Value + '] * [Trans Mode].[Trans Mode].[' + curr.BODTransport.Value + '] * [Sub Location].[Sub Location].[' + curr.SubLoc.Value + '] * [Time].[Week].[' + timeArr[i] + '] * [Item Material].[MSL3].[' + curr.Item.Value + ']); Measure.[BOD List Mtrl W_GR LT]=' + gr_lt + '; end scope;';
                            queryModule.update(updateQuery);
                        }
                    }
                    else {
                        gr_lt = v2;
                    }

                    v3 = query.row(0).cell(query.measureColumnIndex('BOD List Mtrl W_Port To Port'));
                    if (v3 == undefined) {
                        if (port_to_port != Number.MIN_SAFE_INTEGER) {
                            var updateQuery = 'cartesian scope: ([Version].[Version Name].[CWV_MP] * [Location].[Location].[' + curr.Loc.Value + '] * [Trans Mode].[Trans Mode].[' + curr.BODTransport.Value + '] * [Sub Location].[Sub Location].[' + curr.SubLoc.Value + '] * [Time].[Week].[' + timeArr[i] + '] * [Item Material].[MSL3].[' + curr.Item.Value + ']); Measure.[BOD List Mtrl W_Port To Port]=' + port_to_port + '; end scope;';
                            queryModule.update(updateQuery);
                        }
                    }
                    else {
                        port_to_port = v3;
                    }
                }
            }
        } catch (e) {
            RuleOutputToUI = { Status: 'Error', Message: "Js Logic Error : " + e.message };
            return;
        }
    };

    return {
        Ditto: Ditto
    };
});