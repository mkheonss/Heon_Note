define('o9.JS_Material BOD Item_Vendor', ['o9/data/query', 'o9/data/cellset', 'o9.ap.webservice.cliet'], function () {
    //gets all dimensions defined
    var VendorLocation = function (props) {
        Log.Info('----------------------Start  queryForVendor -----------------------');
        var queryModule = require('o9/data/query');
        var cellsetModule = require('o9/data/cellset');

        // Parameta fetch
        var parsedParams = JSON.parse(props);

        // IBPL Vendor Master Map Query which is "Y"
        var Vendor =`(Select([Item Material].[MSL3].[`+ parsedParams.SCMLevel3 +`] * [Item Material].[MSL1].[`+ parsedParams.SCMLevel1 +`] * [Global Top].[GT Code].filter(#.Name Startswith"G") * [Location].[Location].filter(#.Name in {"`+ parsedParams.Plant +`"})) on row, ( {Measure.[Vendor Mtrl_GT Name], Measure.[Vendor Mtrl Map_Master Flag]} ) on column where {&CWVUI} ).filter( Measure.[Vendor Mtrl Map_Master Flag] != [N]  && ~isnull(Measure.[Vendor Mtrl_GT Name]) );`;
        var dataCellSet1 = cellsetModule.createCellSet(queryModule.select(Vendor));
        // Log.Info('Intial Query ===== ' + Vendor);
        // Log.Info('Intial Query ===== ' + JSON.stringify(Vendor));
        // Log.Info('Intial Record ===== ' + JSON.stringify(dataCellSet1));

        var Location = [];
        var NameVal;
        var DisplayNameVal
        for (i = 0; i < dataCellSet1.rowCount; i++) {

            let CodeVal = dataCellSet1.row(i).cell(dataCellSet1.memberColumnIndex('Global Top', 'GT Code')).Name;

            // IBPL Query
            let Local = `Select ([Location].[Location].[`+ CodeVal +`]);`;
            let Localdata = cellsetModule.createCellSet(queryModule.select(Local));
            
            //if Data Present
            if(Localdata.rowCount > 0){
                NameVal = Localdata.row(0).cell(Localdata.memberColumnIndex('Location', 'Location')).Name;
                let VendorMeasureData = dataCellSet1.row(i).cell(dataCellSet1.measureColumnIndex('Vendor Mtrl_GT Name'));
                //DisplayNameVal = Localdata.row(0).cell(Localdata.memberColumnIndex('Location', 'Location')).DisplayName;

                // Add Data in the Location Variable
                Location.push({ Name: NameVal, DisplayName: VendorMeasureData });
            }
        }


        
        // Add Data in the Location P105SP
        Location.push({ Name: 'P105SP', DisplayName: "BUSAN(HUB)" });
        


        // Log.Info('Final Record ===== ' + JSON.stringify(Location));
        Log.Info('----------------------End  queryForVendor -----------------------');
        return Location;

    };
    return { 
        VendorLocation: VendorLocation
    };
});