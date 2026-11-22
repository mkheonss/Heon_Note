define('o9.NSCM.JSPreallocConstraintbyItem', ['o9/data/query', 'o9/data/cellset', 'o9.NSCM.commonLib'], function(){	
	const programName = "o9.NSCM.JSPreallocConstraintbyItem";
    const subLocationDC = "&NSUISubLocationDC";

    function fn_groupId(o9Params){
        try{
            const commonLib = require('o9.NSCM.commonLib');
            const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
            const vdUtil = new commonLib.VdUtil();
            vdCommon.setLogLevel("Debug");
            vdCommon.printParams(o9Params);

            // 파라메타 가져오기
            let parsedParams = JSON.parse(o9Params); 
            let fbVersion = parsedParams.fbVersion;
            
            var result = vdCommon.selectList(['[Version].[Version Name].['+fbVersion+']',
                                            '[Group].[Group ID]'],
                                             ["Measure.[Pre Alloc Const_Created By]", 
                                             "Measure.[Pre Alloc Const_Creation Time]", 
                                             "Measure.[Pre Alloc Const_Grp Description]", 
                                             "Measure.[Pre Alloc Const_Grp1]", 
                                             "Measure.[Pre Alloc Const_Grp2]", 
                                             "Measure.[Pre Alloc Const_Update Time]",
                                             "Measure.[Pre Alloc Const_Updated By]"],
                                             "",
                                             "orderby [Group].[Group ID].DisplayName desc",
                                             "");
            vdCommon.printCsData(result, 3);

            /*var comboList = vdCommon.fn_makeCombo(result, {DimName : "Group", 
                                                           DimAttbName : "Group ID", 
                                                           Sort :"DisplayName", 
                                                           existAll : false, 
                                                           isDisplayNameWithCode : true});
            */
            var comboList = [];

            for(var k = 0; k < result.cs.rowCount ; k++){
                var name = result.cs.row(k).cell(result.cs.memberColumnIndex("Group", "Group ID")).Name; 
                var displayName = result.cs.row(k).cell(result.cs.measureColumnIndex("Pre Alloc Const_Grp Description"));

                displayName = "["+name+"] " + displayName;
                comboList.push({ Name : name, DisplayName : displayName});
            }
            vdCommon.debug("ComboData : " + JSON.stringify(comboList));

            vdCommon.programEnd();

            return comboList;

        }catch ( e ) {
            RuleOutputToUI = { Status : 'Error', Message : "Js Logic Error : " + e.message };
            return;
        }
    } 
     
    function fn_fromSite(o9Params){
        try{
            const commonLib = require('o9.NSCM.commonLib');
            const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
            const vdUtil = new commonLib.VdUtil();
            vdCommon.setLogLevel("Debug");
            vdCommon.printParams(o9Params);

            // 파라메타 가져오기
            let parsedParams = JSON.parse(o9Params); 
            let fbVersion = parsedParams.fbVersion;
            let fbGroupID = parsedParams.fbGroupID;

            var comboList = [];

            //GroupID로 기존에 등록한 Location 정보를 조회한다.
            let selectQuery = 'Select ([Version].[Version Name].['+fbVersion+']';
            selectQuery += '* [Group].[Group ID].['+fbGroupID+']';
            selectQuery += '* [Location].[Location] * [Item].[Item]';
            selectQuery += ') on row, ';
            selectQuery += '({Measure.[Pre Alloc Const by Item_BOD Item ToSite],';
            selectQuery += 'Measure.[Pre Alloc Const by Item_Created By],';
            selectQuery += 'Measure.[Pre Alloc Const by Item_Creation Time],';
            selectQuery += 'Measure.[Pre Alloc Const by Item_Update Time],';
            selectQuery += 'Measure.[Pre Alloc Const by Item_Updated By]}) on column ';
            selectQuery += 'orderby [Location].[Location].DisplayName;';

            let resultGroupID = vdCommon.selectQueryList("fn+fromSite(GroupID)", selectQuery);
            if(resultGroupID.rowCount > 0){
                comboList = vdCommon.fn_makeCombo(resultGroupID, {DimName : "Location", 
                                                            DimAttbName : "Location", 
                                                            Sort :"DisplayName", 
                                                            existAll : false, 
                                                            isDisplayNameWithCode : true});            

                vdCommon.debug("ComboData : " + JSON.stringify(comboList));
            }else{
                //BOD List 메져에서 조회함.
                let dimQuery = [];
                dimQuery.push("[Version].[Version Name].["+fbVersion+"]");
                dimQuery.push("&MFLocation");
                
                let measureQuery = [];
                measureQuery.push("Measure.[BOD List_Eff Enddate]"); 
                measureQuery.push("Measure.[BOD List_Eff Startdate]"); 

                let whereQuery = "Where {";
                whereQuery += "[Sub Location].[Sub Location]" ;
                whereQuery += ",[Trans Mode].[Trans Mode]" ;
                whereQuery += ",(coalesce(Measure.[BOD List_Eff Startdate],DATEADD(Now(),-1,"+'"Day"'+")) < now())";
                whereQuery += ",(coalesce(Measure.[BOD List_Eff Enddate],DATEADD(Now(),-1,"+'"Day"'+")) < now())";
                whereQuery += "}";

                var result = vdCommon.selectList(dimQuery, measureQuery, whereQuery ,"","");
                vdCommon.printCsData(result, 3);    

                comboList = vdCommon.fn_makeCombo(result, {DimName : "Location", 
                                                            DimAttbName : "Location", 
                                                            Sort :"DisplayName", 
                                                            existAll : false, 
                                                            isDisplayNameWithCode : true});            

                vdCommon.debug("ComboData : " + JSON.stringify(comboList));
            }

            vdCommon.programEnd();

            return comboList;

        }catch ( e ) {
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
            vdCommon.printParams(o9Params);
            // 파라메타 가져오기
            let parsedParams = JSON.parse(o9Params); 
            let fbVersion = parsedParams.fbVersion;
            let fbFromSite = parsedParams.fbFromSite;

            let dimensionQuery =[];
            dimensionQuery.push('[Sub Location].[Sub Location GC].filter(~(#.Name in {"All", "-"}))');

            let measureQuery = [];
            measureQuery.push("Measure.[BOD Item_asn] ");

            let whereQuery = "Where {";
            whereQuery += "[Version].[Version Name].["+fbVersion+"]";
            whereQuery += ",[Location].[Location].["+fbFromSite+"]";
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
            let fbFromSite = parsedParams.fbFromSite;
            let fbGC = parsedParams.fbGC;

            let dimensionQuery =[];
            dimensionQuery.push('[Sub Location].[Sub Location Rep AP2].filter(~(#.Name in {"All", "-"}))');

            let measureQuery = [];
            measureQuery.push("Measure.[BOD Item_asn] ");

            let whereQuery = "Where {";
            whereQuery += "[Version].[Version Name].["+fbVersion+"]";
            whereQuery += ",[Location].[Location].["+fbFromSite+"]";
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
            vdCommon.debug("[comboList]"+JSON.stringify(dateAP2));
            let result = vdCommon.selectList(["[Sales Domain].[AP2]" +vdUtil.fn_filterStr(dateAP2)],[],"","","");
            comboList = vdCommon.fn_makeCombo(result, {DimName : "Sales Domain", DimAttbName : "AP2", Sort :"DisplayName", existAll : false, isDisplayNameWithCode : true});   

            //comboList.unshift({ Name : "All", DisplayName : "All"});
    
            vdCommon.programEnd();

            return comboList; 
        }catch ( e ) {
            RuleOutputToUI = { Status : 'Error', Message : "Js Logic Error : " + e.message };
            return;
        }    
    } 

    function fn_toSite(o9Params){
        try{
            const commonLib = require('o9.NSCM.commonLib');
            const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
            const vdUtil = new commonLib.VdUtil();
            vdCommon.setLogLevel("Debug");
            vdCommon.printParams(o9Params);

            // 파라메타 가져오기
            let parsedParams = JSON.parse(o9Params); 
            let fbVersion = parsedParams.fbVersion;
            let fbFromSite = parsedParams.fbFromSite;
            let fbGC = parsedParams.fbGC;
            let fbAP2 = parsedParams.fbAP2;

            //BOD Item 메져에서 조회함.
            let dimQuery = [];
            dimQuery.push(subLocationDC);
            //vdCommon.printStep("dimQuery["+JSON.stringify(dimQuery)+"]");
            let measureQuery = [];
            measureQuery.push("Measure.[BOD Item_asn]"); 
            //vdCommon.printStep("measureQuery["+JSON.stringify(measureQuery)+"]");
            let whereQuery = '';
            whereQuery += 'Where {' ;
            whereQuery += '[Version].[Version Name].['+fbVersion+']';
            whereQuery += ', [Location].[Location]' + vdUtil.fn_filterStr(fbFromSite);
            whereQuery += ', [Item].[Item], [Trans Mode].[Trans Mode]';
            if(fbGC != "All" ){
                whereQuery += ",[Sub Location].[Sub Location GC]"+vdUtil.fn_filterStr(fbGC);
            }
            if(fbAP2 != "All" ){
                whereQuery += ",[Sub Location].[Sub Location Rep AP2]"+vdUtil.fn_filterStr(fbAP2);
            }            
            whereQuery += ', (Measure.[BOD Item_asn] >-1)' ;
            whereQuery += '}';

            vdCommon.printStep("Where["+whereQuery+"]["+JSON.stringify(dimQuery)+"]["+JSON.stringify(measureQuery)+"]");

            var result = vdCommon.selectList(dimQuery, measureQuery,  whereQuery, "","");
            vdCommon.printCsData(result, 3);    

            var comboList = vdCommon.fn_makeCombo(result, {DimName : "Sub Location", 
                                                           DimAttbName : "Sub Location", 
                                                           Sort :"DisplayName", 
                                                           existAll : false, 
                                                           isDisplayNameWithCode : true});            
 
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

            let selectQuery = 'Select (&NSUISetItemProductGroupView);';

            let selectResult = vdCommon.selectQueryList("[fn_productGroupCombo]" ,selectQuery );
            let comboList = vdCommon.fn_makeCombo(selectResult, {DimName : "Item", DimAttbName : "Product Group", existAll : false, Sort : "DisplayName", isDisplayNameWithCode : false});
    
            vdCommon.programEnd();

            return comboList;
        }catch ( e ) {
            RuleOutputToUI = { Status : 'Error', Message : "Js Logic Error : " + e.message };
            return;
        }
    }

    function fn_marketingNameCombo(o9Params){
        try{
            const commonLib = require('o9.NSCM.commonLib');
            const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
            const vdUtil = new commonLib.VdUtil();
            vdCommon.setLogLevel("Debug");

            // 파라메타 가져오기
            vdCommon.printParams(o9Params);
            let parsedParams = JSON.parse(o9Params); 
            let fbProductGroup = parsedParams.fbProductGroup;

            let dimension = [];
            let measure = [];
            let whereQuery = "";

            dimension.push("&NSUIItemMarketingNameView")

            whereQuery = "Where {";
            whereQuery += "&NSUISetItemProductGroupView" + vdUtil.fn_filterStr(fbProductGroup);
            whereQuery += "}";

            let selectResult = vdCommon.selectList(dimension, measure, whereQuery, "", "");
            let comboList = vdCommon.fn_makeCombo(selectResult, {DimName : "Item", DimAttbName : "Marketing Name", existAll : false, Sort : "DisplayName", isDisplayNameWithCode : false});
    
            vdCommon.programEnd();

            return comboList;
        }catch ( e ) {
            RuleOutputToUI = { Status : 'Error', Message : "Js Logic Error : " + e.message };
            return;
        }
    }
    
    function fn_bodItem(o9Params){
        try {
            const commonLib = require('o9.NSCM.commonLib');
            const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
            const vdUtil = new commonLib.VdUtil();
            vdCommon.setLogLevel("Debug");            

            vdCommon.printParams(o9Params);
            // 파라미터 가져오기
            let parsedParams = JSON.parse(o9Params);
            let fbVersion = parsedParams.fbVersion;
            let fbFromSite = vdUtil.fn_nvl(parsedParams.fbFromSite, "");
            let fbToSite = vdUtil.fn_nvl(parsedParams.fbToSite, "");
            let fbGroupID = vdUtil.fn_nvl(parsedParams.fbGroupID, "");
            let fbProductGroup = vdUtil.fn_nvl(parsedParams.fbProductGroup, "");
            let fbMarketingName = vdUtil.fn_nvl(parsedParams.fbMarketingName, "");
           

            //BOD Item 메져에서 조회함.
            let dimQuery = [];
            dimQuery.push("[Item].[Item]");

            let measureQuery = [];
            measureQuery.push("Measure.[BOD Item_asn]");

            let whereQuery = '';
            whereQuery += 'Where {' ;
            whereQuery += '[Version].[Version Name].['+fbVersion+']';
            whereQuery += ',[Location].[Location]'+ vdUtil.fn_filterStr(fbFromSite) ;   
            whereQuery += ','+subLocationDC+vdUtil.fn_filterStr(fbToSite);
            whereQuery += ',[Item].[Product Group]' + vdUtil.fn_filterStr(fbProductGroup);
            whereQuery += ',[Item].[Marketing Name]' + vdUtil.fn_filterStr(fbMarketingName);
            whereQuery += ',[Trans Mode].[Trans Mode]';
            whereQuery += ',Measure.[BOD Item_asn] >-1';
            whereQuery += ',Measure.[BOD Item_Cur Status] in {"PLANNED", "ACTIVE"}';
            whereQuery += '}';

            var result = vdCommon.selectList(dimQuery, measureQuery,  whereQuery, "","");
            //vdCommon.printCsData(result, 3); 
            var comboList = vdCommon.fn_makeCombo(result, {DimName : "Item", DimAttbName : "Item", Sort : "DisplayName", existAll : false});

            vdCommon.programEnd();
            return comboList;
        } catch ( e ) {
            RuleOutputToUI = { Status : 'Error', Message : "Js Logic Error : " + e.message };
            return;
        }
    }

    function fn_strSplit(val,separator){

        var rtnArry = String(val).split(separator);

        for(var k=0; k < rtnArry.length; k++){
            rtnArry[k] = rtnArry[k].replace(/^\s+|\s+$/g,"");
        }

        return rtnArry;        
    }    

    function fn_filterItem(o9Params, itemList){
        try{
            const commonLib = require('o9.NSCM.commonLib');
            const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
            const vdUtil = new commonLib.VdUtil();
            vdCommon.setLogLevel("Debug");            

            // 파라메타 가져오기
            vdCommon.printParams(o9Params);
            let parsedParams = JSON.parse(o9Params); 
            let fbVersion = parsedParams.fbVersion;
            let fbFromSite = parsedParams.fbFromSite;
            let fbToSite = parsedParams.fbToSite;
            let fbProductGroup = parsedParams.fbProductGroup;
            let fbMarketingName = parsedParams.fbMarketingName;

            var strSelect = "";
            for (k = 0; k < itemList.length; k++){
                var sItem = itemList[k];
                if(String(sItem).toUpperCase() === "ALL"){
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
            
            var strFilter = ".filter("+strSelect+")" ;
            
            //BOD Item 메져에서 조회함.
            let dimQuery = [];
            dimQuery.push("[Item].[Item]"+strFilter);
            
            let measureQuery = [];
            measureQuery.push("Measure.[BOD Item_asn]");
            
            let whereQuery = '';
            whereQuery += 'Where {' ;
            whereQuery += '[Version].[Version Name].['+fbVersion+']';
            whereQuery += ',[Location].[Location]'+ vdUtil.fn_filterStr(fbFromSite) ;            
            whereQuery += ','+subLocationDC+vdUtil.fn_filterStr(fbToSite);
            whereQuery += ',[Item].[Product Group]' + vdUtil.fn_filterStr(fbProductGroup);
            whereQuery += ',[Item].[Marketing Name]' + vdUtil.fn_filterStr(fbMarketingName);
            whereQuery += ',[Trans Mode].[Trans Mode]'
            whereQuery += ',(Measure.[BOD Item_asn] >-1)';
            whereQuery += '}';


            let itemResult = vdCommon.selectList(dimQuery, measureQuery, whereQuery, "", "");
            let comboData = vdCommon.fn_makeCombo(itemResult, {DimName : "Item", DimAttbName : "Item", existAll : false, Sort : "DisplayName", isDisplayNameWithCode : false});
            vdCommon.printStep("comboData Count :" + comboData.length );

            return comboData;

        }catch ( e ) {
            RuleOutputToUI = { Status : 'Error', Message : "Js Logic Error : " + e.message };
            return;
        }
    }

    const union = (first, second) => { // first: set, second: set
        const union = [...first]; 
        second.forEach((value) => { if (!union.includes(value)) union.push(value); }) 
        // 없을 때에만 추가 해준다. (합집합 중복 방지)
        return union;
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
            let fbGroupID = parsedParams.fbGroupID;
            let fbFromSite = parsedParams.fbFromSite;
            let fbToSite = parsedParams.fbToSite;
            let fbItem = parsedParams.fbItem;
            let fbItemWildcard = parsedParams.fbItemWildcard;
            let fbItemWildCardData = parsedParams.fbItemWildCardData;


            let itemWildCardData = [];
            let itemWildCardList = [];
            let itemUnion = [];
                        
            if(fbItem == null && fbItemWildCardData == null){
                RuleOutputToUI = { Status : 'Error', Message : "One of the fields Item(Multi) and Item(WildCard) is required." };  
                return 1;
            }else{
                if(fbItemWildCardData != null){
                    itemWildCardData = fn_strSplit(fbItemWildCardData, "^");
                    itemWildCardList = fn_filterItem(o9Params, itemWildCardData);
                    itemWildCardList = itemWildCardList.map((value) => value.Name);
                    itemUnion = itemWildCardList;
                    vdCommon.debug("["+itemWildCardData.length+"]["+itemWildCardList.length+"]");
                    //vdCommon.debug("itemWildCardList["+JSON.stringify(itemWildCardList)+"]");                    
                }
                if(fbItem != null){
                    //vdCommon.debug("fbItem["+JSON.stringify(fbItem)+"]");
                    itemUnion = union(itemUnion, fbItem);
                }

                if(fbItemWildCardData != null && fbItem != null){
                    //Multi Item과 멀티 Item 모두 입력되었을때. 교집합처리를 함.
                    itemUnion = itemWildCardList.filter(item => fbItem.includes(item));
                    vdCommon.debug("[Item 교집합]" + itemUnion);

                    if ( itemUnion == null || itemUnion == "" || itemUnion == undefined ){
                        RuleOutputToUI = { Status : 'Error', Message : "There is no intersection data." };  
                        return 1;
                    }
                }

            }            

            vdCommon.debug("[Union Item Info.]" + itemUnion.length);
            vdCommon.debug("[Union Item Info.]" + JSON.stringify(itemUnion));

            for(var k = 0; k < itemUnion.length; k++){
                    let selectDimension = [];
                    selectDimension.push("[Version].[Version Name].["+fbVersion+"]");
                    selectDimension.push("[Group].[Group ID].["+fbGroupID+"]");
                    selectDimension.push("[Item].[Item].["+itemUnion[k]+"]");
                    selectDimension.push("[Location].[Location].["+fbFromSite+"]");
        
                    let selectMeasure = [];
                    selectMeasure.push("Measure.[Pre Alloc Const by Item_BOD Item ToSite]"); 
                    selectMeasure.push("Measure.[Pre Alloc Const by Item_Created By]"); 
                    selectMeasure.push("Measure.[Pre Alloc Const by Item_Creation Time]"); 
                    selectMeasure.push("Measure.[Pre Alloc Const by Item_Update Time]"); 
                    selectMeasure.push("Measure.[Pre Alloc Const by Item_Updated By]"); 
       
                    let result = vdCommon.selectList(selectDimension, selectMeasure, "", "", "");
    
                    if(result.cs.rowCount > 0){
                        //Update
                        let updateDimension = [];
                        updateDimension.push("[Version].[Version Name].["+fbVersion+"]");
                        updateDimension.push("[Group].[Group ID].["+fbGroupID+"]");
                        updateDimension.push("[Item].[Item].["+itemUnion[k]+"]");
                        updateDimension.push("[Location].[Location].["+fbFromSite+"]");   
    
                        let updateMeasure = [];
                        
                        updateMeasure.push('Measure.[Pre Alloc Const by Item_BOD Item ToSite] = "'+fbToSite.map(item => `${item}`).join(",")+'";'); 
                        updateMeasure.push('Measure.[Pre Alloc Const by Item_Updated By] = CurrentUser().[User Name];'); 
                        updateMeasure.push('Measure.[Pre Alloc Const by Item_Update Time]= dateadd(Now(),9,"hour");'); 
            
                        vdCommon.updateMeasure(updateDimension, updateMeasure);                      
                    }else{
                        //Insert
                        let createDimension = [];
                        createDimension.push("[Version].[Version Name].["+fbVersion+"]");
                        createDimension.push("[Group].[Group ID].["+fbGroupID+"]");
                        createDimension.push("[Item].[Item].["+itemUnion[k]+"]");
                        createDimension.push("[Location].[Location].["+fbFromSite+"]");   
    
                        let createMeasure = [];
                        createMeasure.push('Measure.[Pre Alloc Const by Item_BOD Item ToSite] = "'+fbToSite.map(item => `${item}`).join(",")+'";'); 
                        createMeasure.push('Measure.[Pre Alloc Const by Item_Created By] = CurrentUser().[User Name];'); 
                        createMeasure.push('Measure.[Pre Alloc Const by Item_Creation Time]= dateadd(Now(),9,"hour");'); 
            
                        vdCommon.createMeasure(createDimension, createMeasure);                    
                    }                    
               // }
            }

            // <Pre Alloc Const Detail W > 메져 처리
            //~26주차 measure.[Pre Alloc Const Detail W_Const Qty] = 0 으로 세팅함.
            //Constraint Group Detail 데이타 조회
            let selectDetail = 'Select ([Time].[Week].filter(#.Key >= &CurrentWeek.element(0).LeadOffset(0).Key && #.Key < &CurrentWeek.element(0).LeadOffset(26).Key) * [Version].[Version Name].['+fbVersion+'] ) on row, ';
            selectDetail += '({Measure.[Pre Alloc Const Detail W_Const Qty]}) on column ';
            selectDetail += 'Where {';
            selectDetail += '[Location].[Location].filter(#.Name == "'+fbFromSite+'")' ;
            selectDetail += ', [Group].[Group ID].filter(#.Name == "'+fbGroupID+'")'
            selectDetail += '};';

            selectResult = vdCommon.selectQueryList("fn_add(26Week Select)", selectDetail);
            var comboReg = vdCommon.fn_makeCombo(selectResult, {DimName : "Time", DimAttbName : "Week", Sort : "DisplayName", existAll : false});
            vdCommon.debug("comboReg: " + JSON.stringify(comboReg));
            
            let selectAll = 'Select ([Time].[Week].filter(#.Key >= &CurrentWeek.element(0).LeadOffset(0).Key && #.Key < &CurrentWeek.element(0).LeadOffset(26).Key)) ;';
            var resultAll = vdCommon.selectQueryList("fn_add(26Week TimeList)", selectAll);
            var comboAll = vdCommon.fn_makeCombo(resultAll, {DimName : "Time", DimAttbName : "Week", Sort : "DisplayName", existAll : false});
            vdCommon.debug("comboAll: " + JSON.stringify(comboAll));

            var comboList = comboAll;
            //26주차 중 빠진 주차를 찾는다.
            vdCommon.debug("comboReg.length:" +comboReg.length);
            if(comboReg.length > 0){
                comboList = comboAll.filter(function(item1, idx1){        
                    return comboReg.findIndex(function(item2, idx2){
                        console.log("[chkData]" +idx2 + "<"+item2.Name+">");   
                        return item1.Name == item2.Name
                    }) < 0 ;            
                }); 
            }

            //vdCommon.debug("create");
            for(var k=0; k < comboList.length; k++){
                let createDimension = [];
                createDimension.push("[Version].[Version Name].["+fbVersion+"]");
                createDimension.push("[Location].[Location].["+fbFromSite+"]");            
                createDimension.push("[Group].[Group ID].["+fbGroupID+"]");
                createDimension.push("[Time].[Week].["+comboList[k].Name+"]"); //26주 조회
    
                let createMeasure = [];
                createMeasure.push("Measure.[Pre Alloc Const Detail W_Const Qty] = 0;");
                createMeasure.push('Measure.[Pre Alloc Const Detail W_Created By] = CurrentUser().[User Name];'); 
                createMeasure.push('Measure.[Pre Alloc Const Detail W_Creation Time]= dateadd(Now(),9,"hour");'); 
    
                vdCommon.createMeasure(createDimension, createMeasure);  
            } 
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
                whereQuery.push("[Item].[Item].["+fbDataList[k].Item.Value+"]");
                whereQuery.push("[Location].[Location].["+fbDataList[k].Location.Value+"]");

                vdCommon.deleteMeasure(whereQuery, "Pre Alloc Const by Item");
            }

        }catch ( e ) {
            RuleOutputToUI = { Status : 'Error', Message : "Js Logic Error : " + e.message };
            return;
        }  
    }

    function fn_deleteDetailW(o9Params){
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
                whereQuery.push("[Location].[Location].["+fbDataList[k].Location.Value+"]");
                whereQuery.push("[Time].[Week]");               

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
        fn_groupId:fn_groupId,
        fn_fromSite : fn_fromSite,
        fn_salesGCCombo : fn_salesGCCombo,
        fn_salesAP2Combo : fn_salesAP2Combo,
        fn_toSite : fn_toSite,
        fn_productGroupCombo : fn_productGroupCombo,
        fn_marketingNameCombo :fn_marketingNameCombo,
        fn_bodItem : fn_bodItem,
        fn_deleteDetailW :fn_deleteDetailW
    };		
});