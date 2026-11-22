define('o9.NSCM.JSNewModelItemUpdate', ['o9/data/query', 'o9/data/cellset', 'o9.NSCM.commonLib'], function(){
	const programName = "o9.NSCM.JSNewModelItemUpdate";    
    let dimParams = {};

    function fn_sectionComobo(o9Params){
        try {
            const commonLib = require('o9.NSCM.commonLib');
            const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
            vdCommon.setLogLevel("Debug");

            dimParams.dimName = "Item New Model";
            dimParams.dimAttbName = "Section";
            dimParams.sort = "DisplayName";
            dimParams.existAll = false;
            dimParams.withCode= false;            

            var result = vdCommon.selectList(["[Item New Model].[Section]"],
                                             [],
                                             "",
                                             "",
                                             "");
            vdCommon.printCsData(result, 3);

            var comboList = vdCommon.fn_makeCombo(result, {DimName : dimParams.dimName, 
                                                            DimAttbName : dimParams.dimAttbName, 
                                                            Sort :dimParams.sort, 
                                                            existAll : dimParams.existAll, 
                                                            isDisplayNameWithCode : dimParams.withCode});
            vdCommon.debug("ComboData : " + JSON.stringify(comboList));

            vdCommon.programEnd();

            return comboList;
        } catch ( e ) {
            RuleOutputToUI = { Status : 'Error', Message : "Js Logic Error : " + e.message };
            return;
        }
    }

    function fn_kdTypeComobo(o9Params){
        try {
            const commonLib = require('o9.NSCM.commonLib');
            const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
            vdCommon.setLogLevel("Debug");

            dimParams.dimName = "Item New Model";
            dimParams.dimAttbName = "KD Type";
            dimParams.sort = "DisplayName";
            dimParams.existAll = false;
            dimParams.withCode= false;

            var result = vdCommon.selectList(["[Item New Model].[KD Type]"],
                                             [],
                                             "",
                                             "",
                                             "");
            vdCommon.printCsData(result, 3);

            var comboList = vdCommon.fn_makeCombo(result, {DimName : dimParams.dimName, 
                                                            DimAttbName : dimParams.dimAttbName, 
                                                            Sort :dimParams.sort, 
                                                            existAll : dimParams.existAll, 
                                                            isDisplayNameWithCode : dimParams.withCode});
            vdCommon.debug("ComboData : " + JSON.stringify(comboList));

            vdCommon.programEnd();

            return comboList;
        } catch ( e ) {
            RuleOutputToUI = { Status : 'Error', Message : "Js Logic Error : " + e.message };
            return;
        }
    }

    function fn_projectComobo(o9Params){
        try {
            const commonLib = require('o9.NSCM.commonLib');
            const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
            vdCommon.setLogLevel("Debug");

            dimParams.dimName = "Item New Model";
            dimParams.dimAttbName = "Project";
            dimParams.sort = "DisplayName";
            dimParams.existAll = false;
            dimParams.withCode= false;            

            var result = vdCommon.selectList(["[Item New Model].[Project]"],
                                             [],
                                             "",
                                             "",
                                             "");
            vdCommon.printCsData(result, 3);

            var comboList = vdCommon.fn_makeCombo(result, {DimName : dimParams.dimName, 
                                                            DimAttbName : dimParams.dimAttbName, 
                                                            Sort :dimParams.sort, 
                                                            existAll : dimParams.existAll, 
                                                            isDisplayNameWithCode : dimParams.withCode});
            vdCommon.debug("ComboData : " + JSON.stringify(comboList));

            vdCommon.programEnd();

            return comboList;
        } catch ( e ) {
            RuleOutputToUI = { Status : 'Error', Message : "Js Logic Error : " + e.message };
            return;
        }
    }

    function fn_seriesComobo(o9Params){
        try {
            const commonLib = require('o9.NSCM.commonLib');
            const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
            vdCommon.setLogLevel("Debug");

            dimParams.dimName = "Item New Model";
            dimParams.dimAttbName = "Series";
            dimParams.sort = "DisplayName";
            dimParams.existAll = false;
            dimParams.withCode= false;            

            var result = vdCommon.selectList(["[Item New Model].[Series]"],
                                             [],
                                             "",
                                             "",
                                             "");
            vdCommon.printCsData(result, 3);

            var comboList = vdCommon.fn_makeCombo(result, {DimName : dimParams.dimName, 
                                                            DimAttbName : dimParams.dimAttbName, 
                                                            Sort :dimParams.sort, 
                                                            existAll : dimParams.existAll, 
                                                            isDisplayNameWithCode : dimParams.withCode});
            vdCommon.debug("ComboData : " + JSON.stringify(comboList));

            vdCommon.programEnd();

            return comboList;
        } catch ( e ) {
            RuleOutputToUI = { Status : 'Error', Message : "Js Logic Error : " + e.message };
            return;
        }
    }  

    function fn_drTypeComobo(o9Params){
        try {
            const commonLib = require('o9.NSCM.commonLib');
            const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
            vdCommon.setLogLevel("Debug");

            dimParams.dimName = "Item New Model";
            dimParams.dimAttbName = "DR Type";
            dimParams.sort = "DisplayName";
            dimParams.existAll = false;
            dimParams.withCode= false;

            var result = vdCommon.selectList(["[Item New Model].[DR Type]"],
                                             [],
                                             "",
                                             "",
                                             "");
            vdCommon.printCsData(result, 3);

            var comboList = vdCommon.fn_makeCombo(result, {DimName : dimParams.dimName, 
                                                            DimAttbName : dimParams.dimAttbName, 
                                                            Sort :dimParams.sort, 
                                                            existAll : dimParams.existAll, 
                                                            isDisplayNameWithCode : dimParams.withCode});
            vdCommon.debug("ComboData : " + JSON.stringify(comboList));

            vdCommon.programEnd();

            return comboList;
        } catch ( e ) {
            RuleOutputToUI = { Status : 'Error', Message : "Js Logic Error : " + e.message };
            return;
        }
    }

    function fn_inchComobo(o9Params){
        try {
            const commonLib = require('o9.NSCM.commonLib');
            const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
            vdCommon.setLogLevel("Debug");

            dimParams.dimName = "Item New Model";
            dimParams.dimAttbName = "Inch";
            dimParams.sort = "DisplayName";
            dimParams.existAll = false;
            dimParams.withCode= false;

            var result = vdCommon.selectList(["[Item New Model].[Inch]"],
                                             [],
                                             "",
                                             "",
                                             "");
            vdCommon.printCsData(result, 3);

            var comboList = vdCommon.fn_makeCombo(result, {DimName : dimParams.dimName, 
                                                            DimAttbName : dimParams.dimAttbName, 
                                                            Sort :dimParams.sort, 
                                                            existAll : dimParams.existAll, 
                                                            isDisplayNameWithCode : dimParams.withCode});
            vdCommon.debug("ComboData : " + JSON.stringify(comboList));

            vdCommon.programEnd();

            return comboList;
        } catch ( e ) {
            RuleOutputToUI = { Status : 'Error', Message : "Js Logic Error : " + e.message };
            return;
        }
    }

    function fn_locationComobo(o9Params){        
        try {            
            const commonLib = require('o9.NSCM.commonLib');
            const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
            vdCommon.setLogLevel("Debug");

            var result = vdCommon.selectList(["[Location].[Location]"],
                                             [],
                                             "where{[Location].[MF Site Stage].[KD]}",
                                             "",
                                             "");
            vdCommon.printCsData(result, 3);

            dimParams.dimName = "Location";
            dimParams.dimAttbName = "Location";
            dimParams.sort = "DisplayName";
            dimParams.existAll = false;
            dimParams.withCode= false;

            var comboList = vdCommon.fn_makeCombo(result, {DimName : dimParams.dimName, 
                                                            DimAttbName : dimParams.dimAttbName, 
                                                            Sort :dimParams.sort, 
                                                            existAll : dimParams.existAll, 
                                                            isDisplayNameWithCode : dimParams.withCode});
            vdCommon.debug("ComboData : " + JSON.stringify(comboList));

            vdCommon.programEnd();

            return comboList;
        } catch ( e ) {
            RuleOutputToUI = { Status : 'Error', Message : "Js Logic Error : " + e.message };
            return;
        }
    }
    
    function fn_ap2Comobo(o9Params){    
        try {            
            const commonLib = require('o9.NSCM.commonLib');
            const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
            vdCommon.setLogLevel("Debug");            

            // 파라메타 가져오기
            vdCommon.printParams(o9Params);
            let parsedParams = JSON.parse(o9Params); 
            let fbGC = parsedParams.fbGC;

            dimParams.dimName = "Sales Domain";
            dimParams.dimAttbName = "AP2";
            dimParams.sort = "DisplayName";
            dimParams.existAll = false;
            dimParams.withCode= false;            

            var result = vdCommon.selectList(["[Sales Domain].[AP2] * [Sales Domain].[GC].["+fbGC+"]"],
                                             [],
                                             "",
                                             "",
                                             "");
            vdCommon.printCsData(result, 3);

            var comboList = vdCommon.fn_makeCombo(result, {DimName : dimParams.dimName, 
                                                            DimAttbName : dimParams.dimAttbName, 
                                                            Sort :dimParams.sort, 
                                                            existAll : dimParams.existAll, 
                                                            isDisplayNameWithCode : dimParams.withCode});
            vdCommon.debug("ComboData : " + JSON.stringify(comboList));

            vdCommon.programEnd();

            return comboList;
        } catch ( e ) {
            RuleOutputToUI = { Status : 'Error', Message : "Js Logic Error : " + e.message };
            return;
        }
    }

    function fn_gradeComobo(o9Params){
        try {            
            const commonLib = require('o9.NSCM.commonLib');
            const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
            vdCommon.setLogLevel("Debug");            

            // 파라메타 가져오기
            let parsedParams = JSON.parse(o9Params); 
            let fbGC = parsedParams.fbGC;

            dimParams.dimName = "Item New Model";
            dimParams.dimAttbName = "Grade";
            dimParams.sort = "DisplayName";
            dimParams.existAll = false;
            dimParams.withCode= false;

            var result = vdCommon.selectList(["[Item New Model].[Grade]"],
                                             [],
                                             "",
                                             "",
                                             "");
            vdCommon.printCsData(result, 3);

            var comboList = vdCommon.fn_makeCombo(result, {DimName : dimParams.dimName, 
                                                            DimAttbName : dimParams.dimAttbName, 
                                                            Sort :dimParams.sort, 
                                                            existAll : dimParams.existAll, 
                                                            isDisplayNameWithCode : dimParams.withCode});
            vdCommon.debug("ComboData : " + JSON.stringify(comboList));

            vdCommon.programEnd();

            return comboList;
        } catch ( e ) {
            RuleOutputToUI = { Status : 'Error', Message : "Js Logic Error : " + e.message };
            return;
        }
    }

    function fn_productComobo(o9Params){
        try {            
            const commonLib = require('o9.NSCM.commonLib');
            const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
            vdCommon.setLogLevel("Debug");            

            // 파라메타 가져오기
            let parsedParams = JSON.parse(o9Params); 
            let fbSection = parsedParams.fbSection;

            dimParams.dimName = "Item New Model";
            dimParams.dimAttbName = "Product";
            dimParams.sort = "DisplayName";
            dimParams.existAll = false;
            dimParams.withCode= false;

            var result = vdCommon.selectList(["[Item New Model].[Product] * [Item New Model].[Section].["+fbSection+"]"],
                                             [],
                                             "",
                                             "",
                                             "");
            vdCommon.printCsData(result, 3);  

            var comboList = vdCommon.fn_makeCombo(result, {DimName : dimParams.dimName, 
                                                            DimAttbName : dimParams.dimAttbName, 
                                                            Sort :dimParams.sort, 
                                                            existAll : dimParams.existAll, 
                                                            isDisplayNameWithCode : dimParams.withCode});
            vdCommon.debug("ComboData : " + JSON.stringify(comboList));

            vdCommon.programEnd();

            return comboList;
        } catch ( e ) {
            RuleOutputToUI = { Status : 'Error', Message : "Js Logic Error : " + e.message };
            return;
        }
    }

    function fn_add(o9Params){
        try {            
            const commonLib = require('o9.NSCM.commonLib');
            const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
            vdCommon.setLogLevel("Debug");            

            // 파라메타 가져오기
            vdCommon.printParams(o9Params);
            let parsedParams = JSON.parse(o9Params); 
            let fbVersion = parsedParams.fbVersion;
            let fbSection = parsedParams.fbSection;
            let fbKDType = parsedParams.fbKDType;
            let fbProject = parsedParams.fbProject;
            let fbSeries = parsedParams.fbSeries;
            let fbDRType = parsedParams.fbDRType;
            let fbInch = parsedParams.fbInch;
            let fbLocation = parsedParams.fbLocation;
            let fbItem = parsedParams.fbItem;
            let fbGC = parsedParams.fbGC;
            let fbAP2 = parsedParams.fbAP2;
            let fbGrade = parsedParams.fbGrade;
            let fbProduct = parsedParams.fbProduct;

            let selectDimQuery = [];
            let createDimQuery = [];
            let createDimValue = [];
            let selectMeasureDimQuery = [];            
            let selectMeasureQuery = [];
            let createMeasurDimeQuery = [];            
            let createMeasureQuery = [];

            let categoryData= [];
            categoryData.push("Plan");
            categoryData.push("Actual");

            //1.Item New Model Dimension 체크함.
            selectDimQuery.push('[Item New Model].[Section].['+fbSection+']');
            selectDimQuery.push('[Item New Model].[KD Type].['+fbKDType+']');
            selectDimQuery.push('[Item New Model].[Product].['+fbProduct+']');
            selectDimQuery.push('[Item New Model].[Project].['+fbProject+']');
            selectDimQuery.push('[Item New Model].[Series].['+fbSeries+']');
            selectDimQuery.push('[Item New Model].[DR Type].['+fbDRType+']');
            selectDimQuery.push('[Item New Model].[Inch].['+fbInch+']');
            selectDimQuery.push('[Item New Model].[Grade].['+fbGrade+']');
            selectDimQuery.push('[Item New Model].[Item].['+fbItem+']');
            selectDimQuery.push('[Item New Model].[Marketing Name].[-]');


            if ( !vdCommon.existDimension(selectDimQuery) ) {
                //1.[Item New Model] Dim Create
                vdCommon.debug(" [Item New Model] Dim Create");

                createDimQuery.push('[Item New Model].[Section]');
                createDimQuery.push('[Item New Model].[KD Type]');
                createDimQuery.push('[Item New Model].[Product]');
                createDimQuery.push('[Item New Model].[Project]');
                createDimQuery.push('[Item New Model].[Series]');
                createDimQuery.push('[Item New Model].[DR Type]');
                createDimQuery.push('[Item New Model].[Inch]');
                createDimQuery.push('[Item New Model].[Grade]');
                createDimQuery.push('[Item New Model].[Item]');
                createDimQuery.push('[Item New Model].[Marketing Name]');

                createDimValue.push('"'+fbSection +'"');
                createDimValue.push('"'+fbKDType +'"');
                createDimValue.push('"'+fbProduct +'"');
                createDimValue.push('"'+fbProject +'"');
                createDimValue.push('"'+fbSeries +'"');
                createDimValue.push('"'+fbDRType +'"');
                createDimValue.push('"'+fbInch +'"');
                createDimValue.push('"'+fbGrade +'"');
                createDimValue.push('"'+fbItem +'"');
                createDimValue.push('"'+"-" +'"');                

                vdCommon.createDimension(createDimQuery, createDimValue);
            }

            //2. [New Model Mgmt] Measure 체크
            selectMeasureDimQuery.push("[Version].[Version Name].["+fbVersion+"]");
            selectMeasureDimQuery.push("[Location].[Location].["+fbLocation+"]");
            selectMeasureDimQuery.push("[Sales Domain].[AP2].["+fbAP2+"]");
            selectMeasureDimQuery.push("[Item New Model].[Item].["+fbItem+"]");

            selectMeasureQuery.push("Measure.[New Model Mgmt_AP2 Adj]");            
            selectMeasureQuery.push("Measure.[New Model Mgmt_DR Type Adj]");
            selectMeasureQuery.push("Measure.[New Model Mgmt_GC Adj]");
            selectMeasureQuery.push("Measure.[New Model Mgmt_Grade Adj]");
            selectMeasureQuery.push("Measure.[New Model Mgmt_Inch Adj]");
            selectMeasureQuery.push("Measure.[New Model Mgmt_Item Adj]");
            selectMeasureQuery.push("Measure.[New Model Mgmt_KD Type Adj]");
            selectMeasureQuery.push("Measure.[New Model Mgmt_Location Adj]");
            selectMeasureQuery.push("Measure.[New Model Mgmt_Product Adj]");
            selectMeasureQuery.push("Measure.[New Model Mgmt_Project Adj]");
            selectMeasureQuery.push("Measure.[New Model Mgmt_Section Adj]");
            selectMeasureQuery.push("Measure.[New Model Mgmt_Series Adj]");

            if(!vdCommon.existMeasure(selectMeasureDimQuery, selectMeasureQuery, "")) {
                vdCommon.debug(" [New Model Mgmt] Measure Create");
                //[New Model Mgmt] Measure Create
                createMeasurDimeQuery = [];
                createMeasurDimeQuery.push("[Version].[Version Name].["+fbVersion+"]");
                createMeasurDimeQuery.push("[Location].[Location].["+fbLocation+"]");
                createMeasurDimeQuery.push("[Sales Domain].[AP2].["+fbAP2+"]");
                createMeasurDimeQuery.push("[Item New Model].[Item].["+fbItem+"]");

                createMeasureQuery = [];
                createMeasureQuery.push('Measure.[New Model Mgmt_AP2 Adj] = "-";');             
                createMeasureQuery.push('Measure.[New Model Mgmt_DR Type Adj] = "-";'); 
                createMeasureQuery.push('Measure.[New Model Mgmt_GC Adj] = "-";'); 
                createMeasureQuery.push('Measure.[New Model Mgmt_Grade Adj] = "-";'); 
                createMeasureQuery.push('Measure.[New Model Mgmt_Inch Adj] = "-";'); 
                createMeasureQuery.push('Measure.[New Model Mgmt_Item Adj] = "-";'); 
                createMeasureQuery.push('Measure.[New Model Mgmt_KD Type Adj] = "-";'); 
                createMeasureQuery.push('Measure.[New Model Mgmt_Location Adj] = "-";'); 
                createMeasureQuery.push('Measure.[New Model Mgmt_Product Adj] = "-";'); 
                createMeasureQuery.push('Measure.[New Model Mgmt_Project Adj] = "-";'); 
                createMeasureQuery.push('Measure.[New Model Mgmt_Section Adj] = "-";'); 
                createMeasureQuery.push('Measure.[New Model Mgmt_Series Adj] = "-";'); 
                createMeasureQuery.push('Measure.[New Model Mgmt_Created By] = CurrentUser().[User Name];');
                createMeasureQuery.push('Measure.[New Model Mgmt_Creation Time] = dateadd(Now(),9,"hour");');
                createMeasureQuery.push('Measure.[New Model Mgmt_Valid Flag] = "CREATE";');  

                vdCommon.createMeasure(createMeasurDimeQuery, createMeasureQuery) 
            }

            //3. [New Model] Measure 체크
            //Array Rest
            selectDimQuery = [];
            selectMeasureDimQuery = [];            
            selectMeasureQuery = [];
            createMeasurDimeQuery = [];            
            createMeasureQuery = [];

            selectMeasureDimQuery.push("[Version].[Version Name].["+fbVersion+"]");
            selectMeasureDimQuery.push("[Location].[Location].["+fbLocation+"]");
            selectMeasureDimQuery.push("[Sales Domain].[AP2].["+fbAP2+"]");
            selectMeasureDimQuery.push("[Item New Model].[Item].["+fbItem+"]");
            selectMeasureDimQuery.push("[Category].[Category]");
            
            selectMeasureQuery.push("Measure.[New Model_Air SOP Date]");
            selectMeasureQuery.push("Measure.[New Model_Air SOP Qty]");
            selectMeasureQuery.push("Measure.[New Model_Air SOP To Site]");
            selectMeasureQuery.push("Measure.[New Model_BOM HQ Status]");
            selectMeasureQuery.push("Measure.[New Model_BOM Local Status]");
            selectMeasureQuery.push("Measure.[New Model_Code Status]");
            selectMeasureQuery.push("Measure.[New Model_Dash Status]");
            selectMeasureQuery.push("Measure.[New Model_Dev DV]");
            selectMeasureQuery.push("Measure.[New Model_Dev DVR]");
            selectMeasureQuery.push("Measure.[New Model_Dev LMI]");
            selectMeasureQuery.push("Measure.[New Model_Dev PIA]");
            selectMeasureQuery.push("Measure.[New Model_Dev PR]");
            selectMeasureQuery.push("Measure.[New Model_Dev PRA]");
            selectMeasureQuery.push("Measure.[New Model_Dev PV]");
            selectMeasureQuery.push("Measure.[New Model_Dev PVR]");
            selectMeasureQuery.push("Measure.[New Model_LCM Approval]");
            selectMeasureQuery.push("Measure.[New Model_LCM CDR2]");
            selectMeasureQuery.push("Measure.[New Model_LCM CPA]");
            selectMeasureQuery.push("Measure.[New Model_LCM Code]");
            selectMeasureQuery.push("Measure.[New Model_LCM From Site]");
            selectMeasureQuery.push("Measure.[New Model_LCM L/BOM1]");
            selectMeasureQuery.push("Measure.[New Model_LCM MP]");
            selectMeasureQuery.push("Measure.[New Model_LCM Model]");
            selectMeasureQuery.push("Measure.[New Model_LCM SR]");
            selectMeasureQuery.push("Measure.[New Model_LCM SRA]");
            selectMeasureQuery.push("Measure.[New Model_LCM SRP-F]");
            selectMeasureQuery.push("Measure.[New Model_LCM SRP-S]");
            selectMeasureQuery.push("Measure.[New Model_LCM TP Mode]");
            selectMeasureQuery.push("Measure.[New Model_LCM Vendor]");
            selectMeasureQuery.push("Measure.[New Model_MP DP Status]");
            selectMeasureQuery.push("Measure.[New Model_Mfg Date]");
            selectMeasureQuery.push("Measure.[New Model_Mfg Qty]");
            selectMeasureQuery.push("Measure.[New Model_Platform]");
            selectMeasureQuery.push("Measure.[New Model_RTS DP Status]");
            selectMeasureQuery.push("Measure.[New Model_RTS GI Status]");
            selectMeasureQuery.push("Measure.[New Model_RUN/DROP]");
            selectMeasureQuery.push("Measure.[New Model_SET Aging]");
            selectMeasureQuery.push("Measure.[New Model_SET MP]");
            selectMeasureQuery.push("Measure.[New Model_SET PLM SRA]");
            selectMeasureQuery.push("Measure.[New Model_SET SOP]");
            selectMeasureQuery.push("Measure.[New Model_SET SR]");
            selectMeasureQuery.push("Measure.[New Model_SET SRA]");
            selectMeasureQuery.push("Measure.[New Model_SET SRP-F]");
            selectMeasureQuery.push("Measure.[New Model_SET SRP-S]");
            selectMeasureQuery.push("Measure.[New Model_SOP Date]");
            selectMeasureQuery.push("Measure.[New Model_SOP Qty]");
            selectMeasureQuery.push("Measure.[New Model_SOP Register Date]");
            selectMeasureQuery.push("Measure.[New Model_SOP Status]");
            selectMeasureQuery.push("Measure.[New Model_SR Date]");
            selectMeasureQuery.push("Measure.[New Model_SR Prod Qty]");
            selectMeasureQuery.push("Measure.[New Model_SR Prod To Site]");
            selectMeasureQuery.push("Measure.[New Model_SR Qty]");
            selectMeasureQuery.push("Measure.[New Model_SR To Site]");
            selectMeasureQuery.push("Measure.[New Model_SRP Prod LCM Qty]");
            selectMeasureQuery.push("Measure.[New Model_SRP Prod SET Qty]");
            selectMeasureQuery.push("Measure.[New Model_Sales LT]");
            selectMeasureQuery.push("Measure.[New Model_Sales RDD]");
            selectMeasureQuery.push("Measure.[New Model_Sales RTS]");
            selectMeasureQuery.push("Measure.[New Model_Sales Reset]");
            selectMeasureQuery.push("Measure.[New Model_Update Date]");
            selectMeasureQuery.push("Measure.[New Model_Update Reason]");
            selectMeasureQuery.push("Measure.[New Model_Updated By]");
            selectMeasureQuery.push("Measure.[New Model_Year]");     

            if(!vdCommon.existMeasure(selectMeasureDimQuery, selectMeasureQuery, "")) {
                vdCommon.debug(" [New Model] Measure Create");

                createMeasureQuery.push('Measure.[New Model_Air SOP Date] = null;');
                createMeasureQuery.push('Measure.[New Model_Air SOP Qty] = null;');
                createMeasureQuery.push('Measure.[New Model_Air SOP To Site] = null;');
                createMeasureQuery.push('Measure.[New Model_BOM HQ Status] = null;');
                createMeasureQuery.push('Measure.[New Model_BOM Local Status] = null;');
                createMeasureQuery.push('Measure.[New Model_Code Status] = null;');
                createMeasureQuery.push('Measure.[New Model_Dash Status] = null;');
                createMeasureQuery.push('Measure.[New Model_Dev DV] = null;');
                createMeasureQuery.push('Measure.[New Model_Dev DVR] = null;');
                createMeasureQuery.push('Measure.[New Model_Dev LMI] = null;');
                createMeasureQuery.push('Measure.[New Model_Dev PIA] = null;');
                createMeasureQuery.push('Measure.[New Model_Dev PR] = null;');
                createMeasureQuery.push('Measure.[New Model_Dev PRA] = null;');
                createMeasureQuery.push('Measure.[New Model_Dev PV] = null;');
                createMeasureQuery.push('Measure.[New Model_Dev PVR] = null;');
                createMeasureQuery.push('Measure.[New Model_LCM Approval] = null;');
                createMeasureQuery.push('Measure.[New Model_LCM CDR2] = null;');
                createMeasureQuery.push('Measure.[New Model_LCM CPA] = null;');
                createMeasureQuery.push('Measure.[New Model_LCM Code] = null;');
                createMeasureQuery.push('Measure.[New Model_LCM From Site] = null;');
                createMeasureQuery.push('Measure.[New Model_LCM L/BOM1] = null;');
                createMeasureQuery.push('Measure.[New Model_LCM MP] = null;');
                createMeasureQuery.push('Measure.[New Model_LCM Model] = null;');
                createMeasureQuery.push('Measure.[New Model_LCM SR] = null;');
                createMeasureQuery.push('Measure.[New Model_LCM SRA] = null;');
                createMeasureQuery.push('Measure.[New Model_LCM SRP-F] = null;');
                createMeasureQuery.push('Measure.[New Model_LCM SRP-S] = null;');
                createMeasureQuery.push('Measure.[New Model_LCM TP Mode] = null;');
                createMeasureQuery.push('Measure.[New Model_LCM Vendor] = null;');
                createMeasureQuery.push('Measure.[New Model_MP DP Status] = null;');
                createMeasureQuery.push('Measure.[New Model_Mfg Date] = null;');
                createMeasureQuery.push('Measure.[New Model_Mfg Qty] = null;');
                createMeasureQuery.push('Measure.[New Model_Platform] = null;');
                createMeasureQuery.push('Measure.[New Model_RTS DP Status] = null;');
                createMeasureQuery.push('Measure.[New Model_RTS GI Status] = null;');
                createMeasureQuery.push('Measure.[New Model_RUN/DROP] = null;');
                createMeasureQuery.push('Measure.[New Model_SET Aging] = null;');
                createMeasureQuery.push('Measure.[New Model_SET MP] = null;');
                createMeasureQuery.push('Measure.[New Model_SET PLM SRA] = null;');
                createMeasureQuery.push('Measure.[New Model_SET SOP] = null;');
                createMeasureQuery.push('Measure.[New Model_SET SR] = null;');
                createMeasureQuery.push('Measure.[New Model_SET SRA] = null;');
                createMeasureQuery.push('Measure.[New Model_SET SRP-F] = null;');
                createMeasureQuery.push('Measure.[New Model_SET SRP-S] = null;');
                createMeasureQuery.push('Measure.[New Model_SOP Date] = null;');
                createMeasureQuery.push('Measure.[New Model_SOP Qty] = null;');
                createMeasureQuery.push('Measure.[New Model_SOP Register Date] = null;');
                createMeasureQuery.push('Measure.[New Model_SOP Status] = null;');
                createMeasureQuery.push('Measure.[New Model_SR Date] = null;');
                createMeasureQuery.push('Measure.[New Model_SR Prod Qty] = null;');
                createMeasureQuery.push('Measure.[New Model_SR Prod To Site] = null;');
                createMeasureQuery.push('Measure.[New Model_SR Qty] = null;');
                createMeasureQuery.push('Measure.[New Model_SR To Site] = null;');
                createMeasureQuery.push('Measure.[New Model_SRP Prod LCM Qty] = null;');
                createMeasureQuery.push('Measure.[New Model_SRP Prod SET Qty] = null;');
                createMeasureQuery.push('Measure.[New Model_Sales LT] = null;');
                createMeasureQuery.push('Measure.[New Model_Sales RDD] = null;');
                createMeasureQuery.push('Measure.[New Model_Sales RTS] = null;');
                createMeasureQuery.push('Measure.[New Model_Sales Reset] = null;');
                createMeasureQuery.push('Measure.[New Model_Update Reason] = null;');
                createMeasureQuery.push('Measure.[New Model_Update Date] = dateadd(Now(),9,"hour");');
                createMeasureQuery.push('Measure.[New Model_Updated By] = CurrentUser().[User Name];');
                createMeasureQuery.push('Measure.[New Model_Year] = null;');

                createMeasurDimeQuery = [];
                createMeasurDimeQuery.push('[Version].[Version Name].['+fbVersion+']');
                createMeasurDimeQuery.push('[Location].[Location].['+fbLocation+']');
                createMeasurDimeQuery.push('[Sales Domain].[AP2].['+fbAP2+']');
                createMeasurDimeQuery.push('[Item New Model].[Item].['+fbItem+']');
                createMeasurDimeQuery.push('[Category].[Category].filter(#.Name in {"'+categoryData[0]+'","'+categoryData[1]+'"})');

                vdCommon.createMeasure(createMeasurDimeQuery, createMeasureQuery)

            }

            vdCommon.programEnd();

        } catch ( e ) {
            RuleOutputToUI = { Status : 'Error', Message : "Js Logic Error : " + e.message };
            return;
        }        
    }


    function fn_dataCheck(result, index, measureId, dataType){
        try{
            const commonLib = require('o9.NSCM.commonLib');
            const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
            vdCommon.setLogLevel("Debug");  
            vdCommon.debug("["+result+"]["+index+"]["+measureId+"]["+dataType+"]");

            var measureValue = result.cs.row(index).cell(result.cs.measureColumnIndex(measureId))
            
            if(measureValue != null){
                if(dataType == "String" || dataType == "Datetime"){
                    measureValue = '"' + measureValue + '"';
                }    
            }

            vdCommon.programEnd();
            //vdCommon.debug("["+result+"]["+index+"]["+measureId+"]["+dataType+"]["+measureValue+"][]");
            return measureValue;

        } catch ( e ) {
            RuleOutputToUI = { Status : 'Error', Message : "Js Logic Error : " + e.message };
            return;
        }  
    }

    function fn_dimDataCheck(selectQuery, pDimName, dimData){
        try{
            const commonLib = require('o9.NSCM.commonLib');
            const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
            vdCommon.setLogLevel("Debug");  
            vdCommon.debug("["+selectQuery+"]["+pDimName+"]["+JSON.stringify(dimData)+"]");
            var result = vdCommon.selectList([selectQuery],[], "", "","");
        
            if(result.cs.rowCount <= 0){
                vdCommon.updateMeasure(["[Version].[Version Name].["+fbVersion+"]",
                                    "[Location].[Location].[" + dimData.Location + "]",
                                    "[Sales Domain].[AP2].[" + dimData.AP2 + "]",
                                    "[Item New Model].[Item].[" + dimData.Item + "]"],
                                    ['Measure.[New Model Mgmt_Update Time] = dateadd(Now(),9,"hour");',
                                    'Measure.[New Model Mgmt_Updated By] = CurrentUser().[User Name] ;',
                                    'Measure.[New Model Mgmt_Valid Flag] = "'+pDimName+': not Reg.";']);

                return { rtnValue : false, columns : "" };
                //return false;
            }else{                
                //return true;
                return { rtnValue : true, Value : fn_dataCheck(result, 0,pDimName,"String") };
            }             

        } catch ( e ) {
            RuleOutputToUI = { Status : 'Error', Message : "Js Logic Error : " + e.message };
            return;
        }    
      }

    function fn_apply(o9Params){
        try {            
            const commonLib = require('o9.NSCM.commonLib');
            const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
            vdCommon.setLogLevel("Debug");  
            
            // 파라메타 가져오기
            vdCommon.printParams(o9Params);
            let parsedParams = JSON.parse(o9Params); 
            let fbVersion = parsedParams.fbVersion;

            //New Model Item Update 화면에서 수정한 데이타 있는지 조회한다.
            // [New Model Mgmt] 메져 데이타를 조회
            //dimension
        
            let createDimQuery = [];
            let createDimValue = [];    

            let selectDimension = [];
            let selectMeasure = [];

            let selectMeasureDimQuery = [];
            let selectMeasureQuery = []; 
            let whereQuery = "";
            let createMeasurDimeQuery = [];
            let createMeasureQuery = [];

            let measureDimQuery = [];
            let measureQuery = [];

            let categoryData= [];
            categoryData.push("Plan");
            categoryData.push("Actual");

            selectDimension.push("[Version].[Version Name].["+fbVersion+"]");
            selectDimension.push("[Location].[Location]");
            selectDimension.push("[Sales Domain].[AP2]");
            selectDimension.push("[Item New Model].[Item]");
            selectDimension.push("[Item New Model].[DR Type]");
            selectDimension.push("[Item New Model].[Grade]");
            selectDimension.push("[Item New Model].[Inch]");
            selectDimension.push("[Item New Model].[KD Type]");
            selectDimension.push("[Item New Model].[Marketing Name]");
            selectDimension.push("[Item New Model].[Product]");
            selectDimension.push("[Item New Model].[Project]");
            selectDimension.push("[Item New Model].[Section]");
            selectDimension.push("[Item New Model].[Series]");

            selectMeasure.push("Measure.[New Model Mgmt_AP2 Adj]"); 
            selectMeasure.push("Measure.[New Model Mgmt_DR Type Adj]"); 
            selectMeasure.push("Measure.[New Model Mgmt_GC Adj]"); 
            selectMeasure.push("Measure.[New Model Mgmt_Grade Adj]"); 
            selectMeasure.push("Measure.[New Model Mgmt_Inch Adj]"); 
            selectMeasure.push("Measure.[New Model Mgmt_Item Adj]"); 
            selectMeasure.push("Measure.[New Model Mgmt_KD Type Adj]"); 
            selectMeasure.push("Measure.[New Model Mgmt_Location Adj]"); 
            selectMeasure.push("Measure.[New Model Mgmt_Product Adj]"); 
            selectMeasure.push("Measure.[New Model Mgmt_Project Adj]"); 
            selectMeasure.push("Measure.[New Model Mgmt_Section Adj]"); 
            selectMeasure.push("Measure.[New Model Mgmt_Series Adj]"); 
            selectMeasure.push("Measure.[New Model Mgmt_Valid Flag]");

            //selectList(dimension, measure, where, orderby, limit)           

            whereQuery = 'Where{ '
                    +'~(Measure.[New Model Mgmt_Section Adj] == "-") || '
                    +'~(Measure.[New Model Mgmt_KD Type Adj] == "-") || '
                    +'~(Measure.[New Model Mgmt_Project Adj] == "-") || '
                    +'~(Measure.[New Model Mgmt_Series Adj] == "-") || '
                    +'~(Measure.[New Model Mgmt_DR Type Adj] == "-") || '
                    +'~(Measure.[New Model Mgmt_Inch Adj] == "-") || '
                    +'~(Measure.[New Model Mgmt_Grade Adj] == "-") || '
                    +'~(Measure.[New Model Mgmt_Product Adj] == "-")|| '
                    +'~(Measure.[New Model Mgmt_Item Adj] == "-")' 
                    +'}';                    


            let result = vdCommon.selectList(selectDimension, selectMeasure, whereQuery, "","");

            for ( var i = 0; i < result.cs.rowCount; i++ ) {
                let dimLocation = result.cs.row(i).cell(result.cs.memberColumnIndex("Location", "Location")).Name; 
                let dimAP2 = result.cs.row(i).cell(result.cs.memberColumnIndex("Sales Domain", "AP2")).Name; 
                let dimItem = result.cs.row(i).cell(result.cs.memberColumnIndex("Item New Model", "Item")).Name;
                let dimDRType = result.cs.row(i).cell(result.cs.memberColumnIndex("Item New Model", "DR Type")).Name;
                let dimGrade = result.cs.row(i).cell(result.cs.memberColumnIndex("Item New Model", "Grade")).Name;
                let dimInch = result.cs.row(i).cell(result.cs.memberColumnIndex("Item New Model", "Inch")).Name;
                let dimKDType = result.cs.row(i).cell(result.cs.memberColumnIndex("Item New Model", "KD Type")).Name;
                let dimMarketingName = result.cs.row(i).cell(result.cs.memberColumnIndex("Item New Model", "Marketing Name")).Name;
                let dimProduct = result.cs.row(i).cell(result.cs.memberColumnIndex("Item New Model", "Product")).Name;
                let dimProject = result.cs.row(i).cell(result.cs.memberColumnIndex("Item New Model", "Project")).Name;
                let dimSection = result.cs.row(i).cell(result.cs.memberColumnIndex("Item New Model", "Section")).Name;
                let dimSeries = result.cs.row(i).cell(result.cs.memberColumnIndex("Item New Model", "Series")).Name;

                let measureLocation = result.cs.row(i).cell(result.cs.measureColumnIndex("New Model Mgmt_Location Adj"));
                let measureAP2 = result.cs.row(i).cell(result.cs.measureColumnIndex("New Model Mgmt_AP2 Adj"));
                let measureGC = result.cs.row(i).cell(result.cs.measureColumnIndex("New Model Mgmt_GC Adj")); 
                let measureItem = result.cs.row(i).cell(result.cs.measureColumnIndex("New Model Mgmt_Item Adj"));
                let measureDRType = result.cs.row(i).cell(result.cs.measureColumnIndex("New Model Mgmt_DR Type Adj"));
                let measureGrade = result.cs.row(i).cell(result.cs.measureColumnIndex("New Model Mgmt_Grade Adj"));
                let measureInch = result.cs.row(i).cell(result.cs.measureColumnIndex("New Model Mgmt_Inch Adj"));
                let measureKDType = result.cs.row(i).cell(result.cs.measureColumnIndex("New Model Mgmt_KD Type Adj"));
                let measureProduct = result.cs.row(i).cell(result.cs.measureColumnIndex("New Model Mgmt_Product Adj"));
                let measureProject = result.cs.row(i).cell(result.cs.measureColumnIndex("New Model Mgmt_Project Adj"));
                let measureSection = result.cs.row(i).cell(result.cs.measureColumnIndex("New Model Mgmt_Section Adj"));
                let measureSeries = result.cs.row(i).cell(result.cs.measureColumnIndex("New Model Mgmt_Series Adj"));
                let measureValidFlag = result.cs.row(i).cell(result.cs.measureColumnIndex("New Model Mgmt_Valid Flag"));               

                //AP2, Location 정보를 체크함.              
                let dimData = {};
                dimData.Location = dimLocation;
                dimData.AP2 = dimAP2;
                dimData.Item = dimItem;
                vdCommon.debug("[New Model Mgmt] Data["+measureLocation+"]["+measureAP2+"]Item["+dimItem+"]["+measureItem+"]["+JSON.stringify(dimData)+"]");
                if(measureLocation != "-"){
                    vdCommon.debug("[measureLocation] Checking");
                    var strQuery = '[Location].[Location].filter(#.Name == "'+measureLocation+'" || #.DisplayName == "'+measureLocation+'")'; 
                    var chkDim = fn_dimDataCheck(strQuery, "Location", dimData) ;
                    vdCommon.debug("[measureLocation] Checking::" + JSON.stringify(chkDim) );
                    if(!chkDim.rtnValue){
                        continue;
                    }else{
                        measureLocation = chkDim.Value;
                    }
                }

                if(measureAP2 != "-"){
                    var strQuery = '[Sales Domain].[AP2].filter(#.Name == "'+measureAP2+'" || #.DisplayName == "'+measureAP2+'")';                    
                    var chkDim = fn_dimDataCheck(strQuery, "AP2", dimData) ;
                    vdCommon.debug("[measureAP2] Checking::" + chkDim );
                    vdCommon.debug("[measureLocation] Checking::" + JSON.stringify(chkDim) );
                    if(!chkDim.rtnValue){
                        continue;
                    }else{
                        measureAP2 = chkDim.Value;
                    }
                }                

                //Item 수정 여부체크
                //디엔젼 Item, 메져 Item 다른 경우 신규 디멘져 등록이 필요함.                         
                if((measureItem != "-") & (measureItem != dimItem)){

                    //(1) Item New Model 메져 등록 여부 체크
                    selectDimQuery = [];
                    createDimQuery = [];
                    createDimValue = [];    

                    selectDimQuery.push('[Item New Model].[Item].['+measureItem+']');
                    //selectDimQuery.push('[Item New Model].[Marketing Name].[-]');

                    createDimQuery.push('[Item New Model].[Item]');
                    createDimValue.push('"'+measureItem +'"');
                    createDimQuery.push('[Item New Model].[Marketing Name]');                    
                    createDimValue.push('"'+dimMarketingName +'"');   

                    if(measureSection != "-"){
                        selectDimQuery.push('[Item New Model].[Section].['+measureSection+']');
                        createDimQuery.push('[Item New Model].[Section]');
                        createDimValue.push('"'+measureSection +'"');
                    }else{
                        selectDimQuery.push('[Item New Model].[Section].['+dimSection+']');
                        createDimQuery.push('[Item New Model].[Section]');
                        createDimValue.push('"'+dimSection +'"');
                    }

                    if(measureKDType != "-"){
                        selectDimQuery.push('[Item New Model].[KD Type].['+measureKDType+']');
                        createDimQuery.push('[Item New Model].[KD Type]');
                        createDimValue.push('"'+measureKDType +'"');
                    }else{
                        selectDimQuery.push('[Item New Model].[KD Type].['+dimKDType+']');
                        createDimQuery.push('[Item New Model].[KD Type]');
                        createDimValue.push('"'+dimKDType +'"');
                    }
                    
                    if(measureProject != "-"){
                        selectDimQuery.push('[Item New Model].[Project].['+measureProject+']');
                        createDimQuery.push('[Item New Model].[Project]');
                        createDimValue.push('"'+measureProject +'"');
                    }else{
                        selectDimQuery.push('[Item New Model].[Project].['+dimProject+']');
                        createDimQuery.push('[Item New Model].[Project]');
                        createDimValue.push('"'+dimProject +'"');
                    }
                    
                    if(measureProduct != "-"){
                        selectDimQuery.push('[Item New Model].[Product].['+measureProduct+']');
                        createDimQuery.push('[Item New Model].[Product]');
                        createDimValue.push('"'+measureProduct +'"');
                    }else{
                        selectDimQuery.push('[Item New Model].[Product].['+dimProduct+']');
                        createDimQuery.push('[Item New Model].[Product]');
                        createDimValue.push('"'+dimProduct +'"');
                    }
                    
                    if(measureSeries != "-"){
                        selectDimQuery.push('[Item New Model].[Series].['+measureSeries+']');
                        createDimQuery.push('[Item New Model].[Series]');
                        createDimValue.push('"'+measureSeries +'"');
                    }else{
                        selectDimQuery.push('[Item New Model].[Series].['+dimSeries+']');
                        createDimQuery.push('[Item New Model].[Series]');
                        createDimValue.push('"'+dimSeries +'"');
                    }

                    if(measureDRType != "-"){
                        selectDimQuery.push('[Item New Model].[DR Type].['+measureDRType+']');
                        createDimQuery.push('[Item New Model].[DR Type]');
                        createDimValue.push('"'+measureDRType +'"');
                    }else{
                        selectDimQuery.push('[Item New Model].[DR Type].['+dimDRType+']');
                        createDimQuery.push('[Item New Model].[DR Type]');
                        createDimValue.push('"'+dimDRType +'"');
                    }

                    if(measureInch != "-"){
                        selectDimQuery.push('[Item New Model].[Inch].['+measureInch+']');
                        createDimQuery.push('[Item New Model].[Inch]');
                        createDimValue.push('"'+measureInch +'"');
                    }else{
                        selectDimQuery.push('[Item New Model].[Inch].['+dimInch+']');
                        createDimQuery.push('[Item New Model].[Inch]');
                        createDimValue.push('"'+dimInch +'"');
                    }
    
                    if(measureGrade != "-"){
                        selectDimQuery.push('[Item New Model].[Grade].['+measureGrade+']');
                        createDimQuery.push('[Item New Model].[Grade]');
                        createDimValue.push('"'+measureGrade +'"');
                    }else{
                        selectDimQuery.push('[Item New Model].[Grade].['+dimGrade+']');
                        createDimQuery.push('[Item New Model].[Grade]');
                        createDimValue.push('"'+dimGrade +'"');
                    }
                               
                    if ( !vdCommon.existDimension(selectDimQuery) ) {
                        //1.[Item New Model] Dim Create
                        vdCommon.debug(" [Item New Model] Dim Create");        
                        vdCommon.createDimension(createDimQuery, createDimValue);
                    } 

                    vdCommon.debug("[New Model Mgmt] Data["+dimLocation+"]["+dimAP2+"]Item["+dimItem+"]["+measureItem+"]");
                    //디멘젼 처리 후에 메져 데이타 처리
                    //(1) New Model Mgmt. 
                    //2. [New Model Mgmt] Measure 체크
                    selectMeasureDimQuery = [];
                    selectMeasureQuery = [];

                    selectMeasureDimQuery.push("[Version].[Version Name].["+fbVersion+"]");
                    if(measureLocation != "-"){
                        selectMeasureDimQuery.push("[Location].[Location].["+measureLocation+"]");
                    }else{
                        selectMeasureDimQuery.push("[Location].[Location].["+dimLocation+"]");
                    }

                    if(measureAP2 != "-"){
                        selectMeasureDimQuery.push("[Sales Domain].[AP2].["+measureAP2+"]");
                    }else{
                        selectMeasureDimQuery.push("[Sales Domain].[AP2].["+dimAP2+"]");
                    }

                    selectMeasureDimQuery.push("[Item New Model].[Item].["+measureItem+"]");

                    selectMeasureQuery.push("Measure.[New Model Mgmt_AP2 Adj]");            
                    selectMeasureQuery.push("Measure.[New Model Mgmt_DR Type Adj]");
                    selectMeasureQuery.push("Measure.[New Model Mgmt_GC Adj]");
                    selectMeasureQuery.push("Measure.[New Model Mgmt_Grade Adj]");
                    selectMeasureQuery.push("Measure.[New Model Mgmt_Inch Adj]");
                    selectMeasureQuery.push("Measure.[New Model Mgmt_Item Adj]");
                    selectMeasureQuery.push("Measure.[New Model Mgmt_KD Type Adj]");
                    selectMeasureQuery.push("Measure.[New Model Mgmt_Location Adj]");
                    selectMeasureQuery.push("Measure.[New Model Mgmt_Product Adj]");
                    selectMeasureQuery.push("Measure.[New Model Mgmt_Project Adj]");
                    selectMeasureQuery.push("Measure.[New Model Mgmt_Section Adj]");
                    selectMeasureQuery.push("Measure.[New Model Mgmt_Series Adj]");
                    vdCommon.debug(" [New Model Mgmt] Data Check::" + JSON.stringify(selectMeasureQuery) ); 
                    if(!vdCommon.existMeasure(selectMeasureDimQuery, selectMeasureQuery, "")) {
                        vdCommon.debug(" [New Model Mgmt] Measure Delete(update");       
                        vdCommon.updateMeasure(["[Version].[Version Name].["+fbVersion+"]",
                                            "[Location].[Location].[" + dimLocation + "]",
                                            "[Sales Domain].[AP2].[" + dimAP2 + "]",
                                            "[Item New Model].[Item].[" + dimItem + "]"],
                                            ['Measure.[New Model Mgmt_AP2 Adj] = "-" ;',
                                            'Measure.[New Model Mgmt_DR Type Adj] = "-" ;',
                                            'Measure.[New Model Mgmt_GC Adj] = "-" ;',
                                            'Measure.[New Model Mgmt_Grade Adj] = "-" ;',
                                            'Measure.[New Model Mgmt_Inch Adj] = "-" ;',
                                            'Measure.[New Model Mgmt_Item Adj] = "-" ;',
                                            'Measure.[New Model Mgmt_KD Type Adj] = "-" ;',
                                            'Measure.[New Model Mgmt_Location Adj] = "-" ;',
                                            'Measure.[New Model Mgmt_Product Adj] = "-" ;',
                                            'Measure.[New Model Mgmt_Project Adj] = "-" ;',
                                            'Measure.[New Model Mgmt_Section Adj] = "-" ;',
                                            'Measure.[New Model Mgmt_Series Adj] = "-" ;',
                                            'Measure.[New Model Mgmt_Update Time] =dateadd(Now(),9,"hour");',
                                            'Measure.[New Model Mgmt_Updated By] = CurrentUser().[User Name] ;',
                                            'Measure.[New Model Mgmt_Valid Flag] = "DELETE";']);
                        //데이타 검증 후 삭제함.
                        /*vdCommon.deleteMeasure(["[Version].[Version Name].["+fbVersion+"]", "Location.[Location].[" + dimLocation + "]", 
                                                "[Sales Domainn].[AP2].[" + dimAP2 + "]",
                                                "[Item New Model].[Item].[" + dimItem + "]" ], "New Model Mgmt");*/
                        //Create
                        vdCommon.debug(" [New Model Mgmt] Measure Create");
                        //[New Model Mgmt] Measure Create
                        createMeasurDimeQuery = [];
                        createMeasureQuery = [];
     
                        createMeasurDimeQuery.push("[Version].[Version Name].["+fbVersion+"]");
                        createMeasurDimeQuery.push("[Location].[Location].["+dimLocation+"]");
                        createMeasurDimeQuery.push("[Sales Domain].[AP2].["+dimAP2+"]");
                        createMeasurDimeQuery.push("[Item New Model].[Item].["+measureItem+"]"); //변경된 Item으로 생성함.            
  
                        createMeasureQuery.push('Measure.[New Model Mgmt_AP2 Adj] = "-";');             
                        createMeasureQuery.push('Measure.[New Model Mgmt_DR Type Adj] = "-";'); 
                        createMeasureQuery.push('Measure.[New Model Mgmt_GC Adj] = "-";'); 
                        createMeasureQuery.push('Measure.[New Model Mgmt_Grade Adj] = "-";'); 
                        createMeasureQuery.push('Measure.[New Model Mgmt_Inch Adj] = "-";'); 
                        createMeasureQuery.push('Measure.[New Model Mgmt_Item Adj] = "-";'); 
                        createMeasureQuery.push('Measure.[New Model Mgmt_KD Type Adj] = "-";'); 
                        createMeasureQuery.push('Measure.[New Model Mgmt_Location Adj] = "-";'); 
                        createMeasureQuery.push('Measure.[New Model Mgmt_Product Adj] = "-";'); 
                        createMeasureQuery.push('Measure.[New Model Mgmt_Project Adj] = "-";'); 
                        createMeasureQuery.push('Measure.[New Model Mgmt_Section Adj] = "-";'); 
                        createMeasureQuery.push('Measure.[New Model Mgmt_Series Adj] = "-";'); 
                        createMeasureQuery.push('Measure.[New Model Mgmt_Created By] = CurrentUser().[User Name];');
                        createMeasureQuery.push('Measure.[New Model Mgmt_Creation Time] = dateadd(Now(),9,"hour");');
                        createMeasureQuery.push('Measure.[New Model Mgmt_Valid Flag] = "CREATE";');  
                        //vdCommon.debug(" [New Model Mgmt] Data Create::" + JSON.stringify(createMeasureQuery) ); 
                        vdCommon.createMeasure(createMeasurDimeQuery, createMeasureQuery) 
                    }

                    //
                    //New Model 메져 등록 여부를 체크하여. 
                    selectMeasureDimQuery = [];
                    selectMeasureQuery = [];

                    selectMeasureDimQuery.push("[Version].[Version Name].["+fbVersion+"]");
                    selectMeasureDimQuery.push("[Location].[Location].["+dimLocation+"]");
                    selectMeasureDimQuery.push("[Sales Domain].[AP2].["+dimAP2+"]");
                    selectMeasureDimQuery.push("[Item New Model].[Item].["+measureItem+"]");
                    selectMeasureDimQuery.push("[Category].[Category]");
                    
                    selectMeasureQuery.push("Measure.[New Model_Air SOP Date]");
                    selectMeasureQuery.push("Measure.[New Model_Air SOP Qty]");
                    selectMeasureQuery.push("Measure.[New Model_Air SOP To Site]");
                    selectMeasureQuery.push("Measure.[New Model_BOM HQ Status]");
                    selectMeasureQuery.push("Measure.[New Model_BOM Local Status]");
                    selectMeasureQuery.push("Measure.[New Model_Code Status]");
                    selectMeasureQuery.push("Measure.[New Model_Dash Status]");
                    selectMeasureQuery.push("Measure.[New Model_Dev DV]");
                    selectMeasureQuery.push("Measure.[New Model_Dev DVR]");
                    selectMeasureQuery.push("Measure.[New Model_Dev LMI]");
                    selectMeasureQuery.push("Measure.[New Model_Dev PIA]");
                    selectMeasureQuery.push("Measure.[New Model_Dev PR]");
                    selectMeasureQuery.push("Measure.[New Model_Dev PRA]");
                    selectMeasureQuery.push("Measure.[New Model_Dev PV]");
                    selectMeasureQuery.push("Measure.[New Model_Dev PVR]");
                    selectMeasureQuery.push("Measure.[New Model_LCM Approval]");
                    selectMeasureQuery.push("Measure.[New Model_LCM CDR2]");
                    selectMeasureQuery.push("Measure.[New Model_LCM CPA]");
                    selectMeasureQuery.push("Measure.[New Model_LCM Code]");
                    selectMeasureQuery.push("Measure.[New Model_LCM From Site]");
                    selectMeasureQuery.push("Measure.[New Model_LCM L/BOM1]");
                    selectMeasureQuery.push("Measure.[New Model_LCM MP]");
                    selectMeasureQuery.push("Measure.[New Model_LCM Model]");
                    selectMeasureQuery.push("Measure.[New Model_LCM SR]");
                    selectMeasureQuery.push("Measure.[New Model_LCM SRA]");
                    selectMeasureQuery.push("Measure.[New Model_LCM SRP-F]");
                    selectMeasureQuery.push("Measure.[New Model_LCM SRP-S]");
                    selectMeasureQuery.push("Measure.[New Model_LCM TP Mode]");
                    selectMeasureQuery.push("Measure.[New Model_LCM Vendor]");
                    selectMeasureQuery.push("Measure.[New Model_MP DP Status]");
                    selectMeasureQuery.push("Measure.[New Model_Mfg Date]");
                    selectMeasureQuery.push("Measure.[New Model_Mfg Qty]");
                    selectMeasureQuery.push("Measure.[New Model_Platform]");
                    selectMeasureQuery.push("Measure.[New Model_RTS DP Status]");
                    selectMeasureQuery.push("Measure.[New Model_RTS GI Status]");
                    selectMeasureQuery.push("Measure.[New Model_RUN/DROP]");
                    selectMeasureQuery.push("Measure.[New Model_SET Aging]");
                    selectMeasureQuery.push("Measure.[New Model_SET MP]");
                    selectMeasureQuery.push("Measure.[New Model_SET PLM SRA]");
                    selectMeasureQuery.push("Measure.[New Model_SET SOP]");
                    selectMeasureQuery.push("Measure.[New Model_SET SR]");
                    selectMeasureQuery.push("Measure.[New Model_SET SRA]");
                    selectMeasureQuery.push("Measure.[New Model_SET SRP-F]");
                    selectMeasureQuery.push("Measure.[New Model_SET SRP-S]");
                    selectMeasureQuery.push("Measure.[New Model_SOP Date]");
                    selectMeasureQuery.push("Measure.[New Model_SOP Qty]");
                    selectMeasureQuery.push("Measure.[New Model_SOP Register Date]");
                    selectMeasureQuery.push("Measure.[New Model_SOP Status]");
                    selectMeasureQuery.push("Measure.[New Model_SR Date]");
                    selectMeasureQuery.push("Measure.[New Model_SR Prod Qty]");
                    selectMeasureQuery.push("Measure.[New Model_SR Prod To Site]");
                    selectMeasureQuery.push("Measure.[New Model_SR Qty]");
                    selectMeasureQuery.push("Measure.[New Model_SR To Site]");
                    selectMeasureQuery.push("Measure.[New Model_SRP Prod LCM Qty]");
                    selectMeasureQuery.push("Measure.[New Model_SRP Prod SET Qty]");
                    selectMeasureQuery.push("Measure.[New Model_Sales LT]");
                    selectMeasureQuery.push("Measure.[New Model_Sales RDD]");
                    selectMeasureQuery.push("Measure.[New Model_Sales RTS]");
                    selectMeasureQuery.push("Measure.[New Model_Sales Reset]");
                    selectMeasureQuery.push("Measure.[New Model_Update Date]");
                    selectMeasureQuery.push("Measure.[New Model_Update Reason]");
                    selectMeasureQuery.push("Measure.[New Model_Updated By]");
                    selectMeasureQuery.push("Measure.[New Model_Year]");   
                    vdCommon.debug(" [New Model] Data Check::" + JSON.stringify(selectMeasureDimQuery) ); 
                    if(!vdCommon.existMeasure(selectMeasureDimQuery, selectMeasureQuery, "")) {

                        //New Model 기존 등록된 데이타를 조회하겨. 
                        //산규 생성 데이타 Measure 데이타로 넣는다.
                        selectDimension =[];
                        selectMeasure = [];

                        selectDimension.push("[Version].[Version Name].["+fbVersion+"]");
                        selectDimension.push("[Location].[Location].["+dimLocation+"]");
                        selectDimension.push("[Sales Domain].[AP2].["+dimAP2+"]");
                        selectDimension.push("[Item New Model].[Item].["+dimItem+"]");
                        selectDimension.push("[Category].[Category]");

                        selectMeasure = selectMeasureQuery;

                        let resultNewModel = vdCommon.selectList(selectDimension, selectMeasure, "", "","");
                        vdCommon.debug(" [New Model] Data Select::["+resultNewModel.cs.rowCount+"]" + JSON.stringify(selectDimension) ); 

                        for(var j=0; j < resultNewModel.cs.rowCount; j++){    
                            //var rows = resultNewModel.cs.row(i);    
                            //vdCommon.debug(" [New Model] Data Select row("+i+"):: "+  JSON.stringify(rows) );                     
                            //삭제처리
                            /*vdCommon.deleteMeasure(["[Version].[Version Name].["+fbVersion+"]", "Location.[Location].[" + resultNewModel.cs.row(i).cell(resultNewModel.cs.memberColumnIndex("Location", "Location")).Name + "]", 
                                                "[Sales Domainn].[AP2].[" + resultNewModel.cs.row(i).cell(resultNewModel.cs.memberColumnIndex("Sales Domain", "AP2")).Name + "]",
                                                "[Item New Model].[Item].[" + resultNewModel.cs.row(i).cell(resultNewModel.cs.memberColumnIndex("Item New Model", "Item")).Name + "]",
                                                "[Category].[Category].["+resultNewModel.cs.row(i).cell(resultNewModel.cs.memberColumnIndex("Category", "Category")).Name+"]"], "New Mode");*/
                            vdCommon.updateMeasure(["[Version].[Version Name].["+fbVersion+"]", "[Location].[Location].[" + resultNewModel.cs.row(j).cell(resultNewModel.cs.memberColumnIndex("Location", "Location")).Name + "]", 
                                                "[Sales Domain].[AP2].[" + resultNewModel.cs.row(j).cell(resultNewModel.cs.memberColumnIndex("Sales Domain", "AP2")).Name + "]",
                                                "[Item New Model].[Item].[" + resultNewModel.cs.row(j).cell(resultNewModel.cs.memberColumnIndex("Item New Model", "Item")).Name + "]",
                                                "[Category].[Category].["+resultNewModel.cs.row(j).cell(resultNewModel.cs.memberColumnIndex("Category", "Category")).Name+"]"],
                                                ['Measure.[New Model_New Valid Flag] = "DELETE";']);

                            //Create Measure
                            createMeasurDimeQuery = [];
                            createMeasureQuery = [];

                            createMeasurDimeQuery = [];
                            createMeasurDimeQuery.push('[Version].[Version Name].['+fbVersion+']');
                            createMeasurDimeQuery.push('[Location].[Location].['+resultNewModel.cs.row(j).cell(resultNewModel.cs.memberColumnIndex("Location", "Location")).Name+']');
                            createMeasurDimeQuery.push('[Sales Domain].[AP2].['+resultNewModel.cs.row(j).cell(resultNewModel.cs.memberColumnIndex("Sales Domain", "AP2")).Name+']');
                            createMeasurDimeQuery.push('[Item New Model].[Item].['+measureItem+']');
                            createMeasurDimeQuery.push('[Category].[Category].['+resultNewModel.cs.row(j).cell(resultNewModel.cs.memberColumnIndex("Category", "Category")).Name+']');

                            createMeasureQuery.push('Measure.[New Model_Air SOP Date] = '+fn_dataCheck(resultNewModel, j,"New Model_Air SOP Date","Datetime")+';');
                            createMeasureQuery.push('Measure.[New Model_Air SOP Qty] = '+fn_dataCheck(resultNewModel, j,"New Model_Air SOP Qty","Number")+';');
                            createMeasureQuery.push('Measure.[New Model_Air SOP To Site] = '+fn_dataCheck(resultNewModel, j,"New Model_Air SOP To Site","String")+';');
                            createMeasureQuery.push('Measure.[New Model_BOM HQ Status] = '+fn_dataCheck(resultNewModel, j,"New Model_BOM HQ Status","String")+';');
                            createMeasureQuery.push('Measure.[New Model_BOM Local Status] = '+fn_dataCheck(resultNewModel, j,"New Model_BOM Local Status","String")+';');
                            createMeasureQuery.push('Measure.[New Model_Code Status] = '+fn_dataCheck(resultNewModel, j,"New Model_Code Status","String")+';');
                            createMeasureQuery.push('Measure.[New Model_Dash Status] = '+fn_dataCheck(resultNewModel, j,"New Model_Dash Status","String")+';');
                            createMeasureQuery.push('Measure.[New Model_Dev DV] = '+fn_dataCheck(resultNewModel, j,"New Model_Dev DV","String")+';');
                            createMeasureQuery.push('Measure.[New Model_Dev DVR] = '+fn_dataCheck(resultNewModel, j,"New Model_Dev DVR","String")+';');
                            createMeasureQuery.push('Measure.[New Model_Dev LMI] = '+fn_dataCheck(resultNewModel, j,"New Model_Dev LMI","String")+';');
                            createMeasureQuery.push('Measure.[New Model_Dev PIA] = '+fn_dataCheck(resultNewModel, j,"New Model_Dev PIA","String")+';');
                            createMeasureQuery.push('Measure.[New Model_Dev PR] = '+fn_dataCheck(resultNewModel, j,"New Model_Dev PR","String")+';');
                            createMeasureQuery.push('Measure.[New Model_Dev PRA] = '+fn_dataCheck(resultNewModel, j,"New Model_Dev PRA","Datetime")+';');
                            createMeasureQuery.push('Measure.[New Model_Dev PV] = '+fn_dataCheck(resultNewModel, j,"New Model_Dev PV","String")+';');
                            createMeasureQuery.push('Measure.[New Model_Dev PVR] = '+fn_dataCheck(resultNewModel, j,"New Model_Dev PVR","String")+';');
                            createMeasureQuery.push('Measure.[New Model_LCM Approval] = '+fn_dataCheck(resultNewModel, j,"New Model_LCM Approval","String")+';');
                            createMeasureQuery.push('Measure.[New Model_LCM CDR2] = '+fn_dataCheck(resultNewModel, j,"New Model_LCM CDR2","String")+';');
                            createMeasureQuery.push('Measure.[New Model_LCM Code] = '+fn_dataCheck(resultNewModel, j,"New Model_LCM Code","String")+';');
                            createMeasureQuery.push('Measure.[New Model_LCM CPA] = '+fn_dataCheck(resultNewModel, j,"New Model_LCM CPA","String")+';');
                            createMeasureQuery.push('Measure.[New Model_LCM From Site] = '+fn_dataCheck(resultNewModel, j,"New Model_LCM From Site","String")+';');
                            createMeasureQuery.push('Measure.[New Model_LCM L/BOM1] = '+fn_dataCheck(resultNewModel, j,"New Model_LCM L/BOM1","String")+';');
                            createMeasureQuery.push('Measure.[New Model_LCM Model] = '+fn_dataCheck(resultNewModel, j,"New Model_LCM Model","String")+';');
                            createMeasureQuery.push('Measure.[New Model_LCM MP] = '+fn_dataCheck(resultNewModel, j,"New Model_LCM MP","String")+';');
                            createMeasureQuery.push('Measure.[New Model_LCM SR] = '+fn_dataCheck(resultNewModel, j,"New Model_LCM SR","String")+';');
                            createMeasureQuery.push('Measure.[New Model_LCM SRA] = '+fn_dataCheck(resultNewModel, j,"New Model_LCM SRA","String")+';');
                            createMeasureQuery.push('Measure.[New Model_LCM SRP-F] = '+fn_dataCheck(resultNewModel, j,"New Model_LCM SRP-F","String")+';');
                            createMeasureQuery.push('Measure.[New Model_LCM SRP-S] = '+fn_dataCheck(resultNewModel, j,"New Model_LCM SRP-S","String")+';');
                            createMeasureQuery.push('Measure.[New Model_LCM TP Mode] = '+fn_dataCheck(resultNewModel, j,"New Model_LCM TP Mode","String")+';');
                            createMeasureQuery.push('Measure.[New Model_LCM Vendor] = '+fn_dataCheck(resultNewModel, j,"New Model_LCM Vendor","String")+';');
                            createMeasureQuery.push('Measure.[New Model_Mfg Date] = '+fn_dataCheck(resultNewModel, j,"New Model_Mfg Date","Datetime")+';');
                            createMeasureQuery.push('Measure.[New Model_Mfg Qty] = '+fn_dataCheck(resultNewModel, j,"New Model_Mfg Qty","Number")+';');
                            createMeasureQuery.push('Measure.[New Model_MP DP Status] = '+fn_dataCheck(resultNewModel, j,"New Model_MP DP Status","String")+';');
                            createMeasureQuery.push('Measure.[New Model_Platform] = '+fn_dataCheck(resultNewModel, j,"New Model_Platform","String")+';');
                            createMeasureQuery.push('Measure.[New Model_RTS DP Status] = '+fn_dataCheck(resultNewModel, j,"New Model_RTS DP Status","String")+';');
                            createMeasureQuery.push('Measure.[New Model_RTS GI Status] = '+fn_dataCheck(resultNewModel, j,"New Model_RTS GI Status","String")+';');
                            createMeasureQuery.push('Measure.[New Model_RUN/DROP] = '+fn_dataCheck(resultNewModel, j,"New Model_RUN/DROP","String")+';');
                            createMeasureQuery.push('Measure.[New Model_Sales LT] = '+fn_dataCheck(resultNewModel, j,"New Model_Sales LT","String")+';');
                            createMeasureQuery.push('Measure.[New Model_Sales RDD] = '+fn_dataCheck(resultNewModel, j,"New Model_Sales RDD","String")+';');
                            createMeasureQuery.push('Measure.[New Model_Sales Reset] = '+fn_dataCheck(resultNewModel, j,"New Model_Sales Reset","String")+';');
                            createMeasureQuery.push('Measure.[New Model_Sales RTS] = '+fn_dataCheck(resultNewModel, j,"New Model_Sales RTS","Datetime")+';');
                            createMeasureQuery.push('Measure.[New Model_SET Aging] = '+fn_dataCheck(resultNewModel, j,"New Model_SET Aging","Datetime")+';');
                            createMeasureQuery.push('Measure.[New Model_SET MP] = '+fn_dataCheck(resultNewModel, j,"New Model_SET MP","Datetime")+';');
                            createMeasureQuery.push('Measure.[New Model_SET PLM SRA] = '+fn_dataCheck(resultNewModel, j,"New Model_SET PLM SRA","Datetime")+';');
                            createMeasureQuery.push('Measure.[New Model_SET SOP] = '+fn_dataCheck(resultNewModel, j,"New Model_SET SOP","Datetime")+';');
                            createMeasureQuery.push('Measure.[New Model_SET SR] = '+fn_dataCheck(resultNewModel, j,"New Model_SET SR","String")+';');
                            createMeasureQuery.push('Measure.[New Model_SET SRA] = '+fn_dataCheck(resultNewModel, j,"New Model_SET SRA","String")+';');
                            createMeasureQuery.push('Measure.[New Model_SET SRP-F] = '+fn_dataCheck(resultNewModel, j,"New Model_SET SRP-F","String")+';');
                            createMeasureQuery.push('Measure.[New Model_SET SRP-S] = '+fn_dataCheck(resultNewModel, j,"New Model_SET SRP-S","String")+';');
                            createMeasureQuery.push('Measure.[New Model_SOP Date] = '+fn_dataCheck(resultNewModel, j,"New Model_SOP Date","Datetime")+';');
                            createMeasureQuery.push('Measure.[New Model_SOP Qty] = '+fn_dataCheck(resultNewModel, j,"New Model_SOP Qty","Number")+';');
                            createMeasureQuery.push('Measure.[New Model_SOP Register Date] = '+fn_dataCheck(resultNewModel, j,"New Model_SOP Register Date","Datetime")+';');
                            createMeasureQuery.push('Measure.[New Model_SOP Status] = '+fn_dataCheck(resultNewModel, j,"New Model_SOP Status","String")+';');
                            createMeasureQuery.push('Measure.[New Model_SR Date] = '+fn_dataCheck(resultNewModel, j,"New Model_SR Date","Datetime")+';');
                            createMeasureQuery.push('Measure.[New Model_SR Prod Qty] = '+fn_dataCheck(resultNewModel, j,"New Model_SR Prod Qty","Number")+';');
                            createMeasureQuery.push('Measure.[New Model_SR Prod To Site] = '+fn_dataCheck(resultNewModel, j,"New Model_SR Prod To Site","String")+';');
                            createMeasureQuery.push('Measure.[New Model_SR Qty] = '+fn_dataCheck(resultNewModel, j,"New Model_SR Qty","Number")+';');
                            createMeasureQuery.push('Measure.[New Model_SR To Site] = '+fn_dataCheck(resultNewModel, j,"New Model_SR To Site","String")+';');
                            createMeasureQuery.push('Measure.[New Model_SRP Prod LCM Qty] = '+fn_dataCheck(resultNewModel, j,"New Model_SRP Prod LCM Qty","Number")+';');
                            createMeasureQuery.push('Measure.[New Model_SRP Prod SET Qty] = '+fn_dataCheck(resultNewModel, j,"New Model_SRP Prod SET Qty","Number")+';');
                            createMeasureQuery.push('Measure.[New Model_Update Date] = dateadd(Now(),9,"hour");')
                            createMeasureQuery.push('Measure.[New Model_Update Reason] = '+fn_dataCheck(resultNewModel, j,"New Model_Update Reason","String")+';');
                            createMeasureQuery.push('Measure.[New Model_Updated By] = CurrentUser().[User Name]	;')
                            createMeasureQuery.push('Measure.[New Model_Year] = '+fn_dataCheck(resultNewModel, j,"New Model_Year","String")+';');
                            createMeasureQuery.push('Measure.[New Model_New Valid Flag] = "CREATE";');

                            
                            //vdCommon.debug(" [New Model] Data Create::" + JSON.stringify(createMeasureQuery) ); 
                            vdCommon.createMeasure(createMeasurDimeQuery, createMeasureQuery) ;
                        }
                    }
                }else{
                    //같은 경우 update만 처리함.   
                    //(1) 디멘젼: Item New Model 데이타 업데이트                    
                    createDimQuery = [];
                    createDimValue = [];
                    //         createDimValue.push('"'+"-" +'"');      

                    if(measureSection != "-"){
                        createDimQuery.push('[Item New Model].[Section]');
                        createDimValue.push('"'+ measureSection +'"'); 
                    }else{
                        createDimQuery.push('[Item New Model].[Section]');
                        createDimValue.push('"'+dimSection +'"');
                    }


                    if(measureKDType != "-"){
                        createDimQuery.push('[Item New Model].[KD Type]');
                        createDimValue.push('"'+ measureKDType +'"'); 
                    }else{
                        createDimQuery.push('[Item New Model].[KD Type]');
                        createDimValue.push('"'+dimKDType +'"');                       

                    }

                    if(measureProduct != "-"){
                        createDimQuery.push('[Item New Model].[Product]');
                        createDimValue.push('"'+ measureProduct +'"');
                    }else{
                        createDimQuery.push('[Item New Model].[Product]');
                        createDimValue.push('"'+dimProduct +'"');
                    }

                    if(measureProject != "-"){
                        createDimQuery.push('[Item New Model].[Project]');
                        createDimValue.push('"'+ measureProject +'"');
                    }else{
                        createDimQuery.push('[Item New Model].[Project]');
                        createDimValue.push('"'+dimProject +'"');
                    }
                    
                    if(measureSeries != "-"){
                        createDimQuery.push('[Item New Model].[Series]');
                        createDimValue.push('"'+ measureSeries +'"');
                    }else{
                        createDimQuery.push('[Item New Model].[Series]');
                        createDimValue.push('"'+dimSeries +'"');
                    }

                    if(measureDRType != "-"){
                        createDimQuery.push('[Item New Model].[DR Type]');
                        createDimValue.push('"'+ measureDRType +'"');
                    }else{
                        createDimQuery.push('[Item New Model].[DR Type]');
                        createDimValue.push('"'+dimDRType +'"');
                    }

                    if(measureInch != "-"){
                        createDimQuery.push('[Item New Model].[Inch]');
                        createDimValue.push('"'+ measureInch +'"');
                    }else{
                        createDimQuery.push('[Item New Model].[Inch]');
                        createDimValue.push('"'+dimInch +'"');
                    }
                    
                    if(measureGrade != "-"){
                        createDimQuery.push('[Item New Model].[Grade]');
                        createDimValue.push('"'+ measureGrade +'"');
                    }else{
                        createDimQuery.push('[Item New Model].[Grade]');
                        createDimValue.push('"'+dimGrade +'"'); 
                    }               
                    
                    createDimQuery.push('[Item New Model].[Item]');
                    createDimValue.push('"'+ dimItem +'"');
                    createDimQuery.push('[Item New Model].[Marketing Name]');                    
                    createDimValue.push('"'+dimMarketingName +'"'); 
    
                    vdCommon.createDimension(createDimQuery, createDimValue); //테스트 필요함.

                    vdCommon.debug("New Model Mgmt Update...")
                    
                    //(2) 메저 : New Model Mgmt 데이타 업데이트 => update Date, update User, 데이타(하이픈) 초기화
                    measureDimQuery = [];
                    measureQuery = [];

                    measureDimQuery.push("[Version].[Version Name].["+fbVersion+"]");
                    //measureDimQuery.push("[Location].[Location].["+dimLocation+"]");
                    //measureDimQuery.push("[Sales Domain].[AP2].["+dimAP2+"]");
                    if(measureLocation != "-"){
                        measureDimQuery.push("[Location].[Location].["+measureLocation+"]");
                    }else{
                        measureDimQuery.push("[Location].[Location].["+dimLocation+"]");
                    }

                    if(measureAP2 != "-"){
                        measureDimQuery.push("[Sales Domain].[AP2].["+measureAP2+"]");
                    }else{
                        measureDimQuery.push("[Sales Domain].[AP2].["+dimAP2+"]");
                    }                       
                    measureDimQuery.push("[Item New Model].[Item].["+dimItem+"]");                 

                    measureQuery.push('Measure.[New Model Mgmt_AP2 Adj] = "-";');             
                    measureQuery.push('Measure.[New Model Mgmt_DR Type Adj] = "-";'); 
                    measureQuery.push('Measure.[New Model Mgmt_GC Adj] = "-";'); 
                    measureQuery.push('Measure.[New Model Mgmt_Grade Adj] = "-";'); 
                    measureQuery.push('Measure.[New Model Mgmt_Inch Adj] = "-";'); 
                    measureQuery.push('Measure.[New Model Mgmt_Item Adj] = "-";'); 
                    measureQuery.push('Measure.[New Model Mgmt_KD Type Adj] = "-";'); 
                    measureQuery.push('Measure.[New Model Mgmt_Location Adj] = "-";'); 
                    measureQuery.push('Measure.[New Model Mgmt_Product Adj] = "-";'); 
                    measureQuery.push('Measure.[New Model Mgmt_Project Adj] = "-";'); 
                    measureQuery.push('Measure.[New Model Mgmt_Section Adj] = "-";'); 
                    measureQuery.push('Measure.[New Model Mgmt_Series Adj] = "-";'); 

                    let selectMeasure = [];
                    selectMeasure.push('Measure.[New Model Mgmt_AP2 Adj]');
                    selectMeasure.push('Measure.[New Model Mgmt_DR Type Adj]'); 
                    selectMeasure.push('Measure.[New Model Mgmt_GC Adj]'); 
                    selectMeasure.push('Measure.[New Model Mgmt_Grade Adj]'); 
                    selectMeasure.push('Measure.[New Model Mgmt_Inch Adj]'); 
                    selectMeasure.push('Measure.[New Model Mgmt_Item Adj]'); 
                    selectMeasure.push('Measure.[New Model Mgmt_KD Type Adj]'); 
                    selectMeasure.push('Measure.[New Model Mgmt_Location Adj]'); 
                    selectMeasure.push('Measure.[New Model Mgmt_Product Adj]'); 
                    selectMeasure.push('Measure.[New Model Mgmt_Project Adj]'); 
                    selectMeasure.push('Measure.[New Model Mgmt_Section Adj]'); 
                    selectMeasure.push('Measure.[New Model Mgmt_Series Adj]'); 

                    let whereQuery = 'Where { Measure.[New Model Mgmt_AP2 Adj] == "-"';
                    whereQuery += ',Measure.[New Model Mgmt_DR Type Adj] == "-"';
                    whereQuery += ',Measure.[New Model Mgmt_GC Adj] == "-"';
                    whereQuery += ',Measure.[New Model Mgmt_Grade Adj] == "-"';
                    whereQuery += ',Measure.[New Model Mgmt_Inch Adj] == "-"';
                    whereQuery += ',Measure.[New Model Mgmt_Item Adj] == "-"';
                    whereQuery += ',Measure.[New Model Mgmt_KD Type Adj] == "-"';
                    whereQuery += ',Measure.[New Model Mgmt_Location Adj] == "-"';
                    whereQuery += ',Measure.[New Model Mgmt_Product Adj] == "-"';
                    whereQuery += ',Measure.[New Model Mgmt_Project Adj] == "-"';
                    whereQuery += ',Measure.[New Model Mgmt_Section Adj] == "-"';
                    whereQuery += ',Measure.[New Model Mgmt_Series Adj] == "-" }'; 
                    
                    vdCommon.debug("New Model Mgmt Update(Log)..." + JSON.stringify(measureQuery));

                    if(vdCommon.existMeasure(measureDimQuery, selectMeasure, whereQuery)){
                        measureQuery.push('Measure.[New Model Mgmt_Updated By] = CurrentUser().[User Name];');
                        measureQuery.push('Measure.[New Model Mgmt_Update Time] = dateadd(Now(),9,"hour");');
                        measureQuery.push('Measure.[New Model Mgmt_Valid Flag] = "UPDATE Finish";');  
                        vdCommon.debug("New Model Mgmt Update(Log)[updateMeasure]..." + JSON.stringify(measureQuery));                        
                        vdCommon.updateMeasure(measureDimQuery, measureQuery);
                    }else{
                        //New Model Mgmt Create
                        measureQuery.push('Measure.[New Model Mgmt_Created By] = CurrentUser().[User Name];');
                        measureQuery.push('Measure.[New Model Mgmt_Creation Time] =dateadd(Now(),9,"hour");');
                        measureQuery.push('Measure.[New Model Mgmt_Valid Flag] = "CREATE";');  
                        vdCommon.debug("New Model Mgmt Update(Log)[createMeasure]..." + JSON.stringify(measureQuery));  
                        //vdCommon.createMeasure(measureDimQuery, measureQuery) ;

                        //New Model Create
                        let categoryData= [];
                        categoryData.push("Plan");
                        categoryData.push("Actual");
                        measureDimQuery.push('[Category].[Category].filter(#.Name in {"'+categoryData[0]+'","'+categoryData[1]+'"})');
                    
                        vdCommon.debug("New Model Mgmt Update(Log)[New Model Create]..." + JSON.stringify(measureDimQuery));  
                    //createMeasureQuery.push('Measure.[New Model_New Valid Flag] = "CREATE";');
                        //vdCommon.createMeasure(createMeasurDimeQuery, createMeasureQuery) ;                        
                        vdCommon.createMeasure(measureDimQuery, measureQuery) ;                       
                    }                   

                }
            }

            vdCommon.programEnd();
        } catch ( e ) {
            RuleOutputToUI = { Status : 'Error', Message : "Js Logic Error : " + e.message };
            return;
        }
    }

    

    return{
        fn_sectionComobo:fn_sectionComobo,
        fn_kdTypeComobo:fn_kdTypeComobo,
        fn_projectComobo:fn_projectComobo,
        fn_seriesComobo:fn_seriesComobo,
        fn_drTypeComobo:fn_drTypeComobo,
        fn_inchComobo:fn_inchComobo,
        fn_locationComobo,fn_locationComobo,
        fn_ap2Comobo:fn_ap2Comobo,
        fn_gradeComobo:fn_gradeComobo,
        fn_productComobo:fn_productComobo,
        fn_add:fn_add,
        fn_apply:fn_apply
    };		
});