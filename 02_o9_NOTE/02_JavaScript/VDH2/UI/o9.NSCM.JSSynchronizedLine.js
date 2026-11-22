define('o9.NSCM.JSSynchronizedLine', ['o9/data/query', 'o9/data/cellset', 'o9.NSCM.commonLib'], function(){	
	const programName = "o9.NSCM.JSSynchronizedLine";

    function fn_dataCheck(o9Params){
        try{
            const commonLib = require('o9.NSCM.commonLib');
            const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
            vdCommon.setLogLevel("Debug");    
            vdCommon.printParams(o9Params);   
            
            // 파라메타 가져오기
            let parsedParams = JSON.parse(o9Params);

            var chkLocation = parsedParams.chkLocation;
            var chkLine = parsedParams.chkLine;
            var chkToLine = parsedParams.chkToLine;
            let rtnValue = 0;

            if(chkLocation.length > 1 || chkLine.length > 1 || chkToLine.length > 1){
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
            vdCommon.printParams(o9Params);   
            // 파라메타 가져오기
            let parsedParams = JSON.parse(o9Params); 
            let fbVersion = parsedParams.fbVersion;
            let fbLineType = parsedParams.fbLineType;
            
            //query 정의
            let selectQuery = 'Select ( [Line].[Line] * [Line].[Line Type].filter(#.Name == "'+fbLineType+'")) '
            + 'orderby [Line].[Line].Name;';

            let selectResult = vdCommon.selectQueryList("[fn_selectLine]" ,selectQuery );
            let comboList = vdCommon.fn_makeCombo(selectResult, {DimName : "Line",DimAttbName : "Line", Sort :"Name", existAll : false, isDisplayNameWithCode : false});
            vdCommon.programEnd();

            return comboList;            
            
        }catch ( e ) {
            RuleOutputToUI = { Status : 'Error', Message : "Js Logic Error : " + e.message };
            return;
        }

    }    
    
    function fn_selectToLineOld(o9Params){
        try{
            const commonLib = require('o9.NSCM.commonLib');
            const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
            vdCommon.printParams(o9Params);

            // 파라메타 가져오기
            let parsedParams = JSON.parse(o9Params); 
            let fbVersion = parsedParams.fbVersion;
            let fbLocation = parsedParams.fbLocation;
            let fbLine = parsedParams.fbLine;

            let selectQuery = 'Select ( [To Line].[To Line] ) on row, ';
            selectQuery += ' ({Measure.[Sync Line_Enddate], Measure.[Sync Line_Flag], Measure.[Sync Line_Startdate]}) on column';
            selectQuery += ' Where { [Version].[Version Name].filter(#.Name == "'+fbVersion+ '") ';
            selectQuery += ' , [Location].[Location].filter(#.Name == "'+fbLocation+ '")';
            selectQuery += ' , [Line].[Line].filter(#.Name == "'+fbLine+ '")';
            selectQuery += ' } ;';
            //let regComboList = fn_comboMake(selectQuery, dimParams);  
            let selectResult = vdCommon.selectQueryList("[fn_selectToLine(Reg)]" ,selectQuery );
            let regComboList = vdCommon.fn_makeCombo(selectResult, {DimName : "To Line",DimAttbName : "To Line", Sort :"Name", existAll : false, isDisplayNameWithCode : false});
        
            //query 정의        
            let queryAll = 'Select ([To Line].[To Line])';
            queryAll +=  ' Where {[To Line].[To Line Type].filter(#.Name in {"MAIN", "LCM"})}';
            queryAll +=  ' orderby [To Line].[To Line].Name ;';

            //vdCommon.debug("fn_SelectToLine > select query : " + queryAll);
            let selectAllResult = vdCommon.selectQueryList("[fn_selectToLine(All)]" ,queryAll );
            let comboListAll = vdCommon.fn_makeCombo(selectAllResult, {DimName : "To Line",DimAttbName : "To Line", Sort :"Name", existAll : false, isDisplayNameWithCode : false});

            let blankList = [{ Name: "-", DisplayName: "-" }];
            comboListAll = blankList.concat(comboListAll);

            vdCommon.debug("All ComboData >  : " + JSON.stringify(comboListAll));

            let comboList = comboListAll.filter(function(item1, Name){
                //filter() 메서드는 콜백함수에서 정의한 조건이 true인 항목만 리턴한다.(필터링)
                var findIndex =  regComboList.findIndex(function(item2, Name){
                    //findIndex() 메서드는 콜백함수에 정의한 조건이 true인 항목의 index를 리턴한다.
                    return item1.Name == item2.Name
                });
                if(findIndex < 0) return true;
            });
            vdCommon.debug("Last ComboData >  : " + JSON.stringify(comboList));
            vdCommon.programEnd();

            return comboList;
        }catch ( e ) {
            RuleOutputToUI = { Status : 'Error', Message : "Js Logic Error : " + e.message };
            return;
        }
    }  

    function fn_selectToLine(o9Params){
        try{
            const commonLib = require('o9.NSCM.commonLib');
            const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
            vdCommon.printParams(o9Params);

            // 파라메타 가져오기
            let parsedParams = JSON.parse(o9Params); 
            let fbVersion = parsedParams.fbVersion;
            let fbLocation = parsedParams.fbLocation;
            let fbLine = parsedParams.fbLine;
            let fbLineType = parsedParams.fbLineType;

            //query 정의        
            let queryAll = 'Select ([To Line].[To Line])';
            queryAll +=  ' Where {[To Line].[To Line Type].filter(#.Name in {"LCM"})}';
            queryAll +=  ' orderby [To Line].[To Line].Name ;';

            //vdCommon.debug("fn_SelectToLine > select query : " + queryAll);
            let selectAllResult = vdCommon.selectQueryList("[fn_selectToLine(All)]" ,queryAll );
            let comboListAll = vdCommon.fn_makeCombo(selectAllResult, {DimName : "To Line",DimAttbName : "To Line", Sort :"Name", existAll : false, isDisplayNameWithCode : false});

            let blankList = [{ Name: "-", DisplayName: "-" }];
            let comboList = blankList.concat(comboListAll);

            vdCommon.debug("Last ComboData >  : " + JSON.stringify(comboList));
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

            vdCommon.programStart();
            vdCommon.printStep(">>>>>>>>>>>  fn_SelectPeriod Start");
            vdCommon.printParams(o9Params);

            // 파라메타 가져오기
            let parsedParams = JSON.parse(o9Params); 
            let fbVersion = parsedParams.fbVersion;
            //let fbSelectPeriod = parsedParams.fbSelectPeriod;  

            //Current Week (+ 1)~ 부터 조회
            let selectQuery = 'Select ([Time].[Week].filter(#.Key >= &CurrentWeek.element(0).LeadOffset(1).Key)) ;';

            let selectResult = vdCommon.selectQueryList("[fn_selectPeriod]" ,selectQuery );
            let comboList = vdCommon.fn_makeCombo(selectResult, {DimName : "Time",DimAttbName : "Week", Sort :"Name", existAll : false, isDisplayNameWithCode : false});
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
            vdCommon.setLogLevel("Debug");
            vdCommon.printParams(o9Params);

            // 파라메타 가져오기
            let parsedParams = JSON.parse(o9Params); 
            let fbVersion = parsedParams.fbVersion;
            let fbLocation = parsedParams.fbLocation; 
            let fbLine = parsedParams.fbLine;
            let fbToLine = parsedParams.fbToLine;
            let fbStartWeek = parsedParams.fbStartWeek;


            let isToLineUserEntry = "N";
       
            vdCommon.printStep(">>>>>>>>>>>  fn_Submit Line Eff Check");
            let dimension = [];
            dimension.push("[Version].[Version Name].["+fbVersion+"]");
            dimension.push("[Time].[Week]");
            dimension.push("[Location].[Location].["+fbLocation+"]");
            dimension.push("[Line].[Line].["+fbLine+"]");

            let measure = [];
            measure.push("Measure.[Line Eff W]");
            measure.push("Measure.[Line Eff W_Oper Plan]");

            let where = "";

            if(!vdCommon.existMeasure(dimension, measure, where)){
                let errorMsg = `This data is not registered in the [Line Efficiency]. `;
                RuleOutputToUI = { Status : 'Error', Message : errorMsg };
                return;
            }
            //+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
            //2025.03.07  사용자 요청으로 To Line 수작업으로 입력한 라인을 member로 등록되도록 처리함.
            //+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
            let memberQuery ='Select ([To Line].[To Line].filter(#.Name == "'+fbToLine+'") * [To Line].[To Line Type].[LCM]);';
            let resultToLine = vdCommon.selectQueryList("fn_existMember(ToLine)", memberQuery);
            vdCommon.printStep("[member Result]" + resultToLine.rowCount);
            if(resultToLine.rowCount == 0){
                let query = 'Createmember ( [To Line].[To Line] = {,"' + fbToLine + '" },  [To Line].[To Line Type] = {, "LCM"} );';
                vdCommon.executeQuery("fn_add(To Line Member Create]", query);
                isToLineUserEntry = "Y";
            }
            //+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

            //Sync Line 체크
            dimension = [];
            dimension.push("[Version].[Version Name].["+fbVersion+"]");
            dimension.push("[Location].[Location].["+fbLocation+"]");
            dimension.push("[To Line].[To Line].["+fbToLine+"]");
            dimension.push("[Line].[Line].["+fbLine+"]");

            measure = [];
            measure.push("Measure.[Sync Line_Enddate]");
            measure.push("Measure.[Sync Line_Flag]");
            measure.push("Measure.[Sync Line_Startdate]");

            ///Sync Line Map Measure 등록
            measureGroup = "Sync Line" ;
            let granularity = [];
            granularity.push("[Version].[Version Name]");
            granularity.push("[Location].[Location]");
            granularity.push("[To Line].[To Line]");
            granularity.push("[Line].[Line]");    

            let granularityValues = [];
            granularityValues.push(fbVersion);
            granularityValues.push(fbLocation);   
            granularityValues.push(fbToLine);
            granularityValues.push(fbLine);   
            
            if(vdCommon.existMeasure(dimension, measure, where)){
                vdCommon.updateMeasure(vdCommon.makeDimension(granularity, granularityValues),
                                    ['Measure.[Sync Line_Enddate] = null ;', 
                                    'Measure.[Sync Line_Startdate] = "'+fbStartWeek+'";',
                                    'Measure.[Sync Line_Flag] = "'+'Y' +'";',
                                    'Measure.[Sync Line_ToLineUserEntry] = "'+isToLineUserEntry +'";',
                                    'Measure.[Sync Line_Updated By] = CurrentUser().[User Name];',
                                    'Measure.[Sync Line_Update Time] = dateadd(Now(),9,"hour");',
                                    ]);
            }else{
                //crate
                vdCommon.createMeasure(vdCommon.makeDimension(granularity, granularityValues),
                                        ['Measure.[Sync Line_Enddate] = null ;', 
                                        'Measure.[Sync Line_Startdate] = "'+fbStartWeek+'";',
                                        'Measure.[Sync Line_Flag] = "'+'Y' +'";',
                                        'Measure.[Sync Line_ToLineUserEntry] = "'+isToLineUserEntry +'";',
                                        'Measure.[Sync Line_Created By] = CurrentUser().[User Name];',
                                        'Measure.[Sync Line_Creation Time] = dateadd(Now(),9,"hour");',
                                        ]);
            }

            vdCommon.printStep(">>>>>>>>>>> Sync Line "+measureGroup +" Data createMeasure"); 
   
            // IBPL에서 파이쎤을 실행하여 Work Calendar Group Data 생성
            // Annaul Plan 평일근무 시간 조회           

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

            vdCommon.debug("Data List["+fbDataList.length+"]");

            for(var k=0; k < fbDataList.length; k++){
                let whereQuery = [];
                whereQuery.push("[Version].[Version Name].["+fbVersion+"]");
                whereQuery.push("[Location].[Location].["+fbDataList[k].Location.Value+"]");
                whereQuery.push("[To Line].[To Line].["+fbDataList[k].ToLine.Value+"]");             
                whereQuery.push("[Line].[Line].["+fbDataList[k].Line.Value+"]");

                vdCommon.deleteMeasure(whereQuery, "Sync Line");
            }

        }catch ( e ) {
            RuleOutputToUI = { Status : 'Error', Message : "Js Logic Error : " + e.message };
            return;
        }  
    }    

    return{
        fn_dataCheck : fn_dataCheck,
        fn_selectLine : fn_selectLine,
        fn_selectToLine : fn_selectToLine,
        fn_selectPeriod : fn_selectPeriod, 
        fn_copy : fn_copy,
        fn_delete : fn_delete
    };		
});