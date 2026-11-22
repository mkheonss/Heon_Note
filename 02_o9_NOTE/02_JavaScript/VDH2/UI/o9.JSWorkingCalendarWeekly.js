define('o9.JSWorkingCalendarWeekly', ['o9/data/query', 'o9/data/cellset', 'o9.NSCM.commonLib'], function(){
	
    function fnSelectDataSetIDList(o9Params){
		Log.Info(">>>>>>>>>>@  SelectDataSetIDList 함수 호출");
		var parsedParams = JSON.parse(o9Params);
	    var queryModule = require('o9/data/query');
		var cellsetModule = require('o9/data/cellset');

		var fbVersion = parsedParams.fbVersion;

		var IBPLSQL = ``;
		IBPLSQL += `Select ([Data Set].[Data Set]) on row ;`;
		// IBPLSQL += `Where `;
		Log.Info("Log(SQL) ;;"+ IBPLSQL);

		var ListDataSetID = cellsetModule.createCellSet(queryModule.select(IBPLSQL));

		var result = [];

		if(ListDataSetID && ListDataSetID.rowCount>0) {
			var idx_DimID  = ListDataSetID.memberColumnIndex("Data Set", "Data Set");
			Log.Info(">>>>>> idx_DimID :"+ idx_DimID);

		    for(var i=0; i<ListDataSetID.rowCount; i++) {
    	        var DimensionID = ListDataSetID.row(i).cell(idx_DimID).Name;
    	        // Log.Info(">>>>>> DimensionID :"+ DimensionID);
				var r ={
				  Name:DimensionID,
				  DisplayName: DimensionID
				};

				result.push(r)
            }
		}

		Log.Info("-------------Result-----------");
		Log.Info(result);
		Log.Info(">>>>>>>>>>@  SelectDataSetIDList 함수 종료");
		return result;
    }

    function fnWorkingProcess(o9Params){
        var commonLib = require('o9.NSCM.commonLib');

        var programName = "o9.JSWorkingCalendarWeekly ============> fnWorkingProcess";	
        vdCommon = new commonLib.VdCommon(programName);
        vdCommon.setLogLevel("Debug");

        vdCommon.printParams(o9Params);	

        // 파라미터 가져오기
        var parsedParams = JSON.parse(o9Params);	

		var fbVersion = parsedParams.fbVersion;
		var fbSelectDataID = parsedParams.fbSelectDataID;
		var fbDeleteDataSetID = parsedParams.fbSelectDataID;

		var memberSql = "[Data Set].[Data Set] ";

        // Member 를 추가한다.
        if ( !vdCommon.existMember(memberSql, fbSelectDataID) ) {
            vdCommon.createMember(memberSql, fbSelectDataID);
        }else{

			//다시 생성할 Data Set에 대한 기존 데이타를 삭제함.

			//데이타 처리 : Working Calendar Group
			var workingCalendarGroup_DIM =  "[Data Set].[Data Set].["+fbSelectDataID+"]";
			workingCalendarGroup_DIM += ",[Work Type].[Work Type]";
			workingCalendarGroup_DIM += ",[Group].[Group ID]";
			workingCalendarGroup_DIM += ",[Line].[Line Type]";
			workingCalendarGroup_DIM += ",[Version].[Version Name]";
			workingCalendarGroup_DIM += ",[Location].[Location]";
			workingCalendarGroup_DIM += ",[Time].[Week]";

			vdCommon.deleteMeasure(workingCalendarGroup_DIM, "Working Calendar Group");

			//데이타 처리 : Working Calendar Line
			var workingCalendarLine_DIM =  "[Data Set].[Data Set].["+fbSelectDataID+"]";
			workingCalendarLine_DIM += ",[Work Type].[Work Type]";
			workingCalendarLine_DIM += ",[Line].[Line]";
			workingCalendarLine_DIM += ",[Version].[Version Name]";
			workingCalendarLine_DIM += ",[Location].[Location]";
			workingCalendarLine_DIM += ",[Time].[Week]";

			vdCommon.deleteMeasure(workingCalendarLine_DIM, "Working Calendar Line");	
		}

		//화면에서 선택한 Data Set 데이타를 처리함.
		Log.Info(">>>>>>>>>>@ 화면에서 선택된 Data Set ID ::"+ fbDeleteDataSetID); 
	

		Log.Info(">>>>>>>>>>@  fnWorkingProcess 함수 종료"); 

		//추가된 Memter에 대한 데이타를 파이썬에서 생성함.
	}		
	
    return{
		fnSelectDataSetIDList  : fnSelectDataSetIDList,
		fnWorkingProcess  : fnWorkingProcess
    };	
});