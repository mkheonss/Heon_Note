define('o9.NSCM.JSSETBODListWPriority', ['o9/data/query', 'o9/data/cellset', 'o9.NSCM.commonLib'], function(){

    const programName = "o9.NSCM.JSSETBODListWPriority";

    //-----------------------------------------------------------------------//
    // 2025.02.07 NamedSet 확인 (신승호P)
    // Location : (SET MF, &MFStageSETLocation)
    // Sub Location : (SET DC, &NSUISubLocationDC)
    //-----------------------------------------------------------------------//

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
            vdCommon.debug("---------------------- PY 호출 시작");

            /* APPLY 호출 (PY_UI_BODPriorityValid) */
            var execQuery = 'EXEC plugin instance [PY_UI_BODPriorityValid] ' +
                            'for measures {[BOD Item W_Prty], [BOD Item W_Prty Duplicated Flag]} ' +
                            'using scope ( &CWVUI * &MFStageSETLocation * &NSUISubLocationDC * &SETItem ) ' +
                            'using arguments {(ExecutionMode, "MediumWeight"), (MaxSliceTableCells, 200000000), (MaxConcurrency, 1), ([Param.o9_sys_log_level], "DEBUG") };  ';

            vdCommon.debug("execQuery: " + JSON.stringify(execQuery));
            vdCommon.executeQuery("fn_validation : PY_UI_BODPriorityValid Run", execQuery);
            vdCommon.debug("---------------------- PY 호출 종료");

            vdCommon.programEnd();
        } catch ( e ) {
            RuleOutputToUI = { Status : 'Error', Message : "Js Logic Error : " + e.message };
            return;
        }
    };

    /**
     * Reload Master
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

            /* APPLY 호출 (PY_UI_BODItemW) */
            var execQuery = 'EXEC plugin instance [PY_UI_BODItemW] ' +
                            'for measures {[BOD Item_Priority]} ' +
                            // 'using scope ( &CWVUI ) ' +
                            'using scope ( &CWVUI * &MFStageSETLocation * &NSUISubLocationDC * &SETItem ) ' +   // SET data만 실행
                            'using arguments {(ExecutionMode, "MediumWeight"), (MaxSliceTableCells, 200000000), (MaxConcurrency, 1), ([Param.o9_sys_log_level], "DEBUG") };  ';
            
            vdCommon.debug("execQuery: " + JSON.stringify(execQuery));
            vdCommon.executeQuery("PY Reload Master : PY_UI_BODItemW Run", execQuery);
            vdCommon.debug("---------------------- PY 호출 완료 : PY_UI_BODItemW");
            
            // BOD Prod SET PY 호출 테스트 후 추가하기 2025.01.31 (신승호P 요청)
            /* APPLY 호출 (PY_UI_BODProductSetW) */
            var execQuery2 = 'EXEC plugin instance [PY_UI_BODProductSetW] ' +
                             'for measures {[BOD Prod SET W_BOD LT]} ' +
                             'using scope ( &CWVUI ) ' +        // Product SET 은 SET만 사용하므로 전체 돌려도 됨
                             'using arguments {(ExecutionMode, "MediumWeight"), (MaxSliceTableCells, 200000000), (MaxConcurrency, 1), ([Param.o9_sys_log_level], "DEBUG") };  ';

            vdCommon.debug("execQuery2: " + JSON.stringify(execQuery2));
            vdCommon.executeQuery("PY Reload Master : PY_UI_BODProductSetW Run", execQuery2);
            vdCommon.debug("---------------------- PY 호출 완료 : PY_UI_BODProductSetW");

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
     * 이원화, 일원화 체크, 테스트용 작업 2024.12.03 
     * 배치 실행 프로그램 (UI 테스트용으로 임시 작업) - 삭제예정
     * @param {*} o9Params 
     * @returns 
     */
    var fn_supplyFilter = function(o9Params){
        try {
            const commonLib = require('o9.NSCM.commonLib');
            const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
            const vdUtil = new commonLib.VdUtil();
            
            vdCommon.setLogLevel("Debug");
            vdCommon.printParams(o9Params);

            // 파라미터 가져오기
            var parsedParams = JSON.parse(o9Params);

            // Measure Group 삭제 - add 2025.05.14
            // vdCommon.deleteMeasure(["&CWVUI", "[Item].[Item]", "[Location].[Location]", "[Sub Location].[Sub Location]"], "BOD Item Prty");
            vdCommon.deleteMeasure(["&CWVUI"], "BOD Item Prty");

            vdCommon.debug("---------------------- PY 호출 시작");

            /* APPLY 호출 (PY_UI_BODPriority_SupplyFilter) */
            var execQuery = 'EXEC plugin instance [PY_UI_BODPriority_SupplyFilter] ' +
                            'for measures {[BOD Item Prty_Supply Filter]} ' +
                            'using scope ( &CWVUI ) ' +
                            'using arguments {(ExecutionMode, "MediumWeight"), (MaxSliceTableCells, 200000000), (MaxConcurrency, 1), ([Param.o9_sys_log_level], "DEBUG") };  ';

            vdCommon.debug("execQuery: " + JSON.stringify(execQuery));
            vdCommon.executeQuery("fn_supplyFilter : PY_UI_BODPriority_SupplyFilter Run", execQuery);
            vdCommon.debug("---------------------- PY 호출 종료");

            vdCommon.programEnd();
        } catch ( e ) {
            RuleOutputToUI = { Status : 'Error', Message : "Js Logic Error : " + e.message };
            return;
        }
    };

    return{
        fn_ReloadMaster : fn_ReloadMaster
       ,fn_validation   : fn_validation
       ,fn_supplyFilter : fn_supplyFilter           /* 배치 테스트 이원화,일원화 테스트 PY 2025.02.19 - 버튼으로 사용하기로 (신승호p)*/
    };
});
/*-------------------------------------------------------------------------------------------------*/
/* 프로그램명 : o9.NSCM.JSSETBODListWPriority */
/* 2025.02.10 fn_validation Namedset 변경 */
/* 2025.05.14 fn_supplyFilter 수정 : PY 수행 전 BOD Item Prty 데이터 초기화(삭제) */
/*-------------------------------------------------------------------------------------------------*/