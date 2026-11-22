define('o9.NSCM.JSEWKDSOPCopy', ['o9/data/query', 'o9/data/cellset', 'o9.NSCM.commonLibVD'], function(){

    /*--------------------------------------------------------------------------------------------------*/
    // 프로그램명   : o9.NSCM.JSEWKDSOPCopy
    // 화면명       : KD SOP Copy (EW)
    // Action Button: EWKDSOPCopy
    // UI 개발자    : 김동수P
    // 최초생성     : 2025.08.20 / syif1380.lee
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

    const programName = "o9.NSCM.JSEWKDSOPCopy";
    const queryModule = require('o9/data/query');

    //================================================== -[Combo Data] ==========================================//
    /*------------------------------------------------------------------------------------------------------------
    From Site       > EWKDSOPCopy           >  { "fbFuncName" : "fn_cb_location", "fbParams" : {} }
    To Site         > EWKDSOPCopy           >  { "fbFuncName" : "fn_cb_subLocation", "fbParams" : { "[Location].[Location]" : "P306" } }
    ASIS Item       > EWKDSOPCopy           >  { "fbFuncName" : "fn_cb_asisItem", "fbParams" : { "[Location].[Location]":"P306","[Sub Location].[Sub Location]":"S356" } }
    TOBE Item       > EWKDSOPCopy           >  { "fbFuncName" : "fn_cb_tobeItem", "fbParams" : { "[Location].[Location]":"P306","[Sub Location].[Sub Location]":"S356" } }
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

    var fn_cb_location = function(parsedParams){
        const cLib = fn_cLib(programName + "." + arguments.callee.name);
        cLib.setLogLevel("Debug");

        try {
            cLib.debug("parsedParams.fbParams :: "+JSON.stringify(parsedParams.fbParams));
            //---------------------------- GDC Logic 2025.08.20 ----------------------------//
            //  /*ABKDSopCopyAdd-ds_fromSite_new*/
            // Select (&NSUILocationPlant ) on row
            // where {&CWVUI
            // , (Measure.[BOD Item_Cur Status] in{"PLANNED","ACTIVE","INACTIVE"})
            // , [Item].[ProductType].filter(#.Name in {"SKD","CKD"})
            // };
            //------------------------------------------------------------------------------//

            var where = 'where {'
                               +'&CWVUI'
                               +',[Item].[ProductType].filter(#.Name in {"SKD","CKD"})'
                               +',(Measure.[BOD Item_Cur Status] in {"PLANNED","ACTIVE","INACTIVE"})'
                               +'}';
            var result = cLib.selectList(["&NSUILocationPlant"],
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
            cLib.debug("parsedParams.fbParams :: "+JSON.stringify(parsedParams.fbParams));

            //---------------------------- GDC Logic 2025.08.20 ----------------------------//
            // /*ABKDSopCopyAdd-ds_toSite_new*/
            // Select (&NSUISubLocationDC ) on row
            // where {&CWVUI
            // , (Measure.[BOD Item_Cur Status] in{"PLANNED","ACTIVE","INACTIVE"})
            // , [Item].[ProductType].filter(#.Name in {"SKD","CKD"})
            // , [Location].[Location]{{#filter FromSite}}
            // };
            //------------------------------------------------------------------------------//

            let fbLocation = parsedParams.fbParams["[Location].[Location]"];

            var where = 'where {'
                               +'&CWVUI'
                               +',[Location].[Location]'+ cUtil.fn_filterStr(fbLocation)
                               +',[Item].[ProductType].filter(#.Name in {"SKD","CKD"})'
                               +',(Measure.[BOD Item_Cur Status] in {"PLANNED","ACTIVE","INACTIVE"})'
                               +'}';

            var result = cLib.selectList(["&NSUISubLocationDC"],
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

    // ASIS-Item
    var fn_cb_asisItem = function(parsedParams){
        const cLib = fn_cLib(programName + "." + arguments.callee.name);
        cLib.setLogLevel("Debug");

        try {
            cLib.debug("parsedParams.fbParams :: "+JSON.stringify(parsedParams.fbParams));

            //---------------------------- GDC Logic 2025.08.20 ----------------------------//
            // /*ABKDSopCopyAdd-ds_asis_item*/
            // Select ( [Item].[Item] 
            //     ) on row,({Measure.[BOD Item_Asn]
            //     ,Measure.[BOD Item_Cur Status]
            //     ,Measure.[BOD Item_BOD LT]}) on column 
            //     where {&CWVUI 
            //     , [Location].[Location]{{#filter FromSite}}
            //     , [Sub Location].[Sub Location]{{#filter ToSite}}
            //     , [Item].[ProductType].filter(#.Name in {"SKD","CKD"})
            //     , (Measure.[BOD Item_Cur Status] in{"PLANNED","ACTIVE","INACTIVE"}) } ;
            //------------------------------------------------------------------------------//

            let fbLocation = parsedParams.fbParams["[Location].[Location]"];
            let fbsubLocation = parsedParams.fbParams["[Sub Location].[Sub Location]"];

            var where = 'where {'
                               +'&CWVUI'
                               +',[Location].[Location]'+ cUtil.fn_filterStr(fbLocation)
                               +',[Sub Location].[Sub Location]'+ cUtil.fn_filterStr(fbsubLocation)
                               +',[Item].[ProductType].filter(#.Name in {"SKD","CKD"})'
                               +',(Measure.[BOD Item_Cur Status] in {"PLANNED","ACTIVE","INACTIVE"})'
                               +'}';

            var result = cLib.selectList(["[Item].[Item]"],
                                             [],
                                             where,
                                             "",
                                             "");
            cLib.printCsData(result, 3);

            var comboList = cLib.fn_makeCombo(result, {DimName : "Item", DimAttbName : "Item", Sort : "DisplayName", existAll : false, isDisplayNameWithCode : false});
            cLib.debug("ComboData : " + JSON.stringify(comboList));

            cLib.programEnd();

            return { "Code" : 0, "Msg" : "", "Rows" : comboList };
        } catch ( e ) {
            cLib.error(e.message);
            return { "Code" : -1, "Msg" : e.message };
        }
    };

    // TOBE-Item
    var fn_cb_tobeItem = function(parsedParams){
        const cLib = fn_cLib(programName + "." + arguments.callee.name);
        cLib.setLogLevel("Debug");

        try {
            cLib.debug("parsedParams.fbParams :: "+JSON.stringify(parsedParams.fbParams));

            //---------------------------- GDC Logic 2025.08.20 ----------------------------//
            // /*ABKDSopCopyAdd-ds_tobe_item*/
            // Select ( [Item].[Item] 
            //     ) on row,({Measure.[BOD Item_Asn]
            //     ,Measure.[BOD Item_Cur Status]
            //     ,Measure.[BOD Item_BOD LT]}) on column 
            //     where {&CWVUI 
            //     , [Location].[Location]{{#filter FromSite}}
            //     , [Sub Location].[Sub Location]{{#filter ToSite}}
            //     , [Item].[ProductType].filter(#.Name in {"SKD","CKD","CRT"})
            //     , (Measure.[BOD Item_Cur Status] in{"PLANNED","ACTIVE","INACTIVE"}) } ;
            //------------------------------------------------------------------------------//

            let fbLocation = parsedParams.fbParams["[Location].[Location]"];
            let fbsubLocation = parsedParams.fbParams["[Sub Location].[Sub Location]"];

            var where = 'where {'
                               +'&CWVUI'
                               +',[Location].[Location]'+ cUtil.fn_filterStr(fbLocation)
                               +',[Sub Location].[Sub Location]'+ cUtil.fn_filterStr(fbsubLocation)
                               +',[Item].[ProductType].filter(#.Name in {"SKD","CKD","CRT"})'
                               +',(Measure.[BOD Item_Cur Status] in {"PLANNED","ACTIVE","INACTIVE"})'
                               +'}';

            var result = cLib.selectList(["[Item].[Item]"],
                                             [],
                                             where,
                                             "",
                                             "");
            cLib.printCsData(result, 3);

            var comboList = cLib.fn_makeCombo(result, {DimName : "Item", DimAttbName : "Item", Sort : "DisplayName", existAll : false, isDisplayNameWithCode : false});
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
            cLib.debug("parsedParams.fbGridRows :: "+JSON.stringify(parsedParams.fbGridRows));

            let measureCheck = ["Measure.[KD SOP Copy_Valid]", "Measure.[KD SOP Copy_Desc]"
                              , "Measure.[KD SOP Copy_Created By]", "Measure.[KD SOP Copy_Creation Time]"
                              ," Measure.[KD SOP Copy_Updated By]", "Measure.[KD SOP Copy_Update Time] "];

            errorRowData = [];
            errorRowGrid = [];
            errorMsg = "This is registerd data.";

            for ( var i=0; i<parsedParams.fbGridRows.length; i++){
                let row = parsedParams.fbGridRows[i];
                let rowstatus = row["rowstatus"];
                let rowindex = row["rowindex"];
                row["rowmsg"] = null;

                // 기존 data 중복여부에 대한 체크
                if( rowstatus == "C") {

                    let dimension = [];
                    dimension.push(cUtil.fn_qDimVersionName(parsedParams));
                    dimension.push(cUtil.fn_qDim(row, "[Location].[Location]"));
                    dimension.push(cUtil.fn_qDim(row, "[Sub Location].[Sub Location]"));
                    dimension.push(cUtil.fn_qDim(row, "[Item].[Item]"));
                    dimension.push(cUtil.fn_qDim(row, "[To Item].[To Item]"));
                    
                    // 중복 체크 
                    if ( cLib.existMeasure(dimension, measureCheck, "")){
                        errorRowData.push(rowindex+"^"+errorMsg);
                        errorRowGrid.push(row);
                        // return { "Code" : 1, "Msg" : ["1^This is registerd data."]};
                    }
                }

            } // end for

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
            cLib.debug("fn_save ==========================================================>");
            cLib.debug("parsedParams.fbGridRows :: "+JSON.stringify(parsedParams.fbGridRows));

            let measureCheck = ["Measure.[KD SOP Copy_Valid]", "Measure.[KD SOP Copy_Desc]"
                              , "Measure.[KD SOP Copy_Created By]", "Measure.[KD SOP Copy_Creation Time]"
                              ," Measure.[KD SOP Copy_Updated By]", "Measure.[KD SOP Copy_Update Time] "];

            for ( var i=0; i<parsedParams.fbGridRows.length; i++){

                let row = parsedParams.fbGridRows[i];
                let rowstatus = row["rowstatus"];

                let dimension = [];
                dimension.push(cUtil.fn_qDimVersionName(parsedParams));
                dimension.push(cUtil.fn_qDim(row, "[Location].[Location]"));
                dimension.push(cUtil.fn_qDim(row, "[Sub Location].[Sub Location]"));
                dimension.push(cUtil.fn_qDim(row, "[Item].[Item]"));
                dimension.push(cUtil.fn_qDim(row, "[To Item].[To Item]"));

                let updateMeasure = [];
                updateMeasure.push(cUtil.fn_qMeaStr(row, "Measure.[KD SOP Copy_Valid]"));
                updateMeasure.push(cUtil.fn_qMeaStr(row, "Measure.[KD SOP Copy_Desc]"));
                updateMeasure.push(cUtil.fn_qMeaUpdateTime("Measure.[KD SOP Copy_Update Time]"));
                updateMeasure.push(cUtil.fn_qMeaUpdateUserName("Measure.[KD SOP Copy_Updated By]"));

                // 기존 data 중복여부에 대한 체크
                if( rowstatus == "C") {
                    // 기존 data 중복여부에 대한 체크
                    if ( !cLib.existMeasure(dimension, measureCheck, ""))
                    {
                        cLib.createMeasure(dimension, [cUtil.fn_qMeaStr(row, "Measure.[KD SOP Copy_Valid]")]);

                        updateMeasure.push(cUtil.fn_qMeaUpdateTime("Measure.[KD SOP Copy_Creation Time]"));
                        updateMeasure.push(cUtil.fn_qMeaUpdateUserName("Measure.[KD SOP Copy_Created By]"));
                        cLib.updateBlockMeasure(dimension, updateMeasure);
                    }
                } else if( rowstatus == "U") {
                    cLib.updateBlockMeasure(dimension, updateMeasure);

                } else if( rowstatus == "D") {
                    cLib.deleteMeasure(dimension, "KD SOP Copy");
                }

            } // end for

            cLib.programEnd();

        } catch ( e ) {
            cLib.error(e.message);
            return { "Code" : -1, "Msg" : e.message };
        }
    };

    // Mapping 함수 정의, 마지막에 선언을 해야 함수를 정상적으로 인식함
    const functionMap = {
        "fn_cb_location"        : fn_cb_location
       ,"fn_cb_subLocation"     : fn_cb_subLocation
       ,"fn_cb_asisItem"        : fn_cb_asisItem
       ,"fn_cb_tobeItem"        : fn_cb_tobeItem
       ,"fn_savePostProcess"    : fn_savePostProcess
    };

    return {
        fn_loadFunction : fn_loadFunction
    };

});

/*--------------------------------------------------------------------------------------------------*/
/* 프로그램명 : o9.NSCM.JSEWKDSOPCopy
   화면명 : KD SOP Copy (EW)
   Action Button : EWKDSOPCopy
   [history]
   2025.08.21 : fn_savePostProcess 추가 (중복 validation 체크)
   2025.08.21 : fn_save 삭제 : data 저장은 EW 에서
   2025.08.22 : fn_save : EW에서 add, delete 사용 안됨, rowstatus=C/U/D 통합 로직
   2025.11.05 : syif1380.lee : 공통소스 반영 및 로직 정리
   2025.11.05 : syif1380.lee : n_qMeaUpdateUser() => fn_qMeaUpdateUserName() 로 변경
   2026.03.26 : commonLib 선언 부분 변경 및 공통함수 이름 변경
*/
/*--------------------------------------------------------------------------------------------------*/