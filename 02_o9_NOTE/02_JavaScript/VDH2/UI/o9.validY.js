define('o9.validY', ['o9/data/query', 'o9/data/cellset', 'o9.ap.webservice.cliet'], function () {
    //gets all dimensions defined
    var ValidY = function (props) {

        var queryModule = require('o9/data/query');
        var cellsetModule = require('o9/data/cellset');


        Log.Info('----------------------Start  queryForCoverage -----------------------');

        var parsedParams = JSON.parse(props);

        for (var i = 0; i < parsedParams.tuple.length; i++) {
            var curr = parsedParams.tuple[i];

            if (curr.BOMStatus.Value == "NSCM Assy" || curr.BOMStatus.Value == "Dash KD") {
                var state = 'scope: ([Version].[Version Name].[CWV_MP] * [Location].[Location].[' + curr.Location.Value + '] * [Item].[Item].[' + curr.Item.Value + '] * [BOM Info].[BOM Version].[' + curr.BOMInfo.Value + '] * [Status].[Status].[' + curr.Status.Value + '] * [BOM Type].[BOM Type].[' + curr.BOMType.Value + '] * [To Item].[To Item].[' + curr.ToItem.Value + '] * [To Location].[To Location].[' + curr.ToLocation.Value + '] * [Item Material].[Item Material].[' + curr.ItemMaterial.Value + '] * [BOM Status].[BOM Status].[' + curr.BOMStatus.Value + ']); Measure.[Full BOM_Valid]= Y; Measure.[Full BOM_Update Time]=now(); end scope;';

                queryModule.update(state);
            }
            else {
                RuleOutputToUI = {
                    Status: 'Error',
                    Message: 'This feature only works for some specific BOM Status values. Those are NSCM Assy, Dash KD.'
                };
            }
        }

    };

    var ValidN = function (props) {

        var queryModule = require('o9/data/query');
        var cellsetModule = require('o9/data/cellset');


        Log.Info('----------------------Start  queryForCoverage -----------------------');

        var parsedParams = JSON.parse(props);

        for (var i = 0; i < parsedParams.tuple.length; i++) {
            var curr = parsedParams.tuple[i];

            if (curr.BOMStatus.Value == "NSCM Assy" || curr.BOMStatus.Value == "Dash KD") {
                Log.Info('----------------------Upadte Valid measure to N -----------------------');

                var state = 'scope: ([Version].[Version Name].[CWV_MP] * [Location].[Location].[' + curr.Location.Value + '] * [Item].[Item].[' + curr.Item.Value + '] * [BOM Info].[BOM Version].[' + curr.BOMInfo.Value + '] * [Status].[Status].[' + curr.Status.Value + '] * [BOM Type].[BOM Type].[' + curr.BOMType.Value + '] * [To Item].[To Item].[' + curr.ToItem.Value + '] * [To Location].[To Location].[' + curr.ToLocation.Value + '] * [Item Material].[Item Material].[' + curr.ItemMaterial.Value + '] * [BOM Status].[BOM Status].[' + curr.BOMStatus.Value + ']); Measure.[Full BOM_Valid]= N; Measure.[Full BOM_Update Time]=now(); end scope;';

                queryModule.update(state);
            }
            else {
                RuleOutputToUI = {
                    Status: 'Error',
                    Message: 'This feature only works for some specific BOM Status values. Those are NSCM Assy, Dash KD.'
                };
            }
        }

    };

    var Validation = function (props) {

        var queryModule = require('o9/data/query');
        var cellsetModule = require('o9/data/cellset');
        var parsedParams = JSON.parse(props);


        Log.Info('----------------------Start  queryForCoverage -----------------------');

        Log.Info('------------------------------------------parsedParams.Plant' + parsedParams.Plant);

        var queryForAll = 'Select ([Version].[Version Name].[CWV_MP] * [Location].[Location].[' + parsedParams.Plant + '] * [Item].[Item].[' + parsedParams.SETItem + '] * [BOM Info].[BOM Version].[' + parsedParams.BOMVersion + '] * [Status].[Status].[' + parsedParams.Status + '] * [BOM Type].[BOM Type].[' + parsedParams.BOMType + '] * [To Item].[To Item].[' + parsedParams.LCMKDCode + '] * [To Location].[To Location].[' + parsedParams.Plant01 + '] * [Item Material].[Item Material].[' + parsedParams.OCCode + '] * [BOM Status].[BOM Status].[' + parsedParams.BOMStatus + '] * {Measure.[Full BOM_Valid]});';

        var data = cellsetModule.createCellSet(queryModule.select(queryForAll));

        Log.Info('---------------------' + JSON.stringify(data));

        if (data.rowCount == 0) {
            let state = 'Cartesian scope: ([Version].[Version Name].[CWV_MP] * [Location].[Location].[' + parsedParams.Plant + '] * [Item].[Item].[' + parsedParams.SETItem + '] * [BOM Info].[BOM Version].[' + parsedParams.BOMVersion + '] * [Status].[Status].[' + parsedParams.Status + '] * [BOM Type].[BOM Type].[' + parsedParams.BOMType + '] * [To Item].[To Item].[' + parsedParams.LCMKDCode + '] * [To Location].[To Location].[' + parsedParams.Plant01 + '] * [Item Material].[Item Material].[' + parsedParams.OCCode + '] * [BOM Status].[BOM Status].[' + parsedParams.BOMStatus + ']); Measure.[Full BOM_Valid] = "Y"; Measure.[Full BOM_SRA Date] = now(); Measure.[Full BOM_EOP Date] = now() ;Measure.[Full BOM_Creation Time] = now(); Measure.[Full BOM_Update Time]=now(); end scope;';

            queryModule.update(state);
        }
        else{
            RuleOutputToUI = {
                Status: 'Error',
                Message: 'Already a row exist with this ombination of values.'
            };
        }




        Log.Info('-------------------------------' + props);



        Log.Info('---------------------------------' + parsedParams);

        Log.Info('---------------------' + JSON.stringify(parsedParams));



    };

    return {
        ValidY: ValidY,
        ValidN: ValidN,
        Validation: Validation
    };
});