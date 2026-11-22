define('o9.NSCM.JSMultiLevelSiteMapping', ['o9/data/query', 'o9/data/cellset', 'o9.NSCM.commonLib'], function(){	
	const programName = "o9.NSCM.JSMultiLevelSiteMapping";
    
    function fn_locationCombo(o9Params){
        try{
            const commonLib = require('o9.NSCM.commonLib');
            const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
            const vdUtil = new commonLib.VdUtil();
            vdCommon.setLogLevel("Debug");
            // 파라메타 가져오기
            vdCommon.printParams(o9Params);
            let parsedParams = JSON.parse(o9Params);
            let fbVersion = parsedParams.fbVersion;
            let fbToLocation = parsedParams.fbToLocation;
            let fbSubLocation = parsedParams.fbSubLocation;
            //let fbProductGroup = parsedParams.fbProductGroup;
            //let fbProduct = parsedParams.fbProduct;

            let dimension = [];
            let measure = [];
            let where ="";
            let orderby = "";

            /*25.02.25 심명보프로님 요청으로 Europe 조건 추가*/
            dimension.push("[Location].[Location]");
            dimension.push("[Location].[Region].[EUROPE]"); 
            orderby = "orderby [Location].[Location].DisplayName"; 
              
            let result = vdCommon.selectList(dimension,measure, where, orderby,""); 
            comboList = vdCommon.fn_makeCombo(result, {DimName :"Location",DimAttbName : "Location", sort:"DisplayName", existAll : false, isDisplayNameWithCode : true});

            if(comboList.length <= 0){
                comboList.unshift({ Name : "NA", DisplayName : "NA"});
            }

            vdCommon.programEnd();    
            return comboList;
        }catch ( e ) {
            RuleOutputToUI = { Status : 'Error', Message : "Js Logic Error : " + e.message };
            return;
        }
    }    

    function fn_AP2Combo(o9Params){
        try{
            const commonLib = require('o9.NSCM.commonLib');
            const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
            const vdUtil = new commonLib.VdUtil();
            vdCommon.setLogLevel("Debug");
            // 파라메타 가져오기
            vdCommon.printParams(o9Params);
            let parsedParams = JSON.parse(o9Params);
            let fbVersion = parsedParams.fbVersion;
            let fbToLocation = parsedParams.fbToLocation;
            let fbSubLocation = parsedParams.fbSubLocation;        
            let fbLocation = parsedParams.fbLocation;  
            
            let dimension = [];
            let measure = [];
            let where ="";
            let orderby="";

            /* Sales Domain 디멘젼에서 조회*/
            dimension.push('[Sales Domain].[AP2]');
            dimension.push('[Sales Domain].[GC].[206]');

            let selectResult = vdCommon.selectList(dimension, measure, where ,"","");
            let comboList = vdCommon.fn_makeCombo(selectResult, {DimName : "Sales Domain", DimAttbName : "AP2", existAll : false, Sort : "DisplayName", isDisplayNameWithCode : true});
            
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


    function fn_productCombo(o9Params){
        try{
            const commonLib = require('o9.NSCM.commonLib');
            const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
            const vdUtil = new commonLib.VdUtil();
            vdCommon.setLogLevel("Debug");
            // 파라메타 가져오기
            vdCommon.printParams(o9Params);
            let parsedParams = JSON.parse(o9Params);
            let fbVersion = parsedParams.fbVersion;
            let fbProductGroup = parsedParams.fbProductGroup;

            let dimension = [];
            let measure = [];
            let where ="";
            let orderby = "";

            dimension.push("[Item].[Product]");   
            dimension.push("[Item].[Product Group]"+vdUtil.fn_filterStr(fbProductGroup));             
            
            let result = vdCommon.selectList(dimension,measure, where, orderby,""); 
            comboList = vdCommon.fn_makeCombo(result, {DimName :"Item",DimAttbName : "Product", sort:"DisplayName", existAll : false, isDisplayNameWithCode : false});

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
            let fbToLocation= parsedParams.fbToLocation;        
            let fbLocation= parsedParams.fbLocation;
            let fbSubLocation= parsedParams.fbSubLocation;
            let fbAP2= parsedParams.fbAP2;
            let fbProductGroup = parsedParams.fbProductGroup;
            let fbProduct = parsedParams.fbProduct;  
            
            
            //BOD Item 메져에서 조회함.
            let dimQuery = [];
            dimQuery.push("[Item].[Item]");
            
            let measureQuery = [];
            //BOD Item 메져에 등록된 경우 모두 조회되도록 처리함.
            measureQuery.push("Measure.[BOD Item_Asn] ");
            measureQuery.push("Measure.[BOD Item_BOD Frozen] ");
            measureQuery.push("Measure.[BOD Item_BOD LT] ");
            measureQuery.push("Measure.[BOD Item_BOD LT_BOD List_Inherit] ");
            measureQuery.push("Measure.[BOD Item_BOD LT_BOD ProdSET_Inherit] ");
            measureQuery.push("Measure.[BOD Item_BOD LT_Inherit] ");
            measureQuery.push("Measure.[BOD Item_Created By] ");
            measureQuery.push("Measure.[BOD Item_Creation Time] ");
            measureQuery.push("Measure.[BOD Item_Cur Status] ");
            measureQuery.push("Measure.[BOD Item_Eff Enddate] ");
            measureQuery.push("Measure.[BOD Item_Eff Enddate_BOD List_Inherit] ");
            measureQuery.push("Measure.[BOD Item_Eff Enddate_BOD ProdSET_Inherit] ");
            measureQuery.push("Measure.[BOD Item_Eff Startdate] ");
            measureQuery.push("Measure.[BOD Item_Eff Startdate_BOD List_Inherit] ");
            measureQuery.push("Measure.[BOD Item_Eff Startdate_BOD ProdSET_Inherit] ");
            measureQuery.push("Measure.[BOD Item_Lock Flag] ");
            measureQuery.push("Measure.[BOD Item_Min Lot Qty] ");
            measureQuery.push("Measure.[BOD Item_Multi Lot Qty] ");
            measureQuery.push("Measure.[BOD Item_Need Check] ");
            measureQuery.push("Measure.[BOD Item_Period SET Detail] ");
            measureQuery.push("Measure.[BOD Item_Period1] ");
            measureQuery.push("Measure.[BOD Item_Period2] ");
            measureQuery.push("Measure.[BOD Item_Period3] ");
            measureQuery.push("Measure.[BOD Item_Priority] ");
            measureQuery.push("Measure.[BOD Item_Priority_BOD List_Inherit] ");
            measureQuery.push("Measure.[BOD Item_Priority_BOD ProdSET_Inherit] ");
            measureQuery.push("Measure.[BOD Item_Priority_Inherit] ");
            measureQuery.push("Measure.[BOD Item_Prod Item] ");
            measureQuery.push("Measure.[BOD Item_Shipment LT] ");
            measureQuery.push("Measure.[BOD Item_Shipment LT_BOD List_Inherit] ");
            measureQuery.push("Measure.[BOD Item_Shipment LT_BOD ProdSET_Inherit] ");
            measureQuery.push("Measure.[BOD Item_Shipment LT_Inherit] ");
            measureQuery.push("Measure.[BOD Item_Time Phased BOD] ");
            measureQuery.push("Measure.[BOD Item_Time Phased Prty] ");
            measureQuery.push("Measure.[BOD Item_Time Phased Shipment] ");
            measureQuery.push("Measure.[BOD Item_To Item] ");
            measureQuery.push("Measure.[BOD Item_Update Time]");
            measureQuery.push("Measure.[BOD Item_Updated By]");


            let whereQuery = '';
            whereQuery += 'Where {' ;
            whereQuery += '[Version].[Version Name].['+fbVersion+']';
            whereQuery += ',[Location].[Location]'+ vdUtil.fn_filterStr(fbLocation) ;            
            whereQuery += ',&NSUISubLocationDC';
            whereQuery += ',[Item].[Product Group]' + vdUtil.fn_filterStr(fbProductGroup);
            whereQuery += ',[Item].[Product]' + vdUtil.fn_filterStr(fbProduct);
            whereQuery += ',[Trans Mode].[Trans Mode]';
            //2025.03.18 메져 조건 제외시킴
            //whereQuery += ',Measure.[BOD Item_asn] >-1';
            //whereQuery += ',Measure.[BOD Item_Cur Status] in {"PLANNED", "ACTIVE"}';
            whereQuery += '}';
            
            var result = vdCommon.selectList(dimQuery, measureQuery,  whereQuery, "","");
       
            let comboList = vdCommon.fn_makeCombo(result, {DimName : "Item",DimAttbName : "Item", sort:"Name", existAll : false, isDisplayNameWithCode : false});
           
            vdCommon.debug("fn_SelectItem > Last ComboData : " + JSON.stringify(comboList));
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

            // 파라메타 가져오기
            vdCommon.printParams(o9Params);
            let parsedParams = JSON.parse(o9Params);
            let fbVersion = parsedParams.fbVersion;
            let fbToLocation = parsedParams.fbToLocation;
            let fbSubLocation = parsedParams.fbSubLocation;
            //화면에서 변경되는 내용
            let fbLocation = parsedParams.fbLocation;            
            let fbAP2 = parsedParams.fbAP2;            
            let fbProductGroup = parsedParams.fbProductGroup;  
            let fbProduct = parsedParams.fbProduct;
            let fbItem = parsedParams.fbItem;

            //Multi Site 메져그룹 등록
            var dimensionMultiSite = [];            
            dimensionMultiSite.push('[Version].[Version Name].['+fbVersion+']');
            dimensionMultiSite.push('[Location].[Location].['+fbLocation+']');
            dimensionMultiSite.push('[Item].[Product].['+fbProduct+']');
            dimensionMultiSite.push('[To Location].[To Location].['+fbToLocation+']');
            dimensionMultiSite.push('[Sales Domain].[AP2].['+fbAP2+']'); 
            dimensionMultiSite.push('[Sub Location].[Sub Location].['+fbSubLocation+']'); 

            var measureMultiSite = [];   
            measureMultiSite.push('Measure.[Multi Site_BOD Valid Flag]');
            measureMultiSite.push('Measure.[Multi Site_PSI Toggle]');

            let selectResult = vdCommon.selectList(dimensionMultiSite, measureMultiSite, "", "", "");

            let dataMeasure = [];
            dataMeasure.push('Measure.[Multi Site_BOD Valid Flag] = "REQ";');
            dataMeasure.push('Measure.[Multi Site_PSI Toggle] = "Y";');

            if(selectResult.cs.rowCount > 0){
                dataMeasure.push('Measure.[Multi Site_Updated By] = CurrentUser().[User Name];');
                dataMeasure.push('Measure.[Multi Site_Update Time] = dateadd(Now(),9,"hour");');  
                vdCommon.updateMeasure(dimensionMultiSite, dataMeasure);
            }else{
                dataMeasure.push('Measure.[Multi Site_Created By] = CurrentUser().[User Name];');
                dataMeasure.push('Measure.[Multi Site_Creation Time] = dateadd(Now(),9,"hour");'); 
                vdCommon.createMeasure(dimensionMultiSite, dataMeasure);
            }

            // Multi Site by Item 메저그룹 등록
            //Multi Site by Item 메져 그룹 데이타 처리
            //기존등록된 Item 삭제 처리함. 
            let deleteWhere = [];
            deleteWhere.push("[Version].[Version Name].["+fbVersion+"]");
            deleteWhere.push("[Location].[Location].["+fbLocation+"]");
            deleteWhere.push("[To Location].[To Location].["+fbToLocation+"]");
            deleteWhere.push("[Sales Domain].[AP2].["+fbAP2+"]");
            deleteWhere.push("[Sub Location].[Sub Location].["+fbSubLocation+"]");
            vdCommon.deleteMeasure(deleteWhere, "Multi Site by Item");

            let strQuery = "";
            for(var k = 0; k < fbItem.length ; k++){
                var dimensionMultiSiteByItem = [];
                var measureMultiSiteByItem = [];
                //dimension
                vdCommon.printStep("["+fbItem[k]+"]");
                dimensionMultiSiteByItem.push("[Version].[Version Name].["+fbVersion+"]");
                dimensionMultiSiteByItem.push("[Item].[Item].["+fbItem[k]+"]");
                dimensionMultiSiteByItem.push("[To Location].[To Location].["+fbToLocation+"]");
                dimensionMultiSiteByItem.push("[Location].[Location].["+fbLocation+"]");
                dimensionMultiSiteByItem.push("[Sales Domain].[AP2].["+fbAP2+"]");
                dimensionMultiSiteByItem.push("[Sub Location].[Sub Location].["+fbSubLocation+"]");

                //measure
                measureMultiSiteByItem.push("Measure.[Multi Site by Item_Created By] = CurrentUser().[User Name];");             
                measureMultiSiteByItem.push('Measure.[Multi Site by Item_Creation Time] = dateadd(Now(),9,"hour");');  
                measureMultiSiteByItem.push('Measure.[Multi Site by Item_Updated By] = CurrentUser().[User Name];');
                measureMultiSiteByItem.push('Measure.[Multi Site by Item_Update Time] = dateadd(Now(),9,"hour");');

                vdCommon.printStep("measure["+measureMultiSiteByItem.join(' ') +"]");	
                strQuery += vdCommon.createMeasureQuery(dimensionMultiSiteByItem,measureMultiSiteByItem );
            }  
            if(strQuery.length > 0){
                vdCommon.printStep("SQL :" + strQuery);
                vdCommon.executeQuery("Batch Query" , strQuery);
            }
            vdCommon.programEnd(); 

        }catch ( e ) {
            RuleOutputToUI = { Status : 'Error', Message : "Js Logic Error : " + e.message };
            return;
        }
    }   

    return{
        fn_locationCombo : fn_locationCombo, 
        fn_AP2Combo : fn_AP2Combo,        
        fn_productGroupCombo : fn_productGroupCombo,   
        fn_productCombo : fn_productCombo,        
        fn_itemCombo  : fn_itemCombo,
        fn_add : fn_add
    };		
});