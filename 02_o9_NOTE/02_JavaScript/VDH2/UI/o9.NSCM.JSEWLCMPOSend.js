define('o9.NSCM.JSEWLCMPOSend', ['o9/data/query', 'o9/data/cellset', 'o9.NSCM.commonLibVD'], function(){

    /*--------------------------------------------------------------------------------------------------*/
    // 프로그램명 : o9.NSCM.JSEWLCMPOSend
    // 화면명 : LCM PO Send (EW)
    // UI 설명: LCM PO Send 에 따라 ERP PO 정보 I/F 진행, 수출향 물량 PO 발행 및 관리를 위한 운영 UI
    // Action Button : EWLCMPOSend
    // 최초생성 : 2026.02.19 / syif1380.lee
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

    const programName = "o9.NSCM.JSEWLCMPOSend";
    // const Horizon = "&MPHorizon";

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
     * fn_save : 저장 => 저장 기능 없음? 2026.04.10
     * 
     * 
     * @param {*} o9Params 
     * @returns 
     */
    var fn_save = function(parsedParams){
        const cLib = fn_cLib(programName + "." + arguments.callee.name);
        cLib.setLogLevel("Debug");

        try {
            cLib.debug("parsedParams :: "+JSON.stringify(parsedParams));
            for ( var i=0; i<parsedParams.fbGridRows.length; i++){

                let row = parsedParams.fbGridRows[i];
                let rowstatus = row["rowstatus"];

                // dimension 정의
                let dimension = [];
                dimension.push(cUtil.fn_qDimVersionName(parsedParams));
                dimension.push(cUtil.fn_qDim(row, "[Location].[Location]"));
                dimension.push(cUtil.fn_qDim(row, "[To Item].[To Item]"));
                dimension.push(cUtil.fn_qDim(row, "[Item].[Item]"));
                dimension.push(cUtil.fn_qDim(row, "[Sub Location].[Sub Location]"));
                dimension.push(cUtil.fn_qDim(row, "[Trans Mode].[Trans Mode]"));
                // dimension.push(cUtil.fn_qDim(row, "[Vendor].[Vendor]"));     // 삭제 됨 2026.04.09
                dimension.push(cUtil.fn_qDim(row, "[Sequence].[Sequence]"));
                dimension.push('&Currentweek');

                let measure = [];
                measure.push(cUtil.fn_qMeaStr(row, "Measure.[LCM PO Send_Currency]"));
                measure.push(cUtil.fn_qMeaStr(row, "Measure.[LCM PO Send_DOMEXP]"));
                measure.push(cUtil.fn_qMeaStr(row, "Measure.[LCM PO Send_ETA Week]"));
                measure.push(cUtil.fn_qMeaStr(row, "Measure.[LCM PO Send_ETD Week]"));
                measure.push(cUtil.fn_qMeaStr(row, "Measure.[LCM PO Send_Incoterms1]"));
                measure.push(cUtil.fn_qMeaStr(row, "Measure.[LCM PO Send_Incoterms2]"));
                measure.push(cUtil.fn_qMeaStr(row, "Measure.[LCM PO Send_Lot Size]"));
                measure.push(cUtil.fn_qMeaStr(row, "Measure.[LCM PO Send_MFG Week]"));
                measure.push(cUtil.fn_qMeaStr(row, "Measure.[LCM PO Send_Mst Check]"));
                measure.push(cUtil.fn_qMeaStr(row, "Measure.[LCM PO Send_Org Vendor]"));
                measure.push(cUtil.fn_qMeaStr(row, "Measure.[LCM PO Send_PO Item]"));
                measure.push(cUtil.fn_qMeaStr(row, "Measure.[LCM PO Send_PO No]"));
                measure.push(cUtil.fn_qMeaStr(row, "Measure.[LCM PO Send_PO Status]"));
                measure.push(cUtil.fn_qMeaInt(row, "Measure.[LCM PO Send_POP ID]"));			// Integer
                measure.push(cUtil.fn_qMeaInt(row, "Measure.[LCM PO Send_POP Qty]"));		    // Integer
                measure.push(cUtil.fn_qMeaStr(row, "Measure.[LCM PO Send_Plant]"));
                measure.push(cUtil.fn_qMeaInt(row, "Measure.[LCM PO Send_Price]"));			    // Number
                measure.push(cUtil.fn_qMeaStr(row, "Measure.[LCM PO Send_Pur Grp]"));
                measure.push(cUtil.fn_qMeaStr(row, "Measure.[LCM PO Send_Pur Org]"));
                measure.push(cUtil.fn_qMeaStr(row, "Measure.[LCM PO Send_SLoc]"));
                measure.push(cUtil.fn_qMeaInt(row, "Measure.[LCM PO Send_SOP Qty]"));	        // Integer
                measure.push(cUtil.fn_qMeaStr(row, "Measure.[LCM PO Send_Status]"));

                // add 없음 I/F Data
                if ( rowstatus == "U" ) {
                    cLib.updateMeasure(dimension, measure);
                }

            }

            cLib.programEnd();

            return { "Code" : 0, "Msg" : "", "Rows" : ""};  // 오류 dataset Return

        } catch ( e ) {
            cLib.error(e.message);
            return { "Code" : -1, "Msg" : e.message };
        }
    };

    /**
     * fn_reload : Row 선택 상관없이 Reload 버튼 실행
     * . 순서1) LCM PO Send = "INI" 및 &Currentweek 조건의 기존 Data Delete 쿼리 실행
     * . 순서2) PY 실행 (Scope : &CWVUI) → INI 데이터 재생성
     *
     * Action Button : EWLCMPOSend
     *
     * {"fbFuncName" : "fn_reload",
     * "fbParams" : {"filters":{"[Version].[Version Name]":{"SelectedMembers":["CWV_MP"],"MemberFilter":"&CWVUI"}}}
     * }
     *
     * @param {*} o9Params
     * @returns
     */
    var fn_reload = function(parsedParams){
        const cLib = fn_cLib(programName + "." + arguments.callee.name);
        cLib.setLogLevel("Debug");

        try {
            cLib.debug("parsedParams :: "+JSON.stringify(parsedParams));
            cLib.debug("cUtil.fn_qDimVersionName:: "+cUtil.fn_qDimVersionName(parsedParams));

            // let fbVersion = cUtil.fn_getFilterValue(parsedParams, "[Version].[Version Name]");
            // cLib.debug("### filters > fbVersion : "+fbVersion);

            //--------------------------------------------------------------------------------------------------------//
            // 순서1) LCM PO Send = "INI" 및 &Currentweek 조건의 기존 Data Delete 쿼리 실행
            //--------------------------------------------------------------------------------------------------------//
            let where = [];
            where.push(cUtil.fn_qDimVersionName(parsedParams));
            where.push('&Currentweek');
            where.push('Measure.[LCM PO Send_Status] == "INI"');
            cLib.deleteMeasure(where, "LCM PO Send");

            //--------------------------------------------------------------------------------------------------------//
            // 순서2) PY 실행 (Scope : &CWVUI) → INI 데이터 재생성
            // PY 호출 : INI 재생성 :PY_UI_POProposal_LCM 현재 미개발..
            //--------------------------------------------------------------------------------------------------------//
            var execQuery = 'EXEC plugin instance [PY_UI_POProposal_LCM] for measures {[LCM PO Send_CY Flag]} '
                            +' using scope ( '
                            + cUtil.fn_qDimVersionName(parsedParams)
                            // +' [Version].[Version Name]'+cUtil.fn_filterStr(fbVersion)
                            +' ) '
                          + 'using arguments {(ExecutionMode, "MediumWeight"), ("IncludeNullRows", "False"), (paramOutVersion , "CWV_MP"), (MaxSliceTableCells, 200000000), (MaxConcurrency, 1), ([Param.o9_sys_log_level], "DEBUG")}; ';

            cLib.debug("execQuery: " + JSON.stringify(execQuery));
            cLib.executeQuery("fn_reload : PY_UI_POProposal_LCM Run", execQuery);

            cLib.programEnd();

            return { "Code" : 0, "Msg" : "", "Rows" : ""};  // 오류 dataset Return

        } catch ( e ) {
            cLib.error(e.message);
            return { "Code" : -1, "Msg" : e.message };
        }
    };

    /**
     * fn_send : Row 선택 건에 대해 Send 버튼 실행
     * Send	1. Row 선택 후 Send 가능 (Row 미지정 시 실행 불가)
     *      2. 실행 후 Measure 업데이트 필요 = "REQ"
     *
     * Action Button : EWLCMPOSend
     * // 그리드 Row 선택 넘어올 경우 처리
     * {"fbFuncName" : "fn_send",
     * "fbParams" : {"filters":{"[Version].[Version Name]":{"SelectedMembers":["CWV_MP"],"MemberFilter":"&CWVUI"}}}
     * ,"fbGridRows":[
     * {"rowstatus":""
     * ,"groupkey":"0,0,0,0,0"
     * ,"[Version].[Version Name]":"CWV_MP"
     * ,"[Location].[Location]":"P401LCD"
     * ,"[To Item].[To Item]":"-"
     * ,"[Item].[Item]":"BN95-11051A"
     * ,"[Sub Location].[Sub Location]":"P401SVC"
     * ,"[Trans Mode].[Trans Mode]":"P401SVC"
     * ,"[Sequence].[Sequence]":"1"
     * } ]
     * }
     *
     * @param {*} o9Params
     * @returns
     */
    var fn_send = function(parsedParams){
        const cLib = fn_cLib(programName + "." + arguments.callee.name);
        cLib.setLogLevel("Debug");

        try {
            cLib.debug("parsedParams :: "+JSON.stringify(parsedParams));

            let fbVersion = cUtil.fn_getFilterValue(parsedParams, "[Version].[Version Name]");
            cLib.debug("### filters > fbVersion : "+fbVersion);

            // Measure.[LCM PO Send_Status] == "INI"  ▶ "REQ" 로 변경
            for ( var i=0; i<parsedParams.fbGridRows.length; i++){

                let row = parsedParams.fbGridRows[i];
                let rowstatus = row["rowstatus"];

                // dimension 정의
                let dimension = [];
                dimension.push(cUtil.fn_qDimVersionName(parsedParams));
                dimension.push(cUtil.fn_qDim(row, "[Location].[Location]"));
                dimension.push(cUtil.fn_qDim(row, "[To Item].[To Item]"));
                dimension.push(cUtil.fn_qDim(row, "[Item].[Item]"));
                dimension.push(cUtil.fn_qDim(row, "[Sub Location].[Sub Location]"));
                dimension.push(cUtil.fn_qDim(row, "[Trans Mode].[Trans Mode]"));
                // dimension.push(cUtil.fn_qDim(row, "[Vendor].[Vendor]"));     // 삭제 됨 2026.04.09
                dimension.push(cUtil.fn_qDim(row, "[Sequence].[Sequence]"));
                dimension.push(cUtil.fn_qDim(row, "[Time].[Week]"));
                // dimension.push('&Currentweek');

                let measure = [];
                measure.push(cUtil.fn_qMeaStr(null, "Measure.[LCM PO Send_Status]", "REQ"));
                measure.push(cUtil.fn_qMeaUpdateUserName("Measure.[LCM PO Send_Updated By]"));
                measure.push(cUtil.fn_qMeaUpdateTime("Measure.[LCM PO Send_Update Time]"));

                // add 없음 I/F Data
                // if ( rowstatus == "U" ) {
                cLib.updateMeasure(dimension, measure);
                // }
            }

            cLib.programEnd();

            return { "Code" : 0, "Msg" : "", "Rows" : ""};  // 오류 dataset Return

        } catch ( e ) {
            cLib.error(e.message);
            return { "Code" : -1, "Msg" : e.message };
        }
    };

    // Mapping 함수 정의, 마지막에 선언을 해야 함수를 정상적으로 인식함
    const functionMap = {
        // "fn_save"       : fn_save // 저장 사용여부는
        "fn_reload"     : fn_reload
       ,"fn_send"       : fn_send
    };

    return {
        fn_loadFunction : fn_loadFunction
    };

});

/*--------------------------------------------------------------------------------------------------*/
/* 
    프로그램명 : o9.NSCM.JSEWLCMPOSend
    화면명 : LCM PO Send (EW)
    Action Button : EWLCMPOSend
    [history]
    2026.03.26 : commonLib 선언 부분 변경 및 공통함수 이름 변경
    2026.04.06 : fn_reload() 추가 : 명확히 정의되지 않아 추후 수정해야 함 (PY 개발 미정)
                 fn_send() 추가 : PY명 명시 되지 않음
    2026.04.09 : fn_reload() 수정 : Status == "INI" 데이터 삭제 로직 추가 후 PY 효출 (Row 단위 없고 버전 전체 호출)
    2026.04.16 : fn_reload() 수정 : PY 호출
                 fn_send() 수정 : py 호출 하지 않음, 상태값만 변경
*/