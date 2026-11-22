define('o9.NSCM.PTPMaster', ['o9/data/query', 'o9/data/cellset', 'o9.NSCM.commonLib'], function () {
    const programName = "o9.NSCM.JSGroupDefine ============>";
    const commonLib = require('o9.NSCM.commonLib');
    const queryModule = require('o9/data/query');
    const cellsetModule = require('o9/data/cellset');
    nscmCommon = new commonLib.NSCMCommon(programName); 
    
    var CopyBtn = function (o9Params) {
        nscmUtil = new commonLib.NSCMUtil();

        nscmCommon.setLogLevel("Debug");
        nscmCommon.printParams(o9Params);
        let parsedParams = JSON.parse(o9Params);
        var ItemCheck = parsedParams.fbItem;
        var ShipToCheck = parsedParams.fbShipTo;
        var VersinName = parsedParams.fbVersion;
        
        const queryModule = require('o9/data/query');
        const cellsetModule = require('o9/data/cellset');

        const queryForUIData = 'Select ([Version].[Version Name].['+VersinName+'] * [Item].[Item].['+ItemCheck+'] * [Sales Domain].[Ship To].['+ShipToCheck+']  ) on row, ({Measure.[PTP Master_Created by], Measure.[PTP Master_Creation time], Measure.[PTP Master_Delete Flag], Measure.[PTP Master_Old Item], Measure.[PTP Master_Old Item_Prev], Measure.[PTP Master_RTS Date], Measure.[PTP Master_RTS Date_Prev], Measure.[PTP Master_Status], Measure.[PTP Master_Status_Prev], Measure.[PTP Master_Update time], Measure.[PTP Master_Updated by], Measure.[PTP Master_Valid Flag], Measure.[PTP Master_Valid Flag_Prev]}) on column;';

        const uiData = cellsetModule.createCellSet(queryModule.select(queryForUIData));
        
        
            if(uiData.rowCount>0)
            {
                
                RuleOutputToUI = {Status: 'Error',Message: 'Duplicate Data found'};
                return;      
            }

                
            }
    return {
           CopyBtn: CopyBtn
        };
    
});