define('o9.NSCM.JSWeeklyPlan', ['o9/data/query', 'o9/data/cellset', 'o9.NSCM.commonLib'], function(){
	const programName = "o9.NSCM.JSWeeklyPlan";

    function fn_dataSetCombo(o9Params){
		try{
            const commonLib = require('o9.NSCM.commonLib');
            const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
            vdCommon.setLogLevel("Debug");

			let parsedParams = JSON.parse(o9Params);
			let fbVersion = parsedParams.fbVersion; 
			//2025.03.17 김보은 프로님 요청으로 MP로 고정함.
			//selectList(dimension, measure, where, orderby, limit)
			let selectQuery = `Select ([Data Set].[Data Set].[MP]) on row, () on column orderby [Data Set].[Data Set].Key desc ;`;
			let selectResult = vdCommon.selectQueryList("[fn_MPApply(Capa Simual Line)]", selectQuery);
			//isNameWithDisplayName Local 소스 추가함.
			let comboList = vdCommon.fn_makeCombo(selectResult, {DimName : "Data Set", DimAttbName : "Data Set", existAll : false,  isDisplayNameWithCode : false, isNameWithDisplayName: false});

			return comboList;
		}catch ( e ) {
            RuleOutputToUI = { Status : 'Error', Message : "Js Logic Error : " + e.message };
            return;
        } 
    }

    function fn_submit(o9Params){       
		try{
			const commonLib = require('o9.NSCM.commonLib');
            const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
			vdCommon.setLogLevel("Debug");

			// 파라미터 가져오기
			vdCommon.printParams(o9Params);
			var parsedParams = JSON.parse(o9Params);
			var fbVersion = parsedParams.fbVersion;

			//Current Version 삭제 후 다시 copy함.
			let deleteQuery = ['Version.[Version Name].filter(#.Name =="'+fbVersion+'")'];
			vdCommon.deleteMeasure(deleteQuery, 'Work Cal Line');
			//+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
			// 이전 버젼을 Current Version으로  Copy 함. (MP Version)
			//+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
			let pythonQuery = 'EXEC plugin instance [PY_UI_WeeklyPlanDataCreate] for measures {[Work Cal Line_Time]} ';
			pythonQuery += 'using scope(&LastSyncVersion)'
			pythonQuery += 'using arguments {(ExecutionMode, "MediumWeight"), ("IncludeNullRows", "False"),';
			pythonQuery += '(paramOutVersion , "'+fbVersion+'"),(MaxSliceTableCells, 200000000),(MaxConcurrency, 1), ([Param.o9_sys_log_level], "DEBUG")};';
			
			vdCommon.executeQuery("[python Exec]", pythonQuery); 
			//추가된 Memter에 대한 데이타를 파이썬에서 생성함.
			vdCommon.programEnd();			

		}catch ( e ) {
            RuleOutputToUI = { Status : 'Error', Message : "Js Logic Error : " + e.message };
            return;
        }
	}

    return{
        fn_dataSetCombo : fn_dataSetCombo,
		fn_submit  : fn_submit
    };	
});