define('o9.NSCM.JSSafetyStock', ['o9/data/query', 'o9/data/cellset', 'o9.NSCM.commonLib'], function(){	
	const programName = "o9.NSCM.JSSafetyStock";

    function fn_dataCheck(o9Params){
        try{
            const commonLib = require('o9.NSCM.commonLib');
            const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
            vdCommon.setLogLevel("Debug");

            vdCommon.printParams(o9Params);            
            // 파라메타 가져오기
            let parsedParams = JSON.parse(o9Params);

            var chkLocation = parsedParams.chkLocation;
            var chkItem = parsedParams.chkItem;
            let rtnValue = 0;

            if(chkLocation.length > 1 || chkItem.length > 1){
                rtnValue = 1;
                RuleOutputToUI = { Status : 'Error', Message : "You cannot select multiple rows." };  
            }

            //vdCommon.debug(">>>>>>>>>>>  fn_dataCheck End");        
            vdCommon.programEnd();

            return rtnValue;
        }catch ( e ) {
            RuleOutputToUI = { Status : 'Error', Message : "Js Logic Error : " + e.message };
            return;
        }

    }    
    
    function fn_selDataType(o9Params){

        let comboList = [];
        comboList.push({ Name: "MIN_TIME", DisplayName: "MIN_TIME" });        
        comboList.push({ Name: "MIN_ONHAND", DisplayName: "MIN_ONHAND" });

        return comboList;
    }

    function fn_selectFlag(o9Params){
        try{
            const commonLib = require('o9.NSCM.commonLib');
            const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
            vdCommon.setLogLevel("Debug");

            let comboList = [];
            comboList.push({ Name: "N", DisplayName: "N" });            
            comboList.push({ Name: "Y", DisplayName: "Y" });
            comboList.push({ Name: "-", DisplayName: "-" });

            //vdCommon.debug(">>>>>>>>>>> fn_selectFlag End");		
            vdCommon.programEnd(); 
            return comboList;
        }catch ( e ) {
            RuleOutputToUI = { Status : 'Error', Message : "Js Logic Error : " + e.message };
            return;
        }
    }

    function fn_weekCombo(o9Params){
        try{
            const commonLib = require('o9.NSCM.commonLib');
            const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
            vdCommon.setLogLevel("Debug");

            vdCommon.printParams(o9Params);      
             //2025.02.06 52주 조회 
            let selectQuery = 'select (&Next52Weeks);';
            //let selectQuery = 'Select ([Time].[Week].filter(#.Key >= &CurrentWeek.element(0).LeadOffset(0).Key && #.Key <= &CurrentWeek.element(0).LeadOffset(12).Key));';
            let selectResult = vdCommon.selectQueryList("[fn_weekCombo]" ,selectQuery );
            let comboList = vdCommon.fn_makeCombo(selectResult, {DimName : "Time", DimAttbName : "Week", existAll : false, Sort : "DisplayName", isDisplayNameWithCode : false});

            //vdCommon.debug(">>>>>>>>>>> fn_weekCombo End");		
            vdCommon.programEnd(); 

            return comboList;
        }catch ( e ) {
            RuleOutputToUI = { Status : 'Error', Message : "Js Logic Error : " + e.message };
            return;
        }
    }
    
    /*2025.04.22 수정
        Action Button을 2개로 구분하여 fn_updateValid 기능을 2개로 나눔
        fn_updateType, fn_updateMust
    */
    function fn_updateValid(o9Params){
        try{
            const commonLib = require('o9.NSCM.commonLib');
            const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
            vdCommon.setLogLevel("Debug");                        
            
            // 파라메타 가져오기
            vdCommon.printParams(o9Params);
            let parsedParams = JSON.parse(o9Params);
            let fbVersion = parsedParams.fbVersion;
            let fbCheckDataList =  parsedParams.fbCheckDataList;
            let fbMustFlag = parsedParams.fbMustFlag;
            let fbDataType = parsedParams.fbDataType;
            // SS
            //25.02.06 SS 메져그룹 수정으로 Location 삭제하고 AP2추가
            //vdCommon.debug("[Check List]" + fbCheckDataList.length);
            for(var k=0; k < fbCheckDataList.length; k++){
                let fbLocation = fbCheckDataList[k].fbLocation.Value;
                let fbItem = fbCheckDataList[k].fbItem.Value;
                let fbAP2 = fbCheckDataList[k].fbAP2.Value;

                let updateDimension = [];
                updateDimension.push('[Version].[Version Name].['+fbVersion+']');
                updateDimension.push('[Location].[Location].['+fbLocation+']');
                updateDimension.push('[Item].[Item].['+fbItem+']');
                updateDimension.push('[Sales Domain].[AP2].['+fbAP2+']');
                /*25.06.13 변경된 메져로 update 처리 변경
                    (1) SS_Valid Flag -> SS_Valid Flag Override
                    (2) SS_Must Flag Final -> SS_Must Flag Override
                    (3) SS_SS Type -> SS_SS Type Override
                */
                vdCommon.updateMeasure(updateDimension,
                    ['Measure.[SS_Must Flag Override] = if("'+fbMustFlag+'" == "-") then null else "'+fbMustFlag+'";',
                    'Measure.[SS_Valid Flag Override] = if("'+fbMustFlag+'" == "-") then Measure.[SS_Valid Flag] else "'+fbMustFlag+'";',
                    'Measure.[SS_SS Type Override] = "'+fbDataType+'";',
                    'Measure.[SS_Updated By] = CurrentUser().[User Name];',
                    'Measure.[SS_Update Time] = dateadd(Now(),9,"hour");'
                    ]);

            }
            //vdCommon.debug(">>>>>>>>>>>  fn_flagUpdate Update End");      
            vdCommon.programEnd();
        }catch ( e ) {
            RuleOutputToUI = { Status : 'Error', Message : "Js Logic Error : " + e.message };
            return;
        }
    }
    
    function fn_updateTarget(o9Params){
        try{
            const commonLib = require('o9.NSCM.commonLib');
            const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
            const vdUtil = new commonLib.VdUtil();
            vdCommon.setLogLevel("Debug");   

            vdCommon.printParams(o9Params);
            let parsedParams = JSON.parse(o9Params); 
            let fbVersion = parsedParams.fbVersion;
            let fbCheckDataList =  parsedParams.fbCheckDataList;
            let fbValue = parsedParams.fbValue;        
            let fbWeek = parsedParams.fbWeek; 

            if(!vdUtil.fn_isInt(fbValue)){
                fbValue = 0;
            }
        
            //Safety Stock Update
            // SS W
            for(var k=0; k < fbCheckDataList.length; k++){
                let fbLocation = fbCheckDataList[k].fbLocation.Value;
                let fbItem = fbCheckDataList[k].fbItem.Value;
                let fbAP2 = fbCheckDataList[k].fbAP2.Value;

                //선택한 주차을 제외한 52주차 데이타 중  Measure.[SS W_SS Target] 값의 MAX값을 조회함.
                let maxSelect = "Select([Location].[Location].["+fbLocation+"] * [Item].[Item].["+fbItem+"] * [Sales Domain].[AP2].["+fbAP2+"] ";                
                maxSelect += "* {max(Measure.[SS W_SS Target])as transient.Result}) ";
                maxSelect += "Where{&Next52Weeks.filter(~(#.Name in {"+fbWeek.map(item => `"${item}"`).join(",")+"}))";
                maxSelect += " , [Version].[Version Name].["+fbVersion+"] };";

                let maxSelectResult = vdCommon.selectQueryList("Group ID Select", maxSelect);

                let maxValue = 0
                if(maxSelectResult.rowCount > 0){
                    maxValue = maxSelectResult.cs.row(0).cell(maxSelectResult.cs.measureColumnIndex("Result"));
                }

                let SS_Target = 0;
                if(maxValue >  fbValue){
                    SS_Target  = maxValue;
                }else{
                    SS_Target = fbValue;
                }

                for(var i=0; i < fbWeek.length; i++){
                    let updateDimension = [];

                    updateDimension.push('[Version].[Version Name].['+fbVersion+']');
                    updateDimension.push('[Item].[Item].['+fbItem+']');
                    updateDimension.push('[Location].[Location].['+fbLocation+']');
                    updateDimension.push('[Sales Domain].[AP2].['+fbAP2+']');
                    updateDimension.push('[Time].[Week].['+fbWeek[i]+']');

                    if(vdCommon.existMeasure(updateDimension, ['Measure.[SS W_SS Target]'], "")){
                        vdCommon.updateMeasure(updateDimension, ['Measure.[SS W_SS Target] = "'+fbValue+'";']);
                    }else{
                        vdCommon.createMeasure(updateDimension, ['Measure.[SS W_SS Target] = "'+fbValue+'";']); 
                    }
                    //2025.04.25 김보은프로 요청을 추가함.
                    //SS 메져그룹 Measure.[SS_Update Time], Measure.[SS_Updated By] 메져에 일자와 유저 정보 업데이트    
                    let updateData = 'Measure.[SS_Valid Flag Override] = ';
                    updateData += 'if(Measure.[SS_Must Flag Override] == "N") then ';
                    updateData += 'if (Measure.[SS_3160 Qty] > 0 || Measure.[SS_61 Qty] > 0 || Measure.[SS_EOH Week] > Measure.[SS_Target EOH] || Measure.[SS_Adj WOS] > Measure.[SS_Target WOS] || ';
                    updateData += '(Measure.[SS_SS type Override] == "MIN_ONHAND" && Measure.[SS_Demand] < '+SS_Target+')) then "N" else "Y" ';
                    updateData += 'else "Y";';
                    vdCommon.updateMeasure( ['[Version].[Version Name].['+fbVersion+']',
                                            '[Item].[Item].['+fbItem+']',
                                            '[Location].[Location].['+fbLocation+']',
                                            '[Sales Domain].[AP2].['+fbAP2+']'],
                                            ['Measure.[SS_SS Target] = "'+SS_Target+'";',
                                             updateData,
                                             'Measure.[SS_Updated By] = CurrentUser().[User Name];',
                                             'Measure.[SS_Update Time] = dateadd(Now(),9,"hour");'
                                            ]
                                        );
                }
            }    
            //vdCommon.debug(">>>>>>>>>>> fn_updateTarget End");		
            vdCommon.programEnd(); 
        }catch ( e ) {
            RuleOutputToUI = { Status : 'Error', Message : "Js Logic Error : " + e.message };
            return;
        }
    }

    function fn_updateType(o9Params){
        try{
            const commonLib = require('o9.NSCM.commonLib');
            const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
            vdCommon.setLogLevel("Debug");                        
            
            // 파라메타 가져오기
            vdCommon.printParams(o9Params);
            let parsedParams = JSON.parse(o9Params);
            let fbVersion = parsedParams.fbVersion;
            let fbCheckDataList =  parsedParams.fbCheckDataList;
            let fbDataType = parsedParams.fbDataType;
            // SS
            //25.02.06 SS 메져그룹 수정으로 Location 삭제하고 AP2추가
            //vdCommon.debug("[Check List]" + fbCheckDataList.length);
            for(var k=0; k < fbCheckDataList.length; k++){
                let fbLocation = fbCheckDataList[k].fbLocation.Value;
                let fbItem = fbCheckDataList[k].fbItem.Value;
                let fbAP2 = fbCheckDataList[k].fbAP2.Value;

                let updateDimension = [];
                updateDimension.push('[Version].[Version Name].['+fbVersion+']');
                updateDimension.push('[Location].[Location].['+fbLocation+']');
                updateDimension.push('[Item].[Item].['+fbItem+']');
                updateDimension.push('[Sales Domain].[AP2].['+fbAP2+']');
                /*25.06.13 변경된 메져로 update 처리 변경
                    (1) SS_SS Type -> SS_SS Type Override
                */
                let updateData = 'Measure.[SS_Valid Flag Override] = ';
                updateData += 'if(Measure.[SS_Must Flag Override] == "N") then ';
                updateData += 'if (Measure.[SS_3160 Qty] > 0 || Measure.[SS_61 Qty] > 0 || Measure.[SS_EOH Week] > Measure.[SS_Target EOH] || Measure.[SS_Adj WOS] > Measure.[SS_Target WOS] || ';
                updateData += '("'+fbDataType+'" == "MIN_ONHAND" && Measure.[SS_Demand] < measure.[SS_SS target])) then "N" else "Y" ';
                updateData += 'else "Y";';
                vdCommon.updateMeasure(updateDimension,
                    ['Measure.[SS_SS Type Override] = "'+fbDataType+'";',
                     updateData, 
                     'Measure.[SS_Updated By] = CurrentUser().[User Name];',
                     'Measure.[SS_Update Time] = dateadd(Now(),9,"hour");'
                    ]);
            }
            //vdCommon.debug(">>>>>>>>>>>  fn_flagUpdate Update End");      
            vdCommon.programEnd();
        }catch ( e ) {
            RuleOutputToUI = { Status : 'Error', Message : "Js Logic Error : " + e.message };
            return;
        }
    }
    
    function fn_updateMust(o9Params){
        try{
            const commonLib = require('o9.NSCM.commonLib');
            const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
            vdCommon.setLogLevel("Debug");                        
            
            // 파라메타 가져오기
            vdCommon.printParams(o9Params);
            let parsedParams = JSON.parse(o9Params);
            let fbVersion = parsedParams.fbVersion;
            let fbCheckDataList =  parsedParams.fbCheckDataList;
            let fbMustFlag = parsedParams.fbMustFlag;
            // SS
            //25.02.06 SS 메져그룹 수정으로 Location 삭제하고 AP2추가
            //vdCommon.debug("[Check List]" + fbCheckDataList.length);
            for(var k=0; k < fbCheckDataList.length; k++){
                let fbLocation = fbCheckDataList[k].fbLocation.Value;
                let fbItem = fbCheckDataList[k].fbItem.Value;
                let fbAP2 = fbCheckDataList[k].fbAP2.Value;

                let updateDimension = [];
                updateDimension.push('[Version].[Version Name].['+fbVersion+']');
                updateDimension.push('[Location].[Location].['+fbLocation+']');
                updateDimension.push('[Item].[Item].['+fbItem+']');
                updateDimension.push('[Sales Domain].[AP2].['+fbAP2+']');

                /*
                #25.06.13 변경된 메져로 update 처리 변경
                    (1) SS_Valid -> SS_Valid Flag Override
                    (2) SS_Must Flag Final -> SS_Must Flag Override
                # 25.06.25 
                  fbMustFlag가 "-" 인경우
                   Measure.[SS_Must Flag], Measure.[SS_Must Flag Override] null 처리함.
                */
                let updateMeasure = [];
                let updateData = 'Measure.[SS_Valid Flag Override] = ';
                updateData += 'if("'+fbMustFlag+'" == "N") then ';
                updateData += 'if (Measure.[SS_3160 Qty] > 0 || Measure.[SS_61 Qty] > 0 || Measure.[SS_EOH Week] > Measure.[SS_Target EOH] || Measure.[SS_Adj WOS] > Measure.[SS_Target WOS] || ';
                updateData += '(Measure.[SS_SS type Override] == "MIN_ONHAND" && Measure.[SS_Demand] < measure.[SS_SS target])) then "N" else "Y" ';
                updateData += 'else "Y";';

                if(fbMustFlag == "-"){
                    updateMeasure.push('Measure.[SS_Must Flag] = null;');
                }
                updateMeasure.push('Measure.[SS_Must Flag Override] = if("'+fbMustFlag+'" == "-") then null else "'+fbMustFlag+'";');
                updateMeasure.push(updateData);
                updateMeasure.push('Measure.[SS_Updated By] = CurrentUser().[User Name];');
                updateMeasure.push('Measure.[SS_Update Time] = dateadd(Now(),9,"hour");');
                vdCommon.updateMeasure(updateDimension, updateMeasure);
            }
  
            vdCommon.programEnd();
        }catch ( e ) {
            RuleOutputToUI = { Status : 'Error', Message : "Js Logic Error : " + e.message };
            return;
        }
    }


    return{
        fn_dataCheck : fn_dataCheck,
        fn_selDataType : fn_selDataType,
        fn_selectFlag : fn_selectFlag,
        fn_weekCombo : fn_weekCombo,
        fn_updateValid : fn_updateValid,
        fn_updateTarget : fn_updateTarget,
        fn_updateType : fn_updateType,
        fn_updateMust : fn_updateMust
    };		
});