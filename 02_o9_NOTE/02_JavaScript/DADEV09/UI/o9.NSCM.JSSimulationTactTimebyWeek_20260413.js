define('o9.NSCM.JSSimulationTactTimebyWeek', ['o9/data/query', 'o9/data/cellset', 'o9.NSCM.commonLib'], function () {

    const simulation = function (props) {
    try{

        const queryModule = require('o9/data/query');
        const cellsetModule = require('o9/data/cellset');

        props = JSON.parse(props);

        Log.Info("-------------props-----------------------" + props);

        var error = false;
        var errorMsg = "";
        
        if (props.fb_Efficiency < 0.01 || props.fb_Efficiency>1.99) {
            error = true;
            errorMsg += 'Efficiency input should be in range 0.01 ~ 1.99';
        }

        if (props.fb_BaseTactTime<=0) {
            if (error)
                errorMsg += " & ";
            errorMsg += 'Base Tact Time should be greater than 0.';
            error=true;
        }

        if (error) {
            RuleOutputToUI = {
                Status: 'Error',
                Message: errorMsg
            };
            return;
        }
        
    }
    catch (e) {
        RuleOutputToUI = { Status: 'Error', Message: "Js Logic Error : " + e.message };
        return;
    }
    };

    return {    
        simulation: simulation
    };
});