define('o9.NSCM.JS.PoProcessBatch', ['o9.NSCM.commonLibDA'], function(commonLib)
{
    /**
     * o9.NSCM.JS.PoProcessBatch.js.
     *
     *  Po Process  Batch (Split, Simulation 호출)
     */
/**********************************************************************************************************************/
/***************** CONST 설정 ****************************************************************************/
/**********************************************************************************************************************/
    /* Program Name */
    const programName = "o9.NSCM.JS.PoProcessBatch";

    /* jsErrorMsg   */
    const jsErrorMsg = "Please contact the system administrator.";

    /* setting  */
    let daCommon = new commonLib.DACommon(programName);
    daCommon.setLogLevel("Debug")
    let daUtil = new commonLib.DAUtil();

/**********************************************************************************************************************/
/***************** TRANSACTION START *********************************************************************/
/**********************************************************************************************************************/
    /* Call Exec Po Process Split Python    */
    let fn_ExecPYUIPOProcessSplit =  function(o9Params) {
        let parsedParams = JSON.parse(o9Params);
        // 배치 수행시 MP Pre Plan , MP Main Plan 파라메터로 넘어오는 값 프로그램 수행시  "P", "M"으로 변경
        if(parsedParams.fb_ParamStep === "MP Pre Plan"){
            parsedParams.fb_ParamStep = "P";
        } else if(parsedParams.fb_ParamStep === "MP Main Plan"){
            parsedParams.fb_ParamStep = "M";
        }
        
        // 엔진 수행 종류( "P", "M" ) 에 따라 초기화 후 PY_UI_POProcessSplit_REG 파이썬 실행
        try {
            //0. Split 배치 실행 전,
            // 1) PO Process에 이전 버전 삭제.
            // 2) 상단(PO Process) POP 값  CHECK_QTY 에 COPY.
            QueryCommon.executeScopePoProcessCheckQty(parsedParams);

            //1. Split 배치 수행
             try {
                 QueryCommon.executePYUIPOProcessSplitREG(parsedParams);
             } catch(e) {
                 throw new Error('Split Python Error');
             }

           //2. Simulation 자동 배치 수행
           //2-1. 초기화 (Container planning, Cal Master, Po, Po detail 초기화)
            let query = fn_MakeQueryString(parsedParams);
            daCommon.executeQuery('executeScopeSimulationInitialize', query);

            //2-2. Validation 실행
            try{
                QueryCommon.execUIPOProcessValidNLoadREG(parsedParams);
            } catch(e) {
                throw new Error('Valid Python Error');
            }

            //2-3. Validation 후, 대상건('Y', 'Y', isnull(reason) 인 건)에 대해서만 simulation 수행되어야함.(파이썬 로직에 반영되어 있음)
            try{
                QueryCommon.execUIPOProcessNoneSKUREG(parsedParams);
            } catch(e) {
                throw new Error('Simulation Python Error');
            }

        } catch(e){
            let errMsg = jsErrorMsg;

            if (e.message === 'Split Python Error') { // 1)해당 단계에 split대상(detail) 이 없는 상태
                errMsg = 'An error occurred when running Split Python.' ;
            } else if (e.message === 'Valid Python Error') { // 2) split 까지는 된 상태
                errMsg = 'An error occurred when running Valid Python.' ;
            } else if(e.message === 'Simulation Python Error') {// 3) split와 validation output이 들어간 상태
                errMsg = 'An error occurred while running Simulation Python.' ;
            }

            RuleOutputToUI = {Status: 'Error', Message: errMsg};
        }

    }

    let fn_MakeQueryString = function(params){
        let paramStepList_P = ['P', 'M', 'ADJ1', 'ADJ2', 'ADJ3', 'FINAL'];
        let paramStepList_M = ['M', 'ADJ1', 'ADJ2', 'ADJ3', 'FINAL'];
        let paramStepList = params.fb_ParamStep === 'P' ? paramStepList_P : paramStepList_M;
        let scopeQueryStr = ''

        let scopePoStr = ''
        //결과값 메저는 nullify, P/M 제외하고 나머지 Check Qty 도 nullify
        paramStepList.forEach(
            item =>{
                scopePoStr += `
                Measure.[PO Process_Item Unit Load Mix Match Chk(${item})] = null;
                Measure.[PO Process_Item Unit Load Mix Match(${item})] = null;
                Measure.[PO Process_Lane Load Mix Match Chk(${item})] = null;
                Measure.[PO Process_Lane Load Mix Match(${item})] = null;
                Measure.[PO Process_Valid Fail Reason(${item})] = null;
                Measure.[PO Process_CNTR FR(${item})] = null;
                Measure.[PO Process_Diff Qty(${item})] = null;
                Measure.[PO Process_Item FR(${item})] = null;
                Measure.[PO Process_Loading Qty(${item})] = null;
                Measure.[PO Process_Loading Status(${item})] = null;
                ${(item !== 'P' && item !== 'M') ?  `Measure.[PO Process_Check Qty(${item})] = null;` : ''}    
                `;
            }
        );

        if (params.fb_ParamStep === 'P'){
            // Container planning / Cal Master 삭제,
            // Po Nullfiy(모든단계 결과값 Nullify),
            // Po Detail (split시에 삭제하므로 작업없음.)
            scopeQueryStr = `//Container planning Initialize
                                delete data for model [Loading PO Container Plan]
                                where { &CWV_MP };                                   
                                    
                            //Cal Master Initialize
                                delete data for model [Loading PO Cal Master]
                                where { &CWV_MP };
                                    
                            //Po nullify ( 결과값 메저 nullify)
                                Scope: (  &CWV_MP 
                                         * [Sub Location].[Sub Location] 
                                         * [Seq].[Seq] 
                                         * [Item].[Item]
                                         * [Location].[Location] 
                                         * [Time].[Week] 
                                         * [MFG Week].[MFG Week] 
                                         * [Delivery Week].[Delivery Week] 
                                    );                                    
                                    ${scopePoStr}                    
                                end scope;
                                 `;
        } else {
            //Container planning: P제외하고 모두 삭제,
            //Cal Master 삭제,
            //Po Nullfiy(P 단계 제외하고 모두 Nullify),
            //Po Detail Nullify(P단계 제외하고 모두 Nullify, 단 FINAL 메저 초기화 시 최종 step이 P인 row는 제외 하고 결과값 Nullify)
            let compareStr = `if( "${params.fb_ParamStep}" == "M" && Measure.[PO Process Detail_Last Step] == 1 )`;
            let scopePoDetailStr = ''

            //결과값 메저는 nullify, P/M 제외하고 나머지 Check Qty 도 nullify ( M에서만 생성 )
            paramStepList = ['M', 'ADJ1', 'ADJ2', 'ADJ3']
            paramStepList.forEach(
                item => {
                    scopePoDetailStr += `
                    Measure.[PO Process Detail_Item Unit Load Mix Match Chk(${item})] = null;
                    Measure.[PO Process Detail_Item Unit Load Mix Match(${item})] = null;
                    Measure.[PO Process Detail_Lane Load Mix Match Chk(${item})] = null;
                    Measure.[PO Process Detail_Lane Load Mix Match(${item})] = null;
                    Measure.[PO Process Detail_Valid Fail Reason(${item})] = null;
                    Measure.[PO Process Detail_CNTR FR(${item})] = null;
                    Measure.[PO Process Detail_Diff Qty(${item})] = null;
                    Measure.[PO Process Detail_Item FR(${item})] = null;
                    Measure.[PO Process Detail_Loading Qty(${item})] = null;
                    Measure.[PO Process Detail_Loading Status(${item})] = null;
                    ${(item !== 'P' && item !== 'M') ? `Measure.[PO Process Detail_Check Qty(${item})] = null;` : ''}
                    `;
                }
            )
            //M simulation 인 경우, FINAL 메저 초기화 시 최종 step이 P인 row는 제외 하고 nullify한다.
            scopePoDetailStr += `
            Measure.[PO Process Detail_Item Unit Load Mix Match Chk(FINAL)] = ${compareStr} then Measure.[PO Process Detail_Item Unit Load Mix Match Chk(FINAL)] else null;
            Measure.[PO Process Detail_Item Unit Load Mix Match(FINAL)] = ${compareStr} then Measure.[PO Process Detail_Item Unit Load Mix Match(FINAL)] else null;
            Measure.[PO Process Detail_Lane Load Mix Match Chk(FINAL)] = ${compareStr} then Measure.[PO Process Detail_Lane Load Mix Match Chk(FINAL)] else null;
            Measure.[PO Process Detail_Lane Load Mix Match(FINAL)] = ${compareStr} then Measure.[PO Process Detail_Lane Load Mix Match(FINAL)] else null;
            Measure.[PO Process Detail_Valid Fail Reason(FINAL)] = ${compareStr} then Measure.[PO Process Detail_Valid Fail Reason(FINAL)] else null;                                    
            Measure.[PO Process Detail_CNTR FR(FINAL)] = ${compareStr} then Measure.[PO Process Detail_CNTR FR(FINAL)] else null;
            Measure.[PO Process Detail_Diff Qty(FINAL)] = ${compareStr} then Measure.[PO Process Detail_Diff Qty(FINAL)] else null;
            Measure.[PO Process Detail_Item FR(FINAL)] = ${compareStr}  then Measure.[PO Process Detail_Item FR(FINAL)] else null;
            Measure.[PO Process Detail_Loading Qty(FINAL)] = ${compareStr} then Measure.[PO Process Detail_Loading Qty(FINAL)] else null;
            Measure.[PO Process Detail_Loading Status(FINAL)] = ${compareStr} then Measure.[PO Process Detail_Loading Status(FINAL)] else null;
            Measure.[PO Process Detail_Check Qty(FINAL)] = ${compareStr} then Measure.[PO Process Detail_Check Qty(FINAL)] else null;`;

            scopeQueryStr = `//Container planning Initialize
                                delete data for model [Loading PO Container Plan]
                                where { &CWV_MP,
                                        [Plan Step].[Plan Step].filter(~(#.Name in { "P" }))};                                   
                                    
                            //Cal Master Initialize
                                delete data for model [Loading PO Cal Master]
                                where { &CWV_MP };
                                    
                            //Po nullify ( 결과값 메저 nullify)
                                Scope: (  &CWV_MP 
                                        * [Sub Location].[Sub Location] 
                                        * [Seq].[Seq] 
                                        * [Item].[Item]
                                        * [Location].[Location] 
                                        * [Time].[Week] 
                                        * [MFG Week].[MFG Week] 
                                        * [Delivery Week].[Delivery Week] 
                                        );                                    
                                        ${scopePoStr}                    
                                end scope;
                                
                            //Po Detail nullfy ( 결과값 메저 nullify)
                               Scope: (  &CWV_MP  
                                        * [Sub Location].[Sub Location] 
                                        * [Seq].[Seq] 
                                        * [Item].[Item]
                                        * [Location].[Location] 
                                        * [Time].[Week] 
                                        * [MFG Week].[MFG Week] 
                                       );
                                       ${scopePoDetailStr} 
                                end scope; 
                                 `;
        }
        Log.Info("scopeQueryStr =============================> " + scopeQueryStr);
        return scopeQueryStr;
    }
/**********************************************************************************************************************/
/***************** TRANSACTION END ***********************************************************************/
/**********************************************************************************************************************/

/**********************************************************************************************************************/
/***************** QUERY COMMON START  *******************************************************************/
/**********************************************************************************************************************/
    class QueryCommon {
        static executeScopePoProcessCheckQty(params){
            //1) Pop Qty -> Check Qty 반영. 2) PO Process에 이전 버전 삭제
            let query=
                `delete data for model [PO Process]
                where {&CWV_MP, Time.Week.filter(#.Key < &CurrentWeek.element(0).Key)};
                
                Scope:(
                          &CWV_MP
                        * [Sub Location].[Sub Location] 
                        * [Item].[Item] 
                        * [Location].[Location] 
                        * [Time].[Week] 
                        * [SOP Week].[SOP Week] 
                        * [Delivery Week].[Delivery Week] 
                        * [MFG Week].[MFG Week] 
                        );
                Measure.[PO Process_Check Qty(${params.fb_ParamStep})] = Measure.[PO Process_POP Qty(${params.fb_ParamStep})];
                end scope;
                `;

            daCommon.executeQuery('executeScopePoProcessCheckQty', query);
        }

        static executePYUIPOProcessSplitREG(params) {
            let updateQuery ;
            if(params.fb_ParamStep === 'P'){
                // P수행시 : Detail 메저 그룹과, Dir에만 있어서 상단에 생성된 row(Data Source =='2')를 지운다.
                updateQuery = `delete data for model [PO Process Detail]
                               where { &CWV_MP };
                               
                               delete data for model [PO Process]
                               where { &CWV_MP , Measure.[PO Process_Data Source] == "2" }; 
                               `;
            } else {
                // M 수행시 : M중복 수행시 생성된 row를 지우고, Qty(M)값(POP, Short, Order Mgmt, Check) 초기화 한다.
                // Dir에만 있어서 상단에 생성된 row(Data Source =='3') 지운다.
                updateQuery = `delete data for model [PO Process Detail]
                               where { &CWV_MP , isnull(Measure.[PO Process Detail_Chk Last Step(P)])};
                               
                               scope:( &CWV_MP );
                                    Measure.[PO Process Detail_POP Qty(M)]=null;
                                    Measure.[PO Process Detail_Order Mgmt Qty(M)]=null;
                                    Measure.[PO Process Detail_Check Qty(M)]=null;
                                    Measure.[PO Process Detail_Short Qty(M)]=null;
                                    Measure.[PO Process Detail_DMD ETA 4Week Sum Qty]=
                                    if (Measure.[PO Process Detail_Last Step] == 2) then null
                                    else  Measure.[PO Process Detail_DMD ETA 4Week Sum Qty]; // M Step의 결과값만 초기화
                               end scope;
                               
                               delete data for model [PO Process]
                               where { &CWV_MP , Measure.[PO Process_Data Source] == "3" }; 
                               `;
            }

            let execQuery =
                `EXEC plugin instance [PY_UI_POProcessSplit_REG]
                 for measures { [PO Process Detail_POP Qty(M)]
                               ,[PO Process Detail_POP Qty(P)]
                               ,[PO Process Detail_Order Mgmt Qty(M)]
                               ,[PO Process Detail_Order Mgmt Qty(P)]
                               ,[PO Process Detail_SOP ETD Week]
                            }
                   using scope ( [Version].[Version Name].filter(#.Name == "CWV_MP" 
                   || (#.[Plan Type]=="MP Sync Plan" && #.[Plan Week] == &CurrentWeek.element(0).LeadOffset(-1).Name))
                   )
                   using arguments {(ExecutionMode, "MediumWeight")
                                 , (Param_OUT_VERSION, "CWV_MP")
                                 , (Param_Step, "${params.fb_ParamStep}")
                                 , (MaxSliceTableCells, 200000000)
                                 , (MaxConcurrency, 1 )
                                 , (IncludeNullRows, False)
                                 , ([Param.o9_sys_log_level], "DEBUG")
                                 };`;

            let query = `${updateQuery} 
                                  ${execQuery}`;

            return daCommon.executeQuery('executePYUILoadingDirOrderMgmtNoneSKUREG', query);
        }

         static execUIPOProcessValidNLoadREG(params){
            let query = `EXEC plugin instance [PY_UI_POProcessValidNLoad_REG]
                                  for measures { [PO Process_Valid Fail Reason(${params.fb_ParamStep})] }
                                    using scope (&CWV_MP)
                                    using arguments {(ExecutionMode, "MediumWeight")
                                                   , (Param_OUT_VERSION, "CWV_MP")
                                                   , (Param_Exception_Flag, "N")
                                                   , (Param_Step, "${params.fb_ParamStep}")
                                                   , (MaxSliceTableCells, 200000000)
                                                   , (MaxConcurrency, 1)
                                                   , (IncludeNullRows, False)
                                                   , ([Param.o9_sys_log_level], "DEBUG")
                                     };
                                     `;

            return daCommon.executeQuery('execUIPOProcessValidNLoadREG', query);
         }

         static execUIPOProcessNoneSKUREG(params){
            let query = `EXEC plugin instance [PY_UI_POProcessNoneSKU_REG]
                                  for measures {[PO Process Detail_Simulated By]}
                                    using scope (&CWV_MP)
                                    using arguments {(ExecutionMode, "MediumWeight")
                                                   , (Param_OUT_VERSION, "CWV_MP")
                                                   , (Param_Adjust_Option1, "MAX")
                                                   , (Param_Adjust_Option2 , "Max Profit")
                                                   , (Param_User_Name , "SYSTEM")
                                                   , (Param_Step, "${params.fb_ParamStep}")
                                                   , (MaxSliceTableCells, 200000000)
                                                   , (MaxConcurrency, 1)
                                                   , (IncludeNullRows, False)
                                                   , ([Param.o9_sys_log_level], "DEBUG")
                                     };
                                     `;

            return daCommon.executeQuery('execUIPOProcessNoneSKUREG', query);
         }

    }

/**********************************************************************************************************************/
/***************** QUERY COMMON END  *********************************************************************/
/**********************************************************************************************************************/

    return {
          // Call Exec Po Process Split Python
          fn_ExecPYUIPOProcessSplit : daCommon.fn_decorator(fn_ExecPYUIPOProcessSplit)
    };

});