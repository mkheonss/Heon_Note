define('o9.NSCM.JSTacttimeModelItemSiteMFASN_Asn', ['o9/data/query', 'o9/data/cellset', 'o9.NSCM.commonLib'], function () {



    const programName = "o9.NSCM.JSCurrentUser ============>";
    const commonLib = require('o9.NSCM.commonLib');
    const queryModule = require('o9/data/query');
    const cellsetModule = require('o9/data/cellset');
    nscmCommon = new commonLib.NSCMCommon(programName);


    var fn_ItemSiteMFASN_Asn = function (o9Params) {
        try {
            nscmUtil = new commonLib.NSCMUtil();
            nscmCommon.setLogLevel("Debug");
            nscmCommon.printParams(o9Params);
            let parsedParams = JSON.parse(o9Params);

            Log.Info("props" + JSON.stringify(parsedParams));

            

            const queryForItemSiteMFASN_Asn = `select(&CWV*[Sub Location]. [Sub Location].[${parsedParams.fbFrom_Site}]*[Item].[Item]) on row,({Measure.[Item Site MF ASN_Asn]}) on column where {Measure.[Item Site MF ASN_Asn]==1};`;
            Log.Info('---------queryForItemSiteMFASN_Asn------------' + JSON.stringify(queryForItemSiteMFASN_Asn));

            const ItemSiteMFASN_AsnData = cellsetModule.createCellSet(queryModule.select(queryForItemSiteMFASN_Asn));

            Log.Info('---------ItemSiteMFASN_AsnData------------' + JSON.stringify(ItemSiteMFASN_AsnData));

        //return salesStageData;

         var comboList = [];


        for(let j=0; j< ItemSiteMFASN_AsnData.rowCount; j++)
         {
                let Item= ItemSiteMFASN_AsnData.row(j).cell(ItemSiteMFASN_AsnData.memberColumnIndex('Item', 'Item')).Name;
                let subLocation= ItemSiteMFASN_AsnData.row(j).cell(ItemSiteMFASN_AsnData.memberColumnIndex('Sub Location', 'Sub Location')).Name;

                comboList.push({ Name: Item, DisplayName: Item });
        }

        Log.Info('---------comboList------------' + JSON.stringify(comboList));
       
        return comboList;


        } catch (e) {
            RuleOutputToUI = { Status: 'Error', Message: "Js Logic Error : " + e.message };
            return;
        }

    };

    return {
        fn_ItemSiteMFASN_Asn: fn_ItemSiteMFASN_Asn
    };

});