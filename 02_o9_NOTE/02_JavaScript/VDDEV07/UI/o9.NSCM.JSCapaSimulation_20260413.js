define('o9.NSCM.JSCapaSimulation', ['o9/data/query', 'o9/data/cellset', 'o9.NSCM.commonLib'], function(){
	const programName = "o9.NSCM.JSCapaSimulation";

    function fn_weekCombo(o9Params){
        try{
            const commonLib = require('o9.NSCM.commonLib');
            const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
            vdCommon.setLogLevel("Debug");
            
            // 파라미터 가져오기
            vdCommon.printParams(o9Params);	
            var parsedParams = JSON.parse(o9Params);
            let fbTimeNameSet = parsedParams.fbTimeNameSet;
        
            let selectQuery = 'Select (&'+fbTimeNameSet+' * [Time].[Month]) orderby [Time].[Week].Name;';
            vdCommon.debug("[fn_weekCombo]" +selectQuery );
            //selectList(dimension, measure, where, orderby, limit)
            let selectResult = vdCommon.selectQueryList("[fn_weekCombo]" ,selectQuery );
            let comboList = vdCommon.fn_makeCombo(selectResult, {DimName : "Time", DimAttbName : "Week", existAll : false, Sort : "DisplayName", isDisplayNameWithCode : false});

            return comboList;
        }catch ( e ) {
            RuleOutputToUI = { Status : 'Error', Message : "Js Logic Error : " + e.message };
            return;
        }  
    }    

    function fn_mpApply(o9Params){
        try{
            const commonLib = require('o9.NSCM.commonLib');
            const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
            vdCommon.setLogLevel("Debug");
            
            // 파라미터 가져오기
            vdCommon.printParams(o9Params);	
            var parsedParams = JSON.parse(o9Params);
            var fbVersion = parsedParams.fbVersion;
            var fbLocation = parsedParams.fbLocation;
            var fbDataSet = parsedParams.fbDataSet;
            var fbCopyWeek = parsedParams.fbCopyWeek;          
            var copyWeekList = '', locationList = ''; 
        
            //Week List
            for(var k=0; k < fbCopyWeek.length; k++){
                copyWeekList += '"'+fbCopyWeek[k]+'"';
                
                if ((k + 1) < fbCopyWeek.length){
                    copyWeekList += ','
                }
            }
            vdCommon.debug("[List]" + fbCopyWeek ) ;
            
            //Location List
            for(var k=0; k < fbLocation.length; k++){
                locationList += '"'+fbLocation[k]+'"';
                
                if ((k + 1) < fbLocation.length){
                    locationList += ','
                }
            }
            vdCommon.debug("[List]" + locationList ) ;
        
            let lsResult, csResult ;
            let timeWeek = '', location = '', groupID = '', line = '';
            let normal_OT_hours, special_OT_hours, twoShift_OT_hours, OT_hours ;
            let sWorkType ="";
  
            //Capa Simual Line
            //24.12.23 Group ID 추가함.
            selectQuery = 'Select ([Version].[Version Name].['+fbVersion+'] *'+
                        ' [Time].[Week].filter(#.Name in {'+copyWeekList+'}) *'+
                        ' [Data Set].[Data Set].['+fbDataSet+'] *'+
                        ' [Location].[Location].filter(#.Name in {'+locationList+'}) *'+
                        ' [Group].[Group ID] * [Line].[Line] ) on row, '+
                        '({'+
                        ' Measure.[MFG Capa Simul Line_Normal OT Hours],'+
                        ' Measure.[MFG Capa Simul Line_Special OT Hours],'+
                        ' Measure.[MFG Capa Simul Line_TwoShift OT Hours],'+
                        ' Measure.[MFG Capa Simul Line_OT Hours]'+
                        ' }) on column ;';
 
            lsResult = vdCommon.selectQueryList("[fn_mpApply(Capa Simual Line)]", selectQuery);

            var tempKey= "", checkValue="";
            for ( var i = 0; i <= lsResult.rowCount + 1 ; i++ ) {                
                if(i < lsResult.rowCount){
                    timeWeek = lsResult.cs.row(i).cell(lsResult.cs.memberColumnIndex("Time", "Week")).Name;
                    location = lsResult.cs.row(i).cell(lsResult.cs.memberColumnIndex("Location", "Location")).Name;
                    groupID = lsResult.cs.row(i).cell(lsResult.cs.memberColumnIndex("Group", "Group ID")).Name;
                    line = lsResult.cs.row(i).cell(lsResult.cs.memberColumnIndex("Line", "Line")).Name;
                    
                    checkValue = timeWeek + "_" + location + "_" + line ;
                    vdCommon.debug("[checkValue]"+checkValue + "[tempKey]["+ tempKey+"]");
                }else{
                    checkValue = "";
                }
                    
                if(tempKey != checkValue){
                    vdCommon.debug("check...");
                    if(tempKey != ""){
                        //update 처리함.
                        let updateDimension = [];
                        let updateMeasure =[];
                        //create 처리함.
                        let createDimension = [];
                        let createMeasure =[];

                        //조회하여 updateMeasure OR createMeasure 분기함.
                        // 25.04.28 수정
                        // Work Type을 [O/T Hour]으로 합침.
                        // O/T Hour = NORMAL_OT_TIME(평일잔업 6시간) + SPECIAL_OT_TIME(특근 8시간)
                        let selectWorkCal = 'Select ([Version].[Version Name].['+fbVersion+'] * ';
                        selectWorkCal += '[Time].[Week].['+tempKey.split("_")[0]+'] * ';
                        selectWorkCal += '[Location].[Location].['+tempKey.split("_")[1]+'] * ';
                        selectWorkCal += '[Line].[Line].['+tempKey.split("_")[2]+'] * ';
                        selectWorkCal += '[Work Type].[Work Type].[O/T Hour] * ';
                        selectWorkCal += '[Data Set].[Data Set].['+fbDataSet+']';
                        selectWorkCal += ') on row, ';
                        selectWorkCal += '({Measure.[Work Cal Line_Time], Measure.[Work Cal Line_Lock Flag]}) on column ;';

                        let workCalResult = vdCommon.selectQueryList("[fn_mpApply(selectWorkCal_Normal OT)]", selectWorkCal);

                        if(workCalResult.rowCount > 0){
                            //Update
                            updateDimension = [];
                            updateMeasure =[];
                            //Work Cal Line Update(평일잔업)
                            updateDimension.push('[Version].[Version Name].['+fbVersion+']');
                            updateDimension.push('[Time].[Week].['+tempKey.split("_")[0]+']');
                            updateDimension.push('[Location].[Location].['+tempKey.split("_")[1]+']');
                            updateDimension.push('[Line].[Line].['+tempKey.split("_")[2]+']');
                            updateDimension.push('[Work Type].[Work Type].[O/T Hour]');                        
                            updateDimension.push('[Data Set].[Data Set].['+fbDataSet+']');
                            updateMeasure.push('Measure.[Work Cal Line_Time] = '+OT_hours+';');
                            updateMeasure.push('Measure.[Work Cal Line_Lock Flag] = true;');
                            vdCommon.updateMeasure(updateDimension,updateMeasure);
                        }else{
                            //Create
                            createDimension = [];
                            createMeasure =[];
                            //Work Cal Line Update(평일잔업)
                            createDimension.push('[Version].[Version Name].['+fbVersion+']');
                            createDimension.push('[Time].[Week].['+tempKey.split("_")[0]+']');
                            createDimension.push('[Location].[Location].['+tempKey.split("_")[1]+']');
                            createDimension.push('[Line].[Line].['+tempKey.split("_")[2]+']');
                            createDimension.push('[Work Type].[Work Type].[O/T Hour]');                        
                            createDimension.push('[Data Set].[Data Set].['+fbDataSet+']');
                            createMeasure.push('Measure.[Work Cal Line_Time] = '+OT_hours+';');
                            createMeasure.push('Measure.[Work Cal Line_Lock Flag] = true;');
                            vdCommon.createMeasure(createDimension,createMeasure);
                        }

                    }
                    vdCommon.debug("Reset");
                    tempKey = checkValue ;
                    normal_OT_hours = 0;
                    special_OT_hours = 0;
                    twoShift_OT_hours = 0;
                    OT_hours = 0;
                }
                if(i < lsResult.rowCount){
                    vdCommon.debug("Data Cal["+i+"]["+tempKey+"]["+checkValue+"]");
                    normal_OT_hours += lsResult.cs.row(i).cell(lsResult.cs.measureColumnIndex("MFG Capa Simul Line_Normal OT Hours"));
                    special_OT_hours += lsResult.cs.row(i).cell(lsResult.cs.measureColumnIndex("MFG Capa Simul Line_Special OT Hours"));   
                    twoShift_OT_hours += lsResult.cs.row(i).cell(lsResult.cs.measureColumnIndex("MFG Capa Simul Line_TwoShift OT Hours"));   
                    OT_hours += lsResult.cs.row(i).cell(lsResult.cs.measureColumnIndex("MFG Capa Simul Line_OT Hours"));   
                }                 
            }

        } catch ( e ) {
            RuleOutputToUI = { Status : 'Error', Message : "Js Logic Error : " + e.message };
            return;
        }
    }

    function fn_capaSimulation(o9Params){       
        try{
            const commonLib = require('o9.NSCM.commonLib');
            const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
            vdCommon.setLogLevel("Debug");
            
            // 파라미터 가져오기
            vdCommon.printParams(o9Params);	
            var parsedParams = JSON.parse(o9Params);
            var fbVersion = parsedParams.fbVersion;
            var fbDataSet = parsedParams.fbDataSet;		
					

            if(fbDataSet ){
                //DataSet 존재여부 체크
                let seqQuery = 'Select ([Data Set].[Data Set].filter(#.Name == "'+fbDataSet+'").relatedmembers([Data Set]));';
                let selectResult = vdCommon.selectQueryList("[Location]" ,seqQuery );

                if(selectResult.rowCount > 0){
                    //Weekly 새로 생성을 위해 삭제
                    //fn_DeleteData(); Weekly Plan 데이타를 다시 생성해야할까?

                    //member 있는 경우 => 기존 데이타 삭제 => 배치 호출
                    let deleteWhere = [];
                    deleteWhere.push('[Version].[Version Name].['+fbVersion+']');
                    deleteWhere.push('&MPHorizon');
                    deleteWhere.push('[Data Set].[Data Set].filter(#.Name in {"'+fbDataSet+'"})');

                    vdCommon.deleteMeasure(deleteWhere, "MFG Capa Simul");
                    vdCommon.deleteMeasure(deleteWhere, "MFG Capa Simul Line");
                    vdCommon.deleteMeasure(deleteWhere, "MFG Capa Simul LineGrp");

                }
            }
            //let PREV_VERSION = fn_SelectVersion(o9Params);
            let CURR_VERSION = fbVersion;
            //파이썬 호출
            //데이타 생성 (MPHorizon 기간만큼 생성)
            let execQuery = `EXEC plugin instance [PY_UI_MFGCapaSimul] for Measures {[MFG Capa Simul Line_Week Work Hours]} ` +
                    `using scope ([Version].[Version Name].filter((#.Name == Version.[Version Name].[`+CURR_VERSION+`].[Prev Sync Version Name]) || (#.Name == "`+CURR_VERSION+`"))) ` +            
                    `using arguments {(ExecutionMode, "MediumWeight"), (paramOutVersion , "`+CURR_VERSION+`") , (paramDataSet , "`+fbDataSet+`") ` +
                    ` , (MaxSliceTableCells, 200000000), (MaxConcurrency, 1 ), ([Param.o9_sys_log_level], "DEBUG")};` ;

            //vdCommon.printStep("["+programName+"] EXEC Python Call SQL>>"+execQuery);
            vdCommon.executeQuery("PY_UI_MFGCapaSimul ", execQuery);   	
			Log.Info(">>>>>>>>>>@  fn_capaSimulation 함수 종료"); 
	
			//추가된 Memter에 대한 데이타를 파이썬에서 생성함.
			vdCommon.programEnd();			

		} catch ( e ) {
            RuleOutputToUI = { Status : 'Error', Message : "Js Logic Error : " + e.message };
            return;
        }
	}

    function fn_locationCombo(o9Params){
        try{
            const commonLib = require('o9.NSCM.commonLib');
            const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
            vdCommon.setLogLevel("Debug");

            // 파라메타 가져오기
            let parsedParams = JSON.parse(o9Params); 
            let fbVersion = parsedParams.fbVersion;

            let result = vdCommon.selectList(["&NSUISiteGrp1View * [Location].[Location Type].[MF] * [Location].[Location]"], 
                                            []
                                            ,"","orderby [Location].[Location].DisplayName","");

            vdCommon.printCsData(result, 3);

            let comboList = vdCommon.fn_makeCombo(result, {DimName : "Location",DimAttbName : "Location", Sort :"DisplayName", existAll : false, isDisplayNameWithCode : true});
            vdCommon.debug("ComboData : " + JSON.stringify(comboList));

            vdCommon.programEnd();

            return comboList;
        }catch ( e ) {
            RuleOutputToUI = { Status : 'Error', Message : "Js Logic Error : " + e.message };
            return;
        }      
    }     

    return{
		fn_capaSimulation  : fn_capaSimulation,
        fn_weekCombo: fn_weekCombo,
        fn_mpApply : fn_mpApply,
        fn_locationCombo : fn_locationCombo
    };	
});