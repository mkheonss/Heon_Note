define('o9.NSCM.JSA/CMaster', ['o9/data/query', 'o9/data/cellset', 'o9.NSCM.commonLib'], function () {

    const validBtn = function (props) {
    try{

        const queryModule = require('o9/data/query');
        const cellsetModule = require('o9/data/cellset');

        props = JSON.parse(props);

        Log.Info("-------------props-----------------------" + props);

        var category = props.fb_Category;

        let list = [];

        list.push({ Name: 'Y', DisplayName: 'Y' });
        if(category=="분리 수주(실내외기 다른 공장)"){
            list.push({ Name: 'N', DisplayName: 'N' });
        }
        return list;
    }
    catch (e) {
        RuleOutputToUI = { Status: 'Error', Message: "Js Logic Error : " + e.message };
        return;
    }
    };

    return {    
        validBtn: validBtn
    };
});