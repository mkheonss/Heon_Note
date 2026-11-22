define('o9.JS_MaterialBOD_Apply', ['o9/data/query', 'o9/data/cellset', 'o9.ap.webservice.cliet'], function () {
    //gets all dimensions defined
    var Apply = function (o9Params) {
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

        //var GlobalTop = 'Select ([Version].[Version Name].[CWV_MP] * [Global Top].[GT Name Fix].['+ parsedParams.Vendor +'] * [Trans Mode].[Trans Mode].['+ parsedParams.Plant +'] * [Location].[Location].['+ parsedParams.Plant +'] * [Time].[Week] * [Item Material].[MSL1].['+ parsedParams.SCMLevel1 +'] * [Item Material].[MSL2].['+ parsedParams.SCMLevel2 +'] * [Item Material].[MSL3].['+ parsedParams.SCMLevel3 +'] * {Measure.[Mtrl BOD W_Factory Out], Measure.[BOD List Mtrl W_GR LT], Measure.[BOD List Mtrl W_Portnsit LT], Measure.[BOD List Mtrl W_Port To Port], Measure.[BOD List Mtrl W_Supplier]});';
        
        // Log.Info('---------------------------------' + parsedParams);

        //     Log.Info('---------------------' + JSON.stringify(parsedParams));

        //     Log.Info('---------------------' + JSON.stringify(parsedParams.Plant));

        //     Log.Info('---------------------' + JSON.stringify(parsedParams.Vendor));

        var plant = "";

        for (let i = 0; i < parsedParams.Plant.length; i++) {
            plant = plant + '[' + parsedParams.Plant[i] + ']';
            if (i < parsedParams.Plant.length - 1)
            plant = plant + ',';
        }

        // Log.Info(plant)

        var vendor = "";

        for (let i = 0; i < parsedParams.Vendor.length; i++) {
            vendor = vendor + '[' + parsedParams.Vendor[i] + ']';
            if (i < parsedParams.Vendor.length - 1)
            vendor = vendor + ',';
        }

        // Log.Info(vendor)

        var scmLevel3 = "";

        for (let i = 0; i < parsedParams.SCMLevel3.length; i++) {
            scmLevel3 = scmLevel3 + '[' + parsedParams.SCMLevel3[i] + ']';
            if (i < parsedParams.SCMLevel3.length - 1)
            scmLevel3 = scmLevel3 + ',';
        }

        Log.Info(scmLevel3)

        var GlobalTop = 'Select ([Version].[Version Name].[CWV_MP] * [Location].[Location].Filter(#. Name in {' + vendor + '}) * [Trans Mode].[Trans Mode] * [Sub Location].[Sub Location].Filter(#. Name in {' + plant + '}) * &MPHorizon * [Item Material].[MSL1] * [Item Material].[MSL2] * [Item Material].[MSL3].Filter(#. Name in {' + scmLevel3 + '}) * {Measure.[BOD List Mtrl W_Factory Out], Measure.[BOD List Mtrl W_GR LT], Measure.[BOD List Mtrl W_Port To Port], Measure.[BOD List Mtrl W_Supplier]});';
        var data = cellsetModule.createCellSet(queryModule.select(GlobalTop));
        // Log.Info('O9 data ----------*********************--------------' + JSON.stringify(data));
        // Log.Info('O9 data ---' + JSON.stringify(data.rowCount));

        

            // Log.Info('---------------------------------' + parsedParams);

            // Log.Info('---------------------' + JSON.stringify(parsedParams));

            // Log.Info('---------------------' + JSON.stringify(parsedParams.Plant));

            // Log.Info('---------------------' + JSON.stringify(parsedParams.Vendor));
        // queryModule.update(data);
        var GT = [];
        var VD = [];
        var MS = [];
        var Time = [];

        var Fact = [];
        var GR = [];
        var Port = [];
        var Sup = [];
        var transModeData = [];
        for (i = 0; i < data.rowCount; i++) {
            Log.Info('rows returned...' + data.rowCount);
            GT.push(data.row(i).cell(data.memberColumnIndex('Location', 'Location')).Name);
            VD.push(data.row(i).cell(data.memberColumnIndex('Sub Location', 'Sub Location')).Name);
            MS.push(data.row(i).cell(data.memberColumnIndex('Item Material', 'MSL3')).Name);
            Time.push(data.row(i).cell(data.memberColumnIndex('Time', 'Week')).Name);

            transModeData.push(data.row(i).cell(data.memberColumnIndex('Trans Mode', 'Trans Mode')).Name);

            Fact.push(data.row(i).cell(data.measureColumnIndex('BOD List Mtrl W_Factory Out')));
            GR.push(data.row(i).cell(data.measureColumnIndex('BOD List Mtrl W_GR LT')));
            Port.push(data.row(i).cell(data.measureColumnIndex('BOD List Mtrl W_Port To Port')));
            Sup.push(data.row(i).cell(data.measureColumnIndex('BOD List Mtrl W_Supplier')));
        }

        for (i = 0; i < GT.length; i++) {
            var Buttom = 'Select ([Version].[Version Name].[CWV_MP] * [Location].[Location].[' + GT[i] + '] * [Trans Mode].[Trans Mode].[' + transModeData[i] + '] * [Sub Location].[Sub Location].[' + VD[i] + '] * [Time].[Week].[' + Time[i] + '] * [Item Material].[Item Material] * [Item Material].[MSL1] * [Item Material].[MSL2] * [Item Material].[MSL3].[' + MS[i] + '] * [Item Material].[MSL4] * [Item Material].[MSL5] * {Measure.[BOD Item Mtrl W_Factory Out], Measure.[BOD Item Mtrl W_GR LT], Measure.[BOD Item Mtrl W_Port To Port], Measure.[BOD Item Mtrl W_Supplier], Measure.[BOD Item Mtrl_Lock Flag], Measure.[BOD Item Mtrl_Lot Type]});';
            var dataCell = cellsetModule.createCellSet(queryModule.select(Buttom));
            Log.Info('O9 data --- Buttom  ' + JSON.stringify(dataCell.rowCount));
            for (k = 0; k < dataCell.rowCount; k++) {
                
                let lot = dataCell.row(k).cell(dataCell.measureColumnIndex('BOD Item Mtrl_Lot Type'));
                let covVal = dataCell.row(k).cell(dataCell.measureColumnIndex('BOD Item Mtrl_Lock Flag'));
                let meas = dataCell.row(k).cell(dataCell.memberColumnIndex('Item Material', 'Item Material')).Name;
                //let tp = dataCell.row(k).cell(dataCell.memberColumnIndex('Trans Mode', 'Trans Mode')).Name;
                Log.Info('O9 data --- covVal Boooool Lockkkk' + JSON.stringify(covVal));
                Log.Info('O9 data --- covVal real: ' + covVal);
                Log.Info('O9 data --- Item Material: ' + meas);
                Log.Info('O9 data --- Transport: ' + transModeData[i]);
                if (covVal == "N" || covVal == null) {
                    // Log.Info('O9 data --- Fact' + JSON.stringify(Fact[i]));
                    // Log.Info('O9 data --- GR' + JSON.stringify(GR[i]));
                    // Log.Info('O9 data --- Port' + JSON.stringify(Port[i]));
                    // Log.Info('O9 data --- Sup' + JSON.stringify(Sup[i]));
                    // var Ex = 'scope : ([Version].[Version Name].[CWV_MP] * [Item Material].[MSL3].['+ MS[i] +'] * [Location].[Location].['+ VD[i] +'] * [Time].[Week].['+ Time[i] +']  * [Global Top].[GT Name Fix].['+ GT[i] +'] * [Trans Mode].[Trans Mode]); Measure.[Mtrl BOD Detail W_Factory Out] = Measure.[Mtrl BOD W_Factory Out]; Measure.[Mtrl BOD Detail W_GR LT] = Measure.[BOD List Mtrl W_GR LT]; Measure.[Mtrl BOD Detail W_Portnsit LT] = Measure.[BOD List Mtrl W_Portnsit LT]; Measure.[Mtrl BOD Detail W_Port To Port] = Measure.[BOD List Mtrl W_Port To Port]; Measure.[Mtrl BOD Detail W_Supplier] = Measure.[BOD List Mtrl W_Supplier];end scope;';
                    var Ex1 = 'scope : ([Version].[Version Name].[CWV_MP]* [Item Material].[Item Material].['+ meas +'] * [Item Material].[MSL1] * [Item Material].[MSL2] * [Item Material].[MSL3].[' + MS[i] + '] * [Item Material].[MSL4] * [Item Material].[MSL5] * [Sub Location].[Sub Location].[' + VD[i] + ']  * [Time].[Week].[' + Time[i] + '] * [Location].[Location].[' + GT[i] + '] * [Trans Mode].[Trans Mode].[' + transModeData[i] + ']); Measure.[BOD Item Mtrl W_Factory Out] = ' + Fact[i] + ';Measure.[BOD Item Mtrl W_GR LT]= ' + GR[i] + '; Measure.[BOD Item Mtrl W_Port To Port] = ' + Port[i] + '; Measure.[BOD Item Mtrl W_Supplier] = ' + Sup[i] + '; end scope;';
                    // Log.Info('Ex1 Ex1 .... ...' + Ex1);
                    queryModule.update(Ex1);
                }
            }
        }

    };
    return {
        Apply: Apply
    };
});