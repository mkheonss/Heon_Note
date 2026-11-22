define('o9.NSCM.JSEWVDECPMaster', ['o9/data/query', 'o9/data/cellset', 'o9.NSCM.commonLibVD'], function () {

/**************************************************************************************
    프로그램명  : o9.NSCM.JSEWVDECPMaster
    화면명     : ECP Master
    화면 개발자 : 
    API 개발자 : yj75.park
    최초생성   : 2026.02.23
**************************************************************************************/

	const programName = "o9.NSCM.JSEWVDECPMaster";
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
{ "fbFuncName" : "fn_saveLv3", 
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
	,"[Version].[Version Name]" : "CWV_MP"
	,"[Item Material].[MSL3]":"Mecha.>Mecha.>Press"
	,"[Location].[Location]":"P105"
	,"Measure.[ECP Mst Lv3_ECP Flag]":"Y"
	,"Measure.[ECP Mst Lv3_Air LT]":"2"
	,"Measure.[ECP Mst Lv3 Sub Set_Sub Set Level]":"Lv4"
	}
  ]
}	
*/
    const fn_saveLv3 = function (parsedParams) {
		const VdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
        VdCommon.setLogLevel("Debug");
		VdCommon.debug("parsedParams :: "+JSON.stringify(parsedParams));
	
        try{
            var insertData = [];
			var validData = [];
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
				
				// 데이타 생성
				var dimensionsLv = [];
				dimensionsLv.push(fbVersion);				
				dimensionsLv.push(vdUtil.fn_qDim(uRow, "[Item Material].[MSL3]"));

				var measuresLv = [];
				measuresLv.push(vdUtil.fn_qMeaStr(uRow, "Measure.[ECP Mst Lv3 Sub Set_Sub Set Level]"));

				VdCommon.updateMeasure(dimensionsLv, measuresLv);				
				

				// 데이타 수정
				var dimensions = [];
				dimensions.push(fbVersion);
				dimensions.push(vdUtil.fn_qDim(uRow, "[Location].[Location]"));
				dimensions.push(vdUtil.fn_qDim(uRow, "[Item Material].[MSL3]"));

				var measures = [];
				measures.push(vdUtil.fn_qMeaStr(uRow, "Measure.[ECP Mst Lv3_ECP Flag]"));
				measures.push(vdUtil.fn_qMeaStr(uRow, "Measure.[ECP Mst Lv3_Air LT]"));

				measures.push(vdUtil.fn_qMeaUpdateUser("Measure.[ECP Mst Lv3_Updated by]"));
				measures.push(vdUtil.fn_qMeaUpdateTime("Measure.[ECP Mst Lv3_Update time]"));

				VdCommon.updateMeasure(dimensions, measures);
			}

			VdCommon.programEnd();
			return { "Code" : 0, "Msg" : "", "Rows" : "" };
		
        } catch ( e ) {
            return { "Code" : -1, "Msg" : e.message };
        }
    };

/*

{ "fbFuncName" : "fn_saveLv4", 
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
	 "rowstatus":"C"
	,"rowindex":"0"
	,"[Version].[Version Name]":"CWV_MP"
	,"[Location].[Location]":"ZA10SA51^ZA10SA52"
	,"[Item Material].[MSL4]":"Mecha_Mecha_Remocon_40~"
	,"Measure.[ECP Mst Lv4_ECP Flag]":"Y"
	,"Measure.[ECP Mst Lv4_Air LT]":"2"
	}
  ]
}	

{ "fbFuncName" : "fn_saveLv4", 
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
	,"[Version].[Version Name]":"CWV_MP"
	,"[Location].[Location]":"ZA10SA51"
	,"[Item Material].[MSL4]":"Mecha_Mecha_Remocon_40~"
	,"Measure.[ECP Mst Lv4_ECP Flag]":"N"
	,"Measure.[ECP Mst Lv4_Air LT]":"22"
	}
  ]
}	

{ "fbFuncName" : "fn_saveLv4", 
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
	 "rowstatus":"D"
	,"rowindex":"0"
	,"[Version].[Version Name]":"CWV_MP"
	,"[Location].[Location]":"ZA10SA51"
	,"[Item Material].[MSL4]":"Mecha_Mecha_Remocon_40~"
	,"Measure.[ECP Mst Lv4_ECP Flag]":"N"
	,"Measure.[ECP Mst Lv4_Air LT]":"22"
	}
  ]
}	
*/

    const fn_saveLv4 = function (parsedParams) {
		const VdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
        VdCommon.setLogLevel("Debug");
		VdCommon.debug("parsedParams :: "+JSON.stringify(parsedParams));
	
        try{
            var insertData = [];
			var validData = [];
			var updateData = [];
			var deleteData = [];
			
			var fbVersion = "[Version].[Version Name].["+vdUtil.fn_getFilterValue(parsedParams,"[Version].[Version Name]")+"]"; 

			for ( var i = 0; i < parsedParams.fbGridRows.length; i++ ) {
				var row = parsedParams.fbGridRows[i];
				let rowStatus     = row["rowstatus"];
				var rowindex 	  = row["rowindex"];

				// 데이터 구분
				if( rowStatus == "C") {
					
                    var location = "";
                    if ( vdUtil.fn_getString(row["[Location].[Location]"]) == "" ) {
                        location = "&NSUILocationMFMtrlView";
                    } else {
                        location = "[Location].[Location]" + vdUtil.fn_filterStr(row["[Location].[Location]"].split("^"));
                    }										
					
					let dimchk = [];
					dimchk.push(fbVersion);
					dimchk.push(location);
					dimchk.push(vdUtil.fn_qDim(row, "[Item Material].[MSL4]"));
										
					// 기존 data 중복여부에 대한 체크
					if(!VdCommon.existMeasure(dimchk, ["Measure.[ECP Mst Lv4_ECP Flag]"], "")) {
						insertData.push(parsedParams.fbGridRows[i]);
					} else {
						validData.push(rowindex+" ^ This data is already exists!");
					}
				
				} else if( rowStatus == "D") {
					deleteData.push(parsedParams.fbGridRows[i]);
				} else if( rowStatus == "U") {
					updateData.push(parsedParams.fbGridRows[i]);
				}
			}

			if( validData.length > 0 ){
					return { "Code" : 1, "Msg" : validData };
			} else {
				VdCommon.debug("insertData.length :: "+insertData.length);

				for(var i=0;i<insertData.length; i++) {
					var iRow = insertData[i];
					
                    var location = "";
                    if ( vdUtil.fn_getString(iRow["[Location].[Location]"]) == "" ) {
                        location = "&NSUILocationMFMtrlView";
                    } else {
                        location = "[Location].[Location]" + vdUtil.fn_filterStr(iRow["[Location].[Location]"].split("^"));
                    }					

					// 데이타 생성
					var dimensions = [];
					dimensions.push(fbVersion);				
					dimensions.push(location);
					dimensions.push(vdUtil.fn_qDim(iRow, "[Item Material].[MSL4]"));

					var measures = [];
					measures.push(vdUtil.fn_qMeaStr(iRow, "Measure.[ECP Mst Lv4_ECP Flag]"));
					measures.push(vdUtil.fn_qMeaStr(iRow, "Measure.[ECP Mst Lv4_Air LT]"));
					measures.push(vdUtil.fn_qMeaUpdateUser("Measure.[ECP Mst Lv4_Created by]"));
					measures.push(vdUtil.fn_qMeaUpdateTime("Measure.[ECP Mst Lv4_Creation time]"));
					
					VdCommon.createMeasure(dimensions, measures);

				}

				VdCommon.debug("updateData.length :: "+updateData.length);

				for(var i=0;i<updateData.length; i++) {

					var uRow = updateData[i];

					var dimensions = [];
                    dimensions.push(fbVersion);
                    dimensions.push(vdUtil.fn_qDim(uRow, "[Location].[Location]"));
                    dimensions.push(vdUtil.fn_qDim(uRow, "[Item Material].[MSL4]"));

                    var measures = [];
                    measures.push(vdUtil.fn_qMeaStr(uRow, "Measure.[ECP Mst Lv4_ECP Flag]"));
                    measures.push(vdUtil.fn_qMeaStr(uRow, "Measure.[ECP Mst Lv4_Air LT]"));
                    measures.push(vdUtil.fn_qMeaUpdateUser("Measure.[ECP Mst Lv4_Updated by]"));
                    measures.push(vdUtil.fn_qMeaUpdateTime("Measure.[ECP Mst Lv4_Update time]"));

                    VdCommon.updateMeasure(dimensions, measures);
				}
				
				VdCommon.debug("deleteData.length :: "+deleteData.length);

				for(var i=0;i<deleteData.length; i++) {
					var dRow = deleteData[i];
					
                    var where = [];
                    where.push(fbVersion);
                    where.push(vdUtil.fn_qDim(dRow, "[Location].[Location]"));
                    where.push(vdUtil.fn_qDim(dRow, "[Item Material].[MSL4]"));

                    VdCommon.deleteMeasure(where, "ECP Master Lv4");			

				}				
				
			}
			
			VdCommon.programEnd();
			return { "Code" : 0, "Msg" : "", "Rows" : "" };
		
        } catch ( e ) {
            return { "Code" : -1, "Msg" : e.message };
        }
    };

/*

{ "fbFuncName" : "fn_saveLv5", 
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
	 "rowstatus":"C"
	,"rowindex":"0"
	,"[Version].[Version Name]":"CWV_MP"
	,"[Location].[Location]":"ZA10SA51^ZA10SA52"
	,"[Item Material].[MSL5]":"Mecha_Mecha_Remocon_50~_65"
	,"Measure.[ECP Mst Lv5_ECP Flag]":"Y"
	,"Measure.[ECP Mst Lv5_Air LT]":"2"
	}
  ]
}



{ "fbFuncName" : "fn_saveLv5", 
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
	,"[Version].[Version Name]":"CWV_MP"
	,"[Location].[Location]":"ZA10SA52"
	,"[Item Material].[MSL5]":"Mecha_Mecha_Remocon_50~_65"
	,"Measure.[ECP Mst Lv5_ECP Flag]":"N"
	,"Measure.[ECP Mst Lv5_Air LT]":"12"
	}
  ]
}


{ "fbFuncName" : "fn_saveLv5", 
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
	 "rowstatus":"D"
	,"rowindex":"0"
	,"[Version].[Version Name]":"CWV_MP"
	,"[Location].[Location]":"ZA10SA52"
	,"[Item Material].[MSL5]":"Mecha_Mecha_Remocon_50~_65"
	,"Measure.[ECP Mst Lv5_ECP Flag]":"N"
	,"Measure.[ECP Mst Lv5_Air LT]":"12"
	}
  ]
}
*/
    const fn_saveLv5 = function (parsedParams) {
		const VdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
        VdCommon.setLogLevel("Debug");
		VdCommon.debug("parsedParams :: "+JSON.stringify(parsedParams));
	
        try{
            var insertData = [];
			var validData = [];
			var updateData = [];
			var deleteData = [];
			
			var fbVersion = "[Version].[Version Name].["+vdUtil.fn_getFilterValue(parsedParams,"[Version].[Version Name]")+"]"; 

			for ( var i = 0; i < parsedParams.fbGridRows.length; i++ ) {
				var row = parsedParams.fbGridRows[i];
				let rowStatus     = row["rowstatus"];
				var rowindex 	  = row["rowindex"];

				// 데이터 구분
				if( rowStatus == "C") {
					
                    var location = "";
                    if ( vdUtil.fn_getString(row["[Location].[Location]"]) == "" ) {
                        location = "&NSUILocationMFMtrlView";
                    } else {
                        location = "[Location].[Location]" + vdUtil.fn_filterStr(row["[Location].[Location]"].split("^"));
                    }										
					
					let dimchk = [];
					dimchk.push(fbVersion);
					dimchk.push(location);
					dimchk.push(vdUtil.fn_qDim(row, "[Item Material].[MSL5]"));
										
					// 기존 data 중복여부에 대한 체크
					if(!VdCommon.existMeasure(dimchk, ["Measure.[ECP Mst Lv5_ECP Flag]"], "")) {
						insertData.push(parsedParams.fbGridRows[i]);
					} else {
						validData.push(rowindex+" ^ This data is already exists!");
					}
				
				} else if( rowStatus == "D") {
					deleteData.push(parsedParams.fbGridRows[i]);
				} else if( rowStatus == "U") {
					updateData.push(parsedParams.fbGridRows[i]);
				}
			}

			if( validData.length > 0 ){
					return { "Code" : 1, "Msg" : validData };
			} else {
				VdCommon.debug("insertData.length :: "+insertData.length);

				for(var i=0;i<insertData.length; i++) {
					var iRow = insertData[i];
					
                    var location = "";
                    if ( vdUtil.fn_getString(iRow["[Location].[Location]"]) == "" ) {
                        location = "&NSUILocationMFMtrlView";
                    } else {
                        location = "[Location].[Location]" + vdUtil.fn_filterStr(iRow["[Location].[Location]"].split("^"));
                    }					

					// 데이타 생성
					var dimensions = [];
					dimensions.push(fbVersion);				
					dimensions.push(location);
					dimensions.push(vdUtil.fn_qDim(iRow, "[Item Material].[MSL5]"));

					var measures = [];
					measures.push(vdUtil.fn_qMeaStr(iRow, "Measure.[ECP Mst Lv5_ECP Flag]"));
					measures.push(vdUtil.fn_qMeaStr(iRow, "Measure.[ECP Mst Lv5_Air LT]"));
					measures.push(vdUtil.fn_qMeaUpdateUser("Measure.[ECP Mst Lv5_Created by]"));
					measures.push(vdUtil.fn_qMeaUpdateTime("Measure.[ECP Mst Lv5_Creation time]"));
					
					VdCommon.createMeasure(dimensions, measures);

				}

				VdCommon.debug("updateData.length :: "+updateData.length);

				for(var i=0;i<updateData.length; i++) {

					var uRow = updateData[i];

					var dimensions = [];
                    dimensions.push(fbVersion);
                    dimensions.push(vdUtil.fn_qDim(uRow, "[Location].[Location]"));
                    dimensions.push(vdUtil.fn_qDim(uRow, "[Item Material].[MSL5]"));

                    var measures = [];
                    measures.push(vdUtil.fn_qMeaStr(uRow, "Measure.[ECP Mst Lv5_ECP Flag]"));
                    measures.push(vdUtil.fn_qMeaStr(uRow, "Measure.[ECP Mst Lv5_Air LT]"));
                    measures.push(vdUtil.fn_qMeaUpdateUser("Measure.[ECP Mst Lv5_Updated by]"));
                    measures.push(vdUtil.fn_qMeaUpdateTime("Measure.[ECP Mst Lv5_Update time]"));

                    VdCommon.updateBlockMeasure(dimensions, measures);
				}
				
				VdCommon.debug("deleteData.length :: "+deleteData.length);

				for(var i=0;i<deleteData.length; i++) {
					var dRow = deleteData[i];
					
                    var where = [];
                    where.push(fbVersion);
                    where.push(vdUtil.fn_qDim(dRow, "[Location].[Location]"));
                    where.push(vdUtil.fn_qDim(dRow, "[Item Material].[MSL5]"));

                    VdCommon.deleteMeasure(where, "ECP Master Lv5");			

				}				
				
			}
			
			VdCommon.programEnd();
			return { "Code" : 0, "Msg" : "", "Rows" : "" };
		
        } catch ( e ) {
            return { "Code" : -1, "Msg" : e.message };
        }
    };

/*

{ "fbFuncName" : "fn_saveItmMat", 
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
	 "rowstatus":"C"
	,"rowindex":"0"
	,"[Version].[Version Name]":"CWV_MP"
	,"[Location].[Location]":"ZA10SA51^ZA10SA52"
	,"[Item Material].[Item Material]":"BN96-33321D^BN96-34502C"
	,"Measure.[ECP Mst Mtrl Item_ECP Flag]":"Y"
	,"Measure.[ECP Mst Mtrl Item_Air LT]":"2"
	}
  ]
}

{ "fbFuncName" : "fn_saveItmMat", 
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
	,"[Version].[Version Name]":"CWV_MP"
	,"[Location].[Location]":"ZA10SA52"
	,"[Item Material].[Item Material]":"BN96-34502C"
	,"Measure.[ECP Mst Mtrl Item_ECP Flag]":"N"
	,"Measure.[ECP Mst Mtrl Item_Air LT]":"33"
	}
  ]
}

{ "fbFuncName" : "fn_saveItmMat", 
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
	 "rowstatus":"D"
	,"rowindex":"0"
	,"[Version].[Version Name]":"CWV_MP"
	,"[Location].[Location]":"ZA10SA52"
	,"[Item Material].[Item Material]":"BN96-34502C"
	,"Measure.[ECP Mst Mtrl Item_ECP Flag]":"N"
	,"Measure.[ECP Mst Mtrl Item_Air LT]":"33"
	}
  ]
}
*/
    const fn_saveItmMat = function (parsedParams) {
		const VdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
        VdCommon.setLogLevel("Debug");
		VdCommon.debug("parsedParams :: "+JSON.stringify(parsedParams));
	
        try{
            var insertData = [];
			var validData = [];
			var updateData = [];
			var deleteData = [];
			
			var fbVersion = "[Version].[Version Name].["+vdUtil.fn_getFilterValue(parsedParams,"[Version].[Version Name]")+"]"; 

			for ( var i = 0; i < parsedParams.fbGridRows.length; i++ ) {
				var row = parsedParams.fbGridRows[i];
				let rowStatus     = row["rowstatus"];
				var rowindex 	  = row["rowindex"];

				// 데이터 구분
				if( rowStatus == "C") {
					
                    var location = "";
                    if ( vdUtil.fn_getString(row["[Location].[Location]"]) == "" ) {
                        location = "&NSUILocationMFMtrlView";
                    } else {
                        location = "[Location].[Location]" + vdUtil.fn_filterStr(row["[Location].[Location]"].split("^"));
                    }		

                    var material =  "[Item Material].[Item Material]" + vdUtil.fn_filterStr(row["[Item Material].[Item Material]"].split("^"));

					let dimchk = [];
					dimchk.push(fbVersion);
					dimchk.push(location);
					dimchk.push(material);
										
					// 기존 data 중복여부에 대한 체크
					if(!VdCommon.existMeasure(dimchk, ["Measure.[ECP Mst Mtrl Item_ECP Flag]"], "")) {
						insertData.push(parsedParams.fbGridRows[i]);
					} else {
						validData.push(rowindex+" ^ This data is already exists!");
					}
				
				} else if( rowStatus == "D") {
					deleteData.push(parsedParams.fbGridRows[i]);
				} else if( rowStatus == "U") {
					updateData.push(parsedParams.fbGridRows[i]);
				}
			}

			if( validData.length > 0 ){
					return { "Code" : 1, "Msg" : validData };
			} else {
				VdCommon.debug("insertData.length :: "+insertData.length);

				for(var i=0;i<insertData.length; i++) {
					var iRow = insertData[i];
					
                    var location = "";
                    if ( vdUtil.fn_getString(iRow["[Location].[Location]"]) == "" ) {
                        location = "&NSUILocationMFMtrlView";
                    } else {
                        location = "[Location].[Location]" + vdUtil.fn_filterStr(iRow["[Location].[Location]"].split("^"));
                    }					

                    var material =  "[Item Material].[Item Material]" + vdUtil.fn_filterStr(row["[Item Material].[Item Material]"].split("^"));	

					// 데이타 생성
					var dimensions = [];
					dimensions.push(fbVersion);				
					dimensions.push(location);
					dimensions.push(material);

					var measures = [];
					measures.push(vdUtil.fn_qMeaStr(iRow, "Measure.[ECP Mst Mtrl Item_ECP Flag]"));
					measures.push(vdUtil.fn_qMeaStr(iRow, "Measure.[ECP Mst Mtrl Item_Air LT]"));
					measures.push(vdUtil.fn_qMeaUpdateUser("Measure.[ECP Mst Mtrl Item_Created by]"));
					measures.push(vdUtil.fn_qMeaUpdateTime("Measure.[ECP Mst Mtrl Item_Creation time]"));
					
					VdCommon.createMeasure(dimensions, measures);

				}

				VdCommon.debug("updateData.length :: "+updateData.length);

				for(var i=0;i<updateData.length; i++) {

					var uRow = updateData[i];

					var dimensions = [];
                    dimensions.push(fbVersion);
                    dimensions.push(vdUtil.fn_qDim(uRow, "[Location].[Location]"));
                    dimensions.push(vdUtil.fn_qDim(uRow, "[Item Material].[Item Material]"));

                    var measures = [];
                    measures.push(vdUtil.fn_qMeaStr(uRow, "Measure.[ECP Mst Mtrl Item_ECP Flag]"));
                    measures.push(vdUtil.fn_qMeaStr(uRow, "Measure.[ECP Mst Mtrl Item_Air LT]"));
                    measures.push(vdUtil.fn_qMeaUpdateUser("Measure.[ECP Mst Mtrl Item_Updated by]"));
                    measures.push(vdUtil.fn_qMeaUpdateTime("Measure.[ECP Mst Mtrl Item_Update time]"));

                    VdCommon.updateBlockMeasure(dimensions, measures);
				}
				
				VdCommon.debug("deleteData.length :: "+deleteData.length);

				for(var i=0;i<deleteData.length; i++) {
					var dRow = deleteData[i];
					
                    var where = [];
                    where.push(fbVersion);
                    where.push(vdUtil.fn_qDim(dRow, "[Location].[Location]"));
                    where.push(vdUtil.fn_qDim(dRow, "[Item Material].[Item Material]"));

                    VdCommon.deleteMeasure(where, "ECP Master Material Item");			

				}				
				
			}
			
			VdCommon.programEnd();
			return { "Code" : 0, "Msg" : "", "Rows" : "" };
		
        } catch ( e ) {
            return { "Code" : -1, "Msg" : e.message };
        }
    };


   // { "fbFuncName" : "fn_cb_item", "fbParams" : { "[Item Material].[MSL3]" : "Panel>EB Panel>EB 완Panel", "[Item Material].[MSL4]" : "Panel>EB Panel>EB 완Panel>40~54" } }
	var fn_cb_item = function(parsedParams){
        const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
        vdCommon.setLogLevel("Debug");

		try {
            var msl3 = vdUtil.fn_getParam(parsedParams, "[Item Material].[MSL3]");
            var msl4 = vdUtil.fn_getParam(parsedParams, "[Item Material].[MSL4]");
            var msl5 = vdUtil.fn_getParam(parsedParams, "[Item Material].[MSL5]");

            // 등록된 데이타를 가져온다.
            var rExistItem = vdCommon.selectList(["&CWVUI",
                                                    "[Item Material].[MSL3]" + vdUtil.fn_filterStr(msl3),
                                                    "[Item Material].[MSL4]" + ( msl4 == "All" ? "" : vdUtil.fn_filterStr(msl4) ),
                                                    "[Item Material].[MSL5]" + ( msl5 == "All" ? "" : vdUtil.fn_filterStr(msl5) ),
                                                    "[Item Material].[Item Material]",
                                                    "[Location].[Location]"],
                                                ["Measure.[SS Mtrl Item_Source]"],
                                                "", "", "");

            var validHm = {};
            for ( var i = 0; i < rExistItem.cs.rowCount; i++ ) {
                item = vdCommon.getMember(rExistItem.cs, i, "Item Material", "Item Material").Name;

                if ( validHm[item] == undefined ) {
                    validHm[item] = item;
                }
            }
            //vdCommon.debug("validHm : " + JSON.stringify(validHm));

            var comboList = [];
            var rItem = vdCommon.selectList(["[Item Material].[MSL3]" + vdUtil.fn_filterStr(msl3),
                                                "[Item Material].[MSL4]" + ( msl4 == "All" ? "" : vdUtil.fn_filterStr(msl4) ),
                                                "[Item Material].[MSL5]" + ( msl5 == "All" ? "" : vdUtil.fn_filterStr(msl5) ),
                                                "[Item Material].[Item Material]"],
                                            [],
                                            "", "", "");
            for ( var i = 0; i < rItem.cs.rowCount; i++ ) {
                item = rItem.cs.row(i).cell(rItem.cs.memberColumnIndex("Item Material", "Item Material")).Name;

                if ( validHm[item] == undefined ) {
                    comboList.push({ Name : item, DisplayName : item});
                }
            }

            // 정렬
            comboList.sort((a, b) => {
                    if ( a.Name < b.Name ) return -1;
                    if ( a.Name > b.Name ) return 1;
                    return 0;
                });

            vdCommon.programEnd();

            return { "Code" : 0, "Msg" : "", "Rows" : comboList };
        } catch ( e ) {
            vdCommon.error(e.message);
            return { "Code" : -1, "Msg" : e.message };
        }
    };



    // { "fbFuncName" : "fn_cb_msl345" }
	var fn_cb_msl345 = function(parsedParams){
        const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
        vdCommon.setLogLevel("Debug");

		try {
            var result = vdCommon.selectList(["&NSUIMtrlMSL3View", "&NSUIMtrlMSL4View", "&NSUIMtrlMSL5View"],
                                            [],
                                            "", "orderby [Item Material].[MSL5].[MSL5 Sorting Order]", "");
            var comboList = vdCommon.fn_makeCombo(result, {DimName : "Item Material", DimAttbName : "MSL5", includeField : "Item Material:MSL3:MSL3,Item Material:MSL4:MSL4"});
            vdCommon.debug("ComboData : " + JSON.stringify(comboList.slice(0,3)));

            // All 추가
            comboList.unshift({Name : "All", DisplayName : "All", MSL3 : "All", MSL3_DisplayName : "All", MSL3_DisplayAlias : "All", MSL4 : "All", MSL4_DisplayName : "All", MSL4_DisplayAlias : "All"});

            vdCommon.programEnd();

            return { "Code" : 0, "Msg" : "", "Rows" : comboList };
        } catch ( e ) {
            vdCommon.error(e.message);
            return { "Code" : -1, "Msg" : e.message };
        }
    };
	

    // { "fbFuncName" : "fn_cb_msl34" }
	var fn_cb_msl34 = function(parsedParams){
        const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
        vdCommon.setLogLevel("Debug");

		try {
            var result = vdCommon.selectList(["&NSUIMtrlMSL3View", "&NSUIMtrlMSL4View"],
                                            [],
                                            "", "orderby [Item Material].[MSL4].[MSL4 Sorting Order]", "");
            var comboList = vdCommon.fn_makeCombo(result, {DimName : "Item Material", DimAttbName : "MSL4", includeField : "Item Material:MSL3:MSL3"});
            vdCommon.debug("ComboData : " + JSON.stringify(comboList.slice(0,3)));

            // All 추가
            comboList.unshift({Name : "All", DisplayName : "All", MSL3 : "All", MSL3_DisplayName : "All", MSL3_DisplayAlias : "All"});

            vdCommon.programEnd();

            return { "Code" : 0, "Msg" : "", "Rows" : comboList };
        } catch ( e ) {
            vdCommon.error(e.message);
            return { "Code" : -1, "Msg" : e.message };
        }
    };	
	
    // { "fbFuncName" : "fn_cb_msl23" }
	var fn_cb_msl23 = function(parsedParams){
        const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
        vdCommon.setLogLevel("Debug");

		try {
            var result = vdCommon.selectList(["&NSUIMtrlMSL2View", "&NSUIMtrlMSL3View"],
                                            [],
                                            "", "orderby [Item Material].[MSL3].[MSL3 Sorting Order]", "");
            var comboList = vdCommon.fn_makeCombo(result, {DimName : "Item Material", DimAttbName : "MSL3", includeField : "Item Material:MSL2:MSL2"});
            vdCommon.debug("ComboData : " + JSON.stringify(comboList.slice(0,3)));

            vdCommon.programEnd();

            return { "Code" : 0, "Msg" : "", "Rows" : comboList };
        } catch ( e ) {
            vdCommon.error(e.message);
            return { "Code" : -1, "Msg" : e.message };
        }
    };	
	
    // { "fbFuncName" : "fn_cb_msl12" }
	var fn_cb_msl12 = function(parsedParams){
        const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
        vdCommon.setLogLevel("Debug");

		try {
            var result = vdCommon.selectList(["&NSUIMtrlMSL1View", "&NSUIMtrlMSL2View"],
                                            [],
                                            "", "orderby [Item Material].[MSL2].[MSL2 Sorting Order]", "");
            var comboList = vdCommon.fn_makeCombo(result, {DimName : "Item Material", DimAttbName : "MSL2", includeField : "Item Material:MSL1:MSL1"});
            vdCommon.debug("ComboData : " + JSON.stringify(comboList.slice(0,3)));

            vdCommon.programEnd();

            return { "Code" : 0, "Msg" : "", "Rows" : comboList };
        } catch ( e ) {
            vdCommon.error(e.message);
            return { "Code" : -1, "Msg" : e.message };
        }
    };	
	
    // { "fbFuncName" : "fn_cb_msl1" }
	var fn_cb_msl1 = function(parsedParams){
        const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
        vdCommon.setLogLevel("Debug");

		try {
            var result = vdCommon.selectList(["&NSUIMtrlMSL1View"],
                                            [],
                                            "", "orderby [Item Material].[MSL1].[MSL1 Sorting Order]", "");
            var comboList = vdCommon.fn_makeCombo(result, {DimName : "Item Material", DimAttbName : "MSL1"});
            vdCommon.debug("ComboData : " + JSON.stringify(comboList.slice(0,3)));

            vdCommon.programEnd();

            return { "Code" : 0, "Msg" : "", "Rows" : comboList };
        } catch ( e ) {
            vdCommon.error(e.message);
            return { "Code" : -1, "Msg" : e.message };
        }
    };

    // { "fbFuncName" : "fn_cb_plant" }
	var fn_cb_plant = function(parsedParams){
        const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
        vdCommon.setLogLevel("Debug");

		try {
            var result = vdCommon.selectList(["&NSUILocationMFMtrlView"],
                                            [],
                                            "", "", "");
            var comboList = vdCommon.fn_makeCombo(result, {DimName : "Location", DimAttbName : "Location", Sort : "Name", isDisplayNameWithCode : true});
            vdCommon.debug("ComboData : " + JSON.stringify(comboList.slice(0,3)));

            vdCommon.programEnd();

            return { "Code" : 0, "Msg" : "", "Rows" : comboList };
        } catch ( e ) {
            vdCommon.error(e.message);
            return { "Code" : -1, "Msg" : e.message };
        }
    };	

/*
EWCOECPMasterPopUp
{ "fbFuncName" : "fn_save", 
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
	,"[Version].[Version Name]":"CWV_MP"
	,"[Location].[Location]":"P537"
	,"Measure.[ECP Mst Pop_ECP LT]":"33"
	}
  ]
}
*/
    const fn_save = function (parsedParams) {
		const VdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
        VdCommon.setLogLevel("Debug");
		VdCommon.debug("parsedParams :: "+JSON.stringify(parsedParams));
	
        try{
            var insertData = [];
			var validData = [];
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
				dimensions.push(vdUtil.fn_qDim(uRow, "[Location].[Location]"));				

				var measures = [];
				measures.push(vdUtil.fn_qMeaStr(uRow, "Measure.[ECP Mst Pop_ECP LT]"));

				measures.push(vdUtil.fn_qMeaUpdateUser("Measure.[ECP Mst Pop_Updated by]"));
				measures.push(vdUtil.fn_qMeaUpdateTime("Measure.[ECP Mst Pop_Update time]"));

				VdCommon.updateMeasure(dimensions, measures);
			}

			VdCommon.programEnd();
			return { "Code" : 0, "Msg" : "", "Rows" : "" };
		
        } catch ( e ) {
            return { "Code" : -1, "Msg" : e.message };
        }
    };



/************************************************* util logic *************************************************/

/************************************************* Mapping logic **********************************************/
    // Mapping 함수 정의, 마지막에 선언을 해야 함수를 정상적으로 인식함
    const functionMap = {
        "fn_saveLv3" : fn_saveLv3
	   ,"fn_saveLv4" : fn_saveLv4
	   ,"fn_saveLv5" : fn_saveLv5
	   ,"fn_saveItmMat" : fn_saveItmMat
	   ,"fn_cb_plant" : fn_cb_plant
       ,"fn_cb_msl1" : fn_cb_msl1
       ,"fn_cb_msl12" : fn_cb_msl12
       ,"fn_cb_msl23" : fn_cb_msl23
       ,"fn_cb_msl34" : fn_cb_msl34
       ,"fn_cb_msl345" : fn_cb_msl345
	   ,"fn_cb_item" : fn_cb_item
	   ,"fn_save" : fn_save
    };

    return {
        fn_loadFunction : fn_loadFunction
    };
});
/******************************** o9.NSCM.JSEWVDECPMaster *******************************
**************************************************************************************/

/**************************** o9.NSCM.JSEWVDECPMaster ****************************
26.02.23 : 신규생성
**************************** o9.NSCM.JSEWVDECPMaster ****************************/