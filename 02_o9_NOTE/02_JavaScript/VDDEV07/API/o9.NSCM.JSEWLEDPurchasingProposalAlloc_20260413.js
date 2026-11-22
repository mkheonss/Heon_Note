define('o9.NSCM.JSEWLEDPurchasingProposalAlloc', ['o9/data/query', 'o9/data/cellset', 'o9.NSCM.commonLib'], function() {	
    /*--------------------------------------------------------------------------------------------------*/
    // 프로그램명 : o9.NSCM.JSEWLEDPurchasingProposalAlloc
    // Action Button : EWVDPOPQtyLED
    // 화면명 : Purchasing Proposal
    // 2026.03.06 최초 생성                                                        / gs9.kim */
    // 2026.03.31 구조 변경에 따른 그레인 변경 적용                                 / gs9.kim */
    /*--------------------------------------------------------------------------------------------------*/

    const programName = "o9.NSCM.JSEWLEDPurchasingProposalAlloc";
    const commonLib = require('o9.NSCM.commonLib');
    const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
    const vdUtil = new commonLib.VdUtil();
	
    var fn_loadFunction = function(o9Params) {
		try {
            vdCommon.setLogLevel("Debug");
            vdCommon.printParams(o9Params);

            // 파라메타 가져오기
            const parsedParams = JSON.parse(o9Params);
			const fbFuncName = parsedParams.fbFuncName;
            
			if ( functionMap[fbFuncName] == undefined ) {
                return { "Code" : 1, "Msg" : "No Function" };
            }

            if ( parsedParams["fbParams"] == undefined ) {
                parsedParams["fbParams"] = {};
            }
            if ( parsedParams.fbParams["includeField"] == undefined ) {
                parsedParams.fbParams["includeField"] = "";
            }
            // 조회시 기본 limit 지정( 3000개 )
            if ( parsedParams.fbParams["limit"] == undefined ) {
                parsedParams.fbParams["limit"] = "limit 3000";
            } else if ( parsedParams.fbParams["limit"] == -1 ) {
                parsedParams.fbParams["limit"] = "";    
            } else {
                parsedParams.fbParams["limit"] = "limit " + parsedParams.fbParams.limit;
            }
            // 콤보에 All 추가
            if ( parsedParams.fbParams["existAll"] == undefined ) {
                parsedParams.fbParams["existAll"] = false;
            }
            // where 조건 추가
            if ( parsedParams.fbParams["where"] == undefined ) {
                parsedParams.fbParams["where"] = {};
            }
            
            const rtn = functionMap[fbFuncName](parsedParams);
            return rtn;
        } catch ( e ) {
            return { "Code" : -1, "Msg" : e.message };
        } finally {
            vdCommon.programEnd();
        }
	};

    /*
    {	"fbFuncName" : "fn_save",
        "fbParams" : { "[Version].[Version Name]" : "CWV_MP" },
        "fbGridRows" : [
        {
            "rowstatus":"U",
            "rowindex":"1",
            "[Demand].[DemandID]":"DMD_0000576467",
            "[Location].[Location]":"P306",
            "[To Location].[To Location]":"S356",
            "[Sales Domain].[Ship To]":"5006523",
            "[Time].[Week]":"202535",
            "[To Time].[To Week]":"202535",
            "[Item].[Item]":"LH008IWAMWS/XU",
            "[Item Material].[Item Material]":"0601-004001",
            "[Item Material].[C10]":"R",
            "[Trans Mode].[Trans Mode]":"TRUCK",
            "[Seq1].[Seq1]":"1",
            "[LED Rank].[LED Rank]":"ND85551210",
            "[LED Category].[LED Category]":"ECP",
            "[Inventory Category].[Inventory Category]":"Onhand",
            "Measure.[Purchasing Proposal Alloc LED_LED Qty]":"1800",
			"Measure.[Purchasing Proposal Alloc LED_Org Qty]":"1800",
            "Measure.[Purchasing Proposal Alloc LED_Assigned Qty]":"1800",
            "Measure.[Purchasing Proposal Alloc LED_Select Qty]":"1800",
            "Measure.[Purchasing Proposal Alloc LED_Mixed Rank]":"",
            "Measure.[Purchasing Proposal Alloc LED_Set Rank]":"",
            "Measure.[Purchasing Proposal Alloc LED_Mixed Rank Flag]":""
        },
        {
            "rowstatus":"U",
            "rowindex":"1",
            "[Demand].[DemandID]":"DMD_0000576467",
            "[Location].[Location]":"P306",
            "[To Location].[To Location]":"S356",
            "[Sales Domain].[Ship To]":"5006523",
            "[Time].[Week]":"202535",
            "[To Time].[To Week]":"202535",
            "[Item].[Item]":"LH008IWAMWS/XU",
            "[Item Material].[Item Material]":"0601-004002",
            "[Item Material].[C10]":"G",
            "[Trans Mode].[Trans Mode]":"TRUCK",
            "[Seq1].[Seq1]":"1",
            "[LED Rank].[LED Rank]":"ND85551210",
            "[LED Category].[LED Category]":"ECP",
            "[Inventory Category].[Inventory Category]":"Onhand",
            "Measure.[Purchasing Proposal Alloc LED_LED Qty]":"1800",
			"Measure.[Purchasing Proposal Alloc LED_Org Qty]":"1800",
            "Measure.[Purchasing Proposal Alloc LED_Assigned Qty]":"1800",
            "Measure.[Purchasing Proposal Alloc LED_Select Qty]":"1800",
            "Measure.[Purchasing Proposal Alloc LED_Mixed Rank]":"",
            "Measure.[Purchasing Proposal Alloc LED_Set Rank]":"",
            "Measure.[Purchasing Proposal Alloc LED_Mixed Rank Flag]":""
        },
        {
            "rowstatus":"U",
            "rowindex":"1",
            "[Demand].[DemandID]":"DMD_0000576467",
            "[Location].[Location]":"P306",
            "[To Location].[To Location]":"S356",
            "[Sales Domain].[Ship To]":"5006523",
            "[Time].[Week]":"202535",
            "[To Time].[To Week]":"202535",
            "[Item].[Item]":"LH008IWAMWS/XU",
            "[Item Material].[Item Material]":"0601-004003",
            "[Item Material].[C10]":"B",
            "[Trans Mode].[Trans Mode]":"TRUCK",
            "[Seq1].[Seq1]":"1",
            "[LED Rank].[LED Rank]":"ND85551210",
            "[LED Category].[LED Category]":"ECP",
            "[Inventory Category].[Inventory Category]":"Onhand",
            "Measure.[Purchasing Proposal Alloc LED_LED Qty]":"1800",
			"Measure.[Purchasing Proposal Alloc LED_Org Qty]":"1800",
            "Measure.[Purchasing Proposal Alloc LED_Assigned Qty]":"1800",
            "Measure.[Purchasing Proposal Alloc LED_Select Qty]":"1800",
            "Measure.[Purchasing Proposal Alloc LED_Mixed Rank]":"",
            "Measure.[Purchasing Proposal Alloc LED_Set Rank]":"",
            "Measure.[Purchasing Proposal Alloc LED_Mixed Rank Flag]":""
        }]
    }
    */
    var fn_save = function(parsedParams) {
        vdCommon.debug("parsedParams :: " + JSON.stringify(parsedParams));

		try {
            const rows = parsedParams.fbGridRows;
            const versionName = vdUtil.fn_qDimVersionName(parsedParams);

            // Validation 체크
            fn_validation(rows);
            
            const isIndoorLed = rows.some(row => row["[Item Material].[C10]"].includes("R/G/B Pkg"));
            isIndoorLed ? fn_setIndoorLEDRank(rows, versionName) : fn_setTheWallRank(rows, versionName);

            const selectSum = fn_getSelectSum(rows);

            rows.forEach(row => {
                const dimensions = [];
                dimensions.push(versionName);
                fn_getDimensionFromRow(row).forEach((key) => dimensions.push(vdUtil.fn_qDim(row, key)));
                
                const measures = [];
                Object.keys(row)
                  .filter(
                    (key) =>
                      key.startsWith("Measure.") && !key.startsWith("Measure.[Purchasing Proposal Alloc LED_Org Qty]") &&
                      !key.startsWith("Measure.[Purchasing Proposal Alloc LED_Assigned Qty]") &&
                      !key.startsWith("Measure.[Purchasing Proposal Alloc LED_Remained Qty]")
                  )
                  .forEach((key) => measures.push(vdUtil.fn_qMeaStr(row, key)));
                 
                const assignedQty = row["rowstatus"] === "none" || row["[LED Rank].[LED Rank]"].startsWith("P_")
                    ? row["Measure.[Purchasing Proposal Alloc LED_Assigned Qty]"] : fn_getAssignedQty(row, versionName);
                measures.push(`Measure.[Purchasing Proposal Alloc LED_Assigned Qty]="${assignedQty}";`);
                measures.push(`Measure.[Purchasing Proposal Alloc LED_Select Sum]="${selectSum}";`);
                measures.push(vdUtil.fn_qMeaUpdateTime('Measure.[Purchasing Proposal Alloc LED_Update time]'));
                measures.push('Measure.[Purchasing Proposal Alloc LED_Updated by]=CurrentUser().[User Name];');

                vdCommon.updateMeasure(dimensions, measures);
                // fn_updateAssignedQtyAll(row, versionName, assignedQty);
            });

            return { "Code" : 0, "Msg" : "It was saved successfully." };
        } catch ( e ) {
            vdCommon.error(e.message);
            return { "Code" : -1, "Msg" : e.message };
        }
    };

    var fn_getDimensionFromRow = (row) =>
      Object.keys(row).filter(
        (key) =>
          key.startsWith("[Demand].[DemandID]") ||
          key.startsWith("[Location].[Location]") ||
          key.startsWith("[To Location].[To Location]") ||
          key.startsWith("[Sales Domain].[Ship To]") ||
          key.startsWith("[Time].[Week]") ||
          key.startsWith("[To Time].[To Week]") ||
          key.startsWith("[Item].[Item]") ||
          key.startsWith("[Item Material].[Item Material]") ||
          key.startsWith("[Trans Mode].[Trans Mode]") ||
          key.startsWith("[Seq1].[Seq1]") ||
          key.startsWith("[LED Rank].[LED Rank]") ||
          key.startsWith("[LED Category].[LED Category]") ||
          key.startsWith("[Inventory Category].[Inventory Category]")
      );

    var fn_currentWeek = () => vdCommon.selectResult('&CurrentWeek.element(0).DisplayName');
    
    var fn_getSelectSum = (rows) => rows
        .filter(row => Number(row["Measure.[Purchasing Proposal Alloc LED_Select Qty]"]) > 0)
        .reduce((acc, cur) => acc + Number(cur["Measure.[Purchasing Proposal Alloc LED_Select Qty]"]), 0);

    var fn_getAssignedQty = function(row, versionName) {
        const dimensions = [];
        dimensions.push(versionName);
        fn_getDimensionFromRow(row).forEach((key) =>  {
            if (key.startsWith("[Location].[Location]") || key.startsWith("[Item Material].[Item Material]") || key.startsWith("[LED Rank].[LED Rank]")) {
                dimensions.push(vdUtil.fn_qDim(row, key));
            } else {
                dimensions.push(key);
            }
        });
        
        const measure = ["Measure.[Purchasing Proposal Alloc LED_Remained Qty]"];
        const result = vdCommon.selectList(dimensions, measure, "", "", "");
        if (result.cs.rowCount === 0) {
            return 0;
        }

        const remainedQty = result.cs.row(0).cell(result.cs.measureColumnIndex(result.columns.measure[0]));
        const selectQty = Number(row["Measure.[Purchasing Proposal Alloc LED_Select Qty]"]);
        const assignedQty = selectQty;

        vdCommon.debug(`remainedQty: ${remainedQty}, assignedQty: ${assignedQty}, selectQty: ${selectQty}`);        
        if (assignedQty < 0) {
            throw new Error("Out of stock. Please verify the quantity.");
        }
        return assignedQty;
    }

    var fn_updateAssignedQtyAll = function(row, versionName, qty) {
        const dimensions = [];
        dimensions.push(versionName);
        fn_getDimensionFromRow(row).forEach((key) =>  {
            if (key.startsWith("[Location].[Location]") || key.startsWith("[Item Material].[Item Material]") || key.startsWith("[LED Rank].[LED Rank]")) {
                dimensions.push(vdUtil.fn_qDim(row, key));
            } else {
                dimensions.push(key);
            }
        });
        
        const measures = [`Measure.[Purchasing Proposal Alloc LED_Remained Qty]="${qty}";`];

        vdCommon.updateMeasure(dimensions, measures);
    }

    var fn_validation = function(rows) {
        const ledQty = rows[0]["Measure.[Purchasing Proposal Alloc LED_LED Qty]"];
        let isInvalid = false;

        if (rows[0]["[Item Material].[C10]"].includes("R/G/B Pkg")) {
            const selectSum = fn_getSelectSum(rows);
            vdCommon.debug(`ledQty: ${ledQty}, selectSum: ${selectSum}`);

            isInvalid = selectSum < ledQty;
        } else {
            const redSelectSum = fn_getSelectSum(rows.filter(row => row["[Item Material].[C10]"] === "R"));
            const greenSelectSum = fn_getSelectSum(rows.filter(row => row["[Item Material].[C10]"] === "G"));
            const blueSelectSum = fn_getSelectSum(rows.filter(row => row["[Item Material].[C10]"] === "B"));
            vdCommon.debug(`ledQty: ${ledQty}, redSelectSum: ${redSelectSum}, greenSelectSum: ${greenSelectSum}, blueSelectSum: ${blueSelectSum}`);

            isInvalid = redSelectSum < ledQty || greenSelectSum < ledQty || blueSelectSum < ledQty;
        }

        if (isInvalid) {
            throw new Error("The total selected quantity must be equal to or greater than the required amount.");
        }
    }

    var fn_setIndoorLEDRank = function(rows, versionName) {
        vdCommon.debug("Case 5/6. Indoor LED");
        const notVpoRows = rows.filter(row => !row["[LED Rank].[LED Rank]"].startsWith("P_") && Number(row["Measure.[Purchasing Proposal Alloc LED_Select Qty]"]) > 0);
        let rank = "";
        let rankCase;

        if (notVpoRows.length > 1) {
            const baseRow = rows
              .filter((row) => Number(row["Measure.[Purchasing Proposal Alloc LED_Select Qty]"]) > 0 && !row["[LED Rank].[LED Rank]"].startsWith("P_"))
              .reduce((prev, cur) => Number(prev["Measure.[Purchasing Proposal Alloc LED_Select Qty]"]) > Number(cur["Measure.[Purchasing Proposal Alloc LED_Select Qty]"])
                  ? prev : cur);

            rank = `${baseRow["[LED Rank].[LED Rank]"].substring(0, 6)}${fn_currentWeek().slice(-3)}X`;
            rank = fn_isExistRank(baseRow, versionName, rank) ? fn_getNextRank(baseRow, versionName, rank) : rank;
            rankCase = 6;
        } else {
            rank = notVpoRows.length > 0 ? notVpoRows[0]["[LED Rank].[LED Rank]"] : "";
            rankCase = 5;
        }

        vdCommon.debug(`Mixed Rank: ${rank}, Set Rank: ${rank}`);
        rows.forEach(row => {
            row["Measure.[Purchasing Proposal Alloc LED_Mixed Rank]"] = Number(row["Measure.[Purchasing Proposal Alloc LED_Select Qty]"]) > 0 ? rank : "";
            row["Measure.[Purchasing Proposal Alloc LED_Set Rank]"] = Number(row["Measure.[Purchasing Proposal Alloc LED_Select Qty]"]) > 0 ? rank : "";
            row["Measure.[Purchasing Proposal Alloc LED_Mixed Rank Flag]"] = Number(row["Measure.[Purchasing Proposal Alloc LED_Select Qty]"]) > 0 ? rankCase : 0;
        });
    }

    var fn_setTheWallRank = function(rows, versionName) {
        const redElements = rows.filter(
          (row) => Number(row["Measure.[Purchasing Proposal Alloc LED_Select Qty]"]) > 0 && row["[Item Material].[C10]"] === "R"
        );
        const greenElements = rows.filter(
          (row) => Number(row["Measure.[Purchasing Proposal Alloc LED_Select Qty]"]) > 0 && row["[Item Material].[C10]"] === "G"
        );
        const blueElements = rows.filter(
          (row) => Number(row["Measure.[Purchasing Proposal Alloc LED_Select Qty]"]) > 0 && row["[Item Material].[C10]"] === "B"
        );

        // const isEmptyRank = rows.every(row => !row["Measure.[Purchasing Proposal Alloc LED_Mixed Rank]"] && !row["Measure.[Purchasing Proposal Alloc LED_Set Rank]"]);
        // const isChangedMixRank = rows.every(row =>
        //     !row["Measure.[Purchasing Proposal Alloc LED_Mixed Rank Flag]"] || Number(row["Measure.[Purchasing Proposal Alloc LED_Mixed Rank Flag]"]) < 3) &&
        //     !(redElements.length === 1 && greenElements.length === 1 && blueElements.length === 1);
        
        // vdCommon.debug(`isEmptyRank: ${isEmptyRank}, isChangedMixRank: ${isChangedMixRank}`);
        // if (isEmptyRank || isChangedMixRank) {
            fn_makeNewRank(rows, versionName, redElements, greenElements, blueElements);
        // } else {
        //     rows.filter(row => Number(row["Measure.[Purchasing Proposal Alloc LED_Select Qty]"]) === 0).forEach(row => {
        //         row["Measure.[Purchasing Proposal Alloc LED_Mixed Rank]"] = "";
        //         row["Measure.[Purchasing Proposal Alloc LED_Set Rank]"] = "";
        //         row["Measure.[Purchasing Proposal Alloc LED_Mixed Rank Flag]"] = 0;
        //     });
        // }
    }

    var fn_makeNewRank = function(rows, versionName, redElements, greenElements, blueElements) {
        const rankCase = fn_getCase([redElements, greenElements, blueElements]);
        const allElements = [redElements, greenElements, blueElements];
        const [refRed, refGreen, refBlue] = allElements.map(fn_getBaseRow);
        const isOnlyVpo = allElements.find(e => e.length === 1 && e[0]["[LED Rank].[LED Rank]"].startsWith("P_"));
        
        const mixedRankMap = {};
        let setRank = "";

        if (rankCase === 1) { // Case 1. R/G/B Rank 모두 동일
            vdCommon.debug("Case 1. R/G/B Rank 모두 동일");
            const baseRow = [refRed, refGreen, refBlue].find(e => !e["[LED Rank].[LED Rank]"].startsWith("P_"));

            mixedRankMap["R"] = baseRow ? baseRow["[LED Rank].[LED Rank]"] : "";
            mixedRankMap["G"] = baseRow ? baseRow["[LED Rank].[LED Rank]"] : "";
            mixedRankMap["B"] = baseRow ? baseRow["[LED Rank].[LED Rank]"] : "";

            setRank = baseRow ? baseRow["[LED Rank].[LED Rank]"] : "";
        } else if (rankCase === 2) { // Case 2. R/G/B Rank 상이
            vdCommon.debug("Case 2. R/G/B Rank 상이");
            [refRed, refGreen, refBlue].forEach(ref => mixedRankMap[ref["[Item Material].[C10]"]] = fn_replaceRankEmptyString(ref["[LED Rank].[LED Rank]"]));
          
            setRank = !isOnlyVpo ? `${refRed["[LED Rank].[LED Rank]"].substring(0, 7)}${refGreen["[LED Rank].[LED Rank]"].charAt(7)}${refBlue["[LED Rank].[LED Rank]"].charAt(8)}C` : "";
        } else { // Case 3/4. R/G/B Bin Mix
            vdCommon.debug("Case 3/4. R/G/B Bin Mix");
            const notVpoRedElem = redElements.filter(e => !e["[LED Rank].[LED Rank]"].startsWith("P_"));
            const notVpoGreenElem = greenElements.filter(e => !e["[LED Rank].[LED Rank]"].startsWith("P_"));
            const notVpoBlueElem = blueElements.filter(e => !e["[LED Rank].[LED Rank]"].startsWith("P_"));

            let redNewMixedRank = notVpoRedElem.length <= 1 ? fn_replaceRankEmptyString(refRed["[LED Rank].[LED Rank]"])
                : `${refRed["[LED Rank].[LED Rank]"].substring(0, 7)}00A`;
            redNewMixedRank = notVpoRedElem.length > 1 && fn_isExistRank(refRed, versionName, redNewMixedRank)
                ? fn_getNextRank(refRed, versionName, redNewMixedRank, false) : redNewMixedRank;
            let greenNewMixedRank = notVpoGreenElem.length <= 1 ? fn_replaceRankEmptyString(refGreen["[LED Rank].[LED Rank]"])
                : `${refGreen["[LED Rank].[LED Rank]"].substring(0, 6)}0${refGreen["[LED Rank].[LED Rank]"].charAt(7)}0A`;
            greenNewMixedRank = notVpoGreenElem.length > 1 && fn_isExistRank(refRed, versionName, greenNewMixedRank)
                ? fn_getNextRank(refRed, versionName, greenNewMixedRank, false) : greenNewMixedRank;
            let blueNewMixedRank = notVpoBlueElem.length <= 1 ? fn_replaceRankEmptyString(refBlue["[LED Rank].[LED Rank]"])
                : `${refBlue["[LED Rank].[LED Rank]"].substring(0, 6)}00${refBlue["[LED Rank].[LED Rank]"].charAt(8)}A`;
            blueNewMixedRank = notVpoBlueElem.length > 1 && fn_isExistRank(refRed, versionName, blueNewMixedRank)
                ? fn_getNextRank(refRed, versionName, blueNewMixedRank, false) : blueNewMixedRank;

            mixedRankMap["R"] = redNewMixedRank;
            mixedRankMap["G"] = greenNewMixedRank;
            mixedRankMap["B"] = blueNewMixedRank;
            
            if (!isOnlyVpo) {
                setRank = `${refRed["[LED Rank].[LED Rank]"].substring(0, 3)}AAA${refRed["[LED Rank].[LED Rank]"].charAt(6)}${refGreen["[LED Rank].[LED Rank]"].charAt(7)}${refBlue["[LED Rank].[LED Rank]"].charAt(8)}X`;
                setRank = fn_isExistRank(refRed, versionName, setRank, false) ? fn_getNextRank(refRed, versionName, setRank, false, false) : setRank;
            }
        }

        vdCommon.debug(`Mixed Rank: ${JSON.stringify(mixedRankMap)}, Set Rank: ${setRank}`);
        rows.forEach((row) => {
            row["Measure.[Purchasing Proposal Alloc LED_Mixed Rank]"] = Number(row["Measure.[Purchasing Proposal Alloc LED_Select Qty]"]) > 0 ? mixedRankMap[row["[Item Material].[C10]"]] : "";
            row["Measure.[Purchasing Proposal Alloc LED_Set Rank]"] = Number(row["Measure.[Purchasing Proposal Alloc LED_Select Qty]"]) > 0 ? setRank : "";
            row["Measure.[Purchasing Proposal Alloc LED_Mixed Rank Flag]"] = Number(row["Measure.[Purchasing Proposal Alloc LED_Select Qty]"]) > 0 ? rankCase : 0;
        });
    }

    var fn_getCase = function(rows) {
        const notVpoRows = rows.map(row => row.filter(item => !item["[LED Rank].[LED Rank]"].startsWith("P_") && Number(item["Measure.[Purchasing Proposal Alloc LED_Select Qty]"]) > 0));
        const validRow = notVpoRows.filter(row => row?.length > 0);
        const ranks = validRow.flatMap(row => row.map(item => item["[LED Rank].[LED Rank]"]));
        const baseRank = ranks.find(rank => !rank.startsWith("P_"));
        const isAllSameRank = ranks.every(rank => rank.startsWith("P_") || rank === baseRank);
        const isAllLen1 = validRow.every(row => row.length === 1);
        const isAllNotLen1 = validRow.every(row => row.length !== 1);

        if (isAllSameRank) return 1;
        if (isAllLen1) return 2;
        if (isAllNotLen1) return 3;
        return 4;
    }

    var fn_getBaseRow = function(row) {
      const notVpoRows = row.filter(item => !item["[LED Rank].[LED Rank]"].startsWith("P_"));
      return notVpoRows.length === 0
        ? row[0]
        : notVpoRows.reduce((max, cur) =>
            Number(cur["Measure.[Purchasing Proposal Alloc LED_Select Qty]"]) >
            Number(max["Measure.[Purchasing Proposal Alloc LED_Select Qty]"])
              ? cur
              : max
          );
    }

    var fn_replaceRankEmptyString = (rank) => rank.startsWith("P_") ? "" : rank;

    var fn_isExistRank = function(row, versionName, rank, isMixedRank = true) {
        const dimensions = [];
        dimensions.push(versionName);
        dimensions.push(...fn_getDimensionFromRow(row));

        const rankMeasure = `Measure.[Purchasing Proposal Alloc LED_${isMixedRank ? "Mixed" : "Set"} Rank]`;
        const where = `where {${rankMeasure} == "${rank}"}`;
        return vdCommon.existMeasure(dimensions, [rankMeasure], where);
    }

    var fn_getLastRank = function(row, versionName, rank, isMixedRank = true) {
        const dimensions = [];
        dimensions.push(versionName);
        dimensions.push(...fn_getDimensionFromRow(row));
        
        const rankMeasure = `Measure.[Purchasing Proposal Alloc LED_${isMixedRank ? "Mixed" : "Set"} Rank]`;
        const where = isMixedRank ? `where {${rankMeasure} contains "${rank.slice(0, -1)}"}`
            : `where {${rankMeasure} startswith [${rank.substring(0, 3)}] && ${rankMeasure} endswith [${rank.slice(-4)}]}`;
        const orderby = `orderby ${rankMeasure} desc`;
        const limit = "limit 1";
        const result = vdCommon.selectList(dimensions, [rankMeasure], where, orderby, limit);
        const lastRank = result.cs.row(0).cell(result.cs.measureColumnIndex(result.columns.measure[0]));
        
        return lastRank;
    }

    var fn_getNextRank = function(row, versionName, newRank, isIndoor = true, isMixedRank = true) {
        const lastRank = fn_getLastRank(row, versionName, newRank, isMixedRank);
        let nextRank = "";

        if (isIndoor) { // X > Y > Z > A > B > C ...
            const nextRankChar = String.fromCharCode((lastRank.slice(-1).charCodeAt(0) - 65 + 1) % 26 + 65);
            nextRank = `${newRank.slice(0, -1)}${nextRankChar}`;
        } else {
            if (isMixedRank) { // A > B > C > D
                const nextRankChar = String.fromCharCode(lastRank.slice(-1).charCodeAt(0) + 1);
                nextRank = `${newRank.slice(0, -1)}${nextRankChar}`;
                if (nextRankChar === 'E') {
                    throw new Error(`MixedRank ( ${nextRank} ) is error.`);
                }
            } else { // AAA > AAB > AAC > ... > ZZZ
                const nextRankStr = (s) => s.replace(/([^Z])Z*$/, (m, p) => String.fromCharCode(p.charCodeAt(0) + 1) + 'A'.repeat(m.length - 1));
                nextRank = `${newRank.substring(0, 3)}${nextRankStr(lastRank.substring(3, 6))}${newRank.slice(-4)}`;
            }
        }

        vdCommon.debug(`lastRank: ${lastRank}, nextRank: ${nextRank}`);
        return nextRank;
    }

    const functionMap = {
        "fn_save" : fn_save
    };

    return {
        fn_loadFunction : fn_loadFunction
    };    
});