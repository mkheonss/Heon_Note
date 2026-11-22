define('o9.NSCM.JSLCMSOPAdjust', ['o9/data/query', 'o9/data/cellset', 'o9.NSCM.commonLib'], function(){

    const programName = "o9.NSCM.JSLCMSOPAdjust";
    const MPHorizonWeek1 = "&Week1MPHorizon";

    // Sub Location => From Site , Location => To Site 로 타이틀 변경 2025.03.20 노보람p 요청
    // From Site
    var fn_subLocationCombo = function(o9Params){
        try {
            const commonLib = require('o9.NSCM.commonLib');
            const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
            const vdUtil = new commonLib.VdUtil();

            vdCommon.setLogLevel("Debug");
            let parsedParams = JSON.parse(o9Params);
            // let fbViewSubLocation = parsedParams.fbViewSubLocation;  // View Filter 의 Sub Location (From Site) 추가 2025.03.20
            let fbViewSubLocationGroup4 = parsedParams.fbViewSubLocationGroup4;     // View Filter 의 Sub Location Group4(From Site) 추가 2025.04.07

            // dimension, measure, where, orderby, limit
            // BOD List 정보 가져오기 (임재민p, 노보람p 요청 - 2025.04.17)
            var where = 'where {'
            +' &CWVUI'
            +',  Measure.[BOD List_BOD Valid]== "Y" '
            +'}';
            var result = vdCommon.selectList(["&NSUISubSiteGrp4LCMView"+ vdUtil.fn_filterStr(fbViewSubLocationGroup4)+".relatedmembers([Sub Location])"],
                                             "", // measure
                                             where, // where
                                             "",    // orderby
                                             "");   // limit

            // var where = "";
            // 수정 2025.04.10 
            // var result = vdCommon.selectList(["[Sub Location].[Sub Location Group4]"+ vdUtil.fn_filterStr(fbViewSubLocationGroup4)+".relatedmembers([Sub Location])"],
            // var result = vdCommon.selectList(["&NSUISubSiteGrp4LCMView"+ vdUtil.fn_filterStr(fbViewSubLocationGroup4)+".relatedmembers([Sub Location])"],
            //                                  [],    // measure
            //                                  where,    // where
            //                                  "",    // orderby
            //                                  "");   // limit
            vdCommon.printCsData(result, 3);

            var comboList = vdCommon.fn_makeCombo(result, {DimName : "Sub Location", DimAttbName : "Sub Location", Sort : "DisplayName", existAll : false, isDisplayNameWithCode : true});
            vdCommon.debug("ComboData : " + JSON.stringify(comboList));

            vdCommon.programEnd();

            return comboList;
        } catch ( e ) {
            RuleOutputToUI = { Status : 'Error', Message : "Js Logic Error : " + e.message };
            return;
        }
    };

    // To Site
    var fn_locationCombo = function(o9Params){
        try {
            const commonLib = require('o9.NSCM.commonLib');
            const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
            const vdUtil = new commonLib.VdUtil();

            vdCommon.setLogLevel("Debug");
            let parsedParams = JSON.parse(o9Params); 
            let fbLocation = parsedParams.fbLocation;           // Site(To)
            let fbSubLocation = parsedParams.fbSubLocation;     // Site(From)

            // BOD List 정보 가져오기 (임재민p, 노보람p 요청 - 2025.04.17)
            var where = 'where {'
            +' &CWVUI'
            +', [Location].[Location]'+ vdUtil.fn_filterStr(fbSubLocation)
            // +', [Sub Location].[Sub Location]'+ vdUtil.fn_filterStr(fbLocation)
            +',  Measure.[BOD List_BOD Valid]== "Y" '
            +'}';
            var result = vdCommon.selectList(["&MFStageSETSubLocation.unionwith(&MFStageKDSubLocation)"],
                                             "", // measure
                                             where, // where
                                             "",    // orderby
                                             "");   // limit
            
            // // dimension, measure, where, orderby, limit
            // var result = vdCommon.selectList(["&MFStageSETLocation"],
            //                                  [],    // measure
            //                                  "",    // where
            //                                  "",    // orderby
            //                                  "");   // limit
            vdCommon.printCsData(result, 3);

            var comboList = vdCommon.fn_makeCombo(result, {DimName : "Sub Location", DimAttbName : "Sub Location", Sort : "DisplayName", existAll : false, isDisplayNameWithCode : true});
            vdCommon.debug("ComboData : " + JSON.stringify(comboList));

            vdCommon.programEnd();

            return comboList;
        } catch ( e ) {
            RuleOutputToUI = { Status : 'Error', Message : "Js Logic Error : " + e.message };
            return;
        }
    };    

    var fn_toTransModeCombo = function(o9Params){
        try {
            const commonLib = require('o9.NSCM.commonLib');
            const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
            const vdUtil = new commonLib.VdUtil();
            vdCommon.setLogLevel("Debug");
            
            let parsedParams = JSON.parse(o9Params); 
            let fbLocation = parsedParams.fbLocation;           // Site(To)
            let fbSubLocation = parsedParams.fbSubLocation;     // Site(From)

            // var result = vdCommon.selectList(["&NSUITransModeView"],    // [Trans Mode].[Trans Mode].filter(#.Name in {"AIR","VESSEL","TRUCK"})
            //                                  [], // measure
            //                                  "", // where
            //                                  "orderby [Trans Mode].[Trans Mode].Name desc",    // orderby
            //                                  "");   // limit

            // BOD List 정보 가져오기 (임재민p, 노보람p 요청 - 2025.04.17)
            var where = 'where {'
            +' &CWVUI'
            +', [Location].[Location]'+ vdUtil.fn_filterStr(fbSubLocation)
            +', [Sub Location].[Sub Location]'+ vdUtil.fn_filterStr(fbLocation)
            +',  Measure.[BOD List_BOD Valid]== "Y" '
            +'}';
            var result = vdCommon.selectList(["&NSUITransModeView"],    // [Trans Mode].[Trans Mode].filter(#.Name in {"AIR","VESSEL","TRUCK"})
                                             "", // measure
                                             where, // where
                                             "orderby [Trans Mode].[Trans Mode].Name desc",    // orderby
                                             "");   // limit
            vdCommon.printCsData(result, 3);

            // Sort : null 로 해야 orderby 정의한 대로 Data 나옴 (2025.02.14)
            var comboList = vdCommon.fn_makeCombo(result, {DimName : "Trans Mode", DimAttbName : "Trans Mode", Sort : null, existAll : false, isDisplayNameWithCode : false});
            
            vdCommon.debug("ComboData : " + JSON.stringify(comboList));

            vdCommon.programEnd();

            return comboList;
        } catch ( e ) {
            RuleOutputToUI = { Status : 'Error', Message : "Js Logic Error : " + e.message };
            return;
        }
    };

    // Item 
    // Item > Prod Item > Cell Code 순서 변경 (2025.05.07 노보람p요청)
    var fn_toItemCombo = function(o9Params){
        try {
            const commonLib = require('o9.NSCM.commonLib');
            const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
            const vdUtil = new commonLib.VdUtil();
            vdCommon.setLogLevel("Debug");
            
            let parsedParams = JSON.parse(o9Params); 
            let fbLocation = parsedParams.fbLocation;
            let fbSubLocation = parsedParams.fbSubLocation;
            // let fbItemMaterial    = parsedParams.fbItemMaterial;

            // BOM 정보 가져오기 (임재민p, 노보람p 요청 - 2025.04.17)
            var where = 'where {'
            +' &CWVUI'
            +', [Location].[Location]'+ vdUtil.fn_filterStr(fbSubLocation)          // From Site
            +', &NSUISiteGrp3LCMView '
            +', Item.[Item Stage].[OPEN_CELL] '
            // +', [Item].[Item]'+ vdUtil.fn_filterStr(fbItemMaterial)                 // Cell code (순서 변경으로 삭제 2025.05.07)
            +', [BOM Info].[BOM ID] , Measure.[BOM Comp_Valid Flag] == true '
            +'}';
            var result = vdCommon.selectList(["[BOM Info].[Item]"],
                                                "",     // measure
                                                where,  // where
                                                "",     // "orderby [Item].[Item].Name desc",    // orderby
                                                "");    // limit

            // var where = 'where {'
            //                 +' &CWVUI'
            //                 +', [Location].[Location]'+ vdUtil.fn_filterStr(fbLocation)
            //                 +', [Sub Location].[Sub Location]'+ vdUtil.fn_filterStr(fbSubLocation)
            //                 +', [Trans Mode].[Trans Mode]'+ vdUtil.fn_filterStr(fbTPMode)
            //                 +'}';

            // // &LCMItem 중 BOD Item 에 없는 Item.Item List
            // var result = vdCommon.selectList(["&LCMItem"],
            //                                 ["Measure.[BOD Item_Asn]"
            //                                 ,"Measure.[BOD Item_Cur Status]"
            //                                 ,"Measure.[BOD Item_BOD Frozen]"
            //                                 ,"Measure.[BOD Item_Eff Startdate]"
            //                                 ,"Measure.[BOD Item_Eff Enddate]"
            //                                 ,"Measure.[BOD Item_Min Lot Qty]"
            //                                 ,"Measure.[BOD Item_Multi Lot Qty]"
            //                                 ],    // measure
            //                                 where,
            //                                 "",
            //                                 "");

            vdCommon.printCsData(result, 3);

            var comboList = vdCommon.fn_makeCombo(result, {DimName : "BOM Info", DimAttbName : "Item", Sort : "DisplayName", existAll : false, isDisplayNameWithCode : false});
            vdCommon.debug("ComboData : " + JSON.stringify(comboList));

            vdCommon.programEnd();

            return comboList;

        } catch ( e ) {
            RuleOutputToUI = { Status : 'Error', Message : "Js Logic Error : " + e.message };
            return;
        }
    };
    
    // Prod Item
    var fn_ItemComponentCombo = function(o9Params){
        try {
            const commonLib = require('o9.NSCM.commonLib');
            const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
            const vdUtil = new commonLib.VdUtil();
            vdCommon.setLogLevel("Debug");
            vdCommon.printParams(o9Params);

            let parsedParams = JSON.parse(o9Params); 
            let fbLocation = parsedParams.fbLocation;
            let fbSubLocation = parsedParams.fbSubLocation;
            let fbTPMode    = parsedParams.fbTPMode;
            // var fbItemMaterial = parsedParams.fbItemMaterial;
            var fbToItem = parsedParams.fbToItem;

            // LCM Code MAP 정보 가져오기 (임재민p, 노보람p 요청 - 2025.04.17)
            var where = 'where {'
                            +' &CWVUI'
                            +', [Location].[Location]'+ vdUtil.fn_filterStr(fbSubLocation)  // From Site
                            +', [To Item].[To Item]'+ vdUtil.fn_filterStr(fbToItem)
                            +', Measure.[LCM Code MAP_Status] == "COM" '
                            +'}';
            var result = vdCommon.selectList(["[Item].[Item]"],
                                            "",//["Measure.[LCM Code MAP_Status]"],
                                            where, // where                                           
                                            "",
                                            "");  //"limit 1000"

            // var where = 'where {'
            //                 +' &CWVUI'
            //                 +', [Location].[Location]'+ vdUtil.fn_filterStr(fbLocation)
            //                 +', [Sub Location].[Sub Location]'+ vdUtil.fn_filterStr(fbSubLocation)
            //                 +', [Trans Mode].[Trans Mode]'+ vdUtil.fn_filterStr(fbTPMode)
            //                 +', ~isnull(Measure.[BOD Item_Prod Item]) '
            //                 +'}';

            // // dimension 총 4 Row
            // var result = vdCommon.selectList(["[Item].[Item]"+ vdUtil.fn_filterStr(fbToItem)],
            //                                  ["Measure.[BOD Item_Prod Item]"],
            //                                 //   "where { ~isnull(Measure.[BOD Item_Prod Item]) }",
            //                                   where,
            //                                   "",
            //                                   "");

            vdCommon.printCsData(result, 3);

            var comboList = vdCommon.fn_makeCombo(result, {DimName : "Item", DimAttbName : "Item", Sort : "DisplayName", existAll : false, isDisplayNameWithCode : false});
            // var comboList = vdCommon.fn_makeCombo(result, {MeasureName : "BOD Item_Prod Item",  existAll : false});            
            
            vdCommon.debug("ComboData : " + JSON.stringify(comboList));

            vdCommon.programEnd();

            return comboList;

        } catch ( e ) {
            RuleOutputToUI = { Status : 'Error', Message : "Js Logic Error : " + e.message };
            return;
        }
    };

    // Cell Code
    var fn_ItemMaterialCombo = function(o9Params){
        try {
            const commonLib = require('o9.NSCM.commonLib');
            const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
            const vdUtil = new commonLib.VdUtil();
            vdCommon.setLogLevel("Debug");
            
            let parsedParams = JSON.parse(o9Params); 
            let fbLocation = parsedParams.fbLocation;       // To Site
            let fbSubLocation = parsedParams.fbSubLocation; // From Site
            let fbItemComponent    = parsedParams.fbItemComponent;  // Prod Item

            // dimension 총 79,610 Row
            // var result = vdCommon.selectList(["[Item Material].[Item Material]"],
            //                                  [],    // measure
            //                                   "",
            //                                   "",
            //                                   "");  // limit

            
            // BOM 정보 가져오기 (임재민p, 노보람p 요청 - 2025.04.17)
            var where = 'where {'
            +' &CWVUI'
            +', [Location].[Location]'+ vdUtil.fn_filterStr(fbSubLocation)          // From Site
            +', &NSUISiteGrp3LCMView '
            +', Item.[Item Stage].[OPEN_CELL] '
            +', [BOM Info].[BOM ID] , Measure.[BOM Comp_Valid Flag] == true '
            +', [BOM Info].[Item]'+ vdUtil.fn_filterStr(fbItemComponent)             // add 2025.05.07 테스트중..
            +'}';
            var result = vdCommon.selectList(["[Item].[Item]"],
                                                "",     // measure
                                                where,  // where
                                                "",     // "orderby [Item].[Item].Name desc",    // orderby
                                                "");    // limit

            vdCommon.printCsData(result, 3);

            // var comboList = vdCommon.fn_makeCombo(result, {DimName : "Item Material", DimAttbName : "Item Material", Sort : "DisplayName", existAll : false, isDisplayNameWithCode : false});
            var comboList = vdCommon.fn_makeCombo(result, {DimName : "Item", DimAttbName : "Item", Sort : "DisplayName", existAll : false, isDisplayNameWithCode : false});
            vdCommon.debug("ComboData : " + JSON.stringify(comboList));

            vdCommon.programEnd();

            return comboList;

        } catch ( e ) {
            RuleOutputToUI = { Status : 'Error', Message : "Js Logic Error : " + e.message };
            return;
        }
    };

    /**
     * Apply
     * @param {*} o9Params 
     * @returns 
     */
    var fn_apply = function(o9Params){
        try {
            const commonLib = require('o9.NSCM.commonLib');
            const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
            const vdUtil = new commonLib.VdUtil();
            
            vdCommon.setLogLevel("Debug");
            vdCommon.printParams(o9Params);

            // 파라미터 가져오기
            var parsedParams = JSON.parse(o9Params);

            /* Validation 호출 (PY_UI_SOPAdjustLCM) */
            var execQuery = 'EXEC plugin instance [PY_UI_SOPAdjustLCM] ' +
                            'for measures {[SOP W_LCM MFG Qty]} ' +
                            'using scope ( &CWVUI ) ' +
                            'using arguments {(ExecutionMode, "MediumWeight"), (MaxSliceTableCells, 200000000), (MaxConcurrency, 1), ([Param.o9_sys_log_level], "DEBUG")}; ';   // 2025.02.04 수정 (권태우B 요청)
                            // 'using arguments {(ExecutionMode, "MediumWeight"), ("IncludeNullRows", "False"), (paramOutVersion , "CWV_MP"), (MaxSliceTableCells, 200000000), (MaxConcurrency, 1), ([Param.o9_sys_log_level], "DEBUG")}; ';

            vdCommon.debug("execQuery: " + JSON.stringify(execQuery));
            vdCommon.executeQuery("fn_validation : PY_UI_SOPAdjustLCM Run", execQuery);

            vdCommon.programEnd();
        } catch ( e ) {
            RuleOutputToUI = { Status : 'Error', Message : "Js Logic Error : " + e.message };
            return;
        }
    };

    var fn_add = function(o9Params){
        try {
            const commonLib = require('o9.NSCM.commonLib');
            const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
            const vdUtil = new commonLib.VdUtil();

            vdCommon.setLogLevel("Debug");

            vdCommon.printParams(o9Params);

            // 파라미터 가져오기
            var parsedParams = JSON.parse(o9Params);
            // var fbVersion = "&MPV";
            var fbLocation = parsedParams.fbLocation;
            var fbSubLocation = parsedParams.fbSubLocation;
            var fbTPMode = parsedParams.fbTPMode;
            var fbItemMaterial = parsedParams.fbItemMaterial;
            var fbToItem = parsedParams.fbToItem;
            var fbItemComponent = parsedParams.fbItemComponent;
            // var fbMPHorizon = "&"+parsedParams.fbMPHorizon;

            var dimension = ["&CWVUI"
                            ,"[Location].[Location].[" + fbLocation + "]"               // To Site
                            ,"[Sub Location].[Sub Location].[" + fbSubLocation + "]"    // From Site
                            ,"[To Trans Mode].[To Trans Mode].[" + fbTPMode + "]"
                            ,"[To Item].[To Item].[" + fbToItem + "]"
                            ,"[Item Material].[Item Material].[" + fbItemMaterial + "]"
                            ,"[Item Component].[Item Component].[" + fbItemComponent + "]"
                            ,MPHorizonWeek1
                        ];
            // 중복체크
            if ( vdCommon.existMeasure(dimension
                                      ,["Measure.[SOP Adjust LCM W_Before Adj Qty]"
                                      ,"Measure.[SOP Adjust LCM W_Chg Qty]"
                                      ,"Measure.[SOP Adjust LCM W_SOP Adj Qty]"
                                      ,"Measure.[SOP Adjust LCM W_SOP Qty]"]
                                      , "")) {
                RuleOutputToUI = { Status : 'Error', Message : "The data has already been registered." };
                return;
            }

            // SOP Adjustment LCM W 생성
            vdCommon.createMeasure(dimension
                                 ,[
                                  'Measure.[SOP Adjust LCM W_Before Adj Qty]    = 0;'
                                //  , 'Measure.[SOP Adjust LCM W_Chg Qty]          = 0;'
                                //  , 'Measure.[SOP Adjust LCM W_SOP Adj Qty]      = 0;'
                                 , 'Measure.[SOP Adjust LCM W_SOP Qty]          = 0;'
                                ]);

            vdCommon.programEnd();
        } catch ( e ) {
            RuleOutputToUI = { Status : 'Error', Message : "Js Logic Error : " + e.message };
            return;
        }
    };
    /**
     * 삭제시 Validation Check
     * &MPV 버전만 삭제 하도록 체크 2024.10.22  요청 아님.. Delete시 과거 버전 삭제하지 않도록 처리 테스트 중..(확인 필요)
     * &CWVUI 로 변경 CWV_MP 2024.11.05
     * @param {*} o9Params 
     * @returns 
     */
    var fn_validation = function(o9Params){
        try {
            const commonLib = require('o9.NSCM.commonLib');
            const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
            const vdUtil = new commonLib.VdUtil();

            vdCommon.setLogLevel("Debug");

            vdCommon.printParams(o9Params);
            // 파라미터 가져오기
            let parsedParams = JSON.parse(o9Params);

            // Tuple 정확히 가져올때, 동일한 값만 있는 경우 Merge 됨, key 가 되는 dim 을 모두 표기
            let fbTupleList = parsedParams.fbTupleList;
            let returnValue = 0;    // 0: 정상, 1: 오류메세지
            let mpVersion = "", paramVersion = "";
            var rtnMpVersion = vdCommon.selectList(["&CWVUI"],
                                             [],    // measure
                                             "",    // where
                                             "",    // orderby
                                             "");   // limit

            vdCommon.printCsData(rtnMpVersion, 3);
            if ( rtnMpVersion.cs.rowCount == 1 ){
                mpVersion = rtnMpVersion.cs.row(0).cell(rtnMpVersion.cs.memberColumnIndex("Version", "Version Name")).Name;
                vdCommon.debug("기준 Version : "+mpVersion);
            }
            for ( var i = 0; i < fbTupleList.length; i++ ) {
                const row      = fbTupleList[i];
                fbVersion      = row.fbVersion.Value;
                var rtnParamVersion = vdCommon.selectList(["[Version].[Version Name].["+fbVersion+"]"],
                                            [],    // measure
                                            "",    // where
                                            "",    // orderby
                                            "");   // limit
                if ( rtnParamVersion.cs.rowCount == 1 ){
                    paramVersion = rtnParamVersion.cs.row(0).cell(rtnParamVersion.cs.memberColumnIndex("Version", "Version Name")).Name;
                    vdCommon.debug("비교 Version : "+paramVersion);
                }                
                if ( mpVersion !=  paramVersion){
                    returnString = "["+paramVersion+"] 버전은 삭제할 수 없습니다.";
                    RuleOutputToUI = { Status : 'Error', Message : returnString };
                    returnValue = 1;    // 오류
                    vdCommon.programEnd();
                    return returnValue;
                }
            }
            vdCommon.programEnd();
            return returnValue;       // 0 : 정상, 1 : 오류
        
        } catch ( e ) {
            RuleOutputToUI = { Status : 'Error', Message : "Js Logic Error : " + e.message };
            return;
        }
    };
    var fn_delete = function(o9Params){
        try {
            const commonLib = require('o9.NSCM.commonLib');
            const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
            const vdUtil = new commonLib.VdUtil();

            vdCommon.setLogLevel("Debug");
            vdCommon.printParams(o9Params);

            // 파라미터 가져오기
            var parsedParams = JSON.parse(o9Params);
            let fbTupleList  = parsedParams.fbTupleList;
            let fbLocation   = "", fbSubLocation = "", fbTPMode = "", fbItemMaterial = "", fbToItem="", fbItemComponent="";
            var dimension = [];

            for ( var i = 0; i < fbTupleList.length; i++ ) {
                const row      = fbTupleList[i];
                fbLocation      = row.fbLocation.Value;
                fbSubLocation   = row.fbSubLocation.Value;
                fbTPMode        = row.fbTPMode.Value;
                fbItemMaterial  = row.fbItemMaterial.Value;
                fbToItem        = row.fbToItem.Value;
                fbItemComponent = row.fbItemComponent.Value;

                var dimension = ["&CWVUI"
                                ,"[Location].[Location].[" + fbLocation + "]"
                                ,"[Sub Location].[Sub Location].[" + fbSubLocation + "]"
                                ,"[To Trans Mode].[To Trans Mode].[" + fbTPMode + "]"
                                ,"[Item Material].[Item Material].[" + fbItemMaterial + "]"
                                ,"[To Item].[To Item].[" + fbToItem + "]"                                
                                ,"[Item Component].[Item Component].[" + fbItemComponent + "]"
                                ,MPHorizonWeek1
                                ];

                // SOP Adjustment LCM W 삭제
                vdCommon.deleteMeasure(dimension, "SOP Adjustment LCM W");

            }
            vdCommon.programEnd();
        } catch ( e ) {
            RuleOutputToUI = { Status : 'Error', Message : "Js Logic Error : " + e.message };
            return;
        }
    };

    return{
        fn_locationCombo : fn_locationCombo
       ,fn_subLocationCombo : fn_subLocationCombo
       ,fn_toTransModeCombo : fn_toTransModeCombo
       ,fn_toItemCombo : fn_toItemCombo
       ,fn_ItemMaterialCombo : fn_ItemMaterialCombo
       ,fn_ItemComponentCombo : fn_ItemComponentCombo
       ,fn_apply : fn_apply
       ,fn_add : fn_add
       ,fn_validation : fn_validation
       ,fn_delete : fn_delete
    };    
});

/*-------------------------------------------------------------------------------------------------*/
/* o9.NSCM.JSLCMSOPAdjust */
/* 수정 2025.02.04 Py 호출  MediumWeight 로 변경 */
/* 수정 2025.03.06 combo list 수정 */
/* 수정 2025.03.18 Location - view filter 적용 */
/* 수정 2025.03.20 Sub Location - view filter 적용 Sub Location=From Site, Location=To Site 로 타이틀변경 */
/* 수정 2025.04.07 Sub Location - view filter 적용 Sub Location Group4 로 변경 - 액션버튼 속성 변경 */
/* 수정 2025.04.17 fn_locationCombo, fn_subLocationCombo, fn_toTransModeCombo , fn_toItemCombo, fn_ItemMaterialCombo, fn_ItemComponentCombo  */
/* 수정 2025.05.07 Item (fbToItem)> Prod Item (fbItemComponent) > Cell Code (fbItemMaterial)  순서 변경 */
/*-------------------------------------------------------------------------------------------------*/