define('o9.NSCM.JSTactTime', ['o9/data/query', 'o9/data/cellset', 'o9.NSCM.commonLib'], function(){
	const programName = "o9.NSCM.JSTactTime";   
	
    function fn_update(o9Params){
        try{
            const commonLib = require('o9.NSCM.commonLib');
            const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
            vdCommon.setLogLevel("Debug");

            vdCommon.printParams(o9Params);
            let parsedParams = JSON.parse(o9Params); 
            let fbVersion = parsedParams.fbVersion;
            let fbData = parsedParams.fbData; 
            let fbProductivity= parsedParams.fbProductivity;
            let fbWeek = parsedParams.fbWeek;
            var strQuery = "";
            let weekList = "";     

            for(var k=0; k < fbWeek.length; k++){
                weekList+= '"'+fbWeek[k]+'"';
                
                if ((k + 1) < fbWeek.length){
                    weekList += ','
                }
            }

            for(var k = 0; k < fbData.length ; k++){
                var rows = fbData[k];
                var dimension = [];
                var measure = [];
                dimension.push('[Version].[Version Name].['+fbVersion+']');
                dimension.push('[Item].[Item].['+rows.chkItem.Value+']');
                dimension.push('[Location].[Location].['+rows.chkLocatioin.Value+']');
                dimension.push('[Line].[Line].['+rows.chkLine.Value+']');
                dimension.push('[Time].[Week].filter(#.Name in {'+weekList+'})');

                let productivity = (fbProductivity/100) ;

                measure.push("Measure.[Tact Time W_Time Override] = Measure.[Tact Time W_Time Override] * " + productivity + ";");
                strQuery += vdCommon.updateMeasureQuery(dimension, measure);
            }

            vdCommon.printStep("SQL :" + strQuery);
            vdCommon.executeQuery("Batch Query" , strQuery);
            //vdCommon.printStep(">>>>>>>>>>> fn_Submit End");		
            vdCommon.programEnd(); 
        }catch ( e ) {
            RuleOutputToUI = { Status : 'Error', Message : "Js Logic Error : " + e.message };
            return;
        }
    }

    function fn_selectWeek(o9Params){
        try{
            const commonLib = require('o9.NSCM.commonLib');
            const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
            vdCommon.setLogLevel("Debug");
            // 파라미터 가져오기
            let parsedParams = JSON.parse(o9Params);
            let fbTime = parsedParams.fbTime;

            let result = vdCommon.selectList(["[Time].[Week].filter(#.Key >= &CurrentWeek.element(0).Key && #.Key <= &CurrentWeek.element(0).LeadOffset(34).Key)"], [],"","orderby [Time].[Week].Name","");

            vdCommon.printCsData(result, 3);

            let comboList = vdCommon.fn_makeCombo(result, {DimName : "Time",DimAttbName : "Week", Sort :"DisplayName", existAll : false, isDisplayNameWithCode : false});
            vdCommon.debug("ComboData : " + JSON.stringify(comboList));

            vdCommon.programEnd();

            return comboList;

        }catch ( e ) {
            RuleOutputToUI = { Status : 'Error', Message : "Js Logic Error : " + e.message };
            return;
        }    
    }    

    return{
        fn_update : fn_update,
        fn_selectWeek : fn_selectWeek
    };		
});