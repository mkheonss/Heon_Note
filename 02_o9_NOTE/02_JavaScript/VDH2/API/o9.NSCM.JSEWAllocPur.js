define('o9.NSCM.JSEWAllocPur', ['o9/data/query', 'o9/data/cellset', 'o9.NSCM.commonLib'], function(){	
    
	const programName = "o9.NSCM.JSEWAllocPur";
    const commonLib = require('o9.NSCM.commonLib');
    const vdUtil = new commonLib.VdUtil();
    
    /*--------------------------------------------------------------------------------------------------*/
    // 프로그램명 : o9.NSCM.JSEWAllocPur
    // Action Button : EWAllocPur
    // 화면명 : Alloc(pur)
    // 2025.08.01 최초 생성
    // 2025.08.07 BOD 체크 메져그룹 BOD Item Mtrl로 변경함.
    // 2025.08.11 Save & supply Copy인 경우 조회된 Summary Grid 대상으로 처리함.
    // 2025.08.19 Save & supply Copy인 경우 Detail 변경된 데이타 기준으로 Alloc Pur Sum 에 처리함.
    // 2025.08.25 fn_validation에서 BOD Item Mtrl W 메져로 변경함.
    // 2025.08.28 fn_save시 신규에 대해서 ETD Plan 예외처리 : 첫주만 입력되도록 처리함.
    // 2025.09.09 ETA Plant(+) / On-Hand(+) / To-Plant(-) 첫주 데이타 0 세팅 여부 체크
    // 2025.09.19 소스 정리
    // 2025.12.31 fn_loadFunction() 수정함. => parsedParams 값 체크 로직 추가
    // 2026.02.12 fn_cb_siteMF() 공통에서 true로 설정되어서 AllocPur 파일에 다시 생성함.isDisplayNameWithCode(false로 설정)
    // 2026.03.09 fn_merge() 관련 API 추가
    // 2026.03.10 fn_filterHorizon() 관련 API 추가
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
// Grid 에서 선택한 Item Material, Location 정보를 BOD Item 조회함.
// { "fbFuncName" : "fn_cb_vendor" }
/* 호출 예제
{"fbFuncName" : "fn_cb_vendor", 
"fbParams" : {
"version":"CWV_MP",
"[Item Material].[Item Material]":"BN96-54530A",
"[Location].[Location]":"P406",
"[Sub Location].[Sub Location]" : "P105SP"}
}*/
    var fn_cb_vendor  = function(parsedParams){
        const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
        vdCommon.setLogLevel("Debug");
        try {

            let fbVersion = parsedParams.fbParams["version"];
            if(fbVersion == undefined ){
                fbVersion = "CWV_MP";
            }
            let fbItem = parsedParams.fbParams["[Item Material].[Item Material]"];
            let fbToSite = parsedParams.fbParams["[Location].[Location]"]

            var dims = [];
            dims.push('[Location].[Location].filter(~(#.Name in {"All", "-"}))');

            var measure = [];
            measure.push("Measure.[BOD Item Mtrl_Lock Flag]");
            measure.push("Measure.[BOD Item Mtrl_Lot Size]");
            measure.push("Measure.[BOD Item Mtrl_Lot Type]");   

            let whereQuery = "Where {";
            whereQuery += "[Version].[Version Name].["+fbVersion+"]";
            whereQuery += ",[Sub Location].[Sub Location]" + vdUtil.fn_filterStr(fbToSite);
            whereQuery += ",[Item Material].[Item Material]" + vdUtil.fn_filterStr(fbItem);
            whereQuery += ",[Trans Mode].[Trans Mode]";
            whereQuery += "}";

            var result = vdCommon.selectList(dims, measure, whereQuery, "", parsedParams.fbParams.limit);
            //vdCommon.printCsData(result, 3);
            var comboList = vdCommon.fn_makeCombo(result, {DimName : "Location", DimAttbName : "Location", Sort : "DisplayName",
                                                //includeField :"Sub Location:Sub Location:Sub Location,Item Material:Item Material:Item Material,Location:Location:Location",
                                                existAll : parsedParams.fbParams.existAll});
            vdCommon.programEnd();

            return { "Code" : 0, "Msg" : "", "Rows" : comboList };
        } catch ( e ) {
            return { "Code" : -1, "Msg" : e.message };
        }    
    };     
  
    /* ********************************************************************************** */
    // { "fbFuncName" : "fb_cb_tpMtrl" }
    // Grid 에서 선택한 Item Material, Location 정보로 BOD Item 조회함.
    /* 호출 예제
    {"fbFuncName":"fb_cb_tpMtrl", 
     "fbParams":{"version":"CWV_MP","[Item Material].[Item Material]":"BN96-54530A", "[Location].[Location]":"P406" ,"[Sub Location].[Sub Location]" : "P105SP" } 
    }*/
    var fn_cb_tpMtrl = function(parsedParams){
        const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
        vdCommon.setLogLevel("Debug");
		try {

            let fbVersion = parsedParams.fbParams["version"];
            if(fbVersion == undefined ){
                fbVersion = "CWV_MP";
            }            
            let fbItem = parsedParams.fbParams["[Item Material].[Item Material]"];
            let fbToSite = parsedParams.fbParams["[Location].[Location]"]
            let fbFromLocation = parsedParams.fbParams["[Sub Location].[Sub Location]"];

            var dims = [];
            dims.push('[Trans Mode].[Trans Mode].filter(~(#.Name in {"All", "-"}))');

            var measure = [];
            measure.push("Measure.[BOD Item Mtrl_Lock Flag]");
            measure.push("Measure.[BOD Item Mtrl_Lot Size]");
            measure.push("Measure.[BOD Item Mtrl_Lot Type]");            

            let whereQuery = "Where {";
            whereQuery += "[Version].[Version Name].["+fbVersion+"]";
            whereQuery += ",[Sub Location].[Sub Location]" + vdUtil.fn_filterStr(fbToSite);
            whereQuery += ",[Item Material].[Item Material]" + vdUtil.fn_filterStr(fbItem);
            whereQuery += ",[Location].[Location]" + vdUtil.fn_filterStr(fbFromLocation);
            whereQuery += "}";

            var result = vdCommon.selectList(dims, measure, whereQuery, "", parsedParams.fbParams.limit);
            //vdCommon.printCsData(result, 3);
            var comboList = vdCommon.fn_makeCombo(result, {DimName : "Trans Mode", DimAttbName : "Trans Mode", Sort : "DisplayName",
                                                //includeField:"Sub Location:Sub Location:Sub Location,Item Material:Item Material:Item Material,Location:Location:Location",
                                                existAll : parsedParams.fbParams.existAll});
            vdCommon.programEnd();

            return { "Code" : 0, "Msg" : "", "Rows" : comboList };
        } catch ( e ) {
            return { "Code" : -1, "Msg" : e.message };
        }    
    };  

    /* ********************************************************************************** */
    var fn_validation = function(parsedParams){
        const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
        vdCommon.setLogLevel("Debug"); 
        try{
            let errorCnt = 0;
            let errorMsg = "";
            let fbVersion = parsedParams.fbParams.version;

            for ( var i = 0; i < parsedParams.fbGridRows.length; i++ ) {
                let rowStatus = parsedParams.fbGridRows[i]["rowstatus"];
                let fbToSite = parsedParams.fbGridRows[i]["[Location].[Location]"];
                let fbItemMaterial = parsedParams.fbGridRows[i]["[Item Material].[Item Material]"]; 
                let fbFromLocation = parsedParams.fbGridRows[i]["[Sub Location].[Sub Location]"];
                let fbTransMode = parsedParams.fbGridRows[i]["[Trans Mode].[Trans Mode]"];

                parsedParams.fbGridRows[i]["rowmsg"] = "";
                parsedParams.fbGridRows[i]["errorflag"] = "";

                if(rowStatus == "C"){
                     //validation 체크함.                 
                    //BOD Item 등록여부
                    let bodItemDim =[];
                    let bodItemMeasure = [];

                    /*
                     BOD Item Mtrl W 메져그룹에서 조회하여 BOD 등록 여부 체크함.
                    */
                   
                    bodItemDim.push("[Version].[Version Name].["+fbVersion+"]");
                    bodItemDim.push("[Location].[Location].["+fbFromLocation+"]");
                    bodItemDim.push("&Next52Weeks");
                    bodItemDim.push("[Item Material].[Item Material].["+fbItemMaterial+"]");
                    bodItemDim.push("[Sub Location].[Sub Location].["+fbToSite+"]");                                        
                    bodItemDim.push("[Trans Mode].[Trans Mode].["+fbTransMode+"]");

                    bodItemMeasure.push("Measure.[BOD Item Mtrl W_Factory Out]");
                    bodItemMeasure.push("Measure.[BOD Item Mtrl W_GR LT]");
                    bodItemMeasure.push("Measure.[BOD Item Mtrl W_Intransit LT]");
                    bodItemMeasure.push("Measure.[BOD Item Mtrl W_Port To Port]");
                    bodItemMeasure.push("Measure.[BOD Item Mtrl W_Supplier]");
                    bodItemMeasure.push("Measure.[BOD Item Mtrl W_Total LT]");

                    let selectCount = vdCommon.selectListCount(bodItemDim,bodItemMeasure, "");

                    if(selectCount == 0){
                        errorMsg = "BOD Item is not registered.";
                        errorCnt++;
                        parsedParams.fbGridRows[i]["rowmsg"] = parsedParams.fbGridRows[i]["rowmsg"] + errorMsg;
                        parsedParams.fbGridRows[i]["errorflag"] = "ERROR";
                    }
                }                
            }

            if(errorCnt > 0 ){
                //Error Row만 Return 함.
                let checkGridRows = parsedParams.fbGridRows;
                const errorRows = checkGridRows.filter((checkGridRows)=>{return checkGridRows.errorflag === "ERROR"});
                parsedParams.fbGridRows = errorRows;
                return { "Code" : -1, "Msg" : "validation Error", "Rows" : parsedParams.fbGridRows };
            }

            return { "Code" : 0, "Msg" : "" };
        }catch(e){
            return { "Code" : -1, "Msg" : e.message };
        }  
    }; 

/* ********************************************************************************** */
/*
{"fbFuncName" : "fn_save",
 "fbParams": {"version":"CWV_MP", "starthorizon":"2025-02-19", "endhorizon":"2026-02-16", "saveflag":"N"},
"fbGridRows" : [
{"rowstatus":"C", "rowindex":0,	
"[Version].[Version Name]" : "CWV_MP",
"[Item Material].[Item Material]" : "BN96-54530B",
"[Location].[Location]" : "P401LCD",
"[Sub Location].[Sub Location]" : "P406LCD",
"[Trans Mode].[Trans Mode]" : "TRKEX",
"measurename" : "Alloc Pur_ETD Plan",
"Week.202508" : "100","Week.202509" : "102","Week.202510" : "0","Week.202511" : "0","Week.202512" : "0",
"Week.202513" : "0","Week.202514" : "0","Week.202515" : "0","Week.202516" : "0","Week.202517" : "0",
"Week.202518" : "0","Week.202519" : "0","Week.202520" : "0","Week.202521" : "0","Week.202522" : "0",
"Week.202523" : "0","Week.202524" : "0","Week.202525" : "0","Week.202526" : "0","Week.202527" : "0",
"Week.202528" : "0","Week.202529" : "0","Week.202530" : "0","Week.202531" : "0","Week.202532" : "0",
"Week.202533" : "0","Week.202534" : "0","Week.202535" : "101","Week.202536" : "0","Week.202537" : "0",
"Week.202538" : "0","Week.202539" : "0","Week.202540" : "0","Week.202541" : "0","Week.202542" : "0",
"Week.202543" : "0","Week.202544" : "0","Week.202545" : "0","Week.202546" : "0","Week.202547" : "0",
"Week.202548" : "0","Week.202549" : "0","Week.202550" : "0","Week.202551" : "0","Week.202552" : "0",
"Week.202601" : "0","Week.202602" : "0","Week.202603" : "0","Week.202604" : "0","Week.202605" : "0",
"Week.202606" : "0","Week.202607" : "0","Week.202608" : "0" }]
}
*/
/* fn_save 처리
    (0) fn_validation() 체크
    (1) Alloc Pur 메져그룹 Measure.[Alloc Pur_ETD Plan] 저장
    (2) saveflag가 "Y"인 경우
        Alloc Pur Sum 메져그룹 Measure.[Alloc Pur Sum_Tot Supply] 처리
    (3) 파이썬 호출 : PY_UI_AllocPurSavePostProcess
        (3-1) Alloc Pur 메져그룹 Measure.[Alloc Pur_ETD Plan LT] 처리
        (3-2) Alloc Pur Sum 메져그룹 Measure.[Alloc Pur_ETD Plan] 처리
*/
    const MEASURE_ETDPLAN = "Alloc Pur_ETD Plan";
    const MEASURE_ETDPLAN_LT = "Alloc Pur_ETD Plan LT";
    const MEASURE_TOPLANT = "Alloc Pur_ToPlant";
    var fn_save = function(parsedParams){
        const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
        vdCommon.setLogLevel("Debug"); 
        try{ 
            //Validation 체크
            let errorData = fn_validation(parsedParams);
            if(errorData.Code == -1){
                return errorData
            }

            let fbVersion = parsedParams.fbParams.version;
            let fbSaveFlag = parsedParams.fbParams.saveflag;
            let starthorizon = parsedParams.fbParams.starthorizon;
            let endhorizon = parsedParams.fbParams.endhorizon;

            let bucketQuery = 'Select ( [Time].[Week].filter((#.Key >= &CurrentWeek.element(0).LeadOffset(0).Key) && (#.Name >= "'+starthorizon+'" && #.Name <= "'+endhorizon+'"))) on row, () on column;';
            let bucketResult = vdCommon.selectQueryList("[bucketQuery]" ,bucketQuery );
            let bucketList = vdCommon.fn_makeCombo(bucketResult, {DimName : "Time", DimAttbName : "Week", Sort : "DisplayName"});

            let creatQuery = "";
            let createDimension = [];
            let createMeasure = [];
            let updateDimension = [];
            let updateMeasure = [];
            

            for ( var i = 0; i < parsedParams.fbGridRows.length; i++ ) {
                let rowStatus = parsedParams.fbGridRows[i]["rowstatus"];
                let fbLocation = parsedParams.fbGridRows[i]["[Location].[Location]"];
                let fbItemMaterial = parsedParams.fbGridRows[i]["[Item Material].[Item Material]"];
                let fbSubLocation =  parsedParams.fbGridRows[i]["[Sub Location].[Sub Location]"];
                let fbTransMode =  parsedParams.fbGridRows[i]["[Trans Mode].[Trans Mode]"];
                //let fbVersion = parsedParams.fbGridRows[i]["[Version].[Version Name]"];
                //Mearsure Name
                let measurename = parsedParams.fbGridRows[i]["measurename"];
                
                if(rowStatus == "C"){
                    if(measurename == MEASURE_ETDPLAN){
                        //Create
                        for(var k = 0; k < bucketList.length; k++){
                            createDimension = [];
                            createMeasure = [];    
                            createDimension.push("[Version].[Version Name].["+fbVersion+"]");
                            createDimension.push("[Location].[Location].["+fbLocation+"]");
                            createDimension.push("[Item Material].[Item Material].["+fbItemMaterial+"]");                    
                            createDimension.push("[Sub Location].[Sub Location].["+fbSubLocation+"]");
                            createDimension.push("[Trans Mode].[Trans Mode].["+fbTransMode+"]");   
                            createDimension.push("[Time].[Week].["+bucketList[k]["Name"]+"]");
                            createMeasure.push("Measure.[" +measurename + "] = 0;" );
                            vdCommon.createMeasure(createDimension, createMeasure);
                        }
                        //+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
                        //ETA Plant(+) / On-Hand(+) 데이타 존재 여부 체크
                        //+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
                        let selectDimension = [];    
                        selectDimension.push("[Version].[Version Name].["+fbVersion+"]");
                        selectDimension.push("[Location].[Location].["+fbLocation+"]");
                        selectDimension.push("[Item Material].[Item Material].["+fbItemMaterial+"]");                    
                        selectDimension.push("[Sub Location].[Sub Location].[+]");
                        selectDimension.push("[Trans Mode].[Trans Mode].[-]");
                        selectDimension.push("&Next52Weeks");

                        createDimension = [];
                        createMeasure = [];
                        createDimension.push("[Version].[Version Name].["+fbVersion+"]");
                        createDimension.push("[Location].[Location].["+fbLocation+"]");
                        createDimension.push("[Item Material].[Item Material].["+fbItemMaterial+"]");                    
                        createDimension.push("[Sub Location].[Sub Location].[+]");
                        createDimension.push("[Trans Mode].[Trans Mode].[-]");
                        createDimension.push("[Time].[Week].["+bucketList[0]["Name"]+"]");
                        //+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
                        createMeasure.push("Measure.[Alloc Pur_ETA Plan] = 0;" );

                        if(!vdCommon.existMeasure(selectDimension, ["Measure.[Alloc Pur_ETA Plan]"], "")){
                            //첫주 데이타를 0으로 생성함.
                            vdCommon.createMeasure(createDimension, createMeasure);
                        }
                        //+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
                        //On-Hand(+) 데이타 존재 여부 체크
                        createMeasure = [];
                        createMeasure.push("Measure.[Alloc Pur_ONHAND] = 0;");

                        if(!vdCommon.existMeasure(selectDimension, ["Measure.[Alloc Pur_ONHAND]"], "")){
                            //첫주 데이타를 0으로 생성함.
                            vdCommon.createMeasure(createDimension, createMeasure);
                        }

                        //+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
                        //ToPlant(+) 데이타 존재 여부 체크
                        // fbSubLocation 값이 "P" 로 시작하고 "SP"로 끝나는 SubLocation에 대해서 ToPlant 값을 체크한다.
                        if(fbSubLocation.substring(0,1) == "P" && fbSubLocation.substring(fbSubLocation.length - 2, fbSubLocation.length) == "SP"){
                            let toPlantLocation = fbSubLocation.substring(0,fbSubLocation.length - 2);
                            selectDimension = [];    
                            selectDimension.push("[Version].[Version Name].["+fbVersion+"]");
                            selectDimension.push("[Location].[Location].["+toPlantLocation+"]");
                            selectDimension.push("[Item Material].[Item Material].["+fbItemMaterial+"]");                    
                            selectDimension.push("[Sub Location].[Sub Location].[-]");
                            selectDimension.push("[Trans Mode].[Trans Mode].[-]");
                            selectDimension.push("&Next52Weeks");

                            createDimension = [];
                            createMeasure = [];
                            createDimension.push("[Version].[Version Name].["+fbVersion+"]");
                            createDimension.push("[Location].[Location].["+toPlantLocation+"]");
                            createDimension.push("[Item Material].[Item Material].["+fbItemMaterial+"]");                    
                            createDimension.push("[Sub Location].[Sub Location].[-]");
                            createDimension.push("[Trans Mode].[Trans Mode].[-]");
                            createDimension.push("[Time].[Week].["+bucketList[0]["Name"]+"]");
                            //+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
                            createMeasure.push("Measure.[Alloc Pur_ToPlant] = 0;" );

                            if(!vdCommon.existMeasure(selectDimension, ["Measure.[Alloc Pur_ToPlant]"], "")){
                                //첫주 데이타를 0으로 생성함.
                                vdCommon.createMeasure(createDimension, createMeasure);
                            }
                        }
                        //+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
                        //Summary Data 확인이 필요함.
                        let sDimension = [];
                        let sMeasure = [];
                        sDimension.push("[Version].[Version Name].["+fbVersion+"]");
                        sDimension.push("[Time].[Week].["+bucketList[0]["Name"]+"]");
                        sDimension.push("[Item Material].[Item Material].["+fbItemMaterial+"]");
                        sDimension.push("[Sub Location].[Sub Location].["+fbSubLocation+"]");

                        sMeasure.push("Measure.[Alloc Pur Sum_ETD Plan]");
                        sMeasure.push("Measure.[Alloc Pur Sum_ETD Plan Flag]");
                        sMeasure.push("Measure.[Alloc Pur Sum_Tot Supply]");

                        let iMeasure =[];
                        iMeasure.push("Measure.[Alloc Pur Sum_Tot Supply] = if(isnull(Measure.[Alloc Pur Sum_Tot Supply]))then 0 else Measure.[Alloc Pur Sum_Tot Supply] ;");
                        iMeasure.push("Measure.[Alloc Pur Sum_ETD Plan] = if(isnull(Measure.[Alloc Pur Sum_ETD Plan]))then 0 else Measure.[Alloc Pur Sum_ETD Plan] ;");

                        if(vdCommon.existMeasure(sDimension, sMeasure, "")){
                        //update
                            vdCommon.updateMeasure(sDimension, iMeasure);                        
                        }else{
                            vdCommon.createMeasure(sDimension, 
                                                    ["Measure.[Alloc Pur Sum_Tot Supply] = 0 ;"
                                                    ,"Measure.[Alloc Pur Sum_ETD Plan] = 0;"]); 
                        }
                     }else{
                        if(!(measurename == "Alloc Pur_REQ Total" || measurename == "Alloc Pur_EOHWEEK" || 
                             measurename == "Alloc Pur_BSHub REQ Total" || measurename == "Alloc Pur_BSHub EOHWEEK")){
                            for(var k = 0; k < bucketList.length; k++){
                                let sWeek = bucketList[k]["Name"];
                                let bucketValue = parsedParams.fbGridRows[i]["Week." + sWeek]; 
                                //vdCommon.debug("[Create]["+measurename+"]["+sWeek+"]["+bucketValue+"]");
                                if(bucketValue === undefined || bucketValue === ""){
                                    bucketValue = null;
                                }
    
                                //if(!(bucketValue == undefined || bucketValue == "" || bucketValue == null)){
                                    createDimension = [];
                                    createMeasure = [];    
                                    createDimension.push("[Version].[Version Name].["+fbVersion+"]");
                                    createDimension.push("[Location].[Location].["+fbLocation+"]");
                                    createDimension.push("[Item Material].[Item Material].["+fbItemMaterial+"]");                    
                                    createDimension.push("[Sub Location].[Sub Location].["+fbSubLocation+"]");
                                    createDimension.push("[Trans Mode].[Trans Mode].["+fbTransMode+"]");   
                                    createDimension.push("[Time].[Week].["+sWeek+"]");
                                    createMeasure.push("Measure.[" +measurename + "] = " + bucketValue + ";" );
                                    
                                    if(vdCommon.existMeasure(createDimension, ["Measure.[" +measurename + "]"])){
                                        vdCommon.updateMeasure(createDimension, createMeasure); 
                                    }else{
                                        vdCommon.createMeasure(createMeasure, createMeasure); 
                                    }
                               // }
                            }
                        }
                     }
                }else{
                    //update
                    if(!(measurename == "Alloc Pur_REQ Total" || measurename == "Alloc Pur_EOHWEEK" || 
                    measurename == "Alloc Pur_BSHub REQ Total" || measurename == "Alloc Pur_BSHub EOHWEEK")){
                        for(var k = 0; k < bucketList.length; k++){
                            let sWeek = bucketList[k]["Name"];
                            let bucketValue = parsedParams.fbGridRows[i]["Week."+ sWeek]; 
                            //vdCommon.debug("[update]["+measurename+"]["+sWeek+"]["+bucketValue+"]");
                            if(bucketValue === undefined || bucketValue === ""){
                                bucketValue = null;
                                //vdCommon.debug("[update-nullCheck]["+measurename+"]["+sWeek+"]["+bucketValue+"]");
                            }
                            //if(!(bucketValue == undefined || bucketValue == "" || bucketValue == null)){
                                updateDimension = [];
                                updateMeasure = [];
            
                                updateDimension.push("[Version].[Version Name].["+fbVersion+"]");
                                updateDimension.push("[Location].[Location].["+fbLocation+"]");
                                updateDimension.push("[Item Material].[Item Material].["+fbItemMaterial+"]");                    
                                updateDimension.push("[Sub Location].[Sub Location].["+fbSubLocation+"]");
                                updateDimension.push("[Trans Mode].[Trans Mode].["+fbTransMode+"]");
                                updateDimension.push("[Time].[Week].["+sWeek+"]");
    
                                updateMeasure.push("Measure.[" +measurename + "] = " + bucketValue + ";" );
    
                                if(vdCommon.existMeasure(updateDimension, ["Measure.[" +measurename + "]"])){
                                    vdCommon.updateMeasure(updateDimension, updateMeasure); 
                                }else{
                                    vdCommon.createMeasure(updateDimension, updateMeasure); 
                                }
                            //}
                        } 
                    }
                }

                //++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
                //ETD Plan 데이타 존재 여부 체크 후에 L/T 체크
                //++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
                if(measurename === MEASURE_ETDPLAN){
                    let selectEtdPlan = 'Select ([Time].[Week].filter(#.Name >= "'+starthorizon+'" && #.Name <= "'+endhorizon+'")) on row, ';
                    selectEtdPlan += '({Measure.[Alloc Pur_ETD Plan]}) on column ';
                    selectEtdPlan += 'Where{[Version].[Version Name].['+fbVersion+']';
                    selectEtdPlan += ',[Location].[Location].['+fbLocation+']';
                    selectEtdPlan += ',[Item Material].[Item Material].['+fbItemMaterial+']';
                    selectEtdPlan += ',[Sub Location].[Sub Location].['+fbSubLocation+']';
                    selectEtdPlan += ',[Trans Mode].[Trans Mode].['+fbTransMode+']';
                    selectEtdPlan += '};';
    
                    let result = vdCommon.selectQueryList("[ETD Plan Data]", selectEtdPlan);
                    if(result.rowCount <= 0){
                        //ETD Plan 값이 없는 경우 해당 범위의 L/T 삭제(null값 처리)
                        vdCommon.updateMeasure(['[Version].[Version Name].['+fbVersion+']'
                                            ,'[Location].[Location].['+fbLocation+']'
                                            ,'[Time].[Week].filter(#.Name >="'+starthorizon+'" && #.Name <="'+endhorizon+'")'
                                            ,'[Item Material].[Item Material].['+fbItemMaterial+']'
                                            ,'[Sub Location].[Sub Location].['+fbSubLocation+']'
                                            ,'[Trans Mode].[Trans Mode].['+fbTransMode+']'],
                                            ['Measure.[Alloc Pur_ETD Plan LT] = null;']);    
                    }
                }
                //++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

                if(fbSaveFlag == "Y"){
                    if(measurename == MEASURE_ETDPLAN){
                        /*Grid 조회된 데이타만 적용하기 위해서 fbGridEtc에서 조회된 데이타를 넘겨 받아서 처리함.*/
                        let selectAllocPur = 'Select ([Time].[Week].filter(#.Key >= &CurrentWeek.element(0).LeadOffset(0).Key) * ';
                        selectAllocPur += '[Item Material].[Item Material].['+fbItemMaterial+'] * [Sub Location].[Sub Location].['+fbSubLocation+']) on row, ';
                        selectAllocPur += '({ Measure.[Alloc Pur_ETD Plan] }) on column ';
                        selectAllocPur += 'Where {[Version].[Version Name].['+fbVersion+'], [Location].[Location], [Trans Mode].[Trans Mode]};';
                        
                        let resultAllocPur = vdCommon.selectQueryList("Alloc Pur(Summary)", selectAllocPur);
                        
                        //vdCommon.debug("saveflag :: ["+fbSaveFlag+"]["+fbItemMaterial+"]["+fbSubLocation+"]["+resultAllocPur.cs.rowCount+"]");
                        //vdCommon.debug("saveflag data ["+JSON.stringify(resultAllocPur.cs)+"]");
                        for(var n = 0; n < resultAllocPur.rowCount; n++){
                            //Alloc Pur Sum 메져그룹 Update
                            let sDimension = [];
                            let sMeasure = [];
                            let iMeasure = [];
                            let sumQty = resultAllocPur.cs.row(n).cell(resultAllocPur.cs.measureColumnIndex("Alloc Pur_ETD Plan"));
                            let sTimeWeek = resultAllocPur.cs.row(n).cell(resultAllocPur.cs.memberColumnIndex("Time","Week")).Name;
                            
                            if(sumQty > 0){
                                sDimension.push("[Version].[Version Name].["+fbVersion+"]");
                                sDimension.push("[Time].[Week].["+sTimeWeek+"]");
                                sDimension.push("[Item Material].[Item Material].["+resultAllocPur.cs.row(n).cell(resultAllocPur.cs.memberColumnIndex("Item Material","Item Material")).Name+"]");
                                sDimension.push("[Sub Location].[Sub Location].["+resultAllocPur.cs.row(n).cell(resultAllocPur.cs.memberColumnIndex("Sub Location","Sub Location")).Name+"]");

                                sMeasure.push("Measure.[Alloc Pur Sum_ETD Plan]");
                                sMeasure.push("Measure.[Alloc Pur Sum_ETD Plan Flag]");
                                sMeasure.push("Measure.[Alloc Pur Sum_Tot Supply]");

                                iMeasure.push("Measure.[Alloc Pur Sum_Tot Supply] = "+ sumQty + ";");

                                if(vdCommon.existMeasure(sDimension, sMeasure, "")){
                                    //Update
                                    vdCommon.updateMeasure(sDimension, iMeasure);
                                }else{
                                    //Create
                                    vdCommon.createMeasure(sDimension, iMeasure);
                                }
                            }                      
                        }
                    }
                }
            }
            /*파이쎤 호출
             (1) ETD L/T 처리 
             (2) [Alloc Pur Sum_ETD] 메져 그룹 Measure.[Alloc Pur Sum_ETD Plan] 값처리를 위해 파이쎤 호출함.
             */
            let executePython = 'EXEC plugin instance [PY_UI_AllocPurSavePostProcess] for Measures{[Alloc Pur_ETD Plan], [Alloc Pur Sum_ETD Plan]} ';
            executePython += 'using scope ([Version].[Version Name].['+fbVersion+']) ' ;
            executePython += 'using arguments {(ExecutionMode, "MediumWeight"), ("IncludeNullRows", "False"),';
            executePython += '(paramOutVersion, "CWV_MP"), (MaxSliceTableCells, 200000000), (MaxConcurrency, 1)};';

            vdCommon.executePython("Alloc(pur)(ew)", executePython);

            return { "Code" : 0, "Msg" : "", "Rows" : "" };
        }catch ( e ) {
            return { "Code" : -1, "Msg" : e.message };
        }
    } 
    
    // {"fbFuncName" : "fn_navigationInfo" }
    /* {"fbFuncName" : "fn_navigationInfo",
        "fbParams":{"[Plan ID]":"CWV_MP", 
                    "[To Site]":"P551", 
                    "[Item]":"BN96-54530B",
                    "[Week]":["202508","202509"]
                }
        }
    */
        var fn_navigationInfo= function(parsedParams){
            const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
            vdCommon.setLogLevel("Debug"); 
            try{
                let fbPlanID = parsedParams.fbParams["[Plan ID]"];
                let fbToSite = parsedParams.fbParams["[To Site]"];
                let fbItem = parsedParams.fbParams["[Item]"];
                let fbWeek = parsedParams.fbParams["[Week]"];
    
                let selectQuery = 'Select (';
                selectQuery += '[Version].[Version Name].['+fbPlanID+']';
                selectQuery += ' * [Location].[Location]'+vdUtil.fn_filterStr(fbToSite);
                selectQuery += ' * [Item Material].[Item Material]'+vdUtil.fn_filterStr(fbItem);
                selectQuery += ' * [Sub Location].[Sub Location]';
                selectQuery += ' * [Sequence].[Sequence]';
                selectQuery += ' ) on row, ';
                selectQuery += ' ({Measure.[Intransit Mtrl_Avail Week]}) on column ';
                selectQuery += 'Where { ';
                selectQuery += ' Measure.[Intransit Mtrl_Avail Week]' + 'in {'+fbWeek.map(item => `"${item}"`).join(",")+'}';
                selectQuery += '} ;';
                
                let result = vdCommon.selectQueryList("[fn_nevigatorInfo]", selectQuery);
                let comboSeq = vdCommon.fn_makeCombo(result, {DimName : "Sequence", DimAttbName : "Sequence", existAll : false, Sort : "Name", isDisplayNameWithCode : false});
                
                let arraySeq = comboSeq.map((value) => value.Name);
                //vdCommon.debug("arraySEQ : " + JSON.stringify(arraySeq);
                                                        
                return { "Code" : 0, "Msg" : "", "Rows" : arraySeq };
    
            }catch ( e ) {
                return { "Code" : -1, "Msg" : e.message };
            }
        };    
    // { "fbFuncName" : "fn_cb_siteMF" ,"fbParams":{"isDisplayNameWithCode":false}}
	var fn_cb_siteMF = function(parsedParams){
        const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
        vdCommon.setLogLevel("Debug");
		try {
            
            parsedParams.fbParams["isDisplayNameWithCode"] = false; //공통 디폴트 설정 변경함.

            vdCommon.printParams(parsedParams);

		    var dims = ['&MFStageSETLocation'];

            // filter를 적용할 Dimension 설정
            if ( parsedParams.fbParams["filterDimension"] == undefined ) {
                parsedParams.fbParams["filterDimension"] = ["[Location]"];
            }

		    // Casecade 를 위해서 Dimension 추가
		    dims = vdUtil.fn_addIncludeField(dims, parsedParams);

            var result = vdCommon.selectList(dims, [], vdUtil.fn_makeWhere(parsedParams), "", parsedParams.fbParams.limit);
            //vdCommon.printCsData(result, 3);
            var comboList = vdCommon.fn_makeCombo(result, {DimName : "Location", DimAttbName : "Location", Sort : "DisplayName", 
                                                    isDisplayNameWithCode : parsedParams.fbParams.isDisplayNameWithCode});
            vdCommon.debug("ComboData : " + JSON.stringify(comboList.slice(0,3)));

            vdCommon.programEnd();

            return { "Code" : 0, "Msg" : "", "Rows" : comboList };
        } catch ( e ) {
            vdCommon.error(e.message);
            return { "Code" : -1, "Msg" : e.message };
        }
    };

   /* ********************************************************************************** */
   /* {"fbFuncName":"fn_filterHorizon",
        "fbParams":{
                "filters":{
                "[Version].[Version Name]":{"SelectedMembers":["CWV_MP"],"SelectedMembersAlias":["202547"],"MemberFilter":"&CWVUI","DimensionAliasName":"Plan ID"},
                "[Filter].[Filter]":{"SelectedMembers":[],"SelectedMembersAlias":[],"MemberFilter":"","SelectedMembersExp":"filter((#.[FilterAllocPurHorizon] in {\"-13W\"} && #.[FilterMtrlItem] contains \"BN96-51\"))"},
                "[Time].[Week]":{"SelectedMembers":["202608","202609","202610","202611","202612","202613","202614","202615","202616","202617","202618","202619","202620","202621","202622","202623","202624","202625","202626","202627","202628"],
                                "SelectedMembersAlias":[null,null,null,null,null,null,null,null,null,null,null,null,null,null,null,null,null,null,null,null,null],"MemberFilter":"&NSUIWeekFilterView","DimensionAliasName":"Horizon"}
                }
                ,"reportName":"[NSCM] EW VD Alloc Pur Constraint","menuName":"Alloc Pur Constraint"
            }
    }
   */
  /* 조건별 "[Filter].[Filter]" 처리
        (1) Horizon + Calculate PSI OH  (정상)
            filter((#.[FilterAllocPurHorizon] in {\"-5W\"} && #.[FilterCalPSIOH] in {\"Y\"}))
        (2) Horizon + Material : 
            filter((#.[FilterAllocPurHorizon] in {\"-5W\"} ) && ( #.[FilterMtrlItem] contains \"BN96\"))
        (3) Calculate PSI OH + Material : 
            filter((#.[FilterCalPSIOH] in {\"Y\"} ) && ( #.[FilterMtrlItem] contains \"BN96\"))
        (4) Horizon + Calculate PSI OH + Material :
            filter((#.[FilterAllocPurHorizon] in {\"-5W\"} && #.[FilterCalPSIOH] in {\"Y\"} ) && ( #.[FilterMtrlItem] contains \"BN96\"))
  */
   
   var fn_filterHorizon = function(parsedParams){
    const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
    vdCommon.setLogLevel("Debug");
    try{
        let timeWeeks = vdUtil.fn_getFilterValue(parsedParams, "[Time].[Week]");
        //vdCommon.debug("[Time Weeks]"+ timeWeeks.length );

        let return1 = [];
        let return2 = "";
        let filterInfo = vdUtil.fn_getFilter(parsedParams, "[Filter].[Filter]");
        let filterValue = filterInfo["SelectedMembersExp"];
        
        if(filterValue == undefined || filterValue == ""){
            return { "Code" : 0, "Msg" : "", "Week": return1, "IBPL": return2 };
        }
        filterValue = filterValue.replace("filter","").replace("(","").replace(")","");
        filterValue = filterValue.split("&&");  
        //vdCommon.debug("["+filterValue.length+"]"+JSON.stringify(filterValue));
        for(var k=0; k < filterValue.length; k++){
            let value = filterValue[k];
            value = replaceAll(value, "(", "");
            value = replaceAll(value, ")", "");
            vdCommon.debug("["+k+"]"+value);
            if(value.indexOf("[FilterAllocPurHorizon]") > 0){
                let CurrentWeek = vdCommon.selectResult('&CurrentWeek.element(0).DisplayName');
                let selectQuery = "";
                
                if(value.indexOf("-13W") > 0){
                    selectQuery = "[Time].[Week].filter(#.Key <= &CurrentWeek.element(0).LeadOffset(0).Key && #.Key >=  &CurrentWeek.element(0).LeadOffset(-13).Key)" ;
                }else if(value.indexOf("-9W") > 0){
                    selectQuery = "[Time].[Week].filter(#.Key <= &CurrentWeek.element(0).LeadOffset(0).Key && #.Key >=  &CurrentWeek.element(0).LeadOffset(-9).Key)" ;
                }else if(value.indexOf("-5W") > 0){
                    selectQuery = "[Time].[Week].filter(#.Key <= &CurrentWeek.element(0).LeadOffset(0).Key && #.Key >=  &CurrentWeek.element(0).LeadOffset(-5).Key)" ;
                }
    
                selectQuery = "Select("+selectQuery+");";
                let result = vdCommon.selectQueryList("", selectQuery);
                let comboList = vdCommon.fn_makeCombo(result, {
                    DimName: "Time", DimAttbName: "Week", Sort: "DisplayName", existAll: false,isDisplayNameWithCode: false});
                
                let timeArray = comboList.map((value) => value.Name);
                let arrayIndex = timeArray.length;
    
                for(var j=0; j < timeWeeks.length; j++ ){
                    if(parseInt(CurrentWeek) < parseInt(timeWeeks[j])){
                        timeArray[arrayIndex++] = timeWeeks[j];
                    }
                }
                return1 = timeArray;
            }

            if(value.indexOf("[FilterMtrlItem]") > 0){
                let mtrlItemValue = value.replace("[FilterMtrlItem]","Name").replace("contains", "containsregexp");
                return2 = "[Item Material].[Item Material].filter(" +mtrlItemValue + ")";
            }

        }           

        return { "Code" : 0, "Msg" : "", "Week": return1, "IBPL": return2 };

    }catch (e) {
        return { "Code": -1, "Msg": e.message };
    }
   };
   
   function replaceAll(str, searchStr, replaceStr) {

    return str.split(searchStr).join(replaceStr);
  }   

    /************************ Start : fn_merge *******************************************/      
    /* 관련 Measure Group 
    1. Alloc Pur
    2. Alloc Pur Req
    3. Alloc Pur Sum
    {"fbFuncName" : "fn_merge",
        "fbParams":{ "commitType":1,
        "filters":{
                "[Version].[Version Name]":{"SelectedMembers":["202608_M_WI_04"],"SelectedMembersAlias":["202608_M_WI_04"],"MemberFilter":"&CWVUI","DimensionAliasName":"Plan ID"},
                "[Filter].[Filter]":{"SelectedMembers":[],"SelectedMembersAlias":[],"MemberFilter":""}
            }
        },
        "fbGridRows" : [
            {"rowstatus":"U", "rowindex":0,	
            "[Location].[Location]" : "P551",
            "[Sub Location].[Sub Location]":"P105SP",
            "[Item Material].[Item Material]":"BN96-54530B",
            "[Trans Mode].[Trans Mode]":"VESSEL"
            },
            {"rowstatus":"U", "rowindex":0,	
            "[Location].[Location]" : "P306",
            "[Sub Location].[Sub Location]":"G3294027",
            "[Item Material].[Item Material]":"BN96-54531A",
            "[Trans Mode].[Trans Mode]":"VESSEL"
            }
        ]
    } 
    */
    var fn_merge = function(parsedParams){
        const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
        vdCommon.setLogLevel("Debug"); 
        try{          
            let fbVersion = vdUtil.fn_getFilterValue(parsedParams,"[Version].[Version Name]");
            let dimensionQuery = [];

            let dimensionInfo = [];
            let measureInfo = [];
            dimensionInfo.push("[Version].[Version Name]");
            dimensionInfo.push("[Location].[Location]");
            dimensionInfo.push("[Time].[Week]");
            dimensionInfo.push("[Sub Location].[Sub Location]");
            dimensionInfo.push("[Item Material].[Item Material]");
            dimensionInfo.push("[Trans Mode].[Trans Mode]");
            
            measureInfo.push("Measure.[Alloc Pur_BSHub EOHWEEK_Deno]");
            measureInfo.push("Measure.[Alloc Pur_BSHub EOHWEEK_Numr]");
            measureInfo.push("Measure.[Alloc Pur_BSHub ETA Plan]");
            measureInfo.push("Measure.[Alloc Pur_BSHub ETA Result]");
            measureInfo.push("Measure.[Alloc Pur_BSHub Exception]");
            measureInfo.push("Measure.[Alloc Pur_BSHub NOH]");
            measureInfo.push("Measure.[Alloc Pur_BSHub ONHAND]");
            measureInfo.push("Measure.[Alloc Pur_BSHub Open PO]");
            measureInfo.push("Measure.[Alloc Pur_BSHub SOP Fix]");
            measureInfo.push("Measure.[Alloc Pur_BSHub SOP unFix]");
            measureInfo.push("Measure.[Alloc Pur_BSHub Safety Time]");
            measureInfo.push("Measure.[Alloc Pur_BSHub Service]");
            measureInfo.push("Measure.[Alloc Pur_BSHub Short]");
            measureInfo.push("Measure.[Alloc Pur_BSHub ToPlant]");
            measureInfo.push("Measure.[Alloc Pur_EOHWEEK_Deno]");
            measureInfo.push("Measure.[Alloc Pur_EOHWEEK_Numr]");
            measureInfo.push("Measure.[Alloc Pur_ETA Plan]");
            measureInfo.push("Measure.[Alloc Pur_ETA Result]");
            measureInfo.push("Measure.[Alloc Pur_ETD Aggr]");
            measureInfo.push("Measure.[Alloc Pur_ETD Plan]");
            measureInfo.push("Measure.[Alloc Pur_ETD Plan Flag]");
            measureInfo.push("Measure.[Alloc Pur_ETD Plan LT]");
            measureInfo.push("Measure.[Alloc Pur_ETD Plan_HUB only]");
            measureInfo.push("Measure.[Alloc Pur_Exception]");
            measureInfo.push("Measure.[Alloc Pur_NOH]");
            measureInfo.push("Measure.[Alloc Pur_NOH Flag]");
            measureInfo.push("Measure.[Alloc Pur_ONHAND]");
            measureInfo.push("Measure.[Alloc Pur_Open PO]");
            measureInfo.push("Measure.[Alloc Pur_REQ Total]");
            measureInfo.push("Measure.[Alloc Pur_SOP Fix]");
            measureInfo.push("Measure.[Alloc Pur_SOP unFix]");
            measureInfo.push("Measure.[Alloc Pur_Safety Time]");
            measureInfo.push("Measure.[Alloc Pur_Service]");
            measureInfo.push("Measure.[Alloc Pur_Short]");
            measureInfo.push("Measure.[Alloc Pur_ToPlant]");

            let dimensionInfo_Req = [];            
            let measureInfo_Req = [];
            dimensionInfo_Req.push("[Version].[Version Name]");
            dimensionInfo_Req.push("[Location].[Location]");
            dimensionInfo_Req.push("[Time].[Week]");
            dimensionInfo_Req.push("[Sub Location].[Sub Location]");
            dimensionInfo_Req.push("[Item Material].[Item Material]");
            dimensionInfo_Req.push("[Category].[Category]");

            measureInfo_Req.push("Measure.[Alloc Pur Req_LCM Item]");
            measureInfo_Req.push("Measure.[Alloc Pur Req_LCM Qty]");
            measureInfo_Req.push("Measure.[Alloc Pur Req_Qty]");
            measureInfo_Req.push("Measure.[Alloc Pur Req_SET DC Qty]");
            measureInfo_Req.push("Measure.[Alloc Pur Req_SET DC Site]");
            measureInfo_Req.push("Measure.[Alloc Pur Req_SET DC Week]");
            measureInfo_Req.push("Measure.[Alloc Pur Req_SET MFG Item]");
            measureInfo_Req.push("Measure.[Alloc Pur Req_SET MFG Qty]");
            measureInfo_Req.push("Measure.[Alloc Pur Req_SET MFG Site]");
            measureInfo_Req.push("Measure.[Alloc Pur Req_SET MFG Week]");
            measureInfo_Req.push("Measure.[Alloc Pur Req_ToSite]");
            measureInfo_Req.push("Measure.[Alloc Pur Req_Total]");    

            let dimensionInfo_Sum = [];
            let measureInfo_Sum = [];
            dimensionInfo_Sum.push("[Version].[Version Name]");
            dimensionInfo_Sum.push("[Time].[Week]");
            dimensionInfo_Sum.push("[Sub Location].[Sub Location]");
            dimensionInfo_Sum.push("[Item Material].[Item Material]");

            measureInfo_Sum.push("Measure.[Alloc Pur Sum_ETD Plan]");
            measureInfo_Sum.push("Measure.[Alloc Pur Sum_ETD Plan Flag]");
            measureInfo_Sum.push("Measure.[Alloc Pur Sum_Tot Supply]");

            if(parsedParams.fbParams.commitType == 1){
                for(var k=0; k < parsedParams.fbGridRows.length; k++ ){
                    fn_mergeSetting(dimensionInfo, measureInfo, fbVersion, parsedParams.fbGridRows[k]);
                    fn_mergeSetting(dimensionInfo_Req, measureInfo_Reg, fbVersion, parsedParams.fbGridRows[k]);
                    fn_mergeSetting(dimensionInfo_Sum, measureInfo_Sum, fbVersion, parsedParams.fbGridRows[k]);
                }
            }else{
                fn_mergeSetting(dimensionInfo, measureInfo, fbVersion, "");
                fn_mergeSetting(dimensionInfo_Req, measureInfo_Req, fbVersion, "");
                fn_mergeSetting(dimensionInfo_Sum, measureInfo_Sum, fbVersion, "");
            }

            return { "Code" : 0, "Msg" : "" };

        } catch ( e ) {
            return { "Code" : -1, "Msg" : e.message };
        }
    }

    var fn_mergeSetting = function(dimensionInfo, measureInfo, sVersion, sGridData){
        const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
        vdCommon.setLogLevel("Debug");         
        try{
              
            let dimensionQuery = [];
            for(var j=0; j < dimensionInfo.length; j++){
                let dim = dimensionInfo[j];
                if(dim == "[Version].[Version Name]"){
                    dimensionQuery.push(dim + ".["+sVersion+"]");
                }else{
                    if(sGridData[dim] != undefined || sGridData != ""){
                        dimensionQuery.push(dim + ".["+ sGridData[dim] + "]");
                    }else{
                        dimensionQuery.push(dim);
                    }                    
                }
            }

            let result= vdCommon.selectList(dimensionQuery, measureInfo, "", "", "");
            fn_mergeScope(result, dimensionInfo,  measureInfo, sVersion);

        } catch ( e ) {
            return { "Code" : -1, "Msg" : e.message };
        }
    }

    var fn_mergeScope = function(object, dimension, measure, sVersion){
        const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
        vdCommon.setLogLevel("Debug"); 
        try{
            for(var i=0; i < object.cs.rowCount ; i++){
                let dimensionQuery = [];
                for(var j=0; j < dimension.length; j++){
                    let dim = dimension[j];
                    if(dim == "[Version].[Version Name]"){
                        dimensionQuery.push(dim + ".[CWV_MP]");
                    }else{
                        let value = object.cs.row(i).cell(object.cs.memberColumnIndex(dim[0].replace("[","").replace("]",""), dim[1].replace("[","").replace("]",""))).Name;
                        dimensionQuery.push(dim + ".["+value+"]");
                    }
                }

                let changeMeasure = [];
                for(var n=0; n < measure.length; n++){
                    let measureName = measure[n];
                    changeMeasure.push(vdUtil.fn_qMeaForMerge(measureName, sVersion));
                }
    
                vdCommon.createMeasure(dimensionQuery, changeMeasure);
            }
            return true;

        }catch ( e ) {
            this.error(e.message);
            throw e;
        }

    }

    /************************ End : fn_merge *******************************************/

/************************************************* Mapping logic *************************************************/
    // Mapping 함수 정의, 마지막에 선언을 해야 함수를 정상적으로 인식함
    const functionMap = {
        "fn_cb_vendor" : fn_cb_vendor,
        "fn_cb_tpMtrl" :fn_cb_tpMtrl,
        "fn_save" : fn_save,
        "fn_navigationInfo":fn_navigationInfo
        ,"fn_cb_siteMF":fn_cb_siteMF
        ,"fn_filterHorizon":fn_filterHorizon
        ,"fn_merge" : fn_merge
    };

    return {
        fn_loadFunction : fn_loadFunction
    };    
});