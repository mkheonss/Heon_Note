define('o9.NSCM.JSPLCMgmt', ['o9/data/query', 'o9/data/cellset', 'o9.NSCM.commonLib'], function(){	
	const programName = "o9.NSCM.JSPLCMgmt";

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

    /*whereQuery 
    * @param {array} whereQuery - Where Query
    * @param {array} orderbyQuery - OrderBy Query    
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
                //rtnWhereQuery += " limit 2000;";
                rtnWhereQuery += ";";
            }else{
                //rtnWhereQuery +=" orderby "+orderbyQuery.join(',')+" limit 2000 ;"
                rtnWhereQuery +=" orderby "+orderbyQuery.join(',')+" ;";
            }

            //vdCommon.printStep("[fn_ibplWhereQuery]" + rtnWhereQuery);
            return rtnWhereQuery;
        }catch ( e ) {
            RuleOutputToUI = { Status : 'Error', Message : "Js Logic Error : " + e.message };
            return;
        }
    }   
   
    function fn_itemCheck(o9Params){
        try{
            const commonLib = require('o9.NSCM.commonLib');
            const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
            vdCommon.setLogLevel("Debug");
            
            // 파라메타 가져오기
            vdCommon.printParams(o9Params);
            let parsedParams = JSON.parse(o9Params); 
            let fbVersion = parsedParams.fbVersion;
            let location = parsedParams.fbLocation;
            let item = parsedParams.fbItem;

            let selectQuery = 'Select ([Version].[Version Name].['+fbVersion+'] * ';
            selectQuery += '[Item].[Item].filter(#.Name in {"'+item+'"}) ' ;  
            selectQuery += ') on row,' ; 
            selectQuery += '({Measure.[PLC Mfg_PLC Status], Measure.[Item Site Asn_Cur Status]' ;
            //selectQuery += 'Measure.[PLC Mfg_BOM Date], Measure.[PLC Mfg_BOM Status], Measure.[PLC Mfg_Before EOP], Measure.[PLC Mfg_CTN End Date], Measure.[PLC Mfg_CurrentDate], ';
            //selectQuery += 'Measure.[PLC Mfg_Deleted Item], Measure.[PLC Mfg_Dev SRA Actual Date], Measure.[PLC Mfg_Dev SRA Chg Date], Measure.[PLC Mfg_Dev SRA Init Date], Measure.[PLC Mfg_Dev SRA Plan Date], ';
            //selectQuery += 'Measure.[PLC Mfg_EOP Chg Date], Measure.[PLC Mfg_EOP Com Date], Measure.[PLC Mfg_EOP Cur Date], Measure.[PLC Mfg_EOP FW Limit Date], Measure.[PLC Mfg_EOP Init Date], ';
            //selectQuery += 'Measure.[PLC Mfg_EOP Update Time], Measure.[PLC Mfg_EOP Updated By], Measure.[PLC Mfg_NPR Date], Measure.[PLC Mfg_PLC Status], Measure.[PLC Mfg_SRA Actual Date], ';
            //selectQuery += 'Measure.[PLC Mfg_SRA Chg Date], Measure.[PLC Mfg_SRA Com Date], Measure.[PLC Mfg_SRA Com Override Date], Measure.[PLC Mfg_SRA Dev Date], Measure.[PLC Mfg_SRA FW Limit Date], ';
            //selectQuery += 'Measure.[PLC Mfg_SRA IniCom Date], Measure.[PLC Mfg_SRA Init Date], Measure.[PLC Mfg_SRA Status], Measure.[PLC Mfg_SRA Update Time], Measure.[PLC Mfg_SRA Updated By], ';
            //selectQuery += 'Measure.[PLC Mfg_Short Req Date] ' ;
            selectQuery += '}) on column ' ;
            let whereQuery = [];
            let orderByQuery = [];

            //[Location].[Location]
            whereQuery.push('[Location].[Location].filter(#.Name in {'+fn_multiCheckName(location, "[Location].[Location]")+'})');
            whereQuery.push('Measure.[Item Site Asn_Cur Status] == "DELETED"');

            orderByQuery.push('[Item].[Item].DisplayName');

            selectQuery += fn_ibplWhereQuery(whereQuery, orderByQuery);

            let selectResult = vdCommon.selectQueryList("[fn_itemCombo]" ,selectQuery );            
            //let comboList = vdCommon.fn_makeCombo(selectResult, {DimName : "Item", DimAttbName : "Item", existAll : false, Sort : "DisplayName", isDisplayNameWithCode : false});
            vdCommon.programEnd();
    
            return selectResult;
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
            let selectQuery = 'Select ([Location].[Location]) Where {[Location].[Location Type].filter(#.Name in {"MF"})} orderby [Location].[Location].DisplayName; ' ;

            let selectResult = vdCommon.selectQueryList("[fn_locationCombo]" ,selectQuery );            
            let comboList = vdCommon.fn_makeCombo(selectResult, {DimName : "Location", DimAttbName : "Location", existAll : false, Sort : "DisplayName", isDisplayNameWithCode : true});
''
            vdCommon.programEnd();

            return comboList;
        } catch ( e ) {
            RuleOutputToUI = { Status : 'Error', Message : "Js Logic Error : " + e.message };
            return;
        }       
    }  

    function fn_dataCheck(o9Params, itemData, locationData){
        try{
            const commonLib = require('o9.NSCM.commonLib');
            const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
            vdCommon.setLogLevel("Debug");
            
            // 파라메타 가져오기
            vdCommon.printParams(o9Params);
            let parsedParams = JSON.parse(o9Params); 
            let fbVersion = parsedParams.fbVersion;     

            let selectQuery = 'Select ([Version].[Version Name].['+fbVersion+'] * ';
            selectQuery += '[Item].[Item].['+itemData+'] ' ;
            selectQuery += ') on row,' ; 
            selectQuery += '({ ' ;
            selectQuery += 'Measure.[PLC Mfg_BOM Date], Measure.[PLC Mfg_BOM Status], Measure.[PLC Mfg_Before EOP], Measure.[PLC Mfg_CTN End Date], Measure.[PLC Mfg_CurrentDate], ';
            selectQuery += 'Measure.[PLC Mfg_Deleted Item], Measure.[PLC Mfg_Dev SRA Actual Date], Measure.[PLC Mfg_Dev SRA Chg Date], Measure.[PLC Mfg_Dev SRA Init Date], Measure.[PLC Mfg_Dev SRA Plan Date], ';
            selectQuery += 'Measure.[PLC Mfg_EOP Chg Date], Measure.[PLC Mfg_EOP Com Date], Measure.[PLC Mfg_EOP Cur Date], Measure.[PLC Mfg_EOP FW Limit Date], Measure.[PLC Mfg_EOP Init Date], ';
            selectQuery += 'Measure.[PLC Mfg_EOP Update Time], Measure.[PLC Mfg_EOP Updated By], Measure.[PLC Mfg_NPR Date], Measure.[PLC Mfg_PLC Status], Measure.[PLC Mfg_SRA Actual Date], ';
            selectQuery += 'Measure.[PLC Mfg_SRA Chg Date], Measure.[PLC Mfg_SRA Com Date], Measure.[PLC Mfg_SRA Com Override Date], Measure.[PLC Mfg_SRA Dev Date], Measure.[PLC Mfg_SRA FW Limit Date], ';
            selectQuery += 'Measure.[PLC Mfg_SRA IniCom Date], Measure.[PLC Mfg_SRA Init Date], Measure.[PLC Mfg_SRA Status], Measure.[PLC Mfg_SRA Update Time], Measure.[PLC Mfg_SRA Updated By], ';
            selectQuery += 'Measure.[PLC Mfg_Short Req Date]}) on column ' ;
            let whereQuery = [];
            let orderByQuery = [];

            whereQuery.push('[Location].[Location].filter(#.Name in {'+fn_multiCheckName(locationData, "[Location].[Location]")+'})');
            whereQuery.push('Measure.[Item Site Asn_Cur Status] == "DELETED"');
          

            orderByQuery.push('[Item].[Item].DisplayName');

            selectQuery += fn_ibplWhereQuery(whereQuery, orderByQuery);

            let selectResult = vdCommon.selectQueryList("[fn_itemCombo]" ,selectQuery ); 

            if(selectResult.cs.rowCount <= 0){
                rtnValue = 1;
                RuleOutputToUI = { Status : 'Error', Message : "You cannot select multiple rows." };                
                vdCommon.programEnd();        
                return rtnValue;                
            }else{
                let comboList = vdCommon.fn_makeCombo(selectResult, {DimName : "Item", DimAttbName : "Item", existAll : false, Sort : "DisplayName", isDisplayNameWithCode : false});
                vdCommon.programEnd();        
                return comboList;
            }

        }catch ( e ) {
            RuleOutputToUI = { Status : 'Error', Message : "Js Logic Error : " + e.message };
            return;
        }
    }

    function fn_invokeDelete(o9Params){
        try{
            const commonLib = require('o9.NSCM.commonLib');
            const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
            vdCommon.setLogLevel("Debug");
            vdCommon.printParams(o9Params);

            // 파라메타 가져오기
            let parsedParams = JSON.parse(o9Params); 
            let fbVersion = parsedParams.fbVersion;
            let fbitem = parsedParams.fbItem;
            let fbLocation = parsedParams.fbLocation;
            let sraChgDate =  parsedParams.fbSraChgDate;

            let dimension = [];
            let measure = []; 
            let dimensionItem = [];
            let measureItem = [];

            let resultCheck = fn_itemCheck(o9Params);
            vdCommon.printStep("[fn_itemCheck]" + resultCheck.cs.rowCount);

            if(resultCheck.cs.rowCount <= 0){
                vdCommon.printStep("Message Output");
                rtnValue = 1;
                RuleOutputToUI = { Status : 'Error', Message : "This data cannot be processed." };
            }else{

    
                dimension.push("[Version].[Version Name].["+fbVersion+"]");
                dimension.push("[Item].[Item].["+fbitem+"]");
                dimension.push("[Location].[Location].["+fbLocation+"]");
    
                measure.push('Measure.[PLC Mfg_SRA Chg Date] = if(Measure.[PLC Mfg_PLC Status] == "DELETED") then ToDateTime("'+sraChgDate+'") else Measure.[PLC Mfg_SRA Chg Date];');
                measure.push('Measure.[PLC Mfg_EOP Chg Date] = if(Measure.[PLC Mfg_PLC Status] == "DELETED") then DateAdd(ToDateTime("'+sraChgDate+'"), 365, [day]) else Measure.[PLC Mfg_EOP Chg Date];');
                                
                vdCommon.updateMeasure(dimension, measure);   
                
                dimensionItem.push("[Version].[Version Name].["+fbVersion+"]");
                dimensionItem.push("[Item].[Item].["+fbitem+"]");
                dimensionItem.push("[Location].[Location].["+fbLocation+"]");
    
                measureItem.push('Measure.[Item Site Asn_Cur Status] = if(Measure.[Item Site Asn_Cur Status] == "DELETED") then "ACTIVE" else Measure.[Item Site Asn_Cur Status];');
                measureItem.push('Measure.[Item Site Asn_Cur Status_PL] = if(Measure.[Item Site Asn_Cur Status_PL] == "Deleted") then "Active" else Measure.[Item Site Asn_Cur Status_PL];');
                vdCommon.updateMeasure(dimensionItem, measureItem);                    
            }
	
            vdCommon.programEnd(); 
        }catch ( e ) {
            RuleOutputToUI = { Status : 'Error', Message : "Js Logic Error : " + e.message };
            return;
        }
    }

    return{
        fn_locationCombo : fn_locationCombo,
        fn_invokeDelete : fn_invokeDelete
    };		
});