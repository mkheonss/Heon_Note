define('o9.NSCM.JSEWCapaSimulation', ['o9/data/query', 'o9/data/cellset', 'o9.NSCM.commonLib'], function(){	
	const programName = "o9.NSCM.JSEWCapaSimulation";
    const commonLib = require('o9.NSCM.commonLib');
    const vdUtil = new commonLib.VdUtil();
    /*--------------------------------------------------------------------------------------------------*/
    // 프로그램명 : o9.NSCM.JSEWCapaSimulation
    // Action Button : EWCapaSimul
    // 화면명 : Capa Simulation(EW)
    // 2025.12.17 최초 생성
    // 2025.12.30 fn_simulation() 추가함. : PY_UI_CapaSimulationUpdate 파이썬 호출
    // 2025.12.31 fn_loadFunction() 수정함. => parsedParams 값 체크 로직 추가
    // 2026.02.12 fn_save() 추가함.
    /*--------------------------------------------------------------------------------------------------*/    
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
            if ( parsedParams.fbParams["includeProperty"] == undefined ) {
                parsedParams.fbParams["includeProperty"] = "";
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
            // 콤보에 Blank 추가
            if ( parsedParams.fbParams["existBlank"] == undefined ) {
                parsedParams.fbParams["existBlank"] = false;
            }
            // 콤보에 - 추가
            if ( parsedParams.fbParams["existHyphen"] == undefined ) {
                parsedParams.fbParams["existHyphen"] = false;
            }
            // where 조건 추가
            if ( parsedParams.fbParams["where"] == undefined ) {
                parsedParams.fbParams["where"] = {};
            }
            if ( parsedParams.fbParams["isDisplayNameWithCode"] == undefined ) {
                parsedParams.fbParams["isDisplayNameWithCode"] = true;
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

    /*{"fbFuncName" : "fn_apply", 
            "fbParams":
            {"version":"CWV_MP", 
            "filters":{
                    "[Version].[Version Name]":{"SelectedMembers":["CWV_MP"],"SelectedMembersAlias":["202547"],"MemberFilter":"&CWVUI","DimensionAliasName":"Plan ID"}
                    ,"[Category].[Category]":{"SelectedMembers":[],"SelectedMembersAlias":[],"MemberFilter":"Category.[Category].filter(#.Name in {\"Auto\",\"Normal\"})"}
                    ,"[Location].[Site Group1]":{"SelectedMembers":[],"SelectedMembersAlias":[],"MemberFilter":"&NSUISiteGrp1MFView","DimensionAliasName":"<MF>"}
                    ,"[Location].[Site Group2]":{"SelectedMembers":[],"SelectedMembersAlias":[],"MemberFilter":"&NSUISiteGrp2MFView","DimensionAliasName":"<MF>"}
                    ,"[Location].[Site Group3]":{"SelectedMembers":[],"SelectedMembersAlias":[],"MemberFilter":"&NSUISiteGrp3MFView","DimensionAliasName":"<MF>"}
                    ,"[Location].[Site Group4]":{"SelectedMembers":[],"SelectedMembersAlias":[],"MemberFilter":"&NSUISiteGrp4MFView","DimensionAliasName":"<MF>"}
                    ,"[Line].[Line]" : {"SelectedMembers" : ["L01", "L03"], "MemberFilter" : ""}
                    ,"[Time].[Week]" : {"SelectedMembers":  [ "202549", "202550", "202551", "202552", "202601"],"MemberFilter":"Time.[Planning Month].filter(#.Key < &CurrentMonth.element(0).LeadOffset(3).Key && #.Key >= &CurrentMonth.element(0).LeadOffset(0).Key).relatedmembers([Week])"} 
                    }
            }
        }
    */
    var fn_apply = function (parsedParams) {
        const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
        vdCommon.setLogLevel("Debug");
		try {           
            //let fbFilters = parsedParams.fbParams["filters"];
            let fbFilters = vdUtil.fn_getParam(parsedParams, "filters");
            //let fbVersion = parsedParams.fbParams["version"];
            let fbVersion = vdUtil.fn_getFilterValue(parsedParams,"[Version].[Version Name]");
            let fbCategory = "";
            let fbLine = "";
            let fbTimeWeek = "";
            vdCommon.debug("["+fbFilters+"]["+fbVersion+"]");

            let selectQuery = "";            
            selectQuery = 'Select([Version].[Version Name]'+vdUtil.fn_filterStr(String(fbVersion).split(","));
            selectQuery += ' * [Location].[Location]';
            selectQuery += ' * '+ vdUtil.fn_getFilterQuery(parsedParams, "[Time].[Week]");
            selectQuery += ' * '+ vdUtil.fn_getFilterQuery(parsedParams, "[Line].[Line]");
            selectQuery += ') on row';
            selectQuery += ',({Measure.[Capa Simul_OT Mins], Measure.[Capa Simul_Sat Mins], ';
            selectQuery += 'Measure.[Capa Simul_Base Capa Mins], Measure.[Capa Simul_2nd Shift Mins], Measure.[Capa Simul_2nd Shift Eff]}) on column ';
            selectQuery += 'Where{[Group].[Group ID]';
            selectQuery += ','+vdUtil.fn_getFilterQuery(parsedParams, "[Category].[Category]");
            selectQuery += ','+vdUtil.fn_getFilterQuery(parsedParams, "[Location].[Site Group1]");
            selectQuery += ','+vdUtil.fn_getFilterQuery(parsedParams, "[Location].[Site Group2]");
            selectQuery += ','+vdUtil.fn_getFilterQuery(parsedParams, "[Location].[Site Group3]");
            selectQuery += ','+vdUtil.fn_getFilterQuery(parsedParams, "[Location].[Site Group4]");
            selectQuery += ' };';

            let selectResult = vdCommon.selectQueryList("fn_apply(Select)", selectQuery);

            for(var k = 0; k < selectResult.rowCount; k++){
                let rLocation = selectResult.cs.row(k).cell(selectResult.cs.memberColumnIndex("Location", "Location")).Name;
                let rLine = selectResult.cs.row(k).cell(selectResult.cs.memberColumnIndex("Line", "Line")).Name;
                let rTimeWeek = selectResult.cs.row(k).cell(selectResult.cs.memberColumnIndex("Time", "Week")).Name;

                let otMins = vdCommon.getMeasureValue(selectResult.cs, k, "Capa Simul_OT Mins");
                let satMins = vdCommon.getMeasureValue(selectResult.cs, k, "Capa Simul_Sat Mins");
                let shiftMins_2nd = vdCommon.getMeasureValue(selectResult.cs, k, "Capa Simul_2nd Shift Mins");
                let shiftEff_2nd = vdCommon.getMeasureValue(selectResult.cs, k, "Capa Simul_2nd Shift Eff");
                let baseCapaMins = vdCommon.getMeasureValue(selectResult.cs, k, "Capa Simul_Base Capa Mins");

                //MG[Work Cal Line] Measure.[Work Cal Line_Time] 데이타를 업데이트함.
                let updateDimension = [];
                let updateMeasure = [];                

                //updateDimension.push('[Version].[Version Name].['+fbVersion+']');
                updateDimension.push('[Version].[Version Name]'+vdUtil.fn_filterStr(String(fbVersion).split(",")));
                updateDimension.push('[Location].[Location].['+rLocation+']');
                updateDimension.push('[Time].[Week].['+rTimeWeek+']');
                updateDimension.push('[Line].[Line].['+rLine+']');

                let sumTime = (vdUtil.fn_isInt(otMins) ? otMins : 0) + (vdUtil.fn_isInt(satMins) ? satMins : 0);
                updateMeasure.push('Measure.[Work Cal Line_Time] = ' + Math.round(sumTime/60) + ";" ) ;

                vdCommon.updateMeasure(updateDimension, updateMeasure);

                // MG[Line Eff W] Measure.[Line Eff W] 데이타를 업데이트함.
                let updateMeasureEff = [];
                //let effRatio = 100 + Math.round((vdUtil.fn_isInt(shiftEff_2nd) ? (vdUtil.fn_isInt(baseCapaMins) ? ((shiftMins_2nd/baseCapaMins) * (shiftEff_2nd*100)) : 0) : 0)) ;
                vdCommon.debug("[1nd Shift (min)="+baseCapaMins+"][2nd Shift (min)="+shiftMins_2nd+"][2nd Shift Eff.(%)="+(shiftEff_2nd * 100)+"]")
                let effRatio = 100 + (vdUtil.fn_isInt(baseCapaMins) ? (shiftMins_2nd/baseCapaMins) * (shiftEff_2nd *100) : 0);
                updateMeasureEff.push('Measure.[Line Eff W] = ' + effRatio + ";") ;

                vdCommon.updateMeasure(updateDimension, updateMeasureEff);

            }
            return { "Code" : 0, "Msg" : "", "Rows" : "" };

        } catch ( e ) {
            vdCommon.error(e.message);
            return { "Code" : -1, "Msg" : e.message };
        }
    }

    //{ "fbFuncName" : "fn_simulation" }
    /*파이썬 처리 결과 
    Capa Simul_SOP: 정상적으로 Update
    Capa Simul_SOP Sec Total: 정상적으로 Update
    Capa Simul_SOP Pcs Total: 정상적으로 Update
    Capa Simul_Base Capa Sec: Reporting Measure (반영 X)
    Capa Simul_OT Sat Sec: Reporting Measure (반영 X)
    Capa Simul_Capa Sec Total: Reporting Measure (반영 X)
    Capa Simul_Capa Sec Total Org: 정상적으로 Update
    */
    var fn_simulationOld = function (parsedParams) {
        const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
        vdCommon.setLogLevel("Debug");
		try { 
            let fbVersion = vdUtil.fn_getFilterValue(parsedParams,"[Version].[Version Name]");
            let fbTimeWeeks = vdUtil.fn_getFilterValue(parsedParams,"[Time].[Week]");

            //파이썬 호출
            let execQuery = 'EXEC plugin instance [PY_UI_CapaSimulationUpdate] for measures {[Capa Simul_SOP Sec Total], [Capa Simul_SOP Pcs Total]} ' +
                    'using scope ([Version].[Version Name].filter(#.Name == "'+fbVersion+'") * [Time].[Week]'+vdUtil.fn_filterStr(fbTimeWeeks)+') ' +
                    'using arguments {(ExecutionMode, "MediumWeight"), ("IncludeNullRows", "False"), (paramOutVersion , "'+fbVersion+'"), ' +
                    '(MaxSliceTableCells, 200000000), (MaxConcurrency, 1 ), ([Param.o9_sys_log_level], "DEBUG")};' ;

            vdCommon.executeQuery("fn_simulation ", execQuery);   

            return { "Code" : 0, "Msg" : "", "Rows" : "" };

        } catch ( e ) {
            vdCommon.error(e.message);
            return { "Code" : -1, "Msg" : e.message };
        }
    };
    
    /*
    { "fbFuncName" : "fn_simulation" 
        "fbParams" : {
            "where":{"StartWeek":"202608", "EndWeek":"202610"}
        }
    }*
    /*파이썬 처리 결과 
    Capa Simul_SOP: 정상적으로 Update
    Capa Simul_SOP Sec Total: 정상적으로 Update
    Capa Simul_SOP Pcs Total: 정상적으로 Update
    Capa Simul_Base Capa Sec: Reporting Measure (반영 X)
    Capa Simul_OT Sat Sec: Reporting Measure (반영 X)
    Capa Simul_Capa Sec Total: Reporting Measure (반영 X)
    Capa Simul_Capa Sec Total Org: 정상적으로 Update
    */
    var fn_simulation = function (parsedParams) {
        const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
        vdCommon.setLogLevel("Debug");
		try { 
            let fbVersion = vdUtil.fn_getFilterValue(parsedParams,"[Version].[Version Name]");
            //let fbTimeWeeks = vdUtil.fn_getFilterValue(parsedParams,"[Time].[Week]");
            let fbWhere = parsedParams.fbParams["where"];
            let fbStartWeek = fbWhere["StartWeek"];
            let fbEndWeek = fbWhere["EndWeek"];
//select Time.[Week].filter(#.Name >= "{{StartWeek}}" && #.Name <= "{{EndWeek}}");
            let selectWeek = 'Select ([Time].[Week].filter(#.Name >= "'+fbStartWeek+'" && #.Name <= "'+fbEndWeek+'"))';

            let result = vdCommon.selectQueryList('selectWeek', selectWeek);
            let comboList = vdCommon.fn_makeCombo(result, {DimName: "Time", DimAttbName: "Week", Sort: "DisplayName", 
                                                existAll: false, isDisplayNameWithCode: false});
            let arrayWeek = comboList.map((value) => value.Name);

            //파이썬 호출
            let execQuery = 'EXEC plugin instance [PY_UI_CapaSimulationUpdate] for measures {[Capa Simul_SOP Sec Total], [Capa Simul_SOP Pcs Total]} ' +
                    'using scope ([Version].[Version Name].filter(#.Name == "'+fbVersion+'") * [Time].[Week]' + vdUtil.fn_filterStr(arrayWeek)+') ' +
                    'using arguments {(ExecutionMode, "MediumWeight"), ("IncludeNullRows", "False"), (paramOutVersion , "'+fbVersion+'"), ' +
                    '(MaxSliceTableCells, 200000000), (MaxConcurrency, 1 ), ([Param.o9_sys_log_level], "DEBUG")};' ;

            vdCommon.executeQuery("fn_simulation ", execQuery);   

            return { "Code" : 0, "Msg" : "", "Rows" : "" };

        } catch ( e ) {
            vdCommon.error(e.message);
            return { "Code" : -1, "Msg" : e.message };
        }
    }

/*{"fbFuncName":"fn_save",
"fbParams":{"version":"CWV_MP",
"filters":{
"[Version].[Version Name]":{"SelectedMembers":["CWV_MP"],"SelectedMembersAlias":["202547"],"MemberFilter":"&NSUIVersionDefaultFilterView","DimensionAliasName":"Plan ID"},
"[Location].[Site Group1]":{"SelectedMembers":[],"SelectedMembersAlias":[],"MemberFilter":"&NSUISiteGrp1MFView","DimensionAliasName":"<MF>"},
"[Location].[Site Group2]":{"SelectedMembers":[],"SelectedMembersAlias":[],"MemberFilter":"&NSUISiteGrp2MFView","DimensionAliasName":"<MF>"},
"[Location].[Site Group3]":{"SelectedMembers":[],"SelectedMembersAlias":[],"MemberFilter":"&NSUISiteGrp3MFView","DimensionAliasName":"<MF>"},
"[Location].[Site Group4]":{"SelectedMembers":[],"SelectedMembersAlias":[],"MemberFilter":"&NSUISiteGrp4MFView","DimensionAliasName":"<MF>"},
"[Group].[Group ID]":{"SelectedMembers":[],"SelectedMembersAlias":[],"MemberFilter":""},
"[Category].[Category]":{"SelectedMembers":[],"SelectedMembersAlias":[],"MemberFilter":"Category.[Category].filter(#.Name in {[Auto],[Normal]})"},
"[Line].[Line]":{"SelectedMembers":[],"SelectedMembersAlias":[],"MemberFilter":""},
"[Time].[Week]":{"SelectedMembers":[],"SelectedMembersAlias":[],"MemberFilter":"Time.[Planning Month].filter(#.Key < &CurrentMonth.element(0).LeadOffset(3).Key && #.Key >= &CurrentMonth.element(0).LeadOffset(0).Key).relatedmembers([Week])","DimensionAliasName":"Horizon"}
},
"reportName":"[NSCM] EW VD Capa Simulation","menuName":"Capa Simulation"}
,"fbGridRows":[
{"rowstatus":"U","rowindex":0,"[Version].[Version Name]":"CWV_MP","[Location].[Location]":"P306","[Group].[Group ID]":"VD1","[Category].[Category]":"Auto","[Line].[Line]":"M01","[MeasureName]":"Capa Simul_Capa Sec Total"
,"Week202547":472668,"Week202547_bg":"CellColorBlue"
,"Week202548":"100","Week202548_bg":""
},
{"rowstatus":"U","rowindex":0,
"[Version].[Version Name]":"CWV_MP","[Location].[Location]":"P306","[Group].[Group ID]":"VD1","[Category].[Category]":"Auto","[Line].[Line]":"M01","[MeasureName]":"Capa Simul_OT Sat Sec"
,"Week202547": 31260, "Week202547_bg":"CellColorBlue","Week202548":100,"Week202548_bg":""},
{"rowstatus":"U","rowindex":0,"[Version].[Version Name]":"CWV_MP","[Location].[Location]":"P306","[Group].[Group ID]":"VD1","[Category].[Category]":"Auto","[Line].[Line]":"M01","[MeasureName]":"Capa Simul_2nd Shift Sec"
,"Week202547": 113808.00000000000, "Week202547_bg":"CellColorBlue","Week202548":100,"Week202548_bg":""},
{"rowstatus":"U","rowindex":0,"[Version].[Version Name]":"CWV_MP","[Location].[Location]":"P306","[Group].[Group ID]":"VD1","[Category].[Category]":"Auto","[Line].[Line]":"M01","[MeasureName]":"Capa Simul_Capa SOP Sec Diff"
,"Week202547": 472283, "Week202547_bg":"CellColorBlue","Week202548":100,"Week202548_bg":""},
{"rowstatus":"U","rowindex":0,"[Version].[Version Name]":"CWV_MP","[Location].[Location]":"P306","[Group].[Group ID]":"VD1","[Category].[Category]":"Auto","[Line].[Line]":"M01","[MeasureName]":"Capa Simul_Line Utilization"
,"Week202547": 0.0011752136752136800, "Week202547_bg":"CellColorBlue","Week202548":100,"Week202548_bg":""},
{"rowstatus":"U","rowindex":0,"[Version].[Version Name]":"CWV_MP","[Location].[Location]":"P306","[Group].[Group ID]":"VD1","[Category].[Category]":"Auto","[Line].[Line]":"M01","[MeasureName]":"Capa Simul_Capa Pcs Total"
,"Week202547": 23.73822640838810, "Week202547_bg":"CellColorBlue","Week202548":100,"Week202548_bg":""},
{"rowstatus":"U","rowindex":0,"[Version].[Version Name]":"CWV_MP","[Location].[Location]":"P306","[Group].[Group ID]":"VD1","[Category].[Category]":"Auto","[Line].[Line]":"M01","[MeasureName]":"Capa Simul_Capa SOP Pcs Diff"
,"Week202547": -11.26177359161190, "Week202547_bg":"CellColorBlue","Week202548":100,"Week202548_bg":""},
{"rowstatus":"U","rowindex":0,"[Version].[Version Name]":"CWV_MP","[Location].[Location]":"P306","[Group].[Group ID]":"VD1","[Category].[Category]":"Auto","[Line].[Line]":"M01","[MeasureName]":"Capa Simul_Open Line"
,"Week202547": 2, "Week202547_bg":"CellBgLightYellow,CellColorBlue","Week202548":100,"Week202548_bg":""},
{"rowstatus":"U","rowindex":0,"[Version].[Version Name]":"CWV_MP","[Location].[Location]":"P306","[Group].[Group ID]":"VD1","[Category].[Category]":"Auto","[Line].[Line]":"M01","[MeasureName]":"Capa Simul_OT Mins"
,"Week202547": 40, "Week202547_bg":"CellBgLightYellow,CellColorBlue","Week202548":100,"Week202548_bg":""},
{"rowstatus":"U","rowindex":0,"[Version].[Version Name]":"CWV_MP","[Location].[Location]":"P306","[Group].[Group ID]":"VD1","[Category].[Category]":"Auto","[Line].[Line]":"M01","[MeasureName]":"Capa Simul_Sat Mins"
,"Week202547": 481, "Week202547_bg":"CellBgLightYellow,CellColorBlue","Week202548":100,"Week202548_bg":""},
{"rowstatus":"U","rowindex":0,"[Version].[Version Name]":"CWV_MP","[Location].[Location]":"P306","[Group].[Group ID]":"VD1","[Category].[Category]":"Auto","[Line].[Line]":"M01","[MeasureName]":"Capa Simul_2nd Shift Mins"
,"Week202547": 2371, "Week202547_bg":"CellBgLightYellow,CellColorBlue","Week202548":100,"Week202548_bg":""},
{"rowstatus":"U","rowindex":0,"[Version].[Version Name]":"CWV_MP","[Location].[Location]":"P306","[Group].[Group ID]":"VD1","[Category].[Category]":"Auto","[Line].[Line]":"M01","[MeasureName]":"Capa Simul_2nd Shift Eff"
,"Week202547": 0.8, "Week202547_bg":"CellBgLightYellow,CellColorBlue","Week202548":100,"Week202548_bg":""}
]
}*/
    var fn_save = function (parsedParams) {
        const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
        vdCommon.setLogLevel("Debug");
		try {
            let fbVersion = vdUtil.fn_getFilterValue(parsedParams,"[Version].[Version Name]");
            let fbTimeWeek = vdUtil.fn_getFilterNs(parsedParams, "[Time].[Week]")

            let bucketQuery = 'Select ('+fbTimeWeek+');';
            
            let bucketResult = vdCommon.selectQueryList("[bucketQuery]" ,bucketQuery );
            let bucketList = vdCommon.fn_makeCombo(bucketResult, {DimName : "Time", DimAttbName : "Week", Sort : "DisplayName"});

            
            for (var i = 0; i < parsedParams.fbGridRows.length; i++) {
                let row = parsedParams.fbGridRows[i];
                let rowStatus = row["rowstatus"];
                if(rowStatus != "U"){
                    continue;
                }
                let pVersion = row["[Version].[Version Name]"];
                let pLocation = row["[Location].[Location]"];
                let pLine = row["[Line].[Line]"];
                let pGroupID = row["[Group].[Group ID]"];
                let pCategory = row["[Category].[Category]"];

                if(pLine != "(All)" && pCategory != "(All)" && pGroupID != "(All)"){
                    for(var k = 0; k < bucketList.length; k++){
                        let dimensionQuery = [];              
                        let measureQuery = [];
                        dimensionQuery.push("[Version].[Version Name].["+pVersion+"]");
                        dimensionQuery.push("[Location].[Location].["+pLocation+"]");
                        dimensionQuery.push("[Group].[Group ID].["+pGroupID+"]");
                        dimensionQuery.push("[Category].[Category].["+pCategory+"]");
                        dimensionQuery.push("[Line].[Line].["+pLine+"]");
                        
                        let sWeek = bucketList[k]["Name"];
                        let bucketValue = parsedParams.fbGridRows[i]["Week" + sWeek];                         
                        let bucketBG = parsedParams.fbGridRows[i]["Week" + sWeek+"_bg"];
                        let measureName = parsedParams.fbGridRows[i]["[MeasureName]"];

                        vdCommon.debug("["+sWeek+"]["+bucketValue+"]["+bucketBG+"]["+measureName+"]");

                        //자동계산 Measure는 제외함.
                        if(measureName == "Capa Simul_Capa SOP Pcs Diff" || measureName == "Capa Simul_Capa SOP Sec Diff" 
                        || measureName == "Capa Simul_Line Utilization" || measureName == "Capa Simul_Capa Pcs Total"){                            
                            continue;
                        }

                        if(bucketBG == undefined){
                            continue;
                        }

                        if( bucketBG.indexOf("CellColorBlue") != -1){
                            dimensionQuery.push("[Time].[Week].["+sWeek+"]");
                            measureQuery.push("Measure.["+measureName+"] = "+bucketValue +";");

                            vdCommon.updateMeasure(dimensionQuery, measureQuery);
                        }
                    }
                }  
            }
            vdCommon.programEnd();
            return { "Code": 0, "Msg": "", "Rows": "" };

        } catch ( e ) {
            vdCommon.error(e.message);
            return { "Code" : -1, "Msg" : e.message };
        }
    };

    
/************************************************* Mapping logic *************************************************/
    // Mapping 함수 정의, 마지막에 선언을 해야 함수를 정상적으로 인식함
    const functionMap = {
        "fn_apply": fn_apply
      , "fn_simulation" : fn_simulation
      , "fn_save" : fn_save
    };

    return {
        fn_loadFunction : fn_loadFunction
    };    
});