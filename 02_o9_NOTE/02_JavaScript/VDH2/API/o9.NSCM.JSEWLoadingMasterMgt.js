define('o9.NSCM.JSEWLoadingMasterMgt', ['o9/data/query', 'o9/data/cellset', 'o9.NSCM.commonLibVD'], function(){

    /*--------------------------------------------------------------------------------------------------*/
    // 프로그램명 : o9.NSCM.JSEWLoadingMasterMgt
    // 화면명 : Loading Master (EW)
    // Action Button : EWLoadingMasterMgt
    // EW 개발자 : 권슬기p
    // 최초생성 : 2025.08.19 / syif1380.lee
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

    const programName = "o9.NSCM.JSEWLoadingMasterMgt";
    const queryModule = require('o9/data/query');

    //================================================== -[Combo Data] ==========================================//
    /*------------------------------------------------------------------------------------------------------------
    Product Group   > EWCommonVD            >  { "fbFuncName" : "fn_cb_setProductGroup", "fbParams" : {} }
    Project         > EWCommonVD            >  { "fbFuncName" : "fn_cb_setProject", "fbParams" : { "includeField" : "Item:Product Group:TV" } }
    Inch            > EWCommonVD            >  { "fbFuncName" : "fn_cb_setInch", "fbParams" : { "includeField" :  "Item:Product Group:TV,Item:Project:Q60CJ" } }
    Trans Mode      > EWCommonVD            >  { "fbFuncName" : "fn_cb_tpmodeGO", "fbParams" : {} }
    Item            > EWLoadingMasterMgt    >  { "fbFuncName" : "fn_cb_itemValidBod", "fbParams" : { "[Item].[Product Group]" : "TV", "[Item].[Project]":"S95DA", "[Item].[Inch]":"55" } }
    JDM             > EWLoadingMasterMgt    >  { "fbFuncName" : "fn_cb_jdm", "fbParams" : {"[Item].[Item]":"GQ55S95DATXZG"} }
    Location        > EWLoadingMasterMgt    >  { "fbFuncName" : "fn_cb_location", "fbParams" : {"[Item].[Item]":"GQ55S95DATXZG"} }
    Sub Location    > EWLoadingMasterMgt    >  { "fbFuncName" : "fn_cb_subLocation", "fbParams" : {"[Location].[Location]":"P306","[Item].[Item]":"GQ55S95DATXZG"} }
    -------------------------------------------------------------------------------------------------------------*/
    
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

    var fn_cb_itemValidBod = function(parsedParams){
        const cLib = fn_cLib(programName + "." + arguments.callee.name);
        cLib.setLogLevel("Debug");

        try {
            cLib.debug("parsedParams :: "+JSON.stringify(parsedParams));
            cLib.debug("parsedParams.fbParams :: "+JSON.stringify(parsedParams.fbParams));

            let fbProductGroup = parsedParams.fbParams["[Item].[Product Group]"];
            let fbProject = parsedParams.fbParams["[Item].[Project]"];
            let fbInch = parsedParams.fbParams["[Item].[Inch]"];

            var where = 'where {'
                               +'&CWVUI'
                               +',[Item].[Product Group]'+ cUtil.fn_filterStr(fbProductGroup)
                               +',[Item].[Project]'+ cUtil.fn_filterStr(fbProject)
                               +',[Item].[Inch]'+ cUtil.fn_filterStr(fbInch)
                               +',(Measure.[BOD Item_Cur Status] == "PLANNED" || Measure.[BOD Item_Cur Status] == "ACTIVE" )'
                               +'}';

            var result = cLib.selectList(["&SETItem"], [], where, "", "");
            cLib.printCsData(result, 3);

            var comboList = cLib.fn_makeCombo(result, {DimName : "Item", DimAttbName : "Item", Sort : "DisplayName", existAll : false, isDisplayNameWithCode : true});
            cLib.debug("ComboData : " + JSON.stringify(comboList));

            cLib.programEnd();

            return { "Code" : 0, "Msg" : "", "Rows" : comboList };
        } catch ( e ) {
            cLib.error(e.message);
            return { "Code" : -1, "Msg" : e.message };
        }
    };

    // JDM
    var fn_cb_jdm = function(parsedParams){
        const cLib = fn_cLib(programName + "." + arguments.callee.name);
        cLib.setLogLevel("Debug");

        try {
            cLib.debug("parsedParams :: "+JSON.stringify(parsedParams));
            cLib.debug("parsedParams.fbParams :: "+JSON.stringify(parsedParams.fbParams));

            let fbItem = parsedParams.fbParams["[Item].[Item]"];

            var where = 'where { [Item].[Item Stage].filter(#.Name == "SET")  '
                            +',[Item].[Item]'+ cUtil.fn_filterStr(fbItem)
                            +' }';

            var result = cLib.selectList(["[Item].[JDM].relatedmembers([JDM])"],
                                             [],
                                             where,
                                             "",
                                             "");
            cLib.printCsData(result, 3);

            var comboList = cLib.fn_makeCombo(result, {DimName : "Item", DimAttbName : "JDM", Sort : "DisplayName", existAll : false, isDisplayNameWithCode : true, existHyphen : true});
            cLib.debug("ComboData : " + JSON.stringify(comboList));

            cLib.programEnd();

            return { "Code" : 0, "Msg" : "", "Rows" : comboList };
        } catch ( e ) {
            cLib.error(e.message);
            return { "Code" : -1, "Msg" : e.message };
        }
    };

    var fn_cb_location = function(parsedParams){
        const cLib = fn_cLib(programName + "." + arguments.callee.name);
        cLib.setLogLevel("Debug");

        try {
            cLib.debug("parsedParams :: "+JSON.stringify(parsedParams));
            cLib.debug("parsedParams.fbParams :: "+JSON.stringify(parsedParams.fbParams));

            let fbItem = parsedParams.fbParams["[Item].[Item]"];

            var where = 'where {'
                               +'&CWVUI'
                               +',[Item].[Item]'+ cUtil.fn_filterStr(fbItem)
                               +',(Measure.[BOD Item_Cur Status] == "PLANNED" || Measure.[BOD Item_Cur Status] == "ACTIVE" )'
                               +'}';
            //Item Site Asn_Cur Status==Planned, Active
            var result = cLib.selectList(["&MFStageSETLocation"],
                                             [],
                                             where,
                                             "",
                                             "");
            cLib.printCsData(result, 3);

            var comboList = cLib.fn_makeCombo(result, {DimName : "Location", DimAttbName : "Location", Sort : "DisplayName", existAll : false, isDisplayNameWithCode : true});
            cLib.debug("ComboData : " + JSON.stringify(comboList));

            cLib.programEnd();

            return { "Code" : 0, "Msg" : "", "Rows" : comboList };
        } catch ( e ) {
            cLib.error(e.message);
            return { "Code" : -1, "Msg" : e.message };
        }
    };

    // 
    var fn_cb_subLocation = function(parsedParams){
        const cLib = fn_cLib(programName + "." + arguments.callee.name);
        cLib.setLogLevel("Debug");

        try {
            cLib.debug("parsedParams :: "+JSON.stringify(parsedParams));
            cLib.debug("parsedParams.fbParams :: "+JSON.stringify(parsedParams.fbParams));

            let fbItem = parsedParams.fbParams["[Item].[Item]"];
            let fbLocation = parsedParams.fbParams["[Location].[Location]"];

            var where = 'where {'
                               +'&CWVUI'
                               +',[Location].[Location]'+ cUtil.fn_filterStr(fbLocation)
                               +',[Item].[Item]'+ cUtil.fn_filterStr(fbItem)
                               +',(Measure.[BOD Item_Cur Status] == "PLANNED" || Measure.[BOD Item_Cur Status] == "ACTIVE" )'
                               +'}';

            var result = cLib.selectList(["&NSUISubLocationDC"],
                                             [],
                                             where,
                                             "",
                                             "");
            cLib.printCsData(result, 3);

            var comboList = cLib.fn_makeCombo(result, {DimName : "Sub Location", DimAttbName : "Sub Location", Sort : "DisplayName", existAll : true, isDisplayNameWithCode : true});
            cLib.debug("ComboData : " + JSON.stringify(comboList));

            cLib.programEnd();

            return { "Code" : 0, "Msg" : "", "Rows" : comboList };
        } catch ( e ) {
            cLib.error(e.message);
            return { "Code" : -1, "Msg" : e.message };
        }
    };

    // fn_savePostProcess : 중복 Validation 체크
    var fn_savePostProcess = function(parsedParams){
        const cLib = fn_cLib(programName + "." + arguments.callee.name);
        cLib.setLogLevel("Debug");

        try {
            cLib.debug("fn_save validation ==========================================================>");
            cLib.debug("parsedParams.fbGridRows :: "+JSON.stringify(parsedParams));

            let measureCheck = ["Measure.[Loading Master To Site_Valid]", "Measure.[Loading Master To Site_1st Container]", "Measure.[Loading Master To Site_2nd Container]"
                             , "Measure.[Loading Master To Site_Up Dttm]", "Measure.[Loading Master To Site_Init Dttm]"];

            errorRowData = [];
            errorRowGrid = [];
            errorMsg = "This is registered data.";

            for ( var i=0; i<parsedParams.fbGridRows.length; i++){
                rowstatus = parsedParams.fbGridRows[i]["rowstatus"];
                rowindex = parsedParams.fbGridRows[i]["rowindex"];
                parsedParams.fbGridRows[i]["rowmsg"] = null;

                cLib.debug("rowstatus :: "+rowstatus);

                // 기존 data 중복여부에 대한 체크
                if( rowstatus == "C") {
                    // let fbVersion = parsedParams.fbGridRows[i]["[Version].[Version Name]"];
                    let fbLocation = parsedParams.fbGridRows[i]["[Location].[Location]"];
                    let fbSubLocation = parsedParams.fbGridRows[i]["[Sub Location].[Sub Location]"];
                    let fbTPMode = parsedParams.fbGridRows[i]["[Trans Mode].[Trans Mode]"];
                    let fbItem = parsedParams.fbGridRows[i]["[Item].[Item]"];

                    let dimension = ["&CWVUI"
                                ,"[Location].[Location].[" + fbLocation + "]"
                                ,"[Sub Location].[Sub Location].[" + fbSubLocation + "]"
                                ,"[Trans Mode].[Trans Mode].[" + fbTPMode + "]"
                                ,"[Item].[Item].[" + fbItem + "]"
                                ];

                    // 중복 체크 
                    if ( cLib.existMeasure(dimension, measureCheck, "")){
                        errorRowData.push(rowindex+"^"+errorMsg);
                        errorRowGrid.push(parsedParams.fbGridRows[i]);
                        // return { "Code" : 1, "Msg" : ["1^TThis is registered data."]};
                    }
                }

            } // end for

            cLib.programEnd();

            // 중복된 row 가 존재할 경우
            if( errorRowData.length > 0 ){
                return { "Code" : 1, "Msg" : errorRowData, "Rows" : errorRowGrid };   // 오류 리턴
            }

            fn_save(parsedParams);

            return { "Code" : 0, "Msg" : "", "Rows" : "" }; // 정상 리턴

        } catch ( e ) {
            cLib.error(e.message);
            return { "Code" : -1, "Msg" : e.message };
        }
    };

    /**
     * fn_save
     * 
     * @param {*} o9Params 
     * @returns 
     */
    var fn_save = function(parsedParams){
        const cLib = fn_cLib(programName + "." + arguments.callee.name);
        cLib.setLogLevel("Debug");

        try {
            cLib.debug("fn_save call ==========================================================>");
            cLib.debug("parsedParams :: "+JSON.stringify(parsedParams));

            let measureCheck = ["Measure.[Loading Master To Site_Valid]", "Measure.[Loading Master To Site_1st Container]", "Measure.[Loading Master To Site_2nd Container]"
                             , "Measure.[Loading Master To Site_Up Dttm]", "Measure.[Loading Master To Site_Init Dttm]"];

            for ( var i=0; i<parsedParams.fbGridRows.length; i++){

                let row = parsedParams.fbGridRows[i];

                rowstatus = row["rowstatus"];
                row["rowmsg"] = null;
                cLib.debug("rowstatus :: "+rowstatus);

                // 수정 Measure
                let measureUpdate = [];
                measureUpdate.push(cUtil.fn_qMeaInt(row, "Measure.[Loading Master To Site_20FT Qty Override]"));
                measureUpdate.push(cUtil.fn_qMeaInt(row, "Measure.[Loading Master To Site_40FT Qty Override]"));
                measureUpdate.push(cUtil.fn_qMeaInt(row, "Measure.[Loading Master To Site_40HC Qty Override]"));
                measureUpdate.push(cUtil.fn_qMeaInt(row, "Measure.[Loading Master To Site_45FT Qty Override]"));
                measureUpdate.push(cUtil.fn_qMeaInt(row, "Measure.[Loading Master To Site_53FT Qty Override]"));
                measureUpdate.push(cUtil.fn_qMeaStr(row, "Measure.[Loading Master To Site_FCL]"));             // string
                measureUpdate.push(cUtil.fn_qMeaStr(row, "Measure.[Loading Master To Site_1st Container]"));   // string
                measureUpdate.push(cUtil.fn_qMeaStr(row, "Measure.[Loading Master To Site_2nd Container]"));   // string
                measureUpdate.push(cUtil.fn_qMeaInt(row, "Measure.[Loading Master To Site_40HC Multiple Lot]"));   // integer
                measureUpdate.push(cUtil.fn_qMeaInt(row, "Measure.[Loading Master To Site_40HC Minimum Lot]"));    // integer
                measureUpdate.push(cUtil.fn_qMeaInt(row, "Measure.[Loading Master To Site_20FT Multiple Lot]"));   // number
                measureUpdate.push(cUtil.fn_qMeaInt(row, "Measure.[Loading Master To Site_20FT Minimum Lot]"));    // integer
                // measureUpdate.push(cUtil.fn_qMeaInt(row, "Measure.[Loading Master To Site_TLB MIN Loading Rate]"));    // number
                // measureUpdate.push(cUtil.fn_qMeaInt(row, "Measure.[Loading Master To Site_TLB MAX Loading Rate]"));    // number
                measureUpdate.push(cUtil.fn_qMeaInt(row, "Measure.[Loading Master To Site_TLB MIN Loading Rate Override]"));    // number // 2026.02.06 변경
                measureUpdate.push(cUtil.fn_qMeaInt(row, "Measure.[Loading Master To Site_TLB MAX Loading Rate Override]"));    // number // 2026.02.06 변경
                measureUpdate.push(cUtil.fn_qMeaInt(row, "Measure.[Loading Master To Site_Build Ahead Period]"));  // integer
                measureUpdate.push(cUtil.fn_qMeaUpdateUserName("Measure.[Loading Master To Site_Up By]"));
                measureUpdate.push(cUtil.fn_qMeaUpdateTime("Measure.[Loading Master To Site_Up Dttm]"));

                // 생성 Measure (수정 Measure + 추가 Measure)
                let measureInsert = [];
                measureInsert.push(cUtil.fn_qMeaStr(row, "Measure.[Loading Master To Site_Item Site Cur Status_PL]"));     // 2026.01.07 추가 (이상엽p 요청)
                measureInsert.push(cUtil.fn_qMeaStr(row, "Measure.[Loading Master To Site_1st Container]"));
                measureInsert.push(cUtil.fn_qMeaStr(row, "Measure.[Loading Master To Site_2nd Container]"));
                measureInsert.push(cUtil.fn_qMeaInt(row, "Measure.[Loading Master To Site_40HC Multiple Lot]"));
                measureInsert.push(cUtil.fn_qMeaInt(row, "Measure.[Loading Master To Site_40HC Minimum Lot]"));
                measureInsert.push(cUtil.fn_qMeaInt(row, "Measure.[Loading Master To Site_20FT Multiple Lot]"));
                measureInsert.push(cUtil.fn_qMeaInt(row, "Measure.[Loading Master To Site_20FT Minimum Lot]"));

                // I/F Measure
                // measureInsert.push(cUtil.fn_qMeaInt(row, "Measure.[Loading Master To Site_20FT Qty]"));
                // measureInsert.push(cUtil.fn_qMeaInt(row, "Measure.[Loading Master To Site_40FT Qty]"));
                // measureInsert.push(cUtil.fn_qMeaInt(row, "Measure.[Loading Master To Site_40HC Qty]"));
                // measureInsert.push(cUtil.fn_qMeaInt(row, "Measure.[Loading Master To Site_45FT Qty]"));
                // measureInsert.push(cUtil.fn_qMeaInt(row, "Measure.[Loading Master To Site_53FT Qty]"));

                //2026.02.06 변경
                measureInsert.push(cUtil.fn_qMeaInt(row, "Measure.[Loading Master To Site_20FT Qty Override]"));
                measureInsert.push(cUtil.fn_qMeaInt(row, "Measure.[Loading Master To Site_40FT Qty Override]"));
                measureInsert.push(cUtil.fn_qMeaInt(row, "Measure.[Loading Master To Site_40HC Qty Override]"));
                measureInsert.push(cUtil.fn_qMeaInt(row, "Measure.[Loading Master To Site_45FT Qty Override]"));
                measureInsert.push(cUtil.fn_qMeaInt(row, "Measure.[Loading Master To Site_53FT Qty Override]"));

                measureInsert.push(cUtil.fn_qMeaInt(row, "Measure.[Loading Master To Site_BOX D]"));
                measureInsert.push(cUtil.fn_qMeaInt(row, "Measure.[Loading Master To Site_BOX H]"));
                measureInsert.push(cUtil.fn_qMeaInt(row, "Measure.[Loading Master To Site_BOX W]"));
                measureInsert.push(cUtil.fn_qMeaInt(row, "Measure.[Loading Master To Site_Build Ahead Period]"));
                measureInsert.push(cUtil.fn_qMeaInt(row, "Measure.[Loading Master To Site_CBM]"));
                measureInsert.push(cUtil.fn_qMeaStr(row, "Measure.[Loading Master To Site_FCL]"));
                measureInsert.push(cUtil.fn_qMeaStr(row, "Measure.[Loading Master To Site_FCL Item Flag]"));
                measureInsert.push(cUtil.fn_qMeaInt(row, "Measure.[Loading Master To Site_Gross Weight]"));
                measureInsert.push(cUtil.fn_qMeaInt(row, "Measure.[Loading Master To Site_Net Weight]"));

                // I/F Measure
                // measureInsert.push(cUtil.fn_qMeaInt(row, "Measure.[Loading Master To Site_TLB MAX Loading Rate]"));
                // measureInsert.push(cUtil.fn_qMeaInt(row, "Measure.[Loading Master To Site_TLB MIN Loading Rate]"));
                
                measureInsert.push(cUtil.fn_qMeaInt(row, "Measure.[Loading Master To Site_TLB MAX Loading Rate Override]"));    // number // 2026.02.06 변경
                measureInsert.push(cUtil.fn_qMeaInt(row, "Measure.[Loading Master To Site_TLB MIN Loading Rate Override]"));
                measureInsert.push(cUtil.fn_qMeaInt(row, "Measure.[Loading Master To Site_LastW Item Flag]"));             // 2026.01.07 추가 
                measureInsert.push(cUtil.fn_qMeaInt(row, "Measure.[Loading Master To Site_SOP Item Flag]"));               // 2026.01.07 추가

                measureInsert.push(cUtil.fn_qMeaUpdateUserName("Measure.[Loading Master To Site_Init By]"));
                measureInsert.push(cUtil.fn_qMeaUpdateTime("Measure.[Loading Master To Site_Init Dttm]"));
                measureInsert.push(cUtil.fn_qMeaUpdateUserName("Measure.[Loading Master To Site_Up By]"));
                measureInsert.push(cUtil.fn_qMeaUpdateTime("Measure.[Loading Master To Site_Up Dttm]"));

                // measureInsert.push(cUtil.fn_qMeaInt(row, "Measure.[Loading Master To Site_Minimum Lot]"));  // Reporting Measure > Aggregation Formula 
                // measureInsert.push(cUtil.fn_qMeaInt(row, "Measure.[Loading Master To Site_Multiple Lot]")); // Reporting Measure > Aggregation Formula 

                let dimension = [];
                dimension.push(cUtil.fn_qDimVersionName(parsedParams));
                dimension.push(cUtil.fn_qDim(row, "[Location].[Location]"));
                dimension.push(cUtil.fn_qDim(row, "[Sub Location].[Sub Location]"));
                dimension.push(cUtil.fn_qDim(row, "[Trans Mode].[Trans Mode]"));
                dimension.push(cUtil.fn_qDim(row, "[Item].[Item]"));

                // 기존 data 중복여부에 대한 체크
                if( rowstatus == "C") {
                    // 중복 체크 후 생성 
                    if ( !cLib.existMeasure(dimension, measureCheck, ""))
                    {
                        cLib.debug("fn_save >>  생성 로직");
                        // 선언한 Measure 모두 Grain (cartesian scope) 시 속도가 느림, Grain 은 한번 생성 후 scope 으로 update
                        cLib.createMeasure(dimension, ['Measure.[Loading Master To Site_Valid] = "Y";']);   // picklist(Y/N) => Boolean 변경 (2026.01.07) 이상엽 프로 요청
                        // cLib.createMeasure(dimension, ['Measure.[Loading Master To Site_Valid] = true;']);   // picklist(Y/N) => Boolean 변경 (2026.01.07) 이상엽 프로 요청
                        cLib.updateMeasure(dimension, measureInsert);
                    }
                } else if( rowstatus == "U") {
                    cLib.debug("fn_save >>  수정 로직");
                    cLib.updateMeasure(dimension, measureUpdate);
                } else if( rowstatus == "D") {
                    cLib.debug("fn_save >>  삭제 로직");
                    cLib.deleteMeasure(dimension, "Loading Master To Site");
                }
               
            } // end for

            fn_PY_UI_BODLoadingInfoApply(parsedParams);

        } catch ( e ) {
            cLib.error(e.message);
            return { "Code" : -1, "Msg" : e.message };
        }
    };

    /**
     * PY 호출 추가 2025.08.28 노보람p 요청 
     * Measure.[Loading Master To Site_Minimum Lot], Measure.[Loading Master To Site_Multiple Lot] 데이터 를 BOD Item 에 업데이트
     * EXEC plugin PY_UI_BODLoadingInfoApply (권태우B 생성);
     * scope 추가 변경 Row > Location, Item 으로 변경 (속도문제로 이상엽P 요청)
     * 
     * @param {*} parsedParams 
     * @returns 
     */
    var fn_PY_UI_BODLoadingInfoApply = function(parsedParams){
        const cLib = fn_cLib(programName + "." + arguments.callee.name);
        cLib.setLogLevel("Debug");

        try {
            cLib.debug("PY_UI_BODLoadingInfoApply ==========================================================>");

            // rowstatus C/U 인경우 && Trans Mode ==="VESSEL" row 필터
            const validRows = parsedParams.fbGridRows.filter(row => ["C","U"].includes(row.rowstatus) && row["[Trans Mode].[Trans Mode]"] === "VESSEL");

            if( validRows.length > 0){

                // 각 컬럼별 Set 생성
                let fbLocation = [...new Set(validRows.map(row => row["[Location].[Location]"]))];
                let fbItem = [...new Set(validRows.map(row => row["[Item].[Item]"]))];

                var execQuery = 'EXEC plugin instance [PY_UI_BODLoadingInfoApply] for measures {[BOD Item_Min Lot Qty]}'
                                +' using scope ( '
                                +' &MPV'
                                +' * &SETMFLocation'+cUtil.fn_filterStr(fbLocation)
                                +' * &SETItem'+cUtil.fn_filterStr(fbItem)
                                +' ) '
                                + 'using arguments {(ExecutionMode, "MediumWeight"), (paramOutVersion , "CWV_MP"), (MaxSliceTableCells, 200000000), (MaxConcurrency, 1 )}; ';

                cLib.debug("execQuery: " + JSON.stringify(execQuery));
                cLib.executeQuery("fn_save : PY_UI_BODLoadingInfoApply Run", execQuery);
            }


        } catch ( e ) {
            cLib.error(e.message);
            return { "Code" : -1, "Msg" : e.message };
        }
    };

    

    // Mapping 함수 정의, 마지막에 선언을 해야 함수를 정상적으로 인식함
    const functionMap = {
        "fn_cb_itemValidBod"    : fn_cb_itemValidBod
       ,"fn_cb_jdm"             : fn_cb_jdm
       ,"fn_cb_location"        : fn_cb_location
       ,"fn_cb_subLocation"     : fn_cb_subLocation
       ,"fn_savePostProcess"    : fn_savePostProcess        // 중복 validation
    };

    return {
        fn_loadFunction : fn_loadFunction
    };

});

/*--------------------------------------------------------------------------------------------------*/
/* 
    프로그램명 : o9.NSCM.JSEWLoadingMasterMgt
    화면명 : Loading Master (EW)
    Action Button : EWLoadingMasterMgt
    [history]
    2025.08.21 : fn_savePostProcess 추가
                fn_save 삭제 - EW 저장
    2025.08.22 : fn_save : EW에서 add, delete 사용 안됨, rowstatus=C/U/D 통합 로직
    2025.08.28 : 저장시 : PY_UI_BODLoadingInfoApply 호출
    2025.09.02 | Measure.[Loading Master To Site_FCL] dataType변경 Boolean->picklist(y/n) (String)
    2025.10.30 : 공통소스 반영
    2025.11.05 : syif1380.lee : fn_qMeaUpdateUser() => fn_qMeaUpdateUserName() 로 변경
    2026.01.06 : syif1380.lee : fn_cb_jdm : JDM 에 "-" 보이도록 콤보에 옵션 추가 ( fn_makeCombo > existHyphen : true )
    2026.01.07 : syif1380.lee : fn_save : add시 컬럼 추가
                                - Measure.[Loading Master To Site_Valid] = true;   // picklist(Y/N) => Boolean 변경 (2026.01.07) 이상엽 프로 요청
                                => dataType 검토 필요 아직 변경전이라 원복
    2026.02.05 : syif1380.lee : fn_PY_UI_BODLoadingInfoApply() > scope 추가 : 변경 Row > Location, Item 으로 변경 (속도문제로 이상엽P 요청)
    2026.02.06 : syif1380.lee : fn_save : Override 로 변경 (이상엽p요청)
    
                                [저장시 Measure 변경]
                                Loading Master To Site_20FT Qty Override
                                Loading Master To Site_40FT Qty Override
                                Loading Master To Site_40HC Qty Override
                                Loading Master To Site_45FT Qty Override
                                Loading Master To Site_53FT Qty Override
                                Loading Master To Site_TLB MAX Loading Rate Override
                                Loading Master To Site_TLB MIN Loading Rate Override
    2026.03.26 : commonLib 선언 부분 변경 및 공통함수 이름 변경
*/
/*--------------------------------------------------------------------------------------------------*/