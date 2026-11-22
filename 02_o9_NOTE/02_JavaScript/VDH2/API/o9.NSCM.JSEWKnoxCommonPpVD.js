define('o9.NSCM.JSEWKnoxCommonPpVD', ['o9/data/query', 'o9/data/cellset', 'o9.NSCM.commonLibVD'
                                ,'o9.NSCM.JSKnoxServiceVD'], function () {

/**************************************************************************************
    프로그램명  : o9.NSCM.JSEWKnoxCommonPpVD
    화면명     : Knox 후처리 로직 ( 공통에서만 수정, 모듈별로 수정 불가 )
    API 개발자 : sungmin0.lim
    최초생성   : 2026.02.09
**************************************************************************************/

    // fn_cLib 를 통해서 commonLib 를 생성
    var fn_cLib = function(name) {
        return new commonLib.VdCommon(name);
    }
    var fn_cUtil = function() {
        return new commonLib.VdUtil();
    }

	const programName = "o9.NSCM.JSEWKnoxCommonPpVD";
    const commonLib = require('o9.NSCM.commonLibVD');
    const cUtil = fn_cUtil();

    var division = "VD";

/************************************************* UI Call Common Logic *************************************************/
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

            if ( parsedParams["fbParams"] == undefined ) {
                parsedParams["fbParams"] = {};
            }

            var rtn = functionMap[fbFuncName](parsedParams);

            cLib.programEnd();
            return rtn;
        } catch ( e ) {
            return { "Code" : -1, "Msg" : e.message };
        }
	};

/************************************************* common logic *************************************************/
/*
    결재 후처리
{ "fbFuncName" : "fn_approvalPostProcess"
    ,"fbParams" : { "filters" : { "[Version].[Version Name]" : {"SelectedMembers" : ["CWV_MP"], "MemberFilter" : ""} }
                  }
}

cartesian scope:(&CWVUI*[Personnel].[Email].[sungmin0.lim@partner.samsung.com]*[Time].[Day].[2026-03-03]*[Time Seq].[Time Seq].[140736]);
Measure.[Knox Approval_Status] = "2";
Measure.[Knox Approval_Post Process Flag] = "N";
end scope;

cartesian scope:(&CWVUI*[Personnel].[Email].[sungmin0.lim@partner.samsung.com]*[Time].[Day].[2026-03-03]*[Time Seq].[Time Seq].[140736]);
Measure.[Knox Approval_Status] = "2";
Measure.[Knox Approval_Post Process Flag] = "N";
Measure.[Knox Approval_Post Process Service] = "o9.NSCM.JSKnoxServiceVD";
Measure.[Knox Approval_Post Process Service Function] = "fn_service1";
Measure.[Knox Approval_Post Process Params] = "{\"a\":\"a11\",\"b\":\"b11\"}";
end scope;

cartesian scope:(&CWVUI*[Personnel].[Email].[sungmin0.lim@partner.samsung.com]*[Time].[Day].[2026-02-20]*[Time Seq].[Time Seq].[161201]);
Measure.[Knox Approval_Status] = "2";
Measure.[Knox Approval_Post Process Flag] = "N";
Measure.[Knox Approval_Post Process Service] = "o9.NSCM.JSKnoxService";
Measure.[Knox Approval_Post Process Service Function] = "fn_service2";
Measure.[Knox Approval_Post Process Params] = "{\"a\":\"a11\",\"b\":\"b11\"}";
end scope;

*/
    var fn_approvalPostProcess = function(p){
        const cLib = fn_cLib(programName + "." + arguments.callee.name);
        cLib.setLogLevel("Debug");

		try {
		    // Version 은 CurrentWorkingView 를 사용하도록 함
		    // var version = cUtil.fn_getFilterVersion(p);
		    var version = "[Version].[Version Name].[CurrentWorkingView]";

            // 완결(2), 반려(3) 인 데이타를 가져온다.
            var result = cLib.selectList([version
                                                ,"[Personnel].[Email]"
                                                ,"[Time].[Day]"
                                                ,"[Time Seq].[Time Seq]"]
                                            ,["Measure.[Knox Approval_Post Process Service]"
                                                ,"Measure.[Knox Approval_Post Process Service Function]"
                                                ,"Measure.[Knox Approval_Post Process Params]"
                                                ,"Measure.[Knox Approval_Status]"]
                                            ,'where { Measure.[Knox Approval_Status] in {"2", "3"}, ' +
                                                'Measure.[Knox Approval_Division] == "' + division + '", ' +
                                                'Measure.[Knox Approval_Post Process Flag] == "N" }'
                                            ,""
                                            ,"limit 100");
            for ( var i = 0; i < result.cs.rowCount; i++ ) {
                // 후처리가 오래 걸려서 다시 호출 될 경우 2번이 실행할 우려가 있어 개별적으로 상태를 조회 업데이트를 한다.
                var oneResult = cLib.selectList([version
                                                        ,"[Personnel].[Email].[" + cUtil.fn_getDimValue(result, i, "Personnel", "Email") + "]"
                                                        ,"[Time].[Day].[" + cUtil.fn_getDimValue(result, i, "Time", "Day") + "]"
                                                        ,"[Time Seq].[Time Seq].[" + cUtil.fn_getDimValue(result, i, "Time Seq", "Time Seq") + "]"]
                                                    ,["Measure.[Knox Approval_Post Process Service]"
                                                        ,"Measure.[Knox Approval_Post Process Service Function]"
                                                        ,"Measure.[Knox Approval_Post Process Params]"
                                                        ,"Measure.[Knox Approval_Status]"]
                                                    ,'where { Measure.[Knox Approval_Status] in {"2", "3"}, ' +
                                                        'Measure.[Knox Approval_Post Process Flag] == "N" }'
                                                    ,""
                                                    ,"");
                // 후처리가 안되었으면...
                if ( oneResult.cs.rowCount == 1 ) {
                    var service = cUtil.fn_getMeaValue(result, i, "Knox Approval_Post Process Service");
                    var func = cUtil.fn_getMeaValue(result, i, "Knox Approval_Post Process Service Function");
                    var params = cUtil.fn_getMeaValue(result, i, "Knox Approval_Post Process Params");
                    var status = cUtil.fn_getMeaValue(result, i, "Knox Approval_Status");

                    cLib.debug("service : " + service + ", func : " + func + ", status : " + status);

                    // 시작 업데이트
                    cLib.updateMeasure([version
                                                ,"[Personnel].[Email].[" + cUtil.fn_getDimValue(result, i, "Personnel", "Email") + "]"
                                                ,"[Time].[Day].[" + cUtil.fn_getDimValue(result, i, "Time", "Day") + "]"
                                                ,"[Time Seq].[Time Seq].[" + cUtil.fn_getDimValue(result, i, "Time Seq", "Time Seq") + "]"]
                                           ,[cUtil.fn_qMeaStr(null, "Measure.[Knox Approval_Post Process Flag]", "S")]);

                    // 시작시간
                    var startTime = new Date();
                    // 서비스 호출
                    var jsModule = require(service);
                    var rtn = jsModule[func](status, params);
                    // 종료시간
                    var endTime = new Date();

                    // GMT+9 로 변경
                    startTime.setHours(startTime.getHours() + 9);
                    endTime.setHours(endTime.getHours() + 9);

                    // 결과 기록을 위한 시간 구성 및 저장
                    var runTimeStr = Math.floor((endTime - startTime) / 1000);
                    var startTS = startTime.getFullYear() + "-"
                                    + cUtil.fn_lpad((startTime.getMonth() + 1) + "", 2, "0") + "-"
                                    + cUtil.fn_lpad(startTime.getDate() + "", 2, "0") + " "
                                    + cUtil.fn_lpad(startTime.getHours() + "", 2, "0") + " "
                                    + cUtil.fn_lpad(startTime.getMinutes() + "", 2, "0")
                                    + cUtil.fn_lpad(startTime.getSeconds() + "", 2, "0");
                    var endTS = endTime.getFullYear() + "-"
                                    + cUtil.fn_lpad((endTime.getMonth() + 1) + "", 2, "0") + "-"
                                    + cUtil.fn_lpad(endTime.getDate() + "", 2, "0") + " "
                                    + cUtil.fn_lpad(endTime.getHours() + "", 2, "0") + " "
                                    + cUtil.fn_lpad(endTime.getMinutes() + "", 2, "0")
                                    + cUtil.fn_lpad(endTime.getSeconds() + "", 2, "0");

                    // 결과 업데이트
                    cLib.updateMeasure([version
                                                ,"[Personnel].[Email].[" + cUtil.fn_getDimValue(result, i, "Personnel", "Email") + "]"
                                                ,"[Time].[Day].[" + cUtil.fn_getDimValue(result, i, "Time", "Day") + "]"
                                                ,"[Time Seq].[Time Seq].[" + cUtil.fn_getDimValue(result, i, "Time Seq", "Time Seq") + "]"]
                                           ,[cUtil.fn_qMeaStr(null, "Measure.[Knox Approval_Post Process Start Time]", startTS)
                                                ,cUtil.fn_qMeaStr(null, "Measure.[Knox Approval_Post Process End Time]", endTS)
                                                ,cUtil.fn_qMeaInt(null, "Measure.[Knox Approval_Post Process Run Time]", runTimeStr)
                                                ,cUtil.fn_qMeaStr(null, "Measure.[Knox Approval_Post Process Error Message]", rtn)
                                                ,cUtil.fn_qMeaStr(null, "Measure.[Knox Approval_Post Process Flag]", (rtn == "" ? "Y" : "E"))]);
                }
            }

            cLib.programEnd();

            return { "Code" : 0, "Msg" : "" };
        } catch ( e ) {
            cLib.error(e.message);
            return { "Code" : -1, "Msg" : e.message };
        }
    };

/************************************************* util logic *************************************************/

/************************************************* Mapping logic **********************************************/
    // Mapping 함수 정의, 마지막에 선언을 해야 함수를 정상적으로 인식함
    const functionMap = {
        "fn_approvalPostProcess" : fn_approvalPostProcess
    };

    return {
        fn_loadFunction : fn_loadFunction
        ,fn_approvalPostProcess : fn_approvalPostProcess      // Int3.0 에서 호출할 수 있게 선언
    };
});

/**************************************************************************************************************
**************************************** o9.NSCM.JSEWKnoxCommonPpVD *******************************************/