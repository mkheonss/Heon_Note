define('o9.NSCM.JSCodeMapLCM', ['o9/data/query', 'o9/data/cellset', 'o9.NSCM.commonLib'], function(){

    const programName = "o9.NSCM.JSCodeMapLCM";

    // From Site
    var fn_locationCombo = function(o9Params){
        try {
            const commonLib = require('o9.NSCM.commonLib');
            const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
            vdCommon.setLogLevel("Debug");
            // dimension, measure, where, orderby, limit
            var where = "";
            var result = vdCommon.selectList(["&MFStageLCMLocation"],  // Location.[MF Site Stage].[LCM].relatedmembers(Location)
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

    // To Site
    var fn_subLocationCombo = function(o9Params){
        try {
            const commonLib = require('o9.NSCM.commonLib');
            const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
            vdCommon.setLogLevel("Debug");
            vdCommon.printParams(o9Params);
            // 파라메타 가져오기
            let parsedParams = JSON.parse(o9Params);
            let fbLocation = parsedParams.fbLocation;

            var result = vdCommon.selectList(["&MFStageSETSubLocation.unionwith(&MFStageKDSubLocation)"],   // MF Site Stage in ('SET', 'KD') => 2024.12.06 (MF All) 동일 노보람P
                                             [],
                                             "",
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

    // PO Item (To Item)
    var fn_itemCombo = function(o9Params){
        try {
            const commonLib = require('o9.NSCM.commonLib');
            const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
            const vdUtil = new commonLib.VdUtil();
            vdCommon.setLogLevel("Debug");
            vdCommon.printParams(o9Params);

            // 파라미터 가져오기
            var parsedParams = JSON.parse(o9Params);
            var fbLocation = parsedParams.fbLocation;
            var fbBtnType = parsedParams.fbBtnType; // Button Type = Copy / Add  삭제 예정.. 
            var itemStartswith = "BN95%";   // add 2025.05.02 (임재민p요청)

            // PO Item 콤보 리스트 변경 History
            // 1. Item.Item
            // 2. BOD Item
            // 3. &LCMItem -> (BOD Item 에 없는것도 등록해야 함)
            // 4. &LCMItem 데이타가 많아 MG 변경 -> Item Site Asn (where { Measure.[Item Site Asn_Cur Status] == "ACTIVE" || Measure.[Item Site Asn_Cur Status] == "PLANNED" })
            // LCM Item 2024.11.01 수정, 건수를 줄일수 있는 방법 문의 ( 2025.01.14 류원빈p 줄이는 방법 없다는 답변)
            // Item Site Asn 메저의 Item 을 가져온다 2025.02.14 (김기복P 요청)
            // 5. LCM Code MAP 로 변경 (2025.04.17 노보람p, 임재민p)
            
            var where = 'where {'
            +' &CWVUI'
            +', [Location].[Location]'+ vdUtil.fn_filterStr(fbLocation)
            +', Measure.[LCM Code MAP_Status] != "COM" '
            +', [Item].[Item]'+vdUtil.fn_filterStr(itemStartswith)
            +'}';
            // Select ([To Item].[To Item]) on row, () on column where { &CWVUI, [Location].[Location].filter(#.Name == "P551LCD"), Measure.[LCM Code MAP_Status] != "COM" }  ;
            var result = vdCommon.selectList(["[To Item].[To Item]"],
                                            "",
                                            where, // where
                                            "", // orderby
                                            "");  // limit 1000

            vdCommon.printCsData(result, 3);

            var comboList = vdCommon.fn_makeCombo(result, {DimName : "To Item", DimAttbName : "To Item", Sort : "DisplayName", existAll : false});
            vdCommon.debug("ComboData : " + JSON.stringify(comboList));

            vdCommon.programEnd();

            return comboList;
        } catch ( e ) {
            RuleOutputToUI = { Status : 'Error', Message : "Js Logic Error : " + e.message };
            return;
        }
    };

    // Prod Item (From Item) , 현재 LCM Item
    var fn_prodItemCombo = function(o9Params){
        try {
            const commonLib = require('o9.NSCM.commonLib');
            const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
            const vdUtil = new commonLib.VdUtil();
            vdCommon.setLogLevel("Debug");

            vdCommon.printParams(o9Params);

            // 파라미터 가져오기
            var parsedParams = JSON.parse(o9Params);
            var fbLocation = parsedParams.fbLocation;
            var fbPOItem = parsedParams.fbPOItem;
            var itemStartswith = "BN95%";   // add 2025.05.02 (임재민p요청)

            // // LCM 2024.11.01 수정 건수를 줄일수 있는 방법 문의 ( 2025.01.14 류원빈p 줄이는 방법 없다는 답변)
            // // Item Site Asn 메저의 Item 을 가져온다 2025.02.14 (김기복P 요청)
            // dims.push("&LCMItem");  
            // var where = 'where { Measure.[Item Site Asn_Cur Status] == "ACTIVE" || Measure.[Item Site Asn_Cur Status] == "PLANNED" }';

            // 2025.03.24 이전
            // var where = 'where {'
            //                 +' &CWVUI'
            //                 +', [Location].[Location]'+ vdUtil.fn_filterStr(fbLocation)
            //                 +', Measure.[Item Site Asn_Cur Status] == "ACTIVE" || Measure.[Item Site Asn_Cur Status] == "PLANNED" '
            //                 +'}';            
            // var result = vdCommon.selectList(["&LCMItem"],
            //                                 ["Measure.[Item Site Asn_Cur Status]"],
            //                                 where, // where                                           
            //                                 "",
            //                                 "");  //"limit 1000"

            // LCM Code MAP 의 To Item 을 매핑해서 Item.Item 을 가져오기 - 2025.03.24 변경 : 노보람P요청
            // 5. LCM Code MAP 조건 추가 (2025.04.17 노보람p, 임재민p)
            var where = 'where {'
                            +' &CWVUI'
                            +', [Location].[Location]'+ vdUtil.fn_filterStr(fbLocation)
                            +', [To Item].[To Item]'+ vdUtil.fn_filterStr(fbPOItem)
                            +', Measure.[LCM Code MAP_Status] != "COM" '
                            +'}';
            var result = vdCommon.selectList(["[Item].[Item]"+vdUtil.fn_filterStr(itemStartswith)],
                                            "",//["Measure.[LCM Code MAP_Status]"],
                                            where, // where                                           
                                            "",
                                            "");  //"limit 1000"

            vdCommon.printCsData(result, 3);

            var comboList = vdCommon.fn_makeCombo(result, {DimName : "Item", DimAttbName : "Item", Sort : "DisplayName", existAll : false});
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
            var fbPOItem = parsedParams.fbPOItem;
            var fbProdItem = parsedParams.fbProdItem;

            var dimension = ["&CWVUI"
                            ,"[Location].[Location].[" + fbLocation + "]"
                            ,"[Sub Location].[Sub Location].[" + fbSubLocation + "]"
                            ,"[Item].[Item].[" + fbPOItem + "]"];
            // 중복체크
            if ( vdCommon.existMeasure(dimension
                                      ,["Measure.[Code Map LCM_Valid Flag]"
                                       ,"Measure.[Code Map LCM_Map Status]"
                                       ,"Measure.[Code Map LCM_Prod Item]"
                                       ,"Measure.[Code Map LCM_Created By]"
                                       ,"Measure.[Code Map LCM_Creation Time]"
                                       ,"Measure.[Code Map LCM_Update Time]"
                                       ,"Measure.[Code Map LCM_Updated By]"]
                                      , "") ) {
                RuleOutputToUI = { Status : 'Error', Message : "The data has already been registered." };
                return;
            }

            // Main MG 생성
            vdCommon.createMeasure(dimension, ['Measure.[Code Map LCM_Valid Flag]     = "Y";']);
            vdCommon.updateMeasure(dimension, ['Measure.[Code Map LCM_Map Status]     = "COM";'
                                             , 'Measure.[Code Map LCM_Prod Item]      = "' + vdUtil.fn_getString(fbProdItem) + '";'
                                             , 'Measure.[Code Map LCM_Created By]     = CurrentUser().[User Name];'
                                             , 'Measure.[Code Map LCM_Creation Time]  = dateadd(Now(),9,"hour");'
                                             , 'Measure.[Code Map LCM_Update Time]    = dateadd(Now(),9,"hour");'
                                             , 'Measure.[Code Map LCM_Updated By]     = CurrentUser().[User Name];'
                                            ]);
            
            vdCommon.programEnd();
        } catch ( e ) {
            RuleOutputToUI = { Status : 'Error', Message : "Js Logic Error : " + e.message };
            return;
        }
    };

    var fn_reqChg = function(o9Params){
        try {
            const commonLib = require('o9.NSCM.commonLib');
            const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
            const vdUtil = new commonLib.VdUtil();

            vdCommon.setLogLevel("Debug");
            vdCommon.printParams(o9Params);

            // 파라미터 가져오기
            var parsedParams = JSON.parse(o9Params);

            // Row 선택 데이터 (원본 데이터)
            let tupleList = parsedParams.fbTupleList;
            let fbLocation_org = "", fbSubLocation_org = "", fbPOItem_org = "";
            for (let i=0; i < tupleList.length; i++) {
                const row = tupleList[i];
                fbLocation_org = row.fbLocation.Value;
                fbSubLocation_org = row.fbSubLocation.Value;
                fbPOItem_org = row.fbPOItem.Value;
            }

            // 입력할 데이터
            var fbLocation = parsedParams.fbLocation;
            var fbSubLocation = parsedParams.fbSubLocation;
            var fbPOItem = parsedParams.fbPOItem;
            var fbProdItem = parsedParams.fbProdItem;

            // MG의 Measure 정의
            let measure = ["Measure.[Code Map LCM_Valid Flag]"
                          ,"Measure.[Code Map LCM_Map Status]"
                          ,"Measure.[Code Map LCM_Prod Item]"
                          ,"Measure.[Code Map LCM_Created By]"
                          ,"Measure.[Code Map LCM_Creation Time]"
                          ,"Measure.[Code Map LCM_Update Time]"
                          ,"Measure.[Code Map LCM_Updated By]"];

            let measureDefault = ['Measure.[Code Map LCM_Created By]     = CurrentUser().[User Name];'
                                ,'Measure.[Code Map LCM_Creation Time]   = dateadd(Now(),9,"hour");'
                                ,'Measure.[Code Map LCM_Update Time]     = dateadd(Now(),9,"hour");'
                                ,'Measure.[Code Map LCM_Updated By]      = CurrentUser().[User Name];'
                                ,'Measure.[Code Map LCM_Map Status]      = "COM";'
                                ,'Measure.[Code Map LCM_Valid Flag]      = "Y";'
                                ,'Measure.[Code Map LCM_Prod Item]       = "'+ fbProdItem +'";'
                                ];

            let dimension = ["&CWVUI"
                            ,"[Location].[Location].[" + fbLocation_org + "]"
                            ,"[Sub Location].[Sub Location].[" + fbSubLocation_org + "]"
                            ,"[Item].[Item].[" + fbPOItem_org + "]"];
            //------------------------------------------------------------------------------------------------------------//
            // 1. 선택 Row Data와 팝업 Data 의 Grain이 동일할 경우 update
            //------------------------------------------------------------------------------------------------------------//
            vdCommon.debug(" 1. REQ Data 처리___________________________");

            // 선택 Row 데이터와 팝업 데이터의 Grain이 동일 할 경우
            if ( fbLocation_org == fbLocation && fbSubLocation_org == fbSubLocation && fbPOItem_org == fbPOItem){
                vdCommon.updateMeasure(dimension, measureDefault);
            
            //------------------------------------------------------------------------------------------------------------//
            // 2. 선택 Row Data와 팝업 Data Grain이 이 다를 경우
            //------------------------------------------------------------------------------------------------------------//
            }else{
                //------------------------------------------------------------------------------------------------------------//
                // 2-1. 선택 Row 삭제
                //------------------------------------------------------------------------------------------------------------//
                vdCommon.deleteMeasure(dimension, "Code Map LCM");

                //------------------------------------------------------------------------------------------------------------//
                // 2-2 COM Data 처리 Valid Flag = 'Y', Map Status = 'COM', Item = parsedParams.fbPOItem (dim) , Prod Item = parsedParams.fbProdItem
                // Update or Create
                //------------------------------------------------------------------------------------------------------------//
                vdCommon.debug(" 2. COM Data 처리___________________________");
                let dimensionNew = ["&CWVUI"
                                ,"[Location].[Location].[" + fbLocation + "]"
                                ,"[Sub Location].[Sub Location].[" + fbSubLocation + "]"
                                ,"[Item].[Item].[" + fbPOItem + "]"];

                // 중복시 체크 - 기존데이터 여부 메세지
                if ( vdCommon.existMeasure(dimensionNew, measure, "") ) {
                    RuleOutputToUI = { Status : 'Error', Message : "The data has already been registered." };
                    return;
                }else{ // create
                    vdCommon.createMeasure(dimensionNew, ['Measure.[Code Map LCM_Valid Flag] = "Y";']);
                    vdCommon.updateMeasure(dimensionNew, measureDefault);
                }
            }
            
            vdCommon.programEnd();
        } catch ( e ) {
            RuleOutputToUI = { Status : 'Error', Message : "Js Logic Error : " + e.message };
            return;
        }
    };

    var fn_validation = function(o9Params){
        try {
            const commonLib = require('o9.NSCM.commonLib');
            const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
            const vdUtil = new commonLib.VdUtil();

            vdCommon.setLogLevel("Debug");
            vdCommon.printParams(o9Params);

            // 파라미터 가져오기
            var parsedParams = JSON.parse(o9Params);
            // Tuple 정확히 가져올때, 동일한 값만 있는 경우 Merge 됨, key 가 되는 dim 을 모두 표기
            let tupleList = parsedParams.fbTupleList;
            let fbLocation = "";
            let returnValue = 0;    // 0: 정상, 1: 오류메세지

            if ( tupleList.length > 1){
                returnString = "1건만 선택할 수 있습니다.";
                RuleOutputToUI = { Status : 'Error', Message : returnString };
                returnValue = 1;    // 오류
                return returnValue;
            }

            for (let i=0; i < tupleList.length; i++) {
                const row = tupleList[i];
                fbLocation = row.fbLocation.Value;
                if( fbLocation != null && fbLocation == "-" ){
                    returnString = "From Site : '-' 선택할 수 없습니다.";
                    RuleOutputToUI = { Status : 'Error', Message : returnString };
                    returnValue = 1;    // 오류
                    return returnValue;
                }
            }

            let fbMapStatus = parsedParams.fbMapStatus;
            if( fbMapStatus != null && fbMapStatus != "REQ" ){
                returnString = "Map Status가 REQ 일 경우만 변경 가능합니다.";
                RuleOutputToUI = { Status : 'Error', Message : returnString };
                returnValue = 1;    // 오류
                return returnValue;
            }

            vdCommon.programEnd();

            return returnValue;       // 0 : 정상, 1 : 오류            
            
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

            let tupleList       = parsedParams.fbTupleList;
            let fbLocation = "", fbSubLocation = "", fbPOItem = "";            

            for ( var i = 0; i < tupleList.length; i++ ) {
                const row = tupleList[i];
                fbLocation      = row.fbLocation.Value;
                fbSubLocation   = row.fbSubLocation.Value;
                fbPOItem        = row.fbPOItem.Value;

                dimension = ["&CWVUI"
                            ,"[Location].[Location].[" + fbLocation + "]"
                            ,"[Sub Location].[Sub Location].[" + fbSubLocation + "]"
                            ,"[Item].[Item].[" + fbPOItem + "]"];

                //----------------------------------------------------------------------------------//
                // Code Map LCM delete : Measure.[Code Map LCM_Valid Flag] = "N" or "Y"
                //----------------------------------------------------------------------------------//                
                vdCommon.updateMeasure(dimension,
                    ['Measure.[Code Map LCM_Valid Flag]  = "' + fbValidYN + '";',
                     'Measure.[Code Map LCM_Update Time] = dateadd(Now(),9,"hour");',
                     'Measure.[Code Map LCM_Updated By]  = CurrentUser().Name;']);
            }

            vdCommon.programEnd();
        } catch ( e ) {
            RuleOutputToUI = { Status : 'Error', Message : "Js Logic Error : " + e.message };
            return;
        }
    };

    var fn_validationConfirm = function(o9Params){
        try {
            const commonLib = require('o9.NSCM.commonLib');
            const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
            const vdUtil = new commonLib.VdUtil();

            vdCommon.setLogLevel("Debug");
            vdCommon.printParams(o9Params);

            // 파라미터 가져오기
            var parsedParams = JSON.parse(o9Params);
            vdCommon.debug("###############  fn_validationConfirm o9Params --> "+ JSON.stringify(parsedParams, null, 2));
            // Tuple 정확히 가져올때, 동일한 값만 있는 경우 Merge 됨, key 가 되는 dim 을 모두 표기
            let tupleList = parsedParams.fbTupleList;
            let fbLocation = "", fbSubLocation = "", fbPOItem = "";

            // Prod Item = null or '-' 인 경우
            let mapStatus = "", prodItem = "";
            let returnString = "";
            let returnValue = 0;    // 0: 정상, 1: 오류메세지

            for ( var i = 0; i < tupleList.length; i++ ) {
                const row = tupleList[i];
                fbLocation      = row.fbLocation.Value;
                fbSubLocation   = row.fbSubLocation.Value;
                fbPOItem        = row.fbPOItem.Value;

                dimension = ["&CWVUI"
                            ,"[Location].[Location]"+vdUtil.fn_filterStr(fbLocation)
                            ,"[Sub Location].[Sub Location]"+vdUtil.fn_filterStr(fbSubLocation)
                            ,"[Item].[Item]"+vdUtil.fn_filterStr(fbPOItem)
                            ];

                measure = ["Measure.[Code Map LCM_Map Status]","Measure.[Code Map LCM_Prod Item]"];

                let result = vdCommon.selectList(dimension, measure, '', '', '');

                if ( result.cs.rowCount > 0 ){
                    mapStatus = result.cs.row(0).cell(result.cs.measureColumnIndex("Code Map LCM_Map Status"));
                    prodItem = result.cs.row(0).cell(result.cs.measureColumnIndex("Code Map LCM_Prod Item"));
                    if( prodItem == null || prodItem === "-" ){
                        returnString = "Prod Item 확정 후 Confirm 가능합니다.";
                        RuleOutputToUI = { Status : 'Error', Message : returnString };
                        returnValue = 1;    // 오류
                        return returnValue;
                    }

                    if( mapStatus != null && mapStatus == "COM"){   // 이미 comfirm 된것 validation 사용할지 ..
                        returnString = "이미 Confirm 된 Data가 존재합니다.";
                        RuleOutputToUI = { Status : 'Error', Message : returnString };
                        returnValue = 1;    // 오류
                        return returnValue;
                    }
                }
            }

            vdCommon.programEnd();

            return returnValue;       // 0 : 정상
            
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
            vdCommon.debug("==================>fn_confirm");
            vdCommon.printParams(o9Params);

            // 파라미터 가져오기
            var parsedParams = JSON.parse(o9Params);
            vdCommon.debug("###############  fn_confirm o9Params --> "+ JSON.stringify(parsedParams, null, 2));

            let tupleList       = parsedParams.fbTupleList;
            let fbLocation = "", fbSubLocation = "", fbPOItem = "";

            for ( var i = 0; i < tupleList.length; i++ ) {
                const row = tupleList[i];
                fbLocation      = row.fbLocation.Value;
                fbSubLocation   = row.fbSubLocation.Value;
                fbPOItem        = row.fbPOItem.Value;

                dimension = ["&CWVUI"
                            ,"[Location].[Location]"+vdUtil.fn_filterStr(fbLocation)
                            ,"[Sub Location].[Sub Location]"+vdUtil.fn_filterStr(fbSubLocation)
                            ,"[Item].[Item]"+vdUtil.fn_filterStr(fbPOItem)
                            ];

                vdCommon.updateMeasure(dimension,
                    ['Measure.[Code Map LCM_Map Status]  = "COM";',
                     'Measure.[Code Map LCM_Update Time] = dateadd(Now(),9,"hour");',
                     'Measure.[Code Map LCM_Updated By]  = CurrentUser().Name;']);
            }

            vdCommon.programEnd();
        } catch ( e ) {
            RuleOutputToUI = { Status : 'Error', Message : "Js Logic Error : " + e.message };
            return;
        }
    };

    /**
     * check Prod Item > Validation
     * @param {*} o9Params 
     * @returns 
     */
    var fn_validation_checkProdItem = function(o9Params){
        try {
            const commonLib = require('o9.NSCM.commonLib');
            const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
            const vdUtil = new commonLib.VdUtil();
            
            vdCommon.setLogLevel("Debug");
            vdCommon.printParams(o9Params);

            // 파라미터 가져오기
            var parsedParams = JSON.parse(o9Params);

            let returnString = "";
            let returnValue = 0;    // 0: 정상, 1: 오류메세지

            let where = 'where {Measure.[Code Map LCM_Valid Flag] == "Y" ,Measure.[Code Map LCM_Map Status] != "COM"}';

            let result = vdCommon.selectList(["&CWVUI", "[Location].[Location]", "[Item].[Item]", "[Sub Location].[Sub Location]"]
                                            , ["Measure.[Code Map LCM_Valid Flag]"]
                                            , where
                                            , "", "");

            if ( result.cs.rowCount == 0 ){
                returnString = "Prod Item Check 대상이 없습니다.";
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

    /**
     * checkProdItem
     * @param {*} o9Params 
     * @returns 
     */
    var fn_checkProdItem = function(o9Params){
        try {
            const commonLib = require('o9.NSCM.commonLib');
            const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
            const vdUtil = new commonLib.VdUtil();
            
            vdCommon.setLogLevel("Debug");
            vdCommon.printParams(o9Params);

            vdCommon.debug("fn_checkProdItem===>");

            // 파라미터 가져오기
            var parsedParams = JSON.parse(o9Params);

            /* Validation 호출 (PY_UI_CodeMapLCMCheckProdItem) */
            var execQuery = 'EXEC plugin instance [PY_UI_CodeMapLCMCheckProdItem] ' +
                            'for measures {[Code Map LCM_Valid Flag]} ' +
                            'using scope ( &CWVUI ) ' +
                            'using arguments {(ExecutionMode, "MediumWeight"), (MaxSliceTableCells, 200000000), (MaxConcurrency, 1), ([Param.o9_sys_log_level], "DEBUG")}; ';

            vdCommon.debug("execQuery: " + JSON.stringify(execQuery));
            vdCommon.executeQuery("fn_checkProdItem : PY_UI_CodeMapLCMCheckProdItem Run", execQuery);

            let measure = ['Measure.[Code Map LCM_Update Time] = dateadd(Now(),9,"hour");', 
                           'Measure.[Code Map LCM_Updated By] = CurrentUser().[User Name];'];

            /* Update일자, 사용자 정보입력 */
            vdCommon.updateMeasure(["&CWVUI"],  measure);

            vdCommon.programEnd();
        } catch ( e ) {
            RuleOutputToUI = { Status : 'Error', Message : "Js Logic Error : " + e.message };
            return;
        }
    };

    /**
     * Create BOD > Validation (신규 2025.05.15)
     * @param {*} o9Params 
     * @returns 
     */
    var fn_validation_createBOD = function(o9Params){
        try {
            const commonLib = require('o9.NSCM.commonLib');
            const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
            const vdUtil = new commonLib.VdUtil();
            
            vdCommon.setLogLevel("Debug");
            vdCommon.printParams(o9Params);

            // 파라미터 가져오기
            var parsedParams = JSON.parse(o9Params);

            let returnString = "";
            let returnValue = 0;    // 0: 정상, 1: 오류메세지

            let where = 'where {Measure.[VersionInfo_RunningFlag_LCMProductCopyCreateBOD] == true }';

            let result = vdCommon.selectList(["&CWVUI"]
                                            , ["Measure.[VersionInfo_RunningFlag_LCMProductCopyCreateBOD]"]
                                            , where
                                            , "", "");

            if ( result.cs.rowCount > 0 ){
                returnString = "실행중입니다.";
                RuleOutputToUI = { Status : 'Error', Message : returnString };
                returnValue = 1;    // 오류
            }
            vdCommon.debug("########################## Create BOD Check >>>  성공");
            vdCommon.programEnd();
            return returnValue;       // 0 : 정상, 1 : 오류

        } catch ( e ) {
            RuleOutputToUI = { Status : 'Error', Message : "Js Logic Error : " + e.message };
            return;
        }
    };

    /**
     * Create BOD (신규 2025.05.15)
     * @param {*} o9Params 
     * @returns 
     */
    var fn_createBOD = function(o9Params){
        try {
            const commonLib = require('o9.NSCM.commonLib');
            const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
            const vdUtil = new commonLib.VdUtil();
            
            vdCommon.setLogLevel("Debug");
            vdCommon.debug("==================>fn_createBOD");
            vdCommon.printParams(o9Params);

            // 파라미터 가져오기
            var parsedParams = JSON.parse(o9Params);
            vdCommon.debug("###############  fn_createBOD o9Params --> "+ JSON.stringify(parsedParams, null, 2));

            // 1. Flag 초기화 (Version 전체) - UI 의 Create BOD 액션버튼 실행중인지 체크
            vdCommon.updateMeasure(["&CWVUI"], ['Measure.[VersionInfo_RunningFlag_LCMProductCopyCreateBOD]  = true;']);

            // 2. Flag 초기화 - MG 선택 초기화
            vdCommon.updateMeasure(["&CWVUI"], ['Measure.[Code Map LCM_Create BOD_Target Flag]  = null;']);

            let paramLocation = parsedParams.fbLocation;
            let paramSubLocation = parsedParams.fbSubLocation;
            let paramItem = parsedParams.fbItem;

            let tupleList       = parsedParams.fbTupleList;
            let fbLocation = "", fbSubLocation = "", fbPOItem = "";

            for ( var i = 0; i < tupleList.length; i++ ) {
                const row = tupleList[i];
                fbLocation      = row.fbLocation.Value;
                fbSubLocation   = row.fbSubLocation.Value;
                fbPOItem        = row.fbPOItem.Value;

                dimension = ["&CWVUI"
                            ,"[Location].[Location]"+vdUtil.fn_filterStr(fbLocation)
                            ,"[Sub Location].[Sub Location]"+vdUtil.fn_filterStr(fbSubLocation)
                            ,"[Item].[Item]"+vdUtil.fn_filterStr(fbPOItem)
                            ];

                // 3. 선택한 row 들 intersection에 Flag 처리
                vdCommon.updateMeasure(dimension, ['Measure.[Code Map LCM_Create BOD_Target Flag]  = true;']);
            }

            // 4. PY 실행
            /* PY 호출 (PY_UI_CodeMapLCMCreateBOD) */
            var execQuery = 'EXEC plugin instance [PY_UI_CodeMapLCMCreateBOD] ' +
                            'for measures {[Code Map LCM_Create BOD_Target Flag]} ' +
                            // 'using scope ( &CWVUI ) ' +
                            'using scope ( &CWVUI * [Location].[Location]' + vdUtil.fn_filterStr(paramLocation) + ' * ' +
                            '[Sub Location].[Sub Location]'+ vdUtil.fn_filterStr(paramSubLocation) + ' * ' +
                            '[Item].[Item]'+ vdUtil.fn_filterStr(paramItem) + 
                            ' )'+
                            'using arguments {(ExecutionMode, "MediumWeight"), (MaxSliceTableCells, 200000000), (MaxConcurrency, 1), ([Param.o9_sys_log_level], "DEBUG")}; ';

            vdCommon.debug("execQuery: " + JSON.stringify(execQuery));
            vdCommon.executeQuery("fn_createBOD : PY_UI_CodeMapLCMCreateBOD Run", execQuery);

            let measure = ['Measure.[Code Map LCM_Update Time] = dateadd(Now(),9,"hour");', 
                           'Measure.[Code Map LCM_Updated By] = CurrentUser().[User Name];'];

            /* Update일자, 사용자 정보입력 */
            vdCommon.updateMeasure(["&CWVUI"],  measure);

            // 5. PY 종료 후 Flag 원복
            vdCommon.updateMeasure(["&CWVUI"], ['Measure.[VersionInfo_RunningFlag_LCMProductCopyCreateBOD]  = false;']);
            vdCommon.updateMeasure(["&CWVUI"], ['Measure.[Code Map LCM_Create BOD_Target Flag]  = null;']);

            vdCommon.programEnd();
        } catch ( e ) {
            // RuleOutputToUI = { Status : 'Error', Message : "Js Logic Error : " + e.message };
            // 실패시 Flag 원복
            vdCommon.updateMeasure(["&CWVUI"], ['Measure.[VersionInfo_RunningFlag_LCMProductCopyCreateBOD]  = false;']);
            vdCommon.updateMeasure(["&CWVUI"], ['Measure.[Code Map LCM_Create BOD_Target Flag]  = null;']);

            RuleOutputToUI = { Status : 'Error', Message : "Js Logic Error : " + e.message };
            return;
        }
    };

    return{
        fn_locationCombo : fn_locationCombo
       ,fn_subLocationCombo : fn_subLocationCombo
       ,fn_itemCombo : fn_itemCombo
       ,fn_prodItemCombo : fn_prodItemCombo
       ,fn_add : fn_add
       ,fn_reqChg : fn_reqChg
       ,fn_validYN : fn_validYN
       ,fn_validation : fn_validation
       ,fn_validationConfirm : fn_validationConfirm
       ,fn_confirm : fn_confirm
       ,fn_validation_checkProdItem : fn_validation_checkProdItem
       ,fn_checkProdItem : fn_checkProdItem
       ,fn_validation_createBOD : fn_validation_createBOD
       ,fn_createBOD : fn_createBOD
    };
});

/*-------------------------------------------------------------------------------------------------*/
/* programName : o9.NSCM.JSCodeMapLCM */
/* 수정 2024.12.10 fn_reqChg 변경  */
/* 수정 2025.03.06 combo list 수정 */
/* 수정 2025.03.24 combo list 수정 - Prod Item 변경 - 노보람p요청               */
/* 수정 2025.04.17 combo list 수정 - PO Item 변경   - 임재민p, 노보람p요청      */
/* 수정 2025.04.22 fn_validation, fn_reqChg : 멀티선택으로 변경 - 이도연p요청   */
/* 수정 2025.05.02 fn_validationConfirm, fn_confirm : add - 임재민p요청                               */
/* 수정 2025.05.12 fn_validation_checkProdItem, fn_checkProdItem : check Prod Item 버튼생성 - 임재민p요청   */
/* 수정 2025.05.15 fn_validation_createBOD, fn_createBOD : Create BOD 버튼생성 - 임재민p요청   */
/*-------------------------------------------------------------------------------------------------*/