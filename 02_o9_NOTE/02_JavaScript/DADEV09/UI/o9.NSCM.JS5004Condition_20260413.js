define('o9.NSCM.JS5004Condition', ['o9/data/query', 'o9/data/cellset', 'o9.NSCM.commonLib'], function () {

    const programName = "o9.NSCM.JS5004Condition ============>";
    const commonLib = require('o9.NSCM.commonLib');
    const queryModule = require('o9/data/query');
    const cellsetModule = require('o9/data/cellset');
    nscmCommon = new commonLib.NSCMCommon(programName); 


    var fn_Add= function(o9Params){
        nscmUtil = new commonLib.NSCMUtil();

        nscmCommon.setLogLevel("Debug");
        nscmCommon.printParams(o9Params);
        let parsedParams = JSON.parse(o9Params);
        
        //Sub Location
        var fbFromSiteID = parsedParams.fbFromSiteID;
        var fbFromSite = parsedParams.fbFromSite;
        //Location
        var fbToSite = parsedParams.fbToSite;
        //Site Price Type
        var fbSitePriceType = parsedParams.fbSitePriceType;
        var fbIntercompanyType = parsedParams.fbIntercompanyType;
        var fbKeyCombination = parsedParams.fbKeyCombination;
        var fbDescription = parsedParams.fbDescription;

        var fbViaSite = parsedParams.fbViaSite;
        var fbMeasure = parsedParams.fbMeasure;
        var fbSalesOrg = parsedParams.fbSalesOrg;
        var fbPlant = parsedParams.fbPlant;
        var fbDistributionChannel = parsedParams.fbDistributionChannel;
        var fbDestCountry = parsedParams.fbDestCountry;
        var fbMapStatus = parsedParams.fbMapStatus;
        var fbValidFlag = parsedParams.fbValidFlag;
        
        var mfbViaSite = `"${fbViaSite}"`;
        var mfbMeasure = `"${fbMeasure}"`;
        var mfbSalesOrg = `"${fbSalesOrg}"`;
        var mfbPlant = `"${fbPlant}"`;
        var mfbDistributionChannel = `"${fbDistributionChannel}"`;
        var mfbDestCountry = `"${fbDestCountry}"`;
        var mfbMapStatus = `"${fbMapStatus}"`;
        var mfbValidFlag = `"${fbValidFlag}"`;
        
                
        //Checking Member available for the given Description --
        let duplicateCheck = 'Select (&CWV * [Location].[Location].['+fbToSite+'] * [Sub Location].[Sub Location].['+fbFromSite+']* [Site Price Type].[Site Price Type].['+fbSitePriceType+']*[Site Price Type].[Inter Company Type ID].['+fbIntercompanyType+']*[Site Price Type].[Key Combination].['+fbKeyCombination+']* [Site Price Type].[Description].['+fbDescription+'] ) on row, ({Measure.[Site Price Type Map_Created by], Measure.[Site Price Type Map_Creation time], Measure.[Site Price Type Map_Dest Country], Measure.[Site Price Type Map_Distribution Channel], Measure.[Site Price Type Map_Map Status], Measure.[Site Price Type Map_Measure], Measure.[Site Price Type Map_Plant], Measure.[Site Price Type Map_Sales Org], Measure.[Site Price Type Map_Update time], Measure.[Site Price Type Map_Updated by], Measure.[Site Price Type Map_Valid Flag], Measure.[Site Price Type Map_Via Site]}) on column where {Measure.[Site Price Type Map_Delete Flag]==N};';
        
        var checkQueryResult1 = cellsetModule.createCellSet(queryModule.select(duplicateCheck));
        var duplicateCheckCount= checkQueryResult1.rowCount;
        Log.Info('duplicateChecCount...---' +duplicateCheckCount);

        // Check if fbFieldDescription is zero or more than one(zero means newly data entered)
        if (duplicateCheckCount !== 0) {
                RuleOutputToUI = 
                {
                    Status: 'Error',
                    Message: 'There is previously registered data.'
                };

          return; // Exit the function if duplicates are found
          }
        else
        {
            //Creating a Row for Report "5004 Condition" 
            var updateQuery = 'cartesian scope: (&CWV * [Location].[Location].['+fbToSite+'] * [Sub Location].[Sub Location].['+fbFromSite+'] * [Site Price Type].[Site Price Type].['+fbSitePriceType+']); Measure.[Site Price Type Map_Via Site] = '+mfbViaSite+'; Measure.[Site Price Type Map_Measure] = '+mfbMeasure+'; Measure.[Site Price Type Map_Sales Org] = '+mfbSalesOrg+'; Measure.[Site Price Type Map_Plant] = '+mfbPlant+'; Measure.[Site Price Type Map_Distribution Channel] = '+mfbDistributionChannel+'; Measure.[Site Price Type Map_Dest Country] = '+mfbDestCountry+'; Measure.[Site Price Type Map_Map Status] = '+mfbMapStatus+'; Measure.[Site Price Type Map_Valid Flag] = '+mfbValidFlag+';  Measure.[Site Price Type Map_Delete Flag] = '+'"N"'+';Measure.[Site Price Type Map_Created by]=CurrentUser().[User Name];Measure.[Site Price Type Map_Creation time]=now() ; end scope;';

            // Log.Info('duplicateChecCount...---' +duplicateCheckCount1);
            queryModule.update(updateQuery);
        }   
    };
    var fn_Edit= function(o9Params){
        nscmUtil = new commonLib.NSCMUtil();

        nscmCommon.setLogLevel("Debug");
        nscmCommon.printParams(o9Params);
        let parsedParams = JSON.parse(o9Params);
        
        //Sub Location
        var fbFromSite = parsedParams.fbFromSite;
        //Location
        var fbToSite = parsedParams.fbToSite;
        //Site Price Type
        var fbSitePriceType = parsedParams.fbSitePriceType;
        //Tuple List
        var TupleList = parsedParams.fbTupleList;
        var TupleListLength = TupleList.length;
        
        var fbViaSite = parsedParams.fbViaSite;
        var fbMeasure = parsedParams.fbMeasure;
        var fbSalesOrg = parsedParams.fbSalesOrg;
        var fbPlant = parsedParams.fbPlant;
        var fbDistributionChannel = parsedParams.fbDistributionChannel;
        var fbDestCountry = parsedParams.fbDestCountry;
        var fbMapStatus = parsedParams.fbMapStatus;
        var fbValidFlag = parsedParams.fbValidFlag;
        
        var mfbViaSite = `"${fbViaSite}"`;
        var mfbMeasure = `"${fbMeasure}"`;
        var mfbSalesOrg = `"${fbSalesOrg}"`;
        var mfbPlant = `"${fbPlant}"`;
        var mfbDistributionChannel = `"${fbDistributionChannel}"`;
        var mfbDestCountry = `"${fbDestCountry}"`;
        var mfbMapStatus = `"${fbMapStatus}"`;
        var mfbValidFlag = `"${fbValidFlag}"`;
                
        if (TupleListLength > 1) {
                RuleOutputToUI = 
                {
                    Status: 'Error',
                    Message: 'Multiple Rows Selected. Please Select Single Row and Proceed.'
                };

        return; // Exit the function if Multiple record are found
        }
        else
        {
            //Updating a Row for Report "5004 Condition" 
            var updateQuery = 'scope: (&CWV * [Location].[Location].['+fbToSite+'] * [Sub Location].[Sub Location].['+fbFromSite+'] * [Site Price Type].[Site Price Type].['+fbSitePriceType+']); Measure.[Site Price Type Map_Via Site] = '+mfbViaSite+'; Measure.[Site Price Type Map_Measure] = '+mfbMeasure+'; Measure.[Site Price Type Map_Sales Org] = '+mfbSalesOrg+'; Measure.[Site Price Type Map_Plant] = '+mfbPlant+'; Measure.[Site Price Type Map_Distribution Channel] = '+mfbDistributionChannel+'; Measure.[Site Price Type Map_Dest Country] = '+mfbDestCountry+'; Measure.[Site Price Type Map_Map Status] = '+mfbMapStatus+'; Measure.[Site Price Type Map_Valid Flag] = '+mfbValidFlag+'; end scope;';

            queryModule.update(updateQuery);
        }     
    };
    
    return { 
        fn_Add : fn_Add,
        fn_Edit  : fn_Edit
    };

});