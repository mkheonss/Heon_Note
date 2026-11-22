define('o9.NSCM.JSProductionModel', ['o9/data/query', 'o9/data/cellset', 'o9.NSCM.commonLib'], function(){	
	const programName = "o9.NSCM.JSProductionModel";
    /**
     * 2025.12.16 
     *  (1) fn_apply() 추가함.
     * 
     * 2026.01.06 fn_project() 추가 및 Project Grain 추가 내용 수정
     * 
     **/      

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
            var chkProductGroup = parsedParams.chkProductGroup;
            var chkDefinition = parsedParams.chkDefinition;
            var chkMarketingName = parsedParams.chkMarketingName;                
            let rtnValue = 0;

            if(chkLocation.length > 1 || chkLine.length > 1 || chkProductGroup.length > 1 ||  chkDefinition.length > 1 || chkMarketingName.length > 1){
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
            const vdUtil = new commonLib.VdUtil();
            vdCommon.setLogLevel("Debug");
            vdCommon.printParams(o9Params);

            // 파라메타 가져오기
            let parsedParams = JSON.parse(o9Params); 
            let fbVersion = parsedParams.fbVersion;
            let fbLineType = parsedParams.fbLineType;

            if(fbLineType == undefined){
                fbLineType = "";
            }

            var result = vdCommon.selectList(['[Line].[Line] * [Line].[Line Type]'+vdUtil.fn_filterStr(fbLineType)],
                                             [],
                                             "",
                                             "orderby [Line].[Line].DisplayName",
                                             "");
            vdCommon.printCsData(result, 3);            

            var comboList = vdCommon.fn_makeCombo(result, {DimName : "Line", 
                                                           DimAttbName : "Line", 
                                                           Sort :"DisplayName", 
                                                           existAll : false, 
                                                           isDisplayNameWithCode : false});
            vdCommon.debug("ComboData : " + JSON.stringify(comboList));

            vdCommon.programEnd();

            return comboList;

        }catch ( e ) {
            RuleOutputToUI = { Status : 'Error', Message : "Js Logic Error : " + e.message };
            return;
        }
    }

    function fn_selectInch(o9Params){
        try{
            const commonLib = require('o9.NSCM.commonLib');
            const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
            vdCommon.setLogLevel("Debug");
            vdCommon.printParams(o9Params);

            // 파라메타 가져오기
            let parsedParams = JSON.parse(o9Params); 
            let fbVersion = parsedParams.fbVersion;
            let fbProductGroup = parsedParams.fbProductGroup;

            let query = "";
            if(fbProductGroup == "All"){
                query = '[Item].[Inch].filter(#.Name >= "0" && #.Name <= "999") ' ;
            }else{
                query = '[Item].[Inch].filter(#.Name >= "0" && #.Name <= "999") * [Item].[Product Group].filter(#.Name == "'+fbProductGroup+'")' ;
            }
            var result = vdCommon.selectList([query],
                                             [],
                                             "",
                                             "orderby [Item].[Inch].DisplayName",
                                             "");
            vdCommon.printCsData(result, 3);

            var comboList = vdCommon.fn_makeCombo(result, {DimName : "Item", 
                                                            DimAttbName : "Inch", 
                                                            Sort :"DisplayName", 
                                                            existAll : false, 
                                                            isDisplayNameWithCode : false});
            vdCommon.debug("ComboData : " + JSON.stringify(comboList));

            vdCommon.programEnd();

            if(comboList.length == 0){
                comboList.push({ Name: "-"  , DisplayName: "All" });
            }

            return comboList;           
        
        }catch ( e ) {
            RuleOutputToUI = { Status : 'Error', Message : "Js Logic Error : " + e.message };
            return;
        }
    }

    function fn_updateFlag(o9Params){
        try{
            const commonLib = require('o9.NSCM.commonLib');
            const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
            vdCommon.setLogLevel("Debug");
            vdCommon.printParams(o9Params);

            // 파라메타 가져오기
            let parsedParams = JSON.parse(o9Params); 
            let comboList = [];

            comboList.push({ Name: "Y"  , DisplayName: "Y" });
            comboList.push({ Name: "N"  , DisplayName: "N" });
           
            vdCommon.programEnd();    

            return comboList;           
        
        }catch ( e ) {
            RuleOutputToUI = { Status : 'Error', Message : "Js Logic Error : " + e.message };
            return;
        }
    }   

    function fn_productGroup(o9Params){
        try{
            const commonLib = require('o9.NSCM.commonLib');
            const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
            vdCommon.setLogLevel("Debug");

            // 파라메타 가져오기
            vdCommon.printParams(o9Params);
            let parsedParams = JSON.parse(o9Params); 

            let selectQuery = 'Select ([Item].[Item Stage].[SET] *';
            selectQuery +='[Item].[Product Group].filter(~(#.Name in {"All", "-"}))) on row, () on column ';
            selectQuery +='orderby [Item].[Product Group].DisplayName; ' ;

            let selectResult = vdCommon.selectQueryList("[fn_productGroupCombo]" ,selectQuery );
            var comboList = vdCommon.fn_makeCombo(selectResult, {DimName : "Item", 
                                                            DimAttbName : "Product Group", 
                                                            Sort :"DisplayName", 
                                                            existAll : true, 
                                                            isDisplayNameWithCode : false});
            vdCommon.debug("ComboData : " + JSON.stringify(comboList));
    
            vdCommon.programEnd();

            return comboList;
        }catch ( e ) {
            RuleOutputToUI = { Status : 'Error', Message : "Js Logic Error : " + e.message };
            return;
        }
    }

    function fn_definition(o9Params){
        try{
            const commonLib = require('o9.NSCM.commonLib');
            const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
            vdCommon.setLogLevel("Debug");

            // 파라메타 가져오기
            vdCommon.printParams(o9Params);
            let parsedParams = JSON.parse(o9Params); 
            let fbProductGroup = parsedParams.fbProductGroup;

            let selectQuery = 'Select (';
            selectQuery +='[Item].[Definition].filter(~(#.Name in {"All", "-"}))) on row, () on column ';
            if(fbProductGroup != "All"){
                selectQuery +='Where {[Item].[Product Group].filter(#.Name in {'+fbProductGroup+'})} ';
            }
            selectQuery +='orderby [Item].[Definition].DisplayName; ' ;

            let selectResult = vdCommon.selectQueryList("[fn_definition]" ,selectQuery );
            var comboList = vdCommon.fn_makeCombo(selectResult, {DimName : "Item", 
                                                            DimAttbName : "Definition", 
                                                            Sort :"DisplayName", 
                                                            existAll : true, 
                                                            isDisplayNameWithCode : false});
            vdCommon.debug("ComboData : " + JSON.stringify(comboList));
    
            vdCommon.programEnd();

            return comboList;
        }catch ( e ) {
            RuleOutputToUI = { Status : 'Error', Message : "Js Logic Error : " + e.message };
            return;
        }
    }

    function fn_marketingName(o9Params){
        try{
            const commonLib = require('o9.NSCM.commonLib');
            const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
            vdCommon.setLogLevel("Debug");

            // 파라메타 가져오기
            vdCommon.printParams(o9Params);
            let parsedParams = JSON.parse(o9Params); 
            let fbProductGroup = parsedParams.fbProductGroup;

            let selectQuery = 'Select (';
            selectQuery +='[Item].[Marketing Name].filter(~(#.Name in {"All", "-"}))) on row, () on column ';
            if(fbProductGroup != "All"){
                selectQuery +='Where {[Item].[Product Group].filter(#.Name in {'+fbProductGroup+'})} ';
            }
            selectQuery +='orderby [Item].[Marketing Name].DisplayName; ' ;

            let selectResult = vdCommon.selectQueryList("[fn_definition]" ,selectQuery );
            var comboList = vdCommon.fn_makeCombo(selectResult, {DimName : "Item", 
                                                            DimAttbName : "Marketing Name", 
                                                            Sort :"DisplayName", 
                                                            existAll : true, 
                                                            isDisplayNameWithCode : false});
            vdCommon.debug("ComboData : " + JSON.stringify(comboList));
    
            vdCommon.programEnd();

            return comboList;
        }catch ( e ) {
            RuleOutputToUI = { Status : 'Error', Message : "Js Logic Error : " + e.message };
            return;
        }
    }
    /* 2026.01.06 추가*/
    function fn_project(o9Params){
        try{
            const commonLib = require('o9.NSCM.commonLib');
            const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
            vdCommon.setLogLevel("Debug");

            // 파라메타 가져오기
            vdCommon.printParams(o9Params);
            let parsedParams = JSON.parse(o9Params); 
            let fbMarketingName = parsedParams.fbMarketingName;

            let selectQuery = 'Select (';
            selectQuery +='[Item].[Project].filter(~(#.Name in {"All", "-"}))) on row, () on column ';
            if(fbMarketingName != "All"){
                selectQuery +='Where {[Item].[Marketing Name].filter(#.Name in {'+fbMarketingName+'})} ';
            }
            selectQuery +='orderby [Item].[Project].DisplayName; ' ;

            let selectResult = vdCommon.selectQueryList("[fn_definition]" ,selectQuery );
            var comboList = vdCommon.fn_makeCombo(selectResult, {DimName : "Item", 
                                                            DimAttbName : "Project",
                                                            Sort :"DisplayName", 
                                                            existAll : true, 
                                                            isDisplayNameWithCode : false});
            vdCommon.debug("ComboData : " + JSON.stringify(comboList));
    
            vdCommon.programEnd();

            return comboList;
        }catch ( e ) {
            RuleOutputToUI = { Status : 'Error', Message : "Js Logic Error : " + e.message };
            return;
        }
    }   
    /* 2026.01.06 수정*/
    function fn_copy(o9Params){
        try{
            const commonLib = require('o9.NSCM.commonLib');
            const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
            const vdUtil = new commonLib.VdUtil();
            vdCommon.setLogLevel("Debug");
            vdCommon.printParams(o9Params);

            // 파라메타 가져오기
            let parsedParams = JSON.parse(o9Params); 
            let fbVersion = parsedParams.fbVersion;
            let fbLocation = parsedParams.fbLocation;
            let fbLine = parsedParams.fbLine;
            let fbProductGroup = parsedParams.fbProductGroup;
            let fbDefinition = parsedParams.fbDefinition;
            let fbMarketingName = parsedParams.fbMarketingName;
            let fbFromInch = parsedParams.fbFromInch;
            let fbToInch = parsedParams.fbToInch;
            let fbTactTime = parsedParams.fbTactTime;
            let fbProject = parsedParams.fbProject;
            let fbUpdateFlag = parsedParams.fbUpdateFlag;

            let dimension = [];
            dimension.push("[Version].[Version Name].["+fbVersion+"]");
            dimension.push("[Time].[Week]");
            dimension.push("[Location].[Location].["+fbLocation+"]");
            dimension.push("[Line].[Line].["+fbLine+"]");

            let measure = [];
            measure.push("Measure.[Line Eff W]");
            measure.push("Measure.[Line Eff W_Oper Plan]");

            let where = "";
            //let rtnValue = vdCommon.existMeasure(dimension, measure, where) ;
           // vdCommon.debug("[Select Line Eff. Count]" + rtnValue);

            if(!vdCommon.existMeasure(dimension, measure, where)){
                vdCommon.debug("[Check false]");
                let errorMsg = `This data is not registered in the [Line Efficiency]. `;
                RuleOutputToUI = { Status : 'Error', Message : errorMsg };
                return;
            }
            vdCommon.debug("Sequence 구하기");
            //Sequence 구하기
            let query = 'Select ( ';
            query += ' [Version].[Version Name].['+fbVersion+']';        
            query += ' * &NSUISiteGrp1MFView'+vdUtil.fn_filterStr(fbLocation) ;
            query += ' * [Line].[Line]'+vdUtil.fn_filterStr(fbLine) ;      
            query += ' * [Sequence].[Sequence] ';
            query += ' * [Definition].[Definition]'+vdUtil.fn_filterStr(fbDefinition) ;
            query += ' * [Item].[Marketing Name]'+vdUtil.fn_filterStr(fbMarketingName) ;
            query += ' * [Product].[Product Group]'+vdUtil.fn_filterStr(fbProductGroup) ;
            query += ' * [Project].[Project]'+vdUtil.fn_filterStr(fbProject) ;
            query += ' ) on row, ';
            query += ' ({Measure.[Prod Model_From Inch], Measure.[Prod Model_Line Priority]';
            query += ' , Measure.[Prod Model_Tact Time], Measure.[Prod Model_To Inch]}) on column ';
            query += 'orderby [Sequence].[Sequence].Name asc;';

            let lsResult = vdCommon.selectQueryList("[fn_add(Sequence-Select)]", query);

            let sequenceMax = 0;

            if(lsResult.rowCount > 0){
                const data = lsResult.cs.row(0).cell(lsResult.cs.memberColumnIndex("Sequence", "Sequence")).Name;
                sequenceMax = parseInt(data) + 1;
                vdCommon.printStep("selectList Value [:] " + data + "]["+typeof data +"]["+sequenceMax+"]"); 
            }else{
                sequenceMax = sequenceMax + 1 ;
            }
            vdCommon.printStep("Sequence ::" + sequenceMax);

            //Line Grp Map Measure 등록
            measureGroup = "Product Model" ;
            let granularity = [];
            granularity.push("[Version].[Version Name]");
            granularity.push("[Location].[Location]");
            granularity.push("[Line].[Line]");        
            granularity.push("[Sequence].[Sequence]");
            granularity.push("[Definition].[Definition]");
            granularity.push("[Item].[Marketing Name]");
            granularity.push("[Product].[Product Group]");
            granularity.push("[Project].[Project]");

            let granularityValues = [];
            granularityValues.push(fbVersion);
            granularityValues.push(fbLocation);   
            granularityValues.push(fbLine);             
            granularityValues.push(sequenceMax);
            granularityValues.push(fbDefinition);
            granularityValues.push(fbMarketingName);
            granularityValues.push(fbProductGroup);
            granularityValues.push(fbProject);

            vdCommon.createMeasure(vdCommon.makeDimension(granularity, granularityValues),
                                ['Measure.[Prod Model_From Inch] = if("'+fbFromInch +'" == "-")then null else "'+fbFromInch+'";',    
                                'Measure.[Prod Model_To Inch] = if("'+fbToInch +'" == "-")then null else "'+fbToInch+'";',
                                'Measure.[Prod Model_Tact Time] = "'+fbTactTime+'";',
                                'Measure.[Prod Model_Tact Time Update] = "'+fbUpdateFlag+'";',
                                'Measure.[Prod Model_From Inch Actual] = if("'+fbFromInch +'" == "-")then null else "'+fbFromInch+'";',  
                                'Measure.[Prod Model_To Inch Actual] = if("'+fbToInch +'" == "-")then null else "'+fbToInch+'";',
                                'Measure.[Prod Model_Tact Time Actual] = "'+fbTactTime+'";'
                                ]);
            vdCommon.printStep(">>>>>>>>>>>Product Model:: "+measureGroup +" Data createMeasure");        
            // IBPL에서 파이쎤을 실행하여 Work Calendar Group Data 생성
            vdCommon.printStep(">>>>>>>>>>> fn_Submit End");		
            vdCommon.programEnd(); 
        }catch ( e ) {
            RuleOutputToUI = { Status : 'Error', Message : "Js Logic Error : " + e.message };
            return;
        }
    }
    
    /* 
     2026.01.06 수정 : Proejct 관련 부분 수정
     2026.02.04 삭제시 Project 멤버에 들어온 특수 기호(쌍따옴표) 처리
    */
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
                whereQuery.push("[Item].[Marketing Name].["+fbDataList[k].MarketingName.Value+"]");
                whereQuery.push("[Location].[Location].["+fbDataList[k].Location.Value+"]");
                whereQuery.push("[Sequence].[Sequence].["+fbDataList[k].Sequence.Value+"]");               
                whereQuery.push("[Definition].[Definition].["+fbDataList[k].Definition.Value+"]");              
                whereQuery.push("[Product].[Product Group].["+fbDataList[k].ProductGroup.Value+"]");
                let fbProject = fbDataList[k].Project.Value;
                //sData.replace(/%/g, "")
                whereQuery.push("[Project].[Project].["+fbProject.replace(/"/g, '\\"')+"]");
                whereQuery.push("[Line].[Line].["+fbDataList[k].Line.Value+"]");

                vdCommon.deleteMeasure(whereQuery, "Product Model");
            }

        }catch ( e ) {
            RuleOutputToUI = { Status : 'Error', Message : "Js Logic Error : " + e.message };
            return;
        }  
    }
    /* 2025.12.16
        엔진 결과 값 (Production Result) 을 T/T update flag가 Y인 항목들에 대해서만 MP내 값들에 업데이트   
    */
    function fn_apply(o9Params){
        try{
            const commonLib = require('o9.NSCM.commonLib');
            const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
            const vdUtil = new commonLib.VdUtil();
            vdCommon.setLogLevel("Debug");
            vdCommon.printParams(o9Params);

            let parsedParams = JSON.parse(o9Params); 
            let fbVersion = parsedParams.fbVersion;
            let fbLocation = parsedParams.fbFromSite;

            let dimension = [];
            let measure = [];
            vdCommon.debug("[Product Model] fn_apply 시작");
            dimension.push("[Version].[Version Name].["+fbVersion+"]");
            dimension.push("[Location].[Site Group3]"+vdUtil.fn_filterStr(fbLocation) + ".relatedmembers([Location])");
            dimension.push("[Item].[Marketing Name]");
            dimension.push("[Sequence].[Sequence]");
            dimension.push("[Project].[Project]");
            dimension.push("[Definition].[Definition]");
            dimension.push("[Product].[Product Group]");
            dimension.push("[Line].[Line]");

            measure.push('Measure.[Prod Model_From Inch] = if(Measure.[Prod Model_Tact Time Update] == "Y") then Measure.[Prod Model_From Inch Actual] else Measure.[Prod Model_From Inch];');
            measure.push('Measure.[Prod Model_To Inch] = if(Measure.[Prod Model_Tact Time Update] == "Y") then Measure.[Prod Model_To Inch Actual] else Measure.[Prod Model_To Inch];');
            measure.push('Measure.[Prod Model_Tact Time] = if(Measure.[Prod Model_Tact Time Update] == "Y") then Measure.[Prod Model_Tact Time Actual] else Measure.[Prod Model_Tact Time];');

            vdCommon.updateMeasure(dimension, measure);
            vdCommon.programEnd();
            
        }catch ( e ) {
            RuleOutputToUI = { Status : 'Error', Message : "Js Logic Error : " + e.message };
            return;
        }
    }
    return{
        fn_copy : fn_copy,
        fn_delete : fn_delete,
        fn_dataCheck : fn_dataCheck,
        fn_productGroup : fn_productGroup,
        fn_definition : fn_definition,
        fn_marketingName : fn_marketingName,
        fn_project : fn_project,
        fn_selectLine : fn_selectLine,
        fn_selectInch : fn_selectInch,
        fn_updateFlag : fn_updateFlag,
        fn_apply: fn_apply
    };		
});