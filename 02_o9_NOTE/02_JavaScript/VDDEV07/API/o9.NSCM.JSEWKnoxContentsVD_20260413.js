define('o9.NSCM.JSEWKnoxContentsVD', ['o9/data/query', 'o9/data/cellset', 'o9.NSCM.commonLibVD'], function () {

/**************************************************************************************
    프로그램명  : o9.NSCM.JSEWKnoxContentsVD
    화면명     : Knox 결재 팝업에 들어간 Content 및 기본 정보 세팅( 모듈별로 정의 필요 )
    API 개발자 : sungmin0.lim
    최초생성   : 2026.02.23
**************************************************************************************/

    // fn_cLib 를 통해서 commonLib 를 생성
    var fn_cLib = function(name) {
        return new commonLib.VdCommon(name);
    }
    var fn_cUtil = function() {
        return new commonLib.VdUtil();
    }

	const programName = "o9.NSCM.JSEWKnoxContentsVD";
    const commonLib = require('o9.NSCM.commonLibVD');
    const cUtil = fn_cUtil();

    var division = "VD";
    var service = "o9.NSCM.JSKnoxServiceVD";
    var attachmentService = "o9.NSCM.JSKnoxAttachmentVD";

    // Html 을 그리기 위한 변수 정의
    var tableS = '<table border="1">';
    var trS = "<tr>";
    // {?} 로 컬럼 사이즈 조절, {O} 로 colspan, rowspan 추가
    var thTitleS = '<td align="center" style="background-color:#f3f6f7;" width="{?}"> {O}';
    var tdLS = '<td align="left">';
    var tdCS = '<td align="center">';
    var tdRS = '<td align="right">';

    var tableE = "</table>";
    var trE = "</tr>";
    var tdE = "</td>";
    var thE = "</th>";

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
{ "fbFuncName" : "fn_knoxTest"
    ,"fbParams" : { "Measure.[Knox Approval All Group_Parent Code]" : "Screen"
                    ,"Measure.[Knox Approval All Group_Code]" : "ECP"
                    ,"filters" : {"[Version].[Version Name]" : {"SelectedMembers" : ["CWV_MP"], "MemberFilter" : "" } }
                  }
    ,"fbGridRows" : [
{ "rowstatus":"C","rowindex":"0","[Location].[Location]":"P105","[Seq].[Seq]":"1","Measure.[Knox Test_A]":"A-P105","Measure.[Knox Test_B]":"B","Measure.[Knox Test_C]":"C","Measure.[Knox Test_D]":"D","Measure.[Knox Test_E]":"E" },
{ "rowstatus":"C","rowindex":"0","[Location].[Location]":"P310","[Seq].[Seq]":"1","Measure.[Knox Test_A]":"A-P310","Measure.[Knox Test_B]":"B","Measure.[Knox Test_C]":"C","Measure.[Knox Test_D]":"D","Measure.[Knox Test_E]":"E" }
                  ]
}
*/
    var fn_knoxTest = function(parsedParams){
        const cLib = fn_cLib(programName + "." + arguments.callee.name);
        cLib.setLogLevel("Debug");

        // 결재 Role 정보
        var rtnObj = cLib.fn_approvalRole();

		try {
            cLib.printParams(parsedParams);

            var versionName = cUtil.fn_getFilterVersionName(parsedParams);

            // 사업부 구분을 위해 사용
            rtnObj["division"] = division;

            rtnObj["subject"] = "Knox Test 결재 요청";

            // 전체 결재라인을 가져온다.
            rtnObj["aplns"] = cLib.fn_aplns(parsedParams);

            // 개인별 결재라인을 가져온다.
            rtnObj["userAplns"] = cLib.fn_aplnsForUser(parsedParams);

            // 상신후에 결재 ID 를 반영할 정보
            var approvalTarget = [];

            // 후처리에서 반영할 정보
            var approvalList = [];

            // Contents 생성
            rtnObj["contents"] = "";
            if ( parsedParams.fbGridRows.length > 0 ) {
                var contents = "<br><br><br>" + tableS;

                // 타이틀 구성
                contents += trS;
                contents += thTitleS.replace("{?}", 50).replace("{O}", '') + "Location" + thE;
                contents += thTitleS.replace("{?}", 50).replace("{O}", '') + "Seq" + thE;
                contents += thTitleS.replace("{?}", 50).replace("{O}", '') + "A Column" + thE;
                contents += thTitleS.replace("{?}", 50).replace("{O}", '') + "B Column" + thE;
                contents += thTitleS.replace("{?}", 50).replace("{O}", '') + "C Column" + thE;
                contents += thTitleS.replace("{?}", 50).replace("{O}", '') + "D Column" + thE;
                contents += thTitleS.replace("{?}", 50).replace("{O}", '') + "E Column" + thE;
                contents += trE;

                // Body 구성
                for ( var i = 0; i < parsedParams.fbGridRows.length; i++ ) {
                    var row = parsedParams.fbGridRows[i];

                    contents += trS;

                    contents += tdLS + row["[Location].[Location]"] + tdE;
                    contents += tdCS + row["[Seq].[Seq]"] + tdE;
                    contents += tdLS + row["Measure.[Knox Test_A]"] + tdE;
                    contents += tdCS + row["Measure.[Knox Test_B]"] + tdE;
                    contents += tdRS + row["Measure.[Knox Test_C]"] + tdE;
                    contents += tdLS + row["Measure.[Knox Test_D]"] + tdE;
                    contents += tdCS + row["Measure.[Knox Test_E]"] + tdE;

                    contents += trE;

                    // 결재 ID 를 저장할 정보 세팅
                    approvalTarget.push({"Grain" : { "[Version].[Version Name]" : versionName
                                                        ,"[Location].[Location]" : row["[Location].[Location]"]
                                                        ,"[Seq].[Seq]" : row["[Seq].[Seq]"] }
                                            ,"IdMeasure" : "Measure.[Knox Test_ApInfId]"
                                            ,"UuMeasure" : "Measure.[Knox Test_Approval By]"
                                            ,"UtMeasure" : "Measure.[Knox Test_Approval Time]"
                                            ,"StatusMeasure" : "Measure.[Knox Test_Status]"});

                    // 후처리에 사용할 approvalList 를 만든다.
                    approvalList.push({"[Version].[Version Name]" : versionName
                                            ,"[Location].[Location]" : row["[Location].[Location]"]
                                            ,"[Seq].[Seq]" : row["[Seq].[Seq]"] });
                }

                rtnObj["contents"] = contents;
            }

            // 후처리에 필요한 파라미터 정의
            rtnObj["service"] = service;
            rtnObj["serviceFunction"] = "fn_knoxTest";
            rtnObj["params"] = JSON.stringify({ "approvalList" : approvalList });

            // 결재 ID 를 저장할 정보 세팅
            rtnObj["approvalTarget"] = approvalTarget;

            // 첨부할 엑셀 내용이 있으면 내용 생성할 함수 선언. 없으면 빈문자열
            rtnObj["attachmentService"] = attachmentService;
            rtnObj["attachmentFunction"] = "fn_knoxTest_approval";

            cLib.programEnd();
        } catch ( e ) {
            cLib.error(e.message);
            rtnMsg = e.message;
        }

        return rtnObj;
    };


/************************************************* util logic *************************************************/
    // 결재 Role 정보 - commonLib 로 옮김
    /*
    var fn_role = function() {
        return { "roleCodes" : ["0","1","2","3","4","7","9"]
                    ,"roleValues" : ["Draft","Approval","Agreement","Conclusion","Parallel Consensus","Parallel Approvals","Notification"]
                    ,"roleHanValues" : ["기안","결재","합의","후결","병렬합의","병렬결재","통보"]};
    }
    */

    // 결재라인 정보 - commonLib 로 옮김
    /*
    var fn_aplns = function(parsedParams, cLib){
        var aplns = [];

		try {
            var version = cUtil.fn_getFilterVersion(parsedParams);
            var versionName = cUtil.fn_getFilterVersionName(parsedParams);
            var email = cLib.selectResult('CurrentUser().Name');

            if ( parsedParams.fbParams["Knox Approval Group_Code"] != "" ) {
                var result = cLib.selectList([version
                                                    ,"[Personnel].[Email].[" + email + "]"
                                                    ,"[Seq].[Seq]"]
                                                 ,["Measure.[Knox Approval Group_Name]"]
                                                 ,'where { Measure.[Knox Approval Group_Code] == "' + parsedParams.fbParams["Knox Approval Group_Code"] + '" }'
                                                 ,""
                                                 ,"");
                if ( result.cs.rowCount > 0 ) {
                    var seq = cUtil.fn_getDimValue(result, 0, "Seq", "Seq");

                    // 결재 정보를 가져온다.
                    result = cLib.selectList([version
                                                    ,"[Personnel].[Email].[" + email + "]"
                                                    ,"[Seq].[Seq].[" + seq + "]"
                                                    ,"[Seq1].[Seq1]"]
                                                 ,["Measure.[Knox Approval Group Line_UserId]"
                                                    ,"Measure.[Knox Approval Group Line_Role]"
                                                    ,"Measure.[Knox Approval Group Line_Order]"]
                                                 ,""
                                                 ,"orderby Measure.[Knox Approval Group Line_Order]"
                                                 ,"");
                    for ( var i = 0; i < result.cs.rowCount; i++ ) {
                        var aplnsInfo = {"userId" : cUtil.fn_getMeaValue(result, i, "Knox Approval Group Line_UserId")
                                        ,"role" : cUtil.fn_getMeaValue(result, i, "Knox Approval Group Line_Role") //기안(0), 결재(1), 합의(2), 후결(3), 병렬합의(4), 병렬결재(7), 통보(9)(후결자는 최대 1명, 병렬결재 & 병렬합의자는 최소 2명 이상)
                                        ,"seq" : i + ""
                                        ,"aplnStatsCode" : "0"          //처리구분 미결(0), 결재(1), 반려(2), 전결(3), 자동결재(5)
                                        ,"aplnMdfyPmtYn" : "Y"          //경로변경권한여부
                                        ,"arbPmtYn" : "Y"               //전결권한여부
                                        ,"contentsMdfyPmtYn" : "Y"      //본문수정권한여부
                                     };
                        aplns.push(aplnsInfo);
                    }
                }
            }
        } catch ( e ) {
            cLib.error(e.message);
        }

        return aplns;
    };
    */

    // 결재라인 정보 - commonLib 로 옮김
    /*
    var fn_aplnsKnox = function(parsedParams, cLib){
        var aplns = [];

		try {
            var version = cUtil.fn_getFilterVersion(parsedParams);
            var versionName = cUtil.fn_getFilterVersionName(parsedParams);
            var email = cLib.selectResult('CurrentUser().Name');

            if ( parsedParams.fbParams["Knox Approval Group_Code"] != "" ) {
                var result = cLib.selectList([version
                                                    ,"[Personnel].[Email].[" + email + "]"
                                                    ,"[Seq].[Seq]"]
                                                 ,["Measure.[Knox Approval Group_Name]"]
                                                 ,'where { Measure.[Knox Approval Group_Code] == "' + parsedParams.fbParams["Knox Approval Group_Code"] + '" }'
                                                 ,""
                                                 ,"");
                if ( result.cs.rowCount > 0 ) {
                    var seq = cUtil.fn_getDimValue(result, 0, "Seq", "Seq");

                    // 임직원 정보를 가져온다.
                    var userIds = "";
                    result = cLib.selectList([version
                                                    ,"[Personnel].[Email].[" + email + "]"
                                                    ,"[Seq].[Seq].[" + seq + "]"
                                                    ,"[Seq1].[Seq1]"]
                                                 ,["Measure.[Knox Approval Group Line_UserId]"
                                                    ,"Measure.[Knox Approval Group Line_Role]"
                                                    ,"Measure.[Knox Approval Group Line_Order]"]
                                                 ,""
                                                 ,"orderby Measure.[Knox Approval Group Line_Order]"
                                                 ,"");
                    for ( var i = 0; i < result.cs.rowCount; i++ ) {
                        userIds = cUtil.fn_wordAppend(userIds, cUtil.fn_getMeaValue(result, i, "Knox Approval Group Line_UserId"));
                    }
                    // 데이타 삭제
                    cLib.deleteMeasure([version, "[Personnel].[Email].[" + email + "]"], 'Knox Employee');
                    // Knox 파이썬 실행
                    var execQuery = 'EXEC plugin instance [PY_Knox_Employees] ' +
                                    'for measures {[Knox Employee_UserId]} ' +
                                    'using scope ( ' + version + ' * [Personnel].[Email].[' + email + '] ) ' +
                                    'using arguments { (pVersionName, "' + versionName + '"), ' +
                                    '                  (pEmail, "' + email + '"), ' +
                                    '                  (pField, "userIds"), ' +
                                    '                  (pValue, "' + userIds + '"), ' +
                                    '                  (ExecutionMode, "MediumWeight"), (MaxSliceTableCells, 200000000), (MaxConcurrency, 1 )};'
                    cLib.executePython("PY_Knox_Employees", execQuery);
                    // 싱글정보 가져오기
                    var employees = {};
                    result = cLib.selectList([version
                                                        ,"[Personnel].[Email].[" + email + "]"
                                                        ,"Seq.[Seq]"]
                                                     ,["Measure.[Knox Employee_UserId]"
                                                        ,"Measure.[Knox Employee_Email]"
                                                        ,"Measure.[Knox Employee_UserName]"
                                                        ,"Measure.[Knox Employee_CompanyName]"
                                                        ,"Measure.[Knox Employee_DepartmentName]"]
                                                     ,"", "", "");
                    for ( var i = 0; i < result.cs.rowCount; i++ ) {
                        employees[cUtil.fn_getMeaValue(result, i, "Knox Employee_UserId")] =
                                {"Email" : cUtil.fn_getMeaValue(result, i, "Knox Employee_Email")
                                    ,"UserName" : cUtil.fn_getMeaValue(result, i, "Knox Employee_UserName")
                                    ,"CompanyName" : cUtil.fn_getMeaValue(result, i, "Knox Employee_CompanyName")
                                    ,"DepartmentName" : cUtil.fn_getMeaValue(result, i, "Knox Employee_DepartmentName")};
                    }

                    // 결재 정보를 가져온다.
                    result = cLib.selectList([version
                                                    ,"[Personnel].[Email].[" + email + "]"
                                                    ,"[Seq].[Seq].[" + seq + "]"
                                                    ,"[Seq1].[Seq1]"]
                                                 ,["Measure.[Knox Approval Group Line_UserId]"
                                                    ,"Measure.[Knox Approval Group Line_Role]"
                                                    ,"Measure.[Knox Approval Group Line_Order]"]
                                                 ,""
                                                 ,"orderby Measure.[Knox Approval Group Line_Order]"
                                                 ,"");
                    for ( var i = 0; i < result.cs.rowCount; i++ ) {
                        var aplnsInfo = {"userId" : cUtil.fn_getMeaValue(result, i, "Knox Approval Group Line_UserId")
                                        ,"role" : cUtil.fn_getMeaValue(result, i, "Knox Approval Group Line_Role") //기안(0), 결재(1), 합의(2), 후결(3), 병렬합의(4), 병렬결재(7), 통보(9)(후결자는 최대 1명, 병렬결재 & 병렬합의자는 최소 2명 이상)
                                        ,"seq" : i + ""
                                        ,"aplnStatsCode" : "0"          //처리구분 미결(0), 결재(1), 반려(2), 전결(3), 자동결재(5)
                                        ,"aplnMdfyPmtYn" : "Y"          //경로변경권한여부
                                        ,"arbPmtYn" : "Y"               //전결권한여부
                                        ,"contentsMdfyPmtYn" : "Y"      //본문수정권한여부
                                     };
                        var employee = employees[aplnsInfo["userId"]];
                        if ( employee != undefined ) {
                            aplnsInfo["Email"] = employee["Email"];
                            aplnsInfo["UserName"] = employee["UserName"];
                            aplnsInfo["CompanyName"] = employee["CompanyName"];
                            aplnsInfo["DepartmentName"] = employee["DepartmentName"];
                        }
                        aplns.push(aplnsInfo);
                    }
                }
            }
        } catch ( e ) {
            cLib.error(e.message);
        }

        return aplns;
    };
    */

/************************************************* Mapping logic **********************************************/
    // Mapping 함수 정의, 마지막에 선언을 해야 함수를 정상적으로 인식함
    const functionMap = {
        "fn_knoxTest" : fn_knoxTest
    };

    return {
        fn_loadFunction : fn_loadFunction
    };
});

/**************************************************************************************************************
****************************************** o9.NSCM.JSEWKnoxContentsVD ****************************************/