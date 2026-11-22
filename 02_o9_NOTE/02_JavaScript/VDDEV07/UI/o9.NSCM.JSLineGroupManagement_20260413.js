define('o9.NSCM.JSLineGroupManagement', ['o9/data/query', 'o9/data/cellset', 'o9.NSCM.commonLib'], function(){
	const programName = "o9.NSCM.JSLineGroupManagement";  
    const timeWeekNameSet = "&MDMHorizon"; 
    const next52Weeks = "&Next52Weeks"; 

    function fn_time(selectType, rtnType){
        try{
            const commonLib = require('o9.NSCM.commonLib');
            const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
            vdCommon.setLogLevel("Debug");

            let retunData = '';            
            let selectQuery = '';

            if(rtnType == "STARTWEEK"){
                selectQuery = 'Select ('+selectType+'.first()) ;';
            }else{
                selectQuery = 'Select ('+selectType+'.last()) ;';
            }

            let lsResult = vdCommon.selectQueryList("fn_time", selectQuery);

            if(lsResult.rowCount > 0){
                retunData = lsResult.cs.row(0).cell(lsResult.cs.memberColumnIndex("Time", "Week")).Name;
            }

            vdCommon.printStep("fn_time() Return Week : " + retunData);

            return retunData;
        }catch ( e ) {
            RuleOutputToUI = { Status : 'Error', Message : "Js Logic Error : " + e.message };
            return;
        }        
    };
    
    function fn_dataReload(o9Params){
        try{
            const commonLib = require('o9.NSCM.commonLib');
            const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
            const vdUtil = new commonLib.VdUtil();
            vdCommon.setLogLevel("Debug");
            vdCommon.printParams(o9Params);

            // 파라미터 가져오기
            let parsedParams = JSON.parse(o9Params);	
            let fbVersion = parsedParams.fbVersion;
            let startWeek = fn_time(timeWeekNameSet, "STARTWEEK");
            let lastWeek = fn_time(timeWeekNameSet, "LASTWEEK");
            //vdCommon.printStep("["+startWeek+"]["+lastWeek+"]");
        
            let selectLineGroupManagOrg = "Select (&CWVUI * [Location].[Location] * &Next52Weeks * [Group].[Group ID] ) on row, "
            selectLineGroupManagOrg += "({Measure.[Line Grp_Line Cnt], Measure.[Line Grp_Line Oper Cnt]}) on column ";
            selectLineGroupManagOrg += " Where {Measure.[Line Grp_Line Oper Cnt] > 0} ;";
            
            let resultOrgData = vdCommon.selectQueryList("fn_dataReload(Line Group Manage. Org)", selectLineGroupManagOrg);


            let selectLineGroupMapping = 'Select ([Version].[Version Name].['+fbVersion+']';
            selectLineGroupMapping += ' * [Location].[Location]';
            selectLineGroupMapping += ' * [Group].[Group ID]';
            selectLineGroupMapping += ' * [Line].[Line]' ;  
            selectLineGroupMapping += ') on row, '         
            selectLineGroupMapping += '({Measure.[Line Grp Map_Enddate], Measure.[Line Grp Map_Flag], Measure.[Line Grp Map_Startdate]}) on column '
            selectLineGroupMapping += 'Where {Measure.[Line Grp Map_Startdate] <= '+lastWeek+', association(Measure.[Line Eff Sub_IsValid] == "Y")} ' 
            selectLineGroupMapping += 'orderby [Location].[Location].Name, [Group].[Group ID].Name;';
 
            let lsResult = vdCommon.selectQueryList("fn_dataReload(Group Mapping Select)", selectLineGroupMapping);

            let sLocation = "", sGroupID = "", sLine = "" ;
            let sEndDate = "", sMapFlag = "", sStartDate = "";  
            var tempKey="";
            var groupCnt = 0;

            //+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
            //Line Grp  52주차 데이타 삭제            
            //+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
            let deleteQuery = 'Delete data for model [Line Grp Oper Plan] Where {[Version].[Version Name].['+fbVersion+'], '+timeWeekNameSet+'};';
            vdCommon.executeQuery("fn_dataReload(Data Delete)", deleteQuery);
            //+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

            let LineEffData = new Map();
            let updateQuery = "";
  
            for (let i = 0; i < lsResult.rowCount; i++) {                
                //Dimension Data
                sLocation = lsResult.cs.row(i).cell(lsResult.cs.memberColumnIndex("Location", "Location")).Name;
                sGroupID = lsResult.cs.row(i).cell(lsResult.cs.memberColumnIndex("Group", "Group ID")).Name;
                sLine = lsResult.cs.row(i).cell(lsResult.cs.memberColumnIndex("Line", "Line")).Name;
   
                let selectLineEff = 'Select ([Version].[Version Name].['+fbVersion+'] * '+next52Weeks+' * [Location].[Location].['+sLocation+']  * [Line].[Line].['+sLine+']) on row, ';
                selectLineEff += '({Measure.[Line Eff W], Measure.[Line Eff W_Oper Plan], Measure.[Line Eff Sub_IsValid]}) on column ';
                selectLineEff += 'Where { Measure.[Line Eff W] > 0 , association(Measure.[Line Eff Sub_IsValid] == "Y")};';  
                let resultLineEff = vdCommon.selectQueryList("fn_dataReload(Line efficiency Select)", selectLineEff);  
                
                if(resultLineEff.rowCount > 0){
                    //{ Name : "All", DisplayName : "All"}
                    //LineEffData.push({ Location : sLocation, Line : sLine, EffW: "Y"});
                    
                    let resetQuery = 'cartesian scope :([Version].[Version Name].['+fbVersion+'] * '+timeWeekNameSet+' *  [Location].[Location].['+sLocation+'] * [Group].[Group ID].['+sGroupID+'] ); ' +
                                'Measure.[Line Grp_Line Cnt] = 0; ' +
                                'Measure.[Line Grp_Line Oper Cnt] = 0; ' +
                                'end scope;' ;
        
                    vdCommon.executeQuery("Data reset(update)", resetQuery); 
                }
            }

            for ( i = 0; i < lsResult.rowCount; i++) {  
                //Dimension Data
                sLocation = lsResult.cs.row(i).cell(lsResult.cs.memberColumnIndex("Location", "Location")).Name;
                sGroupID = lsResult.cs.row(i).cell(lsResult.cs.memberColumnIndex("Group", "Group ID")).Name;
                sLine = lsResult.cs.row(i).cell(lsResult.cs.memberColumnIndex("Line", "Line")).Name;

                //Measure Data
                sMapFlag = lsResult.cs.row(i).cell(lsResult.cs.measureColumnIndex("Line Grp Map_Flag"));
                sStartDate = lsResult.cs.row(i).cell(lsResult.cs.measureColumnIndex("Line Grp Map_Startdate"));
                sEndDate = lsResult.cs.row(i).cell(lsResult.cs.measureColumnIndex("Line Grp Map_Enddate"));

                //Location + Line별 가동율을 조회함.
                let selectLineEffWeek = 'Select ([Version].[Version Name].['+fbVersion+'] * '+timeWeekNameSet+' * [Location].[Location].['+sLocation+']  * [Line].[Line].['+sLine+']) on row, ';
                selectLineEffWeek += '({Measure.[Line Eff W]}) on column ';
                selectLineEffWeek += 'Where { Measure.[Line Eff W] > 0 , association(Measure.[Line Eff Sub_IsValid] == "Y")};';  
                let resultLineEffWeek = vdCommon.selectQueryList("fn_dataReload(Line efficiency Week)", selectLineEffWeek);
                let comboEffWeek = vdCommon.fn_makeCombo(resultLineEffWeek, {DimName : "Time", DimAttbName : "Week", existAll : false, Sort : "DisplayName", isDisplayNameWithCode : false}); 
                let effWeekList = comboEffWeek.map(item => item.Name)

                //+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
                if(effWeekList.length > 0){
                    updateQuery = "";
                    //Start Week 체크
                    if(parseInt(sStartDate) < parseInt(startWeek)){
                        sStartDate = startWeek ;
                    }
                    //End Week 체크
                    if(sMapFlag == "N"){
                        vdCommon.debug("sMapFlag["+sLocation+"]["+sGroupID+"]["+sLine+"]["+sEndDate+"]["+vdUtil.fn_getString(sEndDate)+"]")
                    }
                    if(vdUtil.fn_getString(sEndDate) != ""){
                        vdCommon.debug("[sEndDate]["+sEndDate+"], [lastWeek]["+lastWeek+"]")
                        if(parseInt(sEndDate) < parseInt(lastWeek)){
                            sEndDate = sEndDate;
                        }
                    }else{
                        vdCommon.debug("Else [sEndDate]["+sEndDate+"], [lastWeek]["+lastWeek+"]")
                        sEndDate = lastWeek;
                    }
                    updateQuery = 'scope :([Version].[Version Name].['+fbVersion+']'
                    updateQuery +=' * [Time].[Week].filter((#.Name >= "'+sStartDate+'" && #.Name <= "'+sEndDate+'") && #.Name in {'+effWeekList.map(item => `"${item}"`).join(",")+'})' ;                  
                    updateQuery +=' * [Location].[Location].['+sLocation+'] * [Group].[Group ID].['+sGroupID+'] ); ';
                    updateQuery +='Measure.[Line Grp_Line Cnt] = Measure.[Line Grp_Line Cnt] + 1 ; ';
                    updateQuery +='end scope; ' ;
                    vdCommon.executeQuery("Data Cal",updateQuery);
                }
               
            }

            // Line Grp_Line Oper Cnt 메져 데이타 Update
            // MFG Capa Simul Line 메져그룹에서 데이타 조회
            selectQuery = "";
            selectQuery = "Select ([Location].[Location] * [Time].[Week] * [Group].[Group ID]  * {Measure.[MFG Capa Simul Line_Oper Line Cnt]}) " ;
            selectQuery += "Where {[Version].[Version Name].["+fbVersion+"] , [Data Set].[Data Set].[MP] }; ";

            let result = vdCommon.selectQueryList("fn_dataReload(MFG Capa Simul Line)", selectQuery);
            updateQuery = "" ;
            for(var k=0; k < result.rowCount; k++){
                updateQuery = 'scope :([Version].[Version Name].['+fbVersion+'] * [Time].[Week].['+result.cs.row(k).cell(result.cs.memberColumnIndex("Time", "Week")).Name+'] ' ;
                updateQuery += '* [Location].[Location].['+result.cs.row(k).cell(result.cs.memberColumnIndex("Location", "Location")).Name+'] ';
                updateQuery += '* [Group].[Group ID].['+result.cs.row(k).cell(result.cs.memberColumnIndex("Group", "Group ID")).Name+']';
                updateQuery += ');'
                updateQuery += 'Measure.[Line Grp_Line Oper Cnt] = ' + result.cs.row(k).cell(result.cs.measureColumnIndex("MFG Capa Simul Line_Oper Line Cnt")) + ";";
                updateQuery += 'end scope;';

                vdCommon.executeQuery("Data Cal",updateQuery);
            }

            // 2025-08-20 : 유저가 입력한 값은 유지되도록 처리함.
            //Org 값을 처리함. 
            updateQuery = "" ;
            for(var k=0; k < resultOrgData.rowCount; k++){
                updateQuery = 'scope :([Version].[Version Name].['+fbVersion+'] * [Time].[Week].['+resultOrgData.cs.row(k).cell(resultOrgData.cs.memberColumnIndex("Time", "Week")).Name+'] ' ;
                updateQuery += '* [Location].[Location].['+resultOrgData.cs.row(k).cell(resultOrgData.cs.memberColumnIndex("Location", "Location")).Name+'] ';
                updateQuery += '* [Group].[Group ID].['+resultOrgData.cs.row(k).cell(resultOrgData.cs.memberColumnIndex("Group", "Group ID")).Name+']';
                updateQuery += ');'
                updateQuery += 'Measure.[Line Grp_Line Oper Cnt] = ' + resultOrgData.cs.row(k).cell(resultOrgData.cs.measureColumnIndex("Line Grp_Line Oper Cnt")) + ";";
                updateQuery += 'end scope;';

                vdCommon.executeQuery("Org Data Update",updateQuery);
            }

            //vdCommon.debug(" Line Cnt Update SQL : " + updateQuery);

            vdCommon.printStep(">>>>>>>>>>> fn_DataReload End");		
            vdCommon.programEnd();
        }catch ( e ) {
            RuleOutputToUI = { Status : 'Error', Message : "Js Logic Error : " + e.message };
            return;
        }
    }

    return{
        fn_dataReload : fn_dataReload
    };		
});