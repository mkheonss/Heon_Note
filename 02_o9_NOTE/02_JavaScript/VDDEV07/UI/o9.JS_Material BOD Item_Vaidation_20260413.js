define('o9.JS_Material BOD Item_Vaidation', ['o9/data/query', 'o9/data/cellset', 'o9.ap.webservice.cliet'], function () {
    //gets all dimensions defined
    var ValidateItemDate = function (o9Params) {
        Log.Info('----------------------Start  queryForCoverage -----------------------');

        // var queryModule = require('o9/data/query');
        // var cellsetModule = require('o9/data/cellset');

        var parsedParams = JSON.parse(o9Params);
        Log.Info('O9 parsedParams   ---' + JSON.stringify(parsedParams));
        Log.Info('----------------------Start  queryForCoverage -----------------------'+parsedParams.EffectiveStartDate);

        Log.Info('O9 data ----------*********************--------------'+parsedParams.EffectiveEndDate);
        
        // queryModule.update(data);
        
        //Log.Info(' ------------------------------------ERROR--------------------------------------  ' + typeof(data.rowCount));
        // Log.Info(' er00000  ' + err);
        if (parsedParams.EffectiveStartDate > parsedParams.EffectiveEndDate) {
            RuleOutputToUI = {
                Status: 'Error',
                Message: 'EffectiveEndDate is less then EffectiveStartDate'
            };
            return;
        }

    };
    return { 
        ValidateItemDate: ValidateItemDate
    };
});