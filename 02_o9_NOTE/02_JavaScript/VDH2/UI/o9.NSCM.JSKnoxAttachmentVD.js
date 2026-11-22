define('o9.NSCM.JSKnoxAttachmentVD', ['o9/data/query', 'o9/data/cellset', 'o9.NSCM.commonLibVD'], function () {

/**************************************************************************************
    프로그램명  : o9.NSCM.JSKnoxAttachmentVD
    화면명     : Knox 엑셀 첨부 로직
    API 개발자 : sungmin0.lim
    최초생성   : 2026.03.14
**************************************************************************************/

    // fn_cLib 를 통해서 commonLib 를 생성
    var fn_cLib = function(name) {
        return new commonLib.VdCommon(name);
    }
    var fn_cUtil = function() {
        return new commonLib.VdUtil();
    }

	const programName = "o9.NSCM.JSKnoxAttachmentVD";
    const commonLib = require('o9.NSCM.commonLibVD');
    const cUtil = fn_cUtil();

/************************************************* common logic *************************************************/
    var fn_knoxTest_approval = function(o9Params){
        const cLib = fn_cLib(programName + "." + arguments.callee.name);
        cLib.setLogLevel("Debug");

        var rtn = {"Error" : "", "attachmentText" : ""};

		try {
            //cLib.printParams(o9Params);

		    var p = o9Params;

            // Version 은 CurrentWorkingView 를 사용하도록 함
		    // var version = cUtil.fn_getFilterVersion(p);
		    var version = "[Version].[Version Name].[CurrentWorkingView]";

            // 첨부파일 내용 생성
            var attachmentText = "";
            // 헤더
            attachmentText = "Location^:^Seq^:^A^:^B^:^C^:^D^:^E^^^";
            // 정렬
            attachmentText += "left^:^right^:^left^:^center^:^left^:^left^:^left^^^";
            // 사이즈
            attachmentText += "20^:^5^:^40^:^50^:^60^:^30^:^15^^^";
            // Body 구성
            for ( var i = 0; i < p.fbGridRows.length; i++ ) {
                var row = p.fbGridRows[i];

                attachmentText += row["[Location].[Location]"] + "^:^"
                                    + row["[Seq].[Seq]"] + "^:^"
                                    + row["Measure.[Knox Test_A]"] + "^:^"
                                    + row["Measure.[Knox Test_B]"] + "^:^"
                                    + row["Measure.[Knox Test_C]"] + "^:^"
                                    + row["Measure.[Knox Test_D]"] + "^:^"
                                    + row["Measure.[Knox Test_E]"]

                if ( i < p.fbGridRows.length - 1) {
                    attachmentText += "^^^";
                };
            }

            if ( p.fbParams["[Personnel].[Email]"] != undefined ) {
                cLib.updateMeasure([version
                                        ,"[Personnel].[Email].[" + p.fbParams["[Personnel].[Email]"] + "]"
                                        ,"[Time].[Day].[" + p.fbParams["[Time].[Day]"] + "]"
                                        ,"[Time Seq].[Time Seq].[" + p.fbParams["[[Time Seq].[Time Seq]"] + "]"]
                                   ,[cUtil.fn_qMeaStr(null, "Measure.[Knox Approval_Attachment Text]", attachmentText)]);
            } else {
                rtn.attachmentText = attachmentText;
            }

            // 로그룰 남기지 않기 위해 주석처리
            // cLib.programEnd();
        } catch ( e ) {
            cLib.error(e.message);
            rtn.Error = e.message;
        }

        return rtn;
    };

    var fn_knoxTest_mail = function(o9Params){
        const cLib = fn_cLib(programName + "." + arguments.callee.name);
        cLib.setLogLevel("Debug");

        var rtn = {"Error" : "", "attachmentText" : ""};

		try {
            //cLib.printParams(o9Params);

		    var p = o9Params;

            // Version 은 CurrentWorkingView 를 사용하도록 함
		    // var version = cUtil.fn_getFilterVersion(p);
		    var version = "[Version].[Version Name].[CurrentWorkingView]";

            // 첨부파일 내용 생성
            var attachmentText = "";
            // 헤더
            attachmentText = "Location^:^Seq^:^A^:^B^:^C^:^D^:^E^^^";
            // 정렬
            attachmentText += "left^:^right^:^left^:^center^:^left^:^left^:^left^^^";
            // 사이즈
            attachmentText += "20^:^5^:^40^:^50^:^60^:^30^:^15^^^";
            // Body 구성
            for ( var i = 0; i < p.fbGridRows.length; i++ ) {
                var row = p.fbGridRows[i];

                attachmentText += row["[Location].[Location]"] + "^:^"
                                    + row["[Seq].[Seq]"] + "^:^"
                                    + row["Measure.[Knox Test_A]"] + "^:^"
                                    + row["Measure.[Knox Test_B]"] + "^:^"
                                    + row["Measure.[Knox Test_C]"] + "^:^"
                                    + row["Measure.[Knox Test_D]"] + "^:^"
                                    + row["Measure.[Knox Test_E]"]

                if ( i < p.fbGridRows.length - 1) {
                    attachmentText += "^^^";
                };
            }

            if ( p.fbParams["[Personnel].[Email]"] != undefined ) {
                cLib.updateMeasure([version
                                        ,"[Personnel].[Email].[" + p.fbParams["[Personnel].[Email]"] + "]"
                                        ,"[Time].[Day].[" + p.fbParams["[Time].[Day]"] + "]"
                                        ,"[Time Seq].[Time Seq].[" + p.fbParams["[[Time Seq].[Time Seq]"] + "]"]
                                   ,[cUtil.fn_qMeaStr(null, "Measure.[Knox Mail_Attachment Text]", attachmentText)]);
            } else {
                rtn.attachmentText = attachmentText;
            }

            rtn.attachmentText = attachmentText;

            // 로그룰 남기지 않기 위해 주석처리
            // cLib.programEnd();
        } catch ( e ) {
            cLib.error(e.message);
            rtn.Error = e.message;
        }

        return rtn;
    };

    return {
        fn_knoxTest_mail : fn_knoxTest_mail
        ,fn_knoxTest_approval : fn_knoxTest_approval
    };
});

/*************************************************************************************************************
***************************************** o9.NSCM.JSKnoxAttachmentVD *****************************************/