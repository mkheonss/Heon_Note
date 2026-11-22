define('o9.NSCM.JSBODListLCM', ['o9/data/query', 'o9/data/cellset', 'o9.NSCM.commonLib'], function(){

    const programName = "o9.NSCM.JSBODListLCM";

    var fn_locationCombo = function(o9Params){
        try {
            const commonLib = require('o9.NSCM.commonLib');
            const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
            vdCommon.setLogLevel("Debug");
            // dimension, measure, where, orderby, limit
            // var where = "where {&CWVUI, ~isnull(Measure.[BOD Item_Created By]) || ~isnull(Measure.[BOD Item_Creation Time]) || ~isnull(Measure.[BOD Item_Cur Status])}"; // 검토필요 2024.10.25 테스트
            var where = "";
            var result = vdCommon.selectList(["&MFStageLCMLocation"], // &LCMLocation  현재 BOD Item 에 data 없음 2024.10.21
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

    var fn_subLocationCombo = function(o9Params){
        try {
            const commonLib = require('o9.NSCM.commonLib');
            const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
            vdCommon.setLogLevel("Debug");
            vdCommon.printParams(o9Params);
            // 파라메타 가져오기
            let parsedParams = JSON.parse(o9Params);
            let fbLocation = parsedParams.fbLocation;

            // selectList(dimension, measure, where, orderby, limit)
            var where = "where {"
                               +"&CWVUI"
                               +",[Location].[Location].["+fbLocation+"]"
                            //    +",~isnull(Measure.[BOD Item_Created By]) || ~isnull(Measure.[BOD Item_Creation Time]) || ~isnull(Measure.[BOD Item_Cur Status])"
                               +"}";

            var result = vdCommon.selectList(["&MFStageSETSubLocation.unionwith(&MFStageKDSubLocation)"],
                                             [],
                                             where,
                                             "",
                                             "");
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

    var fn_transModeCombo = function(o9Params){
        try {
            const commonLib = require('o9.NSCM.commonLib');
            const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
            const vdUtil = new commonLib.VdUtil();
            vdCommon.setLogLevel("Debug");

            vdCommon.printParams(o9Params);

            // 파라미터 가져오기
            var parsedParams = JSON.parse(o9Params);
            let fbLocation = parsedParams.fbLocation;
            let fbSubLocation = parsedParams.fbSubLocation;

            // Measure 에 등록된 Trans Mode 를 제외하고 보여준다.
            // var dims = [];
            // dims.push("&CWVUI");
            // dims.push("Location.[Location].[" + fbLocation + "]");
            // dims.push("[Sub Location].[Sub Location].[" + fbSubLocation + "]");
            // // dims.push('[Trans Mode].[Trans Mode].filter(#.Name in {"AIR","TRUCK","VESSEL"})');      // "AIR", "TRUCK", "VESSEL"
            // dims.push("&NSUITransModeView");

            var where = 'include nulls where {'
                                            +' &CWVUI'
                                            +', [Location].[Location]'+ vdUtil.fn_filterStr(fbLocation)
                                            +', [Sub Location].[Sub Location]'+ vdUtil.fn_filterStr(fbSubLocation)                                
                                            +'} .filter(isnull(Measure.[BOD List_BOD Valid]))';

            // Measure Group(Code Map LCM) 에 등록된 Item 을 제외하고 보여준다.
            var result = vdCommon.selectList(["&NSUITransModeView"],
                                             ["Measure.[BOD List_BOD Valid]"],
                                              where,
                                              "",   //  "orderby [Item].[Item].Name",
                                              "");
            vdCommon.printCsData(result, 3);

            var comboList = vdCommon.fn_makeCombo(result, {DimName : "Trans Mode", DimAttbName : "Trans Mode", Sort : "DisplayName", existAll : false});
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
            var fbLocation = parsedParams.fbLocation;
            var fbSubLocation = parsedParams.fbSubLocation;
            var fbTPMode = parsedParams.fbTPMode;

            //----------------------------------------------------------------------------------// 
            // BOD List : Clear Measure 정의
            // 주석처리 부분은 다른데서 가져온 data clear 하지 않음
            //----------------------------------------------------------------------------------//
            var measureBodList = [];
            measureBodList.push('Measure.[BOD List_BOD Valid] 				= "Y";');
            measureBodList.push('Measure.[BOD List_Update Time] 			= dateadd(Now(),9,"hour");');
            measureBodList.push('Measure.[BOD List_Updated By] 			    = CurrentUser().[User Name];');
            measureBodList.push('Measure.[BOD List_is New Flag] 			= true;');  // BOD Item Python 튜닝에서 사용 (2025.04.23 임재민p요청)

            var dimension = ["&CWVUI"
                            ,"[Location].[Location].[" + fbLocation + "]"
                            ,"[Sub Location].[Sub Location].[" + fbSubLocation + "]"
                            ,"[Trans Mode].[Trans Mode].[" + fbTPMode + "]"];

            // 중복체크 후 Update
            if ( vdCommon.existMeasure(dimension
                                        ,["Measure.[BOD List_BOD Valid]"
                                        ,"Measure.[BOD List_BOD Frozen]"
                                        ,"Measure.[BOD List_BOD LT]"
                                        ,"Measure.[BOD List_Eff Enddate]"
                                        ,"Measure.[BOD List_Eff Startdate]"
                                        ,"Measure.[BOD List_Priority]"
                                        ,"Measure.[BOD List_Shipment LT]"
                                        ,"Measure.[BOD List_Time Phased BOD LT]"
                                        ,"Measure.[BOD List_Time Phased Shipment LT]"
                                        ,"Measure.[BOD List_Update Time]"
                                        ,"Measure.[BOD List_Updated By]"
                                        ,"Measure.[BOD List_Creation Time]"
                                        ,"Measure.[BOD List_Created By]"]
                                      , "")) {
                // RuleOutputToUI = { Status : 'Error', Message : "The data has already been registered." };
                // return;
                // vdCommon.debug("------------------BOD List Update");
                vdCommon.updateMeasure(dimension, measureBodList);
            }else{
                
                // BOD List MG 생성
                measureBodList.push('Measure.[BOD List_Creation Time]  			= dateadd(Now(),9,"hour");');
                measureBodList.push('Measure.[BOD List_Created By] 			    = CurrentUser().[User Name];');
                // vdCommon.debug("------------------BOD List Create");
                vdCommon.createMeasure(dimension, measureBodList);
                // BOD Item 은 Batch 에서 생성, BOD List 데이터 수정시 Spreading 으로 BOD Item 을 생성 or update 한다.
            }

            vdCommon.programEnd();
        } catch ( e ) {
            RuleOutputToUI = { Status : 'Error', Message : "Js Logic Error : " + e.message };
            return;
        }
    };

    var fn_validYN = function(o9Params){
        try {
            const commonLib = require('o9.NSCM.commonLib');
            const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
            const vdUtil = new commonLib.VdUtil();

            vdCommon.setLogLevel("Debug");

            vdCommon.printParams(o9Params);

            // 파라미터 가져오기
            var parsedParams = JSON.parse(o9Params);
            let fbValidYN = parsedParams.fbValidYN;

            let tupleList       = parsedParams.fbBODListTuple;
            let fbLocation = "", fbSubLocation = "", fbTPMode = "";            
            let dimBodList = [];

            for ( var i = 0; i < tupleList.length; i++ ) {
                const row = tupleList[i];
                fbLocation      = row.fbLocation.Value;
                fbSubLocation   = row.fbSubLocation.Value;
                fbTPMode        = row.fbTPMode.Value;

                dimBodList = ["&CWVUI"
                            ,"[Location].[Location].[" + fbLocation + "]"
                            ,"[Sub Location].[Sub Location].[" + fbSubLocation + "]"
                            ,"[Trans Mode].[Trans Mode].[" + fbTPMode + "]"];

                //----------------------------------------------------------------------------------//
                // BOD List delete : Measure.[BOD List_BOD Valid] = "N" or "Y"
                //----------------------------------------------------------------------------------//                
                vdCommon.updateMeasure(dimBodList,
                    ['Measure.[BOD List_BOD Valid] = "' + fbValidYN + '";',
                     'Measure.[BOD List_Update Time] = dateadd(Now(),9,"hour");',
                     'Measure.[BOD List_Updated By] = CurrentUser().Name;']);
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
    var fn_validation = function(o9Params){
        try {
            const commonLib = require('o9.NSCM.commonLib');
            const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
            const vdUtil = new commonLib.VdUtil();
            
            vdCommon.setLogLevel("Debug");
            vdCommon.printParams(o9Params);

            // 파라미터 가져오기
            var parsedParams = JSON.parse(o9Params);

            /* Validation 호출 (PY_UI_BODItemLCMValid) */
            var execQuery = 'EXEC plugin instance [PY_UI_BODItemLCMValid] ' +
                            'for measures {[BOD Item_Eff Startdate],[BOD Item_BOD LT],[BOD Item_Shipment LT],[BOD Item_Priority],[BOD Item_Update Time],[BOD Item_Updated By]} ' +
                            'using scope ( &CWVUI ) ' +
                            'using arguments {(ExecutionMode, "MediumWeight"), (pDetailLogFlag, "N"), (MaxSliceTableCells, 200000000), (MaxConcurrency, 1), ([Param.o9_sys_log_level], "DEBUG") };  ';

            // /* Validation 호출 (PY_UI_BODItemLCMValid) */
            // EXEC plugin instance [PY_UI_BODItemLCMValid] for measures {[BOD Item_Eff Start Date]} using scope ( &CWVUI ) using arguments {(ExecutionMode, "LightWeight"), (MaxSliceTableCells, 200000000), (MaxConcurrency, 1 )};


            vdCommon.debug("execQuery: " + JSON.stringify(execQuery));
            vdCommon.executeQuery("fn_validation : PY_UI_BODItemLCMValid Run", execQuery);

            vdCommon.programEnd();
        } catch ( e ) {
            RuleOutputToUI = { Status : 'Error', Message : "Js Logic Error : " + e.message };
            return;
        }
    };

    return{
        fn_locationCombo : fn_locationCombo
       ,fn_subLocationCombo : fn_subLocationCombo
       ,fn_transModeCombo : fn_transModeCombo
       ,fn_add : fn_add
       ,fn_validYN : fn_validYN
       ,fn_validation : fn_validation              
    };
});

/*-------------------------------------------------------------------------------------------------*/
/* 수정 2025.01.21 TransMode Namedset 수정 NSUITransModeView */
/* 수정 2025.03.06 combo list 수정 */
/* 수정 2025.04.23 : fn_add - Measure.[BOD List_is New Flag] 추가 , 임재민p 요청                    */
/*-------------------------------------------------------------------------------------------------*/