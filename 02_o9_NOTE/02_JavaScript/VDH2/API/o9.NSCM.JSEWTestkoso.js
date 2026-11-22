define('o9.NSCM.JSEWTestkoso', ['o9/data/query', 'o9/data/cellset', 'o9.NSCM.commonLib'], function(){	

	const programName = "o9.NSCM.JSEWTestkoso";

    function fn_siteIDCombo(o9Params){
        try{
            const commonLib = require('o9.NSCM.commonLib');
            const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
            vdCommon.setLogLevel("Debug");

            vdCommon.printParams(o9Params);
            let parsedParams = JSON.parse(o9Params);
            let fbVersion = parsedParams.fbVersion;

            let selectReg = 'Select ([Location].[Location]) on row,({Measure.[MF Site_Valid Flag]}) on column Where {[Version].[Version Name].['+fbVersion+']}; ';
            let resultReg = vdCommon.selectQueryList("fn_siteIDCombo", selectReg);
            //vdCommon.printStep("[resultReg]" + JSON.stringify(resultReg));
            let comboReg = vdCommon.fn_makeCombo(resultReg, {DimName : "Location", DimAttbName : "Location", existAll : false, Sort : "Name", isDisplayNameWithCode : true});
            //vdCommon.printStep("[comboReg]" + JSON.stringify(comboReg));

            let selectAll = 'Select ([Location].[Location]) on row,() on column Where {[Location].[Location Type].[MF]}; ';
            let resultAll = vdCommon.selectQueryList("fn_siteIDCombo(All)", selectAll);
            //vdCommon.printStep("[resultAll]" + JSON.stringify(coresultAllmboAll));
            let comboAll = vdCommon.fn_makeCombo(resultAll, {DimName : "Location", DimAttbName : "Location", existAll : false, Sort : "Name", isDisplayNameWithCode : true});
            //vdCommon.printStep("[comboAll]" + JSON.stringify(comboAll));
            
            let comboList = comboAll;      
            vdCommon.printStep("[Reg]" + comboReg.length);
            if(comboReg.length > 0){
                comboList = comboAll.filter(function(item1, idx1){                      
                    return comboReg.findIndex(function(item2, idx2){
                        //vdCommon.printStep("[chkData]" +idx2 + "<"+item2.Name+">")        
                        return item1.Name == item2.Name
                    }) < 0 ;            
                }); 
            }

            vdCommon.programEnd();
            return comboList;
        }catch ( e ) {
            RuleOutputToUI = { Status : 'Error', Message : "Js Logic Error : " + e.message };
            return;
        }
    }

    function fn_siteInfo(o9Params){
        try{
            const commonLib = require('o9.NSCM.commonLib');
            const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
            vdCommon.setLogLevel("Debug");

            vdCommon.printParams(o9Params);
            let parsedParams = JSON.parse(o9Params);
            let fbSiteID = parsedParams.fbSiteID;

            let selectQuery = 'Select ([Location].[Location].['+fbSiteID+'] * [Location].[Location Type].[MF]) on row, () on column include memberproperties{[Location].[Location], [Description]}; ';
            let result = vdCommon.selectQueryList("fn_siteInfo", selectQuery);

            let comboList = [];

            for ( var i = 0; i < result.rowCount; i++ ) {
                dimensionValue = vdCommon.getMember(result.cs, i, "Location", "Location")
                dimensionValueType = vdCommon.getMember(result.cs, i, "Location", "Location Type")
                propertyValue = vdCommon.getPropertyValue(result.cs, i, "Location", "Location", "Description");
               
                comboList.push({ Name: dimensionValue.Name, DisplayName: dimensionValue.DisplayName, 
                    PropertyName: "Description" , PropertyValue:propertyValue, 
                    Name2:dimensionValueType.Name, DisplayName2 : dimensionValueType.DisplayName});
            }
            vdCommon.printStep("[fn_siteInfo]" + JSON.stringify(comboList));
            vdCommon.programEnd();
            return comboList;

        }catch ( e ) {
            RuleOutputToUI = { Status : 'Error', Message : "Js Logic Error : " + e.message };
            return;
        }
    }
	
    function fn_countryCodeCombo(o9Params){
        try{
            const commonLib = require('o9.NSCM.commonLib');
            const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
            vdCommon.setLogLevel("Debug");

            let parsedParams = JSON.parse(o9Params); 
            let fbSiteID = parsedParams.fbSiteID;

            let selectQuery = "select ([Location].[Location] * [Location].[Location Type].[MF]) on row, () on column include memberproperties {[Location].[Location], [Country Code]} orderby [Location].[Location].[Country Code] asc;";
            let result = vdCommon.selectQueryList("fn_countryCodeCombo",selectQuery);
            
            let comboList = [];
            vdCommon.printStep("dimension[조회데이타]"+JSON.stringify(result.cs));

            let dimensionValue = "";
            let propertyValue = "";
            let propertyValueTemp = "";
            for ( var i = 0; i < result.rowCount; i++ ) {
                dimensionValue = vdCommon.getMember(result.cs, i, "Location", "Location");                
                //vdCommon.printStep("dimension[조회데이타]"+dimensionValue);
                propertyValue = vdCommon.getPropertyValue(result.cs, i, "Location", "Location", "Country Code");                
                if(propertyValue  === null) continue;
                
                if(propertyValueTemp != propertyValue){
                    comboList.push({ Name: dimensionValue.Name, DisplayName: dimensionValue.DisplayName, PropertyName: "Country Code" , PropertyValue:propertyValue});
                    propertyValueTemp = propertyValue;
                }
            }   
            vdCommon.programEnd();
            vdCommon.printStep("[ComboList]"+ JSON.stringify(comboList));
            return comboList;
        }catch ( e ) {
            RuleOutputToUI = { Status : 'Error', Message : "Js Logic Error : " + e.message };
            return;
        }  
    }  

    function fn_countryNameCombo(o9Params){
        try{
            const commonLib = require('o9.NSCM.commonLib');
            const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
            vdCommon.setLogLevel("Debug");

            vdCommon.printParams(o9Params);
            let parsedParams = JSON.parse(o9Params); 

            let selectQuery = 'Select([Location].[Location Type].[MF] * [Location].[Country Name].filter(~(#.Name =="-"))) Orderby [Location].[Country Name].DisplayName;';
            let result = vdCommon.selectQueryList("fn_countryNameCombo",selectQuery)
            let comboList = vdCommon.fn_makeCombo(result, {DimName : "Location", DimAttbName : "Country Name", existAll : false, Sort : "DisplayName", isDisplayNameWithCode : false});

            vdCommon.programEnd();
            return comboList;
        }catch ( e ) {
            RuleOutputToUI = { Status : 'Error', Message : "Js Logic Error : " + e.message };
            return;
        }
    } 

    function fn_regionCombo(o9Params){
        try{
            const commonLib = require('o9.NSCM.commonLib');
            const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
            vdCommon.setLogLevel("Debug");        

            vdCommon.printParams(o9Params);
            let parsedParams = JSON.parse(o9Params); 

            let selectQuery = 'Select ([Location].[Location Type].[MF] * [Location].[Region].filter(~(#.Name =="-"))) Orderby [Location].[Region].DisplayName;';
            let result = vdCommon.selectQueryList("fn_regionCombo",selectQuery)
            let comboList = vdCommon.fn_makeCombo(result, {DimName : "Location", DimAttbName : "Region", existAll : false, Sort : "DisplayName", isDisplayNameWithCode : false});

            vdCommon.programEnd();
            return comboList;
        }catch ( e ) {
            RuleOutputToUI = { Status : 'Error', Message : "Js Logic Error : " + e.message };
            return;
        }        
    } 

    function fn_businessTypeCombo(o9Params){
        try{
            const commonLib = require('o9.NSCM.commonLib');
            const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
            vdCommon.setLogLevel("Debug");   

            let parsedParams = JSON.parse(o9Params); 
            let comboList = [];
            comboList.push({ Name: "PLANT", DisplayName:"PLANT" });

            vdCommon.programEnd();
            return comboList;
        }catch ( e ) {
            RuleOutputToUI = { Status : 'Error', Message : "Js Logic Error : " + e.message };
            return;
        }
    }

    function fn_salesTypeCombo(o9Params){
        try{
            const commonLib = require('o9.NSCM.commonLib');
            const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
            vdCommon.setLogLevel("Debug");   

            vdCommon.printParams(o9Params);
            let parsedParams = JSON.parse(o9Params); 

            let comboList = [];
            comboList.push({ Name: "PLANT", DisplayName:"PLANT" });

            vdCommon.programEnd();
            return comboList;
        }catch ( e ) {
            RuleOutputToUI = { Status : 'Error', Message : "Js Logic Error : " + e.message };
            return;
        }
    }      

    function fn_companyCombo(o9Params){
        try{
            const commonLib = require('o9.NSCM.commonLib');
            const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
            vdCommon.setLogLevel("Debug"); 

            vdCommon.printParams(o9Params);
            let parsedParams = JSON.parse(o9Params); 

            let selectQuery = 'Select ([Location].[Location Type].[MF] * [Location].[Company].filter(~(#.Name =="-"))) Orderby [Location].[Company].DisplayName;';
            let result = vdCommon.selectQueryList("fn_companyCombo",selectQuery)
            let comboList = vdCommon.fn_makeCombo(result, {DimName : "Location", DimAttbName : "Company", existAll : false, Sort : "DisplayName", isDisplayNameWithCode : false});

            vdCommon.programEnd();
            return comboList;
        }catch ( e ) {
            RuleOutputToUI = { Status : 'Error', Message : "Js Logic Error : " + e.message };
            return;
        }
    }

    function fn_companyNameCombo(o9Params){
        try{
            const commonLib = require('o9.NSCM.commonLib');
            const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
            vdCommon.setLogLevel("Debug"); 

            vdCommon.printParams(o9Params);
            let parsedParams = JSON.parse(o9Params); 

            let selectQuery = 'Select ([Location].[Location Type].[MF] * [Location].[Subsidiary].filter(~(#.Name =="-"))) Orderby [Location].[Subsidiary].DisplayName;';
            let result = vdCommon.selectQueryList("fn_companyCombo",selectQuery)
            let comboList = vdCommon.fn_makeCombo(result, {DimName : "Location", DimAttbName : "Subsidiary", existAll : false, Sort : "DisplayName", isDisplayNameWithCode : false});

            vdCommon.programEnd();
            return comboList;
        }catch ( e ) {
            RuleOutputToUI = { Status : 'Error', Message : "Js Logic Error : " + e.message };
            return;
        }
    }
    
    function fn_siteGroup2Combo(o9Params){
        try{
            const commonLib = require('o9.NSCM.commonLib');
            const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
            vdCommon.setLogLevel("Debug"); 

            vdCommon.printParams(o9Params);
            let parsedParams = JSON.parse(o9Params); 
            let fbGroup1 = parsedParams.fbGroup1;

            if(fbGroup1 == null) fbGroup1 = "MF";

            let selectQuery = 'Select ([Location].[Location Type].[MF] * [Location].[Site Group1].['+fbGroup1+'] * [Location].[Site Group2].filter(~(#.Name in {"-", "All"})));';
            let result = vdCommon.selectQueryList("fn_companyCombo",selectQuery)
            let comboList = vdCommon.fn_makeCombo(result, {DimName : "Location", DimAttbName : "Site Group2", existAll : false, Sort : "DisplayName", isDisplayNameWithCode : false});

            vdCommon.programEnd();
            return comboList;
        }catch ( e ) {
            RuleOutputToUI = { Status : 'Error', Message : "Js Logic Error : " + e.message };
            return;
        }
    }

    function fn_siteGroup3Combo(o9Params){
        try{
            const commonLib = require('o9.NSCM.commonLib');
            const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
            vdCommon.setLogLevel("Debug"); 

            vdCommon.printParams(o9Params);
            let parsedParams = JSON.parse(o9Params); 
            let fbGroup1 = parsedParams.fbGroup1;
            let fbGroup2 = parsedParams.fbGroup2;


            let selectQuery = 'Select ([Location].[Location Type].[MF] * [Location].[Site Group1].['+fbGroup1+'] * [Location].[Site Group2].['+fbGroup2+'] *[Location].[Site Group3].filter(~(#.Name in {"-", "All"})));';
            let result = vdCommon.selectQueryList("fn_companyCombo",selectQuery)
            let comboList = vdCommon.fn_makeCombo(result, {DimName : "Location", DimAttbName : "Site Group3", existAll : false, Sort : "DisplayName", isDisplayNameWithCode : false});

            vdCommon.programEnd();
            return comboList;
        }catch ( e ) {
            RuleOutputToUI = { Status : 'Error', Message : "Js Logic Error : " + e.message };
            return;
        }
    }

    function fn_flagJDMCombo(o9Params){
        try{
            const commonLib = require('o9.NSCM.commonLib');
            const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);

            vdCommon.setLogLevel("Debug");   
            let comboList = [];

            comboList.push({ Name: "Y", DisplayName: "Y" });
            comboList.push({ Name: "-", DisplayName: "-" });

            vdCommon.printStep(">>>>>>>>>>> fn_flagJDMCombo End");		
            vdCommon.programEnd(); 
            return comboList;
        }catch ( e ) {
            RuleOutputToUI = { Status : 'Error', Message : "Js Logic Error : " + e.message };
            return;
        }         
    }

    function fn_mfSiteStageCombo(o9Params){
        try{
            const commonLib = require('o9.NSCM.commonLib');
            const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
            vdCommon.setLogLevel("Debug");
            
            // 파라미터 가져오기
            vdCommon.printParams(o9Params);	
            let parsedParams = JSON.parse(o9Params); 

            let selectQuery = 'Select ([Location].[MF Site Stage].filter(~(#.Name =="-")) * [Location].[Location Type].[MF]) Orderby [Location].[MF Site Stage].DisplayName;';
            let selectResult = vdCommon.selectQueryList("[fn_weekCombo]" ,selectQuery );
            let comboList = vdCommon.fn_makeCombo(selectResult, {DimName : "Location", DimAttbName : "MF Site Stage", existAll : false, Sort : "DisplayName", isDisplayNameWithCode : false});

            vdCommon.printStep(">>>>>>>>>>> fn_SelMFSiteStage End");
            vdCommon.programEnd();
            return comboList;
        }catch ( e ) {
            RuleOutputToUI = { Status : 'Error', Message : "Js Logic Error : " + e.message };
            return;
        } 
    }

    function fn_companyNameOverrideCombo(o9Params){
        try{
            const commonLib = require('o9.NSCM.commonLib');
            const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
            vdCommon.setLogLevel("Debug");

            vdCommon.printParams(o9Params);
            let parsedParams = JSON.parse(o9Params);

            //selectList(dimension, measure, where, orderby, limit)

            let result = vdCommon.selectList(["[Location].[Location Type].[MF] * [Location].[Subsidiary]"],[],"","","");

            let comboList = vdCommon.fn_makeCombo(result, {DimName : "Location", DimAttbName : "Subsidiary", Sort : "DisplayName", existAll : false}); 

            vdCommon.programEnd()
            
        }catch ( e ) {
            RuleOutputToUI = { Status : 'Error', Message : "Js Logic Error : " + e.message };
            return;
        } 
    }

    function fn_companyDescCombo(o9Params){
        try{
            const commonLib = require('o9.NSCM.commonLib');
            const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
            vdCommon.setLogLevel("Debug");

            vdCommon.printParams(o9Params);
            let parsedParams = JSON.parse(o9Params);
            let fbSiteID = parsedParams.fbSiteID;

            let selectQuery = 'Select ([Location].[Location] * [Location].[Location Type].[MF]) on row, () on column include memberproperties{[Location].[Location], [Company Description]}; ';
            let result = vdCommon.selectQueryList("fn_siteInfo", selectQuery);

            let comboList = [];

            for ( var i = 0; i < result.rowCount; i++ ) {
                dimensionValue = vdCommon.getMember(result.cs, i, "Location", "Location")
                dimensionValueType = vdCommon.getMember(result.cs, i, "Location", "Location Type")
                propertyValue = vdCommon.getPropertyValue(result.cs, i, "Location", "Location", "Company Description");
               
                comboList.push({ Name: dimensionValue.Name, DisplayName: dimensionValue.DisplayName, 
                    PropertyName: "Description" , PropertyValue:propertyValue, 
                    Name2:dimensionValueType.Name, DisplayName2 : dimensionValueType.DisplayName});
            }
            vdCommon.printStep("[fn_siteInfo]" + JSON.stringify(comboList));
            vdCommon.programEnd();
            return comboList;

        }catch ( e ) {
            RuleOutputToUI = { Status : 'Error', Message : "Js Logic Error : " + e.message };
            return;
        }
    }

	
	 fn_loadFunction = function(o9Params){
		let returnData = {};
		let obj = this;
		const functionmap = {
			"fn_DataCheck" : fn_DataCheck,
			"fn_countryNameCombo" : fn_countryNameCombo,
			"fn_regionCombo" : fn_regionCombo,
			"fn_businessTypeCombo" : fn_businessTypeCombo,
			"fn_salesTypeCombo" : fn_salesTypeCombo,
			"fn_companyCombo" : fn_companyCombo,
			"fn_companyNameCombo" : fn_companyNameCombo,
			"fn_companyDescCombo":fn_companyDescCombo,
			"fn_siteIDCombo" : fn_siteIDCombo,
			"fn_siteInfo" : fn_siteInfo,
			"fn_siteGroup2Combo" : fn_siteGroup2Combo,
			"fn_siteGroup3Combo" : fn_siteGroup3Combo,
			"fn_add"  : fn_add,
			"fn_flagJDMCombo" : fn_flagJDMCombo, 
			"fn_mfSiteStageCombo":fn_mfSiteStageCombo,
			"fn_countryCodeCombo" : fn_countryCodeCombo,
			"fn_companyNameOverrideCombo" : fn_companyNameOverrideCombo,
			"fn_update" : fn_update
		};
		try {            
            const commonLib = require('o9.NSCM.commonLib');
            const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
    
            vdCommon.programStart();
            vdCommon.debug("fn_loadFunction=======>");
            vdCommon.printParams(o9Params);
            
            var parsedParams = JSON.parse(o9Params);
			var fbFuncName = parsedParams.fbFuncName;
			delete parsedParams.fbFuncName;

			var comboList = functionmap[fbFuncName](JSON.stringify(parsedParams));
		
			vdCommon.programEnd();
			return comboList;

        } catch ( e ) {
            RuleOutputToUI = { Status : 'Error', Message : "Js Logic Error : " + e.message };
            return;
        }
	};
	
    return{
       // fn_DataCheck : fn_DataCheck,
        fn_countryNameCombo : fn_countryNameCombo,
        fn_regionCombo : fn_regionCombo,
        fn_businessTypeCombo : fn_businessTypeCombo,
        fn_salesTypeCombo : fn_salesTypeCombo,
        fn_companyCombo : fn_companyCombo,
        fn_companyNameCombo : fn_companyNameCombo,
        fn_companyDescCombo:fn_companyDescCombo,
        fn_siteIDCombo : fn_siteIDCombo,
        fn_siteInfo : fn_siteInfo,
        fn_siteGroup2Combo : fn_siteGroup2Combo,
        fn_siteGroup3Combo : fn_siteGroup3Combo,
	//	fn_add  : fn_add,
        fn_flagJDMCombo : fn_flagJDMCombo,
        fn_mfSiteStageCombo:fn_mfSiteStageCombo,
        fn_countryCodeCombo : fn_countryCodeCombo,
        fn_companyNameOverrideCombo : fn_companyNameOverrideCombo,
	//	fn_update : fn_update
    };	
});