define('o9.NSCM.JSEWSETFrozenPeriod', ['o9/data/query', 'o9/data/cellset', 'o9.NSCM.commonLibVD'], function () {

/**************************************************************************************
    프로그램명  : o9.NSCM.JSEWSETFrozenPeriod
    화면명     : SET Frozen Period
    화면 개발자 : 권슬기 프로
    API 개발자 : sungmin0.lim
    최초생성   : 2025.08.5
**************************************************************************************/

	const programName = "o9.NSCM.JSEWSETFrozenPeriod";
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
{ "fbFuncName" : "fn_save", "fbParams" : { "[Version].[Version Name]" : "CWV_MP" },
  "fbGridRows" : [
        { "rowstatus":"C","rowindex":"0"
            ,"[Location].[Location]":"P306"
            ,"[Item].[Product Group]":"TV"
            ,"[Plan Group].[Plan Group]":"1"
            ,"[SCM Type].[SCM Type]":"SET"
            ,"Measure.[SET Frozen Period_FP]":"1"
            ,"Measure.[SET Frozen Period_PreRelease]":"2"
            ,"Measure.[SET Frozen Period_PreMinutril]":"3"
            ,"Measure.[SET Frozen Period_MainRelease]":"4"
            ,"Measure.[SET Frozen Period_LotSizing Period]":"1"
            ,"Measure.[SET Frozen Period_LotSizing Remain]":"Down"
            ,"Measure.[SET Frozen Period_Confirm]":"CON"
            ,"Measure.[SET Frozen Period W_Period Type]" : ["202601^1","202602^2","202603^3","202604^4"]
            ,"Measure.[SET Frozen Period_Extended Fence]":"4"
            ,"Measure.[SET Frozen Period_Frozen Period]":"4"
            ,"Measure.[SET Frozen Period_LotSizing Period2]":"4"
            ,"Measure.[SET Frozen Period_LotSizing Remain2]":"Down"
        }
    ]
}
  */

    var fn_save = function(parsedParams){
        const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
        vdCommon.setLogLevel("Debug");

		try {
		    var fbVersion = parsedParams.fbParams["[Version].[Version Name]"];


		    // 26.1.29 엑셀 업로드 기능이 추가되어 Member 데이타 체크하는 로직 추가
		    // 멤버를 배열로 구성
		    var location = [];
		    var productGroup = [];
		    var planGroup = [];
		    var scmType = [];
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

                    value = row["[SCM Type].[SCM Type]"];
                    key += "_" + value;
                    if ( !scmType.includes(value) )    scmType.push(value);

                    value = row["[Plan Group].[Plan Group]"];
                    key += "_" + value;
                    if ( !planGroup.includes(value) )    planGroup.push(value);

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
                result = vdCommon.selectList(["[SCM Type].[SCM Type]" + vdUtil.fn_filterStr(scmType)], [], "", "", "");
                for ( var i = 0; i < result.cs.rowCount; i++ ) {
                    var name = vdUtil.fn_getDimValue(result, i, "SCM Type", "SCM Type");
                    validHm["scmType" + "_" + name] = name;
                }
                result = vdCommon.selectList(["[Plan Group].[Plan Group]" + vdUtil.fn_filterStr(planGroup)], [], "", "", "");
                for ( var i = 0; i < result.cs.rowCount; i++ ) {
                    var name = vdUtil.fn_getDimValue(result, i, "Plan Group", "Plan Group");
                    validHm["planGroup" + "_" + name] = name;
                }

                vdCommon.debug("key : " + JSON.stringify(keyHm));
                vdCommon.debug("validHm : " + JSON.stringify(validHm));
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
                    value = row["[SCM Type].[SCM Type]"];
                    key += "_" + value;
                    if ( validHm["scmType" + "_" + value] == undefined ) {
                        msg = vdUtil.fn_wordAppend(msg, "Check SCM Type(" + value + "). ");
                    }
                    value = row["[Plan Group].[Plan Group]"];
                    key += "_" + value;
                    if ( validHm["planGroup" + "_" + value] == undefined ) {
                        msg = vdUtil.fn_wordAppend(msg, "Check Plan Group(" + value + "). ");
                    }

                    // 중복 체크
                    if ( keyHm[key] != i ) {
                        msg = vdUtil.fn_wordAppend(msg, "Check Duplicate(" + keyHm[key] + " line). ");
                    }

                    var dimensions = [];
                    dimensions.push("[Version].[Version Name].[" + fbVersion + "]");
                    dimensions.push("[Location].[Location].[" + row["[Location].[Location]"] + "]");
                    dimensions.push("[Item].[Product Group].[" + row["[Item].[Product Group]"] + "]");
                    dimensions.push("[SCM Type].[SCM Type].[" + row["[SCM Type].[SCM Type]"] + "]");
                    dimensions.push("[Plan Group].[Plan Group].[" + row["[Plan Group].[Plan Group]"] + "]");

                    // 등록 여부 체크
                    var count = vdCommon.selectListCount(dimensions, ["Measure.[SET Frozen Period_FP]"], "");
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
                    dimensions.push("[Version].[Version Name].[" + fbVersion + "]");
                    dimensions.push("[Location].[Location].[" + row["[Location].[Location]"] + "]");
                    dimensions.push("[Item].[Product Group].[" + row["[Item].[Product Group]"] + "]");
                    dimensions.push("[SCM Type].[SCM Type].[" + row["[SCM Type].[SCM Type]"] + "]");
                    dimensions.push("[Plan Group].[Plan Group].[" + row["[Plan Group].[Plan Group]"] + "]");

                    var measures = [];
                    measures.push('Measure.[SET Frozen Period_FP] = "' + row["Measure.[SET Frozen Period_FP]"] + '";');
                    measures.push('Measure.[SET Frozen Period_PreRelease] = "' + row["Measure.[SET Frozen Period_PreRelease]"] + '";');
                    measures.push('Measure.[SET Frozen Period_PreMinutril] = "' + row["Measure.[SET Frozen Period_PreMinutril]"] + '";');
                    measures.push('Measure.[SET Frozen Period_MainRelease] = "' + row["Measure.[SET Frozen Period_MainRelease]"] + '";');
                    measures.push('Measure.[SET Frozen Period_LotSizing Period] = "' + row["Measure.[SET Frozen Period_LotSizing Period]"] + '";');
                    measures.push('Measure.[SET Frozen Period_LotSizing Remain] = "' + row["Measure.[SET Frozen Period_LotSizing Remain]"] + '";');
                    measures.push('Measure.[SET Frozen Period_Confirm] = "' + row["Measure.[SET Frozen Period_Confirm]"] + '";');
                    measures.push(vdUtil.fn_qMeaUpdateUserName("Measure.[SET Frozen Period_Init By]"));
                    measures.push(vdUtil.fn_qMeaUpdateTime("Measure.[SET Frozen Period_Init Time]"));
                    // 2026.3.27 Measure 추가
                    measures.push(vdUtil.fn_qMeaInt(row, "Measure.[SET Frozen Period_Extended Fence]"));
                    measures.push(vdUtil.fn_qMeaInt(row, "Measure.[SET Frozen Period_Frozen Period]"));
                    measures.push(vdUtil.fn_qMeaInt(row, "Measure.[SET Frozen Period_LotSizing Period2]"));
                    measures.push(vdUtil.fn_qMeaStr(row, "Measure.[SET Frozen Period_LotSizing Remain2]"));

                    vdCommon.createMeasure(dimensions, measures);

                    // Week 데이타 생성
                    vdCommon.createMeasure(["[Version].[Version Name].[" + fbVersion + "]",
                                                "[Location].[Location].[" + row["[Location].[Location]"] + "]",
                                                "[Item].[Product Group].[" + row["[Item].[Product Group]"] + "]",
                                                "[SCM Type].[SCM Type].[" + row["[SCM Type].[SCM Type]"] + "]",
                                                "[Plan Group].[Plan Group].[" + row["[Plan Group].[Plan Group]"] + "]",
                                                "&Next12Weeks"],
                                            ['Measure.[SET Frozen Period W_Period Type] = "-";']);

                    var weekList = row["Measure.[SET Frozen Period W_Period Type]"];
                    var queryStr = "";
                    for ( var m = 0; m < weekList.length; m++ ) {
                        var subDimensions = [];
                        subDimensions.push("[Version].[Version Name].[" + fbVersion + "]");
                        subDimensions.push("[Location].[Location].[" + row["[Location].[Location]"] + "]");
                        subDimensions.push("[Item].[Product Group].[" + row["[Item].[Product Group]"] + "]");
                        subDimensions.push("[SCM Type].[SCM Type].[" + row["[SCM Type].[SCM Type]"] + "]");
                        subDimensions.push("[Plan Group].[Plan Group].[" + row["[Plan Group].[Plan Group]"] + "]");
                        subDimensions.push("[Time].[Week].[" + weekList[m].split("^")[0] + "]");

                        var subMeasures = [];
                        subMeasures.push('Measure.[SET Frozen Period W_Period Type] = "' + weekList[m].split("^")[1] + '";');

                        queryStr += vdCommon.updateMeasureQuery(subDimensions, subMeasures);
                    }
                    if ( queryStr != "" ) {
                        vdCommon.executeQuery("SET Frozen Period W", queryStr);
                    }
                } else if ( rowstatus == "U" ) {
                    var dimensions = [];
                    dimensions.push("[Version].[Version Name].[" + fbVersion + "]");
                    dimensions.push("[Location].[Location].[" + row["[Location].[Location]"] + "]");
                    dimensions.push("[Item].[Product Group].[" + row["[Item].[Product Group]"] + "]");
                    dimensions.push("[SCM Type].[SCM Type].[" + row["[SCM Type].[SCM Type]"] + "]");
                    dimensions.push("[Plan Group].[Plan Group].[" + row["[Plan Group].[Plan Group]"] + "]");

                    var measures = [];
                    measures.push('Measure.[SET Frozen Period_FP] = "' + row["Measure.[SET Frozen Period_FP]"] + '";');
                    measures.push('Measure.[SET Frozen Period_PreRelease] = "' + row["Measure.[SET Frozen Period_PreRelease]"] + '";');
                    measures.push('Measure.[SET Frozen Period_PreMinutril] = "' + row["Measure.[SET Frozen Period_PreMinutril]"] + '";');
                    measures.push('Measure.[SET Frozen Period_MainRelease] = "' + row["Measure.[SET Frozen Period_MainRelease]"] + '";');
                    measures.push('Measure.[SET Frozen Period_LotSizing Period] = "' + row["Measure.[SET Frozen Period_LotSizing Period]"] + '";');
                    measures.push('Measure.[SET Frozen Period_LotSizing Remain] = "' + row["Measure.[SET Frozen Period_LotSizing Remain]"] + '";');
                    measures.push('Measure.[SET Frozen Period_Confirm] = "' + row["Measure.[SET Frozen Period_Confirm]"] + '";');
                    measures.push(vdUtil.fn_qMeaUpdateUserName("Measure.[SET Frozen Period_Update By]"));
                    measures.push(vdUtil.fn_qMeaUpdateTime("Measure.[SET Frozen Period_Update Time]"));
                    // 2026.3.27 Measure 추가
                    measures.push(vdUtil.fn_qMeaInt(row, "Measure.[SET Frozen Period_Extended Fence]"));
                    measures.push(vdUtil.fn_qMeaInt(row, "Measure.[SET Frozen Period_Frozen Period]"));
                    measures.push(vdUtil.fn_qMeaInt(row, "Measure.[SET Frozen Period_LotSizing Period2]"));
                    measures.push(vdUtil.fn_qMeaStr(row, "Measure.[SET Frozen Period_LotSizing Remain2]"));


                    vdCommon.updateBlockMeasure(dimensions, measures);

                    // 주차 수정
                    var weekList = row["Measure.[SET Frozen Period W_Period Type]"];
                    var queryStr = "";
                    for ( var m = 0; m < weekList.length; m++ ) {
                        var subDimensions = [];
                        subDimensions.push("[Version].[Version Name].[" + fbVersion + "]");
                        subDimensions.push("[Location].[Location].[" + row["[Location].[Location]"] + "]");
                        subDimensions.push("[Item].[Product Group].[" + row["[Item].[Product Group]"] + "]");
                        subDimensions.push("[SCM Type].[SCM Type].[" + row["[SCM Type].[SCM Type]"] + "]");
                        subDimensions.push("[Plan Group].[Plan Group].[" + row["[Plan Group].[Plan Group]"] + "]");
                        subDimensions.push("[Time].[Week].[" + weekList[m].split("^")[0] + "]");

                        var subMeasures = [];
                        subMeasures.push('Measure.[SET Frozen Period W_Period Type] = "' + weekList[m].split("^")[1] + '";');

                        queryStr += vdCommon.updateMeasureQuery(subDimensions, subMeasures);
                    }
                    if ( queryStr != "" ) {
                        vdCommon.executeQuery("SET Frozen Period W", queryStr);
                    }
                } else if ( rowstatus == "D" ) {
                    var where = [];
                    where.push("[Version].[Version Name].[" + fbVersion + "]");
                    where.push("[Location].[Location].[" + row["[Location].[Location]"] + "]");
                    where.push("[Item].[Product Group].[" + row["[Item].[Product Group]"] + "]");
                    where.push("[SCM Type].[SCM Type].[" + row["[SCM Type].[SCM Type]"] + "]");
                    where.push("[Plan Group].[Plan Group].[" + row["[Plan Group].[Plan Group]"] + "]");

                    vdCommon.deleteMeasure(where, "SET Frozen Period");
                    vdCommon.deleteMeasure(where, "SET Frozen Period W");
                }
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
    };

    return {
        fn_loadFunction : fn_loadFunction
    };
});

/*************************************************************************************************************
2026-01-29 엑셀 업로드 가능하도록 수정
2026-03-27 컬럼 추가
************************************** o9.NSCM.JSEWSETFrozenPeriod *******************************************/