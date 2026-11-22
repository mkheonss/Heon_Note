define('o9.NSCM.JSOnHandMtrl', ['o9/data/query', 'o9/data/cellset', 'o9.NSCM.commonLib'], function () {
	const programName = "o9.NSCM.JSOnHandMtrl";

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

    var fn_dataCheck = function(o9Params){
        try{
            const commonLib = require('o9.NSCM.commonLib');
            const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
            vdCommon.setLogLevel("Debug");            
            
            // 파라메타 가져오기
            vdCommon.printParams(o9Params);
            let parsedParams = JSON.parse(o9Params);    
            let chkLocation = parsedParams.chkLocation;
            let chkItemMaterial = parsedParams.chkItemMaterial;
            let chkSubLocation = parsedParams.chkSubLocation;
            let chkStorageLoc =  parsedParams.chkStorageLoc;
            let rtnValue = 0;
            vdCommon.debug("["+chkLocation.length+"]["+chkItemMaterial.length+"]["+chkSubLocation.length+"]["+chkStorageLoc.length+"]");

            if(chkLocation.length > 1 || chkItemMaterial.length > 1 || chkSubLocation.length > 1 ){
                rtnValue = 1;
                RuleOutputToUI = { Status : 'Error', Message : "You cannot select multiple rows." };  
            }
    
            vdCommon.printStep(">>>>>>>>>>>  fn_dataCheck End");        
            vdCommon.programEnd();
    
            return rtnValue;            

        }catch ( e ) {
            RuleOutputToUI = { Status : 'Error', Message : "Js Logic Error : " + e.message };
            return;
        }
    }

    var fn_fromStorageLocCombo = function(o9Params){        
        try{
            const commonLib = require('o9.NSCM.commonLib');
            const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);            
            vdCommon.setLogLevel("Debug");

            vdCommon.printParams(o9Params);
            // 파라미터 가져오기
            let parsedParams = JSON.parse(o9Params);
            let fbVersion = parsedParams.fbVersion;
            let fbTimeDay = parsedParams.fbTimeDay;
            let fbLocation = parsedParams.fbLocation;
            let fbItemMaterial = parsedParams.fbItemMaterial;
            let fbSubLocation = parsedParams.fbSubLocation;

            let whereQuery = "Where{";
            whereQuery += "[Version].[Version Name].["+fbVersion+"],";
            whereQuery += "[Time].[Day].["+fbTimeDay+"],";
            whereQuery += "[Location].[Location].["+fbLocation+"],";
            whereQuery += "[Item Material].[Item Material].["+fbItemMaterial+"],";
            whereQuery += "[Sub Location].[Sub Location].["+fbSubLocation+"]";
            whereQuery += "}";


            let result = vdCommon.selectList(['[Storage Loc].[Storage Loc].filter(~(#.Name in {"All"}))'],
                                                ['Measure.[Onhand Mtrl_Avail TTL]',
                                                'Measure.[Onhand Mtrl_Unrestricted]',
                                                'Measure.[Onhand Mtrl_HALB]',
                                                'Measure.[Onhand Mtrl_Inspection]',
                                                'Measure.[Onhand Mtrl_Vendor Stock]',
                                                'Measure.[Onhand Mtrl_CMI]',
                                                //UnAvailable Qty
                                                'Measure.[Onhand Mtrl_Unavail TTL]',
                                                'Measure.[Onhand Mtrl_Block]',
                                                'Measure.[Onhand Mtrl_Return]',
                                                'Measure.[Onhand Mtrl_SVC]',
                                                'Measure.[Onhand Mtrl_Unavail Storage]'], 
                                                whereQuery, 
                                                "","");
            let comboList = vdCommon.fn_makeCombo(result, {DimName : "Storage Loc", DimAttbName : "Storage Loc", existAll : false, Sort : "DisplayName", isDisplayNameWithCode : false});            
            
            if(result.cs.rowCount > comboList.length ){
                comboList.push({ Name : "-", DisplayName : "-"});
            }

            vdCommon.programEnd();
            return comboList;

        }catch ( e ) {
            RuleOutputToUI = { Status : 'Error', Message : "Js Logic Error : " + e.message };
            return;
        }
    }

    var fn_toStorageLocCombo = function(o9Params){        
        try{
            const commonLib = require('o9.NSCM.commonLib');
            const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);            
            vdCommon.setLogLevel("Debug");

            vdCommon.printParams(o9Params);
            // 파라미터 가져오기
            let parsedParams = JSON.parse(o9Params);
            let fbVersion = parsedParams.fbVersion;
            let fbTimeDay = parsedParams.fbTimeDay;
            let fbLocation = parsedParams.fbLocation;
            let fbItemMaterial = parsedParams.fbItemMaterial;
            let fbSubLocation = parsedParams.fbSubLocation;
            let fbFromStorageLoc = parsedParams.fbFromStorageLoc;

            let whereQuery = "Where{";
            whereQuery += "[Version].[Version Name].["+fbVersion+"],";
            whereQuery += "[Time].[Day].["+fbTimeDay+"],";
            whereQuery += "[Location].[Location].["+fbLocation+"],";
            whereQuery += "[Item Material].[Item Material].["+fbItemMaterial+"],";
            whereQuery += "[Sub Location].[Sub Location].["+fbSubLocation+"]";
            whereQuery += "}";


            let result = vdCommon.selectList(['[Storage Loc].[Storage Loc].filter(~(#.Name in {"All", '+fn_multiCheckName(fbFromStorageLoc, "[Storage Loc].[Storage Loc]")+'}))'],
                                                ['Measure.[Onhand Mtrl_Avail TTL]',
                                                'Measure.[Onhand Mtrl_Unrestricted]',
                                                'Measure.[Onhand Mtrl_HALB]',
                                                'Measure.[Onhand Mtrl_Inspection]',
                                                'Measure.[Onhand Mtrl_Vendor Stock]',
                                                'Measure.[Onhand Mtrl_CMI]',
                                                //UnAvailable Qty
                                                'Measure.[Onhand Mtrl_Unavail TTL]',
                                                'Measure.[Onhand Mtrl_Block]',
                                                'Measure.[Onhand Mtrl_Return]',
                                                'Measure.[Onhand Mtrl_SVC]',
                                                'Measure.[Onhand Mtrl_Unavail Storage]'], 
                                                whereQuery, 
                                                "","");
            let comboList = vdCommon.fn_makeCombo(result, {DimName : "Storage Loc", DimAttbName : "Storage Loc", existAll : false, Sort : "DisplayName", isDisplayNameWithCode : false});            
            
            if(result.cs.rowCount > comboList.length ){
                comboList.push({ Name : "-", DisplayName : "-"});
            }            

            vdCommon.programEnd();
            return comboList;

        }catch ( e ) {
            RuleOutputToUI = { Status : 'Error', Message : "Js Logic Error : " + e.message };
            return;
        }
    } 

    //fromStorage Locateion Inventory 수량을 조회함.

    function fn_inventoryQty(o9Params, val){
        try{
            const commonLib = require('o9.NSCM.commonLib');
            const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);            
            vdCommon.setLogLevel("Debug");

            vdCommon.printParams(o9Params);
            // 파라미터 가져오기
            let parsedParams = JSON.parse(o9Params);
            let fbVersion = parsedParams.fbVersion;
            let fbTimeDay = parsedParams.fbTimeDay;
            let fbLocation = parsedParams.fbLocation;
            let fbItemMaterial = parsedParams.fbItemMaterial;
            let fbSubLocation = parsedParams.fbSubLocation;

            let whereQuery = "Where{";
            whereQuery += "[Version].[Version Name].["+fbVersion+"],";
            whereQuery += "[Time].[Day].["+fbTimeDay+"],";
            whereQuery += "[Location].[Location].["+fbLocation+"],";
            whereQuery += "[Item Material].[Item Material].["+fbItemMaterial+"],";
            whereQuery += "[Sub Location].[Sub Location].["+fbSubLocation+"]";
            whereQuery += "}";

            var result = vdCommon.selectList(['[Storage Loc].[Storage Loc].filter(#.Name in {'+fn_multiCheckName(val, "[Storage Loc].[Storage Loc]")+'})'],
                                                ['Measure.[Onhand Mtrl_Avail TTL]',
                                                'Measure.[Onhand Mtrl_Unrestricted]',
                                                'Measure.[Onhand Mtrl_HALB]',
                                                'Measure.[Onhand Mtrl_Inspection]',
                                                'Measure.[Onhand Mtrl_Vendor Stock]',
                                                'Measure.[Onhand Mtrl_CMI]',
                                                //UnAvailable Qty
                                                'Measure.[Onhand Mtrl_Unavail TTL]',
                                                'Measure.[Onhand Mtrl_Block]',
                                                'Measure.[Onhand Mtrl_Return]',
                                                'Measure.[Onhand Mtrl_SVC]',
                                                'Measure.[Onhand Mtrl_Unavail Storage]'], 
                                                whereQuery, 
                                                "","");

            let availQty = 0;
            let unavailQty = 0;
            let comboList = [];
            for(var k = 0; k < result.cs.rowCount; k++){
                availQty += result.cs.row(k).cell(result.cs.measureColumnIndex("Onhand Mtrl_Avail TTL"));
                unavailQty += result.cs.row(k).cell(result.cs.measureColumnIndex("Onhand Mtrl_Unavail TTL"));
            }
            let displayData = "Avail Qty=["+availQty+"], Unavail Qty=["+unavailQty+"]";
            vdCommon.printStep("[Data]"+ displayData);
            comboList.push({ Name: displayData, DisplayName: displayData });
            vdCommon.programEnd();            
            return comboList;
            
        }catch ( e ) {
            RuleOutputToUI = { Status : 'Error', Message : "Js Logic Error : " + e.message };
            return;
        }
    }

    var fn_fromStorageQty = function(o9Params){
        try{
            const commonLib = require('o9.NSCM.commonLib');
            const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);            
            vdCommon.setLogLevel("Debug");

            vdCommon.printParams(o9Params);
            // 파라미터 가져오기
            let parsedParams = JSON.parse(o9Params);
            let fbFromStorageLoc = parsedParams.fbFromStorageLoc;
            vdCommon.printStep("[From Storage]"+ fbFromStorageLoc);
            let comboList = fn_inventoryQty(o9Params, fbFromStorageLoc);

            vdCommon.programEnd();            
            return comboList;

        }catch ( e ) {
            RuleOutputToUI = { Status : 'Error', Message : "Js Logic Error : " + e.message };
            return;
        }
    }
    
    var fn_toStorageQty = function(o9Params){
        try{
            const commonLib = require('o9.NSCM.commonLib');
            const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);            
            vdCommon.setLogLevel("Debug");
            
            vdCommon.printParams(o9Params);
            // 파라미터 가져오기
            let parsedParams = JSON.parse(o9Params);
            let fbToStorageLoc = parsedParams.fbToStorageLoc;
            vdCommon.printStep("[To Storage]"+ fbToStorageLoc);
            let comboList = fn_inventoryQty(o9Params, fbToStorageLoc);

            vdCommon.programEnd();            
            return comboList;

        }catch ( e ) {
            RuleOutputToUI = { Status : 'Error', Message : "Js Logic Error : " + e.message };
            return;
        }
    }     
    
    var fn_transferStorage = function(o9Params){
        try{
            const commonLib = require('o9.NSCM.commonLib');
            const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);            
            vdCommon.setLogLevel("Debug");

            vdCommon.printParams(o9Params);
            // 파라미터 가져오기
            var parsedParams = JSON.parse(o9Params);
            var fbVersion = parsedParams.fbVersion;
            var fbTimeDay = parsedParams.fbTimeDay;
            var fbLocation = parsedParams.fbLocation;
            var fbItemMaterial = parsedParams.fbItemMaterial;
            var fbSubLocation = parsedParams.fbSubLocation;
            var fbFromStorageLoc = parsedParams.fbFromStorageLoc;
            var fbToStorageLoc = parsedParams.fbToStorageLoc;

            let whereQuery = "Where{";
            whereQuery += "[Version].[Version Name].["+fbVersion+"],";
            whereQuery += "[Time].[Day].["+fbTimeDay+"],";
            whereQuery += "[Location].[Location].["+fbLocation+"],";
            whereQuery += "[Item Material].[Item Material].["+fbItemMaterial+"],";
            whereQuery += "[Sub Location].[Sub Location].["+fbSubLocation+"]";
            whereQuery += "}";

            var result = vdCommon.selectList(['[Storage Loc].[Storage Loc].filter(#.Name in {'+fn_multiCheckName(fbFromStorageLoc, "[Storage Loc].[Storage Loc]")+'})'],
                                                ['Measure.[Onhand Mtrl_Avail TTL]',
                                                'Measure.[Onhand Mtrl_Unrestricted]',
                                                'Measure.[Onhand Mtrl_HALB]',
                                                'Measure.[Onhand Mtrl_Inspection]',
                                                'Measure.[Onhand Mtrl_Vendor Stock]',
                                                'Measure.[Onhand Mtrl_CMI]',
                                                //UnAvailable Qty
                                                'Measure.[Onhand Mtrl_Unavail TTL]',
                                                'Measure.[Onhand Mtrl_Block]',
                                                'Measure.[Onhand Mtrl_Return]',
                                                'Measure.[Onhand Mtrl_SVC]',
                                                'Measure.[Onhand Mtrl_Unavail Storage]'], 
                                                whereQuery, 
                                                "","");
            let strToUpdateQuery = "";
            let strFromUpdateQuery = "";
            for(var k = 0; k < result.cs.rowCount; k++){
                let fromStorageLoc = result.cs.row(k).cell(result.cs.memberColumnIndex("Storage Loc", "Storage Loc")).Name;
                let availTTLQty = result.cs.row(k).cell(result.cs.measureColumnIndex("Onhand Mtrl_Avail TTL"));
                let unRestrictedQty = result.cs.row(k).cell(result.cs.measureColumnIndex("Onhand Mtrl_Unrestricted"));
                let halbQty = result.cs.row(k).cell(result.cs.measureColumnIndex("Onhand Mtrl_HALB"));
                let inspectionQty = result.cs.row(k).cell(result.cs.measureColumnIndex("Onhand Mtrl_Inspection"));
                let vendorQty = result.cs.row(k).cell(result.cs.measureColumnIndex("Onhand Mtrl_Vendor Stock"));
                let cmiQty = result.cs.row(k).cell(result.cs.measureColumnIndex("Onhand Mtrl_CMI"));

                let unAvailTTLQty = result.cs.row(k).cell(result.cs.measureColumnIndex("Onhand Mtrl_Unavail TTL"));
                let blockQty = result.cs.row(k).cell(result.cs.measureColumnIndex("Onhand Mtrl_Block"));
                let returnQty = result.cs.row(k).cell(result.cs.measureColumnIndex("Onhand Mtrl_Return"));
                let svcQty = result.cs.row(k).cell(result.cs.measureColumnIndex("Onhand Mtrl_SVC"));
                let unAvailStorageQty = result.cs.row(k).cell(result.cs.measureColumnIndex("Onhand Mtrl_Unavail Storage"));

                //To Storage Location을 update 함.
                strToUpdateQuery += vdCommon.updateMeasureQuery(
                    ["[Version].[Version Name].["+fbVersion+"]",
                    "[Time].[Day].["+fbTimeDay+"]",
                    "[Location].[Location].["+fbLocation+"]",
                    "[Item Material].[Item Material].["+fbItemMaterial+"]",
                    "[Sub Location].[Sub Location].["+fbSubLocation+"]",
                    "[Storage Loc].[Storage Loc].["+fbToStorageLoc+"]"],
                    ["Measure.[Onhand Mtrl_Avail TTL] = Measure.[Onhand Mtrl_Avail TTL] + "+availTTLQty+";",
                    "Measure.[Onhand Mtrl_Unrestricted] = Measure.[Onhand Mtrl_Unrestricted] + "+unRestrictedQty+";",
                    "Measure.[Onhand Mtrl_HALB] = Measure.[Onhand Mtrl_HALB] + "+halbQty+";",
                    "Measure.[Onhand Mtrl_Inspection] = Measure.[Onhand Mtrl_Inspection] + "+inspectionQty+";",
                    "Measure.[Onhand Mtrl_Vendor Stock] = Measure.[Onhand Mtrl_Vendor Stock] + "+vendorQty+";",
                    "Measure.[Onhand Mtrl_CMI] = Measure.[Onhand Mtrl_CMI] + "+cmiQty+";",
                    "Measure.[Onhand Mtrl_Unavail TTL] = Measure.[Onhand Mtrl_Unavail TTL] + "+unAvailTTLQty+";",
                    "Measure.[Onhand Mtrl_Block] = Measure.[Onhand Mtrl_Block] + "+blockQty+";",
                    "Measure.[Onhand Mtrl_Return] = Measure.[Onhand Mtrl_Return] + "+returnQty+";",
                    "Measure.[Onhand Mtrl_SVC] = Measure.[Onhand Mtrl_SVC] + "+svcQty+";",
                    "Measure.[Onhand Mtrl_Unavail Storage] = Measure.[Onhand Mtrl_Unavail Storage] + "+unAvailStorageQty+";"
                    ]);

                strFromUpdateQuery += vdCommon.updateMeasureQuery(
                    ["[Version].[Version Name].["+fbVersion+"]",
                    "[Time].[Day].["+fbTimeDay+"]",
                    "[Location].[Location].["+fbLocation+"]",
                    "[Item Material].[Item Material].["+fbItemMaterial+"]",
                    "[Sub Location].[Sub Location].["+fbSubLocation+"]",
                    "[Storage Loc].[Storage Loc].["+fromStorageLoc+"]"],
                    ["Measure.[Onhand Mtrl_Avail TTL] = null;",
                    "Measure.[Onhand Mtrl_Unrestricted] = null;",
                    "Measure.[Onhand Mtrl_HALB] = null;",
                    "Measure.[Onhand Mtrl_Inspection] = null;",
                    "Measure.[Onhand Mtrl_Vendor Stock] = null;",
                    "Measure.[Onhand Mtrl_CMI] = null;",
                    "Measure.[Onhand Mtrl_Unavail TTL] = null;",
                    "Measure.[Onhand Mtrl_Block] = null;",
                    "Measure.[Onhand Mtrl_Return] =null;",
                    "Measure.[Onhand Mtrl_SVC] = null;",
                    "Measure.[Onhand Mtrl_Unavail Storage] = null;"
                    ]);
            }

            vdCommon.executeQuery("fn_transferStorage(toStorageLoc_Update)", strToUpdateQuery) ;
            vdCommon.executeQuery("fn_transferStorage(fromStorageLoc_Update)", strFromUpdateQuery) ;

            vdCommon.programEnd();

        }catch ( e ) {
            RuleOutputToUI = { Status : 'Error', Message : "Js Logic Error : " + e.message };
            return;
        }
    }

    return {
        fn_dataCheck : fn_dataCheck,
        fn_fromStorageLocCombo : fn_fromStorageLocCombo,
        fn_toStorageLocCombo :fn_toStorageLocCombo,
        fn_fromStorageQty : fn_fromStorageQty,
        fn_toStorageQty : fn_toStorageQty,
        fn_transferStorage : fn_transferStorage
    };
});