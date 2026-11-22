define('o9.NSCM.JSEWKnoxCommon', ['o9/data/query', 'o9/data/cellset', 'o9.NSCM.commonLib'
                                ,'o9.NSCM.JSKnoxAttachmentVD'], function () {

/**************************************************************************************
    프로그램명  : o9.NSCM.JSEWKnoxCommon
    화면명     : Knox ( 공통에서만 수정, 모듈별로 수정 불가 )
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

	const programName = "o9.NSCM.JSEWKnoxCommon";
    const commonLib = require('o9.NSCM.commonLib');
    const cUtil = fn_cUtil();

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
    임직원 조회 Api - 이름으로
{ "fbFuncName" : "fn_employeesForName"
    ,"fbParams" : { "searchValue" : "임성민"
                    ,"filters" : { "[Version].[Version Name]" : {"SelectedMembers" : ["CWV_MP"], "MemberFilter" : ""} }
                  }
 }
*/
    var fn_employeesForName = function(p){
        const cLib = fn_cLib(programName + "." + arguments.callee.name);
        cLib.setLogLevel("Debug");

		try {
		    // Version 은 CurrentWorkingView 를 사용하도록 함
		    // var version = cUtil.fn_getFilterVersion(p);
		    // var versionName = cUtil.fn_getDimensionValue(version);
		    var version = "[Version].[Version Name].[CurrentWorkingView]";
		    var versionName = "CurrentWorkingView";

            var email = cLib.selectResult('CurrentUser().Name');

            // 데이타 삭제
            cLib.deleteMeasure([version, "[Personnel].[Email].[" + email + "]"], 'Knox Employee');

            // Knox 파이썬 실행
            var execQuery = 'EXEC plugin instance [PY_Knox_Employees] ' +
                            'for measures {[Knox Employee_UserId]} ' +
                            'using scope ( ' + version + ' * [Personnel].[Email].[' + email + '] ) ' +
                            'using arguments { (pVersionName, "' + versionName + '"), ' +
                            '                  (pEmail, "' + email + '"), ' +
                            '                  (pField, "name"), ' +
                            '                  (pValue, "' + p.fbParams.searchValue + '"), ' +
                            '                  (ExecutionMode, "MediumWeight"), (MaxSliceTableCells, 200000000), (MaxConcurrency, 1 )};'
            cLib.executePython("PY_Knox_Employees", execQuery);

            // 싱글정보 가져오기
            var employees = [];
            var result = cLib.selectList([version
                                                ,"[Personnel].[Email].[" + email + "]"
                                                ,"Seq.[Seq]"]
                                             ,["Measure.[Knox Employee_UserId]"
                                                ,"Measure.[Knox Employee_Email]"
                                                ,"Measure.[Knox Employee_UserName]"
                                                ,"Measure.[Knox Employee_CompanyName]"
                                                ,"Measure.[Knox Employee_DepartmentName]"]
                                             ,"", "", "");
            for ( var i = 0; i < result.cs.rowCount; i++ ) {
                employees.push({"Seq" : cUtil.fn_getDimValue(result, i, "Seq", "Seq")
                                    ,"UserId" : cUtil.fn_getMeaValue(result, i, "Knox Employee_UserId")
                                    ,"Email" : cUtil.fn_getMeaValue(result, i, "Knox Employee_Email")
                                    ,"UserName" : cUtil.fn_getMeaValue(result, i, "Knox Employee_UserName")
                                    ,"CompanyName" : cUtil.fn_getMeaValue(result, i, "Knox Employee_CompanyName")
                                    ,"DepartmentName" : cUtil.fn_getMeaValue(result, i, "Knox Employee_DepartmentName")});
            }

            cLib.programEnd();

            return { "Code" : 0, "Msg" : "", Rows : employees };
        } catch ( e ) {
            cLib.error(e.message);
            return { "Code" : -1, "Msg" : e.message };
        }
    };

/*
    임직원 조회 Api - user
{ "fbFuncName" : "fn_employeesForUserIds"
    ,"fbParams" : { "searchValue" : "s00.park,sungmin0.lim"
                        ,"filters" : { "[Version].[Version Name]" : {"SelectedMembers" : ["CWV_MP"], "MemberFilter" : ""} }
                  }
 }
*/
    var fn_employeesForUserIds = function(p){
        const cLib = fn_cLib(programName + "." + arguments.callee.name);
        cLib.setLogLevel("Debug");

		try {
		    // Version 은 CurrentWorkingView 를 사용하도록 함
		    // var version = cUtil.fn_getFilterVersion(p);
		    // var versionName = cUtil.fn_getDimensionValue(version);
		    var version = "[Version].[Version Name].[CurrentWorkingView]";
		    var versionName = "CurrentWorkingView";

            var email = cLib.selectResult('CurrentUser().Name');

            // 데이타 삭제
            cLib.deleteMeasure([version, "[Personnel].[Email].[" + email + "]"], 'Knox Employee');

            // Knox 파이썬 실행
            var execQuery = 'EXEC plugin instance [PY_Knox_Employees] ' +
                            'for measures {[Knox Employee_UserId]} ' +
                            'using scope ( ' + version + ' * [Personnel].[Email].[' + email + '] ) ' +
                            'using arguments { (pVersionName, "' + versionName + '"), ' +
                            '                  (pEmail, "' + email + '"), ' +
                            '                  (pField, "userIds"), ' +
                            '                  (pValue, "' + p.fbParams.searchValue + '"), ' +
                            '                  (ExecutionMode, "MediumWeight"), (MaxSliceTableCells, 200000000), (MaxConcurrency, 1 )};'
            cLib.executePython("PY_Knox_Employees", execQuery);

            // 싱글정보 가져오기
            var employees = [];
            var result = cLib.selectList([version
                                                ,"[Personnel].[Email].[" + email + "]"
                                                ,"Seq.[Seq]"]
                                             ,["Measure.[Knox Employee_UserId]"
                                                ,"Measure.[Knox Employee_Email]"
                                                ,"Measure.[Knox Employee_UserName]"
                                                ,"Measure.[Knox Employee_CompanyName]"
                                                ,"Measure.[Knox Employee_DepartmentName]"]
                                             ,"", "", "");
            for ( var i = 0; i < result.cs.rowCount; i++ ) {
                employees.push({"Seq" : cUtil.fn_getDimValue(result, i, "Seq", "Seq")
                                    ,"UserId" : cUtil.fn_getMeaValue(result, i, "Knox Employee_UserId")
                                    ,"Email" : cUtil.fn_getMeaValue(result, i, "Knox Employee_Email")
                                    ,"UserName" : cUtil.fn_getMeaValue(result, i, "Knox Employee_UserName")
                                    ,"CompanyName" : cUtil.fn_getMeaValue(result, i, "Knox Employee_CompanyName")
                                    ,"DepartmentName" : cUtil.fn_getMeaValue(result, i, "Knox Employee_DepartmentName")});
            }

            cLib.programEnd();

            return { "Code" : 0, "Msg" : "", Rows : employees };
        } catch ( e ) {
            cLib.error(e.message);
            return { "Code" : -1, "Msg" : e.message };
        }
    };

/*
    메일 발송
{ "fbFuncName" : "fn_mailSend"
    ,"fbParams" : { "subject" : "EMAIL SUBJECT (이메일 제목)"
                    ,"contents" : "EMAIL BODY (이메일 본문)"
                    ,"recipients" : [{"userId" : "dmin.oh", "emailAddress" : "dmin.oh@stage.miracom-inc.com", "recipientType" : "TO"}]
                    ,"sender" : "sungmin0.lim@stage.partner.samsung.com"
                    ,"filters" : { "[Version].[Version Name]" : {"SelectedMembers" : ["CWV_MP"], "MemberFilter" : ""} }
                    ,"attachmentFunction" : "fn_knoxTest_mail"
                    ,"attachmentService" : "o9.NSCM.JSKnoxAttachmentVD"
                  }
    ,"fbGridRows" : [
            { "rowstatus":"C","rowindex":"0","[Location].[Location]":"P105","[Seq].[Seq]":"1","Measure.[Knox Test_A]":"A-P105","Measure.[Knox Test_B]":"B","Measure.[Knox Test_C]":"C","Measure.[Knox Test_D]":"D","Measure.[Knox Test_E]":"E" },
            { "rowstatus":"C","rowindex":"0","[Location].[Location]":"P310","[Seq].[Seq]":"1","Measure.[Knox Test_A]":"A-P310","Measure.[Knox Test_B]":"B","Measure.[Knox Test_C]":"C","Measure.[Knox Test_D]":"D","Measure.[Knox Test_E]":"E" }
                  ]
 }
*/
    var fn_mailSend = function(p){
        const cLib = fn_cLib(programName + "." + arguments.callee.name);
        cLib.setLogLevel("Debug");

		try {
		    // Version 은 CurrentWorkingView 를 사용하도록 함
		    // var version = cUtil.fn_getFilterVersion(p);
		    // var versionName = cUtil.fn_getDimensionValue(version);
		    var version = "[Version].[Version Name].[CurrentWorkingView]";
		    var versionName = "CurrentWorkingView";

            var email = cLib.selectResult('CurrentUser().Name');

            var nowTime = new Date();
            nowTime.setHours(nowTime.getHours() + 9);

            var day = nowTime.getFullYear() + "-"
                        + cUtil.fn_lpad((nowTime.getMonth() + 1) + "", 2, "0") + "-"
                        + cUtil.fn_lpad(nowTime.getDate() + "", 2, "0");
            var timeSeq = cUtil.fn_lpad(nowTime.getHours() + "", 2, "0")
                            + cUtil.fn_lpad(nowTime.getMinutes() + "", 2, "0")
                            + cUtil.fn_lpad(nowTime.getSeconds() + "", 2, "0");

            // recipients 정보를 스트링으로 만든다.
            var recipients = "";
            var recipientsEmail = "";
            for ( var i = 0; i < p.fbParams.recipients.length; i++ ) {
                recipients = cUtil.fn_wordDistinctAppend(recipients, p.fbParams.recipients[i].userId + "^" + p.fbParams.recipients[i].recipientType);
                recipientsEmail = cUtil.fn_wordDistinctAppend(recipientsEmail, p.fbParams.recipients[i].emailAddress + "^" + p.fbParams.recipients[i].recipientType);
            }

            cLib.createMeasure([version
                                        ,"[Personnel].[Email].[" + email + "]"
                                        ,"[Time].[Day].[" + day + "]"
                                        ,"[Time Seq].[Time Seq].[" + timeSeq + "]"]
                                   ,[cUtil.fn_qMeaStr(null, "Measure.[Knox Mail_Subject]", p.fbParams.subject)
                                        ,cUtil.fn_qMeaStr(null, "Measure.[Knox Mail_Contents]", p.fbParams.contents)
                                        ,cUtil.fn_qMeaStr(null, "Measure.[Knox Mail_Recipients]", recipients)
                                        ,cUtil.fn_qMeaStr(null, "Measure.[Knox Mail_RecipientsEmail]", recipientsEmail)
                                        ,cUtil.fn_qMeaStr(null, "Measure.[Knox Mail_Sender]", p.fbParams.sender)
                                        ,cUtil.fn_qMeaStr(null, "Measure.[Knox Mail_UserId]", p.fbParams.sender.split("@")[0])]);

            // 첨부파일 서비스가 있으면 호출
            if ( p.fbParams["attachmentFunction"] != undefined && p.fbParams.attachmentFunction != "" ) {
                p.fbParams["[Personnel].[Email]"] = email;
                p.fbParams["[Time].[Day]"] = day;
                p.fbParams["[[Time Seq].[Time Seq]"] = timeSeq;

                var jsModule = require(p.fbParams.attachmentService);
                var rtn = jsModule[p.fbParams.attachmentFunction](p);
            }

            // Knox 파이썬 실행
            var execQuery = 'EXEC plugin instance [PY_Knox_Mail] ' +
                            'for measures {[Knox Mail_status]} ' +
                            'using scope ( ' + version + ' * [Personnel].[Email].[' + email + '] * [Time].[Day].[' + day + '] * [Time Seq].[Time Seq].[' + timeSeq + '] ) ' +
                            'using arguments { (pVersionName, "' + versionName + '"), ' +
                            '                  (ExecutionMode, "MediumWeight"), (MaxSliceTableCells, 200000000), (MaxConcurrency, 1 )};'
            cLib.executePython("PY_Knox_Mail", execQuery);

            //  결과 조회
            var status = "";
            var errorMessage = "";
            var result = cLib.selectList([version
                                                ,"[Personnel].[Email].[" + email + "]"
                                                ,"[Time].[Day].[" + day + "]"
                                                ,"[Time Seq].[Time Seq].[" + timeSeq + "]"]
                                             ,["Measure.[Knox Mail_Status]"
                                                ,"Measure.[Knox Mail_Error Message]"]
                                             ,"", "", "");
            if ( result.cs.rowCount > 0 ) {
                status = cUtil.fn_getMeaValue(result, 0, "Knox Mail_Status");
                errorMessage = cUtil.fn_getMeaValue(result, 0, "Knox Mail_Error Message");
            }

            cLib.programEnd();

            return { "Code" : 0, "Msg" : errorMessage, "Status" : status };
        } catch ( e ) {
            cLib.error(e.message);
            return { "Code" : -1, "Msg" : e.message };
        }
    };

/*
    결재 요청
{ "fbFuncName" : "fn_approvalSubmit"
    ,"fbParams" : { "subject" : "Knox Test 결재 요청"
                    ,"contents" : "\"<table><tr><td align=\\\"center\\\" style=\\\"background-color: #f3f6f7;\\\">Location</td><td align=\\\"center\\\" style=\\\"background-color: #f3f6f7;\\\">Seq</td><td align=\\\"center\\\" style=\\\"background-color: #f3f6f7;\\\">A Column</td><td align=\\\"center\\\" style=\\\"background-color: #f3f6f7;\\\">B Column</td><td align=\\\"center\\\" style=\\\"background-color: #f3f6f7;\\\">C Column</td><td align=\\\"center\\\" style=\\\"background-color: #f3f6f7;\\\">D Column</td><td align=\\\"center\\\" style=\\\"background-color: #f3f6f7;\\\">E Column</td></tr><tr><td align=\\\"left\\\">P105</td><td align=\\\"center\\\">1</td><td align=\\\"left\\\">A-P105</td><td align=\\\"center\\\">B</td><td align=\\\"right\\\">C</td><td align=\\\"left\\\">D</td><td align=\\\"center\\\">E</td></tr><tr><td align=\\\"left\\\">P310</td><td align=\\\"center\\\">1</td><td align=\\\"left\\\">A-P310</td><td align=\\\"center\\\">B</td><td align=\\\"right\\\">C</td><td align=\\\"left\\\">D</td><td align=\\\"center\\\">E</td></tr>\""
                    ,"aplns" : [{"aplnMdfyPmtYn":"Y","aplnStatsCode":"0","arbPmtYn":"Y","contentsMdfyPmtYn":"Y","userId":"dmin.oh","role":"0","seq":"0"}
                                ,{"aplnMdfyPmtYn":"Y","aplnStatsCode":"0","arbPmtYn":"Y","contentsMdfyPmtYn":"Y","userId":"sungmin0.lim","role":"1","seq":"1"}]
                    ,"menuName" : "Knox Test"
                    ,"service" : "o9.NSCM.JSKnoxServiceVD"
                    ,"serviceFunction" : "fn_knoxTest"
                    ,"params" : "{\"approvalList\":[{\"[Version].[Version Name]\":\"CWV_MP\",\"[Location].[Location]\":\"P105\",\"[Seq].[Seq]\":\"1\"},{\"[Version].[Version Name]\":\"CWV_MP\",\"[Location].[Location]\":\"P310\",\"[Seq].[Seq]\":\"1\"}]}"
                    ,"approvalTarget" :  [
                                            {
                                              "Grain": {
                                                "[Version].[Version Name]": "CWV_MP",
                                                "[Location].[Location]": "P105",
                                                "[Seq].[Seq]": "1"
                                              },
                                              "IdMeasure": "Measure.[Knox Test_ApInfId]",
                                              "UuMeasure": "Measure.[Knox Test_Approval By]",
                                              "UtMeasure": "Measure.[Knox Test_Approval Time]",
                                              "StatusMeasure": "Measure.[Knox Test_Status]"
                                            },
                                            {
                                              "Grain": {
                                                "[Version].[Version Name]": "CWV_MP",
                                                "[Location].[Location]": "P310",
                                                "[Seq].[Seq]": "1"
                                              },
                                              "IdMeasure": "Measure.[Knox Test_ApInfId]",
                                              "UuMeasure": "Measure.[Knox Test_Approval By]",
                                              "UtMeasure": "Measure.[Knox Test_Approval Time]",
                                              "StatusMeasure": "Measure.[Knox Test_Status]"
                                            }
                                          ]
                    ,"division" : "VD"
                    ,"attachmentFunction" : "fn_knoxTest_approval"
                    ,"attachmentService" : "o9.NSCM.JSKnoxAttachmentVD"
                    ,"filters" : { "[Version].[Version Name]" : {"SelectedMembers" : ["CWV_MP"], "MemberFilter" : ""} }
                  }
    ,"fbGridRows" : [
            { "rowstatus":"C","rowindex":"0","[Location].[Location]":"P105","[Seq].[Seq]":"1","Measure.[Knox Test_A]":"A-P105","Measure.[Knox Test_B]":"B","Measure.[Knox Test_C]":"C","Measure.[Knox Test_D]":"D","Measure.[Knox Test_E]":"E" },
            { "rowstatus":"C","rowindex":"0","[Location].[Location]":"P310","[Seq].[Seq]":"1","Measure.[Knox Test_A]":"A-P310","Measure.[Knox Test_B]":"B","Measure.[Knox Test_C]":"C","Measure.[Knox Test_D]":"D","Measure.[Knox Test_E]":"E" }
                  ]
 }
*/
    var fn_approvalSubmit = function(p){
        const cLib = fn_cLib(programName + "." + arguments.callee.name);
        cLib.setLogLevel("Debug");

		try {
		    // Version 은 CurrentWorkingView 를 사용하도록 함
		    // var version = cUtil.fn_getFilterVersion(p);
		    // var versionName = cUtil.fn_getDimensionValue(version);
		    var version = "[Version].[Version Name].[CurrentWorkingView]";
		    var versionName = "CurrentWorkingView";

            var email = cLib.selectResult('CurrentUser().Name');

            var nowTime = new Date();
            nowTime.setHours(nowTime.getHours() + 9);

            var day = nowTime.getFullYear() + "-"
                        + cUtil.fn_lpad((nowTime.getMonth() + 1) + "", 2, "0") + "-"
                        + cUtil.fn_lpad(nowTime.getDate() + "", 2, "0");
            var timeSeq = cUtil.fn_lpad(nowTime.getHours() + "", 2, "0")
                            + cUtil.fn_lpad(nowTime.getMinutes() + "", 2, "0")
                            + cUtil.fn_lpad(nowTime.getSeconds() + "", 2, "0");
            var apInfId = email.split("@")[0] + "_" + day + "_" + timeSeq + "_" + parseInt(Math.random(1000) * 10000);

            cLib.createMeasure([version
                                        ,"[Personnel].[Email].[" + email + "]"
                                        ,"[Time].[Day].[" + day + "]"
                                        ,"[Time Seq].[Time Seq].[" + timeSeq + "]"]
                                   ,[cUtil.fn_qMeaStr(null, "Measure.[Knox Approval_Division]", p.fbParams.division)
                                        ,cUtil.fn_qMeaStr(null, "Measure.[Knox Approval_Subject]", p.fbParams.subject)
                                        ,cUtil.fn_qMeaStr(null, "Measure.[Knox Approval_Contents]", p.fbParams.contents)
                                        ,cUtil.fn_qMeaStr(null, "Measure.[Knox Approval_Aplns]", JSON.stringify(p.fbParams.aplns))
                                        ,cUtil.fn_qMeaStr(null, "Measure.[Knox Approval_ApInfId]", apInfId)
                                        ,cUtil.fn_qMeaStr(null, "Measure.[Knox Approval_Status]", "1")
                                        ,cUtil.fn_qMeaStr(null, "Measure.[Knox Approval_Menu Name]", p.fbParams.menuName)
                                        ,cUtil.fn_qMeaStr(null, "Measure.[Knox Approval_Post Process Flag]", "N")
                                        ,cUtil.fn_qMeaStr(null, "Measure.[Knox Approval_Post Process Service]", p.fbParams.service)
                                        ,cUtil.fn_qMeaStr(null, "Measure.[Knox Approval_Post Process Service Function]", p.fbParams["serviceFunction"])
                                        ,cUtil.fn_qMeaStr(null, "Measure.[Knox Approval_Post Process Params]", p.fbParams.params)]);

            // 첨부파일 서비스가 있으면 호출
            if ( p.fbParams["attachmentFunction"] != undefined && p.fbParams.attachmentFunction != "" ) {
                p.fbParams["[Personnel].[Email]"] = email;
                p.fbParams["[Time].[Day]"] = day;
                p.fbParams["[[Time Seq].[Time Seq]"] = timeSeq;

                var jsModule = require(p.fbParams.attachmentService);
                var rtn = jsModule[p.fbParams.attachmentFunction](p);
            }

            // Knox 파이썬 실행
            var execQuery = 'EXEC plugin instance [PY_Knox_Approval] ' +
                            'for measures {[Knox Approval_Status]} ' +
                            'using scope ( ' + version + ' * [Personnel].[Email].[' + email + '] * [Time].[Day].[' + day + '] * [Time Seq].[Time Seq].[' + timeSeq + '] ) ' +
                            'using arguments { (pVersionName, "' + versionName + '"), ' +
                            '                  (ExecutionMode, "MediumWeight"), (MaxSliceTableCells, 200000000), (MaxConcurrency, 1 )};'
            cLib.executePython("PY_Knox_Approval", execQuery);

            //  결과 조회
            var approvalStatus = "1";
            var errorCode = "";
            var errorMessage = "";
            var result = cLib.selectList([version
                                                ,"[Personnel].[Email].[" + email + "]"
                                                ,"[Time].[Day].[" + day + "]"
                                                ,"[Time Seq].[Time Seq].[" + timeSeq + "]"]
                                             ,["Measure.[Knox Approval_Subject]"
                                                ,"Measure.[Knox Approval_Error Code]"
                                                ,"Measure.[Knox Mail_Error Message]"]
                                             ,"", "", "");
            if ( result.cs.rowCount > 0 ) {
                errorCode = cUtil.fn_getString(cUtil.fn_getMeaValue(result, 0, "Knox Approval_Error Code"));
                errorMessage = cUtil.fn_getString(cUtil.fn_getMeaValue(result, 0, "Knox Approval_Error Message"));

                if ( errorCode != "-" ) {
                    approvalStatus = "-99";
                }
            }

            // Knox 결재후에 기존 데이타가 ID 세팅
            for ( var i = 0; i < p.fbParams.approvalTarget.length; i++ ) {
                var row = p.fbParams.approvalTarget[i];

                var dimensions = [];
                var grain = row["Grain"];
                for (var key in grain) {
                    dimensions.push(key + ".[" + grain[key] + "]");
                }
                var measures = [cUtil.fn_qMeaStr(null, row["IdMeasure"], apInfId)];
                // 수정자
                if ( row["UuMeasure"] != undefined && row["UuMeasure"] != "" ) {
                    measures.push(cUtil.fn_qMeaUpdateUserName(row["UuMeasure"]));
                }
                // 수정일자
                if ( row["UtMeasure"] != undefined && row["UtMeasure"] != "" ) {
                    measures.push(cUtil.fn_qMeaUpdateTime(row["UtMeasure"]));
                }
                // 결재 상태
                if ( row["StatusMeasure"] != undefined && row["StatusMeasure"] != "" ) {
                    measures.push(cUtil.fn_qMeaStr(null, row["StatusMeasure"], approvalStatus));
                }

                cLib.updateMeasure(dimensions, measures);
            }

            cLib.programEnd();

            return { "Code" : 0, "Msg" : errorMessage, "ErrorCode" : errorCode, "apInfId" : apInfId };
        } catch ( e ) {
            cLib.error(e.message);
            return { "Code" : -1, "Msg" : e.message };
        }
    };

/*
    첨부 내용 조회
{ "fbFuncName" : "fn_attachment"
    ,"fbParams" : { "attachmentFunction" : "fn_knoxTest_approval"
                    ,"attachmentService" : "o9.NSCM.JSKnoxAttachmentVD"
                    ,"filters" : { "[Version].[Version Name]" : {"SelectedMembers" : ["CWV_MP"], "MemberFilter" : ""} }
                  }
    ,"fbGridRows" : [
            { "rowstatus":"C","rowindex":"0","[Location].[Location]":"P105","[Seq].[Seq]":"1","Measure.[Knox Test_A]":"A-P105","Measure.[Knox Test_B]":"B","Measure.[Knox Test_C]":"C","Measure.[Knox Test_D]":"D","Measure.[Knox Test_E]":"E" },
            { "rowstatus":"C","rowindex":"0","[Location].[Location]":"P310","[Seq].[Seq]":"1","Measure.[Knox Test_A]":"A-P310","Measure.[Knox Test_B]":"B","Measure.[Knox Test_C]":"C","Measure.[Knox Test_D]":"D","Measure.[Knox Test_E]":"E" }
                  ]
 }
*/
    var fn_attachment = function(p){
        const cLib = fn_cLib(programName + "." + arguments.callee.name);
        cLib.setLogLevel("Debug");

		try {
            var jsModule = require(p.fbParams.attachmentService);
            var rtn = jsModule[p.fbParams.attachmentFunction](p);

            cLib.programEnd();

            return { "Code" : 0, "Msg" : "", "AttachmentText" : rtn.attachmentText };
        } catch ( e ) {
            cLib.error(e.message);
            return { "Code" : -1, "Msg" : e.message };
        }
    };

/*
    결재 상태 동기화
{ "fbFuncName" : "fn_approvalStatus"
    ,"fbParams" : { "filters" : { "[Version].[Version Name]" : {"SelectedMembers" : ["CWV_MP"], "MemberFilter" : ""} }
                  }
 }
*/
    var fn_approvalStatus = function(p){
        const cLib = fn_cLib(programName + "." + arguments.callee.name);
        cLib.setLogLevel("Debug");

		try {
		    // Version 은 CurrentWorkingView 를 사용하도록 함
		    // var version = cUtil.fn_getFilterVersion(p);
		    // var versionName = cUtil.fn_getDimensionValue(version);
		    var version = "[Version].[Version Name].[CurrentWorkingView]";
		    var versionName = "CurrentWorkingView";

            // Knox 파이썬 실행
            var execQuery = 'EXEC plugin instance [PY_Knox_ApprovalStatus] ' +
                            'for measures {[Knox Approval_Status]} ' +
                            'using scope ( ' + version + ' ) ' +
                            'using arguments { (pVersionName, "' + versionName + '"), ' +
                            '                  (ExecutionMode, "MediumWeight"), (MaxSliceTableCells, 200000000), (MaxConcurrency, 1 )};'
            cLib.executePython("PY_Knox_ApprovalStatus", execQuery);

            cLib.programEnd();

            return { "Code" : 0, "Msg" : "" };
        } catch ( e ) {
            cLib.error(e.message);
            return { "Code" : -1, "Msg" : e.message };
        }
    };

    // { "fbFuncName" : "fn_cb_approvalRole" }
	var fn_cb_approvalRole = function(parsedParams){
        const cLib = fn_cLib(programName + "." + arguments.callee.name);
        cLib.setLogLevel("Debug");

		try {
            cLib.printParams(parsedParams);

            var comboList = cLib.fn_makeCombo(null, {ComboCodes : ["0","1","2","3","4","7","9"]
                                                        ,ComboValues : ["기안","결재","합의","후결","병렬합의","병렬결재","통보"]});

            cLib.programEnd();

            return { "Code" : 0, "Msg" : "", "Rows" : comboList };
        } catch ( e ) {
            cLib.error(e.message);
            return { "Code" : -1, "Msg" : e.message };
        }
    };

    // { "fbFuncName" : "fn_cb_approvalStatus" }
	var fn_cb_approvalStatus = function(parsedParams){
        const cLib = fn_cLib(programName + "." + arguments.callee.name);
        cLib.setLogLevel("Debug");

		try {
            cLib.printParams(parsedParams);

            var comboList = cLib.fn_makeCombo(null, {ComboCodes : ["-99", "-3","-2","-1","0","1","2","3","4","5","6"]
                                                        ,ComboValues : ["발송오류", "암호화실패","암호화중","예약상신","보류","진행중","완결","반려","상신취소","전결","후완결"]});

            cLib.programEnd();

            return { "Code" : 0, "Msg" : "", "Rows" : comboList };
        } catch ( e ) {
            cLib.error(e.message);
            return { "Code" : -1, "Msg" : e.message };
        }
    };

    // { "fbFuncName" : "fn_division" }
	var fn_division = function(parsedParams){
        const cLib = fn_cLib(programName + "." + arguments.callee.name);
        cLib.setLogLevel("Debug");

		try {
		    // 로그를 남길필요 없어서 주석처리
            //cLib.programEnd();

            return { "Code" : 0, "Msg" : "", "Division" : cLib.fn_division() };
        } catch ( e ) {
            cLib.error(e.message);
            return { "Code" : -1, "Msg" : e.message };
        }
    };

/************************************************* util logic *************************************************/

/************************************************* Mapping logic **********************************************/
    // Mapping 함수 정의, 마지막에 선언을 해야 함수를 정상적으로 인식함
    const functionMap = {
        "fn_employeesForName" : fn_employeesForName
        ,"fn_employeesForUserIds" : fn_employeesForUserIds
        ,"fn_mailSend" : fn_mailSend
        ,"fn_approvalSubmit" : fn_approvalSubmit
        ,"fn_approvalStatus" : fn_approvalStatus
        ,"fn_cb_approvalRole" : fn_cb_approvalRole
        ,"fn_cb_approvalStatus" :  fn_cb_approvalStatus
        ,"fn_division" :  fn_division
        ,"fn_attachment" : fn_attachment
    };

    return {
        fn_loadFunction : fn_loadFunction
        ,fn_approvalStatus : fn_approvalStatus      // Int3.0 에서 호출할 수 있게 선언
    };
});

/**********************************************************************************************************
************************************** o9.NSCM.JSEWKnoxCommon *********************************************/