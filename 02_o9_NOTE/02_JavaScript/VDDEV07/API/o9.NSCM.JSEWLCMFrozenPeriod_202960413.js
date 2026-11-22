define('o9.NSCM.JSEWLCMFrozenPeriod', ['o9/data/query', 'o9/data/cellset', 'o9.NSCM.commonLib'], function () {

/**************************************************************************************
    프로그램명  : o9.NSCM.JSEWLCMFrozenPeriod
    화면명     : LCM Frozen Period
    화면 개발자 : 권슬기 프로
    API 개발자 : sungmin0.lim
    최초생성   : 2025.08.22
**************************************************************************************/

	const programName = "o9.NSCM.JSEWLCMFrozenPeriod";
    const commonLib = require('o9.NSCM.commonLib');
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
{ "rowstatus":"C","rowindex":"0","[Location].[Location]":"P306","[Item].[Product Group]":"TV","[Sub Location].[Sub Location]":"L401","Measure.[LCM Frozen Period_PreFPSOP]":"FP","Measure.[LCM Frozen Period_PreRelease]":"1","Measure.[LCM Frozen Period_PreBOMVersion]":"3","Measure.[LCM Frozen Period_PreMinutril]":"4","Measure.[LCM Frozen Period_MainRelease]":"1","Measure.[LCM Frozen Period_MainBOMVersion]":"1","Measure.[LCM Frozen Period_FP]":"1","Measure.[LCM Frozen Period_Confirm]":"CON","Measure.[LCM Frozen Period_SetFrzDataYN]" : "Y", "Measure.[LCM Frozen Period W_Period Type]" : ["202508^FP","202509^BOMVERSION","202510^BOMVERSION","202511^Pre 자원점검"] },
{ "rowstatus":"C","rowindex":"1","[Location].[Location]":"P401","[Item].[Product Group]":"MONITOR","[Sub Location].[Sub Location]":"L401","Measure.[LCM Frozen Period_PreFPSOP]":"FP","Measure.[LCM Frozen Period_PreRelease]":"1","Measure.[LCM Frozen Period_PreBOMVersion]":"3","Measure.[LCM Frozen Period_PreMinutril]":"4","Measure.[LCM Frozen Period_MainRelease]":"1","Measure.[LCM Frozen Period_MainBOMVersion]":"1","Measure.[LCM Frozen Period_FP]":"1","Measure.[LCM Frozen Period_Confirm]":"CON","Measure.[LCM Frozen Period_SetFrzDataYN]" : "N", "Measure.[LCM Frozen Period W_Period Type]" : ["202508^FP","202509^BOMVERSION","202510^BOMVERSION","202511^Pre 자원점검"] }
                  ] }

- 수정 테스트
{ "fbFuncName" : "fn_save", "fbParams" : { "[Version].[Version Name]" : "CWV_MP" },
  "fbGridRows" : [
{ "rowstatus":"U","rowindex":"1","[Location].[Location]":"P306","[Item].[Product Group]":"TV","[Sub Location].[Sub Location]":"L401","Measure.[LCM Frozen Period_PreFPSOP]":"FP","Measure.[LCM Frozen Period_PreRelease]":"1","Measure.[LCM Frozen Period_PreBOMVersion]":"3","Measure.[LCM Frozen Period_PreMinutril]":"4","Measure.[LCM Frozen Period_MainRelease]":"2","Measure.[LCM Frozen Period_MainBOMVersion]":"2","Measure.[LCM Frozen Period_FP]":"1","Measure.[LCM Frozen Period_Confirm]":"CON","Measure.[LCM Frozen Period W_Period Type]" : ["202508^FP","202509^BOMVERSION","202510^BOMVERSION","202511^Pre 자원점검"] }
                  ] }

- 삭제 테스트
{ "fbFuncName" : "fn_save", "fbParams" : { "[Version].[Version Name]" : "CWV_MP" },
  "fbGridRows" : [
{ "rowstatus":"D","rowindex":"1","[Location].[Location]":"P306","[Item].[Product Group]":"TV","[Sub Location].[Sub Location]":"L401","Measure.[LCM Frozen Period_PreFPSOP]":"FP","Measure.[LCM Frozen Period_PreRelease]":"1","Measure.[LCM Frozen Period_PreBOMVersion]":"3","Measure.[LCM Frozen Period_PreMinutril]":"4","Measure.[LCM Frozen Period_MainRelease]":"1","Measure.[LCM Frozen Period_MainBOMVersion]":"1","Measure.[LCM Frozen Period_Confirm]":"CON","Measure.[LCM Frozen Period W_Period Type]" : ["202508^FP","202509^BOMVERSION","202510^BOMVERSION","202511^Pre 자원점검"] },
{ "rowstatus":"D","rowindex":"1","[Location].[Location]":"P401","[Item].[Product Group]":"MONITOR","[Sub Location].[Sub Location]":"L401","Measure.[LCM Frozen Period_PreFPSOP]":"FP","Measure.[LCM Frozen Period_PreRelease]":"1","Measure.[LCM Frozen Period_PreBOMVersion]":"3","Measure.[LCM Frozen Period_PreMinutril]":"4","Measure.[LCM Frozen Period_MainRelease]":"1","Measure.[LCM Frozen Period_MainBOMVersion]":"1","Measure.[LCM Frozen Period_Confirm]":"CON","Measure.[LCM Frozen Period W_Period Type]" : ["202508^FP","202509^BOMVERSION","202510^BOMVERSION","202511^Pre 자원점검"] }
                  ] }
    */

    var fn_save = function(parsedParams){
        const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
        vdCommon.setLogLevel("Debug");

		try {
		    vdCommon.printParams(parsedParams);

		    // 26.1.21 엑셀 업로드 기능이 추가되어 Member 데이타 체크하는 로직 추가
		    // 멤버를 배열로 구성
		    var location = [];
		    var productGroup = [];
		    var subLocation = [];
            var keyHm = {};
            var value = "";
		    for ( var i = 0; i < parsedParams.fbGridRows.length; i++ ) {
                var row = parsedParams.fbGridRows[i];
                var rowstatus = row["rowstatus"];
                var key = "";

                if ( rowstatus == "C" ) {
                    value = row["[Location].[Location]"];
                    key += value;
                    if ( !location.includes(value) )    location.push(value);

                    value = row["[Item].[Product Group]"];
                    key += "_" + value;
                    if ( !productGroup.includes(value) )    productGroup.push(value);

                    value = row["[Sub Location].[Sub Location]"];
                    key += "_" + value;
                    if ( !subLocation.includes(value) )    subLocation.push(value);

                    if ( keyHm[key] == undefined )    keyHm[key] = i;
                }
            }

            // 멤버 데이타 가져와서 hm 구성
            var validHm = {};
            if ( location.length > 0 ) {
                var result = vdCommon.selectList(["[Location].[Location]" + vdUtil.fn_filterStr(location)], [], "", "", "");
                for ( var i = 0; i < result.cs.rowCount; i++ ) {
                    var name = vdUtil.fn_getDimValue(result, i, "Location", "Location");
                    validHm["location" + "_" + name] = name;
                }
                result = vdCommon.selectList(["[Item].[Product Group]" + vdUtil.fn_filterStr(productGroup)], [], "", "", "");
                for ( var i = 0; i < result.cs.rowCount; i++ ) {
                    var name = vdUtil.fn_getDimValue(result, i, "Item", "Product Group");
                    validHm["productGroup" + "_" + name] = name;
                }
                result = vdCommon.selectList(["[Sub Location].[Sub Location]" + vdUtil.fn_filterStr(subLocation)], [], "", "", "");
                for ( var i = 0; i < result.cs.rowCount; i++ ) {
                    var name = vdUtil.fn_getDimValue(result, i, "Sub Location", "Sub Location");
                    validHm["subLocation" + "_" + name] = name;
                }

                //vdCommon.debug("key : " + JSON.stringify(keyHm));
                //vdCommon.debug("validHm : " + JSON.stringify(validHm));
            }

		    // Validation 체크 : 등록 체크
            var validation = [];
            for ( var i = 0; i < parsedParams.fbGridRows.length; i++ ) {
                var row = parsedParams.fbGridRows[i];
                var rowstatus = row["rowstatus"];
                var rowindex = row["rowindex"];
                var msg = "";
                var key = "";

                var count = 0;
                if ( rowstatus == "C" ) {
                    // Member 체크
                    value = row["[Location].[Location]"];
                    key = value;
                    if ( validHm["location" + "_" + value] == undefined ) {
                        msg = vdUtil.fn_wordAppend(msg, "Check Location(" + value + "). ");
                    }
                    value = row["[Item].[Product Group]"];
                    key += "_" + value;
                    if ( validHm["productGroup" + "_" + value] == undefined ) {
                        msg = vdUtil.fn_wordAppend(msg, "Check Product Group(" + value + "). ");
                    }
                    value = row["[Sub Location].[Sub Location]"];
                    key += "_" + value;
                    if ( validHm["subLocation" + "_" + value] == undefined ) {
                        msg = vdUtil.fn_wordAppend(msg, "Check Sub Location(" + value + "). ");
                    }

                    // 중복 체크
                    if ( keyHm[key] != i ) {
                        msg = vdUtil.fn_wordAppend(msg, "Check Duplicate(" + keyHm[key] + " line). ");
                    }

                    // 이미 등록되어 있는지 체크
                    var dimensions = [];
                    dimensions.push(vdUtil.fn_qDimVersionName(parsedParams));
                    dimensions.push(vdUtil.fn_qDim(row, "[Location].[Location]"));
                    dimensions.push(vdUtil.fn_qDim(row, "[Item].[Product Group]"));
                    dimensions.push(vdUtil.fn_qDim(row, "[Sub Location].[Sub Location]"));
                    var count = vdCommon.selectListCount(dimensions, ["Measure.[LCM Frozen Period_FP]"], "");
                    if ( count > 0 ) {
                        msg = vdUtil.fn_wordAppend(msg, "This is registered data. ");
                    }

                    if ( msg != "" ) {
                        validation.push(rowindex + "^" + msg);
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

                if ( rowstatus == "C" ) {
                    var dimensions = [];
                    dimensions.push(vdUtil.fn_qDimVersionName(parsedParams));
                    dimensions.push(vdUtil.fn_qDim(row, "[Location].[Location]"));
                    dimensions.push(vdUtil.fn_qDim(row, "[Item].[Product Group]"));
                    dimensions.push(vdUtil.fn_qDim(row, "[Sub Location].[Sub Location]"));

                    var measures = [];
                    measures.push(vdUtil.fn_qMeaStr(row, "Measure.[LCM Frozen Period_Confirm]"));
                    measures.push(vdUtil.fn_qMeaInt(row, "Measure.[LCM Frozen Period_MainRelease]"));
                    measures.push(vdUtil.fn_qMeaInt(row, "Measure.[LCM Frozen Period_PreRelease]"));
                    measures.push(vdUtil.fn_qMeaUpdateUserName("Measure.[LCM Frozen Period_Init By]"));
                    measures.push(vdUtil.fn_qMeaUpdateTime("Measure.[LCM Frozen Period_Init Time]"));
                    // 26.1.21 추가
                    measures.push(vdUtil.fn_qMeaInt(row, "Measure.[LCM Frozen Period_FP]"));
                    // 26.1.21 삭제요청
                    //measures.push(vdUtil.fn_qMeaStr(row, "Measure.[LCM Frozen Period_MainBOMVersion]"));
                    //measures.push(vdUtil.fn_qMeaStr(row, "Measure.[LCM Frozen Period_PreBOMVersion]"));
                    //measures.push(vdUtil.fn_qMeaStr(row, "Measure.[LCM Frozen Period_PreFPSOP]"));
                    //measures.push(vdUtil.fn_qMeaStr(row, "Measure.[LCM Frozen Period_PreMinutril]"));
                    // 26.1.28 추가
                    measures.push(vdUtil.fn_qMeaInt(row, "Measure.[LCM Frozen Period_SetFrzDataYN]"));

                    vdCommon.createMeasure(dimensions, measures);

                    // Week 데이타 생성
                    vdCommon.createMeasure([vdUtil.fn_qDimVersionName(parsedParams),
                                                vdUtil.fn_qDim(row, "[Location].[Location]"),
                                                vdUtil.fn_qDim(row, "[Item].[Product Group]"),
                                                vdUtil.fn_qDim(row, "[Sub Location].[Sub Location]"),
                                                "&Next12Weeks"],
                                            ['Measure.[LCM Frozen Period W_Period Type] = "-";']);

                    var weekList = row["Measure.[LCM Frozen Period W_Period Type]"];
                    var queryStr = "";
                    for ( var m = 0; m < weekList.length; m++ ) {
                        var subDimensions = [];
                        subDimensions.push(vdUtil.fn_qDimVersionName(parsedParams));
                        subDimensions.push(vdUtil.fn_qDim(row, "[Location].[Location]"));
                        subDimensions.push(vdUtil.fn_qDim(row, "[Item].[Product Group]"));
                        subDimensions.push(vdUtil.fn_qDim(row, "[Sub Location].[Sub Location]"));
                        subDimensions.push("[Time].[Week].[" + weekList[m].split("^")[0] + "]");

                        var subMeasures = [];
                        subMeasures.push(vdUtil.fn_qMeaStr(row, "Measure.[LCM Frozen Period W_Period Type]", weekList[m].split("^")[1]));

                        queryStr += vdCommon.updateMeasureQuery(subDimensions, subMeasures);
                    }
                    if ( queryStr != "" ) {
                        vdCommon.executeQuery("LCM Frozen Period W", queryStr);
                    }
                } else if ( rowstatus == "U" ) {
                    var dimensions = [];
                    dimensions.push(vdUtil.fn_qDimVersionName(parsedParams));
                    dimensions.push(vdUtil.fn_qDim(row, "[Location].[Location]"));
                    dimensions.push(vdUtil.fn_qDim(row, "[Item].[Product Group]"));
                    dimensions.push(vdUtil.fn_qDim(row, "[Sub Location].[Sub Location]"));

                    var measures = [];
                    measures.push(vdUtil.fn_qMeaStr(row, "Measure.[LCM Frozen Period_Confirm]"));
                    measures.push(vdUtil.fn_qMeaInt(row, "Measure.[LCM Frozen Period_MainRelease]"));
                    measures.push(vdUtil.fn_qMeaInt(row, "Measure.[LCM Frozen Period_PreRelease]"));
                    measures.push(vdUtil.fn_qMeaUpdateUserName("Measure.[LCM Frozen Period_Update By]"));
                    measures.push(vdUtil.fn_qMeaUpdateTime("Measure.[LCM Frozen Period_Update Time]"));
                    // 26.1.21 추가
                    measures.push(vdUtil.fn_qMeaInt(row, "Measure.[LCM Frozen Period_FP]"));
                    // 26.1.21 삭제요청
                    //measures.push(vdUtil.fn_qMeaStr(row, "Measure.[LCM Frozen Period_MainBOMVersion]"));
                    //measures.push(vdUtil.fn_qMeaStr(row, "Measure.[LCM Frozen Period_PreBOMVersion]"));
                    //measures.push(vdUtil.fn_qMeaStr(row, "Measure.[LCM Frozen Period_PreFPSOP]"));
                    //measures.push(vdUtil.fn_qMeaStr(row, "Measure.[LCM Frozen Period_PreMinutril]"));

                    vdCommon.updateBlockMeasure(dimensions, measures);

                    // 주차 수정
                    var weekList = row["Measure.[LCM Frozen Period W_Period Type]"];
                    var queryStr = "";
                    for ( var m = 0; m < weekList.length; m++ ) {
                        var subDimensions = [];
                        subDimensions.push(vdUtil.fn_qDimVersionName(parsedParams));
                        subDimensions.push(vdUtil.fn_qDim(row, "[Location].[Location]"));
                        subDimensions.push(vdUtil.fn_qDim(row, "[Item].[Product Group]"));
                        subDimensions.push(vdUtil.fn_qDim(row, "[Sub Location].[Sub Location]"));
                        subDimensions.push("[Time].[Week].[" + weekList[m].split("^")[0] + "]");

                        var subMeasures = [];
                        subMeasures.push(vdUtil.fn_qMeaStr(row, "Measure.[LCM Frozen Period W_Period Type]", weekList[m].split("^")[1]));

                        queryStr += vdCommon.updateMeasureQuery(subDimensions, subMeasures);
                    }
                    if ( queryStr != "" ) {
                        vdCommon.executeQuery("LCM Frozen Period W", queryStr);
                    }
                } else if ( rowstatus == "D" ) {
                    var where = [];
                    where.push(vdUtil.fn_qDimVersionName(parsedParams));
                    where.push(vdUtil.fn_qDim(row, "[Location].[Location]"));
                    where.push(vdUtil.fn_qDim(row, "[Item].[Product Group]"));
                    where.push(vdUtil.fn_qDim(row, "[Sub Location].[Sub Location]"));

                    vdCommon.deleteMeasure(where, "LCM Frozen Period");
                    vdCommon.deleteMeasure(where, "LCM Frozen Period W");
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
        { "fbFuncName" : "fn_setFrozenPeriod", "fbParams" : { "[Version].[Version Name]" : "CWV_MP", "[Location].[Location]" : "P401" } }
    */
    var fn_setFrozenPeriod = function(parsedParams){
        const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
        vdCommon.setLogLevel("Debug");

        try {
            vdCommon.printParams(parsedParams);

            var rtn = { "LCM Frozen Period_SetFrzDataYN" : "N" };

            // Location 을 찾는다.
            result = vdCommon.selectList([vdUtil.fn_getParamQuery(parsedParams, "[Version].[Version Name]")
                                            ,vdUtil.fn_getParamQuery(parsedParams, "[Location].[Location]")
                                            ,"[Item].[Product Group]"
                                            ,'[SCM Type].[SCM Type].filter(#.Name in {"All","SET"})']
                                         ,["Measure.[SET Frozen Period_FP]"
                                            ,"Measure.[SET Frozen Period_MainRelease]"
                                            ,"Measure.[SET Frozen Period_PreRelease]"]
                                         ,""
                                         ,"orderby [Item].[Product Group].Name desc, [SCM Type].[SCM Type].Name"
                                         ,"limit 1");
            for ( var i = 0; i < result.cs.rowCount; i++ ) {
                rtn["SET Frozen Period_FP"] = vdUtil.fn_getMeaValue(result, i, "SET Frozen Period_FP");
                rtn["SET Frozen Period_MainRelease"] = vdUtil.fn_getMeaValue(result, i, "SET Frozen Period_MainRelease");
                rtn["SET Frozen Period_PreRelease"] = vdUtil.fn_getMeaValue(result, i, "SET Frozen Period_PreRelease");

                rtn["LCM Frozen Period_SetFrzDataYN"] = "Y";
            }

            vdCommon.programEnd();

            return rtn;
        } catch ( e ) {
            vdCommon.error(e.message);
            RuleOutputToUI = { Status : 'Error', Message : "Js Logic Error : " + e.message };
            return;
        }
    };
/************************************************* util logic *************************************************/

/************************************************* Mapping logic **********************************************/
    // Mapping 함수 정의, 마지막에 선언을 해야 함수를 정상적으로 인식함
    const functionMap = {
        "fn_save" : fn_save
        ,"fn_setFrozenPeriod" : fn_setFrozenPeriod
    };

    return {
        fn_loadFunction : fn_loadFunction
    };
});

/**************************** o9.NSCM.JSEWLCMFrozenPeriod ****************************
26.01.21 엑셀 업로드 기능이 추가되어 Member 데이타 체크하는 로직 추가
26.01.21 fn_setFrozenPeriod 함수 추가
26.01.28 Measure.[LCM Frozen Period_SetFrzDataYN] 값 세팅하는 로직 추가
**************************** o9.NSCM.JSEWLCMFrozenPeriod ****************************/