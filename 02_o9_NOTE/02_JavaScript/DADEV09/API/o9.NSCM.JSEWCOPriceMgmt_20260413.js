define('o9.NSCM.JSEWCOPriceMgmt', ['o9/data/query', 'o9/data/cellset', 'o9.NSCM.commonLibCO'], function () {

/**************************************************************************************
    프로그램명  : o9.NSCM.JSEWCOPriceMgmt
    화면명     : Finance TP
    설계자     : 송지훈 프로
    화면 개발자 :
    API 개발자 : sungmin0.lim
    최초생성   : 2025.11.06
**************************************************************************************/

	const programName = "o9.NSCM.JSEWCOPriceMgmt";
    const commonLib = require('o9.NSCM.commonLibCO');
    const coUtil = new commonLib.COUtil();

/************************************************* UI Call Common Logic *************************************************/
	var fn_loadFunction = function(o9Params){
        const coCommon = new commonLib.COCommon(programName + "." + arguments.callee.name);
        coCommon.setLogLevel("Debug");

		try {
            let returnData = {};
            let obj = this;

            coCommon.printParams(o9Params);

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

            coCommon.programEnd();
            return rtn;
        } catch ( e ) {
            return { "Code" : -1, "Msg" : e.message };
        }
	};

/************************************************* common logic *************************************************/
    /*
{ "fbFuncName" : "fn_getChangeData", "fbParams" : {  },
  "fbGridRows" : [
{ "rowstatus":"C","rowindex":"0","[Item].[Item]":"CCH016SBEB/STD","[Sub Location].[Sub Location]":"P103","[Location].[Location]":"L403WC4A" },
{ "rowstatus":"C","rowindex":"1","[Item].[Item]":"CCH016SBEB/XAR","[Sub Location].[Sub Location]":"P103","[Location].[Location]":"L420WC4A" },
{ "rowstatus":"C","rowindex":"2","[Item].[Item]":"CCH016SBEC/STD","[Sub Location].[Sub Location]":"P103","[Location].[Location]":"L420WC6A" },
{ "rowstatus":"C","rowindex":"3","[Item].[Item]":"CCH020SBE/PCL","[Sub Location].[Sub Location]":"P103","[Location].[Location]":"L421WC4A" }
                  ] }
    */
    var fn_getChangeData = function(parsedParams){
        const coCommon = new commonLib.COCommon(programName + "." + arguments.callee.name);
        coCommon.setLogLevel("Debug");

		try {
            // Validation 체크
            var validation = [];
            for ( var i = 0; i < parsedParams.fbGridRows.length; i++ ) {
                var row = parsedParams.fbGridRows[i];
                var rowindex = row["rowindex"];

                // 여러건이 들어갈 수 있어서 Max Seq 를 가져온후에, 마지막 Seq 의 TP Change 상태를 체크한다.
                var dimensions = [];
                dimensions.push("&CWV");
                dimensions.push("&CurrentWeek");
                dimensions.push(coUtil.fn_qDim(row, "[Item].[Item]"));
                dimensions.push(coUtil.fn_qDim(row, "[Location].[Location]"));
                dimensions.push(coUtil.fn_qDim(row, "[Sub Location].[Sub Location]"));
                dimensions.push("[Common Code Master].[Master Code]");
                dimensions.push("[Seq].[Seq]");

                var measures = [];
                measures.push("Measure.[TP Change_Change Status]");

                var result = coCommon.selectList(dimensions, measures, "", "orderby [Seq].[Seq].Key desc", "limit 1");
                if ( result.cs.rowCount > 0 ) {
                    var maxSeq = coUtil.fn_getDimValue(result, 0, "Seq", "Seq");

                    dimensions = [];
                    dimensions.push("&CWV");
                    dimensions.push("&CurrentWeek");
                    dimensions.push(coUtil.fn_qDim(row, "[Item].[Item]"));
                    dimensions.push(coUtil.fn_qDim(row, "[Location].[Location]"));
                    dimensions.push(coUtil.fn_qDim(row, "[Sub Location].[Sub Location]"));
                    dimensions.push("[Common Code Master].[Master Code]");
                    dimensions.push("[Seq].[Seq].[" + maxSeq + "]");

                    var result = coCommon.selectList(dimensions, measures, "", "", "limit 1");
                    if ( coUtil.fn_getMeaValue(result, 0, "TP Change_Change Status") == "Submitted" ) {
                        validation.push(rowindex + "^" + "This is the submitted data.");
                    }
                }
            }

            if ( validation.length > 0 ) {
                return { "Code" : 1, "Msg" : validation };
            }

            // 데이타를 가져온다.
            var rows = [];
            for ( var i = 0; i < parsedParams.fbGridRows.length; i++ ) {
                var row = parsedParams.fbGridRows[i];
                var rowindex = row["rowindex"];

                var dimensions = [];
                dimensions.push("&CWV");
                dimensions.push("&CurrentWeek");
                dimensions.push("[Item].[Product]");
                dimensions.push(coUtil.fn_qDim(row, "[Item].[Item]"));
                dimensions.push(coUtil.fn_qDim(row, "[Location].[Location]"));
                dimensions.push(coUtil.fn_qDim(row, "[Sub Location].[Sub Location]"));
                dimensions.push("[Currency].[Currency]");
                dimensions.push("[Common Code Master].[Master Code]" + coUtil.fn_filterStr(["CO03_003","CO03_004","CO03_005"]));
                dimensions.push("[Incoterms].[Incoterms]");

                var measures = [];
                measures.push("Measure.[TP W_Price]");

                var result = coCommon.selectList(dimensions, measures, "", "", "");
                for ( var f1 = 0; f1 < result.cs.rowCount; f1++ ) {
                    rows.push({"[Item].[Product]" : coUtil.fn_getDimValue(result, f1, "Item", "Product")
                                ,"[Item].[Item]" : coUtil.fn_getDimValue(result, f1, "Item", "Item")
                                ,"[Location].[Location]" : coUtil.fn_getDimValue(result, f1, "Location", "Location")
                                ,"[Sub Location].[Sub Location]" : coUtil.fn_getDimValue(result, f1, "Sub Location", "Sub Location")
                                ,"[Common Code Master].[Master Code]" : coUtil.fn_getDimValue(result, f1, "Common Code Master", "Master Code")
                                ,"Measure.[TP Change_Incoterms1 AsIs]" : coUtil.fn_getDimValue(result, f1, "Incoterms", "Incoterms")
                                ,"Measure.[TP Change_Incoterms1 ToBe]" : coUtil.fn_getMeaValue(result, f1, "Incoterms", "Incoterms")
                                ,"Measure.[TP Change_Currency AsIs]" : coUtil.fn_getDimValue(result, f1, "Currency", "Currency")
                                ,"Measure.[TP Change_Currency ToBe]" : coUtil.fn_getMeaValue(result, f1, "Currency", "Currency")
                                ,"Measure.[TP Change_Price AsIs]" : coUtil.fn_getMeaValue(result, f1, "TP W_Price")
                                ,"Measure.[TP Change_Price ToBe]" : coUtil.fn_getMeaValue(result, f1, "TP W_Price")});
                }
            }

            coCommon.programEnd();

            return { "Code" : 0, "Msg" : "", Rows : rows };
        } catch ( e ) {
            coCommon.error(e.message);
            return { "Code" : -1, "Msg" : e.message };
        }
    };

    // { "fbFuncName" : "fn_cb_getList", "fbParams" : { "vFilterName" : "Measure"  } }
	var fn_cb_getList = function(parsedParams){
        const coCommon = new commonLib.COCommon(programName + "." + arguments.callee.name);
        coCommon.setLogLevel("Debug");

		try {
		    var vFilterName = coUtil.fn_getParam(parsedParams, "vFilterName");

            var comboList;
            if ( vFilterName == "Measure" ) {
                var result = coCommon.selectList(['[Common Code Master].[Master Code].filter(#.Name in {"CO03_003","CO03_004","CO03_005"})'],
                                                 [],
                                                 "", "", "");
                comboList = coCommon.fn_makeCombo(result, {DimName : "Common Code Master", DimAttbName : "Master Code"});
            } else if ( vFilterName == "Incoterm" ) {
                var result = coCommon.selectList(['[Incoterms].[Incoterms]'],
                                                 [],
                                                 "", "orderby [Incoterms].[Incoterms].DisplayName", "");
                comboList = coCommon.fn_makeCombo(result, {DimName : "Incoterms", DimAttbName : "Incoterms"});
            } else if ( vFilterName == "Currency" ) {
                var result = coCommon.selectList(['[Currency].[Currency]'],
                                                 [],
                                                 "", "orderby [Currency].[Currency].DisplayName", "");
                comboList = coCommon.fn_makeCombo(result, {DimName : "Currency", DimAttbName : "Currency"});
            } else if ( vFilterName == "Week Valid From" ) {
                var result = coCommon.selectList(['&AllWeeks.filter(#.Key >= &CurrentWeek.element(0).Key && #.Key <= &CurrentWeek.element(0).LeadOffset(24).Key)'],
                                                 [],
                                                 "", "orderby [Time].[Week].DisplayName", "");
                comboList = coCommon.fn_makeCombo(result, {DimName : "Time", DimAttbName : "Week"});
            }
            coCommon.debug("ComboData : " + JSON.stringify(comboList.slice(0,3)));

            coCommon.programEnd();

            return { "Code" : 0, "Msg" : "", "Rows" : comboList };
        } catch ( e ) {
            coCommon.error(e.message);
            return { "Code" : -1, "Msg" : e.message };
        }
    };

    /*
{ "fbFuncName" : "fn_checkValidation", "fbParams" : { },
  "fbGridRows" : [
{ "rowstatus":"C","rowindex":"0","[Item].[Item]":"CCH016SBEB/STD","[Sub Location].[Sub Location]":"P103","[Location].[Location]":"L403WC4A","[Common Code Master].[Master Code]":"CO03_003","Measure.[TP Change_Incoterms1 AsIs]":"CIF","Measure.[TP Change_Incoterms1 ToBe]":"CIF","Measure.[TP Change_Currency AsIs]":"EUR","Measure.[TP Change_Currency ToBe]":"EUR","Measure.[TP Change_Price AsIs]":"1000","Measure.[TP Change_Price ToBe]":"2000","Measure.[TP Change_Valid Week From]":"202547","[Seq].[Seq]":"1" },
{ "rowstatus":"C","rowindex":"1","[Item].[Item]":"CCH016SBEB/XAR","[Sub Location].[Sub Location]":"P103","[Location].[Location]":"L420WC4A","[Common Code Master].[Master Code]":"CO04_001","Measure.[TP Change_Incoterms1 AsIs]":"CIF","Measure.[TP Change_Incoterms1 ToBe]":"CIF","Measure.[TP Change_Currency AsIs]":"EUR","Measure.[TP Change_Currency ToBe]":"KKK","Measure.[TP Change_Price AsIs]":"1000","Measure.[TP Change_Price ToBe]":"2000","Measure.[TP Change_Valid Week From]":"202547","[Seq].[Seq]":"1" },
{ "rowstatus":"C","rowindex":"2","[Item].[Item]":"CCH016SBEC/STD","[Sub Location].[Sub Location]":"P103","[Location].[Location]":"L420WC6A","[Common Code Master].[Master Code]":"CO03_004","Measure.[TP Change_Incoterms1 AsIs]":"FOB","Measure.[TP Change_Incoterms1 ToBe]":"FOB","Measure.[TP Change_Currency AsIs]":"EUR","Measure.[TP Change_Currency ToBe]":"EUR","Measure.[TP Change_Price AsIs]":"1000","Measure.[TP Change_Price ToBe]":"2000","Measure.[TP Change_Valid Week From]":"202547","[Seq].[Seq]":"2" },
{ "rowstatus":"C","rowindex":"3","[Item].[Item]":"CCH020SBE/PCL","[Sub Location].[Sub Location]":"P103","[Location].[Location]":"L421WC4A","[Common Code Master].[Master Code]":"CO03_005","Measure.[TP Change_Incoterms1 AsIs]":"CIP","Measure.[TP Change_Incoterms1 ToBe]":"CIP","Measure.[TP Change_Currency AsIs]":"EUR","Measure.[TP Change_Currency ToBe]":"EUR","Measure.[TP Change_Price AsIs]":"1000","Measure.[TP Change_Price ToBe]":"2000","Measure.[TP Change_Valid Week From]":"202547","[Seq].[Seq]":"2" }
                  ] }
    */
    var fn_checkValidation = function(parsedParams){
        const coCommon = new commonLib.COCommon(programName + "." + arguments.callee.name);
        coCommon.setLogLevel("Debug");

		try {
		    function fn_makeHm(row, dimension, value) {
		        if ( validHm[value] == undefined ) {
                    var result = coCommon.selectList([dimension + ".[" + value + "]"], "", "", "", "");
                    if ( result.cs.rowCount > 0 ) {
                        var dims = dimension.split(".");
                        var data = coUtil.fn_getDimValue(result, 0, dims[0].replace(/[\[\]]/g, ""), dims[1].replace(/[\[\]]/g, ""));
                        validHm[data] = data;
                    }
                }
		    }

		    var validHm = {};

            // 주차 데이타 생성
            var result = coCommon.selectList(["&AllWeeks.filter(#.Key >= &CurrentWeek.element(0).Key && #.Key <= &CurrentWeek.element(0).LeadOffset(24).Key)"], "", "", "", "");
            for ( var f1 = 0; f1 < result.cs.rowCount; f1++ ) {
                var data = coUtil.fn_getDimValue(result, f1, "Time", "Week");
                validHm[data] = data;
            }

            // 값 비교를 위해서 hm 에 등록
//            for ( var i = 0; i < parsedParams.fbGridRows.length; i++ ) {
//                var row = parsedParams.fbGridRows[i];
//
//                validHm[row["[Item].[Item]"] + "_" + row["[Sub Location].[Sub Location]"] + "_" +
//                        row["[Location].[Location]"] + "_" + row["[Common Code Master].[Master Code]"] + "_AsIs"] = row["Measure.[TP Change_Price AsIs]"];
//                validHm[row["[Item].[Item]"] + "_" + row["[Sub Location].[Sub Location]"] + "_" +
//                        row["[Location].[Location]"] + "_" + row["[Common Code Master].[Master Code]"] + "_ToBe"] = row["Measure.[TP Change_Price ToBe]"];
//            }

            // Validation 체크
            var validation = [];
            for ( var i = 0; i < parsedParams.fbGridRows.length; i++ ) {
                var row = parsedParams.fbGridRows[i];
                var rowindex = row["rowindex"];
                var result;

                var validate = "";

                fn_makeHm(row, "[Item].[Item]", row["[Item].[Item]"]);
                if ( validHm[row["[Item].[Item]"]] == undefined ) {
                    validate = "존재하지 않는 아이템 입니다.";
                }
                fn_makeHm(row, "[Sub Location].[Sub Location]", row["[Sub Location].[Sub Location]"]);
                if ( validHm[row["[Sub Location].[Sub Location]"]] == undefined ) {
                    validate = coUtil.fn_wordAppend(validate, "From Site에서 존재하지 않는 사이트 입니다.");
                }
                fn_makeHm(row, "[Location].[Location]", row["[Location].[Location]"]);
                if ( validHm[row["[Location].[Location]"]] == undefined ) {
                    validate = coUtil.fn_wordAppend(validate, "To Site에서 존재하지 않는 사이트 입니다.");
                }
                fn_makeHm(row, "[Common Code Master].[Master Code]", row["[Common Code Master].[Master Code]"]);
                if ( validHm[row["[Common Code Master].[Master Code]"]] == undefined ) {
                    validate = coUtil.fn_wordAppend(validate, "잘못된 Measure를 입력했습니다.");
                }
                fn_makeHm(row, "[Incoterms].[Incoterms]", row["Measure.[TP Change_Incoterms1 AsIs]"]);
                if ( validHm[row["Measure.[TP Change_Incoterms1 AsIs]"]] == undefined ) {
                    validate = coUtil.fn_wordAppend(validate, "(AsIs)잘못된 Incoterms를 입력했습니다.");
                }
                fn_makeHm(row, "[Incoterms].[Incoterms]", row["Measure.[TP Change_Incoterms1 ToBe]"]);
                if ( validHm[row["Measure.[TP Change_Incoterms1 ToBe]"]] == undefined ) {
                    validate = coUtil.fn_wordAppend(validate, "(ToBe)잘못된 Incoterms를 입력했습니다.");
                }
//                if ( row["[Common Code Master].[Master Code]"] == "CO03_004" && row["Measure.[TP Change_Incoterms1 ToBe]"] != "FOB" ) {
//                    validate = coUtil.fn_wordAppend(validate, "메저가 FOB Price인 경우, Incoterms는 반드시 FOB여야 합니다.");
//                }
                fn_makeHm(row, "[Currency].[Currency]", row["Measure.[TP Change_Currency AsIs]"]);
                if ( validHm[row["Measure.[TP Change_Currency AsIs]"]] == undefined ) {
                    validate = coUtil.fn_wordAppend(validate, "(AsIs)잘못된 Currency를 입력했습니다.");
                }
                fn_makeHm(row, "[Currency].[Currency]", row["Measure.[TP Change_Currency ToBe]"]);
                if ( validHm[row["Measure.[TP Change_Currency ToBe]"]] == undefined ) {
                    validate = coUtil.fn_wordAppend(validate, "(ToBe)잘못된 Currency를 입력했습니다.");
                }
//                if ( coUtil.fn_isInt(row["Measure.[TP Change_Price AsIs]"]) == false ) {
//                    validate = coUtil.fn_wordAppend(validate, "(AsIs)Price는 반드시 숫자로 입력해야 합니다.");
//                }
//                if ( row["[Common Code Master].[Master Code]"] == "CO03_003" ) {
//                    var price3 = parseInt(row["Measure.[TP Change_Price ToBe]"]);
//                    if ( validHm[row["[Item].[Item]"] + "_" + row["[Sub Location].[Sub Location]"] + "_" + row["[Location].[Location]"] + "_" + "CO03_004" + "_ToBe"] != undefined ) {
//                        var price4 = parseInt(validHm[row["[Item].[Item]"] + "_" + row["[Sub Location].[Sub Location]"] + "_" + row["[Location].[Location]"] + "_" + "CO03_004" + "_ToBe"]);
//                        if ( price3 < price4 ) {
//                            validate = coUtil.fn_wordAppend(validate, "(ToBe)EX-FAC PRICE 값은 FOB Price( 값보다 크거나 같아야 합니다.");
//                        }
//                    }
//                }
//                if ( coUtil.fn_isInt(row["Measure.[TP Change_Price ToBe]"]) == false ) {
//                    validate = coUtil.fn_wordAppend(validate, "(ToBe)Price는 반드시 숫자로 입력해야 합니다.");
//                }
//                if ( coUtil.fn_isInt(row["Measure.[TP Change_Valid Week From]"]) == false ) {
//                    validate = coUtil.fn_wordAppend(validate, "Valid Week From은 반드시 년도 4자리와 주차 2자리의 숫자로 구성되어야 합니다.");
//                }
                if ( validHm[row["Measure.[TP Change_Valid Week From]"]] == undefined ) {
                    validate = coUtil.fn_wordAppend(validate, "Valid Week From 값이 과거이거나 잘못입력했습니다.");
                }

                if ( validate != "" ) {
                    validation.push(rowindex + "^" + validate);
                }
            }

            if ( validation.length > 0 ) {
                return { "Code" : 1, "Msg" : validation };
            }

            coCommon.programEnd();

            return { "Code" : 0, "Msg" : "" };
        } catch ( e ) {
            coCommon.error(e.message);
            return { "Code" : -1, "Msg" : e.message };
        }
    };

    /*
{ "fbFuncName" : "fn_reqeustChangePrice", "fbParams" : { },
  "fbGridRows" : [
{ "rowstatus":"C","rowindex":"0","[Item].[Item]":"CCH016SBEB/STD","[Sub Location].[Sub Location]":"P103","[Location].[Location]":"L403WC4A","[Common Code Master].[Master Code]":"CO03_003","Measure.[TP Change_Incoterms1 AsIs]":"CIF","Measure.[TP Change_Incoterms1 ToBe]":"CIF","Measure.[TP Change_Currency AsIs]":"EUR","Measure.[TP Change_Currency ToBe]":"EUR","Measure.[TP Change_Price AsIs]":"1000","Measure.[TP Change_Price ToBe]":"2000","Measure.[TP Change_Valid Week From]":"202547","[Seq].[Seq]":"1" },
{ "rowstatus":"C","rowindex":"1","[Item].[Item]":"CCH016SBEB/XAR","[Sub Location].[Sub Location]":"P103","[Location].[Location]":"L420WC4A","[Common Code Master].[Master Code]":"CO04_001","Measure.[TP Change_Incoterms1 AsIs]":"CIF","Measure.[TP Change_Incoterms1 ToBe]":"CIF","Measure.[TP Change_Currency AsIs]":"EUR","Measure.[TP Change_Currency ToBe]":"KKK","Measure.[TP Change_Price AsIs]":"1000","Measure.[TP Change_Price ToBe]":"2000","Measure.[TP Change_Valid Week From]":"202547","[Seq].[Seq]":"1" },
{ "rowstatus":"C","rowindex":"2","[Item].[Item]":"CCH016SBEC/STD","[Sub Location].[Sub Location]":"P103","[Location].[Location]":"L420WC6A","[Common Code Master].[Master Code]":"CO03_004","Measure.[TP Change_Incoterms1 AsIs]":"FOB","Measure.[TP Change_Incoterms1 ToBe]":"FOB","Measure.[TP Change_Currency AsIs]":"EUR","Measure.[TP Change_Currency ToBe]":"EUR","Measure.[TP Change_Price AsIs]":"1000","Measure.[TP Change_Price ToBe]":"2000","Measure.[TP Change_Valid Week From]":"202547","[Seq].[Seq]":"2" },
{ "rowstatus":"C","rowindex":"3","[Item].[Item]":"CCH020SBE/PCL","[Sub Location].[Sub Location]":"P103","[Location].[Location]":"L421WC4A","[Common Code Master].[Master Code]":"CO03_005","Measure.[TP Change_Incoterms1 AsIs]":"CIP","Measure.[TP Change_Incoterms1 ToBe]":"CIP","Measure.[TP Change_Currency AsIs]":"EUR","Measure.[TP Change_Currency ToBe]":"EUR","Measure.[TP Change_Price AsIs]":"1000","Measure.[TP Change_Price ToBe]":"2000","Measure.[TP Change_Valid Week From]":"202547","[Seq].[Seq]":"2" }
                  ] }
    */
    var fn_reqeustChangePrice = function(parsedParams){
        const coCommon = new commonLib.COCommon(programName + "." + arguments.callee.name);
        coCommon.setLogLevel("Debug");

		try {
            var maxSeqHm = {};
            for ( var i = 0; i < parsedParams.fbGridRows.length; i++ ) {
                var row = parsedParams.fbGridRows[i];
                var rowindex = row["rowindex"];

                // Max 값을 구한다.
                if ( maxSeqHm[row["[Item].[Item]"] + "_" + row["[Sub Location].[Sub Location]"] + "_" + row["[Location].[Location]"] + "_" + row["[Seq].[Seq]"]] == undefined ) {
                    var dimensions = [];
                    dimensions.push("&CWV");
                    dimensions.push("&CurrentWeek");
                    dimensions.push(coUtil.fn_qDim(row, "[Item].[Item]"));
                    dimensions.push(coUtil.fn_qDim(row, "[Location].[Location]"));
                    dimensions.push(coUtil.fn_qDim(row, "[Sub Location].[Sub Location]"));
                    dimensions.push("[Common Code Master].[Master Code]");
                    dimensions.push("[Seq].[Seq]");

                    var measures = [];
                    measures.push("Measure.[TP Change_Change Status]");

                    var result = coCommon.selectList(dimensions, measures, "", "orderby [Seq].[Seq].Key desc", "limit 1");
                    var seq = 100;
                    if ( result.cs.rowCount > 0 ) {
                        seq = parseInt(coUtil.fn_getDimValue(result, 0, "Seq", "Seq")) + 1;
                    }
                    maxSeqHm[row["[Item].[Item]"] + "_" + row["[Sub Location].[Sub Location]"] + "_" + row["[Location].[Location]"] + "_" + row["[Seq].[Seq]"]] = seq;
                }

                var maxSeq = maxSeqHm[row["[Item].[Item]"] + "_" + row["[Sub Location].[Sub Location]"] + "_" + row["[Location].[Location]"] + "_" + row["[Seq].[Seq]"]];

                // TP_Status 업데이트
                var dimensions = [];
                dimensions.push("&CWV");
                dimensions.push(coUtil.fn_qDim(row, "[Item].[Item]"));
                dimensions.push(coUtil.fn_qDim(row, "[Location].[Location]"));
                dimensions.push(coUtil.fn_qDim(row, "[Sub Location].[Sub Location]"));
                dimensions.push("[Currency].[Currency]");
                dimensions.push("[Common Code Master].[Master Code]");
                dimensions.push("[Incoterms].[Incoterms]");

                var measures = [];
                measures.push(coUtil.fn_qMeaStr(null, "Measure.[TP_Status]", "Submitted"));

                coCommon.updateMeasure(dimensions, measures);

                // 데이타 생성
                var dimensions = [];
                dimensions.push("&CWV");
                dimensions.push("&CurrentWeek");
                dimensions.push(coUtil.fn_qDim(row, "[Item].[Item]"));
                dimensions.push(coUtil.fn_qDim(row, "[Location].[Location]"));
                dimensions.push(coUtil.fn_qDim(row, "[Sub Location].[Sub Location]"));
                dimensions.push(coUtil.fn_qDim(row, "[Common Code Master].[Master Code]"));
                dimensions.push("[Seq].[Seq].[" + maxSeq + "]");

                var measures = [];
                measures.push(coUtil.fn_qMeaStr(null, "Measure.[TP Change_Change Status]", "Submitted"));
                measures.push(coUtil.fn_qMeaStr(row, "Measure.[TP Change_Incoterms1 AsIs]"));
                measures.push(coUtil.fn_qMeaStr(row, "Measure.[TP Change_Incoterms1 ToBe]"));
                measures.push(coUtil.fn_qMeaStr(row, "Measure.[TP Change_Currency AsIs]"));
                measures.push(coUtil.fn_qMeaStr(row, "Measure.[TP Change_Currency ToBe]"));
                measures.push(coUtil.fn_qMeaStr(row, "Measure.[TP Change_Price AsIs]"));
                measures.push(coUtil.fn_qMeaStr(row, "Measure.[TP Change_Price ToBe]"));
                measures.push(coUtil.fn_qMeaStr(row, "Measure.[TP Change_Valid Week From]"));
                measures.push(coUtil.fn_qMeaUpdateUser("Measure.[TP Change_Created by]"));
                measures.push(coUtil.fn_qMeaUpdateTime("Measure.[TP Change_Creation time]"));
                measures.push(coUtil.fn_qMeaUpdateUser("Measure.[TP Change_Updated by]"));
                measures.push(coUtil.fn_qMeaUpdateTime("Measure.[TP Change_Update time]"));

                coCommon.createMeasure(dimensions, measures);
            }

            coCommon.programEnd();

            return { "Code" : 0, "Msg" : "It was saved successfully." };
        } catch ( e ) {
            coCommon.error(e.message);
            return { "Code" : -1, "Msg" : e.message };
        }
    };



    /*
{ "fbFuncName" : "fn_checkValidationSels", "fbParams" : { },
  "fbGridRows" : [
{ "rowstatus":"C","rowindex":"0","[Item].[Item]":"CCH016SBEB/STD","[Sub Location].[Sub Location]":"P103","[Location].[Location]":"L403WC4A","[Common Code Master].[Master Code]":"CO03_003","Measure.[TP Change_Incoterms1 ToBe]":"CIF","Measure.[TP Change_Currency ToBe]":"EUR" },
{ "rowstatus":"C","rowindex":"1","[Item].[Item]":"CCH016SBEB/STD","[Sub Location].[Sub Location]":"P103","[Location].[Location]":"L403WC4A","[Common Code Master].[Master Code]":"CO04_001","Measure.[TP Change_Incoterms1 ToBe]":"CIF","Measure.[TP Change_Currency ToBe]":"KKK" },
{ "rowstatus":"C","rowindex":"2","[Item].[Item]":"CCH016SBEC/STD","[Sub Location].[Sub Location]":"P103","[Location].[Location]":"L420WC6A","[Common Code Master].[Master Code]":"CO03_004","Measure.[TP Change_Incoterms1 ToBe]":"FOB","Measure.[TP Change_Currency ToBe]":"EUR" },
{ "rowstatus":"C","rowindex":"3","[Item].[Item]":"CCH020SBE/PCL","[Sub Location].[Sub Location]":"P103","[Location].[Location]":"L421WC4A","[Common Code Master].[Master Code]":"CO03_005","Measure.[TP Change_Incoterms1 ToBe]":"CIP","Measure.[TP Change_Currency ToBe]":"EUR" }
                  ] }
    */
    var fn_checkValidationSels = function(parsedParams){
        const coCommon = new commonLib.COCommon(programName + "." + arguments.callee.name);
        coCommon.setLogLevel("Debug");

		try {
		    function fn_makeHm(row, dimension, value) {
		        if ( validHm[value] == undefined ) {
                    var result = coCommon.selectList([dimension + ".[" + value + "]"], "", "", "", "");
                    if ( result.cs.rowCount > 0 ) {
                        var dims = dimension.split(".");
                        var data = coUtil.fn_getDimValue(result, 0, dims[0].replace(/[\[\]]/g, ""), dims[1].replace(/[\[\]]/g, ""));
                        validHm[data] = data;
                    }
                }
		    }

		    var validHm = {};

            // 주차 데이타 생성
            var result = coCommon.selectList(["&AllWeeks.filter(#.Key >= &CurrentWeek.element(0).Key && #.Key <= &CurrentWeek.element(0).LeadOffset(24).Key)"], "", "", "", "");
            for ( var f1 = 0; f1 < result.cs.rowCount; f1++ ) {
                var data = coUtil.fn_getDimValue(result, f1, "Time", "Week");
                validHm[data] = data;
            }

            // Validation 체크
            var validation = [];
            for ( var i = 0; i < parsedParams.fbGridRows.length; i++ ) {
                var row = parsedParams.fbGridRows[i];
                var rowindex = row["rowindex"];
                var result;

                var validate = "";

                fn_makeHm(row, "[Item].[Item]", row["[Item].[Item]"]);
                if ( validHm[row["[Item].[Item]"]] == undefined ) {
                    validate = "존재하지 않는 아이템 입니다.";
                }
                fn_makeHm(row, "[Sub Location].[Sub Location]", row["[Sub Location].[Sub Location]"]);
                if ( validHm[row["[Sub Location].[Sub Location]"]] == undefined ) {
                    validate = coUtil.fn_wordAppend(validate, "From Site에서 존재하지 않는 사이트 입니다.");
                }
                fn_makeHm(row, "[Location].[Location]", row["[Location].[Location]"]);
                if ( validHm[row["[Location].[Location]"]] == undefined ) {
                    validate = coUtil.fn_wordAppend(validate, "To Site에서 존재하지 않는 사이트 입니다.");
                }
                fn_makeHm(row, "[Common Code Master].[Master Code]", row["[Common Code Master].[Master Code]"]);
                if ( validHm[row["[Common Code Master].[Master Code]"]] == undefined ) {
                    validate = coUtil.fn_wordAppend(validate, "잘못된 Measure를 입력했습니다.");
                }
                fn_makeHm(row, "[Incoterms].[Incoterms]", row["Measure.[TP Change_Incoterms1 ToBe]"]);
                if ( validHm[row["Measure.[TP Change_Incoterms1 ToBe]"]] == undefined ) {
                    validate = coUtil.fn_wordAppend(validate, "(ToBe)잘못된 Incoterms를 입력했습니다.");
                }
                fn_makeHm(row, "[Currency].[Currency]", row["Measure.[TP Change_Currency ToBe]"]);
                if ( validHm[row["Measure.[TP Change_Currency ToBe]"]] == undefined ) {
                    validate = coUtil.fn_wordAppend(validate, "(ToBe)잘못된 Currency를 입력했습니다.");
                }

                if ( validate != "" ) {
                    validation.push(rowindex + "^" + validate);
                }
            }

            if ( validation.length > 0 ) {
                return { "Code" : 1, "Msg" : validation };
            }

            coCommon.programEnd();

            return { "Code" : 0, "Msg" : "" };
        } catch ( e ) {
            coCommon.error(e.message);
            return { "Code" : -1, "Msg" : e.message };
        }
    };


/************************************************* util logic *************************************************/

/************************************************* Mapping logic **********************************************/
    // Mapping 함수 정의, 마지막에 선언을 해야 함수를 정상적으로 인식함
    const functionMap = {
        "fn_getChangeData" : fn_getChangeData
        ,"fn_cb_getList" : fn_cb_getList
        ,"fn_checkValidation" : fn_checkValidation
        ,"fn_reqeustChangePrice" : fn_reqeustChangePrice
        ,"fn_checkValidationSels" : fn_checkValidationSels
    };

    return {
        fn_loadFunction : fn_loadFunction
    };
});

/******************************** o9.NSCM.JSEWCOPriceMgmt *******************************
2025.11.11 : fn_checkValidationSels 추가
**************************************************************************************/