define('o9.NSCM.JSCTNItemConstraint', ['o9/data/query', 'o9/data/cellset', 'o9.NSCM.commonLib'], function(){
	const programName = "o9.NSCM.JSCTNItemConstraint";
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
            vdCommon.printStep("[fn_strSplit]" + JSON.stringify(rtnArry));
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

            vdCommon.debug("[fn_filter]" +val);   
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

            val = val.toString();

            if(val === "" || val === "-" || val === null || val === undefined){
                rtnValue = false;
            }else{
         
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
            //vdCommon.printStep("[fn_ibplWhereQuery]" + rtnWhereQuery);
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
            //vdCommon.printStep("[fn_itemInfo(1170)]" + itemFilter + "["+itemSelectQuery+"]");
            if (fn_ParamsCheck(fbGC)) {
                selectGCQuery = '* [Sales Domain].[GC]' + vdUtil.fn_filterStr(fbGC);
            }else{
                vdCommon.debug("[fn_itemInfo(GC -ALL)]");
                if (fn_ParamsCheck(fbAP2)) {
                    selectGCQuery = '* [Sales Domain].[GC]';
                }else{
                    vdCommon.debug("[fn_itemInfo(AP2-ALL)]");
                    //GC All && AP2 ALL인 경우 : t선택한 Location에 해당되는 GC 코드를 조회함.
                    let selectGC = 'Select ([Sub Location].[Sub Location GC].filter(~(#.Name in {"All", "-"}))) on row, ';
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
                    var dataListGC = comboGC.map((value) => value.Name);
                    vdCommon.debug("[fn_itemInfo]" + dataListGC);
                    selectGCQuery = '* [Sales Domain].[GC]' + vdUtil.fn_filterStr(dataListGC);
                }
            }
            vdCommon.debug("[fn_itemInfo(GC)]" + selectGCQuery);

            if (fn_ParamsCheck(fbAP2)) {
                selectAP2Query = '* [Sales Domain].[AP2]' + vdUtil.fn_filterStr(fbAP2);
            }else{
                selectAP2Query = '* [Sales Domain].[AP2]';
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
            comboList = fn_combo(selectResult, {DimName : "Item", DimAttbName : "Item", existAll : false, Sort : "DisplayName", isDisplayNameWithCode : false});

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

    function fn_ApplyFlag(o9Params){
        try{
            const commonLib = require('o9.NSCM.commonLib');
            const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
            vdCommon.setLogLevel("Debug");

            let comboList = [];
            comboList.push({ Name: "Y", DisplayName: "Y" });
            comboList.push({ Name: "N", DisplayName: "N" });
    
            vdCommon.printStep(">>>>>>>>>>> fn_ApplyFlag End");		
            vdCommon.programEnd(); 
            return comboList;
        } catch ( e ) {
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
            let fbGC = parsedParams.fbGC;
            let fbAP2 = parsedParams.fbAP2; // 멀티 선택 가능
            let fbAP2List = fbAP2.join(",");
            let fbItem = parsedParams.fbItem;  
            let fbItemWildCardData = parsedParams.fbItemWildCardData; 
            let fbApply = "N";               
            
            //Item 멀티 선택과 WildCard 입력 리스트 체크
            let itemList = "";
            if(fbItem != null){
                itemList = fbItem.join(",");
            }
            if(fbItemWildCardData != null){
                if(itemList.length > 0){
                    itemList += "," + fbItemWildCardData;
                }                
            }
            vdCommon.debug("[Item]["+itemList+"]" );           
            //fbItem(Multi) & WildCard 합집합 Item 데이타 분석
            let strItemFilter = "";
            if(fbItem != null && fbItem != "" && fbItem != undefined){
                strItemFilter += fn_filter(fbItem);
            }
            if(fbItemWildCardData != null && fbItemWildCardData != "" && fbItemWildCardData != undefined){
                let itemWildCardData = fn_strSplit(fbItemWildCardData, "^");
                //vdCommon.printStep("[item WildCard Data]" + itemWildCardData.length );
                var m =0;
                for( m=0; m < itemWildCardData.length; m++){
                    if(strItemFilter.length > 0 ){
                        //strItemFilter += " || ";
                        strItemFilter += " && ";
                    }
                    strItemFilter += fn_filter(itemWildCardData[m]) ;
                }  
            }
            vdCommon.debug("[item Filter SQL]" + strItemFilter );                      
            let comboItemList = fn_itemInfo(o9Params, strItemFilter);

            if(comboItemList.rowCount <= 0){
                RuleOutputToUI = { Status : 'Error', Message : "There is no intersection data." };  
                return 1;
            }

            //+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
            // 2025. 05. 15 추가함.
            //+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++            
            // (1) CTN Frozen Week : Row 생성할 때 Sync PlanID 주차로 세팅함.(JS 처리)
            // (2) Const. Start : CTN Frozen Week + 1(Week) (JS 처리)
            // (3) Const. End : Detail Item별 PLC Mgmt의 EOP Current 날짜의 Max 일자(파이썬 처리)
            // (4) CTN Frozen SOP : Detail Item별 PLC Mgmt의 EOP Current 날짜의 Max 일자(파이썬 처리)
            //  데이타 없는 경우 '-'으로 처리함.
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

            let tempKey = "";
            strQuery = "";
            for(var k = 0; k < comboItemList.rowCount ; k++){
                var sItem = comboItemList.cs.row(k).cell(comboItemList.cs.memberColumnIndex("Item", "Item")).Name;
                var sAP2 = comboItemList.cs.row(k).cell(comboItemList.cs.memberColumnIndex("Sales Domain", "AP2")).Name;
                var checkKey = sAP2+"_" + sItem;
                
                if(tempKey != checkKey ){
                    vdCommon.debug("Data ["+checkKey+"]["+sAP2+"]["+sItem+"]");
                    var dimension = [];
                    var measure = [];
    
                    dimension.push("[Version].[Version Name].["+fbVersion+"]");
                    dimension.push("[Item].[Item].["+sItem+"]");
                    dimension.push("[Location].[Location].["+fbLocation+"]");
                    dimension.push("[Sales Domain].[AP2].["+sAP2+"]");
    
                    measure.push('Measure.[CTN Item Const_Frozen Week] = "' + planWeek +'";');
                    measure.push('Measure.[CTN Item Const_Start Week] = "' + nextPlanWeek + '";');
                    measure.push('Measure.[CTN Item Const_Apply Flag] = "' + fbApply + '";');     
                    measure.push('Measure.[CTN Item Const_Created By] = CurrentUser().[User Name];');  
                    measure.push('Measure.[CTN Item Const_Creation Time] = dateadd(Now(),9,"hour");');    
                    measure.push('Measure.[CTN Item Const_Updated By] = CurrentUser().[User Name];');  
                    measure.push('Measure.[CTN Item Const_Update Time] = dateadd(Now(),9,"hour");');        
                    strQuery += vdCommon.createMeasureQuery(dimension,measure );                    

                    tempKey = checkKey;
                }
            }
            vdCommon.debug("SQL :" + strQuery);
            vdCommon.executeQuery("Batch Query" , strQuery);

            //2025.05.09 파이썬 호출하여 처리됨.
            let execQuery = 'EXEC plugin instance [PY_UI_CTNItemConst] for measures {[CTN Item Const_Apply Flag]} ' +
            'using scope ([Version].[Version Name].['+fbVersion+'])' +         
            'using arguments {(ExecutionMode, "MediumWeight"), ("IncludeNullRows", "False"),' +
            ' (MaxSliceTableCells, 200000000), (MaxConcurrency, 1 ), ([Param.o9_sys_log_level], "DEBUG")} ;' ;

            vdCommon.printStep("["+programName+"] EXEC Python Call SQL>>"+execQuery);
            vdCommon.executeQuery("PY_UI_CTNItemConst ", execQuery);  
            
            vdCommon.programEnd();            
        } catch ( e ) {
            RuleOutputToUI = { Status : 'Error', Message : "Js Logic Error : " + e.message };
            return;
        }
    }

    return{
        fn_itemCombo : fn_itemCombo,
        fn_ApplyFlag : fn_ApplyFlag,
        fn_add : fn_add
    };		
});