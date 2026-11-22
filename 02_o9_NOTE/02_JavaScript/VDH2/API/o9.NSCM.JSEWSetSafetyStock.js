define('o9.NSCM.JSEWSetSafetyStock', ['o9/data/query', 'o9/data/cellset', 'o9.NSCM.commonLib'], function(){
    
    const programName = "o9.NSCM.JSEWSetSafetyStock";
    const commonLib = require('o9.NSCM.commonLib');
    const vdUtil = new commonLib.VdUtil();
    /*--------------------------------------------------------------------------------------------------*/
    // 프로그램명 : o9.NSCM.JSEWSetSafetyStock
    // Action Button : EWSetSafetyStock
    // 화면명 : SET/LCM Safety Stock
    // 2025.07.29 최초 생성
    // 2025.09.02 Error 메세지 처리 부분 수정
    // 2025.09.04 넘어오지 않은 주차를 체크하여 처리하도록 수정함.
    // 2025.09.08 API 호출 화면 구분, fn_save 호출시 viewtype param  추가함.
    // 2025.09.10 Must Flag "-"인 경우 Measure.[SS_Valid Flag Override] 값을 Measure.[SS_Valid Flag]로 Update 함.
    // 2025.09.23 save시  Vaild Flag 처리 조건에 Must flag 값 조건을 제외함.
    // 2025.09.23 update 일자 처리 수정
    // 2025.09.25 LCM 인 경우 조건 비교가 없음(default Vaild Flag값이 "Y" )
    // 2025.10.22 Measure.[SS_Must Flag Override],Measure.[SS_SS Type Override],Measure.[SS_Valid Flag Override] 삭제
    //            MIN_TIME인 경우 CurrentWeek 주차도 전주 데이타와 비교함.
    // 2025.11.06 Ensure Min_TIME week gap ≤ 7 days. ==> Ensure Min_TIME week gap < 7 days. 수정함.
    // 2025.12.31 fn_loadFunction() 수정함. => parsedParams 값 체크 로직 추가
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
    // { "fbFuncName" : "fn_cb_must" }
    // companyNameCombo
    var fn_cb_must = function(parsedParams){
        const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
        vdCommon.setLogLevel("Debug"); 
        try{

            let comboList = [];
            comboList.push({ Name: "N", DisplayName: "N" });            
            comboList.push({ Name: "Y", DisplayName: "Y" });
            comboList.push({ Name: "-", DisplayName: "-" });

            return { "Code" : 0, "Msg" : "", "Rows" : comboList };

        }catch ( e ) {
            return { "Code" : -1, "Msg" : e.message };
        }
    }
    /* ********************************************************************************** */
    // { "fbFuncName" : "fn_cb_ssType" }
    // companyNameCombo
    var fn_cb_ssType = function(parsedParams){
        const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
        vdCommon.setLogLevel("Debug"); 
        try{

            let comboList = [];
            comboList.push({ Name: "MIN_TIME", DisplayName: "MIN_TIME" });        
            comboList.push({ Name: "MIN_ONHAND", DisplayName: "MIN_ONHAND" });

            return { "Code" : 0, "Msg" : "", "Rows" : comboList };

        }catch ( e ) {
            return { "Code" : -1, "Msg" : e.message };
        }
    };
    /* ********************************************************************************** */
    var fn_validation = function(parsedParams){
        const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
        vdCommon.setLogLevel("Debug"); 
        try{
            vdCommon.debug("fn_validation parsedParams :: "+JSON.stringify(parsedParams));
            let fbBucketList = parsedParams.fbBucket;            
            vdCommon.debug("Params(fbBucketList) : " + JSON.stringify(fbBucketList));
            vdCommon.debug("[parsedParams.fbGridRows.length]" + parsedParams.fbGridRows.length);

            let errorCnt1 = 0, errorCnt2 = 0, errorCnt3 = 0;
            let errorMsg = "";
            let errorMsg1 = "Ensure Min_ONHAND ≤ Demand value.";
            let errorMsg2 = "Ensure Min_TIME week gap < 7 days.";
            let errorMsg3 = "Please enter <Must Flag>.";
            let viewtype = parsedParams.fbParams.viewtype;

            for ( var i = 0; i < parsedParams.fbGridRows.length; i++ ) {
                let rowStatus = parsedParams.fbGridRows[i]["rowstatus"];
                let fbLocation = parsedParams.fbGridRows[i]["[Location].[Location]"];
                let fbItem = parsedParams.fbGridRows[i]["[Item].[Item]"];
                let fbAP2 = parsedParams.fbGridRows[i]["[Sales Domain].[AP2]"];
                let fbMustFlag = parsedParams.fbGridRows[i]["Measure.[SS_Must Flag]"];

                parsedParams.fbGridRows[i]["rowmsg"] = "";
                parsedParams.fbGridRows[i]["errorflag"] = "";

                if(rowStatus == "U"){
                     //validation 체크함.
                     /*
                        1) measure.[SS_SS Type] == "MIN_ONHAND" 일 때, 
                        measure.[SS_Demand] 를 초과해서 입력했을 때 저장 불가 메시지 
                        "Please set MIN_ONHAND Target so that it does not exceed the Demand value."  보여줌.
                        1.1) MIN_ONHANE일때.. 52주차 Bucket 구간에서 MAX 데이타를 찾는다.
                     */
                     let ssType = parsedParams.fbGridRows[i]["Measure.[SS_SS Type]"];

                     let maxSSTargetQty = 0;
                     if(ssType == "MIN_ONHAND" && viewtype == "SET"){
                        let ssDemandQty = parsedParams.fbGridRows[i]["Measure.[SS_Demand]"];
                        for(var k =0; k < fbBucketList.length ; k++){
                            let sWeek = fbBucketList[k]["Name"];
                            let ssTargetQty = parsedParams.fbGridRows[i]["Week." + sWeek];
                            if(ssTargetQty == undefined || ssTargetQty == null){
                                ssTargetQty = 0;
                            }                            
                            //Max 데이타 체크
                            if( parseInt(ssTargetQty) >= parseInt(maxSSTargetQty)){
                                maxSSTargetQty = parseInt(ssTargetQty) ;
                            }
                            //vdCommon.debug("[Validateion-Max Finde]Max["+maxSSTargetQty+"],Value["+ssTargetQty+"]");
                        }

                        //vdCommon.debug("[Validateion]["+maxSSTargetQty+"]DemandQty["+ssDemandQty+"]");
                        if(parseInt(ssDemandQty) <= parseInt(maxSSTargetQty)){                            
                            errorCnt1++;
                            parsedParams.fbGridRows[i]["rowmsg"] = errorMsg1;
                            parsedParams.fbGridRows[i]["errorflag"] = "ERROR";
                        }
                     }

                     /*
                        2) measure.[SS_SS Type] == "MIN_TIME" 일 때 
				        전 주차 대비 7일 초과해서 셋팅하는 경우 해당 셀 빨간색 표시 + 저장 불가 메시지 
				        "Please set Min_Time Target so that the difference between weeks does not exceed 7 days." 보여줌.
                     */
                    if(ssType == "MIN_TIME"){
                        for(var k = 1; k < fbBucketList.length; k++){
                            let preWeek = "";
                            let currentWeek = "";
                            let preTargetQty = 0;
                            let currentTargetQty = 0;
                            preWeek = fbBucketList[k - 1]["Name"];
                            currentWeek = fbBucketList[k]["Name"];
                            preTargetQty = parsedParams.fbGridRows[i]["Week." +preWeek]; 
                            //주차별 SS W_SS Target 데이타가 어떤 포맷으로 넘어올까요?                            
                            if(preTargetQty == undefined || preTargetQty == null){
                                preTargetQty = 0;
                            }
                            currentTargetQty = parsedParams.fbGridRows[i]["Week." +currentWeek];                             
                            if(currentTargetQty == undefined || currentTargetQty == null){
                                currentTargetQty = 0;
                            }
                            vdCommon.debug("[MIN_TIME Check]["+k+"]["+preWeek+"]["+preTargetQty+"]["+currentWeek+"]["+currentTargetQty+"]");   
                            if( Math.abs(parseInt(currentTargetQty) -  parseInt(preTargetQty)) > 7){
                                errorCnt2++;
                                //errorMsgTemp += "["+currentWeek+"]["+parseInt(currentTargetQty)+"] - ["+currentWeek+"]["+parseInt(preTargetQty)+"]" ;
                                parsedParams.fbGridRows[i]["rowmsg"] = errorMsg2;
                                parsedParams.fbGridRows[i]["errorflag"] = "ERROR";
                                vdCommon.debug("[Error]" + errorMsg2);
                            }
                        }
                    }                   
                } 
            }

            if(errorCnt1 > 0 ){
                errorMsg = errorMsg1;       
            }
            if(errorCnt2 > 0 ){
                errorMsg += (errorMsg == "" ? "" : "\n")  + errorMsg2 ;                
            }
            if(errorCnt3 > 0 ){
                errorMsg += (errorMsg == "" ? "" : "\n")  + errorMsg3 ;                
            }

            if((errorCnt1 + errorCnt2 + errorCnt3 ) > 0){
                //Error Row만 Return 함.
                let checkGridRows = parsedParams.fbGridRows;
                const errorRows = checkGridRows.filter((checkGridRows)=>{return checkGridRows.errorflag === "ERROR"});
                parsedParams.fbGridRows = errorRows;
                vdCommon.debug("[Result]" + errorMsg);
                return { "Code" : -1, "Msg" : errorMsg, "Rows" : parsedParams.fbGridRows };
            }

            return { "Code" : 0, "Msg" : "" };
        }catch ( e ) {
            return { "Code" : -1, "Msg" : e.message };
        }  
    } ; 
    /* ********************************************************************************** */
    // Grid 데이타 저장시 호출되는 함수
    /* viewtype : SET /LCM

{"fbFuncName" : "fn_save",
 "fbParams": {"version":"CWV_MP", "viewtype":"SET"},
"fbGridRows" : [
{"rowstatus":"U", "rowindex":0,	
"[Location].[Location]" : "S422",
"[Item].[Item]" : "CY-BD40WD/EN",
"[Sales Domain].[AP2]" : "300672",
"Measure.[SS_Must Flag]" : "N",
"Measure.[SS_SS Type]" : "MIN_ONHAND",
"Measure.[SS_Demand]" : "0",
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
    var fn_save = function(parsedParams){
        const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
        vdCommon.setLogLevel("Debug"); 
        try{
            vdCommon.debug("parsedParams :: "+JSON.stringify(parsedParams));
            let fbVersion = parsedParams.fbParams.version;
            let viewtype = parsedParams.fbParams.viewtype;
            //2025.10.16 전주 데이타 조회
            let selectWeekQuery  = 'Select (&Next52Weeks. unionwith(&LastPastWeek));';
            let weekList = vdCommon.selectQueryList("fn_time", selectWeekQuery); 
            let bucketList = vdCommon.fn_makeCombo(weekList, {DimName : "Time", DimAttbName : "Week", Sort : "DisplayName"});
            parsedParams.fbBucket = bucketList;
            //Validation 체크            
            let errorData = fn_validation(parsedParams);
            if(errorData.Code == -1){
                return errorData
            }            

            for ( var i = 0; i < parsedParams.fbGridRows.length; i++ ) {
                let rowStatus = parsedParams.fbGridRows[i]["rowstatus"];

                if(rowStatus == "U"){                    
                    let fbLocation = parsedParams.fbGridRows[i]["[Location].[Location]"];
                    let fbItem = parsedParams.fbGridRows[i]["[Item].[Item]"];
                    let fbAP2 = parsedParams.fbGridRows[i]["[Sales Domain].[AP2]"];

                    let fbMustFlag = parsedParams.fbGridRows[i]["Measure.[SS_Must Flag]"];
                    let fbSSType = parsedParams.fbGridRows[i]["Measure.[SS_SS Type]"];
                    //vdCommon.debug("Data["+fbLocation+"]["+fbItem+"]["+fbAP2+"]["+fbMustFlag+"]["+fbSSType+"]");
                    
                    let maxSSTargetQty= 0;
                    let updateDimension = [];
                    let updateMeasure = [];

                    for(var k =0; k < bucketList.length; k++){
                        let sWeek = bucketList[k]["Name"];
                        //주차별 SS W_SS Target 데이타가 어떤 포맷으로 넘어올까요?
                        //Bucket 컬럼 명칭 방법 미정?
                        let ssTargetQty = parsedParams.fbGridRows[i]["Week." + sWeek];
                        //vdCommon.debug("[MaxTarget Check(1)]["+sWeek+"]["+maxSSTargetQty+"]["+ssTargetQty+"]");
                        if(ssTargetQty == undefined || ssTargetQty == null){
                            ssTargetQty = 0;
                        }
                        //Max 데이타 체크
                        if( parseInt(ssTargetQty) > parseInt(maxSSTargetQty)){
                            maxSSTargetQty = parseInt(ssTargetQty) ;
                        }
                        //vdCommon.debug("[MaxTarget Check(2)]["+sWeek+"]["+maxSSTargetQty+"]["+ssTargetQty+"]");

                        // SS W
                        if(ssTargetQty != undefined &&  ssTargetQty != null){
                            updateDimension = [];                      
                            updateDimension.push('[Version].[Version Name].['+fbVersion+']');
                            updateDimension.push('[Item].[Item].['+fbItem+']');
                            updateDimension.push('[Location].[Location].['+fbLocation+']');
                            updateDimension.push('[Sales Domain].[AP2].['+fbAP2+']');
                            updateDimension.push('[Time].[Week].['+sWeek+']');
    
                            updateMeasure = [];  
                            updateMeasure.push('Measure.[SS W_SS Target] ="'+ssTargetQty+'";'); 
    
                            if(vdCommon.existMeasure(updateDimension, ['Measure.[SS W_SS Target]'], "")){
                                vdCommon.updateMeasure(updateDimension,updateMeasure);
                            }else{
                                vdCommon.createMeasure(updateDimension,updateMeasure);
                            }
                        }
                    }

                    updateDimension = [];
                    updateMeasure = [];
                    updateDimension.push('[Version].[Version Name].['+fbVersion+']');
                    updateDimension.push('[Item].[Item].['+fbItem+']');
                    updateDimension.push('[Location].[Location].['+fbLocation+']');
                    updateDimension.push('[Sales Domain].[AP2].['+fbAP2+']');

                    if(fbSSType == "MIN_ONHAND"){
                        updateMeasure.push('Measure.[SS_SS Target] = "'+maxSSTargetQty+'";');
                    }                    
                    updateMeasure.push('Measure.[SS_SS Type] = "'+fbSSType+'";');

                    if(fbMustFlag == null || fbMustFlag == undefined ){
                        updateMeasure.push('Measure.[SS_Must Flag] = null;');
                    }else{
                        updateMeasure.push('Measure.[SS_Must Flag] = if("'+fbMustFlag+'" == "-") then null else "'+fbMustFlag+'";');
                    }
                    
                    let sUpdate = "";
                    /* 
                        2025.09.23 SS_Valid Flag 값 update시 Must Flag 조건 체크를 제외함.
                    */
                    if(viewtype == "SET"){
                        sUpdate = 'Measure.[SS_Valid Flag] = ';
                        sUpdate += 'if ((Measure.[SS_3160 Qty] > 0 || Measure.[SS_61 Qty] > 0) || ';
                        sUpdate += '(Measure.[SS_EOH Week] > Measure.[SS_Target EOH]) || ';
                        sUpdate += '(Measure.[SS_Adj WOS] > Measure.[SS_Target WOS]) || ';
                        sUpdate += '("'+fbSSType+'" == "MIN_ONHAND" && Measure.[SS_Demand] <= '+maxSSTargetQty+')) then "N" else "Y" ';
                        sUpdate += ';';
                    }else{
                        //2025.09.25 LCM 인 경우 조건 비교가 없음.
                        sUpdate = 'Measure.[SS_Valid Flag] =  "Y";';
                    }

                    updateMeasure.push(sUpdate);
                    updateMeasure.push('Measure.[SS_Updated By] = CurrentUser().[User Name];');
                    updateMeasure.push('Measure.[SS_Update Time] = Now();');

                    vdCommon.updateMeasure(updateDimension, updateMeasure);  
                }
            }

            return { "Code" : 0, "Msg" : "", "Rows" : "" };
            //

        }catch ( e ) {
            return { "Code" : -1, "Msg" : e.message };
        }
    }
    
    /* Scenario Version => Current Version(CWV_MP) Merge  */
    /* case1) param.commitType = 1 ( selected )
       case2) param.commitType = 0 ( bulk )
     */ 
/*
    {"fbFuncName" : "fn_merge",
        "fbParams":{ "commitType":1,
        "filters":{
                "[Version].[Version Name]":{"SelectedMembers":["202608_M_WI_05"],"SelectedMembersAlias":["202608_M_WI_05"],"MemberFilter":"&CWVUI","DimensionAliasName":"Plan ID"},
                "[Filter].[Filter]":{"SelectedMembers":[],"SelectedMembersAlias":[],"MemberFilter":""}
            }
        },
        "fbGridRows" : [
        {"[Location].[Location]" : "S422",
        "[Item].[Item]" : "CY-BD40WD/EN",
        "[Sales Domain].[AP2]" : "300672"
        }
        ]
    }
*/
    var fn_merge = function(parsedParams){
        const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
        vdCommon.setLogLevel("Debug"); 
        try{
            let fbVersion = vdUtil.fn_getFilterValue(parsedParams,"[Version].[Version Name]");
            let dimensionInfo = [];
            let dimensionValue = [];
            let measure = [];
            let whereQuery = 'Where { (Measure.[SS_Updated By] == CurrentUser().[User Name] ||  Measure.[SS_Updated By] == CurrentUser().Name)}'; // 정리가 필요함.(유저 Email, 녹스ID)
            let rtn = false;

            dimensionInfo.push("[Version].[Version Name]");
            dimensionInfo.push("[Location].[Location]");
            dimensionInfo.push("[Sales Domain].[AP2]");
            dimensionInfo.push("[Item].[Item]");

            measure.push("Measure.[SS_3160 Qty]");
            measure.push("Measure.[SS_61 Qty]");
            measure.push("Measure.[SS_Adj WOS]");
            measure.push("Measure.[SS_Asn]");
            measure.push("Measure.[SS_Demand]");
            //measure.push("Measure.[SS_Demand Gap]");
            //measure.push("Measure.[SS_EOH Gap]");
            measure.push("Measure.[SS_EOH Week]");
            measure.push("Measure.[SS_Must Flag]");
            measure.push("Measure.[SS_Must Flag Override]");
            measure.push("Measure.[SS_SS Target]");
            measure.push("Measure.[SS_SS Type]");
            measure.push("Measure.[SS_SS Type Override]");
            measure.push("Measure.[SS_Target EOH]");
            measure.push("Measure.[SS_Target WOS]");
            measure.push("Measure.[SS_Valid Flag]");
            measure.push("Measure.[SS_Valid Flag Override]");
            //measure.push("Measure.[SS_WOS Gap]");

            if(parsedParams.fbParams.commitType == 1){
                //Check 한 데이타 Merge
                for(var k=0; k < parsedParams.fbGridRows.length; k++ ){
                    dimensionValue = [];
                    for(var j=0; j < dimensionInfo.length; j++){
                        let dim = dimensionInfo[j];
                        if(dim == "[Version].[Version Name]"){
                            dimensionValue.push(dim + ".["+fbVersion+"]");
                        }else{
                            dimensionValue.push(dim + ".["+ parsedParams.fbGridRows[k][dim] + "]");
                        }
                    }

                    let result= vdCommon.selectList(dimensionValue, measure, whereQuery, "", "");
                    rtn = fn_mergeScope(result, dimensionInfo,  measure, fbVersion);
                }
            }else{
                //Current User 수정 데이타 전체 Merge
                dimensionValue = [];
                for(var j=0; j < dimensionInfo.length; j++){
                    let dim = dimensionInfo[j];
                    if(dim == "[Version].[Version Name]"){
                        dimensionValue.push(dim + ".["+fbVersion+"]");
                    }else{
                        dimensionValue.push(dim);
                    }
                }
                vdCommon.debug("[]")
                let result= vdCommon.selectList(dimensionValue, measure, whereQuery, "", "");
                rtn = fn_mergeScope(result, dimensionInfo,  measure, fbVersion);                
            }
            return { "Code" : 0, "Msg" : "" };
        }catch ( e ) {
            return { "Code" : -1, "Msg" : e.message };
        }
    }


    var fn_mergeScope = function(object, dimension, measure, sVersion){
        const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
        vdCommon.setLogLevel("Debug"); 
        try{

            for(var i=0; i < object.cs.rowCount ; i++){
                let dimensionValue = [];
                let dimensionSSW = [];
                for(var m = 0; m < dimension.length; m++){                    
                    if(dimension[m] == "[Version].[Version Name]"){
                        dimensionValue.push("CWV_MP");
                        dimensionSSW.push("[Version].[Version Name].[CWV_MP]");
                    }else{
                        let dim = dimension[m].split(".");
                        let value = object.cs.row(i).cell(object.cs.memberColumnIndex(dim[0].replace("[","").replace("]",""), dim[1].replace("[","").replace("]",""))).Name
                        dimensionValue.push(value);                        
                        dimensionSSW.push(dimension[m] +".["+value+"]");
                    }                   
                }
                let changeMeasure = [];
                let changeMeasureSSW = [];
                for(var n=0; n < measure.length; n++){
                    let measureName = measure[n];
                    changeMeasure.push(vdUtil.fn_qMeaForMerge(measureName, sVersion));
                }
                //CWV_MP 버젼 데이타 조회하여 createMeasure인지 updateMeasure 인치 체크함.
                let selectDimension = vdCommon.makeDimension(dimension, dimensionValue);

                //Merge 데이타 

                //fn_mergeUser
                changeMeasure.push(vdCommon.fn_mergeUser("Measure.[SS_Updated By]", sVersion));
                changeMeasure.push(vdUtil.fn_qMeaUpdateTime("Measure.[SS_Update Time]"));

                vdCommon.createMeasure(selectDimension, changeMeasure);

                //SS W 데이타 처리
                dimensionSSW.push('[Time].[Week]');                
                changeMeasureSSW.push(vdUtil.fn_qMeaForMerge("Measure.[SS W_SS Target]", sVersion));
                vdCommon.updateMeasure(dimensionSSW, changeMeasureSSW);
            }

        }catch ( e ) {
            this.error(e.message);
            throw e;
        }

    }
    
     /********************************** Mapping logic ************************************/
    // Mapping 함수 정의, 마지막에 선언을 해야 함수를 정상적으로 인식함
    const functionMap = {
        "fn_cb_must" : fn_cb_must,
        "fn_cb_ssType" : fn_cb_ssType,
        "fn_save" : fn_save
        ,"fn_merge" : fn_merge
    };

    return {
        fn_loadFunction : fn_loadFunction
    };    
});