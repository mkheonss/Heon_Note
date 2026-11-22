define('o9.NSCM.JSEWPreAllocConstraint', ['o9/data/query', 'o9/data/cellset', 'o9.NSCM.commonLib'], function(){	
	const programName = "o9.NSCM.JSEWPreAllocConstraint";
    const commonLib = require('o9.NSCM.commonLib');
    const vdUtil = new commonLib.VdUtil();
    /*--------------------------------------------------------------------------------------------------*/
    // 프로그램명 : o9.NSCM.JSEWPreAllocConstraint
    // Action Button : EWPreAlloc
    // 화면명 : Pre-alloc Constraint
    // 2025.08.14 최초 생성
    // 2025.08.20 변경된 메저 그룹 적용
    // 2025.09.03 Item, Except Item 처리 수정
    // 2025.09.11 Action Button 명칭 변경
    // 2025.09.12 fn_cb_groupId() 추가함.
    // 2025.09.19 소스 정리
    // 2025.09.23 update 일자 처리 수정
    // 2025.10.15 fn_cb_inch, fn_cb_project, fn_cb_setYear, fn_cb_setMarketingName 함수 추가함.
    // 2025.11.06 Where절 데이타 중 All인 경우 다른 선택 무시함.
    // 2025.11.06 Measure.[Pre Alloc Const_GC Code], Measure.[Pre Alloc Const_AP2 Code] 추가 되어 Code, Name 별도로 관리함.
    // 2025.11.07 AP2 조회 NameSet 변경 &NSUISalesStd1View -> &NSUISalesStd2View
    // 2025.11.11 Save시 Version 정보를 Grid Row 단위로 받아서 처리함.
    // 2025.11.18 fn_filterConstWeek 추가함.
    // 2025.12.08 Bod Item 기준으로 Item 속성을 조회함. (CTN Group Const. 기준 동일함.) 
    //            기존 함수 삭제함.
    // 2025.12.19 Measure.[Pre Alloc Const by Item_PLC Status] 추가 메져 처리
    // 2025.12.19 fn_save_exception() 추가함.
    // 2025.12.31 fn_loadFunction() 수정함. => parsedParams 값 체크 로직 추가  
    // 2026.01.27 Save Item/Filter 메저 생성을 파이썬(PY_UI_PreAllocConstItemReg)에서 처리함.
    // 2026.01.29 fn_filterItemStatus() 
    // 2026.03.04 fn_merge() 관련 API 추가
    /*--------------------------------------------------------------------------------------------------*/
    
	var fn_loadFunction = function(o9Params){
        const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
        vdCommon.setLogLevel("Debug");

		try {
            let returnData = {};
            let obj = this;

            vdCommon.printParams(o9Params);

            // 파라메타 가져오기
            var parsedParams = JSON.parse(o9Params);
			var fbFuncName = parsedParams.fbFuncName;

            if ( functionMap[fbFuncName] == undefined ) {
                return { "Code" : 1, "Msg" : "No Function" };
            }

            if ( parsedParams["fbParams"] == undefined ) {
                parsedParams["fbParams"] = {};
            }
            if ( parsedParams.fbParams["includeField"] == undefined ) {
                parsedParams.fbParams["includeField"] = "";
            }
            if ( parsedParams.fbParams["includeProperty"] == undefined ) {
                parsedParams.fbParams["includeProperty"] = "";
            }
            // 조회시 기본 limit 지정( 3000개 )
            if ( parsedParams.fbParams["limit"] == undefined ) {
                parsedParams.fbParams["limit"] = "limit 3000";
            } else if ( parsedParams.fbParams["limit"] == -1 ) {
                parsedParams.fbParams["limit"] = "";
            } else {
                parsedParams.fbParams["limit"] = "limit " + parsedParams.fbParams.limit;
            }
            // 콤보에 All 추가
            if ( parsedParams.fbParams["existAll"] == undefined ) {
                parsedParams.fbParams["existAll"] = false;
            }
            // 콤보에 Blank 추가
            if ( parsedParams.fbParams["existBlank"] == undefined ) {
                parsedParams.fbParams["existBlank"] = false;
            }
            // 콤보에 - 추가
            if ( parsedParams.fbParams["existHyphen"] == undefined ) {
                parsedParams.fbParams["existHyphen"] = false;
            }
            // where 조건 추가
            if ( parsedParams.fbParams["where"] == undefined ) {
                parsedParams.fbParams["where"] = {};
            }
            if ( parsedParams.fbParams["isDisplayNameWithCode"] == undefined ) {
                parsedParams.fbParams["isDisplayNameWithCode"] = true;
            }
            // filters 조건 추가
            if ( parsedParams.fbParams["filters"] == undefined ) {
                parsedParams.fbParams["filters"] = {};
            }

            var rtn = functionMap[fbFuncName](parsedParams);

            vdCommon.programEnd();
            return rtn;
        } catch ( e ) {
            vdCommon.error(e.message);
            return { "Code" : -1, "Msg" : e.message };
        }
	};

    var fn_dataCheck = function(val){
        const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
        vdCommon.setLogLevel("Debug");
        try {        
            var k = 0;

            if(vdUtil.fn_getString(val) == ""){
                return "";
            }

            if ( Array.isArray(val)){
                for (k = 0; k < val.length; k++){
                    if(val[k] == "All"){                    
                        return "";
                    }
                }
                return val;
            }

            let rtnValue = val.split("^");
            for (k = 0; k < rtnValue.length; k++){
                if(rtnValue[k] == "All"){
                    return "";
                }
            } 
            return rtnValue;
        } catch (e) {
            return { "Code": -1, "Msg": e.message };
        }
    }
    
    //wild card & multi select 데이타에 대한 Filter 조건  
    var fn_filterList = function(list){
        const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
        const vdUtil = new commonLib.VdUtil();
        vdCommon.setLogLevel("Debug"); 
        try{
            var strSelect = "";

            if ( list == "All"  || list == "") {
                return strSelect ;
            }

            for (k = 0; k < list.length; k++){
                var sData = list[k];
                if(String(sData).toUpperCase() === "ALL"){
                    strSelect = '';
                    return strSelect;
                }else{
                    var startChar = sData.substring(0,1);
                    var endChar = sData.substring(sData.length - 1 ,sData.length);

                    if(k > 0){
                        strSelect += ' || '; //OR 조건식 추가
                    }
        
                    if(startChar === "%" && endChar === "%"){
                        //console.log("중간체크") 
                        strSelect += '#.Name contains "'+sData.replace(/%/g, "")+'"';
                    }else if(startChar === "%"){
                        //console.log("끝")
                        strSelect += '#.Name endswith "'+sData.replace(/%/g, '')+'"';
                    }else if(endChar === "%"){
                        //console.log("startswith")
                        strSelect += '#.Name startswith "'+sData.replace(/%/g, '')+'"';
                    }else{
                        //console.log("equals")
                        strSelect += '#.Name == "'+sData.trim()+'"';
                    }                
                }
            }
            
            vdCommon.debug("[fn_filterList]" + strSelect );
            return strSelect;

        }catch ( e ) {
            RuleOutputToUI = { Status : 'Error', Message : "Js Logic Error : " + e.message };
            return;
        }
    }

    /* ********************************************************************************** */
    // { "fbFuncName" : "fn_cb_group1" }
    /* 호출 예제
    {"fbFuncName":"fn_cb_group1", "fbParams":{"version":"CWV_MP"}}
    */
    var fn_cb_group1 = function(parsedParams){
        const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
        vdCommon.setLogLevel("Debug"); 
        try{        

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
            //vdCommon.debug("ComboData : " + JSON.stringify(comboData));

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

            return { "Code" : 0, "Msg" : "", "Rows" : comboList };

        }catch ( e ) {
            return { "Code" : -1, "Msg" : e.message };
        }
    }
    /* ********************************************************************************** */
    // { "fbFuncName" : "fn_cb_group2" }
    /* 호출 예제
    {"fbFuncName":"fn_cb_group2", 
    "fbParams":{
        "version":"CWV_MP", 
        "Measure.[Pre Alloc Const_Grp1]":"CIRCUIT"}
    }
    */
    var fn_cb_group2 = function(parsedParams){
        const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
        vdCommon.setLogLevel("Debug"); 
        try{        
            let fbGroup1 = parsedParams.fbParams["Measure.[Pre Alloc Const_Grp1]"];
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
            //vdCommon.debug("ComboData : " + JSON.stringify(comboList));

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
         

            return { "Code" : 0, "Msg" : "", "Rows" : comboList };

        }catch ( e ) {
            return { "Code" : -1, "Msg" : e.message };
        }
    }    
    /* ********************************************************************************** */
    var fn_cb_groupId = function(parsedParams){
        const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
        vdCommon.setLogLevel("Debug"); 
        try{
            let comboList = [];
            let fbVersion = parsedParams.fbParams.version;
            let fbGroupID = parsedParams.fbParams["[Group].[Group ID]"];

            let dimensionQuery =[];
            dimensionQuery.push('[Version].[Version Name].['+fbVersion+']');
            dimensionQuery.push('[Group].[Group ID]' + vdUtil.fn_filterStr(fbGroupID));
            let measureQuery = [];
            measureQuery.push('Measure.[Pre Alloc Const_Grp1]');
            measureQuery.push('Measure.[Pre Alloc Const_Grp2]');
            measureQuery.push('Measure.[Pre Alloc Const_Grp Description]');
            measureQuery.push('Measure.[Pre Alloc Const_From Site]');
            measureQuery.push('Measure.[Pre Alloc Const_From Site ID]');            

            let selectResult = vdCommon.selectList(dimensionQuery, measureQuery, "" ,"orderby [Group].[Group ID].Name ",parsedParams.fbParams.limit);

            for(var k=0; k < selectResult.cs.rowCount; k++){ 
                let groupid = selectResult.cs.row(k).cell(selectResult.cs.memberColumnIndex("Group", "Group ID")).Name;
                let groupName = selectResult.cs.row(k).cell(selectResult.cs.memberColumnIndex("Group", "Group ID")).DisplayName;
                let grp1 = vdCommon.getMeasureValue(selectResult.cs, k, "Pre Alloc Const_Grp1");
                let grp2 = vdCommon.getMeasureValue(selectResult.cs, k, "Pre Alloc Const_Grp2");
                let grpDesc = vdCommon.getMeasureValue(selectResult.cs, k, "Pre Alloc Const_Grp Description");
                let fromSite = vdCommon.getMeasureValue(selectResult.cs, k, "Pre Alloc Const_From Site");
                let fbFromSiteID = vdCommon.getMeasureValue(selectResult.cs, k, "Pre Alloc Const_From Site ID");
                comboList.push({ Name:groupid , DisplayName:groupName , Group1:grp1, Group2:grp2, Grp_Desc:grpDesc, Form_Site_ID: fbFromSiteID, From_Site:fromSite });
            }   
            return { "Code" : 0, "Msg" : "", "Rows" : comboList };

        }catch ( e ) {
            return { "Code" : -1, "Msg" : e.message };
        }
    }
    /* ********************************************************************************** */
    /*
        Pre Alloc Group ID 채번
    */ 
    var fn_groupId = function(pVersion){
        const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
        vdCommon.setLogLevel("Debug"); 
        try{
            
            let fbGroupID ="";

            let selectDimension = [];
            selectDimension.push("[Version].[Version Name].["+pVersion+"]");
            selectDimension.push("[Group].[Group ID].filter(#.Name startswith([PAC_]))");

            let selectMeasure = [];
            selectMeasure.push("Measure.[Pre Alloc Const_Created By]"); 
            selectMeasure.push("Measure.[Pre Alloc Const_Creation Time]"); 
            selectMeasure.push("Measure.[Pre Alloc Const_Grp Description]"); 
            selectMeasure.push("Measure.[Pre Alloc Const_Grp1]"); 
            selectMeasure.push("Measure.[Pre Alloc Const_Grp2]"); 
            selectMeasure.push("Measure.[Pre Alloc Const_Update Time]"); 
            selectMeasure.push("Measure.[Pre Alloc Const_Updated By]");

            let resultData = vdCommon.selectList(selectDimension, selectMeasure, "", "orderby [Group].[Group ID].Name desc", "limit 1");

            if(resultData.cs.rowCount > 0){
                fbGroupID = resultData.cs.row(0).cell(resultData.cs.memberColumnIndex("Group", "Group ID")).Name; 
                fbGroupID = String(fbGroupID).substring(4, 9); //ex) PAC_00001 => 00001 자르기
                fbGroupID =  parseInt(fbGroupID) + 1 ;
                fbGroupID = "PAC_" + String(fbGroupID).padStart(5, "0") ;
            }else{
                fbGroupID = "PAC_00001";
            }

            //Member 등록여부 확인
            var memberSql = "[Group].[Group ID] ";
            if (!vdCommon.existMember(memberSql, fbGroupID) ) {
                vdCommon.createMember(memberSql, fbGroupID);
            }
            return fbGroupID;
        }catch(e){
            return -1;
        }
    }
    
    var fn_selectItems = function(params){
        const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
        vdCommon.setLogLevel("Debug"); 
        try{
            //vdCommon.debug("[fn_selectItems]"+JSON.stringify(params));
            let itemUnion = [];

            let fbVersion = params["Version"];
            let fbFromSiteID = params["Location"];
            let fbGC = fn_dataCheck(params["GC"]);
            let fbAP2 = fn_dataCheck(params["AP2"]);
            let fbProductGroup = fn_dataCheck(params["ProductGroup"]);
            let fbProject = fn_dataCheck(params["Project"]);
            let fbMarketingName = fn_dataCheck(params["MarketingName"]);
            let fbInch = fn_dataCheck(params["Inch"]);
            let fbYear = fn_dataCheck(params["Year"]);
            let itemList = params["Item"].split("^");

            let strFilterQuery  = fn_filterList(itemList);
            if(strFilterQuery.length > 0){
                strFilterQuery = ".filter("+strFilterQuery+")";
            }
            let itemSelectQuery = "(Select(";
            itemSelectQuery += "[Version].[Version Name].["+fbVersion+"] " ;
            itemSelectQuery += "* [Location].[Location].["+fbFromSiteID+"] " ;
            itemSelectQuery += "* &SETItem"+ strFilterQuery  ;
            itemSelectQuery += ") on row, ";
            itemSelectQuery += "({Measure.[BOD Item_asn], Measure.[Item Site Asn_Cur Status]}) on column ";
            itemSelectQuery += "Where {";
            itemSelectQuery += " [Sub Location].[Sub Location GC]"+vdUtil.fn_filterStr(fbGC);
            itemSelectQuery += ",[Sub Location].[Sub Location Rep AP2]"+vdUtil.fn_filterStr(fbAP2);
            itemSelectQuery += ",&NSUISubLocationDC";
            itemSelectQuery += ",[Item].[Product Group]"+ vdUtil.fn_filterStr(fbProductGroup);
            itemSelectQuery += ",[Item].[Project]"+ vdUtil.fn_filterStr(fbProject);
            itemSelectQuery += ",[Item].[Marketing Name]"+ vdUtil.fn_filterStr(fbMarketingName);
            itemSelectQuery += ",[Item].[Inch]"+ vdUtil.fn_filterStr(fbInch);
            itemSelectQuery += ",[Item].[Year]"+ vdUtil.fn_filterStr(fbYear);
            itemSelectQuery += ",[Trans Mode].[Trans Mode]";
            itemSelectQuery += ",(Measure.[BOD Item_asn] == 1)";
            itemSelectQuery += ',(Measure.[BOD Item_Cur Status] in {"PLANNED","ACTIVE","INACTIVE"})';
            itemSelectQuery += ',(coalesce(Measure.[BOD Item_Eff Startdate],DATEADD(Now(),-1,"Day")) < now() && coalesce(Measure.[BOD Item_Eff Enddate],DATEADD(Now(),1,"Day")) > now()) ';
            itemSelectQuery += "}).filter(~isnull(Measure.[BOD Item_asn])) ;";                

            vdCommon.debug("[fn_selectItems][SelectQuery]"+itemSelectQuery);
            let selectResult = vdCommon.selectQueryList("fn_selectItems(Filter)",itemSelectQuery);
            vdCommon.debug("Count["+selectResult.cs.rowCount+"]");
            for ( var i = 0; i < selectResult.cs.rowCount; i++ ) {
                let name = selectResult.cs.row(i).cell(selectResult.cs.memberColumnIndex("Item","Item")).Name;
                let plcStatus = vdCommon.getMeasureValue(selectResult.cs, i, "Item Site Asn_Cur Status");

                itemUnion.push({"Name":name, "Status":plcStatus}) ;
            }
            vdCommon.debug(itemUnion.length + "/" + JSON.stringify(itemUnion));
            return itemUnion;
        }catch(e){
            return -1;
        }
    }   

    /* ********************************************************************************** */
    /* fn_Save() 관련 */
    var fn_validation = function(parsedParams){
        const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
        vdCommon.setLogLevel("Debug"); 
        try{
            let errorCnt1 = 0;
            let errorMsg1 = "Error : Duplicated Intersection(s)";            

            let fbVersion = parsedParams.fbParams.version;

            for ( var i = 0; i < parsedParams.fbGridRows.length; i++ ) {
                let rowStatus = parsedParams.fbGridRows[i]["rowstatus"];
                let fbLocation = parsedParams.fbGridRows[i]["[Location].[Location]"];

                parsedParams.fbGridRows[i]["rowmsg"] = "";
                parsedParams.fbGridRows[i]["errorflag"] = "";

                let dimensionQuery = [];
                let measureQuery = [];

                if(rowStatus != "D"){
                    //validation 체크함.
                    dimensionQuery.push("[Version].[Version Name]"+vdUtil.fn_filterStr(parsedParams.fbGridRows[i]["[Version].[Version Name]"]));
                    dimensionQuery.push("[Group].[Group ID]");

                    measureQuery.push("Measure.[Pre Alloc Const_Grp1]");
                    measureQuery.push("Measure.[Pre Alloc Const_Grp2]");
                    measureQuery.push("Measure.[Pre Alloc Const_From Site ID]");
                    measureQuery.push("Measure.[Pre Alloc Const_From Site]");
                    measureQuery.push("Measure.[Pre Alloc Const_GC]");
                    measureQuery.push("Measure.[Pre Alloc Const_GC Code]");
                    measureQuery.push("Measure.[Pre Alloc Const_AP2]");
                    measureQuery.push("Measure.[Pre Alloc Const_AP2 Code]");
                    measureQuery.push("Measure.[Pre Alloc Const_Grp Description]");
                    measureQuery.push("Measure.[Pre Alloc Const_Product Grp]");
                    measureQuery.push("Measure.[Pre Alloc Const_Inch]");
                    measureQuery.push("Measure.[Pre Alloc Const_Project]");
                    measureQuery.push("Measure.[Pre Alloc Const_Year]");
                    measureQuery.push("Measure.[Pre Alloc Const_MKT Name]");
                    measureQuery.push("Measure.[Pre Alloc Const_Item]");
                    measureQuery.push("Measure.[Pre Alloc Const_Exception]");

                    let whereQuery = 'Where{';
                    whereQuery += 'Measure.[Pre Alloc Const_Grp1] == "'+parsedParams.fbGridRows[i]["Measure.[Pre Alloc Const_Grp1]"]+'"';
                    whereQuery += ',Measure.[Pre Alloc Const_Grp2] == "'+parsedParams.fbGridRows[i]["Measure.[Pre Alloc Const_Grp2]"]+'"';
                    whereQuery += ',Measure.[Pre Alloc Const_Grp Description] == "'+parsedParams.fbGridRows[i]["Measure.[Pre Alloc Const_Grp Description]"]+'"';                    
                    whereQuery += ',Measure.[Pre Alloc Const_From Site ID] == "'+parsedParams.fbGridRows[i]["Measure.[Pre Alloc Const_From Site ID]"]+'"';
                    whereQuery += ',Measure.[Pre Alloc Const_GC Code] == "'+parsedParams.fbGridRows[i]["Measure.[Pre Alloc Const_GC Code]"]+'"';
                    whereQuery += ',Measure.[Pre Alloc Const_AP2 Code] == "'+parsedParams.fbGridRows[i]["Measure.[Pre Alloc Const_AP2 Code]"]+'"';
                    whereQuery += ',Measure.[Pre Alloc Const_Product Grp] == "'+parsedParams.fbGridRows[i]["Measure.[Pre Alloc Const_Product Grp]"]+'"';
                    whereQuery += ',Measure.[Pre Alloc Const_Inch] == "'+parsedParams.fbGridRows[i]["Measure.[Pre Alloc Const_Inch]"]+'"';
                    whereQuery += ',Measure.[Pre Alloc Const_Project] == "'+parsedParams.fbGridRows[i]["Measure.[Pre Alloc Const_Project]"]+'"';
                    whereQuery += ',Measure.[Pre Alloc Const_Year] == "'+parsedParams.fbGridRows[i]["Measure.[Pre Alloc Const_Year]"]+'"';
                    whereQuery += ',Measure.[Pre Alloc Const_MKT Name] == "'+parsedParams.fbGridRows[i]["Measure.[Pre Alloc Const_MKT Name]"]+'"';
                    whereQuery += ',Measure.[Pre Alloc Const_Item] == "'+parsedParams.fbGridRows[i]["Measure.[Pre Alloc Const_Item]"]+'"';
                    whereQuery += ',Measure.[Pre Alloc Const_Exception] == "'+parsedParams.fbGridRows[i]["Measure.[Pre Alloc Const_Exception]"]+'"';
                    whereQuery += '}';


                    let result = vdCommon.selectList(dimensionQuery, measureQuery, whereQuery, "", "");

                    if(result.cs.rowCount > 0){
                        errorCnt1++;
                        parsedParams.fbGridRows[i]["rowmsg"] = errorMsg1;
                        parsedParams.fbGridRows[i]["errorflag"] = "ERROR";
                    }
                }
            }

            let errorMsg = "";
            if(errorCnt1 > 0){
                errorMsg += (errorMsg == "" ? "" : " ")  + errorMsg1 ;
            }

            if(errorCnt1 > 0 ){
                //Error Row만 Return 함.
                //let checkGridRows = parsedParams.fbGridRows;
                //const errorRows = checkGridRows.filter((checkGridRows)=>{return checkGridRows.errorflag === "ERROR"});
                //parsedParams.fbGridRows = errorRows;
                //2025. 09.17 EW쪽 팝업을 처리하기 위해서 Code 값을 "1"로 처리함.
                //return { "Code" : 1, "Msg" : errorMsg, "Rows" : parsedParams.fbGridRows };
                return { "Code" : 1, "Msg" : errorMsg};
            }

            return { "Code" : 0, "Msg" : "" };
        }catch(e){
            return { "Code" : -1, "Msg" : e.message };
        }  
    };
    
    /*{"fbFuncName":"fn_save","fbParams":{"version":"CWV_MP"},
    "fbGridRows" : [
    {"rowstatus":"C", "rowindex":0,	
    "[Version].[Version Name]" : "CWV_MP",
    "[Group].[Group ID]" : "",
    "Measure.[Pre Alloc Const_From Site]":"SAMEX",
    "Measure.[Pre Alloc Const_From Site ID]":"P306",
    "Measure.[Pre Alloc Const_Grp1]":"CIRCUIT",
    "Measure.[Pre Alloc Const_Grp2]":"ETC",
    "Measure.[Pre Alloc Const_Grp Description]":"20250902_TEST_DATA",
    "Measure.[Pre Alloc Const_Product Grp]":"All",
    "Measure.[Pre Alloc Const_GC Code]":"207",
    "Measure.[Pre Alloc Const_GC]":"LATIN AMERICA",
    "Measure.[Pre Alloc Const_AP2 Code]":"300340^300139",
    "Measure.[Pre Alloc Const_AP2]":"SEASA^SELA-P",
    "Measure.[Pre Alloc Const_Inch]":"All",
    "Measure.[Pre Alloc Const_Project]":"All",
    "Measure.[Pre Alloc Const_Year]":"2024",
    "Measure.[Pre Alloc Const_MKT Name]":"All",
    "Measure.[Pre Alloc Const_Item]":"All",
    "Measure.[Pre Alloc Const_Exception]":""
    }]}
    */
    var fn_save = function(parsedParams){
        const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
        vdCommon.setLogLevel("Debug"); 
        try{           

            //Validation 체크
            let errorData = fn_validation(parsedParams);
            if(errorData.Code != 0){
                return errorData;
            }

            for ( var i = 0; i < parsedParams.fbGridRows.length; i++ ) {

                let rowStatus = parsedParams.fbGridRows[i]["rowstatus"];
                let fbVersion =  parsedParams.fbGridRows[i]["[Version].[Version Name]"];
                let fbGroup1 = parsedParams.fbGridRows[i]["Measure.[Pre Alloc Const_Grp1]"];
                let fbGroup2 = parsedParams.fbGridRows[i]["Measure.[Pre Alloc Const_Grp2]"];
                let fbGroupDesc = parsedParams.fbGridRows[i]["Measure.[Pre Alloc Const_Grp Description]"];

                let fbFromSiteID = parsedParams.fbGridRows[i]["Measure.[Pre Alloc Const_From Site ID]"];
                let fbFromSite = parsedParams.fbGridRows[i]["Measure.[Pre Alloc Const_From Sit]"];
                //Multi Select
                let fbProductGroup = parsedParams.fbGridRows[i]["Measure.[Pre Alloc Const_Product Grp]"];
                let fbGC = parsedParams.fbGridRows[i]["Measure.[Pre Alloc Const_GC Code]"];
                let fbGCName = parsedParams.fbGridRows[i]["Measure.[Pre Alloc Const_GC]"];
                let fbAP2 = parsedParams.fbGridRows[i]["Measure.[Pre Alloc Const_AP2 Code]"];
                let fbAP2Name = parsedParams.fbGridRows[i]["Measure.[Pre Alloc Const_AP2]"];
                let fbInch = parsedParams.fbGridRows[i]["Measure.[Pre Alloc Const_Inch]"];
                let fbProject = parsedParams.fbGridRows[i]["Measure.[Pre Alloc Const_Project]"];
                let fbYear = parsedParams.fbGridRows[i]["Measure.[Pre Alloc Const_Year]"];
                let fbMarketingName = parsedParams.fbGridRows[i]["Measure.[Pre Alloc Const_MKT Name]"];

                //wild card & multi select
                let fbItem = parsedParams.fbGridRows[i]["Measure.[Pre Alloc Const_Item]"];
                let fbExceptItem = parsedParams.fbGridRows[i]["Measure.[Pre Alloc Const_Exception]"];
                let fbGroupID = "";
                
                if(rowStatus == "D"){
                    fbGroupID = parsedParams.fbGridRows[i]["[Group].[Group ID]"];
                    let deleteWhere = [];
                    deleteWhere.push("[Version].[Version Name].["+fbVersion+"]");
                    deleteWhere.push("[Group].[Group ID].["+fbGroupID+"]");

                    vdCommon.deleteMeasure(deleteWhere, "Pre Alloc Const");
                    vdCommon.deleteMeasure(deleteWhere, "Pre Alloc Const Detail");
                    vdCommon.deleteMeasure(deleteWhere, "Pre Alloc Const Detail W");
                    vdCommon.deleteMeasure(deleteWhere, "Pre Alloc Const by Item");
                    //2026.01.12 추가함.
                    vdCommon.deleteMeasure(deleteWhere, "Pre Alloc Const Filter");

                }else{            
                    if(rowStatus == "C"){
                        fbGroupID= fn_groupId(fbVersion);
                        if(fbGroupID == -1){
                            return { "Code" : 0, "Msg" : "Abnormal [Group ID] occurrence.", "Rows" : "" };
                        }
                    }else{
                        fbGroupID = parsedParams.fbGridRows[i]["[Group].[Group ID]"];
                    }    
                    //+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
                      let dimension = [];
                    let measure = [];
                    let deleteWhere = [];

                    if(fbFromSite == undefined || fbFromSite == ""){
                        fbFromSite = vdCommon.fn_getCodeName("Location", fbFromSiteID);
                    }
                    //Pre Alloc Const 데이타 처리
                    dimension.push("[Version].[Version Name].["+fbVersion+"]");
                    dimension.push("[Group].[Group ID].["+fbGroupID+"]");

                    measure.push('Measure.[Pre Alloc Const_Grp1] = "'+fbGroup1+'";');
                    measure.push('Measure.[Pre Alloc Const_Grp2] = "'+fbGroup2+'";');
                    measure.push('Measure.[Pre Alloc Const_Grp Description] = "'+fbGroupDesc+'";');

                    if(rowStatus == "C"){
                        //++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
                        //Site Name 조회
                        var result = vdCommon.selectList(['&MFStageSETLocation.filter(#.Name == "'+fbFromSiteID+'")'], [], "", "", "");
                        fbFromSite = vdCommon.getPropertyValue(result.cs, 0, "Location", "Location", "Location Site ID");
                        //++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
                        measure.push('Measure.[Pre Alloc Const_From Site] = "'+fbFromSite+'";');
                        measure.push('Measure.[Pre Alloc Const_From Site ID] = "'+fbFromSiteID+'";'); //
                        measure.push('Measure.[Pre Alloc Const_Product Grp] = "'+fbProductGroup+'";');
                        //-----------------------------------------------------------------------------------------
                        measure.push('Measure.[Pre Alloc Const_GC] = "' + fbGCName + '";');
                        measure.push('Measure.[Pre Alloc Const_GC Code] = "' + fbGC + '";');
                        //-----------------------------------------------------------------------------------------
                        measure.push('Measure.[Pre Alloc Const_AP2] = "'+fbAP2Name+'";');                      
                        measure.push('Measure.[Pre Alloc Const_AP2 Code] = "'+fbAP2+'";'); 
                        //-----------------------------------------------------------------------------------------
                        measure.push('Measure.[Pre Alloc Const_Inch] = "'+fbInch+'";');
                        measure.push('Measure.[Pre Alloc Const_Project] = "'+fbProject+'";');
                        measure.push('Measure.[Pre Alloc Const_Year] = "'+fbYear+'";'); 
                        measure.push('Measure.[Pre Alloc Const_MKT Name]  = "'+fbMarketingName+'";');
                        measure.push('Measure.[Pre Alloc Const_Item] = "'+fbItem+'";');
                        measure.push('Measure.[Pre Alloc Const_Exception] = "'+fbExceptItem+'";');
                        measure.push('Measure.[Pre Alloc Const_Created By] = CurrentUser().[User Name];'); 
                        measure.push('Measure.[Pre Alloc Const_Creation Time]= Now();'); 
                        measure.push('Measure.[Pre Alloc Const_Updated By] = CurrentUser().[User Name];'); 
                        measure.push('Measure.[Pre Alloc Const_Update Time]= Now();'); 

                        vdCommon.createMeasure(dimension, measure);
                    }else{
                        measure.push('Measure.[Pre Alloc Const_Updated By] = CurrentUser().[User Name];'); 
                        measure.push('Measure.[Pre Alloc Const_Update Time]= Now();');                         
                        vdCommon.updateMeasure(dimension, measure);
                    }

                    //+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
                    //Pre Alloc Const Detail W 처리
                    dimension = [];
                    measure = [];
                    dimension.push("[Version].[Version Name].["+fbVersion+"]");
                    dimension.push("[Location].[Location].["+fbFromSiteID+"]");            
                    dimension.push("[Group].[Group ID].["+fbGroupID+"]");
                    dimension.push("[Sequence].[Sequence].[1]");
                    dimension.push("[Time].[Week].filter(#.Key >= &CurrentWeek.element(0).LeadOffset(0).Key && #.Key <= &CurrentWeek.element(0).LeadOffset(26).Key)"); //26주 조회

                    measure.push("Measure.[Pre Alloc Const Detail W_Const Qty] = 0;");
                    measure.push('Measure.[Pre Alloc Const Detail W_Created By] = CurrentUser().[User Name];'); 
                    measure.push('Measure.[Pre Alloc Const Detail W_Creation Time]= Now();'); 

                    if(rowStatus == "C"){
                        vdCommon.createMeasure(dimension, measure);                      
                    }else{
                        
                        vdCommon.updateMeasure(dimension, measure);  
                    }
                    
                    //+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
                    //Pre Alloc Const Detail 처리
                    dimension = [];
                    measure = [];
                    dimension.push("[Version].[Version Name].["+fbVersion+"]");
                    dimension.push("[Location].[Location].["+fbFromSiteID+"]");            
                    dimension.push("[Group].[Group ID].["+fbGroupID+"]");
                    dimension.push("[Sequence].[Sequence].[1]");

                    measure.push("Measure.[Pre Alloc Const Detail_IsValid] = false;");

                    if(rowStatus == "C"){
                        vdCommon.createMeasure(dimension, measure);                      
                    }else{
                        vdCommon.updateMeasure(dimension, measure);  
                    }

                    //+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
                    //Pre Alloc Const By Item 처리 ==> 2026.01.28 파이썬에서 생성함.
                    //Pre Alloc Const Filter 처리 ==> 2026.01.28 파이썬에서 생성함.
                    //삭제 후에 저장
                    deleteWhere = [];
                    deleteWhere.push("[Version].[Version Name].["+fbVersion+"]");
                    deleteWhere.push("[Group].[Group ID].["+fbGroupID+"]");
                    vdCommon.deleteMeasure(deleteWhere, "Pre Alloc Const by Item");
                    vdCommon.deleteMeasure(deleteWhere, "Pre Alloc Const Filter");
                    //++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
                    // Pre Alloc Const by Item, Pre Alloc Const Filter 메저그룹 데이타 생성
                    var userName = vdCommon.selectResult('CurrentUser().Name');
                    vdCommon.debug("[User Name]" + userName);
                    //파이썬 호출 : 
                    let executeQuery = 'EXEC plugin instance [PY_UI_PreAllocConstItemReg] for measures {[Pre Alloc Const by Item_Flag]} '
                    executeQuery += 'using scope ([Version].[Version Name].[' + fbVersion + '] * [Group].[Group ID].[' + fbGroupID + ']) '
                    executeQuery += 'using arguments {(ExecutionMode, "MediumWeight"), ("IncludeNullRows", "False")';
                    executeQuery += ',(paramOutVersion , "CWV_MP"),(paramOutCreatedByUser,"'+userName+'")';
                    executeQuery += ',(MaxSliceTableCells, 200000000), (MaxConcurrency, 1 ), ([Param.o9_sys_log_level], "DEBUG")} ;';

                    vdCommon.printStep("[" + programName + "] EXEC Python Call SQL>>" + executeQuery);
                    vdCommon.executeQuery("PY_UI_PreAllocConstItemReg ", executeQuery);                    
                } 
            }
            vdCommon.programEnd();
            return { "Code" : 0, "Msg" : "", "Rows" : "" };
            //
        }catch ( e ) {
            return { "Code" : -1, "Msg" : e.message };
        }
    }    
    
    /* ********************************************************************************** */
    // { "fbFuncName" : "fn_save_exception" }
    /* 호출 예제
    {"fbFuncName":"fn_save_exception","fbParams":{"version":"CWV_MP"},
    "fbGridRows" : [
    {"rowstatus":"C", "rowindex":0,	
    "[Version].[Version Name]" : "CWV_MP",
    "[Group].[Group ID]" : "PAC_77341",
    "[Location].[Location]" : "P306",
    "[Item].[Item]" : "UN50DU7000FXZX",
    "Measure.[Pre Alloc Const by Item_Flag]" : false }
    ]
    }
    */
    var fn_save_exception = function(parsedParams){
        const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
        vdCommon.setLogLevel("Debug"); 
        try{            
            let updateDimension = [];
            let updateMeasure = []; 
            
            for ( var i = 0; i < parsedParams.fbGridRows.length; i++ ) {
                let rowStatus = parsedParams.fbGridRows[i]["rowstatus"];
                let fbVersion =  parsedParams.fbGridRows[i]["[Version].[Version Name]"];
                let fbGroupID = parsedParams.fbGridRows[i]["[Group].[Group ID]"];
                let fbLocation = parsedParams.fbGridRows[i]["[Location].[Location]"];
                let fbItem = parsedParams.fbGridRows[i]["[Item].[Item]"];
                let isFlag = parsedParams.fbGridRows[i]["Measure.[Pre Alloc Const by Item_Flag]"];
                
                updateDimension = [];
                updateMeasure = []; 

                if(rowStatus == "U"){ //Update
                  updateDimension.push("[Version].[Version Name].["+fbVersion+"]");
                  updateDimension.push("[Location].[Location].["+fbLocation+"]");
                  updateDimension.push("[Group].[Group ID].["+fbGroupID+"]");   
                  updateDimension.push("[Item].[Item].["+fbItem+"]");
                 
                  updateMeasure.push("Measure.[Pre Alloc Const by Item_Flag] ="+isFlag +";");
                  
                  vdCommon.updateMeasure(updateDimension, updateMeasure);
                }
            }        
            return { "Code" : 0, "Msg" : "", "Rows" : ""};

        }catch ( e ) {
            return { "Code" : -1, "Msg" : e.message };
        }
    }
    /* ********************************************************************************** */
    // { "fbFuncName" : "fn_save_detail" }
    /* 호출 예제
    {"fbFuncName":"fn_save_detail","fbParams":{"version":"CWV_MP"},
    "fbGridRows" : [
    {"rowstatus":"C", "rowindex":0,	
    "[Version].[Version Name]" : "CWV_MP",
    "[Group].[Group ID]" : "PAC_77341",
    "[Sequence].[Sequence]" : "",
    "[Location].[Location]" : "P306",
    "Measure.[Pre Alloc Const Detail_IsValid]" : false,
    "Week.202508" : "100","Week.202509" : "102","Week.202510" : "100","Week.202511" : "0","Week.202512" : "0" }]
    }
    */
    var fn_save_detail = function(parsedParams){
        const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
        vdCommon.setLogLevel("Debug"); 
        try{
  
            for ( var i = 0; i < parsedParams.fbGridRows.length; i++ ) {
                let rowStatus = parsedParams.fbGridRows[i]["rowstatus"];
                let fbVersion =  parsedParams.fbGridRows[i]["[Version].[Version Name]"];
                let fbGroupID = parsedParams.fbGridRows[i]["[Group].[Group ID]"];
                let fbLocation = parsedParams.fbGridRows[i]["[Location].[Location]"];
                let maxSequence = parsedParams.fbGridRows[i]["[Sequence].[Sequence]"];
                let isValidFlag = parsedParams.fbGridRows[i]["Measure.[Pre Alloc Const Detail_IsValid]"];

                //vdCommon.debug("[Data]["+fbGroupID+"]["+fbLocation+"]["+rowStatus+"]");
                //26주 Bucket 데이타 조회
                let bucketQuery = 'Select ([Time].[Week].filter(#.Key >= &CurrentWeek.element(0).LeadOffset(0).Key && #.Key <= &CurrentWeek.element(0).LeadOffset(26).Key)) on row, () on column ';
                //bucketQuery += "Where {[Time].[Day].filter(#.Name >= "+'"'+starthorizon+'"'+" && #.Name <= "+'"'+endhorizon+'"'+")};";
                
                let bucketResult = vdCommon.selectQueryList("[bucketQuery]" ,bucketQuery );
                let bucketList = vdCommon.fn_makeCombo(bucketResult, {DimName : "Time", DimAttbName : "Week", Sort : "DisplayName"});

                if(rowStatus == "C"){
                    //Max Sequence 조회함.
                    let resultMaxData = vdCommon.selectList(
                        ["[Version].[Version Name].["+fbVersion+"]",
                        "[Location].[Location].["+fbLocation+"]",
                        "[Group].[Group ID].["+fbGroupID+"]",
                        "[Sequence].[Sequence]"],
                        ["Measure.[Pre Alloc Const Detail W_Const Qty]"],
                        "Where {[Time].[Week]} ",
                        "orderby [Sequence].[Sequence].Name desc",
                        "limit 1"
                    );
                    //vdCommon.debug("[length(Max)]" + resultMaxData.cs.rowCount);
                    if(resultMaxData.cs.rowCount > 0){
                        maxSequence = resultMaxData.cs.row(0).cell(resultMaxData.cs.memberColumnIndex("Sequence", "Sequence")).Name; 
                        maxSequence =  parseInt(maxSequence) + 1 ;
                    }else{
                        maxSequence = "1";
                    }
                    //vdCommon.debug("[maxSequence]" + maxSequence);

                    //Member 등록여부
                    var memberSql = "[Sequence].[Sequence] ";
                    if (!vdCommon.existMember(memberSql, maxSequence) ) {
                        vdCommon.createMember(memberSql, maxSequence);
                    }

                    for(var k = 0; k < bucketList.length; k++){
                        let sWeek = bucketList[k]["Name"];
                        let bucketValue = parsedParams.fbGridRows[i]["Week." + sWeek]; 
                        //vdCommon.debug("[bucketValue]["+sWeek+"]["+bucketValue+"]");
                        if(bucketValue == undefined || bucketValue == null){
                            bucketValue = 0;                         
                        }
                        createDimension = [];
                        createMeasure = [];    
                        createDimension.push("[Version].[Version Name].["+fbVersion+"]");
                        createDimension.push("[Location].[Location].["+fbLocation+"]");
                        createDimension.push("[Group].[Group ID].["+fbGroupID+"]");                    
                        createDimension.push("[Sequence].[Sequence].["+maxSequence+"]");
                        createDimension.push("[Time].[Week].["+sWeek+"]");
                        createMeasure.push("Measure.[Pre Alloc Const Detail W_Const Qty] = " + bucketValue + ";" );  
                        vdCommon.createMeasure(createDimension, createMeasure);                      
                    }

                    //Pre Alloc Const Detail
                    dimension = [];
                    measure = [];
                    dimension.push("[Version].[Version Name].["+fbVersion+"]");
                    dimension.push("[Location].[Location].["+fbLocation+"]");            
                    dimension.push("[Group].[Group ID].["+fbGroupID+"]");
                    dimension.push("[Sequence].[Sequence].["+maxSequence+"]");

                    measure.push("Measure.[Pre Alloc Const Detail_IsValid] = "+isValidFlag+";");
                    
                    if(rowStatus == "C"){
                        vdCommon.createMeasure(dimension, measure);
                    }else{
                        vdCommon.updateMeasure(dimension, measure);  
                    }                 
                }else{
                    //UPDATE 처리
                    let updateDimension = [];
                    let updateMeasure = [];

                    for(var k = 0; k < bucketList.length; k++){
                        let sWeek = bucketList[k]["Name"];
                        let bucketValue = parsedParams.fbGridRows[i]["Week." + sWeek]; 

                        if(bucketValue != undefined && bucketValue != null){
                            updateDimension = [];
                            updateMeasure = [];    
                            updateDimension.push("[Version].[Version Name].["+fbVersion+"]");
                            updateDimension.push("[Location].[Location].["+fbLocation+"]");
                            updateDimension.push("[Group].[Group ID].["+fbGroupID+"]");                    
                            updateDimension.push("[Sequence].[Sequence].["+maxSequence+"]");
                            updateDimension.push("[Time].[Week].["+sWeek+"]");
                            updateMeasure.push("Measure.[Pre Alloc Const Detail W_Const Qty] = " + bucketValue + ";" );

                            if(vdCommon.existMeasure(updateDimension, ["Measure.[Pre Alloc Const Detail W_Const Qty]"], "")){
                                vdCommon.updateMeasure(updateDimension, updateMeasure);
                            }else{
                                vdCommon.createMeasure(updateDimension, updateMeasure);
                            }   
                        }
                    }
                    //Pre Alloc Const Detail
                    updateDimension = [];
                    updateMeasure = [];
                    updateDimension.push("[Version].[Version Name].["+fbVersion+"]");
                    updateDimension.push("[Location].[Location].["+fbLocation+"]");            
                    updateDimension.push("[Group].[Group ID].["+fbGroupID+"]");
                    updateDimension.push("[Sequence].[Sequence].["+maxSequence+"]");

                    updateMeasure.push("Measure.[Pre Alloc Const Detail_IsValid] = "+isValidFlag+";");

                    vdCommon.updateMeasure(updateDimension, updateMeasure); 
                }
            }        
            return { "Code" : 0, "Msg" : "", "Rows" : ""};

        }catch ( e ) {
            return { "Code" : -1, "Msg" : e.message };
        }
    }
    
    var fn_filterItemStatus= function(parsedParams){
        const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
        vdCommon.setLogLevel("Debug"); 
        try{
            let fbFilter = vdUtil.fn_getFilter(parsedParams, "[Filter].[Filter]");
            let fbFilterValue = fbFilter["SelectedMembersExp"];
            let ibplQuery = "";
            if(!(fbFilterValue == undefined && fbFilterValue == "")){
                vdCommon.debug("[Filter Value]"+ fbFilterValue);
                //fbFilterValue = "."+ fbFilterValue.replace(/#.[FilterPLCStatusWithDeleted]/g, "Measure.[BOD Item_Cur Status]");
                let startIndex = fbFilterValue.indexOf("{");
                let endIndex = fbFilterValue.indexOf("}");
                ibplQuery = '.filter(Measure.[BOD Item_Cur Status] in '+fbFilterValue.substring(startIndex, endIndex+1 )+')';
            }
            vdCommon.programEnd();                          
            return { "Code" : 0, "Msg" : "", "Rows" : [{Name : ibplQuery}] };

        }catch ( e ) {
            return { "Code" : -1, "Msg" : e.message };
        }
    };
    
    /* 관련 Measure Group 
    1. Pre Alloc Const
    2. Pre Alloc Const Detail
    3. Pre Alloc Const Detail W
    4. Pre Alloc Const Filter
    5. Pre Alloc Const by Item
    */
    var fn_merge = function(parsedParams){
        const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
        vdCommon.setLogLevel("Debug"); 
        try{
            var userName = vdCommon.fn_getUserId();
            vdCommon.debug("[User Name]" + userName);            
            let fbVersion = vdUtil.fn_getFilterValue(parsedParams,"[Version].[Version Name]");
            let dimensionQuery = [];
            let comboList = [];
            let arrayGroupID = [];
            let deleteWhere = [];
            let deleteMeasureGroup = "";

            let dimensionInfo = [];
            let measureInfo = [];
            let measureUpdateInfo = [];
            let whereQuery = 'Where {(Measure.[Pre Alloc Const_Updated By] == CurrentUser().[User Name] ||  Measure.[Pre Alloc Const_Updated By] == CurrentUser().Name)}';

            dimensionInfo.push("[Version].[Version Name]");
            dimensionInfo.push("[Group].[Group ID]");
            measureInfo.push("Measure.[Pre Alloc Const_AP2]");
            measureInfo.push("Measure.[Pre Alloc Const_AP2 Code]");
            measureInfo.push("Measure.[Pre Alloc Const_Created By]");
            measureInfo.push("Measure.[Pre Alloc Const_Creation Time]");
            measureInfo.push("Measure.[Pre Alloc Const_Exception]");
            measureInfo.push("Measure.[Pre Alloc Const_From Site]");
            measureInfo.push("Measure.[Pre Alloc Const_From Site ID]");
            measureInfo.push("Measure.[Pre Alloc Const_GC]");
            measureInfo.push("Measure.[Pre Alloc Const_GC Code]");
            measureInfo.push("Measure.[Pre Alloc Const_Grp Description]");
            measureInfo.push("Measure.[Pre Alloc Const_Grp1]");
            measureInfo.push("Measure.[Pre Alloc Const_Grp2]");
            measureInfo.push("Measure.[Pre Alloc Const_Inch]");
            measureInfo.push("Measure.[Pre Alloc Const_Item]");
            measureInfo.push("Measure.[Pre Alloc Const_MKT Name]");
            measureInfo.push("Measure.[Pre Alloc Const_Product Grp]");
            measureInfo.push("Measure.[Pre Alloc Const_Project]");
            measureInfo.push("Measure.[Pre Alloc Const_Year]");   
           
            measureUpdateInfo.push(vdCommon.fn_mergeUser("Measure.[Pre Alloc Const_Updated By]",fbVersion));            
            measureUpdateInfo.push(vdUtil.fn_qMeaUpdateTime("Measure.[Pre Alloc Const_Update Time]"));
            
            if(parsedParams.fbParams.commitType == 1){
                //Check 한 데이타 Merge
                for(var k=0; k < parsedParams.fbGridRows.length; k++ ){
                    dimensionQuery = [];
                    for(var j=0; j < dimensionInfo.length; j++){
                        let dim = dimensionInfo[j];
                        if(dim == "[Version].[Version Name]"){
                            dimensionQuery.push(dim + ".["+fbVersion+"]");
                        }else{
                            dimensionQuery.push(dim + ".["+ parsedParams.fbGridRows[k][dim] + "]");
                        }
                    }

                    let result= vdCommon.selectList(dimensionQuery, measureInfo, whereQuery, "", "");
                    comboList = vdCommon.fn_makeCombo(result, {
                        DimName: "Group", DimAttbName: "Group ID", Sort: "DisplayName",
                        existAll: false,isDisplayNameWithCode: false});

                    arrayGroupID = comboList.map((value) => value.Name);
                    vdCommon.debug("arrayGroupID : " + JSON.stringify(arrayGroupID));
                    fn_mergeScope(result, dimensionInfo, measureInfo, measureUpdateInfo, fbVersion);
                }
            }else{
                dimensionQuery = [];
                for(var j=0; j < dimensionInfo.length; j++){
                    let dim = dimensionInfo[j];
                    if(dim == "[Version].[Version Name]"){
                        dimensionQuery.push(dim + ".["+fbVersion+"]");
                    }else{
                        dimensionQuery.push(dim);
                    }
                }

                let result= vdCommon.selectList(dimensionQuery, measureInfo, whereQuery, "", "");
                comboList = vdCommon.fn_makeCombo(result, {
                    DimName: "Group", DimAttbName: "Group ID", Sort: "DisplayName",
                    existAll: false,isDisplayNameWithCode: false});

                arrayGroupID = comboList.map((value) => value.Name);
                vdCommon.debug("arrayGroupID : " + JSON.stringify(arrayGroupID));
                //fn_mergeSetting(dimensionInfo, measureInfo, whereQuery, fbVersion, arrayGroupID);
                fn_mergeScope(result, dimensionInfo, measureInfo, measureUpdateInfo, fbVersion);
            }
            //++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
            //Pre Alloc Const Detail
            //++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
            dimensionInfo = [];
            measureInfo = [];
            measureUpdateInfo = [];
            whereQuery = '';

            dimensionInfo.push("[Version].[Version Name]");
            dimensionInfo.push("[Location].[Location]");
            dimensionInfo.push("[Group].[Group ID]");
            dimensionInfo.push("[Sequence].[Sequence]");

            measureInfo.push("Measure.[Pre Alloc Const Detail_IsValid]");

            vdCommon.debug("[Pre Alloc Const Detail]");
            fn_mergeSetting(dimensionInfo, measureInfo, whereQuery, measureUpdateInfo, fbVersion, arrayGroupID);
            //++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
            //Pre Alloc Const Detail W
            //++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
            dimensionInfo = [];
            measureInfo = [];
            measureUpdateInfo = [];
            whereQuery = 'Where {(Measure.[Pre Alloc Const Detail W_Updated By] == CurrentUser().[User Name] ||  Measure.[Pre Alloc Const Detail W_Updated By] == CurrentUser().Name)}'; 

            dimensionInfo.push("[Version].[Version Name]");
            dimensionInfo.push("[Location].[Location]");
            dimensionInfo.push("[Time].[Week]");
            dimensionInfo.push("[Group].[Group ID]");
            dimensionInfo.push("[Sequence].[Sequence]");

            measureInfo.push("Measure.[Pre Alloc Const Detail W_Const Qty]");

            measureUpdateInfo.push(vdCommon.fn_mergeUser("Measure.[Pre Alloc Const Detail W_Updated By]",fbVersion));            
            measureUpdateInfo.push(vdUtil.fn_qMeaUpdateTime("Measure.[Pre Alloc Const Detail W_Update Time]"));            
            vdCommon.debug("[Pre Alloc Const Detail W]");
            //++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
            //Delete가 필요함.
            deleteWhere = [];
            deleteMeasureGroup = "Pre Alloc Const Detail W";
            deleteWhere.push("[Version].[Version Name].[CWV_MP]");
            deleteWhere.push("[Group].[Group ID]"+vdUtil.fn_filterStr(arrayGroupID));            
            vdCommon.deleteMeasure(deleteWhere, deleteMeasureGroup)            
            //++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
            fn_mergeSetting(dimensionInfo, measureInfo, whereQuery, measureUpdateInfo, fbVersion, arrayGroupID);

            //++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
            //Pre Alloc Const Filter
            //++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
            dimensionInfo = [];
            measureInfo = [];
            measureUpdateInfo = [];
            whereQuery = ''; 

            dimensionInfo.push("[Version].[Version Name]");
            dimensionInfo.push("[Location].[Location]");
            dimensionInfo.push("[Sales Domain].[AP2]");
            dimensionInfo.push("[Group].[Group ID]");
            dimensionInfo.push("[Item].[Item Std1]");

            measureInfo.push("Measure.[Pre Alloc Const Filter_Asn]");
            vdCommon.debug("[Pre Alloc Const Filter]");
            //++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
            //Delete가 필요함.
            deleteWhere = [];
            deleteMeasureGroup = "Pre Alloc Const Filter";
            deleteWhere.push("[Version].[Version Name].[CWV_MP]");
            deleteWhere.push("[Group].[Group ID]"+vdUtil.fn_filterStr(arrayGroupID));            
            vdCommon.deleteMeasure(deleteWhere, deleteMeasureGroup)            
            //++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
            fn_mergeSetting(dimensionInfo, measureInfo, whereQuery, measureUpdateInfo, fbVersion, arrayGroupID);

            //+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
            //Pre Alloc Const by Item
            //++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
            dimensionInfo = [];
            measureInfo = [];
            measureUpdateInfo = [];
            whereQuery = 'Where {(Measure.[Pre Alloc Const by Item_Updated By] == CurrentUser().[User Name] ||  Measure.[Pre Alloc Const by Item_Updated By] == CurrentUser().Name)}'; 
            
            dimensionInfo.push("[Version].[Version Name]");
            dimensionInfo.push("[Location].[Location]");
            dimensionInfo.push("[Group].[Group ID]");
            dimensionInfo.push("[Item].[Item]");

            measureInfo.push("Measure.[Pre Alloc Const by Item_BOD Item ToSite]");
            measureInfo.push("Measure.[Pre Alloc Const by Item_Created By]");
            measureInfo.push("Measure.[Pre Alloc Const by Item_Creation Time]");
            measureInfo.push("Measure.[Pre Alloc Const by Item_Flag]");
            measureInfo.push("Measure.[Pre Alloc Const by Item_PLC Status]");

            measureUpdateInfo.push(vdCommon.fn_mergeUser("Measure.[Pre Alloc Const by Item_Updated By]",fbVersion));            
            measureUpdateInfo.push(vdUtil.fn_qMeaUpdateTime("Measure.[Pre Alloc Const by Item_Update Time]"));             
            vdCommon.debug("[Pre Alloc Const by Item]");
            //++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
            //Delete가 필요함.
            deleteWhere = [];
            deleteMeasureGroup = "Pre Alloc Const by Item";
            deleteWhere.push("[Version].[Version Name].[CWV_MP]");
            deleteWhere.push("[Group].[Group ID]"+vdUtil.fn_filterStr(arrayGroupID));            
            vdCommon.deleteMeasure(deleteWhere, deleteMeasureGroup)            
            //++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
            fn_mergeSetting(dimensionInfo, measureInfo, whereQuery, measureUpdateInfo, fbVersion, arrayGroupID);

            //++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++     
            return { "Code" : 0, "Msg" : "" };

        } catch ( e ) {
            return { "Code" : -1, "Msg" : e.message };
        }
    }

    var fn_mergeSetting = function(dimensionInfo, measureInfo, whereQuery, measureUpdateInfo, sVersion, arrayGroupID){        
        const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
        vdCommon.setLogLevel("Debug"); 
        try{
            let dimensionQuery = [];
            vdCommon.debug("[fn_mergeSetting]"+dimensionInfo.length);
            for(var j=0; j < dimensionInfo.length; j++){

                if(dimensionInfo[j] == "[Version].[Version Name]"){
                    dimensionQuery.push(dimensionInfo[j] + ".["+sVersion+"]");
                }else if(dimensionInfo[j] == "[Group].[Group ID]"){
                    dimensionQuery.push(dimensionInfo[j] + vdUtil.fn_filterStr(arrayGroupID));
                }else{
                    dimensionQuery.push(dimensionInfo[j]);
                }
            }
            vdCommon.debug("<DIM> " + JSON.stringify(dimensionQuery));
            vdCommon.debug("<Measure> " + JSON.stringify(measureInfo));
            vdCommon.debug("<Where> " +whereQuery);
            result= vdCommon.selectList(dimensionQuery, measureInfo, whereQuery, "", "");
            fn_mergeScope(result, dimensionInfo, measureInfo,measureUpdateInfo, sVersion);

        }catch ( e ) {
            this.error(e.message);
            throw e;
        }

    }   

    var fn_mergeScope = function(result, dimensionInfo, measureInfo, measureUpdateInfo, sVersion){
        const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
        vdCommon.setLogLevel("Debug"); 
        try{
            vdCommon.debug("[fn_mergeScope] Count:" +result.cs.rowCount);
            for(var k=0; k < result.cs.rowCount ; k++){
                let dimension = [];
                let changeMeasure = [];                
                // Dimension 처리
                for(var i=0; i < dimensionInfo.length ; i++){
                    if(dimensionInfo[i] == "[Version].[Version Name]"){
                        dimension.push(dimensionInfo[i] +".[CWV_MP]");
                    //}else if(dimensionInfo[i] == "[Group].[Group ID]"){
                     //   dimension.push(dimensionInfo[i] +vdUtil.fn_filterStr(sGroupID));
                    }else{                        
                        let dim = dimensionInfo[i].split(".");
                        let dimValue = result.cs.row(k).cell(result.cs.memberColumnIndex(dim[0].replace("[","").replace("]",""), dim[1].replace("[","").replace("]",""))).Name;
                        vdCommon.debug(dim +"["+dimValue+"]");
                        dimension.push(dimensionInfo[i] + ".["+dimValue+"]");
                    }
                    
                }
                vdCommon.debug("For-End[Dim Info]"+JSON.stringify(dimension));
                //Measure 처리
                vdCommon.debug("[fn_mergeScope] Measure Info:" +measureInfo.length);
                for(var j=0; j < measureInfo.length ; j++){  
                    changeMeasure.push(vdUtil.fn_qMeaForMerge(measureInfo[j], sVersion));
                }

                for(var m=0; m < measureUpdateInfo.length; m++){                    
                    changeMeasure.push(measureUpdateInfo[m]);
                }
                
                vdCommon.createMeasure(dimension, changeMeasure);
            }

        } catch ( e ) {
            return { "Code" : -1, "Msg" : e.message };
        }      
    }
    
    /************************************************************************************/

/************************************************* Mapping logic *************************************************/
    // Mapping 함수 정의, 마지막에 선언을 해야 함수를 정상적으로 인식함
    const functionMap = {
        "fn_cb_group1" : fn_cb_group1,
        "fn_cb_group2" : fn_cb_group2,
        "fn_save":fn_save,
        "fn_save_exception":fn_save_exception,
        "fn_save_detail":fn_save_detail,
        "fn_cb_groupId":fn_cb_groupId
        ,"fn_filterItemStatus":fn_filterItemStatus
        ,"fn_merge" :fn_merge
    };

    return {
        fn_loadFunction : fn_loadFunction
    };    
});