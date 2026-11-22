define('o9.NSCM.JSEWSOPVolatility', ['o9/data/query', 'o9/data/cellset', 'o9.NSCM.commonLib'], function(){
    const programName = "o9.NSCM.JSEWSOPVolatility";
    const commonLib = require('o9.NSCM.commonLib');
    const vdUtil = new commonLib.VdUtil();

    /*--------------------------------------------------------------------------------------------------*/
    // 프로그램명 : o9.NSCM.JSEWSOPVolatility
    // Action Button : EWSOPVolatility
    // 화면명 : SOP Volatility
    // 2026.03.23 최초 생성
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
   /* ********************************************************************************** */
   /*{ "fbFuncName" : "fn_getPlanWeekForGetData" ,
        "fbParams":{
                "filters":{
                "[Version].[Version Name]":{"SelectedMembers":["CWV_MP"],"SelectedMembersAlias":["202547"],"MemberFilter":"&CWVUI","DimensionAliasName":"Plan ID"},
                "[Filter].[Filter]":{"SelectedMembers":[],"SelectedMembersAlias":[],"MemberFilter":"","SelectedMembersExp":"filter((#.[FilterSOPVolatilityAnalysisMethod] in {\"PSI\",\"Weekly\",\"Monthly First Week\", \"Monthly Last Week\"}))"},
                "[Plan Week].[Plan Week]":{"SelectedMembers":["202608"],"SelectedMembersAlias":["202608"],"MemberFilter":"[Plan Week].[Plan Week].filter(#.Name <= &CurrentPlanWeek.element(0).LeadOffset(0).Name && #.Name > &CurrentPlanWeek.element(0).LeadOffset(-30).Name)","DimensionAliasName":"Plan ID"},
                "[Compare With].[Compare With]":{"SelectedMembers":["W-16"],"SelectedMembersAlias":["W-16"],"MemberFilter":"","DimensionAliasName":"Compare With"},
                "[Time].[Week]":{"SelectedMembers":["202547","202548","202549","202550","202551","202552","202601","202602","202603","202604","202605","202606","202607","202608"],
                                "SelectedMembersAlias":[null,null,null,null,null,null,null,null,null,null,null,null,null,null],"MemberFilter":"&NSUIWeekFilterView","DimensionAliasName":"Horizon"}
                }
                ,"reportName":"[NSCM] EW VD SOP Volatility SET LCM","menuName":"SOP Volatility (SET/LCM) (EW)"
            }
   }*/
    var fn_getPlanWeekForGetData = function(parsedParams){
        const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
        vdCommon.setLogLevel("Debug");
        try{

            let analysisMethod = "";
            let filterInfo = vdUtil.fn_getFilter(parsedParams, "[Filter].[Filter]");
            let filterValue = filterInfo["SelectedMembersExp"];
            filterValue = filterValue.replace("filter","").replace("(","").replace(")","");
            filterValue = filterValue.split("&&");
            for(var k=0; k < filterValue.length; k++){
                if(filterValue[k].indexOf("[FilterSOPVolatilityAnalysisMethod]") > 0){
                    if(filterValue[k].indexOf("PSI") > 0){
                        analysisMethod = "PSI";
                    }else if(filterValue[k].indexOf("Weekly") > 0){
                        analysisMethod = "Weekly";
                    }else if(filterValue[k].indexOf("Monthly First Week") > 0){
                        analysisMethod = "First";
                    }else if(filterValue[k].indexOf("Monthly Last Week") > 0){
                        analysisMethod = "Last";
                    }
                }
            }

            //Compare With
            let compareWith = vdUtil.fn_getFilterValue(parsedParams, "[Compare With].[Compare With]");
            compareWith = String(compareWith).replace("W","");
            let compareSeq = parseInt(compareWith);
            let planWeek = vdUtil.fn_getFilterValue(parsedParams, "[Plan Week].[Plan Week]");

            //filter 주차 기준으로 조회함.
            let timeWeeks = vdUtil.fn_getFilterValue(parsedParams, "[Time].[Week]");
            let tiemWeekQuery = "Select ([Time].[Planning Month] * [Time].[Week]"+vdUtil.fn_filterStr(timeWeeks) +" ) on row, () on column ";
            tiemWeekQuery += "Where{[Time].[Day of Week].[MON]};" ;
            let resultTimeWeek = vdCommon.selectQueryList('TimeWeek', tiemWeekQuery);

            //추가로 조회 : Month 기준으로 주차를 조회함.
            let comboMonth = vdCommon.fn_makeCombo(resultTimeWeek, {DimName: "Time", DimAttbName: "Planning Month", Sort: "DisplayName", 
                                                existAll: false, isDisplayNameWithCode: false});
            arrayMonth = comboMonth.map((value) => value.Name);

            let timeWeekQuery2 = "Select ([Time].[Planning Month]"+vdUtil.fn_filterStr(arrayMonth)+" * [Time].[Week] ) on row, () on column ";
            timeWeekQuery2 += "Where{[Time].[Day of Week].[MON]};" ;
            let resultTimeWeek2 = vdCommon.selectQueryList('TimeWeek', timeWeekQuery2);

            /*let timeWeek1 = fn_dataFilter(resultTimeWeek);
            let timeWeek2 = fn_dataFilter(resultTimeWeek2);
            let unionTimeWeek = [...timeWeek1, ...timeWeek2];*/
            /* array1, array2 합집합 */
            /*const mapTemp = new Map();
            unionTimeWeek.forEach(item =>{ mapTemp.set(item.Week,item);});            
            const timeWeek = Array.from(mapTemp.values());*/
            let timeWeek = [];
            let timeWeek1 = fn_dataFilter(resultTimeWeek);

            if(analysisMethod != "PSI" && analysisMethod != "Weekly"){
                let timeWeek2 = fn_dataFilter(resultTimeWeek2);
                let unionTimeWeek = [...timeWeek1, ...timeWeek2]; 
                /* array1, array2 합집합 */
                const mapTemp = new Map();
                unionTimeWeek.forEach(item =>{ mapTemp.set(item.Week,item);});            
                timeWeek = Array.from(mapTemp.values());
            }else{
                timeWeek = timeWeek1;
            }              

            //1.Sorting
            let tiemWeeks = fn_sorting(timeWeek, "Week", "asc");

            //2. Sequence 체크
            let resultValue = [];
            for(var i = 0; i < tiemWeeks.length; i++){
                resultValue.push({"Month":timeWeek[i].Month, "Week":timeWeek[i].Week, "WeekSeq": i + 1 })
            }
            //vdCommon.debug("2.[SEQ]["+resultValue.length+"]" + JSON.stringify(resultValue));

            //3. PlanWeek info.
            let planWeekInfo = fn_planweekInfo(resultValue, planWeek);
            //vdCommon.debug("3.[planWeekInfo]" + JSON.stringify(planWeekInfo));

            //4. AnalysisMethod 별 체크
            vdCommon.debug("Shift Master["+analysisMethod+"]");
            let ShiftMaster = [];
            
            if(analysisMethod == "PSI"){
                ShiftMaster = fn_psi(resultValue,planWeekInfo);
            }else if(analysisMethod == "Weekly"){
                ShiftMaster = fn_weekly(resultValue,planWeekInfo);
            }else if(analysisMethod == "First"){
                let monthGroup = fn_monthGrouped(resultValue);
                ShiftMaster = fn_firstMonth(monthGroup,planWeekInfo);
            }else if(analysisMethod == "Last"){
                let monthGroup = fn_monthGrouped(resultValue);
                ShiftMaster = fn_lastMonth(monthGroup,planWeekInfo);
                ShiftMaster = fn_sorting(ShiftMaster, "week", "asc");                
            }
            vdCommon.debug("WeekDiff Master["+compareWith+"]");
            vdCommon.debug("resultValue["+JSON.stringify(resultValue)+"]");
            //5.Week Diff Master
            let WeekDiffMaster = fn_weekDiffMaster(resultValue, planWeekInfo, compareSeq);

            //+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

            return { "Code" : 0, "Msg" : "", "Rows": {"shiftMaster": ShiftMaster, "WeekDiffMaster":WeekDiffMaster} };

            //return { "Code" : 0, "Msg" : "", "Week": ""\"" };

        }catch (e) {
            return { "Code": -1, "Msg": e.message };
        }
    };

    var fn_dataFilter = function(result){
        const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
        vdCommon.setLogLevel("Debug");
        try{
            let array = [];
            for(var i=0; i < result.cs.rowCount; i++){
                let _month = result.cs.row(i).cell(result.cs.memberColumnIndex("Time", "Planning Month")).Name;
                let _week = result.cs.row(i).cell(result.cs.memberColumnIndex("Time", "Week")).Name;

                array.push({Month:_month, Week:_week});
            }

            return array;
        }catch (e) {
            return { "Code": -1, "Msg": e.message };
        }
    };
    
    var fn_sorting = function(array, key, sortType){

        const result = array.sort((a,b) =>{

            if(sortType == "desc"){

                if ( a[key] > b[key] ) return-1;
                if ( a[key] < b[key] ) return 1;
                return 0;
            }else{
                if ( a[key] < b[key] ) return -1;
                if ( a[key] > b[key] ) return 1;
                return 0;
            }
        });

        return result;
    }

    var fn_planweekInfo = function(result, planWeek){
        const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
        vdCommon.setLogLevel("Debug");
        let planWeekInfo = {};
        for(var k=0; k < result.length; k++){
            if(result[k].Week == planWeek){
                planWeekInfo["Month"] = result[k].Month;
                planWeekInfo["Week"] = result[k].Week;
                planWeekInfo["WeekSeq"] = result[k].WeekSeq;
                planWeekInfo["Weekly"] = 0;
                //vdCommon.debug("[Info-planweek]"+JSON.stringify(planWeekInfo[k]));
                return planWeekInfo;
            }
        }
    };
    
    var fn_psi = function(array, planWeekInfo){

        let result = [];
    
        for(var k=0; k < array.length; k++){
    
            result.push({"method":"psi", "week":array[k].Week, "shift":0}); 
        }
    
        return result;
    }    

    var fn_weekly = function(array, planWeekInfo){
        const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
        vdCommon.setLogLevel("Debug");
        
        let weekSeq = planWeekInfo.WeekSeq;
        let weeklyShift = 0;
        let result = [];
    
        for(var k=0; k < array.length; k++){
            weeklyShift = array[k].WeekSeq - weekSeq;
            array[k].Shift = weeklyShift;
    
            result.push({"method":"weekly", "week":array[k].Week, "shift":weeklyShift}); 
        }
    
        return result;
    }

    var fn_monthGrouped = function(array){    

        const monthGrouped = array.reduce((acc,cur) =>{
            if(!acc[cur.Month]) acc[cur.Month] = [];
            acc[cur.Month].push(cur);
            return acc;
        },{});
    
        return monthGrouped;
    }

    var fn_firstMonth = function(array, planWeekInfo){

        let weekSeq = planWeekInfo.WeekSeq;
        let result = [];
       
        Object.keys(array).forEach(Month=>{
            const sorted = fn_sorting(array[Month], "Week", "asc");
    
            let firstShift = 0 ;
            for(var k=0 ; k < sorted.length; k++){
                if(k == 0){
                    sorted[k].Flag = "F";
                    firstShift = sorted[k].WeekSeq - weekSeq;
                }else{
                    sorted[k].Flag = "-";
                } 
    
                result.push({"method":"firstweek", "week":sorted[k].Week, "shift":firstShift});          
            }
        });
        //console.log("[monthGrouped]" + JSON.stringify(result))
        const lastResult = Object.values(result).flat();
    
        return lastResult;
    }
    
    var fn_lastMonth = function(array, planWeekInfo){
    
        let weekSeq = planWeekInfo.WeekSeq;
        let result = [];  
       
        Object.keys(array).reverse().forEach(Month=>{
            const sorted = fn_sorting(array[Month], "Week", "desc");
    
            let lastShift = 0;
            for(var k=0 ; k < sorted.length; k++){
                if(k == 0){
                   sorted[k].Flag = "L";
                   lastShift = sorted[k].WeekSeq - weekSeq;
                }else{
                    sorted[k].Flag = "-";
                } 
                result.push({"method":"lastweek", "week":sorted[k].Week, "shift":lastShift});       
            }
        });
        const lastResult = Object.values(result).flat();
        
        return lastResult;
    }

    var fn_weekDiffMaster = function(array, planWeekInfo, commparSeq){

        let WeekDiffMaster = [];
        for(var j = (array.length -1); j >= 0 ; j--){
            let diff = parseInt(array[j].WeekSeq) - parseInt(planWeekInfo.WeekSeq) ;

            if(diff == 0){
                WeekDiffMaster.push({"Planweek":array[j].Week, "WeekDiff":"W-00", "isVisible":"Y", "desc":"current"});
            }else if( diff >= commparSeq && diff < 0){
                let sWeekDiff = "W-" + String(parseInt(diff) * -1).padStart(2, "0") ;
                WeekDiffMaster.push({"Planweek":array[j].Week, "WeekDiff":sWeekDiff, "isVisible":"Y", "desc":""});
            }else{
                if(diff < 0){
                    WeekDiffMaster.push({"Planweek":array[j].Week, "WeekDiff":"", "isVisible":"N", "desc":""});
                }     
            };
        };

        WeekDiffMaster = fn_sorting(WeekDiffMaster, "Planweek", "asc");

        return WeekDiffMaster;
    };
    
    // Mapping 함수 정의, 마지막에 선언을 해야 함수를 정상적으로 인식함
    const functionMap = {
       "fn_getPlanWeekForGetData" : fn_getPlanWeekForGetData
    };

    return {
        fn_loadFunction : fn_loadFunction
    };

});