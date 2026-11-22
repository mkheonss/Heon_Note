define('o9.NSCM.JSEWVDECPSimulation', ['o9/data/query', 'o9/data/cellset', 'o9.NSCM.commonLibVD'], function () {

/**************************************************************************************
    프로그램명  : o9.NSCM.JSEWVDECPSimulation
    화면명     : ECP Simulation
    화면 개발자 :
    API 개발자 : yj75.park
    최초생성   : 2026.03.30
**************************************************************************************/

	const programName = "o9.NSCM.JSEWVDECPSimulation";
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

/*
{ "fbFuncName" : "fn_saveECP",
    "fbParams": {
        "limit": -1,
        "filters": {
            "[Version].[Version Name]": {
                "SelectedMembers": [
                    "CWV_MP"
                ],
                "SelectedMembersAlias": [],
                "MemberFilter": "",
                "DimensionAliasName": ""
            }
        },
        "reportName": "",
        "menuName": ""
    },
  "fbGridRows" : [
	{"rowstatus":"U"
	,"rowindex":"0"
	,"[Item Material].[Item Material]":"BN96-62553R"
	,"[Location].[Location]":"P105"
	,"[BOM Info].[BOM Version]":"WA01"
	,"Measure.[ECP Simulation Confirm_Remark]":"Remark Update Test22"
	}
  ]
}
*/
    const fn_saveECP = function (parsedParams) {
		const VdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
        VdCommon.setLogLevel("Debug");
		VdCommon.debug("parsedParams :: "+JSON.stringify(parsedParams));

        try{
           var updateData = [];

			var fbVersion = "[Version].[Version Name].["+vdUtil.fn_getFilterValue(parsedParams,"[Version].[Version Name]")+"]";

			for ( var i = 0; i < parsedParams.fbGridRows.length; i++ ) {
				var row = parsedParams.fbGridRows[i];
				let rowStatus     = row["rowstatus"];
				var rowindex 	  = row["rowindex"];

				// 데이터 구분
				if( rowStatus == "U") {
					updateData.push(parsedParams.fbGridRows[i]);
				}
			}

			VdCommon.debug("updateData.length :: "+updateData.length);

			for(var i=0;i<updateData.length; i++) {

				var uRow = updateData[i];

				// 데이타 수정
				var dimensions = [];
				dimensions.push(fbVersion);
				dimensions.push(vdUtil.fn_qDim(uRow, "[Item Material].[Item Material]"));
				dimensions.push(vdUtil.fn_qDim(uRow, "[Location].[Location]"));
				dimensions.push(vdUtil.fn_qDim(uRow, "[BOM Info].[BOM Version]"));

				var measures = [];
				measures.push(vdUtil.fn_qMeaStr(uRow, "Measure.[ECP Simulation Confirm_Remark]"));
                measures.push(vdUtil.fn_qMeaUpdateUser("Measure.[ECP Simulation Confirm_Updated by]"));
                measures.push(vdUtil.fn_qMeaUpdateTime("Measure.[ECP Simulation Confirm_Update time]"));

				VdCommon.updateMeasure(dimensions, measures);

			}

			VdCommon.programEnd();
			return { "Code" : 0, "Msg" : "", "Rows" : "" };

        } catch ( e ) {
            return { "Code" : -1, "Msg" : e.message };
        }
    };

/*

{ "fbFuncName" : "fn_saveECPConfirm",
    "fbParams": {
        "limit": -1,
        "filters": {
            "[Version].[Version Name]": {
                "SelectedMembers": [
                    "CWV_MP"
                ],
                "SelectedMembersAlias": [],
                "MemberFilter": "",
                "DimensionAliasName": ""
            }
        },
        "reportName": "",
        "menuName": ""
    },
  "fbGridRows" : [
	{
	 "rowstatus":"U"
	,"rowindex":"0"
	,"[Item Material].[Item Material]":"BN96-62553R"
	,"[Location].[Location]":"P105"
	,"[BOM Info].[BOM Version]":"A202"
	,"[Item Material].[MSL4]":"Elec.>Elec.>3IN1>*"
	,"Measure.[ECP Simulation Confirm_ETD W]":"1"
	,"Measure.[ECP Simulation Confirm_ETD Qty]":"2"
	,"Measure.[ECP Simulation Confirm_Air ETA W]":"3"
	,"Measure.[ECP Simulation Confirm_Air N Price]":"4"
	,"Measure.[ECP Simulation Confirm_Air Amt]":"5"
	,"Measure.[ECP Simulation Confirm_Remark]":"Remark Update Test333"
	}
  ]
}

*/
    const fn_saveECPConfirm = function (parsedParams) {
		const VdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
        VdCommon.setLogLevel("Debug");
		VdCommon.debug("parsedParams :: "+JSON.stringify(parsedParams));

        try{
            var updateData = [];

			var fbVersion = "[Version].[Version Name].["+vdUtil.fn_getFilterValue(parsedParams,"[Version].[Version Name]")+"]";

			for ( var i = 0; i < parsedParams.fbGridRows.length; i++ ) {
				var row = parsedParams.fbGridRows[i];
				let rowStatus     = row["rowstatus"];
				var rowindex 	  = row["rowindex"];

				// 데이터 구분
				if( rowStatus == "U") {
					updateData.push(parsedParams.fbGridRows[i]);
				}
			}


			VdCommon.debug("updateData.length :: "+updateData.length);

			for(var i=0;i<updateData.length; i++) {

				var uRow = updateData[i];

				var dimensions = [];
				dimensions.push(fbVersion);
				dimensions.push(vdUtil.fn_qDim(uRow, "[Item Material].[Item Material]"));
				dimensions.push(vdUtil.fn_qDim(uRow, "[Location].[Location]"));
				dimensions.push(vdUtil.fn_qDim(uRow, "[BOM Info].[BOM Version]"));

				var result = VdCommon.selectList(dimensions, ["Measure.[ECP Simulation Confirm_Creation time]"], "", "", "");

				var measures = [];

				measures.push(vdUtil.fn_qMeaNotStr(uRow, "Measure.[ECP Simulation Confirm_ETD W]"));
				measures.push(vdUtil.fn_qMeaNotStr(uRow, "Measure.[ECP Simulation Confirm_ETD Qty]"));
				measures.push(vdUtil.fn_qMeaNotStr(uRow, "Measure.[ECP Simulation Confirm_Air ETA W]"));
				measures.push(vdUtil.fn_qMeaNotStr(uRow, "Measure.[ECP Simulation Confirm_Air N Price]"));
				measures.push(vdUtil.fn_qMeaNotStr(uRow, "Measure.[ECP Simulation Confirm_Air Amt]"));

				measures.push(vdUtil.fn_qMeaUpdateUser("Measure.[ECP Simulation Confirm_Updated by]"));
				measures.push(vdUtil.fn_qMeaUpdateTime("Measure.[ECP Simulation Confirm_Update time]"));

				if(result.cs.rowCount > 0) {

					measures.push(vdUtil.fn_qMeaStr(uRow, "Measure.[ECP Simulation Confirm_Remark]"));

					VdCommon.updateMeasure(dimensions, measures);

				} else {

					measures.push(vdUtil.fn_qMeaStr(null, "Measure.[ECP Simulation Confirm_Remark]",""));
					measures.push(vdUtil.fn_qMeaStr(null, "Measure.[ECP Simulation Confirm_TP Mode]","AIR"));
					measures.push(vdUtil.fn_qMeaUpdateUser("Measure.[ECP Simulation Confirm_Created by]"));
					measures.push(vdUtil.fn_qMeaUpdateTime("Measure.[ECP Simulation Confirm_Creation time]"));

					VdCommon.createMeasure(dimensions, measures);
				}
			}

			VdCommon.programEnd();

			return { "Code" : 0, "Msg" : "", "Rows" : "" };

        } catch ( e ) {
            return { "Code" : -1, "Msg" : e.message };
        }
    };

/*

{ "fbFuncName" : "fn_saveECPSimulPSI",
    "fbParams": {
        "limit": -1,
        "filters": {
            "[Version].[Version Name]": {
                "SelectedMembers": [
                    "CWV_MP"
                ],
                "SelectedMembersAlias": [],
                "MemberFilter": "",
                "DimensionAliasName": ""
            }
        },
        "reportName": "",
        "menuName": ""
    },
  "fbGridRows" : [
	{
	 "rowstatus":"U"
	,"rowindex":"0"
	,"[Item Material].[Item Material]":"BN96-62553R"
	,"[Location].[Location]":"P105"
	,"[BOM Info].[BOM Version]":"A202"
	,"[Group].[Group ID]":"G1"
	,"[Time].[Week]" : "200210"
				,"Measure.[ECP Simulation PSI W_REQ_SOP]" : "23",
                "Measure.[ECP Simulation PSI W_REQ_Air ECP]" : "23",
                "Measure.[ECP Simulation PSI W_REQ_ECP]" : "23",
                "Measure.[ECP Simulation PSI W_BOH]" : "23",
                "Measure.[ECP Simulation PSI W_BOH_SOP ECP]" : "23",
                "Measure.[ECP Simulation PSI W_BOH_SOP+Air+Norm]" : "23",
                "Measure.[ECP Simulation PSI W_Arrival_Total]" : "23",
                "Measure.[ECP Simulation PSI W_Arrival_SN]" : "23",
                "Measure.[ECP Simulation PSI W_Arrival_Supply Plan]" : "23",
                "Measure.[ECP Simulation PSI W_Arrival_Open PO]" : "23",
                "Measure.[ECP Simulation PSI W_Arrival_RTP]" : "23",
                "Measure.[ECP Simulation PSI W_Arrival_RTF]" : "23",
                "Measure.[ECP Simulation PSI W_Arrival_Global RTF]" : "23",
                "Measure.[ECP Simulation PSI W_Arrival_CMI]" : "23",
                "Measure.[ECP Simulation PSI W_Arrival_Excel]" : "23",
                "Measure.[ECP Simulation PSI W_AR Qty(SOP)]" : "23",
                "Measure.[ECP Simulation PSI W_AR Qty(SOP+Air)]" : "23",
                "Measure.[ECP Simulation PSI W_AR Qty(SOP+Air+Norm)]" : "23",
                "Measure.[ECP Simulation PSI W_Air ETD Guide]" : "23",
                "Measure.[ECP Simulation PSI W_SOP_ETC]" : "23",
                "Measure.[ECP Simulation PSI W_SOP_ETD]" : "23",
                "Measure.[ECP Simulation PSI W_SOP_ETA]" : "23",
                "Measure.[ECP Simulation PSI W_EOH_SOP_Arrival Total]" : "23",
                "Measure.[ECP Simulation PSI W_EOH_SOP+Air]" : "23",
                "Measure.[ECP Simulation PSI W_EOH_SOP+Air+Norm]" : "23",
                "Measure.[ECP Simulation PSI W_EOH_Stock Level]" : "23",
                "Measure.[ECP Simulation PSI W_Air LT]" : "23"
	}
  ]
}
*/
    const fn_saveECPSimulPSI = function (parsedParams) {
		const VdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
        VdCommon.setLogLevel("Debug");
		VdCommon.debug("parsedParams :: "+JSON.stringify(parsedParams));

        try{
			var updateData = [];

			var fbVersion = "[Version].[Version Name].["+vdUtil.fn_getFilterValue(parsedParams,"[Version].[Version Name]")+"]";

			for ( var i = 0; i < parsedParams.fbGridRows.length; i++ ) {
				var row = parsedParams.fbGridRows[i];
				let rowStatus     = row["rowstatus"];
				var rowindex 	  = row["rowindex"];

				// 데이터 구분
				if( rowStatus == "U") {
					updateData.push(parsedParams.fbGridRows[i]);
				}
			}

			VdCommon.debug("updateData.length :: "+updateData.length);

			for(var i=0;i<updateData.length; i++) {

				var uRow = updateData[i];

				var dimensions = [];
				dimensions.push(fbVersion);
				dimensions.push(vdUtil.fn_qDim(uRow, "[Group].[Group ID]"));
				dimensions.push(vdUtil.fn_qDim(uRow, "[Location].[Location]"));
				dimensions.push(vdUtil.fn_qDim(uRow, "[Item Material].[Item Material]"));
				dimensions.push(vdUtil.fn_qDim(uRow, "[BOM Info].[BOM Version]"));
				dimensions.push(vdUtil.fn_qDim(uRow, "[Time].[Week]"));

				var measures = [];

                measures.push(vdUtil.fn_qMeaStr(uRow, "Measure.[ECP Simulation PSI W_REQ_SOP]"));
                measures.push(vdUtil.fn_qMeaStr(uRow, "Measure.[ECP Simulation PSI W_REQ_Air ECP]"));
                measures.push(vdUtil.fn_qMeaStr(uRow, "Measure.[ECP Simulation PSI W_REQ_ECP]"));
                measures.push(vdUtil.fn_qMeaStr(uRow, "Measure.[ECP Simulation PSI W_BOH]"));
                measures.push(vdUtil.fn_qMeaStr(uRow, "Measure.[ECP Simulation PSI W_BOH_SOP ECP]"));
                measures.push(vdUtil.fn_qMeaStr(uRow, "Measure.[ECP Simulation PSI W_BOH_SOP+Air+Norm]"));
                measures.push(vdUtil.fn_qMeaStr(uRow, "Measure.[ECP Simulation PSI W_Arrival_Total]"));
                measures.push(vdUtil.fn_qMeaStr(uRow, "Measure.[ECP Simulation PSI W_Arrival_SN]"));
                measures.push(vdUtil.fn_qMeaStr(uRow, "Measure.[ECP Simulation PSI W_Arrival_Supply Plan]"));
                measures.push(vdUtil.fn_qMeaStr(uRow, "Measure.[ECP Simulation PSI W_Arrival_Open PO]"));
                measures.push(vdUtil.fn_qMeaStr(uRow, "Measure.[ECP Simulation PSI W_Arrival_RTP]"));
                measures.push(vdUtil.fn_qMeaStr(uRow, "Measure.[ECP Simulation PSI W_Arrival_RTF]"));
                measures.push(vdUtil.fn_qMeaStr(uRow, "Measure.[ECP Simulation PSI W_Arrival_Global RTF]"));
                measures.push(vdUtil.fn_qMeaStr(uRow, "Measure.[ECP Simulation PSI W_Arrival_CMI]"));
                measures.push(vdUtil.fn_qMeaStr(uRow, "Measure.[ECP Simulation PSI W_Arrival_Excel]"));
                measures.push(vdUtil.fn_qMeaStr(uRow, "Measure.[ECP Simulation PSI W_AR Qty(SOP)]"));
                measures.push(vdUtil.fn_qMeaStr(uRow, "Measure.[ECP Simulation PSI W_AR Qty(SOP+Air)]"));
                measures.push(vdUtil.fn_qMeaStr(uRow, "Measure.[ECP Simulation PSI W_AR Qty(SOP+Air+Norm)]"));
                measures.push(vdUtil.fn_qMeaStr(uRow, "Measure.[ECP Simulation PSI W_Air ETD Guide]"));
                measures.push(vdUtil.fn_qMeaStr(uRow, "Measure.[ECP Simulation PSI W_SOP_ETC]"));
                measures.push(vdUtil.fn_qMeaStr(uRow, "Measure.[ECP Simulation PSI W_SOP_ETD]"));
                measures.push(vdUtil.fn_qMeaStr(uRow, "Measure.[ECP Simulation PSI W_SOP_ETA]"));
                measures.push(vdUtil.fn_qMeaStr(uRow, "Measure.[ECP Simulation PSI W_EOH_SOP_Arrival Total]"));
                measures.push(vdUtil.fn_qMeaStr(uRow, "Measure.[ECP Simulation PSI W_EOH_SOP+Air]"));
                measures.push(vdUtil.fn_qMeaStr(uRow, "Measure.[ECP Simulation PSI W_EOH_SOP+Air+Norm]"));
                measures.push(vdUtil.fn_qMeaStr(uRow, "Measure.[ECP Simulation PSI W_EOH_Stock Level]"));
                measures.push(vdUtil.fn_qMeaStr(uRow, "Measure.[ECP Simulation PSI W_Air LT]"));

				measures.push(vdUtil.fn_qMeaUpdateUser("Measure.[ECP Simulation PSI W_Updated by]"));
				measures.push(vdUtil.fn_qMeaUpdateTime("Measure.[ECP Simulation PSI W_Update time]"));

				VdCommon.updateMeasure(dimensions, measures);
			}

			VdCommon.programEnd();
			return { "Code" : 0, "Msg" : "", "Rows" : "" };

        } catch ( e ) {
            return { "Code" : -1, "Msg" : e.message };
        }
    };

/*

{
"fbFuncName" : "fn_getECPMasterLv3AirLT",
    "fbParams": {
        "limit": -1,
		"where":{},
        "filters": {
            "[Version].[Version Name]": {
                "SelectedMembers": [
                    "CWV_MP"
                ],
                "SelectedMembersAlias": [],
                "MemberFilter": "",
                "DimensionAliasName": ""
            },
            "[Item Material].[MSL3]": {
                "SelectedMembers": [
                    "Optics>Optics>LGP"
                ],
                "SelectedMembersAlias": [],
                "MemberFilter": "",
                "DimensionAliasName": ""
            },
            "[Location].[Location]": {
                "SelectedMembers": [
                    "P306"
                ],
                "SelectedMembersAlias": [],
                "MemberFilter": "",
                "DimensionAliasName": ""
            }
        },
        "reportName": "",
        "menuName": ""
    }
}
*/
    const fn_getECPMasterLv3AirLT = function (parsedParams) {
        const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
        vdCommon.setLogLevel("Debug");

		try {

			var dimensions = [];
			dimensions.push(vdUtil.fn_getFilterQuery(parsedParams, "[Version].[Version Name]"));
			dimensions.push(vdUtil.fn_getFilterQuery(parsedParams, "[Location].[Location]"));
			dimensions.push(vdUtil.fn_getFilterQuery(parsedParams, "[Item Material].[MSL3]"));

            var result = vdCommon.selectList(dimensions,
                                             ["Measure.[ECP Mst Lv3_Air LT]"],
                                             'Where {Measure.[ECP Mst Lv3_ECP Flag] == "Y"}', "", "");

			var comboList = [];
			var measure = result.columns.measure;
			for ( var i = 0; i < result.cs.rowCount; i++ ) {
				var rows = { 
							 "Version"   : vdUtil.fn_getDimValue(result,i,"Version", "Version Name")
				           , "Plant"     : vdUtil.fn_getDimValue(result,i,"Location", "Location")
						   , "Lv3"       : vdUtil.fn_getDimValue(result,i,"Item Material", "MSL3")	 
						   , "Lv3 Air LT": vdUtil.fn_getMeaValue(result,i,measure[0])
						   };
				comboList.push(rows);
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
{
"fbFuncName" : "fn_getAirUnitPrice",
    "fbParams": {
        "limit": -1,
		"where":{"[Item Material].[Item Material]":"BN44-00932N"},
        "filters": {
            "[Version].[Version Name]": {
                "SelectedMembers": [
                    "CWV_MP"
                ],
                "SelectedMembersAlias": [],
                "MemberFilter": "",
                "DimensionAliasName": ""
            },
            "[Location].[Location]": {
                "SelectedMembers": [
                    "P306"
                ],
                "SelectedMembersAlias": [],
                "MemberFilter": "",
                "DimensionAliasName": ""
            }
        },
        "reportName": "",
        "menuName": ""
    }
}
*/
	var fn_getAirUnitPrice = function(parsedParams){
        const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
        vdCommon.setLogLevel("Debug");

		try {

			var where = parsedParams.fbParams["where"];

			var pMaterial = vdUtil.fn_filterStr(where["[Item Material].[Item Material]"]);

			var dimensions = [];
			dimensions.push(vdUtil.fn_getFilterQuery(parsedParams, "[Version].[Version Name]"));
			dimensions.push(vdUtil.fn_getFilterQuery(parsedParams, "[Location].[Location]"));
			dimensions.push("[Country].[Country]");
			dimensions.push("[Item Material].[Item Material]"+pMaterial);

            // 등록된 데이타를 가져온다.
            var result = vdCommon.selectList(dimensions,
                                                ["Measure.[Air Cost Mst_TTL Air Cost]"],
                                                "", "", "");		
			var comboList = [];
			var measure = result.columns.measure;
			for ( var i = 0; i < result.cs.rowCount; i++ ) {
				var rows = { 
				             "Version"  : vdUtil.fn_getDimValue(result,i,"Version", "Version Name")
						   , "Plant"    : vdUtil.fn_getDimValue(result,i,"Location", "Location")
				           , "Country"  : vdUtil.fn_getDimValue(result,i,"Country", "Country")
						   , "Material" : vdUtil.fn_getDimValue(result,i,"Item Material", "Item Material")
						   , "Air Cost" : vdUtil.fn_getMeaValue(result,i,measure[0])
						   };
				comboList.push(rows);
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
{
"fbFuncName" : "fn_getECPRangeLT",
    "fbParams": {
        "limit": -1,
        "filters": {
            "[Version].[Version Name]": {
                "SelectedMembers": [
                    "CWV_MP"
                ],
                "SelectedMembersAlias": [],
                "MemberFilter": "",
                "DimensionAliasName": ""
            }
        },
        "reportName": "",
        "menuName": ""
    }
}
*/
	var fn_getECPRangeLT = function(parsedParams){
        const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
        vdCommon.setLogLevel("Debug");

		try {

			var dimensions = [];
			dimensions.push(vdUtil.fn_getFilterQuery(parsedParams, "[Version].[Version Name]"));
			dimensions.push("[Location].[Location]");

            var result = vdCommon.selectList(dimensions,
                                            ["Measure.[ECP Mst Pop_ECP LT]"],
                                            "", "", "");
			var comboList = [];
			var measure = result.columns.measure;
			for ( var i = 0; i < result.cs.rowCount; i++ ) {
				var rows = { 
				             "Version"  : vdUtil.fn_getDimValue(result,i,"Version", "Version Name")
						   , "Plant"    : vdUtil.fn_getDimValue(result,i,"Location", "Location")
						   , "ECP RANGE": vdUtil.fn_getMeaValue(result,i,measure[0])
						   };
				comboList.push(rows);
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
{
"fbFuncName" : "fn_ecpSimulationPopUp", 
    "fbParams": {
        "limit": -1,
		"where":{
			"[Location].[Location]" : "P105"
		   ,"[Item Material].[Item Material]" : "BN96-62553R"
		   ,"[Item].[Item]" : "MHWA.LEE"
		   ,"[Item Material].[MSL3]" : "Elec.>Elec.>3IN1"
		   ,"[Time].[Week]" : "200132"
		},
        "filters": {
            "[Version].[Version Name]": {
                "SelectedMembers": [
                    "CWV_MP"
                ],
                "SelectedMembersAlias": [],
                "MemberFilter": "",
                "DimensionAliasName": ""           
            },			
            "[Location].[Location]": {
                "SelectedMembers": [
                    "P306"
                ],
                "SelectedMembersAlias": [],
                "MemberFilter": "",
                "DimensionAliasName": ""
            }			
        },
        "reportName": "",
        "menuName": ""
    }
}
*/
	var fn_ecpSimulationPopUp = function(parsedParams){
        const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
        vdCommon.setLogLevel("Debug");

		try {

			var where = parsedParams.fbParams["where"];

			var pMaterial = vdUtil.fn_filterStr(where["[Item Material].[Item Material]"]);
			var pItem = vdUtil.fn_filterStr(where["[Item].[Item]"]);
			var pWeek = vdUtil.fn_filterStr(where["[Time].[Week]"]);
			var pMSL3 = vdUtil.fn_filterStr(where["[Item Material].[MSL3]"]);

			var dimensions = [];
			dimensions.push(vdUtil.fn_getFilterQuery(parsedParams, "[Version].[Version Name]"));
			dimensions.push(vdUtil.fn_getFilterQuery(parsedParams, "[Location].[Location]"));
			dimensions.push("[Item Material].[MSL3]"+pMSL3);
			dimensions.push("[Item Material].[Item Material]"+pMaterial);
			dimensions.push("[Item].[Item]"+pItem);
			dimensions.push("[Time].[Week]"+pWeek);

			var measure = [];
			measure.push("Measure.[ECP Simulation PSI Detail W_Base Qty]");
			measure.push("Measure.[ECP Simulation PSI Detail W_REQ_Air ECP]");
			measure.push("Measure.[ECP Simulation PSI Detail W_REQ_ECP]");
			
            var result = vdCommon.selectList(dimensions,measure,"", "", "");
			
			var comboList = [];
			var measure = result.columns.measure;
			for ( var i = 0; i < result.cs.rowCount; i++ ) {
				var rows = { 
				             "Version"        : vdUtil.fn_getDimValue(result,i,"Version", "Version Name")
						   , "Plant"          : vdUtil.fn_getDimValue(result,i,"Location", "Location")
						   , "Lv3"            : vdUtil.fn_getDimValue(result,i,"Item Material", "MSL3")
						   , "Material"       : vdUtil.fn_getDimValue(result,i,"Item Material", "Item Material")
						   , "Model Name"     : vdUtil.fn_getDimValue(result,i,"Item", "Item")
						   , "Week"           : vdUtil.fn_getDimValue(result,i,"Time", "Week")
						   , "Base Qty"       : vdUtil.fn_getMeaValue(result,i,measure[0])
						   , "Req Air ECP"    : vdUtil.fn_getMeaValue(result,i,measure[1])
						   , "Req Normal ECP" : vdUtil.fn_getMeaValue(result,i,measure[2])
						   };
				comboList.push(rows);
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
{
"fbFuncName" : "fn_ecpSimulationTotalPopUp", 
    "fbParams": {
        "limit": -1,
		"where":{
			"[Location].[Location]" : "P105"
		   ,"[Item Material].[Item Material]" : "BN96-62553R"
		   ,"[Item].[Item]" : "MHWA.LEE"
		   ,"[Item Material].[MSL3]" : "Elec.>Elec.>3IN1"
		   ,"[Time].[Week]" : "200132^200133"
		},
        "filters": {
            "[Version].[Version Name]": {
                "SelectedMembers": [
                    "CWV_MP"
                ],
                "SelectedMembersAlias": [],
                "MemberFilter": "",
                "DimensionAliasName": ""           
            },			
            "[Location].[Location]": {
                "SelectedMembers": [
                    "P306"
                ],
                "SelectedMembersAlias": [],
                "MemberFilter": "",
                "DimensionAliasName": ""
            }			
        },
        "reportName": "",
        "menuName": ""
    }
}
*/	
	var fn_ecpSimulationTotalPopUp = function(parsedParams){
        const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
        vdCommon.setLogLevel("Debug");

		try {

			var where = parsedParams.fbParams["where"];

			var pMaterial = vdUtil.fn_filterStr(where["[Item Material].[Item Material]"]);
			var pItem = vdUtil.fn_filterStr(where["[Item].[Item]"]);
			var pWeek = vdUtil.fn_filterStr(where["[Time].[Week]"].split("^"));
			var pMSL3 = vdUtil.fn_filterStr(where["[Item Material].[MSL3]"]);

			var dimensions = [];
			dimensions.push(vdUtil.fn_getFilterQuery(parsedParams, "[Version].[Version Name]"));
			dimensions.push(vdUtil.fn_getFilterQuery(parsedParams, "[Location].[Location]"));
			dimensions.push("[Item Material].[MSL3]"+pMSL3);
			dimensions.push("[Item Material].[Item Material]"+pMaterial);
			dimensions.push("[Item].[Item]"+pItem);
			dimensions.push("[Time].[Week]"+pWeek);

			var measure = [];
			measure.push("Measure.[ECP Simulation PSI Detail W_Base Qty]");
			measure.push("Measure.[ECP Simulation PSI Detail W_REQ_Air ECP]");
			measure.push("Measure.[ECP Simulation PSI Detail W_REQ_ECP]");
			
            var result = vdCommon.selectList(dimensions,measure,"", "", "");
			
			var comboList = [];
			var measure = result.columns.measure;
			for ( var i = 0; i < result.cs.rowCount; i++ ) {
				var rows = { 
				             "Version"        : vdUtil.fn_getDimValue(result,i,"Version", "Version Name")
						   , "Plant"          : vdUtil.fn_getDimValue(result,i,"Location", "Location")
						   , "Lv3"            : vdUtil.fn_getDimValue(result,i,"Item Material", "MSL3")
						   , "Material"       : vdUtil.fn_getDimValue(result,i,"Item Material", "Item Material")
						   , "Model Name"     : vdUtil.fn_getDimValue(result,i,"Item", "Item")
						   , "Week"           : vdUtil.fn_getDimValue(result,i,"Time", "Week")
						   , "Base Qty"       : vdUtil.fn_getMeaValue(result,i,measure[0])
						   , "Req Air ECP"    : vdUtil.fn_getMeaValue(result,i,measure[1])
						   , "Req Normal ECP" : vdUtil.fn_getMeaValue(result,i,measure[2])
						   };
				comboList.push(rows);
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

/************************************************* Mapping logic **********************************************/
    // Mapping 함수 정의, 마지막에 선언을 해야 함수를 정상적으로 인식함
    const functionMap = {
        "fn_saveECP" : fn_saveECP
	   ,"fn_saveECPConfirm" : fn_saveECPConfirm
	   ,"fn_saveECPSimulPSI" : fn_saveECPSimulPSI
	   ,"fn_getECPMasterLv3AirLT" : fn_getECPMasterLv3AirLT
	   ,"fn_getAirUnitPrice" : fn_getAirUnitPrice
       ,"fn_getECPRangeLT" : fn_getECPRangeLT
	   ,"fn_ecpSimulationPopUp" : fn_ecpSimulationPopUp
	   ,"fn_ecpSimulationTotalPopUp" : fn_ecpSimulationTotalPopUp
    };

    return {
        fn_loadFunction : fn_loadFunction
    };
});
/******************************** o9.NSCM.JSEWVDECPSimulation *******************************
**************************************************************************************/

/**************************** o9.NSCM.JSEWVDECPSimulation ****************************
26.03.30 : 신규생성
**************************** o9.NSCM.JSEWVDECPSimulation ****************************/