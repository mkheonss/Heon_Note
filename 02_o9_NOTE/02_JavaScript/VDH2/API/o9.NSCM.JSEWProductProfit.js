define('o9.NSCM.JSEWProductProfit', ['o9/data/query', 'o9/data/cellset', 'o9.NSCM.commonLibVD'], function () {

/**************************************************************************************
    프로그램명  : o9.NSCM.JSEWProductProfit
    화면명     : Product Profit
    화면 설계자 : 이상엽 프로
    화면 개발자 :
    API 개발자 : sungmin0.lim
    최초생성   : 2026.01.07
**************************************************************************************/

	const programName = "o9.NSCM.JSEWProductProfit";
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
            vdCommon.error(e.message);
            return { "Code" : -1, "Msg" : e.message };
        }
	};

/************************************************* common logic *************************************************/
/*
{ "fbFuncName" : "fn_save", "fbParams" : { "[Version].[Version Name]" : "CWV_MP" },
  "fbGridRows" : [
                    { "rowstatus":"C","rowindex":"0","[Location].[Location]":"SESK","[To Time].[To Year]":"2025","[Item].[Item]":"GQ100QN80FUXZG","[Time].[Planning Month]":"6","[Sales Domain].[AP2]":"C460","[Execution Version].[Execution Version]":"T03","[Business Area].[Business Area]":"780A","[Comb Company].[Comb Company]":"C780","[Prof Loc].[Prof Loc]":"SESK","Measure.[Product Profit Upload_Sales Qty]":"200","Measure.[Product Profit Upload_N Price]":"2657.11","Measure.[Product Profit Upload_C Profit Rate]":"7.6332321908608" },
                    { "rowstatus":"C","rowindex":"1","[Location].[Location]":"SEH","[To Time].[To Year]":"2025","[Item].[Item]":"GQ32LS03CBUXZG","[Time].[Planning Month]":"3","[Sales Domain].[AP2]":"C460","[Execution Version].[Execution Version]":"T03","[Business Area].[Business Area]":"780A","[Comb Company].[Comb Company]":"C780","[Prof Loc].[Prof Loc]":"SESK","Measure.[Product Profit Upload_Sales Qty]":"748","Measure.[Product Profit Upload_N Price]":"276.192513368984","Measure.[Product Profit Upload_C Profit Rate]":"-3.36680425093117" },
                    { "rowstatus":"C","rowindex":"2","[Location].[Location]":"SEH","[To Time].[To Year]":"2025","[Item].[Item]":"GQ32LS03CBUXZG","[Time].[Planning Month]":"4","[Sales Domain].[AP2]":"C460","[Execution Version].[Execution Version]":"T03","[Business Area].[Business Area]":"780A","[Comb Company].[Comb Company]":"C780","[Prof Loc].[Prof Loc]":"SESK","Measure.[Product Profit Upload_Sales Qty]":"200","Measure.[Product Profit Upload_N Price]":"276.19","Measure.[Product Profit Upload_C Profit Rate]":"-5.67037092453889" },
                    { "rowstatus":"C","rowindex":"3","[Location].[Location]":"SEH","[To Time].[To Year]":"2025","[Item].[Item]":"GQ32LS03CBUXZG","[Time].[Planning Month]":"5","[Sales Domain].[AP2]":"C460","[Execution Version].[Execution Version]":"T03","[Business Area].[Business Area]":"780A","[Comb Company].[Comb Company]":"C780","[Prof Loc].[Prof Loc]":"SESK","Measure.[Product Profit Upload_Sales Qty]":"450","Measure.[Product Profit Upload_N Price]":"276.191111111111","Measure.[Product Profit Upload_C Profit Rate]":"-5.10463251575702" }
                  ]
}
*/
    var fn_save = function(parsedParams){
        const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
        vdCommon.setLogLevel("Debug");
        vdCommon.printParams(parsedParams);

		try {
		    // Validation - 멤버 확인을 위한 데이타 생성
            var validation = [];

            var profLoc = [];
            var toYear = [];
            var item = [];
            var executionVersion = [];
            var businessArea = [];
            var planningMonth = [];
            var combCompany = [];
            var keyHm = {};
            var value = "";
            for ( var i = 0; i < parsedParams.fbGridRows.length; i++ ) {
                var row = parsedParams.fbGridRows[i];
                var key = "";
                value = row["[Prof Loc].[Prof Loc]"];
                key += value;
                if ( !profLoc.includes(value) )    profLoc.push(value);
                value = row["[To Time].[To Year]"];
                key += "_" + value;
                if ( !toYear.includes(value) )    toYear.push(value);
                value = row["[Item].[Item]"];
                key += "_" + value;
                if ( !item.includes(value) )    item.push(value);
                value = row["[Comb Company].[Comb Company]"];
                key += "_" + value;
                if ( !combCompany.includes(value) )    combCompany.push(value);
                value = row["[To Time].[To Year]"] + "_" + row["[Execution Version].[Execution Version]"];
                key += "_" + value;
                if ( !executionVersion.includes(value) )    executionVersion.push(value);
                value = row["[Business Area].[Business Area]"];
                key += "_" + value;
                if ( !businessArea.includes(value) )    businessArea.push(value);
                value = row["[To Time].[To Year]"] + vdUtil.fn_lpad(row["[Time].[Planning Month]"], 2, "0");
                key += "_" + value;
                if ( !planningMonth.includes(value) )    planningMonth.push(value);

                if ( keyHm[key] == undefined )    keyHm[key] = i;
            }

            // Validation - 키 데이타 생성
            var validHm = {};
            var result = vdCommon.selectList(["[Prof Loc].[Prof Loc]" + vdUtil.fn_filterStrForDN(profLoc)], [], "", "", "");
            for ( var i = 0; i < result.cs.rowCount; i++ ) {
                var name = vdUtil.fn_getDimValue(result, i, "Prof Loc", "Prof Loc");
                var displayName = vdUtil.fn_getDimDisplayName(result, i, "Prof Loc", "Prof Loc", false);
                validHm["profLoc" + "_" + displayName] = name;
            }
            result = vdCommon.selectList(["[To Time].[To Year]" + vdUtil.fn_filterStr(toYear)], [], "", "", "");
            for ( var i = 0; i < result.cs.rowCount; i++ ) {
                var name = vdUtil.fn_getDimValue(result, i, "To Time", "To Year");
                validHm["toYear" + "_" + name] = name;
            }
            result = vdCommon.selectList(["[Item].[Item]" + vdUtil.fn_filterStr(item)], [], "", "", "");
            for ( var i = 0; i < result.cs.rowCount; i++ ) {
                var name = vdUtil.fn_getDimValue(result, i, "Item", "Item");
                validHm["item" + "_" + name] = name;
            }
            result = vdCommon.selectList(["[Comb Company].[Comb Company]" + vdUtil.fn_filterStrForDN(combCompany)], [], "", "", "");
            for ( var i = 0; i < result.cs.rowCount; i++ ) {
                var name = vdUtil.fn_getDimValue(result, i, "Comb Company", "Comb Company");
                var displayName = vdUtil.fn_getDimDisplayName(result, i, "Comb Company", "Comb Company", false);

                validHm["combCompany" + "_" + displayName] = name;
            }
            result = vdCommon.selectList(["[Execution Version].[Execution Version]" + vdUtil.fn_filterStr(executionVersion)], [], "", "", "");
            for ( var i = 0; i < result.cs.rowCount; i++ ) {
                var name = vdUtil.fn_getDimValue(result, i, "Execution Version", "Execution Version");
                validHm["executionVersion" + "_" + name] = name;
            }
            result = vdCommon.selectList(["[Business Area].[Business Area]" + vdUtil.fn_filterStr(businessArea)], [], "", "", "");
            for ( var i = 0; i < result.cs.rowCount; i++ ) {
                var name = vdUtil.fn_getDimValue(result, i, "Business Area", "Business Area");
                validHm["businessArea" + "_" + name] = name;
            }
            result = vdCommon.selectList(["[Time].[Planning Month]" + vdUtil.fn_filterStr(planningMonth)], [], "", "", "");
            for ( var i = 0; i < result.cs.rowCount; i++ ) {
                var name = vdUtil.fn_getDimValue(result, i, "Time", "Planning Month");
                validHm["planningMonth" + "_" + name] = name;
            }
            // Ap2 Mapping 정보를 가져온다.
            result = vdCommon.selectList(["[Version].[Version Name].[" + parsedParams.fbParams["[Version].[Version Name]"] + "]"
                                            ,"[Sales Domain].[AP2]"
                                            ,"[Business Area].[Business Area]"
                                            ,"[Comb Company].[Comb Company]"]
                                         ,["Measure.[CombComp BA AP2 Asn_Valid]"]
                                         ,"", "", "");
            for ( var i = 0; i < result.cs.rowCount; i++ ) {
                var name = vdUtil.fn_getDimValue(result, i, "Comb Company", "Comb Company") + "_" + vdUtil.fn_getDimValue(result, i, "Business Area", "Business Area");
                var value = vdUtil.fn_getDimValue(result, i, "Sales Domain", "AP2");
                validHm["ap2" + "_" + name] = value;
            }

            vdCommon.debug("profLoc : " + profLoc.length + " , toYear : " + toYear.length + " , item : " + item.length +
                                " , combCompany : " + combCompany.length + " , executionVersion : " + executionVersion.length +
                                " , businessArea : " + businessArea.length + " , planningMonth : " + planningMonth.length);

            // Validation - Validation 체크
            for ( var i = 0; i < parsedParams.fbGridRows.length; i++ ) {
                var row = parsedParams.fbGridRows[i];
                var rowstatus = row["rowstatus"];
                var rowindex = row["rowindex"];
                var key = "";

                var msg = "";

                value = row["[Prof Loc].[Prof Loc]"];
                key += value;
                /* 멤버 생성을 위해서 로직 제거
                if ( validHm["profLoc" + "_" + value] == undefined ) {
                    msg = vdUtil.fn_wordAppend(msg, "Check Prof Loc(" + value + "). ");
                } else {
                    row["[Prof Loc].[Prof Loc]"] = validHm["profLoc" + "_" + value];
                }
                */

                value = row["[To Time].[To Year]"];
                key += "_" + value;
                if ( validHm["toYear" + "_" + value] == undefined ) {
                    msg = vdUtil.fn_wordAppend(msg, "Check Year(" + value + "). ");
                }

                value = row["[Item].[Item]"];
                key += "_" + value;
                if ( validHm["item" + "_" + value] == undefined ) {
                    msg = vdUtil.fn_wordAppend(msg, "Check Item(" + value + "). ");
                }

                value = row["[Comb Company].[Comb Company]"];
                key += "_" + value;
                if ( validHm["combCompany" + "_" + value] == undefined ) {
                    msg = vdUtil.fn_wordAppend(msg, "Check Comb Company(" + value + "). ");
                } else {
                    row["[Comb Company].[Comb Company]"] = validHm["combCompany" + "_" + value];
                }

                value = row["[To Time].[To Year]"] + "_" + row["[Execution Version].[Execution Version]"];
                key += "_" + value;
                /* 멤버 생성을 위해서 로직 제거
                if ( validHm["executionVersion" + "_" + value] == undefined ) {
                    msg = vdUtil.fn_wordAppend(msg, "Check Execution Version(" + value + "). ");
                }
                */

                value = row["[Business Area].[Business Area]"];
                key += "_" + value;
                /* 멤버 생성을 위해서 로직 제거
                if ( validHm["businessArea" + "_" + value] == undefined ) {
                    msg = vdUtil.fn_wordAppend(msg, "Check Business Area(" + value + "). ");
                }
                */

                value = row["[To Time].[To Year]"] + vdUtil.fn_lpad(row["[Time].[Planning Month]"], 2, "0");
                key += "_" + value;
                if ( validHm["planningMonth" + "_" + value] == undefined ) {
                    msg = vdUtil.fn_wordAppend(msg, "Check Month(" + value + "). ");
                }

                value = row["[Comb Company].[Comb Company]"] + "_" + row["[Business Area].[Business Area]"];
                if ( validHm["ap2" + "_" + value] == undefined ) {
                    msg = vdUtil.fn_wordAppend(msg, "Check AP2(" + value + "). ");
                }

                if ( keyHm[key] != i ) {
                    msg = vdUtil.fn_wordAppend(msg, "Check Duplicate(" + keyHm[key] + " line). ");
                }

                if ( msg != "" ) {
                    validation.push(rowindex + "^" + msg);
                }
            }

            if ( validation.length > 0 ) {
                return { "Code" : 1, "Msg" : validation };
            }

            // [Prof Loc].[Prof Loc] 멤버 생성
            for ( var i = 0; i < profLoc.length; i++ ) {
                if ( validHm["profLoc" + "_" + profLoc[i]] == undefined ) {
                    vdCommon.createMember('[Prof Loc].[Prof Loc]',  profLoc[i]);
                }
            }
            // [Business Area].[Business Area] 멤버 생성
            for ( var i = 0; i < businessArea.length; i++ ) {
                if ( validHm["businessArea" + "_" + businessArea[i]] == undefined ) {
                    vdCommon.createMember('[Business Area].[Business Area]',  businessArea[i]);
                }
            }
            // [Execution Version].[Execution Version] 멤버 생성
            for ( var i = 0; i < executionVersion.length; i++ ) {
                if ( validHm["executionVersion" + "_" + executionVersion[i]] == undefined ) {
                    vdCommon.createMember('[Execution Version].[Execution Version]',  executionVersion[i]);
                }
            }

            // [Execution Version].[Execution Version] 으로 삭제후에 저장
            var where = [];
            where.push(vdUtil.fn_qDimVersionName(parsedParams));
            where.push("[Execution Version].[Execution Version]" + vdUtil.fn_filterStr(executionVersion));
            vdCommon.deleteMeasure(where, "Product Profit Upload");

            var versionName = parsedParams.fbParams["[Version].[Version Name]"];
            // 데이타 업로드 - 옮겨질 MG 의 Dimension 정의
            var dimension = "Version.[Version Name]^Prof Loc.[Prof Loc]^To Time.[To Year]^Item.[Item]^Time.[Planning Month]^Comb Company.[Comb Company]^Sales Domain.[AP2]^Execution Version.[Execution Version]^Business Area.[Business Area]";
            // 데이타 업로드 - 옮겨질 MG 의 Measure 정의
            var measure = "Product Profit Upload_Sales Qty^Product Profit Upload_N Price^Product Profit Upload_C Profit Rate";
            // 데이타 업로드 - 데이타 배열 생성
            var dataArray = [];
            for ( var i = 0; i < parsedParams.fbGridRows.length; i++ ) {
                var row = parsedParams.fbGridRows[i];
                dataArray[i] = versionName + "^" +
                                row["[Prof Loc].[Prof Loc]"] + "^" +
                                row["[To Time].[To Year]"] + "^" +
                                row["[Item].[Item]"] + "^" +
                                row["[To Time].[To Year]"] + vdUtil.fn_lpad(row["[Time].[Planning Month]"], 2, "0") + "^" +
                                row["[Comb Company].[Comb Company]"] + "^" +
                                validHm["ap2" + "_" + row["[Comb Company].[Comb Company]"] + "_" + row["[Business Area].[Business Area]"]] + "^" +  // AP2
                                row["[To Time].[To Year]"] + "_" + row["[Execution Version].[Execution Version]"] + "^" +
                                row["[Business Area].[Business Area]"] + "^" +
                                row["Measure.[Product Profit Upload_Sales Qty]"] + "^" +
                                vdUtil.fn_stringToFloat(row["Measure.[Product Profit Upload_N Price]"]).toFixed(2) + "^" +
                                vdUtil.fn_stringToFloat(row["Measure.[Product Profit Upload_C Profit Rate]"]).toFixed(2);
            }
            // 데이타 업로드 - 업로드 함수 호출
            vdCommon.fn_dataUpload(vdUtil.fn_qDimVersionName(parsedParams), dimension, measure, dataArray);

            // 후처리 파이썬 호출
            execQuery = 'EXEC plugin instance [PY_UI_ProductProfit] ' +
                            'for measures {[Product Profit_C Profit Rate]} ' +
                            'using scope ( [Version].[Version Name].filter((#.Name == "CWV_MP") || (#.Name == "VD")) ) ' +
                            'using arguments {(paramOutVersion, "' + versionName + '"), (ExecutionMode, "MediumWeight"), ("IncludeNullRows", "False"), (MaxSliceTableCells, 200000000), (MaxConcurrency, 1 )};'
            vdCommon.executePython("PY_UI_ProductProfit", execQuery);

            return { "Code" : 0, "Msg" : "It was saved successfully." };
        } catch ( e ) {
            vdCommon.error(e.message);
            return { "Code" : -1, "Msg" : e.message };
        } finally {
            vdCommon.programEnd();
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

/**************************************************************************************************************
26.04.09 : [Prof Loc].[Prof Loc] 도 멤버 생성하도록 로직 수정
26.04.15 : Ap2 Mapping 로직을 변경
**************************************** o9.NSCM.JSEWProductProfit *******************************************/