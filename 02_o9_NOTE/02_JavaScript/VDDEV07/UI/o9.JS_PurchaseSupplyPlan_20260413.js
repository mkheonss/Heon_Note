define('o9.JS_PurchaseSupplyPlan', ['o9/data/query', 'o9/data/cellset', 'o9.NSCM.commonLib'], function () {

    const programName = "o9.JS_PurchaseSupplyPlan ============>";
    const commonLib = require('o9.NSCM.commonLib');
    const queryModule = require('o9/data/query');
    const cellsetModule = require('o9/data/cellset');
    vdCommon = new commonLib.VdCommon(programName);

    const allCheckN = "N";
    const allCheckY = "Y";
    let dimParams = {};

    //fn_comboMake is used to return a List consisting of Name and DisplayName and including "All" for any query,dimParams calling this.
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
        vdCommon.debug("Final List Length : "+comboList.length);
        return comboList;
    }

    //fn_VendorMake is used to return a List consisting of Name and DisplayName and including "All" for any query,dimParams for Vendor calling this.
    function fn_VendorMake(query, dimParams) {

        let selectResult = cellsetModule.createCellSet(queryModule.select(query));
        let selectResultCount = selectResult.rowCount;
        vdCommon.debug("fn_VendorMake > selectResult : " + JSON.stringify(selectResult));
        vdCommon.debug("fn_VendorMake > selectResultCount : " + selectResultCount);

        let comboList = [];
        let validHashMap = new Map();
        let allCheck = dimParams.allCheck;

        if (allCheck === "Y") {
            comboList.push({ Name: "All", DisplayName: "All" });
        }

        for (let i = 0; i < selectResultCount; i++) {
            const comboData = selectResult.row(i).cell(selectResult.memberColumnIndex(dimParams.levelKey, dimParams.levelValue)).Name;
            const comboName = selectResult.row(i).cell(selectResult.measureColumnIndex("Vendor Mtrl_GT Name"));
//            vdCommon.debug("fn_comboMake > selectResult>memberColumnIndex : " + comboData);

            if (!validHashMap.has(comboData)) {
                comboList.push({ Name: comboData, DisplayName: comboName });
                validHashMap.set(comboData, comboName);
            }
        }
        return comboList;
    }

    //fn_plant is used to return a List consisting of Name and DisplayName and including "All" for any query,dimParams for Plant calling this.
    var fn_plant = function(o9Params){

        vdUtil = new commonLib.VdUtil();

        vdCommon.setLogLevel("Debug");

        vdCommon.printParams(o9Params);
        let parsedParams = JSON.parse(o9Params);

        let comboPlantList = [];
        let validPlantHashMap = new Map();

        let query = `
                    select (&NSUISubLocationMFMtrlView);
        `;
        vdCommon.debug("GetToSiteAllSelectList > select query : " + query);
        let selectPlantResult = cellsetModule.createCellSet(queryModule.select(query));
        let selectPlantResultCount = selectPlantResult.rowCount;
        vdCommon.debug("Plant Row Count : "+ selectPlantResultCount);
        
        var fList = {Name : "All", DisplayName : "All"};

        for (let i = 0; i < selectPlantResultCount; i++) {
            const comboData = selectPlantResult.row(i).cell(selectPlantResult.memberColumnIndex("Sub Location", "Sub Location")).Name;

            if (!validPlantHashMap.has(comboData)) {
                comboPlantList.push({ Name: comboData, DisplayName: comboData });
                validPlantHashMap.set(comboData, comboData);
            }
        }
        comboPlantList.unshift(fList);
        return comboPlantList;
    };

    //fn_materialCode is used to return a List consisting of Name and DisplayName and including "All" for any query,dimParams for Material Code depending on Lv3 calling this.
    var fn_materialCode = function(o9Params){

        vdUtil = new commonLib.VdUtil();

        vdCommon.setLogLevel("Debug");

        vdCommon.printParams(o9Params);
        let parsedParams = JSON.parse(o9Params);

        var Lev5 = parsedParams.Lev5;
        
        dimParams.levelKey = "Item Material";
        dimParams.levelValue = "Item Material";
        dimParams.allCheck = allCheckY;

    
        // let query = `select ([Item Material].[Item Material]) on row where {[Item Material].[MSL3].filter(#.Name =="${Lev3}")};`;
        let query = `Select ( [Item Material]. [Item Material]. filter(#. [Item Material$InActive]!=True)*[Item Material].[MSL5].filter(#.Name =="${Lev5}") ) on row where {&CWVUI,Measure.[Item Mtrl Site Asn_Cur Status] in {"ACTIVE","PLANNED"}  };`;

        vdCommon.debug("fn_materialCode > select query : " + query);
        let comboList = fn_comboMake(query, dimParams);

        RuleOutputToUI={comboList};
        vdCommon.programEnd();
        vdCommon.debug("fn_comboMake > ComboList Materail Code : " + JSON.stringify(comboList));
        return comboList;
    };

    //fn_vendor is used to call the fn_VendrMake based on conditions of Material Code and Query.
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
        if(MaterialCode=="All")
        {
            let query = 'Select ( &CWVUI *[Global Top].[GT Code].filter(#.Name startswith "G") ) on row, ({Measure.[Vendor Mtrl_GT Name]}) on column;';

            vdCommon.debug("GetToSiteAllSelectList > select query : " + query);
    
            let comboList = fn_VendorMake(query, dimParams);
            RuleOutputToUI={comboList};
            vdCommon.programEnd();
            vdCommon.debug("fn_comboMake > ComboList Vendor : " + JSON.stringify(comboList));
            return comboList; 
        }
        else
        {
            let query = 'Select ( &CWVUI * [Item Material].[Item Material].['+MaterialCode+'] * [Global Top].[GT Code].filter(#.Name startswith "G")  ) on row, ({Measure.[Vendor Mtrl_GT Name]}) on column;';

            vdCommon.debug("GetToSiteAllSelectList > select query : " + query);

            let comboList = fn_VendorMake(query, dimParams);
            RuleOutputToUI={comboList};
            vdCommon.programEnd();
            vdCommon.debug("fn_comboMake > ComboList Vendor : " + JSON.stringify(comboList));
            return comboList;
        }
    };

    //fn_AddException is the function that is called when Action Button is submitteed and Adds a row to bottom report depending on the values given in Action Button. Every time a new row is inserted sequence is incresed by 1.
    var fn_AddException = function(o9Params){

        vdUtil = new commonLib.VdUtil();

        vdCommon.setLogLevel("Debug");

        vdCommon.printParams(o9Params);
        let parsedParams = JSON.parse(o9Params);
        var Lv5 = parsedParams.Lev5;
        var ABSource = parsedParams.Source;
        var ABCMI = parsedParams.CMI;
        var MaterialCode = parsedParams.MaterialCode; //All
        var Vendor = parsedParams.Vendor;
        var Plant = parsedParams.Plant;

        // var ABMaterialCode = '"'+parsedParams.MaterialCode+'"'; // "All"
        // var ABPlant = '"'+parsedParams.Plant+'"';
        // // var ABPlant = '"'+ffplant+'"';
        // var ABVendor = '"'+parsedParams.Vendor+'"';

        vdCommon.debug("Material : " + MaterialCode);
        vdCommon.debug("Vendor : " + Vendor);
        vdCommon.debug("Plant : " + Plant);

        if(MaterialCode=="All" && Vendor=="All" && Plant=="All")
        {
            RuleOutputToUI = {
                Status: 'Error',
                Message: 'Please select at least one field from Material Code, Vendor(HQ), and Plant'
            };
        }
        // else
        // {
        //     var IncSeq = 0;
        //     var seq = [];
        //     let ExistRowCounter = 'Select ([Version].[Version Name].[CWV_MP] * [Sequence].[Sequence] * [Item Material].[MSL5] ) on row, ({Measure.[Supply Plan Source Map Ecp_CMI Flag], Measure.[Supply Plan Source Map Ecp_Excel Flag], Measure.[Supply Plan Source Map Ecp_GT Code], Measure.[Supply Plan Source Map Ecp_GT Name], Measure.[Supply Plan Source Map Ecp_Global RTF Flag], Measure.[Supply Plan Source Map Ecp_Mtrl Code], Measure.[Supply Plan Source Map Ecp_Open PO Flag], Measure.[Supply Plan Source Map Ecp_Plant], Measure.[Supply Plan Source Map Ecp_RTF Flag], Measure.[Supply Plan Source Map Ecp_RTP Flag], Measure.[Supply Plan Source Map Ecp_Source], Measure.[Supply Plan Source Map Ecp_UI Alloc], Measure.[Supply Plan Source Map Ecp_Update Time], Measure.[Supply Plan Source Map Ecp_Updated By]}) on column;';
        //     let checkResultCounter = cellsetModule.createCellSet(queryModule.select(ExistRowCounter));
        //     let RowCounter = checkResultCounter.rowCount;
        //     for(let i=0;i<RowCounter;i++)
        //     {
        //         var sequenceCompare = checkResultCounter.row(i).cell(checkResultCounter.memberColumnIndex("Sequence","Sequence")).Name;
        //         vdCommon.debug("Sequence Printer :: "+sequenceCompare);
        //         if(!seq.includes(sequenceCompare))
        //         {
        //             seq.push(sequenceCompare);
        //         }
        //     }
        //     vdCommon.debug("RowCounter ::: "+RowCounter);
        //     seq.forEach((num) => {
        //             if (num != null && num !== "") {
        //             const parsedNum = parseInt(num);
        //             if (parsedNum > IncSeq) {
        //             IncSeq = parsedNum;
        //             }
        //             }
        //         });
        //     IncSeq = IncSeq+1;
        //     vdCommon.debug("Highest Sequence Number ::::" + IncSeq);

        //             let finalquery = 'cartesian scope: ([Version].[Version Name].[CWV_MP] * [Sequence].[Sequence].['+IncSeq+'] * [Item Material].[MSL5].['+Lv5+'] ); Measure.[Supply Plan Source Map Ecp_CMI Flag] = '+ABCMI+'; Measure.[Supply Plan Source Map Ecp_GT Name] = '+ABVendor+'; Measure.[Supply Plan Source Map Ecp_Mtrl Code] ='+ABMaterialCode+' ; Measure.[Supply Plan Source Map Ecp_Plant] = '+ABPlant+'; Measure.[Supply Plan Source Map Ecp_Source] = '+ABSource+'; end scope;';
        //             vdCommon.debug("Pause : "+finalquery);
        //             queryModule.update(finalquery);
        // }
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

            let createQuery = '';1

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

    //fn_LevelMake is used to return the query consisting of Name and DisplayName of the dimParams passed to it
    function fn_LevelMake(query, dimParams) {

        let selectResult = cellsetModule.createCellSet(queryModule.select(query));
        let selectResultCount = selectResult.rowCount;
        vdCommon.debug("fn_LevelMake > selectResult : " + JSON.stringify(selectResult));
        vdCommon.debug("fn_LevelMake > selectResultCount : " + selectResultCount);

        let comboList = [];
        let validHashMap = new Map();
        let allCheck = dimParams.allCheck;

        for (let i = 0; i < selectResultCount; i++) {
            const comboData = selectResult.row(i).cell(selectResult.memberColumnIndex(dimParams.levelKey, dimParams.levelValue)).Name;
            const comboName = selectResult.row(i).cell(selectResult.memberColumnIndex(dimParams.levelKey, dimParams.levelValue)).DisplayName;
            const comboDA = selectResult.row(i).cell(selectResult.memberColumnIndex(dimParams.levelKey, dimParams.levelValue)).DisplayAlias;
//            vdCommon.debug("fn_comboMake > selectResult>memberColumnIndex : " + comboData);

            if (!validHashMap.has(comboData)) {
                comboList.push({ Name: comboData, DisplayName: comboDA });
                validHashMap.set(comboData, comboDA);
            }
        }
        return comboList;
    }

    //fn_MSL1 is used to call and return comboList in such a way that selected row element is shown first
    var fn_MSL1 = function(o9Params){

        vdUtil = new commonLib.VdUtil();

        vdCommon.setLogLevel("Debug");

        vdCommon.printParams(o9Params);
        let parsedParams = JSON.parse(o9Params);
        var Lev1 = parsedParams.Lev1;
        var TupleList = parsedParams.TupleList;

        var element1 = TupleList[0].MSL1.Value;

        vdCommon.debug(" Found Something : "+element1);

        let query ='select (&NSUIMtrlMSL1View) on row include memberproperties {[Item Material].[MSL1], [MSL1 Sorting Order]} ORDERBY [Item Material].[MSL1].[MSL1 Sorting Order] asc;';
        // vdCommon.debug("GetToSiteAllSelectList > select query : " + query);
        dimParams.levelKey = "Item Material";
        dimParams.levelValue = "MSL1";
        dimParams.allCheck = allCheckY;
        let comboList = fn_LevelMake(query, dimParams);
        RuleOutputToUI={comboList};
        // vdCommon.programEnd();
         vdCommon.debug("fn_LevelMake > ComboList Plant : " + JSON.stringify(comboList));
        //  vdCommon.debug("Pause Please : "+Value1);

        let queryMSL1 = 'select (&NSUIMtrlMSL1View.['+element1+']);';
        let queryMSL1Table = cellsetModule.createCellSet(queryModule.select(queryMSL1)); 
        let ffLev1 = queryMSL1Table.row(0).cell(queryMSL1Table.memberColumnIndex("Item Material","MSL1")).Name;
        let ffLev1DN = queryMSL1Table.row(0).cell(queryMSL1Table.memberColumnIndex("Item Material","MSL1")).DisplayName;
        let ffLev1DA = queryMSL1Table.row(0).cell(queryMSL1Table.memberColumnIndex("Item Material","MSL1")).DisplayAlias;   
        // comboList.push({Name : ffLev1, DisplayName : ffLev1DA });
        // vdCommon.debug("ComboList : "+ JSON.stringify(comboList));

        var fList = {Name : ffLev1, DisplayName : ffLev1DA};
        
        const isPresent = comboList.some(item=>item.Name === ffLev1);
        if (isPresent)
        {
            comboList.forEach((item,index)=>{if(item.Name===ffLev1){comboList.splice(index,1)}});
            comboList.unshift(fList);
            vdCommon.debug("ComboList MSL1 : " + JSON.stringify(comboList));
            return comboList;
        }
        else
        {
            vdCommon.debug("ComboList MSL1 : " + JSON.stringify(comboList));
            return comboList;
        }  
    };

    //fn_MSL2 is used to call and return comboList in such a way that selected row element is shown first
    var fn_MSL2 = function(o9Params){

        vdUtil = new commonLib.VdUtil();

        vdCommon.setLogLevel("Debug");

        vdCommon.printParams(o9Params);
        let parsedParams = JSON.parse(o9Params);
        var Lev1 = parsedParams.Lev1;
        var TupleList = parsedParams.TupleList;

        var element2 = TupleList[0].MSL2.Value;

        let query ='select (&NSUIMtrlMSL1View.['+Lev1+']*&NSUIMtrlMSL2View) on row include memberproperties {[Item Material].[MSL2], [MSL2 Sorting Order]} ORDERBY [Item Material].[MSL2].[MSL2 Sorting Order] asc;';
        // vdCommon.debug("GetToSiteAllSelectList > select query : " + query);
        dimParams.levelKey = "Item Material";
        dimParams.levelValue = "MSL2";
        dimParams.allCheck = allCheckY;
        let comboList = fn_LevelMake(query, dimParams);
        RuleOutputToUI={comboList};
        // vdCommon.programEnd();
         vdCommon.debug("fn_LevelMake > ComboList Plant : " + JSON.stringify(comboList));
        //  vdCommon.debug("Pause Please : "+Value1);

        let queryMSL2 = 'select (&NSUIMtrlMSL2View.['+element2+']);';
        let queryMSL2Table = cellsetModule.createCellSet(queryModule.select(queryMSL2)); 
        let ffLev2 = queryMSL2Table.row(0).cell(queryMSL2Table.memberColumnIndex("Item Material","MSL2")).Name;
        let ffLev2DN = queryMSL2Table.row(0).cell(queryMSL2Table.memberColumnIndex("Item Material","MSL2")).DisplayName;
        let ffLev2DA = queryMSL2Table.row(0).cell(queryMSL2Table.memberColumnIndex("Item Material","MSL2")).DisplayAlias;   
        // comboList.push({Name : ffLev2, DisplayName : ffLev2DA });
        // vdCommon.debug("ComboList : "+ JSON.stringify(comboList));

        var fList = {Name : ffLev2, DisplayName : ffLev2DA};
        
        const isPresent = comboList.some(item=>item.Name === ffLev2);
        if (isPresent)
        {
            comboList.forEach((item,index)=>{if(item.Name===ffLev2){comboList.splice(index,1)}});
            comboList.unshift(fList);
            vdCommon.debug("ComboList MSL2 : " + JSON.stringify(comboList));
            return comboList;
        }
        else
        {
            vdCommon.debug("ComboList MSL2 : " + JSON.stringify(comboList));
            return comboList;
        }  
    };

    //fn_MSL3 is used to call and return comboList in such a way that selected row element is shown first
    var fn_MSL3 = function(o9Params){

        vdUtil = new commonLib.VdUtil();

        vdCommon.setLogLevel("Debug");

        vdCommon.printParams(o9Params);
        let parsedParams = JSON.parse(o9Params);
        var Lev2 = parsedParams.Lev2;
        var TupleList = parsedParams.TupleList;

        var element3 = TupleList[0].MSL3.Value;

        let query ='select (&NSUIMtrlMSL2View.['+Lev2+']*&NSUIMtrlMSL3View)  on row include memberproperties {[Item Material].[MSL3], [MSL3 Sorting Order]} ORDERBY [Item Material].[MSL3].[MSL3 Sorting Order] asc;';
        // vdCommon.debug("GetToSiteAllSelectList > select query : " + query);
        dimParams.levelKey = "Item Material";
        dimParams.levelValue = "MSL3";
        dimParams.allCheck = allCheckY;
        let comboList = fn_LevelMake(query, dimParams);
        RuleOutputToUI={comboList};
        // vdCommon.programEnd();
         vdCommon.debug("fn_LevelMake > ComboList Plant : " + JSON.stringify(comboList));
        //  vdCommon.debug("Pause Please : "+Value1);

        let queryMSL3 = 'select (&NSUIMtrlMSL3View.['+element3+']);';
        let queryMSL3Table = cellsetModule.createCellSet(queryModule.select(queryMSL3)); 
        let ffLev3 = queryMSL3Table.row(0).cell(queryMSL3Table.memberColumnIndex("Item Material","MSL3")).Name;
        let ffLev3DN = queryMSL3Table.row(0).cell(queryMSL3Table.memberColumnIndex("Item Material","MSL3")).DisplayName;
        let ffLev3DA = queryMSL3Table.row(0).cell(queryMSL3Table.memberColumnIndex("Item Material","MSL3")).DisplayAlias;

        var fList = {Name : ffLev3, DisplayName : ffLev3DA};
        
        const isPresent = comboList.some(item=>item.Name === ffLev3);
        if (isPresent)
        {
            comboList.forEach((item,index)=>{if(item.Name===ffLev3){comboList.splice(index,1)}});
            comboList.unshift(fList);
            vdCommon.debug("ComboList MSL3 : " + JSON.stringify(comboList));
            return comboList;
        }
        else
        {
            vdCommon.debug("ComboList MSL3 : " + JSON.stringify(comboList));
            return comboList;
        }  
    };

    //fn_MSL4 is used to call and return comboList in such a way that selected row element is shown first
    var fn_MSL4 = function(o9Params){

        vdUtil = new commonLib.VdUtil();

        vdCommon.setLogLevel("Debug");

        vdCommon.printParams(o9Params);
        let parsedParams = JSON.parse(o9Params);
        var Lev3 = parsedParams.Lev3;
        var TupleList = parsedParams.TupleList;

        var element4 = TupleList[0].MSL4.Value;

        let query ='select (&NSUIMtrlMSL3View.['+Lev3+']*&NSUIMtrlMSL4View) on row include memberproperties {[Item Material].[MSL4], [MSL4 Sorting Order]} ORDERBY [Item Material].[MSL4].[MSL4 Sorting Order] asc;';
        // vdCommon.debug("GetToSiteAllSelectList > select query : " + query);
        dimParams.levelKey = "Item Material";
        dimParams.levelValue = "MSL4";
        dimParams.allCheck = allCheckY;
        let comboList = fn_LevelMake(query, dimParams);
        RuleOutputToUI={comboList};
        // vdCommon.programEnd();
         vdCommon.debug("fn_LevelMake > ComboList Plant : " + JSON.stringify(comboList));
        //  vdCommon.debug("Pause Please : "+Value1);

        let queryMSL4 = 'select (&NSUIMtrlMSL4View.['+element4+']);';
        let queryMSL4Table = cellsetModule.createCellSet(queryModule.select(queryMSL4)); 
        let ffLev4 = queryMSL4Table.row(0).cell(queryMSL4Table.memberColumnIndex("Item Material","MSL4")).Name;
        let ffLev4DN = queryMSL4Table.row(0).cell(queryMSL4Table.memberColumnIndex("Item Material","MSL4")).DisplayName;
        let ffLev4DA = queryMSL4Table.row(0).cell(queryMSL4Table.memberColumnIndex("Item Material","MSL4")).DisplayAlias;

        var fList = {Name : ffLev4, DisplayName : ffLev4DA};
        
        const isPresent = comboList.some(item=>item.Name === ffLev4);
        if (isPresent)
        {
            comboList.forEach((item,index)=>{if(item.Name===ffLev4){comboList.splice(index,1)}});
            comboList.unshift(fList);
            vdCommon.debug("ComboList MSL4 : " + JSON.stringify(comboList));
            return comboList;
        }
        else
        {
            vdCommon.debug("ComboList MSL4 : " + JSON.stringify(comboList));
            return comboList;
        }  
    };

    //fn_MSL5 is used to call and return comboList in such a way that selected row element is shown first
    var fn_MSL5 = function(o9Params){

        vdUtil = new commonLib.VdUtil();

        vdCommon.setLogLevel("Debug");

        vdCommon.printParams(o9Params);
        let parsedParams = JSON.parse(o9Params);
        var Lev4 = parsedParams.Lev4;
        var TupleList = parsedParams.TupleList;

        var element5 = TupleList[0].MSL5.Value;

        let query ='select (&NSUIMtrlMSL4View.['+Lev4+']*&NSUIMtrlMSL5View) on row include memberproperties {[Item Material].[MSL5], [MSL5 Sorting Order]} ORDERBY [Item Material].[MSL5].[MSL5 Sorting Order] asc;';
        // vdCommon.debug("GetToSiteAllSelectList > select query : " + query);
        dimParams.levelKey = "Item Material";
        dimParams.levelValue = "MSL5";
        dimParams.allCheck = allCheckY;
        let comboList = fn_LevelMake(query, dimParams);
        RuleOutputToUI={comboList};
        // vdCommon.programEnd();
         vdCommon.debug("fn_LevelMake > ComboList Plant : " + JSON.stringify(comboList));
        //  vdCommon.debug("Pause Please : "+Value1);

        let queryMSL5 = 'select (&NSUIMtrlMSL5View.['+element5+']);';
        let queryMSL5Table = cellsetModule.createCellSet(queryModule.select(queryMSL5)); 
        let ffLev5 = queryMSL5Table.row(0).cell(queryMSL5Table.memberColumnIndex("Item Material","MSL5")).Name;
        let ffLev5DN = queryMSL5Table.row(0).cell(queryMSL5Table.memberColumnIndex("Item Material","MSL5")).DisplayName;
        let ffLev5DA = queryMSL5Table.row(0).cell(queryMSL5Table.memberColumnIndex("Item Material","MSL5")).DisplayAlias;

        var fList = {Name : ffLev5, DisplayName : ffLev5DA};
        
        const isPresent = comboList.some(item=>item.Name === ffLev5);
        if (isPresent)
        {
            comboList.forEach((item,index)=>{if(item.Name===ffLev5){comboList.splice(index,1)}});
            comboList.unshift(fList);
            vdCommon.debug("ComboList MSL5 : " + JSON.stringify(comboList));
            return comboList;
        }
        else
        {
            vdCommon.debug("ComboList MSL5 : " + JSON.stringify(comboList));
            return comboList;
        }  
    };

    return {
        fn_materialCode : fn_materialCode,
        fn_plant : fn_plant,
        fn_vendor : fn_vendor,
        fn_AddException : fn_AddException,
        fn_MSL1 : fn_MSL1,
        fn_MSL2 : fn_MSL2,
        fn_MSL3 : fn_MSL3,
        fn_MSL4 : fn_MSL4,
        fn_MSL5 : fn_MSL5
    };
});