define('o9.NSCM.JSEWCOSopFixedPeriod', ['o9/data/query', 'o9/data/cellset', 'o9.NSCM.commonLib', 'o9.NSCM.JSEWCommonCO'], function() {	
    /*--------------------------------------------------------------------------------------------------*/
    // 프로그램명 : o9.NSCM.JSEWCOSopFixedPeriod
    // Action Button : EWCOSopFixedPeriod
    // 화면명 : Fixed Period
    // 2025.12.09 최초 생성                 / gs9.kim */
    /*--------------------------------------------------------------------------------------------------*/

    const programName = "o9.NSCM.JSEWCOSopFixedPeriod";
	const commonLib = require('o9.NSCM.commonLibCO');
    const coUtil = new commonLib.COUtil();
    const coCommon = new commonLib.COCommon(programName + "." + arguments.callee.name);
	
    var fn_loadFunction = function(o9Params) {
		try {
            coCommon.setLogLevel("Debug");
            coCommon.printParams(o9Params);

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
            coCommon.programEnd();
        }
	};

    var fn_save = function(parsedParams) {
        coCommon.debug("parsedParams :: " + JSON.stringify(parsedParams));

		try {
            const versionName = coUtil.fn_qDimVersionName(parsedParams);

            // Validation 체크
            fn_validation(parsedParams, versionName);
            
            parsedParams.fbGridRows.forEach(row => {
                const rowstatus = row["rowstatus"];

                if (rowstatus == "C") {
                    fn_insert(row, versionName);
                } else if (rowstatus == "U") {
                    fn_update(row, versionName);
                } else if (rowstatus == "D") {
                    fn_delete(row, versionName);
                }
            });

            return { "Code" : 0, "Msg" : "It was saved successfully." };
        } catch ( e ) {
            coCommon.error(e.message);
            return { "Code" : -1, "Msg" : e.message };
        }
    };

    var fn_validation = function(parsedParams, versionName) {
        const errorMsg = "The data has already been registered.";
        const measures = Object.keys(parsedParams.fbGridRows[0]).filter(key => key.startsWith("Measure") && (key.includes("Fixed Group") || key.includes("Fixed Week")));
        const cRows = parsedParams.fbGridRows.filter(row => row["rowstatus"] == "C" || row["rowstatus"] == "U");
        cRows.forEach(row => {
            const dimensions = [];
            dimensions.push(versionName);
            dimensions.push(coUtil.fn_qDim(row, "[Time].[Week]"));
            dimensions.push('[Seq].[Seq]');

            const where = `WHERE { Measure.[SOP Fixed Period_Fixed Group] == "${row["Measure.[SOP Fixed Period_Fixed Group]"]}"`
                + `, Measure.[SOP Fixed Period_Fixed Week] == "${row["Measure.[SOP Fixed Period_Fixed Week]"]}"`
                + ', Measure.[SOP Fixed Period_Delete Flag] == "N" }';
            
            if (coCommon.existMeasure(dimensions, measures, where)) {
                throw new Error(errorMsg);
            }
        });
    };

    /*
    { "fbFuncName" : "fn_Save", "fbParams" : { "[Version].[Version Name]" : "CurrentWorkingView" },
        "fbGridRows" : [
        {
            "rowstatus":"C",
            "rowindex":"1",
            "[Time].[Week]":"202532",
			"[Seq].[Seq]":"1",
			"Measure.[SOP Fixed Period_Fixed Group]":"1 MONTH",
			"Measure.[SOP Fixed Period_Fixed Week]":"202534",
			"Measure.[SOP Fixed Period_Valid Flag]":"Y"
        }]
    }
    */
    var fn_insert = function(row, versionName) {
        coCommon.debug("insert row: " + JSON.stringify(row));

        const dimensions = [];
        dimensions.push(versionName);
        Object.keys(row).filter(key => key.startsWith("[Time].[Week]")).forEach(key => dimensions.push(coUtil.fn_qDim(row, key)));
        dimensions.push(`[Seq].[Seq].[${fn_getSeq(versionName)}]`);

        const measures = [];
        Object.keys(row).filter(key => key.startsWith("Measure.")).forEach(key => measures.push(coUtil.fn_qMeaStr(row, key)));
        measures.push('Measure.[SOP Fixed Period_Delete Flag]="N";');
        measures.push(coUtil.fn_qMeaUpdateTime("Measure.[SOP Fixed Period_Creation time]"));
        measures.push(`Measure.[SOP Fixed Period_Created by]=CurrentUser().[User Name];`);

        coCommon.createMeasure(dimensions, measures);
    }
	
    var fn_update = function(row, versionName) {
        coCommon.debug("update row: " + JSON.stringify(row));

        const dimensions = [];
        dimensions.push(versionName);
        Object.keys(row).filter(key => key.startsWith("[Time].[Week]") || key.startsWith("[Seq].[Seq]")).forEach(key => dimensions.push(coUtil.fn_qDim(row, key)));
        
        const measures = [];
        Object.keys(row).filter(key => key.startsWith("Measure.")).forEach(key => measures.push(coUtil.fn_qMeaStr(row, key)));

        measures.push(coUtil.fn_qMeaUpdateTime('Measure.[SOP Fixed Period_Update time]'));
        measures.push('Measure.[SOP Fixed Period_Updated by]=CurrentUser().[User Name];');

        coCommon.updateMeasure(dimensions, measures);
    }

    var fn_delete = function(row, versionName) {
        coCommon.debug("delete row: " + JSON.stringify(row));

        const dimensions = [];
        dimensions.push(versionName);
        Object.keys(row).filter(key => key.startsWith("[Time].[Week]") || key.startsWith("[Seq].[Seq]")).forEach(key => dimensions.push(coUtil.fn_qDim(row, key)));

        const measures = [];
        measures.push('Measure.[SOP Fixed Period_Delete Flag]="Y";');
        measures.push(coUtil.fn_qMeaUpdateTime('Measure.[SOP Fixed Period_Update time]'));
        measures.push('Measure.[SOP Fixed Period_Updated by]=CurrentUser().[User Name];');

        coCommon.updateMeasure(dimensions, measures);
    }

    var fn_getSeq = function(versionName) {
        const dimensions = [];
        dimensions.push(versionName);
        dimensions.push('[Seq].[Seq]');

        const where = 'where { Measure.[SOP Fixed Period_Delete Flag]=="N" }';
        const orderby = 'orderby [Seq].[Seq].Key desc';
        const limit = 'limit 1';

        const result = coCommon.selectList(dimensions, [], where, orderby, limit);

        let seq;
        const dimension = result.columns.dimension;
        for (let i = 0; i < dimension.length; i++) {
            if (dimension[i] === "Seq.Seq") {
                seq = result.cs.row(0).cell(result.cs.memberColumnIndex(dimension[i].split(".")[0], dimension[i].split(".")[1])).Name;
            }
        }
        coCommon.debug(`seq : ${seq}`);

        return Number(seq) + 1;
    }

    const functionMap = {
        "fn_Save" : fn_save
    };

    return {
        fn_loadFunction : fn_loadFunction
    };    
});