define('o9.NSCM.JSLineGroupMapping', ['o9/data/query', 'o9/data/cellset', 'o9.NSCM.commonLib'], function(){	
	const programName = "o9.NSCM.JSLineGroupMapping";

    function fn_dataCheck(o9Params){
        try{
            const commonLib = require('o9.NSCM.commonLib');
            const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
            vdCommon.setLogLevel("Debug");            
            
            // 파라메타 가져오기
            vdCommon.printParams(o9Params);
            let parsedParams = JSON.parse(o9Params);    
            var chkLocation = parsedParams.chkLocation;
            var chkLine = parsedParams.chkLine;
            var chkGroupID = parsedParams.chkGroupID;
            let rtnValue = 0;
            vdCommon.debug("["+chkLocation.length+"]["+chkLine.length+"]["+chkGroupID.length+"]");

            if(chkLocation.length > 1 || chkLine.length > 1 || chkGroupID.length > 1){
                rtnValue = 1;
                RuleOutputToUI = { Status : 'Error', Message : "You cannot select multiple rows." };  
            }
    
            vdCommon.printStep(">>>>>>>>>>>  fn_DataCheck End");        
            vdCommon.programEnd();
    
            return rtnValue;            

        }catch ( e ) {
            RuleOutputToUI = { Status : 'Error', Message : "Js Logic Error : " + e.message };
            return;
        }
    }

    function fn_selectLine(o9Params){
        try{
            const commonLib = require('o9.NSCM.commonLib');
            const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
            vdCommon.setLogLevel("Debug");  
                
            // 파라메타 가져오기
            vdCommon.printParams(o9Params);
            let parsedParams = JSON.parse(o9Params); 
            let fbVersion = parsedParams.fbVersion;
            let fbLineType = parsedParams.fbLineType;    
            
            //query 정의
            let selectQuery = 'Select ( [Line].[Line] * [Line].[Line Type].filter(#.Name == "'+fbLineType+'")) on row, () on column '
            selectQuery += 'orderby [Line].[Line].DisplayName;';
            let selectResult = vdCommon.selectQueryList("[fn_selectLine]" ,selectQuery );
            let comboList = vdCommon.fn_makeCombo(selectResult, {DimName : "Line", DimAttbName : "Line", existAll : false, Sort : "DisplayName", isDisplayNameWithCode : false});

            vdCommon.programEnd();    
            return comboList;            
        }catch ( e ) {
            RuleOutputToUI = { Status : 'Error', Message : "Js Logic Error : " + e.message };
            return;
        }
    }       
	

    function fn_selectGroupID(o9Params){
        try{      
            const commonLib = require('o9.NSCM.commonLib');
            const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
            vdCommon.setLogLevel("Debug");  
                
            // 파라메타 가져오기
            vdCommon.printParams(o9Params);
            let parsedParams = JSON.parse(o9Params); 
            let fbVersion = parsedParams.fbVersion;
            let fbLocation = parsedParams.fbLocation;
            let fbLine = parsedParams.fbLine;
       
            //query 정의        
            let query = 'Select ([Group].[Group ID] * [Group].[Group Type].filter(#.Name in { "Line Group"})) orderby [Group].[Group ID].DisplayName;';

            let selectResult = vdCommon.selectQueryList("[fn_selectLine]" ,query );
            let comboList = vdCommon.fn_makeCombo(selectResult, {DimName : "Group", DimAttbName : "Group ID", existAll : false, Sort : "DisplayName", isDisplayNameWithCode : false});    
        
            vdCommon.programEnd();
    
            return comboList;            
        }catch ( e ) {
            RuleOutputToUI = { Status : 'Error', Message : "Js Logic Error : " + e.message };
            return;
        }          
    }

    function fn_selectPeriod(o9Params){
        try{      
            const commonLib = require('o9.NSCM.commonLib');
            const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
            vdCommon.setLogLevel("Debug");  
                
            // 파라메타 가져오기
            vdCommon.printParams(o9Params);
            let parsedParams = JSON.parse(o9Params); 
            let fbVersion = parsedParams.fbVersion;
            let fbSelectPeriod = parsedParams.fbSelectPeriod;  
   
            //Current Week (+ 1)~ 부터 조회
            let query = 'Select (&MDMHorizon.filter(#.Key >= &CurrentWeek.element(0).LeadOffset(1).Key)) ;';
    
            let selectResult = vdCommon.selectQueryList("[fn_selectLine]" ,query );
            let comboList = vdCommon.fn_makeCombo(selectResult, {DimName : "Time", DimAttbName : "Week", existAll : false, Sort : "DisplayName", isDisplayNameWithCode : false});    
            
            vdCommon.programEnd();
    
            return comboList;            
        }catch ( e ) {
            RuleOutputToUI = { Status : 'Error', Message : "Js Logic Error : " + e.message };
            return;
        }  
    } 

    function fn_copy(o9Params){
        try{
            const commonLib = require('o9.NSCM.commonLib');
            const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
            const vdUtil = new commonLib.VdUtil();
            vdCommon.setLogLevel("Debug");  
                
            // 파라메타 가져오기
            vdCommon.printParams(o9Params);
            let parsedParams = JSON.parse(o9Params); 
            let fbVersion = parsedParams.fbVersion;
            let fbLocation = parsedParams.fbLocation; 
            let fbLineType = parsedParams.fbLineType;
            let fbLine = parsedParams.fbLine;
            let fbGroupID = parsedParams.fbGroupID;
            let fbStartWeek = parsedParams.fbStartWeek;

            let dimension = [];
            dimension.push("[Version].[Version Name].["+fbVersion+"]");
            dimension.push("[Time].[Week]");
            dimension.push("[Location].[Location].["+fbLocation+"]");
            dimension.push("[Line].[Line].["+fbLine+"]");

            let measure = [];
            measure.push("Measure.[Line Eff W]");
            measure.push("Measure.[Line Eff W_Oper Plan]");
            

            if(!vdCommon.existMeasure(dimension, measure, "")){
                let errorMsg = `This data is not registered in the [Line Efficiency]. `;
                RuleOutputToUI = { Status : 'Error', Message : errorMsg };
                return;
            }

            //Line Grp Map Measure 등록
            measureGroup = "Line Grp Map" ;
            let granularity = [];
            granularity.push("[Version].[Version Name]");
            granularity.push("[Location].[Location]");
            granularity.push("[Line].[Line]");        
            granularity.push("[Group].[Group ID]");

            let granularityValues = [];
            granularityValues.push(fbVersion);
            granularityValues.push(fbLocation);   
            granularityValues.push(fbLine);             
            granularityValues.push(fbGroupID);   
            
            if(vdCommon.existMeasure(vdCommon.makeDimension(granularity, granularityValues),
             ['Measure.[Line Grp Map_Enddate]','Measure.[Line Grp Map_Startdate]','Measure.[Line Grp Map_Flag]'], '')){
                vdCommon.updateMeasure(vdCommon.makeDimension(granularity, granularityValues),
                                        ['Measure.[Line Grp Map_Enddate] = null ;', 
                                        'Measure.[Line Grp Map_Startdate] = "'+fbStartWeek+'";',
                                        'Measure.[Line Grp Map_Flag] = "'+'Y' +'";',
                                        ]);
            }else{
                //Location + Line 에 등록된 Group ID가 있는지 확인함.
                //등록된 데이타 있는 경우 : Line Grp Map_Flag은 'N', Line Grp Map_Enddate은 fbStartWeek -1로 처리 후에 등록함.
                let result = vdCommon.selectList(['[Version].[Version Name].['+fbVersion+']',
                                                '[Location].[Location].['+fbLocation+']',
                                                '[Line].[Line].['+fbLine+']',
                                                '[Group].[Group ID]'],
                                                ['Measure.[Line Grp Map_Enddate]',
                                                'Measure.[Line Grp Map_Startdate]',
                                                'Measure.[Line Grp Map_Flag]'], '','','' );

                if(result.cs.rowCount > 0){
                    for ( var i = 0; i < result.cs.rowCount; i++ ) {
                        let dimGroupID = result.cs.row(i).cell(result.cs.memberColumnIndex("Group", "Group ID")).Name;

                        let preWeekQuery = 'Select ([Time].[Week].filter(#.Key == [Time].[Week].filter(#.Name == "'+fbStartWeek+'").element(0).LeadOffset(-1).Key));';
                        let resultPreWeek = vdCommon.selectQueryList("fn_copy(PreWeek)", preWeekQuery);
                        let sPreWeek = "";
                        if(resultPreWeek.rowCount > 0){
                            sPreWeek = resultPreWeek.cs.row(0).cell(resultPreWeek.cs.memberColumnIndex("Time", "Week")).Name;
                        }
                        vdCommon.updateMeasure(
                            ['[Version].[Version Name].['+fbVersion+']',
                            '[Location].[Location].['+fbLocation+']',
                            '[Line].[Line].['+fbLine+']',
                            '[Group].[Group ID].['+dimGroupID+']'],
                            ['Measure.[Line Grp Map_Flag] = "'+'N' +'";']);

                        vdCommon.updateMeasure(
                            ['[Version].[Version Name].['+fbVersion+']',
                            '[Location].[Location].['+fbLocation+']',
                            '[Line].[Line].['+fbLine+']',
                            '[Group].[Group ID].['+dimGroupID+']'],
                            ['Measure.[Line Grp Map_Enddate] = "'+sPreWeek+'" ;']);
                    }
                }
                vdCommon.createMeasure(vdCommon.makeDimension(granularity, granularityValues),
                                        ['Measure.[Line Grp Map_Enddate] = null ;', 
                                        'Measure.[Line Grp Map_Startdate] = "'+fbStartWeek+'";',
                                        'Measure.[Line Grp Map_Flag] = "'+'Y' +'";',
                                        ]);
            }

            vdCommon.printStep(">>>>>>>>>>> Line Grp Map. "+measureGroup +" Data createMeasure"); 
            vdCommon.printStep(">>>>>>>>>>> fn_Submit End");		
            vdCommon.programEnd();  
                       
        }catch ( e ) {
            RuleOutputToUI = { Status : 'Error', Message : "Js Logic Error : " + e.message };
            return;
        }
    }

    function fn_delete(o9Params){
        try{
            const commonLib = require('o9.NSCM.commonLib');
            const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
            vdCommon.setLogLevel("Debug");
            vdCommon.printParams(o9Params);

            // 파라메타 가져오기
            let parsedParams = JSON.parse(o9Params); 
            let fbVersion = parsedParams.fbVersion;
            let fbDataList = parsedParams.fbDataList;

            vdCommon.debug("Data List["+fbDataList.length+"]" + JSON.stringify(fbDataList));
            vdCommon.debug("["+fbDataList[0].Location.Value+"]");

            for(var k=0; k < fbDataList.length; k++){
                let whereQuery = [];
                whereQuery.push("[Version].[Version Name].["+fbVersion+"]");
                whereQuery.push("[Location].[Location].["+fbDataList[k].Location.Value+"]");
                whereQuery.push("[Group].[Group ID].["+fbDataList[k].GroupID.Value+"]");
                whereQuery.push("[Line].[Line].["+fbDataList[k].Line.Value+"]");

                vdCommon.deleteMeasure(whereQuery, "Line Grp Map");
            }

        }catch ( e ) {
            RuleOutputToUI = { Status : 'Error', Message : "Js Logic Error : " + e.message };
            return;
        }  
    }    

    return{
          fn_dataCheck : fn_dataCheck,
          fn_selectLine : fn_selectLine, 
          fn_selectGroupID : fn_selectGroupID,
          fn_selectPeriod : fn_selectPeriod, 
          fn_copy : fn_copy,
          fn_delete : fn_delete
    };		
});