define('o9.NSCM.JSFulfillmentMasterData', ['o9/data/query', 'o9/data/cellset', 'o9.NSCM.commonLib'], function () {


    const programName = "o9.NSCM.JSCurrentUser ============>";
    const commonLib = require('o9.NSCM.commonLib');
    const queryModule = require('o9/data/query');
    const cellsetModule = require('o9/data/cellset');
    const nscmCommon = new commonLib.NSCMCommon(programName);
    const fn_ItemFunction = function (o9Params) {

      try
      {
        let nscmUtil = new commonLib.NSCMUtil();
        nscmCommon.setLogLevel("Debug");
        nscmCommon.printParams(o9Params);
        let parsedParams = JSON.parse(o9Params);

        Log.Info("props" + JSON.stringify(parsedParams));
        const queryForUIData = `Select (&CWV_MP * [Sub Location].[Sub Location].[${parsedParams.fb_HubSite}] * [Seq].[Seq] * [Item].[Item] * [Location].[Location].[${parsedParams.fb_ToSite}] * {Measure.[Fulfillment Master_Status]});`;
        //Log.Info("Statues Query" + JSON.stringify(queryForUIData));
        const uiData = cellsetModule.createCellSet(queryModule.select(queryForUIData));
        //Log.Info("Statues Query Data" + JSON.stringify(uiData));

        const ItemMap = new Map();
        for (let i = 0; i < uiData.rowCount; i++) {
            let NameVal = uiData.row(i).cell(uiData.memberColumnIndex('Item', 'Item')).Name;
            let dataMeasure = uiData.row(i).cell(uiData.measureColumnIndex('Fulfillment Master_Status'));
            Log.Info("Data Type status" + JSON.stringify(dataMeasure));
            ItemMap.set(NameVal, JSON.stringify(dataMeasure));
        }

        // Log.Info("Item Mapped Data" + [...ItemMap]);
        // Log.Info("Item Mapped Data Size" + ItemMap.size);
        
        const ItemData = `Select ([Item].[Item] ) on row,  ({Measure.[BOD Lane Item_Transit Time]}) on column where{[BOD].[To Site ID].[${parsedParams.fb_ToSite}], [BOD].[From Site ID].[${parsedParams.fb_HubSite}],  [BOD].[Transport Mode].[TRUCK],[Version].[Version Name].[CWV_MP], Item.[Product Group].[${parsedParams.fb_ProductGroup}], Item.[Product].[${parsedParams.fb_Product}] };`;
        //Log.Info("Item Query" + JSON.stringify(ItemData));
        const uiItemData = cellsetModule.createCellSet(queryModule.select(ItemData));
        //Log.Info("Item Query Data" + JSON.stringify(uiItemData));
        Log.Info("--------------------------Add Command----------------------");
        var Item = [];
        // var NameVal;
        // var DisplayNameVal
        for (let i = 0; i < uiItemData.rowCount; i++) {
            let NameVal = uiItemData.row(i).cell(uiItemData.memberColumnIndex('Item', 'Item')).Name;  
            
            //if(ItemMap.get(NameVal) === JSON.stringify('CON') || ItemMap.get(NameVal) === JSON.stringify('COM')){
            //    Log.Info("Item Condition Matched: " + ItemMap.get(NameVal));
                
            //}else{
                //Log.Info("Item Condition not matched: " + ItemMap.get(NameVal));
                let DisplayNameVal = uiItemData.row(i).cell(uiItemData.memberColumnIndex('Item', 'Item')).DisplayName;
        
                // Add Data in the ItemData Variable
                Item.push({ Name: NameVal, DisplayName: DisplayNameVal });
            //}
        }
        Log.Info("Final Item Data" + JSON.stringify(Item));
        
        return Item;
       
     }catch ( e ) {
        RuleOutputToUI = { Status : 'Error', Message : "Js Logic Error : " + e.message };
        return;
     } 

    };



    const fn_AddButton = function (o9Params) {
     
        try{

        let nscmUtil = new commonLib.NSCMUtil();
        nscmCommon.setLogLevel("Debug");
        nscmCommon.printParams(o9Params);
        let parsedParams = JSON.parse(o9Params);
        Log.Info("-------------parsedParams-------------"+parsedParams);
        Log.Info("item-----"+parsedParams.fb_Item);

        Log.Info("props" + JSON.stringify(parsedParams));
        
        var item=parsedParams.fb_Item;
        var loc=parsedParams.fb_ToSite;
        var subLoc=parsedParams.fb_HubSite;

        const queryForUIData = `Select (&CWV_MP * [Sub Location].[Sub Location].[${subLoc}] * [Seq].[Seq] * [Item].[Item].[${item}] * [Location].[Location].[${loc}] * {Measure.[Fulfillment Master_Status],Measure.[Fulfillment Master_HUB LDC BOD],Measure.[Fulfillment Master_MF LDC BOD]});`;
        const uiData = cellsetModule.createCellSet(queryModule.select(queryForUIData));
        Log.Info("queryForUIDatabelow"+queryForUIData);

        var maxSeq=0
		
        if(uiData.rowCount>0){
            for(var i=0;i<uiData.rowCount;i++){
                var temp=+uiData.row(i).cell(uiData.memberColumnIndex('Seq', 'Seq')).Name;
                if(temp>maxSeq){
                    maxSeq=temp;
                }
            }
        }
		
		var fbItem=parsedParams.fb_Item;
        Log.Info("--fbItem--------"+fbItem);
		   
		//Bod Query
        const QueryForBodName= `Select ([BOD].[BOD Name]) on row, ({Measure.[BOD Lane Item_Transit Time], if(isnull(Measure.[BOD Lane Item_Eff Enddate])||dateadd(Measure.[BOD Lane Item_Eff Enddate],-1,"week")>=Measure.[W Plan Current Date]) then("Y") else("N") as transient.[BODValid]}) on column where {[BOD].[To Site ID].filter(#.Name in {${parsedParams.fb_ToSite}}), Item.[Item].filter(#.Name in {"${fbItem}"}), [BOD].[From Site ID].Filter(#.[From Site ID Type] == "MF") , [Version]. [Version Name].[CWV_MP]};`;
		
		Log.Info("-----Fulfillment_Master_HUB_LDC_BOD-------"+QueryForBodName)
		
		const DataOfBodName=cellsetModule.createCellSet(queryModule.select(QueryForBodName));

        for(var j=1;j<=DataOfBodName.rowCount;j++){            

			var BodData=DataOfBodName.row(j-1).cell(DataOfBodName.memberColumnIndex('BOD', 'BOD Name')).Name;
            var BODValid=DataOfBodName.row(j-1).cell(DataOfBodName.measureColumnIndex('BODValid'));
			var Fulfillment_Master_HUB_LDC_BOD=`${parsedParams.fb_HubSite}`+"_"+ `${parsedParams.fb_ToSite}`+"_"+"TRUCK";

			Log.Info("--------------------------Fulfillment_Master_HUB_LDC_BOD----------------------"+Fulfillment_Master_HUB_LDC_BOD);
				
			const queryForUIData = `Select (&CWV_MP * [Sub Location].[Sub Location].[${subLoc}] * [Seq].[Seq] * [Item].[Item].[${item}] * [Location].[Location].[${loc}] * {Measure.[Fulfillment Master_Status]}) Where {Measure.[Fulfillment Master_HUB LDC BOD] == "${Fulfillment_Master_HUB_LDC_BOD}", Measure.[Fulfillment Master_MF LDC BOD] == "${BodData}"};`;
			const uiData2 = cellsetModule.createCellSet(queryModule.select(queryForUIData));
			Log.Info("queryForUIDatabelow"+queryForUIData);
			
			// if uiData2.rowCount > 0 then skip
			if(uiData2.rowCount == 0){
				maxSeq = maxSeq + 1
				Log.Info("---------------------------BodData---------------------"+BodData);
				var updateQuery=`cartesian scope: (&CWV_MP * [Sub Location].[Sub Location].filter(#.Name in {${parsedParams.fb_HubSite}}) * [Seq].[Seq].[${maxSeq}] * Item.[Item].filter(#.Name in {"${fbItem}"}) * [Location].[Location].filter(#.Name in {${parsedParams.fb_ToSite}}));
				Measure.[Fulfillment Master_HUB LDC BOD]="${Fulfillment_Master_HUB_LDC_BOD}";
				Measure.[Fulfillment Master_MF LDC BOD]="${BodData}";
				Measure.[Fulfillment Master_BOD Valid] = "${BODValid}";
				Measure.[Fulfillment Master_Fulfillment] = "N";
				Measure.[Fulfillment Master_Status] = "REQ";

				end scope;`;

				queryModule.update(updateQuery);
			}
        }

      }catch ( e ) {
        RuleOutputToUI = { Status : 'Error', Message : "Js Logic Error : " + e.message };
        return;
     } 
    
    };

    


    return {
        fn_ItemFunction: fn_ItemFunction,
        fn_AddButton: fn_AddButton
       
    };
});