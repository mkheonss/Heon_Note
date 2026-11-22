define('o9.JS_KdSopCopy', ['o9/data/query', 'o9/data/cellset', 'o9.NSCM.commonLib'], function () {

    const programName = "o9.JS_KdSopCopy ============>";
    const commonLib = require('o9.NSCM.commonLib');
    const queryModule = require('o9/data/query');
    const cellsetModule = require('o9/data/cellset');
    vdCommon = new commonLib.VdCommon(programName);

    //fn_fromSite is used to Get the Location Data from the query "checkQuery"and show the result and display the DisplayName
    var fn_fromSite = function(o9Params){
        vdUtil = new commonLib.VdUtil();

        vdCommon.setLogLevel("Debug");

        vdCommon.printParams(o9Params);
        let parsedParams = JSON.parse(o9Params);     
        let comboList = [];
        let validHashMap = [];

        let checkQuery = 'Select ([Version].[Version Name].[CWV_MP]* [Location].[Location]) on row,({Measure.[BOD Item_Asn]}) on column;';
        
        var checkQueryResult = cellsetModule.createCellSet(queryModule.select(checkQuery));
        var checkQueryResultRow = checkQueryResult.rowCount;
        // vdCommon.debug("Rows : "+checkQueryResultRow);
        for(let i = 0;i<checkQueryResultRow;i++)
        {
            var checkLocationName = checkQueryResult.row(i).cell(checkQueryResult.memberColumnIndex("Location","Location")).Name;
            var checkLocationDName = checkQueryResult.row(i).cell(checkQueryResult.memberColumnIndex("Location","Location")).DisplayName;
            if(!validHashMap.includes(checkLocationName))
            {
                comboList.push({Name : checkLocationName,DisplayName :checkLocationDName });
                validHashMap.push(checkLocationName);
            }
        }
        return comboList;
    };
    
    //fn_toSite is used to Get the Sub-Location Data from the query "checkQuery"and show the result and display the DisplayName
    var fn_toSite = function(o9Params){
        vdUtil = new commonLib.VdUtil();

        vdCommon.setLogLevel("Debug");

        vdCommon.printParams(o9Params);
        let parsedParams = JSON.parse(o9Params);
        
        let comboList = [];
        let validHashMap = [];

        let checkQuery = 'Select ([Version].[Version Name].[CWV_MP]*[Sub Location].[Sub Location]) on row,({Measure.[BOD Item_Asn]}) on column;';
        var checkQueryResult = cellsetModule.createCellSet(queryModule.select(checkQuery));
        var checkQueryResultRow = checkQueryResult.rowCount;
        // vdCommon.debug("Rows : "+checkQueryResultRow);
        for(let i=0;i<checkQueryResultRow;i++)
        {
            var checkSubLocationName = checkQueryResult.row(i).cell(checkQueryResult.memberColumnIndex("Sub Location","Sub Location")).Name;
            var checkSubLocationDName = checkQueryResult.row(i).cell(checkQueryResult.memberColumnIndex("Sub Location","Sub Location")).DisplayName;
            if(!validHashMap.includes(checkSubLocationName))
            {
                comboList.push({Name : checkSubLocationName,DisplayName :checkSubLocationDName });
                validHashMap.push(checkSubLocationName);
            }
        }
        return comboList;
    };

    //fn_Add is used to Get the all the elements fom Action Button and insert the row and when there is null value in Action Button, there should be blank in the final Insertion of row.
    var fn_Add = function(o9Params){

        vdUtil = new commonLib.VdUtil();

        vdCommon.setLogLevel("Debug");

        vdCommon.printParams(o9Params);
        let parsedParams = JSON.parse(o9Params);

        var fromSite = parsedParams.FromSite;
        var toSite = parsedParams.ToSite;
        var ass_item = parsedParams.ASIS_ITEM;
        var toBeItem = parsedParams.TOBE_ITEM;
        var isValid = parsedParams.isValid;
        var description = parsedParams.Description;
        var ndescription = `"${description}"`;
        // const item = [...ass_item];

        vdCommon.debug("From Site : "+fromSite);
        vdCommon.debug("To Site : "+toSite);
        vdCommon.debug("ASS_ITEM : "+ass_item);
        vdCommon.debug("ToBE_ITEM : "+toBeItem);
        vdCommon.debug("Valid : "+isValid);
        vdCommon.debug("Description : "+description);
        if(isValid==0)
        {
            isValid=null;
        }
        if(parsedParams.Description==null)
        {
            ndescription=null;
        }
        let checkQuery = 'Select ([Version].[Version Name].[CWV_MP] * [Item].[Item].['+ass_item+'] * [Location].[Location].['+fromSite+'] * [To Item].[To Item].['+toBeItem+'] * [Sub Location].[Sub Location].['+toSite+'] ) on row,({Measure.[KD SOP Copy_Created By], Measure.[KD SOP Copy_Creation Time], Measure.[KD SOP Copy_Desc], Measure.[KD SOP Copy_Update Time], Measure.[KD SOP Copy_Updated By], Measure.[KD SOP Copy_Valid]}) on column;';
        var checkQueryResult = cellsetModule.createCellSet(queryModule.select(checkQuery));
        var checkQueryResultRow = checkQueryResult.rowCount;
        vdCommon.debug("Rows : "+checkQueryResultRow);
        if(checkQueryResultRow>0)
        {
            let updateQuery = 'cartesian scope :([Version].[Version Name].[CWV_MP] * [Item].[Item].['+ass_item+'] * [Location].[Location].['+fromSite+'] * [To Item].[To Item].['+toBeItem+'] * [Sub Location].[Sub Location].['+toSite+']);Measure.[KD SOP Copy_Update Time] = now();Measure.[KD SOP Copy_Updated By] = CurrentUser().Name;Measure.[KD SOP Copy_Desc] = '+ndescription+';Measure.[KD SOP Copy_Valid] = '+isValid+';end scope;';
            vdCommon.debug(updateQuery);
            queryModule.update(updateQuery);
        }
        if(checkQueryResultRow===0)
        {
            let createQuery = 'cartesian scope :([Version].[Version Name].[CWV_MP] * [Item].[Item].['+ass_item+'] * [Location].[Location].['+fromSite+'] * [To Item].[To Item].['+toBeItem+'] * [Sub Location].[Sub Location].['+toSite+']);Measure.[KD SOP Copy_Created By] = CurrentUser().Name;Measure.[KD SOP Copy_Creation Time] = now();Measure.[KD SOP Copy_Desc]='+ndescription+'; Measure.[KD SOP Copy_Valid]='+isValid+';end scope;';
            vdCommon.debug(createQuery);
            queryModule.update(createQuery);
        }   
    };


   //fn_delete is used to delete the selected Row.
    var fn_delete = function(o9Params){

        vdUtil = new commonLib.VdUtil();

        vdCommon.setLogLevel("Debug");

        vdCommon.printParams(o9Params);
        let parsedParams = JSON.parse(o9Params);

        var fromSite = parsedParams.FromSite;
        var toSite = parsedParams.ToSite;
        var ass_item = parsedParams.ASIS_ITEM;
        var toBeItem = parsedParams.TOBE_ITEM;
        var isValid = parsedParams.isValid;
        var description = parsedParams.Description;
        var ndescription = `"${description}"`;
        // const item = [...ass_item];

        var arrayfromSite = [...fromSite];
        var arraytoSite = [...toSite];
        var arrayass_item = [...ass_item];
        var arraytoBeItem = [...toBeItem];

        // const testfromSite = Object.values(fromSite);

        var finalfromSite = `{${arrayfromSite.join(',')}}`;
        var finaltoSite = `{${arraytoSite.join(',')}}`;
        var finalass_item = `{${arrayass_item.join(',')}}`;
        var finaltoBeItem = `{${arraytoBeItem.join(',')}}`;

        var ffromSite = finalfromSite.replace(/(\w+(-\w+)*(_\w+)*\/?\w*)/g,'"$1"');
        var ftoSite = finaltoSite.replace(/(\w+(-\w+)*(_\w+)*\/?\w*)/g,'"$1"');
        var fass_item = finalass_item.replace(/(\w+(-\w+)*(_\w+)*\/?\w*)/g,'"$1"');
        var ftoBeItem = finaltoBeItem.replace(/(\w+(-\w+)*(_\w+)*\/?\w*)/g,'"$1"');

        let finalquery = 'Select ([Version].[Version Name].[CWV_MP] * [Item].[Item].filter(#.Name in '+fass_item+') * [Location].[Location].filter(#.Name in '+ffromSite+') * [To Item].[To Item].filter(#.Name in '+ftoBeItem+') * [Sub Location].[Sub Location].filter(#.Name in '+ftoSite+') ) on row, ({Measure.[KD SOP Copy_Created By], Measure.[KD SOP Copy_Creation Time], Measure.[KD SOP Copy_Desc], Measure.[KD SOP Copy_Update Time], Measure.[KD SOP Copy_Updated By], Measure.[KD SOP Copy_Valid]}) on column;';
        vdCommon.debug("Final Query : "+finalquery);
        var checkfinalResult = cellsetModule.createCellSet(queryModule.select(finalquery));
        var checkfinalResultRow = checkfinalResult.rowCount;
        vdCommon.debug("Row of Final GOT :: "+checkfinalResultRow);

        for(let i=0;i<checkfinalResultRow;i++)
        {
            var checkItem = checkfinalResult.row(i).cell(checkfinalResult.memberColumnIndex("Item","Item")).Name;
            var checkLocatoin = checkfinalResult.row(i).cell(checkfinalResult.memberColumnIndex("Location","Location")).Name;
            var checktoItem = checkfinalResult.row(i).cell(checkfinalResult.memberColumnIndex("To Item","To Item")).Name;
            var checksubLocation = checkfinalResult.row(i).cell(checkfinalResult.memberColumnIndex("Sub Location","Sub Location")).Name;

            let deletequery = 'delete data for model [KD SOP Copy] where {[Version].[Version Name].[CWV_MP],[Item].[Item].['+checkItem+'],[Location].[Location].['+checkLocatoin+'],[To Item].[To Item].['+checktoItem+'],[Sub Location].[Sub Location].['+checksubLocation+']};';
            vdCommon.debug("Delete Query :::: "+deletequery);
            queryModule.update(deletequery);
            //vdCommon.debug(checkItem);
        }
    };

    return {
        fn_fromSite : fn_fromSite,
        fn_toSite : fn_toSite,
        fn_Add : fn_Add,
        fn_delete : fn_delete
    };
});