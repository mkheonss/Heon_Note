define('o9.NSCM.JSEWKnoxContentsMailVD', ['o9/data/query', 'o9/data/cellset', 'o9.NSCM.commonLibVD'], function () {

/**************************************************************************************
    프로그램명  : o9.NSCM.JSEWKnoxContentsMailVD
    화면명     : Knox 메일 팝업에 들어간 Content 및 기본 정보 세팅( 모듈별로 정의 필요 )
    API 개발자 : sungmin0.lim
    최초생성   : 2026.03.13
**************************************************************************************/

    // fn_cLib 를 통해서 commonLib 를 생성
    var fn_cLib = function(name) {
        return new commonLib.VdCommon(name);
    }
    var fn_cUtil = function() {
        return new commonLib.VdUtil();
    }

	const programName = "o9.NSCM.JSEWKnoxContentsMailVD";
    const commonLib = require('o9.NSCM.commonLibVD');
    const cUtil = fn_cUtil();

    var division = "VD";
    var attachmentService = "o9.NSCM.JSKnoxAttachmentVD";

    // Html 을 그리기 위한 변수 정의
    var tableS = '<table border="1">';
    var trS = "<tr>";
    // {?} 로 컬럼 사이즈 조절, {O} 로 colspan, rowspan 추가
    var thTitleS = '<th align="center" style="background-color:#f3f6f7;" width="{?}" {O}>';
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
    ,"fbParams" : { "Measure.[Knox Mail All Group_Parent Code]" : "Screen"
                    ,"Measure.[Knox Mail All Group_Code]" : "ECP"
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

        var rtnObj = {};

		try {
            cLib.printParams(parsedParams);

            var versionName = cUtil.fn_getFilterVersionName(parsedParams);

            // 사업부 구분을 위해 사용
            rtnObj["division"] = division;

            rtnObj["subject"] = "Knox Test 메일";

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
                }
                rtnObj["contents"] = contents;
            }

            // 첨부할 엑셀 내용이 있으면 내용 생성할 함수 선언. 없으면 빈문자열
            rtnObj["attachmentService"] = attachmentService;
            rtnObj["attachmentFunction"] = "fn_knoxTest_mail";

            // 수신자 정보를 가져온다.
            rtnObj["recipients"] = cLib.fn_recipients(parsedParams);

            cLib.programEnd();
        } catch ( e ) {
            cLib.error(e.message);
            rtnMsg = e.message;
        }

        return rtnObj;
    };

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
****************************************** o9.NSCM.JSEWKnoxContentsMailVD *************************************/