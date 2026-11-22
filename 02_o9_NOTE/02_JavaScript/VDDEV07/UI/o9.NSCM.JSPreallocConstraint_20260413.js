define('o9.NSCM.JSPreallocConstraint', ['o9/data/query', 'o9/data/cellset', 'o9.NSCM.commonLib'], function(){	
	const programName = "o9.NSCM.JSPreallocConstraint";

	let dimParams = {};

    function fn_group1(o9Params){
        try{
            const commonLib = require('o9.NSCM.commonLib');
            const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
            vdCommon.setLogLevel("Debug");
            vdCommon.printParams(o9Params);

            // 파라메타 가져오기
            let parsedParams = JSON.parse(o9Params); 
            let fbVersion = parsedParams.fbVersion;
            let fbGroup1 = parsedParams.fbGroup1;
         
            
            /*var result = vdCommon.selectList(['[Problem Type].[Problem Category2]'],
                                             [],
                                             "Where {[Problem Type].[Problem Category1].[PRE ALLOC]}",
                                             "",
                                             "");*/
            var result = vdCommon.selectList(['[Problem Type].[Short Reason]'],
                                            [],
                                            "Where {[Problem Type].[Problem Category1].[PRE ALLOC]}",
                                            "",
                                            "");                                             
            vdCommon.printCsData(result, 3);    

            var comboData = vdCommon.fn_makeCombo(result, {DimName : "Problem Type", 
                                                           DimAttbName : "Short Reason", 
                                                           Sort :"DisplayName", 
                                                           existAll : false, 
                                                           isDisplayNameWithCode : false});
            vdCommon.debug("ComboData : " + JSON.stringify(comboData));

            var comboList = [];
            var tempName = "";
            for(var k=0; k < comboData.length; k++){
                var name = comboData[k]["Name"];
                var rtnArry = String(name).split("_");
            
                var filterValue = "";
                if(rtnArry.length === 1){
                    filterValue = rtnArry[0];
                }else{
                    filterValue = rtnArry[1];
                }
                //console.log("comboList["+k+"]["+name+"]["+filterValue+"]" + JSON.stringify(rtnArry));
                comboList.push({ Name : filterValue, DisplayName : filterValue});
            }
            //Unique Data 조회
            comboList = comboList.filter(function(item1,idx1){       
                return comboList.findIndex(function(item2, idx2){
                    console.log("["+item1.Name+"]["+item2.Name+"]["+idx2+"]"); 
                    return (item1.Name == item2.Name) ;
                }) >= idx1;  
            });

            //Sort
            comboList.sort((a, b) => {
                //console.log("["+parseInt(a.name)+"]["+parseInt(b.name)+"]");                 
                if ( a.Name < b.Name ) return -1;
                if ( a.Name > b.Name) return 1;
                return 0;
            });

            vdCommon.programEnd();
            return comboList;

        }catch ( e ) {
            RuleOutputToUI = { Status : 'Error', Message : "Js Logic Error : " + e.message };
            return;
        }
    }   

    function fn_group2(o9Params){
        try{
            const commonLib = require('o9.NSCM.commonLib');
            const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
            const vdUtil = new commonLib.VdUtil();
            vdCommon.setLogLevel("Debug");
            vdCommon.printParams(o9Params);

            // 파라메타 가져오기
            let parsedParams = JSON.parse(o9Params); 
            let fbVersion = parsedParams.fbVersion;
            let fbGroup1 = parsedParams.fbGroup1;
            let strFilter = "PAC_"+ fbGroup1 + "%";  
            vdCommon.printStep("[strFilter]" + strFilter + "["+vdUtil.fn_filterStr(strFilter)+"]");     
            
            var result = vdCommon.selectList(['[Problem Type].[Problem Reason]'],
                                             [],
                                             "Where {[Problem Type].[Problem Category1].[PRE ALLOC],[Problem Type].[Short Reason]"+vdUtil.fn_filterStr(strFilter)+"}",
                                             "",
                                             "");
            vdCommon.printCsData(result, 3);

            var comboList = vdCommon.fn_makeCombo(result, {DimName : "Problem Type", 
                                                           DimAttbName : "Problem Reason", 
                                                           Sort :"DisplayName", 
                                                           existAll : false, 
                                                           isDisplayNameWithCode : false});
            vdCommon.debug("ComboData : " + JSON.stringify(comboList));

            //+++++++++++++++++++++++++++++++++++++++++++++++++++++++++
            //Display Name에서 PAC_ 제외시킴
            //+++++++++++++++++++++++++++++++++++++++++++++++++++++++++
            for(var k=0; k < comboList.length; k++){
                var name = comboList[k]["Name"];
                var displayName = comboList[k]["DisplayName"];
                var rtnArry = String(displayName).split("_");
                comboList[k]["DisplayName"] = rtnArry[rtnArry.length - 1];
                comboList[k]["Name"] = rtnArry[rtnArry.length - 1];
            }
            //+++++++++++++++++++++++++++++++++++++++++++++++++++++++++
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
            vdCommon.setLogLevel("Debug");
            vdCommon.printParams(o9Params);

            // 파라메타 가져오기
            let parsedParams = JSON.parse(o9Params); 
            let fbVersion = parsedParams.fbVersion;
            let fbGroupID = "";
            let fbGroup1 = parsedParams.fbGroup1;
            let fbGroup2 = parsedParams.fbGroup2;
            let fbDesc = parsedParams.fbDesc;        
            //GroupID 키 생성을 위해 마지막 Group ID 조회

            let selectDimension = [];
            selectDimension.push("[Version].[Version Name].["+fbVersion+"]");
            selectDimension.push("[Group].[Group ID].filter(#.Name startswith([PAC_]))");

            let selectMeasure = [];
            selectMeasure.push("Measure.[Pre Alloc Const_Created By]"); 
            selectMeasure.push("Measure.[Pre Alloc Const_Creation Time]"); 
            selectMeasure.push("Measure.[Pre Alloc Const_Grp Description]"); 
            selectMeasure.push("Measure.[Pre Alloc Const_Grp1]"); 
            selectMeasure.push("Measure.[Pre Alloc Const_Grp2]"); 
            selectMeasure.push("Measure.[Pre Alloc Const_Update Time]"); 
            selectMeasure.push("Measure.[Pre Alloc Const_Updated By]");

            let resultData = vdCommon.selectList(selectDimension, selectMeasure, "", "orderby [Group].[Group ID].Name desc", "");
            //selectList(dimension, measure, where, orderby, limit)
            if(resultData.cs.rowCount > 0){
                fbGroupID = resultData.cs.row(0).cell(resultData.cs.memberColumnIndex("Group", "Group ID")).Name; 
                fbGroupID = String(fbGroupID).substring(4, 9); //ex) PAC_00001 => 00001 자르기
                fbGroupID =  parseInt(fbGroupID) + 1 ;
                fbGroupID = "PAC_" + String(fbGroupID).padStart(5, "0") ;
            }else{
                fbGroupID = "PAC_00001";
            }

            //vdCommon.debug("GroupID["+fbGroupID+"]");

            //Group ID 멤버 확인
            var memberSql = "[Group].[Group ID] ";
            if (!vdCommon.existMember(memberSql, fbGroupID) ) {
                vdCommon.createMember(memberSql, fbGroupID);
            }
            //Group ID 등록
            let crateDimension = [];
            crateDimension.push("[Version].[Version Name].["+fbVersion+"]");
            crateDimension.push("[Group].[Group ID].["+fbGroupID+"]");

            let createMeasure = [];
            createMeasure.push('Measure.[Pre Alloc Const_Created By] = CurrentUser().[User Name];'); 
            createMeasure.push('Measure.[Pre Alloc Const_Creation Time]= dateadd(Now(),9,"hour");'); 
            createMeasure.push('Measure.[Pre Alloc Const_Grp Description]= "'+fbDesc+'";'); 
            createMeasure.push('Measure.[Pre Alloc Const_Grp1]= "'+fbGroup1+'";'); 
            createMeasure.push('Measure.[Pre Alloc Const_Grp2]= "'+fbGroup2+'";'); 

            vdCommon.createMeasure(crateDimension, createMeasure);
	
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
                whereQuery.push("[Group].[Group ID].["+fbDataList[k].GroupID.Value+"]");

                vdCommon.deleteMeasure(whereQuery, "Pre Alloc Const");
                vdCommon.deleteMeasure(whereQuery, "Pre Alloc Const by Item");
                vdCommon.deleteMeasure(whereQuery, "Pre Alloc Const Detail W");
           }

        }catch ( e ) {
            RuleOutputToUI = { Status : 'Error', Message : "Js Logic Error : " + e.message };
            return;
        }  
    }
    return{
        fn_add : fn_add,
        fn_delete : fn_delete,
        fn_group1 : fn_group1,
        fn_group2 : fn_group2
    };		
});