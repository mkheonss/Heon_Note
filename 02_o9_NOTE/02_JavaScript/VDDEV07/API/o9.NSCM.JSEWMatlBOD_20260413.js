define('o9.NSCM.JSEWMatlBOD', ['o9/data/query', 'o9/data/cellset', 'o9.NSCM.commonLibVD'], function(){

    /*--------------------------------------------------------------------------------------------------*/
    /* 프로그램명 : o9.NSCM.JSEWMatlBOD
     * 화면명 : Matl BOD (EW)  
     * Action Button : EWMatlBOD
     * 최초생성 : 2025.08.27 / syif1380.lee   
    */
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

    const programName = "o9.NSCM.JSEWMatlBOD";
    const Horizon = "&MDMHorizon";
    const queryModule = require('o9/data/query');

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

    // Plant
    var fn_cb_subLocation = function(parsedParams){
        const cLib = fn_cLib(programName + "." + arguments.callee.name);
        cLib.setLogLevel("Debug");

        try {
            cLib.debug("parsedParams :: "+JSON.stringify(parsedParams));
            // var result = cLib.selectList(["&NSUISubLocationMFMtrlView"], [], "", "", "");

            // View Filter 정보 적용 2025.12.29
            let conditions = [];
            conditions.push(cUtil.fn_getFilterQuery(parsedParams,"[Sub Location].[Sub Location Group3]"));

            let where = conditions.length ? `where { ${conditions.join(',')} } ` : '' ;

            var result = cLib.selectList([cUtil.fn_getFilterQuery(parsedParams,"[Sub Location].[Sub Location]")],
                                             [],
                                             where,
                                             "",
                                             "");
            cLib.printCsData(result, 3);

            var comboList = cLib.fn_makeCombo(result, {DimName : "Sub Location", DimAttbName : "Sub Location", Sort : "DisplayName", existAll : false, isDisplayNameWithCode : true});
            cLib.debug("ComboData : " + JSON.stringify(comboList));

            cLib.programEnd();

            return { "Code" : 0, "Msg" : "", "Rows" : comboList };
        } catch ( e ) {
            cLib.error(e.message);
            return { "Code" : -1, "Msg" : e.message };
        }
    };

    // Lv3
    var fn_cb_msl3 = function(parsedParams){
        const cLib = fn_cLib(programName + "." + arguments.callee.name);
        cLib.setLogLevel("Debug");

        try {
            cLib.debug("parsedParams :: "+JSON.stringify(parsedParams));

            // // View Filter 정보
            // let fbMSL1 = parsedParams.fbParams.filter["[Item Material].[MSL1]"];
            // cLib.debug("### fbMSL1.MemberFilter : "+fbMSL1.MemberFilter);
            // cLib.debug("### fbMSL1.SelectedMembers : "+fbMSL1.SelectedMembers);

            // let dimension = [];
            // dimension.push(cUtil.fn_getFilterQuery(parsedParams, "[Item Material].[MSL1]"));
            // dimension.push(cUtil.fn_getFilterQuery(parsedParams, "[Item Material].[MSL3]"));
            // cLib.debug("############### fn_cb_msl3 >> dimension : "+JSON.stringify(dimension)); // a2 : "&NSUIMtrlMSL3View.filter(#.Name in {\"Panel>TV Panel>TV OpenCell\"})"

            // var result = cLib.selectList([fbMSL1.MemberFilter + cUtil.fn_filterStr(fbMSL1.SelectedMembers), "&NSUIMtrlMSL3View"],
            //                                  [],
            //                                  "",
            //                                  "",
            //                                  "");

            // View Filter 정보 적용 2025.12.29
            let conditions = [];
            conditions.push(cUtil.fn_getFilterQuery(parsedParams,"[Item Material].[MSL1]"));
            let where = conditions.length ? `where { ${conditions.join(',')} } ` : '' ;

            var result = cLib.selectList(["&NSUIMtrlMSL3View"],
                                            [],
                                            where,
                                            "",
                                            "");

            cLib.printCsData(result, 3);

            var comboList = cLib.fn_makeCombo(result, {DimName : "Item Material", DimAttbName : "MSL3", Sort : "DisplayName", existAll : false, isDisplayNameWithCode : false});
            cLib.debug("ComboData : " + JSON.stringify(comboList));

            cLib.programEnd();

            return { "Code" : 0, "Msg" : "", "Rows" : comboList };
        } catch ( e ) {
            cLib.error(e.message);
            return { "Code" : -1, "Msg" : e.message };
        }
    };

    // Vendor(HQ)
    var fn_cb_vendor = function(parsedParams){
        const cLib = fn_cLib(programName + "." + arguments.callee.name);
        cLib.setLogLevel("Debug");

        try {
            cLib.debug("parsedParams :: "+JSON.stringify(parsedParams));
            cLib.debug("parsedParams.fbParams.filter :: "+JSON.stringify(parsedParams.fbParams.filter));

            // let fbMSL1 = parsedParams.fbParams.filter["[Item Material].[MSL1]"];

            let fbMSL3 = parsedParams.fbParams["[Item Material].[MSL3]"];
            let fbSubLocation = parsedParams.fbParams["[Sub Location].[Sub Location]"]; // Plant > Sub Location

            // &NSUIGlobalTopView : [Global Top].[GT Code].filter(#.Name in{"G2928239","G1120505","G2685143","G2929950",...)  로 임시로 정의됨. 2025.08.28

            let sql = '(Select ( [Item Material].[MSL3]' + cUtil.fn_filterStr(fbMSL3)
                      +' *  [Item Material].[MSL1] '
                    //   +' * [Global Top].[GT Code].filter(#.Name Startswith"G") '
                      +' * &NSUIGlobalTopView'  // 변경 (2025.08.28 임재민 프로 요청)
                      +' * [Location].[Location]' + cUtil.fn_filterStr(fbSubLocation)
                      +') on row, ({ Measure.[Vendor Mtrl_GT Name], Measure.[Vendor Mtrl Map_Master Flag] } ) on column'
                      +' where { '+ cUtil.fn_getFilterQuery(parsedParams, "[Version].[Version Name]") + ' }'
                      +').filter( Measure.[Vendor Mtrl Map_Master Flag] != "N"  && ~isnull(Measure.[Vendor Mtrl_GT Name]) );'

            let result = cLib.selectQueryList("vendorHQ",sql);
            cLib.printCsData(result, 3);

            let comboList = [];
            let NameVal;
            for (i = 0; i < result.rowCount; i++) {
                let CodeVal = result.cs.row(i).cell(result.cs.memberColumnIndex("Global Top","GT Code")).Name;

                // IBPL Query - 로직 추가 ( 2025.11.20 )
                let LocalSql = `Select ([Location].[Location].[`+ CodeVal +`]);`;
                let Localdata = cLib.selectQueryList("Location", LocalSql);

                if( Localdata.rowCount > 0 ){
                    NameVal = Localdata.cs.row(0).cell(Localdata.cs.memberColumnIndex('Location', 'Location')).Name;
                    let vendorName = result.cs.row(i).cell(result.cs.measureColumnIndex("Vendor Mtrl_GT Name"));

                    // Add Data in the Location Variable
                    comboList.push({ Name: NameVal, DisplayName: vendorName });
                }
            }
            
            // Add Data in the Location P105SP
            // comboList.push({ Name: 'P105SP', DisplayName: "BUSAN(HUB)" });
            // comboList.push({ Name: 'P105SP', DisplayName: "P105SP" });  // DisplayName 도 코드랑 동일하게.. ( 2025.11.20 )

            //====== P105SP 강제추가 부분 삭제 : vendor(HQ)자리에는 GT Code 만 오게한다 (신승호p 요청) 2025.12.09
            // let locationName = cLib.fn_getCodeName("Location", "P105SP");
            // comboList.push({ Name: 'P105SP', DisplayName: locationName});  // Location DisplayName 조회하여 세팅하기 차후 명칭이 변경되어도 자동 적용되도록 함 ( 2025.11.20 )

            cLib.debug("ComboData : " + JSON.stringify(comboList));
            cLib.programEnd();

            return { "Code" : 0, "Msg" : "", "Rows" : comboList };
        } catch ( e ) {
            cLib.error(e.message);
            return { "Code" : -1, "Msg" : e.message };
        }
    };

    // { "fbFuncName" : "fn_cb_tpmode" }
    var fn_cb_tpmode = function(parsedParams){
        const cLib = fn_cLib(programName + "." + arguments.callee.name);
        cLib.setLogLevel("Debug");

        try {
            var result = cLib.selectList(["&NSUITransModeMtrlView"], [], "", "", "");
            cLib.printCsData(result, 3);

            var comboList = cLib.fn_makeCombo(result, {DimName : "Trans Mode", DimAttbName : "Trans Mode", Sort : "DisplayName", existAll : false, isDisplayNameWithCode : false});
            
            cLib.debug("ComboData : " + JSON.stringify(comboList.slice(0,3)));

            cLib.programEnd();

            return { "Code" : 0, "Msg" : "", "Rows" : comboList };
        } catch ( e ) {
            cLib.error(e.message);
            return { "Code" : -1, "Msg" : e.message };
        }
    };

    // Lot Size (하단그리드-Detail)
    // { "fbFuncName" : "fn_cb_lotSize", "fbParams" : {"[Item Material].[Item Material]":"BN96-54530A"} }
    var fn_cb_lotSize = function(parsedParams){
        const cLib = fn_cLib(programName + "." + arguments.callee.name);
        cLib.setLogLevel("Debug");

        try {
            cLib.debug("parsedParams :: "+JSON.stringify(parsedParams));

            let fbItemMaterial = parsedParams.fbParams["[Item Material].[Item Material]"];
            let where = ' where { '+ cUtil.fn_getFilterQuery(parsedParams, "[Version].[Version Name]") + ' }';
            var result = cLib.selectList(["[Item Material].[Item Material].["+fbItemMaterial+"]"]
                                           , ["Measure.[Mtrl Attr_Pallet]", "Measure.[Mtrl Attr_20FT]"
                                           ,"Measure.[Mtrl Attr_40FT]", "Measure.[Mtrl Attr_40FT HC]"], where, "", "");

            cLib.printCsData(result, 3);

            var comboList = [];
            for (i = 0; i < result.cs.rowCount; i++) {
                let nameValue = result.cs.row(i).cell(result.cs.memberColumnIndex("Item Material","Item Material")).Name;
                let attrPallet = result.cs.row(i).cell(result.cs.measureColumnIndex("Mtrl Attr_Pallet"));
                let attr20FT = result.cs.row(i).cell(result.cs.measureColumnIndex("Mtrl Attr_20FT"));
                let attr40FT = result.cs.row(i).cell(result.cs.measureColumnIndex("Mtrl Attr_40FT"));
                let attr40FTHC = result.cs.row(i).cell(result.cs.measureColumnIndex("Mtrl Attr_40FT HC"));

                comboList.push({ Name: nameValue, DisplayName: nameValue, attrPallet, attr20FT, attr40FT, attr40FTHC});
            }

            cLib.debug("ComboData : " + JSON.stringify(comboList));

            return { "Code" : 0, "Msg" : "", "Rows" : comboList };
        } catch ( e ) {
            cLib.error(e.message);
            return { "Code" : -1, "Msg" : e.message };
        }
    };

    // fn_save : 중복 Validation 체크 후 fn_saveProcess 실행
    var fn_save = function(parsedParams){
        const cLib = fn_cLib(programName + "." + arguments.callee.name);
        cLib.setLogLevel("Debug");

        try {
            cLib.debug("fn_save validation ==========================================================>");
            cLib.debug("parsedParams.fbGridRows :: "+JSON.stringify(parsedParams));

            let measureCheck = ["Measure.[BOD List Mtrl_EFF Startdate]","Measure.[BOD List Mtrl_EFF Enddate]","Measure.[BOD List Mtrl_Lot Size]","Measure.[BOD List Mtrl_Lot Type]"];

            errorRowData = [];
            errorRowGrid = [];
            errorMsg = "This is registerd data.";
            errorMsg2 = "Member 해당 코드가 없습니다. ";

            for ( var i=0; i<parsedParams.fbGridRows.length; i++){

                let row = parsedParams.fbGridRows[i];
                let rowstatus = row["rowstatus"];
                let rowindex = row["rowindex"];
                row["rowmsg"] = null;

                // 기존 data 중복여부에 대한 체크
                if( rowstatus == "C") {

                    let fbLocation = row["[Location].[Location]"];               // Vendor(HQ)

                    let dimension = [];
                    dimension.push(cUtil.fn_qDimVersionName(parsedParams));
                    dimension.push(cUtil.fn_qDim(row, "[Location].[Location]"));           // Vendor(HQ)
                    dimension.push(cUtil.fn_qDim(row, "[Item Material].[MSL3]"));
                    dimension.push(cUtil.fn_qDim(row, "[Sub Location].[Sub Location]"));   // Plant
                    dimension.push(cUtil.fn_qDim(row, "[Trans Mode].[Trans Mode]"));

                    // 중복 체크 
                    if ( cLib.existMeasure(dimension, measureCheck, "")){
                        errorRowData.push(rowindex+"^"+errorMsg);
                        errorRowGrid.push(row);
                    }

                    // vendor(HQ) : GT Code 가 Location 멤버등록이 안된 경우 체크
                    var result = cLib.selectList(["[Location].[Location].["+fbLocation+"]"], [], "", "", "");
                    if ( result.cs.rowCount == 0 ) {
                        errorRowData.push(rowindex+"^"+"Location : ["+fbLocation +"] "+errorMsg2);
                        errorRowGrid.push(row);
                    }
                }

            } // end for

            cLib.programEnd();

            // Error row 가 존재할 경우
            if( errorRowData.length > 0 ){
                return { "Code" : 1, "Msg" : errorRowData, "Rows" : errorRowGrid };   // 오류 리턴
            }

            fn_saveProcess(parsedParams);   // 저장 로직 수행

            return { "Code" : 0, "Msg" : "", "Rows" : "" }; // 정상 리턴

        } catch ( e ) {
            cLib.error(e.message);
            return { "Code" : -1, "Msg" : e.message };
        }
    };

    /**
     * fn_saveProcess 실제 Data 저장 Logic
     * 상단그리드 저장 ( BOD List Mtrl, BOD List Mtrl W )
     * 
     * @param {*} o9Params 
     * @returns 
     */
    var fn_saveProcess = function(parsedParams){
        const cLib = fn_cLib(programName + "." + arguments.callee.name);
        cLib.setLogLevel("Debug");

        try {
            cLib.debug("parsedParams :: "+JSON.stringify(parsedParams));

            // let measureCheck = ["Measure.[BOD List Mtrl_EFF Startdate]","Measure.[BOD List Mtrl_EFF Enddate]","Measure.[BOD List Mtrl_Lot Size]","Measure.[BOD List Mtrl_Lot Type]"];
            for ( var i=0; i<parsedParams.fbGridRows.length; i++){

                let row = parsedParams.fbGridRows[i];
                let rowstatus = row["rowstatus"];

                // BOD List Mtrl (MG) : Grain - [Version].[Version Name] * [Location].[Location] * [Item Material].[MSL3] * [Sub Location].[Sub Location] * [Trans Mode].[Trans Mode]
                let dimension = [];
                dimension.push(cUtil.fn_qDimVersionName(parsedParams));
                dimension.push(cUtil.fn_qDim(row, "[Location].[Location]"));           // Vendor(HQ)
                dimension.push(cUtil.fn_qDim(row, "[Item Material].[MSL3]"));
                dimension.push(cUtil.fn_qDim(row, "[Sub Location].[Sub Location]"));   // Plant
                dimension.push(cUtil.fn_qDim(row, "[Trans Mode].[Trans Mode]"));

                // BOD List Mtrl W
                let dimensionW = [...dimension];
                dimensionW.push(Horizon);

                // Measure
                // let fbLotSize = parsedParams.fbGridRows[i]["Measure.[BOD List Mtrl_Lot Size]"];         // Integer  // 설계서에 정의되어 있지 않음.
                // update 메저
                let measureUpdate = [];
                measureUpdate.push(cUtil.fn_qMeaUpdateUserName("Measure.[BOD List Mtrl_Updated By]"));
                measureUpdate.push(cUtil.fn_qMeaUpdateTime("Measure.[BOD List Mtrl_Updated Time]"));
                measureUpdate.push(cUtil.fn_qMeaStr(row, "Measure.[BOD List Mtrl_Lot Type]"));
                measureUpdate.push(cUtil.fn_qMeaStr(row, "Measure.[BOD List Mtrl_EFF Enddate]"));
                measureUpdate.push(cUtil.fn_qMeaStr(row, "Measure.[BOD List Mtrl_EFF Startdate]"));
                measureUpdate.push(cUtil.fn_qMeaInt(row, "Measure.[BOD List Mtrl_Priority]"));             // 추가 2025.12.11
                measureUpdate.push(cUtil.fn_qMeaStr(row, "Measure.[BOD List Mtrl_Time Varying Flag]"));    // 추가 2025.12.11

                // insert 메저
                let measureInsert = [...measureUpdate];
                measureInsert.push(cUtil.fn_qMeaUpdateUserName("Measure.[BOD List Mtrl_Created By]"));
                measureInsert.push(cUtil.fn_qMeaUpdateTime("Measure.[BOD List Mtrl_Created Time]"));

                if( rowstatus == "C"){

                    // BOD List Mtrl 생성
                    cLib.createMeasure(dimension, [cUtil.fn_qMeaUpdateTime("Measure.[BOD List Mtrl_Created Time]")]);
                    cLib.updateBlockMeasure(dimension, measureInsert);

                    // BOD List Mtrl W 저장 (주차별 저장)
                    fn_measureWUpdate(row, dimension, "BOD List Mtrl W");

                }else if( rowstatus == "U"){

                    // BOD List Mtrl 수정
                    cLib.updateBlockMeasure(dimension, measureUpdate);

                    // BOD List Mtrl W 저장 (주차별 저장)
                    fn_measureWUpdate(row, dimension, "BOD List Mtrl W");

                }else if( rowstatus == "D"){
                    cLib.deleteMeasure(dimension, "BOD List Mtrl");
                    cLib.deleteMeasure(dimensionW, "BOD List Mtrl W");
                    cLib.deleteMeasure(dimension, "BOD Item Mtrl");
                    cLib.deleteMeasure(dimensionW, "BOD Item Mtrl W");
                }
            }

            cLib.debug("javascript --------------- 저장 로직 종료 ==> PY호출 시작");

            // PY 호출 (PY_UI_MtrlBODItem)
            fn_savePostProcess(parsedParams);

        } catch ( e ) {
            cLib.error(e.message);
            return { "Code" : -1, "Msg" : e.message };
        }
    };

    var fn_savePostProcess = function(parsedParams){
        const cLib = fn_cLib(programName + "." + arguments.callee.name);
        cLib.setLogLevel("Debug");

        try {
            cLib.debug("parsedParams :: "+JSON.stringify(parsedParams));

            // 변경 된 Row 중 중복을 제외한 멀티 선택 
            let fbLocation = [...new Set(parsedParams.fbGridRows.map(row => row["[Location].[Location]"]))];             // Vendor (HQ) : &NSUILocVendorBODView
            let fbSubLocation = [...new Set(parsedParams.fbGridRows.map(row => row["[Sub Location].[Sub Location]"]))];  // Factory.
            let fbMsl3 = [...new Set(parsedParams.fbGridRows.map(row => row["[Item Material].[MSL3]"]))];
            let fbTPMode = [...new Set(parsedParams.fbGridRows.map(row => row["[Trans Mode].[Trans Mode]"]))];

            cLib.debug(" PY 호출 ======================>PY_UI_MtrlBODItem : fbLocation : "+ fbLocation);
            cLib.debug(" PY 호출 ======================>PY_UI_MtrlBODItem : fbSubLocation : "+ fbSubLocation);
            cLib.debug(" PY 호출 ======================>PY_UI_MtrlBODItem : fbMsl3 : "+ fbMsl3);
            cLib.debug(" PY 호출 ======================>PY_UI_MtrlBODItem : fbTPMode : "+ fbTPMode);

            cLib.debug(" fn_save #############   PY 실행 : PY_UI_MtrlBODItem ##############");

            // PY 호출 변경 2025.10.16 신승호p 요청 (PY 권태우B 개발)
            var execQuery = 'EXEC plugin instance [PY_UI_MtrlBODItem] for measures {[BOD Item Mtrl W_Factory Out]} '
                            +' using scope ( '
                            +' &MPV'
                            // +' * [Location].[Location]'+cUtil.fn_filterStr(fbLocation)
                            +' * [Sub Location].[Sub Location]'+cUtil.fn_filterStr(fbSubLocation)
                            +' * [Item Material].[MSL3]'+cUtil.fn_filterStr(fbMsl3)
                            +' * [Trans Mode].[Trans Mode]'+cUtil.fn_filterStr(fbTPMode)
                            +' * [Global Top].[GT Code]'+cUtil.fn_filterStr(fbLocation)
                            +' ) '
                          + 'using arguments {(ExecutionMode, "MediumWeight"), ("IncludeNullRows", "False"), (paramOutVersion , "CWV_MP"), (MaxSliceTableCells, 200000000), (MaxConcurrency, 1), ([Param.o9_sys_log_level], "DEBUG")}; ';

            cLib.debug("execQuery: " + JSON.stringify(execQuery));
            cLib.executeQuery("fn_save : PY_UI_MtrlBODItem Run", execQuery);

            // PY 호출 추가 2025.08.28 신승호p 요청
            // 하단 그리드 Data 상속해주는 Python 실행
            // var execQuery = 'EXEC plugin instance [PY_UI_MatlBODApply] ' +
            //                 'for measures {[BOD Item Mtrl W_Factory Out],[BOD Item Mtrl W_GR LT],[BOD Item Mtrl W_Port To Port],[BOD Item Mtrl_EFF Startdate],[BOD Item Mtrl_EFF Enddate],[BOD Item Mtrl_Lock Flag],[BOD Item Mtrl_Lot Type],[BOD Item Mtrl_Lot Size]} ' +
            //                 'using scope ( &CWVUI )' +
            //                 'using arguments {(ExecutionMode, "MediumWeight"), (paramOutVersion , "CWV_MP"), (MaxSliceTableCells, 200000000), (MaxConcurrency, 1 )}; ';

            // PY 호출 변경 2025.10.16 신승호p 요청 (PY 권태우B 개발)
            // var execQuery = 'EXEC plugin instance [PY_UI_MtrlBODItem] for measures {[BOD Item Mtrl W_Factory Out]} using scope (&MPV) '+
            //                 'using arguments {(ExecutionMode, "MediumWeight"), ("IncludeNullRows", "False"), (paramOutVersion , "CWV_MP"), (MaxSliceTableCells, 200000000), (MaxConcurrency, 1), ([Param.o9_sys_log_level], "DEBUG")}; ';
            // cLib.debug("execQuery: " + JSON.stringify(execQuery));
            // cLib.executeQuery("fn_save : PY_UI_MtrlBODItem Run", execQuery);

        } catch ( e ) {
            cLib.error(e.message);
            return { "Code" : -1, "Msg" : e.message };
        }
    };

    /**
     * fn_saveDetail 실제 Data 저장 Logic
     * 하단 그리드 저장 ( BOD Item Mtrl, BOD Item Mtrl W)  
     * Add 기능 없음
     * @param {*} o9Params 
     * @returns 
     */
    var fn_saveDetail = function(parsedParams){
        const cLib = fn_cLib(programName + "." + arguments.callee.name);
        cLib.setLogLevel("Debug");

        try {
            cLib.debug("### fn_saveDetail >> parsedParams :: "+JSON.stringify(parsedParams));

            // let measureCheck = ["Measure.[BOD List Mtrl_EFF Startdate]","Measure.[BOD List Mtrl_EFF Enddate]","Measure.[BOD List Mtrl_Lot Size]","Measure.[BOD List Mtrl_Lot Type]"];
            for ( var i=0; i<parsedParams.fbGridRows.length; i++){

                let row = parsedParams.fbGridRows[i];
                let rowstatus = row["rowstatus"];

                // BOD Item Mtrl (MG) : Grain - [Version].[Version Name] * [Location].[Location] * [Item Material].[MSL3] * [Sub Location].[Sub Location] * [Trans Mode].[Trans Mode]
                let dimension = [];
                dimension.push(cUtil.fn_qDimVersionName(parsedParams));
                dimension.push(cUtil.fn_qDim(row, "[Location].[Location]"));           // Vendor(HQ)
                dimension.push(cUtil.fn_qDim(row, "[Sub Location].[Sub Location]"));   // Plant
                dimension.push(cUtil.fn_qDim(row, "[Trans Mode].[Trans Mode]"));
                dimension.push(cUtil.fn_qDim(row, "[Item Material].[Item Material]"));
                
                // BOD Item Mtrl W
                let dimensionW = [...dimension];
                dimensionW.push(Horizon);

                // update 메저
                let measureUpdate = [];
                measureUpdate.push(cUtil.fn_qMeaUpdateUserName("Measure.[BOD Item Mtrl_Updated By]"));
                measureUpdate.push(cUtil.fn_qMeaUpdateTime("Measure.[BOD Item Mtrl_Updated Time]"));
                measureUpdate.push(cUtil.fn_qMeaStr(row, "Measure.[BOD Item Mtrl_EFF Enddate]"));      // Datetime
                measureUpdate.push(cUtil.fn_qMeaStr(row, "Measure.[BOD Item Mtrl_EFF Startdate]"));    // Datetime
                measureUpdate.push(cUtil.fn_qMeaStr(row, "Measure.[BOD Item Mtrl_Lock Flag]"));        // String
                measureUpdate.push(cUtil.fn_qMeaStr(row, "Measure.[BOD Item Mtrl_Lot Type]"));         // String
                measureUpdate.push(cUtil.fn_qMeaStr(row, "Measure.[BOD Item Mtrl_Lot Size]"));         // String 추가 2025.11.04
                measureUpdate.push(cUtil.fn_qMeaInt(row, "Measure.[BOD Item Mtrl_Priority]"));             // 추가 2025.12.11
                measureUpdate.push(cUtil.fn_qMeaStr(row, "Measure.[BOD Item Mtrl_Time Varying Flag]"));    // 추가 2025.12.11

                // Update만 (신규 생성 없음)
                if( rowstatus == "U"){

                    // BOD Item Mtrl 저장
                    cLib.updateBlockMeasure(dimension, measureUpdate);

                    // BOD Item Mtrl W 저장 (주차별 저장)
                    fn_measureWUpdate(row, dimension, "BOD Item Mtrl W");

                }else if( rowstatus == "D"){
                    cLib.deleteMeasure(dimension, "BOD Item Mtrl");
                    cLib.deleteMeasure(dimensionW, "BOD Item Mtrl W");
                }
            }

            cLib.programEnd();

            return { "Code" : 0, "Msg" : "", "Rows" : "" };

        } catch ( e ) {
            cLib.error(e.message);
            return { "Code" : -1, "Msg" : e.message };
        }
    };

    /**
     * 주차별 Update ( BOD List Mtrl W , BOD Item Mtrl W)
     * update 할 메저 대상이 추가될 경우 measureList 에 배열로 추가한다. 이후 자동메저 update 문장 완성 됨
     * @param {*} row 
     * @param {*} dimension 
     * @param {*} measureGroup 
     * @returns 
     */
    var fn_measureWUpdate = function(row, dimension, measureGroup){
        const cLib = fn_cLib(programName + "." + arguments.callee.name);
        cLib.setLogLevel("Debug");
        try {

            let measureList = [];       // 메저 명칭 정의
            let measureCheck = [];

            if( measureGroup == "BOD List Mtrl W"){
                measureList = ["Measure.[BOD List Mtrl W_Factory Out]", "Measure.[BOD List Mtrl W_Port To Port]", "Measure.[BOD List Mtrl W_GR LT]"];
                measureCheck = ["Measure.[BOD List Mtrl W_Factory Out]","Measure.[BOD List Mtrl W_GR LT]","Measure.[BOD List Mtrl W_Port To Port]","Measure.[BOD List Mtrl W_Supplier]"];
            }else{
                measureList = ["Measure.[BOD Item Mtrl W_Factory Out]","Measure.[BOD Item Mtrl W_Port To Port]","Measure.[BOD Item Mtrl W_GR LT]"];
                measureCheck = ["Measure.[BOD Item Mtrl W_Factory Out]","Measure.[BOD Item Mtrl W_Port To Port]","Measure.[BOD Item Mtrl W_GR LT]"];
            }

            for ( var i=0; i < measureList.length; i++){

                let measureName = measureList[i]; // measure 명
                let measureValueArray = row[measureName]; // measure value ["202508^10","202509^20","202510^30"]

                if( measureValueArray !== null && measureValueArray !== undefined ){
                    for ( var k=0; k < measureValueArray.length; k++){
                        let weekValue = measureValueArray[k].split("^"); // "202508^1" > weekValue[0] => 주차(202508), weekValue[1] =>주차값(10)
                        let dimWeek1 = [...dimension];
                        dimWeek1.push("[Time].[Week].["+weekValue[0]+"]");  // 202508
                        let measureUpdate = [];
                        measureUpdate.push(cUtil.fn_qMeaInt(null, measureName, weekValue[1])); // 'Measure.[BOD List Mtrl W_Factory Out] = 10;'

                        if ( !cLib.existMeasure(dimWeek1, measureCheck, "")){
                            cLib.createMeasure(dimWeek1, measureUpdate);
                        }else{
                            cLib.updateBlockMeasure(dimWeek1, measureUpdate);
                        }
                    }
                }
            }

        } catch ( e ) {
            cLib.error(e.message);
            return { "Code" : -1, "Msg" : e.message };
        }
    };

    // /**
    //  * fn_merge : Scenario Plan >> 테스트 필요..
    //  * 2026.03.03 생성
    //  * @param {*} o9Params 
    //  * @returns 
    //  */
    // var fn_merge = function(parsedParams){
    //     const cLib = fn_cLib(programName + "." + arguments.callee.name);
    //     cLib.setLogLevel("Debug");

    //     try {
    //         cLib.debug("fn_merge call ==========================================================>");
    //         cLib.debug("parsedParams :: "+JSON.stringify(parsedParams));

    //         var fbVersion = parsedParams.fbParams["[Version].[Version Name]"];  // ew에서 버전이 어떻게 넘어 오는지???

    //         for ( var i=0; i<parsedParams.fbGridRows.length; i++){

    //             var row = parsedParams.fbGridRows[i];

    //             // cLib.deleteMeasure(dimension, "BOD List Mtrl");
    //             // cLib.deleteMeasure(dimensionW, "BOD List Mtrl W");
    //             // cLib.deleteMeasure(dimension, "BOD Item Mtrl");
    //             // cLib.deleteMeasure(dimensionW, "BOD Item Mtrl W");
    //             //[Version].[Version Name] * [Location].[Location] * [Sub Location].[Sub Location] * [Item Material].[MSL3] * [Trans Mode].[Trans Mode] 

    //             //----------------------------------------------------------------------------------------------//
    //             // BOD List Mtrl
    //             //----------------------------------------------------------------------------------------------//
    //             // dimension 정의
    //             let dimension = [];
    //             dimension.push("[Version].[Version Name].[CWV_MP]");
    //             dimension.push(cUtil.fn_qDim(row, "[Location].[Location]"));
    //             dimension.push(cUtil.fn_qDim(row, "[Sub Location].[Sub Location]"));
    //             dimension.push(cUtil.fn_qDim(row, "[Trans Mode].[Trans Mode]"));
    //             dimension.push(cUtil.fn_qDim(row, "[Item Material].[MSL3]"));
    //             //  Update
    //             let measure = [];
    //             measure.push(cUtil.fn_qMeaForMerge("Measure.[BOD List Mtrl_EFF Enddate]", fbVersion));
    //             measure.push(cUtil.fn_qMeaForMerge("Measure.[BOD List Mtrl_EFF Startdate]", fbVersion));
    //             measure.push(cUtil.fn_qMeaForMerge("Measure.[BOD List Mtrl_Lot Size]", fbVersion));
    //             measure.push(cUtil.fn_qMeaForMerge("Measure.[BOD List Mtrl_Lot Type]", fbVersion));
    //             measure.push(cUtil.fn_qMeaForMerge("Measure.[BOD List Mtrl_Priority]", fbVersion));
    //             measure.push(cUtil.fn_qMeaForMerge("Measure.[BOD List Mtrl_Time Varying Flag]", fbVersion));
    //             measure.push(cLib.fn_mergeUser("Measure.[BOD List Mtrl_Updated By]", fbVersion));
    //             measure.push(cUtil.fn_qMeaUpdateTime("Measure.[BOD List Mtrl_Updated Time]"));

    //             cLib.createMeasure(dimension, measure);

    //             //----------------------------------------------------------------------------------------------//
    //             // BOD List Mtrl W
    //             //----------------------------------------------------------------------------------------------//
    //             // dimension 정의
    //             dimension = [];
    //             dimension.push("[Version].[Version Name].[CWV_MP]");
    //             dimension.push(cUtil.fn_qDim(row, "[Location].[Location]"));
    //             dimension.push(cUtil.fn_qDim(row, "[Sub Location].[Sub Location]"));
    //             dimension.push(cUtil.fn_qDim(row, "[Trans Mode].[Trans Mode]"));
    //             dimension.push(cUtil.fn_qDim(row, "[Item Material].[MSL3]"));
    //             dimension.push(Horizon);

    //             //  Update
    //             measure = [];
    //             measure.push(cUtil.fn_qMeaForMerge("Measure.[BOD List Mtrl_EFF Enddate]", fbVersion));
    //             measure.push(cUtil.fn_qMeaForMerge("Measure.[BOD List Mtrl_EFF Startdate]", fbVersion));
    //             measure.push(cUtil.fn_qMeaForMerge("Measure.[BOD List Mtrl_Lot Size]", fbVersion));
    //             measure.push(cUtil.fn_qMeaForMerge("Measure.[BOD List Mtrl_Lot Type]", fbVersion));
    //             measure.push(cUtil.fn_qMeaForMerge("Measure.[BOD List Mtrl_Priority]", fbVersion));
    //             measure.push(cUtil.fn_qMeaForMerge("Measure.[BOD List Mtrl_Time Varying Flag]", fbVersion));
    //             measure.push(cLib.fn_mergeUser("Measure.[BOD List Mtrl_Updated By]", fbVersion));
    //             measure.push(cUtil.fn_qMeaUpdateTime("Measure.[BOD List Mtrl_Updated Time]"));

    //             cLib.createMeasure(dimension, measure);

    //             //----------------------------------------------------------------------------------------------//
    //             // BOD Item Mtrl
    //             //----------------------------------------------------------------------------------------------//
    //             // dimension 정의
    //             dimension = [];
    //             dimension.push("[Version].[Version Name].[CWV_MP]");
    //             dimension.push(cUtil.fn_qDim(row, "[Location].[Location]"));
    //             dimension.push(cUtil.fn_qDim(row, "[Sub Location].[Sub Location]"));
    //             dimension.push(cUtil.fn_qDim(row, "[Trans Mode].[Trans Mode]"));
    //             dimension.push(cUtil.fn_qDim(row, "[Item Material].[Item Material]"));

    //             measure = [];
    //             measure.push(cUtil.fn_qMeaForMerge("Measure.[BOD Item Mtrl_EFF Enddate]", fbVersion));
    //             measure.push(cUtil.fn_qMeaForMerge("Measure.[BOD Item Mtrl_EFF Startdate]", fbVersion));
    //             measure.push(cUtil.fn_qMeaForMerge("Measure.[BOD Item Mtrl_Lock Flag]", fbVersion));
    //             measure.push(cUtil.fn_qMeaForMerge("Measure.[BOD Item Mtrl_Lot Size]", fbVersion));
    //             measure.push(cUtil.fn_qMeaForMerge("Measure.[BOD Item Mtrl_Lot Type]", fbVersion));
    //             measure.push(cUtil.fn_qMeaForMerge("Measure.[BOD Item Mtrl_Priority]", fbVersion));
    //             measure.push(cUtil.fn_qMeaForMerge("Measure.[BOD Item Mtrl_Time Varying Flag]", fbVersion));
    //             measure.push(cLib.fn_mergeUser("Measure.[BOD Item Mtrl_Updated By]", fbVersion));
    //             measure.push(cUtil.fn_qMeaUpdateTime("Measure.[BOD Item Mtrl_Updated Time]"));

    //             cLib.createMeasure(dimension, measure);

    //             //----------------------------------------------------------------------------------------------//
    //             // BOD Item Mtrl W
    //             //----------------------------------------------------------------------------------------------//
    //             // dimension 정의
    //             dimension = [];
    //             dimension.push("[Version].[Version Name].[CWV_MP]");
    //             dimension.push(cUtil.fn_qDim(row, "[Location].[Location]"));
    //             dimension.push(cUtil.fn_qDim(row, "[Sub Location].[Sub Location]"));
    //             dimension.push(cUtil.fn_qDim(row, "[Trans Mode].[Trans Mode]"));
    //             dimension.push(cUtil.fn_qDim(row, "[Item Material].[Item Material]"));
    //             dimension.push(Horizon);

    //             measure = [];
    //             measure.push(cUtil.fn_qMeaForMerge("Measure.[BOD Item Mtrl W_Factory Out]", fbVersion));
    //             measure.push(cUtil.fn_qMeaForMerge("Measure.[BOD Item Mtrl W_GR LT]", fbVersion));
    //             // measure.push(cUtil.fn_qMeaForMerge("Measure.[BOD Item Mtrl W_Intransit LT]", fbVersion));   // Reporting Measure
    //             measure.push(cUtil.fn_qMeaForMerge("Measure.[BOD Item Mtrl W_Port To Port]", fbVersion));
    //             measure.push(cUtil.fn_qMeaForMerge("Measure.[BOD Item Mtrl W_Supplier]", fbVersion));
    //             // measure.push(cUtil.fn_qMeaForMerge("Measure.[BOD Item Mtrl W_Total LT]", fbVersion));       // Reporting Measure

    //             cLib.createMeasure(dimension, measure);
            
    //         }

    //         cLib.programEnd();

    //         //  정상 저장 후 리턴 값?? Warn 종류는 저장은 되고, 화면으로 메세지 리턴해줘야 함
    //         return { "Code" : 0, "Msg" : "It was saved successfully." };

    //     } catch ( e ) {
    //         cLib.error(e.message);
    //         return { "Code" : -1, "Msg" : e.message };
    //     }
    // };

    // var fn_merge_bak = function(parsedParams){
    //     const cLib = fn_cLib(programName + "." + arguments.callee.name);
    //     cLib.setLogLevel("Debug");

    //     try {
    //         cLib.debug("fn_merge call ==========================================================>");
    //         cLib.debug("parsedParams :: "+JSON.stringify(parsedParams));

    //         cLib.debug("fn_getFilterValue >>"+cUtil.fn_getFilterValue(parsedParams, "[Version].[Version Name]"));

    //         // var fbVersion = parsedParams.fbParams["[Version].[Version Name]"];  // ew에서 버전이 어떻게 넘어 오는지??? (시나리오 버전)
    //         var fbVersion = cUtil.fn_getFilterValue(parsedParams, "[Version].[Version Name]");  // ew에서 버전이 어떻게 넘어 오는지??? (시나리오 버전)
    //         var toVersion = "[Version].[Version Name].[CWV_MP]";

    //         let grid = parsedParams.fbParams["grid"];   // Top , Bottom

    //         if( grid == "Top"){
    //             for ( var i=0; i<parsedParams.fbGridRows.length; i++){

    //                 var row = parsedParams.fbGridRows[i];

    //                 let dimMtrl = [];
    //                 dimMtrl.push(cUtil.fn_qDim(row, "[Location].[Location]"));
    //                 dimMtrl.push(cUtil.fn_qDim(row, "[Sub Location].[Sub Location]"));
    //                 dimMtrl.push(cUtil.fn_qDim(row, "[Trans Mode].[Trans Mode]"));
    //                 dimMtrl.push(cUtil.fn_qDim(row, "[Item Material].[MSL3]"));

    //                 let dimMtrlW = [];
    //                 dimMtrlW.push(cUtil.fn_qDim(row, "[Location].[Location]"));
    //                 dimMtrlW.push(cUtil.fn_qDim(row, "[Sub Location].[Sub Location]"));
    //                 dimMtrlW.push(cUtil.fn_qDim(row, "[Trans Mode].[Trans Mode]"));
    //                 dimMtrlW.push(cUtil.fn_qDim(row, "[Item Material].[MSL3]"));
    //                 dimMtrlW.push(Horizon);
    
    //                 //-------------------------------------------------------------------------------------
    //                 // 시나리오 버전 Copy ( fbVersion => toVersion (CWP_MP) 로 copy )
    //                 // 각 MG 의 시나리오 버전 데이터가 없는 경우 copy 안됨
    //                 //-------------------------------------------------------------------------------------
    //                 let query = 'UpdateScenario( '
    //                 + toVersion         // To 버전
    //                 + ',' + "[Version].[Version Name].["+fbVersion+"]"   // 시나리오 버전(from 버전)
    //                 + ',false'
    //                 + ',for model [BOD List Mtrl] using scope (' + dimMtrl.join('*') + ')'
    //                 + ',for model [BOD List Mtrl W] using scope (' + dimMtrlW.join('*') + ')'
    //                 +'); ';
    
    //                 cLib.debug("UpdateScenario >> "+query);
    //                 queryModule.update(query);
    
    //                 //-------------------------------------------------------------------------------------
    //                 // BOD List Mtrl : 사용자 Update > 시나리오 버전 Data 가 존재할 때만 update
    //                 //-------------------------------------------------------------------------------------
    //                 let dimMtrlChk = [...dimMtrl];
    //                 dimMtrlChk.push("[Version].[Version Name].["+fbVersion+"]"); // 시나리오 버전
    //                 if( cLib.existMeasure(dimMtrlChk, ["Measure.[BOD List Mtrl_Created Time]","Measure.[BOD List Mtrl_Updated Time]"], "") ){
    
    //                     dimMtrl.push(toVersion);
    
    //                     let measure = [];
    //                     measure.push(cLib.fn_mergeUser("Measure.[BOD List Mtrl_Updated By]", fbVersion));
    //                     measure.push(cUtil.fn_qMeaUpdateTime("Measure.[BOD List Mtrl_Updated Time]"));
    //                     cLib.updateMeasure(dimMtrl, measure);
    //                 }

    //                 //-------------------------------------------------------------------------------------
    //                 // BOD List Mtrl W : 사용자 Update > Measure 없어서 skip
    //                 //-------------------------------------------------------------------------------------
    //             }

    //         }else if( grid == "Bottom"){

    //             for ( var i=0; i<parsedParams.fbGridRows.length; i++){

    //                 var row = parsedParams.fbGridRows[i];

    //                 let dimMtrl = [];
    //                 dimMtrl.push(cUtil.fn_qDim(row, "[Location].[Location]"));
    //                 dimMtrl.push(cUtil.fn_qDim(row, "[Sub Location].[Sub Location]"));
    //                 dimMtrl.push(cUtil.fn_qDim(row, "[Trans Mode].[Trans Mode]"));
    //                 dimMtrl.push(cUtil.fn_qDim(row, "[Item Material].[Item Material]"));

    //                 let dimMtrlW = [];
    //                 dimMtrlW.push(cUtil.fn_qDim(row, "[Location].[Location]"));
    //                 dimMtrlW.push(cUtil.fn_qDim(row, "[Sub Location].[Sub Location]"));
    //                 dimMtrlW.push(cUtil.fn_qDim(row, "[Trans Mode].[Trans Mode]"));
    //                 dimMtrlW.push(cUtil.fn_qDim(row, "[Item Material].[Item Material]"));
    //                 dimMtrlW.push(Horizon);
    
    //                 //-------------------------------------------------------------------------------------
    //                 // 시나리오 버전 Copy ( fbVersion => toVersion (CWP_MP) 로 copy )
    //                 // 각 MG 의 시나리오 버전 데이터가 없는 경우 copy 안됨
    //                 //-------------------------------------------------------------------------------------
    //                 let query = 'UpdateScenario( '
    //                 + toVersion         // To 버전
    //                 + ',' + "[Version].[Version Name].["+fbVersion+"]"   // 시나리오 버전(from 버전)
    //                 + ',false'
    //                 + ',for model [BOD Item Mtrl] using scope (' + dimMtrl.join('*') + ')'
    //                 + ',for model [BOD Item Mtrl W] using scope (' + dimMtrlW.join('*') + ')'
    //                 +'); ';
    
    //                 cLib.debug("UpdateScenario >> "+query);
    //                 queryModule.update(query);
    
    //                 //-------------------------------------------------------------------------------------
    //                 // BOD Item Mtrl : 사용자 Update > 시나리오 버전 Data 가 존재할 때만 update
    //                 //-------------------------------------------------------------------------------------
    //                 let dimMtrlChk = [...dimMtrl];
    //                 dimMtrlChk.push("[Version].[Version Name].["+fbVersion+"]"); // 시나리오 버전
    //                 if( cLib.existMeasure(dimMtrlChk, ["Measure.[BOD Item Mtrl_Created Time]","Measure.[BOD Item Mtrl_Updated Time]"], "") ){
    
    //                     dimMtrl.push(toVersion);
    
    //                     let measure = [];
    //                     measure.push(cLib.fn_mergeUser("Measure.[BOD Item Mtrl_Updated By]", fbVersion));
    //                     measure.push(cUtil.fn_qMeaUpdateTime("Measure.[BOD Item Mtrl_Updated Time]"));
    //                     cLib.updateMeasure(dimMtrl, measure);
    //                 }

    //                 //-------------------------------------------------------------------------------------
    //                 // BOD Item Mtrl W : 사용자 Update > Measure 없어서 skip
    //                 //-------------------------------------------------------------------------------------
    //             }
    //         }

    //         cLib.programEnd();

    //         //  정상 저장 후 리턴
    //         return { "Code" : 0, "Msg" : "It was saved successfully." };

    //     } catch ( e ) {
    //         cLib.error(e.message);
    //         return { "Code" : -1, "Msg" : e.message };
    //     }
    // };

    var fn_merge = function(parsedParams){
        const cLib = fn_cLib(programName + "." + arguments.callee.name);
        cLib.setLogLevel("Debug");

        try {
            cLib.debug("fn_merge call ==========================================================>");
            cLib.debug("parsedParams :: "+JSON.stringify(parsedParams));

            cLib.debug("fn_getFilterValue >>"+cUtil.fn_getFilterValue(parsedParams, "[Version].[Version Name]"));

            // var fbVersion = parsedParams.fbParams["[Version].[Version Name]"];  // ew에서 버전이 어떻게 넘어 오는지??? (시나리오 버전)
            var fbVersion = cUtil.fn_getFilterValue(parsedParams, "[Version].[Version Name]");  // ew에서 버전이 어떻게 넘어 오는지??? (시나리오 버전)
            var toVersion = "[Version].[Version Name].[CWV_MP]";

            if( parsedParams.fbParams["mergeType"] == "1"){

                let query = 'UpdateScenario( '
                    + toVersion         // To 버전
                    + ',' + "[Version].[Version Name].["+fbVersion+"]"   // 시나리오 버전(from 버전)
                    + ',false'
                    + ',for model [BOD List Mtrl] '
                    + ',for model [BOD List Mtrl W] '
                    + ',for model [BOD Item Mtrl] '
                    + ',for model [BOD Item Mtrl W] '
                    +'); ';

                    cLib.debug("UpdateScenario >> "+query);
                    queryModule.update(query);

            }else if( parsedParams.fbParams["mergeType"] == "0"){

                // parsedParams.fbGridRows.master
                for ( var i=0; i<parsedParams.fbGridRows.master.length; i++){

                    var row = parsedParams.fbGridRows.master[i];

                    let dimMtrl = [];
                    dimMtrl.push(cUtil.fn_qDim(row, "[Location].[Location]"));
                    dimMtrl.push(cUtil.fn_qDim(row, "[Sub Location].[Sub Location]"));
                    dimMtrl.push(cUtil.fn_qDim(row, "[Trans Mode].[Trans Mode]"));
                    dimMtrl.push(cUtil.fn_qDim(row, "[Item Material].[MSL3]"));

                    let dimMtrlW = [];
                    dimMtrlW.push(cUtil.fn_qDim(row, "[Location].[Location]"));
                    dimMtrlW.push(cUtil.fn_qDim(row, "[Sub Location].[Sub Location]"));
                    dimMtrlW.push(cUtil.fn_qDim(row, "[Trans Mode].[Trans Mode]"));
                    dimMtrlW.push(cUtil.fn_qDim(row, "[Item Material].[MSL3]"));
                    dimMtrlW.push(Horizon);

                    // let dimMtrlItem = [];
                    // dimMtrl.push(cUtil.fn_qDim(row, "[Location].[Location]"));
                    // dimMtrl.push(cUtil.fn_qDim(row, "[Sub Location].[Sub Location]"));
                    // dimMtrl.push(cUtil.fn_qDim(row, "[Trans Mode].[Trans Mode]"));
                    // dimMtrl.push(cUtil.fn_qDim(row, "[Item Material].[Item Material]"));

                    // let dimMtrlItemW = [];
                    // dimMtrlW.push(cUtil.fn_qDim(row, "[Location].[Location]"));
                    // dimMtrlW.push(cUtil.fn_qDim(row, "[Sub Location].[Sub Location]"));
                    // dimMtrlW.push(cUtil.fn_qDim(row, "[Trans Mode].[Trans Mode]"));
                    // dimMtrlW.push(cUtil.fn_qDim(row, "[Item Material].[Item Material]"));
                    // dimMtrlW.push(Horizon);

                    //-------------------------------------------------------------------------------------
                    // 시나리오 버전 Copy ( fbVersion => toVersion (CWP_MP) 로 copy )
                    // 각 MG 의 시나리오 버전 데이터가 없는 경우 copy 안됨
                    //-------------------------------------------------------------------------------------
                    let query = 'UpdateScenario( '
                    + toVersion         // To 버전
                    + ',' + "[Version].[Version Name].["+fbVersion+"]"   // 시나리오 버전(from 버전)
                    + ',false'
                    + ',for model [BOD List Mtrl] using scope (' + dimMtrl.join('*') + ')'
                    + ',for model [BOD List Mtrl W] using scope (' + dimMtrlW.join('*') + ')'
                    + ',for model [BOD Item Mtrl] using scope (' + dimMtrl.join('*') + ')'
                    + ',for model [BOD Item Mtrl W] using scope (' + dimMtrlW.join('*') + ')'
                    +'); ';

                    cLib.debug("UpdateScenario >> "+query);
                    queryModule.update(query);

                    //-------------------------------------------------------------------------------------
                    // BOD List Mtrl : 사용자 Update > 시나리오 버전 Data 가 존재할 때만 update
                    //-------------------------------------------------------------------------------------
                    let dimMtrlChk = [...dimMtrl];
                    dimMtrlChk.push("[Version].[Version Name].["+fbVersion+"]"); // 시나리오 버전
                    if( cLib.existMeasure(dimMtrlChk, ["Measure.[BOD List Mtrl_Created Time]","Measure.[BOD List Mtrl_Updated Time]"], "") ){

                        dimMtrl.push(toVersion);

                        let measure = [];
                        measure.push(cLib.fn_mergeUser("Measure.[BOD List Mtrl_Updated By]", fbVersion));
                        measure.push(cUtil.fn_qMeaUpdateTime("Measure.[BOD List Mtrl_Updated Time]"));
                        cLib.updateMeasure(dimMtrl, measure);
                    }

                    //-------------------------------------------------------------------------------------
                    // BOD List Mtrl W : 사용자 Update > Measure 없어서 skip
                    //-------------------------------------------------------------------------------------
                }
            }

            cLib.programEnd();

            //  정상 저장 후 리턴
            return { "Code" : 0, "Msg" : "It was saved successfully." };

        } catch ( e ) {
            cLib.error(e.message);
            return { "Code" : -1, "Msg" : e.message };
        }
    };


    // Mapping 함수 정의, 마지막에 선언을 해야 함수를 정상적으로 인식함
    const functionMap = {
        "fn_cb_subLocation"     : fn_cb_subLocation
        ,"fn_cb_msl3"           : fn_cb_msl3
        ,"fn_cb_vendor"         : fn_cb_vendor
        ,"fn_cb_tpmode"         : fn_cb_tpmode
        ,"fn_cb_lotSize"        : fn_cb_lotSize
        ,"fn_save"              : fn_save                  // 상단 그리드 중복, validation, 저장, PY 실행
        ,"fn_saveDetail"        : fn_saveDetail     // 하단 그리드 저장
        ,"fn_merge"             : fn_merge
    };

    return {
        fn_loadFunction : fn_loadFunction
    };

});


/*--------------------------------------------------------------------------------------------------*/
/* 
    프로그램명 : o9.NSCM.JSEWMatlBOD
    화면명 : Material BOD (EW)
    Action Button : EWMatlBOD
    [history]
    2025.08.28 : syif1380.lee : Combo 생성(Plant, Lv3, Vendor(HQ) ), 저장 로직 구현
    2025.08.29 : syif1380.lee : Save시 validation 추가 : vendor(HQ) : GT Code 가 Location 멤버등록이 안된 경우 체크
    2025.09.19 : syif1380.lee : Item Materil 별 Lot Size 조회 (fn_cb_lotSize), Lot Type 에 따른 세팅은 EW에서 활용
    2025.10.16 : syif1380.lee : PY_UI_MatlBODApply => PY_UI_MtrlBODItem : PY 호출 변경
    2025.10.31 : syif1380.lee : 공통소스 반영 및 BOD List Mtrl W, BOD Item Mtrl W 저장하는 공통함수 생성 (fn_measureWUpdate)
    2025.11.04 : syif1380.lee : fn_saveDetail => Measure.[BOD Item Mtrl_Lot Size] 추가 (임재민p)
    2025.11.05 : syif1380.lee : fn_qMeaUpdateUser() => fn_qMeaUpdateUserName() 로 변경
    2025.11.20 : syif1380.lee : fn_cb_vendor() 변경 : vendor HQ의 P105SP / BUSAN(HUB) => P105SP / P105SP 로 변경 (신승호P요청)
    2025.12.09 : syif1380.lee : fn_cb_vendor() 변경 : vendor HQ의 P105SP 강제 추가 부분 삭제 
                                - vendor(HQ)자리에는 GT Code 만 오게한다 (신승호P요청)
    2025.12.11 : syif1380.lee : 저장시 메저 추가
                                Measure.[BOD List Mtrl_Priority]
                                Measure.[BOD List Mtrl_Time Varying Flag]
                                Measure.[BOD Item Mtrl_Priority]
                                Measure.[BOD Item Mtrl_Time Varying Flag]
    2025.12.29 : 콤보에 filter 적용
    2026.03.03 : fn_merge() : Scenario Plan 정의
                 콤보데이터 : &CWVUI 하디코딩 -> cUtil.fn_getFilterQuery 변경
    2026.03.05 : fn_merge() : Scenario Plan 정의 -> UpdateScenario 로 변경
    2026.03.18 : fn_merge() : mergeType 추가 정의
    2026.03.26 : commonLib 선언 부분 변경 및 공통함수 이름 변경
*/
/*--------------------------------------------------------------------------------------------------*/