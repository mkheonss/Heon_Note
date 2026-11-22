define('o9.NSCM.JSPythonBatch', ['o9/data/query', 'o9/data/cellset', 'o9.NSCM.commonLib'], function () {
    const programName = "o9.NSCM.JSPythonBatch";

    var fn_add = function(o9Params){
        const commonLib = require('o9.NSCM.commonLib');
        const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
        vdCommon.setLogLevel("Debug");

        try {
            vdCommon.printParams(o9Params);

            // 파라미터 가져오기
            var parsedParams = JSON.parse(o9Params);
            var fbVersionName = "CWV_MP";
            var fbPythonName = parsedParams.fbPythonName;
            var fbDesc = parsedParams.fbDesc;
            var fbMeasures = parsedParams.fbMeasures;
            var fbScope = parsedParams.fbScope;
            var fbArguments = parsedParams.fbArguments;
            var fbManager = parsedParams.fbManager;
            var fbDeveloper = parsedParams.fbDeveloper;

            if ( !vdCommon.existDimension(['[Python Batch].[Python Name].[' + fbPythonName + ']']) ) {
                vdCommon.createDimension(['[Python Batch].[Python Name]'], [fbPythonName]);
            }

            var isExist = vdCommon.existMeasure(["[Version].[Version Name].[" + fbVersionName + "]",
                                                    "[Python Batch].[Python Name].[" + fbPythonName + "]"],
                                                ["Measure.[Python Batch_Measures]"],
                                                "");
            if ( isExist ) {
                RuleOutputToUI = { Status : 'Error', Message : "This Data has already been registered." };
                return;
            } else {
                vdCommon.createMeasure(["[Version].[Version Name].[" + fbVersionName + "]",
                                            "[Python Batch].[Python Name].[" + fbPythonName + "]"],
                                       ['Measure.[Python Batch_Desc] = "' + fbDesc + '";',
                                            'Measure.[Python Batch_Measures] = "' + fbMeasures + '";',
                                            'Measure.[Python Batch_Scope] = "' + fbScope + '";',
                                            'Measure.[Python Batch_Arguments] = "' + fbArguments.replace(/\"/g, '\\\"') + '";',
                                            'Measure.[Python Batch_Manager] = "' + fbManager + '";',
                                            'Measure.[Python Batch_Developer] = "' + fbDeveloper + '";']);
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

            // 파라미터 가져오기
            var parsedParams = JSON.parse(o9Params);
            var fbSelect = parsedParams.fbSelect;
            var fbVersionName = "CWV_MP";

            for ( var i = 0; i < fbSelect.length; i++ ) {
                var row = fbSelect[i];

                var where = [];
                where.push("[Version].[Version Name].[" + fbVersionName + "]");
                where.push("[Python Batch].[Python Name].[" + row.PythonName.Value + "]");

                vdCommon.deleteMeasure(where, "Python Batch");
            }

            vdCommon.programEnd();
        } catch ( e ) {
            RuleOutputToUI = { Status : 'Error', Message : "Js Logic Error : " + e.message };
            return;
        }
    };

    var fn_run = function(o9Params){
        const commonLib = require('o9.NSCM.commonLib');
        const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
        const vdUtil = new commonLib.VdUtil();

        vdCommon.setLogLevel("Debug");

        try {
            vdCommon.printParams(o9Params);

            // 파라미터 가져오기
            var parsedParams = JSON.parse(o9Params);
            var fbVersionName = "CWV_MP";
            var fbPythonName = parsedParams.fbPythonName;
            var fbMeasures = parsedParams.fbMeasures;
            var fbScope = parsedParams.fbScope;
            var fbArguments = parsedParams.fbArguments;
            var fbRequester = parsedParams.fbRequester;
            var fbRequestMemo = parsedParams.fbRequestMemo;

            // 파이썬 실행
            try {
                if ( fbArguments != "" ) {
                    fbArguments += ", ";
                }

                var execQuery = 'EXEC plugin instance [' + fbPythonName + '] ' +
                                'for measures {' + fbMeasures + '} ' +
                                'using scope ( ' + fbScope + ' ) ' +
                                'using arguments {' + fbArguments + '(ExecutionMode, "MediumWeight"), (MaxSliceTableCells, 200000000), (MaxConcurrency, 1 )};'
                vdCommon.executeQuery("Python Batch Run", execQuery);

                // 평균 시간을 가져온다.
                result = vdCommon.selectList(["[Version].[Version Name].[" + fbVersionName + "]",
                                                        "[Python Batch].[Python Name].[" + fbPythonName + "]"],
                                                    ["Measure.[Python Batch Log_Elasped Time]"],
                                                    "",
                                                    "",
                                                    "");
                var avgElaspedTime = 0;
                if ( result.cs.rowCount > 0 ) {
                    avgElaspedTime = result.cs.row(0).cell(result.cs.measureColumnIndex("Python Batch Log_Elasped Time"));
                }

                // 마지막 결과를 가져온다.
                result = vdCommon.selectList(["[Version].[Version Name].[" + fbVersionName + "]",
                                                    "[Python Batch].[Python Name].[" + fbPythonName + "]"
                                                    ,"[Time].[Day]"
                                                    ,"[Sequence].[Sequence]"],
                                                ["Measure.[Python Batch Log_Elasped Time]"
                                                    ,"Measure.[Python Batch Log_Start Time]"
                                                    ,"Measure.[Python Batch Log_End Time]"
                                                    ,"Measure.[Python Batch Log_Error Message]"],
                                                "",
                                                "orderby [Time].[Day].Key desc, [Sequence].[Sequence].Key desc",
                                                "limit 1");
                var day = "";
                var sequence = "";
                var elaspedTime = "";
                var startTime = "";
                var endTime = "";
                var errorMessage = "";
                var userName = vdCommon.selectResult('CurrentUser().Name');
                if ( result.cs.rowCount > 0 ) {
                    day = result.cs.row(0).cell(result.cs.memberColumnIndex("Time", "Day")).Name;
                    sequence = result.cs.row(0).cell(result.cs.memberColumnIndex("Sequence", "Sequence")).Name;
                    elaspedTime = result.cs.row(0).cell(result.cs.measureColumnIndex("Python Batch Log_Elasped Time"));
                    startTime = result.cs.row(0).cell(result.cs.measureColumnIndex("Python Batch Log_Start Time"));
                    endTime = result.cs.row(0).cell(result.cs.measureColumnIndex("Python Batch Log_End Time"));
                    errorMessage = result.cs.row(0).cell(result.cs.measureColumnIndex("Python Batch Log_Error Message")) ||"";
                }

                vdCommon.createMeasure(["[Version].[Version Name].[" + fbVersionName + "]",
                                            "[Python Batch].[Python Name].[" + fbPythonName + "]"],
                                        ['Measure.[Python Batch_Error Message] = "' + errorMessage.replace(/\"/g, '\\\"') + '";',
                                            'Measure.[Python Batch_Start Time] = "' + startTime + '";',
                                            'Measure.[Python Batch_End Time] = "' + endTime + '";',
                                            'Measure.[Python Batch_Elasped Time] = ' + elaspedTime + ';',
                                            'Measure.[Python Batch_Avg Elasped Time] = ' + avgElaspedTime + ';']);

                vdCommon.createMeasure(["[Version].[Version Name].[" + fbVersionName + "]",
                                            "[Python Batch].[Python Name].[" + fbPythonName + "]",
                                            "[Time].[Day].[" + day + "]",
                                            "[Sequence].[Sequence].[" + sequence + "]"],
                                        ['Measure.[Python Batch Log_Requester] = "' + fbRequester + '";',
                                            'Measure.[Python Batch Log_Performer] = "' + userName + '";',
                                            'Measure.[Python Batch Log_Request Memo] = "' + fbRequestMemo + '";']);
            } catch ( e ) {
                RuleOutputToUI = { Status : 'Error', Message : "Js Logic Error : " + e.message.replace(/"/g, "'") };
                return;
            }

            vdCommon.programEnd();
        } catch ( e ) {
            RuleOutputToUI = { Status : 'Error', Message : "Js Logic Error : " + e.message };
            return;
        }
    };

    var fn_multiRun = function(o9Params){
        const commonLib = require('o9.NSCM.commonLib');
        const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
        const vdUtil = new commonLib.VdUtil();

        vdCommon.setLogLevel("Debug");

        try {
            vdCommon.printParams(o9Params);

            // 파라미터 가져오기
            var parsedParams = JSON.parse(o9Params);
            var fbVersionName = "CWV_MP";
            var fbSelect = parsedParams.fbSelect;
            var fbRequester = parsedParams.fbRequester;
            var fbRequestMemo = parsedParams.fbRequestMemo;
            var userName = vdCommon.selectResult('CurrentUser().Name');

            for ( var i = 0; i < fbSelect.length; i++ ) {
                var row = fbSelect[i];

                var errorMessage = "";
                var result = vdCommon.selectList(["[Version].[Version Name].[" + fbVersionName + "]",
                                                        "[Python Batch].[Python Name].[" + row.PythonName.Value + "]"],
                                                    ["Measure.[Python Batch_Measures]",
                                                        "Measure.[Python Batch_Scope]",
                                                        "Measure.[Python Batch_Arguments]"],
                                                    "",
                                                    "",
                                                    "");
                vdCommon.printCsData(result, 3);

                var measures = result.cs.row(0).cell(result.cs.measureColumnIndex("Python Batch_Measures"));
                var scope = result.cs.row(0).cell(result.cs.measureColumnIndex("Python Batch_Scope"));
                var argument = result.cs.row(0).cell(result.cs.measureColumnIndex("Python Batch_Arguments"));

                // 파이썬 실행
                try {
                    if ( argument != "" ) {
                        argument += ", ";
                    }

                    var execQuery = 'EXEC plugin instance [' + row.PythonName.Value + '] ' +
                                    'for measures {' + measures + '} ' +
                                    'using scope ( ' + scope + ' ) ' +
                                    'using arguments {' + argument + '(ExecutionMode, "MediumWeight"), (MaxSliceTableCells, 200000000), (MaxConcurrency, 1 )};'
                    vdCommon.executeQuery("Python Batch Run", execQuery);

                    // 평균 시간을 가져온다.
                    result = vdCommon.selectList(["[Version].[Version Name].[" + fbVersionName + "]",
                                                            "[Python Batch].[Python Name].[" + row.PythonName.Value + "]"],
                                                        ["Measure.[Python Batch Log_Elasped Time]"],
                                                        "",
                                                        "",
                                                        "");
                    var avgElaspedTime = 0;
                    if ( result.cs.rowCount > 0 ) {
                        avgElaspedTime = result.cs.row(0).cell(result.cs.measureColumnIndex("Python Batch Log_Elasped Time"));
                    }

                    // 마지막 결과를 가져온다.
                    result = vdCommon.selectList(["[Version].[Version Name].[" + fbVersionName + "]",
                                                        "[Python Batch].[Python Name].[" + row.PythonName.Value + "]"
                                                        ,"[Time].[Day]"
                                                        ,"[Sequence].[Sequence]"],
                                                    ["Measure.[Python Batch Log_Elasped Time]"
                                                        ,"Measure.[Python Batch Log_Start Time]"
                                                        ,"Measure.[Python Batch Log_End Time]"
                                                        ,"Measure.[Python Batch Log_Error Message]"],
                                                    "",
                                                    "orderby [Time].[Day].Key desc, [Sequence].[Sequence].Key desc",
                                                    "limit 1");
                    var day = "";
                    var sequence = "";
                    var elaspedTime = "";
                    var startTime = "";
                    var endTime = "";
                    var errorMessage = "";
                    if ( result.cs.rowCount > 0 ) {
                        day = result.cs.row(0).cell(result.cs.memberColumnIndex("Time", "Day")).Name;
                        sequence = result.cs.row(0).cell(result.cs.memberColumnIndex("Sequence", "Sequence")).Name;
                        elaspedTime = result.cs.row(0).cell(result.cs.measureColumnIndex("Python Batch Log_Elasped Time"));
                        startTime = result.cs.row(0).cell(result.cs.measureColumnIndex("Python Batch Log_Start Time"));
                        endTime = result.cs.row(0).cell(result.cs.measureColumnIndex("Python Batch Log_End Time"));
                        errorMessage = result.cs.row(0).cell(result.cs.measureColumnIndex("Python Batch Log_Error Message")) ||"";
                    }

                    vdCommon.createMeasure(["[Version].[Version Name].[" + fbVersionName + "]",
                                                "[Python Batch].[Python Name].[" + row.PythonName.Value + "]"],
                                            ['Measure.[Python Batch_Error Message] = "' + errorMessage.replace(/\"/g, '\\\"') + '";',
                                                'Measure.[Python Batch_Start Time] = "' + startTime + '";',
                                                'Measure.[Python Batch_End Time] = "' + endTime + '";',
                                                'Measure.[Python Batch_Elasped Time] = ' + elaspedTime + ';',
                                                'Measure.[Python Batch_Avg Elasped Time] = ' + avgElaspedTime + ';']);

                    vdCommon.createMeasure(["[Version].[Version Name].[" + fbVersionName + "]",
                                                "[Python Batch].[Python Name].[" + row.PythonName.Value + "]",
                                                "[Time].[Day].[" + day + "]",
                                                "[Sequence].[Sequence].[" + sequence + "]"],
                                            ['Measure.[Python Batch Log_Requester] = "' + fbRequester + '";',
                                                'Measure.[Python Batch Log_Performer] = "' + userName + '";',
                                                'Measure.[Python Batch Log_Request Memo] = "' + fbRequestMemo + '";']);
                } catch ( e ) {
                    RuleOutputToUI = { Status : 'Error', Message : "Js Logic Error : " + e.message.replace(/"/g, "'") };
                    return;
                }
            }

            vdCommon.programEnd();
        } catch ( e ) {
            RuleOutputToUI = { Status : 'Error', Message : "Js Logic Error : " + e.message };
            return;
        }
    };

    var fn_deleteB = function(o9Params){
        const commonLib = require('o9.NSCM.commonLib');
        const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
        vdCommon.setLogLevel("Debug");

        try {
            vdCommon.printParams(o9Params);

            // 파라미터 가져오기
            var parsedParams = JSON.parse(o9Params);
            var fbSelect = parsedParams.fbSelect;
            var fbVersionName = "CWV_MP";

            for ( var i = 0; i < fbSelect.length; i++ ) {
                var row = fbSelect[i];

                var where = [];
                where.push("[Version].[Version Name].[" + fbVersionName + "]");
                where.push("[Sequence].[Sequence].[" + row.Sequence.Value + "]");
                where.push("[Python Batch].[Python Name].[" + row.PythonName.Value + "]");

                vdCommon.deleteMeasure(where, "Python Batch Log");
            }

            vdCommon.programEnd();
        } catch ( e ) {
            RuleOutputToUI = { Status : 'Error', Message : "Js Logic Error : " + e.message };
            return;
        }
    };

    return {
        fn_add : fn_add,
        fn_delete : fn_delete,
        fn_run : fn_run,
        fn_multiRun : fn_multiRun,
        fn_deleteB : fn_deleteB
    };
});

/**************************** o9.NSCM.JSPythonBatch ****************************
    2025-02-26 : Version 은 CWV_MP로 고정한다. Filter 에서 제외
    2025-03-11 : 파이썬은 실행만 하도록 한다.
    2026-01-27 : 배치 실행후에 마지막 결과를 넣도록 수정
*********************************************************************/define('o9.NSCM.JSPythonBatch', ['o9/data/query', 'o9/data/cellset', 'o9.NSCM.commonLib'], function () {
    const programName = "o9.NSCM.JSPythonBatch";

    var fn_add = function(o9Params){
        const commonLib = require('o9.NSCM.commonLib');
        const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
        vdCommon.setLogLevel("Debug");

        try {
            vdCommon.printParams(o9Params);

            // 파라미터 가져오기
            var parsedParams = JSON.parse(o9Params);
            var fbVersionName = "CWV_MP";
            var fbPythonName = parsedParams.fbPythonName;
            var fbDesc = parsedParams.fbDesc;
            var fbMeasures = parsedParams.fbMeasures;
            var fbScope = parsedParams.fbScope;
            var fbArguments = parsedParams.fbArguments;
            var fbManager = parsedParams.fbManager;
            var fbDeveloper = parsedParams.fbDeveloper;

            if ( !vdCommon.existDimension(['[Python Batch].[Python Name].[' + fbPythonName + ']']) ) {
                vdCommon.createDimension(['[Python Batch].[Python Name]'], [fbPythonName]);
            }

            var isExist = vdCommon.existMeasure(["[Version].[Version Name].[" + fbVersionName + "]",
                                                    "[Python Batch].[Python Name].[" + fbPythonName + "]"],
                                                ["Measure.[Python Batch_Measures]"],
                                                "");
            if ( isExist ) {
                RuleOutputToUI = { Status : 'Error', Message : "This Data has already been registered." };
                return;
            } else {
                vdCommon.createMeasure(["[Version].[Version Name].[" + fbVersionName + "]",
                                            "[Python Batch].[Python Name].[" + fbPythonName + "]"],
                                       ['Measure.[Python Batch_Desc] = "' + fbDesc + '";',
                                            'Measure.[Python Batch_Measures] = "' + fbMeasures + '";',
                                            'Measure.[Python Batch_Scope] = "' + fbScope + '";',
                                            'Measure.[Python Batch_Arguments] = "' + fbArguments.replace(/\"/g, '\\\"') + '";',
                                            'Measure.[Python Batch_Manager] = "' + fbManager + '";',
                                            'Measure.[Python Batch_Developer] = "' + fbDeveloper + '";']);
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

            // 파라미터 가져오기
            var parsedParams = JSON.parse(o9Params);
            var fbSelect = parsedParams.fbSelect;
            var fbVersionName = "CWV_MP";

            for ( var i = 0; i < fbSelect.length; i++ ) {
                var row = fbSelect[i];

                var where = [];
                where.push("[Version].[Version Name].[" + fbVersionName + "]");
                where.push("[Python Batch].[Python Name].[" + row.PythonName.Value + "]");

                vdCommon.deleteMeasure(where, "Python Batch");
            }

            vdCommon.programEnd();
        } catch ( e ) {
            RuleOutputToUI = { Status : 'Error', Message : "Js Logic Error : " + e.message };
            return;
        }
    };

    var fn_run = function(o9Params){
        const commonLib = require('o9.NSCM.commonLib');
        const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
        const vdUtil = new commonLib.VdUtil();

        vdCommon.setLogLevel("Debug");

        try {
            vdCommon.printParams(o9Params);

            // 파라미터 가져오기
            var parsedParams = JSON.parse(o9Params);
            var fbVersionName = "CWV_MP";
            var fbPythonName = parsedParams.fbPythonName;
            var fbMeasures = parsedParams.fbMeasures;
            var fbScope = parsedParams.fbScope;
            var fbArguments = parsedParams.fbArguments;
            var fbRequester = parsedParams.fbRequester;
            var fbRequestMemo = parsedParams.fbRequestMemo;

            // 파이썬 실행
            try {
                if ( fbArguments != "" ) {
                    fbArguments += ", ";
                }

                var execQuery = 'EXEC plugin instance [' + fbPythonName + '] ' +
                                'for measures {' + fbMeasures + '} ' +
                                'using scope ( ' + fbScope + ' ) ' +
                                'using arguments {' + fbArguments + '(ExecutionMode, "MediumWeight"), (MaxSliceTableCells, 200000000), (MaxConcurrency, 1 )};'
                vdCommon.executeQuery("Python Batch Run", execQuery);

                // 평균 시간을 가져온다.
                result = vdCommon.selectList(["[Version].[Version Name].[" + fbVersionName + "]",
                                                        "[Python Batch].[Python Name].[" + fbPythonName + "]"],
                                                    ["Measure.[Python Batch Log_Elasped Time]"],
                                                    "",
                                                    "",
                                                    "");
                var avgElaspedTime = 0;
                if ( result.cs.rowCount > 0 ) {
                    avgElaspedTime = result.cs.row(0).cell(result.cs.measureColumnIndex("Python Batch Log_Elasped Time"));
                }

                // 마지막 결과를 가져온다.
                result = vdCommon.selectList(["[Version].[Version Name].[" + fbVersionName + "]",
                                                    "[Python Batch].[Python Name].[" + fbPythonName + "]"
                                                    ,"[Time].[Day]"
                                                    ,"[Sequence].[Sequence]"],
                                                ["Measure.[Python Batch Log_Elasped Time]"
                                                    ,"Measure.[Python Batch Log_Start Time]"
                                                    ,"Measure.[Python Batch Log_End Time]"
                                                    ,"Measure.[Python Batch Log_Error Message]"],
                                                "",
                                                "orderby [Time].[Day].Key desc, [Sequence].[Sequence].Key desc",
                                                "limit 1");
                var day = "";
                var sequence = "";
                var elaspedTime = "";
                var startTime = "";
                var endTime = "";
                var errorMessage = "";
                var userName = vdCommon.selectResult('CurrentUser().Name');
                if ( result.cs.rowCount > 0 ) {
                    day = result.cs.row(0).cell(result.cs.memberColumnIndex("Time", "Day")).Name;
                    sequence = result.cs.row(0).cell(result.cs.memberColumnIndex("Sequence", "Sequence")).Name;
                    elaspedTime = result.cs.row(0).cell(result.cs.measureColumnIndex("Python Batch Log_Elasped Time"));
                    startTime = result.cs.row(0).cell(result.cs.measureColumnIndex("Python Batch Log_Start Time"));
                    endTime = result.cs.row(0).cell(result.cs.measureColumnIndex("Python Batch Log_End Time"));
                    errorMessage = result.cs.row(0).cell(result.cs.measureColumnIndex("Python Batch Log_Error Message")) ||"";
                }

                vdCommon.createMeasure(["[Version].[Version Name].[" + fbVersionName + "]",
                                            "[Python Batch].[Python Name].[" + fbPythonName + "]"],
                                        ['Measure.[Python Batch_Error Message] = "' + errorMessage.replace(/\"/g, '\\\"') + '";',
                                            'Measure.[Python Batch_Start Time] = "' + startTime + '";',
                                            'Measure.[Python Batch_End Time] = "' + endTime + '";',
                                            'Measure.[Python Batch_Elasped Time] = ' + elaspedTime + ';',
                                            'Measure.[Python Batch_Avg Elasped Time] = ' + avgElaspedTime + ';']);

                vdCommon.createMeasure(["[Version].[Version Name].[" + fbVersionName + "]",
                                            "[Python Batch].[Python Name].[" + fbPythonName + "]",
                                            "[Time].[Day].[" + day + "]",
                                            "[Sequence].[Sequence].[" + sequence + "]"],
                                        ['Measure.[Python Batch Log_Requester] = "' + fbRequester + '";',
                                            'Measure.[Python Batch Log_Performer] = "' + userName + '";',
                                            'Measure.[Python Batch Log_Request Memo] = "' + fbRequestMemo + '";']);
            } catch ( e ) {
                RuleOutputToUI = { Status : 'Error', Message : "Js Logic Error : " + e.message.replace(/"/g, "'") };
                return;
            }

            vdCommon.programEnd();
        } catch ( e ) {
            RuleOutputToUI = { Status : 'Error', Message : "Js Logic Error : " + e.message };
            return;
        }
    };

    var fn_multiRun = function(o9Params){
        const commonLib = require('o9.NSCM.commonLib');
        const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
        const vdUtil = new commonLib.VdUtil();

        vdCommon.setLogLevel("Debug");

        try {
            vdCommon.printParams(o9Params);

            // 파라미터 가져오기
            var parsedParams = JSON.parse(o9Params);
            var fbVersionName = "CWV_MP";
            var fbSelect = parsedParams.fbSelect;
            var fbRequester = parsedParams.fbRequester;
            var fbRequestMemo = parsedParams.fbRequestMemo;
            var userName = vdCommon.selectResult('CurrentUser().Name');

            for ( var i = 0; i < fbSelect.length; i++ ) {
                var row = fbSelect[i];

                var errorMessage = "";
                var result = vdCommon.selectList(["[Version].[Version Name].[" + fbVersionName + "]",
                                                        "[Python Batch].[Python Name].[" + row.PythonName.Value + "]"],
                                                    ["Measure.[Python Batch_Measures]",
                                                        "Measure.[Python Batch_Scope]",
                                                        "Measure.[Python Batch_Arguments]"],
                                                    "",
                                                    "",
                                                    "");
                vdCommon.printCsData(result, 3);

                var measures = result.cs.row(0).cell(result.cs.measureColumnIndex("Python Batch_Measures"));
                var scope = result.cs.row(0).cell(result.cs.measureColumnIndex("Python Batch_Scope"));
                var argument = result.cs.row(0).cell(result.cs.measureColumnIndex("Python Batch_Arguments"));

                // 파이썬 실행
                try {
                    if ( argument != "" ) {
                        argument += ", ";
                    }

                    var execQuery = 'EXEC plugin instance [' + row.PythonName.Value + '] ' +
                                    'for measures {' + measures + '} ' +
                                    'using scope ( ' + scope + ' ) ' +
                                    'using arguments {' + argument + '(ExecutionMode, "MediumWeight"), (MaxSliceTableCells, 200000000), (MaxConcurrency, 1 )};'
                    vdCommon.executeQuery("Python Batch Run", execQuery);

                    // 평균 시간을 가져온다.
                    result = vdCommon.selectList(["[Version].[Version Name].[" + fbVersionName + "]",
                                                            "[Python Batch].[Python Name].[" + row.PythonName.Value + "]"],
                                                        ["Measure.[Python Batch Log_Elasped Time]"],
                                                        "",
                                                        "",
                                                        "");
                    var avgElaspedTime = 0;
                    if ( result.cs.rowCount > 0 ) {
                        avgElaspedTime = result.cs.row(0).cell(result.cs.measureColumnIndex("Python Batch Log_Elasped Time"));
                    }

                    // 마지막 결과를 가져온다.
                    result = vdCommon.selectList(["[Version].[Version Name].[" + fbVersionName + "]",
                                                        "[Python Batch].[Python Name].[" + row.PythonName.Value + "]"
                                                        ,"[Time].[Day]"
                                                        ,"[Sequence].[Sequence]"],
                                                    ["Measure.[Python Batch Log_Elasped Time]"
                                                        ,"Measure.[Python Batch Log_Start Time]"
                                                        ,"Measure.[Python Batch Log_End Time]"
                                                        ,"Measure.[Python Batch Log_Error Message]"],
                                                    "",
                                                    "orderby [Time].[Day].Key desc, [Sequence].[Sequence].Key desc",
                                                    "limit 1");
                    var day = "";
                    var sequence = "";
                    var elaspedTime = "";
                    var startTime = "";
                    var endTime = "";
                    var errorMessage = "";
                    if ( result.cs.rowCount > 0 ) {
                        day = result.cs.row(0).cell(result.cs.memberColumnIndex("Time", "Day")).Name;
                        sequence = result.cs.row(0).cell(result.cs.memberColumnIndex("Sequence", "Sequence")).Name;
                        elaspedTime = result.cs.row(0).cell(result.cs.measureColumnIndex("Python Batch Log_Elasped Time"));
                        startTime = result.cs.row(0).cell(result.cs.measureColumnIndex("Python Batch Log_Start Time"));
                        endTime = result.cs.row(0).cell(result.cs.measureColumnIndex("Python Batch Log_End Time"));
                        errorMessage = result.cs.row(0).cell(result.cs.measureColumnIndex("Python Batch Log_Error Message")) ||"";
                    }

                    vdCommon.createMeasure(["[Version].[Version Name].[" + fbVersionName + "]",
                                                "[Python Batch].[Python Name].[" + row.PythonName.Value + "]"],
                                            ['Measure.[Python Batch_Error Message] = "' + errorMessage.replace(/\"/g, '\\\"') + '";',
                                                'Measure.[Python Batch_Start Time] = "' + startTime + '";',
                                                'Measure.[Python Batch_End Time] = "' + endTime + '";',
                                                'Measure.[Python Batch_Elasped Time] = ' + elaspedTime + ';',
                                                'Measure.[Python Batch_Avg Elasped Time] = ' + avgElaspedTime + ';']);

                    vdCommon.createMeasure(["[Version].[Version Name].[" + fbVersionName + "]",
                                                "[Python Batch].[Python Name].[" + row.PythonName.Value + "]",
                                                "[Time].[Day].[" + day + "]",
                                                "[Sequence].[Sequence].[" + sequence + "]"],
                                            ['Measure.[Python Batch Log_Requester] = "' + fbRequester + '";',
                                                'Measure.[Python Batch Log_Performer] = "' + userName + '";',
                                                'Measure.[Python Batch Log_Request Memo] = "' + fbRequestMemo + '";']);
                } catch ( e ) {
                    RuleOutputToUI = { Status : 'Error', Message : "Js Logic Error : " + e.message.replace(/"/g, "'") };
                    return;
                }
            }

            vdCommon.programEnd();
        } catch ( e ) {
            RuleOutputToUI = { Status : 'Error', Message : "Js Logic Error : " + e.message };
            return;
        }
    };

    var fn_deleteB = function(o9Params){
        const commonLib = require('o9.NSCM.commonLib');
        const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
        vdCommon.setLogLevel("Debug");

        try {
            vdCommon.printParams(o9Params);

            // 파라미터 가져오기
            var parsedParams = JSON.parse(o9Params);
            var fbSelect = parsedParams.fbSelect;
            var fbVersionName = "CWV_MP";

            for ( var i = 0; i < fbSelect.length; i++ ) {
                var row = fbSelect[i];

                var where = [];
                where.push("[Version].[Version Name].[" + fbVersionName + "]");
                where.push("[Sequence].[Sequence].[" + row.Sequence.Value + "]");
                where.push("[Python Batch].[Python Name].[" + row.PythonName.Value + "]");

                vdCommon.deleteMeasure(where, "Python Batch Log");
            }

            vdCommon.programEnd();
        } catch ( e ) {
            RuleOutputToUI = { Status : 'Error', Message : "Js Logic Error : " + e.message };
            return;
        }
    };

    return {
        fn_add : fn_add,
        fn_delete : fn_delete,
        fn_run : fn_run,
        fn_multiRun : fn_multiRun,
        fn_deleteB : fn_deleteB
    };
});

/**************************** o9.NSCM.JSPythonBatch ****************************
    2025-02-26 : Version 은 CWV_MP로 고정한다. Filter 에서 제외
    2025-03-11 : 파이썬은 실행만 하도록 한다.
    2026-01-27 : 배치 실행후에 마지막 결과를 넣도록 수정
*********************************************************************/