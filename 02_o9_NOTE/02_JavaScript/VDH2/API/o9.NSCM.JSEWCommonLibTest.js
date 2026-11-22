define('o9.NSCM.JSEWCommonLibTest', ['o9/data/query', 'o9/data/cellset', 'o9.NSCM.commonLibVD'
                                        ,'o9.NSCM.JSDailyTimeRolling'
                                        ,'o9.NSCM.JSPlanCycleRollingPreConfigured'
                                        ,'o9.NSCM.JSWhatIfScenarioCreation'
                                        ,'o9.NSCM.JSPlanCycleRollingBackupAdd'], function () {

/**************************************************************************************
    프로그램명  : o9.NSCM.JSEWCommonLibTest
    화면명     : CommonLibTest
    화면 개발자 :
    API 개발자 : sungmin0.lim
    최초생성   : 2025.1118
**************************************************************************************/

	const programName = "o9.NSCM.JSEWCommonLibTest";
    const commonLib = require('o9.NSCM.commonLibVD');
    const vdUtil = new commonLib.VdUtil();

/************************************************* UI Call Common Logic *************************************************/
	var fn_loadFunction = function(o9Params){
        const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
        vdCommon.setLogLevel("Debug");

		try {
            let returnData = {};
            let obj = this;

            vdCommon.printParams(o9Params);

            // 파라메타 가져오기
            var parsedParams = JSON.parse(o9Params);
			var fbFuncName = parsedParams.fbFuncName;

            if ( functionMap[fbFuncName] == undefined ) {
                return { "Code" : 1, "Msg" : "No Function" };
            }

            if ( parsedParams["fbParams"] == undefined ) {
                parsedParams["fbParams"] = {};
            }

            var rtn = functionMap[fbFuncName](parsedParams);

            vdCommon.programEnd();
            return rtn;
        } catch ( e ) {
            return { "Code" : -1, "Msg" : e.message };
        }
	};

/************************************************* common logic *************************************************/
    /*
        vdUtil.fn_getDimPropertyValue 테스트
        { "fbFuncName" : "fn_test251118"}
    */
    var fn_test251118 = function(parsedParams){
        const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
        vdCommon.setLogLevel("Debug");

		try {
		    var result = vdCommon.selectList(["[Version].[Version Name].[CWV_MP]"], [], "", "", "");
            for ( var i = 0; i < result.cs.rowCount; i++ ) {
                vdCommon.debug("fn_getDimValue : " + vdUtil.fn_getDimValue(result, i, "Version", "Version Name"));
                vdCommon.debug("fn_getDimPropertyValue : " + vdUtil.fn_getDimPropertyValue(result, i, "Version", "Version Name", "Version Created By"));
            }

            vdCommon.programEnd();

            return { "Code" : 0, "Msg" : "fn_test251118 OK" };
        } catch ( e ) {
            vdCommon.error(e.message);
            return { "Code" : -1, "Msg" : e.message };
        }
    };

    /*
        콤보에 - 이 나오는지 테스트
        { "fbFuncName" : "fn_test251125"}
    */
    var fn_test251125 = function(parsedParams){
        const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
        vdCommon.setLogLevel("Debug");

		try {
		    var result = vdCommon.selectList(["[Version].[Version Name]"], [], "", "", "");

            var comboList = vdCommon.fn_makeCombo(result, {DimName : "Version", DimAttbName : "Version Name", Sort : "DisplayName",
                                                    existHyphen : true});
            vdCommon.debug("ComboData : " + JSON.stringify(comboList.slice(0,3)));

            vdCommon.programEnd();

            return { "Code" : 0, "Msg" : "fn_test251118 OK", rtn : comboList };
        } catch ( e ) {
            vdCommon.error(e.message);
            return { "Code" : -1, "Msg" : e.message };
        }
    };

    /*
        콤보에 ALL 이 나오는지 테스트
        { "fbFuncName" : "fn_test251126"}
    */
    var fn_test251126 = function(parsedParams){
        const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
        vdCommon.setLogLevel("Debug");

		try {
		    var result = vdCommon.selectList(["[Version].[Version Name]"], [], "", "", "");

            var comboList = vdCommon.fn_makeCombo(result, {DimName : "Version", DimAttbName : "Version Name", Sort : "DisplayName",
                                                    existALL : true});
            vdCommon.debug("ComboData : " + JSON.stringify(comboList.slice(0,3)));

            vdCommon.programEnd();

            return { "Code" : 0, "Msg" : "fn_test251118 OK", rtn : comboList };
        } catch ( e ) {
            vdCommon.error(e.message);
            return { "Code" : -1, "Msg" : e.message };
        }
    };

    /*
        콤보에 ALL 이 나오는지 테스트
        { "fbFuncName" : "fn_test251126_2"}
    */
    var fn_test251126_2 = function(parsedParams){
        const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
        vdCommon.setLogLevel("Debug");

		try {
            vdCommon.debug("fn_getDivision : " + vdCommon.fn_getDivision());

		    var result = vdCommon.selectList(["[Location].[Location]"], [], "", "", "limit 100");

            var comboList = vdCommon.fn_makeCombo(result, {DimName : "Location", DimAttbName : "Location", Sort : "DisplayName",
                                                    existALL : true});
            vdCommon.debug("ComboData : " + JSON.stringify(comboList.slice(0,3)));

            vdCommon.programEnd();

            return { "Code" : 0, "Msg" : "fn_test251126_2 OK", rtn : comboList };
        } catch ( e ) {
            vdCommon.error(e.message);
            return { "Code" : -1, "Msg" : e.message };
        }
    };

    /*
        웹호출을 할 수없네.....
        { "fbFuncName" : "fn_log_test"}
    */
    var fn_log_test = function(parsedParams){
        const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
        vdCommon.setLogLevel("Debug");

		try {
		    function getUrlText(url) {
                const xhr = new XMLHttpRequest();
                xhr.open('GET', url, false); // 세 번째 인자를 false로 설정하여 동기화
                xhr.send(null); // 요청을 보내고 응답을 받을 때까지 대기

                if (xhr.status === 200) {
                    return JSON.parse(xhr.responseText);
                } else {
                    return null;
                }
            }

            // RId 가져오기
            var json = getUrlText("https://nscm.sec.samsung.net/api/logs?tenantId=5233&timestamp=2025-12-01T00%3A00%3A00.000Z&message=Query%20Received.*EXEC%20PROCEDURE%20RunLPSWeeklyScopedbytheProductGroup&messageSearchByRegex=true&id=692c9a8c4c5e4dd8e6db5bf1&_=1764554007651");
            console.log(json);
            var rid = json[0].RId;
            console.log(rid);
            json = getUrlText("https://nscm.sec.samsung.net/api/logs?tenantId=5233&message=Successfully%20pulled%20data%20from%20S3&rId=" + rid + "&messageSearchByRegex=false&id=692c911815aeaa1393dd9f65&_=1764549944985");
            var time1 = json[0].Timestamp;
            console.log(time1);
            json = getUrlText("https://nscm.sec.samsung.net/api/logs?tenantId=5233&message=Started%20Solver%20Optimization%20Process&rId=" + rid + "&messageSearchByRegex=false&id=692c911815aeaa1393dd9f65&_=1764549944985");
            var time2 = json[0].Timestamp;
            console.log(time2);
            json = getUrlText("https://nscm.sec.samsung.net/api/logs?tenantId=5233&message=Completed%20Solver%20Optimization%20Process&rId=" + rid + "&messageSearchByRegex=false&id=692c911815aeaa1393dd9f65&_=1764549944985");
            var time3 = json[0].Timestamp;
            console.log(time3);
            json = getUrlText("https://nscm.sec.samsung.net/api/logs?tenantId=5233&message=CPU%20TIME&rId=" + rid + "&messageSearchByRegex=false&id=692c911815aeaa1393dd9f65&_=1764549944985");
            var time4 = json[0].Timestamp;
            console.log(time4);
            console.log(json[0].Message);

            return { "Code" : 0, "Msg" : "fn_log_test OK" };
        } catch ( e ) {
            vdCommon.error(e.message);
            return { "Code" : -1, "Msg" : e.message };
        }
    };

    /*
        o9.NSCM.JSDailyTimeRolling AB 호출
        { "fbFuncName" : "fn_JSDailyTimeRolling", "fbParams" : { }}
        { "fbFuncName" : "fn_JSDailyTimeRolling", "fbParams" : { "fbCurrentDate" : "2025-12-03" }}
    */
    var fn_JSDailyTimeRolling = function(parsedParams){
        const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
        vdCommon.setLogLevel("Debug");

		try {
            var jsModule = require('o9.NSCM.JSDailyTimeRolling');
            jsModule.dailyTimeRolling(JSON.stringify(parsedParams.fbParams));

            vdCommon.programEnd();

            return { "Code" : 0, "Msg" : "fn_JSDailyTimeRolling OK" };
        } catch ( e ) {
            vdCommon.error(e.message);
            return { "Code" : -1, "Msg" : e.message };
        }
    };

    /*
        o9.NSCM.JSPlanCycleRollingPreConfigured AB 호출
        { "fbFuncName" : "fn_JSPlanCycleRollingPreConfigured", "fbParams" : { "PlanType" : "MP-Pre" } }
        { "fbFuncName" : "fn_JSPlanCycleRollingPreConfigured", "fbParams" : { "PlanType" : "MP-Main" } }
    */
    var fn_JSPlanCycleRollingPreConfigured = function(parsedParams){
        const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
        vdCommon.setLogLevel("Debug");

		try {
            var jsModule = require('o9.NSCM.JSPlanCycleRollingPreConfigured');
            jsModule.planCycleRollingPreConfigured(JSON.stringify(parsedParams.fbParams));

            vdCommon.programEnd();

            return { "Code" : 0, "Msg" : "fn_JSPlanCycleRollingPreConfigured OK" };
        } catch ( e ) {
            vdCommon.error(e.message);
            return { "Code" : -1, "Msg" : e.message };
        }
    };

    /*
        fn_qMeaStr 기능 테스트
        { "fbFuncName" : "fn_test251209"}
    */
    var fn_test251209 = function(parsedParams){
        const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
        vdCommon.setLogLevel("Debug");

		try {
            vdCommon.updateMeasure(["[Version].[Version Name].[CWV_MP]"
                                       ,"[Location].[Location].[P551]"
                                       ,"[Item Material].[MSL4].[Elec.>Elec.>SMPS>Adaptor]"]
                                    ,[vdUtil.fn_qMeaStr(null, "Measure.[SS Mtrl L4_ECP Flag]", null)]);

            vdCommon.updateMeasure(["[Version].[Version Name].[CWV_MP]"
                                       ,"[Location].[Location].[P551]"
                                       ,"[Item Material].[MSL4].[Elec.>Elec.>SMPS>Adaptor]"]
                                    ,[vdUtil.fn_qMeaStr(null, "Measure.[SS Mtrl L4_ECP Flag]", "on")]);

            vdCommon.updateMeasure(["[Version].[Version Name].[CWV_MP]"
                                       ,"[Group].[Group ID].[BAL_00003]"
                                       ,"[Time].[Week].[202504]"]
                                    ,[vdUtil.fn_qMeaNotStr(null, "Measure.[Build Ahead Group W_Period]", null)]);

            vdCommon.updateMeasure(["[Version].[Version Name].[CWV_MP]"
                                       ,"[Group].[Group ID].[BAL_00003]"
                                       ,"[Time].[Week].[202504]"]
                                    ,[vdUtil.fn_qMeaNotStr(null, "Measure.[Build Ahead Group W_Period]", 1)]);

            vdCommon.updateMeasure(["[Version].[Version Name].[CWV_MP]"
                                       ,"[Group].[Group ID].[BAL_00003]"
                                       ,"[Time].[Week].[202504]"]
                                    ,[vdUtil.fn_qMeaInt(null, "Measure.[Build Ahead Group W_Period]", null)]);

            vdCommon.updateMeasure(["[Version].[Version Name].[CWV_MP]"
                                       ,"[Group].[Group ID].[BAL_00003]"
                                       ,"[Time].[Week].[202504]"]
                                    ,[vdUtil.fn_qMeaInt(null, "Measure.[Build Ahead Group W_Period]", 1)]);

            vdCommon.programEnd();

            return { "Code" : 0, "Msg" : "fn_test251209 OK" };
        } catch ( e ) {
            vdCommon.error(e.message);
            return { "Code" : -1, "Msg" : e.message };
        }
    };

    /*
        o9.NSCM.JSWhatIfScenarioCreation AB 호출
        { "fbFuncName" : "fn_JSWhatIfScenarioCreation", "fbParams" : { "fbVersion" : "202545_P" }}
    */
    var fn_JSWhatIfScenarioCreation = function(parsedParams){
        const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
        vdCommon.setLogLevel("Debug");

		try {
            var jsModule = require('o9.NSCM.JSWhatIfScenarioCreation');
            jsModule.jsRun(JSON.stringify(parsedParams.fbParams));

            vdCommon.programEnd();

            return { "Code" : 0, "Msg" : "fn_JSWhatIfScenarioCreation OK" };
        } catch ( e ) {
            vdCommon.error(e.message);
            return { "Code" : -1, "Msg" : e.message };
        }
    };

    /*
        Item 정규식 검색 구현 : QE55Q75BATXZT
        { "fbFuncName" : "fn_260126", "fbParams" : { "item" : "QE55Q75%" }}
        { "fbFuncName" : "fn_260126", "fbParams" : { "item" : "%75BATXZT" }}
        { "fbFuncName" : "fn_260126", "fbParams" : { "item" : "%55Q%TX%" }}
        { "fbFuncName" : "fn_260126", "fbParams" : { "item" : "QE55%75B%TX%T" }}
    */
    var fn_260126 = function(parsedParams){
        const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
        vdCommon.setLogLevel("Debug");

		try {
		    function fn_filterStr(val) {
                if ( (val.match(/%/g) || []).length > 0 ) {
                    // 26.1.26 : % 가 들어간 경우는 정규식을 활용하도록 로직 추가
                    var prefix = "";
                    var postfix = "";
                    if ( val.indexOf("%") == 0 && val.lastIndexOf("%") == val.length - 1 ) {
                        val = val.substr(1, val.length - 2);
                    }
                    if ( val.indexOf("%") == 0 ) {
                        postfix = "$";
                        val = val.substr(1);
                    }
                    if ( val.lastIndexOf("%") == val.length - 1 ) {
                        prefix = "^";
                        val = val.substr(0, val.length - 2);
                    }

                    return '.filter(#.Name containsregexp "' + prefix + val.replace(/%/g,".*") + postfix + '")';
                } else {
                    return "";
                }
            }

            var result = vdCommon.selectList(["[Item].[Item]" + fn_filterStr(parsedParams.fbParams.item)], [], "", "", "limit 100");

            var comboList = vdCommon.fn_makeCombo(result, {DimName : "Item", DimAttbName : "Item", Sort : "DisplayName"});
            vdCommon.debug("ComboData : " + JSON.stringify(comboList.slice(0,3)));

            vdCommon.programEnd();

            return { "Code" : 0, "Msg" : "fn_260126 OK", rtn : comboList };
        } catch ( e ) {
            vdCommon.error(e.message);
            return { "Code" : -1, "Msg" : e.message };
        }
    };

    /*
        o9.NSCM.JSPlanCycleRollingBackupAdd 호출
        { "fbFuncName" : "fn_260209", "fbParams" : { "Version" : "202545_P", "PlanType" : "MP-Pre", "TargetVersion" : "" }}
        { "fbFuncName" : "fn_260209", "fbParams" : { "Version" : "202545_P", "PlanType" : "MP-Main", "TargetVersion" : "" }}
        { "fbFuncName" : "fn_260209", "fbParams" : { "Version" : "202545_P", "PlanType" : "MP-Sync", "TargetVersion" : "" }}
    */
    var fn_260209 = function(parsedParams){
        const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
        vdCommon.setLogLevel("Debug");

		try {
            var jsModule = require('o9.NSCM.JSPlanCycleRollingBackupAdd');
            jsModule.planCycleRollingAdd(JSON.stringify(parsedParams.fbParams));

            vdCommon.programEnd();

            return { "Code" : 0, "Msg" : "JSPlanCycleRollingAdd_NewTest OK" };
        } catch ( e ) {
            vdCommon.error(e.message);
            return { "Code" : -1, "Msg" : e.message };
        }
    };

    /*
        fn_qDimVersionName 테스트
        { "fbFuncName" : "fn_260209", "fbParams" : { "[Version].[Version Name]" : "CWV_MP" } }
        { "fbFuncName" : "fn_260209", "fbParams" : { "filters" : { "[Version].[Version Name]" : {"SelectedMembers" : ["CWV_MP"], "MemberFilter" : ""} } } }
    */
    var fn_260303 = function(parsedParams){
        const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
        vdCommon.setLogLevel("Debug");

		try {
            vdCommon.debug("Version : " + vdUtil.fn_qDimVersionName(parsedParams));

            vdCommon.programEnd();

            return { "Code" : 0, "Msg" : "fn_260303 OK" };
        } catch ( e ) {
            vdCommon.error(e.message);
            return { "Code" : -1, "Msg" : e.message };
        }
    };





/************************************************* util logic *************************************************/

/************************************************* Mapping logic **********************************************/
    // Mapping 함수 정의, 마지막에 선언을 해야 함수를 정상적으로 인식함
    const functionMap = {
        "fn_test251118" : fn_test251118
        ,"fn_test251125" : fn_test251125
        ,"fn_test251126" : fn_test251126
        ,"fn_test251126_2" : fn_test251126_2
        ,"fn_log_test" : fn_log_test
        ,"fn_JSDailyTimeRolling" : fn_JSDailyTimeRolling
        ,"fn_JSPlanCycleRollingPreConfigured" : fn_JSPlanCycleRollingPreConfigured
        ,"fn_test251209" : fn_test251209
        ,"fn_JSWhatIfScenarioCreation" : fn_JSWhatIfScenarioCreation
        ,"fn_260126" : fn_260126
        ,"fn_260209" : fn_260209
        ,"fn_260303" : fn_260303
    };

    return {
        fn_loadFunction : fn_loadFunction
    };
});

/**************************** o9.NSCM.JSEWCommonLibTest ****************************
**************************************************************************************/