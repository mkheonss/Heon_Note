define('o9.NSCM.JSEWLCMFrozenPeriodDetail', ['o9/data/query', 'o9/data/cellset', 'o9.NSCM.commonLibVD'], function () {

/**************************************************************************************
    프로그램명  : o9.NSCM.JSEWLCMFrozenPeriodDetail
    화면명     : LCM Frozen Period(Detail)
    화면 개발자 : 김훈섭 프로
    API 개발자 : sungmin0.lim
    최초생성   : 2025.08.22
**************************************************************************************/

	const programName = "o9.NSCM.JSEWLCMFrozenPeriodDetail";
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
{ "rowstatus":"C","rowindex":"0","[Location].[Location]":"P306","[Item].[Item]":"VG-LFF55SWG/ZA","[Sub Location].[Sub Location]":"L401","Measure.[LCM Frozen Period Detail_From Item]":"VG-LFF55SWG/ZA","Measure.[LCM Frozen Period Detail_Valid]":"Y","Measure.[LCM Frozen Period Detail_Frz]":"1","Measure.[LCM Frozen Period Detail_Frz Startdate]":"202534","Measure.[LCM Frozen Period Detail_Frz Enddate]":"202539" },
{ "rowstatus":"C","rowindex":"1","[Location].[Location]":"P401","[Item].[Item]":"VG-LFF55SDG/ZA","[Sub Location].[Sub Location]":"L401","Measure.[LCM Frozen Period Detail_From Item]":"VG-LFF55SDG/ZA","Measure.[LCM Frozen Period Detail_Valid]":"N","Measure.[LCM Frozen Period Detail_Frz]":"2","Measure.[LCM Frozen Period Detail_Frz Startdate]":"202535","Measure.[LCM Frozen Period Detail_Frz Enddate]":"202540" }
                  ] }

- 수정 테스트
{ "fbFuncName" : "fn_save", "fbParams" : { "[Version].[Version Name]" : "CWV_MP" },
  "fbGridRows" : [
{ "rowstatus":"U","rowindex":"1","[Location].[Location]":"P306","[Item].[Item]":"VG-LFF55SWG/ZA","[Sub Location].[Sub Location]":"L401","Measure.[LCM Frozen Period Detail_From Item]":"VG-LFF55SWG/ZA","Measure.[LCM Frozen Period Detail_Valid]":"Y","Measure.[LCM Frozen Period Detail_Frz]":"111","Measure.[LCM Frozen Period Detail_Frz Startdate]":"202544","Measure.[LCM Frozen Period Detail_Frz Enddate]":"202549" }
                  ] }

- 삭제 테스트
{ "fbFuncName" : "fn_save", "fbParams" : { "[Version].[Version Name]" : "CWV_MP" },
  "fbGridRows" : [
{ "rowstatus":"D","rowindex":"1","[Location].[Location]":"P306","[Item].[Item]":"VG-LFF55SWG/ZA","[Sub Location].[Sub Location]":"L401","Measure.[LCM Frozen Period Detail_From Item]":"VG-LFF55SWG/ZA","Measure.[LCM Frozen Period Detail_Valid]":"N","Measure.[LCM Frozen Period Detail_Frz]":"2","Measure.[LCM Frozen Period Detail_Frz Startdate]":"202535","Measure.[LCM Frozen Period Detail_Frz Enddate]":"202540" },
{ "rowstatus":"D","rowindex":"1","[Location].[Location]":"P401","[Item].[Item]":"VG-LFF55SDG/ZA","[Sub Location].[Sub Location]":"L401","Measure.[LCM Frozen Period Detail_From Item]":"VG-LFF55SWG/ZA","Measure.[LCM Frozen Period Detail_Valid]":"N","Measure.[LCM Frozen Period Detail_Frz]":"2","Measure.[LCM Frozen Period Detail_Frz Startdate]":"202535","Measure.[LCM Frozen Period Detail_Frz Enddate]":"202540" }
                  ] }

    */
    var fn_save = function(parsedParams){
        const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
        vdCommon.setLogLevel("Debug");

		try {
		    // 26.1.21 엑셀 업로드 기능이 추가되어 Member 데이타 체크하는 로직 추가
		    // 멤버를 배열로 구성
		    var location = [];
		    var item = [];
		    var subLocation = [];
            var keyHm = {};
            var value = "";
		    for ( var i = 0; i < parsedParams.fbGridRows.length; i++ ) {
                var row = parsedParams.fbGridRows[i];
                var rowstatus = row["rowstatus"];
                var key = "";

                if ( rowstatus == "C" ) {
                    value = row["[Location].[Location]"];
                    key = value;
                    if ( !location.includes(value) )    location.push(value);

                    value = row["[Item].[Item]"];
                    key += "_" + value;
                    if ( !item.includes(value) )    item.push(value);

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
                result = vdCommon.selectList(["[Item].[Item]" + vdUtil.fn_filterStr(item)], [], "", "", "");
                for ( var i = 0; i < result.cs.rowCount; i++ ) {
                    var name = vdUtil.fn_getDimValue(result, i, "Item", "Item");
                    validHm["item" + "_" + name] = name;
                }
                result = vdCommon.selectList(["[Sub Location].[Sub Location]" + vdUtil.fn_filterStr(subLocation)], [], "", "", "");
                for ( var i = 0; i < result.cs.rowCount; i++ ) {
                    var name = vdUtil.fn_getDimValue(result, i, "Sub Location", "Sub Location");
                    validHm["subLocation" + "_" + name] = name;
                }
            }

            //vdCommon.debug("key : " + JSON.stringify(keyHm));
            //vdCommon.debug("validHm : " + JSON.stringify(validHm));
            var currentWeek = vdCommon.selectResult('&CurrentWeek.element(0).DisplayName');

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
                    value = row["[Item].[Item]"];
                    key += "_" + value;
                    if ( validHm["item" + "_" + value] == undefined ) {
                        msg = vdUtil.fn_wordAppend(msg, "Check Item(" + value + "). ");
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

                    /* 2026.3.31 주석처리함
                    if ( currentWeek > row["Measure.[LCM Frozen Period Detail_Frz Enddate]"] ) {
                        msg = vdUtil.fn_wordAppend(msg, "End Plan ID is smaller than the Current Plan ID. ");
                    }
                    */

                    // 이미 등록되어 있는지 체크
                    var dimensions = [];
                    dimensions.push(vdUtil.fn_qDimVersionName(parsedParams));
                    dimensions.push(vdUtil.fn_qDim(row, "[Location].[Location]"));
                    dimensions.push(vdUtil.fn_qDim(row, "[Item].[Item]"));
                    dimensions.push(vdUtil.fn_qDim(row, "[Sub Location].[Sub Location]"));
                    var count = vdCommon.selectListCount(dimensions, ["Measure.[LCM Frozen Period Detail_Valid]"], "");
                    if ( count > 0 ) {
                        msg = vdUtil.fn_wordAppend(msg, "This is registered data. ");
                    }
                } if ( rowstatus == "U" ) {
                    /* 2026.3.31 주석처리함
                    if ( currentWeek > row["Measure.[LCM Frozen Period Detail_Frz Enddate]"] ) {
                        msg = vdUtil.fn_wordAppend(msg, "End Plan ID is smaller than the Current Plan ID. ");
                    }
                    */
                }

                if ( msg != "" ) {
                    validation.push(rowindex + "^" + msg);
                }
            }
            //vdCommon.debug("msg : " + JSON.stringify(keyHm));

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
                    dimensions.push(vdUtil.fn_qDim(row, "[Item].[Item]"));
                    dimensions.push(vdUtil.fn_qDim(row, "[Sub Location].[Sub Location]"));

                    var measures = [];
                    measures.push(vdUtil.fn_qMeaInt(row, "Measure.[LCM Frozen Period Detail_Frz]"));
                    measures.push(vdUtil.fn_qMeaStr(row, "Measure.[LCM Frozen Period Detail_Frz Enddate]"));
                    // 26.1.21 삭제처리
                    //measures.push(vdUtil.fn_qMeaStr(row, "Measure.[LCM Frozen Period Detail_Frz Startdate]"));
                    measures.push(vdUtil.fn_qMeaStr(row, "Measure.[LCM Frozen Period Detail_From Item]"));
                    measures.push(vdUtil.fn_qMeaStr(row, "Measure.[LCM Frozen Period Detail_Valid]"));
                    measures.push(vdUtil.fn_qMeaUpdateUserName("Measure.[LCM Frozen Period Detail_Init By]"));
                    measures.push(vdUtil.fn_qMeaUpdateTime("Measure.[LCM Frozen Period Detail_Init Time]"));

                    vdCommon.createMeasure(dimensions, measures);
                } else if ( rowstatus == "U" ) {
                    var dimensions = [];
                    dimensions.push(vdUtil.fn_qDimVersionName(parsedParams));
                    dimensions.push(vdUtil.fn_qDim(row, "[Location].[Location]"));
                    dimensions.push(vdUtil.fn_qDim(row, "[Item].[Item]"));
                    dimensions.push(vdUtil.fn_qDim(row, "[Sub Location].[Sub Location]"));

                    var measures = [];
                    measures.push(vdUtil.fn_qMeaInt(row, "Measure.[LCM Frozen Period Detail_Frz]"));
                    measures.push(vdUtil.fn_qMeaStr(row, "Measure.[LCM Frozen Period Detail_Frz Enddate]"));
                    // 26.1.21 삭제처리
                    //measures.push(vdUtil.fn_qMeaStr(row, "Measure.[LCM Frozen Period Detail_Frz Startdate]"));
                    measures.push(vdUtil.fn_qMeaStr(row, "Measure.[LCM Frozen Period Detail_Valid]"));
                    measures.push(vdUtil.fn_qMeaUpdateUserName("Measure.[LCM Frozen Period Detail_Update By]"));
                    measures.push(vdUtil.fn_qMeaUpdateTime("Measure.[LCM Frozen Period Detail_Update Time]"));

                    vdCommon.updateBlockMeasure(dimensions, measures);
                } else if ( rowstatus == "D" ) {
                    var where = [];
                    where.push(vdUtil.fn_qDimVersionName(parsedParams));
                    where.push(vdUtil.fn_qDim(row, "[Location].[Location]"));
                    where.push(vdUtil.fn_qDim(row, "[Item].[Item]"));
                    where.push(vdUtil.fn_qDim(row, "[Sub Location].[Sub Location]"));

                    vdCommon.deleteMeasure(where, "LCM Frozen Period Detail");
                }
            }

            vdCommon.programEnd();

            return { "Code" : 0, "Msg" : "It was saved successfully." };
        } catch ( e ) {
            vdCommon.error(e.message);
            return { "Code" : -1, "Msg" : e.message };
        }
    };

    // { "fbFuncName" : "fn_cb_fromItem", "fbParams" : { "[Location].[Location]" : "P112SP", "[Sub Location].[Sub Location]" : "P105", "[Item].[Item]" : "BN95-02719A" } }
    var fn_cb_fromItem = function(parsedParams){
        const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
        vdCommon.setLogLevel("Debug");

		try {
		    var dims = ['[To Item].[To Item]'];

            var where = 'where { &CWVUI ';
            if ( parsedParams.fbParams["[Location].[Location]"] != undefined ) {
                where += ', [Location].[Location].[' + parsedParams.fbParams["[Location].[Location]"] + ']';
            }
            if ( parsedParams.fbParams["[Sub Location].[Sub Location]"] != undefined ) {
                where += ', [Sub Location].[Sub Location].[' + parsedParams.fbParams["[Sub Location].[Sub Location]"] + ']';
            }
            if ( parsedParams.fbParams["[Item].[Item]"] != undefined ) {
                where += ', [Item].[Item].[' + parsedParams.fbParams["[Item].[Item]"] + ']';
            }
            where += ', Measure.[Code Map LCM_Map Status]=="CON", Measure.[Code Map LCM_Valid Flag] =="Y" }';
            var result = vdCommon.selectList(dims, ["Measure.[Code Map LCM_Map Status]"], where, "orderby [To Item].[To Item].DisplayName", "");
            var comboList = [];
            for ( var i = 0; i < result.cs.rowCount; i++ ) {
                comboList.push({ "Name" : vdUtil.fn_getDimValue(result, i, "To Item", "To Item")
                                ,"DisplayName" : vdUtil.fn_getDimValue(result, i, "To Item", "To Item") });
            }
            vdCommon.debug("ComboData : " + JSON.stringify(comboList.slice(0,3)));

            vdCommon.programEnd();

            return { "Code" : 0, "Msg" : "", "Rows" : comboList };
        } catch ( e ) {
            vdCommon.error(e.message);
            return { "Code" : -1, "Msg" : e.message };
        }
    };

    // 2025.08.29 Append
    // { "fbFuncName" : "fn_cb_toItem", "fbParams" : { "[Location].[Location]" : "P105", "[Sub Location].[Sub Location]" : "P551","filters" : { "[Version].[Version Name]" : {"SelectedMembers" : ["CWV_MP"], "MemberFilter" : ""} } } }
    var fn_cb_toItem = function(parsedParams){
        const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
        vdCommon.setLogLevel("Debug");

		try {
            vdCommon.printParams(parsedParams);

		    var dims = ['&LCMItemIncludeLED'];

            var version = vdUtil.fn_getFilterQuery(parsedParams, "[Version].[Version Name]");

            var where = 'where { ' + version + ', Measure.[BOD Item_BOD Valid] == "Y", ';
            if ( parsedParams.fbParams["[Location].[Location]"] != undefined ) {
                where += '[Location].[Location].[' + parsedParams.fbParams["[Location].[Location]"] + '], ';
            }
            if ( parsedParams.fbParams["[Sub Location].[Sub Location]"] != undefined ) {
                where += '[Sub Location].[Sub Location].[' + parsedParams.fbParams["[Sub Location].[Sub Location]"] + '], ';
            }
            where += 'Measure.[BOD Item_Asn]==1 }';

            var result = vdCommon.selectList(dims, ["Measure.[BOD Item_Asn]"], where, "orderby Item.Item.DisplayName", "limit 1000");
            var comboList = vdCommon.fn_makeCombo(result, {DimName : "Item", DimAttbName : "Item", Sort : "DisplayName"});
            vdCommon.debug("ComboData : " + JSON.stringify(comboList.slice(0,3)));

            vdCommon.programEnd();

            return { "Code" : 0, "Msg" : "", "Rows" : comboList };
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
        ,"fn_cb_toItem" : fn_cb_toItem
        ,"fn_cb_fromItem" : fn_cb_fromItem
    };

    return {
        fn_loadFunction : fn_loadFunction
    };
});

/******************************************************************************************************
26.01.21 : 엑셀 업로드 기능이 추가되어 Member 데이타 체크하는 로직 추가
26.02.02 : Measure.[Code Map LCM_Prod Item] => ProdItem 로 변경
26.03.05 : fn_cb_item 에서 To Item 에서 ProdItem 을 가져오도록 변경
26.03.25 : fn_cd_toItem 추가, fn_cb_fromItem 로직 변경
26.04.09 : fn_cb_fromItem 에 where 추가
********************************** o9.NSCM.JSEWLCMFrozenPeriodDetail **********************************/