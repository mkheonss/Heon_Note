define('o9.JS_Material_BOD_Semi', ['o9/data/query', 'o9/data/cellset', 'o9.ap.webservice.cliet'], function () {
    //gets all dimensions defined
    var SemiconTMode = function (o9Params) {
        Log.Info('----------------------Start  queryForCoverage -----------------------');
    
        var queryModule = require('o9/data/query');
        var cellsetModule = require('o9/data/cellset');
    
        var parsedParams = JSON.parse(o9Params);
        Log.Info('O9 parsedParams   ---' + JSON.stringify(parsedParams));
        Log.Info('----------------------Start  queryForCoverage -----------------------');
        
        //Storing fieldbinding variable of MSL1
        var Qquery = parsedParams.SCMLevel1;

        var Q3query = parsedParams.SCMLevel3;

        var QPquery = parsedParams.Plant;

        var QVquery = parsedParams.Vendor;

        Log.Info('CheckingFB -- '+Q3query+'---'+QPquery+'---'+QVquery);

        
        //This array will store Trans Mode Data
        var arrysemi=[];
        if(Qquery=="Semicon.")
        {
            let UIDataQuery = 'Select ([Version].[Version Name].[CWV_MP] * [Location].[Location].['+parsedParams.Vendor+'] * [Item Material].[MSL3].['+parsedParams.SCMLevel3+'] * [Sub Location].[Sub Location].['+parsedParams.Plant+'] * [Trans Mode].[Trans Mode]* {Measure.[BOD List Mtrl W_Factory Out],Measure.[BOD List Mtrl_EFF Startdate]});';
            var UIDataQueryResult = cellsetModule.createCellSet(queryModule.select(UIDataQuery));
            var UIDataQueryCT = UIDataQueryResult.rowCount;
            if(UIDataQueryCT==0)
            {
            let checkQuery = 'select([Item Material].[MSL1].[Semicon.]*[Trans Mode].[Trans Mode].[AIR] );';
            var checkQueryResult = cellsetModule.createCellSet(queryModule.select(checkQuery));
            var checkTM = checkQueryResult.row(0).cell(checkQueryResult.memberColumnIndex("Trans Mode","Trans Mode")).Name;
            arrysemi.push({Name : checkTM,DisplayName : checkTM});
            Log.Info('Checking if data storing in array  ---' + JSON.stringify(arrysemi));
            }
            else
            {
                return;
            }

        }
        else{
            let checkQuery = 'select (&NSUITransModeMtrlView);';
            var checkQueryResult = cellsetModule.createCellSet(queryModule.select(checkQuery));
            var checkQueryResultRow = checkQueryResult.rowCount;

            let UIDataQuery = 'Select ([Version].[Version Name].[CWV_MP] * [Location].[Location].['+parsedParams.Vendor+']* [Item Material].[MSL3].['+parsedParams.SCMLevel3+'] * [Sub Location].[Sub Location].['+parsedParams.Plant+'] * [Trans Mode].[Trans Mode]* {Measure.[BOD List Mtrl W_Factory Out],Measure.[BOD List Mtrl_EFF Startdate]});';
            var UIDataQueryResult = cellsetModule.createCellSet(queryModule.select(UIDataQuery));
            var UIDataQueryCT = UIDataQueryResult.rowCount;

            var arrysemi = [];
            Log.Info('Array T Before Insertion : ---' + arrysemi);
        for (let i = 0; i < checkQueryResultRow; i++) {
            var checkTMOriginal = checkQueryResult.row(i).cell(checkQueryResult.memberColumnIndex("Trans Mode","Trans Mode")).Name;
            var existsInTemp = false;
            for (let j = 0; j < UIDataQueryCT; j++) {
                var checkTMTemp = UIDataQueryResult.row(j).cell(UIDataQueryResult.memberColumnIndex("Trans Mode","Trans Mode")).Name;
                if (checkTMOriginal === checkTMTemp) {
                    existsInTemp = true;
                    break;
                }
            }
            if (!existsInTemp) {
                arrysemi.push({Name : checkTMOriginal,DisplayName : checkTMOriginal});
            }
        }

        }
        // Return the arrysemi array as is contain Trans Mode Data
        return arrysemi;
    };
        
    return {
        SemiconTMode: SemiconTMode
    };
});