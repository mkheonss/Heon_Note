define('o9.JS_PurchaseSupplyPlanException', ['o9/data/query', 'o9/data/cellset', 'o9.NSCM.commonLib'], function () {

    const programName = "o9.JS_PurchaseSupplyPlanException============>";
    const commonLib = require('o9.NSCM.commonLib');
    const queryModule = require('o9/data/query');
    const cellsetModule = require('o9/data/cellset');
    vdCommon = new commonLib.VdCommon(programName);

    const allCheckN = "N";
    const allCheckY = "Y";
    let dimParams = {};

     //fn_comboMake is used to Fetch Material Code Details from Query variable "query"  and add "All" to it.
    function fn_comboMake(query, dimParams) {

        let selectResult = cellsetModule.createCellSet(queryModule.select(query));
        let selectResultCount = selectResult.rowCount;
        vdCommon.debug("fn_comboMake > selectResult : " + JSON.stringify(selectResult));
        vdCommon.debug("fn_comboMake > selectResultCount : " + selectResultCount);

        let comboList = [];
        let validHashMap = new Map();
        let allCheck = dimParams.allCheck;

        if (allCheck === "Y") {
            comboList.push({ Name: "All", DisplayName: "All" });
        }

        for (let i = 0; i < selectResultCount; i++) {
            const comboData = selectResult.row(i).cell(selectResult.memberColumnIndex(dimParams.levelKey, dimParams.levelValue)).Name;
            const comboName = selectResult.row(i).cell(selectResult.memberColumnIndex(dimParams.levelKey, dimParams.levelValue)).DisplayName;
//            vdCommon.debug("fn_comboMake > selectResult>memberColumnIndex : " + comboData);

            if (!validHashMap.has(comboData)) {
                comboList.push({ Name: comboData, DisplayName: comboData });
                validHashMap.set(comboData, comboData);
            }
        }
        return comboList;
    }

    //fn_VendorMake is used to Fetch Vendor Details related to Material Code Selected in Action Button and add "All" to it.
    function fn_VendorMake(query, dimParams) {

        let selectResult = cellsetModule.createCellSet(queryModule.select(query));
        let selectResultCount = selectResult.rowCount;
        vdCommon.debug("fn_comboMake > selectResult : " + JSON.stringify(selectResult));
        vdCommon.debug("fn_comboMake > selectResultCount Vendor: " + selectResultCount);

        let comboList = [];
        let validHashMap = new Map();
        let allCheck = dimParams.allCheck;

        if (allCheck === "Y") {
            comboList.push({ Name: "All", DisplayName: "All" });
        }

        for (let i = 0; i < selectResultCount; i++) {
            const comboData = selectResult.row(i).cell(selectResult.memberColumnIndex(dimParams.levelKey, dimParams.levelValue)).Name;
            const comboName = selectResult.row(i).cell(selectResult.measureColumnIndex("Vendor Mtrl_GT Name"));

            if (!validHashMap.has(comboData)) {
                comboList.push({ Name: comboData, DisplayName: comboName });
                validHashMap.set(comboData, comboName);
            }
        }
        return comboList;
    }

    //fn_plant is used to Fetch Plant Details fron Variable "query" and call fn_comboMake and add "All" to it.
    var fn_plant = function(o9Params){

        vdUtil = new commonLib.VdUtil();

        vdCommon.setLogLevel("Debug");

        vdCommon.printParams(o9Params);
        let parsedParams = JSON.parse(o9Params);

        dimParams.levelKey = "Sub Location";
        dimParams.levelValue = "Sub Location";
        dimParams.allCheck = allCheckY;

        let query = `
        select (&NSUISubLocationMFMtrlView);
        `;
        vdCommon.debug("GetToSiteAllSelectList > select query : " + query);
        let comboList = fn_comboMake(query, dimParams);
        RuleOutputToUI={comboList};
        vdCommon.programEnd();
        vdCommon.debug("fn_comboMake > ComboList Plant : " + JSON.stringify(comboList));
        return comboList;
    };

    //fn_materialCode is used to call the function fn_comboMake and pass the query
    var fn_materialCode = function(o9Params){

        vdUtil = new commonLib.VdUtil();

        vdCommon.setLogLevel("Debug");

        vdCommon.printParams(o9Params);
        let parsedParams = JSON.parse(o9Params);
        let Lv5 = parsedParams.Lv5;

        dimParams.levelKey = "Item Material";
        dimParams.levelValue = "Item Material";
        dimParams.allCheck = allCheckY;

        let query = 'Select ( [Item Material]. [MSL5].['+Lv5+']*[Item Material]. [Item Material]. filter(#. [Item Material$InActive]!=True) ) on row where {&CWVUI,Measure.[Item Mtrl Site Asn_Cur Status] in {"ACTIVE","PLANNED"}  };';
        vdCommon.debug("GetToSiteAllSelectList > select query : " + query);
        let comboList = fn_comboMake(query, dimParams);
        RuleOutputToUI={comboList};
        vdCommon.programEnd();
        vdCommon.debug("fn_comboMake > ComboList Materail Code : " + JSON.stringify(comboList));
        vdCommon.debug("fn_comboMake > ComboList Materail Code : " + comboList.length);
        return comboList;
    };

    //fn_vendor is used to call the function fn_vendorMake and pass the query based on the Material Code Value
    var fn_vendor = function(o9Params){

        vdUtil = new commonLib.VdUtil();

        vdCommon.setLogLevel("Debug");

        vdCommon.printParams(o9Params);
        let parsedParams = JSON.parse(o9Params);

        var MaterialCode = parsedParams.MaterialCode;

        dimParams.levelKey = "Global Top";
        dimParams.levelValue = "GT Code";
        dimParams.allCheck = allCheckY;

        // let query = `
        //             select (&VendorHQLocation);
        // `;

        if(MaterialCode==="All")
        {
            let query = '​Select ( &CWVUI * [Global Top].[GT Code].filter(#.Name startswith "G") ) on row, ({Measure.[Vendor Mtrl_GT Name]}) on column;';
            vdCommon.debug("GetToSiteAllSelectList > select query : " + query);
            let comboList = fn_VendorMake(query, dimParams);
            RuleOutputToUI={comboList};
            vdCommon.programEnd();
            vdCommon.debug("fn_comboMake > ComboList Vendor : " + JSON.stringify(comboList));
            return comboList;
        }
        else
        {
            let query = '​Select (&CWVUI * [Item Material].[Item Material].['+MaterialCode+'] * [Global Top].[GT Code] ) on row, ({Measure.[Vendor Mtrl_GT Name]}) on column;';
            vdCommon.debug("GetToSiteAllSelectList > select query : " + query);
            let comboList = fn_VendorMake(query, dimParams);
            RuleOutputToUI={comboList};
            vdCommon.programEnd();
            vdCommon.debug("fn_comboMake > ComboList Vendor : " + JSON.stringify(comboList));
            return comboList;
        }
    };


    //fn_Add is used for Insertion of Data based on Values Action Button, considering "All" values in Plant, Vendor.
    // Some test Cases has not been considered assuming Atrributes "[Item Material].[Item Material]", "[Location].[Location]" contains value "All".
    //Update - As of 07/05/2025, Data consist "All" in mentioned attributes.
    var fn_Add= function(o9Params){

        vdUtil = new commonLib.VdUtil();

        vdCommon.setLogLevel("Debug");

        vdCommon.printParams(o9Params);
        let parsedParams = JSON.parse(o9Params);
        // Parameters from Action Button
        var Lv5 = parsedParams.Lv5;
        var ABSource = parsedParams.Source;
        var ABCMI = parsedParams.CMI;
        var MaterialCode = parsedParams.MaterialCode;
        var Vendor = parsedParams.Vendor;
        var Plant = parsedParams.Plant;

        //Condition 1 - All Variables are "All"
        if(MaterialCode =="All" && Vendor=="All" && Plant == "All")
        {
            RuleOutputToUI = {
                Status: 'Error',
                Message: 'Please select at least one field from Material Code, Vendor(HQ), and Plant'
            };
        }

        var IncSeq = 0;
        var seq = [];
        
        let ExistRowCounter = 'Select ([Version].[Version Name].[CWV_MP] * [Sequence].[Sequence] * [Item Material].[MSL5] ) on row, ({Measure.[Supply Plan Source Map Ecp_CMI Flag], Measure.[Supply Plan Source Map Ecp_Excel Flag], Measure.[Supply Plan Source Map Ecp_GT Code], Measure.[Supply Plan Source Map Ecp_GT Name], Measure.[Supply Plan Source Map Ecp_Global RTF Flag], Measure.[Supply Plan Source Map Ecp_Mtrl Code], Measure.[Supply Plan Source Map Ecp_Open PO Flag], Measure.[Supply Plan Source Map Ecp_Plant], Measure.[Supply Plan Source Map Ecp_RTF Flag], Measure.[Supply Plan Source Map Ecp_RTP Flag], Measure.[Supply Plan Source Map Ecp_Source], Measure.[Supply Plan Source Map Ecp_UI Alloc], Measure.[Supply Plan Source Map Ecp_Update Time], Measure.[Supply Plan Source Map Ecp_Updated By]}) on column;';
        let checkResultCounter = cellsetModule.createCellSet(queryModule.select(ExistRowCounter));
        let RowCounter = checkResultCounter.rowCount;
        for(let i=0;i<RowCounter;i++)
        {
            var sequenceCompare = checkResultCounter.row(i).cell(checkResultCounter.memberColumnIndex("Sequence","Sequence")).Name;
            // vdCommon.debug("Sequence Printer :: "+sequenceCompare);
            if(!seq.includes(sequenceCompare))
            {
                seq.push(sequenceCompare);
            }
        }
        vdCommon.debug("RowCounter ::: "+RowCounter);
        seq.forEach((num) => {
                if (num != null && num !== "") {
                const parsedNum = parseInt(num);
                if (parsedNum > IncSeq) {
                IncSeq = parsedNum;
                }
                }
            });
        IncSeq = IncSeq + 1;
        
        
        //Condition 2 - Only MaterialCode is not "All"
        if (MaterialCode != "All" && Vendor == "All" && Plant == "All")
        {
            var Gt = [];
            var validHashMap = [];

            ABVendor = '"'+Vendor+'"';
            ABPlant = '"'+Plant+'"';
            ABMaterialCode = '"'+MaterialCode+'"';

            fGTquery = 'Select ([Version].[Version Name].[CWV_MP] * [Location].[Location] * [Item Material].[Item Material].['+MaterialCode+'] * [Vendor].[Vendor] * [Global Top].[GT Code].filter(#. Name startswith([G])) * [Partner Vendor].[Partner Vendor] ) on row, ({Measure.[Vendor Mtrl_GT Name], Measure.[Vendor Mtrl_Master Ecp Flag], Measure.[Vendor Mtrl_Master Flag], Measure.[Vendor Mtrl_Quota], Measure.[Vendor Mtrl_Result Ecp Flag], Measure.[Vendor Mtrl_Result Flag]}) on column; ';

            let fGTTable = cellsetModule.createCellSet(queryModule.select(fGTquery));
            let fGTCount = fGTTable.rowCount;
            for(let i=0;i<fGTCount;i++)
            {
                var Gtcode = fGTTable.row(i).cell(fGTTable.memberColumnIndex("Global Top","GT Code")).Name;
                if(!validHashMap.includes(Gtcode))
                {
                    Gt.push(Gtcode);
                    validHashMap.push(Gtcode);
                }
            }
            vdCommon.debug("Pause : "+Gt);

            let createQuery = '';

            if (Gt.length>1)
            {
                createQuery = 'cartesian scope: ([Version].[Version Name].[CWV_MP] * [Sequence].[Sequence].['+IncSeq+'] * [Item Material].[MSL5].['+Lv5+'] ); Measure.[Supply Plan Source Map Ecp_CMI Flag] = '+ABCMI+'; Measure.[Supply Plan Source Map Ecp_Source] = '+ABSource+';  Measure.[Supply Plan Source Map Ecp_GT Name] = '+ABVendor+'; Measure.[Supply Plan Source Map Ecp_Mtrl Code] ='+ABMaterialCode+' ; Measure.[Supply Plan Source Map Ecp_Plant] = '+ABPlant+';Measure.[Supply Plan Source Map Ecp_GT Code]="All"; end scope;';
            }
            else if (Gt.length==1)
            {
                fGTCodeValue = fGTTable.row(0).cell(fGTTable.memberColumnIndex("Global Top","GT Code")).Name;
                fGTCode = '"'+fGTCodeValue+'"';
                createQuery = 'cartesian scope: ([Version].[Version Name].[CWV_MP] * [Sequence].[Sequence].['+IncSeq+'] * [Item Material].[MSL5].['+Lv5+'] ); Measure.[Supply Plan Source Map Ecp_CMI Flag] = '+ABCMI+'; Measure.[Supply Plan Source Map Ecp_Source] = '+ABSource+';  Measure.[Supply Plan Source Map Ecp_GT Name] = '+ABVendor+'; Measure.[Supply Plan Source Map Ecp_Mtrl Code] ='+ABMaterialCode+' ; Measure.[Supply Plan Source Map Ecp_Plant] = '+ABPlant+';Measure.[Supply Plan Source Map Ecp_GT Code]='+fGTCode+'; end scope;';
            }
            else
            {
                fGTCodeValue = "-";
                fGTCode = '"'+fGTCodeValue+'"';
                createQuery = 'cartesian scope: ([Version].[Version Name].[CWV_MP] * [Sequence].[Sequence].['+IncSeq+'] * [Item Material].[MSL5].['+Lv5+'] ); Measure.[Supply Plan Source Map Ecp_CMI Flag] = '+ABCMI+'; Measure.[Supply Plan Source Map Ecp_Source] = '+ABSource+';  Measure.[Supply Plan Source Map Ecp_GT Name] = '+ABVendor+'; Measure.[Supply Plan Source Map Ecp_Mtrl Code] ='+ABMaterialCode+' ; Measure.[Supply Plan Source Map Ecp_Plant] = '+ABPlant+';Measure.[Supply Plan Source Map Ecp_GT Code]='+fGTCode+'; end scope;';
            }
            vdCommon.debug("Pause : "+createQuery);
            // vdCommon.debug("Pause : "+Plant2);
            queryModule.update(createQuery);
        }
        //Condition 3 - Only Vendor is not "All"
        else if (MaterialCode == "All" && Vendor != "All" && Plant == "All")
        {
            let VendorCheck = 'select ([Location].[Location].['+Vendor+']);';
            let VendorcheckResult = cellsetModule.createCellSet(queryModule.select(VendorCheck));
            VendorCompare = VendorcheckResult.row(0).cell(VendorcheckResult.memberColumnIndex("Location","Location")).DisplayName;

            var Gt = [];
            var validHashMap = [];

            ABVendor = '"'+VendorCompare+'"';
            ABPlant = '"'+Plant+'"';
            ABMaterialCode = '"'+MaterialCode+'"';

            fGTquery = 'Select ([Version].[Version Name].[CWV_MP] * [Location].[Location] * [Item Material].[Item Material] * [Vendor].[Vendor] * [Global Top].[GT Code].['+Vendor+'] * [Partner Vendor].[Partner Vendor] ) on row, ({Measure.[Vendor Mtrl_GT Name], Measure.[Vendor Mtrl_Master Ecp Flag], Measure.[Vendor Mtrl_Master Flag], Measure.[Vendor Mtrl_Quota], Measure.[Vendor Mtrl_Result Ecp Flag], Measure.[Vendor Mtrl_Result Flag]}) on column; ';

            let fGTTable = cellsetModule.createCellSet(queryModule.select(fGTquery));
            
            fGTCodeValue = fGTTable.row(0).cell(fGTTable.memberColumnIndex("Global Top","GT Code")).Name;
            fGTCode = '"'+fGTCodeValue+'"';

            let createQuery = 'cartesian scope: ([Version].[Version Name].[CWV_MP] * [Sequence].[Sequence].['+IncSeq+'] * [Item Material].[MSL5].['+Lv5+'] ); Measure.[Supply Plan Source Map Ecp_CMI Flag] = '+ABCMI+'; Measure.[Supply Plan Source Map Ecp_Source] = '+ABSource+';  Measure.[Supply Plan Source Map Ecp_GT Name] = '+ABVendor+'; Measure.[Supply Plan Source Map Ecp_Mtrl Code] ='+ABMaterialCode+' ; Measure.[Supply Plan Source Map Ecp_Plant] = '+ABPlant+';Measure.[Supply Plan Source Map Ecp_GT Code]='+fGTCode+'; end scope;'; 
            
            vdCommon.debug("Pause : "+createQuery);
            // vdCommon.debug("Pause : "+Plant3);
            queryModule.update(createQuery);
        }
        //Condition 4 - Only Plant is not "All"
        else if (MaterialCode == "All" && Vendor == "All" && Plant != "All")
        {
            var Gt = [];
            var validHashMap = [];

            ABVendor = '"'+Vendor+'"';
            ABPlant = '"'+Plant+'"';
            ABMaterialCode = '"'+MaterialCode+'"';

            fGTquery = 'Select ([Version].[Version Name].[CWV_MP] * [Location].[Location].['+Plant+'] * [Global Top].[GT Code].filter(#. Name startswith([G]))) on row, ({Measure.[Vendor Mtrl_GT Name], Measure.[Vendor Mtrl_Master Ecp Flag], Measure.[Vendor Mtrl_Master Flag], Measure.[Vendor Mtrl_Quota], Measure.[Vendor Mtrl_Result Ecp Flag], Measure.[Vendor Mtrl_Result Flag]}) on column; ';

            let fGTTable = cellsetModule.createCellSet(queryModule.select(fGTquery));
            let fGTCount = fGTTable.rowCount;
            for(let i=0;i<fGTCount;i++)
            {
                var Gtcode = fGTTable.row(i).cell(fGTTable.memberColumnIndex("Global Top","GT Code")).Name;
                if(!validHashMap.includes(Gtcode))
                {
                    Gt.push(Gtcode);
                    validHashMap.push(Gtcode);
                }
            }
            vdCommon.debug("Pause : "+Gt);

            let createQuery = '';

            if (Gt.length>1)
            {
                createQuery = 'cartesian scope: ([Version].[Version Name].[CWV_MP] * [Sequence].[Sequence].['+IncSeq+'] * [Item Material].[MSL5].['+Lv5+'] ); Measure.[Supply Plan Source Map Ecp_CMI Flag] = '+ABCMI+'; Measure.[Supply Plan Source Map Ecp_Source] = '+ABSource+';  Measure.[Supply Plan Source Map Ecp_GT Name] = '+ABVendor+'; Measure.[Supply Plan Source Map Ecp_Mtrl Code] ='+ABMaterialCode+' ; Measure.[Supply Plan Source Map Ecp_Plant] = '+ABPlant+';Measure.[Supply Plan Source Map Ecp_GT Code]="All"; end scope;';
            }
            else if (Gt.length==1)
            {
                fGTCodeValue = fGTTable.row(0).cell(fGTTable.memberColumnIndex("Global Top","GT Code")).Name;
                fGTCode = '"'+fGTCodeValue+'"';
                createQuery = 'cartesian scope: ([Version].[Version Name].[CWV_MP] * [Sequence].[Sequence].['+IncSeq+'] * [Item Material].[MSL5].['+Lv5+'] ); Measure.[Supply Plan Source Map Ecp_CMI Flag] = '+ABCMI+'; Measure.[Supply Plan Source Map Ecp_Source] = '+ABSource+';  Measure.[Supply Plan Source Map Ecp_GT Name] = '+ABVendor+'; Measure.[Supply Plan Source Map Ecp_Mtrl Code] ='+ABMaterialCode+' ; Measure.[Supply Plan Source Map Ecp_Plant] = '+ABPlant+';Measure.[Supply Plan Source Map Ecp_GT Code]='+fGTCode+'; end scope;';
            }
            else
            {
                fGTCodeValue = "-";
                fGTCode = '"'+fGTCodeValue+'"';
                createQuery = 'cartesian scope: ([Version].[Version Name].[CWV_MP] * [Sequence].[Sequence].['+IncSeq+'] * [Item Material].[MSL5].['+Lv5+'] ); Measure.[Supply Plan Source Map Ecp_CMI Flag] = '+ABCMI+'; Measure.[Supply Plan Source Map Ecp_Source] = '+ABSource+';  Measure.[Supply Plan Source Map Ecp_GT Name] = '+ABVendor+'; Measure.[Supply Plan Source Map Ecp_Mtrl Code] ='+ABMaterialCode+' ; Measure.[Supply Plan Source Map Ecp_Plant] = '+ABPlant+';Measure.[Supply Plan Source Map Ecp_GT Code]='+fGTCode+'; end scope;';
            }
            vdCommon.debug("Pause : "+createQuery);
            // vdCommon.debug("Pause : "+Plant4);
            queryModule.update(createQuery);

        }
        //Condition 5 - MaterialCode and Vendor are not "All"
        else if (MaterialCode != "All" && Vendor != "All" && Plant == "All")
        {
            let VendorCheck = 'select ([Location].[Location].['+Vendor+']);';
            let VendorcheckResult = cellsetModule.createCellSet(queryModule.select(VendorCheck));
            VendorCompare = VendorcheckResult.row(0).cell(VendorcheckResult.memberColumnIndex("Location","Location")).DisplayName;

            var Gt = [];
            var validHashMap = [];

            ABVendor = '"'+VendorCompare+'"';
            ABPlant = '"'+Plant+'"';
            ABMaterialCode = '"'+MaterialCode+'"';

            fGTquery = 'Select ([Version].[Version Name].[CWV_MP] * [Location].[Location] * [Item Material].[Item Material].['+MaterialCode+'] * [Vendor].[Vendor] * [Global Top].[GT Code].['+Vendor+'] * [Partner Vendor].[Partner Vendor] ) on row, ({Measure.[Vendor Mtrl_GT Name], Measure.[Vendor Mtrl_Master Ecp Flag], Measure.[Vendor Mtrl_Master Flag], Measure.[Vendor Mtrl_Quota], Measure.[Vendor Mtrl_Result Ecp Flag], Measure.[Vendor Mtrl_Result Flag]}) on column; ';

            let fGTTable = cellsetModule.createCellSet(queryModule.select(fGTquery));
            
            fGTCodeValue = fGTTable.row(0).cell(fGTTable.memberColumnIndex("Global Top","GT Code")).Name;
            fGTCode = '"'+fGTCodeValue+'"';

            let createQuery = 'cartesian scope: ([Version].[Version Name].[CWV_MP] * [Sequence].[Sequence].['+IncSeq+'] * [Item Material].[MSL5].['+Lv5+'] ); Measure.[Supply Plan Source Map Ecp_CMI Flag] = '+ABCMI+'; Measure.[Supply Plan Source Map Ecp_Source] = '+ABSource+';  Measure.[Supply Plan Source Map Ecp_GT Name] = '+ABVendor+'; Measure.[Supply Plan Source Map Ecp_Mtrl Code] ='+ABMaterialCode+' ; Measure.[Supply Plan Source Map Ecp_Plant] = '+ABPlant+';Measure.[Supply Plan Source Map Ecp_GT Code]='+fGTCode+'; end scope;'; 
            
            vdCommon.debug("Pause : "+createQuery);
            // vdCommon.debug("Pause : "+Plant5);
            queryModule.update(createQuery);
        }
        //Condition 6 - MaterialCode and Plant are not "All"
        else if (MaterialCode != "All" && Vendor == "All" && Plant != "All")
        {
            var Gt = [];
            var validHashMap = [];

            ABVendor = '"'+Vendor+'"';
            ABPlant = '"'+Plant+'"';
            ABMaterialCode = '"'+MaterialCode+'"';

            fGTquery = 'Select ([Version].[Version Name].[CWV_MP] * [Location].[Location].['+Plant+'] * [Item Material].[Item Material].['+MaterialCode+'] * [Vendor].[Vendor] * [Global Top].[GT Code].filter(#. Name startswith([G])) * [Partner Vendor].[Partner Vendor] ) on row, ({Measure.[Vendor Mtrl_GT Name], Measure.[Vendor Mtrl_Master Ecp Flag], Measure.[Vendor Mtrl_Master Flag], Measure.[Vendor Mtrl_Quota], Measure.[Vendor Mtrl_Result Ecp Flag], Measure.[Vendor Mtrl_Result Flag]}) on column; ';

            let fGTTable = cellsetModule.createCellSet(queryModule.select(fGTquery));
            let fGTCount = fGTTable.rowCount;
            for(let i=0;i<fGTCount;i++)
            {
                var Gtcode = fGTTable.row(i).cell(fGTTable.memberColumnIndex("Global Top","GT Code")).Name;
                if(!validHashMap.includes(Gtcode))
                {
                    Gt.push(Gtcode);
                    validHashMap.push(Gtcode);
                }
            }
            vdCommon.debug("Pause : "+Gt);

            let createQuery = '';

            if (Gt.length>1)
            {
                createQuery = 'cartesian scope: ([Version].[Version Name].[CWV_MP] * [Sequence].[Sequence].['+IncSeq+'] * [Item Material].[MSL5].['+Lv5+'] ); Measure.[Supply Plan Source Map Ecp_CMI Flag] = '+ABCMI+'; Measure.[Supply Plan Source Map Ecp_Source] = '+ABSource+';  Measure.[Supply Plan Source Map Ecp_GT Name] = '+ABVendor+'; Measure.[Supply Plan Source Map Ecp_Mtrl Code] ='+ABMaterialCode+' ; Measure.[Supply Plan Source Map Ecp_Plant] = '+ABPlant+';Measure.[Supply Plan Source Map Ecp_GT Code]="All"; end scope;';
            }
            else if (Gt.length==1)
            {
                fGTCodeValue = fGTTable.row(0).cell(fGTTable.memberColumnIndex("Global Top","GT Code")).Name;
                fGTCode = '"'+fGTCodeValue+'"';
                createQuery = 'cartesian scope: ([Version].[Version Name].[CWV_MP] * [Sequence].[Sequence].['+IncSeq+'] * [Item Material].[MSL5].['+Lv5+'] ); Measure.[Supply Plan Source Map Ecp_CMI Flag] = '+ABCMI+'; Measure.[Supply Plan Source Map Ecp_Source] = '+ABSource+';  Measure.[Supply Plan Source Map Ecp_GT Name] = '+ABVendor+'; Measure.[Supply Plan Source Map Ecp_Mtrl Code] ='+ABMaterialCode+' ; Measure.[Supply Plan Source Map Ecp_Plant] = '+ABPlant+';Measure.[Supply Plan Source Map Ecp_GT Code]='+fGTCode+'; end scope;';
            }
            else
            {
                fGTCodeValue = "-";
                fGTCode = '"'+fGTCodeValue+'"';
                createQuery = 'cartesian scope: ([Version].[Version Name].[CWV_MP] * [Sequence].[Sequence].['+IncSeq+'] * [Item Material].[MSL5].['+Lv5+'] ); Measure.[Supply Plan Source Map Ecp_CMI Flag] = '+ABCMI+'; Measure.[Supply Plan Source Map Ecp_Source] = '+ABSource+';  Measure.[Supply Plan Source Map Ecp_GT Name] = '+ABVendor+'; Measure.[Supply Plan Source Map Ecp_Mtrl Code] ='+ABMaterialCode+' ; Measure.[Supply Plan Source Map Ecp_Plant] = '+ABPlant+';Measure.[Supply Plan Source Map Ecp_GT Code]='+fGTCode+'; end scope;';
            }
            vdCommon.debug("Pause : "+createQuery);
            // vdCommon.debug("Pause : "+Plant6);
            queryModule.update(createQuery);
        }
        //Condition 7 - Vendor and Plant are not "All"
        else if (MaterialCode == "All" && Vendor != "All" && Plant != "All")
        {
            let VendorCheck = 'select ([Location].[Location].['+Vendor+']);';
            let VendorcheckResult = cellsetModule.createCellSet(queryModule.select(VendorCheck));
            VendorCompare = VendorcheckResult.row(0).cell(VendorcheckResult.memberColumnIndex("Location","Location")).DisplayName;

            var Gt = [];
            var validHashMap = [];

            ABVendor = '"'+VendorCompare+'"';
            ABPlant = '"'+Plant+'"';
            ABMaterialCode = '"'+MaterialCode+'"';

            fGTquery = 'Select ([Version].[Version Name].[CWV_MP] * [Location].[Location].['+Plant+'] * [Item Material].[Item Material]* [Vendor].[Vendor] * [Global Top].[GT Code].['+Vendor+'] * [Partner Vendor].[Partner Vendor] ) on row, ({Measure.[Vendor Mtrl_GT Name], Measure.[Vendor Mtrl_Master Ecp Flag], Measure.[Vendor Mtrl_Master Flag], Measure.[Vendor Mtrl_Quota], Measure.[Vendor Mtrl_Result Ecp Flag], Measure.[Vendor Mtrl_Result Flag]}) on column; ';

            let fGTTable = cellsetModule.createCellSet(queryModule.select(fGTquery));
            let fGTCount = fGTTable.rowCount;
            for(let i=0;i<fGTCount;i++)
            {
                var Gtcode = fGTTable.row(i).cell(fGTTable.memberColumnIndex("Global Top","GT Code")).Name;
                if(!validHashMap.includes(Gtcode))
                {
                    Gt.push(Gtcode);
                    validHashMap.push(Gtcode);
                }
            }
            vdCommon.debug("Pause : "+Gt);

            let createQuery = '';

            if (Gt.length>1)
            {
                createQuery = 'cartesian scope: ([Version].[Version Name].[CWV_MP] * [Sequence].[Sequence].['+IncSeq+'] * [Item Material].[MSL5].['+Lv5+'] ); Measure.[Supply Plan Source Map Ecp_CMI Flag] = '+ABCMI+'; Measure.[Supply Plan Source Map Ecp_Source] = '+ABSource+';  Measure.[Supply Plan Source Map Ecp_GT Name] = '+ABVendor+'; Measure.[Supply Plan Source Map Ecp_Mtrl Code] ='+ABMaterialCode+' ; Measure.[Supply Plan Source Map Ecp_Plant] = '+ABPlant+';Measure.[Supply Plan Source Map Ecp_GT Code]="All"; end scope;';
            }
            else if (Gt.length==1)
            {
                fGTCodeValue = fGTTable.row(0).cell(fGTTable.memberColumnIndex("Global Top","GT Code")).Name;
                fGTCode = '"'+fGTCodeValue+'"';
                createQuery = 'cartesian scope: ([Version].[Version Name].[CWV_MP] * [Sequence].[Sequence].['+IncSeq+'] * [Item Material].[MSL5].['+Lv5+'] ); Measure.[Supply Plan Source Map Ecp_CMI Flag] = '+ABCMI+'; Measure.[Supply Plan Source Map Ecp_Source] = '+ABSource+';  Measure.[Supply Plan Source Map Ecp_GT Name] = '+ABVendor+'; Measure.[Supply Plan Source Map Ecp_Mtrl Code] ='+ABMaterialCode+' ; Measure.[Supply Plan Source Map Ecp_Plant] = '+ABPlant+';Measure.[Supply Plan Source Map Ecp_GT Code]='+fGTCode+'; end scope;';
            }
            else
            {
                fGTCodeValue = "-";
                fGTCode = '"'+fGTCodeValue+'"';
                createQuery = 'cartesian scope: ([Version].[Version Name].[CWV_MP] * [Sequence].[Sequence].['+IncSeq+'] * [Item Material].[MSL5].['+Lv5+'] ); Measure.[Supply Plan Source Map Ecp_CMI Flag] = '+ABCMI+'; Measure.[Supply Plan Source Map Ecp_Source] = '+ABSource+';  Measure.[Supply Plan Source Map Ecp_GT Name] = '+ABVendor+'; Measure.[Supply Plan Source Map Ecp_Mtrl Code] ='+ABMaterialCode+' ; Measure.[Supply Plan Source Map Ecp_Plant] = '+ABPlant+';Measure.[Supply Plan Source Map Ecp_GT Code]='+fGTCode+'; end scope;';
            }
            vdCommon.debug("Pause : "+createQuery);
            // vdCommon.debug("Pause : "+Plant7);
            queryModule.update(createQuery);
        }
        //Condition 8 - All Variables are not "All"
        else if (MaterialCode != "All" && Vendor != "All" && Plant != "All")
        {
            let VendorCheck = 'select ([Location].[Location].['+Vendor+']);';
            let VendorcheckResult = cellsetModule.createCellSet(queryModule.select(VendorCheck));
            VendorCompare = VendorcheckResult.row(0).cell(VendorcheckResult.memberColumnIndex("Location","Location")).DisplayName;

            var Gt = [];
            var validHashMap = [];

            ABVendor = '"'+VendorCompare+'"';
            ABPlant = '"'+Plant+'"';
            ABMaterialCode = '"'+MaterialCode+'"';

            fGTquery = 'Select ([Version].[Version Name].[CWV_MP] * [Location].[Location].['+Plant+'] * [Item Material].[Item Material].['+MaterialCode+']* [Vendor].[Vendor] * [Global Top].[GT Code].['+Vendor+'] * [Partner Vendor].[Partner Vendor] ) on row, ({Measure.[Vendor Mtrl_GT Name], Measure.[Vendor Mtrl_Master Ecp Flag], Measure.[Vendor Mtrl_Master Flag], Measure.[Vendor Mtrl_Quota], Measure.[Vendor Mtrl_Result Ecp Flag], Measure.[Vendor Mtrl_Result Flag]}) on column; ';

            let fGTTable = cellsetModule.createCellSet(queryModule.select(fGTquery));
            let fGTCount = fGTTable.rowCount;
            for(let i=0;i<fGTCount;i++)
            {
                var Gtcode = fGTTable.row(i).cell(fGTTable.memberColumnIndex("Global Top","GT Code")).Name;
                if(!validHashMap.includes(Gtcode))
                {
                    Gt.push(Gtcode);
                    validHashMap.push(Gtcode);
                }
            }
            vdCommon.debug("Pause : "+Gt);

            let createQuery = '';

            if (Gt.length>1)
            {
                createQuery = 'cartesian scope: ([Version].[Version Name].[CWV_MP] * [Sequence].[Sequence].['+IncSeq+'] * [Item Material].[MSL5].['+Lv5+'] ); Measure.[Supply Plan Source Map Ecp_CMI Flag] = '+ABCMI+'; Measure.[Supply Plan Source Map Ecp_Source] = '+ABSource+';  Measure.[Supply Plan Source Map Ecp_GT Name] = '+ABVendor+'; Measure.[Supply Plan Source Map Ecp_Mtrl Code] ='+ABMaterialCode+' ; Measure.[Supply Plan Source Map Ecp_Plant] = '+ABPlant+';Measure.[Supply Plan Source Map Ecp_GT Code]="All"; end scope;';
            }
            else if (Gt.length==1)
            {
                fGTCodeValue = fGTTable.row(0).cell(fGTTable.memberColumnIndex("Global Top","GT Code")).Name;
                fGTCode = '"'+fGTCodeValue+'"';
                createQuery = 'cartesian scope: ([Version].[Version Name].[CWV_MP] * [Sequence].[Sequence].['+IncSeq+'] * [Item Material].[MSL5].['+Lv5+'] ); Measure.[Supply Plan Source Map Ecp_CMI Flag] = '+ABCMI+'; Measure.[Supply Plan Source Map Ecp_Source] = '+ABSource+';  Measure.[Supply Plan Source Map Ecp_GT Name] = '+ABVendor+'; Measure.[Supply Plan Source Map Ecp_Mtrl Code] ='+ABMaterialCode+' ; Measure.[Supply Plan Source Map Ecp_Plant] = '+ABPlant+';Measure.[Supply Plan Source Map Ecp_GT Code]='+fGTCode+'; end scope;';
            }
            else
            {
                fGTCodeValue = "-";
                fGTCode = '"'+fGTCodeValue+'"';
                createQuery = 'cartesian scope: ([Version].[Version Name].[CWV_MP] * [Sequence].[Sequence].['+IncSeq+'] * [Item Material].[MSL5].['+Lv5+'] ); Measure.[Supply Plan Source Map Ecp_CMI Flag] = '+ABCMI+'; Measure.[Supply Plan Source Map Ecp_Source] = '+ABSource+';  Measure.[Supply Plan Source Map Ecp_GT Name] = '+ABVendor+'; Measure.[Supply Plan Source Map Ecp_Mtrl Code] ='+ABMaterialCode+' ; Measure.[Supply Plan Source Map Ecp_Plant] = '+ABPlant+';Measure.[Supply Plan Source Map Ecp_GT Code]='+fGTCode+'; end scope;';
            }
            vdCommon.debug("Pause : "+createQuery);
            // vdCommon.debug("Pause : "+Plant8);
            queryModule.update(createQuery);
        }
           
    };

    //fn_delete is used for Delete based on Sequence and Lv5 selected.
    var fn_delete= function(o9Params){

        vdUtil = new commonLib.VdUtil();

        vdCommon.setLogLevel("Debug");

        vdCommon.printParams(o9Params);
        let parsedParams = JSON.parse(o9Params);

        var Lv5 = parsedParams.Lv5;
        var Sequence = parsedParams.Sequence

        var fLev5 = JSON.stringify(Lv5).replace(/\{([^}]+)\}/, (m, p1) => '{' + p1.split(',').map(item => `"${item.trim()}"`).join(', ') + '}');
        var fSequence = JSON.stringify(Sequence).replace(/\{([^}]+)\}/, (m, p1) => '{' + p1.split(',').map(item => `"${item.trim()}"`).join(', ') + '}');
        
        let Lev5Array =JSON.parse(fLev5);
        let fLev5f = `{${Lev5Array.map(item => `"${item}"`).join(",")}}`;
        let sequenceArray =JSON.parse(fSequence);
        let fSequencef = `{${sequenceArray.map(item => `"${item}"`).join(",")}}`;
        vdCommon.debug("Lev5 :::: "+fLev5f);
        vdCommon.debug("Sequence :::: "+fSequencef);        

        let checkQuery = 'Select ([Version].[Version Name].[CWV_MP] * [Sequence].[Sequence].filter(#.Name in '+fSequencef+') * [Item Material].[MSL5].filter(#.Name in '+fLev5f+') ) on row,({Measure.[Supply Plan Source Map Ecp_CMI Flag],Measure.[Supply Plan Source Map Ecp_Excel Flag],Measure.[Supply Plan Source Map Ecp_GT Name],Measure.[Supply Plan Source Map Ecp_Global RTF Flag],Measure.[Supply Plan Source Map Ecp_Mtrl Code],Measure.[Supply Plan Source Map Ecp_Open PO Flag],Measure.[Supply Plan Source Map Ecp_Plant],Measure.[Supply Plan Source Map Ecp_RTF Flag],Measure.[Supply Plan Source Map Ecp_RTP Flag],Measure.[Supply Plan Source Map Ecp_Source],Measure.[Supply Plan Source Map Ecp_UI Alloc],Measure.[Supply Plan Source Map Ecp_Update Time],Measure.[Supply Plan Source Map Ecp_Updated By]}) on column;';
        var checkQueryResult = cellsetModule.createCellSet(queryModule.select(checkQuery));
        var checkQueryResultRow = checkQueryResult.rowCount;
        vdCommon.debug("Rows : "+checkQueryResultRow);
        
        for(let i=0;i<checkQueryResultRow;i++)
        {
            let ffLev5 = checkQueryResult.row(i).cell(checkQueryResult.memberColumnIndex("Item Material","MSL5")).Name;
            let ffSequence = checkQueryResult.row(i).cell(checkQueryResult.memberColumnIndex("Sequence","Sequence")).Name;

            query2 = 'delete data for model [Supply Plan Source Map Ecp] where {[Version].[Version Name].[CWV_MP],[Sequence].[Sequence].['+ffSequence +'],[Item Material].[MSL5].['+ffLev5+']};';
            queryModule.update(query2);
        }
    };

    var fn_MSL1= function(o9Params){

        vdUtil = new commonLib.VdUtil();

        vdCommon.setLogLevel("Debug");

        vdCommon.printParams(o9Params);
        let parsedParams = JSON.parse(o9Params);

        var comboList = [];

        var TupleList = parsedParams.TupleList;
        vdCommon.debug("TupleList : "+TupleList);
        var element1 = TupleList[0].MSL1.Value;
        vdCommon.debug("MSL1 Value : "+element1);
        
        let queryMSL1 = 'select (&NSUIMtrlMSL1View.['+element1+']);';
        let queryMSL1Table = cellsetModule.createCellSet(queryModule.select(queryMSL1)); 
        let ffLev1 = queryMSL1Table.row(0).cell(queryMSL1Table.memberColumnIndex("Item Material","MSL1")).Name;
        let ffLev1DN = queryMSL1Table.row(0).cell(queryMSL1Table.memberColumnIndex("Item Material","MSL1")).DisplayName;
        let ffLev1DA = queryMSL1Table.row(0).cell(queryMSL1Table.memberColumnIndex("Item Material","MSL1")).DisplayAlias;   
        comboList.push({Name : ffLev1, DisplayName : ffLev1DA });
        vdCommon.debug("ComboList MSL1: "+ JSON.stringify(comboList));
        return comboList;
    };

    var fn_MSL2= function(o9Params){

        vdUtil = new commonLib.VdUtil();

        vdCommon.setLogLevel("Debug");

        vdCommon.printParams(o9Params);
        let parsedParams = JSON.parse(o9Params);

        var comboList = [];

        var TupleList = parsedParams.TupleList;
        vdCommon.debug("TupleList : "+TupleList);
        var element2 = TupleList[0].MSL2.Value;
        vdCommon.debug("MSL2 Value : "+element2);
        
        let queryMSL2 = 'select (&NSUIMtrlMSL2View.['+element2+']);';
        let queryMSL2Table = cellsetModule.createCellSet(queryModule.select(queryMSL2)); 
        let ffLev2 = queryMSL2Table.row(0).cell(queryMSL2Table.memberColumnIndex("Item Material","MSL2")).Name;
        let ffLev2DN = queryMSL2Table.row(0).cell(queryMSL2Table.memberColumnIndex("Item Material","MSL2")).DisplayName;
        let ffLev2DA = queryMSL2Table.row(0).cell(queryMSL2Table.memberColumnIndex("Item Material","MSL2")).DisplayAlias;   
        comboList.push({Name : ffLev2, DisplayName : ffLev2DA });
        vdCommon.debug("ComboList MSL2: "+ JSON.stringify(comboList));
        return comboList;
    };

    var fn_MSL3= function(o9Params){

        vdUtil = new commonLib.VdUtil();

        vdCommon.setLogLevel("Debug");

        vdCommon.printParams(o9Params);
        let parsedParams = JSON.parse(o9Params);

        var comboList = [];

        var TupleList = parsedParams.TupleList;
        vdCommon.debug("TupleList : "+TupleList);
        var element3 = TupleList[0].MSL3.Value;
        vdCommon.debug("MSL3 Value : "+element3);
        
        let queryMSL3 = 'select (&NSUIMtrlMSL3View.['+element3+']);';
        let queryMSL3Table = cellsetModule.createCellSet(queryModule.select(queryMSL3)); 
        let ffLev3 = queryMSL3Table.row(0).cell(queryMSL3Table.memberColumnIndex("Item Material","MSL3")).Name;
        let ffLev3DN = queryMSL3Table.row(0).cell(queryMSL3Table.memberColumnIndex("Item Material","MSL3")).DisplayName;
        let ffLev3DA = queryMSL3Table.row(0).cell(queryMSL3Table.memberColumnIndex("Item Material","MSL3")).DisplayAlias;   
        comboList.push({Name : ffLev3, DisplayName : ffLev3DA });
        vdCommon.debug("ComboList MSL3: "+ JSON.stringify(comboList));
        return comboList;
    };

    var fn_MSL4= function(o9Params){

        vdUtil = new commonLib.VdUtil();

        vdCommon.setLogLevel("Debug");

        vdCommon.printParams(o9Params);
        let parsedParams = JSON.parse(o9Params);

        var comboList = [];

        var TupleList = parsedParams.TupleList;
        vdCommon.debug("TupleList : "+TupleList);
        var element4 = TupleList[0].MSL4.Value;
        vdCommon.debug("MSL4 Value : "+element4);
        
        let queryMSL4 = 'select (&NSUIMtrlMSL4View.['+element4+']);';
        let queryMSL4Table = cellsetModule.createCellSet(queryModule.select(queryMSL4)); 
        let ffLev4 = queryMSL4Table.row(0).cell(queryMSL4Table.memberColumnIndex("Item Material","MSL4")).Name;
        let ffLev4DN = queryMSL4Table.row(0).cell(queryMSL4Table.memberColumnIndex("Item Material","MSL4")).DisplayName;
        let ffLev4DA = queryMSL4Table.row(0).cell(queryMSL4Table.memberColumnIndex("Item Material","MSL4")).DisplayAlias;   
        comboList.push({Name : ffLev4, DisplayName : ffLev4DA });
        vdCommon.debug("ComboList MSL4: "+ JSON.stringify(comboList));
        return comboList;
    };

    var fn_MSL5= function(o9Params){

        vdUtil = new commonLib.VdUtil();

        vdCommon.setLogLevel("Debug");

        vdCommon.printParams(o9Params);
        let parsedParams = JSON.parse(o9Params);

        var comboList = [];

        var TupleList = parsedParams.TupleList;
        vdCommon.debug("TupleList : "+TupleList);
        var element5 = TupleList[0].MSL5.Value;
        vdCommon.debug("MSL5 Value : "+element5);
        
        let queryMSL5 = 'select (&NSUIMtrlMSL5View.['+element5+']);';
        let queryMSL5Table = cellsetModule.createCellSet(queryModule.select(queryMSL5)); 
        let ffLev5 = queryMSL5Table.row(0).cell(queryMSL5Table.memberColumnIndex("Item Material","MSL5")).Name;
        let ffLev5DN = queryMSL5Table.row(0).cell(queryMSL5Table.memberColumnIndex("Item Material","MSL5")).DisplayName;
        let ffLev5DA = queryMSL5Table.row(0).cell(queryMSL5Table.memberColumnIndex("Item Material","MSL5")).DisplayAlias;   
        comboList.push({Name : ffLev5, DisplayName : ffLev5DA });
        vdCommon.debug("ComboList MSL5: "+ JSON.stringify(comboList));
        return comboList;
    };

    return {
        fn_MSL1 : fn_MSL1,
        fn_MSL2 : fn_MSL2,
        fn_MSL3 : fn_MSL3,
        fn_MSL4 : fn_MSL4,
        fn_MSL5 : fn_MSL5,
        fn_materialCode : fn_materialCode,
        fn_plant : fn_plant,
        fn_vendor : fn_vendor,
        fn_Add : fn_Add,
        fn_delete : fn_delete
    };
});