define('o9.NSCM.JSEWCOSiteDetail', ['o9/data/query', 'o9/data/cellset', 'o9.NSCM.commonLib', 'o9.NSCM.JSEWCommonCO'], function() {	
    /*-------------------------------------------------------------------------------------------------------*/
    // 프로그램명 : o9.NSCM.JSEWCOSiteDetail
    // Action Button : EWCOSiteDetail
    // 화면명 : Site Detail
    // 2025.12.11 최초 생성                                                                         / gs9.kim */
    // 2026.02.03 그레인 변경으로 [Product Group].[Product Group] > [Item].[Product Group] 수정      / gs9.kim */
    // 2026.03.05 쿼리 오류 수정                                                                     / gs9.kim */
    // 2026.03.26 DA 이관으로 인한 쿼리 수정                                                         / gs9.kim */
    /*-------------------------------------------------------------------------------------------------------*/

    const programName = "o9.NSCM.JSEWCOSiteDetail";
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

    var fn_getDimension = function(row, versionName) {
      const dimensions = [];
      dimensions.push(versionName);
      Object.keys(row)
        .filter(
          (key) =>
            key.startsWith("[Item].[Product Group]") ||
            key.startsWith("[Location].[Location]") ||
            key.startsWith("[Sub Location].[Sub Location]") ||
            key.startsWith("[ERP Sold to].[ERP Sold to ID]") ||
            key.startsWith("[ERP Ship to].[ERP Ship to ID]")
        )
        .forEach((key) => {
          if (key.startsWith("[Item].[Product Group]")) {
            dimensions.push(coUtil.fn_qDim(row, key));
          } else if (key.startsWith("[Location].[Location]") || key.startsWith("[Sub Location].[Sub Location]")) {
            dimensions.push(`${key}.filter(#.[${key.includes("Sub") ? "Sub " : ""}Location ${key.includes("Sub") ? "" : "Site "}ID]  == "${row[`${key}`]}")`);
          } else {
            dimensions.push(coUtil.fn_qDimWithDN(row, key));
          }
        });
      return dimensions;
    };

    var fn_validation = function(parsedParams, versionName) {
        const errorMsg = "The data has already been registered.";
        const measures = Object.keys(parsedParams.fbGridRows[0]).filter(key => key.startsWith("Measure"));
        const cRows = parsedParams.fbGridRows.filter(row => row["rowstatus"] == "C");
        cRows.forEach(row => {
            const dimensions = fn_getDimension(row, versionName);
            const where = 'WHERE { Measure.[Site Detail_Delete Flag] == "N" }';

            if (coCommon.existMeasure(dimensions, measures, where)) {
                throw new Error(errorMsg);
            }
        });
    };

    /*
    {	"fbFuncName":"fn_Save",
        "fbParams":{ "[Version].[Version Name]":"CurrentWorkingView" },
        "fbGridRows":[
        {
            "rowstatus":"C",
            "rowindex":1,
            "[Item].[Product Group]":"LAUNDRY",
            "[Sub Location].[Sub Location]":"P509",
            "[Location].[Location]":"S501WC05",
            "[ERP Sold to].[ERP Sold to ID]":"C1T0_0001253519",
            "[ERP Ship to].[ERP Ship to ID]":"C1E0_0006149861",
            "Measure.[Site Detail_Priority]":"1",
            "Measure.[Site Detail_Status]":"CON"
        }]
    }
    */
    var fn_insert = function(row, versionName) {
        coCommon.debug("insert row: " + JSON.stringify(row));

        const dimensions = fn_getDimension(row, versionName);

        const measures = [];
        Object.keys(row).filter(key => key.startsWith("Measure.")).forEach(key => measures.push(coUtil.fn_qMeaStr(row, key)));
        measures.push('Measure.[Site Detail_Delete Flag]="N";');
        measures.push(coUtil.fn_qMeaUpdateTime("Measure.[Site Detail_Creation time]"));
        measures.push(`Measure.[Site Detail_Created by]=CurrentUser().[User Name];`);

        coCommon.createMeasure(dimensions, measures);
    }
	
    var fn_update = function(row, versionName) {
        coCommon.debug("update row: " + JSON.stringify(row));

        const dimensions = fn_getDimension(row, versionName);

        const measures = [];
        Object.keys(row).filter(key => key.startsWith("Measure.")).forEach(key => measures.push(coUtil.fn_qMeaStr(row, key)));

        measures.push(coUtil.fn_qMeaUpdateTime('Measure.[Site Detail_Update time]'));
        measures.push('Measure.[Site Detail_Updated by]=CurrentUser().[User Name];');

        coCommon.updateMeasure(dimensions, measures);
    }

    var fn_delete = function(row, versionName) {
        coCommon.debug("delete row: " + JSON.stringify(row));

        const dimensions = fn_getDimension(row, versionName);
        
        const measures = [];
        measures.push('Measure.[Site Detail_Delete Flag]="Y";');
        measures.push(coUtil.fn_qMeaUpdateTime('Measure.[Site Detail_Update time]'));
        measures.push('Measure.[Site Detail_Updated by]=CurrentUser().[User Name];');

        coCommon.updateMeasure(dimensions, measures);
    }

    const functionMap = {
        "fn_Save" : fn_save
    };

    return {
        fn_loadFunction : fn_loadFunction
    };    
});