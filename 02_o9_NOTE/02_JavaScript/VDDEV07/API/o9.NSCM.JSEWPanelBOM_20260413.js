define('o9.NSCM.JSEWPanelBOM', ['o9/data/query', 'o9/data/cellset', 'o9.NSCM.commonLibVD'], function(){

    /*--------------------------------------------------------------------------------------------------*/
    // 프로그램명       : o9.NSCM.JSEWPanelBOM
    // 화면명           : Panel BOM (EW)
    // Action Button    : EWPanelBOM
    // 최초생성         : 2025.07.31 / syif1380.lee
    /*--------------------------------------------------------------------------------------------------*/

    // fn_cLib 를 통해서 commonLib 를 생성 // 2026.03.26 공통적용변경
    var fn_cLib = function(name) {
        return new commonLib.VdCommon(name);
    }
    var fn_cUtil = function() {
        return new commonLib.VdUtil();
    }
        
    const commonLib = require('o9.NSCM.commonLibVD');   // 2026.03.26 공통적용변경
    const cUtil = fn_cUtil();                           // 2026.03.26 공통적용변경

    const programName = "o9.NSCM.JSEWPanelBOM";

    //================================= 공통 콤보 사용 ===============================//
    // Action Button : EWCommon
    // 
    //================================================================================//
    // Action Button : EWPanelBOM
    // Category : fn_cb_category
    // Inch     : fn_cb_inch
    // LCM/KD   : fn_cb_item
    //================================================================================//

	var fn_loadFunction = function(o9Params){
        const cLib = fn_cLib(programName + "." + arguments.callee.name);
        cLib.setLogLevel("Debug");

		try {
            let returnData = {};
            let obj = this;

            cLib.printParams(o9Params);

            // 파라메타 가져오기
            var parsedParams = JSON.parse(o9Params);
			var fbFuncName = parsedParams.fbFuncName;

            if ( functionMap[fbFuncName] == undefined ) {
                return { "Code" : 1, "Msg" : "No Function" };
            }

            var rtn = functionMap[fbFuncName](parsedParams);

            cLib.programEnd();
            return rtn;
        } catch ( e ) {
            cLib.error(e.message);
            return { "Code" : -1, "Msg" : e.message };
        }
	};

    // LCM / SKD / CKD / CRT / CPT(예정)  ==> 사용안함 (2025.08.12) 삭제예정, 화면에서 pickList 사용
    var fn_cb_category = function(parsedParams){
        const cLib = fn_cLib(programName + "." + arguments.callee.name);
        cLib.setLogLevel("Debug");

        try {
            cLib.debug("parsedParams :: "+JSON.stringify(parsedParams));
            cLib.debug("parsedParams.fbParams :: "+JSON.stringify(parsedParams.fbParams));

            // LCM
            var resultLcm = cLib.selectList(["[Item].[Item Stage].[LCM]"], [], "", "", "");
            var comboListLcm = cLib.fn_makeCombo(resultLcm, {DimName : "Item", DimAttbName : "Item Stage", Sort : "DisplayName", existAll : false});
            cLib.printCsData(resultLcm, 3);
            cLib.debug("comboListLcm : " + JSON.stringify(comboListLcm));

            // SKD, CKD, CRT, CPT(예정)
            var resultEtc = cLib.selectList(["&ItemKDProductType"], [], "", "", "");
            var comboListEtc = cLib.fn_makeCombo(resultEtc, {DimName : "Item", DimAttbName : "ProductType", Sort : "DisplayName", existAll : false});
            cLib.printCsData(resultEtc, 3);
            cLib.debug("comboListEtc : " + JSON.stringify(comboListEtc));

            // combo Data 합침
            var comboList = [...comboListLcm, ...comboListEtc];

            cLib.debug("comboList : " + JSON.stringify(comboList));
            cLib.programEnd();

            return { "Code" : 0, "Msg" : "", "Rows" : comboList };
        } catch ( e ) {
            cLib.error(e.message);
            return { "Code" : -1, "Msg" : e.message };
        }
    };

    var fn_categoryList = function(paramCategory){
        let fbCategory = paramCategory;     // UI Param : "fbParams":{"category":"LCM,CKD,CRT"}
        let categoryParamList = fbCategory.split("^").map(item => item.trim());

        let categoryArray = [];
        if( categoryParamList.includes("LCM") ){
        }
        if( categoryParamList.includes("CKD") ){
            categoryArray.push("CKD","SKD");
        }
        if( categoryParamList.includes("CRT") ){
            categoryArray.push("CRT","CPT");
        }

        return categoryArray;
    };

    // Category별 Inch
    var fn_cb_inch = function(parsedParams){
        const cLib = fn_cLib(programName + "." + arguments.callee.name);
        cLib.setLogLevel("Debug");

        try {
            cLib.debug("parsedParams.fbParams :: "+JSON.stringify(parsedParams.fbParams));

            // category 는 multi 로 옴
            let fbCategory = parsedParams.fbParams["category"]; // UI Param : "fbParams":{"category":"LCM^CKD^CRT"}
            let categoryParamList = fbCategory.split("^").map(item => item.trim());

            let categoryArray = fn_categoryList(fbCategory);

            cLib.debug("## categoryArray : "+JSON.stringify(categoryArray));
            // cLib.debug("####### categoryArray :: "+categoryArray);  // ####### categoryArray :: CKD,SKD,CRT,CPT

            // let comboList;
            let comboListLcm = [];
            let comboListEtc = [];
            if( categoryParamList.includes("LCM")){
                var result = cLib.selectList(["[Item].[Item Stage].[LCM].relatedmembers([Inch])"], [], "", "", "");
                cLib.printCsData(result, 3);
                comboListLcm = cLib.fn_makeCombo(result, {DimName : "Item", DimAttbName : "Inch", Sort : "DisplayName", existAll : false, existHyphen : true});
                cLib.debug("ComboData LCM: " + JSON.stringify(comboListLcm));
            }
            if( categoryParamList.includes("CKD") || categoryParamList.includes("CRT") ){
                var result = cLib.selectList(["&ItemKDProductType"+cUtil.fn_filterStr(categoryArray)+".relatedmembers([Inch])"], [], "", "", "");
                comboListEtc = cLib.fn_makeCombo(result, {DimName : "Item", DimAttbName : "Inch", Sort : "DisplayName", existAll : false, existHyphen : true});
                cLib.printCsData(result, 3);
                cLib.debug("ComboData ETC : " + JSON.stringify(comboListEtc));
            }

            // combo Data 합침
            let combined = [...(comboListLcm || []), ...(comboListEtc || [])].filter(item => item && item.Name); // Name 없는 값 제거
            // cLib.debug("combined 합침 : " + JSON.stringify(combined));

            // 중복 제거 Name기준
            let comboList = Array.from(new Map(combined.map(item => [item.Name, item])).values());

            // cLib.debug("comboList 중복제거 : " + JSON.stringify(comboList));

            // 정렬(Name 기준)
            // comboList.sort((x,y) => x.Name.localeCompare(y.Name));
            comboList.sort((a,b) => {
                const isNumA = !isNaN(a.Name);
                const isNumB = !isNaN(b.Name);

                // All 을 가장 앞으로
                if( a.Name === "All") return -1;
                if( b.Name === "All") return 1;

                // 숫자 vs 숫자 -> 숫자 오름차순
                if( isNumA && isNumB ) {
                    return Number(a.Name) - Number(b.Name);
                }

                // 숫자 vs 문자 -> 숫자 먼저
                if( isNumA && !isNumB) return -1;
                if( !isNumA && isNumB) return 1;

                // 문자 vs 문자 -> 알파벳 순서
                return a.Name.localeCompare(b.Name);
            });

            cLib.debug("ComboData 최종 : " + JSON.stringify(comboList));

            cLib.programEnd();

            return { "Code" : 0, "Msg" : "", "Rows" : comboList };
        } catch ( e ) {
            cLib.error(e.message);
            return { "Code" : -1, "Msg" : e.message };
        }
    };

    // LCM/KD Item
    // ItemCategory 추가 LCM/KD 코드에 따른 구분을 추가 : 신승호P요청,2025.12.17
    /**
     * LCM/KD Item
     * ItemCategory 추가 LCM/KD 코드에 따른 구분을 추가 : 신승호P요청,2025.12.17
     * { "fbFuncName" : "fn_cb_item", "fbParams" : {"category":"LCM^CKD","[Location].[Location]":"P105","[Item].[Inch]":"40"}}
     * @param {*} parsedParams 
     * @returns 
     */
    var fn_cb_item = function(parsedParams){
        const cLib = fn_cLib(programName + "." + arguments.callee.name);
        cLib.setLogLevel("Debug");

        try {
            cLib.debug("parsedParams.fbParams :: "+JSON.stringify(parsedParams.fbParams));

            // let fbCategory  = parsedParams.fbParams["category"];        // UI Param
            let fbLocation  = parsedParams.fbParams["[Location].[Location]"];   // Plant
            let fbInch      = parsedParams.fbParams["[Item].[Inch]"];
            let inchParamList = (fbInch || "").split("^").map(item => item.trim()); // null or undefined 일 경우 체크

            // category 는 multi 로 옴
            let fbCategory = parsedParams.fbParams["category"]; // UI Param : "fbParams":{"category":"LCM,CKD,CRT"}
            let categoryParamList = (fbCategory || "").split("^").map(item => item.trim());
            let categoryArray = fn_categoryList(fbCategory);

            //===========================================================================================================================================//
            // LCM일 경우 : BOD Item 의 유효한(BOD Item Eff Startdate/Enddate) Item.Item 을 가져온다.
            // itemName 
            //===========================================================================================================================================//
            cLib.debug("### BOD Item 의 유효한 Item 가져온다. -- start");
            var itemNameLcm = [];
            if( categoryParamList.includes("LCM")){
                var whereBODItemLCM = 'where {'
                                    +' &CWVUI'
                                    // +', [Location].[Location]'+ cUtil.fn_filterStr(fbLocation)
                                    +', [Sub Location].[Sub Location]'+ cUtil.fn_filterStr(fbLocation)     // 2026.03.04 변경 신승호P요청
                                    +', [Item].[Item Stage].[LCM]'
                                    +', (coalesce(Measure.[BOD Item_Eff Startdate],DATEADD(Now(),-1,"Day")) < now() && coalesce(Measure.[BOD Item_Eff Enddate],DATEADD(Now(),1,"Day")) > now() )'
                                    +'}';
                var resultBODItemLCM = cLib.selectList(["[Item].[Item]"], [], whereBODItemLCM, "", "");     // LCM
                cLib.printCsData(resultBODItemLCM, 3);

                if ( resultBODItemLCM.cs.rowCount > 0 ){
                    for (let i=0; i < resultBODItemLCM.cs.rowCount; i++) {
                        itemNameLcm.push(resultBODItemLCM.cs.row(i).cell(resultBODItemLCM.cs.memberColumnIndex("Item", "Item")).Name);
                    }
                }
            }
            //===========================================================================================================================================//
            // 유효한 BOD Item 에서 조회된 Item 을 조건에 추가한다.
            //===========================================================================================================================================//
            cLib.debug("### BOD Item 에 Item 조건 추가 -- start");

            // LCM > Code Map LCM
            let comboListLcm = [];
            if( categoryParamList.includes("LCM")){

                let whereLcm = 'where {'
                            +' &CWVUI'
                            +', [Sub Location].[Sub Location]'+ cUtil.fn_filterStr(fbLocation)
                            +', Measure.[Code Map LCM_Valid Flag] == "Y" '
                            // +', [Item].[Item Stage]'+ cUtil.fn_filterStr(categoryArray)
                            +', [Item].[Item Stage].[LCM]'
                            +', [Item].[Inch]'+ cUtil.fn_filterStr(inchParamList)
                            +'}';

                var resultLcm = cLib.selectList(["[Item].[Item]"+ cUtil.fn_filterStr(itemNameLcm),"[Item].[Description]"], [], whereLcm, "", "");
                cLib.printCsData(resultLcm, 3);
                comboListLcm = cLib.fn_makeCombo(resultLcm, {DimName : "Item", DimAttbName : "Item", Sort : "DisplayName", DimDescAttbName : "Description", existAll : false});

                if( comboListLcm.length > 0){
                    comboListLcm = comboListLcm.map(item => ({ ...item, ItemCategory: "LCM"}));
                }
                cLib.debug("### comboListLcm : " + JSON.stringify(comboListLcm));
            }
            // SKD, CKD, CRT > BOD Item
            let comboListEtc = [];
            if( categoryParamList.includes("CKD") || categoryParamList.includes("CRT") ){
                let whereEtc = 'where {'
                            +' &CWVUI'
                            +', [Location].[Location]'+ cUtil.fn_filterStr(fbLocation)
                            +', &ItemKDProductType'+ cUtil.fn_filterStr(categoryArray)
                            +', [Item].[Inch]'+ cUtil.fn_filterStr(inchParamList)
                            +', (coalesce(Measure.[BOD Item_Eff Startdate],DATEADD(Now(),-1,"Day")) < now() && coalesce(Measure.[BOD Item_Eff Enddate],DATEADD(Now(),1,"Day")) > now() )'
                            +'}';

                // var resultEtc = cLib.selectList(["[Item].[Item]"+ cUtil.fn_filterStr(itemNameEtc),"[Item].[Description]"], [], whereEtc, "", "");
                var resultEtc = cLib.selectList(["[Item].[Item]","[Item].[Description]"], [], whereEtc, "", "");
                cLib.printCsData(resultEtc, 3);
                comboListEtc = cLib.fn_makeCombo(resultEtc, {DimName : "Item", DimAttbName : "Item", Sort : "DisplayName", DimDescAttbName : "Description", existAll : false});
                
                if( comboListEtc.length > 0){
                    comboListEtc = comboListEtc.map(item => ({ ...item, ItemCategory: "CKD"}));
                }
                cLib.debug("### comboListEtc : " + JSON.stringify(comboListEtc));
            }

            // combo Data 합침
            let comboList = [...(comboListLcm || []), ...(comboListEtc || [])].filter(item => item && item.Name); // Name 없는 값 제거

            // 조회된 콤보 데이터가 있을 경우
            if( comboList.length > 0){
                // Name 을 오름차순 정렬 (대소문자 구분없이 정렬)
                comboList.sort((a,b) => a.Name.localeCompare(b.Name));

                // ItemCategory 추가 2025.12.17
                comboList.unshift({Name : "Dummy",DisplayName: "Dummy", ItemCategory: "LCM"});   // add 2025.05.29 syif1380.lee

                cLib.debug("### comboList : " + JSON.stringify(comboList));
                cLib.programEnd();
                return { "Code" : 0, "Msg" : "", "Rows" : comboList };
            }else{
                comboList.unshift({Name : "Dummy",DisplayName: "Dummy", ItemCategory: "LCM"});   // add 2025.05.29 syif1380.lee

                // return { "Code" : 1, "Msg" : "Plant : "+fbLocation +"", "Rows" : comboList };
                return { "Code" : 1, "Msg" : `해당 Plant [ ${fbLocation} ] 에 등록된 BOD Item 이 없습니다.`, "Rows" : comboList };
            }

            // return { "Code" : 0, "Msg" : "", "Rows" : comboList };
        } catch ( e ) {
            cLib.error(e.message);
            return { "Code" : -1, "Msg" : e.message };
        }
    };

    /**
     * fn_save
     * 
     * @param {*} parsedParams 
     * @returns 
     */
    var fn_save = function(parsedParams){
        const cLib = fn_cLib(programName + "." + arguments.callee.name);
        cLib.setLogLevel("Debug");

        try {
            cLib.debug("parsedParams :: "+JSON.stringify(parsedParams));

            insertData = [];
            updateData = [];
            deleteData = [];

            for ( var i=0; i<parsedParams.fbGridRows.length; i++){

                let row = parsedParams.fbGridRows[i];
                let rowstatus = row["rowstatus"];
                row["rowmsg"] = null;

                cLib.debug("rowstatus :: "+rowstatus);

                let dimension = [];
                dimension.push(cUtil.fn_qDimVersionName(parsedParams));
                dimension.push(cUtil.fn_qDim(row, "[Location].[Location]"));
                dimension.push(cUtil.fn_qDim(row, "[Item].[Item]"));
                dimension.push(cUtil.fn_qDim(row, "[To Location].[To Location]"));
                dimension.push(cUtil.fn_qDim(row, "[To Item].[To Item]"));
                dimension.push(cUtil.fn_qDim(row, "[Item Material].[Item Material]"));
                dimension.push(cUtil.fn_qDim(row, "[BOM Info].[BOM Version]"));
                dimension.push(cUtil.fn_qDim(row, "[Status].[Status]"));
                dimension.push(cUtil.fn_qDim(row, "[BOM Type].[BOM Type]"));
                dimension.push(cUtil.fn_qDim(row, "[BOM Status].[BOM Status]"));
                
                let fbStatus = row["[Status].[Status]"];
                let fbBOMStatus = row["[BOM Status].[BOM Status]"];

                // 기존 data 중복여부에 대한 체크
                if( rowstatus == "C") {
                    //================================================================================================================================//
                    // Full BOM : create 
                    //================================================================================================================================//
                    fn_create(row);

                } else if( rowstatus == "U") {
                    //================================================================================================================================//
                    // Full BOM : update 
                    //================================================================================================================================//
                    let measure = [];
                    measure.push(cUtil.fn_qMeaUpdateUserName("Measure.[Full BOM_Updated By]"));
                    measure.push(cUtil.fn_qMeaUpdateTime("Measure.[Full BOM_Update Time]"));

                    if( fbStatus != "COM" ){
                        measure.push(cUtil.fn_qMeaStr(row, "Measure.[Full BOM_Valid]"));
                    }

                    if( fbBOMStatus == "Dash KD" || fbBOMStatus == "NSCM KD"){
                        measure.push(cUtil.fn_qMeaStr(row, "Measure.[Full BOM_Eff Startdate]"));
                        measure.push(cUtil.fn_qMeaStr(row, "Measure.[Full BOM_Eff Enddate]"));
                    }

                    cLib.updateMeasure(dimension, measure);

                } else if( rowstatus == "D") {
                    //================================================================================================================================//
                    // Full BOM : Delete 
                    //================================================================================================================================//
                    cLib.deleteMeasure(dimension, "Full BOM");
                }

            } // end for

            cLib.programEnd();

            return { "Code" : 0, "Msg" : "", "Rows" : "" };

        } catch ( e ) {
            cLib.error(e.message);
            return { "Code" : -1, "Msg" : e.message };
        }
    };

    // Create 로직
    var fn_create = function(row){
        const cLib = fn_cLib(programName + "." + arguments.callee.name);
        cLib.setLogLevel("Debug");
        try {
            // cLib.debug("parsedParams :: "+JSON.stringify(parsedParams));

            let fbLocation = row["[Location].[Location]"];
            let fbItem = row["[Item].[Item]"];
            let fbToItem = row["[To Item].[To Item]"];

            // let LCMKDCode = parsedParams.LCMKDCode; // 팝업에서 선택한 LCM/KD Item
            let LCMKDCode = fbToItem; // 팝업에서 선택한 LCM/KD Item => "LCMKDCode":"item01^item02^item03" => ^ 로 구분
            let LCMKDCodeArray = (LCMKDCode || "").split("^").map(item => item.trim());
            // cLib.debug("############## LCMKDCodeArray.length >>> " + LCMKDCodeArray.length);

            // LCM/KD Code > Item 의 속성 데이타----------------//
            let openCellData = "";
            let LCMKDCodeItemData = "";    // Full BOM > To Item
            let vBOMType = "", itemStage = "";

            //====================================================================================//
            // BOM Version 채번 : Location , Item 별 WW~
            //====================================================================================//
            let vBOMVersion = "";
            let where = 'where {'
                                +' &CWVUI'
                                +', [Location].[Location]'+ cUtil.fn_filterStr(fbLocation)
                                +', [Item].[Item]'+cUtil.fn_filterStr(fbItem)
                                +'}';
            let bomVersionQuery = cLib.selectList(['[BOM Info].[BOM Version].filter(#.Name startswith "WW")'], ["Measure.[Full BOM_Valid]"], where, "orderby [BOM Info].[BOM Version].[Name] desc", "");
            if ( bomVersionQuery.cs.rowCount == 0 ){
                vBOMVersion = "WW01";
            }else{
                let boVersionMaxData = bomVersionQuery.cs.row(0).cell(bomVersionQuery.cs.memberColumnIndex("BOM Info", "BOM Version")).Name;
                // 숫자 2자리 추출
                let number = parseInt(boVersionMaxData.slice(-2));
                if ( number >= 99 ){
                    cLib.debug(" number :: "+number);
                    // RuleOutputToUI = { Status : 'Error', Message : "BOM Version : WW99 이상은 생성할 수 없습니다." };
                    // return;
                    return { "Code" : -1, "Msg" : "BOM Version : WW99 이상은 생성할 수 없습니다." };
                }
                vBOMVersion = "WW"+ String(number + 1).padStart(2,"0");
            }

            // cLib.debug("=========>vBOMVersion : "+vBOMVersion);
            // BOM Version 채번 종료
            
            let toLocationData = "";    // Full BOM > To Location
            for( let j=0; j<LCMKDCodeArray.length; j++){
                LCMKDCodeItemData = LCMKDCodeArray[j];
                cLib.debug("#####################=========>LCMKDCodeItemData ::  "+LCMKDCodeItemData);
                
                if( LCMKDCodeItemData != null && LCMKDCodeItemData == "Dummy"){

                    let param = {Location:fbLocation, Item:fbItem, ToLocation:"-", ToItem:LCMKDCodeItemData
                                , ItemMaterial:"-", BOMVersion:"DUMMY", BOMType:"-"};
                    fn_createFullBOM(param, row);

                }else{
                    //====================================================================================//
                    // Open Cell - Item.Material, Item Stage 가져오기 (Item Stage : LCM/LCM이외 구분값) : LCM 이외 상세 구분은 ItemProduct(SKD/CKD/CRT)
                    //====================================================================================//
                    let openCellQuery = cLib.selectList(["[Item].[Item]"+cUtil.fn_filterStr(LCMKDCodeItemData),"[Item].[Open Cell]","[Item].[Item Stage]"], [], "", "", "");
                    openCellData = openCellQuery.cs.row(0).cell(openCellQuery.cs.memberColumnIndex("Item", "Open Cell")).Name;
                    itemStage = openCellQuery.cs.row(0).cell(openCellQuery.cs.memberColumnIndex("Item", "Item Stage")).Name;
                    
                    // LCM
                    if(itemStage != null && itemStage == "LCM"){
                        cLib.debug(" itemStage :: LCM ");
                        // Code Map LCM 의 Location -> To Location 가져오기
                        let lcmWhere = 'where { &CWVUI , [Sub Location].[Sub Location]'+cUtil.fn_filterStr(fbLocation)
                                            +', [Item].[Item]'+cUtil.fn_filterStr(LCMKDCodeItemData)
                                            +', Measure.[Code Map LCM_Valid Flag]=="Y" '
                                            +" }";
                        let toLocationQuery = cLib.selectList(["[Location].[Location]"], [], lcmWhere, "", "");

                        if ( toLocationQuery.cs.rowCount > 0 ){
                            for (let k=0; k < toLocationQuery.cs.rowCount; k++) {
                                toLocationData = toLocationQuery.cs.row(k).cell(toLocationQuery.cs.memberColumnIndex("Location", "Location")).Name;
                                vBOMType = "SOP Assy";

                                let param = {Location:fbLocation, Item:fbItem, ToLocation:toLocationData, ToItem:LCMKDCodeItemData
                                        , ItemMaterial:openCellData, BOMVersion:vBOMVersion, BOMType:vBOMType};
                                fn_createFullBOM(param, row);
                            
                            } // for > To location
                        }
                    // SKD, CKD, CRT
                    }else{
                        toLocationData = "-";   // LCM 이외는 "-" 로 사용 2025.05.26 신승호p요청
                        vBOMType = "Export Assy";

                        let param = {Location:fbLocation, Item:fbItem, ToLocation:toLocationData, ToItem:LCMKDCodeItemData
                                , ItemMaterial:openCellData, BOMVersion:vBOMVersion, BOMType:vBOMType};

                        fn_createFullBOM(param, row);
                    }
                }

            }

        } catch ( e ) {
            cLib.error(e.message);
            return { "Code" : -1, "Msg" : e.message };
        }
    };

    // Params : {"Location":"P306","Item":"QN65QN700CFXZX","ToLocation":"P306LCD","ToItem":"BN95-02681F","ItemMaterial":"BN96-39266A","BOMVersion":"WW01","BOMType":"SOP Assy"}
    var fn_createFullBOM = function(Params, row){
        const cLib = fn_cLib(programName + "." + arguments.callee.name);
        cLib.setLogLevel("Debug");
        try {
            cLib.debug(" fn_createFullBOM Params :: "+JSON.stringify(Params));
            cLib.debug(" fn_createFullBOM row :: "+JSON.stringify(row));

            fbBOMStatus = row["[BOM Status].[BOM Status]"];
            
            let dimension = ["&CWVUI"
                        ,"[Location].[Location].[" + Params.Location + "]"
                        ,"[Item].[Item].[" + Params.Item + "]"
                        ,"[To Location].[To Location].[" + Params.ToLocation + "]"
                        ,"[To Item].[To Item].[" + Params.ToItem + "]"
                        ,"[Item Material].[Item Material].[" + Params.ItemMaterial + "]"
                        ,"[BOM Info].[BOM Version].[" + Params.BOMVersion + "]"
                        ,"[BOM Type].[BOM Type].[" + Params.BOMType + "]"
                        ,"[Status].[Status].[Temp]"
                        ,"[BOM Status].[BOM Status].[" + fbBOMStatus + "]"  // 2025.12.17 변경
                        // ,"[BOM Status].[BOM Status].[NSCM Assy]"
                        ];

            // 중복체크
            if ( cLib.existMeasure(dimension,["Measure.[Full BOM_Valid]","Measure.[Full BOM_SOP SET Qty]"], "")) {
                return { "Code" : -1, "Msg" : "The data has already been registered." };
            }

            let measureCreate = [];
            measureCreate.push(cUtil.fn_qMeaUpdateUserName("Measure.[Full BOM_Created By]"));
            measureCreate.push(cUtil.fn_qMeaUpdateTime("Measure.[Full BOM_Creation Time]"));

            let measureUpdate = [];
            measureUpdate.push(cUtil.fn_qMeaUpdateUserName("Measure.[Full BOM_Updated By]"));
            measureUpdate.push(cUtil.fn_qMeaUpdateTime("Measure.[Full BOM_Update Time]"));
            measureUpdate.push('Measure.[Full BOM_Valid] = "Y";');
            measureUpdate.push('Measure.[Full BOM_SOP SET Qty]   = 0;');

            if( fbBOMStatus == "Dash KD" || fbBOMStatus == "NSCM KD"){
                measureUpdate.push(cUtil.fn_qMeaStr(row, "Measure.[Full BOM_Eff Startdate]"));
                measureUpdate.push(cUtil.fn_qMeaStr(row, "Measure.[Full BOM_Eff Enddate]"));
            }

            // Main MG 생성
            cLib.createMeasure(dimension, measureCreate);
            cLib.updateMeasure(dimension, measureUpdate);

        } catch ( e ) {
            cLib.error(e.message);
            return { "Code" : -1, "Msg" : e.message };
        }
    };

    // Mapping 함수 정의, 마지막에 선언을 해야 함수를 정상적으로 인식함
    const functionMap = {
        "fn_save"               : fn_save
       ,"fn_cb_category"        : fn_cb_category
       ,"fn_cb_inch"            : fn_cb_inch
       ,"fn_cb_item"            : fn_cb_item
    };

    return {
        fn_loadFunction : fn_loadFunction
    };

});

/*--------------------------------------------------------------------------------------------------*/
/* 프로그램명 : o9.NSCM.JSEWPanelBOM
    화면명 : Panel BOM (EW)
    Action Button : EWPanelBOM
    [history]
    2025.08.12 | syif1380.lee | category 멀티선택 변경, combo 조건 변경
    2025.09.11 | syif1380.lee | combo 멀티조건 "," -> "^" 로 변경
                                create 로직 변경 (LCMCode 멀티조건 및 변수명 변경)
    2025.09.24 | syif1380.lee | fn_update() : Measure.[Full BOM_Update Time] 추가
    2025.09.25 | syif1380.lee | 저장시 Measure.[Full BOM_Updated By] , Measure.[Full BOM_Created By] 추가
    2025.10.30 : 공통소스 반영
    2025.11.06 : syif1380.lee : fn_qMeaUpdateUser() => fn_qMeaUpdateUserName() 로 변경
    2025.12.17 : syif1380.lee : fn_save() : 저장시 메저 추가 Measure.[Full BOM_Eff Startdate], Measure.[Full BOM_Eff Enddate]
                                : fn_cb_item() : ItemCategory 구분자 추가(LCM/KD 코드에 따른) 신승호P요청
    2025.12.18 : syif1380.lee : fn_cb_item() : combo data 없을 경우 리턴 메세지 추가
    2026.03.04 : syif1380.lee : Item.[A1] -> Item.[Inch] 로 변경 
    2026.03.04 : syif1380.lee : fn_cb_item() : LCM 일떄 첫번째 쿼리 [Location].[Location] -> [Sub Location].[Sub Location] 으로 변경 (신승호P요청)
    2026.03.26 : commonLib 선언 부분 변경 및 공통함수 이름 변경
*/
/*--------------------------------------------------------------------------------------------------*/