define('o9.NSCM.JSSafetyStockMonitoring', ['o9/data/query', 'o9/data/cellset', 'o9.NSCM.commonLib'], function(){
	const programName = "o9.NSCM.JSSafetyStockMonitoring";
    /*--------------------------------------------------------------------------------------------------*/
    // 프로그램명 : JSSafetyStockMonitoring
    // 화면명 : Safety Stock Monitoring
    // 2025.10.02 fn_dataCreate() 데이타 생성 유무 체크 관련 수정
    // 2025.10.10 데이타 유무 체크 IBPL 수정
    /*--------------------------------------------------------------------------------------------------*/   

    function fn_dataCreate(o9Params){
        //safetyStockMonitoring Data Create
        try{
            const commonLib = require('o9.NSCM.commonLib');
            const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
            vdCommon.setLogLevel("Debug");
            vdCommon.printParams(o9Params);
    
            // 파라메타 가져오기
            let parsedParams = JSON.parse(o9Params); 
            let fbVersion = parsedParams.fbVersion;

            //데이타 생성 유무를 체크함.
            let selectCount = vdCommon.selectListCount(["[Version].[Version Name].["+fbVersion+"]","[Location].[Location]","[Item].[Item]", "[Time].[Week]"], 
                                                    ["Measure.[W Ending On Hand]","Measure.[W Target Inventory]","Measure.[W WOS Target]"],
                                                    'Where{[Location].[Location Type].filter(#.Name == "DC"), association(~Isnull(Measure.[W Target Inventory]))}'); 
            //vdCommon.debug("[selectCount]" + selectCount);

            if(selectCount > 0){
                let deleteQuery = ["[Version].[Version Name].["+fbVersion+"]"];
                vdCommon.deleteMeasure( deleteQuery, "SS Monitor");            
    
                let pythonQuery = 'EXEC plugin instance [PY_UI_SSMonitor] for measures {[SS Monitor_Arrival]} ';
                pythonQuery += 'using scope([Version].[Version Name].['+fbVersion+'] * [Sales Domain].[AP2].filter(~(#.Name in {"All", "-"}))) ';
                pythonQuery += 'using arguments {(ExecutionMode, "MediumWeight"), (paramOutVersion , "'+fbVersion+'"), ';
                pythonQuery += '(MaxSliceTableCells, 200000000), (MaxConcurrency, 1 ), ([Param.o9_sys_log_level], "DEBUG")} ;';
    
                vdCommon.executeQuery("[PY_UI_SSMonitor Call] ", pythonQuery);                
            }else{
                RuleOutputToUI = { Status : 'Error', Message : "There is no data to generate.." };  
            }

            vdCommon.programEnd(); 

        }catch ( e ) {
            RuleOutputToUI = { Status : 'Error', Message : "Js Logic Error : " + e.message };
            return;
        }    
    }

    return{
		fn_dataCreate  : fn_dataCreate
    };	
});