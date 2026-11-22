define('o9.NSCM.JSEWCommonCO', ['o9/data/query', 'o9/data/cellset', 'o9.NSCM.commonLibCO'], function () {
    const programName = "o9.NSCM.JSEWCommonCO";
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
            
            var rtn = functionMap[fbFuncName](parsedParams);

            coCommon.programEnd();
            return rtn;
        } catch ( e ) {
            return { "Code" : -1, "Msg" : e.message };
        }
	};
	
/************************************************* Internal Util Common Logic *************************************************/	
    //// util logic
		// Meausre 명칭 분리
    var fn_getMeasureName = function(measure){
        var measureSplit = measure.split(".");
        return measureSplit[1].replace("[", "").replace("]", "")
    }


/************************************************* External UI combo logic *************************************************/
    // 여러개의 콤보를 한번에 가져올때
    // { "fbFuncName" : "fn_cb_common", "fbParams" : { "codes" : ["jdm", "mfSiteStageForMF", "subsidiaryForMF", "SiteMF", "SiteDC", "tpmodeGO"] } }
	  var fn_cb_common = function(parsedParams){
        const coCommon = new commonLib.COCommon(programName + "." + arguments.callee.name);
        coCommon.setLogLevel("Debug");

		try {
            var codes = parsedParams.fbParams.codes;
            var rtn = {};

            for ( var i = 0; i < codes.length; i++ ) {
                var sRtn = functionMap["fn_cb_" + codes[i]](parsedParams);
                rtn[codes[i]] = sRtn.Rows;
            }

            coCommon.programEnd();

            return { "Code" : 0, "Msg" : "", "Rows" : rtn };
        } catch ( e ) {
            coCommon.error(e.message);
            return { "Code" : -1, "Msg" : e.message };
        }
    };


    //// common logic
		// 수정자 정보
    // { "fbFuncName" : "fn_updateInfo", "fbParams" : { "version" : "CWV_MP", "measureList" : ["Measure.[VersionInfo_Time Phased BOD Master Update User]", "Measure.[VersionInfo_Time Phased BOD Master Update Time]"] } }
    var fn_updateInfo = function(parsedParams){
        const coCommon = new commonLib.COCommon(programName + "." + arguments.callee.name);
        coCommon.setLogLevel("Debug");

		try {
            var result = coCommon.selectList(["[Version].[Version Name].[" + parsedParams.fbParams.version + "]"], parsedParams.fbParams.measureList, "", "", "");
            var rtn = { "Code" : 0, "Msg" : "" };
            for ( var i = 0; i < result.cs.rowCount; i++ ) {
                for ( var m = 0; m < parsedParams.fbParams.measureList.length; m++ ) {
                    var measure = parsedParams.fbParams.measureList[m];
                    rtn[measure] = result.cs.row(i).cell(result.cs.measureColumnIndex(fn_getMeasureName(measure)));
                }
            }

            coCommon.programEnd();

            return rtn;
        } catch ( e ) {
            coCommon.error(e.message);
            return { "Code" : -1, "Msg" : e.message };
        }
    };

    


    //// util logic
    // 사용방법 확인 필요
    //{ "fbFuncName" : "fn_validation", "fbGridRows" : [{ "Field11" : "11", "Field12" : "12", "Field13" : "13"}, { "Field11" : "21", "Field12" : "22", "Field13" : "23"}, { "Field11" : "31", "Field12" : "32", "Field13" : "33"}] }
    var fn_validation = function(parsedParams){
        const coCommon = new commonLib.COCommon(programName + "." + arguments.callee.name);
        coCommon.setLogLevel("Debug");

		try {

            for ( var i = 0; i < parsedParams.fbGridRows.length; i++ ) {
                parsedParams.fbGridRows[i]["Rtn1"] = i;
                parsedParams.fbGridRows[i]["Rtn2"] = i + 1;
            }

            coCommon.programEnd();

            return { "Code" : 0, "Msg" : "", "Rows" : parsedParams.fbGridRows };
        } catch ( e ) {
            return { "Code" : -1, "Msg" : e.message };
        }
    };


/************************************************* 사업부별 combo logic *************************************************/



   /* ********************************************************************************** */
    // { "fbFuncName" : "fn_cb_BasePlan" }
    var fn_cb_BasePlan = function(parsedParams){
        const coCommon = new commonLib.COCommon(programName + "." + arguments.callee.name);
        coCommon.setLogLevel("Debug"); 

        		  try {
//		    var dims = ['&NSUILocationDC'];
 		    var dims = ['[Base Plan].[Base Plan]'];

		    // Casecade 를 위해서 Dimension 추가
		    dims = coUtil.fn_addincludeField(dims, parsedParams);
           // where절 세팅
            //parsedParams.fbParams.where["[Location].[Location Type]"] = "DC";

            var result = coCommon.selectList(dims, [], coUtil.fn_makeWhere(parsedParams), "", parsedParams.fbParams.limit);
            //coCommon.printCsData(result, 3);
            var comboList = coCommon.fn_makeCombo(result, {DimName : "Base Plan", DimAttbName : "Base Plan", Sort : "DisplayName",
                                                    includeField : parsedParams.fbParams.includeField, existAll : parsedParams.fbParams.existAll});
            coCommon.debug("ComboData : " + JSON.stringify(comboList.slice(0,3)));

            coCommon.programEnd();

            return { "Code" : 0, "Msg" : "", "Rows" : comboList };
        } catch ( e ) {
            coCommon.error(e.message);
            return { "Code" : -1, "Msg" : e.message };
        }
    };

   /* ********************************************************************************** */
    // { "fbFuncName" : "fn_cb_CopySourceMP" }
    var fn_cb_CopySourceMP = function(parsedParams){
        const coCommon = new commonLib.COCommon(programName + "." + arguments.callee.name);
        coCommon.setLogLevel("Debug"); 

        		  try {
//		    var dims = ['&NSUILocationDC'];
 		    var dims = ['[Copy Source MP].[Copy Source MP]'];

		    // Casecade 를 위해서 Dimension 추가
		    dims = coUtil.fn_addIncludeField(dims, parsedParams);
           // where절 세팅
            //parsedParams.fbParams.where["[Location].[Location Type]"] = "DC";

            var result = coCommon.selectList(dims, [], coUtil.fn_makeWhere(parsedParams), "", parsedParams.fbParams.limit);
            //coCommon.printCsData(result, 3);
            var comboList = coCommon.fn_makeCombo(result, {DimName : "Copy Source MP", DimAttbName : "Copy Source MP", Sort : "DisplayName",
                                                    includeField : parsedParams.fbParams.includeField, existAll : parsedParams.fbParams.existAll});
            coCommon.debug("ComboData : " + JSON.stringify(comboList.slice(0,3)));

            coCommon.programEnd();

            return { "Code" : 0, "Msg" : "", "Rows" : comboList };
        } catch ( e ) {
            coCommon.error(e.message);
            return { "Code" : -1, "Msg" : e.message };
        }
    };


    /* ********************************************************************************** */
    // { "fbFuncName" : "fn_cb_eolGroupID" }
    // eolGroupIDCombo
    var fn_cb_eolGroupID = function(parsedParams){
        const coCommon = new commonLib.COCommon(programName + "." + arguments.callee.name);
        coCommon.setLogLevel("Debug");

		try {
//		    var dims = ['&NSUIToLocationDC'];
 		    var dims = ['[EOL Group].[EOL Group ID]','[EOL Group].[EOL Group Description]'];
				parsedParams.fbParams.includeField



		    // Casecade 를 위해서 Dimension 추가
				dims = coUtil.fn_addincludeField(dims, parsedParams);
           // where절 세팅
            //parsedParams.fbParams.where["[Location].[Location Type]"] = "DC";

            var result = coCommon.selectList(dims, [], coUtil.fn_makeWhere(parsedParams), "orderby [EOL Group].[EOL Group Description].DisplayName asc", parsedParams.fbParams.limit);
            //coCommon.printCsData(result, 3);
            
						var comboList = [];
						var _name =[];
						var _displayname =[];
						
						for(var i=0; i<result.cs.rowCount;i++) {
						  _name.push(result.cs.row(i).cell(result.cs.memberColumnIndex("EOL Group", "EOL Group ID")).Name);
							_displayname.push(result.cs.row(i).cell(result.cs.memberColumnIndex("EOL Group", "EOL Group Description")).Name);
						}
						
						var comboList = coCommon.fn_makeCombo(null, {ComboCodes : _name , ComboValues : _displayname });
						
						
						//var comboList = coCommon.fn_makeCombo(result, {DimName : "EOL Group", DimAttbName : "EOL Group ID", Sort : "DisplayName",
            //                                        includeField : parsedParams.fbParams.includeField, existAll : parsedParams.fbParams.existAll});
											
            coCommon.debug("ComboData : " + JSON.stringify(comboList.slice(0,3)));

            coCommon.programEnd();

            return { "Code" : 0, "Msg" : "", "Rows" : comboList };
        } catch ( e ) {
            coCommon.error(e.message);
            return { "Code" : -1, "Msg" : e.message };
        }
    };



   /* ********************************************************************************** */
    // { "fbFuncName" : "fn_cb_LevelList" }
    var fn_cb_LevelList = function(parsedParams){
        const coCommon = new commonLib.COCommon(programName + "." + arguments.callee.name);
        coCommon.setLogLevel("Debug"); 

        		  try {
//		    var dims = ['&NSUILocationDC'];
 		    var dims = ['[Product Level].[Level List]'];

		    // Casecade 를 위해서 Dimension 추가
		    dims = coUtil.fn_addincludeField(dims, parsedParams);
           // where절 세팅
            //parsedParams.fbParams.where["[Location].[Location Type]"] = "DC";

            var result = coCommon.selectList(dims, [], coUtil.fn_makeWhere(parsedParams), "", parsedParams.fbParams.limit);
            //coCommon.printCsData(result, 3);
            var comboList = coCommon.fn_makeCombo(result, {DimName : "Product Level", DimAttbName : "Level List", Sort : "DisplayName",
                                                    includeField : parsedParams.fbParams.includeField, existAll : parsedParams.fbParams.existAll});
            coCommon.debug("ComboData : " + JSON.stringify(comboList.slice(0,3)));

            coCommon.programEnd();

            return { "Code" : 0, "Msg" : "", "Rows" : comboList };
        } catch ( e ) {
            coCommon.error(e.message);
            return { "Code" : -1, "Msg" : e.message };
        }
    };


    // { "fbFuncName" : "fn_cb_plBoolean" }
	  var fn_cb_plBoolean = function(parsedParams){
        const coCommon = new commonLib.COCommon(programName + "." + arguments.callee.name);
        coCommon.setLogLevel("Debug");

		try {
            var comboList = coCommon.fn_makeCombo(null, {ComboCodes : ["","true","false"], ComboValues : ["","Y","N"]});
            coCommon.debug("ComboData : " + JSON.stringify(comboList.slice(0,3)));

            coCommon.programEnd();

            return { "Code" : 0, "Msg" : "", "Rows" : comboList };
        } catch ( e ) {
            coCommon.error(e.message);
            return { "Code" : -1, "Msg" : e.message };
        }
    };


    // { "fbFuncName" : "fn_cb_PLBooleanFlagN" }
	  var fn_cb_PLBooleanFlagN = function(parsedParams){
        const coCommon = new commonLib.COCommon(programName + "." + arguments.callee.name);
        coCommon.setLogLevel("Debug");

		try {
            var comboList = coCommon.fn_makeCombo(null, {ComboCodes : ["","Y","N","-"], ComboValues : ["","Y","N","-"]});
            coCommon.debug("ComboData : " + JSON.stringify(comboList.slice(0,3)));

            coCommon.programEnd();

            return { "Code" : 0, "Msg" : "", "Rows" : comboList };
        } catch ( e ) {
            coCommon.error(e.message);
            return { "Code" : -1, "Msg" : e.message };
        }
    };
				
    // { "fbFuncName" : "fn_cb_plCompanyCode" }
	  var fn_cb_plCompanyCode = function(parsedParams){
        const coCommon = new commonLib.COCommon(programName + "." + arguments.callee.name);
        coCommon.setLogLevel("Debug");

		try {
						var companycode = [];
						
						companycode.push("B100");
						companycode.push("B1A0");
						companycode.push("B201");
						companycode.push("B301");
						companycode.push("B305");
						companycode.push("B312");
						companycode.push("B401");
						companycode.push("B402");
						companycode.push("B403");
						companycode.push("B407");
						companycode.push("B4XC");
						companycode.push("B504");
						companycode.push("B508");
						companycode.push("B509");
						companycode.push("B520");
						companycode.push("B522");
						companycode.push("B526");
						companycode.push("B527");
						companycode.push("B605");
						companycode.push("B607");
						companycode.push("B908");
						companycode.push("B910");
						companycode.push("C000");
						companycode.push("C060");
						companycode.push("C100");
						companycode.push("C105");
						companycode.push("C109");
						companycode.push("C110");
						companycode.push("C114");
						companycode.push("C116");
						companycode.push("C119");
						companycode.push("C130");
						companycode.push("C140");
						companycode.push("C150");
						companycode.push("C160");
						companycode.push("C190");
						companycode.push("C1A0");
						companycode.push("C1B5");
						companycode.push("C1C1");
						companycode.push("C1E0");
						companycode.push("C1E1");
						companycode.push("C1F0");
						companycode.push("C1G0");
						companycode.push("C1J0");
						companycode.push("C1K0");
						companycode.push("C1L0");
						companycode.push("C1N0");
						companycode.push("C1S0");
						companycode.push("C1T0");
						companycode.push("C1V0");
						companycode.push("C1W0");
						companycode.push("C1X0");
						companycode.push("C201");
						companycode.push("C210");
						companycode.push("C230");
						companycode.push("C290");
						companycode.push("C2A0");
						companycode.push("C310");
						companycode.push("C31A");
						companycode.push("C31B");
						companycode.push("C31H");
						companycode.push("C31M");
						companycode.push("C31Y");
						companycode.push("C320");
						companycode.push("C321");
						companycode.push("C322");
						companycode.push("C323");
						companycode.push("C326");
						companycode.push("C330");
						companycode.push("C340");
						companycode.push("C346");
						companycode.push("C347");
						companycode.push("C350");
						companycode.push("C355");
						companycode.push("C360");
						companycode.push("C370");
						companycode.push("C380");
						companycode.push("C390");
						companycode.push("C391");
						companycode.push("C394");
						companycode.push("C3A0");
						companycode.push("C3B0");
						companycode.push("C3C0");
						companycode.push("C3Z0");
						companycode.push("C410");
						companycode.push("C420");
						companycode.push("C430");
						companycode.push("C432");
						companycode.push("C438");
						companycode.push("C440");
						companycode.push("C450");
						companycode.push("C451");
						companycode.push("C452");
						companycode.push("C453");
						companycode.push("C460");
						companycode.push("C470");
						companycode.push("C480");
						companycode.push("C482");
						companycode.push("C490");
						companycode.push("C491");
						companycode.push("C492");
						companycode.push("C493");
						companycode.push("C4A0");
						companycode.push("C4B0");
						companycode.push("C4B1");
						companycode.push("C4B2");
						companycode.push("C4B3");
						companycode.push("C4B4");
						companycode.push("C4B5");
						companycode.push("C4B6");
						companycode.push("C4C0");
						companycode.push("C4CV");
						companycode.push("C4CW");
						companycode.push("C4CX");
						companycode.push("C4D0");
						companycode.push("C4E0");
						companycode.push("C4F0");
						companycode.push("C4F2");
						companycode.push("C4J0");
						companycode.push("C4K0");
						companycode.push("C4L0");
						companycode.push("C4L1");
						companycode.push("C4L2");
						companycode.push("C4M0");
						companycode.push("C4M6");
						companycode.push("C4N0");
						companycode.push("C4N1");
						companycode.push("C4N2");
						companycode.push("C4N6");
						companycode.push("C4P4");
						companycode.push("C510");
						companycode.push("C511");
						companycode.push("C520");
						companycode.push("C530");
						companycode.push("C540");
						companycode.push("C54H");
						companycode.push("C550");
						companycode.push("C551");
						companycode.push("C552");
						companycode.push("C553");
						companycode.push("C554");
						companycode.push("C560");
						companycode.push("C565");
						companycode.push("C570");
						companycode.push("C571");
						companycode.push("C580");
						companycode.push("C590");
						companycode.push("C5A0");
						companycode.push("C5A1");
						companycode.push("C5B0");
						companycode.push("C5B1");
						companycode.push("C5B2");
						companycode.push("C5B3");
						companycode.push("C5D1");
						companycode.push("C5D3");
						companycode.push("C5F0");
						companycode.push("C5G0");
						companycode.push("C5G2");
						companycode.push("C5H0");
						companycode.push("C5H1");
						companycode.push("C5H2");
						companycode.push("C5H3");
						companycode.push("C605");
						companycode.push("C607");
						companycode.push("C610");
						companycode.push("C611");
						companycode.push("C620");
						companycode.push("C621");
						companycode.push("C630");
						companycode.push("C631");
						companycode.push("C632");
						companycode.push("C633");
						companycode.push("C634");
						companycode.push("C635");
						companycode.push("C636");
						companycode.push("C63L");
						companycode.push("C640");
						companycode.push("C660");
						companycode.push("C670");
						companycode.push("C680");
						companycode.push("C690");
						companycode.push("C6A0");
						companycode.push("C6A1");
						companycode.push("C6B0");
						companycode.push("C6D0");
						companycode.push("C6E0");
						companycode.push("C6F0");
						companycode.push("C6G0");
						companycode.push("C6H0");
						companycode.push("C6J0");
						companycode.push("C6J1");
						companycode.push("C6K0");
						companycode.push("C6L0");
						companycode.push("C6M0");
						companycode.push("C6N0");
						companycode.push("C6P0");
						companycode.push("C6Q0");
						companycode.push("C6S0");
						companycode.push("C6S1");
						companycode.push("C6S2");
						companycode.push("C6T0");
						companycode.push("C6U0");
						companycode.push("C6V0");
						companycode.push("C6W0");
						companycode.push("C701");
						companycode.push("C702");
						companycode.push("C710");
						companycode.push("C711");
						companycode.push("C712");
						companycode.push("C713");
						companycode.push("C714");
						companycode.push("C715");
						companycode.push("C717");
						companycode.push("C718");
						companycode.push("C720");
						companycode.push("C721");
						companycode.push("C750");
						companycode.push("C751");
						companycode.push("C760");
						companycode.push("C770");
						companycode.push("C780");
						companycode.push("C7B1");
						companycode.push("C810");
						companycode.push("C811");
						companycode.push("C812");
						companycode.push("C813");
						companycode.push("C814");
						companycode.push("C820");
						companycode.push("C830");
						companycode.push("C831");
						companycode.push("C850");
						companycode.push("C860");
						companycode.push("C910");
						companycode.push("C920");
						companycode.push("C940");
						companycode.push("C941");
						companycode.push("C960");
						companycode.push("C961");
						companycode.push("C962");
						companycode.push("C964");
						companycode.push("C970");
						companycode.push("C980");
						companycode.push("C981");
						companycode.push("C982");
						companycode.push("C983");
						companycode.push("C990");
						companycode.push("C9D0");
						companycode.push("C9E0");
						companycode.push("D100");
						companycode.push("D301");
						companycode.push("D302");
						companycode.push("D401");
						companycode.push("D501");
						companycode.push("D502");
						companycode.push("D601");
						companycode.push("D602");
						companycode.push("D603");
						companycode.push("D801");
						companycode.push("E100");
						companycode.push("E301");
						companycode.push("E302");
						companycode.push("E401");
						companycode.push("E402");
						companycode.push("E501");
						companycode.push("E502");
						companycode.push("E503");
						companycode.push("E601");
						companycode.push("E602");
						companycode.push("E603");
						companycode.push("E610");
						companycode.push("G100");
						companycode.push("H100");
						companycode.push("I100");
						companycode.push("I102");
						companycode.push("I104");
						companycode.push("I302");
						companycode.push("I402");
						companycode.push("I601");
						companycode.push("J100");
						companycode.push("J601");
						companycode.push("J603");
						companycode.push("K100");
						companycode.push("K201");
						companycode.push("K301");
						companycode.push("K404");
						companycode.push("K405");
						companycode.push("K406");
						companycode.push("K601");
						companycode.push("L100");
						companycode.push("L103");
						companycode.push("L1C0");
						companycode.push("L1D0");
						companycode.push("L1I0");
						companycode.push("L2A0");
						companycode.push("L3A0");
						companycode.push("L3B0");
						companycode.push("L5A0");
						companycode.push("L6A0");
						companycode.push("N100");
						companycode.push("N101");
						companycode.push("N401");
						companycode.push("N501");
						companycode.push("N601");
						companycode.push("N602");
						companycode.push("P100");
						companycode.push("R100");
						companycode.push("S100");
						companycode.push("S310");
						companycode.push("S410");
						companycode.push("T100");
						companycode.push("T1A0");
						companycode.push("T301");
						companycode.push("U100");
						companycode.push("W100");
						companycode.push("X100");
						companycode.push("X501");
						companycode.push("X503");
						companycode.push("Y1A0");
						companycode.push("Y1B0");
						companycode.push("Y1D0");
						companycode.push("Y1E0");
						companycode.push("Y1F0");
						companycode.push("Y1N1");
						companycode.push("Y1N2");
						companycode.push("Y1N3");
						companycode.push("Y1N4");
						companycode.push("Y1N5");

						
		
            var comboList = coCommon.fn_makeCombo(null, {ComboCodes : companycode, ComboValues : companycode});
            coCommon.debug("ComboData : " + JSON.stringify(comboList.slice(0,3)));

            coCommon.programEnd();

            return { "Code" : 0, "Msg" : "", "Rows" : comboList };
        } catch ( e ) {
            coCommon.error(e.message);
            return { "Code" : -1, "Msg" : e.message };
        }
    };


    // { "fbFuncName" : "fn_cb_PLCopyPerdFlag" }
	  var fn_cb_PLCopyPerdFlag = function(parsedParams){
        const coCommon = new commonLib.COCommon(programName + "." + arguments.callee.name);
        coCommon.setLogLevel("Debug");

		try {
						var plList = [];
						
						plList.push("N");
						plList.push("ALL");
						plList.push("MON");
						plList.push("TUE");
						plList.push("WED");
						plList.push("THU");
						plList.push("FRI");
						plList.push("SAT");
						plList.push("SUN");
		
            var comboList = coCommon.fn_makeCombo(null, {ComboCodes : plList, ComboValues : plList});
            coCommon.debug("ComboData : " + JSON.stringify(comboList.slice(0,3)));

            coCommon.programEnd();

            return { "Code" : 0, "Msg" : "", "Rows" : comboList };
        } catch ( e ) {
            coCommon.error(e.message);
            return { "Code" : -1, "Msg" : e.message };
        }
    };


    // { "fbFuncName" : "fn_cb_item" }
	  var fn_cb_item = function(parsedParams){
        const coCommon = new commonLib.COCommon(programName + "." + arguments.callee.name);
        coCommon.setLogLevel("Debug");

		try {
//		    var dims = ['&NSUIToLocationDC'];
 		    var dims = ['[Item].[Item]'];

		    // Casecade 를 위해서 Dimension 추가
				dims = coUtil.fn_addincludeField(dims, parsedParams);
           // where절 세팅
            //parsedParams.fbParams.where["[Location].[Location Type]"] = "DC";

            var result = coCommon.selectList(dims, [], coUtil.fn_makeWhere(parsedParams), "", parsedParams.fbParams.limit);
            //coCommon.printCsData(result, 3);
            
						var comboList = [];
            var comboList = coCommon.fn_makeCombo(result, {DimName : "Item", DimAttbName : "Item", Sort : "DisplayName",
                                                    includeField : parsedParams.fbParams.includeField, existAll : parsedParams.fbParams.existAll});
            coCommon.debug("ComboData : " + JSON.stringify(comboList.slice(0,3)));

            coCommon.programEnd();

            return { "Code" : 0, "Msg" : "", "Rows" : comboList };
        } catch ( e ) {
            coCommon.error(e.message);
            return { "Code" : -1, "Msg" : e.message };
        }
    };


    // { "fbFuncName" : "fn_cb_plRddFlag" }
	  var fn_cb_plRddFlag = function(parsedParams){
        const coCommon = new commonLib.COCommon(programName + "." + arguments.callee.name);
        coCommon.setLogLevel("Debug");

		try {
						var plList = [];
						plList.push("MON");
						plList.push("TUE");
						plList.push("WED");
						plList.push("THU");
						plList.push("FRI");
						plList.push("SAT");
						plList.push("SUN");
		
            var comboList = coCommon.fn_makeCombo(null, {ComboCodes : plList, ComboValues : plList});
            coCommon.debug("ComboData : " + JSON.stringify(comboList.slice(0,3)));

            coCommon.programEnd();

            return { "Code" : 0, "Msg" : "", "Rows" : comboList };
        } catch ( e ) {
            coCommon.error(e.message);
            return { "Code" : -1, "Msg" : e.message };
        }
    };




    /* ********************************************************************************** */
    // { "fbFuncName" : "fn_cb_erpShipDescription" }
    // erp Ship to Description Combo

//{
//"fbFuncName":"fn_cb_erpShipDescription"
//, "fbParams" : { "includeField":"ERP Ship to:ERP Ship to Company:Company" }
//}


    var fn_cb_erpShipDescription = function(parsedParams){
        const coCommon = new commonLib.COCommon(programName + "." + arguments.callee.name);
        coCommon.setLogLevel("Debug"); 

		  try {
//		    var dims = ['&NSUIToLocationDC'];
 		    var dims = ['[ERP Ship to].[ERP Ship to Code]','[ERP Ship to].[ERP Ship to ID]'];

		    // Casecade 를 위해서 Dimension 추가
		    dims = coUtil.fn_addincludeField(dims, parsedParams);
           // where절 세팅
            //parsedParams.fbParams.where["[Location].[Location Type]"] = "DC";

            var result = coCommon.selectList(dims, [], coUtil.fn_makeWhere(parsedParams), "", parsedParams.fbParams.limit);
            //coCommon.printCsData(result, 3);
            var comboList = coCommon.fn_makeCombo(result, {DimName : "ERP Ship to", DimAttbName : "ERP Ship to Code", DimDisplayAttbName : "ERP Ship to ID", Sort : "DisplayName",
                                                    includeField : parsedParams.fbParams.includeField, existAll : parsedParams.fbParams.existAll});
            coCommon.debug("ComboData : " + JSON.stringify(comboList.slice(0,3)));

            coCommon.programEnd();

            return { "Code" : 0, "Msg" : "", "Rows" : comboList };
        } catch ( e ) {
            coCommon.error(e.message);
            return { "Code" : -1, "Msg" : e.message };
        }
    };


    /* ********************************************************************************** */
    // { "fbFuncName" : "fn_cb_erpSoldDescription" }
    // erp Sold to Description Combo


//{
//"fbFuncName":"fn_cb_erpSoldDescription"
//, "fbParams" : { "includeField":"ERP Sold to:ERP Sold to Company:Company" }
//}

    var fn_cb_erpSoldDescription = function(parsedParams){
        const coCommon = new commonLib.COCommon(programName + "." + arguments.callee.name);
        coCommon.setLogLevel("Debug"); 


		  try {
//		    var dims = ['&NSUIToLocationDC'];
 		    var dims = ['[ERP Sold to].[ERP Sold to Code]','[ERP Sold to].[ERP Sold to ID]'];

		    // Casecade 를 위해서 Dimension 추가
		    dims = coUtil.fn_addincludeField(dims, parsedParams);
           // where절 세팅
            //parsedParams.fbParams.where["[Location].[Location Type]"] = "DC";

            var result = coCommon.selectList(dims, [], coUtil.fn_makeWhere(parsedParams), "", parsedParams.fbParams.limit);
            //coCommon.printCsData(result, 3);
            var comboList = coCommon.fn_makeCombo(result, {DimName : "ERP Sold to", DimAttbName : "ERP Sold to Code", DimDisplayAttbName : "ERP Sold to ID", Sort : "DisplayName",
                                                    includeField : parsedParams.fbParams.includeField, existAll : parsedParams.fbParams.existAll});
            coCommon.debug("ComboData : " + JSON.stringify(comboList.slice(0,3)));

            coCommon.programEnd();

            return { "Code" : 0, "Msg" : "", "Rows" : comboList };
        } catch ( e ) {
            coCommon.error(e.message);
            return { "Code" : -1, "Msg" : e.message };
        }
    };



    // { "fbFuncName" : "fn_cb_jdm" }
	  var fn_cb_jdm = function(parsedParams){
        const coCommon = new commonLib.COCommon(programName + "." + arguments.callee.name);
        coCommon.setLogLevel("Debug");

		try {
            var comboList = coCommon.fn_makeCombo(null, {ComboCodes : ["true","-"], ComboValues : ["Y","-"]});
            coCommon.debug("ComboData : " + JSON.stringify(comboList.slice(0,3)));

            coCommon.programEnd();

            return { "Code" : 0, "Msg" : "", "Rows" : comboList };
        } catch ( e ) {
            coCommon.error(e.message);
            return { "Code" : -1, "Msg" : e.message };
        }
    };



    /* ********************************************************************************** */
    // { "fbFuncName" : "fn_cb_progrpProductGroup" }
    // ProductGroup ProductGroupNameCombo
    var fn_cb_progrpProductGroup = function(parsedParams){
        const coCommon = new commonLib.COCommon(programName + "." + arguments.callee.name);
        coCommon.setLogLevel("Debug"); 

		  try {
//		    var dims = ['&NSUIToLocationDC'];
 		    var dims = ['[Product Group].[Product Group].filter(~(#.Name =="-"))'];

		    // Casecade 를 위해서 Dimension 추가
		    dims = coUtil.fn_addincludeField(dims, parsedParams);
           // where절 세팅
            //parsedParams.fbParams.where["[Location].[Location Type]"] = "DC";

            var result = coCommon.selectList(dims, [], coUtil.fn_makeWhere(parsedParams), "", parsedParams.fbParams.limit);
            //coCommon.printCsData(result, 3);
            var comboList = coCommon.fn_makeCombo(result, {DimName : "Product Group", DimAttbName : "Product Group", Sort : "DisplayName",
                                                    includeField : parsedParams.fbParams.includeField, existAll : parsedParams.fbParams.existAll});
            coCommon.debug("ComboData : " + JSON.stringify(comboList.slice(0,3)));

            coCommon.programEnd();

            return { "Code" : 0, "Msg" : "", "Rows" : comboList };
        } catch ( e ) {
            coCommon.error(e.message);
            return { "Code" : -1, "Msg" : e.message };
        }
    };


    /* ********************************************************************************** */
    // { "fbFuncName" : "fn_cb_progrpSection" }
    // ProductGroup SectionNameCombo
    var fn_cb_progrpSection = function(parsedParams){
        const coCommon = new commonLib.COCommon(programName + "." + arguments.callee.name);
        coCommon.setLogLevel("Debug"); 

		  try {
//		    var dims = ['&NSUIToLocationDC'];
 		    var dims = ['[Product Group].[Section].filter(~(#.Name =="-"))'];

		    // Casecade 를 위해서 Dimension 추가
		    dims = coUtil.fn_addincludeField(dims, parsedParams);
           // where절 세팅
            //parsedParams.fbParams.where["[Location].[Location Type]"] = "DC";

            var result = coCommon.selectList(dims, [], coUtil.fn_makeWhere(parsedParams), "", parsedParams.fbParams.limit);
            //coCommon.printCsData(result, 3);
            var comboList = coCommon.fn_makeCombo(result, {DimName : "Product Group", DimAttbName : "Section", Sort : "DisplayName",
                                                    includeField : parsedParams.fbParams.includeField, existAll : parsedParams.fbParams.existAll});
            coCommon.debug("ComboData : " + JSON.stringify(comboList.slice(0,3)));

            coCommon.programEnd();

            return { "Code" : 0, "Msg" : "", "Rows" : comboList };
        } catch ( e ) {
            coCommon.error(e.message);
            return { "Code" : -1, "Msg" : e.message };
        }
    };


    /* ********************************************************************************** */
    // { "fbFuncName" : "fn_cb_project" }
    // projectNameCombo
    var fn_cb_project = function(parsedParams){
        const coCommon = new commonLib.COCommon(programName + "." + arguments.callee.name);
        coCommon.setLogLevel("Debug"); 

		  try {
//		    var dims = ['&NSUIToLocationDC'];
 		    var dims = ['[Project].[Project].filter(~(#.Name =="-"))'];

		    // Casecade 를 위해서 Dimension 추가
		    dims = coUtil.fn_addincludeField(dims, parsedParams);
           // where절 세팅
            //parsedParams.fbParams.where["[Location].[Location Type]"] = "DC";

            var result = coCommon.selectList(dims, [], coUtil.fn_makeWhere(parsedParams), "", parsedParams.fbParams.limit);
            //coCommon.printCsData(result, 3);
            var comboList = coCommon.fn_makeCombo(result, {DimName : "Project", DimAttbName : "Project", Sort : "DisplayName",
                                                    includeField : parsedParams.fbParams.includeField, existAll : parsedParams.fbParams.existAll});
            coCommon.debug("ComboData : " + JSON.stringify(comboList.slice(0,3)));

            coCommon.programEnd();

            return { "Code" : 0, "Msg" : "", "Rows" : comboList };
        } catch ( e ) {
            coCommon.error(e.message);
            return { "Code" : -1, "Msg" : e.message };
        }
    };


    /* ********************************************************************************** */
    // { "fbFuncName" : "fn_cb_projectProduct" }
    // projectProductNameCombo
    var fn_cb_projectProduct = function(parsedParams){
        const coCommon = new commonLib.COCommon(programName + "." + arguments.callee.name);
        coCommon.setLogLevel("Debug"); 

		  try {
//		    var dims = ['&NSUIToLocationDC'];
 		    var dims = ['[Project].[Project Product].filter(~(#.Name =="-"))'];

		    // Casecade 를 위해서 Dimension 추가
		    dims = coUtil.fn_addincludeField(dims, parsedParams);
           // where절 세팅
            //parsedParams.fbParams.where["[Location].[Location Type]"] = "DC";

            var result = coCommon.selectList(dims, [], coUtil.fn_makeWhere(parsedParams), "", parsedParams.fbParams.limit);
            //coCommon.printCsData(result, 3);
            var comboList = coCommon.fn_makeCombo(result, {DimName : "Project", DimAttbName : "Project Product", Sort : "DisplayName",
                                                    includeField : parsedParams.fbParams.includeField, existAll : parsedParams.fbParams.existAll});
            coCommon.debug("ComboData : " + JSON.stringify(comboList.slice(0,3)));

            coCommon.programEnd();

            return { "Code" : 0, "Msg" : "", "Rows" : comboList };
        } catch ( e ) {
            coCommon.error(e.message);
            return { "Code" : -1, "Msg" : e.message };
        }
    };


    /* ********************************************************************************** */
    // { "fbFuncName" : "fn_cb_projectPrdGrp" }
    // projectProductGroupNameCombo
    var fn_cb_projectPrdGrp = function(parsedParams){
        const coCommon = new commonLib.COCommon(programName + "." + arguments.callee.name);
        coCommon.setLogLevel("Debug"); 

		  try {
//		    var dims = ['&NSUIToLocationDC'];
 		    var dims = ['[Project].[Project Product Group].filter(~(#.Name =="-"))'];

		    // Casecade 를 위해서 Dimension 추가
		    dims = coUtil.fn_addincludeField(dims, parsedParams);
           // where절 세팅
            //parsedParams.fbParams.where["[Location].[Location Type]"] = "DC";

            var result = coCommon.selectList(dims, [], coUtil.fn_makeWhere(parsedParams), "", parsedParams.fbParams.limit);
            //coCommon.printCsData(result, 3);
            var comboList = coCommon.fn_makeCombo(result, {DimName : "Project", DimAttbName : "Project Product Group", Sort : "DisplayName",
                                                    includeField : parsedParams.fbParams.includeField, existAll : parsedParams.fbParams.existAll});
            coCommon.debug("ComboData : " + JSON.stringify(comboList.slice(0,3)));

            coCommon.programEnd();

            return { "Code" : 0, "Msg" : "", "Rows" : comboList };
        } catch ( e ) {
            coCommon.error(e.message);
            return { "Code" : -1, "Msg" : e.message };
        }
    };


    /* ********************************************************************************** */
    // { "fbFuncName" : "fn_cb_regionDC" }
    // regionDCNameCombo
    var fn_cb_regionDC = function(parsedParams){
        const coCommon = new commonLib.COCommon(programName + "." + arguments.callee.name);
        coCommon.setLogLevel("Debug"); 

		  try {
//		    var dims = ['&NSUIToLocationDC'];
 		    var dims = ['[Location].[Region].filter(~(#.Name =="-"))'];

		    // Casecade 를 위해서 Dimension 추가
		    dims = coUtil.fn_addincludeField(dims, parsedParams);
           // where절 세팅
            parsedParams.fbParams.where["[Location].[Location Type]"] = "DC";

            var result = coCommon.selectList(dims, [], coUtil.fn_makeWhere(parsedParams), "", parsedParams.fbParams.limit);
            //coCommon.printCsData(result, 3);
            var comboList = coCommon.fn_makeCombo(result, {DimName : "Location", DimAttbName : "Region", Sort : "DisplayName",
                                                    includeField : parsedParams.fbParams.includeField, existAll : parsedParams.fbParams.existAll});
            coCommon.debug("ComboData : " + JSON.stringify(comboList.slice(0,3)));

            coCommon.programEnd();

            return { "Code" : 0, "Msg" : "", "Rows" : comboList };
        } catch ( e ) {
            coCommon.error(e.message);
            return { "Code" : -1, "Msg" : e.message };
        }
    };

    /* ********************************************************************************** */
    // { "fbFuncName" : "fn_cb_plShotReason" }
    // shotReasonCombo
    var fn_cb_plShotReason = function(parsedParams){
        const coCommon = new commonLib.COCommon(programName + "." + arguments.callee.name);
        coCommon.setLogLevel("Debug"); 

        try {
            var comboList = coCommon.fn_makeCombo(null, {ComboCodes : ["AGING_STOCK","BBOM_DELAYED","BOD_CAPACITY","BOD_EFFECTIVENESS","BOM_EFFECTIVENESS","CH_CONSTRAINT","CONSENSUS_ERROR","DBOM_DELAYED","DEV_DELAYED","DP_AVAIL_UN","DP_UNBALANCE","EMPTY_BOM","EOL","EOL_CAPACITY","EOL_CAPOVER","EOL_MATERIAL","FACTORY_HOLIDAY","FIXED","FIXED_SOP","FROZEN","F_CAPACITY_SHORTAGE","F_DEV_DELAYED","F_DP_UNBALANCE","F_INVENTORY_ADJUST","F_LC_DELAY","F_LOTSIZE","F_MASTERDATA_ERROR","F_MATERIAL","F_PRE_BUILD","F_PROFIT_ADJUST","F_QUALITY_PROBLEM","F_REDUCTION_REQUEST","F_SALES_REQUEST","F_SOP_FIXED","F_TOOL_CAPACITY","F_TPMODE","HDMI","INVENTORY_ADJUSTMENT","JDM_CAPOVER","LINE_CAPACITY","MARKETING_SPEC","MATERIAL","MATERIAL_SHORT","MAT_APPROV_DELAYED","MBOM_DELAYED","NEW_BOM","NEW_FCST","NEW_FCST_FROZEN","NEW_MODEL","NO_BOD","NO_BOM","NO_BULK_STOCK","NO_PAYMENT","NO_REASON","NO_ROUTING","NPI_CAPACITY","PBC","PLANNED_EOL","PRE_CONSTRAINT","QUALITY_PROBLEM","RAMPUP_PLAN","RELEASED","RTF_EXP","SELLER_PREALLOC","SHIP_DELAY","SHORT_RMA","SOFT_PLAN_DELAYED","SOP_FIXED","SUPPLY_CHANGE","TOOL_CAPACITY"], ComboValues : ["AGING_STOCK","BBOM_DELAYED","BOD_CAPACITY","BOD_EFFECTIVENESS","BOM_EFFECTIVENESS","CH_CONSTRAINT","CONSENSUS_ERROR","DBOM_DELAYED","DEV_DELAYED","DP_AVAIL_UN","DP_UNBALANCE","EMPTY_BOM","EOL","EOL_CAPACITY","EOL_CAPOVER","EOL_MATERIAL","FACTORY_HOLIDAY","FIXED","FIXED_SOP","FROZEN","F_CAPACITY_SHORTAGE","F_DEV_DELAYED","F_DP_UNBALANCE","F_INVENTORY_ADJUST","F_LC_DELAY","F_LOTSIZE","F_MASTERDATA_ERROR","F_MATERIAL","F_PRE_BUILD","F_PROFIT_ADJUST","F_QUALITY_PROBLEM","F_REDUCTION_REQUEST","F_SALES_REQUEST","F_SOP_FIXED","F_TOOL_CAPACITY","F_TPMODE","HDMI","INVENTORY_ADJUSTMENT","JDM_CAPOVER","LINE_CAPACITY","MARKETING_SPEC","MATERIAL","MATERIAL_SHORT","MAT_APPROV_DELAYED","MBOM_DELAYED","NEW_BOM","NEW_FCST","NEW_FCST_FROZEN","NEW_MODEL","NO_BOD","NO_BOM","NO_BULK_STOCK","NO_PAYMENT","NO_REASON","NO_ROUTING","NPI_CAPACITY","PBC","PLANNED_EOL","PRE_CONSTRAINT","QUALITY_PROBLEM","RAMPUP_PLAN","RELEASED","RTF_EXP","SELLER_PREALLOC","SHIP_DELAY","SHORT_RMA","SOFT_PLAN_DELAYED","SOP_FIXED","SUPPLY_CHANGE","TOOL_CAPACITY"]});
            coCommon.debug("ComboData : " + JSON.stringify(comboList.slice(0,3)));

            coCommon.programEnd();

            return { "Code" : 0, "Msg" : "", "Rows" : comboList };
        } catch ( e ) {
            coCommon.error(e.message);
            return { "Code" : -1, "Msg" : e.message };
        }
    };




    /* ********************************************************************************** */
    // { "fbFuncName" : "fn_cb_salesShipTo" }
    // salesShipToCombo
    var fn_cb_salesShipTo = function(parsedParams){
        const coCommon = new commonLib.COCommon(programName + "." + arguments.callee.name);
        coCommon.setLogLevel("Debug");

		try {
//		    var dims = ['&NSUIToLocationDC'];
 		    var dims = ['[Sales Domain].[Ship To]'];

		    // Casecade 를 위해서 Dimension 추가
		    dims = coUtil.fn_addincludeField(dims, parsedParams);
           // where절 세팅
            //parsedParams.fbParams.where["[Location].[Location Type]"] = "DC";

            var result = coCommon.selectList(dims, [], coUtil.fn_makeWhere(parsedParams), "", parsedParams.fbParams.limit);
            //coCommon.printCsData(result, 3);
            var comboList = coCommon.fn_makeCombo(result, {DimName : "Sales Domain", DimAttbName : "Ship To", Sort : "DisplayName",
                                                    includeField : parsedParams.fbParams.includeField, existAll : parsedParams.fbParams.existAll});
            coCommon.debug("ComboData : " + JSON.stringify(comboList.slice(0,3)));

            coCommon.programEnd();

            return { "Code" : 0, "Msg" : "", "Rows" : comboList };
        } catch ( e ) {
            coCommon.error(e.message);
            return { "Code" : -1, "Msg" : e.message };
        }
    };

			
    /* ********************************************************************************** */
    // { "fbFuncName" : "fn_cb_salesID" }
    // salesIDCombo
    var fn_cb_salesID = function(parsedParams){
        const coCommon = new commonLib.COCommon(programName + "." + arguments.callee.name);
        coCommon.setLogLevel("Debug");

		try {
//		    var dims = ['&NSUIToLocationDC'];
 		    var dims = ['[Sales Domain].[Sales ID]'];

		    // Casecade 를 위해서 Dimension 추가
		    dims = coUtil.fn_addincludeField(dims, parsedParams);
           // where절 세팅
            //parsedParams.fbParams.where["[Location].[Location Type]"] = "DC";

            var result = coCommon.selectList(dims, [], coUtil.fn_makeWhere(parsedParams), "", parsedParams.fbParams.limit);
            //coCommon.printCsData(result, 3);
            var comboList = coCommon.fn_makeCombo(result, {DimName : "Sales Domain", DimAttbName : "Sales ID", Sort : "DisplayName",
                                                    includeField : parsedParams.fbParams.includeField, existAll : parsedParams.fbParams.existAll});
            coCommon.debug("ComboData : " + JSON.stringify(comboList.slice(0,3)));

            coCommon.programEnd();

            return { "Code" : 0, "Msg" : "", "Rows" : comboList };
        } catch ( e ) {
            coCommon.error(e.message);
            return { "Code" : -1, "Msg" : e.message };
        }
    };

    /* ********************************************************************************** */
    // { "fbFuncName" : "fn_cb_salesName" }
    // salesNameCombo
    var fn_cb_salesName = function(parsedParams){
        const coCommon = new commonLib.COCommon(programName + "." + arguments.callee.name);
        coCommon.setLogLevel("Debug");

		try {
//		    var dims = ['&NSUIToLocationDC'];
 		    var dims = ['[Sales Domain].[Ship To]'];

		    // Casecade 를 위해서 Dimension 추가
		    dims = coUtil.fn_addincludeField(dims, parsedParams);
           // where절 세팅
            //parsedParams.fbParams.where["[Location].[Location Type]"] = "DC";

            var result = coCommon.selectList(dims, [], coUtil.fn_makeWhere(parsedParams), "", parsedParams.fbParams.limit);
            //coCommon.printCsData(result, 3);
            var comboList = coCommon.fn_makeCombo(result, {DimName : "Sales Domain", DimAttbName : "Ship To", Sort : "DisplayName",
                                                    includeField : parsedParams.fbParams.includeField, existAll : parsedParams.fbParams.existAll});
            coCommon.debug("ComboData : " + JSON.stringify(comboList.slice(0,3)));

            coCommon.programEnd();

            return { "Code" : 0, "Msg" : "", "Rows" : comboList };
        } catch ( e ) {
            coCommon.error(e.message);
            return { "Code" : -1, "Msg" : e.message };
        }
    };


    /* ********************************************************************************** */
    // { "fbFuncName" : "fn_cb_salesLv1" }
    // salesLv1combo
    var fn_cb_salesLv1 = function(parsedParams){
        const coCommon = new commonLib.COCommon(programName + "." + arguments.callee.name);
        coCommon.setLogLevel("Debug");

		try {
//		    var dims = ['&NSUIToLocationDC'];
 		    var dims = ['[Sales Domain].[Sales Lv1]','[Sales Domain].[Sales Lv1 Name]'];

		    // Casecade 를 위해서 Dimension 추가
		    dims = coUtil.fn_addincludeField(dims, parsedParams);
           // where절 세팅
            //parsedParams.fbParams.where["[Location].[Location Type]"] = "DC";

            var result = coCommon.selectList(dims, [], coUtil.fn_makeWhere(parsedParams), "", parsedParams.fbParams.limit);
            //coCommon.printCsData(result, 3);
            var comboList = coCommon.fn_makeCombo(result, {DimName : "Sales Domain", DimAttbName : "Sales Lv1", DimDisplayAttbName : "Sales Lv1 Name",Sort : "DisplayName",
                                                    includeField : parsedParams.fbParams.includeField, existAll : parsedParams.fbParams.existAll});
            coCommon.debug("ComboData : " + JSON.stringify(comboList.slice(0,3)));

            coCommon.programEnd();

            return { "Code" : 0, "Msg" : "", "Rows" : comboList };
        } catch ( e ) {
            coCommon.error(e.message);
            return { "Code" : -1, "Msg" : e.message };
        }
    };


    /* ********************************************************************************** */
    // { "fbFuncName" : "fn_cb_salesLv1ID" }
    // salesLv1IDCombo
    var fn_cb_salesLv1ID = function(parsedParams){
        const coCommon = new commonLib.COCommon(programName + "." + arguments.callee.name);
        coCommon.setLogLevel("Debug");

		try {
//		    var dims = ['&NSUIToLocationDC'];
 		    var dims = ['[Sales Domain].[Sales Lv1]'];

		    // Casecade 를 위해서 Dimension 추가
		    dims = coUtil.fn_addincludeField(dims, parsedParams);
           // where절 세팅
            //parsedParams.fbParams.where["[Location].[Location Type]"] = "DC";

            var result = coCommon.selectList(dims, [], coUtil.fn_makeWhere(parsedParams), "", parsedParams.fbParams.limit);
            //coCommon.printCsData(result, 3);
            var comboList = coCommon.fn_makeCombo(result, {DimName : "Sales Domain", DimAttbName : "Sales Lv1", Sort : "DisplayName",
                                                    includeField : parsedParams.fbParams.includeField, existAll : parsedParams.fbParams.existAll});
            coCommon.debug("ComboData : " + JSON.stringify(comboList.slice(0,3)));

            coCommon.programEnd();

            return { "Code" : 0, "Msg" : "", "Rows" : comboList };
        } catch ( e ) {
            coCommon.error(e.message);
            return { "Code" : -1, "Msg" : e.message };
        }
    };

    /* ********************************************************************************** */
    // { "fbFuncName" : "fn_cb_salesLv1Name" }
    // salesLv1NameCombo
    var fn_cb_salesLv1Name = function(parsedParams){
        const coCommon = new commonLib.COCommon(programName + "." + arguments.callee.name);
        coCommon.setLogLevel("Debug");

		try {
//		    var dims = ['&NSUIToLocationDC'];
 		    var dims = ['[Sales Domain].[Sales Lv1 Name]'];

		    // Casecade 를 위해서 Dimension 추가
		    dims = coUtil.fn_addincludeField(dims, parsedParams);
           // where절 세팅
            //parsedParams.fbParams.where["[Location].[Location Type]"] = "DC";

            var result = coCommon.selectList(dims, [], coUtil.fn_makeWhere(parsedParams), "", parsedParams.fbParams.limit);
            //coCommon.printCsData(result, 3);
            var comboList = coCommon.fn_makeCombo(result, {DimName : "Sales Domain", DimAttbName : "Sales Lv1 Name", Sort : "DisplayName",
                                                    includeField : parsedParams.fbParams.includeField, existAll : parsedParams.fbParams.existAll});
            coCommon.debug("ComboData : " + JSON.stringify(comboList.slice(0,3)));

            coCommon.programEnd();

            return { "Code" : 0, "Msg" : "", "Rows" : comboList };
        } catch ( e ) {
            coCommon.error(e.message);
            return { "Code" : -1, "Msg" : e.message };
        }
    };
		

    /* ********************************************************************************** */
    /*
    {
      "fbFuncName": "fn_cb_salesLv2",
      "fbParams": {
        "filters": {
          "[Sales Domain].[All Sales Domain]": {
            "SelectedMembers": [
              "All"
            ],
            "MemberFilter": ""
          },
          "[Sales Domain].[Sales Std1]": {
            "SelectedMembers": [
              "RH000225",
              "RH000201",
              "RH000202",
              "RH000203",
              "RH000206",
              "RH000207",
              "RH000205",
              "RH000208",
              "RH000209",
              "RH000210",
              "RH000221",
              "RH000226",
              "RH000211"
            ],
            "MemberFilter": "&NSUINewSalesStd1View"
          },
          "[Sales Domain].[Sales Std2]": {
            "SelectedMembers": [],
            "MemberFilter": "&NSUINewSalesStd2View"
          },
          "[Sales Domain].[Sales Std3]": {
            "SelectedMembers": [],
            "MemberFilter": "&NSUINewSalesStd3View"
          },
          "[Sales Domain].[Sales Std4]": {
            "SelectedMembers": [],
            "MemberFilter": "&NSUINewSalesStd4View"
          },
          "[Sales Domain].[Sales Std5]": {
            "SelectedMembers": [],
            "MemberFilter": "&NSUINewSalesStd5View"
          },
          "[Version].[Version Name]": {
            "SelectedMembers": [
              "CurrentWorkingView"
            ],
            "MemberFilter": "&CWV"
          }
        }
      }
    }
    */
    // salesLv2combo
    var fn_cb_salesLv2 = function(parsedParams){
        const coCommon = new commonLib.COCommon(programName + "." + arguments.callee.name);
        coCommon.setLogLevel("Debug");

		try {
//		    var dims = ['&NSUIToLocationDC'];
// 		    var dims = ['[Sales Domain].[Sales Lv2]','[Sales Domain].[Sales Lv2 Name]'];
			var dims = ['&NSUISalesLv2View','[Sales Domain].[Sales Lv2 Name]']; // 251028 jaemin

            // Casecade 를 위해서 Dimension 추가
		    dims = coUtil.fn_addincludeField(dims, parsedParams);

            // where절 세팅
            const salesStd1SelectedMembers = parsedParams.fbParams.filters["[Sales Domain].[Sales Std1]"].SelectedMembers.join(",");
            const additionalWhere = `${salesStd1SelectedMembers.length > 0 ? `[Sales Domain].[Sales Std1].filter(#.Name in {${salesStd1SelectedMembers}})` : ""}`;

            var result = coCommon.selectList(dims, [], coUtil.fn_makeWhere(parsedParams, additionalWhere), "", parsedParams.fbParams.limit);
            //coCommon.printCsData(result, 3);
            var comboList = coCommon.fn_makeCombo(result, {DimName : "Sales Domain", DimAttbName : "Sales Lv2", DimDisplayAttbName : "Sales Lv2 Name",Sort : "DisplayName",
                                                    includeField : parsedParams.fbParams.includeField, existAll : parsedParams.fbParams.existAll});
            coCommon.debug("ComboData : " + JSON.stringify(comboList.slice(0,3)));

            coCommon.programEnd();

            return { "Code" : 0, "Msg" : "", "Rows" : comboList };
        } catch ( e ) {
            coCommon.error(e.message);
            return { "Code" : -1, "Msg" : e.message };
        }
    };

		
    /* ********************************************************************************** */
    // { "fbFuncName" : "fn_cb_salesLv2ID" }
    // salesLv2IDCombo
    var fn_cb_salesLv2ID = function(parsedParams){
        const coCommon = new commonLib.COCommon(programName + "." + arguments.callee.name);
        coCommon.setLogLevel("Debug");

		try {
//		    var dims = ['&NSUIToLocationDC'];
// 		    var dims = ['[Sales Domain].[Sales Lv2]'];
			var dims = ['&NSUISalesLv2View']; // 251028 jaemin

		    // Casecade 를 위해서 Dimension 추가
		    dims = coUtil.fn_addincludeField(dims, parsedParams);
           // where절 세팅
            //parsedParams.fbParams.where["[Location].[Location Type]"] = "DC";

            var result = coCommon.selectList(dims, [], coUtil.fn_makeWhere(parsedParams), "", parsedParams.fbParams.limit);
            //coCommon.printCsData(result, 3);
            var comboList = coCommon.fn_makeCombo(result, {DimName : "Sales Domain", DimAttbName : "Sales Lv2", Sort : "DisplayName",
                                                    includeField : parsedParams.fbParams.includeField, existAll : parsedParams.fbParams.existAll});
            coCommon.debug("ComboData : " + JSON.stringify(comboList.slice(0,3)));

            coCommon.programEnd();

            return { "Code" : 0, "Msg" : "", "Rows" : comboList };
        } catch ( e ) {
            coCommon.error(e.message);
            return { "Code" : -1, "Msg" : e.message };
        }
    };

    /* ********************************************************************************** */
    // { "fbFuncName" : "fn_cb_salesLv2Name" }
    // salesLv2NameCombo
    var fn_cb_salesLv2Name = function(parsedParams){
        const coCommon = new commonLib.COCommon(programName + "." + arguments.callee.name);
        coCommon.setLogLevel("Debug");

		try {
//		    var dims = ['&NSUIToLocationDC'];
 		    var dims = ['[Sales Domain].[Sales Lv2 Name]'];

		    // Casecade 를 위해서 Dimension 추가
		    dims = coUtil.fn_addincludeField(dims, parsedParams);
           // where절 세팅
            //parsedParams.fbParams.where["[Location].[Location Type]"] = "DC";

            var result = coCommon.selectList(dims, [], coUtil.fn_makeWhere(parsedParams), "", parsedParams.fbParams.limit);
            //coCommon.printCsData(result, 3);
            var comboList = coCommon.fn_makeCombo(result, {DimName : "Sales Domain", DimAttbName : "Sales Lv2 Name", Sort : "DisplayName",
                                                    includeField : parsedParams.fbParams.includeField, existAll : parsedParams.fbParams.existAll});
            coCommon.debug("ComboData : " + JSON.stringify(comboList.slice(0,3)));

            coCommon.programEnd();

            return { "Code" : 0, "Msg" : "", "Rows" : comboList };
        } catch ( e ) {
            coCommon.error(e.message);
            return { "Code" : -1, "Msg" : e.message };
        }
    };


    /* ********************************************************************************** */
    // { "fbFuncName" : "fn_cb_salesLv3" }
    // salesLv3combo
    var fn_cb_salesLv3 = function(parsedParams){
        const coCommon = new commonLib.COCommon(programName + "." + arguments.callee.name);
        coCommon.setLogLevel("Debug");

		try {
//		    var dims = ['&NSUIToLocationDC'];
// 		    var dims = ['[Sales Domain].[Sales Lv3]','[Sales Domain].[Sales Lv3 Name]'];
			var dims = ['&NSUISalesLv3View','[Sales Domain].[Sales Lv3 Name]']; // 251028 jaemin

		    // Casecade 를 위해서 Dimension 추가
		    dims = coUtil.fn_addincludeField(dims, parsedParams);

            var result = coCommon.selectList(dims, [], coUtil.fn_makeWhere(parsedParams), "", parsedParams.fbParams.limit);
            coCommon.printCsData(result, 3);

            const dimension = result.columns.dimension;
            const rows = [];
            for (let i = 0; i < result.cs.rowCount; i++) {
                const row = {};
                for (let idx = 0; idx < dimension.length; idx++) {
                    if (dimension[idx] === "Sales Domain.Sales Lv3") {
                        row["Name"] = result.cs.row(i).cell(result.cs.memberColumnIndex(dimension[idx].split(".")[0], dimension[idx].split(".")[1])).Name;
                        row["SubsType"] = coCommon.getPropertyValue(result.cs, i, dimension[idx].split(".")[0], dimension[idx].split(".")[1], "Sales Lv3 Type") || null;
                        row["Region"] = coCommon.getPropertyValue(result.cs, i, dimension[idx].split(".")[0], dimension[idx].split(".")[1], "Sales Lv3 Subsidiary Region") || null;
                    } else {
                        row["DisplayName"] = result.cs.row(i).cell(result.cs.memberColumnIndex(dimension[idx].split(".")[0], dimension[idx].split(".")[1])).Name;
                    }
                }
                rows.push(row);
            }

            coCommon.programEnd();

            return { "Code" : 0, "Msg" : "", "Rows" : rows };
        } catch ( e ) {
            coCommon.error(e.message);
            return { "Code" : -1, "Msg" : e.message };
        }
    };


    /* ********************************************************************************** */
    // { "fbFuncName" : "fn_cb_salesLv3ID" }
    // salesLv3IDCombo
    var fn_cb_salesLv3ID = function(parsedParams){
        const coCommon = new commonLib.COCommon(programName + "." + arguments.callee.name);
        coCommon.setLogLevel("Debug");

		try {
//		    var dims = ['&NSUIToLocationDC'];
// 		    var dims = ['[Sales Domain].[Sales Lv3]'];
			var dims = ['&NSUISalesLv3View']; // 251028 jaemin

		    // Casecade 를 위해서 Dimension 추가
		    dims = coUtil.fn_addincludeField(dims, parsedParams);
           // where절 세팅
            //parsedParams.fbParams.where["[Location].[Location Type]"] = "DC";

            var result = coCommon.selectList(dims, [], coUtil.fn_makeWhere(parsedParams), "", parsedParams.fbParams.limit);
            //coCommon.printCsData(result, 3);
            var comboList = coCommon.fn_makeCombo(result, {DimName : "Sales Domain", DimAttbName : "Sales Lv3", Sort : "DisplayName",
                                                    includeField : parsedParams.fbParams.includeField, existAll : parsedParams.fbParams.existAll});
            coCommon.debug("ComboData : " + JSON.stringify(comboList.slice(0,3)));

            coCommon.programEnd();

            return { "Code" : 0, "Msg" : "", "Rows" : comboList };
        } catch ( e ) {
            coCommon.error(e.message);
            return { "Code" : -1, "Msg" : e.message };
        }
    };

    /* ********************************************************************************** */
    // { "fbFuncName" : "fn_cb_salesLv3Name" }
    // salesLv3NameCombo
    var fn_cb_salesLv3Name = function(parsedParams){
        const coCommon = new commonLib.COCommon(programName + "." + arguments.callee.name);
        coCommon.setLogLevel("Debug");

		try {
//		    var dims = ['&NSUIToLocationDC'];
 		    var dims = ['[Sales Domain].[Sales Lv3 Name]'];

		    // Casecade 를 위해서 Dimension 추가
		    dims = coUtil.fn_addincludeField(dims, parsedParams);
           // where절 세팅
            //parsedParams.fbParams.where["[Location].[Location Type]"] = "DC";

            var result = coCommon.selectList(dims, [], coUtil.fn_makeWhere(parsedParams), "", parsedParams.fbParams.limit);
            //coCommon.printCsData(result, 3);
            var comboList = coCommon.fn_makeCombo(result, {DimName : "Sales Domain", DimAttbName : "Sales Lv3 Name", Sort : "DisplayName",
                                                    includeField : parsedParams.fbParams.includeField, existAll : parsedParams.fbParams.existAll});
            coCommon.debug("ComboData : " + JSON.stringify(comboList.slice(0,3)));

            coCommon.programEnd();

            return { "Code" : 0, "Msg" : "", "Rows" : comboList };
        } catch ( e ) {
            coCommon.error(e.message);
            return { "Code" : -1, "Msg" : e.message };
        }
    };

    /* ********************************************************************************** */
    // { "fbFuncName" : "fn_cb_salesLv4" }
    // salesLv4combo
    var fn_cb_salesLv4 = function(parsedParams){
        const coCommon = new commonLib.COCommon(programName + "." + arguments.callee.name);
        coCommon.setLogLevel("Debug");

		try {
//		    var dims = ['&NSUIToLocationDC'];
// 		    var dims = ['[Sales Domain].[Sales Lv4]','[Sales Domain].[Sales Lv4 Name]'];
			var dims = ['&NSUISalesLv4View','[Sales Domain].[Sales Lv4 Name]']; // 251028 jaemin

		    // Casecade 를 위해서 Dimension 추가
		    dims = coUtil.fn_addincludeField(dims, parsedParams);
           // where절 세팅
            //parsedParams.fbParams.where["[Location].[Location Type]"] = "DC";

            var result = coCommon.selectList(dims, [], coUtil.fn_makeWhere(parsedParams), "", parsedParams.fbParams.limit);
            //coCommon.printCsData(result, 3);
            var comboList = coCommon.fn_makeCombo(result, {DimName : "Sales Domain", DimAttbName : "Sales Lv4", DimDisplayAttbName : "Sales Lv4 Name", Sort : "DisplayName",
                                                    includeField : parsedParams.fbParams.includeField, existAll : parsedParams.fbParams.existAll});
            coCommon.debug("ComboData : " + JSON.stringify(comboList.slice(0,3)));

            coCommon.programEnd();

            return { "Code" : 0, "Msg" : "", "Rows" : comboList };
        } catch ( e ) {
            coCommon.error(e.message);
            return { "Code" : -1, "Msg" : e.message };
        }
    };



    /* ********************************************************************************** */
    // { "fbFuncName" : "fn_cb_salesLv4ID" }
    // salesLv4IDCombo
    var fn_cb_salesLv4ID = function(parsedParams){
        const coCommon = new commonLib.COCommon(programName + "." + arguments.callee.name);
        coCommon.setLogLevel("Debug");

		try {
//		    var dims = ['&NSUIToLocationDC'];
// 		    var dims = ['[Sales Domain].[Sales Lv4]'];
			var dims = ['&NSUISalesLv4View']; // 251028 jaemin

		    // Casecade 를 위해서 Dimension 추가
		    dims = coUtil.fn_addincludeField(dims, parsedParams);
           // where절 세팅
            //parsedParams.fbParams.where["[Location].[Location Type]"] = "DC";

            var result = coCommon.selectList(dims, [], coUtil.fn_makeWhere(parsedParams), "", parsedParams.fbParams.limit);
            //coCommon.printCsData(result, 3);
            var comboList = coCommon.fn_makeCombo(result, {DimName : "Sales Domain", DimAttbName : "Sales Lv4", Sort : "DisplayName",
                                                    includeField : parsedParams.fbParams.includeField, existAll : parsedParams.fbParams.existAll});
            coCommon.debug("ComboData : " + JSON.stringify(comboList.slice(0,3)));

            coCommon.programEnd();

            return { "Code" : 0, "Msg" : "", "Rows" : comboList };
        } catch ( e ) {
            coCommon.error(e.message);
            return { "Code" : -1, "Msg" : e.message };
        }
    };

    /* ********************************************************************************** */
    // { "fbFuncName" : "fn_cb_salesLv4Name" }
    // salesLv4NameCombo
    var fn_cb_salesLv4Name = function(parsedParams){
        const coCommon = new commonLib.COCommon(programName + "." + arguments.callee.name);
        coCommon.setLogLevel("Debug");

		try {
//		    var dims = ['&NSUIToLocationDC'];
 		    var dims = ['[Sales Domain].[Sales Lv4 Name]'];

		    // Casecade 를 위해서 Dimension 추가
		    dims = coUtil.fn_addincludeField(dims, parsedParams);
           // where절 세팅
            //parsedParams.fbParams.where["[Location].[Location Type]"] = "DC";

            var result = coCommon.selectList(dims, [], coUtil.fn_makeWhere(parsedParams), "", parsedParams.fbParams.limit);
            //coCommon.printCsData(result, 3);
            var comboList = coCommon.fn_makeCombo(result, {DimName : "Sales Domain", DimAttbName : "Sales Lv4 Name", Sort : "DisplayName",
                                                    includeField : parsedParams.fbParams.includeField, existAll : parsedParams.fbParams.existAll});
            coCommon.debug("ComboData : " + JSON.stringify(comboList.slice(0,3)));

            coCommon.programEnd();

            return { "Code" : 0, "Msg" : "", "Rows" : comboList };
        } catch ( e ) {
            coCommon.error(e.message);
            return { "Code" : -1, "Msg" : e.message };
        }
    };


    /* ********************************************************************************** */
    // { "fbFuncName" : "fn_cb_salesLv5" }
    // salesLv5combo
    var fn_cb_salesLv5 = function(parsedParams){
        const coCommon = new commonLib.COCommon(programName + "." + arguments.callee.name);
        coCommon.setLogLevel("Debug");

		try {
//		    var dims = ['&NSUIToLocationDC'];
// 		    var dims = ['[Sales Domain].[Sales Lv5]','[Sales Domain].[Sales Lv5 Name]'];
			var dims = ['&NSUISalesLv5View','[Sales Domain].[Sales Lv5 Name]']; // 251028 jaemin

		    // Casecade 를 위해서 Dimension 추가
		    dims = coUtil.fn_addincludeField(dims, parsedParams);
           // where절 세팅
            //parsedParams.fbParams.where["[Location].[Location Type]"] = "DC";

            var result = coCommon.selectList(dims, [], coUtil.fn_makeWhere(parsedParams), "", parsedParams.fbParams.limit);
            //coCommon.printCsData(result, 3);
            var comboList = coCommon.fn_makeCombo(result, {DimName : "Sales Domain", DimAttbName : "Sales Lv5", DimDisplayAttbName : "Sales Lv5 Name",Sort : "DisplayName",
                                                    includeField : parsedParams.fbParams.includeField, existAll : parsedParams.fbParams.existAll});
            coCommon.debug("ComboData : " + JSON.stringify(comboList.slice(0,3)));

            coCommon.programEnd();

            return { "Code" : 0, "Msg" : "", "Rows" : comboList };
        } catch ( e ) {
            coCommon.error(e.message);
            return { "Code" : -1, "Msg" : e.message };
        }
    };




    /* ********************************************************************************** */
    // { "fbFuncName" : "fn_cb_salesLv5ID" }
    // salesLv5IDCombo
    var fn_cb_salesLv5ID = function(parsedParams){
        const coCommon = new commonLib.COCommon(programName + "." + arguments.callee.name);
        coCommon.setLogLevel("Debug");

		try {
//		    var dims = ['&NSUIToLocationDC'];
// 		    var dims = ['[Sales Domain].[Sales Lv5]'];
			var dims = ['&NSUISalesLv5View']; // 251028 jaemin

		    // Casecade 를 위해서 Dimension 추가
		    dims = coUtil.fn_addincludeField(dims, parsedParams);
           // where절 세팅
            //parsedParams.fbParams.where["[Location].[Location Type]"] = "DC";

            var result = coCommon.selectList(dims, [], coUtil.fn_makeWhere(parsedParams), "", parsedParams.fbParams.limit);
            //coCommon.printCsData(result, 3);
            var comboList = coCommon.fn_makeCombo(result, {DimName : "Sales Domain", DimAttbName : "Sales Lv5", Sort : "DisplayName",
                                                    includeField : parsedParams.fbParams.includeField, existAll : parsedParams.fbParams.existAll});
            coCommon.debug("ComboData : " + JSON.stringify(comboList.slice(0,3)));

            coCommon.programEnd();

            return { "Code" : 0, "Msg" : "", "Rows" : comboList };
        } catch ( e ) {
            coCommon.error(e.message);
            return { "Code" : -1, "Msg" : e.message };
        }
    };

    /* ********************************************************************************** */
    // { "fbFuncName" : "fn_cb_salesLv5Name" }
    // salesLv5NameCombo
    var fn_cb_salesLv5Name = function(parsedParams){
        const coCommon = new commonLib.COCommon(programName + "." + arguments.callee.name);
        coCommon.setLogLevel("Debug");

		try {
//		    var dims = ['&NSUIToLocationDC'];
 		    var dims = ['[Sales Domain].[Sales Lv5 Name]'];

		    // Casecade 를 위해서 Dimension 추가
		    dims = coUtil.fn_addincludeField(dims, parsedParams);
           // where절 세팅
            //parsedParams.fbParams.where["[Location].[Location Type]"] = "DC";

            var result = coCommon.selectList(dims, [], coUtil.fn_makeWhere(parsedParams), "", parsedParams.fbParams.limit);
            //coCommon.printCsData(result, 3);
            var comboList = coCommon.fn_makeCombo(result, {DimName : "Sales Domain", DimAttbName : "Sales Lv5 Name", Sort : "DisplayName",
                                                    includeField : parsedParams.fbParams.includeField, existAll : parsedParams.fbParams.existAll});
            coCommon.debug("ComboData : " + JSON.stringify(comboList.slice(0,3)));

            coCommon.programEnd();

            return { "Code" : 0, "Msg" : "", "Rows" : comboList };
        } catch ( e ) {
            coCommon.error(e.message);
            return { "Code" : -1, "Msg" : e.message };
        }
    };

    
		
    /* ********************************************************************************** */
    // { "fbFuncName" : "fn_cb_salesLv6" }
    // salesLv6combo
    var fn_cb_salesLv6 = function(parsedParams){
        const coCommon = new commonLib.COCommon(programName + "." + arguments.callee.name);
        coCommon.setLogLevel("Debug");

		try {
//		    var dims = ['&NSUIToLocationDC'];
// 		    var dims = ['[Sales Domain].[Sales Lv6]','[Sales Domain].[Sales Lv6 Name]'];
			var dims = ['&NSUISalesLv6View','[Sales Domain].[Sales Lv6 Name]']; // 251028 jaemin

		    // Casecade 를 위해서 Dimension 추가
		    dims = coUtil.fn_addincludeField(dims, parsedParams);
           // where절 세팅
            //parsedParams.fbParams.where["[Location].[Location Type]"] = "DC";

            var result = coCommon.selectList(dims, [], coUtil.fn_makeWhere(parsedParams), "", parsedParams.fbParams.limit);
            //coCommon.printCsData(result, 3);
            var comboList = coCommon.fn_makeCombo(result, {DimName : "Sales Domain", DimAttbName : "Sales Lv6", DimDisplayAttbName : "Sales Lv6 Name",Sort : "DisplayName",
                                                    includeField : parsedParams.fbParams.includeField, existAll : parsedParams.fbParams.existAll});
            coCommon.debug("ComboData : " + JSON.stringify(comboList.slice(0,3)));

            coCommon.programEnd();

            return { "Code" : 0, "Msg" : "", "Rows" : comboList };
        } catch ( e ) {
            coCommon.error(e.message);
            return { "Code" : -1, "Msg" : e.message };
        }
    };
		
		
		
		
		
		/* ********************************************************************************** */
    // { "fbFuncName" : "fn_cb_salesLv6ID" }
    // salesLv6IDCombo
    var fn_cb_salesLv6ID = function(parsedParams){
        const coCommon = new commonLib.COCommon(programName + "." + arguments.callee.name);
        coCommon.setLogLevel("Debug");

		try {
//		    var dims = ['&NSUIToLocationDC'];
// 		    var dims = ['[Sales Domain].[Sales Lv6]'];
			var dims = ['&NSUISalesLv6View']; // 251028 jaemin
			
		    // Casecade 를 위해서 Dimension 추가
		    dims = coUtil.fn_addincludeField(dims, parsedParams);
           // where절 세팅
            //parsedParams.fbParams.where["[Location].[Location Type]"] = "DC";

            var result = coCommon.selectList(dims, [], coUtil.fn_makeWhere(parsedParams), "", parsedParams.fbParams.limit);
            //coCommon.printCsData(result, 3);
            var comboList = coCommon.fn_makeCombo(result, {DimName : "Sales Domain", DimAttbName : "Sales Lv6", Sort : "DisplayName",
                                                    includeField : parsedParams.fbParams.includeField, existAll : parsedParams.fbParams.existAll});
            coCommon.debug("ComboData : " + JSON.stringify(comboList.slice(0,3)));

            coCommon.programEnd();

            return { "Code" : 0, "Msg" : "", "Rows" : comboList };
        } catch ( e ) {
            coCommon.error(e.message);
            return { "Code" : -1, "Msg" : e.message };
        }
    };

    /* ********************************************************************************** */
    // { "fbFuncName" : "fn_cb_salesLv6Name" }
    // salesLv6NameCombo
    var fn_cb_salesLv6Name = function(parsedParams){
        const coCommon = new commonLib.COCommon(programName + "." + arguments.callee.name);
        coCommon.setLogLevel("Debug");

		try {
//		    var dims = ['&NSUIToLocationDC'];
 		    var dims = ['[Sales Domain].[Sales Lv6 Name]'];

		    // Casecade 를 위해서 Dimension 추가
		    dims = coUtil.fn_addincludeField(dims, parsedParams);
           // where절 세팅
            //parsedParams.fbParams.where["[Location].[Location Type]"] = "DC";

            var result = coCommon.selectList(dims, [], coUtil.fn_makeWhere(parsedParams), "", parsedParams.fbParams.limit);
            //coCommon.printCsData(result, 3);
            var comboList = coCommon.fn_makeCombo(result, {DimName : "Sales Domain", DimAttbName : "Sales Lv6 Name", Sort : "DisplayName",
                                                    includeField : parsedParams.fbParams.includeField, existAll : parsedParams.fbParams.existAll});
            coCommon.debug("ComboData : " + JSON.stringify(comboList.slice(0,3)));

            coCommon.programEnd();

            return { "Code" : 0, "Msg" : "", "Rows" : comboList };
        } catch ( e ) {
            coCommon.error(e.message);
            return { "Code" : -1, "Msg" : e.message };
        }
    };


    /* ********************************************************************************** */
    // { "fbFuncName" : "fn_cb_salesLv7" }
    // salesLv7combo
    var fn_cb_salesLv7 = function(parsedParams){
        const coCommon = new commonLib.COCommon(programName + "." + arguments.callee.name);
        coCommon.setLogLevel("Debug");

		try {
//		    var dims = ['&NSUIToLocationDC'];
// 		    var dims = ['[Sales Domain].[Sales Lv7]','[Sales Domain].[Sales Lv7 Name]'];
			var dims = ['&NSUISalesLv7View','[Sales Domain].[Sales Lv7 Name]']; // 251028 jaemin

		    // Casecade 를 위해서 Dimension 추가
		    dims = coUtil.fn_addincludeField(dims, parsedParams);
           // where절 세팅
            //parsedParams.fbParams.where["[Location].[Location Type]"] = "DC";

            var result = coCommon.selectList(dims, [], coUtil.fn_makeWhere(parsedParams), "", parsedParams.fbParams.limit);
            //coCommon.printCsData(result, 3);
            var comboList = coCommon.fn_makeCombo(result, {DimName : "Sales Domain", DimAttbName : "Sales Lv7", DimDisplayAttbName : "Sales Lv7 Name",Sort : "DisplayName",
                                                    includeField : parsedParams.fbParams.includeField, existAll : parsedParams.fbParams.existAll});
            coCommon.debug("ComboData : " + JSON.stringify(comboList.slice(0,3)));

            coCommon.programEnd();

            return { "Code" : 0, "Msg" : "", "Rows" : comboList };
        } catch ( e ) {
            coCommon.error(e.message);
            return { "Code" : -1, "Msg" : e.message };
        }
    };




    /* ********************************************************************************** */
    // { "fbFuncName" : "fn_cb_salesLv7ID" }
    // salesLv7IDCombo
    var fn_cb_salesLv7ID = function(parsedParams){
        const coCommon = new commonLib.COCommon(programName + "." + arguments.callee.name);
        coCommon.setLogLevel("Debug");

		try {
//		    var dims = ['&NSUIToLocationDC'];
// 		    var dims = ['[Sales Domain].[Sales Lv7]'];
			var dims = ['&NSUISalesLv7View']; // 251028 jaemin

		    // Casecade 를 위해서 Dimension 추가
		    dims = coUtil.fn_addincludeField(dims, parsedParams);
           // where절 세팅
            //parsedParams.fbParams.where["[Location].[Location Type]"] = "DC";

            var result = coCommon.selectList(dims, [], coUtil.fn_makeWhere(parsedParams), "", parsedParams.fbParams.limit);
            //coCommon.printCsData(result, 3);
            var comboList = coCommon.fn_makeCombo(result, {DimName : "Sales Domain", DimAttbName : "Sales Lv7", Sort : "DisplayName",
                                                    includeField : parsedParams.fbParams.includeField, existAll : parsedParams.fbParams.existAll});
            coCommon.debug("ComboData : " + JSON.stringify(comboList.slice(0,3)));

            coCommon.programEnd();

            return { "Code" : 0, "Msg" : "", "Rows" : comboList };
        } catch ( e ) {
            coCommon.error(e.message);
            return { "Code" : -1, "Msg" : e.message };
        }
    };

    /* ********************************************************************************** */
    // { "fbFuncName" : "fn_cb_salesLv7Name" }
    // salesLv7NameCombo
    var fn_cb_salesLv7Name = function(parsedParams){
        const coCommon = new commonLib.COCommon(programName + "." + arguments.callee.name);
        coCommon.setLogLevel("Debug");

		try {
//		    var dims = ['&NSUIToLocationDC'];
 		    var dims = ['[Sales Domain].[Sales Lv7 Name]'];

		    // Casecade 를 위해서 Dimension 추가
		    dims = coUtil.fn_addincludeField(dims, parsedParams);
           // where절 세팅
            //parsedParams.fbParams.where["[Location].[Location Type]"] = "DC";

            var result = coCommon.selectList(dims, [], coUtil.fn_makeWhere(parsedParams), "", parsedParams.fbParams.limit);
            //coCommon.printCsData(result, 3);
            var comboList = coCommon.fn_makeCombo(result, {DimName : "Sales Domain", DimAttbName : "Sales Lv7 Name", Sort : "DisplayName",
                                                    includeField : parsedParams.fbParams.includeField, existAll : parsedParams.fbParams.existAll});
            coCommon.debug("ComboData : " + JSON.stringify(comboList.slice(0,3)));

            coCommon.programEnd();

            return { "Code" : 0, "Msg" : "", "Rows" : comboList };
        } catch ( e ) {
            coCommon.error(e.message);
            return { "Code" : -1, "Msg" : e.message };
        }
    };

    /* ********************************************************************************** */
    // { "fbFuncName" : "fn_cb_salesAP0" }
    // salesLvAP0OperationCombo
    var fn_cb_salesAP0 = function(parsedParams){
        const coCommon = new commonLib.COCommon(programName + "." + arguments.callee.name);
        coCommon.setLogLevel("Debug");

		try {
//		    var dims = ['&NSUIToLocationDC'];
 		    var dims = ['[Sales Domain].[Sales Lv7 Name]'];

		    // Casecade 를 위해서 Dimension 추가
		    dims = coUtil.fn_addincludeField(dims, parsedParams);
           // where절 세팅
            //parsedParams.fbParams.where["[Location].[Location Type]"] = "DC";

            var result = coCommon.selectList(dims, [], coUtil.fn_makeWhere(parsedParams), "", parsedParams.fbParams.limit);
            //coCommon.printCsData(result, 3);
            var comboList = coCommon.fn_makeCombo(result, {DimName : "Sales Domain", DimAttbName : "Sales Lv7 Name", DimDisplayPropertyName : "Sales Lv7 AP0 Operation", Sort : "DisplayName",
                                                    includeField : parsedParams.fbParams.includeField, existAll : parsedParams.fbParams.existAll});
            coCommon.debug("ComboData : " + JSON.stringify(comboList.slice(0,3)));

            coCommon.programEnd();

            return { "Code" : 0, "Msg" : "", "Rows" : comboList };
        } catch ( e ) {
            coCommon.error(e.message);
            return { "Code" : -1, "Msg" : e.message };
        }
    };

    /* ********************************************************************************** */
    // { "fbFuncName" : "fn_cb_salesPurpose" }
    // salesLvAP0OperationCombo
    var fn_cb_salesPurpose = function(parsedParams){
        const coCommon = new commonLib.COCommon(programName + "." + arguments.callee.name);
        coCommon.setLogLevel("Debug");

		try {
 		    let dims = ['[Sales Domain].[Sales Lv7 Name]'];
		    dims = coUtil.fn_addincludeField(dims, parsedParams);

            const result = coCommon.selectList(dims, [], coUtil.fn_makeWhere(parsedParams), "", parsedParams.fbParams.limit);
            const comboList = coCommon.fn_makeCombo(result, {DimName : "Sales Domain", DimAttbName : "Sales Lv7 Name", DimDisplayPropertyName : "Sales Lv7 Name Purpose", Sort : "DisplayName",
                                                    includeField : parsedParams.fbParams.includeField, existAll : parsedParams.fbParams.existAll});
            coCommon.debug("ComboData : " + JSON.stringify(comboList.slice(0,3)));

            coCommon.programEnd();

            return { "Code" : 0, "Msg" : "", "Rows" : comboList };
        } catch ( e ) {
            coCommon.error(e.message);
            return { "Code" : -1, "Msg" : e.message };
        }
    };

   /* ********************************************************************************** */
    // { "fbFuncName" : "fn_cb_SCMType" }
    var fn_cb_SCMType = function(parsedParams){
        const coCommon = new commonLib.COCommon(programName + "." + arguments.callee.name);
        coCommon.setLogLevel("Debug"); 

        		  try {
//		    var dims = ['&NSUILocationDC'];
 		    var dims = ['[Item].[SCM Type]'];

		    // Casecade 를 위해서 Dimension 추가
		    dims = coUtil.fn_addincludeField(dims, parsedParams);
           // where절 세팅
            //parsedParams.fbParams.where["[Location].[Location Type]"] = "DC";

            var result = coCommon.selectList(dims, [], coUtil.fn_makeWhere(parsedParams), "", parsedParams.fbParams.limit);
            //coCommon.printCsData(result, 3);
            var comboList = coCommon.fn_makeCombo(result, {DimName : "Item", DimAttbName : "SCM Type", Sort : "DisplayName",
                                                    includeField : parsedParams.fbParams.includeField, existAll : parsedParams.fbParams.existAll});
            coCommon.debug("ComboData : " + JSON.stringify(comboList.slice(0,3)));

            coCommon.programEnd();

            return { "Code" : 0, "Msg" : "", "Rows" : comboList };
        } catch ( e ) {
            coCommon.error(e.message);
            return { "Code" : -1, "Msg" : e.message };
        }
    };


    /* ********************************************************************************** */
    // { "fbFuncName" : "fn_cb_salesSiteBuyer" }
    // salesSiteBuyer Combo
    var fn_cb_salesSiteBuyer = function(parsedParams){
        const coCommon = new commonLib.COCommon(programName + "." + arguments.callee.name);
        coCommon.setLogLevel("Debug");

		try {
//		    var dims = ['&NSUIToLocationDC'];
 		    var dims = ['[Buyer].[Buyer]'];

		    // Casecade 를 위해서 Dimension 추가
		    dims = coUtil.fn_addincludeField(dims, parsedParams);
           // where절 세팅
            //parsedParams.fbParams.where["[Location].[Location Type]"] = "DC";

            var result = coCommon.selectList(dims, [], coUtil.fn_makeWhere(parsedParams), "", parsedParams.fbParams.limit);
            //coCommon.printCsData(result, 3);
            var comboList = coCommon.fn_makeCombo(result, {DimName : "Buyer", DimAttbName : "Buyer", Sort : "DisplayName",
                                                    includeField : parsedParams.fbParams.includeField, existAll : parsedParams.fbParams.existAll});
            coCommon.debug("ComboData : " + JSON.stringify(comboList.slice(0,3)));

            coCommon.programEnd();

            return { "Code" : 0, "Msg" : "", "Rows" : comboList };
        } catch ( e ) {
            coCommon.error(e.message);
            return { "Code" : -1, "Msg" : e.message };
        }
    };


    /* ********************************************************************************** */
    // { "fbFuncName" : "fn_cb_siteChannelDC" }
    // ChannelsiteDCNameCombo
    var fn_cb_siteChannelDC = function(parsedParams){
        const coCommon = new commonLib.COCommon(programName + "." + arguments.callee.name);
        coCommon.setLogLevel("Debug");

		try {
//		    var dims = ['&NSUIToLocationDC'];
 		    var dims = ['[Channel Site].[Channel Site Group]'];

		    // Casecade 를 위해서 Dimension 추가
		    dims = coUtil.fn_addincludeField(dims, parsedParams);
           // where절 세팅
            parsedParams.fbParams.where["[Channel Site].[Channel Site Stage]"] = "DC";

            var result = coCommon.selectList(dims, [], coUtil.fn_makeWhere(parsedParams), "", parsedParams.fbParams.limit);
            //coCommon.printCsData(result, 3);
            var comboList = coCommon.fn_makeCombo(result, {DimName : "Channel Site", DimAttbName : "Channel Site Group", Sort : "DisplayName",
                                                    includeField : parsedParams.fbParams.includeField, existAll : parsedParams.fbParams.existAll});
            coCommon.debug("ComboData : " + JSON.stringify(comboList.slice(0,3)));

            coCommon.programEnd();

            return { "Code" : 0, "Msg" : "", "Rows" : comboList };
        } catch ( e ) {
            coCommon.error(e.message);
            return { "Code" : -1, "Msg" : e.message };
        }
    };


    /* ********************************************************************************** */
    // { "fbFuncName" : "fn_cb_siteDC" }
    // siteDCNameCombo
    var fn_cb_siteDC = function(parsedParams) {
        const coCommon = new commonLib.COCommon(programName + "." + arguments.callee.name);
        coCommon.setLogLevel("Debug");

		try {
 		    let dims = ['&NSUILocationDC'];
		    // Casecade 를 위해서 Dimension 추가
		    dims = coUtil.fn_addincludeField(dims, parsedParams);

            const whereWithFilter = coUtil.fn_makeClauseWithFilter("Location", parsedParams);
            const result = coCommon.selectList(dims, [], coUtil.fn_makeWhere(parsedParams, whereWithFilter), "", parsedParams.fbParams.limit);
            coCommon.printCsData(result, 3);

            const comboList = coCommon.fn_makeCombo(result, {DimName : "Location", DimAttbName : "Location", Sort : "DisplayName",
                                                    includeField : parsedParams.fbParams.includeField, existAll : parsedParams.fbParams.existAll});
            coCommon.debug("ComboData : " + JSON.stringify(comboList.slice(0,3)));

            coCommon.programEnd();

            return { "Code" : 0, "Msg" : "", "Rows" : comboList };
        } catch ( e ) {
            coCommon.error(e.message);
            return { "Code" : -1, "Msg" : e.message };
        }
    };


    /* ********************************************************************************** */
    // { "fbFuncName" : "fn_cb_siteMF" }
    // siteMFNameCombo
    var fn_cb_siteMF = function(parsedParams){
        const coCommon = new commonLib.COCommon(programName + "." + arguments.callee.name);
        coCommon.setLogLevel("Debug");

		try {
//		    var dims = ['&MFStageSETLocation'];
 		    var dims = ['&NSUISubLocationPlant'];

		    // Casecade 를 위해서 Dimension 추가
		    dims = coUtil.fn_addincludeField(dims, parsedParams);
           // where절 세팅
            //parsedParams.fbParams.where["[Location].[Location Type]"] = "MF";

            var result = coCommon.selectList(dims, [], coUtil.fn_makeWhere(parsedParams), "", parsedParams.fbParams.limit);
            //coCommon.printCsData(result, 3);
            var comboList = coCommon.fn_makeCombo(result, {DimName : "Sub Location", DimAttbName : "Sub Location", Sort : "DisplayName",
                                                    includeField : parsedParams.fbParams.includeField, existAll : parsedParams.fbParams.existAll});
            coCommon.debug("ComboData : " + JSON.stringify(comboList.slice(0,3)));

            coCommon.programEnd();

            return { "Code" : 0, "Msg" : "", "Rows" : comboList };
        } catch ( e ) {
            coCommon.error(e.message);
            return { "Code" : -1, "Msg" : e.message };
        }
    };
	
    /* ********************************************************************************** */
    // { "fbFuncName" : "fn_cb_plStatus" }
    // Plcklist Status Combo
    var fn_cb_plStatus = function(parsedParams){
        const coCommon = new commonLib.COCommon(programName + "." + arguments.callee.name);
        coCommon.setLogLevel("Debug"); 

        try {
            var comboList = coCommon.fn_makeCombo(null, {ComboCodes : ["","REQ","CON"], ComboValues : ["","REQ","CON"] });
            coCommon.debug("ComboData : " + JSON.stringify(comboList.slice(0,3)));

            coCommon.programEnd();

            return { "Code" : 0, "Msg" : "", "Rows" : comboList };
        } catch ( e ) {
            coCommon.error(e.message);
            return { "Code" : -1, "Msg" : e.message };
        }
    };


   /* ********************************************************************************** */
    // { "fbFuncName" : "fn_cb_ProductLevel" }
    var fn_cb_ProductLevel = function(parsedParams){
        const coCommon = new commonLib.COCommon(programName + "." + arguments.callee.name);
        coCommon.setLogLevel("Debug"); 

        try {
//		    var dims = ['&NSUILocationDC'];
 		    var dims = ['[Product Level].[Product Level]'];

		    // Casecade 를 위해서 Dimension 추가
		    dims = coUtil.fn_addincludeField(dims, parsedParams);
            // where절 세팅
            //parsedParams.fbParams.where["[Location].[Location Type]"] = "DC";

            var result = coCommon.selectList(dims, [], coUtil.fn_makeWhere(parsedParams), "", parsedParams.fbParams.limit);
            //coCommon.printCsData(result, 3);
            var comboList = coCommon.fn_makeCombo(result, {DimName : "Product Level", DimAttbName : "Product Level", Sort : "DisplayName",
                                                    includeField : parsedParams.fbParams.includeField, existAll : parsedParams.fbParams.existAll});
            coCommon.debug("ComboData : " + JSON.stringify(comboList.slice(0,3)));

            coCommon.programEnd();

            return { "Code" : 0, "Msg" : "", "Rows" : comboList };
        } catch ( e ) {
            coCommon.error(e.message);
            return { "Code" : -1, "Msg" : e.message };
        }
    };


    /* ********************************************************************************** */
    // { "fbFuncName" : "fn_cb_subsidiaryDC" }
    // subsidiaryDCNameCombo
    var fn_cb_subsidiaryDC = function(parsedParams){
        const coCommon = new commonLib.COCommon(programName + "." + arguments.callee.name);
        coCommon.setLogLevel("Debug"); 

        try {
//		    var dims = ['&NSUILocationDC'];
 		    var dims = ['&NSUILocationDC.relatedmembers([Subsidiary])'];

		    // Casecade 를 위해서 Dimension 추가
		    dims = coUtil.fn_addincludeField(dims, parsedParams);
            // where절 세팅
            parsedParams.fbParams.where["[Location].[Location Type]"] = "DC";

            var result = coCommon.selectList(dims, [], coUtil.fn_makeWhere(parsedParams), "", parsedParams.fbParams.limit);
            coCommon.printCsData(result, 3);
            
            var comboList = coCommon.fn_makeCombo(result, {DimName : "Location", DimAttbName : "Subsidiary", Sort : "DisplayName",
                                                    includeField : parsedParams.fbParams.includeField, existAll : parsedParams.fbParams.existAll});
            coCommon.debug("ComboData : " + JSON.stringify(comboList.slice(0,3)));

            coCommon.programEnd();

            return { "Code" : 0, "Msg" : "", "Rows" : comboList };
        } catch ( e ) {
            coCommon.error(e.message);
            return { "Code" : -1, "Msg" : e.message };
        }
    };


   /* ********************************************************************************** */
    // { "fbFuncName" : "fn_cb_tpMode" }
    // TPModeNameCombo
    var fn_cb_tpMode = function(parsedParams){
        const coCommon = new commonLib.COCommon(programName + "." + arguments.callee.name);
        coCommon.setLogLevel("Debug"); 

        try {
 		    var dims = ['[Activity2].[Activity2]'];

		    // Casecade 를 위해서 Dimension 추가
		    dims = coUtil.fn_addincludeField(dims, parsedParams);

            var result = coCommon.selectList(dims, [], coUtil.fn_makeWhere(parsedParams), "", parsedParams.fbParams.limit);
            coCommon.printCsData(result, 3);

            var comboList = coCommon.fn_makeCombo(result, {DimName : "Activity2", DimAttbName : "Activity2", Sort : "DisplayName",
                                                    includeField : parsedParams.fbParams.includeField, existAll : parsedParams.fbParams.existAll});
            coCommon.debug("ComboData : " + JSON.stringify(comboList.slice(0,3)));

            coCommon.programEnd();

            return { "Code" : 0, "Msg" : "", "Rows" : comboList };
        } catch ( e ) {
            coCommon.error(e.message);
            return { "Code" : -1, "Msg" : e.message };
        }
    };

    /* ********************************************************************************** */
    // { "fbFuncName" : "fn_cb_bodlist" }
    var fn_cb_bodlist = function(parsedParams) {
        const coCommon = new commonLib.COCommon(programName + "." + arguments.callee.name);
        coCommon.setLogLevel("Debug"); 

        try {
 		    let dims = ['[Activity1].[Activity1]'];
		    dims = coUtil.fn_addincludeField(dims, parsedParams);

            const result = coCommon.selectList(dims, [], coUtil.fn_makeWhere(parsedParams), "", parsedParams.fbParams.limit);
            coCommon.printCsData(result, 3);
            var comboList = coCommon.fn_makeCombo(result, {DimName : "Activity1", DimAttbName : "Activity1", Sort : "DisplayName",
                                                    includeField : parsedParams.fbParams.includeField, existAll : parsedParams.fbParams.existAll});
            coCommon.debug("ComboData : " + JSON.stringify(comboList.slice(0,3)));

            coCommon.programEnd();
            return { "Code" : 0, "Msg" : "", "Rows" : comboList };
        } catch ( e ) {
            coCommon.error(e.message);
            return { "Code" : -1, "Msg" : e.message };
        }
    };

    /* ********************************************************************************** */
    // { "fbFuncName" : "fn_cb_Item" }
    var fn_cb_Item = function(parsedParams) {
        const coCommon = new commonLib.COCommon(programName + "." + arguments.callee.name);
        coCommon.setLogLevel("Debug"); 

        try {
 		    let dims = ['[Item].[Item]'];
		    dims = coUtil.fn_addincludeField(dims, parsedParams);

            const result = coCommon.selectList(dims, [], coUtil.fn_makeWhere(parsedParams), "", parsedParams.fbParams.limit);
            coCommon.printCsData(result, 3);
            var comboList = coCommon.fn_makeCombo(result, {DimName : "Item", DimAttbName : "Item", Sort : "DisplayName",
                                                    includeField : parsedParams.fbParams.includeField, existAll : parsedParams.fbParams.existAll});
            coCommon.debug("ComboData : " + JSON.stringify(comboList.slice(0,3)));

            coCommon.programEnd();

            return { "Code" : 0, "Msg" : "", "Rows" : comboList };
        } catch ( e ) {
            coCommon.error(e.message);
            return { "Code" : -1, "Msg" : e.message };
        }
    };

    /* ********************************************************************************** */
    // { "fbFuncName" : "fn_cb_salesIDList", "fbParams" : { "limit" : 5000 } }
    var fn_cb_salesIDList = function(parsedParams) {
        const coCommon = new commonLib.COCommon(programName + "." + arguments.callee.name);
        coCommon.setLogLevel("Debug"); 

        try {
 		    let dims = ['[Sales Domain].[Ship To].filter(#.[Ship To New Flag]==true)'];
		    dims = coUtil.fn_addincludeField(dims, parsedParams);
            const where = '[Sales Domain].[Sales Stage].filter(#.Name in{"6","7"})';

            const result = coCommon.selectList(dims, [], coUtil.fn_makeWhere(parsedParams, where), "", "");
            coCommon.printCsData(result, 3);

            const dimension = result.columns.dimension;
            const rows = [];
            for (let i = 0; i < result.cs.rowCount; i++) {
                const name = result.cs.row(i).cell(result.cs.memberColumnIndex(dimension[0].split(".")[0], dimension[0].split(".")[1])).Name;
                const displayName = result.cs.row(i).cell(result.cs.memberColumnIndex(dimension[0].split(".")[0], dimension[0].split(".")[1])).DisplayName;
                rows.push({"Name": name, "DisplayName": `${displayName}(${name})`});
            }

            coCommon.programEnd();

            return { "Code" : 0, "Msg" : "", "Rows" : rows };
        } catch ( e ) {
            coCommon.error(e.message);
            return { "Code" : -1, "Msg" : e.message };
        }
    };

    /* ********************************************************************************** */
    // { "fbFuncName" : "fn_cb_salesIDInfo", "fbParams" : { "[Sales Domain].[Sales ID]" : "RH000226" } }
    var fn_cb_salesIDInfo = function(parsedParams) {
        const coCommon = new commonLib.COCommon(programName + "." + arguments.callee.name);
        coCommon.setLogLevel("Debug");
        coCommon.debug("parsedParams : " + JSON.stringify(parsedParams));

        try {
 		    let dims = [];
            dims.push(
              "[Sales Domain].[Sales ID].filter(" +
                '#.Name Startswith "CH"' +
                '|| #.Name Startswith "CO"' +
                '|| #.Name Startswith "CT"' +
                '|| #.Name Startswith "RH"' +
                '|| #.Name Startswith "SC"' +
                '|| #.Name Startswith "SU")' +
                `.[${parsedParams.fbParams['[Sales Domain].[Sales ID]']}]` +
                "* [Sales Domain].[Sales Lv2]" +
                "* [Sales Domain].[Sales Lv2 Name]" +
                "* [Sales Domain].[Sales Lv3]" +
                "* [Sales Domain].[Sales Lv3 Name]" +
                "* [Sales Domain].[Sales Lv4]" +
                "* [Sales Domain].[Sales Lv4 Name]" +
                "* [Sales Domain].[Sales Lv5]" +
                "* [Sales Domain].[Sales Lv5 Name]" +
                "* [Sales Domain].[Sales Lv6]" +
                "* [Sales Domain].[Sales Lv6 Name]"
            );
		    dims = coUtil.fn_addincludeField(dims, parsedParams);

            const memberproperties = "include memberproperties " +
              "{[Sales Domain].[Sales Lv3 Name], [Sales Lv3 Name Company Code]}" +
              "{[Sales Domain].[Sales Lv3 Name], [Sales Lv3 Name Type]}" +
              "{[Sales Domain].[Sales Lv3 Name], [Sales Lv3 Name Region]} ";
            const result = coCommon.selectList(dims, [], memberproperties + coUtil.fn_makeWhere(parsedParams), "", parsedParams.fbParams.limit);
            coCommon.printCsData(result, 3);

            const dimension = result.columns.dimension;
            const rows = [];
            for (let i = 0; i < result.cs.rowCount; i++) {
                const row = {};
                for (let idx = 0; idx < dimension.length; idx++) {
                    row[dimension[idx]] = result.cs.row(i).cell(result.cs.memberColumnIndex(dimension[idx].split(".")[0], dimension[idx].split(".")[1])).Name;
                    if (dimension[idx] === "Sales Domain.Sales Lv3 Name") {
                        row["Sales Domain.Sales Lv3 Name Company Code"] = coCommon.getPropertyValue(result.cs, i, dimension[idx].split(".")[0], dimension[idx].split(".")[1], "Sales Lv3 Name Company Code") || null;
                        row["Sales Domain.Sales Lv3 Name Type"] = coCommon.getPropertyValue(result.cs, i, dimension[idx].split(".")[0], dimension[idx].split(".")[1], "Sales Lv3 Name Type") || null;
                        row["Sales Domain.Sales Lv3 Name Region"] = coCommon.getPropertyValue(result.cs, i, dimension[idx].split(".")[0], dimension[idx].split(".")[1], "Sales Lv3 Name Region") || null;
                        
                    }
                }
                rows.push(row);
            }

            coCommon.programEnd();
            return { "Code" : 0, "Msg" : "", "Rows" : rows };
        } catch ( e ) {
            coCommon.error(e.message);
            return { "Code" : -1, "Msg" : e.message };
        }
    };

    // { "fbFuncName" : "fn_cb_FromSite" }
    var fn_cb_FromSite = function(parsedParams) {
        const coCommon = new commonLib.COCommon(programName + "." + arguments.callee.name);
        coCommon.setLogLevel("Debug"); 

        try {
 		    let dims = ['[Sub Location].[Sub Site Stage].filter(#.[Name] == "MF").relatedmembers([Sub Site ID])', '[Sub Location].[Sub Location]'];
            dims = coUtil.fn_addincludeField(dims, parsedParams);

            const whereWithFilter = coUtil.fn_makeClauseWithFilter("Sub Location", parsedParams);
            const result = coCommon.selectList(dims, [], coUtil.fn_makeWhere(parsedParams, whereWithFilter), "", "");
            coCommon.printCsData(result, 3);

            const dimension = result.columns.dimension;
            const rows = [];
            for (let i = 0; i < result.cs.rowCount; i++) {
                const row = {};
                for (let idx = 0; idx < dimension.length; idx++) {
                    if (dimension[idx] == "Sub Location.Sub Site ID") {
                        row["Name"] = result.cs.row(i).cell(result.cs.memberColumnIndex(dimension[idx].split(".")[0], dimension[idx].split(".")[1])).Name;
                        row["DisplayName"] = result.cs.row(i).cell(result.cs.memberColumnIndex(dimension[idx].split(".")[0], dimension[idx].split(".")[1])).DisplayName;
                    } else {
                        row["FromSite"] = result.cs.row(i).cell(result.cs.memberColumnIndex(dimension[idx].split(".")[0], dimension[idx].split(".")[1])).DisplayName;
                    }
                }
                rows.push(row);
            }

            coCommon.programEnd();
            return { "Code" : 0, "Msg" : "", "Rows" : rows };
        } catch ( e ) {
            coCommon.error(e.message);
            return { "Code" : -1, "Msg" : e.message };
        }
    };

    // { "fbFuncName" : "fn_cb_ToSite" }
    var fn_cb_ToSite = function(parsedParams) {
        const coCommon = new commonLib.COCommon(programName + "." + arguments.callee.name);
        coCommon.setLogLevel("Debug"); 

        try {
 		    let dims = ['[Location].[Site ID]', '[Location].[Location]'];
            dims = coUtil.fn_addincludeField(dims, parsedParams);

            const whereWithFilter = coUtil.fn_makeClauseWithFilter("Location", parsedParams);
            const result = coCommon.selectList(dims, [], coUtil.fn_makeWhere(parsedParams, whereWithFilter), "", "");
            coCommon.printCsData(result, 3);

            const dimension = result.columns.dimension;
            const rows = [];
            for (let i = 0; i < result.cs.rowCount; i++) {
                const row = {};
                for (let idx = 0; idx < dimension.length; idx++) {
                    if (dimension[idx] == "Location.Site ID") {
                        row["Name"] = result.cs.row(i).cell(result.cs.memberColumnIndex(dimension[idx].split(".")[0], dimension[idx].split(".")[1])).Name;
                        row["DisplayName"] = result.cs.row(i).cell(result.cs.memberColumnIndex(dimension[idx].split(".")[0], dimension[idx].split(".")[1])).DisplayName;
                    } else {
                        row["ToSite"] = result.cs.row(i).cell(result.cs.memberColumnIndex(dimension[idx].split(".")[0], dimension[idx].split(".")[1])).DisplayName;
                    }
                }
                rows.push(row);
            }

            coCommon.programEnd();
            return { "Code" : 0, "Msg" : "", "Rows" : rows };
        } catch ( e ) {
            coCommon.error(e.message);
            return { "Code" : -1, "Msg" : e.message };
        }
    };

    // { "fbFuncName" : "fn_cb_ProductGroup" }
    var fn_cb_ProductGroup = function(parsedParams) {
        const coCommon = new commonLib.COCommon(programName + "." + arguments.callee.name);
        coCommon.setLogLevel("Debug"); 

        try {
 		    let dims = ['[Item].[Product Group]'];
            dims = coUtil.fn_addincludeField(dims, parsedParams);

            const whereWithFilter = coUtil.fn_makeClauseWithFilter("Item", parsedParams);
            const result = coCommon.selectList(dims, [], coUtil.fn_makeWhere(parsedParams, whereWithFilter), "", parsedParams.fbParams.limit);
            coCommon.printCsData(result, 3);

            var comboList = coCommon.fn_makeCombo(result, {DimName : "Item", DimAttbName : "Product Group", Sort : "DisplayName",
                                                    includeField : parsedParams.fbParams.includeField, existAll : parsedParams.fbParams.existAll});
            coCommon.debug("ComboData : " + JSON.stringify(comboList.slice(0,3)));

            coCommon.programEnd();
            return { "Code" : 0, "Msg" : "", "Rows" : comboList };
        } catch ( e ) {
            coCommon.error(e.message);
            return { "Code" : -1, "Msg" : e.message };
        }
    };

    // { "fbFuncName" : "fn_cb_Product" }
    var fn_cb_Product = function(parsedParams) {
        const coCommon = new commonLib.COCommon(programName + "." + arguments.callee.name);
        coCommon.setLogLevel("Debug"); 

        try {
 		    let dims = ['[Item].[Product]'];
            dims = coUtil.fn_addincludeField(dims, parsedParams);
            
            const whereWithFilter = coUtil.fn_makeClauseWithFilter("Item", parsedParams);
            const result = coCommon.selectList(dims, [], coUtil.fn_makeWhere(parsedParams, whereWithFilter), "", parsedParams.fbParams.limit);
            coCommon.printCsData(result, 3);

            var comboList = coCommon.fn_makeCombo(result, {DimName : "Item", DimAttbName : "Product", Sort : "DisplayName",
                                                    includeField : parsedParams.fbParams.includeField, existAll : parsedParams.fbParams.existAll});
            coCommon.debug("ComboData : " + JSON.stringify(comboList.slice(0,3)));

            coCommon.programEnd();
            return { "Code" : 0, "Msg" : "", "Rows" : comboList };
        } catch ( e ) {
            coCommon.error(e.message);
            return { "Code" : -1, "Msg" : e.message };
        }
    };

    // { "fbFuncName" : "fn_cb_Project" }
    var fn_cb_Project = function(parsedParams) {
        const coCommon = new commonLib.COCommon(programName + "." + arguments.callee.name);
        coCommon.setLogLevel("Debug"); 

        try {
 		    let dims = ['[Item].[Project]'];
            dims = coUtil.fn_addincludeField(dims, parsedParams);

            const whereWithFilter = coUtil.fn_makeClauseWithFilter("Item", parsedParams);
            const result = coCommon.selectList(dims, [], coUtil.fn_makeWhere(parsedParams, whereWithFilter), "", parsedParams.fbParams.limit);
            coCommon.printCsData(result, 3);

            var comboList = coCommon.fn_makeCombo(result, {DimName : "Item", DimAttbName : "Project", Sort : "DisplayName",
                                                    includeField : parsedParams.fbParams.includeField, existAll : parsedParams.fbParams.existAll});
            coCommon.debug("ComboData : " + JSON.stringify(comboList.slice(0,3)));

            coCommon.programEnd();
            return { "Code" : 0, "Msg" : "", "Rows" : comboList };
        } catch ( e ) {
            coCommon.error(e.message);
            return { "Code" : -1, "Msg" : e.message };
        }
    };

    /*
    { "fbFuncName":"fn_cb_SopFixedItem",
        "fbParams": { 
            "filters": {
                "[Location].[All Location]":{"SelectedMembers":[],"MemberFilter":""},
                "[Location].[Site Org1]":{"SelectedMembers":[],"MemberFilter":"&NSUISiteOrg1DCView"},
                "[Location].[Site Org2]":{"SelectedMembers":[],"MemberFilter":"&NSUISiteOrg2DCView"},
                "[Location].[Site Org3]":{"SelectedMembers":[],"MemberFilter":"&NSUISiteOrg3DCView"},
                "[Location].[Site Org4]":{"SelectedMembers":[],"MemberFilter":"&NSUISiteOrg4DCView"},
                "[Sub Location].[All Sub Location]":{"SelectedMembers":[],"MemberFilter":""},
                "[Sub Location].[Sub Location Group3]":{"SelectedMembers":[],"MemberFilter":"&NSUISubLocGrp3MFView"},
                "[Sub Location].[Sub Location Group4]":{"SelectedMembers":[],"MemberFilter":"&NSUISubLocGrp4MFView"},
                "[Item].[Item Std1]":{"SelectedMembers":["MOBILE"],"MemberFilter":"&NSUIItemStd1View"},
                "[Item].[Item Std2]":{"SelectedMembers":["MOBILE_TABLET"],"MemberFilter":"&NSUIItemStd2View"},
                "[Item].[Item Std3]":{"SelectedMembers":["TABLET","MOBILE_TABLET_3G"],"MemberFilter":"&NSUIItemStd3View"},
                "[Item].[Item Std4]":{"SelectedMembers":["MOBILE_TABLET_3G_Galaxy Mega 6.3","MOBILE_TABLET_3G_-","MOBILE_TABLET_LTE_Galaxy Tab2 7","MOBILE_TABLET_3G_Galaxy Tab 7.0","MOBILE_TABLET_LTE_Galaxy Tab 7.7","MOBILE_TABLET_LTE_Galaxy Tab 10.1","MOBILE_TABLET_3G_Galaxy Tab 10.1"],"MemberFilter":"&NSUIItemStd4View"},
                "[Version].[Version Name]":{"SelectedMembers":["CurrentWorkingView"],"MemberFilter":"&CWV"}
            }
        }
    }
    */
    var fn_cb_SopFixedItem = function(parsedParams) {
        const coCommon = new commonLib.COCommon(programName + "." + arguments.callee.name);
        coCommon.setLogLevel("Debug"); 

        try {
 		    let dims = ['[Item].[Item]', '[Item].[SCM Type]'];
            dims = coUtil.fn_addincludeField(dims, parsedParams);
            
            const whereWithFilter = coUtil.fn_makeClauseWithFilter("Item", parsedParams);
            const result = coCommon.selectList(dims, [], coUtil.fn_makeWhere(parsedParams, whereWithFilter), "", parsedParams.fbParams.limit);
            coCommon.printCsData(result, 3);

            const dimension = result.columns.dimension;
            const rows = [];
            for (let i = 0; i < result.cs.rowCount; i++) {
                const row = {};
                for (let idx = 0; idx < dimension.length; idx++) {
                    if (dimension[idx] == "Item.Item") {
                        row["Name"] = result.cs.row(i).cell(result.cs.memberColumnIndex(dimension[idx].split(".")[0], dimension[idx].split(".")[1])).Name;
                        row["DisplayName"] = result.cs.row(i).cell(result.cs.memberColumnIndex(dimension[idx].split(".")[0], dimension[idx].split(".")[1])).DisplayName;
                    } else {
                        row["SCM Type"] = result.cs.row(i).cell(result.cs.memberColumnIndex(dimension[idx].split(".")[0], dimension[idx].split(".")[1])).DisplayName;
                    }
                }
                rows.push(row);
            }

            coCommon.programEnd();
            return { "Code" : 0, "Msg" : "", "Rows" : rows };
        } catch ( e ) {
            coCommon.error(e.message);
            return { "Code" : -1, "Msg" : e.message };
        }
    };

    // { "fbFuncName" : "fn_cb_progrpBusinessUnit" }
    var fn_cb_progrpBusinessUnit = function(parsedParams) {
        const coCommon = new commonLib.COCommon(programName + "." + arguments.callee.name);
        coCommon.setLogLevel("Debug"); 

        try {
 		    let dims = ['[Product Group].[Business Unit].filter(~(#.Name =="-"))'];
            dims = coUtil.fn_addincludeField(dims, parsedParams);
            
            const orderby = "orderby [Product Group].[Business Unit].[Business Unit Sorting Order] asc";
            const result = coCommon.selectList(dims, [], coUtil.fn_makeWhere(parsedParams), orderby, parsedParams.fbParams.limit);
            coCommon.printCsData(result, 3);

            var comboList = coCommon.fn_makeCombo(result, {DimName : "Product Group", DimAttbName : "Business Unit",
                                                    includeField : parsedParams.fbParams.includeField, existAll : parsedParams.fbParams.existAll});
            coCommon.debug("ComboData : " + JSON.stringify(comboList.slice(0,3)));

            coCommon.programEnd();
            return { "Code" : 0, "Msg" : "", "Rows" : comboList };
        } catch ( e ) {
            coCommon.error(e.message);
            return { "Code" : -1, "Msg" : e.message };
        }
    };

    // { "fbFuncName" : "fn_cb_ErpSoldtoCompany" }
    var fn_cb_ErpSoldtoCompany = function(parsedParams) {
        const coCommon = new commonLib.COCommon(programName + "." + arguments.callee.name);
        coCommon.setLogLevel("Debug"); 

        try {
 		    let dims = ['[ERP Sold to].[ERP Sold to Company]'];
            dims = coUtil.fn_addincludeField(dims, parsedParams);
            
            const result = coCommon.selectList(dims, [], coUtil.fn_makeWhere(parsedParams), "", parsedParams.fbParams.limit);
            coCommon.printCsData(result, 3);
            
            var comboList = coCommon.fn_makeCombo(result, {DimName : "ERP Sold to", DimAttbName : "ERP Sold to Company",
                                                    includeField : parsedParams.fbParams.includeField, existAll : parsedParams.fbParams.existAll});
            coCommon.debug("ComboData : " + JSON.stringify(comboList.slice(0,3)));

            coCommon.programEnd();
            return { "Code" : 0, "Msg" : "", "Rows" : comboList };
        } catch ( e ) {
            coCommon.error(e.message);
            return { "Code" : -1, "Msg" : e.message };
        }
    };

    // { "fbFuncName" : "fn_cb_ErpSoldto", "fbParams" : { "where" : { "[ERP Sold to].[ERP Sold to Company]" : "C4M6" } } }
    var fn_cb_ErpSoldto = function(parsedParams) {
        const coCommon = new commonLib.COCommon(programName + "." + arguments.callee.name);
        coCommon.setLogLevel("Debug"); 

        try {
 		    let dims = ['[ERP Sold to].[ERP Sold to Code]', '[ERP Sold to].[ERP Sold to ID]'];
            dims = coUtil.fn_addincludeField(dims, parsedParams);
            
            const result = coCommon.selectList(dims, [], coUtil.fn_makeWhere(parsedParams, ""), "", parsedParams.fbParams.limit);
            coCommon.printCsData(result, 3);

            const dimension = result.columns.dimension;
            const rows = [];
            for (let i = 0; i < result.cs.rowCount; i++) {
                const row = {};
                for (let idx = 0; idx < dimension.length; idx++) {
                    if (dimension[idx] == "ERP Sold to.ERP Sold to Code") {
                        row["Name"] = result.cs.row(i).cell(result.cs.memberColumnIndex(dimension[idx].split(".")[0], dimension[idx].split(".")[1])).Name;
                    } else {
                        row["DisplayName"] = result.cs.row(i).cell(result.cs.memberColumnIndex(dimension[idx].split(".")[0], dimension[idx].split(".")[1])).DisplayName;
                    }
                }
                rows.push(row);
            }

            coCommon.programEnd();
            return { "Code" : 0, "Msg" : "", "Rows" : rows };
        } catch ( e ) {
            coCommon.error(e.message);
            return { "Code" : -1, "Msg" : e.message };
        }
    };

    // { "fbFuncName" : "fn_cb_ErpShiptoCompany" }
    var fn_cb_ErpShiptoCompany = function(parsedParams) {
        const coCommon = new commonLib.COCommon(programName + "." + arguments.callee.name);
        coCommon.setLogLevel("Debug"); 

        try {
 		    let dims = ['[ERP Ship to].[ERP Ship to Company]'];
            dims = coUtil.fn_addincludeField(dims, parsedParams);

            const result = coCommon.selectList(dims, [], coUtil.fn_makeWhere(parsedParams), "", parsedParams.fbParams.limit);
            coCommon.printCsData(result, 3);
            
            var comboList = coCommon.fn_makeCombo(result, {DimName : "ERP Ship to", DimAttbName : "ERP Ship to Company",
                                                    includeField : parsedParams.fbParams.includeField, existAll : parsedParams.fbParams.existAll});
            coCommon.debug("ComboData : " + JSON.stringify(comboList.slice(0,3)));

            coCommon.programEnd();
            return { "Code" : 0, "Msg" : "", "Rows" : comboList };
        } catch ( e ) {
            coCommon.error(e.message);
            return { "Code" : -1, "Msg" : e.message };
        }
    };
    
    // { "fbFuncName" : "fn_cb_ErpShipto", "fbParams" : { "where" : { "[ERP Ship to].[ERP Ship to Company]" : "C4L1" } } }
    var fn_cb_ErpShipto = function(parsedParams) {
        const coCommon = new commonLib.COCommon(programName + "." + arguments.callee.name);
        coCommon.setLogLevel("Debug"); 

        try {
 		    let dims = ['[ERP Ship to].[ERP Ship to Code]', '[ERP Ship to].[ERP Ship to ID]'];
            dims = coUtil.fn_addincludeField(dims, parsedParams);
            
            const result = coCommon.selectList(dims, [], coUtil.fn_makeWhere(parsedParams), "", parsedParams.fbParams.limit);
            coCommon.printCsData(result, 3);

            const dimension = result.columns.dimension;
            const rows = [];
            for (let i = 0; i < result.cs.rowCount; i++) {
                const row = {};
                for (let idx = 0; idx < dimension.length; idx++) {
                    if (dimension[idx] == "ERP Ship to.ERP Ship to Code") {
                        row["Name"] = result.cs.row(i).cell(result.cs.memberColumnIndex(dimension[idx].split(".")[0], dimension[idx].split(".")[1])).Name;
                    } else {
                        row["DisplayName"] = result.cs.row(i).cell(result.cs.memberColumnIndex(dimension[idx].split(".")[0], dimension[idx].split(".")[1])).DisplayName;
                    }
                }
                rows.push(row);
            }

            coCommon.programEnd();
            return { "Code" : 0, "Msg" : "", "Rows" : rows };
        } catch ( e ) {
            coCommon.error(e.message);
            return { "Code" : -1, "Msg" : e.message };
        }
    };

    // { "fbFuncName" : "fb_PlanWeek" }
    var fb_PlanWeek = function(parsedParams) {
        const coCommon = new commonLib.COCommon(programName + "." + arguments.callee.name);
        coCommon.setLogLevel("Debug"); 

        try {
 		    let dims = ['&AllWeeks.filter(#.Key >= &CurrentWeek.element(0).LeadOffset(-5).Key && #.Key <= &CurrentWeek.element(0).LeadOffset(10).Key)'];
            dims = coUtil.fn_addincludeField(dims, parsedParams);

            const result = coCommon.selectList(dims, [], coUtil.fn_makeWhere(parsedParams), "", parsedParams.fbParams.limit);
            coCommon.printCsData(result, 3);
            
            var comboList = coCommon.fn_makeCombo(result, {DimName : "Time", DimAttbName : "Week",
                                                    includeField : parsedParams.fbParams.includeField, existAll : parsedParams.fbParams.existAll});
            coCommon.debug("ComboData : " + JSON.stringify(comboList.slice(0,3)));

            coCommon.programEnd();
            return { "Code" : 0, "Msg" : "", "Rows" : comboList };
        } catch ( e ) {
            coCommon.error(e.message);
            return { "Code" : -1, "Msg" : e.message };
        }
    };

    // { "fbFuncName" : "fn_cb_ChannelSite", "fbParams" : { "where" : { "[Channel Site].[Channel Site Company]" : "C290" } } }
    var fn_cb_ChannelSite = function(parsedParams) {
        const coCommon = new commonLib.COCommon(programName + "." + arguments.callee.name);
        coCommon.setLogLevel("Debug"); 

        try {
 		    let dims = ['[Channel Site].[Channel Site Name]', '[Channel Site].[Channel Site ID]'];
            dims = coUtil.fn_addincludeField(dims, parsedParams);

            const orderby = 'orderby [Channel Site].[Channel Site Name].[DisplayName] asc'
            const result = coCommon.selectList(dims, [], coUtil.fn_makeWhere(parsedParams), orderby, parsedParams.fbParams.limit);
            coCommon.printCsData(result, 3);
            
            const dimension = result.columns.dimension;
            const rows = [];
            for (let i = 0; i < result.cs.rowCount; i++) {
                const row = {};
                for (let idx = 0; idx < dimension.length; idx++) {
                    row[dimension[idx].split(".")[1]] = result.cs.row(i).cell(result.cs.memberColumnIndex(dimension[idx].split(".")[0], dimension[idx].split(".")[1])).Name;
                }
                rows.push(row);
            }

            coCommon.programEnd();
            return { "Code" : 0, "Msg" : "", "Rows" : rows };
        } catch ( e ) {
            coCommon.error(e.message);
            return { "Code" : -1, "Msg" : e.message };
        }
    };

    // { "fbFuncName" : "fn_cb_LocationSite" }
    var fn_cb_LocationSite = function(parsedParams) {
        const coCommon = new commonLib.COCommon(programName + "." + arguments.callee.name);
        coCommon.setLogLevel("Debug"); 

        try {
 		    let dims = ['[Location].[Location Type].filter(#.Name in {"DC","DC_EX"}).relatedmembers([Location])',
                '[Location].[Location Name]', '[Location].[Site ID]', '[Location].[Company]'
            ];
            dims = coUtil.fn_addincludeField(dims, parsedParams);

            const orderby = 'orderby [Location].[Location Name].[DisplayName] asc'
            const result = coCommon.selectList(dims, [], coUtil.fn_makeWhere(parsedParams), orderby, parsedParams.fbParams.limit);
            coCommon.printCsData(result, 3);
            
            const dimension = result.columns.dimension;
            const rows = [];
            for (let i = 0; i < result.cs.rowCount; i++) {
                const row = {};
                for (let idx = 0; idx < dimension.length; idx++) {
                    row[dimension[idx].split(".")[1]] = result.cs.row(i).cell(result.cs.memberColumnIndex(dimension[idx].split(".")[0], dimension[idx].split(".")[1])).Name;
                }
                rows.push(row);
            }

            coCommon.programEnd();
            return { "Code" : 0, "Msg" : "", "Rows" : rows };
        } catch ( e ) {
            coCommon.error(e.message);
            return { "Code" : -1, "Msg" : e.message };
        }
    };

    // { "fbFuncName" : "fn_cb_tenant" }
    var fn_cb_tenant = function(parsedParams) {
        const coCommon = new commonLib.COCommon(programName + "." + arguments.callee.name);
        coCommon.setLogLevel("Debug"); 

        try {
 		    let dims = ['[Tenant].[Tenant]'];
            
            const result = coCommon.selectList(dims, [], "", "", parsedParams.fbParams.limit);
            coCommon.printCsData(result, 3);
            
            var comboList = coCommon.fn_makeCombo(result, {DimName : "Tenant", DimAttbName : "Tenant", Sort : "DisplayName"});
            coCommon.debug("ComboData : " + JSON.stringify(comboList.slice(0,3)));

            coCommon.programEnd();
            return { "Code" : 0, "Msg" : "", "Rows" : comboList };
        } catch ( e ) {
            coCommon.error(e.message);
            return { "Code" : -1, "Msg" : e.message };
        }
    };

    // { "fbFuncName" : "fn_cb_userGroup" }
    var fn_cb_userGroup = function(parsedParams) {
        const coCommon = new commonLib.COCommon(programName + "." + arguments.callee.name);
        coCommon.setLogLevel("Debug"); 

        try {
 		    let dims = ['[User Group].[User Group]'];
            
            const result = coCommon.selectList(dims, [], "", "", parsedParams.fbParams.limit);
            coCommon.printCsData(result, 3);
            
            var comboList = coCommon.fn_makeCombo(result, {DimName : "User Group", DimAttbName : "User Group", Sort : "DisplayName"});
            coCommon.debug("ComboData : " + JSON.stringify(comboList.slice(0,3)));

            coCommon.programEnd();
            return { "Code" : 0, "Msg" : "", "Rows" : comboList };
        } catch ( e ) {
            coCommon.error(e.message);
            return { "Code" : -1, "Msg" : e.message };
        }
    };

    /************************************************* Test용 함수 Mapping logic *************************************************/
    // { "fbFuncName" : "fn_commonTest" }
    var fn_commonTest = function(parsedParams) {
        const coCommon = new commonLib.COCommon(programName + "." + arguments.callee.name);
        coCommon.setLogLevel("Debug");

		try {
		    var rtn = {};

            rtn["fn_cb_BasePlan"] = fn_cb_BasePlan(parsedParams).Rows;
            rtn["fn_cb_CopySourceMP"] = fn_cb_CopySourceMP(parsedParams).Rows;
            rtn["fn_cb_item"] = fn_cb_item(parsedParams).Rows;
            rtn["fn_cb_jdm"] = fn_cb_jdm(parsedParams).Rows;
            rtn["fn_cb_erpShipDescription"] = fn_cb_erpShipDescription(parsedParams).Rows;
            rtn["fn_cb_erpSoldDescription"] = fn_cb_erpSoldDescription(parsedParams).Rows;
            rtn["fn_cb_LevelList"] = fn_cb_LevelList(parsedParams).Rows;
            rtn["fn_cb_ProductLevel"] = fn_cb_ProductLevel(parsedParams).Rows;
            rtn["fn_cb_progrpProductGroup"] = fn_cb_progrpProductGroup(parsedParams).Rows;
            rtn["fn_cb_progrpSection"] = fn_cb_progrpSection(parsedParams).Rows;
            rtn["fn_cb_project"] = fn_cb_project(parsedParams).Rows;
            rtn["fn_cb_projectPrdGrp"] = fn_cb_projectPrdGrp(parsedParams).Rows;
            rtn["fn_cb_projectProduct"] = fn_cb_projectProduct(parsedParams).Rows;
            rtn["fn_cb_regionDC"] = fn_cb_regionDC(parsedParams).Rows;
            rtn["fn_cb_plBoolean"] = fn_cb_plBoolean(parsedParams).Rows;
            rtn["fn_cb_PLBooleanFlagN"] = fn_cb_PLBooleanFlagN(parsedParams).Rows;						
            rtn["fn_cb_plCompanyCode"] = fn_cb_plCompanyCode(parsedParams).Rows;
            rtn["fn_cb_PLCopyPerdFlag"] = fn_cb_PLCopyPerdFlag(parsedParams).Rows;
            rtn["fn_cb_plRddFlag"] = fn_cb_plRddFlag(parsedParams).Rows;
            rtn["fn_cb_plShotReason"] = fn_cb_plShotReason(parsedParams).Rows;
            rtn["fn_cb_siteChannelDC"] = fn_cb_siteChannelDC(parsedParams).Rows;
            rtn["fn_cb_salesShipTo"] = fn_cb_salesShipTo(parsedParams).Rows;
            rtn["fn_cb_salesID"] = fn_cb_salesID(parsedParams).Rows;
            rtn["fn_cb_salesName"] = fn_cb_salesName(parsedParams).Rows;
            rtn["fn_cb_salesLv1"] = fn_cb_salesLv1(parsedParams).Rows;
            rtn["fn_cb_salesLv1ID"] = fn_cb_salesLv1ID(parsedParams).Rows;
            rtn["fn_cb_salesLv1Name"] = fn_cb_salesLv1Name(parsedParams).Rows;
            rtn["fn_cb_salesLv2"] = fn_cb_salesLv2(parsedParams).Rows;
            rtn["fn_cb_salesLv2ID"] = fn_cb_salesLv2ID(parsedParams).Rows;
            rtn["fn_cb_salesLv2Name"] = fn_cb_salesLv2Name(parsedParams).Rows;
            rtn["fn_cb_salesLv3"] = fn_cb_salesLv3(parsedParams).Rows;
            rtn["fn_cb_salesLv3ID"] = fn_cb_salesLv3ID(parsedParams).Rows;
            rtn["fn_cb_salesLv3Name"] = fn_cb_salesLv3Name(parsedParams).Rows;
            rtn["fn_cb_salesLv4"] = fn_cb_salesLv4(parsedParams).Rows;
            rtn["fn_cb_salesLv4ID"] = fn_cb_salesLv4ID(parsedParams).Rows;
            rtn["fn_cb_salesLv4Name"] = fn_cb_salesLv4Name(parsedParams).Rows;
            rtn["fn_cb_salesLv5"] = fn_cb_salesLv5(parsedParams).Rows;
            rtn["fn_cb_salesLv5ID"] = fn_cb_salesLv5ID(parsedParams).Rows;
            rtn["fn_cb_salesLv5Name"] = fn_cb_salesLv5Name(parsedParams).Rows;
            rtn["fn_cb_salesLv6"] = fn_cb_salesLv6(parsedParams).Rows;
            rtn["fn_cb_salesLv6ID"] = fn_cb_salesLv6ID(parsedParams).Rows;
            rtn["fn_cb_salesLv6Name"] = fn_cb_salesLv6Name(parsedParams).Rows;
            rtn["fn_cb_salesLv7"] = fn_cb_salesLv7(parsedParams).Rows;
            rtn["fn_cb_salesLv7ID"] = fn_cb_salesLv7ID(parsedParams).Rows;
            rtn["fn_cb_salesLv7Name"] = fn_cb_salesLv7Name(parsedParams).Rows;
            rtn["fn_cb_salesAP0"] = fn_cb_salesAP0(parsedParams).Rows;			
            rtn["fn_cb_salesPurpose"] = fn_cb_salesPurpose(parsedParams).Rows;			
            rtn["fn_cb_salesSiteBuyer"] = fn_cb_salesSiteBuyer(parsedParams).Rows;
            rtn["fn_cb_SCMType"] = fn_cb_SCMType(parsedParams).Rows;
            rtn["fn_cb_siteDC"] = fn_cb_siteDC(parsedParams).Rows;
            rtn["fn_cb_siteMF"] = fn_cb_siteMF(parsedParams).Rows;
            rtn["fn_cb_tpMode"] = fn_cb_tpMode(parsedParams).Rows;
            rtn["fn_cb_plStatus"] = fn_cb_plStatus(parsedParams).Rows;
            rtn["fn_cb_subsidiaryDC"] = fn_cb_subsidiaryDC(parsedParams).Rows;
            rtn["fn_cb_bodlist"] = fn_cb_bodlist(parsedParams).Rows;
            rtn["fn_cb_Item"] = fn_cb_Item(parsedParams).Rows;
            rtn["fn_cb_salesIDList"] = fn_cb_salesIDList(parsedParams).Rows;
            rtn["fn_cb_salesIDInfo"] = fn_cb_salesIDInfo(parsedParams).Rows;
            rtn["fn_cb_FromSite"] = fn_cb_FromSite(parsedParams).Rows;
            rtn["fn_cb_ToSite"] = fn_cb_ToSite(parsedParams).Rows;
            rtn["fn_cb_ProductGroup"] = fn_cb_ProductGroup(parsedParams).Rows;
            rtn["fn_cb_Product"] = fn_cb_Product(parsedParams).Rows;
            rtn["fn_cb_Project"] = fn_cb_Project(parsedParams).Rows;
            rtn["fn_cb_SopFixedItem"] = fn_cb_SopFixedItem(parsedParams).Rows;
            rtn["fn_cb_progrpBusinessUnit"] = fn_cb_progrpBusinessUnit(parsedParams).Rows;
            rtn["fn_cb_ErpSoldtoCompany"] = fn_cb_ErpSoldtoCompany(parsedParams).Rows;
            rtn["fn_cb_ErpSoldto"] = fn_cb_ErpSoldto(parsedParams).Rows;
            rtn["fn_cb_ErpShiptoCompany"] = fn_cb_ErpShiptoCompany(parsedParams).Rows;
            rtn["fn_cb_ErpShipto"] = fn_cb_ErpShipto(parsedParams).Rows;
            rtn["fb_PlanWeek"] = fb_PlanWeek(parsedParams).Rows;
            rtn["fn_cb_ChannelSite"] = fn_cb_ChannelSite(parsedParams).Rows;
            rtn["fn_cb_LocationSite"] = fn_cb_LocationSite(parsedParams).Rows;
            rtn["fn_cb_tenant"] = fn_cb_tenant(parsedParams).Rows;
            rtn["fn_cb_userGroup"] = fn_cb_userGroup(parsedParams).Rows;
            
            coCommon.programEnd();

            return { "Code" : 0, "Msg" : "", "Rows" : rtn };
        } catch ( e ) {
            return { "Code" : -1, "Msg" : e.message };
        }
    };

/************************************************* Mapping logic *************************************************/
    // Mapping 함수 정의, 마지막에 선언을 해야 함수를 정상적으로 인식함
    const functionMap = {
        "fn_cb_common" : fn_cb_common
        ,"fn_cb_BasePlan" : fn_cb_BasePlan
        ,"fn_cb_CopySourceMP" : fn_cb_CopySourceMP
        ,"fn_cb_eolGroupID" : fn_cb_eolGroupID
        ,"fn_cb_erpShipDescription" : fn_cb_erpShipDescription
        ,"fn_cb_erpSoldDescription" : fn_cb_erpSoldDescription
        ,"fn_cb_item" : fn_cb_item
        ,"fn_cb_jdm" : fn_cb_jdm
        ,"fn_cb_LevelList" : fn_cb_LevelList
        ,"fn_cb_progrpSection" : fn_cb_progrpSection
        ,"fn_cb_progrpProductGroup" : fn_cb_progrpProductGroup
        ,"fn_cb_project" : fn_cb_project
        ,"fn_cb_projectPrdGrp" : fn_cb_projectPrdGrp
        ,"fn_cb_projectProduct" : fn_cb_projectProduct
        ,"fn_cb_plBoolean" : fn_cb_plBoolean
        ,"fn_cb_PLBooleanFlagN" : fn_cb_PLBooleanFlagN				
        ,"fn_cb_plCompanyCode" : fn_cb_plCompanyCode
        ,"fn_cb_PLCopyPerdFlag" : fn_cb_PLCopyPerdFlag
        ,"fn_cb_plRddFlag" : fn_cb_plRddFlag
        ,"fn_cb_plShotReason" : fn_cb_plShotReason
        ,"fn_cb_ProductLevel" : fn_cb_ProductLevel
        ,"fn_cb_regionDC" : fn_cb_regionDC
        ,"fn_cb_siteChannelDC" : fn_cb_siteChannelDC
        ,"fn_cb_salesShipTo" : fn_cb_salesShipTo
        ,"fn_cb_salesID" : fn_cb_salesID
        ,"fn_cb_salesName" : fn_cb_salesName
        ,"fn_cb_salesLv1" : fn_cb_salesLv1
        ,"fn_cb_salesLv1ID" : fn_cb_salesLv1ID
        ,"fn_cb_salesLv1Name" : fn_cb_salesLv1Name
        ,"fn_cb_salesLv2" : fn_cb_salesLv2
        ,"fn_cb_salesLv2ID" : fn_cb_salesLv2ID
        ,"fn_cb_salesLv2Name" : fn_cb_salesLv2Name
        ,"fn_cb_salesLv3" : fn_cb_salesLv3
        ,"fn_cb_salesLv3ID" : fn_cb_salesLv3ID
        ,"fn_cb_salesLv3Name" : fn_cb_salesLv3Name
        ,"fn_cb_salesLv4" : fn_cb_salesLv4
        ,"fn_cb_salesLv4ID" : fn_cb_salesLv4ID
        ,"fn_cb_salesLv4Name" : fn_cb_salesLv4Name
        ,"fn_cb_salesLv5" : fn_cb_salesLv5
        ,"fn_cb_salesLv5ID" : fn_cb_salesLv5ID
        ,"fn_cb_salesLv5Name" : fn_cb_salesLv5Name
        ,"fn_cb_salesLv6" : fn_cb_salesLv6
        ,"fn_cb_salesLv6ID" : fn_cb_salesLv6ID
        ,"fn_cb_salesLv6Name" : fn_cb_salesLv6Name
        ,"fn_cb_salesLv7" : fn_cb_salesLv7
        ,"fn_cb_salesLv7ID" : fn_cb_salesLv7ID
        ,"fn_cb_salesLv7Name" : fn_cb_salesLv7Name
        ,"fn_cb_salesAP0" : fn_cb_salesAP0
        ,"fn_cb_salesPurpose" : fn_cb_salesPurpose
        ,"fn_cb_salesSiteBuyer" : fn_cb_salesSiteBuyer
        ,"fn_cb_SCMType" : fn_cb_SCMType
        ,"fn_cb_siteDC" : fn_cb_siteDC
        ,"fn_cb_siteMF" : fn_cb_siteMF
        ,"fn_cb_tpMode" : fn_cb_tpMode
        ,"fn_cb_plStatus" : fn_cb_plStatus
        ,"fn_cb_subsidiaryDC" : fn_cb_subsidiaryDC
        ,"fn_updateInfo" : fn_updateInfo
        ,"fn_validation" : fn_validation
        ,"fn_commonTest" : fn_commonTest
        ,"fn_cb_bodlist" : fn_cb_bodlist
        ,"fn_cb_Item" : fn_cb_Item
        ,"fn_cb_salesIDList" : fn_cb_salesIDList
        ,"fn_cb_salesIDInfo" : fn_cb_salesIDInfo
        ,"fn_cb_FromSite" : fn_cb_FromSite
        ,"fn_cb_ToSite" : fn_cb_ToSite
        ,"fn_cb_ProductGroup" : fn_cb_ProductGroup
        ,"fn_cb_Product" : fn_cb_Product
        ,"fn_cb_Project" : fn_cb_Project
        ,"fn_cb_SopFixedItem" : fn_cb_SopFixedItem
        ,"fn_cb_progrpBusinessUnit" : fn_cb_progrpBusinessUnit
        ,"fn_cb_ErpSoldtoCompany" : fn_cb_ErpSoldtoCompany
        ,"fn_cb_ErpSoldto" : fn_cb_ErpSoldto
        ,"fn_cb_ErpShiptoCompany" : fn_cb_ErpShiptoCompany
        ,"fn_cb_ErpShipto" : fn_cb_ErpShipto
        ,"fb_PlanWeek" : fb_PlanWeek
        ,"fn_cb_ChannelSite" : fn_cb_ChannelSite
        ,"fn_cb_LocationSite" : fn_cb_LocationSite
        ,"fn_cb_tenant" : fn_cb_tenant
        ,"fn_cb_userGroup" : fn_cb_userGroup
    };

    return {
        fn_loadFunction : fn_loadFunction
    };
});

/**************************** o9.NSCM.JSEWCommonCO ****************************
    2025-06-17 : 신규 생성
    2025-06-23 : 콤보 데이타 조회시 갯수 제한 ( 3,000 개 )
    2025-06-24 : 콤보 구성시 existAll 파라미터 추가
    2025-07-15 : VdUtil 전사용 COUtil로 변경
    2025-07-16 : 함수 초기 설정
    fn_cb_regionDC, fn_cb_plBoolean, fn_cb_plShotReason, fn_cb_siteDC, fn_cb_siteMF, fn_cb_subsidiaryDC
    fn_cb_project, fn_cb_projectProduct, fn_cb_projectPrdGrp
    fn_updateInfo, fn_validation, fn_commonTest - 기존 동일
    함수 생성
    2025-08-04 : fn_cb_eolGroupID 함수 생성
    2025-08-08 : fn_cb_plStatus 함수 생성
    2025-08-18 : fn_cb_plCompanyCode, fn_cb_erpSoldDescription, fn_cb_erpShipDescription, fn_cb_salesSiteBuyer 함수 생성
    2025-08-21 : fn_cb_progrpProductGroup, fn_cb_progrpSection 함수생성
    2025-08-22 : fn_cb_Sales* 함수생성
    2025-08-25 : fn_cb_plRddFlag 함수생성
    2025-09-18 : fn_cb_item, fn_cb_bodlist, fn_cb_salesPurpose 함수생성
    2025-09-18 : fn_cb_ProductLevel, fn_cb_SCMType, fn_cb_BasePlan, fn_cb_CopySourceMP, cn_cb_LevelList 함수생성
    2025-10-17 : fn_cb_salesIDList, fn_cb_salesIDInfo 함수생성
    2025-10-28 : fn_cb_salesLv#, fn_cb_salesLv#ID 일괄 Namedset 적용 (jaemin)
    2025-11-04 : fn_cb_salesLv2 Sales Domain.[Sales Std1] 조건 추가
    2025-12-01 : fn_cb_FromSite, fn_cb_ToSite, fn_cb_ProductGroup, fn_cb_Product, fn_cb_Project, fn_cb_SopFixedItem 함수 생성
    2025-12-04 : fn_cb_progrpBusinessUnit 함수 생성
    2025-12-10 : fn_cb_FromSite, fn_cb_ToSite, fn_cb_ProductGroup, fn_cb_Product, fn_cb_Project, fn_cb_SopFixedItem 에서 Filter 로 Where 조건 추가
    2025-12-11 : fn_cb_ErpSoldtoCompany, fn_cb_ErpSoldto, fn_cb_ErpSoldto, fn_cb_ErpShipto 함수 생성
    2025-12-15 : fb_PlanWeek 함수 생성
    2025-12-18 : fn_cb_siteDC 에서 Filter 로 Where 조건 추가, fn_cb_LocationSite 함수 생성
    2025-12-31 : fn_cb_tenant, fn_cb_userGroup 함수 생성
    2026-01-26 : fn_cb_salesLv3 return 값에 Sales Lv3 Type 및 Sales Lv3 Subsidiary Region Property 추가
    2026-02-09 : fn_cb_salesPurpose DimDisplayPropertyName 을 Sales Lv7 Purpose > Sales Lv7 Name Purpose 으로 수정
*******************************************************************************/