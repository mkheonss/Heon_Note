define('o9.NSCM.JSBODListSET', ['o9/data/query', 'o9/data/cellset', 'o9.NSCM.commonLib'], function(){

    const programName = "o9.NSCM.JSBODListSET";

    var fn_locationCombo = function(o9Params){
        try {            
            const commonLib = require('o9.NSCM.commonLib');
            const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);

            vdCommon.setLogLevel("Debug");

            var parsedParams = JSON.parse(o9Params);
            let fbButtonType = parsedParams.fbButtonType;   //fbButtonType : bod / prod

            let where = "";
            if ( fbButtonType != null && fbButtonType == "prod"){
                where = "where { &CWVUI, Measure.[BOD List_BOD Valid] == Y}";
            }
            // dimension, measure, where, orderby, limit
            var result = vdCommon.selectList(["&MFStageSETLocation"], // 2024.10.29 변경 &SETLocation
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
            let fbButtonType = parsedParams.fbButtonType;   //fbButtonType : bod / prod

            let where = "";
            if ( fbButtonType != null && fbButtonType == "prod"){
                where = "where { &CWVUI"
                            +",[Location].[Location].["+fbLocation+"]"
                            +", Measure.[BOD List_BOD Valid] == Y"
                            +"}";
            } else {
                // where = "where { &CWVUI"
                //             +",[Location].[Location].["+fbLocation+"]"
                //             +"}";                
            }
            // Site(To)는 DC만 나와야 함, [Location].[Location Type] = 'DC'
            // var result = vdCommon.selectList(["[Sub Location].[Sub Location]","[Sub Location].[Sub Location Type].[DC]"],   //["[Sub Location].[Sub Location]"]
            var result = vdCommon.selectList(["&NSUISubLocationDC"],   //["[Sub Location].[Sub Location]"]
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

            let fbButtonType = parsedParams.fbButtonType;   //fbButtonType : bod / prod

            // dims.push('[Trans Mode].[Trans Mode].filter(#.Name in {"AIR","TRUCK","VESSEL"})');      // "AIR", "TRUCK", "VESSEL"
            // select [Trans Mode].[Trans Mode].filter(#.Name in {"VESSEL","TRUCK","RAIL","AIR","EXPRESS","VESSEL1"});  // 2025.03.06 문지윤p 요청 

            if ( fbButtonType != null && fbButtonType == "prod"){
                // var dims = [];
                // dims.push("&CWVUI");
                // dims.push("Location.[Location].[" + fbLocation + "]");
                // dims.push("[Sub Location].[Sub Location].[" + fbSubLocation + "]");
                // dims.push("&NSUITransModeView");
                var where = 'where {'
                                +' &CWVUI'
                                +', [Location].[Location]'+ vdUtil.fn_filterStr(fbLocation)
                                +', [Sub Location].[Sub Location]'+ vdUtil.fn_filterStr(fbSubLocation)
                                +', Measure.[BOD List_BOD Valid] == "Y" '
                                +'}';
                
                var result = vdCommon.selectList(["&NSUITransModeView"],
                                                 ["Measure.[BOD List_BOD Valid]"],
                                                where,
                                                "",
                                                "");

            } else {
                // Measure 에 등록된 Trans Mode 를 제외하고 보여준다. => BOD List
                // var dims = [];
                // dims.push("&CWVUI");
                // dims.push("Location.[Location].[" + fbLocation + "]");
                // dims.push("[Sub Location].[Sub Location].[" + fbSubLocation + "]");
                // dims.push("&NSUITransModeView");
                // dims.push('[Trans Mode].[Trans Mode].filter(#.Name in {"AIR","TRUCK","VESSEL"})');      // "AIR", "TRUCK", "VESSEL"

                var where = 'include nulls where {'
                                +' &CWVUI'
                                +', [Location].[Location]'+ vdUtil.fn_filterStr(fbLocation)
                                +', [Sub Location].[Sub Location]'+ vdUtil.fn_filterStr(fbSubLocation)                                
                                +'} .filter(isnull(Measure.[BOD List_BOD Valid]))';

                // Measure Group(Code Map LCM) 에 등록된 Item 을 제외하고 보여준다.
                var result = vdCommon.selectList(["&NSUITransModeView"],
                                                 ["Measure.[BOD List_BOD Valid]"],
                                                // "include nulls .filter(isnull(Measure.[BOD List_BOD Valid]))",
                                                where,
                                                "",   //  "orderby [Item].[Item].Name",
                                                "");
            }

            // // Measure 에 등록된 Trans Mode 를 제외하고 보여준다.
            // // 2024.09.11 변경
            // let query = `
            //             select ( 
            //                 &TransMode
            //             ) on row, 
            //             ({Measure.[BOD List_BOD Valid]}) on column 
            //             include nulls
            //             where {
            //                   Version.[Version Name].filter(#.Name == "${fbVersion}")
            //                 , [Location].[Location].filter(#.Name == "${fbLocation}")
            //                 , [Sub Location].[Sub Location].filter(#.Name == "${fbSubLocation}")
            //             }.filter(isnull(Measure.[BOD List_BOD Valid]))
            //             orderby [Trans Mode].[Trans Mode].Name ;   `;

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

    var fn_productCombo = function(o9Params){
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

            // Measure 에 등록된 Trans Mode 를 제외하고 보여준다. => BOD List
            // var dims = [];
            // dims.push("&CWVUI");
            // dims.push("Location.[Location].[" + fbLocation + "]");
            // dims.push("[Sub Location].[Sub Location].[" + fbSubLocation + "]");
            // dims.push("[Item].[Product]");

            // [Item].[Item Stage].[SET] => SET/LCM 구분
            // let where = "include nulls where {[Item].[Item Stage].[SET]}.filter(isnull(Measure.[BOD Prod SET_BOD LT]) || isnull(Measure.[BOD Prod SET_Priority]) || isnull(Measure.[BOD Prod SET_Shipment LT]))";
            var where = 'include nulls where {'
                            +' &CWVUI'
                            +', [Location].[Location]'+ vdUtil.fn_filterStr(fbLocation)
                            +', [Sub Location].[Sub Location]'+ vdUtil.fn_filterStr(fbSubLocation)
                            +', [Item].[Item Stage].[SET]'
                            +'}.filter(isnull(Measure.[BOD Prod SET_BOD LT]) || isnull(Measure.[BOD Prod SET_Priority]) || isnull(Measure.[BOD Prod SET_Shipment LT])) ';

            // Measure Group(Code Map LCM) 에 등록된 Item 을 제외하고 보여준다.
            var result = vdCommon.selectList(["[Item].[Product]"],
                                            ["Measure.[BOD Prod SET_BOD LT]"
                                            ,"Measure.[BOD Prod SET_Priority]"
                                            ,"Measure.[BOD Prod SET_Shipment LT]"]
                                            ,where
                                            ,"orderby [Item].[Product].Name"
                                            ,"");

            vdCommon.printCsData(result, 3);

            var comboList = vdCommon.fn_makeCombo(result, {DimName : "Item", DimAttbName : "Product", Sort : "DisplayName", existAll : false});
            vdCommon.debug("ComboData : " + JSON.stringify(comboList));

            vdCommon.programEnd();

            return comboList;
        } catch ( e ) {
            RuleOutputToUI = { Status : 'Error', Message : "Js Logic Error : " + e.message };
            return;
        }
    };

    var fn_addBODList = function(o9Params){
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

            var dimension = ["&CWVUI"
                            ,"[Location].[Location].[" + fbLocation + "]"
                            ,"[Sub Location].[Sub Location].[" + fbSubLocation + "]"
                            ,"[Trans Mode].[Trans Mode].[" + fbTPMode + "]"];

            // 중복체크
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
                RuleOutputToUI = { Status : 'Error', Message : "The data has already been registered." };
                return;
            }

            // BOD List MG 생성
            // vdCommon.createMeasure(dimension
            //                       ,['Measure.[BOD List_BOD Frozen]      = null;'       // 다른 UI 에서 data 가져올 예정, 현재 미정의 상태(2024.06.25)
            //                       , 'Measure.[BOD List_BOD LT]          = null;'
            //                       , 'Measure.[BOD List_BOD Valid]       = "Y";'
            //                       , 'Measure.[BOD List_Created By]      = CurrentUser().[User Name];'
            //                       , 'Measure.[BOD List_Creation Time]   = dateadd(Now(),9,"hour");'
            //                       , 'Measure.[BOD List_Eff Enddate]     = null;'
            //                       , 'Measure.[BOD List_Eff Startdate]   = null;'
            //                       , 'Measure.[BOD List_Priority]        = null;'
            //                       , 'Measure.[BOD List_Shipment LT]     = null;'
            //                       , 'Measure.[BOD List_Time Phased BOD LT]       = null;'
            //                       , 'Measure.[BOD List_Time Phased Shipment LT]  = null;'
            //                       , 'Measure.[BOD List_Update Time]     = dateadd(Now(),9,"hour");'
            //                       , 'Measure.[BOD List_Updated By]      = CurrentUser().[User Name];'
            //                       ]);
            // BOD Prod SET 은 BOD List 데이터 수정시 Spreading 으로 BOD Item 을 생성 or update 한다.
            // BOD Item 은 Batch 에서 생성, BOD List 데이터 수정시 Spreading 으로 BOD Item 을 생성 or update 한다.
            vdCommon.createMeasure(dimension, ['Measure.[BOD List_BOD Valid]       = "Y";']);
            vdCommon.updateMeasure(dimension, ['Measure.[BOD List_Created By]      = CurrentUser().[User Name];'
                                             , 'Measure.[BOD List_Creation Time]   = dateadd(Now(),9,"hour");'
                                             , 'Measure.[BOD List_Update Time]     = dateadd(Now(),9,"hour");'
                                             , 'Measure.[BOD List_Updated By]      = CurrentUser().[User Name];'
                                             , 'Measure.[BOD List_is New Flag]     = true;'     // BOD Item Python 튜닝에서 사용 (2025.04.23 임재민p요청)
                                            ]);

            vdCommon.programEnd();
        } catch ( e ) {
            RuleOutputToUI = { Status : 'Error', Message : "Js Logic Error : " + e.message };
            return;
        }
    };

    var fn_validYNBODList = function(o9Params){
        try {
            const commonLib = require('o9.NSCM.commonLib');
            const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
            const vdUtil = new commonLib.VdUtil();

            vdCommon.setLogLevel("Debug");
            vdCommon.printParams(o9Params);

            // 파라미터 가져오기
            var parsedParams = JSON.parse(o9Params);
            let fbValidYN = parsedParams.fbValidYN;

            // Tuple List 변수 
            let tupleList  = parsedParams.fbBODListTuple;
            let fbLocation = "", fbSubLocation = "", fbTPMode = "";
            let dimBodList = [];
            let dimBodProd = [];

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
                // BOD List delete : Measure.[BOD List_BOD Valid] = "N"
                //----------------------------------------------------------------------------------//                
                vdCommon.updateMeasure(dimBodList,
                                        ['Measure.[BOD List_BOD Valid] = "' + fbValidYN + '";',
                                         'Measure.[BOD List_Update Time] = dateadd(Now(),9,"hour");',
                                         'Measure.[BOD List_Updated By] = CurrentUser().Name;']);
                //----------------------------------------------------------------------------------//
                // BOD Prod SET delete : Measure.[BOD Prod SET_BOD Valid] = "N"
                //----------------------------------------------------------------------------------//
                dimBodProd = [...dimBodList];
                dimBodProd.push("[Item].[Product]");

                vdCommon.updateMeasure(dimBodProd,
                                        ['Measure.[BOD Prod SET_BOD Valid] = "' + fbValidYN + '";',
                                        'Measure.[BOD Prod SET_Update Time] = dateadd(Now(),9,"hour");',
                                        'Measure.[BOD Prod SET_Updated By] = CurrentUser().Name;']);
            }

            vdCommon.programEnd();
        } catch ( e ) {
            RuleOutputToUI = { Status : 'Error', Message : "Js Logic Error : " + e.message };
            return;
        }
    };

    /**
     * BOD Product SET : Add
     * @param {*} o9Params 
     * @returns 
     */
    var fn_addProdSET = function(o9Params){
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
            var fbProduct = parsedParams.fbProduct;

            var dimBODList = ["&CWVUI"
                            ,"[Location].[Location].[" + fbLocation + "]"
                            ,"[Sub Location].[Sub Location].[" + fbSubLocation + "]"
                            ,"[Trans Mode].[Trans Mode].[" + fbTPMode + "]"
                        ];
            
            var dimProd = [...dimBODList];
            dimProd.push("[Item].[Product].[" + fbProduct + "]");

            // 중복체크
            if ( vdCommon.existMeasure(dimProd
                                      ,["Measure.[BOD Prod SET_BOD LT]"
                                      ,"Measure.[BOD Prod SET_BOD Valid]"
                                      ,"Measure.[BOD Prod SET_Created By]"
                                      ,"Measure.[BOD Prod SET_Creation Time]"
                                      ,"Measure.[BOD Prod SET_Eff Enddate]"
                                      ,"Measure.[BOD Prod SET_Eff Startdate]"
                                      ,"Measure.[BOD Prod SET_Lock Flag]"
                                      ,"Measure.[BOD Prod SET_Priority]"
                                      ,"Measure.[BOD Prod SET_Shipment LT]"]
                                      , "")) {
                RuleOutputToUI = { Status : 'Error', Message : "The data has already been registered." };
                return;
            }

            // Param 으로 넘어온 값으로 BOD List Grain의 Data를 가져온다.            
            var rtnBODList = vdCommon.selectList(dimBODList
                                                ,["Measure.[BOD List_BOD Valid]"
                                                  ,"Measure.[BOD List_BOD Frozen]"
                                                  ,"Measure.[BOD List_BOD LT]"
                                                  ,"Measure.[BOD List_Created By]"
                                                  ,"Measure.[BOD List_Eff Enddate]"
                                                  ,"Measure.[BOD List_Eff Startdate]"
                                                  ,"Measure.[BOD List_Priority]"
                                                  ,"Measure.[BOD List_Shipment LT]"
                                                  ,"Measure.[BOD List_Time Phased BOD LT]"
                                                  ,"Measure.[BOD List_Time Phased Shipment LT]"
                                                  ,"Measure.[BOD List_Update Time]"
                                                  ,"Measure.[BOD List_Updated By]"]    // measure
                                                ,""    // where
                                                ,""    // orderby
                                                ,"");   // limit

            vdCommon.printCsData(rtnBODList, 3);

            // BOD List 의 Data 가져오기
            let rtnBOD_LT, rtnPriority, rtnShipment_LT;
            if ( rtnBODList.cs.rowCount == 1 ){
                rtnBOD_LT = rtnBODList.cs.row(0).cell(rtnBODList.cs.measureColumnIndex("BOD List_BOD LT"));
                rtnPriority = rtnBODList.cs.row(0).cell(rtnBODList.cs.measureColumnIndex("BOD List_Priority"));
                rtnShipment_LT = rtnBODList.cs.row(0).cell(rtnBODList.cs.measureColumnIndex("BOD List_Shipment LT"));
                vdCommon.debug("BOD List >>  Qty : "+rtnBOD_LT + " :: " + rtnPriority + " :: " + rtnShipment_LT);
            }

            // BOD Product SET MG 생성
            vdCommon.createMeasure(dimProd
                                  ,['Measure.[BOD Prod SET_BOD Valid]   = "Y";'
                                  ,'Measure.[BOD Prod SET_Created By]	= CurrentUser().[User Name];'
                                  ,'Measure.[BOD Prod SET_Update Time]	= dateadd(Now(),9,"hour");'
                                  ,'Measure.[BOD Prod SET_Updated By]	= CurrentUser().[User Name];'
                                  ,'Measure.[BOD Prod SET_Lock Flag]    = true;'        //  Active Rule > Spread > Assortment (필수)
                                  ,'Measure.[BOD Prod SET_BOD LT]       = '+rtnBOD_LT+';'
                                  ,'Measure.[BOD Prod SET_Priority]     = '+rtnPriority+';'
                                  ,'Measure.[BOD Prod SET_Shipment LT]  = '+rtnShipment_LT+';'
                                  ]);
            // BOD Item 은 Batch 에서 생성, BOD Prod SET 데이터 수정시 Spreading 으로 BOD Item 을 생성 or update 한다.

            vdCommon.programEnd();
        } catch ( e ) {
            RuleOutputToUI = { Status : 'Error', Message : "Js Logic Error : " + e.message };
            return;
        }
    };

    /**
     * BOD Product SET : Assign
     * @param {*} o9Params 
     * @returns 
     */
    var fn_assignProdSET = function(o9Params){
        try {
            const commonLib = require('o9.NSCM.commonLib');
            const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
            const vdUtil = new commonLib.VdUtil();

            vdCommon.setLogLevel("Debug");
            vdCommon.printParams(o9Params);

            // 파라미터 가져오기
            var parsedParams = JSON.parse(o9Params);
            // Assign 팝업
            let fbBODPriority   = parsedParams.fbBODPriority;
            let fbBODLT         = parsedParams.fbBODLT;
            let fbShipmentLT    = parsedParams.fbShipmentLT;
            let fbEffStartDate  = parsedParams.fbEffStartDate;
            let fbEffEndDate    = parsedParams.fbEffEndDate;

            let strEffStartDate  = parsedParams.fbEffStartDate ? parsedParams.fbEffStartDate.substring(0, 10).replace(/-/g, '') : null;
            let strEffEndDate    = parsedParams.fbEffEndDate ? parsedParams.fbEffEndDate.substring(0, 10).replace(/-/g, '') : null;

            vdCommon.debug("strEffStartDate=======>"+strEffStartDate);
            vdCommon.debug("strEffEndDate=======>"+strEffEndDate);

            // Start/End 에 Not Null 일 경우 체크
            if( strEffStartDate != null && strEffStartDate !== "" && strEffEndDate != null && strEffEndDate !== "" ){
                if( parseInt(strEffStartDate) > parseInt(strEffEndDate)){
                    returnString = "Start Date가 End Date 보다 큽니다..";
                    RuleOutputToUI = { Status : 'Error', Message : returnString };
                    return;
                }
            }
    
            // Tuple List 변수 
            let tupleList = parsedParams.fbBODProdSETTuple;
            let fbLocation = "", fbSubLocation = "", fbProduct = "", fbTPMode = "";
            let dimension = [];

            for (let i=0; i < tupleList.length; i++) {
                const row = tupleList[i];
                fbLocation      = row.Location.Value;
                fbSubLocation   = row.SubLocation.Value;
                fbProduct       = row.Product.Value;
                fbTPMode        = row.TPMode.Value;

                dimension = ["&CWVUI"
                            ,"[Location].[Location].[" + fbLocation + "]"
                            ,"[Sub Location].[Sub Location].[" + fbSubLocation + "]"
                            ,"[Trans Mode].[Trans Mode].[" + fbTPMode + "]"
                            ,"[Item].[Product].[" + fbProduct + "]"
                        ];

                vdCommon.updateMeasure(dimension
                                    ,['Measure.[BOD Prod SET_Priority]     = '+fbBODPriority+';'
                                    ,'Measure.[BOD Prod SET_BOD LT]        = '+fbBODLT+';'
                                    ,'Measure.[BOD Prod SET_Shipment LT]   = '+fbShipmentLT+';'
                                    ,'Measure.[BOD Prod SET_Eff Startdate] = "'+fbEffStartDate+'";'
                                    ,'Measure.[BOD Prod SET_Eff Enddate]   = "'+fbEffEndDate+'";'
                                    ,'Measure.[BOD Prod SET_Update Time]   = dateadd(Now(),9,"hour");'
                                    ,'Measure.[BOD Prod SET_Updated By]	   = CurrentUser().[User Name];'
                                    ]);                
            }
            vdCommon.programEnd();
        } catch ( e ) {
            RuleOutputToUI = { Status : 'Error', Message : "Js Logic Error : " + e.message };
            return;
        }
    };

    var fn_validYNProdSET = function(o9Params){
        try {
            const commonLib = require('o9.NSCM.commonLib');
            const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
            const vdUtil = new commonLib.VdUtil();

            vdCommon.setLogLevel("Debug");
            vdCommon.printParams(o9Params);

            // 파라미터 가져오기
            var parsedParams = JSON.parse(o9Params);
            let fbValidYN = parsedParams.fbValidYN;

            // Tuple List 변수 
            let tupleList = parsedParams.fbBODListTuple;
            let fbLocation = "", fbSubLocation = "", fbTPMode = "", fbProduct = "";

            for ( var i = 0; i < tupleList.length; i++ ) {
                const row = tupleList[i];
                fbLocation      = row.fbLocation.Value;
                fbSubLocation   = row.fbSubLocation.Value;
                fbTPMode        = row.fbTPMode.Value;
                fbProduct       = row.fbProduct.Value;

                dimBodProd = ["&CWVUI"
                            ,"[Location].[Location].[" + fbLocation + "]"
                            ,"[Sub Location].[Sub Location].[" + fbSubLocation + "]"
                            ,"[Trans Mode].[Trans Mode].[" + fbTPMode + "]"
                            ,"[Item].[Product].[" + fbProduct + "]"];
                //----------------------------------------------------------------------------------//
                // BOD Prod SET delete : Measure.[BOD Prod SET_BOD Valid] = "N"
                //----------------------------------------------------------------------------------//
                vdCommon.updateMeasure(dimBodProd,
                    ['Measure.[BOD Prod SET_BOD Valid] = "' + fbValidYN + '";',
                    'Measure.[BOD Prod SET_Update Time] = dateadd(Now(),9,"hour");',
                    'Measure.[BOD Prod SET_Updated By] = CurrentUser().Name;']);
                
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

            /* Validation 호출 (PY_UI_BODItemSETValid) */
            var execQuery = 'EXEC plugin instance [PY_UI_BODItemSETValid] ' +
                            'for measures {[BOD Item_Eff Startdate],[BOD Item_BOD LT],[BOD Item_Shipment LT],[BOD Item_Priority],[BOD Item_Update Time],[BOD Item_Updated By]} ' +
                            'using scope ( &CWVUI ) ' +
                            'using arguments {(ExecutionMode, "MediumWeight"), (pDetailLogFlag, "N"), (MaxSliceTableCells, 200000000), (MaxConcurrency, 1), ([Param.o9_sys_log_level], "DEBUG") };  ';

            vdCommon.debug("execQuery: " + JSON.stringify(execQuery));
            vdCommon.executeQuery("fn_validation : PY_UI_BODItemSETValid Run", execQuery);

            vdCommon.programEnd();
        } catch ( e ) {
            RuleOutputToUI = { Status : 'Error', Message : "Js Logic Error : " + e.message };
            return;
        }
    };

    /**
     * fn_apply
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

            /* Validation 호출 (PY_MG_BODItem) */
            var execQuery = 'EXEC plugin instance [PY_MG_BODItem] ' +
                            'for measures {[BOD Item_Cur Status]} ' +
                            'using scope ( &CWVUI ) ' +
                            'using arguments {(ExecutionMode, "MediumWeight"), (paramOutVersion , "CWV_MP"), (MaxSliceTableCells, 200000000), (MaxConcurrency, 1), ([Param.o9_sys_log_level], "DEBUG") };  ';

            vdCommon.debug("execQuery: " + JSON.stringify(execQuery));
            vdCommon.executeQuery("fn_apply : PY_MG_BODItem Run", execQuery);

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
       ,fn_productCombo : fn_productCombo

       /* BOD List(첫번째 그리드) */
       ,fn_addBODList : fn_addBODList
       ,fn_validYNBODList : fn_validYNBODList
       ,fn_apply : fn_apply

       /* BOD Product SET(두번째 그리드) */
       ,fn_addProdSET : fn_addProdSET
       ,fn_assignProdSET : fn_assignProdSET
       ,fn_validYNProdSET : fn_validYNProdSET

       /* BOD Item(세번째 그리드) */
       ,fn_validation : fn_validation       
    };
});

/*-------------------------------------------------------------------------------------------------*/
/* 수정 2025.01.21 TransMode Namedset 수정 NSUITransModeView */
/* 수정 2025.03.06 combo list 수정 */
/* 수정 2025.04.23 : fn_addBODList - Measure.[BOD List_is New Flag] 추가 , 임재민p 요청             */
/*-------------------------------------------------------------------------------------------------*/