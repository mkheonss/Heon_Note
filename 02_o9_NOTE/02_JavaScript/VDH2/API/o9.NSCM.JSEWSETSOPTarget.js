define('o9.NSCM.JSEWSETSOPTarget', ['o9/data/query', 'o9/data/cellset', 'o9.NSCM.commonLibVD'], function () {

/**************************************************************************************
    프로그램명  : o9.NSCM.JSEWSETSOPTarget
    화면명     : SET SOP Target
    화면 개발자 : 이성한 프로
    API 개발자 : sungmin0.lim
    최초생성   : 2025.08.4
**************************************************************************************/

	const programName = "o9.NSCM.JSEWSETSOPTarget";
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
- 추가 테스트
{ "fbFuncName" : "fn_save", "fbParams" : { "[Version].[Version Name]" : "CWV_MP" },
  "fbGridRows" : [
{ "rowstatus":"C","rowindex":"0","[Group].[Group ID]":"","[Location].[Location]":"P306","[Item].[Product Group]":"TV","Measure.[SET Frozen SOP Target_Product]":"QLED","Measure.[SET Frozen SOP Target_Forminch]":"55","Measure.[SET Frozen SOP Target_Toinch]":"55","Measure.[SET Frozen SOP Target_Definition]":"QLED","Measure.[SET Frozen SOP Target_Year]":"2025","Measure.[SET Frozen SOP Target_SCMType]":"SET","Measure.[SET Frozen SOP Target_Mktname]":"Frame","Measure.[SET Frozen SOP Target_Item]":"QE55LS03FAUXMI","Measure.[SET Frozen SOP Target_Itemfence]":"4","Measure.[SET Frozen SOP Target_Groupfence]":"-","Measure.[SET Frozen SOP Target_Hero]":"11","Measure.[SET Frozen SOP Target_Valid]":"Y","Measure.[SET Frozen SOP Target_Applyorder]":"3","Measure.[SET Frozen SOP Target_Description]":"" },
{ "rowstatus":"C","rowindex":"1","[Group].[Group ID]":"","[Location].[Location]":"P306","[Item].[Product Group]":"TV","Measure.[SET Frozen SOP Target_Product]":"LED_TV","Measure.[SET Frozen SOP Target_Forminch]":"50","Measure.[SET Frozen SOP Target_Toinch]":"50","Measure.[SET Frozen SOP Target_Definition]":"UHD","Measure.[SET Frozen SOP Target_Year]":"2025","Measure.[SET Frozen SOP Target_SCMType]":"SET","Measure.[SET Frozen SOP Target_Mktname]":"U8↑","Measure.[SET Frozen SOP Target_Item]":"UE50U8000FUXMI","Measure.[SET Frozen SOP Target_Itemfence]":"2","Measure.[SET Frozen SOP Target_Groupfence]":"202526","Measure.[SET Frozen SOP Target_Hero]":"8","Measure.[SET Frozen SOP Target_Valid]":"Y","Measure.[SET Frozen SOP Target_Applyorder]":"12","Measure.[SET Frozen SOP Target_Description]":"25년 모델 FIX" }
                  ] }

- 수정 테스트
{ "fbFuncName" : "fn_save", "fbParams" : { "[Version].[Version Name]" : "CWV_MP" },
  "fbGridRows" : [
{ "rowstatus":"U","rowindex":"1","[Group].[Group ID]":"MFF_S_00001","[Location].[Location]":"P306","[Item].[Product Group]":"TV","Measure.[SET Frozen SOP Target_Product]":"QLED","Measure.[SET Frozen SOP Target_Forminch]":"55","Measure.[SET Frozen SOP Target_Toinch]":"55","Measure.[SET Frozen SOP Target_Definition]":"QLED","Measure.[SET Frozen SOP Target_Year]":"2025","Measure.[SET Frozen SOP Target_SCMType]":"SET","Measure.[SET Frozen SOP Target_Mktname]":"Frame","Measure.[SET Frozen SOP Target_Item]":"QE55LS03FAUXMI","Measure.[SET Frozen SOP Target_Itemfence]":"4","Measure.[SET Frozen SOP Target_Groupfence]":"-","Measure.[SET Frozen SOP Target_Hero]":"111","Measure.[SET Frozen SOP Target_Valid]":"Y","Measure.[SET Frozen SOP Target_Applyorder]":"12","Measure.[SET Frozen SOP Target_Description]":"" }
                  ] }

- 삭제 테스트
{ "fbFuncName" : "fn_save", "fbParams" : { "[Version].[Version Name]" : "CWV_MP" },
  "fbGridRows" : [
{ "rowstatus":"D","rowindex":"1","[Group].[Group ID]":"MFF_S_00001","[Location].[Location]":"P306","[Item].[Product Group]":"TV","Measure.[SET Frozen SOP Target_Product]":"QLED","Measure.[SET Frozen SOP Target_Forminch]":"55","Measure.[SET Frozen SOP Target_Toinch]":"55","Measure.[SET Frozen SOP Target_Definition]":"QLED","Measure.[SET Frozen SOP Target_Year]":"2025","Measure.[SET Frozen SOP Target_SCMType]":"SET","Measure.[SET Frozen SOP Target_Mktname]":"Frame","Measure.[SET Frozen SOP Target_Item]":"QE55LS03FAUXMI","Measure.[SET Frozen SOP Target_Itemfence]":"4","Measure.[SET Frozen SOP Target_Groupfence]":"-","Measure.[SET Frozen SOP Target_Hero]":"11","Measure.[SET Frozen SOP Target_Valid]":"Y","Measure.[SET Frozen SOP Target_Applyorder]":"3","Measure.[SET Frozen SOP Target_Description]":"" }
                  ] }
    */
    var fn_save = function(parsedParams){
        const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
        vdCommon.setLogLevel("Debug");

		try {
		    var validHm = {};
		    function existMember(gubun, memberData) {
		        var exist = false;

                if ( memberData == "All" ) {
                    return true;
                }
		        if ( validHm[gubun + "_" + memberData] == undefined ) {
	                if ( vdCommon.existMember(gubun, memberData) ) {
	                    validHm[gubun + "_" + memberData] = "Y";
	                    exist = true;
		            }
		        } else {
		            exist = true;
		        }
		        return exist;
		    }

		    var fbVersion = parsedParams.fbParams["[Version].[Version Name]"];

            // Validation 체크
            var validation = [];
            for ( var i = 0; i < parsedParams.fbGridRows.length; i++ ) {
                var row = parsedParams.fbGridRows[i];
                var rowstatus = row["rowstatus"];
                var rowindex = row["rowindex"];

                var validMsg = "";
                if ( rowstatus == "C" || rowstatus == "U" ) {
                    if ( existMember("[Item].[Product]", row["Measure.[SET Frozen SOP Target_Product]"]) == false ) {
                        validMsg += (validMsg == "" ? "" : ", ") + "Product";
                    }
                    if ( existMember("[Item].[Inch]", row["Measure.[SET Frozen SOP Target_Forminch]"]) == false ) {
                        validMsg += (validMsg == "" ? "" : ", ") + "Forminch";
                    }
                    if ( existMember("[Item].[Inch]", row["Measure.[SET Frozen SOP Target_Toinch]"]) == false ) {
                        validMsg += (validMsg == "" ? "" : ", ") + "Toinch";
                    }
                    if ( existMember("[Item].[Definition]", row["Measure.[SET Frozen SOP Target_Definition]"]) == false ) {
                        validMsg += (validMsg == "" ? "" : ", ") + "Definition";
                    }
                    if ( existMember("[Item].[Year]", row["Measure.[SET Frozen SOP Target_Year]"]) == false ) {
                        validMsg += (validMsg == "" ? "" : ", ") + "Year";
                    }
                    if ( existMember("[Item].[SCM Type]", row["Measure.[SET Frozen SOP Target_SCMType]"]) == false ) {
                        validMsg += (validMsg == "" ? "" : ", ") + "SCM Type";
                    }
                    if ( existMember("[Item].[Marketing Name]", row["Measure.[SET Frozen SOP Target_Mktname]"]) == false ) {
                        validMsg += (validMsg == "" ? "" : ", ") + "Mktname";
                    }
                    if ( existMember("[Item].[Item]", row["Measure.[SET Frozen SOP Target_Item]"]) == false ) {
                        validMsg += (validMsg == "" ? "" : ", ") + "Item";
                    }

                    if ( validMsg != "" ) {
                        validation.push(rowindex + "^" + "check [" + validMsg + "]");
                    }
                }
            }

            if ( validation.length > 0 ) {
                return { "Code" : 1, "Msg" : validation };
            }

            // 저장
            for ( var i = 0; i < parsedParams.fbGridRows.length; i++ ) {
                var row = parsedParams.fbGridRows[i];
                var rowstatus = row["rowstatus"];

                if ( rowstatus == "C" ) {// Max 값을 구한다.
                    var result = vdCommon.selectList([vdUtil.fn_qDimVersionName(parsedParams),
                                                        "[Location].[Location]",
                                                        "[Item].[Product Group]",
                                                        "[Group].[Group ID].filter(#.Name startswith([MFF_S_]))"],
                                                    ["Measure.[SET Frozen SOP Target_Product]"],
                                                    "",
                                                    "orderby [Group].[Group ID].Name desc",
                                                    "limit 1");
                    var groupId = "MFF_S_00001";
                    if ( result.cs.rowCount > 0 ) {
                        groupId = "MFF_S_" + vdUtil.fn_lpad((parseInt(result.cs.row(0).cell(result.cs.memberColumnIndex("Group", "Group ID")).Name.substr(6)) + 1) + "", 5, "0");
                    }
                    // Dimension 을  추가한다.
                    if ( !vdCommon.existDimension(['[Group].[Group Type].[MFF_S]','[Group].[Group ID].[' + groupId + ']']) ) {
                        vdCommon.createDimension(['[Group].[Group Type]','[Group].[Group Name]','[Group].[Group ID]'], ["MFF_S", groupId, groupId]);
                    }

                    var dimensions = [];
                    dimensions.push(vdUtil.fn_qDimVersionName(parsedParams));
                    dimensions.push(vdUtil.fn_qDim(row, "[Location].[Location]"));
                    dimensions.push(vdUtil.fn_qDim(row, "[Item].[Product Group]"));
                    dimensions.push(vdUtil.fn_qDim(row, "[Group].[Group ID]", groupId));

                    var measures = [];
                    measures.push(vdUtil.fn_qMeaStr(row, "Measure.[SET Frozen SOP Target_Product]"));
                    measures.push(vdUtil.fn_qMeaStr(row, "Measure.[SET Frozen SOP Target_Forminch]"));
                    measures.push(vdUtil.fn_qMeaStr(row, "Measure.[SET Frozen SOP Target_Toinch]"));
                    measures.push(vdUtil.fn_qMeaStr(row, "Measure.[SET Frozen SOP Target_Definition]"));
                    measures.push(vdUtil.fn_qMeaStr(row, "Measure.[SET Frozen SOP Target_Year]"));
                    measures.push(vdUtil.fn_qMeaStr(row, "Measure.[SET Frozen SOP Target_SCMType]"));
                    measures.push(vdUtil.fn_qMeaStr(row, "Measure.[SET Frozen SOP Target_Mktname]"));
                    measures.push(vdUtil.fn_qMeaStr(row, "Measure.[SET Frozen SOP Target_Item]"));
                    measures.push(vdUtil.fn_qMeaInt(row, "Measure.[SET Frozen SOP Target_Itemfence]"));
                    measures.push(vdUtil.fn_qMeaStr(row, "Measure.[SET Frozen SOP Target_Groupfence]"));
                    measures.push(vdUtil.fn_qMeaStr(row, "Measure.[SET Frozen SOP Target_Hero]"));
                    measures.push(vdUtil.fn_qMeaStr(row, "Measure.[SET Frozen SOP Target_Valid]"));
                    measures.push(vdUtil.fn_qMeaInt(row, "Measure.[SET Frozen SOP Target_Applyorder]"));
                    measures.push(vdUtil.fn_qMeaStr(row, "Measure.[SET Frozen SOP Target_Description]"));
                    measures.push(vdUtil.fn_qMeaUpdateUserName("Measure.[SET Frozen SOP Target_Init by]"));
                    measures.push(vdUtil.fn_qMeaUpdateTime("Measure.[SET Frozen SOP Target_Init Time]"));
                    // 2026.3.31 추가
                    measures.push(vdUtil.fn_qMeaStr(row, "Measure.[SET Frozen SOP Target_Extended Fence]"));

                    vdCommon.createMeasure(dimensions, measures);
                } else if ( rowstatus == "U" ) {
                    var dimensions = [];
                    dimensions.push(vdUtil.fn_qDimVersionName(parsedParams));
                    dimensions.push(vdUtil.fn_qDim(row, "[Location].[Location]"));
                    dimensions.push(vdUtil.fn_qDim(row, "[Item].[Product Group]"));
                    dimensions.push(vdUtil.fn_qDim(row, "[Group].[Group ID]"));

                    var measures = [];
                    measures.push(vdUtil.fn_qMeaStr(row, "Measure.[SET Frozen SOP Target_Product]"));
                    measures.push(vdUtil.fn_qMeaStr(row, "Measure.[SET Frozen SOP Target_Forminch]"));
                    measures.push(vdUtil.fn_qMeaStr(row, "Measure.[SET Frozen SOP Target_Toinch]"));
                    measures.push(vdUtil.fn_qMeaStr(row, "Measure.[SET Frozen SOP Target_Definition]"));
                    measures.push(vdUtil.fn_qMeaStr(row, "Measure.[SET Frozen SOP Target_Year]"));
                    measures.push(vdUtil.fn_qMeaStr(row, "Measure.[SET Frozen SOP Target_SCMType]"));
                    measures.push(vdUtil.fn_qMeaStr(row, "Measure.[SET Frozen SOP Target_Mktname]"));
                    measures.push(vdUtil.fn_qMeaStr(row, "Measure.[SET Frozen SOP Target_Item]"));
                    measures.push(vdUtil.fn_qMeaInt(row, "Measure.[SET Frozen SOP Target_Itemfence]"));
                    measures.push(vdUtil.fn_qMeaStr(row, "Measure.[SET Frozen SOP Target_Groupfence]"));
                    measures.push(vdUtil.fn_qMeaStr(row, "Measure.[SET Frozen SOP Target_Hero]"));
                    measures.push(vdUtil.fn_qMeaStr(row, "Measure.[SET Frozen SOP Target_Valid]"));
                    measures.push(vdUtil.fn_qMeaInt(row, "Measure.[SET Frozen SOP Target_Applyorder]"));
                    measures.push(vdUtil.fn_qMeaStr(row, "Measure.[SET Frozen SOP Target_Description]"));
                    measures.push(vdUtil.fn_qMeaUpdateUserName("Measure.[SET Frozen SOP Target_Update by]"));
                    measures.push(vdUtil.fn_qMeaUpdateTime("Measure.[SET Frozen SOP Target_Update Time]"));
                    // 2026.3.31 추가
                    measures.push(vdUtil.fn_qMeaStr(row, "Measure.[SET Frozen SOP Target_Extended Fence]"));

                    vdCommon.updateBlockMeasure(dimensions, measures);
                } else if ( rowstatus == "D" ) {
                    var where = [];
                    where.push(vdUtil.fn_qDimVersionName(parsedParams));
                    where.push(vdUtil.fn_qDim(row, "[Location].[Location]"));
                    where.push(vdUtil.fn_qDim(row, "[Item].[Product Group]"));
                    where.push(vdUtil.fn_qDim(row, "[Group].[Group ID]", groupId));

                    vdCommon.deleteMeasure(where, "SET Frozen SOP Target");
                }
            }

            vdCommon.programEnd();

            return { "Code" : 0, "Msg" : "It was saved successfully." };
        } catch ( e ) {
            vdCommon.error(e.message);
            return { "Code" : -1, "Msg" : e.message };
        }
    };

    /*
- 파라미터
{ "fbFuncName" : "fn_merge"
    ,"fbParams" : { "commitType" : "1"
                    ,"filters" : { "[Version].[Version Name]" : {"SelectedMembers" : ["202605_P_WI_01"], "MemberFilter" : ""} }
                   }
    ,"fbGridRows" : [
        { "rowstatus":"D","rowindex":"1","[Group].[Group ID]":"MFF_S_00001","[Location].[Location]":"P306","[Item].[Product Group]":"TV" }
                  ] }
    */
    var fn_merge = function(parsedParams){
        const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
        vdCommon.setLogLevel("Debug");

		try {
            var fbVersionName = "[Version].[Version Name].[CWV_MP]";
		    var fbVersion = vdUtil.fn_getDimensionValue(vdUtil.fn_getFilterVersion(parsedParams));

            var name = vdCommon.selectResult('CurrentUser().Name');
            var userName = vdCommon.selectResult('CurrentUser().[User Name]');

		    if ( ( parsedParams.fbParams.commitType + "" ) == "0" ) {
                // 전체이면 내가 수정한 것만 가져와서 배열을 생성
		        var name = vdCommon.selectResult('CurrentUser().Name');
                var userName = vdCommon.selectResult('CurrentUser().[User Name]');

                var where = 'where { Measure.[SET Frozen SOP Target_Update by] == "' + name + '" || Measure.[SET Frozen SOP Target_Update by] == "' + userName + '"}';
                var result = vdCommon.selectList(["[Version].[Version Name].[" + fbVersion + "]"
                                                        ,"[Location].[Location]"
                                                        ,"[Item].[Product Group]"
                                                        ,"[Group].[Group ID]"]
                                                 ,["Measure.[SET Frozen SOP Target_Product]"]
                                                 ,where, "", "");
                for ( var i = 0; i < result.cs.rowCount; i++ ) {
                    parsedParams.fbGridRows.push({ "[Location].[Location]" : vdUtil.fn_getDimValue(result, i, "Location", "Location")
                                                        ,"[Item].[Product Group]" : vdUtil.fn_getDimValue(result, i, "Item", "Product Group")
                                                        ,"[Group].[Group ID]" : vdUtil.fn_getDimValue(result, i, "Group", "Group ID")});
                }
            }

            for ( var i = 0; i < parsedParams.fbGridRows.length; i++ ) {
                var row = parsedParams.fbGridRows[i];

                var dimensions = [];
                dimensions.push(fbVersionName);
                dimensions.push(vdUtil.fn_qDim(row, "[Location].[Location]"));
                dimensions.push(vdUtil.fn_qDim(row, "[Item].[Product Group]"));
                dimensions.push(vdUtil.fn_qDim(row, "[Group].[Group ID]"));
                var measures = [];
                measures.push(vdUtil.fn_qMeaForMerge("Measure.[SET Frozen SOP Target_Product]", fbVersion));
                measures.push(vdUtil.fn_qMeaForMerge("Measure.[SET Frozen SOP Target_Forminch]", fbVersion));
                measures.push(vdUtil.fn_qMeaForMerge("Measure.[SET Frozen SOP Target_Toinch]", fbVersion));
                measures.push(vdUtil.fn_qMeaForMerge("Measure.[SET Frozen SOP Target_Definition]", fbVersion));
                measures.push(vdUtil.fn_qMeaForMerge("Measure.[SET Frozen SOP Target_Year]", fbVersion));
                measures.push(vdUtil.fn_qMeaForMerge("Measure.[SET Frozen SOP Target_SCMType]", fbVersion));
                measures.push(vdUtil.fn_qMeaForMerge("Measure.[SET Frozen SOP Target_Mktname]", fbVersion));
                measures.push(vdUtil.fn_qMeaForMerge("Measure.[SET Frozen SOP Target_Item]", fbVersion));
                measures.push(vdUtil.fn_qMeaForMerge("Measure.[SET Frozen SOP Target_Itemfence]", fbVersion));
                measures.push(vdUtil.fn_qMeaForMerge("Measure.[SET Frozen SOP Target_Groupfence]", fbVersion));
                measures.push(vdUtil.fn_qMeaForMerge("Measure.[SET Frozen SOP Target_Hero]", fbVersion));
                measures.push(vdUtil.fn_qMeaForMerge("Measure.[SET Frozen SOP Target_Valid]", fbVersion));
                measures.push(vdUtil.fn_qMeaForMerge("Measure.[SET Frozen SOP Target_Applyorder]", fbVersion));
                measures.push(vdUtil.fn_qMeaForMerge("Measure.[SET Frozen SOP Target_Description]", fbVersion));
                measures.push(vdUtil.fn_qMeaUpdateTime("Measure.[SET Frozen SOP Target_Update Time]"));
                measures.push(vdCommon.fn_mergeUser("Measure.[SET Frozen SOP Target_Update by]", fbVersion));
                // 2026.3.31 추가
                measures.push(vdUtil.fn_qMeaForMerge("Measure.[SET Frozen SOP Target_Extended Fence]", fbVersion));
                vdCommon.createMeasure(dimensions, measures);
            }

            vdCommon.programEnd();

            return { "Code" : 0, "Msg" : "It was saved successfully." };
        } catch ( e ) {
            vdCommon.error(e.message);
            return { "Code" : -1, "Msg" : e.message };
        }
    };

/************************************************* util logic *************************************************/

/************************************************* Mapping logic **********************************************/
    // Mapping 함수 정의, 마지막에 선언을 해야 함수를 정상적으로 인식함
    const functionMap = {
        "fn_save" : fn_save
        ,"fn_merge" : fn_merge
    };

    return {
        fn_loadFunction : fn_loadFunction
    };
});

/**************************** o9.NSCM.JSEWSETSOPTarget ****************************
26.02.23 : Digit 삭제, Hero 추가
26.03.04 : fn_merge 추가
26.03.31 : "SET Frozen SOP Target_Extended Fence" 추가
**************************** o9.NSCM.JSEWSETSOPTarget ****************************/