define('o9.NSCM.JSSOPFrozenPeriod', ['o9/data/query', 'o9/data/cellset', 'o9.NSCM.commonLib'], function(){

    const programName = "o9.NSCM.JSSOPFrozenPeriod";
    const FPHorizon = "&FPHorizon";
    // const FPHorizon = "&MDMHorizon";

    var fn_locationCombo = function(o9Params){
        try {
            const commonLib = require('o9.NSCM.commonLib');
            const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
            vdCommon.setLogLevel("Debug");
            // dimension, measure, where, orderby, limit
            // 'where {coalesce(Measure.[BOD Item_Eff Startdate],DATEADD(Now(),-1,"Day")) < now(), coalesce(Measure.[BOD Item_Eff Enddate],DATEADD(Now(),1,"Day")) > now()}',
            //  "limit 1000"
            // var where = "where {&CWVUI, ~isnull(Measure.[BOD Item_Created By]) || ~isnull(Measure.[BOD Item_Creation Time]) || ~isnull(Measure.[BOD Item_Cur Status])}";

            var where = 'where {&CWVUI, coalesce(Measure.[BOD Item_Eff Startdate],DATEADD(Now(),-1,"Day")) < now() || coalesce(Measure.[BOD Item_Eff Enddate],DATEADD(Now(),1,"Day")) > now()}'
            var result = vdCommon.selectList(["&MFLocation"],   // Site(From) : Location Type = 'MF' : 변경 2024.11.05
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

    var fn_productGroupCombo = function(o9Params){
        try {
            const commonLib = require('o9.NSCM.commonLib');
            const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
            vdCommon.setLogLevel("Debug");

            var result = vdCommon.selectList(["Product.[Product Group]"],
                                             [],
                                             "",
                                             "",
                                             "");
            vdCommon.printCsData(result, 3);

            var comboList = vdCommon.fn_makeCombo(result, {DimName : "Product", DimAttbName : "Product Group", Sort : "DisplayName"});
            vdCommon.debug("ComboData : " + JSON.stringify(comboList));

            vdCommon.programEnd();

            return comboList;
        } catch ( e ) {
            RuleOutputToUI = { Status : 'Error', Message : "Js Logic Error : " + e.message };
            return;
        }
    };

    var fn_SCMTypeCombo = function(o9Params){
        try {
            const commonLib = require('o9.NSCM.commonLib');
            const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
            vdCommon.setLogLevel("Debug");

            var result = vdCommon.selectList(["Item.[SCM Type]"],
                                             [],
                                             "",
                                             "",
                                             "");
            vdCommon.printCsData(result, 3);

            var comboList = vdCommon.fn_makeCombo(result, {DimName : "Item", DimAttbName : "SCM Type", Sort : "DisplayName"});
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
            // var fbVersion = parsedParams.fbVersion;
            var fbLocation = parsedParams.fbLocation;
            var fbProductGroup = parsedParams.fbProductGroup;
            var fbSCMType = parsedParams.fbSCMType;
            var fbReason = parsedParams.fbReason;
            // var fbFPHorizon = "&FPHorizon";

            var dimension = ["&CWVUI"
                            ,"[Location].[Location].[" + fbLocation + "]"
                            ,"[Product].[Product Group].[" + fbProductGroup + "]"
                            ,"[Item].[SCM Type].[" + fbSCMType + "]"];
            // 중복체크
            if ( vdCommon.existMeasure(dimension
                                      ,["Measure.[SOP Frozen Period_Status]"]
                                      , "") ) {
                RuleOutputToUI = { Status : 'Error', Message : "The data has already been registered." };
                return;
            }

            // Main MG 생성
            vdCommon.createMeasure(dimension
                                  ,[
                                    'Measure.[SOP Frozen Period_Reason]         = "' + vdUtil.fn_getString(fbReason) + '";'    // null 값이 올수 있음.
                                   ,'Measure.[SOP Frozen Period_Status]         = "Chg";'
                                   ,'Measure.[SOP Frozen Period_Update Time]    = now();'
                                   ,'Measure.[SOP Frozen Period_Updated By]     = CurrentUser().[User Name];']);

            var dimensionW = [...dimension];    // dimension 을 복사후 추가 (Main MG의 Grain 에서 추가되는 경우 활용)
            dimensionW.push(FPHorizon);

            // Detail MG 생성
            vdCommon.createMeasure(dimensionW
                                 ,['Measure.[SOP Frozen Period W_Period Type]           = null;'
                                 ,'Measure.[SOP Frozen Period W_Period Type.Lock]       = null;'
                                 ,'Measure.[SOP Frozen Period W_Period Copy_CountValue] = null;'
                                 ,'Measure.[SOP Frozen Period W_Period Item_CountValue] = null;'
                                 ,'Measure.[SOP Frozen Period W_Period Exnd_CountValue] = null;'
                                ]);

            vdCommon.programEnd();
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
            let tupleList       = parsedParams.fbListTuple;
            var dimension = [];

            for ( var i = 0; i < tupleList.length; i++ ) {
                const row      = tupleList[i];
                fbLocation       = row.fbLocation.Value;
                fbProductGroup   = row.fbProductGroup.Value;
                fbSCMType        = row.fbSCMType.Value;

                dimension = ["&CWVUI"
                            ,"[Location].[Location].[" + fbLocation + "]"
                            ,"[Product].[Product Group].[" + fbProductGroup + "]"
                            ,"[Item].[SCM Type].[" + fbSCMType + "]"];

                // Main MG
                vdCommon.deleteMeasure(dimension, "SOP Frozen Period");

                // Detail MG
                var dimensionW = [...dimension];    // dimension 을 복사후 추가 (Main MG의 Grain 에서 추가되는 경우 활용)
                dimensionW.push(FPHorizon);

                vdCommon.deleteMeasure(dimensionW, "SOP Frozen Period W");
            }
            vdCommon.programEnd();
        } catch ( e ) {
            RuleOutputToUI = { Status : 'Error', Message : "Js Logic Error : " + e.message };
            return;
        }
    };

    var fn_clear = function(o9Params){
        try {
            const commonLib = require('o9.NSCM.commonLib');
            const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
            const vdUtil = new commonLib.VdUtil();

            vdCommon.setLogLevel("Debug");

            vdCommon.printParams(o9Params);

            // 파라미터 가져오기
            var parsedParams = JSON.parse(o9Params);

            let tupleList       = parsedParams.fbListTuple;
            var dimension = [];

            for ( var i = 0; i < tupleList.length; i++ ) {
                const row      = tupleList[i];
                fbLocation       = row.fbLocation.Value;
                fbProductGroup   = row.fbProductGroup.Value;
                fbSCMType        = row.fbSCMType.Value;

                dimension = ["&CWVUI"
                            ,"[Location].[Location].[" + fbLocation + "]"
                            ,"[Product].[Product Group].[" + fbProductGroup + "]"
                            ,"[Item].[SCM Type].[" + fbSCMType + "]"];

                // Main MG
                vdCommon.updateMeasure(dimension
                                      ,['Measure.[SOP Frozen Period_Reason]        = null;'
                                      ,'Measure.[SOP Frozen Period_Status]         = "Chg";'
                                      ,'Measure.[SOP Frozen Period_Update Time]    = now();'
                                      ,'Measure.[SOP Frozen Period_Updated By]     = CurrentUser().[User Name];'
                                    ]);
                // Detail MG
                vdCommon.updateMeasure(dimension
                                      ,['Measure.[SOP Frozen Period W_Period Type]           = null;'
                                      ,'Measure.[SOP Frozen Period W_Period Type.Lock]       = null;'
                                      ,'Measure.[SOP Frozen Period W_Period Copy_CountValue] = null;'
                                      ,'Measure.[SOP Frozen Period W_Period Item_CountValue] = null;'
                                      ,'Measure.[SOP Frozen Period W_Period Exnd_CountValue] = null;'
                                    ]);
            }
            
            vdCommon.programEnd();

        } catch ( e ) {
            RuleOutputToUI = { Status : 'Error', Message : "Js Logic Error : " + e.message };
            return;
        }
    };

    var fn_confirm = function(o9Params){
        try {
            const commonLib = require('o9.NSCM.commonLib');
            const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
            const vdUtil = new commonLib.VdUtil();

            vdCommon.setLogLevel("Debug");

            vdCommon.printParams(o9Params);

            // 파라미터 가져오기
            var parsedParams = JSON.parse(o9Params);

            let tupleList       = parsedParams.fbListTuple;
            var dimension = [];

            for ( var i = 0; i < tupleList.length; i++ ) {
                const row      = tupleList[i];
                fbLocation       = row.fbLocation.Value;
                fbProductGroup   = row.fbProductGroup.Value;
                fbSCMType        = row.fbSCMType.Value;

                dimension = ["&CWVUI"
                            ,"[Location].[Location].[" + fbLocation + "]"
                            ,"[Product].[Product Group].[" + fbProductGroup + "]"
                            ,"[Item].[SCM Type].[" + fbSCMType + "]"];

                // Main MG
                vdCommon.updateMeasure(dimension
                                      ,['Measure.[SOP Frozen Period_Status]        = "COM";'
                                      ,'Measure.[SOP Frozen Period_Update Time]    = now();'
                                      ,'Measure.[SOP Frozen Period_Updated By]     = CurrentUser().[User Name];'
                                    ]);
            }
            
            vdCommon.programEnd();

        } catch ( e ) {
            RuleOutputToUI = { Status : 'Error', Message : "Js Logic Error : " + e.message };
            return;
        }
    };

    // 단건 선택 처리 2025.04.18 이전 소스
    // var fn_change = function(o9Params){
    //     try {
    //         const commonLib = require('o9.NSCM.commonLib');
    //         const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
    //         const vdUtil = new commonLib.VdUtil();

    //         vdCommon.setLogLevel("Debug");

    //         vdCommon.printParams(o9Params);

    //         // 파라미터 가져오기
    //         var parsedParams = JSON.parse(o9Params);

    //         // var fbVersion = parsedParams.fbVersion;
    //         var fbLocation = parsedParams.fbLocation;
    //         var fbProductGroup = parsedParams.fbProductGroup;
    //         var fbSCMType = parsedParams.fbSCMType;
    //         var fbReason = parsedParams.fbReason;
    //         // var fbFPHorizon = "&FPHorizon";

    //         var dimension = ["&CWVUI"
    //                         ,"[Location].[Location].[" + fbLocation + "]"
    //                         ,"[Product].[Product Group].[" + fbProductGroup + "]"
    //                         ,"[Item].[SCM Type].[" + fbSCMType + "]"];

    //         // Main MG
    //         vdCommon.updateMeasure(dimension
    //                                 ,['Measure.[SOP Frozen Period_Reason]        = "' + fbReason + '";'
    //                                 ,'Measure.[SOP Frozen Period_Status]         = "Chg";'
    //                                 ,'Measure.[SOP Frozen Period_Update Time]    = now();'
    //                                 ,'Measure.[SOP Frozen Period_Updated By]     = CurrentUser().[User Name];'
    //                             ]);
    //         // Detail MG
    //         var dimensionW = [...dimension];    // dimension 을 복사후 추가 (Main MG의 Grain 에서 추가되는 경우 활용)
    //         dimensionW.push(FPHorizon);
    //         vdCommon.updateMeasure(dimensionW
    //                                 ,['Measure.[SOP Frozen Period W_Period LockFlag] = false;'
    //                                 ,'Measure.[SOP Frozen Period W_Period Type.Lock] = null;'
    //                             ]);
            
    //         vdCommon.programEnd();

    //     } catch ( e ) {
    //         RuleOutputToUI = { Status : 'Error', Message : "Js Logic Error : " + e.message };
    //         return;
    //     }
    // };

    // 다건 선택 처리 2025.04.18 이후 변경
    var fn_change = function(o9Params){
        try {
            const commonLib = require('o9.NSCM.commonLib');
            const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
            const vdUtil = new commonLib.VdUtil();

            vdCommon.setLogLevel("Debug");

            vdCommon.printParams(o9Params);

            // 파라미터 가져오기
            var parsedParams = JSON.parse(o9Params);
            var fbReason = parsedParams.fbReason;

            let tupleList       = parsedParams.fbListTuple;
            var dimension = [];

            for ( var i = 0; i < tupleList.length; i++ ) {
                const row      = tupleList[i];
                fbLocation       = row.fbLocation.Value;
                fbProductGroup   = row.fbProductGroup.Value;
                fbSCMType        = row.fbSCMType.Value;

                dimension = ["&CWVUI"
                            ,"[Location].[Location].[" + fbLocation + "]"
                            ,"[Product].[Product Group].[" + fbProductGroup + "]"
                            ,"[Item].[SCM Type].[" + fbSCMType + "]"];

                // Main MG
                vdCommon.updateMeasure(dimension
                                      ,['Measure.[SOP Frozen Period_Reason]        = "' + fbReason + '";'
                                      ,'Measure.[SOP Frozen Period_Status]         = "Chg";'
                                      ,'Measure.[SOP Frozen Period_Update Time]    = now();'
                                      ,'Measure.[SOP Frozen Period_Updated By]     = CurrentUser().[User Name];'
                                    ]);

                // Detail MG
                var dimensionW = [...dimension];    // dimension 을 복사후 추가 (Main MG의 Grain 에서 추가되는 경우 활용)
                dimensionW.push(FPHorizon);
                vdCommon.updateMeasure(dimensionW
                                        ,['Measure.[SOP Frozen Period W_Period LockFlag] = false;'
                                        ,'Measure.[SOP Frozen Period W_Period Type.Lock] = null;'
                                    ]);
            }

            // var fbLocation = parsedParams.fbLocation;
            // var fbProductGroup = parsedParams.fbProductGroup;
            // var fbSCMType = parsedParams.fbSCMType;
            // var fbReason = parsedParams.fbReason;

            // var dimension = ["&CWVUI"
            //                 ,"[Location].[Location].[" + fbLocation + "]"
            //                 ,"[Product].[Product Group].[" + fbProductGroup + "]"
            //                 ,"[Item].[SCM Type].[" + fbSCMType + "]"];

            // // Main MG
            // vdCommon.updateMeasure(dimension
            //                         ,['Measure.[SOP Frozen Period_Reason]        = "' + fbReason + '";'
            //                         ,'Measure.[SOP Frozen Period_Status]         = "Chg";'
            //                         ,'Measure.[SOP Frozen Period_Update Time]    = now();'
            //                         ,'Measure.[SOP Frozen Period_Updated By]     = CurrentUser().[User Name];'
            //                     ]);
            // // Detail MG
            // var dimensionW = [...dimension];    // dimension 을 복사후 추가 (Main MG의 Grain 에서 추가되는 경우 활용)
            // dimensionW.push(FPHorizon);
            // vdCommon.updateMeasure(dimensionW
            //                         ,['Measure.[SOP Frozen Period W_Period LockFlag] = false;'
            //                         ,'Measure.[SOP Frozen Period W_Period Type.Lock] = null;'
            //                     ]);
            
            vdCommon.programEnd();

        } catch ( e ) {
            RuleOutputToUI = { Status : 'Error', Message : "Js Logic Error : " + e.message };
            return;
        }
    };

    /**
     * fn_Validation
     * UI 화면의 Validation Check : [Change]
     * Confirm 할수 있는 데이터 체크
     * @param {*} o9Params 
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
            let tupleList = parsedParams.fbListTuple;
            let parseTupleSize = parsedParams.fbListTuple.length;
            let returnValue = 0;    // 0: 정상, 1: 오류메세지
            let fbActionBtnType = parsedParams.fbActionBtnType;   // Action Button Type

            vdCommon.debug("parseTupleSize size =======>"+ parseTupleSize);

            if( fbActionBtnType == null || fbActionBtnType === ""){
                returnString = "Action Button 이 정의되지 않았습니다.";
                RuleOutputToUI = { Status : 'Error', Message : returnString };
                returnValue = 1;    // 오류                    
                return returnValue;
            }

            // Change Validation  => 멀티 선택으로 변경 테스트 심명보p 요청 2025.04.17 
            // if ( fbActionBtnType == "change" ){

            //     if ( parseTupleSize == 0){
            //         returnString = "1개의 행을 선택하세요.";
            //         RuleOutputToUI = { Status : 'Error', Message : returnString };
            //         returnValue = 1;    // 오류
            //         return returnValue;
            //     }

            //     if ( parseTupleSize > 1){
            //         returnString = "1건만 선택할 수 있습니다.";
            //         RuleOutputToUI = { Status : 'Error', Message : returnString };
            //         returnValue = 1;    // 오류
            //         return returnValue;
            //     }
            // }
            vdCommon.programEnd();
            return returnValue;       // 0 : 정상, 1 : 오류
        } catch ( e ) {
            RuleOutputToUI = { Status : 'Error', Message : "Js Logic Error : " + e.message };
            return;
        }
    };

    return{
          fn_locationCombo : fn_locationCombo
         ,fn_productGroupCombo : fn_productGroupCombo
         ,fn_SCMTypeCombo : fn_SCMTypeCombo
         ,fn_add : fn_add
         ,fn_delete : fn_delete
         ,fn_clear : fn_clear
         ,fn_confirm : fn_confirm
         ,fn_change : fn_change
         ,fn_validation : fn_validation
    };
});
/* 2025.04.18 : fn_change - multi 선책 처리로 변경 - 노보람p 요청 */