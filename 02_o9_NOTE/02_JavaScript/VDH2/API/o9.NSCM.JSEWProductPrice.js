define('o9.NSCM.JSEWProductPrice', ['o9/data/query', 'o9/data/cellset', 'o9.NSCM.commonLibVD'], function(){

    /*--------------------------------------------------------------------------------------------------*/
    // 프로그램명 : o9.NSCM.JSEWProductPrice
    // 화면명 : Product Price (EW)
    // Action Button : EWProductPrice
    // EW 개발자 : 권진수P
    // 최초생성 : 2025.12.01 / syif1380.lee
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

    const programName = "o9.NSCM.JSEWProductPrice";
    const CurrentMonth = "&CurrentMonth";   // 2026.03.10 추가

    //================================= 공통 콤보 사용 ===============================//
    // Action Button : EWCommonVD
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

    /**
     * Sub Location(From Site) 기준의 매핑된 Currency가 표기
     * Action Button : EWProductPrice
     * @param {*} parsedParams 
     * @returns 
     */
    var fb_cb_SubLocation_Currency = function(parsedParams){
        const cLib = fn_cLib(programName + "." + arguments.callee.name);
        cLib.setLogLevel("Debug");

        try {
            cLib.debug("parsedParams :: "+JSON.stringify(parsedParams));
            let fbSubLocation  = parsedParams.fbParams["[Sub Location].[Sub Location]"];    // From Site

            var where = 'where {'
                        +' &CWVUI'
                        +', [Sub Location].[Sub Location]' + cUtil.fn_filterStr(fbSubLocation)
                        +', Measure.[Currency SubLocation Currency_Asn] == true'
                        +' }';
            var result = cLib.selectList(["[Currency].[Currency]"],
                                             [],
                                             where,
                                             "",
                                             "");
            cLib.printCsData(result, 3);

            var comboList = cLib.fn_makeCombo(result, {DimName : "Currency", DimAttbName : "Currency", Sort : "DisplayName", existAll : false, isDisplayNameWithCode : false});
            cLib.debug("ComboData : " + JSON.stringify(comboList));

            cLib.programEnd();

            return { "Code" : 0, "Msg" : "", "Rows" : comboList };
        } catch ( e ) {
            cLib.error(e.message);
            return { "Code" : -1, "Msg" : e.message };
        }
    };

    /**
     * Action Button : EWProductPrice
     * @param {*} parsedParams 
     * @returns 
     */
    var fb_cb_CurrencyM_Rate = function(parsedParams){
        const cLib = fn_cLib(programName + "." + arguments.callee.name);
        cLib.setLogLevel("Debug");

        try {
            cLib.debug("parsedParams :: "+JSON.stringify(parsedParams));

            var fbMonth = parsedParams.fbParams["[Time].[Planning Month]"];
            var fbCurrency = parsedParams.fbParams["[Currency].[Currency]"];
            var fbPlanningMonth = "";

            if ( fbMonth === undefined || fbMonth === null ){
                fbMonth = "";
            }

            // CurrentMonth
            if( String(fbMonth).toLowerCase() === "currentmonth"){
                fbPlanningMonth = CurrentMonth; // &CurrentMonth // 상단 콤보(상단에는 Month가 없어 디폴트(&CurrentMonth) 사용)
            }else{
                fbPlanningMonth = "[Time].[Planning Month]"+cUtil.fn_filterStr(fbMonth);   // 하단 콤보
            }

            var where = 'where {'
                        + cUtil.fn_getFilterQuery(parsedParams, "[Version].[Version Name]")
                        +', '+cUtil.fn_getFilterQuery(parsedParams, "[Category].[Category]")   // AOP Filter
                        +' }';
            var result = cLib.selectList([fbPlanningMonth,"[Currency].[Currency]"+cUtil.fn_filterStr(fbCurrency)],
                                             ["Measure.[Product Price Currency M_Rate]"],
                                             where,
                                             "",
                                             "");
            cLib.printCsData(result, 3);

            var comboList = [];
            for (i = 0; i < result.cs.rowCount; i++) {
                let monthName = result.cs.row(i).cell(result.cs.memberColumnIndex("Time","Planning Month")).Name;
                let monthDisplayName = result.cs.row(i).cell(result.cs.memberColumnIndex("Time","Planning Month")).DisplayName;

                let currencyName = result.cs.row(i).cell(result.cs.memberColumnIndex("Currency","Currency")).Name;
                let currencyDisplayName = result.cs.row(i).cell(result.cs.memberColumnIndex("Currency","Currency")).DisplayName;

                let Rate = result.cs.row(i).cell(result.cs.measureColumnIndex("Product Price Currency M_Rate"));

                comboList.push({ Month: monthName, Currency: currencyName, Rate});
            }
            cLib.debug("ComboData : " + JSON.stringify(comboList));

            cLib.programEnd();

            return { "Code" : 0, "Msg" : "", "Rows" : comboList };
        } catch ( e ) {
            cLib.error(e.message);
            return { "Code" : -1, "Msg" : e.message };
        }
    };

    /**
     * 상단 그리드 저장
     * @param {*} parsedParams 
     * @returns 
     */
    var fn_save = function(parsedParams){
        const cLib = fn_cLib(programName + "." + arguments.callee.name);
        cLib.setLogLevel("Debug");

        try {
            cLib.debug("fn_save ==========================================================>");
            cLib.debug("parsedParams :: "+JSON.stringify(parsedParams));

            for ( var i=0; i<parsedParams.fbGridRows.length; i++){

                //===============================================================================================//
                // 그리드 공통 선언 부분 - Start
                //===============================================================================================//
                var row = parsedParams.fbGridRows[i];
                var rowstatus = row["rowstatus"];

                // Grain 정의
                let dimension = [];
                dimension.push(cUtil.fn_qDimVersionName(parsedParams));
                dimension.push(cUtil.fn_qDim(row, "[Location].[Location]"));
                dimension.push(cUtil.fn_qDim(row, "[Sub Location].[Sub Location]"));
                dimension.push(cUtil.fn_qDim(row, "[Item].[Item]"));

                let measureCheck = ["Measure.[Product Price_Inco Terms]","Measure.[Product Price_View Flag]"
                                   ,"Measure.[Product Price_Create Time]","Measure.[Product Price_Created By]"
                                   ,"Measure.[Product Price_Update Time]","Measure.[Product Price_Updated By]"
                                ];
                
                let measureCreate = [];
                measureCreate.push(cUtil.fn_qMeaUpdateUserName("Measure.[Product Price_Created By]"));
                measureCreate.push(cUtil.fn_qMeaUpdateTime("Measure.[Product Price_Create Time]"));
                measureCreate.push('Measure.[Product Price_View Flag] = "Y"; ');

                let measureUpdate = [];
                measureUpdate.push(cUtil.fn_qMeaUpdateUserName("Measure.[Product Price_Updated By]"));
                measureUpdate.push(cUtil.fn_qMeaUpdateTime("Measure.[Product Price_Update Time]"));
                measureUpdate.push(cUtil.fn_qMeaStr(row, "Measure.[Product Price_Inco Terms]"));
                measureUpdate.push(cUtil.fn_qMeaInt(row, "Measure.[Product Price_RRP]"));
                measureUpdate.push(cUtil.fn_qMeaStr(row, "Measure.[Product Price_RRP Currency]"));
                measureUpdate.push(cUtil.fn_qMeaInt(row, "Measure.[Product Price_DM]"));
                measureUpdate.push(cUtil.fn_qMeaInt(row, "Measure.[Product Price_VAT]"));
                measureUpdate.push(cUtil.fn_qMeaStr(row, "Measure.[Product Price_D Price Currency]"));
                measureUpdate.push(cUtil.fn_qMeaInt(row, "Measure.[Product Price_SD]"));
                measureUpdate.push(cUtil.fn_qMeaStr(row, "Measure.[Product Price_N Price Currency]"));
                measureUpdate.push(cUtil.fn_qMeaInt(row, "Measure.[Product Price_PO Price]"));
                measureUpdate.push(cUtil.fn_qMeaStr(row, "Measure.[Product Price_PO Price Currency]"));
                
                // 2026.03.18 추가 한승진p요청
                measureUpdate.push(cUtil.fn_qMeaInt(row, "Measure.[Product Price_D Price USD]"));
                measureUpdate.push(cUtil.fn_qMeaInt(row, "Measure.[Product Price_N Price USD]"));
                measureUpdate.push(cUtil.fn_qMeaInt(row, "Measure.[Product Price_PO Price USD]"));
                measureUpdate.push(cUtil.fn_qMeaInt(row, "Measure.[Product Price_RRP USD]"));
         
                //===============================================================================================//
                // 그리드 공통 선언 부분 - End
                //===============================================================================================//

                if ( rowstatus == "C" ) {
                    if ( !cLib.existMeasure(dimension,measureCheck, "")){
                        cLib.createMeasure(dimension, measureCreate);
                        cLib.updateMeasure(dimension, measureUpdate);
                    }
                
                } else if ( rowstatus == "U" ) {
                    cLib.updateMeasure(dimension, measureUpdate);

                // } else if ( rowstatus == "D" ) {
                    // delete 없음
                }
            }

            //================================================================================================================================//
            // PY 호출 : View Flag 업데이트 : 일배치 기능으로 저장시에서는 제외 하기로 함 (2026.01.21 한승진P 요청)
            //================================================================================================================================//
            // if( parsedParams.fbGridRows.length > 0){
            //     fn_callPyUIProductPrice();  // View Flag 업데이트
            // }

            cLib.programEnd();

            return { "Code" : 0, "Msg" : "", "Rows" : "" };

        } catch ( e ) {
            cLib.error(e.message);
            return { "Code" : -1, "Msg" : e.message };
        }
    };

    /**
     * 하단 그리드 저장 (하단 모든 탭..)
     * @param {*} parsedParams 
     * @returns 
     */
    var fn_saveMonth = function(parsedParams){
        const cLib = fn_cLib(programName + "." + arguments.callee.name);
        cLib.setLogLevel("Debug");

        try {
            cLib.debug("fn_saveAllItem ==========================================================>");
            cLib.debug("parsedParams :: "+JSON.stringify(parsedParams));

            for ( var i=0; i<parsedParams.fbGridRows.length; i++){

                //===============================================================================================//
                // 그리드 공통 선언 부분 - Start
                //===============================================================================================//
                var row = parsedParams.fbGridRows[i];
                var rowstatus = row["rowstatus"];
                // Grain 정의
                let dimension = [];
                dimension.push(cUtil.fn_qDimVersionName(parsedParams));
                dimension.push(cUtil.fn_qDim(row, "[Location].[Location]"));
                dimension.push(cUtil.fn_qDim(row, "[Sub Location].[Sub Location]"));
                dimension.push(cUtil.fn_qDim(row, "[Item].[Item]"));
                dimension.push(cUtil.fn_qDim(row, "[Time].[Planning Month]"));

                let measureUpdate = [];
                measureUpdate.push(cUtil.fn_qMeaUpdateUserName("Measure.[Product Price M_Updated By]"));
                measureUpdate.push(cUtil.fn_qMeaUpdateTime("Measure.[Product Price M_Update Time]"));
                measureUpdate.push(cUtil.fn_qMeaInt(row, "Measure.[Product Price M_RRP]"));
                measureUpdate.push(cUtil.fn_qMeaStr(row, "Measure.[Product Price M_RRP Currency]"));
                measureUpdate.push(cUtil.fn_qMeaInt(row, "Measure.[Product Price M_DM]"));
                measureUpdate.push(cUtil.fn_qMeaInt(row, "Measure.[Product Price M_VAT]"));
                measureUpdate.push(cUtil.fn_qMeaStr(row, "Measure.[Product Price M_D Price Currency]"));
                measureUpdate.push(cUtil.fn_qMeaInt(row, "Measure.[Product Price M_SD]"));
                measureUpdate.push(cUtil.fn_qMeaStr(row, "Measure.[Product Price M_N Price Currency]"));
                measureUpdate.push(cUtil.fn_qMeaInt(row, "Measure.[Product Price M_PO Price]"));
                measureUpdate.push(cUtil.fn_qMeaStr(row, "Measure.[Product Price M_PO Price Currency]"));
                measureUpdate.push(cUtil.fn_qMeaInt(row, "Measure.[Product Price M_PO Price Week1]"));
                measureUpdate.push(cUtil.fn_qMeaInt(row, "Measure.[Product Price M_PO Price Week2]"));
                measureUpdate.push(cUtil.fn_qMeaInt(row, "Measure.[Product Price M_PO Price Week3]"));
                measureUpdate.push(cUtil.fn_qMeaInt(row, "Measure.[Product Price M_PO Price Week4]"));
                measureUpdate.push(cUtil.fn_qMeaInt(row, "Measure.[Product Price M_PO Price Week5]"));

                // 2026.03.18 추가 한승진p요청
                measureUpdate.push(cUtil.fn_qMeaInt(row, "Measure.[Product Price M_D Price USD]"));
                measureUpdate.push(cUtil.fn_qMeaInt(row, "Measure.[Product Price M_N Price USD]"));
                measureUpdate.push(cUtil.fn_qMeaInt(row, "Measure.[Product Price M_PO Price USD]"));
                measureUpdate.push(cUtil.fn_qMeaInt(row, "Measure.[Product Price M_RRP USD]"));
         
                //===============================================================================================//
                // 그리드 공통 선언 부분 - End
                //===============================================================================================//
                if ( rowstatus == "U" ) {
                    cLib.updateMeasure(dimension, measureUpdate);
                }
            }

            //================================================================================================================================//
            // PY 호출 : View Flag 업데이트 : 일배치 기능으로 저장시에서는 제외 하기로 함 (2026.01.21 한승진P 요청)
            //================================================================================================================================//
            // if( parsedParams.fbGridRows.length > 0){
            //     fn_callPyUIProductPrice();  // View Flag 업데이트
            // }

            cLib.programEnd();

            return { "Code" : 0, "Msg" : "", "Rows" : "" };

        } catch ( e ) {
            cLib.error(e.message);
            return { "Code" : -1, "Msg" : e.message };
        }
    };


    /**
     * PY 호출 : View Flag 업데이트
     * 
     * @param {*} parsedParams 
     * @returns 
     */
    var fn_callPyUIProductPrice = function(){
        const cLib = fn_cLib(programName + "." + arguments.callee.name);
        cLib.setLogLevel("Debug");

        try {
            cLib.debug("fn_callPyUIProductPrice ==========================================================>");
           
            var execQuery = 'EXEC plugin instance [PY_UI_ProductPrice] for measures {[Product Price_NewItemFlag]}'
                            +' using scope ( &MPV )'
                            +' using arguments {(ExecutionMode, "MediumWeight"), ("IncludeNullRows", "False"), (paramOutVersion , "CWV_MP"), (MaxSliceTableCells, 200000000), (MaxConcurrency, 1), ([Param.o9_sys_log_level], "DEBUG")}; ';

                cLib.debug("execQuery: " + JSON.stringify(execQuery));
                cLib.executeQuery("PY_UI_ProductPrice Run", execQuery);

        } catch ( e ) {
            cLib.error(e.message);
            return { "Code" : -1, "Msg" : e.message };
        }
    };


    /**
     * Threshold
     * PY 만 호출 (한승진p) 2025.12.16
     * @param {*} parsedParams 
     * @returns 
     */
    var fn_threshold = function(parsedParams){
        const cLib = fn_cLib(programName + "." + arguments.callee.name);
        cLib.setLogLevel("Debug");

        try {
            cLib.debug("fn_threshold ==========================================================>");
            cLib.debug("parsedParams :: "+JSON.stringify(parsedParams));
           
            //================================================================================================================================//
            // PY 호출 : Product Price M_Threshold 값 세팅 : 입력된 값 초과하는 Price를 표기하기 위한 Price별 Threshold 값 계산 (Product Price (EW) 화면 내 Threshold 기능에 사용할 Base 값)
            //================================================================================================================================//
            var execQuery = 'EXEC plugin instance [PY_UI_ProdPrice_Threshold] for measures {[Product Price M_Threshold RRP],[Product Price M_Threshold D Price], [Product Price M_Threshold N Price], [Product Price M_Threshold PO Price]}'
                        +' using scope ( &MPV )'
                        +' using arguments {(ExecutionMode, "MediumWeight"), ("IncludeNullRows", "False"), (paramOutVersion , "CWV_MP"), (MaxSliceTableCells, 200000000), (MaxConcurrency, 1), ([Param.o9_sys_log_level], "DEBUG")}; ';

            cLib.debug("execQuery: " + JSON.stringify(execQuery));
            cLib.executeQuery("PY_UI_ProdPrice_Threshold Run", execQuery);

            cLib.programEnd();

            return { "Code" : 0, "Msg" : "", "Rows" : "" };

        } catch ( e ) {
            cLib.error(e.message);
            return { "Code" : -1, "Msg" : e.message };
        }
    };

    /**
     * startMonth / endMonth : "YYYYMM"
     * return : ["202601","202602","202603"]
     * @param {*} start 
     * @param {*} end 
     * @returns 
     */
    var fn_makeMonth = function(startMonth, endMonth){
        const cLib = fn_cLib(programName + "." + arguments.callee.name);
        cLib.setLogLevel("Debug");
        try {
            
            // "-" 대시 제거
            startMonth = String(startMonth).replace(/-/g,"");
            endMonth = String(endMonth).replace(/-/g,"");

            const startYear = parseInt(startMonth.slice(0, 4),10);
            const startMM = parseInt(startMonth.slice(4, 6),10);

            const endYear = parseInt(endMonth.slice(0, 4),10);
            const endMM = parseInt(endMonth.slice(4, 6),10);

            let sIdx = startYear * 12 + (startMM - 1);
            let eIdx = endYear * 12 + (endMM - 1);

            const months = [];
            for( let idx = sIdx; idx <= eIdx; idx++) {
                const y = Math.floor(idx / 12);
                const m = (idx %12) + 1;
                months.push(String(y) + String(m).padStart(2, "0"));
            }
            return months;

        } catch ( e ) {
            cLib.error(e.message);
            return { "Code" : -1, "Msg" : e.message };
        }
    }

    /**
     * Define Month : 액션버튼 (Submit)
     * @param {*} parsedParams 
     * @returns 
     */
    var fn_defineMonth = function(parsedParams){
        const cLib = fn_cLib(programName + "." + arguments.callee.name);
        cLib.setLogLevel("Debug");

        try {
            cLib.debug("fn_defineMonth ==========================================================>");
            cLib.debug("fn_defineMonth parsedParams :: "+JSON.stringify(parsedParams));

            let fbStartMonth = parsedParams.fbParams["Measure.[Product Price_Start Month]"];
            let fbEndMonth = parsedParams.fbParams["Measure.[Product Price_End Month]"];

            let planningMonth = fn_makeMonth(fbStartMonth, fbEndMonth);

            cLib.debug("fn_defineMonth planningMonth :: "+JSON.stringify(planningMonth));

            cLib.debug("### parsedParams.fbGridRows.length >> "+parsedParams.fbGridRows.length);

            for ( var i=0; i<parsedParams.fbGridRows.length; i++){

                //===============================================================================================//
                // 그리드 공통 선언 부분 - Start
                //===============================================================================================//
                var row = parsedParams.fbGridRows[i];
                // var rowstatus = row["rowstatus"];
                // Grain 정의
                let dimension = [];
                dimension.push(cUtil.fn_qDimVersionName(parsedParams));
                dimension.push(cUtil.fn_qDim(row, "[Location].[Location]"));
                dimension.push(cUtil.fn_qDim(row, "[Sub Location].[Sub Location]"));
                dimension.push(cUtil.fn_qDim(row, "[Item].[Item]"));

                // 상단 그리드 데이터 저장하지 않음, start month/end month 만 업데이트 함
                // 상단 그리드 변경 데이터가 존재할 경우 EW 에서 메세지 띄움, (변경되지 않은 row=normal 상태만 넘김)
                let measureUpdate = [];
                measureUpdate.push(cUtil.fn_qMeaStr(null, "Measure.[Product Price_Start Month]", fbStartMonth));   // datetime
                measureUpdate.push(cUtil.fn_qMeaStr(null, "Measure.[Product Price_End Month]", fbEndMonth));       // datetime
                measureUpdate.push(cUtil.fn_qMeaUpdateUserName("Measure.[Product Price_Updated By]"));
                measureUpdate.push(cUtil.fn_qMeaUpdateTime("Measure.[Product Price_Update Time]"));
                
                // Product Price 저장
                if( measureUpdate.length > 0){
                    cLib.updateMeasure(dimension, measureUpdate);
                }

                let measureCheck = ["Measure.[Product Price M_View Flag]","Measure.[Product Price M_RRP]"
                                   ,"Measure.[Product Price M_Create Time]","Measure.[Product Price M_Created By]"
                                   ,"Measure.[Product Price M_Update Time]","Measure.[Product Price M_Updated By]"
                                ];
                
                let measureCreate = [];
                measureCreate.push(cUtil.fn_qMeaUpdateUserName("Measure.[Product Price M_Created By]"));
                measureCreate.push(cUtil.fn_qMeaUpdateTime("Measure.[Product Price M_Create Time]"));

                let measureSelect = ["Measure.[Product Price_RRP]", "Measure.[Product Price_RRP Currency]", "Measure.[Product Price_DM]", "Measure.[Product Price_VAT]"
                                    ,"Measure.[Product Price_D Price Currency]", "Measure.[Product Price_SD]", "Measure.[Product Price_N Price Currency]"
                                    ,"Measure.[Product Price_PO Price]", "Measure.[Product Price_PO Price Currency]"
                                    ,"Measure.[Product Price_D Price]","Measure.[Product Price_N Price]", "Measure.[Product Price_View Flag]","Measure.[Product Price_Inco Terms]"];
                
                                    // 
                var result = cLib.selectList(dimension,measureSelect,"","","");
                cLib.printCsData(result, 3);

                for ( var k = 0; k < result.cs.rowCount; k++ ) {

                    // PO_Price = parseInt(result.cs.row(k).cell(result.cs.measureColumnIndex("Product Price_PO Price")));
                    PO_Price = result.cs.row(k).cell(result.cs.measureColumnIndex("Product Price_PO Price"));

                    cLib.debug("###### PO_Price : "+PO_Price);
                    cLib.debug("###### PO_Price 2 : "+result.cs.row(k).cell(result.cs.measureColumnIndex("Product Price_PO Price")));

                    let measureM = [];
                    measureM.push(cUtil.fn_qMeaInt(null, "Measure.[Product Price M_RRP]", result.cs.row(k).cell(result.cs.measureColumnIndex("Product Price_RRP"))));
                    measureM.push(cUtil.fn_qMeaStr(null, "Measure.[Product Price M_RRP Currency]", result.cs.row(k).cell(result.cs.measureColumnIndex("Product Price_RRP Currency"))));
                    measureM.push(cUtil.fn_qMeaInt(null, "Measure.[Product Price M_DM]", result.cs.row(k).cell(result.cs.measureColumnIndex("Product Price_DM"))));
                    measureM.push(cUtil.fn_qMeaInt(null, "Measure.[Product Price M_VAT]", result.cs.row(k).cell(result.cs.measureColumnIndex("Product Price_VAT"))));
                    measureM.push(cUtil.fn_qMeaStr(null, "Measure.[Product Price M_D Price Currency]", result.cs.row(k).cell(result.cs.measureColumnIndex("Product Price_D Price Currency"))));
                    measureM.push(cUtil.fn_qMeaInt(null, "Measure.[Product Price M_SD]", result.cs.row(k).cell(result.cs.measureColumnIndex("Product Price_SD"))));
                    measureM.push(cUtil.fn_qMeaStr(null, "Measure.[Product Price M_N Price Currency]", result.cs.row(k).cell(result.cs.measureColumnIndex("Product Price_N Price Currency"))));
                    measureM.push(cUtil.fn_qMeaInt(null, "Measure.[Product Price M_PO Price]", PO_Price));
                    measureM.push(cUtil.fn_qMeaStr(null, "Measure.[Product Price M_PO Price Currency]", result.cs.row(k).cell(result.cs.measureColumnIndex("Product Price_PO Price Currency"))));
                    measureM.push(cUtil.fn_qMeaInt(null, "Measure.[Product Price M_D Price]", result.cs.row(k).cell(result.cs.measureColumnIndex("Product Price_D Price"))));
                    measureM.push(cUtil.fn_qMeaInt(null, "Measure.[Product Price M_N Price]", result.cs.row(k).cell(result.cs.measureColumnIndex("Product Price_N Price"))));
                    measureM.push(cUtil.fn_qMeaStr(null, "Measure.[Product Price M_View Flag]", result.cs.row(k).cell(result.cs.measureColumnIndex("Product Price_View Flag"))));
                    measureM.push(cUtil.fn_qMeaStr(null, "Measure.[Product Price M_Inco Terms]", result.cs.row(k).cell(result.cs.measureColumnIndex("Product Price_Inco Terms"))));
                    
                    // Measure.[Product Price_PO Price] >> Week1 ~Week5  같이 세팅
                    measureM.push(cUtil.fn_qMeaInt(null, "Measure.[Product Price M_PO Price Week1]", PO_Price));
                    measureM.push(cUtil.fn_qMeaInt(null, "Measure.[Product Price M_PO Price Week2]", PO_Price));
                    measureM.push(cUtil.fn_qMeaInt(null, "Measure.[Product Price M_PO Price Week3]", PO_Price));
                    measureM.push(cUtil.fn_qMeaInt(null, "Measure.[Product Price M_PO Price Week4]", PO_Price));
                    measureM.push(cUtil.fn_qMeaInt(null, "Measure.[Product Price M_PO Price Week5]", PO_Price));

                    // 수정자 정보
                    measureM.push(cUtil.fn_qMeaUpdateUserName("Measure.[Product Price M_Updated By]"));
                    measureM.push(cUtil.fn_qMeaUpdateTime("Measure.[Product Price M_Update Time]"));

                    for( var j=0; j<planningMonth.length; j++){
                        let dimensionM = [...dimension];
                        dimensionM.push(cUtil.fn_qDim(null,"[Time].[Planning Month]", planningMonth[j]));
    
                        // 신규 입력
                        if ( !cLib.existMeasure(dimensionM,measureCheck, "")){
                            cLib.createMeasure(dimensionM, measureCreate);
                            cLib.updateMeasure(dimensionM, measureM);
                        // 수정
                        }else{
                            // Month 데이터 Product Price 데이터로 업데이트
                            // Month 데이터 차후 변경되어 Product Price 와 데이터 싱크가 안맞을 경우는??  검토필요 (한승진P 에게 공유 함)
                            cLib.updateMeasure(dimensionM, measureM);
                        }
                    }
                }
            }

            fn_PyUiProdPriceCurrency(parsedParams);

            cLib.programEnd();

            return { "Code" : 0, "Msg" : "", "Rows" : "" };

        } catch ( e ) {
            cLib.error(e.message);
            return { "Code" : -1, "Msg" : e.message };
        }
    };

    /**
     * 
     * PY 만 호출 (한승진p) 2026.03.18
     * @param {*} parsedParams 
     * @returns 
     */
    var fn_PyUiProdPriceCurrency = function(parsedParams){
        const cLib = fn_cLib(programName + "." + arguments.callee.name);
        cLib.setLogLevel("Debug");

        try {
            cLib.debug("fn_PyUiProdPriceCurrency ==========================================================>");
            cLib.debug("parsedParams :: "+JSON.stringify(parsedParams));


            let fbVersion = parsedParams.fbParams["[Version].[Version Name]"];
            let fbStartMonth = parsedParams.fbParams["Measure.[Product Price_Start Month]"];
            let fbEndMonth = parsedParams.fbParams["Measure.[Product Price_End Month]"];

            // fn_defineMonth planningMonth :: ["202603","202610"]
            let planningMonth = fn_makeMonth(fbStartMonth, fbEndMonth);

            let fbLocation = [...new Set(parsedParams.fbGridRows.map(row => row["[Location].[Location]"]))];
            let fbSubLocation = [...new Set(parsedParams.fbGridRows.map(row => row["[Sub Location].[Sub Location]"]))];
            let fbItem = [...new Set(parsedParams.fbGridRows.map(row => row["[Item].[Item]"]))];
           
            var execQuery = 'EXEC plugin instance [PY_UI_ProdPrice_Currency] for measures {[Product Price M_RRP USD]}'
                        // +' using scope ( &MPV )'
                        +' using scope ( '
                            +' [Version].[Version Name]'+cUtil.fn_filterStr(fbVersion)
                            +' * [Location].[Location]'+cUtil.fn_filterStr(fbLocation)
                            +' * [Sub Location].[Sub Location]'+cUtil.fn_filterStr(fbSubLocation)
                            +' * [Item].[Item]'+cUtil.fn_filterStr(fbItem)
                            +' * [Time].[Planning Month].filter(#.Name >= "'+planningMonth[0]+'").filter(#.Name <= "'+planningMonth[1]+'")'
                            +' ) '
                        +' using arguments {(ExecutionMode, "MediumWeight"), ("IncludeNullRows", "False"), (paramOutVersion , "CWV_MP"), (MaxSliceTableCells, 200000000), (MaxConcurrency, 1), ([Param.o9_sys_log_level], "DEBUG")}; ';

            cLib.debug("execQuery: " + JSON.stringify(execQuery));
            cLib.executeQuery("PY_UI_ProdPrice_Currency Run", execQuery);

            cLib.programEnd();

            return { "Code" : 0, "Msg" : "", "Rows" : "" };

        } catch ( e ) {
            cLib.error(e.message);
            return { "Code" : -1, "Msg" : e.message };
        }
    };

    // Mapping 함수 정의, 마지막에 선언을 해야 함수를 정상적으로 인식함
    const functionMap = {
        "fb_cb_SubLocation_Currency" : fb_cb_SubLocation_Currency
       ,"fb_cb_CurrencyM_Rate"  : fb_cb_CurrencyM_Rate
    //    ,"fn_startMonth"   : fn_startMonth
    //    ,"fn_endMonth"   : fn_endMonth
       ,"fn_save"    : fn_save
       ,"fn_saveMonth" : fn_saveMonth
       ,"fn_threshold" : fn_threshold
       ,"fn_defineMonth" : fn_defineMonth
    };

    return {
        fn_loadFunction : fn_loadFunction
    };

});

/*--------------------------------------------------------------------------------------------------*/
/* 
    프로그램명 : o9.NSCM.JSEWProductPrice
    화면명 : Product Price (EW)
    Action Button : EWProductPrice
    [history]
    2025.12.15 :  fn_threshold 추가, PY호출
    2025.12.30 :  fn_saveMonth 추가, PY호출 (하단 그리드 저장 (탭 통합))
    2026.01.06 :  fn_callPyUIProductPrice 추가, PY호출
    2026.01.07 :  fn_defineMonth 추가 (Define Month > Submit 기능)
    2026.01.09 :  fn_defineMonth : Product Price View Flag => Product Price M_View Flag 복사 메저 추가 (한승진p요청)
    2026.01.09 :  fn_defineMonth : Product Price_Inco Terms=> Product Price M_Inco Terms 복사 메저 추가 (한승진p요청)
    2026.01.21 :  fn_save , fn_defineMonth : 일배치 기능으로 저장시에서는 제외 하기로 함 (2026.01.21 한승진P 요청)
    2026.03.10 :  fb_cb_CurrencyM_Rate combo 추가 (한승진P 요청)
    2026.03.18 :  fn_save, fn_saveMonth : USD 저장 메저 추가 (한승진P 요청)
                  - fn_PyUiProdPriceCurrency : py호출 추가
    2026.03.26 : commonLib 선언 부분 변경 및 공통함수 이름 변경
*/
/*--------------------------------------------------------------------------------------------------*/