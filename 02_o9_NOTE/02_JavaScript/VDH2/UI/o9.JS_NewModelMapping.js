define('o9.JS_NewModelMapping', ['o9/data/query', 'o9/data/cellset', 'o9.NSCM.commonLib'], function () {

    const programName = "o9.JS_NewModelMapping ============>";
    const commonLib = require('o9.NSCM.commonLib');
    const queryModule = require('o9/data/query');
    const cellsetModule = require('o9/data/cellset');
    vdCommon = new commonLib.VdCommon(programName);

    //Returns the Materail Code 
    var fn_materialCode = function(o9Params){

        vdUtil = new commonLib.VdUtil();

        vdCommon.setLogLevel("Debug");

        vdCommon.printParams(o9Params);
        let parsedParams = JSON.parse(o9Params);

        //variables from Action Button
        var Project = parsedParams.Project;
        var Basic = parsedParams.Basic;
        var Inch = parsedParams.Inch;
        var Model = parsedParams.Model;
        var Buyer = parsedParams.Buyer;
        var nMaterialCode = parsedParams.ItemMaterial;
        var BaseQty = parsedParams.BaseQty;
        var BomType = parsedParams.BomType;
        var SpecUser = parsedParams.Spec;

        var inBaseQty = '"'+parsedParams.BaseQty+'"';
        var inBomType = '"'+parsedParams.BomType+'"';
        var inSpecUser = '"'+parsedParams.SpecUser+'"';
        // const SpecUserWithQuotes = '"'+SpecUser+'"';

        var nProject = `"${Project}"`;
        var nBasic = `"${Basic}"`;
        var nInch = `"${Inch}"`;
        var nModel = `"${Model}"`;
        var nBuyer = `"${Buyer}"`;
        var nSpecUser = `"${SpecUser}"`;
        var MaterialCode = `${nMaterialCode}`;

        vdCommon.debug("Spec User : "+SpecUser+":::::"+inSpecUser+":::::"+nSpecUser);
        // var nSpecUser = '"SpecUser"';


//        vdCommon.debug("Project : "+Project + " Basic : "+ Basic+" Inch : "+Inch+" Material Code : "+MaterialCode+" BOM Type : "+BomType+" Spec(User) : "+SpecUser);

        // Query to fetch only the table for 1 measure.
        let table = 'Select (&CWVUI* [Item].[Item] * [Project].[Project] * [Item Material].[Item Material] * [Rule].[Rule No] * [Inch].[Inch] * [Buyer Group].[Buyer Group] * [Basic Name].[Basic Name] ) on row, ({Measure.[New Model Map_BOM Type], Measure.[New Model Map_Base Qty], Measure.[New Model Map_Created By], Measure.[New Model Map_Creation Time], Measure.[New Model Map_HQ Dev Purchaser], Measure.[New Model Map_HQ Purchaser], Measure.[New Model Map_Update Time], Measure.[New Model Map_Updated By], Measure.[New Model Map_User Spec]}) on column;';

        //Storing table in variable tableresult
        let tableresult = cellsetModule.createCellSet(queryModule.select(table));

        //Count row of the table
        let tablerow = tableresult.rowCount;

//        vdCommon.debug("row Count : "+tablerow);
        var ruleno = 0;
        var ruleno1 = 0;
        var rule = [];
        for(let i=0;i<tablerow;i++)
        {
            ruleno1 = tableresult.row(i).cell(tableresult.memberColumnIndex("Rule","Rule No")).Name;
            if(!rule.includes(ruleno1))
            {
                rule.push(ruleno1);
                vdCommon.debug("point !!!! : "+ ruleno1);
            }
        }
        // rule.forEach((num)=>{if(num!="-") const parsedNum=parseInt(num); if(parsedNum>ruleno){ruleno=parsedNum}});
        rule.forEach((num) => {
            if (num !== "-") {
              const parsedNum = parseInt(num);
              if (parsedNum > ruleno) {
                ruleno = parsedNum;
              }
            }
          });
        vdCommon.debug("Rule No : "+ruleno);
        var intrule = parseInt(ruleno)+1;
        var strrule = intrule.toString().padStart(4,'0');
        vdCommon.debug("ruleno incremented : "+strrule);
        vdCommon.debug("Material Code : "+MaterialCode);
        vdCommon.debug("DataType of MatrlCode:"+ typeof MaterialCode)
        const myArr = MaterialCode;
        const updateMaterial = [];

        if (SpecUser==null)
        {
            nSpecUser=null;  
            // vdCommon.debug(" Pause Inside "+nSpecUser);   
        }
        vdCommon.debug(" Pause "+nSpecUser);
        // vdCommon.debug(" Pause "+Plant1);
        let updateMaterialQuery = 'cartesian scope :(&CWVUI * [Item Material].[Item Material].['+MaterialCode+']* [Rule].[Rule No].['+strrule+'] * [Item].[Item].['+Model+'] * [Project].[Project].['+Project+']* [Inch].[Inch].['+Inch+'] * [Buyer Group].[Buyer Group].['+Buyer+'] * [Basic Name].[Basic Name].['+Basic+']);Measure.[New Model Map_BOM Type]='+inBomType+';Measure.[New Model Map_Base Qty]='+inBaseQty+';Measure.[New Model Map_User Spec]='+nSpecUser+';Measure.[New Model Map_Created By] = CurrentUser().Name;Measure.[New Model Map_Creation Time]=dateadd(Now(),9,"hour");end scope;';
        vdCommon.debug("Pause Query : "+updateMaterialQuery);
        
        queryModule.update(updateMaterialQuery);

        };

    // Function to have Plant value and "All" and return
    function fn_comboMakePlant(query) {
        let selectResult = cellsetModule.createCellSet(queryModule.select(query));
        let selectResultCount = selectResult.rowCount;
        vdCommon.debug("fn_comboMake > selectResult : " + JSON.stringify(selectResult));
        vdCommon.debug("fn_comboMake > selectResultCount : " + selectResultCount);
        let comboList = [];
        let validHashMap = new Map(); 
        comboList.push({ Name: "All", DisplayName: "All" });
        for (let i = 0; i < selectResultCount; i++) {
            const comboData = selectResult.row(i).cell(selectResult.memberColumnIndex("Item","Project" )).Name;
            const comboName = selectResult.row(i).cell(selectResult.memberColumnIndex("Item","Project" )).DisplayName;
            if (!validHashMap.has(comboData)) {
                comboList.push({ Name: comboData, DisplayName: comboName });
                validHashMap.set(comboData, comboData);
            }
        }
        return comboList;     
    }

    // Function to have Basic Name value and "All" and return
    function fn_comboMakeBasic(querybasic) {

        let selectResultbasic = cellsetModule.createCellSet(queryModule.select(querybasic));
        let selectResultCountbasic = selectResultbasic.rowCount;
        vdCommon.debug("fn_comboMakeBasic > selectResult : " + JSON.stringify(selectResultbasic));
        vdCommon.debug("fn_comboMakeBasic > selectResultCount : " + selectResultCountbasic);
        let comboListbasic = [];
        let validHashMapbasic = new Map();
        comboListbasic.push({ Name: "All", DisplayName: "All" });
        vdCommon.debug("BASIC : "+querybasic);
        for (let i = 0; i < selectResultCountbasic; i++) {
            const comboDatabasic = selectResultbasic.row(i).cell(selectResultbasic.memberColumnIndex("Item","Basic Name" )).Name;
            const comboNamebasic = selectResultbasic.row(i).cell(selectResultbasic.memberColumnIndex("Item","Basic Name" )).DisplayName;

            if (!validHashMapbasic.has(comboDatabasic)) {
                comboListbasic.push({ Name: comboDatabasic, DisplayName: comboNamebasic });
                validHashMapbasic.set(comboDatabasic, comboDatabasic);
            }
        }
         return comboListbasic;
    }
     
    // Function to have Inch value and "All" and return
    function fn_comboMakeInch(queryinch) {
        let selectResultinch = cellsetModule.createCellSet(queryModule.select(queryinch));
        let selectResultCountinch = selectResultinch.rowCount;
        vdCommon.debug("fn_comboMakeInch > selectResult : " + JSON.stringify(selectResultinch));
        vdCommon.debug("fn_comboMakeInch > selectResultCount : " + selectResultCountinch);
        let comboListinch = [];
        let validHashMapinch = new Map(); 
        comboListinch.push({ Name: "All", DisplayName: "All" });
        for (let i = 0; i < selectResultCountinch; i++) {
            const comboDatainch = selectResultinch.row(i).cell(selectResultinch.memberColumnIndex("Item","Inch" )).Name;
            const comboNameinch = selectResultinch.row(i).cell(selectResultinch.memberColumnIndex("Item","Inch" )).DisplayName;
            if (!validHashMapinch.has(comboDatainch)) {
                comboListinch.push({ Name: comboDatainch, DisplayName: comboNameinch });
                validHashMapinch.set(comboDatainch, comboDatainch);
            }
        }
        return comboListinch;     
    }

    // Function to have Model value and "All" and return
    function fn_comboMakeModel(querymodel) {
        let selectResultmodel = cellsetModule.createCellSet(queryModule.select(querymodel));
        let selectResultCountmodel = selectResultmodel.rowCount;
        vdCommon.debug("fn_comboMakemodel > selectResult : " + JSON.stringify(selectResultmodel));
        vdCommon.debug("fn_comboMakemodel > selectResultCount : " + selectResultCountmodel);
        let comboListmodel = [];
        let validHashMapmodel = new Map(); 
        comboListmodel.push({ Name: "All", DisplayName: "All" });
        for (let i = 0; i < selectResultCountmodel; i++) {
            const comboDatamodel = selectResultmodel.row(i).cell(selectResultmodel.memberColumnIndex("Item","Item" )).Name;
            const comboNamemodel = selectResultmodel.row(i).cell(selectResultmodel.memberColumnIndex("Item","Item" )).DisplayName;
            if (!validHashMapmodel.has(comboDatamodel)) {
                comboListmodel.push({ Name: comboDatamodel, DisplayName: comboNamemodel });
                validHashMapmodel.set(comboDatamodel, comboDatamodel);
            }
        }
        return comboListmodel;     
    }

    // Function to have Buyer value and "All" and return
    function fn_comboMakeBuyer(querybuyer) {
        
        let selectResultbuyer = cellsetModule.createCellSet(queryModule.select(querybuyer));
        let selectResultCountbuyer = selectResultbuyer.rowCount;
        vdCommon.debug("fn_comboMakeBuyer > selectResult : " + JSON.stringify(selectResultbuyer));
        vdCommon.debug("fn_comboMakeBuyer > selectResultCount : " + selectResultCountbuyer);
        
        //always will be one value of MSL3 with respect to one Item Material 
        const comboDatabuyer = selectResultbuyer.row(0).cell(selectResultbuyer.memberColumnIndex("Item Material","MSL3" )).Name;
        const comboNamebuyer = selectResultbuyer.row(0).cell(selectResultbuyer.memberColumnIndex("Item Material","MSL3" )).DisplayName;
        //Printing MSL3 value    
        vdCommon.debug("MSL3 Successful Value : "+comboDatabuyer);
        //New Query to find The Buyer Group with respect to MSL3 here also there will only one value of Measure with respect to MSL3.
        const msl3query = 'Select ([Version].[Version Name].[CWV_MP] * [Item Material].[MSL3].['+comboDatabuyer+'] ) on row, ({Measure.[Mtrl Master MSL3_Buyer Group]}) on column;';
        let msl3table = cellsetModule.createCellSet(queryModule.select(msl3query));
        let msl3tablerow = msl3table.rowCount; // not necessary to do so.
        //Measure value with respect to MSL3
        
        let comboListbuyer = [];
        let validHashMapbuyer = new Map(); 

        if(msl3tablerow == 0)
        {
            return comboListbuyer;
        }     
        else
        {
            var msl3BuyerGroup = msl3table.row(0).cell(msl3table.measureColumnIndex("Mtrl Master MSL3_Buyer Group"));

            const finalmeasure  = 'Select ([Version].[Version Name].[CWV_MP] * [Item].[Buyer] * [Category].[Category].['+msl3BuyerGroup+'] ) on row, ({Measure.[Buyer Group Mapping_Buyer Group]}) on column;';
            let finaltable = cellsetModule.createCellSet(queryModule.select(finalmeasure));
            let finaltablerow = finaltable.rowCount;

            // comboListbuyer.push({ Name: "", DisplayName: "" });
            for (let i = 0; i < finaltablerow; i++) {

                const buyerValue = finaltable.row(i).cell(finaltable.measureColumnIndex("Buyer Group Mapping_Buyer Group"));
                if (!validHashMapbuyer.has(buyerValue)) {
                    comboListbuyer.push({ Name: buyerValue, DisplayName: buyerValue });
                    validHashMapbuyer.set(buyerValue, buyerValue);
                }
            }
            return comboListbuyer;
        }
    }

    //Material Code entered by currentUser
    function fn_comboMakeMaterialC(materialquery)
    {
        let selectResultmaterial = cellsetModule.createCellSet(queryModule.select(materialquery));
        let selectResultCountmaterial = selectResultmaterial.rowCount;
        vdCommon.debug("fn_comboMakeMaterial > selectResult : " + JSON.stringify(selectResultmaterial));
        vdCommon.debug("fn_comboMakeMaterial > selectResultCount : " + selectResultCountmaterial);
        
        let comboListmaterial = [];
        let validHashMapmaterial = new Map();

        //Get CurrentUser Created Item Material.
        for(let i=0;i<selectResultCountmaterial;i++)
        {
            const materialValue = selectResultmaterial.row(i).cell(selectResultmaterial.memberColumnIndex("Item Material","Item Material" )).Name;
            comboListmaterial.push({ Name: materialValue, DisplayName: materialValue });
        }

        vdCommon.debug("Current User Material : "+ JSON.stringify(comboListmaterial));
        //Get All Item Material
        var Item = 'Select ( [Item Material]. [Item Material]. filter(#. [Item Material$InActive]!=True) ) on row where {&CWVUI,Measure.[Item Mtrl Site Asn_Cur Status] in {"ACTIVE","PLANNED"}  };';
        let selectResultmaterialC = cellsetModule.createCellSet(queryModule.select(Item));
        let selectResultCountmaterialC = selectResultmaterialC.rowCount;
        vdCommon.debug("ROW COUNT  ITEM MATERIAL : "+selectResultCountmaterialC);
        var materialC = [];
        for(let i=0;i<selectResultCountmaterialC;i++)
        {
            const materialCValue = selectResultmaterialC.row(i).cell(selectResultmaterialC.memberColumnIndex("Item Material","Item Material" )).Name;
            if (!validHashMapmaterial.has(materialCValue)) {
                materialC.push({ Name: materialCValue, DisplayName: materialCValue });
                validHashMapmaterial.set(materialCValue, materialCValue);
            }
        }
        let resultmaterial = [];

        //removing common element from MaterialC
        materialC.forEach(item => {
            let isMatch = comboListmaterial.some(comboItem => 
              comboItem.Name === item.Name && comboItem.DisplayName === item.DisplayName
            );
            if (!isMatch) {
                resultmaterial.push(item);
            }
          });
        
        var fresultmaterial = [...comboListmaterial,...resultmaterial];
        vdCommon.debug("Final Length : "+resultmaterial.length);
        return fresultmaterial;
    }

    var fn_MaterialC = function(o9Params){

        vdUtil = new commonLib.VdUtil();

        vdCommon.setLogLevel("Debug");

        // vdCommon.printParams("Material Code : "+o9Params);
        vdCommon.printParams(o9Params);
        let parsedParams = JSON.parse(o9Params);
        var materialQuery = 'Select (&CWVUI * [Item Material].[Item Material] * [Rule].[Rule No] ) on row, ({Measure.[New Model Map Rule_Buyer Group], Measure.[New Model Map Rule_Basic], Measure.[New Model Map Rule_Inch], Measure.[New Model Map Rule_Model], Measure.[New Model Map Rule_Project],     Measure.[New Model Map_BOM Type], Measure.[New Model Map_Base Qty], Measure.[New Model Map_HQ Dev Purchaser], Measure.[New Model Map_HQ Purchaser], Measure.[New Model Map_User Spec],Measure.[New Model Map_Created By]}) on column where {Measure.[New Model Map_Created By]==CurrentUser().Name} ;';
        var comboList = fn_comboMakeMaterialC(materialQuery);

        return comboList;
    };
    
    // function conatins o9 Params and cAlls Plant Function for further computation
    var fn_bomPlant = function(o9Params){

        vdUtil = new commonLib.VdUtil();

        vdCommon.setLogLevel("Debug");

        vdCommon.printParams(o9Params);
        let parsedParams = JSON.parse(o9Params);
        var value =1;
        var plantQuery = 'select ([Item].[Item Stage].[SET].relatedmembers([Project]));';
        vdCommon.debug("PLLLAllALALALNT !!!!");
        var comboList = fn_comboMakePlant(plantQuery);
        return comboList;
    };

    // function conatins o9 Params and cAlls Basic Name Function for further computation
    var fn_bomBasicName = function(o9Params){

        vdUtil = new commonLib.VdUtil();

        vdCommon.setLogLevel("Debug");

        vdCommon.printParams(o9Params);
        let parsedParams = JSON.parse(o9Params);
        var project = parsedParams.Project;

        if (project === "All")
        {
            var basicNameQuery = 'select ([Item].[Item Stage].[SET].relatedmembers([Basic Name]));';
        }
        else
        {
            var basicNameQuery = 'select ([Item].[Project].['+project+']*[Item].[Basic Name]);';
        }

        vdCommon.debug("BASSSSSICCC ::::");
        var comboList = fn_comboMakeBasic(basicNameQuery);
        return comboList;
    };

    
    // function conatins o9 Params and cAlls Inch Function for further computation
    var fn_bomInch = function(o9Params){

        vdUtil = new commonLib.VdUtil();

        vdCommon.setLogLevel("Debug");

        vdCommon.printParams(o9Params);
        let parsedParams = JSON.parse(o9Params);
        let Basic = parsedParams.Basic;
        let project = parsedParams.Project;
        // let basic = parsedParams.Basic;

        var inchQuery ='';
        if (Basic ==="All" && project ==="All")
        {
            inchQuery = 'select ([Item].[Inch]*[Item].[Basic Name]*[Item].[Project]);';
        }
        else if(Basic ==="All" && project !="All")
        {
            inchQuery = 'select ([Item].[Inch]*[Item].[Basic Name]*[Item].[Project].['+project+']);';
        } 
        else if(Basic !="All" && project==="All")
        {
            inchQuery = 'select ([Item].[Inch]*[Item].[Basic Name].['+Basic+']*[Item].[Project]);';
        }
        else if(Basic !="All" && project !="All")
        {
            inchQuery = 'select ([Item].[Inch]*[Item].[Basic Name].['+Basic+']*[Item].[Project].['+project+']);';
        }
        
        vdCommon.debug("Inch ::::");
        var comboList = fn_comboMakeInch(inchQuery);
        return comboList;
    };

    // function conatins o9 Params and cAlls Model Function for further computation
    var fn_bomModel = function(o9Params){

        vdUtil = new commonLib.VdUtil();

        vdCommon.setLogLevel("Debug");

        vdCommon.printParams(o9Params);
        let parsedParams = JSON.parse(o9Params);
        let Inch = parsedParams.Inch;
        let Basic = parsedParams.Basic;
        let Project = parsedParams.Project;

        if(Inch ==="All" && Basic ==="All" && Project ==="All")
        {
            var modelQuery = 'select ([Item].[Item Stage].[SET].relatedmembers([Item])) limit 10000;';
        }
        else if(Inch ==="All" && Basic ==="All" && Project!="All")
        {
            var modelQuery = 'select ([Item].[Project].['+Project+']*[Item].[Item Stage].[SET].relatedmembers([Item]));';
        }
        else if(Inch ==="All" && Basic!="All" && Project!="All")
        {
            var modelQuery = 'select ([Item].[Basic Name].['+Basic+']*[Item].[Project].['+Project+']*[Item].[Item Stage].[SET].relatedmembers([Item]));';
        }
        else if (Inch !="All" && Basic!="All" && Project!="All")
        {
            var modelQuery = 'select ([Item].[Inch].['+Inch+']*[Item].[Basic Name].['+Basic+']*[Item].[Project].['+Project+']*[Item].[Item Stage].[SET].relatedmembers([Item]));';
        }
        else if (Inch ==="All" && Basic!="All" && Project ==="All")
        {
            var modelQuery = 'select ([Item].[Basic Name].['+Basic+']*[Item].[Item Stage].[SET].relatedmembers([Item]));';
        }
       
        else if (Inch !="All" && Basic ==="All" && Project !="All")
        {
            var modelQuery = 'select ([Item].[Item Stage].[SET].relatedmembers([Item])*[Item].[Inch].['+Inch+']*[Item].[Basic Name]*[Item].[Project].['+Project+']);';
        }
        else if (Inch !="All" && Basic !="All" && Project ==="All")
        {
            var modelQuery = 'select ([Item].[Item Stage].[SET].relatedmembers([Item])*[Item].[Inch].['+Inch+']*[Item].[Basic Name].['+Basic+']*[Item].[Project]);';
        }
        else if (Inch !="All" && Basic ==="All" && Project ==="All")
        {
            var modelQuery = 'select ([Item].[Item Stage].[SET].relatedmembers([Item])*[Item].[Inch].['+Inch+']*[Item].[Basic Name]*[Item].[Project]);';
        }

        
        vdCommon.debug("Model ::::");
        var comboList = fn_comboMakeModel(modelQuery);
        return comboList;
    };

    // function conatins o9 Params and cAlls Buyer Function for further computation
    var fn_bomBuyer = function(o9Params){

        vdUtil = new commonLib.VdUtil();

        vdCommon.setLogLevel("Debug");

        vdCommon.printParams(o9Params);
        let parsedParams = JSON.parse(o9Params);

        var mtrlCode = parsedParams.ItemMaterial;
        // var mtrlarray = [...mtrlCode];
        vdCommon.debug("mtrl Array : "+ mtrlCode);

        var comboList = [];
        var buyerQuery = 'select ([Item Material].[MSL3]*[Item Material].[Item Material].['+mtrlCode+']);';
       
        vdCommon.debug("Buyer Query : "+buyerQuery);
        comboList = fn_comboMakeBuyer(buyerQuery);
        
        var comboListAll = { Name: "All", DisplayName: "All" };
        comboList.unshift(comboListAll);
        return comboList;
    };

    var fn_Delete= function(o9Params){

        vdUtil = new commonLib.VdUtil();

        vdCommon.setLogLevel("Debug");

        vdCommon.printParams(o9Params);
        let parsedParams = JSON.parse(o9Params);

        var TupleList = parsedParams.TupleList;
        vdCommon.debug("List :"+TupleList);
        vdCommon.debug("List Length :"+TupleList.length);
        
        for(let i=0;i<TupleList.length;i++)
        {
            var Rule = TupleList[i].Rule.Value;
            var Material = TupleList[i].Material.Value;
            var Item = TupleList[i].Item.Value;
            var project = TupleList[i].Project.Value;
            var Inch = TupleList[i].Inch.Value;
            var Buyer = TupleList[i].BuyerGroup.Value;
            var Basic = TupleList[i].BasicName.Value;
            //Delete Top Report Rows

            var dBquery = '';

            if (Item === "All" && project === "All" && Basic === "All" && Inch === "All" && Buyer === "All") {
                // console.log("Condition 1");
                dBquery = 'delete data for model [New Model Map BOM] where {[Version].[Version Name].[CWV_MP],[Item].[Item] ,[Item Material].[Item Material].['+Material+']};';
                vdCommon.debug("Delte Query : "+dBquery);
                queryModule.update(dBquery);
            }
            else if (Item === "All" && project === "All" && Basic === "All" && Inch === "All" && Buyer != "All") {
                // console.log("Condition 2");
                var dBuyer = `"${Buyer}"`;

                var fitem = 'Select (&CWVUI * [Item].[Buyer] * [Category].[Category] ) on row, ({Measure.[Buyer Group Mapping_Asn], Measure.[Buyer Group Mapping_Buyer Group]}) on column where {Measure.[Buyer Group Mapping_Buyer Group]=='+dBuyer+'};';

                
                let buyerlistquery = cellsetModule.createCellSet(queryModule.select(fitem));
                let buyerCcount = buyerlistquery.rowCount;
                let comboListCBuyer = [];
                let validHashMapCbuyer = [];
                for(let i=0;i<buyerCcount;i++)
                {
                    const buyerCValue = buyerlistquery.row(i).cell(buyerlistquery.memberColumnIndex("Item","Buyer" )).Name;
                    if (!validHashMapCbuyer.includes(buyerCValue)) {
                        comboListCBuyer.push({ Name: buyerCValue, DisplayName: buyerCValue });
                        validHashMapCbuyer.push(buyerCValue, buyerCValue);
                    }
                }
                vdCommon.debug("Length of Buyer Group : "+comboListCBuyer.length);

                var dflag = 1;
                //query to get bottom report
                while(dflag!=0)
                {
                    var fquery = 'Select (&CWVUI * [Item].[Item]*[Item].[Buyer]*[Item].[Project] * [Item Material].[Item Material].['+Material+'] ) on row, ({Measure.[New Model Map BOM_BOM Type], Measure.[New Model Map BOM_Base Qty], Measure.[New Model Map BOM_Created By], Measure.[New Model Map BOM_Creation Time], Measure.[New Model Map BOM_HQ Dev Purchaser], Measure.[New Model Map BOM_HQ Purchaser], Measure.[New Model Map BOM_User Spec]}) on column limit 10000;';
    
                    let buyerdBuyer = cellsetModule.createCellSet(queryModule.select(fquery)); 
                    let buyerdCount = buyerdBuyer.rowCount;
                    vdCommon.debug("Length of Buyer Group Count : "+buyerdCount);
                    let comboListDBuyer = [];
                    let validItem = '';
                    for(let i=0;i<buyerdCount;i++)
                    {
                        const buyerDValue = buyerdBuyer.row(i).cell(buyerdBuyer.memberColumnIndex("Item","Buyer")).Name;
                        if (validHashMapCbuyer.includes(buyerDValue)) {
                            validItem = buyerdBuyer.row(i).cell(buyerdBuyer.memberColumnIndex("Item","Item")).Name;
                            comboListDBuyer.push({ Name: validItem, DisplayName: validItem });
                            // validHashMapDbuyer.set(buyerDValue, buyerDValue);
                        }
                    }

                    for(let i=0;i<comboListDBuyer.length;i++)
                    {
                        // let dB = `"${comboListDBuyer[i].Name}"`;
                        let dB = comboListDBuyer[i].Name;
                        dBquery = 'delete data for model [New Model Map BOM] where {[Version].[Version Name].[CWV_MP],[Item].[Item].['+dB+'] ,[Item Material].[Item Material].['+Material+']};';
                        vdCommon.debug("Delte Query : "+dBquery);
                        queryModule.update(dBquery);
                    }
                    if(buyerdCount<10000 )
                    {
                        dflag=0;
                    }
                }      
            }
            else if (Item === "All" && project === "All" && Basic === "All" && Inch !== "All" && Buyer === "All") {
                // console.log("Condition 3");
                dflag =1 ;
                while(dflag!=0){
                    var fquery = 'Select (&CWVUI * [Item].[Item]*[Item].[Buyer]*[Item].[Inch].['+Inch+']*[Item].[Basic Name] * [Item Material].[Item Material].['+Material+'] ) on row, ({Measure.[New Model Map BOM_BOM Type], Measure.[New Model Map BOM_Base Qty], Measure.[New Model Map BOM_Created By], Measure.[New Model Map BOM_Creation Time], Measure.[New Model Map BOM_HQ Dev Purchaser], Measure.[New Model Map BOM_HQ Purchaser], Measure.[New Model Map BOM_User Spec]}) on column limit 10000;';

                    let buyerlistquery = cellsetModule.createCellSet(queryModule.select(fquery));
                    let buyerCcount = buyerlistquery.rowCount;
                    let comboListCBuyer = [];
                    let validHashMapCbuyer = [];
                    for(let i=0;i<buyerCcount;i++)
                    {
                        const buyerCValue = buyerlistquery.row(i).cell(buyerlistquery.memberColumnIndex("Item","Inch" )).Name;
                        if (!validHashMapCbuyer.includes(buyerCValue)) {
                            const buyerDValue = buyerlistquery.row(i).cell(buyerlistquery.memberColumnIndex("Item","Item" )).Name;
                            comboListCBuyer.push({ Name: buyerDValue, DisplayName: buyerDValue });
                            validHashMapCbuyer.push(buyerDValue, buyerDValue);
                        }
                    }
                    for(let i=0;i<comboListCBuyer.length;i++)
                    {
                        // let dB = `"${comboListCBuyer[i].Name}"`;;
                        let dB = comboListCBuyer[i].Name;
                        dBquery = 'delete data for model [New Model Map BOM] where {[Version].[Version Name].[CWV_MP],[Item].[Item].['+dB+'] ,[Item Material].[Item Material].['+Material+']};';
                        vdCommon.debug("Delte Query : "+dBquery);
                        queryModule.update(dBquery);
                    }
                    if(buyerCcount<10000)
                    {
                        dflag=0;
                    }
                }
            }
                // vdCommon.debug("Delte Query : "+dBquery1);
            else if (Item === "All" && project === "All" && Basic === "All" && Inch != "All" && Buyer != "All") {
                // console.log("Condition 4");
                // Convert Buyer into "" format
                var dBuyer = `"${Buyer}"`;
                // Query to get table on buyer entered from Action Button
                let bquery = 'Select (&CWVUI * [Item].[Buyer] * [Category].[Category] ) on row, ({Measure.[Buyer Group Mapping_Asn], Measure.[Buyer Group Mapping_Buyer Group]}) on column where {Measure.[Buyer Group Mapping_Buyer Group]=='+dBuyer+'};';

                let comboBuyerList = [];
                let validHashMapBList = [];
                let buyerlistquery = cellsetModule.createCellSet(queryModule.select(bquery));
                let buyerCcount = buyerlistquery.rowCount;
                for(let i=0;i<buyerCcount;i++)
                {
                    const buyerCValue = buyerlistquery.row(i).cell(buyerlistquery.memberColumnIndex("Item","Buyer" )).Name;
                    if (!validHashMapBList.includes(buyerCValue)) {
                        // const buyerDValue = buyerlistquery.row(i).cell(buyerlistquery.memberColumnIndex("Item","Item" )).Name;
                        comboBuyerList.push({ Name: buyerCValue, DisplayName: buyerCValue });
                        validHashMapBList.push(buyerCValue, buyerCValue);
                    }
                }

                //Bottom query to  get the record based on buyer and inch only
                dflag =1 ;
                while(dflag!=0){
                    var fquery = 'Select (&CWVUI * [Item].[Item]*[Item].[Buyer]*[Item].[Inch].['+Inch+']*[Item].[Basic Name] * [Item Material].[Item Material].['+Material+'] ) on row, ({Measure.[New Model Map BOM_BOM Type], Measure.[New Model Map BOM_Base Qty], Measure.[New Model Map BOM_Created By], Measure.[New Model Map BOM_Creation Time], Measure.[New Model Map BOM_HQ Dev Purchaser], Measure.[New Model Map BOM_HQ Purchaser], Measure.[New Model Map BOM_User Spec]}) on column limit 10000;';

                    let comboDBuyerList = [];
                    let validHashMapDBList = [];
                    let buyerDlistquery = cellsetModule.createCellSet(queryModule.select(fquery));
                    let buyerDCcount = buyerDlistquery.rowCount;
                    for(let i=0;i<buyerDCcount;i++)
                    {
                        const buyerDValue = buyerDlistquery.row(i).cell(buyerDlistquery.memberColumnIndex("Item","Buyer" )).Name;
                        if (validHashMapBList.includes(buyerDValue)) {
                            const buyerfDValue = buyerDlistquery.row(i).cell(buyerDlistquery.memberColumnIndex("Item","Item" )).Name;
                            comboDBuyerList.push({ Name: buyerfDValue, DisplayName: buyerfDValue });
                            validHashMapDBList.push(buyerDValue, buyerDValue);
                        }
                    }
                    for(let i=0;i<comboDBuyerList.length;i++)
                    {
                        // let dB = `"${comboDBuyerList[i].Name}"`;
                        let dB = comboDBuyerList[i].Name;
                        dBquery = 'delete data for model [New Model Map BOM] where {[Version].[Version Name].[CWV_MP],[Item].[Item].['+dB+'] ,[Item Material].[Item Material].['+Material+']};';
                        vdCommon.debug("Delte Query : "+dBquery);
                        queryModule.update(dBquery);
                    }
                    if(buyerDCcount<10000)
                    {
                        dflag=0;
                    }
                }
                // vdCommon.debug("Delte Query : "+dBquery1);
            }
            
            else if (Item === "All" && project === "All" && Basic != "All" && Inch === "All" && Buyer === "All") {
                // console.log("Condition 5");
                
                dflag =1 ;
                while(dflag!=0){
                    var fquery = 'Select (&CWVUI * [Item].[Item]*[Item].[Buyer]*[Item].[Inch]*[Item].[Basic Name].['+Basic+'] * [Item Material].[Item Material].['+Material+'] ) on row, ({Measure.[New Model Map BOM_BOM Type], Measure.[New Model Map BOM_Base Qty], Measure.[New Model Map BOM_Created By], Measure.[New Model Map BOM_Creation Time], Measure.[New Model Map BOM_HQ Dev Purchaser], Measure.[New Model Map BOM_HQ Purchaser], Measure.[New Model Map BOM_User Spec]}) on column limit 10000;';

                    let comboDBuyerList = [];
                    // let validHashMapDBList = [];
                    let buyerDlistquery = cellsetModule.createCellSet(queryModule.select(fquery));
                    let buyerDCcount = buyerDlistquery.rowCount;
                    for(let i=0;i<buyerDCcount;i++)
                    {
                        const buyerfDValue = buyerDlistquery.row(i).cell(buyerDlistquery.memberColumnIndex("Item","Item" )).Name;
                        comboDBuyerList.push({ Name: buyerfDValue, DisplayName: buyerfDValue });
                        // validHashMapDBList.set(buyerDValue, buyerDValue);        
                    }
                    for(let i=0;i<comboDBuyerList.length;i++)
                    {
                        // let dB = `"${comboDBuyerList[i].Name}"`;;
                        let dB = comboDBuyerList[i].Name;
                        dBquery = 'delete data for model [New Model Map BOM] where {[Version].[Version Name].[CWV_MP],[Item].[Item].['+dB+'] ,[Item Material].[Item Material].['+Material+']};';
                        vdCommon.debug("Delte Query : "+dBquery);
                        queryModule.update(dBquery);
                    }
                    if(buyerDCcount<10000)
                    {
                        dflag=0;
                    } 
                }   
            }

            else if (Item === "All" && project === "All" && Basic != "All" && Inch === "All" && Buyer != "All") {
                // console.log("Condition 6");
                // Convert Buyer into "" format
                var dBuyer = `"${Buyer}"`;
                // Query to get table on buyer entered from Action Button
                let bquery = 'Select (&CWVUI * [Item].[Buyer] * [Category].[Category] ) on row, ({Measure.[Buyer Group Mapping_Asn], Measure.[Buyer Group Mapping_Buyer Group]}) on column where {Measure.[Buyer Group Mapping_Buyer Group]=='+dBuyer+'};';

                let comboBuyerList = [];
                let validHashMapBList = [];
                let buyerlistquery = cellsetModule.createCellSet(queryModule.select(bquery));
                let buyerCcount = buyerlistquery.rowCount;
                for(let i=0;i<buyerCcount;i++)
                {
                    const buyerCValue = buyerlistquery.row(i).cell(buyerlistquery.memberColumnIndex("Item","Buyer" )).Name;
                    if (!validHashMapBList.includes(buyerCValue)) {
                        // const buyerDValue = buyerlistquery.row(i).cell(buyerlistquery.memberColumnIndex("Item","Item" )).Name;
                        comboBuyerList.push({ Name: buyerCValue, DisplayName: buyerCValue });
                        validHashMapBList.push(buyerCValue, buyerCValue);
                    }
                }

                dflag =1 ;
                while(dflag!=0){
                    var fquery = 'Select (&CWVUI * [Item].[Item]*[Item].[Buyer]*[Item].[Inch]*[Item].[Basic Name].['+Basic+'] * [Item Material].[Item Material].['+Material+'] ) on row, ({Measure.[New Model Map BOM_BOM Type], Measure.[New Model Map BOM_Base Qty], Measure.[New Model Map BOM_Created By], Measure.[New Model Map BOM_Creation Time], Measure.[New Model Map BOM_HQ Dev Purchaser], Measure.[New Model Map BOM_HQ Purchaser], Measure.[New Model Map BOM_User Spec]}) on column limit 10000;';

                    let comboDBuyerList = [];
                    let validHashMapDBList = [];
                    let buyerDlistquery = cellsetModule.createCellSet(queryModule.select(fquery));
                    let buyerDCcount = buyerDlistquery.rowCount;
                    for(let i=0;i<buyerDCcount;i++)
                    {
                        const buyerDValue = buyerDlistquery.row(i).cell(buyerDlistquery.memberColumnIndex("Item","Buyer" )).Name;
                        if (validHashMapBList.includes(buyerDValue)) {
                            const buyerfDValue = buyerDlistquery.row(i).cell(buyerDlistquery.memberColumnIndex("Item","Item" )).Name;
                            comboDBuyerList.push({ Name: buyerfDValue, DisplayName: buyerfDValue });
                            validHashMapDBList.push(buyerDValue, buyerDValue);
                        }
                    }
                    for(let i=0;i<comboDBuyerList.length;i++)
                    {
                        // let dB = `"${comboDBuyerList[i].Name}"`;;
                        let dB = comboDBuyerList[i].Name;
                        dBquery = 'delete data for model [New Model Map BOM] where {[Version].[Version Name].[CWV_MP],[Item].[Item].['+dB+'] ,[Item Material].[Item Material].['+Material+']};';
                        vdCommon.debug("Delte Query : "+dBquery);
                        queryModule.update(dBquery);
                    }
                    if(buyerDCcount<10000)
                    {
                        dflag=0;
                    }
                }
            }
            else if (Item === "All" && project === "All" && Basic != "All" && Inch != "All" && Buyer === "All") {
                // console.log("Condition 7");
                dflag =1 ;
                while(dflag!=0){
                    var fquery = 'Select (&CWVUI * [Item].[Item]*[Item].[Buyer]*[Item].[Inch].['+Inch+']*[Item].[Basic Name].['+Basic+'] * [Item Material].[Item Material].['+Material+'] ) on row, ({Measure.[New Model Map BOM_BOM Type], Measure.[New Model Map BOM_Base Qty], Measure.[New Model Map BOM_Created By], Measure.[New Model Map BOM_Creation Time], Measure.[New Model Map BOM_HQ Dev Purchaser], Measure.[New Model Map BOM_HQ Purchaser], Measure.[New Model Map BOM_User Spec]}) on column limit 10000;';

                    let comboDBuyerList = [];
                    // let validHashMapDBList = [];
                    let buyerDlistquery = cellsetModule.createCellSet(queryModule.select(fquery));
                    let buyerDCcount = buyerDlistquery.rowCount;
                    for(let i=0;i<buyerDCcount;i++)
                    {
                        const buyerfDValue = buyerDlistquery.row(i).cell(buyerDlistquery.memberColumnIndex("Item","Item" )).Name;
                        comboDBuyerList.push({ Name: buyerfDValue, DisplayName: buyerfDValue });
                        // validHashMapDBList.set(buyerDValue, buyerDValue);        
                    }
                    for(let i=0;i<comboDBuyerList.length;i++)
                    {
                        // let dB = `"${comboDBuyerList[i].Name}"`;;
                        let dB = comboDBuyerList[i].Name;
                        dBquery = 'delete data for model [New Model Map BOM] where {[Version].[Version Name].[CWV_MP],[Item].[Item].['+dB+'] ,[Item Material].[Item Material].['+Material+']};';
                        vdCommon.debug("Delte Query : "+dBquery);
                        queryModule.update(dBquery);
                    }
                    if(buyerDCcount<10000)
                    {
                        dflag=0;
                    }
                }
                
            }
            else if (Item === "All" && project === "All" && Basic != "All" && Inch != "All" && Buyer != "All") {
                // console.log("Condition 8");
                // Convert Buyer into "" format
                var dBuyer = `"${Buyer}"`;
                // Query to get table on buyer entered from Action Button
                let bquery = 'Select (&CWVUI * [Item].[Buyer] * [Category].[Category] ) on row, ({Measure.[Buyer Group Mapping_Asn], Measure.[Buyer Group Mapping_Buyer Group]}) on column where {Measure.[Buyer Group Mapping_Buyer Group]=='+dBuyer+'};';

                let comboBuyerList = [];
                let validHashMapBList = [];
                let buyerlistquery = cellsetModule.createCellSet(queryModule.select(bquery));
                let buyerCcount = buyerlistquery.rowCount;
                for(let i=0;i<buyerCcount;i++)
                {
                    const buyerCValue = buyerlistquery.row(i).cell(buyerlistquery.memberColumnIndex("Item","Buyer" )).Name;
                    if (!validHashMapBList.includes(buyerCValue)) {
                        // const buyerDValue = buyerlistquery.row(i).cell(buyerlistquery.memberColumnIndex("Item","Item" )).Name;
                        comboBuyerList.push({ Name: buyerCValue, DisplayName: buyerCValue });
                        validHashMapBList.push(buyerCValue, buyerCValue);
                    }
                }

                dflag =1 ;
                while(dflag!=0){
                    var fquery = 'Select (&CWVUI * [Item].[Item]*[Item].[Buyer]*[Item].[Inch].['+Inch+']*[Item].[Basic Name].['+Basic+'] * [Item Material].[Item Material].['+Material+'] ) on row, ({Measure.[New Model Map BOM_BOM Type], Measure.[New Model Map BOM_Base Qty], Measure.[New Model Map BOM_Created By], Measure.[New Model Map BOM_Creation Time], Measure.[New Model Map BOM_HQ Dev Purchaser], Measure.[New Model Map BOM_HQ Purchaser], Measure.[New Model Map BOM_User Spec]}) on column limit 10000;';

                    let comboDBuyerList = [];
                    let validHashMapDBList = [];
                    let buyerDlistquery = cellsetModule.createCellSet(queryModule.select(fquery));
                    let buyerDCcount = buyerDlistquery.rowCount;
                    for(let i=0;i<buyerDCcount;i++)
                    {
                        const buyerDValue = buyerDlistquery.row(i).cell(buyerDlistquery.memberColumnIndex("Item","Buyer" )).Name;
                        if (validHashMapBList.includes(buyerDValue)) {
                            const buyerfDValue = buyerDlistquery.row(i).cell(buyerDlistquery.memberColumnIndex("Item","Item" )).Name;
                            comboDBuyerList.push({ Name: buyerfDValue, DisplayName: buyerfDValue });
                            validHashMapDBList.push(buyerDValue, buyerDValue);
                        }
                    }
                    for(let i=0;i<comboDBuyerList.length;i++)
                    {
                        // let dB = `"${comboDBuyerList[i].Name}"`;;
                        let dB = comboDBuyerList[i].Name;
                        dBquery = 'delete data for model [New Model Map BOM] where {[Version].[Version Name].[CWV_MP],[Item].[Item].['+dB+'] ,[Item Material].[Item Material].['+Material+']};';
                        vdCommon.debug("Delte Query : "+dBquery);
                        queryModule.update(dBquery);
                    }
                    if(buyerDCcount<10000)
                    {
                        dflag=0;
                    }
                }
            }
            else if (Item === "All" && project != "All" && Basic === "All" && Inch === "All" && Buyer === "All") {
                // console.log("Condition 9");
                
                dflag =1 ;
                while(dflag!=0){
                    var fquery = 'Select (&CWVUI * [Item].[Item]*[Item].[Buyer]*[Item].[Project].['+project+']*[Item].[Inch]*[Item].[Basic Name] * [Item Material].[Item Material].['+Material+'] ) on row, ({Measure.[New Model Map BOM_BOM Type], Measure.[New Model Map BOM_Base Qty], Measure.[New Model Map BOM_Created By], Measure.[New Model Map BOM_Creation Time], Measure.[New Model Map BOM_HQ Dev Purchaser], Measure.[New Model Map BOM_HQ Purchaser], Measure.[New Model Map BOM_User Spec]}) on column limit 10000;';

                    let comboDBuyerList = [];
                    // let validHashMapDBList = [];
                    let buyerDlistquery = cellsetModule.createCellSet(queryModule.select(fquery));
                    let buyerDCcount = buyerDlistquery.rowCount;
                    for(let i=0;i<buyerDCcount;i++)
                    {
                        const buyerfDValue = buyerDlistquery.row(i).cell(buyerDlistquery.memberColumnIndex("Item","Item" )).Name;
                        comboDBuyerList.push({ Name: buyerfDValue, DisplayName: buyerfDValue });
                        // validHashMapDBList.set(buyerDValue, buyerDValue);        
                    }
                    for(let i=0;i<comboDBuyerList.length;i++)
                    {
                        // let dB = `"${comboDBuyerList[i].Name}"`;;
                        let dB = comboDBuyerList[i].Name;
                        dBquery = 'delete data for model [New Model Map BOM] where {[Version].[Version Name].[CWV_MP],[Item].[Item].['+dB+'] ,[Item Material].[Item Material].['+Material+']};';
                        vdCommon.debug("Delte Query : "+dBquery);
                        queryModule.update(dBquery);
                    }
                    if(buyerDCcount<10000)
                    {
                        dflag=0;
                    }
                }
            }
            else if (Item === "All" && project != "All" && Basic === "All" && Inch === "All" && Buyer != "All") {
                // console.log("Condition 10");
                // Convert Buyer into "" format
                var dBuyer = `"${Buyer}"`;
                // Query to get table on buyer entered from Action Button
                let bquery = 'Select (&CWVUI * [Item].[Buyer] * [Category].[Category] ) on row, ({Measure.[Buyer Group Mapping_Asn], Measure.[Buyer Group Mapping_Buyer Group]}) on column where {Measure.[Buyer Group Mapping_Buyer Group]=='+dBuyer+'};';

                let comboBuyerList = [];
                let validHashMapBList = [];
                let buyerlistquery = cellsetModule.createCellSet(queryModule.select(bquery));
                let buyerCcount = buyerlistquery.rowCount;
                for(let i=0;i<buyerCcount;i++)
                {
                    const buyerCValue = buyerlistquery.row(i).cell(buyerlistquery.memberColumnIndex("Item","Buyer" )).Name;
                    if (!validHashMapBList.includes(buyerCValue)) {
                        // const buyerDValue = buyerlistquery.row(i).cell(buyerlistquery.memberColumnIndex("Item","Item" )).Name;
                        comboBuyerList.push({ Name: buyerCValue, DisplayName: buyerCValue });
                        validHashMapBList.push(buyerCValue, buyerCValue);
                    }
                }

                dflag =1 ;
                while(dflag!=0){
                    var fquery = 'Select (&CWVUI * [Item].[Item]*[Item].[Buyer]*[Item].[Project].['+project+']*[Item].[Inch]*[Item].[Basic Name] * [Item Material].[Item Material].['+Material+'] ) on row, ({Measure.[New Model Map BOM_BOM Type], Measure.[New Model Map BOM_Base Qty], Measure.[New Model Map BOM_Created By], Measure.[New Model Map BOM_Creation Time], Measure.[New Model Map BOM_HQ Dev Purchaser], Measure.[New Model Map BOM_HQ Purchaser], Measure.[New Model Map BOM_User Spec]}) on column limit 10000;';

                    let comboDBuyerList = [];
                    let validHashMapDBList = [];
                    let buyerDlistquery = cellsetModule.createCellSet(queryModule.select(fquery));
                    let buyerDCcount = buyerDlistquery.rowCount;
                    for(let i=0;i<buyerDCcount;i++)
                    {
                        const buyerDValue = buyerDlistquery.row(i).cell(buyerDlistquery.memberColumnIndex("Item","Buyer" )).Name;
                        if (validHashMapBList.includes(buyerDValue)) {
                            const buyerfDValue = buyerDlistquery.row(i).cell(buyerDlistquery.memberColumnIndex("Item","Item" )).Name;
                            comboDBuyerList.push({ Name: buyerfDValue, DisplayName: buyerfDValue });
                            validHashMapDBList.push(buyerDValue, buyerDValue);
                        }
                    }
                    for(let i=0;i<comboDBuyerList.length;i++)
                    {
                        // let dB = `"${comboDBuyerList[i].Name}"`;;
                        let dB = comboDBuyerList[i].Name;
                        dBquery = 'delete data for model [New Model Map BOM] where {[Version].[Version Name].[CWV_MP],[Item].[Item].['+dB+'] ,[Item Material].[Item Material].['+Material+']};';
                        vdCommon.debug("Delte Query : "+dBquery);
                        queryModule.update(dBquery);
                    }
                    if(buyerDCcount<10000)
                    {
                        dflag=0;
                    }
                }
            }
            else if (Item === "All" && project != "All" && Basic === "All" && Inch != "All" && Buyer === "All") {
                // console.log("Condition 11");
                dflag =1 ;
                while(dflag!=0){
                    var fquery = 'Select (&CWVUI * [Item].[Item]*[Item].[Buyer]*[Item].[Project].['+project+']*[Item].[Inch].['+Inch+']*[Item].[Basic Name] * [Item Material].[Item Material].['+Material+'] ) on row, ({Measure.[New Model Map BOM_BOM Type], Measure.[New Model Map BOM_Base Qty], Measure.[New Model Map BOM_Created By], Measure.[New Model Map BOM_Creation Time], Measure.[New Model Map BOM_HQ Dev Purchaser], Measure.[New Model Map BOM_HQ Purchaser], Measure.[New Model Map BOM_User Spec]}) on column limit 10000;';

                    let comboDBuyerList = [];
                    // let validHashMapDBList = [];
                    let buyerDlistquery = cellsetModule.createCellSet(queryModule.select(fquery));
                    let buyerDCcount = buyerDlistquery.rowCount;
                    for(let i=0;i<buyerDCcount;i++)
                    {
                        const buyerfDValue = buyerDlistquery.row(i).cell(buyerDlistquery.memberColumnIndex("Item","Item" )).Name;
                        comboDBuyerList.push({ Name: buyerfDValue, DisplayName: buyerfDValue });
                        // validHashMapDBList.set(buyerDValue, buyerDValue);        
                    }
                    for(let i=0;i<comboDBuyerList.length;i++)
                    {
                        // let dB = `"${comboDBuyerList[i].Name}"`;;
                        let dB = comboDBuyerList[i].Name;
                        dBquery = 'delete data for model [New Model Map BOM] where {[Version].[Version Name].[CWV_MP],[Item].[Item].['+dB+'] ,[Item Material].[Item Material].['+Material+']};';
                        vdCommon.debug("Delte Query : "+dBquery);
                        queryModule.update(dBquery);
                    }
                    if(buyerDCcount<10000)
                    {
                        dflag=0;
                    }
                }
                
            }
            else if (Item === "All" && project != "All" && Basic === "All" && Inch != "All" && Buyer != "All") {
                // console.log("Condition 12");
                 // Convert Buyer into "" format
                 var dBuyer = `"${Buyer}"`;
                 // Query to get table on buyer entered from Action Button
                 let bquery = 'Select (&CWVUI * [Item].[Buyer] * [Category].[Category] ) on row, ({Measure.[Buyer Group Mapping_Asn], Measure.[Buyer Group Mapping_Buyer Group]}) on column where {Measure.[Buyer Group Mapping_Buyer Group]=='+dBuyer+'};';
 
                 let comboBuyerList = [];
                 let validHashMapBList = [];
                 let buyerlistquery = cellsetModule.createCellSet(queryModule.select(bquery));
                 let buyerCcount = buyerlistquery.rowCount;
                 for(let i=0;i<buyerCcount;i++)
                 {
                     const buyerCValue = buyerlistquery.row(i).cell(buyerlistquery.memberColumnIndex("Item","Buyer" )).Name;
                     if (!validHashMapBList.includes(buyerCValue)) {
                         // const buyerDValue = buyerlistquery.row(i).cell(buyerlistquery.memberColumnIndex("Item","Item" )).Name;
                         comboBuyerList.push({ Name: buyerCValue, DisplayName: buyerCValue });
                         validHashMapBList.push(buyerCValue, buyerCValue);
                     }
                 }
 
                dflag =1 ;
                while(dflag!=0){
                    var fquery = 'Select (&CWVUI * [Item].[Item]*[Item].[Buyer]*[Item].[Project].['+project+']*[Item].[Inch].['+Inch+']*[Item].[Basic Name] * [Item Material].[Item Material].['+Material+'] ) on row, ({Measure.[New Model Map BOM_BOM Type], Measure.[New Model Map BOM_Base Qty], Measure.[New Model Map BOM_Created By], Measure.[New Model Map BOM_Creation Time], Measure.[New Model Map BOM_HQ Dev Purchaser], Measure.[New Model Map BOM_HQ Purchaser], Measure.[New Model Map BOM_User Spec]}) on column limit 10000;';
    
                    let comboDBuyerList = [];
                    let validHashMapDBList = [];
                    let buyerDlistquery = cellsetModule.createCellSet(queryModule.select(fquery));
                    let buyerDCcount = buyerDlistquery.rowCount;
                    for(let i=0;i<buyerDCcount;i++)
                    {
                        const buyerDValue = buyerDlistquery.row(i).cell(buyerDlistquery.memberColumnIndex("Item","Buyer" )).Name;
                        if (validHashMapBList.includes(buyerDValue)) {
                            const buyerfDValue = buyerDlistquery.row(i).cell(buyerDlistquery.memberColumnIndex("Item","Item" )).Name;
                            comboDBuyerList.push({ Name: buyerfDValue, DisplayName: buyerfDValue });
                            validHashMapDBList.push(buyerDValue, buyerDValue);
                        }
                    }
                    for(let i=0;i<comboDBuyerList.length;i++)
                    {
                        //  let dB = `"${comboDBuyerList[i].Name}"`;;
                        let dB = comboDBuyerList[i].Name;
                        dBquery = 'delete data for model [New Model Map BOM] where {[Version].[Version Name].[CWV_MP],[Item].[Item].['+dB+'] ,[Item Material].[Item Material].['+Material+']};';
                        vdCommon.debug("Delte Query : "+dBquery);
                        queryModule.update(dBquery);
                    }
                    if(buyerDCcount<10000)
                    {
                        dflag=0;
                    }
                }
            }
            else if (Item === "All" && project != "All" && Basic != "All" && Inch === "All" && Buyer === "All") {
                // console.log("Condition 13");
                dflag =1 ;
                while(dflag!=0){
                    var fquery = 'Select (&CWVUI * [Item].[Item]*[Item].[Buyer]*[Item].[Project].['+project+']*[Item].[Inch]*[Item].[Basic Name].['+Basic+'] * [Item Material].[Item Material].['+Material+'] ) on row, ({Measure.[New Model Map BOM_BOM Type], Measure.[New Model Map BOM_Base Qty], Measure.[New Model Map BOM_Created By], Measure.[New Model Map BOM_Creation Time], Measure.[New Model Map BOM_HQ Dev Purchaser], Measure.[New Model Map BOM_HQ Purchaser], Measure.[New Model Map BOM_User Spec]}) on column limit 10000;';

                    let comboDBuyerList = [];
                    // let validHashMapDBList = [];
                    let buyerDlistquery = cellsetModule.createCellSet(queryModule.select(fquery));
                    let buyerDCcount = buyerDlistquery.rowCount;
                    for(let i=0;i<buyerDCcount;i++)
                    {
                        const buyerfDValue = buyerDlistquery.row(i).cell(buyerDlistquery.memberColumnIndex("Item","Item" )).Name;
                        comboDBuyerList.push({ Name: buyerfDValue, DisplayName: buyerfDValue });
                        // validHashMapDBList.set(buyerDValue, buyerDValue);        
                    }
                    for(let i=0;i<comboDBuyerList.length;i++)
                    {
                        // let dB = `"${comboDBuyerList[i].Name}"`;;
                        let dB = comboDBuyerList[i].Name;
                        dBquery = 'delete data for model [New Model Map BOM] where {[Version].[Version Name].[CWV_MP],[Item].[Item].['+dB+'] ,[Item Material].[Item Material].['+Material+']};';
                        vdCommon.debug("Delte Query : "+dBquery);
                        queryModule.update(dBquery);
                    }
                    if(buyerDCcount<10000)
                    {
                        dflag=0;
                    }
                }
            }
            else if (Item === "All" && project !== "All" && Basic !== "All" && Inch === "All" && Buyer !== "All") {
                // console.log("Condition 14");
                // Convert Buyer into "" format
                var dBuyer = `"${Buyer}"`;
                // Query to get table on buyer entered from Action Button
                let bquery = 'Select (&CWVUI * [Item].[Buyer] * [Category].[Category] ) on row, ({Measure.[Buyer Group Mapping_Asn], Measure.[Buyer Group Mapping_Buyer Group]}) on column where {Measure.[Buyer Group Mapping_Buyer Group]=='+dBuyer+'};';

                let comboBuyerList = [];
                let validHashMapBList = [];
                let buyerlistquery = cellsetModule.createCellSet(queryModule.select(bquery));
                let buyerCcount = buyerlistquery.rowCount;
                for(let i=0;i<buyerCcount;i++)
                {
                    const buyerCValue = buyerlistquery.row(i).cell(buyerlistquery.memberColumnIndex("Item","Buyer" )).Name;
                    if (!validHashMapBList.includes(buyerCValue)) {
                        // const buyerDValue = buyerlistquery.row(i).cell(buyerlistquery.memberColumnIndex("Item","Item" )).Name;
                        comboBuyerList.push({ Name: buyerCValue, DisplayName: buyerCValue });
                        validHashMapBList.push(buyerCValue, buyerCValue);
                    }
                }

                dflag =1 ;
                while(dflag!=0){
                    var fquery = 'Select (&CWVUI * [Item].[Item]*[Item].[Buyer]*[Item].[Project].['+project+']*[Item].[Inch]*[Item].[Basic Name].['+Basic+'] * [Item Material].[Item Material].['+Material+'] ) on row, ({Measure.[New Model Map BOM_BOM Type], Measure.[New Model Map BOM_Base Qty], Measure.[New Model Map BOM_Created By], Measure.[New Model Map BOM_Creation Time], Measure.[New Model Map BOM_HQ Dev Purchaser], Measure.[New Model Map BOM_HQ Purchaser], Measure.[New Model Map BOM_User Spec]}) on column limit 10000;';

                    let comboDBuyerList = [];
                    let validHashMapDBList = [];
                    let buyerDlistquery = cellsetModule.createCellSet(queryModule.select(fquery));
                    let buyerDCcount = buyerDlistquery.rowCount;
                    for(let i=0;i<buyerDCcount;i++)
                    {
                        const buyerDValue = buyerDlistquery.row(i).cell(buyerDlistquery.memberColumnIndex("Item","Buyer" )).Name;
                        if (validHashMapBList.includes(buyerDValue)) {
                            const buyerfDValue = buyerDlistquery.row(i).cell(buyerDlistquery.memberColumnIndex("Item","Item" )).Name;
                            comboDBuyerList.push({ Name: buyerfDValue, DisplayName: buyerfDValue });
                            validHashMapDBList.push(buyerDValue, buyerDValue);
                        }
                    }
                    for(let i=0;i<comboDBuyerList.length;i++)
                    {
                        // let dB = `"${comboDBuyerList[i].Name}"`;;
                        let dB = comboDBuyerList[i].Name;
                        dBquery = 'delete data for model [New Model Map BOM] where {[Version].[Version Name].[CWV_MP],[Item].[Item].['+dB+'] ,[Item Material].[Item Material].['+Material+']};';
                        vdCommon.debug("Delte Query : "+dBquery);
                        queryModule.update(dBquery);
                    }
                    if(buyerDCcount<10000)
                    {
                        dflag=0;
                    }
                }
                
            }
            else if (Item === "All" && project !== "All" && Basic !== "All" && Inch !== "All" && Buyer === "All") {
                // console.log("Condition 15");
                dflag =1 ;
                while(dflag!=0){
                    var fquery = 'Select (&CWVUI * [Item].[Item]*[Item].[Buyer]*[Item].[Project].['+project+']*[Item].[Inch].['+Inch+']*[Item].[Basic Name].['+Basic+'] * [Item Material].[Item Material].['+Material+'] ) on row, ({Measure.[New Model Map BOM_BOM Type], Measure.[New Model Map BOM_Base Qty], Measure.[New Model Map BOM_Created By], Measure.[New Model Map BOM_Creation Time], Measure.[New Model Map BOM_HQ Dev Purchaser], Measure.[New Model Map BOM_HQ Purchaser], Measure.[New Model Map BOM_User Spec]}) on column limit 10000;';

                    let comboDBuyerList = [];
                    // let validHashMapDBList = [];
                    let buyerDlistquery = cellsetModule.createCellSet(queryModule.select(fquery));
                    let buyerDCcount = buyerDlistquery.rowCount;
                    for(let i=0;i<buyerDCcount;i++)
                    {
                        const buyerfDValue = buyerDlistquery.row(i).cell(buyerDlistquery.memberColumnIndex("Item","Item" )).Name;
                        comboDBuyerList.push({ Name: buyerfDValue, DisplayName: buyerfDValue });
                        // validHashMapDBList.set(buyerDValue, buyerDValue);        
                    }
                    for(let i=0;i<comboDBuyerList.length;i++)
                    {
                        // let dB = `"${comboDBuyerList[i].Name}"`;;
                        let dB = comboDBuyerList[i].Name;
                        dBquery = 'delete data for model [New Model Map BOM] where {[Version].[Version Name].[CWV_MP],[Item].[Item].['+dB+'] ,[Item Material].[Item Material].['+Material+']};';
                        vdCommon.debug("Delte Query : "+dBquery);
                        queryModule.update(dBquery);
                    }
                    if(buyerDCcount<10000)
                    {
                        dflag=0;
                    }
                }
                
            }
            else if (Item === "All" && project !== "All" && Basic !== "All" && Inch !== "All" && Buyer !== "All") {
                vdCommon.debug("Condition 16");
                // Convert Buyer into "" format
                var dBuyer = `"${Buyer}"`;
                // Query to get table on buyer entered from Action Button
                let bquery = 'Select (&CWVUI * [Item].[Buyer] * [Category].[Category] ) on row, ({Measure.[Buyer Group Mapping_Asn], Measure.[Buyer Group Mapping_Buyer Group]}) on column where {Measure.[Buyer Group Mapping_Buyer Group]=='+dBuyer+'};';

                let comboBuyerList = [];
                let validHashMapBList = [];
                let buyerlistquery = cellsetModule.createCellSet(queryModule.select(bquery));
                let buyerCcount = buyerlistquery.rowCount;
                for(let i=0;i<buyerCcount;i++)
                {
                    const buyerCValue = buyerlistquery.row(i).cell(buyerlistquery.memberColumnIndex("Item","Buyer" )).Name;
                    if (!validHashMapBList.includes(buyerCValue)) {
                        // const buyerDValue = buyerlistquery.row(i).cell(buyerlistquery.memberColumnIndex("Item","Item" )).Name;
                        comboBuyerList.push({ Name: buyerCValue, DisplayName: buyerCValue });
                        validHashMapBList.push(buyerCValue, buyerCValue);
                    }
                }

                dflag =1 ;
                while(dflag!=0){
                    var fquery = 'Select (&CWVUI * [Item].[Item]*[Item].[Buyer]*[Item].[Project].['+project+']*[Item].[Inch].['+Inch+']*[Item].[Basic Name].['+Basic+'] * [Item Material].[Item Material].['+Material+'] ) on row, ({Measure.[New Model Map BOM_BOM Type], Measure.[New Model Map BOM_Base Qty], Measure.[New Model Map BOM_Created By], Measure.[New Model Map BOM_Creation Time], Measure.[New Model Map BOM_HQ Dev Purchaser], Measure.[New Model Map BOM_HQ Purchaser], Measure.[New Model Map BOM_User Spec]}) on column limit 10000;';

                    let comboDBuyerList = [];
                    let validHashMapDBList = [];
                    let buyerDlistquery = cellsetModule.createCellSet(queryModule.select(fquery));
                    let buyerDCcount = buyerDlistquery.rowCount;
                    for(let i=0;i<buyerDCcount;i++)
                    {
                        const buyerDValue = buyerDlistquery.row(i).cell(buyerDlistquery.memberColumnIndex("Item","Buyer" )).Name;
                        if (validHashMapBList.includes(buyerDValue)) {
                            const buyerfDValue = buyerDlistquery.row(i).cell(buyerDlistquery.memberColumnIndex("Item","Item" )).Name;
                            comboDBuyerList.push({ Name: buyerfDValue, DisplayName: buyerfDValue });
                            validHashMapDBList.push(buyerDValue, buyerDValue);
                        }
                    }
                    for(let i=0;i<comboDBuyerList.length;i++)
                    {
                        // let dB = `"${comboDBuyerList[i].Name}"`;;
                        let dB = comboDBuyerList[i].Name;
                        dBquery = 'delete data for model [New Model Map BOM] where {[Version].[Version Name].[CWV_MP],[Item].[Item].['+dB+'] ,[Item Material].[Item Material].['+Material+']};';
                        vdCommon.debug("Delte Query : "+dBquery);
                        queryModule.update(dBquery);
                    }
                    if(buyerDCcount<10000)
                    {
                        dflag=0;
                    }
                }
                
            }
            else if (Item != "All" && project === "All" && Basic === "All" && Inch === "All" && Buyer === "All") {
                // console.log("Condition 17");
                dBquery = 'delete data for model [New Model Map BOM] where {[Version].[Version Name].[CWV_MP],[Item].[Item].['+Item+'] ,[Item Material].[Item Material].['+Material+']};';
                vdCommon.debug("Delte Query : "+dBquery);
                queryModule.update(dBquery);
            }
            else if (Item != "All" && project === "All" && Basic === "All" && Inch === "All" && Buyer != "All") {
                // console.log("Condition 18");
                // Convert Buyer into "" format
                var dBuyer = `"${Buyer}"`;
                // Query to get table on buyer entered from Action Button
                let bquery = 'Select (&CWVUI * [Item].[Buyer] * [Category].[Category] ) on row, ({Measure.[Buyer Group Mapping_Asn], Measure.[Buyer Group Mapping_Buyer Group]}) on column where {Measure.[Buyer Group Mapping_Buyer Group]=='+dBuyer+'};';

                let comboBuyerList = [];
                let validHashMapBList = [];
                let buyerlistquery = cellsetModule.createCellSet(queryModule.select(bquery));
                let buyerCcount = buyerlistquery.rowCount;
                for(let i=0;i<buyerCcount;i++)
                {
                    const buyerCValue = buyerlistquery.row(i).cell(buyerlistquery.memberColumnIndex("Item","Buyer" )).Name;
                    if (!validHashMapBList.includes(buyerCValue)) {
                        // const buyerDValue = buyerlistquery.row(i).cell(buyerlistquery.memberColumnIndex("Item","Item" )).Name;
                        comboBuyerList.push({ Name: buyerCValue, DisplayName: buyerCValue });
                        validHashMapBList.push(buyerCValue, buyerCValue);
                    }
                }

                var fquery = 'Select (&CWVUI* [Item].[Item].['+Item+']*[Item].[Buyer]*[Item].[Project]*[Item].[Inch]*[Item].[Basic Name] * [Item Material].[Item Material].['+Material+'] ) on row, ({Measure.[New Model Map BOM_BOM Type], Measure.[New Model Map BOM_Base Qty], Measure.[New Model Map BOM_Created By], Measure.[New Model Map BOM_Creation Time], Measure.[New Model Map BOM_HQ Dev Purchaser], Measure.[New Model Map BOM_HQ Purchaser], Measure.[New Model Map BOM_User Spec]}) on column;';

                let comboDBuyerList = [];
                let validHashMapDBList = [];
                let buyerDlistquery = cellsetModule.createCellSet(queryModule.select(fquery));
                let buyerDCcount = buyerDlistquery.rowCount;
                for(let i=0;i<buyerDCcount;i++)
                {
                    const buyerDValue = buyerDlistquery.row(i).cell(buyerDlistquery.memberColumnIndex("Item","Buyer" )).Name;
                    if (validHashMapBList.includes(buyerDValue)) {
                        const buyerfDValue = buyerDlistquery.row(i).cell(buyerDlistquery.memberColumnIndex("Item","Item" )).Name;
                        comboDBuyerList.push({ Name: buyerfDValue, DisplayName: buyerfDValue });
                        validHashMapDBList.push(buyerDValue, buyerDValue);
                    }
                }
                for(let i=0;i<comboDBuyerList.length;i++)
                {
                    // let dB = `"${comboDBuyerList[i].Name}"`;;
                    let dB = comboDBuyerList[i].Name;
                    dBquery = 'delete data for model [New Model Map BOM] where {[Version].[Version Name].[CWV_MP],[Item].[Item].['+dB+'] ,[Item Material].[Item Material].['+Material+']};';
                    vdCommon.debug("Delte Query : "+dBquery);
                    queryModule.update(dBquery);
                }
            }
            else if (Item != "All" && project === "All" && Basic === "All" && Inch != "All" && Buyer === "All") {
                // console.log("Condition 19");
                var fquery = 'Select (&CWVUI * [Item].[Item].['+Item+']*[Item].[Buyer]*[Item].[Project]*[Item].[Inch].['+Inch+']*[Item].[Basic Name] * [Item Material].[Item Material].['+Material+'] ) on row, ({Measure.[New Model Map BOM_BOM Type], Measure.[New Model Map BOM_Base Qty], Measure.[New Model Map BOM_Created By], Measure.[New Model Map BOM_Creation Time], Measure.[New Model Map BOM_HQ Dev Purchaser], Measure.[New Model Map BOM_HQ Purchaser], Measure.[New Model Map BOM_User Spec]}) on column;';

                let buyerDlistquery = cellsetModule.createCellSet(queryModule.select(fquery));
                let buyerDCcount = buyerDlistquery.rowCount;
                // var dItem = `"${Item}"`;
                if(buyerDCcount>0)
                {
                    dBquery = 'delete data for model [New Model Map BOM] where {[Version].[Version Name].[CWV_MP],[Item].[Item].['+Item+'] ,[Item Material].[Item Material].['+Material+']};';
                    queryModule.update(dBquery);
                }
            }
            else if (Item != "All" && project === "All" && Basic === "All" && Inch != "All" && Buyer != "All") {
                // console.log("Condition 20");
                // Convert Buyer into "" format
                var dBuyer = `"${Buyer}"`;
                // Query to get table on buyer entered from Action Button
                let bquery = 'Select (&CWVUI * [Item].[Buyer] * [Category].[Category] ) on row, ({Measure.[Buyer Group Mapping_Asn], Measure.[Buyer Group Mapping_Buyer Group]}) on column where {Measure.[Buyer Group Mapping_Buyer Group]=='+dBuyer+'};';

                let comboBuyerList = [];
                let validHashMapBList = [];
                let buyerlistquery = cellsetModule.createCellSet(queryModule.select(bquery));
                let buyerCcount = buyerlistquery.rowCount;
                for(let i=0;i<buyerCcount;i++)
                {
                    const buyerCValue = buyerlistquery.row(i).cell(buyerlistquery.memberColumnIndex("Item","Buyer" )).Name;
                    if (!validHashMapBList.includes(buyerCValue)) {
                        // const buyerDValue = buyerlistquery.row(i).cell(buyerlistquery.memberColumnIndex("Item","Item" )).Name;
                        comboBuyerList.push({ Name: buyerCValue, DisplayName: buyerCValue });
                        validHashMapBList.push(buyerCValue, buyerCValue);
                    }
                }

                var fquery = 'Select (&CWVUI * [Item].[Item].['+Item+']*[Item].[Buyer]*[Item].[Project]*[Item].[Inch].['+Inch+']*[Item].[Basic Name] * [Item Material].[Item Material].['+Material+'] ) on row, ({Measure.[New Model Map BOM_BOM Type], Measure.[New Model Map BOM_Base Qty], Measure.[New Model Map BOM_Created By], Measure.[New Model Map BOM_Creation Time], Measure.[New Model Map BOM_HQ Dev Purchaser], Measure.[New Model Map BOM_HQ Purchaser], Measure.[New Model Map BOM_User Spec]}) on column;';

                let comboDBuyerList = [];
                let validHashMapDBList = [];
                let buyerDlistquery = cellsetModule.createCellSet(queryModule.select(fquery));
                let buyerDCcount = buyerDlistquery.rowCount;
                for(let i=0;i<buyerDCcount;i++)
                {
                    const buyerDValue = buyerDlistquery.row(i).cell(buyerDlistquery.memberColumnIndex("Item","Buyer" )).Name;
                    if (validHashMapBList.includes(buyerDValue)) {
                        const buyerfDValue = buyerDlistquery.row(i).cell(buyerDlistquery.memberColumnIndex("Item","Item" )).Name;
                        comboDBuyerList.push({ Name: buyerfDValue, DisplayName: buyerfDValue });
                        validHashMapDBList.push(buyerDValue, buyerDValue);
                    }
                }
                for(let i=0;i<comboDBuyerList.length;i++)
                {
                    // let dB = `"${comboDBuyerList[i].Name}"`;;
                    let dB = comboDBuyerList[i].Name;
                    dBquery = 'delete data for model [New Model Map BOM] where {[Version].[Version Name].[CWV_MP],[Item].[Item].['+dB+'] ,[Item Material].[Item Material].['+Material+']};';
                    vdCommon.debug("Delte Query : "+dBquery);
                    queryModule.update(dBquery);
                }
            }
            else if (Item != "All" && project === "All" && Basic != "All" && Inch === "All" && Buyer === "All") {
                // console.log("Condition 21");
                var fquery = 'Select (&CWVUI * [Item].[Item].['+Item+']*[Item].[Buyer]*[Item].[Project]*[Item].[Inch]*[Item].[Basic Name].['+Basic+'] * [Item Material].[Item Material].['+Material+'] ) on row, ({Measure.[New Model Map BOM_BOM Type], Measure.[New Model Map BOM_Base Qty], Measure.[New Model Map BOM_Created By], Measure.[New Model Map BOM_Creation Time], Measure.[New Model Map BOM_HQ Dev Purchaser], Measure.[New Model Map BOM_HQ Purchaser], Measure.[New Model Map BOM_User Spec]}) on column;';

                let buyerDlistquery = cellsetModule.createCellSet(queryModule.select(fquery));
                let buyerDCcount = buyerDlistquery.rowCount;
                // var dItem = `"${Item}"`;
                if(buyerDCcount>0)
                {
                    dBquery = 'delete data for model [New Model Map BOM] where {[Version].[Version Name].[CWV_MP],[Item].[Item].['+Item+'] ,[Item Material].[Item Material].['+Material+']};';
                    queryModule.update(dBquery);
                }
            }
            else if (Item != "All" && project === "All" && Basic != "All" && Inch === "All" && Buyer != "All") {
                // console.log("Condition 22");
                var dBuyer = `"${Buyer}"`;
                // Query to get table on buyer entered from Action Button
                let bquery = 'Select (&CWVUI * [Item].[Buyer] * [Category].[Category] ) on row, ({Measure.[Buyer Group Mapping_Asn], Measure.[Buyer Group Mapping_Buyer Group]}) on column where {Measure.[Buyer Group Mapping_Buyer Group]=='+dBuyer+'};';

                let comboBuyerList = [];
                let validHashMapBList = [];
                let buyerlistquery = cellsetModule.createCellSet(queryModule.select(bquery));
                let buyerCcount = buyerlistquery.rowCount;
                for(let i=0;i<buyerCcount;i++)
                {
                    const buyerCValue = buyerlistquery.row(i).cell(buyerlistquery.memberColumnIndex("Item","Buyer" )).Name;
                    if (!validHashMapBList.includes(buyerCValue)) {
                        // const buyerDValue = buyerlistquery.row(i).cell(buyerlistquery.memberColumnIndex("Item","Item" )).Name;
                        comboBuyerList.push({ Name: buyerCValue, DisplayName: buyerCValue });
                        validHashMapBList.push(buyerCValue, buyerCValue);
                    }
                }

                var fquery = 'Select (&CWVUI* [Item].[Item].['+Item+']*[Item].[Buyer]*[Item].[Project]*[Item].[Inch]*[Item].[Basic Name].['+Basic+'] * [Item Material].[Item Material].['+Material+'] ) on row, ({Measure.[New Model Map BOM_BOM Type], Measure.[New Model Map BOM_Base Qty], Measure.[New Model Map BOM_Created By], Measure.[New Model Map BOM_Creation Time], Measure.[New Model Map BOM_HQ Dev Purchaser], Measure.[New Model Map BOM_HQ Purchaser], Measure.[New Model Map BOM_User Spec]}) on column;';

                let comboDBuyerList = [];
                let validHashMapDBList = [];
                let buyerDlistquery = cellsetModule.createCellSet(queryModule.select(fquery));
                let buyerDCcount = buyerDlistquery.rowCount;
                for(let i=0;i<buyerDCcount;i++)
                {
                    const buyerDValue = buyerDlistquery.row(i).cell(buyerDlistquery.memberColumnIndex("Item","Buyer" )).Name;
                    if (validHashMapBList.includes(buyerDValue)) {
                        const buyerfDValue = buyerDlistquery.row(i).cell(buyerDlistquery.memberColumnIndex("Item","Item" )).Name;
                        comboDBuyerList.push({ Name: buyerfDValue, DisplayName: buyerfDValue });
                        validHashMapDBList.push(buyerDValue, buyerDValue);
                    }
                }
                for(let i=0;i<comboDBuyerList.length;i++)
                {
                    // let dB = `"${comboDBuyerList[i].Name}"`;;
                    let dB = comboDBuyerList[i].Name;
                    dBquery = 'delete data for model [New Model Map BOM] where {[Version].[Version Name].[CWV_MP],[Item].[Item].['+dB+'] ,[Item Material].[Item Material].['+Material+']};';
                    vdCommon.debug("Delte Query : "+dBquery);
                    queryModule.update(dBquery);
                }
            }
            else if (Item != "All" && project === "All" && Basic != "All" && Inch != "All" && Buyer === "All") {
                // console.log("Condition 23");
                var fquery = 'Select (&CWVUI* [Item].[Item].['+Item+']*[Item].[Buyer]*[Item].[Project]*[Item].[Inch].['+Inch+']*[Item].[Basic Name].['+Basic+'] * [Item Material].[Item Material].['+Material+'] ) on row, ({Measure.[New Model Map BOM_BOM Type], Measure.[New Model Map BOM_Base Qty], Measure.[New Model Map BOM_Created By], Measure.[New Model Map BOM_Creation Time], Measure.[New Model Map BOM_HQ Dev Purchaser], Measure.[New Model Map BOM_HQ Purchaser], Measure.[New Model Map BOM_User Spec]}) on column;';

                let buyerDlistquery = cellsetModule.createCellSet(queryModule.select(fquery));
                let buyerDCcount = buyerDlistquery.rowCount;
                // var dItem = `"${Item}"`;
                if(buyerDCcount>0)
                {
                    dBquery = 'delete data for model [New Model Map BOM] where {[Version].[Version Name].[CWV_MP],[Item].[Item].['+Item+'] ,[Item Material].[Item Material].['+Material+']};';
                    queryModule.update(dBquery);
                }
            }
            else if (Item != "All" && project === "All" && Basic != "All" && Inch !== "All" && Buyer != "All") {
                // console.log("Condition 24");
                var dBuyer = `"${Buyer}"`;
                // Query to get table on buyer entered from Action Button
                let bquery = 'Select (&CWVUI * [Item].[Buyer] * [Category].[Category] ) on row, ({Measure.[Buyer Group Mapping_Asn], Measure.[Buyer Group Mapping_Buyer Group]}) on column where {Measure.[Buyer Group Mapping_Buyer Group]=='+dBuyer+'};';

                let comboBuyerList = [];
                let validHashMapBList = [];
                let buyerlistquery = cellsetModule.createCellSet(queryModule.select(bquery));
                let buyerCcount = buyerlistquery.rowCount;
                for(let i=0;i<buyerCcount;i++)
                {
                    const buyerCValue = buyerlistquery.row(i).cell(buyerlistquery.memberColumnIndex("Item","Buyer" )).Name;
                    if (!validHashMapBList.includes(buyerCValue)) {
                        // const buyerDValue = buyerlistquery.row(i).cell(buyerlistquery.memberColumnIndex("Item","Item" )).Name;
                        comboBuyerList.push({ Name: buyerCValue, DisplayName: buyerCValue });
                        validHashMapBList.push(buyerCValue, buyerCValue);
                    }
                }

                var fquery = 'Select (&CWVUI * [Item].[Item].['+Item+']*[Item].[Buyer]*[Item].[Project]*[Item].[Inch].['+Inch+']*[Item].[Basic Name].['+Basic+'] * [Item Material].[Item Material].['+Material+'] ) on row, ({Measure.[New Model Map BOM_BOM Type], Measure.[New Model Map BOM_Base Qty], Measure.[New Model Map BOM_Created By], Measure.[New Model Map BOM_Creation Time], Measure.[New Model Map BOM_HQ Dev Purchaser], Measure.[New Model Map BOM_HQ Purchaser], Measure.[New Model Map BOM_User Spec]}) on column;';

                let comboDBuyerList = [];
                let validHashMapDBList = [];
                let buyerDlistquery = cellsetModule.createCellSet(queryModule.select(fquery));
                let buyerDCcount = buyerDlistquery.rowCount;
                for(let i=0;i<buyerDCcount;i++)
                {
                    const buyerDValue = buyerDlistquery.row(i).cell(buyerDlistquery.memberColumnIndex("Item","Buyer" )).Name;
                    if (validHashMapBList.includes(buyerDValue)) {
                        const buyerfDValue = buyerDlistquery.row(i).cell(buyerDlistquery.memberColumnIndex("Item","Item" )).Name;
                        comboDBuyerList.push({ Name: buyerfDValue, DisplayName: buyerfDValue });
                        validHashMapDBList.push(buyerDValue, buyerDValue);
                    }
                }
                for(let i=0;i<comboDBuyerList.length;i++)
                {
                    // let dB = `"${comboDBuyerList[i].Name}"`;;
                    let dB = comboDBuyerList[i].Name;
                    dBquery = 'delete data for model [New Model Map BOM] where {[Version].[Version Name].[CWV_MP],[Item].[Item].['+dB+'] ,[Item Material].[Item Material].['+Material+']};';
                    vdCommon.debug("Delte Query : "+dBquery);
                    queryModule.update(dBquery);
                }
            }
            else if (Item != "All" && project !="All" && Basic === "All" && Inch === "All" && Buyer === "All") {
                // console.log("Condition 25");
                var fquery = 'Select (&CWVUI * [Item].[Item].['+Item+']*[Item].[Buyer]*[Item].[Project].['+project+']*[Item].[Inch]*[Item].[Basic Name] * [Item Material].[Item Material].['+Material+'] ) on row, ({Measure.[New Model Map BOM_BOM Type], Measure.[New Model Map BOM_Base Qty], Measure.[New Model Map BOM_Created By], Measure.[New Model Map BOM_Creation Time], Measure.[New Model Map BOM_HQ Dev Purchaser], Measure.[New Model Map BOM_HQ Purchaser], Measure.[New Model Map BOM_User Spec]}) on column;';

                let buyerDlistquery = cellsetModule.createCellSet(queryModule.select(fquery));
                let buyerDCcount = buyerDlistquery.rowCount;
                // var dItem = `"${Item}"`;
                if(buyerDCcount>0)
                {
                    dBquery = 'delete data for model [New Model Map BOM] where {[Version].[Version Name].[CWV_MP],[Item].[Item].['+Item+'] ,[Item Material].[Item Material].['+Material+']};';
                    queryModule.update(dBquery);
                }
            }
            else if (Item != "All" && project != "All" && Basic === "All" && Inch === "All" && Buyer != "All") {
                // console.log("Condition 26");
                var dBuyer = `"${Buyer}"`;
                // Query to get table on buyer entered from Action Button
                let bquery = 'Select (&CWVUI * [Item].[Buyer] * [Category].[Category] ) on row, ({Measure.[Buyer Group Mapping_Asn], Measure.[Buyer Group Mapping_Buyer Group]}) on column where {Measure.[Buyer Group Mapping_Buyer Group]=='+dBuyer+'};';

                let comboBuyerList = [];
                let validHashMapBList = [];
                let buyerlistquery = cellsetModule.createCellSet(queryModule.select(bquery));
                let buyerCcount = buyerlistquery.rowCount;
                for(let i=0;i<buyerCcount;i++)
                {
                    const buyerCValue = buyerlistquery.row(i).cell(buyerlistquery.memberColumnIndex("Item","Buyer" )).Name;
                    if (!validHashMapBList.includes(buyerCValue)) {
                        // const buyerDValue = buyerlistquery.row(i).cell(buyerlistquery.memberColumnIndex("Item","Item" )).Name;
                        comboBuyerList.push({ Name: buyerCValue, DisplayName: buyerCValue });
                        validHashMapBList.push(buyerCValue, buyerCValue);
                    }
                }

                var fquery = 'Select (&CWVUI * [Item].[Item].['+Item+']*[Item].[Buyer]*[Item].[Project].['+project+']*[Item].[Inch]*[Item].[Basic Name] * [Item Material].[Item Material].['+Material+'] ) on row, ({Measure.[New Model Map BOM_BOM Type], Measure.[New Model Map BOM_Base Qty], Measure.[New Model Map BOM_Created By], Measure.[New Model Map BOM_Creation Time], Measure.[New Model Map BOM_HQ Dev Purchaser], Measure.[New Model Map BOM_HQ Purchaser], Measure.[New Model Map BOM_User Spec]}) on column;';

                let comboDBuyerList = [];
                let validHashMapDBList = [];
                let buyerDlistquery = cellsetModule.createCellSet(queryModule.select(fquery));
                let buyerDCcount = buyerDlistquery.rowCount;
                for(let i=0;i<buyerDCcount;i++)
                {
                    const buyerDValue = buyerDlistquery.row(i).cell(buyerDlistquery.memberColumnIndex("Item","Buyer" )).Name;
                    if (validHashMapBList.includes(buyerDValue)) {
                        const buyerfDValue = buyerDlistquery.row(i).cell(buyerDlistquery.memberColumnIndex("Item","Item" )).Name;
                        comboDBuyerList.push({ Name: buyerfDValue, DisplayName: buyerfDValue });
                        validHashMapDBList.push(buyerDValue, buyerDValue);
                    }
                }
                for(let i=0;i<comboDBuyerList.length;i++)
                {
                    // let dB = `"${comboDBuyerList[i].Name}"`;;
                    let dB = comboDBuyerList[i].Name;
                    dBquery = 'delete data for model [New Model Map BOM] where {[Version].[Version Name].[CWV_MP],[Item].[Item].['+dB+'] ,[Item Material].[Item Material].['+Material+']};';
                    vdCommon.debug("Delte Query : "+dBquery);
                    queryModule.update(dBquery);
                }
            }
            else if (Item != "All" && project != "All" && Basic === "All" && Inch != "All" && Buyer === "All") {
                // console.log("Condition 27");
                var fquery = 'Select (&CWVUI * [Item].[Item].['+Item+']*[Item].[Buyer]*[Item].[Project].['+project+']*[Item].[Inch].['+Inch+']*[Item].[Basic Name] * [Item Material].[Item Material].['+Material+'] ) on row, ({Measure.[New Model Map BOM_BOM Type], Measure.[New Model Map BOM_Base Qty], Measure.[New Model Map BOM_Created By], Measure.[New Model Map BOM_Creation Time], Measure.[New Model Map BOM_HQ Dev Purchaser], Measure.[New Model Map BOM_HQ Purchaser], Measure.[New Model Map BOM_User Spec]}) on column;';

                let buyerDlistquery = cellsetModule.createCellSet(queryModule.select(fquery));
                let buyerDCcount = buyerDlistquery.rowCount;
                // var dItem = `"${Item}"`;
                if(buyerDCcount>0)
                {
                    dBquery = 'delete data for model [New Model Map BOM] where {[Version].[Version Name].[CWV_MP],[Item].[Item].['+Item+'] ,[Item Material].[Item Material].['+Material+']};';
                    queryModule.update(dBquery);
                }
            }
            else if (Item != "All" && project != "All" && Basic === "All" && Inch != "All" && Buyer != "All") {
                // console.log("Condition 28");
                var dBuyer = `"${Buyer}"`;
                // Query to get table on buyer entered from Action Button
                let bquery = 'Select (&CWVUI * [Item].[Buyer] * [Category].[Category] ) on row, ({Measure.[Buyer Group Mapping_Asn], Measure.[Buyer Group Mapping_Buyer Group]}) on column where {Measure.[Buyer Group Mapping_Buyer Group]=='+dBuyer+'};';

                let comboBuyerList = [];
                let validHashMapBList = [];
                let buyerlistquery = cellsetModule.createCellSet(queryModule.select(bquery));
                let buyerCcount = buyerlistquery.rowCount;
                for(let i=0;i<buyerCcount;i++)
                {
                    const buyerCValue = buyerlistquery.row(i).cell(buyerlistquery.memberColumnIndex("Item","Buyer" )).Name;
                    if (!validHashMapBList.includes(buyerCValue)) {
                        // const buyerDValue = buyerlistquery.row(i).cell(buyerlistquery.memberColumnIndex("Item","Item" )).Name;
                        comboBuyerList.push({ Name: buyerCValue, DisplayName: buyerCValue });
                        validHashMapBList.push(buyerCValue, buyerCValue);
                    }
                }

                var fquery = 'Select (&CWVUI * [Item].[Item].['+Item+']*[Item].[Buyer]*[Item].[Project].['+project+']*[Item].[Inch].['+Inch+']*[Item].[Basic Name] * [Item Material].[Item Material].['+Material+'] ) on row, ({Measure.[New Model Map BOM_BOM Type], Measure.[New Model Map BOM_Base Qty], Measure.[New Model Map BOM_Created By], Measure.[New Model Map BOM_Creation Time], Measure.[New Model Map BOM_HQ Dev Purchaser], Measure.[New Model Map BOM_HQ Purchaser], Measure.[New Model Map BOM_User Spec]}) on column;';

                let comboDBuyerList = [];
                let validHashMapDBList = [];
                let buyerDlistquery = cellsetModule.createCellSet(queryModule.select(fquery));
                let buyerDCcount = buyerDlistquery.rowCount;
                for(let i=0;i<buyerDCcount;i++)
                {
                    const buyerDValue = buyerDlistquery.row(i).cell(buyerDlistquery.memberColumnIndex("Item","Buyer" )).Name;
                    if (validHashMapBList.includes(buyerDValue)) {
                        const buyerfDValue = buyerDlistquery.row(i).cell(buyerDlistquery.memberColumnIndex("Item","Item" )).Name;
                        comboDBuyerList.push({ Name: buyerfDValue, DisplayName: buyerfDValue });
                        validHashMapDBList.push(buyerDValue, buyerDValue);
                    }
                }
                for(let i=0;i<comboDBuyerList.length;i++)
                {
                    // let dB = `"${comboDBuyerList[i].Name}"`;;
                    let dB = comboDBuyerList[i].Name;
                    dBquery = 'delete data for model [New Model Map BOM] where {[Version].[Version Name].[CWV_MP],[Item].[Item].['+dB+'] ,[Item Material].[Item Material].['+Material+']};';
                    vdCommon.debug("Delte Query : "+dBquery);
                    queryModule.update(dBquery);
                }
            }
            else if (Item != "All" && project != "All" && Basic != "All" && Inch === "All" && Buyer === "All") {
                // console.log("Condition 29");
                var fquery = 'Select (&CWVUI * [Item].[Item].['+Item+']*[Item].[Buyer]*[Item].[Project].['+project+']*[Item].[Inch]*[Item].[Basic Name].['+Basic+'] * [Item Material].[Item Material].['+Material+'] ) on row, ({Measure.[New Model Map BOM_BOM Type], Measure.[New Model Map BOM_Base Qty], Measure.[New Model Map BOM_Created By], Measure.[New Model Map BOM_Creation Time], Measure.[New Model Map BOM_HQ Dev Purchaser], Measure.[New Model Map BOM_HQ Purchaser], Measure.[New Model Map BOM_User Spec]}) on column;';

                let buyerDlistquery = cellsetModule.createCellSet(queryModule.select(fquery));
                let buyerDCcount = buyerDlistquery.rowCount;
                // var dItem = `"${Item}"`;
                if(buyerDCcount>0)
                {
                    dBquery = 'delete data for model [New Model Map BOM] where {[Version].[Version Name].[CWV_MP],[Item].[Item].['+Item+'] ,[Item Material].[Item Material].['+Material+']};';
                    queryModule.update(dBquery);
                }
            }
            else if (Item != "All" && project != "All" && Basic != "All" && Inch === "All" && Buyer != "All") {
                // console.log("Condition 30");
                var dBuyer = `"${Buyer}"`;
                // Query to get table on buyer entered from Action Button
                let bquery = 'Select (&CWVUI * [Item].[Buyer] * [Category].[Category] ) on row, ({Measure.[Buyer Group Mapping_Asn], Measure.[Buyer Group Mapping_Buyer Group]}) on column where {Measure.[Buyer Group Mapping_Buyer Group]=='+dBuyer+'};';

                let comboBuyerList = [];
                let validHashMapBList = [];
                let buyerlistquery = cellsetModule.createCellSet(queryModule.select(bquery));
                let buyerCcount = buyerlistquery.rowCount;
                for(let i=0;i<buyerCcount;i++)
                {
                    const buyerCValue = buyerlistquery.row(i).cell(buyerlistquery.memberColumnIndex("Item","Buyer" )).Name;
                    if (!validHashMapBList.includes(buyerCValue)) {
                        // const buyerDValue = buyerlistquery.row(i).cell(buyerlistquery.memberColumnIndex("Item","Item" )).Name;
                        comboBuyerList.push({ Name: buyerCValue, DisplayName: buyerCValue });
                        validHashMapBList.push(buyerCValue, buyerCValue);
                    }
                }

                var fquery = 'Select (&CWVUI * [Item].[Item].['+Item+']*[Item].[Buyer]*[Item].[Project].['+project+']*[Item].[Inch]*[Item].[Basic Name].['+Basic+'] * [Item Material].[Item Material].['+Material+'] ) on row, ({Measure.[New Model Map BOM_BOM Type], Measure.[New Model Map BOM_Base Qty], Measure.[New Model Map BOM_Created By], Measure.[New Model Map BOM_Creation Time], Measure.[New Model Map BOM_HQ Dev Purchaser], Measure.[New Model Map BOM_HQ Purchaser], Measure.[New Model Map BOM_User Spec]}) on column;';

                let comboDBuyerList = [];
                let validHashMapDBList = [];
                let buyerDlistquery = cellsetModule.createCellSet(queryModule.select(fquery));
                let buyerDCcount = buyerDlistquery.rowCount;
                for(let i=0;i<buyerDCcount;i++)
                {
                    const buyerDValue = buyerDlistquery.row(i).cell(buyerDlistquery.memberColumnIndex("Item","Buyer" )).Name;
                    if (validHashMapBList.includes(buyerDValue)) {
                        const buyerfDValue = buyerDlistquery.row(i).cell(buyerDlistquery.memberColumnIndex("Item","Item" )).Name;
                        comboDBuyerList.push({ Name: buyerfDValue, DisplayName: buyerfDValue });
                        validHashMapDBList.push(buyerDValue, buyerDValue);
                    }
                }
                for(let i=0;i<comboDBuyerList.length;i++)
                {
                    // let dB = `"${comboDBuyerList[i].Name}"`;;
                    let dB = comboDBuyerList[i].Name;
                    dBquery = 'delete data for model [New Model Map BOM] where {[Version].[Version Name].[CWV_MP],[Item].[Item].['+dB+'] ,[Item Material].[Item Material].['+Material+']};';
                    vdCommon.debug("Delte Query : "+dBquery);
                    queryModule.update(dBquery);
                }
            }
            else if (Item != "All" && project != "All" && Basic != "All" && Inch != "All" && Buyer === "All") {
                // console.log("Condition 31");
                var fquery = 'Select (&CWVUI * [Item].[Item].['+Item+']*[Item].[Buyer]*[Item].[Project].['+project+']*[Item].[Inch].['+Inch+']*[Item].[Basic Name].['+Basic+'] * [Item Material].[Item Material].['+Material+'] ) on row, ({Measure.[New Model Map BOM_BOM Type], Measure.[New Model Map BOM_Base Qty], Measure.[New Model Map BOM_Created By], Measure.[New Model Map BOM_Creation Time], Measure.[New Model Map BOM_HQ Dev Purchaser], Measure.[New Model Map BOM_HQ Purchaser], Measure.[New Model Map BOM_User Spec]}) on column;';

                let buyerDlistquery = cellsetModule.createCellSet(queryModule.select(fquery));
                let buyerDCcount = buyerDlistquery.rowCount;
                // var dItem = `"${Item}"`;
                if(buyerDCcount>0)
                {
                    dBquery = 'delete data for model [New Model Map BOM] where {[Version].[Version Name].[CWV_MP],[Item].[Item].['+Item+'] ,[Item Material].[Item Material].['+Material+']};';
                    queryModule.update(dBquery);
                }
            }
            else if (Item != "All" && project != "All" && Basic != "All" && Inch != "All" && Buyer != "All") {
                // console.log("Condition 32");
                vdCommon.debug("Condition 32");
                var dBuyer = `"${Buyer}"`;
                // Query to get table on buyer entered from Action Button
                let bquery = 'Select (&CWVUI * [Item].[Buyer] * [Category].[Category] ) on row, ({Measure.[Buyer Group Mapping_Asn], Measure.[Buyer Group Mapping_Buyer Group]}) on column where {Measure.[Buyer Group Mapping_Buyer Group]=='+dBuyer+'};';

                let comboBuyerList = [];
                let validHashMapBList = [];
                let buyerlistquery = cellsetModule.createCellSet(queryModule.select(bquery));
                let buyerCcount = buyerlistquery.rowCount;
                for(let i=0;i<buyerCcount;i++)
                {
                    const buyerCValue = buyerlistquery.row(i).cell(buyerlistquery.memberColumnIndex("Item","Buyer" )).Name;
                    if (!validHashMapBList.includes(buyerCValue)) {
                        // const buyerDValue = buyerlistquery.row(i).cell(buyerlistquery.memberColumnIndex("Item","Item" )).Name;
                        comboBuyerList.push({ Name: buyerCValue, DisplayName: buyerCValue });
                        validHashMapBList.push(buyerCValue, buyerCValue);
                    }
                }

                var fquery = 'Select (&CWVUI * [Item].[Item].['+Item+']*[Item].[Buyer]*[Item].[Project].['+project+']*[Item].[Inch].['+Inch+']*[Item].[Basic Name].['+Basic+'] * [Item Material].[Item Material].['+Material+'] ) on row, ({Measure.[New Model Map BOM_BOM Type], Measure.[New Model Map BOM_Base Qty], Measure.[New Model Map BOM_Created By], Measure.[New Model Map BOM_Creation Time], Measure.[New Model Map BOM_HQ Dev Purchaser], Measure.[New Model Map BOM_HQ Purchaser], Measure.[New Model Map BOM_User Spec]}) on column;';

                let comboDBuyerList = [];
                let validHashMapDBList = [];
                let buyerDlistquery = cellsetModule.createCellSet(queryModule.select(fquery));
                let buyerDCcount = buyerDlistquery.rowCount;
                for(let i=0;i<buyerDCcount;i++)
                {
                    const buyerDValue = buyerDlistquery.row(i).cell(buyerDlistquery.memberColumnIndex("Item","Buyer" )).Name;
                    if (validHashMapBList.includes(buyerDValue)) {
                        const buyerfDValue = buyerDlistquery.row(i).cell(buyerDlistquery.memberColumnIndex("Item","Item" )).Name;
                        comboDBuyerList.push({ Name: buyerfDValue, DisplayName: buyerfDValue });
                        validHashMapDBList.push(buyerDValue, buyerDValue);
                    }
                }
                vdCommon.debug("comboDBuyerList: "+comboDBuyerList);
                for(let i=0;i<comboDBuyerList.length;i++)
                {
                    // let dB = `"${comboDBuyerList[i].Name}"`;;
                    let dB = comboDBuyerList[i].Name;
                    dBquery = 'delete data for model [New Model Map BOM] where {[Version].[Version Name].[CWV_MP],[Item].[Item].['+dB+'] ,[Item Material].[Item Material].['+Material+']};';
                    vdCommon.debug("Delte Query : "+dBquery);
                    queryModule.update(dBquery);
                }
            }
            // vdCommon.debug("Pause : "+Plant1);
            var dQuery = 'delete data for model [New Model Map] where {[Version].[Version Name].[CWV_MP],[Rule].[Rule No].['+Rule+'],[Item Material].[Item Material].['+Material+']};';
            queryModule.update(dQuery);
            // queryModule.select(dBquery);
        }        
    };

    return {
        fn_materialCode : fn_materialCode,
        fn_bomPlant : fn_bomPlant,
        fn_bomBasicName : fn_bomBasicName,
        fn_bomInch :fn_bomInch,
        fn_bomModel : fn_bomModel,
        fn_bomBuyer : fn_bomBuyer,
        fn_MaterialC :fn_MaterialC,
        fn_Delete : fn_Delete
    };
});