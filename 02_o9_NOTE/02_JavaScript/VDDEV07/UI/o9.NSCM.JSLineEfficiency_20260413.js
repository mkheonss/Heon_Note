define('o9.NSCM.JSLineEfficiency', ['o9/data/query', 'o9/data/cellset', 'o9.NSCM.commonLib'], function(){	
	const programName = "o9.NSCM.JSLineEfficiency";
    /**
     * 2025.12.16 
     *  (1) Work Cal Line 처리 IBPL 수정함.
     *      MG[Work Cal Line] ]Work Type].[Work Type], [Data Set].[Data Set] Grain 삭제됨.
     *      Measure.[Work Cal Line_Capa Short Criteria] = "O/T" ; 디폴트 값 처리함.
     *      
     *  (2) fn_change_PreSOP() 함수 추가
     *      ABLineEfficiencyPreSOPEdit 데이타 처리 추가함. (0 ~ 20 범위 체크 로직 추가함.)
     * 
     * 2026.02.04
     *  저장시 Product Model 메저그룹에 [Project] 디멘젼 추가 및 메져 추가 (Measure.[Prod Model_Tact Time Update] = "N")
     **/

    function fn_selectLocation(o9Params){
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

    function fn_selectLineType(o9Params){
        try{
            const commonLib = require('o9.NSCM.commonLib');
            const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
            vdCommon.setLogLevel("Debug");
            vdCommon.printParams(o9Params);

            // 파라메타 가져오기
            let parsedParams = JSON.parse(o9Params); 
            let fbVersion = parsedParams.fbVersion;
            let fbLineType = parsedParams.fbLineType;      

            let result = vdCommon.selectList(['[Line].[Line Type].filter(#.Name in {"MAIN"})'], 
                                            []
                                            ,"","","");

            vdCommon.printCsData(result, 3);

            let comboList = vdCommon.fn_makeCombo(result, {DimName : "Line",DimAttbName : "Line Type", Sort :"DisplayName", existAll : false, isDisplayNameWithCode : false});
            vdCommon.debug("ComboData : " + JSON.stringify(comboList));
                        
            vdCommon.programEnd();

            return comboList;
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
            let fbLocation = parsedParams.fbLocation;
            let fbLineType = parsedParams.fbLineType;            
           
            //query 정의
            //25.04.01 Tact Time에서 Line 코드 조회
            let whereQuery = 'Where {[Version].[Version Name].['+fbVersion+']';
            whereQuery += ',[Location].[Location].filter(#.Name in {"'+fbLocation+'"})';
            whereQuery += ',[Line].[Line Type].['+fbLineType+']';
            whereQuery += ',[Item].[Item], Measure.[Tact Time_Valid Asn] == true';
            whereQuery += '}';

            let result = vdCommon.selectList(["[Line].[Line]"],["Measure.[Tact Time_Valid Asn]"],
                                            whereQuery,
                                            "orderby [Line].[Line].Name","");
            vdCommon.printCsData(result, 3);

            let comboList = vdCommon.fn_makeCombo(result, {DimName : "Line",DimAttbName : "Line", Sort :"DisplayName", existAll : false, isDisplayNameWithCode : false});
            vdCommon.debug("ComboData : " + JSON.stringify(comboList));
            vdCommon.programEnd();
    
            return comboList;            
        }catch ( e ) {
            RuleOutputToUI = { Status : 'Error', Message : "Js Logic Error : " + e.message };
            return;
        }
    }

	function fn_add(o9Params){
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
            let fbTime = parsedParams.fbTime;
            
            let query = '';
            let returValue = true ;
            let measureGroup ="";
            let isUserEntry = "N";

            //#################################################################
            //Tiem Week 조회
            //#################################################################
            let selectWeekQuery = "select (&CurrentPlanningYear.relatedmembers([Week]).unionwith (&NextPlanningYear.relatedmembers([Week])));";
            let resultWeek = vdCommon.selectQueryList("fn_add_weekList", selectWeekQuery);
            let weekCombo = vdCommon.fn_makeCombo(resultWeek, {DimName : "Time",DimAttbName : "Week", Sort :"DisplayName", existAll : false, isDisplayNameWithCode : false});
            let fbWeekList = weekCombo.map((value) => value.Name);
            vdCommon.debug("[Week List]" + JSON.stringify(fbWeekList));

            //#################################################################
            // LineEfficiency 처리
            //#################################################################
            //Line Member 체크
            var memberSql = "[Line].[Line] ";
            if(!vdCommon.existMember(memberSql,fbLine)){
                let query = 'Createmember ( [Line].[Line] = {,"' + fbLine + '" }, [Line].[Line Type] = {, "MAIN"} );';
                vdCommon.executeQuery("fn_add(Line Member Create]", query);
                isUserEntry = "Y";
            }

            measureGroup = "Line Efficiency W" ;
            // 팝업에서 입력 받은 Location, Line Type, Line 등록 여부를 체크함.
            //query = `select (&${fbTime}`
            query = `select( [Time].[Week]` + vdUtil.fn_filterStr(fbWeekList)
            query += ` * [Location].[Location].filter(#.Name == "${fbLocation}") * [Line].[Line].filter(#.Name == "${fbLine}")) on row,`
            query += `({Measure.[Line Eff W], Measure.[Line Eff W_Oper Plan]}) on column `
            query += `where { Version.[Version Name].filter(#.Name == "${fbVersion}")}; `;

            vdCommon.debug("SQL>>"+query);	
            vdCommon.debug("fn_Submit > select query : " + query);
            //let selectResult = cellsetModule.createCellSet(queryModule.select(query));
            //let selectResultCount = selectResult.rowCount;
            let result = vdCommon.selectQueryList("fn_add_LineEfficiency", query);

            if(result.rowCount > 0){
                //데이타 삭제
                //deleteMeasure(where, measureGroup) 
                query = ['Version.[Version Name].filter(#.Name =="'+fbVersion+'")'
                        //,'&'+fbTime
                        ,'[Time].[Week]' + vdUtil.fn_filterStr(fbWeekList)
                        ,'[Location].[Location].filter(#.Name in {"'+fbLocation+'"})'
                        ,'[Line].[Line].filter(#.Name in {"'+fbLine+'"})'];

                vdCommon.debug("["+measureGroup+"] Delete Where SQL>>"+query);
                var tempquery = 'delete data for model [' + measureGroup + '] where {' + query.join(",") + '};';
                vdCommon.debug("["+measureGroup+"] Delete SQL>>"+tempquery);
                
                vdCommon.deleteMeasure(query, measureGroup);
                
            }
            vdCommon.debug("[Log(Line Eff W)]");
            //데이타 생성 (Next52Weeks 기간만큼 생성) 필터 Time 조건 체크
            let createDimension = [];
            let createMeasure = [];

            createDimension.push("[Version].[Version Name].["+fbVersion+"]");
            //createDimension.push("&"+fbTime);
            createDimension.push("[Time].[Week]"+vdUtil.fn_filterStr(fbWeekList));
            createDimension.push("[Location].[Location].["+fbLocation+"]");
            createDimension.push("[Line].[Line].["+fbLine+"]");

            createMeasure.push('Measure.[Line Eff W] = 100;'); 
            createMeasure.push('Measure.[Line Eff W_Oper Plan] = "Y";'); 
            createMeasure.push('Measure.[Line Eff W_Created By] = CurrentUser().[User Name];'); 
            createMeasure.push('Measure.[Line Eff W_Creation Time] = Now();'); 

            vdCommon.createMeasure(createDimension, createMeasure);

            vdCommon.debug("[Log(Line Eff Sub)]");
            //Line Eff Sub 메져 등록
            let createQuery = "cartesian scope:([Version].[Version Name].["+fbVersion+"] * [Location].[Location].["+fbLocation+"] * [Line].[Line].["+fbLine+"]);";
            createQuery += "Measure.[Line Eff Sub_IsUserEntry] = " + '"'+isUserEntry + '";';
            createQuery += "Measure.[Line Eff Sub_IsValid] = " + '"Y";';
            createQuery += "Measure.[Line Eff Sub_Created By] = CurrentUser().[User Name];";
            createQuery += 'Measure.[Line Eff Sub_Creation Time] = Now();'
            createQuery += "end scope;";
            vdCommon.executeQuery("fn_add(Line Member Create]", createQuery);

            let granularity = [];
            let granularityValues = [];
            //#################################################################
            // Product Model Measure 등록
            //#################################################################
            vdCommon.debug("[Log(Prod Model)]");
            measureGroup = "Product Model" ;
            granularity = [];
            granularity.push("[Version].[Version Name]");
            granularity.push("[Location].[Location]");
            granularity.push("[Line].[Line]");        
            granularity.push("[Sequence].[Sequence]");
            granularity.push("[Definition].[Definition]");
            granularity.push("[Item].[Marketing Name]");
            granularity.push("[Product].[Product Group]");
            granularity.push("[Project].[Project]");  //2026.02.04 디멘젼 추가 

            granularityValues = [];
            granularityValues.push(fbVersion);
            granularityValues.push(fbLocation);   
            granularityValues.push(fbLine);             
            granularityValues.push(1);
            granularityValues.push("All");
            granularityValues.push("All");
            granularityValues.push("All");
            granularityValues.push("All");  //2026.02.04 디멘젼 추가 

            vdCommon.createMeasure(vdCommon.makeDimension(granularity, granularityValues),
                                ['Measure.[Prod Model_From Inch] = 0;',                                
                                'Measure.[Prod Model_Line Priority] = 0;',
                                'Measure.[Prod Model_Tact Time] = null;',
                                'Measure.[Prod Model_To Inch] = 0;',
                                'Measure.[Prod Model_Tact Time Update] = "N";'  //2026.02.04 메져 추가
                                ]);

            //#################################################################
            // Sync Line Measure 등록(?)
            //#################################################################
            vdCommon.debug("[Log(Sync Line)]");
            measureGroup = "Sync Line" ;
            granularity = [];
            granularity.push("[Version].[Version Name]");
            granularity.push("[Location].[Location]");
            granularity.push("[To Line].[To Line]");             
            granularity.push("[Line].[Line]");        

            granularityValues = [];
            granularityValues.push(fbVersion);
            granularityValues.push(fbLocation);  
            granularityValues.push("-");              
            granularityValues.push(fbLine);  
            
            vdCommon.createMeasure(vdCommon.makeDimension(granularity, granularityValues),
                                ['Measure.[Sync Line_Flag] = "Y";',                                
                                'Measure.[Sync Line_ToLineUserEntry] = "N";', 
                                'Measure.[Sync Line_Startdate] = null;',
                                'Measure.[Sync Line_Enddate] = null;',
                                'Measure.[Sync Line_Created By] = CurrentUser().[User Name];',
                                'Measure.[Sync Line_Creation Time] = Now();'
                                ]);
  
            //#################################################################
            // Line Grp Map Measure 등록
            // 2025.03.07 
            // Line Group Mapping 화면에서 다시 Group ID를 매핑하는 것이 귀찮다고 하여 
            // Line Efficiency 화면에서 매핑할 Group ID를 선택할 수 있도록 수정함.
            // 미선택시은 '-'으로 처리함.
            //#################################################################
            let fbGroupID = parsedParams.fbGroupID;

            if(fbGroupID == null) fbGroupID = "-" ;

            measureGroup = "Line Grp Map" ;
            vdCommon.debug("[Log(Line Grp Map)]");
            vdCommon.createMeasure(["[Version].[Version Name].["+fbVersion+"]",
                                    "[Location].[Location].["+fbLocation+"]",
                                    "[Group].[Group ID]"+vdUtil.fn_filterStr(fbGroupID),  
                                    "[Line].[Line].["+fbLine+"]"                                  
                                    ],
                                    ['Measure.[Line Grp Map_Enddate] = null ;', 
                                    'Measure.[Line Grp Map_Startdate] = null;',
                                    'Measure.[Line Grp Map_Flag] = "'+'N' +'";',
                                    ]);
            vdCommon.debug(">>>>>>>>>>>  "+measureGroup +" Data createMeasure");

            //#################################################################
            // Work Annual Plan 처리
            //#################################################################
            // Work Calendar 관련 부분 데이타 반영
            const WORK_MINS_PER_DAY = 480;
            const OFF_TIME_MINS = 60;

            //Working Hrs Annual Measrue  데이타 확인
            vdCommon.debug("[Log(Work Hrs Annual(1))]");
            measureGroup = "Work Hrs Annual" ;            
            let query02 = `Select ([Version].[Version Name].filter(#.Name == "`+ fbVersion +`") *` +
                    ` [Location].[Location].filter(#.Name == "`+ fbLocation +`") ) on row,  ` +
                    `({Measure.[Work Hrs Annual_Off Time Mins]` +
                    ` ,Measure.[Work Hrs Annual_Total Work Mins Per Day w/ Off Time]` +
                    ` ,Measure.[Work Hrs Annual_Work Hrs Per Day]` +
                    ` ,Measure.[Work Hrs Annual_Work Mins Per Day]}) on column ;` ;

            let queryResult = vdCommon.selectQueryList("fn_add(WorkAnnualPlan)", query02);

            if(queryResult.rowCount == 0){
                vdCommon.debug("[Log(Work Hrs Annual)]");
                //건수가 없는 경우 Measure 등록함.
                granularity = [];                
                granularity.push("[Version].[Version Name]");
                granularity.push("[Location].[Location]");
    
                granularityValues = [];
                granularityValues.push(fbVersion);
                granularityValues.push(fbLocation);                
            
                vdCommon.createMeasure(vdCommon.makeDimension(granularity, granularityValues),
                                     ['Measure.[Work Hrs Annual_Off Time Mins] = '+OFF_TIME_MINS+';', 
                                     'Measure.[Work Hrs Annual_Total Work Mins Per Day w/ Off Time] = '+WORK_MINS_PER_DAY +';',
                                     //Reporting measure 변경되어 할당할 필요가 없음.
                                     //'Measure.[Work Hrs Annual_Work Hrs Per Day] = '+((WORK_MINS_PER_DAY - OFF_TIME_MINS) / OFF_TIME_MINS) +';',
                                     //'Measure.[Work Hrs Annual_Work Mins Per Day] = '+  WORK_MINS_PER_DAY +';',
                                   ]);
                vdCommon.debug(">>>>>>>>>>>  "+measureGroup +" Data createMeasure");
            }

            //Working Cal. Annual Measrue  데이타를 확인한다.
            vdCommon.debug("[Log(Work Cal Annual)]");
            measureGroup = "Work Cal Annual" ;
            //생성 전에 삭제함
            query02 = ['Version.[Version Name].filter(#.Name =="'+fbVersion+'")'
                    //,' &'+fbTime
                    ,"[Time].[Week]"+vdUtil.fn_filterStr(fbWeekList)
                    ,'[Location].[Location].filter(#.Name in {"'+fbLocation+'"})'];

            vdCommon.debug("["+measureGroup+"] Delete Where SQL>>"+query02);
            
            vdCommon.deleteMeasure( query02, measureGroup);

            vdCommon.debug(">>>>>>>>>>>  Work Cal Annual Data Delete");

            //Work Cal. Annual Measure 데이타 생성
            // 2025.02.26 박병훈 부장님 파이썬으로 수정함.
            query02 = `EXEC plugin instance [PY_UI_WorkCalAnnual] for measures {[Work Cal Annual_Lock Flag]} ` +
                    `using scope ( Version.[Version Name].filter(#.Name == "`+fbVersion+`") * ` +
                    //` &`+fbTime +
                    '[Time].[Week]' + vdUtil.fn_filterStr(fbWeekList) +
                    ` * [Location].[Location].filter(#.Name == "`+fbLocation+`") ) ` +
                    ` using arguments {(ExecutionMode, "MediumWeight"), (MaxSliceTableCells, 200000000), (MaxConcurrency, 1 ), ([Param.o9_sys_log_level],"DEBUG")}; `;

            vdCommon.executeQuery("PY_UI_WorkCalAnnual ", query02);

            //Work Cal Line, Work Cal LineGrp 메져 등록  => Weekly Plan 화면 조회
            // 25.04.28 [O/T Hour]Type으로 변경하고 Deault Time 14로 처라힘.
            vdCommon.debug("[Log(Work Cal Line (caresian))]");
            let createWorkCalLine = "";
            createWorkCalLine += "cartesian scope:([Version].[Version Name].["+fbVersion+"] * [Location].[Location].["+fbLocation+"] * "; 
            createWorkCalLine += "[Time].[Week]" + vdUtil.fn_filterStr(fbWeekList);
            createWorkCalLine += " * [Line].[Line].["+fbLine+"]);";
            createWorkCalLine += "Measure.[Work Cal Line_Time] = 14;";
            createWorkCalLine += 'Measure.[Work Cal Line_Capa Short Criteria] = "O/T";'; //25.12.16 수정함.
            createWorkCalLine += "end scope;";

            vdCommon.executeQuery("[Work Cal Line Create] ", createWorkCalLine);

            vdCommon.debug(">>>>>>>>>>> fn_add End");		
            vdCommon.programEnd();            
  
        }catch ( e ) {
            RuleOutputToUI = { Status : 'Error', Message : "Js Logic Error : " + e.message };
            return;
        }
	}

    //Update
    function fn_selectUpdateLocation(o9Params){
        try{
            const commonLib = require('o9.NSCM.commonLib');
            const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
            vdCommon.setLogLevel("Debug");
            vdCommon.printParams(o9Params);
    
            // 파라메타 가져오기
            let parsedParams = JSON.parse(o9Params); 
            let fbVersion = parsedParams.fbVersion;
            let fbTime = parsedParams.fbTime;
            let fbLocation = parsedParams.fbLocation;

            let where = "Where {";
            where += "[Version].[Version Name].["+fbVersion+"]"
            where += " ,[Time].[Week]";
            where += ", [Line].[Line]";
            where += " ,Measure.[Line Eff W] >= 0" ;
            where += "}"
           
            //query 정의
            let result = vdCommon.selectList(["[Location].[Location]"], 
                                            ["Measure.[Line Eff W]","Measure.[Dummy]"]
                                            ,where
                                            ,"orderby [Location].[Location].DisplayName","");
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
    function fn_selectUpdateLine(o9Params){
        try{
            const commonLib = require('o9.NSCM.commonLib');
            const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
            vdCommon.setLogLevel("Debug");
            vdCommon.printParams(o9Params);
    
            // 파라메타 가져오기
            let parsedParams = JSON.parse(o9Params); 
            let fbVersion = parsedParams.fbVersion;
            let fbTime = parsedParams.fbTime;
            let fbLocation = parsedParams.fbLocation;

            let where = "Where {";
            where += "[Version].[Version Name].["+fbVersion+"]"
            //where += " ,&"+fbTime;
            where += " ,[Time].[Week]";
            where += " ,[Location].[Location].["+fbLocation+"]" ;
            where += " ,Measure.[Line Eff W] >= 0" ;
            where += "}"
           
            //query 정의
            let result = vdCommon.selectList(["[Line].[Line]"], 
                                            ["Measure.[Line Eff W]","Measure.[Dummy]"]
                                            ,where
                                            ,"orderby [Line].[Line].DisplayName","");
            vdCommon.printCsData(result, 3);

            let comboList = vdCommon.fn_makeCombo(result, {DimName : "Line",DimAttbName : "Line", Sort :"DisplayName", existAll : false, isDisplayNameWithCode : false});
            vdCommon.debug("ComboData : " + JSON.stringify(comboList));
            vdCommon.programEnd();
    
            return comboList;            
        }catch ( e ) {
            RuleOutputToUI = { Status : 'Error', Message : "Js Logic Error : " + e.message };
            return;
        }
    }

    function fn_validFlag(o9Params){
        try{
            const commonLib = require('o9.NSCM.commonLib');
            const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
            vdCommon.setLogLevel("Debug");

            let comboList = [];
            comboList.push({ Name: "Y", DisplayName: "Y" });
            comboList.push({ Name: "N", DisplayName: "N" });
    
            vdCommon.debug(">>>>>>>>>>> fn_validFlag End");		
            vdCommon.programEnd(); 
            return comboList;
        } catch ( e ) {
            RuleOutputToUI = { Status : 'Error', Message : "Js Logic Error : " + e.message };
            return;
        }

    }     

    function fn_update(o9Params){
        try{
            const commonLib = require('o9.NSCM.commonLib');
            const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
            const vdUtil = new commonLib.VdUtil();
            vdCommon.setLogLevel("Debug");
            vdCommon.printParams(o9Params);
    
            // 파라메타 가져오기
            let parsedParams = JSON.parse(o9Params); 
            let fbVersion = parsedParams.fbVersion;
            let fbTime = parsedParams.fbTime;
            let fbLocation = parsedParams.fbLocation;
            let fbLine = parsedParams.fbLine;
            let fbValid = parsedParams.fbValid;

            //create, update을 분리함.
            
            //let select = vdCommon.selectList()
            let dimension = ["[Version].[Version Name].["+fbVersion+"]",
                            "[Location].[Location].["+fbLocation+"]",
                            "[Line].[Line]" + vdUtil.fn_filterStr(fbLine)
                            ];

            vdCommon.deleteMeasure(dimension, "Line Efficiency Sub") ;

            let measure = ["Measure.[Line Eff Sub_IsValid] =" +'"'+fbValid+'";' ,
                            "Measure.[Line Eff Sub_Updated By] = CurrentUser().[User Name];",
                            'Measure.[Line Eff Sub_Update Time] = Now();'
                          ];            

            //vdCommon.updateMeasure(dimension, measure)
            vdCommon.createMeasure(dimension, measure);

            // 25.04.07 Line에 대한 Y/N 설정에 따라 Work Cal Line 정보 변경함.
            //Work Cal Line 데이타 삭제
            let deleteWhere = [];
            deleteWhere.push('[Version].[Version Name].['+fbVersion+']');
            deleteWhere.push('[Location].[Location].['+fbLocation+']');
            deleteWhere.push('&'+fbTime);
            deleteWhere.push('[Line].[Line]' + vdUtil.fn_filterStr(fbLine));

            vdCommon.deleteMeasure(deleteWhere, "Work Cal Line");   

            if(fbValid == "Y"){
                //Work Cal Line, Work Cal LineGrp 메져 등록  => Weekly Plan 화면 조회
                // 25.04.28 [O/T Hour]Type으로 변경하고 Deault Time 14로 처라힘.
                let createWorkCalLine = "cartesian scope:([Version].[Version Name].["+fbVersion+"] * [Location].[Location].["+fbLocation+"] * "; 
                createWorkCalLine += "&"+fbTime+" * [Line].[Line]"+ vdUtil.fn_filterStr(fbLine) +" );";
                createWorkCalLine += "Measure.[Work Cal Line_Time] = 14;";
                createWorkCalLine += 'Measure.[Work Cal Line_Capa Short Criteria] = "O/T";'; //25.12.16 수정함.;
                createWorkCalLine += "end scope;";

                vdCommon.executeQuery("[Work Cal Line Create] ", createWorkCalLine);             
            }

        }catch ( e ) {
            RuleOutputToUI = { Status : 'Error', Message : "Js Logic Error : " + e.message };
            return;
        }
    }

    function fn_change_PreSOP(o9Params){
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
            let fbPreSOP = parsedParams.fbPreSOP;
            let rtnValue = 0;
            vdCommon.debug("[Value]["+fbPreSOP+"]["+ parseFloat(fbPreSOP) + "]");
            if(fbPreSOP >= 0 && fbPreSOP <= 20){
                vdCommon.debug("Update...")
                let dimension = ["[Version].[Version Name].["+fbVersion+"]",
                                "[Location].[Location]" + vdUtil.fn_filterStr(fbLocation),
                                "[Line].[Line]" + vdUtil.fn_filterStr(fbLine)
                                ];

                let measure = ["Measure.[Line Eff Sub_Pre SOP(%)] =" +'"'+fbPreSOP+'";' ,
                                "Measure.[Line Eff Sub_Updated By] = CurrentUser().[User Name];",
                                'Measure.[Line Eff Sub_Update Time] = Now();'
                            ];            

                vdCommon.updateMeasure(dimension, measure)
            }else{
                vdCommon.debug("Error")
                rtnValue = 1;
                RuleOutputToUI = { Status : 'Error', Message : "[Error]The input range is 0 to 20." };  
            }
            vdCommon.programEnd();
            return rtnValue;

        }catch ( e ) {
            RuleOutputToUI = { Status : 'Error', Message : "Js Logic Error : " + e.message };
            return;
        }
    }

    return{
        fn_selectLocation : fn_selectLocation,
        fn_selectLineType : fn_selectLineType,
        fn_selectLine  : fn_selectLine,
        fn_add : fn_add,
        fn_selectUpdateLocation : fn_selectUpdateLocation,
        fn_selectUpdateLine : fn_selectUpdateLine,
        fn_validFlag : fn_validFlag,
        fn_update : fn_update,
        fn_change_PreSOP:fn_change_PreSOP
    };		
});