define('o9.NSCM.JSLCMKDPlanningBOM', ['o9/data/query', 'o9/data/cellset', 'o9.NSCM.commonLib'], function(){
    const programName = "o9.NSCM.JSLCMKDPlanningBOM";

    /** fn_makeCombo 의 combolist 예외 처리 */    
    var fn_makeComboEtc = function(result, param) {

        const commonLib = require('o9.NSCM.commonLib');
        const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);

        vdCommon.setLogLevel("Debug");
        var comboList = [];
        var validHashMap = {};
        var name = "";
        var displayName = "";
        var displayNameTmp = "";
        if ( param["ComboCodes"] != undefined ) {
            var codes = param["ComboCodes"];
            var values = param["ComboValues"];
            for ( var i = 0; i < codes.length; i++ ) {
                comboList.push({ Name : codes[i], DisplayName : values[i]});
            }
        } else {
            for ( var i = 0; i < result.cs.rowCount; i++ ) {
                if ( param["DimName"] != undefined ) {
                    name = result.cs.row(i).cell(result.cs.memberColumnIndex(param["DimName"], param["DimAttbName"])).Name;
                    if ( param["DimAttbNameEtc"] != undefined ) {   // add 2025.05.22
                        displayNameTmp = result.cs.row(i).cell(result.cs.memberColumnIndex(param["DimName"], param["DimAttbNameEtc"])).DisplayName;
                        if ( param["DisplayNameType"] != undefined && param["DisplayNameType"] == "codeName") {
                            displayName = name + " ("+displayNameTmp+")";
                        }else{
                            displayName = name + " ("+displayNameTmp+")";
                        }
                        // var firows = irows+" ("+drows+")";
                    }else{
                        displayName = result.cs.row(i).cell(result.cs.memberColumnIndex(param["DimName"], param["DimAttbName"])).DisplayName;
                    }

                    // - 일 경우는 무시
                    if ( name == "-" ) {
                        continue;
                    }

                    // DisplayName 에 코드도 같이 보여줄지 여부
                    if ( param["isDisplayNameWithCode"] != undefined && param["isDisplayNameWithCode"] ) {
                        displayName = displayName + " (" + name + ")";
                    }
                    // Name, Display를 Name으로 보여준다.
                    if ( param["isOnlyName"] != undefined && param["isOnlyName"] ) {
                        displayName = name;
                    }
                } else if ( param["MeasureName"] != undefined ) {
                    name = result.cs.row(i).cell(result.cs.measureColumnIndex(param["MeasureName"]));
                    displayName = name;
                }
                if ( validHashMap[name] == undefined ) {
                    comboList.push({ Name : name, DisplayName : displayName});
                    validHashMap[name] = name;
                }
            }
        }

        if ( param["Sort"] != undefined ) {
            if ( param["Sort"] == "Name" ) {
                comboList.sort((a, b) => {
                        if ( a.Name < b.Name ) return -1;
                        if ( a.Name > b.Name ) return 1;
                        return 0;
                    });
            } else {
                comboList.sort((a, b) => {
                        if ( a.DisplayName < b.DisplayName ) return -1;
                        if ( a.DisplayName > b.DisplayName ) return 1;
                        return 0;
                    });
            }
        }

        if ( param["existAll"] != undefined && param["existAll"] ) {
            comboList.unshift({ Name : "All", DisplayName : "All"});
        }
        vdCommon.debug("fn_makeComboEtc=========>End");
        return comboList;
    };

    /** Category Combolist */
    var fn_category = function(o9params) {
        try {
            const commonLib = require('o9.NSCM.commonLib');
            const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
            vdCommon.setLogLevel("Debug");

            // LCM
            var resultLcm = vdCommon.selectList(["[Item].[Item Stage].[LCM]"], [], "", "", "");
            var comboListLcm = vdCommon.fn_makeCombo(resultLcm, {DimName : "Item", DimAttbName : "Item Stage", Sort : "DisplayName", existAll : false});
            vdCommon.printCsData(resultLcm, 3);
            vdCommon.debug("comboListLcm : " + JSON.stringify(comboListLcm));

            // SKD, CKD, CRT
            var resultEtc = vdCommon.selectList(["&ItemKDProductType"], [], "", "", "");
            var comboListEtc = vdCommon.fn_makeCombo(resultEtc, {DimName : "Item", DimAttbName : "ProductType", Sort : "DisplayName", existAll : false});
            vdCommon.printCsData(resultEtc, 3);
            vdCommon.debug("comboListEtc : " + JSON.stringify(comboListEtc));

            // combo Data 합침
            var comboListCombined = [...comboListLcm, ...comboListEtc];
            // comboListCombined.unshift({Name : "All",DisplayName: "All"});

            vdCommon.debug("comboListCombined : " + JSON.stringify(comboListCombined));
            vdCommon.programEnd();

            return comboListCombined;

        } catch ( e ) {
            RuleOutputToUI = { Status : 'Error', Message : "Js Logic Error : " + e.message };
            return;
        }

    };    

    /** Inch Combolist */
    var fn_Inch = function(o9Params){
        try {
            const commonLib = require('o9.NSCM.commonLib');
            const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
            const vdUtil = new commonLib.VdUtil();

            vdCommon.setLogLevel("Debug");

            vdCommon.printParams(o9Params);
            let parsedParams = JSON.parse(o9Params);

            var Category = parsedParams.Category;
            vdCommon.debug("pause : "+JSON.stringify(Category));
            vdCommon.debug("Length Check :"+Category.length);

            // LCM
            var resultLcm = vdCommon.selectList(["[Item].[Item Stage]"+vdUtil.fn_filterStr(Category)+".relatedmembers([A1])"], [], "", "", "");
            var comboListLcm = vdCommon.fn_makeCombo(resultLcm, {DimName : "Item", DimAttbName : "A1", Sort : "DisplayName", existAll : false});
            vdCommon.printCsData(resultLcm, 3);
            vdCommon.debug("comboListLcm : " + JSON.stringify(comboListLcm));

            // SKD, CKD, CRT
            // var resultEtc = vdCommon.selectList(["[Item].[ProductType]"+vdUtil.fn_filterStr(Category)+".relatedmembers([Inch])"], [], "", "", "");
            var resultEtc = vdCommon.selectList(["&ItemKDProductType"+vdUtil.fn_filterStr(Category)+".relatedmembers([Inch])"], [], "", "", "");
            var comboListEtc = vdCommon.fn_makeCombo(resultEtc, {DimName : "Item", DimAttbName : "Inch", Sort : "DisplayName", existAll : false});
            vdCommon.printCsData(resultEtc, 3);
            vdCommon.debug("comboListEtc : " + JSON.stringify(comboListEtc));

            // combo Data 합침
            var comboListCombined = [...comboListLcm, ...comboListEtc];

            // Name 을 오름차순 정렬 (대소문자 구분없이 정렬)
            comboListCombined.sort((a,b) => a.Name.localeCompare(b.Name));

            // // Name 을 내림차순 정렬 (대소문자 구분없이 정렬)
            // comboListCombined.sort((a,b) => b.Name.localeCompare(a.Name));

            comboListCombined.unshift({Name : "All",DisplayName: "All"});

            vdCommon.debug("comboListCombined : " + JSON.stringify(comboListCombined));

            return comboListCombined;

        } catch ( e ) {
            RuleOutputToUI = { Status : 'Error', Message : "Js Logic Error : " + e.message };
            return;
        }
    };

    /** LCM/KD Code comboList (Item) */
    var fn_Inchcascad = function(o9Params){

        try {
            const commonLib = require('o9.NSCM.commonLib');
            const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
            const vdUtil = new commonLib.VdUtil();

            vdCommon.setLogLevel("Debug");
            vdCommon.programStart();
            vdCommon.printParams(o9Params);
            var parsedParams = JSON.parse(o9Params);

            // 파라미터 가져오기
            var paramCategory = parsedParams.Category;
            var paramInch = parsedParams.Inch;
            var paramPlant = parsedParams.Plant;

            vdCommon.debug("paramPlant : "+paramPlant);
            vdCommon.debug("paramCategory : "+paramCategory);
            vdCommon.debug("paramInch : "+paramInch);

            //===========================================================================================================================================//
            // BOD Item 의 유효한(BOD Item Eff Startdate/Enddate) Item.Item 을 가져온다.
            //===========================================================================================================================================//
            var whereBODItemLCM = 'where {'
            +' &CWVUI'
            +', [Location].[Location]'+ vdUtil.fn_filterStr(paramPlant)
            +', [Item].[Item Stage]'+ vdUtil.fn_filterStr(paramCategory)
            +', (coalesce(Measure.[BOD Item_Eff Startdate],DATEADD(Now(),-1,"Day")) < now() && coalesce(Measure.[BOD Item_Eff Enddate],DATEADD(Now(),1,"Day")) > now() )'
            +'}';
            var whereBODItemEtc = 'where {'
            +' &CWVUI'
            +', [Location].[Location]'+ vdUtil.fn_filterStr(paramPlant)
            +', [Item].[ProductType]'+ vdUtil.fn_filterStr(paramCategory)
            +', (coalesce(Measure.[BOD Item_Eff Startdate],DATEADD(Now(),-1,"Day")) < now() && coalesce(Measure.[BOD Item_Eff Enddate],DATEADD(Now(),1,"Day")) > now() )'
            +'}';
            var resultBODItemLCM = vdCommon.selectList(["[Item].[Item]"], [], whereBODItemLCM, "", "");     // LCM
            var resultBODItemEtc = vdCommon.selectList(["[Item].[Item]"], [], whereBODItemEtc, "", "");     // LCM 이외

            vdCommon.printCsData(resultBODItemLCM, 3);
            vdCommon.printCsData(resultBODItemEtc, 3);

            var itemName = [];
            if ( resultBODItemLCM.cs.rowCount > 0 ){
                for (let i=0; i < resultBODItemLCM.cs.rowCount; i++) {
                    itemName.push(resultBODItemLCM.cs.row(i).cell(resultBODItemLCM.cs.memberColumnIndex("Item", "Item")).Name);
                }
            }
            if ( resultBODItemEtc.cs.rowCount > 0 ){
                for (let i=0; i < resultBODItemEtc.cs.rowCount; i++) {
                    itemName.push(resultBODItemEtc.cs.row(i).cell(resultBODItemEtc.cs.memberColumnIndex("Item", "Item")).Name);
                }
            }
            //===========================================================================================================================================//

            // 유효한 BOD Item 에서 조회된 Item 을 조건에 추가한다.
            var whereLcm = "";
            var whereEtc = "";

            if(paramInch == "All"){
                vdCommon.debug("Inch All====================>AA");

                // LCM
                whereLcm = 'where {'
                +' &CWVUI'
                +', [Sub Location].[Sub Location]'+ vdUtil.fn_filterStr(paramPlant)
                +', Measure.[Code Map LCM_Valid Flag] == "Y" '
                +', [Item].[Item Stage]'+ vdUtil.fn_filterStr(paramCategory)
                +'}';

                // SKD, CKD, CRT ===> 선택 location, sub location ??
                whereEtc = 'where {'
                +' &CWVUI'
                +', [Location].[Location]'+ vdUtil.fn_filterStr(paramPlant)
                +', &ItemKDProductType'+ vdUtil.fn_filterStr(paramCategory)
                +', (coalesce(Measure.[BOD Item_Eff Startdate],DATEADD(Now(),-1,"Day")) < now() && coalesce(Measure.[BOD Item_Eff Enddate],DATEADD(Now(),1,"Day")) > now() )'
                +'}';

            }else{
                vdCommon.debug("Inch Multi Select====================>BB");
                // LCM
                whereLcm = 'where {'
                +' &CWVUI'
                +', [Sub Location].[Sub Location]'+ vdUtil.fn_filterStr(paramPlant)
                +', Measure.[Code Map LCM_Valid Flag] == "Y" '
                +', [Item].[Item Stage]'+ vdUtil.fn_filterStr(paramCategory)
                +', [Item].[A1]'+ vdUtil.fn_filterStr(paramInch)
                +'}';

                // SKD, CKD, CRT 
                whereEtc = 'where {'
                +' &CWVUI'
                +', [Location].[Location]'+ vdUtil.fn_filterStr(paramPlant)
                +', &ItemKDProductType'+ vdUtil.fn_filterStr(paramCategory)
                +', [Item].[Inch]'+ vdUtil.fn_filterStr(paramInch)
                +', (coalesce(Measure.[BOD Item_Eff Startdate],DATEADD(Now(),-1,"Day")) < now() && coalesce(Measure.[BOD Item_Eff Enddate],DATEADD(Now(),1,"Day")) > now() )'
                +'}';
            }

            // LCM : Code Map LCM
            var resultLcm = vdCommon.selectList(["[Item].[Item]"+ vdUtil.fn_filterStr(itemName),"[Item].[Description]"], [], whereLcm, "", "");
            vdCommon.printCsData(resultLcm, 3);

            // SKD, CKD, CRT : BOD Item
            var resultEtc = vdCommon.selectList(["[Item].[Item]"+ vdUtil.fn_filterStr(itemName),"[Item].[Description]"], [], whereEtc, "", "");
            vdCommon.printCsData(resultEtc, 3);

            var comboListLcm = fn_makeComboEtc(resultLcm, {DimName : "Item", DimAttbName : "Item", DimAttbNameEtc : "Description", DisplayNameType : "codeName",Sort : "DisplayName", existAll : false});
            var comboListEtc = fn_makeComboEtc(resultEtc, {DimName : "Item", DimAttbName : "Item", DimAttbNameEtc : "Description", DisplayNameType : "codeName",Sort : "DisplayName", existAll : false});

            vdCommon.debug("comboListLcm : " + JSON.stringify(comboListLcm));
            vdCommon.debug("comboListEtc : " + JSON.stringify(comboListEtc));

            // combo Data 합침
            var comboListCombined = [...comboListLcm, ...comboListEtc];

            // Name 을 오름차순 정렬 (대소문자 구분없이 정렬)
            comboListCombined.sort((a,b) => a.Name.localeCompare(b.Name));

            // // Name 을 내림차순 정렬 (대소문자 구분없이 정렬)
            // comboListCombined.sort((a,b) => b.Name.localeCompare(a.Name));

            comboListCombined.unshift({Name : "Dummy",DisplayName: "Dummy"});   // add 2025.05.29 syif1380.lee

            vdCommon.debug("comboListCombined : " + JSON.stringify(comboListCombined));

            // // comboList의 데이터가 없을 경우 예외처리
            // if ( !Array.isArray(comboListCombined) || comboListCombined.length === 0 ){
            //     comboListCombined.push({ Name : "XXXXXX", DisplayName : "Item Not Found"});
            // }
            vdCommon.programEnd();

            return comboListCombined;

        } catch ( e ) {
            RuleOutputToUI = { Status : 'Error', Message : "Js Logic Error : " + e.message };
            return;
        }
    };

    /**
     * BOM Version Add > Validation (신규 2025.05.22)
     * @param {*} o9Params 
     * @returns 
     */
    var fn_validation_finalAdd = function(o9Params){
        try {
            const commonLib = require('o9.NSCM.commonLib');
            const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
            const vdUtil = new commonLib.VdUtil();
            
            vdCommon.setLogLevel("Debug");
            vdCommon.printParams(o9Params);

            // 파라미터 가져오기
            var parsedParams = JSON.parse(o9Params);
            var TupleList = parsedParams.TupleList;

            let returnString = "";
            let returnValue = 0;    // 0: 정상, 1: 오류메세지

            if(TupleList.length > 1){
                returnString = "1건만 선택해주세요.";
                RuleOutputToUI = { Status : 'Error', Message : returnString };
                returnValue = 1;    // 오류
            }
            vdCommon.programEnd();
            return returnValue;       // 0 : 정상, 1 : 오류

        } catch ( e ) {
            RuleOutputToUI = { Status : 'Error', Message : "Js Logic Error : " + e.message };
            return;
        }
    };

    /** Full BOM 생성 함수 */
    var fn_createFullBOM = function(param) {
        try {

            const commonLib = require('o9.NSCM.commonLib');
            const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
            const vdUtil = new commonLib.VdUtil();
            
            vdCommon.setLogLevel("Debug");
            vdCommon.debug("===================> fn_createFullBOM :: "+JSON.stringify(param,null, 2));

            var dimension = ["&CWVUI"
                            ,"[Location].[Location]"+vdUtil.fn_filterStr(param.Location)             // 그리드 row
                            ,"[Item].[Item]"+vdUtil.fn_filterStr(param.Item)                         // 그리드 row
                            ,"[To Location].[To Location]"+vdUtil.fn_filterStr(param.ToLocation)      // LCM : Code Map LCM 의 Location, LCM 이외 '-'
                            ,"[To Item].[To Item]"+vdUtil.fn_filterStr(param.ToItem)           // 팝업의 필드바인딩 LCM/KD Code
                            ,"[Item Material].[Item Material]"+vdUtil.fn_filterStr(param.ItemMaterial)    // LCM/KD Code(Item) 의 Item.Open Cell
                            ,"[BOM Info].[BOM Version]"+vdUtil.fn_filterStr(param.BOMVersion)            // WW + (max+1)
                            ,"[BOM Type].[BOM Type]"+vdUtil.fn_filterStr(param.BOMType)
                            ,"[Status].[Status].[Temp]"
                            ,"[BOM Status].[BOM Status].[NSCM Assy]"
                            ];
            // 중복체크
            if ( vdCommon.existMeasure(dimension,["Measure.[Full BOM_Valid]","Measure.[Full BOM_SOP SET Qty]"], "")) {
            RuleOutputToUI = { Status : 'Error', Message : "The data has already been registered." };
            return;
            }
            // Main MG 생성
            vdCommon.createMeasure(dimension, ['Measure.[Full BOM_Valid]        = "Y";'
                                            , 'Measure.[Full BOM_SOP SET Qty]   = 0;'
                                            , 'Measure.[Full BOM_Update Time]   = dateadd(Now(),9,"hour");'
                                            , 'Measure.[Full BOM_Creation Time] = dateadd(Now(),9,"hour");'
                            ]);
        } catch ( e ) {
            RuleOutputToUI = { Status : 'Error', Message : "Js Logic Error : " + e.message };
            return;
        }
    };

    var fn_finalAdd = function(o9Params) {
        try {
            const commonLib = require('o9.NSCM.commonLib');
            const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
            vdUtil = new commonLib.VdUtil();
            vdCommon.setLogLevel("Debug");            

            vdCommon.printParams(o9Params);
            let parsedParams = JSON.parse(o9Params);
            var TupleList = parsedParams.TupleList;
            LCMKDCode = parsedParams.LCMKDCode;

            // if( LCMKDCode.length === 1 && LCMKDCode[0] == "XXXXXX"){
            //     RuleOutputToUI = { Status : 'Error', Message : "LCM/KD Code : Item Not Found" };
            //     return;
            // }

            // 그리드 Row 선택 Data -----------------------------//
            var tupleLocation = TupleList[0].Location.Value;
            var tupleItem = TupleList[0].Item.Value;

            // LCM/KD Code > Item 의 속성 데이타----------------//
            var openCellData = "";
            var LCMKDCodeItemData = "";    // Full BOM > To Item
            var vBOMType = "", itemStage = "";

            //====================================================================================//
            // BOM Version 채번 : Location , Item 별 WW~
            //====================================================================================//
            var vBOMVersion = "";
            var where = 'where {'
                                +' &CWVUI'
                                +', [Location].[Location]'+ vdUtil.fn_filterStr(tupleLocation)
                                +', [Item].[Item]'+vdUtil.fn_filterStr(tupleItem)
                                +'}';
            var bomVersionQuery = vdCommon.selectList(['[BOM Info].[BOM Version].filter(#.Name startswith "WW")'], ["Measure.[Full BOM_Valid]"], where, "orderby [BOM Info].[BOM Version].[Name] desc", "");
            if ( bomVersionQuery.cs.rowCount == 0 ){
                vBOMVersion = "WW01";
            }else{
                var boVersionMaxData = bomVersionQuery.cs.row(0).cell(bomVersionQuery.cs.memberColumnIndex("BOM Info", "BOM Version")).Name;
                // 숫자 2자리 추출
                var number = parseInt(boVersionMaxData.slice(-2));
                if ( number >= 99 ){
                    vdCommon.debug(" number :: "+number);
                    RuleOutputToUI = { Status : 'Error', Message : "BOM Version : WW99 이상은 생성할 수 없습니다." };
                    return;
                }
                vBOMVersion = "WW"+ String(number + 1).padStart(2,"0");
            }

            vdCommon.debug("=========>vBOMVersion : "+vBOMVersion);
            // BOM Version 채번 종료
            
            var toLocationData = "";    // Full BOM > To Location
            for( let i=0; i<LCMKDCode.length; i++){
                LCMKDCodeItemData = LCMKDCode[i];
                
                if( LCMKDCodeItemData != null && LCMKDCodeItemData == "Dummy"){
                    vdCommon.debug("=========>DUMMY 생성 ");

                    var param = {Location:tupleLocation, Item:tupleItem, ToLocation:"-", ToItem:LCMKDCodeItemData
                                , ItemMaterial:"-", BOMVersion:"DUMMY", BOMType:"-"};
                    fn_createFullBOM(param);

                }else{
                    //====================================================================================//
                    // Open Cell - Item.Material, Item Stage 가져오기 (Item Stage : LCM/LCM이외 구분값) : LCM 이외 상세 구분은 ItemProduct(SKD/CKD/CRT)
                    //====================================================================================//
                    var openCellQuery = vdCommon.selectList(["[Item].[Item]"+vdUtil.fn_filterStr(LCMKDCodeItemData),"[Item].[Open Cell]","[Item].[Item Stage]"], [], "", "", "");
                    openCellData = openCellQuery.cs.row(0).cell(openCellQuery.cs.memberColumnIndex("Item", "Open Cell")).Name;
                    itemStage = openCellQuery.cs.row(0).cell(openCellQuery.cs.memberColumnIndex("Item", "Item Stage")).Name;
                    
                    // LCM
                    if(itemStage != null && itemStage == "LCM"){
                        vdCommon.debug(" itemStage :: LCM ");
                        // Code Map LCM 의 Location -> To Location 가져오기
                        var lcmWhere = 'where { &CWVUI , [Sub Location].[Sub Location]'+vdUtil.fn_filterStr(tupleLocation)
                                            +', [Item].[Item]'+vdUtil.fn_filterStr(LCMKDCodeItemData)
                                            +', Measure.[Code Map LCM_Valid Flag]=="Y" '
                                            +" }";
                        var toLocationQuery = vdCommon.selectList(["[Location].[Location]"], [], lcmWhere, "", "");
                        if ( toLocationQuery.cs.rowCount > 0 ){
                            for (let k=0; k < toLocationQuery.cs.rowCount; k++) {
                                toLocationData = toLocationQuery.cs.row(k).cell(toLocationQuery.cs.memberColumnIndex("Location", "Location")).Name;
                                vBOMType = "SOP Assy";

                                var param = {Location:tupleLocation, Item:tupleItem, ToLocation:toLocationData, ToItem:LCMKDCodeItemData
                                        , ItemMaterial:openCellData, BOMVersion:vBOMVersion, BOMType:vBOMType};
                                fn_createFullBOM(param);
                            
                            } // for > To location
                        }
                    // SKD, CKD, CRT
                    }else{
                        toLocationData = "-";   // LCM 이외는 "-" 로 사용 2025.05.26 신승호p요청
                        vBOMType = "Export Assy";

                        var param = {Location:tupleLocation, Item:tupleItem, ToLocation:toLocationData, ToItem:LCMKDCodeItemData
                                , ItemMaterial:openCellData, BOMVersion:vBOMVersion, BOMType:vBOMType};

                        fn_createFullBOM(param);
                    }
                }

            }

            vdCommon.programEnd();
              
        } catch ( e ) {
            RuleOutputToUI = { Status : 'Error', Message : "Js Logic Error : " + e.message };
            return;
        }
    };
    
    return {
        fn_category: fn_category
       ,fn_Inch : fn_Inch
       ,fn_Inchcascad : fn_Inchcascad
       ,fn_finalAdd : fn_finalAdd
       ,fn_validation_finalAdd : fn_validation_finalAdd
    };  
});

/* o9.NSCM.JSLCMKDPlanningBOM */
/* 2025.05.28 syif1380.lee  JS 전체 수정 */