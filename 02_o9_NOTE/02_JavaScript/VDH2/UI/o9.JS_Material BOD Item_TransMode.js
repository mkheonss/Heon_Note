define('o9.JS_Material BOD Item_TransMode', ['o9/data/query', 'o9/data/cellset', 'o9.ap.webservice.cliet'], function () {
    //gets all dimensions defined
    var TransMode = function () {
        Log.Info('----------------------Start  queryForCoverage -----------------------');
        var queryModule = require('o9/data/query');
        var cellsetModule = require('o9/data/cellset');

        var Tempvsl = `select ([Trans Mode].[Trans Mode].filter(#. Name startswith([VSL])));`;
        var dataCellSet1 = cellsetModule.createCellSet(queryModule.select(Tempvsl));
        //var vsl = dataCellSet1[0];

        Log.Info('rows dataCellSet1...' + JSON.stringify(dataCellSet1));
        //Log.Info('rows vsl...' + JSON.stringify(vsl));
        //JSON.stringify(dataCellSet)

        var transMode = `select ([Trans Mode].[Trans Mode]);`;
        var dataCell = cellsetModule.createCellSet(queryModule.select(transMode));
        Log.Info('rows dataCell...' + JSON.stringify(dataCell));
        let Mode = [];
        let covVal = dataCellSet1.row(0).cell(dataCellSet1.memberColumnIndex('Trans Mode', 'Trans Mode')).Name;
        Log.Info('rows covVal...' + JSON.stringify(covVal));
        Mode.push({ Name: covVal, DisplayName: covVal });
        //Mode[0] = {Name : covVal,DisplayName:covVal};

        Log.Info('rows Mode...' + JSON.stringify(Mode));
        //Mode.push(dataCellSet1[0]);
        for (i = 0; i < dataCell.rowCount; i++) {
            
            covVal = dataCell.row(i).cell(dataCell.memberColumnIndex('Trans Mode', 'Trans Mode')).Name;
            //Log.Info('rows covVal returned...' + JSON.stringify(covVal));
            if(covVal != "VSL"){
                Mode.push({ Name: covVal, DisplayName: covVal });
                //Mode.push({Name : covVal,DisplayName:covVal});
                //Mode[i+1] = {Name : covVal,DisplayName:covVal};
            }
        }
    
        //Log.Info('rows Mode...' + JSON.stringify(Mode));
        return Mode;

    };
    return { 
        TransMode: TransMode
    };
});