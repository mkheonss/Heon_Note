define('o9.NSCM.JSLoadingMasterMgt', ['o9/data/query', 'o9/data/cellset', 'o9.NSCM.commonLib'], function(){

    const programName = "o9.NSCM.JSLoadingMasterMgt";

    var fn_subLocationCombo = function(o9Params){
        try {
            const commonLib = require('o9.NSCM.commonLib');
            const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
            vdCommon.setLogLevel("Debug");
            vdCommon.printParams(o9Params);
            // 파라메타 가져오기
            let parsedParams = JSON.parse(o9Params);
            let fbLocation = parsedParams.fbLocation;
            let fbItem = parsedParams.fbItem;   // 2025.01.09 add (노보람프로 요청)

            // selectList(dimension, measure, where, orderby, limit)
            var where = "where {"
                               +"&CWVUI"
                               +",[Location].[Location].["+fbLocation+"]"
                               +",[Item].[Item].["+fbItem+"]"
                               +',coalesce(Measure.[BOD Item_Eff Startdate],DATEADD(Now(),-1,"Day")) < now() && coalesce(Measure.[BOD Item_Eff Enddate],DATEADD(Now(),1,"Day")) > now()'
                               +"}";

            var result = vdCommon.selectList(["[Sub Location].[Sub Location]"],
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
            
            let parsedParams = JSON.parse(o9Params); 

            var result = vdCommon.selectList(["&NSUITransModeView"],    // [Trans Mode].[Trans Mode].filter(#.Name in {"AIR","VESSEL","TRUCK"})
                                             [], // measure
                                             "", // where
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

    /**
     * Loading Master (상단 그리드)
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
            // Row 선택 변수
            // let fbVersion = parsedParams.fbVersion;
            let fbLocation = parsedParams.fbLocation;
            let fbItem = parsedParams.fbItem;
            let fbSubLocation = parsedParams.fbSubLocation;
            let fbTPMode = parsedParams.fbTPMode;

            // Loading Master
            var dimension = ["&CWVUI"
                            ,"[Location].[Location].[" + fbLocation + "]"
                            ,"[Item].[Item].[" + fbItem + "]"
                            ];

            // Measure Group 정의 ( 변경 2025.01.16 )
            let measures = [ 'Measure.[Loading Master_BOX W]'
                            ,'Measure.[Loading Master_BOX D]'
                            ,'Measure.[Loading Master_BOX H]'
                            ,'Measure.[Loading Master_CBM]'
                            ,'Measure.[Loading Master_Net Weight]'
                            ,'Measure.[Loading Master_Gross Weight]'
                            // ,'Measure.[Loading Master_20FT Qty]'
                            // ,'Measure.[Loading Master_40FT Qty]'
                            ,'Measure.[Loading Master_20FT Qty Override]'
                            ,'Measure.[Loading Master_40FT Qty Override]'
                            ,'Measure.[Loading Master_40HC Qty]'
                            ,'Measure.[Loading Master_45FT Qty]'
                            ,'Measure.[Loading Master_53FT Qty]'
                            ,'Measure.[Loading Master_FCL]'
                            ,'Measure.[Loading Master_FCL N]'                 // add 2025.05.20
                            ,'Measure.[Loading Master_FCL Item Flag]'         // add 2025.05.20
                            ,'Measure.[Loading Master_1st Container]'
                            ,'Measure.[Loading Master_2nd Container]'
                            ,'Measure.[Loading Master_20FT Minimum Lot]'
                            ,'Measure.[Loading Master_20FT Multiple Lot]'
                            ,'Measure.[Loading Master_40HC Minimum Lot]'
                            ,'Measure.[Loading Master_40HC Multiple Lot]'
                            ,'Measure.[TLB MAX Loading Rate]'
                            ,'Measure.[TLB MIN Loading Rate]'
                            ,'Measure.[Loading Master_Init By]'
                            ,'Measure.[Loading Master_Init Dttm]'
                            ,'Measure.[Loading Master_Up By]'
                            ,'Measure.[Loading Master_Up Dttm]'
                            ,'Measure.[Item Site Asn_Cur Status]'                // add 2025.01.09
                            ,'Measure.[Loading Master_Build Ahead Period]'       // add 2025.02.13
                            ];

            var result = vdCommon.selectList(dimension,
                                            measures,
                                            "",
                                            "",
                                            "");
            vdCommon.printCsData(result, 3);
            if ( result.cs.rowCount == 0 ){
                RuleOutputToUI = { Status : 'Error', Message : "There is no registered data." };
                return;
            }
            
            //--------------------------------------------------------------------------------------------------------------------------------//
            // Loading Master
            //--------------------------------------------------------------------------------------------------------------------------------//
            let MinimumLot_20FT  = result.cs.row(0).cell(result.cs.measureColumnIndex('Loading Master_20FT Minimum Lot'));  // 추가 2025.01.16
            let MultipleLot_20FT = result.cs.row(0).cell(result.cs.measureColumnIndex('Loading Master_20FT Multiple Lot')); // 추가 2025.01.16
            let MinimumLot_40HC  = result.cs.row(0).cell(result.cs.measureColumnIndex('Loading Master_40HC Minimum Lot'));  // 추가 2025.01.16
            let MultipleLot_40HC = result.cs.row(0).cell(result.cs.measureColumnIndex('Loading Master_40HC Multiple Lot')); // 추가 2025.01.16
            let TLBMaxLoadingRate = result.cs.row(0).cell(result.cs.measureColumnIndex('TLB MAX Loading Rate'));            // 추가 2025.01.16
            let TLBMinLoadingRate = result.cs.row(0).cell(result.cs.measureColumnIndex('TLB MIN Loading Rate'));            // 추가 2025.01.16
            let FCL               = result.cs.row(0).cell(result.cs.measureColumnIndex('Loading Master_FCL'));
            let FCL_N             = result.cs.row(0).cell(result.cs.measureColumnIndex('Loading Master_FCL N'));            // add 2025.05.20 (노보람p 요청) : Loading Master_FCL (Boolean) => Loading Master_FCL N (Picklist) Y/N
            let FCLItemFlag       = result.cs.row(0).cell(result.cs.measureColumnIndex('Loading Master_FCL Item Flag'));
            let FCL_Lock          = (vdUtil.fn_getString(FCLItemFlag) == "Y") ? false : true;            

            // vdCommon.debug("FCL :: "+FCL +" ==> FCL_Lock :: "+FCL_Lock + "==> FCLItemFlag :: "+ FCLItemFlag);

            let Container1st     = result.cs.row(0).cell(result.cs.measureColumnIndex('Loading Master_1st Container'));
            let Container2nd     = result.cs.row(0).cell(result.cs.measureColumnIndex('Loading Master_2nd Container'));
            let BuildAheadPeriod = result.cs.row(0).cell(result.cs.measureColumnIndex('Loading Master_Build Ahead Period'));  // 추가 2025.02.13

            //--------------------------------------------------------------------------------------------------------------------------------//
            // Loading Master To Site
            //--------------------------------------------------------------------------------------------------------------------------------//
            var measureSub = [];
            
            if (vdUtil.fn_isInt(MinimumLot_20FT)){
                measureSub.push('Measure.[Loading Master To Site_20FT Minimum Lot]      = ' + MinimumLot_20FT + ';');
            }
            if (vdUtil.fn_isInt(MultipleLot_20FT)){
                measureSub.push('Measure.[Loading Master To Site_20FT Multiple Lot]     = ' + MultipleLot_20FT + ';');
            }
            if (vdUtil.fn_isInt(MinimumLot_40HC)){
                measureSub.push('Measure.[Loading Master To Site_40HC Minimum Lot]      = ' + MinimumLot_40HC + ';');
            }
            if (vdUtil.fn_isInt(MultipleLot_40HC)){
                measureSub.push('Measure.[Loading Master To Site_40HC Multiple Lot]     = ' + MultipleLot_40HC + ';');
            }
            if (vdUtil.fn_isInt(TLBMaxLoadingRate)){
                measureSub.push('Measure.[Loading Master To Site_TLB MAX Loading Rate]  = ' + TLBMaxLoadingRate + ';');
            }
            if (vdUtil.fn_isInt(TLBMinLoadingRate)){
                measureSub.push('Measure.[Loading Master To Site_TLB MIN Loading Rate]  = ' + TLBMinLoadingRate + ';');
            }
            if (vdUtil.fn_isInt(BuildAheadPeriod)){
                measureSub.push('Measure.[Loading Master To Site_Build Ahead Period]    = ' + BuildAheadPeriod + ';');
            }

            measureSub.push('Measure.[Loading Master To Site_FCL]               = ' + FCL + ';');
            measureSub.push('Measure.[Loading Master To Site_FCL N]               = "' + vdUtil.fn_getString(FCL_N) + '";');    // add 2025.05.16 datatype 변경 ( Boolean -> picklist(String: Y/N)) , 노보람p요청
            measureSub.push('Measure.[Loading Master To Site_FCL N.Lock]          = ' + FCL_Lock + ';');
            // measureSub.push('Measure.[Loading Master To Site_FCL Item Flag]     = "'+ FCLItemFlag + '";');  // null 일 경우 "null"로 입력됨
            measureSub.push('Measure.[Loading Master To Site_FCL Item Flag]     = "' + vdUtil.fn_getString(FCLItemFlag) + '";');    // null 일 경우 정상
            measureSub.push('Measure.[Loading Master To Site_1st Container]		= "' + vdUtil.fn_getString(Container1st) + '";');
            measureSub.push('Measure.[Loading Master To Site_2nd Container]     = "' + vdUtil.fn_getString(Container2nd) + '";');

            //Loading Master To Site_TLB MAX Loading Rate
            //Loading Master To Site_TLB MIN Loading Rate
            measureSub.push('Measure.[Loading Master To Site_Up By]             = CurrentUser().[User Name];');
            measureSub.push('Measure.[Loading Master To Site_Up Dttm]           = dateadd(Now(),9,"hour");');

            var dimensionSub = [...dimension];    // dimension 을 복사후 추가 (Main MG의 Grain 에서 추가되는 경우 활용)
            dimensionSub.push("[Sub Location].[Sub Location].[" + fbSubLocation + "]");
            dimensionSub.push("[Trans Mode].[Trans Mode].[" + fbTPMode + "]");              // Grain 추가, 노보람p 요청 2025.04.17

            // 중복일 경우 Update
            if ( vdCommon.existMeasure(dimensionSub
                                      ,['Measure.[Loading Master To Site_1st Container]'
                                      ,'Measure.[Loading Master To Site_FCL]'
                                      ,'Measure.[Loading Master To Site_FCL Item Flag]'
                                      ,'Measure.[Loading Master To Site_Init By]'
                                      ,'Measure.[Loading Master To Site_Init Dttm]'
                                      ,'Measure.[Loading Master To Site_20FT Minimum Lot]'
                                      ,'Measure.[Loading Master To Site_20FT Multiple Lot]'
                                      ,'Measure.[Loading Master To Site_40HC Minimum Lot]'
                                      ,'Measure.[Loading Master To Site_40HC Multiple Lot]'
                                      ,'Measure.[Loading Master To Site_TLB MAX Loading Rate]'
                                      ,'Measure.[Loading Master To Site_TLB MIN Loading Rate]'
                                      ,'Measure.[Loading Master To Site_Up By]'
                                      ,'Measure.[Loading Master To Site_Up Dttm]'
                                      ,'Measure.[Loading Master To Site_Valid]'
                                      ,'Measure.[Loading Master To Site_Build Ahead Period]']
                                      ,"") ) {
                vdCommon.updateMeasure(dimensionSub, measureSub);
            } else {    // 중복이 아닐 경우 MG Create
                measureSub.push('Measure.[Loading Master To Site_Init By]             = CurrentUser().[User Name];');
                measureSub.push('Measure.[Loading Master To Site_Init Dttm]           = dateadd(Now(),9,"hour");');
                measureSub.push('Measure.[Loading Master To Site_Valid]               = "Y";');

                // vdCommon.createMeasure(dimensionSub, measureSub);
                // 성능향상을 위해 createMeasure 는 Measure 1개만 등록 후 updateMeasure 실행
                vdCommon.createMeasure(dimensionSub, ['Measure.[Loading Master To Site_Up Dttm]    = dateadd(Now(),9,"hour");']);
                vdCommon.updateMeasure(dimensionSub, measureSub);
            }
            vdCommon.programEnd();
        } catch ( e ) {
            RuleOutputToUI = { Status : 'Error', Message : "Js Logic Error : " + e.message };
            return;
        }
    };

    /**
     * Loading Master To Site (하단 그리드)
     * @param {*} o9Params 
     * @returns 
     */
    var fn_validYN = function(o9Params){
        try {
            const commonLib = require('o9.NSCM.commonLib');
            const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
            const vdUtil = new commonLib.VdUtil();
            
            vdCommon.setLogLevel("Debug");

            vdCommon.printParams(o9Params);

            // 파라미터 가져오기
            let parsedParams = JSON.parse(o9Params);
            let fbValidYN = parsedParams.fbValidYN;

            // Tuple List 변수 
            let tupleList = parsedParams.fbTupleList;
            let dimension = [];

            for (let i=0; i < tupleList.length; i++) {
                const row = tupleList[i];
                fbLocation      = row.fbLocation.Value;
                fbSubLocation   = row.fbSubLocation.Value;
                fbItem          = row.fbItem.Value;
                fbTPMode        = row.fbTPMode.Value;           // Grain 추가, 노보람p 요청 2025.04.17

                dimension = ["&CWVUI"
                            ,"[Location].[Location].[" + fbLocation + "]"
                            ,"[Sub Location].[Sub Location].[" + fbSubLocation + "]"
                            ,"[Item].[Item].[" + fbItem + "]"
                            ,"[Trans Mode].[Trans Mode].[" + fbTPMode + "]"];

                //----------------------------------------------------------------------------------//
                // BOD Prod SET delete : Measure.[Loading Master To Site_Valid] = "N"
                //----------------------------------------------------------------------------------//
                vdCommon.updateMeasure(dimension,
                    ['Measure.[Loading Master To Site_Valid] = "' + fbValidYN + '";',
                     'Measure.[Loading Master To Site_Up Dttm] = dateadd(Now(),9,"hour");',
                     'Measure.[Loading Master To Site_Up By] = CurrentUser().Name;']);
            }
            
            vdCommon.programEnd();
        } catch ( e ) {
            RuleOutputToUI = { Status : 'Error', Message : "Js Logic Error : " + e.message };
            return;
        }
    };

    return{
        fn_subLocationCombo : fn_subLocationCombo
       ,fn_transModeCombo   : fn_transModeCombo         // Trans Mode 추가 (노보람p 요청 2025.04.17)
       ,fn_apply : fn_apply
       ,fn_validYN : fn_validYN       
    };
});
/* 프로그램명 : o9.NSCM.JSLoadingMasterMgt */
/* 수정 2025.02.13 수정 fn_apply - measure 추가(Loading Master_Build Ahead Period)  */
/* 수정 2025.04.17 수정 fn_transModeCombo 추가, Loading Master To Site 에 Trans Mode Grain 추가  */
/* 수정 2025.05.20 Measure.[Loading Master_FCL N] 추가, Measure.[Loading Master To Site_FCL N] 추가 */