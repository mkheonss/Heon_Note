define('o9.NSCM.JSCTNGroupConstraint', ['o9/data/query', 'o9/data/cellset', 'o9.NSCM.commonLib'], function(){	
	const programName = "o9.NSCM.JSCTNGroupConstraint";
    const productGroupNameSet = "&NSUISetItemProductGroupView";
    const itemStage = "SET";    

    function fn_strSplit(val,separator){
        try{
            const commonLib = require('o9.NSCM.commonLib');
            const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
            vdCommon.setLogLevel("Debug");        

            var rtnArry = String(val).split(separator);

            for(var k=0; k < rtnArry.length; k++){
                rtnArry[k] = rtnArry[k].replace("null","");
                rtnArry[k] = rtnArry[k].replace(/^\s+|\s+$/g,"");
            }
            vdCommon.debug("[fn_strSplit]" + JSON.stringify(rtnArry));
            return rtnArry;   
        } catch ( e ) {
            RuleOutputToUI = { Status : 'Error', Message : "Js Logic Error : " + e.message };
            return;
        }             
    }

    function fn_filter(val) {     
        try{
            const commonLib = require('o9.NSCM.commonLib');
            const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
            vdCommon.setLogLevel("Debug");  

            //vdCommon.printStep("[fn_filter]");   
            if ( val == "All" || val == "%") {
                return "";
            } else if ( Array.isArray(val) ) {
                return '#.Name in {' + val.map(item => `"${item}"`).join(",") + '}';
            } else if ( val.indexOf("%") == -1 ) {
                return '#.Name == "' + val + '"';
            } else if ( val.indexOf("%") == 0 ) {
                return '#.Name endswith "' + val.replace("%","") + '"';
            } else if ( val.indexOf("%") == val.length - 1 ) {
                return '#.Name startswith "' + val.replace("%","") + '"';
            } else if(val.indexOf("%") == val.length - 1  && val.indexOf("%") == 0){
                return '#.Name contains "' + val.replace("%","") + '"';
            } else {
                return "";
            }
        } catch ( e ) {
            RuleOutputToUI = { Status : 'Error', Message : "Js Logic Error : " + e.message };
            return;
        }  
    }

    function fn_ParamsCheck(val){
        try{
            const commonLib = require('o9.NSCM.commonLib');
            const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
            vdCommon.setLogLevel("Debug");
            //vdCommon.debug("TEST[fn_ParamsCheck]["+val+"]");
            var rtnValue = true;
            
            if(val === "" || val === "-" || val === null || val === undefined){
                rtnValue = false;
            }else{
                val = val.toString();
                if(val.toUpperCase().indexOf("ALL") != -1) 
                    rtnValue = false;
                else 
                    rtnValue = true;
            }
            vdCommon.debug("TEST[fn_ParamsCheck]["+val+"]["+rtnValue+"]");
            return rtnValue;
        } catch ( e ) {
            RuleOutputToUI = { Status : 'Error', Message : "Js Logic Error : " + e.message };
            return;
        }
    }

    function fn_valueCheck(val, checkValue, replaceFalg){
       try{
            const commonLib = require('o9.NSCM.commonLib');
            const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
            vdCommon.setLogLevel("Debug");

            if(val === "null" ||val === null || val === "-" || val === undefined){
                return rtnValue = "";
            }

            var strVal = val.toString().toUpperCase();
            var strCheckValue = checkValue.toUpperCase();
            var rtnValue = val;

            if(String(strVal).indexOf(strCheckValue) != -1) {
                rtnValue =  checkValue;                
            }else{
                rtnValue = val;
            }
            if(replaceFalg == "Y" && rtnValue === ""){
                rtnValue = "All";
            }
            return rtnValue;
        } catch ( e ) {
            RuleOutputToUI = { Status : 'Error', Message : "Js Logic Error : " + e.message };
            return;
        }
    } 

    /*whereQuery 
    * @param {array} whereQuery - Where Query
    * @param {array} orderbyQuery - OrderBy Query    dkgk
    */
    function fn_ibplWhereQuery(whereQuery, orderbyQuery){
        try{
            const commonLib = require('o9.NSCM.commonLib');
            const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
            vdCommon.setLogLevel("Debug");

            let rtnWhereQuery = "";
            if(whereQuery.length == 0 && orderbyQuery.length == 0){
                return ";";
            }

            if(whereQuery.length > 0){
                rtnWhereQuery= " Where {" + whereQuery.join(',') + "}" ;
            }

            if(orderbyQuery.length == 0){
                rtnWhereQuery += ";";
            }else{
                rtnWhereQuery +=" orderby "+orderbyQuery.join(',')+";"
            }
            //vdCommon.debug("[fn_ibplWhereQuery]" + rtnWhereQuery);
            return rtnWhereQuery;
        }catch ( e ) {
            RuleOutputToUI = { Status : 'Error', Message : "Js Logic Error : " + e.message };
            return;
        }
    }    

    function fn_multiCheckName(val){
        //멀티 선택 값을 Where 조건으로 넘기기 위해 처리함.
        try{
            const commonLib = require('o9.NSCM.commonLib');
            const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
            vdCommon.setLogLevel("Debug");
            var rtnChkList = "";
            var dataList = String(val).split(",");
            for(var k=0; k < dataList.length; k++){
                var sData = dataList[k];
    
                rtnChkList += '"' +sData + '"';    
                if ((k + 1) < dataList.length){
                    rtnChkList += ','
                }
            }
            //vdCommon.printStep("[fn_multiCheckName]" + rtnChkList );
            return rtnChkList;
        }catch ( e ) {
            RuleOutputToUI = { Status : 'Error', Message : "Js Logic Error : " + e.message };
            return;
        }
    }

    function fn_multiCheckDisplayName(val, dimension){
        try{
            const commonLib = require('o9.NSCM.commonLib');
            const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
            const vdUtil = new commonLib.VdUtil();
            vdCommon.setLogLevel("Debug");

            //All check
            if(val.toString().toUpperCase().indexOf("ALL") != -1){
                return "All";
            }
            var rtnChkList = "";
            rtnChkList = val.map(item => vdCommon.fn_getCodeName(dimension, `${item}`)).join(",");

            return rtnChkList;
        }catch ( e ) {
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
''
            //BOD List 메져에서 조회함.
            let dimensionQuery = [];
            dimensionQuery.push("[Version].[Version Name].["+fbVersion+"]");
            //dimensionQuery.push("&MFLocation");
            //2025.06.10 
            dimensionQuery.push("&MFStageSETLocation.filter(#.[Location Valid Flag]==true)");
            
            let measureQuery = [];
            measureQuery.push("Measure.[BOD List_Eff Enddate]"); 
            measureQuery.push("Measure.[BOD List_Eff Startdate]"); 

            let whereQuery = "Where {";
            whereQuery += "[Sub Location].[Sub Location]" ;
            whereQuery += ",[Trans Mode].[Trans Mode]" ;
            //whereQuery += ",(coalesce(Measure.[BOD List_Eff Startdate],DATEADD(Now(),-1,"+'"Day"'+")) < now())";
            //whereQuery += ",(coalesce(Measure.[BOD List_Eff Enddate],DATEADD(Now(),-1,"+'"Day"'+")) < now())";
            whereQuery += "}";

            var selectResult = vdCommon.selectList(dimensionQuery, measureQuery, whereQuery ,"","");
            let comboList = vdCommon.fn_makeCombo(selectResult, {DimName : "Location", DimAttbName : "Location", existAll : false, Sort : "DisplayName", isDisplayNameWithCode : true});
    
            vdCommon.programEnd();

            return comboList;
        } catch ( e ) {
            RuleOutputToUI = { Status : 'Error', Message : "Js Logic Error : " + e.message };
            return;
        }       
    } 

    function fn_salesGCCombo(o9Params){
        try{
            const commonLib = require('o9.NSCM.commonLib');
            const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
            const vdUtil = new commonLib.VdUtil();
            vdCommon.setLogLevel("Debug");

            // 파라메타 가져오기
            let parsedParams = JSON.parse(o9Params); 
            let fbVersion = parsedParams.fbVersion;
            let fbLocation = parsedParams.fbLocation;

            let dimensionQuery =[];
            dimensionQuery.push('[Sub Location].[Sub Location GC].filter(~(#.Name in {"All", "-"}))');

            let measureQuery = [];
            measureQuery.push("Measure.[BOD Item_asn] ");

            let whereQuery = "Where {";
            whereQuery += "[Version].[Version Name].["+fbVersion+"]";
            whereQuery += ",[Location].[Location].["+fbLocation+"]";
            whereQuery += ",&NSUISubLocationDC";            
            whereQuery += ",[Item].[Item]";
            whereQuery += ",[Trans Mode].[Trans Mode]";
            whereQuery += ",(Measure.[BOD Item_asn] >-1)";
            whereQuery += "}";

            let selectResult = vdCommon.selectList(dimensionQuery, measureQuery, whereQuery ,"","");
            let comboList = vdCommon.fn_makeCombo(selectResult, {DimName : "Sub Location", DimAttbName : "Sub Location GC", existAll : true, Sort : "DisplayName", isDisplayNameWithCode : false});
            var dateGC = comboList.map((value) => value.Name);

            let result = vdCommon.selectList(["[Sales Domain].[GC]" +vdUtil.fn_filterStr(dateGC)],[],"","","");
            comboList = vdCommon.fn_makeCombo(result, {DimName : "Sales Domain", DimAttbName : "GC", Sort :"DisplayName", existAll : false, isDisplayNameWithCode : true});
            
            comboList.unshift({ Name : "All", DisplayName : "All"});
    
            vdCommon.programEnd();

            return comboList;
        }catch ( e ) {
            RuleOutputToUI = { Status : 'Error', Message : "Js Logic Error : " + e.message };
            return;
        }
    }

    function fn_salesAP2Combo(o9Params){
        try{
            const commonLib = require('o9.NSCM.commonLib');
            const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
            const vdUtil = new commonLib.VdUtil();
            vdCommon.setLogLevel("Debug");

            // 파라메타 가져오기
            let parsedParams = JSON.parse(o9Params); 
            let fbVersion = parsedParams.fbVersion;
            let fbLocation = parsedParams.fbLocation;
            let fbGC = parsedParams.fbGC;

            let dimensionQuery =[];
            dimensionQuery.push('[Sub Location].[Sub Location Rep AP2].filter(~(#.Name in {"All", "-"}))');

            let measureQuery = [];
            measureQuery.push("Measure.[BOD Item_asn] ");

            let whereQuery = "Where {";
            whereQuery += "[Version].[Version Name].["+fbVersion+"]";
            whereQuery += ",[Location].[Location].["+fbLocation+"]";
            whereQuery += ",&NSUISubLocationDC";
            
            if(fbGC != "All" ){
                whereQuery += ",[Sub Location].[Sub Location GC]"+vdUtil.fn_filterStr(fbGC);
            }
            whereQuery += ",[Item].[Item]";
            whereQuery += ",[Trans Mode].[Trans Mode]";
            whereQuery += ",(Measure.[BOD Item_asn] >-1)";
            whereQuery += "}";

            let selectResult = vdCommon.selectList(dimensionQuery, measureQuery, whereQuery ,"","");
            let comboList = vdCommon.fn_makeCombo(selectResult, {DimName : "Sub Location", DimAttbName : "Sub Location Rep AP2", existAll : false, Sort : "DisplayName", isDisplayNameWithCode : false});
            var dateAP2 = comboList.map((value) => value.Name);
            vdCommon.printStep("[comboList]"+JSON.stringify(dateAP2));
            let result = vdCommon.selectList(["[Sales Domain].[AP2]" +vdUtil.fn_filterStr(dateAP2)],[],"","","");
            comboList = vdCommon.fn_makeCombo(result, {DimName : "Sales Domain", DimAttbName : "AP2", Sort :"DisplayName", existAll : false, isDisplayNameWithCode : true});   

            comboList.unshift({ Name : "All", DisplayName : "All"});
    
            vdCommon.programEnd();

            return comboList; 
        }catch ( e ) {
            RuleOutputToUI = { Status : 'Error', Message : "Js Logic Error : " + e.message };
            return;
        }    
    }

    function fn_productGroupCombo(o9Params){
        try{
            const commonLib = require('o9.NSCM.commonLib');
            const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
            const vdUtil = new commonLib.VdUtil();
            vdCommon.setLogLevel("Debug");

            // 파라메타 가져오기
            vdCommon.printParams(o9Params);
            let parsedParams = JSON.parse(o9Params); 

            let selectQuery = 'Select ('+productGroupNameSet+');';

            let selectResult = vdCommon.selectQueryList("[fn_productGroupCombo]" ,selectQuery );
            let comboList = vdCommon.fn_makeCombo(selectResult, {DimName : "Item", DimAttbName : "Product Group", existAll : true, Sort : "DisplayName", isDisplayNameWithCode : false});
    
            vdCommon.programEnd();

            return comboList;
        }catch ( e ) {
            RuleOutputToUI = { Status : 'Error', Message : "Js Logic Error : " + e.message };
            return;
        }
    }

    function fn_projectCombo(o9Params){
        try{
            const commonLib = require('o9.NSCM.commonLib');
            const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
            const vdUtil = new commonLib.VdUtil();
            vdCommon.setLogLevel("Debug");
            
            // 파라메타 가져오기
            vdCommon.printParams(o9Params);
            let parsedParams = JSON.parse(o9Params); 
            let fbVersion = parsedParams.fbVersion;
            let productGroupList = parsedParams.fbProductGroup;

            let selectQuery = 'Select ([Item].[Item Stage].[SET].relatedmembers([Project]).filter(~(#.Name =="-"))) ';

            let whereQuery = [];
            let orderByQuery = [];
            //if(fn_ParamsCheck(productGroupList)){    
                whereQuery.push('[Item].[Product Group]'+vdUtil.fn_filterStr(productGroupList));
            //}
            orderByQuery.push('[Item].[Project].DisplayName');
            selectQuery += fn_ibplWhereQuery(whereQuery, orderByQuery);

            let selectResult = vdCommon.selectQueryList("[fn_projectCombo]" ,selectQuery );
            let comboList = vdCommon.fn_makeCombo(selectResult, {DimName : "Item", DimAttbName : "Project", existAll : true, Sort : "DisplayName", isDisplayNameWithCode : false});

            if(comboList.length == 0){
                comboList.unshift({ Name : "All", DisplayName : "All"});
            }
   
            vdCommon.programEnd();
            return comboList;
        }catch ( e ) {
            RuleOutputToUI = { Status : 'Error', Message : "Js Logic Error : " + e.message };
            return;
        }
    }   

    function fn_seriesNameCombo(o9Params){
        try{
            const commonLib = require('o9.NSCM.commonLib');
            const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
            const vdUtil = new commonLib.VdUtil();
            vdCommon.setLogLevel("Debug");
            
            // 파라메타 가져오기
            vdCommon.printParams(o9Params);
            let parsedParams = JSON.parse(o9Params); 
            let fbVersion = parsedParams.fbVersion;
            let productGroupList = parsedParams.fbProductGroup;
            let projectList = parsedParams.fbProject;          

            let selectQuery = 'Select ([Item].[Item Stage].[SET].relatedmembers([Series Name]).filter(~(#.Name =="-")))';
            let whereQuery = [];
            let orderByQuery = [];            

            if(fn_ParamsCheck(productGroupList)){    
                //whereQuery.push('[Item].[Product Group].filter(#.Name in {'+fn_multiCheckName(productGroupList, "[Item].[Product Group]")+'})');
                whereQuery.push('[Item].[Product Group]'+vdUtil.fn_filterStr(productGroupList));
            }

            if(fn_ParamsCheck(projectList)){    
                whereQuery.push('[Item].[Project]'+vdUtil.fn_filterStr(projectList));
            }

            orderByQuery.push('[Item].[Series Name].DisplayName');

            selectQuery += fn_ibplWhereQuery(whereQuery, orderByQuery);

            let selectResult = vdCommon.selectQueryList("[fn_seriesNameCombo]" ,selectQuery );            
            let comboList = vdCommon.fn_makeCombo(selectResult, {DimName : "Item", DimAttbName : "Series Name", existAll : true, Sort : "DisplayName", isDisplayNameWithCode : false});

            if(comboList.length == 0){
                comboList.unshift({ Name : "All", DisplayName : "All"});
            }

            vdCommon.programEnd();
    
            return comboList;
        }catch ( e ) {
            RuleOutputToUI = { Status : 'Error', Message : "Js Logic Error : " + e.message };
            return;
        }
    }  

    function fn_inchCombo(o9Params){
        try{
            const commonLib = require('o9.NSCM.commonLib');
            const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
            const vdUtil = new commonLib.VdUtil();
            vdCommon.setLogLevel("Debug");

            // 파라메타 가져오기
            vdCommon.printParams(o9Params);
            let parsedParams = JSON.parse(o9Params); 
            let fbVersion = parsedParams.fbVersion;
            let productGroupList = parsedParams.fbProductGroup;
            let projectList = parsedParams.fbProject;
            let serieNameList = parsedParams.fbSeriesName;

            let whereQuery = [];
            let orderByQuery = [];
            //let selectQuery = 'Select ([Item].[Item Stage].['+itemStage+'] * [Item].[Inch].filter(~(#.Name in {"All", "-"})) ) on row, () on column ';
            let selectQuery = 'Select ([Item].[Item Stage].[SET].relatedmembers([Inch]).filter(~(#.Name =="-"))) ';

            if(fn_ParamsCheck(productGroupList)){    
                whereQuery.push('[Item].[Product Group]' + vdUtil.fn_filterStr(productGroupList));
            }            

            if (fn_ParamsCheck(projectList)){
                whereQuery.push('[Item].[Project]' + vdUtil.fn_filterStr(projectList));
            }

            if(fn_ParamsCheck(serieNameList)){
                whereQuery.push('[Item].[Series Name]' + vdUtil.fn_filterStr(serieNameList));
            }
            
            //orderByQuery.push('[Item].[Inch].DisplayName');

            selectQuery += fn_ibplWhereQuery(whereQuery, orderByQuery);

            let selectResult = vdCommon.selectQueryList("[fn_inchCombo]" ,selectQuery );
            let comboList = vdCommon.fn_makeCombo(selectResult, {DimName : "Item", DimAttbName : "Inch", existAll : false, Sort : "DisplayName", isDisplayNameWithCode : false});  
            
            if(comboList.length > 0 ){
                //숫자가 아닌 것은 제외시킴
                comboList = comboList.filter(function(item1, idx1){
                    return parseInt(item1.Name);
               });
               // 숫자를 Sort시킴
               comboList.sort((a, b) => {
                //console.log("["+parseInt(a.name)+"]["+parseInt(b.name)+"]");                 
                if ( parseInt(a.Name) < parseInt(b.Name) ) return -1;
                if ( parseInt(a.Name) > parseInt(b.Name) ) return 1;
                return 0;
                });
            }
            //if(comboList.length == 0 ){
            comboList.unshift({ Name : "All", DisplayName : "All"}); //All 맨앞에 넣는다.
            //}           
            vdCommon.programEnd();
    
            return comboList;
        }catch ( e ) {
            RuleOutputToUI = { Status : 'Error', Message : "Js Logic Error : " + e.message };
            return;
        }
    }  

    function fn_yearCombo(o9Params){        
        try{
            const commonLib = require('o9.NSCM.commonLib');
            const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
            const vdUtil = new commonLib.VdUtil();
            vdCommon.setLogLevel("Debug");

            // 파라메타 가져오기
            vdCommon.printParams(o9Params);
            let parsedParams = JSON.parse(o9Params); 
            let fbVersion = parsedParams.fbVersion;
            let productGroupList = parsedParams.fbProductGroup;
            let projectList = parsedParams.fbProject;
            let seriesNameList = parsedParams.fbSeriesName;
            let inchList = parsedParams.fbInch;

            let whereQuery = [];
            let orderByQuery = [];
            let selectQuery = 'Select ([Item].[Item Stage].[SET].relatedmembers([Year]).filter(~(#.Name =="-"))) ';

            if(fn_ParamsCheck(productGroupList)){    
                whereQuery.push('[Item].[Product Group]' + vdUtil.fn_filterStr(productGroupList));
            }

            if (fn_ParamsCheck(projectList)) {
                whereQuery.push('[Item].[Project]'+ vdUtil.fn_filterStr(projectList));
            }
            //Series 조건
            if(fn_ParamsCheck(seriesNameList)){            
                whereQuery.push('[Item].[Series Name]'+ vdUtil.fn_filterStr(seriesNameList));
            }
            //Inch 조건
            if(fn_ParamsCheck(inchList)){  
                whereQuery.push('[Item].[Inch]'+ vdUtil.fn_filterStr(inchList));
            }

            orderByQuery.push('[Item].[Year].DisplayName desc') ;        
            selectQuery += fn_ibplWhereQuery(whereQuery, orderByQuery);

            var selectResult = vdCommon.selectQueryList("[fn_year]", selectQuery);
            let comboList = vdCommon.fn_makeCombo(selectResult, {DimName : "Item", DimAttbName : "Year", existAll : false, Sort : "DisplayName", isDisplayNameWithCode : false});    
                  
            if(comboList.length >0 ){
                //숫자가 아닌 것은 제외시킴
                comboList = comboList.filter(function(item1, idx1){
                    return parseInt(item1.Name);
               });
               // 숫자를 Sort시킴
               comboList.sort((a, b) => {
                //console.log("["+parseInt(a.name)+"]["+parseInt(b.name)+"]");                 
                if ( parseInt(a.Name) < parseInt(b.Name) ) return 1;
                if ( parseInt(a.Name) > parseInt(b.Name) ) return -1;
                return 0;
                });
            }
            //if(comboList.length == 0 ){
            comboList.unshift({ Name : "All", DisplayName : "All"});
            //}
            vdCommon.programEnd();
    
            return comboList;
        }catch ( e ) {
            RuleOutputToUI = { Status : 'Error', Message : "Js Logic Error : " + e.message };
            return;
        }
    }

    function fn_itemCombo_SalesItem(o9Params){
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
            let productGroupList = parsedParams.fbProductGroup;
            let projectList = parsedParams.fbProject;
            let seriesNameList = parsedParams.fbSeriesName;
            let inchList = parsedParams.fbInch; 
            let yearList = parsedParams.fbYear; 
            let fbGC = parsedParams.fbGC;
            let fbAP2 = parsedParams.fbAP2; 
            
            let comboList = [];
            let whereQuery = [];
            let orderByQuery = [];
            let selectQuery = "";           

            selectQuery = 'Select ([Version].[Version Name].['+fbVersion+'] * [Item].[Item Stage].['+itemStage+'] ';
            selectQuery += '* [Item].[Item] * [Location].[Location]';
            if (fn_ParamsCheck(fbGC)) {
                selectQuery += '* [Sales Domain].[GC]' + vdUtil.fn_filterStr(fbGC) ;
            }            
            if (fn_ParamsCheck(fbAP2)) {
                selectQuery += '* [Sales Domain].[AP2]' + vdUtil.fn_filterStr(fbAP2) ;
            }else{
                selectQuery += '* [Sales Domain].[AP2]';
            }
            selectQuery += ') on row, ({Measure.[Sales Item Asn_Valid Flag]}) on column '; 

            whereQuery.push('Upper(Measure.[Sales Item Asn_Valid Flag]) == "TRUE"');

            //productGroup
            if (fn_ParamsCheck(productGroupList)) {
                whereQuery.push('[Item].[Product Group]'+ vdUtil.fn_filterStr(productGroupList));
            }
            //Project
            if (fn_ParamsCheck(projectList)) {
                whereQuery.push('[Item].[Project]'+ vdUtil.fn_filterStr(projectList));
            }
            //Series 조건
            if(fn_ParamsCheck(seriesNameList)){
                whereQuery.push('[Item].[Series Name]'+ vdUtil.fn_filterStr(seriesNameList));
            }
            //Inch 조건
            if(fn_ParamsCheck(inchList)){  
                whereQuery.push('[Item].[Inch]'+ vdUtil.fn_filterStr(inchList));
            }
            // Year
            if(fn_ParamsCheck(yearList)){  
                whereQuery.push('[Item].[Year]'+ vdUtil.fn_filterStr(yearList));
            }

            orderByQuery.push('[Item].[Item].DisplayName');

            selectQuery += fn_ibplWhereQuery(whereQuery, orderByQuery);

            let selectResult = vdCommon.selectQueryList("[fn_itemCombo]", selectQuery);
            comboList = vdCommon.fn_makeCombo(selectResult, {DimName : "Item", DimAttbName : "Item", existAll : false, Sort : "DisplayName", isDisplayNameWithCode : false});

            if(comboList.length > 0){
                comboList.unshift({ Name : "All", DisplayName : "All"});
            }else{
                comboList.unshift({ Name : "NA", DisplayName : "NA"});
            }
      
            vdCommon.programEnd();    
            return comboList;
        }catch ( e ) {
            RuleOutputToUI = { Status : 'Error', Message : "Js Logic Error : " + e.message };
            return;
        }
    }

    function fn_itemCombo(o9Params){
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
            let productGroupList = parsedParams.fbProductGroup;
            let projectList = parsedParams.fbProject;
            let seriesNameList = parsedParams.fbSeriesName;
            let inchList = parsedParams.fbInch; 
            let yearList = parsedParams.fbYear; 
            let fbGC = parsedParams.fbGC;
            let fbAP2 = parsedParams.fbAP2; 
            
            let comboList = [];
            let whereQuery = [];
            let orderByQuery = [];
            let selectQuery = "";           

            selectQuery = 'Select ([Version].[Version Name].['+fbVersion+'] * [Item].[Item Stage].['+itemStage+'] ';
            selectQuery += '* [Item].[Item] * [Location].[Location].['+fbLocation+']';
            if (fn_ParamsCheck(fbGC)) {
                selectQuery += '* [Sub Location].[Sub Location GC]' + vdUtil.fn_filterStr(fbGC) ;
            }            
            if (fn_ParamsCheck(fbAP2)) {
                selectQuery += '* [Sub Location].[Sub Location Rep AP2]' + vdUtil.fn_filterStr(fbAP2) ;
            }else{
                selectQuery += '* [Sub Location].[Sub Location Rep AP2]';
            }
            selectQuery += ') on row, ({Measure.[BOD Item_asn]}) on column '; 

            whereQuery.push('Measure.[BOD Item_asn] >= -1');

            //productGroup
            if (fn_ParamsCheck(productGroupList)) {
                whereQuery.push('[Item].[Product Group]'+ vdUtil.fn_filterStr(productGroupList));
            }
            //Project
            if (fn_ParamsCheck(projectList)) {
                whereQuery.push('[Item].[Project]'+ vdUtil.fn_filterStr(projectList));
            }
            //Series 조건
            if(fn_ParamsCheck(seriesNameList)){
                whereQuery.push('[Item].[Series Name]'+ vdUtil.fn_filterStr(seriesNameList));
            }
            //Inch 조건
            if(fn_ParamsCheck(inchList)){  
                whereQuery.push('[Item].[Inch]'+ vdUtil.fn_filterStr(inchList));
            }
            // Year
            if(fn_ParamsCheck(yearList)){  
                whereQuery.push('[Item].[Year]'+ vdUtil.fn_filterStr(yearList));
            }

            orderByQuery.push('[Item].[Item].DisplayName');

            selectQuery += fn_ibplWhereQuery(whereQuery, orderByQuery);

            let selectResult = vdCommon.selectQueryList("[fn_itemCombo]", selectQuery);
            comboList = vdCommon.fn_makeCombo(selectResult, {DimName : "Item", DimAttbName : "Item", existAll : false, Sort : "DisplayName", isDisplayNameWithCode : false});

            if(comboList.length > 0){
                comboList.unshift({ Name : "All", DisplayName : "All"});
            }else{
                comboList.unshift({ Name : "NA", DisplayName : "NA"});
            }
      
            vdCommon.programEnd();    
            return comboList;
        }catch ( e ) {
            RuleOutputToUI = { Status : 'Error', Message : "Js Logic Error : " + e.message };
            return;
        }
    }    

    function fn_descriptionCombo(o9Params){
        try{
            const commonLib = require('o9.NSCM.commonLib');
            const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
            vdCommon.setLogLevel("Debug");
            
            // 파라메타 가져오기
            vdCommon.printParams(o9Params);
            let parsedParams = JSON.parse(o9Params); 
            let fbVersion = parsedParams.fbVersion;
            //let fbLocation = fn_strSplit(parsedParams.fbLocation, ":"); 
            let fbLocation =parsedParams.fbLocation;
            let fbLocationName = vdCommon.fn_getCodeName("[Location].[Location]",fbLocation.toString());

            let fbGC = parsedParams.fbGC;
            let fbAP2 = fn_multiCheckDisplayName(parsedParams.fbAP2, "[Sales Domain].[AP2]");
            
            let productGroupList = fn_multiCheckDisplayName(parsedParams.fbProductGroup, "[Item].[Product Group]");
            let projectList = fn_multiCheckDisplayName(parsedParams.fbProject, "[Item].[Project]");
            let seriesNameList = fn_multiCheckDisplayName(parsedParams.fbSeriesName, "[Item].[Series Name]");
            let inchList = fn_multiCheckDisplayName(parsedParams.fbInch, "[Item].[Inch]");
            let yearList = fn_multiCheckDisplayName(parsedParams.fbYear, "[Item].[Year]");
            let fbItem = parsedParams.fbItem;

            //vdCommon.printStep("["+fbLocationName+"]["+fbGC+"]["+fbAP2+"]["+productGroupList+"]");

            let sDescription = fbLocation +"("+fbLocationName+")"+ " " ;

            if(fn_ParamsCheck(productGroupList)) {
                sDescription += productGroupList + " ";
            }            

            if(fn_ParamsCheck(projectList)) {
                sDescription += projectList + " ";
            }

            if(fn_ParamsCheck(seriesNameList)) {
                sDescription += seriesNameList + " ";
            }

            if(fn_ParamsCheck(inchList)) {
                sDescription += inchList + " ";
            }

            if(fn_ParamsCheck(yearList)) {
                sDescription += yearList + " ";
            }
            //Item 데이타가 '%' 인 경우 제외함.
            if(fn_ParamsCheck(fbItem) || fbItem != "%") {
                sDescription += fbItem + " ";
            }    
            //sDescription += fbItem + " ";
            if(fn_ParamsCheck(fbGC)) {         
                sDescription += vdCommon.fn_getCodeName("[Sales Domain].[GC]",fbGC.toString()) + " ";
            }

            if(fn_ParamsCheck(fbAP2)) { 
                sDescription += vdCommon.fn_getCodeName("[Sales Domain].[AP2]",fbAP2.toString()) + " "; 
            }

            let comboList = [];
            comboList.push({ Name: sDescription, DisplayName: sDescription });
      
            vdCommon.programEnd();
    
            return comboList;
        }catch ( e ) {
            RuleOutputToUI = { Status : 'Error', Message : "Js Logic Error : " + e.message };
            return;
        }
    }

    function fn_exceptItemCombo_SalesItem(o9Params){
        try{
            const commonLib = require('o9.NSCM.commonLib');
            const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
            const vdUtil = new commonLib.VdUtil();
            vdCommon.setLogLevel("Debug");

            vdCommon.printParams(o9Params);
            let parsedParams = JSON.parse(o9Params); 
            let fbVersion = parsedParams.fbVersion;
            let fbLocation = parsedParams.fbLocation;
            let productGroupList = parsedParams.fbProductGroup;
            let projectList = parsedParams.fbProject;
            let seriesNameList = parsedParams.fbSeriesName;
            let inchList = parsedParams.fbInch; 
            let yearList = parsedParams.fbYear;    
            let fbGC = parsedParams.fbGC;
            let fbAP2 = parsedParams.fbAP2;               
            let fbItem = parsedParams.fbItem;
            let fbItemWildCardData = parsedParams.fbItemWildCardData;            
            
            let comboList = [];
            let whereQuery = [];
            let orderByQuery = [];
            let selectQuery = "";
            let strItemFilter = "";

            if(fbItemWildCardData == null){
                if(fn_ParamsCheck(fbItem)){                    
                    strItemFilter = vdUtil.fn_filterStr(fbItem);
                }else{
                    //All 세팅
                    strItemFilter = "";
                }
            }else{
                //Wild Card Data  
                let wildCardData = fn_strSplit(fbItemWildCardData, "^");    

                for(var i= 0; i < wildCardData.length; i++){
                    //vdCommon.debug("[fn_exceptItemCombo(For)]["+ strItemFilter + "]["+wildCardData[i]+"]["+strItemFilter.length+"]");
                    if(strItemFilter.length > 0 ){
                        strItemFilter += " || ";
                    }
                    //vdCommon.printStep("[fn_exceptItemCombo(For)]["+strItemFilter+"]");
                    strItemFilter += fn_filter(wildCardData[i]);
                    vdCommon.debug("[fn_exceptItemCombo(For)]["+strItemFilter+"]");
                }          
                
                vdCommon.debug("[fn_exceptItemCombo(WileCardData)]["+ strItemFilter + "]");

                if(fn_ParamsCheck(fbItem)){
                    //All 선택이 아닌 경우
                    if(strItemFilter.length > 0){
                        strItemFilter = "(" + strItemFilter + ")";
                        strItemFilter += " && " + "("+ fn_filter(fbItem) +")";
                    }else{
                        strItemFilter += fn_filter(fbItem);
                    }             
                }
                vdCommon.printStep("[fn_exceptItemCombo(+ Item)]["+ strItemFilter + "]");
                if(strItemFilter.length > 0){
                    strItemFilter = " .filter(" + strItemFilter + " )";
                }
            }
            vdCommon.debug("[fn_exceptItemCombo(Last)]["+ strItemFilter + "]");

            selectQuery = 'Select ([Version].[Version Name].['+fbVersion+'] * [Item].[Item Stage].['+itemStage+'] ';
            selectQuery += '* [Item].[Item]' + strItemFilter ;
            selectQuery += '* [Location].[Location]';
                    
            if (fn_ParamsCheck(fbGC)) {
                selectQuery += '* [Sales Domain].[GC]' + vdUtil.fn_filterStr(fbGC) ;
            }            
            if (fn_ParamsCheck(fbAP2)) {
                selectQuery += '* [Sales Domain].[AP2]' + vdUtil.fn_filterStr(fbAP2) ;
            }else{
                selectQuery += '* [Sales Domain].[AP2]';
            }
            selectQuery += ') on row, ({Measure.[Sales Item Asn_Valid Flag]}) on column '; 

            whereQuery.push('Upper(Measure.[Sales Item Asn_Valid Flag]) == "TRUE"');

            //productGroup
            if (fn_ParamsCheck(productGroupList)) {
                whereQuery.push('[Item].[Product Group]'+ vdUtil.fn_filterStr(productGroupList));
            }
            //Project
            if (fn_ParamsCheck(projectList)) {
                whereQuery.push('[Item].[Project]'+ vdUtil.fn_filterStr(projectList));
            }
            //Series 조건
            if(fn_ParamsCheck(seriesNameList)){
                whereQuery.push('[Item].[Series Name]'+ vdUtil.fn_filterStr(seriesNameList));
            }
            //Inch 조건
            if(fn_ParamsCheck(inchList)){  
                whereQuery.push('[Item].[Inch]'+ vdUtil.fn_filterStr(inchList));
            }
            // Year
            if(fn_ParamsCheck(yearList)){  
                whereQuery.push('[Item].[Year]'+ vdUtil.fn_filterStr(yearList));
            }

            orderByQuery.push('[Item].[Item].DisplayName');

            selectQuery += fn_ibplWhereQuery(whereQuery, orderByQuery);

            let selectResult = vdCommon.selectQueryList("[fn_itemCombo]", selectQuery);
            comboList = vdCommon.fn_makeCombo(selectResult, {DimName : "Item", DimAttbName : "Item", existAll : false, Sort : "DisplayName", isDisplayNameWithCode : false});

            if(comboList.length == 0){
                comboList.unshift({ Name : "NA", DisplayName : "NA"});
            } 
    
            return comboList;           

        }catch ( e ) {
            RuleOutputToUI = { Status : 'Error', Message : "Js Logic Error : " + e.message };
            return;
        }
    }  

    function fn_exceptItemCombo(o9Params){
        try{
            const commonLib = require('o9.NSCM.commonLib');
            const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
            const vdUtil = new commonLib.VdUtil();
            vdCommon.setLogLevel("Debug");

            vdCommon.printParams(o9Params);
            let parsedParams = JSON.parse(o9Params); 
            let fbVersion = parsedParams.fbVersion;
            let fbLocation = parsedParams.fbLocation;
            let productGroupList = parsedParams.fbProductGroup;
            let projectList = parsedParams.fbProject;
            let seriesNameList = parsedParams.fbSeriesName;
            let inchList = parsedParams.fbInch; 
            let yearList = parsedParams.fbYear;    
            let fbGC = parsedParams.fbGC;
            let fbAP2 = parsedParams.fbAP2;               
            let fbItem = parsedParams.fbItem;
            let fbItemWildCardData = parsedParams.fbItemWildCardData;            
            
            let comboList = [];
            let whereQuery = [];
            let orderByQuery = [];
            let selectQuery = "";
            let strItemFilter = "";

            if(fbItemWildCardData == null){
                if(fn_ParamsCheck(fbItem)){                    
                    strItemFilter = vdUtil.fn_filterStr(fbItem);
                }else{
                    //All 세팅
                    strItemFilter = "";
                }
            }else{
                //Wild Card Data  
                let wildCardData = fn_strSplit(fbItemWildCardData, "^");    

                for(var i= 0; i < wildCardData.length; i++){
                    //vdCommon.debug("[fn_exceptItemCombo(For)]["+ strItemFilter + "]["+wildCardData[i]+"]["+strItemFilter.length+"]");
                    if(strItemFilter.length > 0 ){
                        strItemFilter += " || ";
                    }
                    //vdCommon.printStep("[fn_exceptItemCombo(For)]["+strItemFilter+"]");
                    strItemFilter += fn_filter(wildCardData[i]);
                    vdCommon.debug("[fn_exceptItemCombo(For)]["+strItemFilter+"]");
                }          
                
                vdCommon.debug("[fn_exceptItemCombo(WileCardData)]["+ strItemFilter + "]");

                if(fn_ParamsCheck(fbItem)){
                    //All 선택이 아닌 경우
                    if(strItemFilter.length > 0){
                        strItemFilter = "(" + strItemFilter + ")";
                        strItemFilter += " && " + "("+ fn_filter(fbItem) +")";
                    }else{
                        strItemFilter += fn_filter(fbItem);
                    }             
                }
                vdCommon.printStep("[fn_exceptItemCombo(+ Item)]["+ strItemFilter + "]");
                if(strItemFilter.length > 0){
                    strItemFilter = " .filter(" + strItemFilter + " )";
                }
            }
            vdCommon.debug("[fn_exceptItemCombo(Last)]["+ strItemFilter + "]");

            selectQuery = 'Select ([Version].[Version Name].['+fbVersion+'] * [Item].[Item Stage].['+itemStage+'] ';
            selectQuery += '* [Item].[Item]' + strItemFilter ;
            selectQuery += '* [Location].[Location].['+fbLocation+']';
                    
            if (fn_ParamsCheck(fbGC)) {
                selectQuery += '* [Sub Location].[Sub Location GC]' + vdUtil.fn_filterStr(fbGC) ;
            }            
            if (fn_ParamsCheck(fbAP2)) {
                selectQuery += '* [Sub Location].[Sub Location Rep AP2]' + vdUtil.fn_filterStr(fbAP2) ;
            }else{
                selectQuery += '*[Sub Location].[Sub Location Rep AP2]';
            }
            selectQuery += ') on row, ({Measure.[BOD Item_asn]}) on column '; 

            whereQuery.push('Measure.[BOD Item_asn] >= -1');

            //productGroup
            if (fn_ParamsCheck(productGroupList)) {
                whereQuery.push('[Item].[Product Group]'+ vdUtil.fn_filterStr(productGroupList));
            }
            //Project
            if (fn_ParamsCheck(projectList)) {
                whereQuery.push('[Item].[Project]'+ vdUtil.fn_filterStr(projectList));
            }
            //Series 조건
            if(fn_ParamsCheck(seriesNameList)){
                whereQuery.push('[Item].[Series Name]'+ vdUtil.fn_filterStr(seriesNameList));
            }
            //Inch 조건
            if(fn_ParamsCheck(inchList)){  
                whereQuery.push('[Item].[Inch]'+ vdUtil.fn_filterStr(inchList));
            }
            // Year
            if(fn_ParamsCheck(yearList)){  
                whereQuery.push('[Item].[Year]'+ vdUtil.fn_filterStr(yearList));
            }

            orderByQuery.push('[Item].[Item].DisplayName');

            selectQuery += fn_ibplWhereQuery(whereQuery, orderByQuery);

            let selectResult = vdCommon.selectQueryList("[fn_itemCombo]", selectQuery);
            comboList = vdCommon.fn_makeCombo(selectResult, {DimName : "Item", DimAttbName : "Item", existAll : false, Sort : "DisplayName", isDisplayNameWithCode : false});

            if(comboList.length == 0){
                comboList.unshift({ Name : "NA", DisplayName : "NA"});
            } 
    
            return comboList;           

        }catch ( e ) {
            RuleOutputToUI = { Status : 'Error', Message : "Js Logic Error : " + e.message };
            return;
        }
    }  

    function fn_filterItem(o9Params, itemList){
        try{
            const commonLib = require('o9.NSCM.commonLib');
            const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
            vdCommon.setLogLevel("Debug");            

            // 파라메타 가져오기
            vdCommon.printParams(o9Params);
            let parsedParams = JSON.parse(o9Params); 
            let fbVersion = parsedParams.fbVersion;
            let fbLocation = parsedParams.fbLocation;
            let productGroupList = parsedParams.fbProductGroup;
            let projectList = parsedParams.fbProject;
            let seriesNameList = parsedParams.fbSeriesName;
            let inchList = parsedParams.fbInch; 
            let yearList = parsedParams.fbYear; 
            let fbAP2 = parsedParams.fbAP2; 

            var strSelect = "";
            vdCommon.debug("[fn_filterItem]" + itemList.length);
            for (k = 0; k < itemList.length; k++){
                var sItem = itemList[k];
                //vdCommon.printStep("[fn_filterItem(797)]" + sItem);
                if(String(sItem).toUpperCase() === "ALL" || String(sItem).toUpperCase() === "%"){
                    strSelect = '';
                }else{

                    var startChar = sItem.substring(0,1);
                    var endChar = sItem.substring(sItem.length - 1 ,sItem.length);

                    if(k > 0){
                        strSelect += ' || '; //OR 조건식 추가
                    }
        
                    if(startChar === "%" && endChar === "%"){
                        //console.log("중간체크") 
                        strSelect += '#.Name contains "'+sItem.replace(/%/g, "")+'"';
                    }else if(startChar === "%"){
                        //console.log("끝")
                        strSelect += '#.Name endswith "'+sItem.replace(/%/g, '')+'"';
                    }else if(endChar === "%"){
                        //console.log("startswith")
                        strSelect += '#.Name startswith "'+sItem.replace(/%/g, '')+'"';
                    }else{
                        //console.log("equals")
                        strSelect += '#.Name == "'+sItem+'"';
                    }                
                }
            }

            let whereQuery = [];
            let orderByQuery = [];
            let selectItemQuery = "";
            let selectAP2Query = "";
            let itemSelectQuery = "";

            if(strSelect.length > 0){ 
                selectItemQuery = '* [Item].[Item].filter('+strSelect+') ' ;
            }else{
                selectItemQuery += '* [Item].[Item] ' ; 
            }

            if (fn_ParamsCheck(fbAP2)) {
                selectAP2Query = '* [Sales Domain].[AP2].filter(#.Name in {'+fn_multiCheckName(fbAP2, "[Sales Domain].[AP2]")+'})';
            }else{
                selectAP2Query = '* [Sales Domain].[AP2]';
            }            

            itemSelectQuery = 'Select ([Version].[Version Name].['+fbVersion+'] * [Item].[Item Stage].[SET] ';
            itemSelectQuery += '* [Location].[Location]' ;
            itemSelectQuery += selectItemQuery ; 
            itemSelectQuery += selectAP2Query ;
            itemSelectQuery += ' ) on row, ({Measure.[Sales Item Asn_Valid Flag]}) on column ' ;                

            whereQuery.push('Upper(Measure.[Sales Item Asn_Valid Flag]) == "TRUE"');
            //productGroup
            if (fn_ParamsCheck(productGroupList)) {
                whereQuery.push('[Item].[Product Group].filter(#.Name in {'+fn_multiCheckName(productGroupList, "[Item].[Product Group]")+'})');
            }
            //Project
            if (fn_ParamsCheck(projectList)) {
                whereQuery.push('[Item].[Project].filter(#.Name in {'+fn_multiCheckName(projectList, "[Item].[Project]")+'})');
            }
            //Series 조건
            if(fn_ParamsCheck(seriesNameList)){
                whereQuery.push('[Item].[Series Name].filter(#.Name in {'+fn_multiCheckName(seriesNameList, "[Item].[Series Name]")+'})');
            }
            //Inch 조건
            if(fn_ParamsCheck(inchList)){  
                whereQuery.push('[Item].[Inch].filter(#.Name in {'+fn_multiCheckName(inchList, "[Item].[Inch]")+'})');
            }
            // Year
            if(fn_ParamsCheck(yearList)){  
                whereQuery.push('[Item].[Year].filter(#.Name in {'+fn_multiCheckName(yearList, "[Item].[Year]")+'})');
            }

            orderByQuery.push('[Item].[Item].DisplayName');

            itemSelectQuery += fn_ibplWhereQuery(whereQuery, orderByQuery);

            let itemResult = vdCommon.selectQueryList("fn_filterItem(SQL)", itemSelectQuery);
            let comboData = vdCommon.fn_makeCombo(itemResult, {DimName : "Item", DimAttbName : "Item", existAll : false, Sort : "DisplayName", isDisplayNameWithCode : false});

            return comboData;

        }catch ( e ) {
            RuleOutputToUI = { Status : 'Error', Message : "Js Logic Error : " + e.message };
            return;
        }

    }

    function fn_updateExceptItemList(o9Params){
        try{
            const commonLib = require('o9.NSCM.commonLib');
            const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
            const vdUtil = new commonLib.VdUtil();
            vdCommon.setLogLevel("Debug");

            vdCommon.printParams(o9Params);
            let parsedParams = JSON.parse(o9Params); 
            let fbVersion = parsedParams.fbVersion;
            let fbLocation = parsedParams.fbMeasureLocation;
            let fbAP2 = parsedParams.fbAP2;
            let fbGroupID = parsedParams.fbGroupID;
            let fbSequence = parsedParams.fbSequence;

            fbAP2 = fbAP2.split(",");

            let selectQuery = 'Select ([Item].[Item]) on row, ';
            selectQuery += '({Measure.[CTN Grp Const Ecp_Created By], Measure.[CTN Grp Const Ecp_Creation Time],';
            selectQuery += 'Measure.[CTN Grp Const Ecp_DP Qty from W0], Measure.[CTN Grp Const Ecp_EOH at PSI],';
            selectQuery += 'Measure.[CTN Grp Const Ecp_Ecp Flag], Measure.[CTN Grp Const Ecp_End Week],';
            selectQuery += 'Measure.[CTN Grp Const Ecp_PLC EOP Curr Week], Measure.[CTN Grp Const Ecp_PLC SRA Curr Week],';
            selectQuery += 'Measure.[CTN Grp Const Ecp_Prod Result Qty before W0], Measure.[CTN Grp Const Ecp_Start Week],';
            selectQuery += 'Measure.[CTN Grp Const Ecp_Total SOP DP Diff Qty], Measure.[CTN Grp Const Ecp_Total SOP Qty from W0],';
            selectQuery += 'Measure.[CTN Grp Const Ecp_Update Time], Measure.[CTN Grp Const Ecp_Updated By]}) on column ';
            selectQuery += 'Where {';
            selectQuery += '[Version].[Version Name].['+fbVersion+'],';
            selectQuery += '[Location].[Location].['+fbLocation+'],';
            selectQuery += '[Sales Domain].[AP2]'+vdUtil.fn_filterStr(fbAP2)+',';
            selectQuery += '[Sequence].[Sequence].['+fbSequence+'],';
            selectQuery += '[Group].[Group ID].['+fbGroupID+'],';
            selectQuery += '(Measure.[CTN Grp Const Ecp_Ecp Flag] == false || isnull(Measure.[CTN Grp Const Ecp_Ecp Flag]))';
            selectQuery += '} ';
            selectQuery += 'Orderby [Item].[Item].Name;';
            vdCommon.debug("ExceptList Query ::" + selectQuery);
            let resultList = vdCommon.selectQueryList("fn_exceptItemList", selectQuery); 
            let comboList = vdCommon.fn_makeCombo(resultList, {DimName : "Item", DimAttbName : "Item",  Sort :"DisplayName",  existAll : false, isDisplayNameWithCode : false});

            vdCommon.programEnd();
    
            return comboList;           

        }catch ( e ) {
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
            let parsedParams = JSON.parse(o9Params); 
            let fbVersion = parsedParams.fbVersion;
            let fbLocation = parsedParams.fbMeasureLocation;
            let fbGroupID = parsedParams.fbGroupID;
            let fbSequence = parsedParams.fbSequence;
            let fbAP2 = parsedParams.fbAP2;
            let fbExceptItem = parsedParams.fbExceptItem;
            let fbFrozenWeek = parsedParams.fbFrozenWeek;
            let fbWildExceptItem = parsedParams.fbWildExceptItem;
            
            if(fbExceptItem == null && fbWildExceptItem == null && fbFrozenWeek == null){
                RuleOutputToUI = { Status : 'Error', Message : "Enter the data to be updated." };  
                return 1
            }
            
            fbAP2 = fbAP2.split(",");

            if(fbExceptItem != null){               
                //fbExceptItem = fbExceptItem.join(",");                

                vdCommon.updateMeasure(
                    ['[Version].[Version Name].['+fbVersion+']',
                    '[Group].[Group ID].['+fbGroupID+']',
                    '[Sequence].[Sequence].['+fbSequence+']',
                    '[Location].[Location].['+fbLocation+']',
                    '[Sales Domain].[AP2]'+vdUtil.fn_filterStr(fbAP2),
                    '[Item].[Item]'+vdUtil.fn_filterStr(fbExceptItem)
                    ],
                    ['Measure.[CTN Grp Const Ecp_Ecp Flag] = '+'true'+';']);
            }

            if(fbWildExceptItem != null){
                let wildExceptItem = fn_strSplit(fbWildExceptItem, "^");

                if(wildExceptItem.length > 0){
                    let strSelect = "";
                    for (var k = 0; k < wildExceptItem.length; k++){
                        var sItem = wildExceptItem[k];
                        if(String(sItem).toUpperCase() === "ALL"){
                            strSelect = '';
                        }else{
                            var startChar = sItem.substring(0,1);
                            var endChar = sItem.substring(sItem.length - 1 ,sItem.length);

                            if(k > 0){
                                strSelect += ' || '; //OR 조건식 추가
                            }

                            if(startChar === "%" && endChar === "%"){
                                console.log("중간체크") 
                                strSelect += '#.Name contains "'+sItem.replace(/%/g, "")+'"';
                            }else if(startChar === "%"){
                                console.log("끝")
                                strSelect += '#.Name endswith "'+sItem.replace(/%/g, '')+'"';
                            }else if(endChar === "%"){
                                console.log("startswith")
                                strSelect += '#.Name startswith "'+sItem.replace(/%/g, '')+'"';
                            }else{
                                console.log("equals")
                                strSelect += '#.Name == "'+sItem+'"';
                            } 
                        }

                        vdCommon.updateMeasure(
                            ['[Version].[Version Name].['+fbVersion+']',
                            '[Group].[Group ID].['+fbGroupID+']',
                            '[Sequence].[Sequence].['+fbSequence+']',
                            '[Location].[Location].['+fbLocation+']',
                            '[Sales Domain].[AP2]'+vdUtil.fn_filterStr(fbAP2),
                            '[Item].[Item]'+'.filter('+strSelect+')'
                            ],
                            ['Measure.[CTN Grp Const Ecp_Ecp Flag] = '+'true'+';']);                        
                    }
                }    
            }
            
            //CTN Grp Const Update
            // Measure.[CTN Grp Const_Frozen Week]
            if(fbFrozenWeek != null){
                let strQuery = 'Select ([Time].[Week].filter(#.Key == [Time].[Week].filter(#.Name == "'+fbFrozenWeek+'").element(0).LeadOffset(1).Key));';
                let result = vdCommon.selectQueryList("[CTN Group Update Frozen Week + 1]", strQuery);
                let nextPlanWeek = vdCommon.getMember(result.cs, 0, "Time", "Week").Name;

                vdCommon.updateMeasure(
                    ['[Version].[Version Name].['+fbVersion+']',
                     '[Sequence].[Sequence].['+fbSequence+']',   
                     '[Group].[Group ID].['+fbGroupID+']'
                    ],
                    ['Measure.[CTN Grp Const_Frozen Week] = "'+fbFrozenWeek+'";',
                    'Measure.[CTN Grp Const_Start Week] = "'+nextPlanWeek+'";',
                    'Measure.[CTN Grp Const_Updated By] = CurrentUser().[User Name];',
                    'Measure.[CTN Grp Const_Update Time] = dateadd(Now(),9,"hour");'                
                    ]
                );

                vdCommon.updateMeasure(
                    ['[Version].[Version Name].['+fbVersion+']',
                     '[Location].[Location].['+fbLocation+']',
                     '[Sequence].[Sequence].['+fbSequence+']',   
                     '[Group].[Group ID].['+fbGroupID+']'
                    ],
                    ['Measure.[CTN Grp Const Ecp_Start Week]= "'+nextPlanWeek+'";',
                    'Measure.[CTN Grp Const Ecp_Updated By] = CurrentUser().[User Name];',
                    'Measure.[CTN Grp Const Ecp_Update Time] = dateadd(Now(),9,"hour");'                
                    ]
                );                
            }

        }catch ( e ) {
            RuleOutputToUI = { Status : 'Error', Message : "Js Logic Error : " + e.message };
            return;
        }
    }
   
    function fn_itemInfo(o9Params, itemFilter){
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
            let fbGC = parsedParams.fbGC; 
            let fbAP2 = parsedParams.fbAP2; 

            
            let whereQuery = [];
            let orderByQuery = [];
            let selectGCQuery = "";
            let selectAP2Query = "";
            let itemSelectQuery = "";
            let selectGC = ""; 
            let dataListGC = [];
            let dataListAP2 = [];
            //vdCommon.printStep("[fn_itemInfo(1170)]" + itemFilter + "["+itemSelectQuery+"]");
            if (fn_ParamsCheck(fbGC)) {
                selectGCQuery = '* [Sales Domain].[GC]' + vdUtil.fn_filterStr(fbGC);
            }else{
                vdCommon.debug("[fn_itemInfo(GC -ALL)]");
                if (fn_ParamsCheck(fbAP2)) {
                    selectGCQuery = '* [Sales Domain].[GC]';
                }else{
                    vdCommon.debug("[fn_itemInfo(AP2-ALL)]");
                    //GC All && AP2 ALL인 경우 : 선택한 Location에 해당되는 GC 코드를 조회함.
                    selectGC = 'Select ([Sub Location].[Sub Location GC].filter(~(#.Name in {"All", "-"}))) on row, ';
                    selectGC += '({Measure.[BOD Item_asn]}) on column ';
                    selectGC += 'Where { [Version].[Version Name].['+fbVersion+']';
                    selectGC += ',[Location].[Location].['+fbLocation+'] ';
                    selectGC += ',&NSUISubLocationDC';
                    selectGC += ',[Item].[Item],[Trans Mode].[Trans Mode] ';
                    selectGC += ',(Measure.[BOD Item_asn] >-1)';
                    selectGC += '};';
                    vdCommon.debug("[fn_itemInfo(GC Select)]" + selectGC);
                    let resultGC = vdCommon.selectQueryList("fn_itemInfo(GC)",selectGC);
                    let comboGC = vdCommon.fn_makeCombo(resultGC, {DimName : "Sub Location", DimAttbName : "Sub Location GC", Sort :"DisplayName", existAll : false, isDisplayNameWithCode : false});   
                    dataListGC = comboGC.map((value) => value.Name);
                    vdCommon.debug("[fn_itemInfo]" + dataListGC);
                    selectGCQuery = '* [Sales Domain].[GC]' + vdUtil.fn_filterStr(dataListGC);
                }
            }
            vdCommon.debug("[fn_itemInfo(GC)]" + selectGCQuery);

            if (fn_ParamsCheck(fbAP2)) {
                selectAP2Query = '* [Sales Domain].[AP2]' + vdUtil.fn_filterStr(fbAP2);
            }else{
                //GC에 해당되는 AP2를 조회한다.
                //if (!fn_ParamsCheck(fbGC)) {
                    let selectBODItemAP2 = 'Select ([Sub Location].[Sub Location Rep AP2].filter(~(#.Name in {"All", "-"}))) on row, ';
                    selectBODItemAP2 += '({Measure.[BOD Item_asn]}) on column ';
                    selectBODItemAP2 += 'Where { [Version].[Version Name].['+fbVersion+']';
                    selectBODItemAP2 += ',[Location].[Location].['+fbLocation+'] ';
                    selectBODItemAP2 += ',&NSUISubLocationDC';
                    selectBODItemAP2 += ',[Sub Location].[Sub Location GC]' + vdUtil.fn_filterStr(fbGC);
                    selectBODItemAP2 += ',[Item].[Item],[Trans Mode].[Trans Mode] ';
                    selectBODItemAP2 += ',(Measure.[BOD Item_asn] >-1)';
                    selectBODItemAP2 += '};';

                    let resultAP2 = vdCommon.selectQueryList("fn_itemInfo(AP2)",selectBODItemAP2);
                    let comboAP2 = vdCommon.fn_makeCombo(resultAP2, {DimName : "Sub Location", DimAttbName : "Sub Location Rep AP2", Sort :"DisplayName", existAll : false, isDisplayNameWithCode : false});   
                    dataListAP2 = comboAP2.map((value) => value.Name);
                    vdCommon.debug("[fn_itemInfo(AP2)]" + dataListAP2);

                    selectAP2Query = '* [Sales Domain].[AP2]'+vdUtil.fn_filterStr(dataListAP2);
               // }                
            }            
            vdCommon.debug("[fn_itemInfo(AP)]" + selectAP2Query);

            itemSelectQuery = 'Select ([Version].[Version Name].['+fbVersion+'] ';
            itemSelectQuery += '* [Location].[Location]';
            if(itemFilter.length > 0){
                itemSelectQuery += '* [Item].[Item].filter('+itemFilter+') ' ;
            }else{
                itemSelectQuery += '* [Item].[Item] ' ;
                whereQuery.push('[Item].[Product Group]'+ vdUtil.fn_filterStr(parsedParams.fbProductGroup));
                whereQuery.push('[Item].[Project]'+ vdUtil.fn_filterStr(parsedParams.fbProject));
                whereQuery.push('[Item].[Series Name]'+ vdUtil.fn_filterStr(parsedParams.fbSeriesName));
                whereQuery.push('[Item].[Inch]'+ vdUtil.fn_filterStr(parsedParams.fbInch));
                whereQuery.push('[Item].[Year]'+ vdUtil.fn_filterStr(parsedParams.fbYear));
            }
             
            itemSelectQuery += selectGCQuery ;
            itemSelectQuery += selectAP2Query ;
            itemSelectQuery += ' ) on row, ({Measure.[Sales Item Asn_Valid Flag]}) on column ' ;                

            whereQuery.push('Upper(Measure.[Sales Item Asn_Valid Flag]) == "TRUE"');
            orderByQuery.push('[Item].[Item].Name, [Sales Domain].[AP2].Name');

            itemSelectQuery += fn_ibplWhereQuery(whereQuery, orderByQuery);           
            vdCommon.debug("[fn_itemInfo(SQL))]" + itemSelectQuery);
            let itemResult = vdCommon.selectQueryList("fn_itemInfo(SQL)", itemSelectQuery);
            vdCommon.debug("[fn_itemInfo(RETURN)]" + itemResult);
            return itemResult;

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

            // 파라메타 가져오기
            vdCommon.printParams(o9Params);
            let parsedParams = JSON.parse(o9Params); 
            let fbVersion = parsedParams.fbVersion;
            let fbLocation = parsedParams.fbLocation; 
            let fbGC = parsedParams.fbGC;
            let fbAP2 = parsedParams.fbAP2;
            let fbAP2List = fbAP2.join(",");
            let fbAP2NameList = fn_multiCheckDisplayName(parsedParams.fbAP2, "[Sales Domain].[AP2]");         

            let productGroupDescList = fn_multiCheckDisplayName(parsedParams.fbProductGroup, "[Item].[Product Group]");
            let projectDescList = fn_multiCheckDisplayName(parsedParams.fbProject, "[Item].[Project]");
            let seriesNameDescList = fn_multiCheckDisplayName(parsedParams.fbSeriesName, "[Item].[Series Name]");
            let inchDescList = fn_multiCheckDisplayName(parsedParams.fbInch, "[Item].[Inch]");
            let yearDescList = fn_multiCheckDisplayName(parsedParams.fbYear, "[Item].[Year]");
            //let productDescList = fn_multiCheckDisplayName(parsedParams.fbProduct, "[Item].[Project]");

            // 선택한 데이타 Name
            let productGroupList = fn_multiCheckName(parsedParams.fbProductGroup);
            let projectList = fn_multiCheckName(parsedParams.fbProject);
            let seriesNameList = fn_multiCheckDisplayName(parsedParams.fbSeriesName);
            let inchList = fn_multiCheckDisplayName(parsedParams.fbInch); 
            let yearList = fn_multiCheckName(parsedParams.fbYear); 

            let fbItem = parsedParams.fbItem;  
            let fbItemWildCardData = parsedParams.fbItemWildCardData; 
            let fbExceptItem = parsedParams.fbExceptItem;
            let fbExceptItemWildCardData = parsedParams.fbExceptItemWildCardData;

            let fbApply ="N";

            let strCTNGrpConstQuery = "";

            if(fbItem == "NA"){
                RuleOutputToUI = { Status : 'Error', Message : "There is no Item code data to register." };                  
                return 1;
            }

            //Group ID 생성
            let seqQuery =  'Select ([Version].[Version Name].['+fbVersion+'] * [Group].[Group ID].filter(#.Name startswith "MCT_") * [Sequence].[Sequence]) on row, ';        
            seqQuery += '({Measure.[CTN Grp Const_From Site] ,Measure.[CTN Grp Const_Product Grp]}) on column ';
            seqQuery += 'Where {Measure.[CTN Grp Const_From Site ID] == "'+fbLocation+'"} ';            
            seqQuery += 'Orderby [Group].[Group ID].Name Desc, [Sequence].[Sequence].Name desc ;' ;

            //let sequenceResult = cellsetModule.createCellSet(queryModule.select(seqQuery));
            let sequenceResult = vdCommon.selectQueryList("Group ID Select", seqQuery);
            //vdCommon.debug("selectList Count : " + sequenceResult.rowCount);
            let groupIdMax = "0";
            let sequenceMax = 0;
            let groupIdData = "";
            let seqData = "";

            if(sequenceResult.rowCount > 0){
                groupIdData = sequenceResult.cs.row(0).cell(sequenceResult.cs.memberColumnIndex("Group", "Group ID")).Name;            
                seqData = sequenceResult.cs.row(0).cell(sequenceResult.cs.memberColumnIndex("Sequence", "Sequence")).Name;

                groupIdMax = groupIdData ;
                sequenceMax =  parseInt(seqData) + 1 ;
                //vdCommon.debug("selectList Value [:] " + groupIdData + "]["+seqData+"]["+ groupIdMax +"]["+ sequenceMax+"]"); 
            }else{
                let groupIDQuery =  'Select ([Version].[Version Name].['+fbVersion+'] * [Group].[Group ID].filter(#.Name startswith "MCT_")) on row, ';        
                groupIDQuery += '({Measure.[CTN Grp Const_From Site ID] ,Measure.[CTN Grp Const_Product Grp]}) on column ';
                groupIDQuery += 'Orderby [Group].[Group ID].Name Desc ;' ; 
                //vdCommon.debug("groupIDQuery Query : " + groupIDQuery);
                //let groupIDResult = cellsetModule.createCellSet(queryModule.select(groupIDQuery));
                let groupIDResult = vdCommon.selectQueryList("Group ID Select(1)", groupIDQuery);

                if(groupIDResult.rowCount > 0){
                    groupIdData = groupIDResult.cs.row(0).cell(groupIDResult.cs.memberColumnIndex("Group", "Group ID")).Name;   
                    groupIdMax = String(groupIdData).substring(4, 9); //ex) MCT_00001 => 00001 자르기

                    groupIdMax =  parseInt(groupIdMax) + 1 ;
                    groupIdMax = "MCT_" + String(groupIdMax).padStart(5, "0") ;
                    sequenceMax = 1;
                   //vdCommon.debug("selectList Value [:] ["+ groupIdMax +"]["+ sequenceMax+"]"); 
                }else{
                    let groupIDMaxQuery =  'Select ([Version].[Version Name].['+fbVersion+'] * [Group].[Group ID].filter(#.Name startswith "MCT_") * [Sequence].[Sequence]) on row, ';        
                    groupIDMaxQuery += '({Measure.[CTN Grp Const_From Site] ,Measure.[CTN Grp Const_Product Grp]}) on column ';
                    groupIDMaxQuery += 'Orderby [Group].[Group ID].Name Desc, [Sequence].[Sequence].Name desc ;' ;
                    let groupIDMaxResult = vdCommon.selectQueryList("Group ID Select(2)", groupIDMaxQuery);

                    if(groupIDMaxResult.rowCount > 0){
                        groupIdData = groupIDMaxResult.cs.row(0).cell(groupIDMaxResult.cs.memberColumnIndex("Group", "Group ID")).Name;   
                        groupIdMax = String(groupIdData).substring(4, 9); //ex) MCT_00001 => 00001 자르기

                        groupIdMax =  parseInt(groupIdMax) + 1 ;
                        groupIdMax = "MCT_" + String(groupIdMax).padStart(5, "0") ;
                        sequenceMax = 1;
                    }else{
                        groupIdMax = "MCT_00001" ;
                        sequenceMax = 1;
                    }
                }
            }

            vdCommon.debug("[Last GroupID]" + groupIdMax + "[Last Seq]" + sequenceMax);

            //데이타 저장
            //Group ID 멤버 등록체크
            var memberSql = "[Group].[Group ID] ";
            if ( !vdCommon.existMember(memberSql, groupIdMax) ) {
                //vdCommon.createMember(memberSql, groupIdMax);
                vdCommon.createDimension(['[Group].[Group ID]','[Group].[Group Name]','[Group].[Group Type]'], [groupIdMax,groupIdMax, "MCT"]);
            }

            let fbDescription = parsedParams.fbDescription;
            let newDescription = fn_descriptionCombo(o9Params);
            fbDescription = newDescription[0].Name;

            //AP2 멀티 선택 리스트
            //vdCommon.debug("[AP2]["+fbAP2List+"]" +fbAP2NameList );
            
            //Item 멀티 선택과 WildCard 입력 리스트 체크
            let itemList = "";
            if(fbItem != null){
                itemList = fbItem.join(",");
            }
            if(fbItemWildCardData != null){
                if(itemList.length > 0){
                    itemList += "," + fbItemWildCardData;
                }else{
                    itemList += fbItemWildCardData;
                }           
            }
            vdCommon.debug("[Item]["+itemList+"]" );
            //Except Item 체크
            let exceptItemList = "";
            if(fbExceptItem != null){
                exceptItemList = fbExceptItem.join(",");
            }
            if(fbExceptItemWildCardData != null){
                if(exceptItemList.length > 0){
                    exceptItemList += "," + fbExceptItemWildCardData;
                }else{
                    exceptItemList += fbExceptItemWildCardData;
                }
            }
            vdCommon.debug("[exceptItem]["+exceptItemList+"]" );
            //+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++            
            // (1) CTN Frozen Week : Row 생성할 때 Sync PlanID 주차로 세팅함.(JS 처리)
            // (2) Const. Start : CTN Frozen Week + 1(Week) (JS 처리)
            // (3) Const. End : Detail Item별 PLC Mgmt의 EOP Current 날짜의 Max 일자(파이썬 처리)
            // (4) CTN Frozen SOP : Detail Item별 PLC Mgmt의 EOP Current 날짜의 Max 일자(파이썬 처리)
            //+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
            let planWeek = "" ;
            let nextPlanWeek="";

            let strQuery = 'Select (&LastSyncVersion);';
            let result = vdCommon.selectQueryList("[Sync Version Select]", strQuery); 
            let sVersion = vdCommon.getMember(result.cs, 0, "Version", "Version Name");
            //Last Sync Version Plan Week 조회
            strQuery = 'select ([Version].[Version Name].['+sVersion.Name+']) on row, () on column include memberproperties {[Version].[Version Name],[Plan Week]};';
            result = vdCommon.selectQueryList("[SyncVersion Plan Week]", strQuery);
            planWeek = vdCommon.getPropertyValue(result.cs, 0, "Version", "Version Name", "Plan Week");

            if(vdUtil.fn_getString(planWeek) == ""){
                planWeek = "-";
                nextPlanWeek = "-";
            }else{
                // Last Sync Version Plan Week + 1 조회
                strQuery = 'Select ([Time].[Week].filter(#.Key == [Time].[Week].filter(#.Name == "'+planWeek+'").element(0).LeadOffset(1).Key));';
                result = vdCommon.selectQueryList("[SyncVersion Plan Week + 1]", strQuery);
                nextPlanWeek = vdCommon.getMember(result.cs, 0, "Time", "Week");
                nextPlanWeek = nextPlanWeek.Name;
            }

            vdCommon.debug("CTN Frozen Week ["+sVersion.Name+"]["+planWeek+"]["+nextPlanWeek+"]");
            //+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
            let measureGroup = "";
            //CTN Grp Const 메져 저장
            measureGroup = "CTN Grp Const" ;
            let granularity = [];
            granularity.push("[Version].[Version Name]");
            granularity.push("[Sequence].[Sequence]");
            granularity.push("[Group].[Group ID]");

            let granularityValues = [];
            granularityValues.push(fbVersion);
            granularityValues.push(sequenceMax);
            granularityValues.push(groupIdMax);

            //strQuery += vdCommon.updateMeasureQuery(dimension, measure);
            strCTNGrpConstQuery = vdCommon.createMeasureQuery(vdCommon.makeDimension(granularity, granularityValues),
                                ['Measure.[CTN Grp Const_From Site] = "'+vdCommon.fn_getCodeName("[Location].[Location]",fbLocation.toString())+'";',
                                'Measure.[CTN Grp Const_From Site ID] = "'+fbLocation+'";',
                                'Measure.[CTN Grp Const_Product Grp]= "'+fn_valueCheck(productGroupDescList, "All", "Y")+'";',
                                'Measure.[CTN Grp Const_Project] = "'+fn_valueCheck(projectDescList, "All", "Y")+'";',      
                                'Measure.[CTN Grp Const_Series] = "'+fn_valueCheck(seriesNameDescList, "All", "Y")+'";',
                                'Measure.[CTN Grp Const_Inch] = "'+fn_valueCheck(inchDescList, "All", "Y")+'";',
                                'Measure.[CTN Grp Const_Year] = "'+fn_valueCheck(yearDescList, "All", "Y")+'";',
                                'Measure.[CTN Grp Const_Item] = "'+itemList+'";',
                                'Measure.[CTN Grp Const_Item Description] = "'+fbDescription+'";',
                                'Measure.[CTN Grp Const_Except Item] = "'+exceptItemList+'";',  
                                'Measure.[CTN Grp Const_Apply Flag] = "'+fbApply+'";',
                                'Measure.[CTN Grp Const_GC] = "'+vdCommon.fn_getCodeName("[Sales Domain].[GC]",fbGC.toString())+'";',
                                'Measure.[CTN Grp Const_GC ID] = "'+ fbGC+'";',
                                'Measure.[CTN Grp Const_AP2] = "'+fbAP2NameList+'";',
                                'Measure.[CTN Grp Const_AP2 ID] ="'+fbAP2List+'";',
                                'Measure.[CTN Grp Const_Frozen Week] ="'+planWeek+'";',
                                'Measure.[CTN Grp Const_Start Week] ="'+nextPlanWeek+'";',
                                'Measure.[CTN Grp Const_Created By] = CurrentUser().[User Name];',
                                'Measure.[CTN Grp Const_Creation Time] = dateadd(Now(),9,"hour");',
                                'Measure.[CTN Grp Const_Insert Flag] = "Y";',
                                ]);

            vdCommon.executeQuery("[CTN Grp Const] Measrue Group Create", strCTNGrpConstQuery); 

            //Item 처리는  파이썬 호출하여 처리됨.
            let execQuery = 'EXEC plugin instance [PY_UI_CTNMgmt] for measures {[CTN Grp Const_From Site]} ' +
            'using scope ([Version].[Version Name].['+fbVersion+'] * [Group].[Group ID].['+groupIdMax+'] * [Sequence].[Sequence].['+sequenceMax+'])' +         
            'using arguments {(ExecutionMode, "MediumWeight"), ("IncludeNullRows", "False"),' +
            ' (MaxSliceTableCells, 200000000), (MaxConcurrency, 1 ), ([Param.o9_sys_log_level], "DEBUG")} ;' ;

            vdCommon.printStep("["+programName+"] EXEC Python Call SQL>>"+execQuery);
            vdCommon.executeQuery("PY_UI_CTNMgmt ", execQuery);  
            vdCommon.programEnd();

        }catch ( e ) {
            RuleOutputToUI = { Status : 'Error', Message : "Js Logic Error : " + e.message };
            return;
        }
    }

    return{
        fn_locationCombo : fn_locationCombo,
        fn_salesGCCombo: fn_salesGCCombo,   
        fn_salesAP2Combo : fn_salesAP2Combo,            
        fn_productGroupCombo : fn_productGroupCombo,
        fn_projectCombo : fn_projectCombo,
        fn_seriesNameCombo : fn_seriesNameCombo,
        fn_inchCombo : fn_inchCombo,
        fn_yearCombo : fn_yearCombo,
        fn_itemCombo : fn_itemCombo,
        fn_descriptionCombo : fn_descriptionCombo,
        fn_exceptItemCombo : fn_exceptItemCombo,
        fn_updateExceptItemList : fn_updateExceptItemList,
        fn_add : fn_add,
        fn_update : fn_update
    };		
});