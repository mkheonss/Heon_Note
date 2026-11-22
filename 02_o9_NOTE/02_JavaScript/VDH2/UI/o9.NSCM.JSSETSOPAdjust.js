define('o9.NSCM.JSSETSOPAdjust', ['o9/data/query', 'o9/data/cellset', 'o9.NSCM.commonLib'], function(){

    const programName = "o9.NSCM.JSSETSOPAdjust";
    const MPHorizon = "&MPHorizon";

    var fn_locationCombo = function(o9Params){
        try {
            const commonLib = require('o9.NSCM.commonLib');
            const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
            vdCommon.setLogLevel("Debug");
            // dimension, measure, where, orderby, limit
            var where = "";
            var result = vdCommon.selectList(["&MFStageSETLocation"],
            // var result = vdCommon.selectList(["[Location].[Location]"],
                                             [],    // measure
                                             where,    // where
                                             "",    // orderby
                                             "");   // limit
            vdCommon.printCsData(result, 3);

            var comboList = vdCommon.fn_makeCombo(result, {DimName : "Location", DimAttbName : "Location", Sort : "DisplayName", existAll : false, isDisplayNameWithCode : true});
            vdCommon.debug("ComboData : " + JSON.stringify(comboList));

            vdCommon.programEnd();

            return comboList;
        } catch ( e ) {
            RuleOutputToUI = { Status : 'Error', Message : "Js Logic Error : " + e.message };
            return;
        }
    };

    var fn_toLocationCombo = function(o9Params){
        try {
            const commonLib = require('o9.NSCM.commonLib');
            const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
            vdCommon.setLogLevel("Debug");
            // dimension, measure, where, orderby, limit
            var where = "";
            var result = vdCommon.selectList(["&NSUIToLocationDC"],
                                             [],    // measure
                                             where,    // where
                                             "",    // orderby
                                             "");   // limit
            vdCommon.printCsData(result, 3);

            var comboList = vdCommon.fn_makeCombo(result, {DimName : "To Location", DimAttbName : "To Location", Sort : "DisplayName", existAll : false, isDisplayNameWithCode : true});
            vdCommon.debug("ComboData : " + JSON.stringify(comboList));

            vdCommon.programEnd();

            return comboList;
        } catch ( e ) {
            RuleOutputToUI = { Status : 'Error', Message : "Js Logic Error : " + e.message };
            return;
        }
    };

    var fn_transModeCombo = function(o9Params){
        try {
            const commonLib = require('o9.NSCM.commonLib');
            const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
            vdCommon.setLogLevel("Debug");
            // dimension, measure, where, orderby, limit
            var where = "";
            var result = vdCommon.selectList(["&NSUITransModeView"],    // [Trans Mode].[Trans Mode].filter(#.Name in {"AIR","VESSEL","TRUCK"})
                                             [],    // measure
                                             where, // where
                                             "orderby [Trans Mode].[Trans Mode].Name desc",    // orderby
                                             "");   // limit
            vdCommon.printCsData(result, 3);

            // var comboList = vdCommon.fn_makeCombo(result, {DimName : "Trans Mode", DimAttbName : "Trans Mode", Sort : "DisplayName", existAll : false, isDisplayNameWithCode : false});
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

    var fn_itemCombo = function(o9Params){
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
            let fbViewItemStd    = parsedParams.fbViewItemStd;  // View Filter 의 Item Std4 추가 2025.02.18

            // var dims = [];
            // dims.push("&CWVUI");
            // dims.push("Location.[Location].[" + fbLocation + "]");
            // dims.push("[Sub Location].[Sub Location].[" + fbSubLocation + "]");
            // dims.push("[Trans Mode].[Trans Mode].[" + fbTPMode +"]");            
            // dims.push("&NSUIItemStd4View"+ vdUtil.fn_filterStr(fbViewItemStd)); // View Filter 의 Item Std4 추가 2025.02.18
            // dims.push("&SETItem");
            // let where = 'where {coalesce(Measure.[BOD Item_Eff Startdate],DATEADD(Now(),-1,"Day")) < now(), coalesce(Measure.[BOD Item_Eff Enddate],DATEADD(Now(),1,"Day")) > now()} '
            //             +'.filter(isnull(Measure.[SOP Adjust SET_Min LOT Qty]) && isnull(Measure.[SOP Adjust SET_Multiple LOT Qty]))';


            var where = 'where {'
                            +' &CWVUI'
                            +', [Location].[Location]'+ vdUtil.fn_filterStr(fbLocation)
                            +', [Sub Location].[Sub Location]'+ vdUtil.fn_filterStr(fbSubLocation)
                            +', [Trans Mode].[Trans Mode]'+ vdUtil.fn_filterStr(fbTPMode)
                            +', &NSUIItemStd4View'+ vdUtil.fn_filterStr(fbViewItemStd)              // View Filter 의 Item Std4 추가 2025.02.18
                            +', coalesce(Measure.[BOD Item_Eff Startdate],DATEADD(Now(),-1,"Day")) < now() '
                            +', coalesce(Measure.[BOD Item_Eff Enddate],DATEADD(Now(),1,"Day")) > now() '
                            +'} .filter(isnull(Measure.[SOP Adjust SET_Min LOT Qty]) && isnull(Measure.[SOP Adjust SET_Multiple LOT Qty]))';
                        
            // BOD Item 에 있고 SOP Adjust 에 없는것.. Adjust에 등록할꺼니까..02.18 문지윤p
            // 다른 그레인은 동일하고, 
            // BOD Item 의 Sub Location 과 SOP Adjust SET 의 To Location 이 그레인이 달라도 member 가 동일하므로 join 됨.
            var result = vdCommon.selectList(["&SETItem"],
                                             ["Measure.[BOD Item_Asn]"
                                             ,"Measure.[BOD Item_Created By]"
                                             ,"Measure.[BOD Item_Creation Time]"
                                             ,"Measure.[BOD Item_Cur Status]"
                                             ,"Measure.[BOD Item_BOD LT]"],    // measure
                                             where,
                                              "",
                                              "");
            vdCommon.printCsData(result, 3);
            
            var comboList = vdCommon.fn_makeCombo(result, {DimName : "Item", DimAttbName : "Item", Sort : "DisplayName", existAll : false, isDisplayNameWithCode : false});
            vdCommon.debug("ComboData : " + JSON.stringify(comboList));

            vdCommon.programEnd();

            return comboList;

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
            var fbSubLocation = parsedParams.fbSubLocation; // To Location
            var fbTPMode = parsedParams.fbTPMode;
            var fbItem = parsedParams.fbItem;
            // var fbMPHorizon = "&"+parsedParams.fbMPHorizon;

            var dimension = ["&CWVUI"
                            ,"[Location].[Location].[" + fbLocation + "]"
                            ,"[To Location].[To Location].[" + fbSubLocation + "]"
                            ,"[Trans Mode].[Trans Mode].[" + fbTPMode + "]"
                            ,"[Item].[Item].[" + fbItem + "]"];
            // 중복체크
            if ( vdCommon.existMeasure(dimension
                                      ,["Measure.[SOP Adjust SET_Min LOT Qty]"
                                      ,"Measure.[SOP Adjust SET_Multiple LOT Qty]"]
                                      , "")) {
                RuleOutputToUI = { Status : 'Error', Message : "The data has already been registered." };
                return;
            }

            // SOP Adjustment SET 생성
            vdCommon.createMeasure(dimension
                                  ,['Measure.[SOP Adjust SET_Min LOT Qty]      = 0;'    // default data 정의 필요
                                   ,'Measure.[SOP Adjust SET_Multiple LOT Qty] = 0;']);

            var dimensionW = [...dimension];    // dimension 을 복사후 추가 (Main MG의 Grain 에서 추가되는 경우 활용)
            dimensionW.push(MPHorizon);

            // // SOP Adjustment SET W 생성
            vdCommon.createMeasure(dimensionW
                                 ,[
                                  'Measure.[SOP Adjust SET W_SOP Qty]      = 0;'     // Default 값 세팅 = 0 (2024.11.06)
                                 //, 'Measure.[SOP Adjust SET W_SOP Adj Qty]  = 100;'   // Twin Measure : data 생성 안됨(null) 2024.09.20
                                 //, 'Measure.[SOP Adjust SET W_Sht Qty]    = 0;'       // Reporting Measure 는 값을 세팅하지 않음.
                                 //, 'Measure.[SOP Adjust SET W_Chg Qty]      = 0;'       // Twin Measure : data 생성 안됨(null) 2024.09.20
                                 , 'Measure.[SOP Adjust SET W_Chg Reason]   = null;'
                                 , 'Measure.[SOP Adjust SET W_Lock Flag]    = 0;'
                                 , 'Measure.[SOP Adjust SET W_JIT]          = 0;'
                                 , 'Measure.[SOP Adjust SET W_SS]           = 0;'
                                 , 'Measure.[SOP Adjust SET W_BLD]          = 0;'
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
            let fbTupleList     = parsedParams.fbTupleList;
            let fbLocation = "", fbSubLocation = "", fbTPMode = "", fbItem = "";
            var dimension = [];

            for ( var i = 0; i < fbTupleList.length; i++ ) {
                const row      = fbTupleList[i];
                fbLocation      = row.fbLocation.Value;
                fbSubLocation   = row.fbSubLocation.Value;  // To Location
                fbTPMode        = row.fbTPMode.Value;
                fbItem          = row.fbItem.Value;

                dimension = ["&MPV"
                            ,"[Location].[Location].[" + fbLocation + "]"
                            ,"[To Location].[To Location].[" + fbSubLocation + "]"
                            ,"[Trans Mode].[Trans Mode].[" + fbTPMode + "]"
                            ,"[Item].[Item].[" + fbItem + "]"];

                // SOP Adjustment SET 삭제
                vdCommon.deleteMeasure(dimension, "SOP Adjustment SET");

                // Detail MG
                var dimensionW = [...dimension];    // dimension 을 복사후 추가 (Main MG의 Grain 에서 추가되는 경우 활용)
                dimensionW.push(MPHorizon);

                vdCommon.deleteMeasure(dimensionW, "SOP Adjustment SET W");
            }
            vdCommon.programEnd();
        } catch ( e ) {
            RuleOutputToUI = { Status : 'Error', Message : "Js Logic Error : " + e.message };
            return;
        }
    };

    /**
     * Validation
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

            /* Validation 호출 (PY_UI_SOPAdjustSET) */
            var execQuery = 'EXEC plugin instance [PY_UI_SOPAdjustSET] ' +
                            'for measures {[SOP W_SET MFG Qty]} ' +
                            'using scope ( &CWVUI ) ' +
                            'using arguments {(ExecutionMode, "MediumWeight"), (MaxSliceTableCells, 200000000), (MaxConcurrency, 1 ), ([Param.o9_sys_log_level], "DEBUG")}; ';      // 2025.02.04 수정(권태우B 요청)
                            // 'using arguments {(ExecutionMode, "LightWeight"), (MaxSliceTableCells, 200000000), (MaxConcurrency, 1 ), ([Param.o9_sys_log_level], "DEBUG")}; ';    // 2025.02.04 이전 버전
                            //'using arguments {(ExecutionMode, "MediumWeight"), ("IncludeNullRows", "False"), (paramOutVersion , "CWV_MP"), (MaxSliceTableCells, 200000000), (MaxConcurrency, 1), ([Param.o9_sys_log_level], "DEBUG")}; ';

            vdCommon.debug("execQuery: " + JSON.stringify(execQuery));
            vdCommon.executeQuery("fn_validation : PY_UI_SOPAdjustSET Run", execQuery);

            vdCommon.programEnd();
        } catch ( e ) {
            RuleOutputToUI = { Status : 'Error', Message : "Js Logic Error : " + e.message };
            return;
        }
    };

    /**
     * Validation
     * @param {*} o9Params 
     * @returns 
     */
    var fn_apply_M = function(o9Params){
        try {
            const commonLib = require('o9.NSCM.commonLib');
            const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
            const vdUtil = new commonLib.VdUtil();
            
            vdCommon.setLogLevel("Debug");
            vdCommon.printParams(o9Params);

            // 파라미터 가져오기
            var parsedParams = JSON.parse(o9Params);

            /* Validation 호출 (PY_UI_SOPAdjustSET) */
            var execQuery = 'EXEC plugin instance [PY_UI_SOPAdjustSET] ' +
                            'for measures {[SOP W_SET MFG Qty]} ' +
                            'using scope ( &CWVUI ) ' +
                            'using arguments {(ExecutionMode, "MediumWeight"), (MaxSliceTableCells, 200000000), (MaxConcurrency, 1), ([Param.o9_sys_log_level], "DEBUG")}; ';
                            // 'using arguments {(ExecutionMode, "MediumWeight"), ("IncludeNullRows", "False"), (paramOutVersion , "CWV_MP"), (MaxSliceTableCells, 200000000), (MaxConcurrency, 1), ([Param.o9_sys_log_level], "DEBUG")}; ';

            vdCommon.debug("execQuery: " + JSON.stringify(execQuery));
            vdCommon.executeQuery("fn_validation : PY_UI_SOPAdjustSET Run", execQuery);

            vdCommon.programEnd();
        } catch ( e ) {
            RuleOutputToUI = { Status : 'Error', Message : "Js Logic Error : " + e.message };
            return;
        }
    };

    return{
        fn_locationCombo : fn_locationCombo
       ,fn_toLocationCombo : fn_toLocationCombo
       ,fn_transModeCombo : fn_transModeCombo
       ,fn_itemCombo : fn_itemCombo
       ,fn_validation : fn_validation
       ,fn_add : fn_add
       ,fn_delete : fn_delete
       ,fn_apply : fn_apply
       ,fn_apply_M : fn_apply_M /* MediumWeight Test */
    };
});

/*-------------------------------------------------------------------------------------------------*/
/* 수정 2025.02.04 Py 호출  MediumWeight 로 변경 */
/* fn_itemCombo - BOD Item의 Item 중 SOP Adjust 에 등록되지 않은 Item List 2025.02.19 수정 */
/* 수정 2025.03.06 combo list 수정 */
/*-------------------------------------------------------------------------------------------------*/