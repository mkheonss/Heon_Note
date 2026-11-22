define('o9.NSCM.JSEWItemSearch', ['o9/data/query', 'o9/data/cellset', 'o9.NSCM.commonLib'], function () {
	const programName = "o9.NSCM.JSEWItemSearch";
    const commonLib = require('o9.NSCM.commonLib');
    const vdUtil = new commonLib.VdUtil();

    // Log 를 위해서 선언
    const commonLog = new commonLib.VdCommon(programName + ".Log");
    commonLog.setLogLevel("Debug");

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
            if ( parsedParams.fbParams["includeField"] == undefined ) {
                parsedParams.fbParams["includeField"] = "";
            }
            // 조회시 기본 limit 지정( 3000개 )
            if ( parsedParams.fbParams["limit"] == undefined ) {
                parsedParams.fbParams["limit"] = "limit 40000";
            } else if ( parsedParams.fbParams["limit"] == -1 ) {
                parsedParams.fbParams["limit"] = "";
            } else {
                parsedParams.fbParams["limit"] = "limit " + parsedParams.fbParams.limit;
            }
            // filters 조건 추가
            if ( parsedParams.fbParams["filters"] == undefined ) {
                parsedParams.fbParams["filters"] = {};
            }

            var rtn = functionMap[fbFuncName](parsedParams);

            vdCommon.programEnd();
            return rtn;
        } catch ( e ) {
            vdCommon.error(e.message);
            return { "Code" : -1, "Msg" : e.message };
        }
	};

/************************************************* combo logic *************************************************/

    // { "fbFuncName" : "fn_setItem", "fbParams" : { "[Item].[Product Group]" : "TV", "[Item].[Definition]" : "ACCESSORY", "[Item].[Item]" : "PSN42%" } }
    var fn_setItem = function(parsedParams){
        const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
        vdCommon.setLogLevel("Debug");

		try {
		    var dims = ['&SETItem' + vdUtil.fn_filterStr(vdUtil.fn_getParam(parsedParams, "[Item].[Item]"))];

            // filter를 적용할 Dimension 설정
            if ( parsedParams.fbParams["filterDimension"] == undefined ) {
                parsedParams.fbParams["filterDimension"] = ["[Item]"];
            }

            parsedParams.fbParams.includeField = "Item:Product Group:ProductGroup";
            parsedParams.fbParams.includeField += ",Item:Project:Project";
            parsedParams.fbParams.includeField += ",Item:Definition:Definition";
            parsedParams.fbParams.includeField += ",Item:Marketing Name:MarketingName";
            parsedParams.fbParams.includeField += ",Item:Inch:Inch";
            parsedParams.fbParams.includeField += ",Item:Year:Year";

		    // Casecade 를 위해서 Dimension 추가
		    dims = fn_addIncludeField(dims, parsedParams);

            var comboList = [];
            var name = "";
            var displayName = "";
            var result = vdCommon.selectList(dims, [], fn_makeWhere(parsedParams), "orderby Item.Item.DisplayName", parsedParams.fbParams.limit);
            for ( var i = 0; i < result.cs.rowCount; i++ ) {
                var row = { "[Item].[Item]" : result.cs.row(i).cell(result.cs.memberColumnIndex("Item", "Item")).Name };

                // includeField 반영
                var includeField = parsedParams.fbParams.includeField.split(",");
                for ( var m = 0; m < includeField.length; m++ ) {
                    var tSplit = includeField[m].split(":");
                    row["[" + tSplit[0] + "].[" + tSplit[1] + "]"] = result.cs.row(i).cell(result.cs.memberColumnIndex(tSplit[0], tSplit[1])).Name;
                }

                comboList.push(row);
            }
            vdCommon.debug("ComboData : " + JSON.stringify(comboList.slice(0,3)));

            vdCommon.programEnd();

            return { "Code" : 0, "Msg" : "", "Rows" : comboList };
        } catch ( e ) {
            vdCommon.error(e.message);
            return { "Code" : -1, "Msg" : e.message };
        }
    };

    /*
        { "fbFuncName" : "fn_setBodItem", "fbParams" : { "[Item].[Product Group]" : "TV", "[Item].[Definition]" : "ACCESSORY", "[Item].[Item]" : "CY-AU55%" } }

        { "fbFuncName" : "fn_setBodItem"
            ,"fbParams" : {
                "[Item].[Product Group]" : "TV"
                ,"[Item].[Definition]" : "ACCESSORY"
                ,"[Item].[Item]" : "CY%"
                ,"[Location].[Location]" : "P401"
                ,"[Sub Location].[Sub Location]" : "S751"
                ,"filters" : {
                    "[Item].[Item Std1]":{"SelectedMembers":["TV","MONITOR"],"MemberFilter":""}
                }
            }
        }


    */
    var fn_setBodItem = function(parsedParams){
        const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
        vdCommon.setLogLevel("Debug");

		try {
		    var dims = ['&SETItem' + vdUtil.fn_filterStr(vdUtil.fn_getParam(parsedParams, "[Item].[Item]"))];

            // filter를 적용할 Dimension 설정
            if ( parsedParams.fbParams["filterDimension"] == undefined ) {
                parsedParams.fbParams["filterDimension"] = ["[Item]"];
            }

            parsedParams.fbParams.includeField = "Item:Product Group:ProductGroup";
            parsedParams.fbParams.includeField += ",Item:Project:Project";
            parsedParams.fbParams.includeField += ",Item:Definition:Definition";
            parsedParams.fbParams.includeField += ",Item:Marketing Name:MarketingName";
            parsedParams.fbParams.includeField += ",Item:Inch:Inch";
            parsedParams.fbParams.includeField += ",Item:Year:Year";

		    // Casecade 를 위해서 Dimension 추가
		    dims = fn_addIncludeField(dims, parsedParams);

            var where = [];
            where.push('&CWVUI');
            where.push('Measure.[BOD List_BOD Valid] == "Y"');
            where.push('Measure.[BOD Item_Asn] == 1');
            where.push('coalesce(Measure.[BOD Item_Eff Startdate],DATEADD(Now(),-1,"Day")) < now()');
            where.push('coalesce(Measure.[BOD Item_Eff Enddate],DATEADD(Now(),1,"Day")) > now()');
            where.push('[Location].[Location]' + vdUtil.fn_filterStr(vdUtil.fn_getParam(parsedParams, "[Location].[Location]")));
            where.push('[Sub Location].[Sub Location]' + vdUtil.fn_filterStr(vdUtil.fn_getParam(parsedParams, "[Sub Location].[Sub Location]")));

            var comboList = [];
            var name = "";
            var displayName = "";
            var result = vdCommon.selectList(dims, ["Measure.[BOD Item_Asn]"], fn_makeWhere(parsedParams, where), "orderby Item.Item.DisplayName", parsedParams.fbParams.limit);
            for ( var i = 0; i < result.cs.rowCount; i++ ) {
                var row = { "[Item].[Item]" : result.cs.row(i).cell(result.cs.memberColumnIndex("Item", "Item")).Name };

                // includeField 반영
                var includeField = parsedParams.fbParams.includeField.split(",");
                for ( var m = 0; m < includeField.length; m++ ) {
                    var tSplit = includeField[m].split(":");
                    row["[" + tSplit[0] + "].[" + tSplit[1] + "]"] = result.cs.row(i).cell(result.cs.memberColumnIndex(tSplit[0], tSplit[1])).Name;
                }

                comboList.push(row);
            }
            vdCommon.debug("ComboData : " + JSON.stringify(comboList.slice(0,3)));

            vdCommon.programEnd();

            return { "Code" : 0, "Msg" : "", "Rows" : comboList };
        } catch ( e ) {
            vdCommon.error(e.message);
            return { "Code" : -1, "Msg" : e.message };
        }
    };

    // { "fbFuncName" : "fn_lcmItem", "fbParams" : { "[Item].[Product Group]" : "LCD", "[Item].[Definition]" : "ACCESSORY", "[Item].[Item]" : "CY-AD07%" } }
    var fn_lcmItem = function(parsedParams){
        const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
        vdCommon.setLogLevel("Debug");

		try {
		    var dims = ['&LCMItem' + vdUtil.fn_filterStr(vdUtil.fn_getParam(parsedParams, "[Item].[Item]"))];

            // filter를 적용할 Dimension 설정
            if ( parsedParams.fbParams["filterDimension"] == undefined ) {
                parsedParams.fbParams["filterDimension"] = ["[Item]"];
            }

            parsedParams.fbParams.includeField = "Item:Product Group:ProductGroup";
            parsedParams.fbParams.includeField += ",Item:Series:Series";
            parsedParams.fbParams.includeField += ",Item:Definition:Definition";
            parsedParams.fbParams.includeField += ",Item:Strategy:Strategy";
            parsedParams.fbParams.includeField += ",Item:Hz:Hz";
            parsedParams.fbParams.includeField += ",Item:Inch:Inch";
            parsedParams.fbParams.includeField += ",Item:Year:Year";
            parsedParams.fbParams.includeField += ",Item:Open Cell:OpenCell";

		    // Casecade 를 위해서 Dimension 추가
		    dims = fn_addIncludeField(dims, parsedParams);

            var comboList = [];
            var name = "";
            var displayName = "";
            var result = vdCommon.selectList(dims, [], fn_makeWhere(parsedParams), "orderby Item.Item.DisplayName", parsedParams.fbParams.limit);
            for ( var i = 0; i < result.cs.rowCount; i++ ) {
                var row = { "[Item].[Item]" : result.cs.row(i).cell(result.cs.memberColumnIndex("Item", "Item")).Name };

                // includeField 반영
                var includeField = parsedParams.fbParams.includeField.split(",");
                for ( var m = 0; m < includeField.length; m++ ) {
                    var tSplit = includeField[m].split(":");
                    row["[" + tSplit[0] + "].[" + tSplit[1] + "]"] = result.cs.row(i).cell(result.cs.memberColumnIndex(tSplit[0], tSplit[1])).Name;
                }

                comboList.push(row);
            }
            vdCommon.debug("ComboData : " + JSON.stringify(comboList.slice(0,3)));

            vdCommon.programEnd();

            return { "Code" : 0, "Msg" : "", "Rows" : comboList };
        } catch ( e ) {
            vdCommon.error(e.message);
            return { "Code" : -1, "Msg" : e.message };
        }
    };

    /*
        { "fbFuncName" : "fn_lcmBodItem", "fbParams" : { "[Location].[Location]" : "P105", "[Sub Location].[Sub Location]" : "P406", "[Item].[Product Group]" : "LCD" } }
        { "fbFuncName" : "fn_lcmBodItem", "fbParams" : { "[Location].[Location]" : "P105", "[Sub Location].[Sub Location]" : "P406", "[Item].[Product Group]" : "LCD", "[Item].[Definition]" : "HD", "[Item].[Item]" : "BN95-%" } }
        { "fbFuncName" : "fn_lcmBodItem", "fbParams" : { "[Location].[Location]" : "P105", "[Sub Location].[Sub Location]" : "P406", "[Item].[Product Group]" : "LCD", "[Item].[Definition]" : "HD", "[Item].[Strategy]" : "Y18 SDC%" } }
    */
    var fn_lcmBodItem = function(parsedParams){
        const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
        vdCommon.setLogLevel("Debug");

		try {
		    var dims = ['&LCMItem' + vdUtil.fn_filterStr(vdUtil.fn_getParam(parsedParams, "[Item].[Item]"))];

            // filter를 적용할 Dimension 설정
            if ( parsedParams.fbParams["filterDimension"] == undefined ) {
                parsedParams.fbParams["filterDimension"] = ["[Item]"];
            }

		    parsedParams.fbParams.includeField = "Item:Product Group:ProductGroup";
            parsedParams.fbParams.includeField += ",Item:Series:Series";
            parsedParams.fbParams.includeField += ",Item:Definition:Definition";
            parsedParams.fbParams.includeField += ",Item:Strategy:Strategy";
            parsedParams.fbParams.includeField += ",Item:Hz:Hz";
            parsedParams.fbParams.includeField += ",Item:Inch:Inch";
            parsedParams.fbParams.includeField += ",Item:Year:Year";
            parsedParams.fbParams.includeField += ",Item:Open Cell:OpenCell";

		    // Casecade 를 위해서 Dimension 추가
		    dims = fn_addIncludeField(dims, parsedParams);

            var where = [];
            where.push('&CWVUI');
            where.push('Measure.[BOD List_BOD Valid] == "Y"');
            where.push('Measure.[BOD Item_Asn] == 1');
            where.push('coalesce(Measure.[BOD Item_Eff Startdate],DATEADD(Now(),-1,"Day")) < now()');
            where.push('coalesce(Measure.[BOD Item_Eff Enddate],DATEADD(Now(),1,"Day")) > now()');
            where.push('[Location].[Location]' + vdUtil.fn_filterStr(vdUtil.fn_getParam(parsedParams, "[Location].[Location]")));
            where.push('[Sub Location].[Sub Location]' + vdUtil.fn_filterStr(vdUtil.fn_getParam(parsedParams, "[Sub Location].[Sub Location]")));

            var comboList = [];
            var name = "";
            var displayName = "";
            var result = vdCommon.selectList(dims, ["Measure.[BOD Item_Asn]"], fn_makeWhere(parsedParams, where), "orderby Item.Item.DisplayName", parsedParams.fbParams.limit);
            for ( var i = 0; i < result.cs.rowCount; i++ ) {
                var row = { "[Item].[Item]" : result.cs.row(i).cell(result.cs.memberColumnIndex("Item", "Item")).Name };

                // includeField 반영
                var includeField = parsedParams.fbParams.includeField.split(",");
                for ( var m = 0; m < includeField.length; m++ ) {
                    var tSplit = includeField[m].split(":");
                    row["[" + tSplit[0] + "].[" + tSplit[1] + "]"] = result.cs.row(i).cell(result.cs.memberColumnIndex(tSplit[0], tSplit[1])).Name;
                }

                comboList.push(row);
            }
            vdCommon.debug("ComboData : " + JSON.stringify(comboList.slice(0,3)));

            vdCommon.programEnd();

            return { "Code" : 0, "Msg" : "", "Rows" : comboList };
        } catch ( e ) {
            vdCommon.error(e.message);
            return { "Code" : -1, "Msg" : e.message };
        }
    };

    /*
        { "fbFuncName" : "fn_lcmMappingItem", "fbParams" : { "[Location].[Location]" : "P413", "[Sub Location].[Sub Location]" : "P901SVC", "[Item].[Product Group]" : "LCD" } }
    */
    var fn_lcmMappingItem = function(parsedParams){
        const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
        vdCommon.setLogLevel("Debug");

		try {
		    var dims = ['&LCMItem' + vdUtil.fn_filterStr(vdUtil.fn_getParam(parsedParams, "[Item].[Item]"))];

            // filter를 적용할 Dimension 설정
            if ( parsedParams.fbParams["filterDimension"] == undefined ) {
                parsedParams.fbParams["filterDimension"] = ["[Item]"];
            }

		    parsedParams.fbParams.includeField = "Location:Location:Location";
		    parsedParams.fbParams.includeField += ",Sub Location:Sub Location:SubLocation";
		    parsedParams.fbParams.includeField += ",Item:Product Group:ProductGroup";
            parsedParams.fbParams.includeField += ",Item:Series:Series";
            parsedParams.fbParams.includeField += ",Item:Definition:Definition";
            parsedParams.fbParams.includeField += ",Item:Strategy:Strategy";
            parsedParams.fbParams.includeField += ",Item:Hz:Hz";
            parsedParams.fbParams.includeField += ",Item:Inch:Inch";
            parsedParams.fbParams.includeField += ",Item:Year:Year";
            parsedParams.fbParams.includeField += ",Item:Open Cell:OpenCell";

		    // Casecade 를 위해서 Dimension 추가
		    dims = fn_addIncludeField(dims, parsedParams);

            var where = [];
            where.push('&CWVUI');
            where.push('Measure.[Code Map LCM_Valid Flag] == "Y"');

            var comboList = [];
            var name = "";
            var displayName = "";
            var result = vdCommon.selectList(dims, ["Measure.[Code Map LCM_Prod Item]"], fn_makeWhere(parsedParams, where), "orderby Item.Item.DisplayName", parsedParams.fbParams.limit);
            for ( var i = 0; i < result.cs.rowCount; i++ ) {
                var row = { "[Item].[Item]" : result.cs.row(i).cell(result.cs.memberColumnIndex("Item", "Item")).Name
                            ,"Measure.[Code Map LCM_Prod Item]" : result.cs.row(i).cell(result.cs.measureColumnIndex("Code Map LCM_Prod Item")) };

                // includeField 반영
                var includeField = parsedParams.fbParams.includeField.split(",");
                for ( var m = 0; m < includeField.length; m++ ) {
                    var tSplit = includeField[m].split(":");
                    row["[" + tSplit[0] + "].[" + tSplit[1] + "]"] = result.cs.row(i).cell(result.cs.memberColumnIndex(tSplit[0], tSplit[1])).Name;
                }

                comboList.push(row);
            }
            vdCommon.debug("ComboData : " + JSON.stringify(comboList.slice(0,3)));

            vdCommon.programEnd();

            return { "Code" : 0, "Msg" : "", "Rows" : comboList };
        } catch ( e ) {
            vdCommon.error(e.message);
            return { "Code" : -1, "Msg" : e.message };
        }
    };

/************************************************* util logic *************************************************/
    // Dimension 에 includeField의 정보를 추가한다.
    var fn_addIncludeField = function(dims, parsedParams){
        if ( parsedParams.fbParams["includeField"] != "" ) {
            // 필터에 where 에서 뺄 대상을 추가할 배열
            parsedParams.fbParams["filterExistGrain"] = [];

            var includeField = parsedParams.fbParams.includeField.split(",");
            for ( var i = 0; i < includeField.length; i++ ) {
                var tSplit = includeField[i].split(":");

                // 2025-11-24 : attribute 에 attribute^property 형태로 넣은 경우 로직 추가
                var attrSplit = tSplit[1].split("^");

                if ( parsedParams.fbParams["filters"] != undefined &&
                        parsedParams.fbParams["filterDimension"] != undefined &&
                        parsedParams.fbParams["filterDimension"].length > 0 &&
                        parsedParams.fbParams.filters["[" + tSplit[0] + "].[" + attrSplit[0] + "]"] != undefined ) {
                    // 필터를 반영한 로직
                    var filter = vdUtil.fn_getFilterQuery(parsedParams, "[" + tSplit[0] + "].[" + attrSplit[0] + "]");

                    // 파라미터를 반영
                    if ( parsedParams.fbParams["[" + tSplit[0] + "].[" + attrSplit[0] + "]"] != undefined ) {
                        filter += vdUtil.fn_filterStr(parsedParams.fbParams["[" + tSplit[0] + "].[" + attrSplit[0] + "]"]);
                    }

                    dims.push(filter);
                } else {
                    // 필터를 반영 안하는 로직
                    var value = "";

                    // 파라미터를 반영
                    if ( parsedParams.fbParams["[" + tSplit[0] + "].[" + attrSplit[0] + "]"] != undefined ) {
                        value += vdUtil.fn_filterStr(parsedParams.fbParams["[" + tSplit[0] + "].[" + attrSplit[0] + "]"]);
                    }

                    dims.push("[" + tSplit[0] + "].[" + attrSplit[0] + "]" + value);
                }

                // 필터에 where 에서 뺄 대상을 추가한다.
                parsedParams.fbParams.filterExistGrain.push("[" + tSplit[0] + "].[" + attrSplit[0] + "]");
            }
        }

        return dims;
    }

    // where 절 생성
    var fn_makeWhere = function(parsedParams, otherWhere){
        var whereStr = "";

        // 로직에 있는 where 조건 반영
        if ( otherWhere != undefined ) {
            //for ( var i = 0; i < otherWhere.length; i++ ) {
            //    whereStr += ( whereStr == "" ? "" : ", " ) + otherWhere[i];
            //}
            whereStr = otherWhere.join(", ");
        }

        // filter를 위한 where 절 생성
        var filterWhere = fn_makeFilterWhere(parsedParams);
        if ( filterWhere.length > 0 ) {
            whereStr += ( whereStr == "" ? "" : ", " ) + filterWhere.join(", ");
        }

        // 파라미터에 있는 where 조건 반영
        var where = parsedParams.fbParams["where"];
        for ( let key in where ) {
            whereStr += ( whereStr == "" ? "" : ", " ) + key + vdUtil.fn_filterStr(where[key]);
        }

        if ( whereStr == "" ) {
            return "";
        } else {
            return "where { " + whereStr + " } ";
        }
    }

    // filter where 절 생성
    var fn_makeFilterWhere = function(parsedParams, log) {
        var filtersArr = [];

        // filters 가 있어야 하고, filterDimension 에 필터를 적용할 Dimension 이 있어야함.
        if ( parsedParams.fbParams["filters"] != undefined && parsedParams.fbParams["filterDimension"] != undefined) {
            var filterDimension = parsedParams.fbParams.filterDimension;
            var filterExistGrain = [];
            if ( parsedParams.fbParams["filterExistGrain"] != undefined ) {
                filterExistGrain = parsedParams.fbParams.filterExistGrain;
            }

            var filters = parsedParams.fbParams["filters"];
            for ( let key in filters ) {
                if ( key != "[Item].[Item]" && filterDimension.includes(key.split(".")[0]) && !filterExistGrain.includes(key) ) {
                    filtersArr.push(vdUtil.fn_getFilterQuery(parsedParams, key));
                }
            }
        }

        return filtersArr;
    }

/************************************************* Mapping logic *************************************************/
    // Mapping 함수 정의, 마지막에 선언을 해야 함수를 정상적으로 인식함
    const functionMap = {
        "fn_setItem" : fn_setItem
        ,"fn_setBodItem" : fn_setBodItem
        ,"fn_lcmItem" : fn_lcmItem
        ,"fn_lcmBodItem" : fn_lcmBodItem
        ,"fn_lcmMappingItem" : fn_lcmMappingItem
    };

    return {
        fn_loadFunction : fn_loadFunction
    };
});


/**************************** o9.NSCM.JSEWItemSearch ****************************
    2025-11-20 : 최초 생성
*********************************************************************************/