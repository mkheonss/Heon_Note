define('o9.NSCM.JSOEMPlant', ['o9/data/query', 'o9/data/cellset', 'o9.NSCM.commonLib'], function () {

    const duplicateCheck = function (props) {
    try{

        const queryModule = require('o9/data/query');
        const cellsetModule = require('o9/data/cellset');

        props = JSON.parse(props);

        Log.Info("-------------props-----------------------" + JSON.stringify(props));

        //const queryForUIData = `Select ([Version].[Version Name].[CurrentWorkingView] * [Item].[Item].[${props.fbItem}] * [Location].[Location].[${props.fbOrgSite}] * [Sub Location].[Sub Location].[${props.fbOEMSiteName}]) on row, ({Measure.[OEM Plant_CM Indicator], Measure.[OEM Plant_OEM Type], Measure.[OEM Plant_Valid Flag], Measure.[OEM Plant_Delete Flag]}) on column;`;
        const queryForUIData = `Select ([Version].[Version Name].[${props.fbVersion}] * [Item].[Item].[${props.fbItem}] * [Location].[Location].[${props.fbOrgSite}] * [Sub Location].[Sub Location].[${props.fbOEMSiteName}]) on row, ({Measure.[OEM Plant_CM Indicator], Measure.[OEM Plant_OEM Type], Measure.[OEM Plant_Valid Flag], Measure.[OEM Plant_Delete Flag]}) on column;`;
        const uiData = cellsetModule.createCellSet(queryModule.select(queryForUIData));

        Log.Info("-------------queryForUIData-----------------------" + queryForUIData);
        Log.Info("-------------uiData-----------------------" + JSON.stringify(uiData));

        if (uiData.rowCount > 0) {
            var deleteFlag = uiData.row(0).cell(uiData.measureColumnIndex('OEM Plant_Delete Flag'));
            Log.Info("-------------deleteFlag-----------------------" + deleteFlag);
            if(deleteFlag){
                return;
            }
            RuleOutputToUI = {
                Status: 'Error',
                Message: 'Data already present for these values.'
            };
            return;
        }
    }
    catch (e) {
        RuleOutputToUI = { Status: 'Error', Message: "Js Logic Error : " + e.message };
        return;
    }
    };

    var fnDelete = function (props) {
        Log.Info('----------------------Start fnDelete queryForCoverage -----------------------');

        var queryModule = require('o9/data/query');
        var cellsetModule = require('o9/data/cellset');


        //Log.Info('----------------------Start  queryForCoverage -----------------------');

        var parsedParams = JSON.parse(props);

        Log.Info('------------------------- Parsed Params ::'  + JSON.stringify(parsedParams));

        for (var i = 0; i < parsedParams.fbDelete.length; i++) {
            var curr = parsedParams.fbDelete[i];

            //let state = `cartesian scope: ([Version].[Version Name].[CurrentWorkingView] * [Item].[Item].[${curr.Item.Value}] * [Location].[Location].[${curr.OrgSite.Value}] * [Sub Location].[Sub Location].[${curr.OEMSiteName.Value}]); Measure.[OEM Plant_Delete Flag]=true; end scope;`;
            let state = `scope: ([Version].[Version Name].[${parsedParams.fbVersion}] * [Item].[Item].[${curr.Item.Value}] * [Location].[Location].[${curr.OrgSite.Value}] * [Sub Location].[Sub Location].[${curr.OEMSiteName.Value}]); Measure.[OEM Plant_Delete Flag]=true; end scope;`;
            Log.Info('-------------------------fnDelete state Query ::'  + state);
            queryModule.update(state);
        }

    };

    return {    
        duplicateCheck: duplicateCheck,
        fnDelete: fnDelete
    };
});