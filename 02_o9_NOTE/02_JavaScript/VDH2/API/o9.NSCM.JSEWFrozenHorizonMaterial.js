define('o9.NSCM.JSEWFrozenHorizonMaterial', ['o9/data/query', 'o9/data/cellset', 'o9.NSCM.commonLibVD'], function(){

    /*--------------------------------------------------------------------------------------------------*/
    // 프로그램명 : o9.NSCM.JSEWFrozenHorizonMaterial
    // 화면명 : Frozen Horizon (Material) (EW)
    // Action Button : EWFrozenHorizonMaterial
    // UI 개발자 : 권슬기P
    // 최초생성 : 2025.09.04 / syif1380.lee
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

    const programName = "o9.NSCM.JSEWFrozenHorizonMaterial";
    const queryModule = require('o9/data/query');
    const Horizon = "&Last8WeeksAndNextWeek";   // "&MDMHorizon";

    //================================================== -[Combo Data] ==========================================//
    /*------------------------------------------------------------------------------------------------------------
    Lv5             > EWFrozenHorizonMaterial           >  { "fbFuncName" : "fn_msl5", "fbParams" : {"[Item Material].[MSL3]":"Panel>EB Panel>EB OpenCell"} }
    Material        > EWFrozenHorizonMaterial           >  { "fbFuncName" : "fn_cb_itemMaterial", "fbParams" : { "[Item Material].[MSL5]" : "Panel>EB Panel>EB OpenCell>30~39>32" } }
    From Site       > EWFrozenHorizonMaterial           >  { "fbFuncName" : "fn_cb_location", "fbParams" : { "[Item Material].[Item Material]":"BN96-52421A" } }
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

    /**
     * 중단 그리드의 Lv1 콤보 (Single 선택) - 2026.02.04 추가 요청 (신승호P)
     * [Item Material].[MSL1].[Panel]
     * @param {*} parsedParams 
     * @returns 
     */
    var fn_msl1 = function(parsedParams){
        const cLib = fn_cLib(programName + "." + arguments.callee.name);
        cLib.setLogLevel("Debug");

        try {
            cLib.printParams(parsedParams);

            var result = cLib.selectList(["&NSUIMtrlMSL1Panel"],
                                             [],
                                             "",
                                             "",
                                             "");

            cLib.printCsData(result, 3);

            var comboList = cLib.fn_makeCombo(result, {DimName : "Item Material", DimAttbName : "MSL1", Sort : "DisplayName", existAll : false, isDisplayNameWithCode : false});
            cLib.debug("ComboData : " + JSON.stringify(comboList));

            cLib.programEnd();

            return { "Code" : 0, "Msg" : "", "Rows" : comboList };
        } catch ( e ) {
            cLib.error(e.message);
            return { "Code" : -1, "Msg" : e.message };
        }
    };

    /**
     * 중단 그리드의 Lv2 콤보 (Single 선택) - 2026.02.04 추가 요청 (신승호P)
     * 
     * @param {*} parsedParams 
     * @returns 
     */
    var fn_msl2 = function(parsedParams){
        const cLib = fn_cLib(programName + "." + arguments.callee.name);
        cLib.setLogLevel("Debug");

        try {
            cLib.printParams(parsedParams);

            let fbMSL1 = parsedParams.fbParams["[Item Material].[MSL1]"];

            let where = 'where {'
                        +' &NSUIMtrlMSL1View'+ cUtil.fn_filterStr(fbMSL1)
                        + '} ';

            var result = cLib.selectList(["&NSUIMtrlMSL2View"],
                                             [],
                                             where,
                                             "",
                                             "");

            cLib.printCsData(result, 3);

            var comboList = cLib.fn_makeCombo(result, {DimName : "Item Material", DimAttbName : "MSL2", Sort : "DisplayName", existAll : false, isDisplayNameWithCode : false});
            cLib.debug("ComboData : " + JSON.stringify(comboList));

            cLib.programEnd();

            return { "Code" : 0, "Msg" : "", "Rows" : comboList };
        } catch ( e ) {
            cLib.error(e.message);
            return { "Code" : -1, "Msg" : e.message };
        }
    };

    /**
     * 중단 그리드의 Lv3 콤보 (Single 선택) - 2026.02.04 추가 요청 (신승호P)
     * Lv1~Lv3 을 파라메타로 받음
     * @param {*} parsedParams 
     * @returns 
     */
    var fn_msl3 = function(parsedParams){
        const cLib = fn_cLib(programName + "." + arguments.callee.name);
        cLib.setLogLevel("Debug");

        try {
            cLib.printParams(parsedParams);

            let fbMSL1 = parsedParams.fbParams["[Item Material].[MSL1]"];
            let fbMSL2 = parsedParams.fbParams["[Item Material].[MSL2]"];

            let where = 'where {'
                        +' &NSUIMtrlMSL1View'+ cUtil.fn_filterStr(fbMSL1)
                        +',&NSUIMtrlMSL2View'+ cUtil.fn_filterStr(fbMSL2)
                        + '} ';

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

    /**
     * 중단 그리드의 Lv4 콤보 (Single 선택) - 2026.02.04 추가 요청 (신승호P)
     * Lv1~Lv3 을 파라메타로 받음
     * @param {*} parsedParams 
     * @returns 
     */
    var fn_msl4 = function(parsedParams){
        const cLib = fn_cLib(programName + "." + arguments.callee.name);
        cLib.setLogLevel("Debug");

        try {
            cLib.printParams(parsedParams);

            let fbMSL1 = parsedParams.fbParams["[Item Material].[MSL1]"];
            let fbMSL2 = parsedParams.fbParams["[Item Material].[MSL2]"];
            let fbMSL3 = parsedParams.fbParams["[Item Material].[MSL3]"];

            let where = 'where {'
                        +' &NSUIMtrlMSL1View'+ cUtil.fn_filterStr(fbMSL1)
                        +',&NSUIMtrlMSL2View'+ cUtil.fn_filterStr(fbMSL2)
                        +',&NSUIMtrlMSL3View'+ cUtil.fn_filterStr(fbMSL3)
                        + '} ';

            var result = cLib.selectList(["&NSUIMtrlMSL4View"],
                                             [],
                                             where,
                                             "",
                                             "");

            cLib.printCsData(result, 3);

            var comboList = cLib.fn_makeCombo(result, {DimName : "Item Material", DimAttbName : "MSL4", Sort : "DisplayName", existAll : false, isDisplayNameWithCode : false});
            cLib.debug("ComboData : " + JSON.stringify(comboList));

            cLib.programEnd();

            return { "Code" : 0, "Msg" : "", "Rows" : comboList };
        } catch ( e ) {
            cLib.error(e.message);
            return { "Code" : -1, "Msg" : e.message };
        }
    };


    /**
     * 중단 그리드의 Lv5 콤보 (Multi 선택 가능)
     * @param {*} parsedParams 
     * @returns 
     */
    var fn_msl5 = function(parsedParams){
        const cLib = fn_cLib(programName + "." + arguments.callee.name);
        cLib.setLogLevel("Debug");

        try {
            cLib.printParams(parsedParams);
            let fbMSL3 = parsedParams.fbParams["[Item Material].[MSL3]"];
            let fbMSL4 = (parsedParams.fbParams["[Item Material].[MSL4]"]) ? parsedParams.fbParams["[Item Material].[MSL4]"] : "";   // 추가 2025.09.10

            // var result = cLib.selectList(["&NSUIMtrlMSL3View"+cUtil.fn_filterStr(fbMSL3), "&NSUIMtrlMSL5View"],
            //                                  [],
            //                                  "",
            //                                  "",
            //                                  "");

            // // Supply Frozen Mtrl L5 에 등록되지 않은 MSL5 만 보여주기. 2025.09.10 (신승호p 요청)
            // let where = 'include nulls '
            //             +'where { &CWVUI, &NSUIMtrlMSL3View' + cUtil.fn_filterStr(fbMSL3) 
            //             +', &NSUIMtrlMSL4View' + cUtil.fn_filterStr(fbMSL4)
            //             + ' }.filter(isnull(Measure.[Supply Frozen Mtrl L5_Updated By]))';
            // var result = cLib.selectList(["&NSUIMtrlMSL5View"],
            //                                 ["Measure.[Supply Frozen Mtrl L5_Updated By]"],
            //                                 where,
            //                                 "",
            //                                 "");

            // Dimension 내용으로 변경 2026.02.10 (신승호p 요청)
            // let where = 'where { &CWVUI, &NSUIMtrlMSL3View' + cUtil.fn_filterStr(fbMSL3) 
            let where = 'where { '+cUtil.fn_getFilterQuery(parsedParams, "[Version].[Version Name]")
                        +', &NSUIMtrlMSL3View' + cUtil.fn_filterStr(fbMSL3) 
                        +', &NSUIMtrlMSL4View' + cUtil.fn_filterStr(fbMSL4)
                        + ' } ';
            var result = cLib.selectList(["&NSUIMtrlMSL5View"], [], where, "", "");

            cLib.printCsData(result, 3);

            var comboList = cLib.fn_makeCombo(result, {DimName : "Item Material", DimAttbName : "MSL5", Sort : "DisplayName", existAll : false, isDisplayNameWithCode : false});
            cLib.debug("ComboData : " + JSON.stringify(comboList));

            cLib.programEnd();

            return { "Code" : 0, "Msg" : "", "Rows" : comboList };
        } catch ( e ) {
            cLib.error(e.message);
            return { "Code" : -1, "Msg" : e.message };
        }
    };

    // 
    var fn_cb_itemMaterial = function(parsedParams){
        const cLib = fn_cLib(programName + "." + arguments.callee.name);
        cLib.setLogLevel("Debug");

        try {
            cLib.printParams(parsedParams);

            let fbMSL5 = parsedParams.fbParams["[Item Material].[MSL5]"];

            var result = cLib.selectList(["[Item Material].[MSL5]"+cUtil.fn_filterStr(fbMSL5), "[Item Material].[Item Material]", "[Item Material].[C02]"],
                                             [],
                                             "",
                                             "",
                                             "");
            cLib.printCsData(result, 3);

            // var comboList = cLib.fn_makeCombo(result, {DimName : "Item Material", DimAttbName : "Item Material", Sort : "DisplayName", existAll : false, isDisplayNameWithCode : false});

            //==========================================================
            var comboList = [];
            for (i = 0; i < result.cs.rowCount; i++) {
                let nameValue1 = result.cs.row(i).cell(result.cs.memberColumnIndex("Item Material","Item Material")).Name;
                let displayName1 = result.cs.row(i).cell(result.cs.memberColumnIndex("Item Material","Item Material")).DisplayName;

                let nameValue2 = result.cs.row(i).cell(result.cs.memberColumnIndex("Item Material","C02")).Name;
                let displayName2 = result.cs.row(i).cell(result.cs.memberColumnIndex("Item Material","C02")).DisplayName;

                comboList.push({ Name: nameValue1, DisplayName: displayName1, Name2: nameValue2, DisplayName2: displayName2});
            }
            //==========================================================
            cLib.debug("ComboData : " + JSON.stringify(comboList));

            cLib.programEnd();

            return { "Code" : 0, "Msg" : "", "Rows" : comboList };
        } catch ( e ) {
            cLib.error(e.message);
            return { "Code" : -1, "Msg" : e.message };
        }
    };

    // From Site
    var fn_cb_location = function(parsedParams){
        const cLib = fn_cLib(programName + "." + arguments.callee.name);
        cLib.setLogLevel("Debug");

        try {
            cLib.printParams(parsedParams);

            let fbItemMaterial = parsedParams.fbParams["[Item Material].[Item Material]"];

            // `Select ([Location].[Location] * &CWVUI * [Item Material].[Item Material].[`+ Item +`] * [Vendor].[Vendor] * [Global Top].[GT Code] * [Partner Vendor].[Partner Vendor] ) on row, ({Measure.[Vendor Mtrl_GT Name]}) on column;`;
            // var sql = 'Select ( [Location].[Location] * &CWVUI * [Item Material].[Item Material]' + cUtil.fn_filterStr(fbItemMaterial)
            var sql = 'Select ( [Location].[Location] '
                      +' * ' + cUtil.fn_getFilterQuery(parsedParams, "[Version].[Version Name]")
                      +' * [Item Material].[Item Material]' + cUtil.fn_filterStr(fbItemMaterial)
                      +' * [Vendor].[Vendor] * [Global Top].[GT Code] * [Partner Vendor].[Partner Vendor]'
                      +') on row, ({Measure.[Vendor Mtrl_GT Name]}) on column;';

            var result = cLib.selectQueryList("GTCode",sql);
            cLib.printCsData(result, 3);

            var comboList = [];
            for (i = 0; i < result.rowCount; i++) {
                let nameValue = result.cs.row(i).cell(result.cs.memberColumnIndex("Global Top","GT Code")).Name;
                let vendorName = result.cs.row(i).cell(result.cs.measureColumnIndex("Vendor Mtrl_GT Name"));

                comboList.push({ Name: nameValue, DisplayName: vendorName });
            }

            // Add Data in the Location P105SP
            let locationDisplayName = cLib.fn_getCodeName("Location", "P105");    // P105 , SUWON(VD)
            comboList.unshift({ Name: 'P105', DisplayName: locationDisplayName })   // 첫번째 row 에 추가
            
            cLib.debug("ComboData : " + JSON.stringify(comboList));

            cLib.programEnd();

            return { "Code" : 0, "Msg" : "", "Rows" : comboList };
        } catch ( e ) {
            cLib.error(e.message);
            return { "Code" : -1, "Msg" : e.message };
        }
    };

    // fn_save : 중복 Validation 체크
    var fn_save = function(parsedParams){
        const cLib = fn_cLib(programName + "." + arguments.callee.name);
        cLib.setLogLevel("Debug");

        try {
            cLib.debug("fn_save=========================================================>");
            cLib.printParams(parsedParams);

            let gridType = parsedParams.fbParams["gridType"];   // Lv3, Lv5, Material

            if( gridType == "Lv3"){
                fn_saveLv3(parsedParams);
            }else if( gridType == "Lv5"){
                fn_saveLv5(parsedParams);
            }else if( gridType == "Material"){
                fn_saveMaterial(parsedParams);
            }

            cLib.programEnd();

            return { "Code" : 0, "Msg" : "", "Rows" : "" }; // 정상 리턴

        } catch ( e ) {
            cLib.error(e.message);
            return { "Code" : -1, "Msg" : e.message };
        }
    };

    /**
     * Frozen Horizon Material (Lv3)
     * fn_saveLv3
     * update (Add 없음)
     * 상단 그리드 (1번)
     * @param {*} o9Params 
     * @returns 
     */
    var fn_saveLv3 = function(parsedParams){
        const cLib = fn_cLib(programName + "." + arguments.callee.name);
        cLib.setLogLevel("Debug");

        try {
            cLib.debug("fn_saveLv3 ==========================================================>");
            cLib.printParams(parsedParams);

            for ( var i=0; i<parsedParams.fbGridRows.length; i++){
                let row = parsedParams.fbGridRows[i];
                rowstatus = row["rowstatus"];
                row["rowmsg"] = null;

                let dimension = [];
                dimension.push(cUtil.fn_qDimVersionName(parsedParams));
                dimension.push(cUtil.fn_qDim(row, "[Item Material].[MSL3]"));

                if ( rowstatus == "U" ){

                    //=============================================================================//
                    // Supply Frozen Mtrl L3 MDP update
                    //=============================================================================//
                    // MDP 날짜 Update
                    cLib.updateMeasure(dimension, [cUtil.fn_qMeaUpdateTime("Measure.[Supply Frozen Mtrl L3_Update Time]")
                                                      ,cUtil.fn_qMeaUpdateUserName("Measure.[Supply Frozen Mtrl L3_Updated By]")]);

                    //=============================================================================//
                    // Supply Frozen Mtrl L3 W 주차 update
                    //=============================================================================//
                    fn_measureWUpdate(row, dimension, "Supply Frozen Mtrl L3 W");

                }

            } // end for

        } catch ( e ) {
            cLib.error(e.message);
            return { "Code" : -1, "Msg" : e.message };
        }
    };

    /**
     * 주차별 Update ( Supply Frozen Mtrl L3 W , Supply Frozen Mtrl L5 W) ================> 수정 중..11/03
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
            let measureCreate = [];

            // Measure.[Supply Frozen Mtrl L3 W_Fix Range]      // integer
            // Measure.[Supply Frozen Mtrl L3 W_IsRelativeWeek] // Boolean

            if( measureGroup == "Supply Frozen Mtrl L3 W"){
                measureList = ["Measure.[Supply Frozen Mtrl L3 W_Fix Range]", "Measure.[Supply Frozen Mtrl L3 W_IsRelativeWeek]"];
                measureCheck = ["Measure.[Supply Frozen Mtrl L3 W_Fix Range]", "Measure.[Supply Frozen Mtrl L3 W_IsRelativeWeek]"];
                measureCreate.push("Measure.[Supply Frozen Mtrl L3 W_Fix Range] = null;");
                measureCreate.push("Measure.[Supply Frozen Mtrl L3 W_IsRelativeWeek] = null;");
            }else if( measureGroup == "Supply Frozen Mtrl L5 W"){
                measureList = ["Measure.[Supply Frozen Mtrl L5 W_Fix Range]", "Measure.[Supply Frozen Mtrl L5 W_IsRelativeWeek]"];
                measureCheck = ["Measure.[Supply Frozen Mtrl L5 W_Fix Range]", "Measure.[Supply Frozen Mtrl L5 W_IsRelativeWeek]"];
                measureCreate.push("Measure.[Supply Frozen Mtrl L5 W_Fix Range] = null;");
                measureCreate.push("Measure.[Supply Frozen Mtrl L5 W_IsRelativeWeek] = null;");
            }else if( measureGroup == "Supply Frozen Mtrl Item W"){
                measureList = ["Measure.[Supply Frozen Mtrl Item W_Fix Range]","Measure.[Supply Frozen Mtrl Item W_IsRelativeWeek]"];
                measureCheck = ["Measure.[Supply Frozen Mtrl Item W_Fix Range]","Measure.[Supply Frozen Mtrl Item W_IsRelativeWeek]"];
                measureCreate.push("Measure.[Supply Frozen Mtrl Item W_Fix Range] = null;");
                measureCreate.push("Measure.[Supply Frozen Mtrl Item W_IsRelativeWeek] = null;");
            }

            let dimWeek1 = [];
            for ( var i=0; i < measureList.length; i++){

                let measureName = measureList[i]; // measure 명
                let measureValueArray = row[measureName]; // measure value ["202508^10","202509^20","202510^30"]

                cLib.debug("measureValueArray >> " + measureValueArray);

                // W 주차 정보가 없을 경우 강제로 Grain 생성 // 추가 2026.03.04 신승호p 요청
                // 화면에서 리플래시 후 주차 정보 다시 저장
                if( measureValueArray.length == 0 ){
                    dimWeek1 = [...dimension];
                    dimWeek1.push(Horizon);
                    cLib.createMeasure(dimWeek1, measureCreate);
                }

                if( measureValueArray !== null && measureValueArray !== undefined ){
                    for ( var k=0; k < measureValueArray.length; k++){
                        let weekValue = measureValueArray[k].split("^"); // "202508^1" > weekValue[0] => 주차(202508), weekValue[1] =>주차값(10)
                        dimWeek1 = [];
                        dimWeek1 = [...dimension];
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

    /**
     * Frozen Horizon Material (Lv5)
     * fn_saveLv5
     * Add / update
     * 중단 그리드 (2번)
     * @param {*} o9Params 
     * @returns 
     */
    var fn_saveLv5 = function(parsedParams){
        const cLib = fn_cLib(programName + "." + arguments.callee.name);
        cLib.setLogLevel("Debug");

        try {
            cLib.debug("fn_saveLv5 ==========================================================>");
            cLib.printParams(parsedParams);

            let measureMdp = ["Measure.[Supply Frozen Mtrl L5_Valid]", "Measure.[Supply Frozen Mtrl L5_Update Time]", "Measure.[Supply Frozen Mtrl L5_Updated By]"];

            for ( var i=0; i<parsedParams.fbGridRows.length; i++){
                let row = parsedParams.fbGridRows[i];
                let rowstatus = row["rowstatus"];
                row["rowmsg"] = null;

                let dimension = [];
                dimension.push(cUtil.fn_qDimVersionName(parsedParams));
                dimension.push(cUtil.fn_qDim(row, "[Item Material].[MSL5]"));
                
                let updateMeasure = [cUtil.fn_qMeaUpdateTime("Measure.[Supply Frozen Mtrl L5_Update Time]")
                                    ,cUtil.fn_qMeaUpdateUserName("Measure.[Supply Frozen Mtrl L5_Updated By]")];
                
                //=============================================================================//
                // Supply Frozen Mtrl L5 MDP 생성, update
                //=============================================================================//
                // 기존 data 중복여부에 대한 체크
                if( rowstatus == "C") {
                    // MDP data 중복여부에 대한 체크
                    if ( !cLib.existMeasure(dimension, measureMdp, ""))
                    {
                        cLib.createMeasure(dimension, [cUtil.fn_qMeaStr(row, "Measure.[Supply Frozen Mtrl L5_Valid]")]);
                        cLib.updateMeasure(dimension, updateMeasure);
                    }else{
                        updateMeasure.push(cUtil.fn_qMeaStr(row, "Measure.[Supply Frozen Mtrl L5_Valid]"));
                        cLib.updateMeasure(dimension, updateMeasure);
                    }
                }else{
                    updateMeasure.push(cUtil.fn_qMeaStr(row, "Measure.[Supply Frozen Mtrl L5_Valid]"));
                    cLib.updateMeasure(dimension, updateMeasure);
                }

                //=============================================================================//
                // Supply Frozen Mtrl L5 W 주차 update
                //=============================================================================//
                fn_measureWUpdate(row, dimension, "Supply Frozen Mtrl L5 W");

            } // end for

        } catch ( e ) {
            cLib.error(e.message);
            return { "Code" : -1, "Msg" : e.message };
        }
    };

    /**
     * Frozen Horizon Material (Item)
     * fn_saveMaterial
     * Add / update
     * 하단단 그리드 (3번)
     * @param {*} o9Params 
     * @returns 
     */
    var fn_saveMaterial = function(parsedParams){
        const cLib = fn_cLib(programName + "." + arguments.callee.name);
        cLib.setLogLevel("Debug");

        try {
            cLib.debug("fn_saveMaterial ==========================================================>");
            cLib.printParams(parsedParams);

            let measureMdp = ["Measure.[Supply Frozen Mtrl Item_Valid]", "Measure.[Supply Frozen Mtrl Item_Update Time]", "Measure.[Supply Frozen Mtrl Item_Updated By]"];

            for ( var i=0; i<parsedParams.fbGridRows.length; i++){

                let row = parsedParams.fbGridRows[i];
                let rowstatus = row["rowstatus"];
                row["rowmsg"] = null;

                let dimension = [];
                dimension.push(cUtil.fn_qDimVersionName(parsedParams));
                dimension.push(cUtil.fn_qDim(row, "[Location].[Location]"));
                dimension.push(cUtil.fn_qDim(row, "[Item Material].[Item Material]"));

                let updateMeasure = [cUtil.fn_qMeaUpdateTime("Measure.[Supply Frozen Mtrl Item_Update Time]")
                                    ,cUtil.fn_qMeaUpdateUserName("Measure.[Supply Frozen Mtrl Item_Updated By]")];

                //=============================================================================//
                // Supply Frozen Mtrl Item MDP 생성, update
                //=============================================================================//
                // 기존 data 중복여부에 대한 체크
                if( rowstatus == "C") {
                    // MDP data 중복여부에 대한 체크
                    if ( !cLib.existMeasure(dimension, measureMdp, ""))
                    {
                        cLib.createMeasure(dimension, [cUtil.fn_qMeaStr(row, "Measure.[Supply Frozen Mtrl Item_Valid]")]);
                        cLib.updateMeasure(dimension, updateMeasure);
                    }else{
                        updateMeasure.push(cUtil.fn_qMeaStr(row, "Measure.[Supply Frozen Mtrl Item_Valid]"));
                        cLib.updateMeasure(dimension,updateMeasure);
                    }
                }else{
                    updateMeasure.push(cUtil.fn_qMeaStr(row, "Measure.[Supply Frozen Mtrl Item_Valid]"));
                    cLib.updateMeasure(dimension,updateMeasure);
                }

                //=============================================================================//
                // Supply Frozen Mtrl Item W 주차 update
                //=============================================================================//
                fn_measureWUpdate(row, dimension, "Supply Frozen Mtrl Item W");

            } // end for

        } catch ( e ) {
            cLib.error(e.message);
            return { "Code" : -1, "Msg" : e.message };
        }
    };

    /**
     * fn_merge : Scenario Plan >> 테스트 필요..
     * 2026.03.03 생성
     * @param {*} o9Params 
     * @returns 
     */
    // var fn_merge = function(parsedParams){
    //     const cLib = fn_cLib(programName + "." + arguments.callee.name);
    //     cLib.setLogLevel("Debug");

    //     try {
    //         cLib.debug("fn_merge call ==========================================================>");
    //         cLib.printParams(parsedParams);

    //         // var fbVersion = parsedParams.fbParams["[Version].[Version Name]"];  // ew에서 버전이 어떻게 넘어 오는지???
    //         var fbVersion = cUtil.fn_getFilterValue(parsedParams, "[Version].[Version Name]");  // ew에서 버전이 어떻게 넘어 오는지??? (시나리오 버전)

    //         // top, 

    //         for ( var i=0; i<parsedParams.fbGridRows.length; i++){

    //             var row = parsedParams.fbGridRows[i];

    //             //----------------------------------------------------------------------------------------------//
    //             // Supply Frozen Mtrl L3
    //             //----------------------------------------------------------------------------------------------//
    //             // dimension 정의
    //             let dimension = [];
    //             dimension.push("[Version].[Version Name].[CWV_MP]");
    //             dimension.push(cUtil.fn_qDim(row, "[Item Material].[MSL3]"));

    //             // Measure 정의
    //             let measure = [];
    //             measure.push(cLib.fn_mergeUser("Measure.[Supply Frozen Mtrl L3_Updated By]", fbVersion));
    //             measure.push(cUtil.fn_qMeaUpdateTime("Measure.[Supply Frozen Mtrl L3_Update Time]"));
    //             cLib.createMeasure(dimension, measure);

    //             //----------------------------------------------------------------------------------------------//
    //             // Supply Frozen Mtrl L3 W
    //             //----------------------------------------------------------------------------------------------//
    //             dimension = [];
    //             dimension.push("[Version].[Version Name].[CWV_MP]");
    //             dimension.push(cUtil.fn_qDim(row, "[Item Material].[MSL3]"));
    //             dimension.push(Horizon);

    //             measure = [];
    //             measure.push(cLib.fn_mergeUser("Measure.[Supply Frozen Mtrl L3_Updated By]", fbVersion));
    //             measure.push(cUtil.fn_qMeaUpdateTime("Measure.[Supply Frozen Mtrl L3_Update Time]"));
    //             cLib.createMeasure(dimension, measure);

    //             //----------------------------------------------------------------------------------------------//
    //             // Supply Frozen Mtrl L5
    //             //----------------------------------------------------------------------------------------------//
    //             dimension = [];
    //             dimension.push("[Version].[Version Name].[CWV_MP]");
    //             dimension.push(cUtil.fn_qDim(row, "[Item Material].[MSL5]"));

    //             measure = [];
    //             measure.push(cUtil.fn_qMeaForMerge("Measure.[Supply Frozen Mtrl L5_Delete]", fbVersion));
    //             measure.push(cUtil.fn_qMeaForMerge("Measure.[Supply Frozen Mtrl L5_Valid]", fbVersion));
    //             measure.push(cLib.fn_mergeUser("Measure.[Supply Frozen Mtrl L5_Updated By]", fbVersion));
    //             measure.push(cUtil.fn_qMeaUpdateTime("Measure.[Supply Frozen Mtrl L5_Update Time]"));
    //             cLib.createMeasure(dimension, measure);

    //             //----------------------------------------------------------------------------------------------//
    //             // Supply Frozen Mtrl L5 W
    //             //----------------------------------------------------------------------------------------------//
    //             dimension = [];
    //             dimension.push("[Version].[Version Name].[CWV_MP]");
    //             dimension.push(cUtil.fn_qDim(row, "[Item Material].[MSL5]"));
    //             dimension.push(Horizon);

    //             measure = [];
    //             measure.push(cUtil.fn_qMeaForMerge("Measure.[Supply Frozen Mtrl L5 W_Fix Range]", fbVersion));
    //             measure.push(cUtil.fn_qMeaForMerge("Measure.[Supply Frozen Mtrl L5 W_IsRelativeWeek]", fbVersion));
    //             cLib.createMeasure(dimension, measure);

    //             //----------------------------------------------------------------------------------------------//
    //             // Supply Frozen Mtrl Item
    //             //----------------------------------------------------------------------------------------------//
    //             dimension = [];
    //             dimension.push("[Version].[Version Name].[CWV_MP]");
    //             dimension.push(cUtil.fn_qDim(row, "[Location].[Location]"));
    //             dimension.push(cUtil.fn_qDim(row, "[Item Material].[Item Material].[Item Material]"));

    //             measure = [];
    //             measure.push(cUtil.fn_qMeaForMerge("Measure.[Supply Frozen Mtrl Item_Delete]", fbVersion));
    //             measure.push(cUtil.fn_qMeaForMerge("Measure.[Supply Frozen Mtrl Item_Valid]", fbVersion));
    //             measure.push(cLib.fn_mergeUser("Measure.[Supply Frozen Mtrl Item_Updated By]", fbVersion));
    //             measure.push(cUtil.fn_qMeaUpdateTime("Measure.[Supply Frozen Mtrl Item_Update Time]"));
    //             cLib.createMeasure(dimension, measure);

    //             //----------------------------------------------------------------------------------------------//
    //             // Supply Frozen Mtrl Item W
    //             //----------------------------------------------------------------------------------------------//
    //             dimension = [];
    //             dimension.push("[Version].[Version Name].[CWV_MP]");
    //             dimension.push(cUtil.fn_qDim(row, "[Location].[Location]"));
    //             dimension.push(cUtil.fn_qDim(row, "[Item Material].[Item Material].[Item Material]"));
    //             dimension.push(Horizon);

    //             measure = [];
    //             measure.push(cUtil.fn_qMeaForMerge("Measure.[Supply Frozen Mtrl Item W_Fix Range]", fbVersion));
    //             measure.push(cUtil.fn_qMeaForMerge("Measure.[Supply Frozen Mtrl Item W_IsRelativeWeek]", fbVersion));
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

    /**
     * fn_merge : Scenario Plan >> 테스트 필요..
     * 2026.03.05 생성
     * @param {*} parsedParams 
     * @returns 
     */
    // { "fbFuncName" : "fn_merge"
    // ,"fbParams" : { "commitType" : "1", "grid" : "Lv3"
    // ,"filters" : { "[Version].[Version Name]" : {"SelectedMembers" : ["202605_P_WI_01"], "MemberFilter" : ""} }
    // }
    // ,"fbGridRows" : [
    // { "rowstatus":"C","[Location].[Location]":"P551","[Item Material].[MSL3]":"Semicon.>Semicon.>Non Memory" }
    // ] }
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
                    + ',for model [Supply Frozen Mtrl L3] '
                    + ',for model [Supply Frozen Mtrl L3 W] '
                    + ',for model [Supply Frozen Mtrl L5] '
                    + ',for model [Supply Frozen Mtrl L5 W] '
                    + ',for model [Supply Frozen Mtrl Item] '
                    + ',for model [Supply Frozen Mtrl Item W] '
                    +'); ';

                    cLib.debug("UpdateScenario >> "+query);
                    queryModule.update(query);

            }else if( parsedParams.fbParams["mergeType"] == "0"){

                //-------------------------------------------------------------------------//
                // Lv3
                //-------------------------------------------------------------------------//
                for ( var i=0; i<parsedParams.fbGridRows.lv3.length; i++){

                    var row = parsedParams.fbGridRows.lv3[i];

                    let dimLv3 = [];
                    dimLv3.push(cUtil.fn_qDim(row, "[Item Material].[MSL3]"));

                    let dimLv3W = [];
                    dimLv3W.push(cUtil.fn_qDim(row, "[Item Material].[MSL3]"));
                    dimLv3W.push(Horizon);
    
                    //-------------------------------------------------------------------------------------
                    // 시나리오 버전 Copy ( fbVersion => toVersion (CWP_MP) 로 copy )
                    // 각 MG 의 시나리오 버전 데이터가 없는 경우 copy 안됨
                    //-------------------------------------------------------------------------------------
                    let query = 'UpdateScenario( '
                    + toVersion         // To 버전
                    + ',' + "[Version].[Version Name].["+fbVersion+"]"   // 시나리오 버전(from 버전)
                    + ',false'
                    + ',for model [Supply Frozen Mtrl L3] using scope (' + dimLv3.join('*') + ')'
                    + ',for model [Supply Frozen Mtrl L3 W] using scope (' + dimLv3W.join('*') + ')'
                    +'); ';
    
                    cLib.debug("UpdateScenario >> "+query);
                    queryModule.update(query);
    
                    //-------------------------------------------------------------------------------------
                    // Supply Frozen Mtrl L3 : 사용자 Update > 시나리오 버전 Data 가 존재할 때만 update
                    //-------------------------------------------------------------------------------------
                    let dimLv3Chk = [...dimLv3];
                    dimLv3Chk.push("[Version].[Version Name].["+fbVersion+"]"); // 시나리오 버전
                    if( cLib.existMeasure(dimLv3Chk, ["Measure.[Supply Frozen Mtrl L3_Update Time]"], "") ){
    
                        dimLv3.push(toVersion);
    
                        let measure = [];
                        measure.push(cLib.fn_mergeUser("Measure.[Supply Frozen Mtrl L3_Updated By]", fbVersion));
                        measure.push(cUtil.fn_qMeaUpdateTime("Measure.[Supply Frozen Mtrl L3_Update Time]"));
                        cLib.updateMeasure(dimLv3, measure);
                    }

                    //-------------------------------------------------------------------------------------
                    // Supply Frozen Mtrl L3 W : 사용자 Update > Measure 없어서 skip
                    //-------------------------------------------------------------------------------------

                }

                //-------------------------------------------------------------------------//
                // Lv5
                //-------------------------------------------------------------------------//
                for ( var i=0; i<parsedParams.fbGridRows.lv5.length; i++){

                    var row = parsedParams.fbGridRows.lv5[i];

                    let dimLv5 = [];
                    dimLv5.push(cUtil.fn_qDim(row, "[Item Material].[MSL5]"));

                    let dimLv5W = [];
                    dimLv5W.push(cUtil.fn_qDim(row, "[Item Material].[MSL5]"));
                    dimLv5W.push(Horizon);
    
                    //-------------------------------------------------------------------------------------
                    // 시나리오 버전 Copy ( fbVersion => toVersion (CWP_MP) 로 copy )
                    // 각 MG 의 시나리오 버전 데이터가 없는 경우 copy 안됨
                    //-------------------------------------------------------------------------------------
                    let query = 'UpdateScenario( '
                    + toVersion         // To 버전
                    + ',' + "[Version].[Version Name].["+fbVersion+"]"   // 시나리오 버전(from 버전)
                    + ',false'
                    + ',for model [Supply Frozen Mtrl L5] using scope (' + dimLv5.join('*') + ')'
                    + ',for model [Supply Frozen Mtrl L5 W] using scope (' + dimLv5W.join('*') + ')'
                    +'); ';
    
                    cLib.debug("UpdateScenario >> "+query);
                    queryModule.update(query);
    
                    //-------------------------------------------------------------------------------------
                    // Supply Frozen Mtrl L5 : 사용자 Update > 시나리오 버전 Data 가 존재할 때만 update
                    //-------------------------------------------------------------------------------------
                    let dimLv5Chk = [...dimLv5];
                    dimLv5Chk.push("[Version].[Version Name].["+fbVersion+"]"); // 시나리오 버전
                    if( cLib.existMeasure(dimLv5Chk, ["Measure.[Supply Frozen Mtrl L5_Valid]","Measure.[Supply Frozen Mtrl L5_Update Time]"], "") ){
    
                        dimLv5.push(toVersion);
    
                        let measure = [];
                        measure.push(cLib.fn_mergeUser("Measure.[Supply Frozen Mtrl L5_Updated By]", fbVersion));
                        measure.push(cUtil.fn_qMeaUpdateTime("Measure.[Supply Frozen Mtrl L5_Update Time]"));
                        cLib.updateMeasure(dimLv5, measure);
                    }

                    //-------------------------------------------------------------------------------------
                    // Supply Frozen Mtrl L5 W : 사용자 Update > Measure 없어서 skip
                    //-------------------------------------------------------------------------------------
                }

                //-------------------------------------------------------------------------//
                // item
                //-------------------------------------------------------------------------//
                for ( var i=0; i<parsedParams.fbGridRows.item.length; i++){

                    var row = parsedParams.fbGridRows.item[i];

                    let dimItem = [];
                    dimItem.push(cUtil.fn_qDim(row, "[Location].[Location]"));
                    dimItem.push(cUtil.fn_qDim(row, "[Item Material].[Item Material]"));

                    let dimItemW = [];
                    dimItemW.push(cUtil.fn_qDim(row, "[Location].[Location]"));
                    dimItemW.push(cUtil.fn_qDim(row, "[Item Material].[Item Material]"));
                    dimItemW.push(Horizon);
    
                    //-------------------------------------------------------------------------------------
                    // 시나리오 버전 Copy ( fbVersion => toVersion (CWP_MP) 로 copy )
                    // 각 MG 의 시나리오 버전 데이터가 없는 경우 copy 안됨
                    //-------------------------------------------------------------------------------------
                    let query = 'UpdateScenario( '
                    + toVersion         // To 버전
                    + ',' + "[Version].[Version Name].["+fbVersion+"]"   // 시나리오 버전(from 버전)
                    + ',false'
                    + ',for model [Supply Frozen Mtrl Item] using scope (' + dimItem.join('*') + ')'
                    + ',for model [Supply Frozen Mtrl Item W] using scope (' + dimItemW.join('*') + ')'
                    +'); ';
    
                    cLib.debug("UpdateScenario >> "+query);
                    queryModule.update(query);
    
                    //-------------------------------------------------------------------------------------
                    // Supply Frozen Mtrl Item : 사용자 Update > 시나리오 버전 Data 가 존재할 때만 update
                    //-------------------------------------------------------------------------------------
                    let dimItemChk = [...dimItem];
                    dimItemChk.push("[Version].[Version Name].["+fbVersion+"]"); // 시나리오 버전
                    if( cLib.existMeasure(dimItemChk, ["Measure.[Supply Frozen Mtrl Item_Valid]","Measure.[Supply Frozen Mtrl Item_Update Time]"], "") ){
    
                        dimItem.push(toVersion);
    
                        let measure = [];
                        measure.push(cLib.fn_mergeUser("Measure.[Supply Frozen Mtrl Item_Updated By]", fbVersion));
                        measure.push(cUtil.fn_qMeaUpdateTime("Measure.[Supply Frozen Mtrl Item_Update Time]"));
                        cLib.updateMeasure(dimItem, measure);
                    }

                    //-------------------------------------------------------------------------------------
                    // Supply Frozen Mtrl Item W : 사용자 Update > Measure 없어서 skip
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
        "fn_msl1"               : fn_msl1   // 2026.01.04 추가
       ,"fn_msl2"               : fn_msl2   // 2026.01.04 추가
       ,"fn_msl3"               : fn_msl3   // 2026.01.04 추가
       ,"fn_msl4"               : fn_msl4   // 2026.01.04 추가
       ,"fn_msl5"               : fn_msl5
       ,"fn_cb_itemMaterial"    : fn_cb_itemMaterial
       ,"fn_cb_location"        : fn_cb_location
       ,"fn_save"               : fn_save
       ,"fn_merge"              : fn_merge
    };

    return {
        fn_loadFunction : fn_loadFunction
    };

});

/*--------------------------------------------------------------------------------------------------*/
/* 
    프로그램명 : o9.NSCM.JSEWFrozenHorizonMaterial
    화면명 : Frozen Horizon(Material) (EW)
    Action Button : EWFrozenHorizonMaterial
    [history]
    2025.09.10 | syif1380.lee | fn_msl5() : Supply Frozen Mtrl L5 (MG) 에 등록되지 않은 것만 조회 (신승호P요청)
    2025.09.24 | syif1380.lee | Measure 명 변경 (신승호P요청)
                                - Supply Frozen Mtrl L5_Delete   => Supply Frozen Mtrl L5_Valid
                                - Supply Frozen Mtrl Item_Delete => Supply Frozen Mtrl Item_Valid
    2025.11.05 : syif1380.lee : 공통소스 반영 및 로직 정리
    2025.11.05 : syif1380.lee : fn_qMeaUpdateUser() => fn_qMeaUpdateUserName() 로 변경
    2026.02.04 : syif1380.lee : fn_msl1 ~ fn_msl4 (콤보)추가 (신승호P요청)
    2026.02.10 : syif1380.lee : fn_msl5 (콤보)수정 :  Supply Frozen Mtrl L5 에 등록여부 상관 없이 멤버값 보이기 (msl3,msl4) (신승호P요청)
    2026.03.03 : fn_merge() : Scenario Plan 정의
                 콤보데이터 : &CWVUI 하디코딩 -> cUtil.fn_getFilterQuery 변경
    2026.03.04 : W 주차 정보가 없을 경우 강제로 Grain 생성 // 추가 2026.03.04 신승호p 요청
                 - 화면에서 리플래시 후 주차 정보 다시 저장 (주차 정보 없을 경우엔 화면에서 2번 저장 함)
    2026.03.05 : fn_merge() : Scenario Plan 정의 -> UpdateScenario 로 변경
    2026.03.19 : fn_merge() : mergeType 추가 정의
    2026.03.26 : commonLib 선언 부분 변경 및 공통함수 이름 변경
*/
/*--------------------------------------------------------------------------------------------------*/