define('o9.NSCM.JSBatchJob', ['o9/data/query', 'o9/data/cellset', 'o9.NSCM.commonLibVD'], function () {
    const programName = "o9.NSCM.JSBatchJob";
    const commonLib = require('o9.NSCM.commonLibVD');
    const vdUtil = new commonLib.VdUtil();

    var fn_add = function(o9Params){
        const commonLib = require('o9.NSCM.commonLib');
        const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
        vdCommon.setLogLevel("Debug");

        try {
            vdCommon.printParams(o9Params);

            var p = JSON.parse(o9Params);

            if ( vdCommon.existMeasure(["&CWVUI"
                                            ,"[Batch Job].[Job]" + vdUtil.fn_filterStr(p.fbJob.split(","))]
                                        ,['Measure.[Batch Job_Parent Job]']) ) {
                RuleOutputToUI = { Status : 'Error', Message : "This Data has already been registered." };
                return 1;
            } else {
                // 멤버 생성
                var jobs = p.fbJob.split(",");
                for ( var i = 0; i < jobs.length; i++ ) {
                    if ( !vdCommon.existMember('[Batch Job].[Job]', jobs[i]) ) {
                        vdCommon.createMember('[Batch Job].[Job]', jobs[i]);
                    }

                    // MG 생성
                    vdCommon.createMeasure(["&CWVUI"
                                                ,"[Batch Job].[Job]" + vdUtil.fn_filterStr(jobs[i])],
                                           ['Measure.[Batch Job_Parent Job] = "' + p.fbParentJob + '";'
                                                ,'Measure.[Batch Job_Order] = "' + ( parseInt(p.fbOrder) + i ) + '";'
                                                ,'Measure.[Batch Job_Job Kind] = "' + p.fbJobKind + '";']);
                }
            }

            vdCommon.programEnd();
        } catch ( e ) {
            RuleOutputToUI = { Status : 'Error', Message : "Js Logic Error : " + e.message };
            return;
        }
    };

    var fn_delete = function(o9Params){
        const commonLib = require('o9.NSCM.commonLib');
        const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
        vdCommon.setLogLevel("Debug");

        try {
            vdCommon.printParams(o9Params);

            var p = JSON.parse(o9Params);

            for ( var i = 0; i < p.fbSelect.length; i++ ) {
                var row = p.fbSelect[i];

                vdCommon.deleteMeasure(["&CWVUI"
                                            ,"[Batch Job].[Job]" + vdUtil.fn_filterStr(row.Job.Value)]
                                       ,"Batch Job");
                vdCommon.deleteMeasure(["&CWVUI"
                                            ,"[Batch Job].[Job]" + vdUtil.fn_filterStr(row.Job.Value)]
                                       ,"Batch Job Log");
            }

            vdCommon.programEnd();
        } catch ( e ) {
            RuleOutputToUI = { Status : 'Error', Message : "Js Logic Error : " + e.message };
            return;
        }
    };

    // Level 데이타를 생성한다.
    var fn_updateDimensionInfo = function(o9Params){
        const commonLib = require('o9.NSCM.commonLib');
        const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
        vdCommon.setLogLevel("Debug");

        try {
            vdCommon.printParams(o9Params);

            var p = JSON.parse(o9Params);

            // Leaf 여부를 N
            vdCommon.updateMeasure(["&CWVUI",
                                        "[Batch Job].[Job]"],
                                    ['Measure.[Batch Job_Leaf] = "N";']);

            // Level 데이타 생성하는 파이썬 호출
            var execQuery = 'EXEC plugin instance [PY_MG_BatchJob] ' +
                            'for measures {[Batch Job_Level 1]} ' +
                            'using scope ( &CWVUI ) ' +
                            'using arguments {(outVersionName, "CWV_MP"), (ExecutionMode, "MediumWeight"), (MaxSliceTableCells, 200000000), (MaxConcurrency, 1 )};'
            vdCommon.executePython("PY_MG_BatchJob", execQuery);

            // Dimension 정보를 수정한다.
            var createQuery = ' createmember( ' +
                              '  [Batch Job].[Job] = {, [Batch Job].#.Name}, ' +
                              '  [Batch Job].[Job Kind] = {, Measure.[Batch Job_Job Kind]}, ' +
                              '  [Batch Job].[Is Leaf] = {, Measure.[Batch Job_Leaf]}, ' +
                              '  [Batch Job].[Level 1] = {, Measure.[Batch Job_Level 1]}, ' +
                              '  [Batch Job].[Level 2] = {, Measure.[Batch Job_Level 2]}, ' +
                              '  [Batch Job].[Level 3] = {, Measure.[Batch Job_Level 3]}, ' +
                              '  [Batch Job].[Level 4] = {, Measure.[Batch Job_Level 4]}, ' +
                              '  [Batch Job].[Level 5] = {, Measure.[Batch Job_Level 5]}, ' +
                              '  [Batch Job].[Level 6] = {, Measure.[Batch Job_Level 6]}, ' +
                              '  [Batch Job].[Level 7] = {, Measure.[Batch Job_Level 7]}, ' +
                              '  [Batch Job].[Job Order] = {Measure.[Batch Job_All Order],}, ' +
                              '  [Batch Job].[Level 1 Order] = {Measure.[Batch Job_Level 1 Order],}, ' +
                              '  [Batch Job].[Level 2 Order] = {Measure.[Batch Job_Level 2 Order],}, ' +
                              '  [Batch Job].[Level 3 Order] = {Measure.[Batch Job_Level 3 Order],}, ' +
                              '  [Batch Job].[Level 4 Order] = {Measure.[Batch Job_Level 4 Order],}, ' +
                              '  [Batch Job].[Level 5 Order] = {Measure.[Batch Job_Level 5 Order],}, ' +
                              '  [Batch Job].[Level 6 Order] = {Measure.[Batch Job_Level 6 Order],}, ' +
                              '  [Batch Job].[Level 7 Order] = {Measure.[Batch Job_Level 7 Order],} ' +
                              '  ) using scope (&CWVUI * [Batch Job].[Job]); ';
            vdCommon.executeQuery("Member 생성", createQuery);

            vdCommon.programEnd();
        } catch ( e ) {
            RuleOutputToUI = { Status : 'Error', Message : "Js Logic Error : " + e.message };
            return;
        }
    };

    var fn_makeLog = function(o9Params){
        const commonLib = require('o9.NSCM.commonLib');
        const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
        vdCommon.setLogLevel("Debug");

        try {
            vdCommon.printParams(o9Params);

            var p = JSON.parse(o9Params);

            var nowTime = new Date();
            nowTime.setHours(nowTime.getHours() + 9);
            var day = nowTime.getFullYear() + "-"
                        + vdUtil.fn_lpad((nowTime.getMonth() + 1) + "", 2, "0") + "-"
                        + vdUtil.fn_lpad(nowTime.getDate() + "", 2, "0");

            // Level 데이타 생성하는 파이썬 호출
            var execQuery = 'EXEC plugin instance [PY_MG_BatchJobLog] ' +
                            'for measures {[Batch Job Log_Start Time]} ' +
                            'using scope ( &CWVUI * [Time].[Day].[' + day + '] ) ' +
                            'using arguments {(outVersionName, "CWV_MP"), (ExecutionMode, "MediumWeight"), (MaxSliceTableCells, 200000000), (MaxConcurrency, 1 )};'
            vdCommon.executePython("PY_MG_BatchJob", execQuery);

            vdCommon.programEnd();
        } catch ( e ) {
            RuleOutputToUI = { Status : 'Error', Message : "Js Logic Error : " + e.message };
            return;
        }
    };

    return {
        fn_add : fn_add
        ,fn_delete : fn_delete
        ,fn_updateDI : fn_updateDimensionInfo
        ,fn_makeLog : fn_makeLog
    };
});

/**************************** o9.NSCM.JSBatchJob ****************************
***************************** o9.NSCM.JSBatchJob ***************************/