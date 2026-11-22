define('o9.NSCM.JSLCMBODListWPriority', ['o9/data/query', 'o9/data/cellset', 'o9.NSCM.commonLib'], function(){

    const programName = "o9.NSCM.JSLCMBODListWPriority";

    //-----------------------------------------------------------------------//
    // 2025.02.07 NamedSet 확인 (신승호P)
    // Location : (LCM MF, &MFStageLCMLocation)
    // Sub Location : (SET MF, &MFStageSETSubLocation)
    //-----------------------------------------------------------------------//

    /**
     * Reload Master (LCM)
     * 배치 실행 프로그램
     * @param {*} o9Params 
     * @returns 
     */
    var fn_ReloadMaster = function(o9Params){
        try {
            const commonLib = require('o9.NSCM.commonLib');
            const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
            const vdUtil = new commonLib.VdUtil();
            
            vdCommon.setLogLevel("Debug");

            vdCommon.printParams(o9Params);

            // 파라미터 가져오기
            var parsedParams = JSON.parse(o9Params);

            /* APPLY 호출 (PY_UI_BODItemW) - LCM */
            var execQuery = 'EXEC plugin instance [PY_UI_BODItemW] ' +
                            'for measures {[BOD Item_Priority]} ' +
                            // 'using scope ( &CWVUI ) ' +
                            'using scope ( &CWVUI * &MFStageLCMLocation * &MFStageSETSubLocation * &LCMItem ) ' +   // LCM data만 실행      
                            'using arguments {(ExecutionMode, "MediumWeight"), (MaxSliceTableCells, 200000000), (MaxConcurrency, 1), ([Param.o9_sys_log_level], "DEBUG") };  ';
            
            vdCommon.debug("execQuery: " + JSON.stringify(execQuery));
            vdCommon.executeQuery("PY Reload Master : PY_UI_BODItemW Run", execQuery);
            vdCommon.debug("---------------------- PY 호출 완료 : PY_UI_BODItemW");
            
            // BOD List W PY 호출
            /* APPLY 호출 (PY_UI_BODListW) - LCM */
            var execQuery2 = 'EXEC plugin instance [PY_UI_BODListW] ' +
                             'for measures {[BOD List W_BOD LT]} ' +
                             'using scope ( &CWVUI ) ' +
                             'using arguments {(ExecutionMode, "MediumWeight"), (MaxSliceTableCells, 200000000), (MaxConcurrency, 1), ([Param.o9_sys_log_level], "DEBUG") };  ';

            vdCommon.debug("execQuery2: " + JSON.stringify(execQuery2));
            vdCommon.executeQuery("PY Reload Master : PY_UI_BODListW Run", execQuery2);
            vdCommon.debug("---------------------- PY 호출 완료 : PY_UI_BODListW");

            let dimension = ["&CWVUI"];
            let measure = ['Measure.[VersionInfo_Time Phased BOD Master Update Time] = dateadd(Now(),9,"hour");', 
                           'Measure.[VersionInfo_Time Phased BOD Master Update User] = CurrentUser().[User Name];'];

            /* Update일자, 사용자 정보입력 */
            // Measure Group 존재하는지 체크후 생성 및 수정
            if ( !vdCommon.existMeasure(dimension, ['Measure.[VersionInfo_Time Phased BOD Master Update Time]'], "") ) {
                vdCommon.createMeasure(dimension, measure);
            } else {                
                vdCommon.updateMeasure(dimension,  measure);
            }
            vdCommon.debug("---------------------- 사용자 업데이트 완료");

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

            /* APPLY 호출 (PY_UI_BODPriorityValid) */
            var execQuery = 'EXEC plugin instance [PY_UI_BODPriorityValid] ' +
                            'for measures {[BOD Item W_Prty], [BOD Item W_Prty Duplicated Flag]} ' +
                            // 'using scope ( &CWVUI * &MFStageLCMLocation * &MFStageSETSubLocation.unionwith(&MFStageKDSubLocation) * &LCMItem ) ' +
                            'using scope ( &CWVUI * &MFStageLCMLocation * &MFStageSETSubLocation * &LCMItem ) ' +  // 2025.02.10 수정 namedset 변경
                            'using arguments {(ExecutionMode, "MediumWeight"), (MaxSliceTableCells, 200000000), (MaxConcurrency, 1), ([Param.o9_sys_log_level], "DEBUG") };  ';

            vdCommon.debug("execQuery: " + JSON.stringify(execQuery));
            vdCommon.executeQuery("fn_validation : PY_UI_BODPriorityValid Run", execQuery);

            vdCommon.programEnd();
        } catch ( e ) {
            RuleOutputToUI = { Status : 'Error', Message : "Js Logic Error : " + e.message };
            return;
        }
    };

    return{
        fn_ReloadMaster : fn_ReloadMaster
       ,fn_validation   : fn_validation
    };
});
/* 2025.02.10 fn_validation Namedset 변경 */