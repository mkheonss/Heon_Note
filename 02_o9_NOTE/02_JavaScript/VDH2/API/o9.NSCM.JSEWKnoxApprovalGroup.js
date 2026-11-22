define('o9.NSCM.JSEWKnoxApprovalGroup', ['o9/data/query', 'o9/data/cellset', 'o9.NSCM.commonLibVD'], function () {

/**************************************************************************************
    프로그램명  : o9.NSCM.JSEWKnoxApprovalGroup
    화면명     : Knox Approval Group
    화면 설계자 : 임성민 프로
    화면 개발자 : 오동민 프로
    API 개발자 : sungmin0.lim
    최초생성   : 2026.03.24
**************************************************************************************/

    // fn_cLib 를 통해서 commonLib 를 생성
    var fn_cLib = function(name) {
        return new commonLib.VdCommon(name);
    }
    var fn_cUtil = function() {
        return new commonLib.VdUtil();
    }

	const programName = "o9.NSCM.JSEWKnoxApprovalGroup";
    const commonLib = require('o9.NSCM.commonLibVD');
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
            cLib.error(e.message);
            return { "Code" : -1, "Msg" : e.message };
        }
	};

/************************************************* common logic *************************************************/
/*
{ "fbFuncName" : "fn_save"
  ,"fbParams" : { "filters" : { "[Version].[Version Name]" : {"SelectedMembers" : ["CWV_MP"], "MemberFilter" : "" } }
                }
  ,"fbGridRows" : {
        "tGrid" : [
                        { "rowstatus":"U","rowindex":"0","[Personnel].[Email]" : "sungmin0.lim", "[Seq].[Seq]":"1","Measure.[Knox Approval Group_Code]":"Screen","Measure.[Knox Approval Group_Name]":"화면별 결재 라인" },
                        { "rowstatus":"U","rowindex":"1","[Personnel].[Email]" : "sungmin0.lim", "[Seq].[Seq]":"2","Measure.[Knox Approval Group_Code]":"TP","Measure.[Knox Approval Group_Name]":"TP 화면 결재 라인" },
                        { "rowstatus":"U","rowindex":"2","[Personnel].[Email]" : "sungmin0.lim", "[Seq].[Seq]":"3","Measure.[Knox Approval Group_Code]":"ECP","Measure.[Knox Approval Group_Name]":"ECP 화면 결재 라인" }
                   ]
        ,"bGrid" : [
                        { "rowstatus":"U","rowindex":"0","[Personnel].[Email]" : "sungmin0.lim", "[Seq].[Seq]":"2","[Seq1].[Seq1]":"1","Measure.[Knox Approval Group Line_UserId]":"dmin.oh","Measure.[Knox Approval Group Line_Role]":"1","Measure.[Knox Approval Group Line_Role Name]":"결재","Measure.[Knox Approval Group Line_Order]":"1" },
                        { "rowstatus":"U","rowindex":"1","[Personnel].[Email]" : "sungmin0.lim", "[Seq].[Seq]":"3","[Seq1].[Seq1]":"1","Measure.[Knox Approval Group Line_UserId]":"dmin.oh","Measure.[Knox Approval Group Line_Role]":"1","Measure.[Knox Approval Group Line_Role Name]":"결재","Measure.[Knox Approval Group Line_Order]":"1" },
                        { "rowstatus":"U","rowindex":"2","[Personnel].[Email]" : "sungmin0.lim", "[Seq].[Seq]":"4","[Seq1].[Seq1]":"1","Measure.[Knox Approval Group Line_UserId]":"dmin.oh","Measure.[Knox Approval Group Line_Role]":"1","Measure.[Knox Approval Group Line_Role Name]":"결재","Measure.[Knox Approval Group Line_Order]":"1" }
                   ]
  }
}
*/
    var fn_save = function(parsedParams){
        const cLib = fn_cLib(programName + "." + arguments.callee.name);
        cLib.setLogLevel("Debug");

		try {
		    cLib.printParams(parsedParams);

            var version = cUtil.fn_getFilterVersion(parsedParams);

            // Top Grid 저장
            for ( var i = 0; i < parsedParams.fbGridRows.tGrid.length; i++ ) {
                var row = parsedParams.fbGridRows.tGrid[i];
                var rowstatus = row["rowstatus"];

                if ( rowstatus == "C" ) {
                    // Max 값을 구한다.
                    var result = cLib.selectList([version
                                                    ,cUtil.fn_qDim(row, "[Personnel].[Email]")
                                                    ,"[Seq].[Seq]"],
                                                 ["Measure.[Knox Approval Group_Code]"],
                                                 "",
                                                 "orderby [Seq].[Seq].Key desc",
                                                 "limit 1");
                    var seq = "1";
                    if ( result.cs.rowCount > 0 ) {
                        seq = (parseInt(cUtil.fn_getDimValue(result, 0, "Seq", "Seq")) + 1) + "";
                    }

                    var dimensions = [];
                    dimensions.push(version);
                    dimensions.push(cUtil.fn_qDim(row, "[Personnel].[Email]"));
                    dimensions.push(cUtil.fn_qDim(row, "[Seq].[Seq]", seq));

                    var measures = [];
                    measures.push(cUtil.fn_qMeaStr(row, "Measure.[Knox Approval Group_Code]"));
                    measures.push(cUtil.fn_qMeaStr(row, "Measure.[Knox Approval Group_Name]"));

                    cLib.createMeasure(dimensions, measures);
                } else if ( rowstatus == "U" ) {
                    var dimensions = [];
                    dimensions.push(version);
                    dimensions.push(cUtil.fn_qDim(row, "[Personnel].[Email]"));
                    dimensions.push(cUtil.fn_qDim(row, "[Seq].[Seq]"));

                    var measures = [];
                    measures.push(cUtil.fn_qMeaStr(row, "Measure.[Knox Approval Group_Code]"));
                    measures.push(cUtil.fn_qMeaStr(row, "Measure.[Knox Approval Group_Name]"));

                    cLib.updateBlockMeasure(dimensions, measures);
                } else if ( rowstatus == "D" ) {
                    var where = [];
                    where.push(version);
                    where.push(cUtil.fn_qDim(row, "[Personnel].[Email]"));
                    where.push(cUtil.fn_qDim(row, "[Seq].[Seq]"));

                    cLib.deleteMeasure(where, "Knox Approval Group");
                    cLib.deleteMeasure(where, "Knox Approval Group Line");
                }
            }


            // Bottom Grid 저장
            for ( var i = 0; i < parsedParams.fbGridRows.bGrid.length; i++ ) {
                var row = parsedParams.fbGridRows.bGrid[i];
                var rowstatus = row["rowstatus"];

                if ( rowstatus == "C" ) {
                    // Max 값을 구한다.
                    var result = cLib.selectList([version
                                                    ,cUtil.fn_qDim(row, "[Personnel].[Email]")
                                                    ,cUtil.fn_qDim(row, "[Seq].[Seq]")
                                                    ,"[Seq1].[Seq1]"],
                                                 ["Measure.[Knox Approval Group Line_UserId]"],
                                                 "",
                                                 "orderby [Seq1].[Seq1].Key desc",
                                                 "limit 1");
                    var seq1 = "1";
                    if ( result.cs.rowCount > 0 ) {
                        seq1 = (parseInt(cUtil.fn_getDimValue(result, 0, "Seq1", "Seq1")) + 1) + "";
                    }

                    var dimensions = [];
                    dimensions.push(version);
                    dimensions.push(cUtil.fn_qDim(row, "[Personnel].[Email]"));
                    dimensions.push(cUtil.fn_qDim(row, "[Seq].[Seq]"));
                    dimensions.push(cUtil.fn_qDim(null, "[Seq1].[Seq1]", seq1));

                    var measures = [];
                    measures.push(cUtil.fn_qMeaStr(row, "Measure.[Knox Approval Group Line_UserId]"));
                    measures.push(cUtil.fn_qMeaStr(row, "Measure.[Knox Approval Group Line_Role]"));
                    measures.push(cUtil.fn_qMeaStr(row, "Measure.[Knox Approval Group Line_Role Name]"));
                    measures.push(cUtil.fn_qMeaStr(row, "Measure.[Knox Approval Group Line_Order]"));

                    cLib.createMeasure(dimensions, measures);
                } else if ( rowstatus == "U" ) {
                    var dimensions = [];
                    dimensions.push(version);
                    dimensions.push(cUtil.fn_qDim(row, "[Personnel].[Email]"));
                    dimensions.push(cUtil.fn_qDim(row, "[Seq].[Seq]"));
                    dimensions.push(cUtil.fn_qDim(row, "[Seq1].[Seq1]"));

                    var measures = [];
                    measures.push(cUtil.fn_qMeaStr(row, "Measure.[Knox Approval Group Line_UserId]"));
                    measures.push(cUtil.fn_qMeaStr(row, "Measure.[Knox Approval Group Line_Role]"));
                    measures.push(cUtil.fn_qMeaStr(row, "Measure.[Knox Approval Group Line_Role Name]"));
                    measures.push(cUtil.fn_qMeaStr(row, "Measure.[Knox Approval Group Line_Order]"));

                    cLib.updateBlockMeasure(dimensions, measures);
                } else if ( rowstatus == "D" ) {
                    var where = [];
                    where.push(version);
                    where.push(cUtil.fn_qDim(row, "[Personnel].[Email]"));
                    where.push(cUtil.fn_qDim(row, "[Seq].[Seq]"));
                    where.push(cUtil.fn_qDim(row, "[Seq1].[Seq1]"));

                    cLib.deleteMeasure(where, "Knox Approval Group Line");
                }
            }

            return { "Code" : 0, "Msg" : "It was saved successfully." };
        } catch ( e ) {
            cLib.error(e.message);
            return { "Code" : -1, "Msg" : e.message };
        } finally {
            cLib.programEnd();
        }
    };

    // { "fbFuncName" : "fn_cb_role" }
	var fn_cb_role = function(parsedParams){
        const cLib = fn_cLib(programName + "." + arguments.callee.name);
        cLib.setLogLevel("Debug");

		try {
            cLib.printParams(parsedParams);

            var comboList = cLib.fn_makeCombo(null, {ComboCodes : ["1","2","3","4","7","9"], ComboValues : ["결재","합의","후결","병렬합의","병렬결재","통보"]});
            cLib.debug("ComboData : " + JSON.stringify(comboList.slice(0,3)));

            cLib.programEnd();

            return { "Code" : 0, "Msg" : "", "Rows" : comboList };
        } catch ( e ) {
            cLib.error(e.message);
            return { "Code" : -1, "Msg" : e.message };
        }
    };

    /*
        { "fbFuncName" : "fn_cb_email"
          ,"fbParams" : { "[Personnel].[Email]" : "sungmin" }
        }
    */
	var fn_cb_email = function(parsedParams){
        const cLib = fn_cLib(programName + "." + arguments.callee.name);
        cLib.setLogLevel("Debug");

		try {
            cLib.printParams(parsedParams);

            var result = cLib.selectList(["[Personnel].[Email]" + cUtil.fn_filterStr(cUtil.fn_getParam(parsedParams, "[Personnel].[Email]") + "%")], [], "", "", "limit 3000");
            var comboList = cLib.fn_makeCombo(result, {DimName : "Personnel", DimAttbName : "Email", Sort : "Name"});
            cLib.debug("ComboData : " + JSON.stringify(comboList.slice(0,3)));

            cLib.programEnd();

            return { "Code" : 0, "Msg" : "", "Rows" : comboList };
        } catch ( e ) {
            cLib.error(e.message);
            return { "Code" : -1, "Msg" : e.message };
        }
    };

/************************************************* util logic *************************************************/

/************************************************* Mapping logic **********************************************/
    // Mapping 함수 정의, 마지막에 선언을 해야 함수를 정상적으로 인식함
    const functionMap = {
        "fn_save" : fn_save
        ,"fn_cb_role" : fn_cb_role
        ,"fn_cb_email" : fn_cb_email
    };

    return {
        fn_loadFunction : fn_loadFunction
    };
});

/**************************** o9.NSCM.JSEWKnoxApprovalGroup ****************************
**************************************************************************************/