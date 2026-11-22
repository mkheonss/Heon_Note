define('o9.NSCM.zzSelectTest', ['o9/data/query', 'o9/data/cellset'], function(){
	
	
	function GetToSitewithALL(o9Params){
		var parsedParams = JSON.parse(o9Params);
	    var queryModule = require('o9/data/query');
		var cellsetModule = require('o9/data/cellset');
		
		var fbVersion = parsedParams.fbVersion;
		var fbFromSite = parsedParams.fbFromSite;
		Log.Info(">>>>>>>>>>fbVersion @"  + fbVersion+"@");
		Log.Info(">>>>>>>>>>fbFromSite @" + fbFromSite+"@");
		
		var IBPLforToSitewithALL = ``;
		IBPLforToSitewithALL    += `Select ([BOD].[To Site ID] ) on row  where `;
		IBPLforToSitewithALL    += `{Version.[Version Name].[${fbVersion}]`;
		IBPLforToSitewithALL    += ` ,(Measure.[BOD Lane_EFF Enddate]>now() && Measure.[BOD Lane_EFF Startdate]<Now())`;		
		IBPLforToSitewithALL    += ` ,[BOD].[From Site ID].[${fbFromSite}]};`;
		Log.Info(">>>>>>>>>>Query ");
		Log.Info(IBPLforToSitewithALL);
		
		
		//var ItemListRsSet = cellsetModule.createCellSet(queryModule.select(IBPLforToSitewithALL));
		var ListforToSitewithALL = cellsetModule.createCellSet(queryModule.select(IBPLforToSitewithALL));
		
	    var result = [];
		Log.Info(">>>>>> count :"+ ListforToSitewithALL.rowCount);
		
		if(ListforToSitewithALL && ListforToSitewithALL.rowCount>0) {
		    var idx_ToSiteID  = ListforToSitewithALL.memberColumnIndex("BOD", "To Site ID");
		    Log.Info(">>>>>> idx_ToSiteID :"+ idx_ToSiteID);
		    
		    var all ={ Name:"ALL", DisplayName:"ALL"};
		    result.push(all)
		    
		    for(var i=0; i<ListforToSitewithALL.rowCount; i++) {
    	        Log.Info(">>>>>> i :"+ i);
    	        var ToSiteID = ListforToSitewithALL.row(i).cell(idx_ToSiteID).Name;	
    	        Log.Info(">>>>>> ToSiteID :"+ ToSiteID);
				var r ={
				  Name:ToSiteID,
				  DisplayName: ToSiteID+"  <  이름바꿈. 뒤에서 fb를 참조할 땐, Name을 가져감"
				};
				
				result.push(r)
            }
    	}else{
    	    Log.Info(">>>>>> non data : 결과없으면 - 라도 보여주자");
		    var r={
			    Name:'-',
				DisplayName: '-'
			}
			result.push(r) 
		}
		Log.Info("-------------Result-----------");
		Log.Info(result);
		return result;
	}

    return{
		GetToSitewithALL : GetToSitewithALL
    };
});