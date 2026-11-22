define('o9.NSCM.JSEWNewModelDetail', ['o9/data/query', 'o9/data/cellset', 'o9.NSCM.commonLib'], function(){
    const programName = "o9.NSCM.JSEWNewModel";
    const commonLib = require('o9.NSCM.commonLib');
    const vdUtil = new commonLib.VdUtil();

    /*--------------------------------------------------------------------------------------------------*/
    // 프로그램명 : o9.NSCM.JSEWNewModelDetail
    // Action Button : EWNewModelDetail
    // 화면명 : New Model Detail
    // 2026.03.04 최초 생성
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
   /*{ "fbFuncName" : "fn_filterWeek" }*/
    var fn_filterWeek = function(parsedParams){
        const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
        vdCommon.setLogLevel("Debug");
        try{

            let CurrentMonth = vdCommon.selectResult('&CurrentMonth.element(0).DisplayName');
            let month = parseInt(CurrentMonth.substring(4,6));
            let selectQuery = "";

           if( month>= 1 && month <=9){
                selectQuery = 'Select (&LastYear.relatedmembers([Planning Month]).filter(#.[Planning Month$DisplayAlias] in {"Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"}).relatedmembers([Week])';
                selectQuery += '.unionwith(&CurrentYear.relatedmembers([Planning Month]).filter(#.[Planning Month$DisplayAlias] in {"Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep"}).relatedmembers([Week])));';                
           }else{
                selectQuery = 'Select (&CurrentYear.relatedmembers([Planning Month]).filter(#.[Planning Month$DisplayAlias] in {"Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"}).relatedmembers([Week])';
                selectQuery +='.unionwith(&NextYear.relatedmembers([Planning Month]).filter(#.[Planning Month$DisplayAlias] in {"Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep"}).relatedmembers([Week])));'; 
            } ;

            let result =  vdCommon.selectQueryList("fn_filterWeek", selectQuery);
            let comboList = vdCommon.fn_makeCombo(result, {DimName : "Time", DimAttbName : "Week", Sort : "DisplayName"});
            let arrayWeek = comboList.map((value) => value.Name);

            return { "Code" : 0, "Msg" : "", "Week": arrayWeek };

        }catch (e) {
            return { "Code": -1, "Msg": e.message };
        }
    }
    
    // Mapping 함수 정의, 마지막에 선언을 해야 함수를 정상적으로 인식함
    const functionMap = {
       "fn_filterWeek"   : fn_filterWeek
    };

    return {
        fn_loadFunction : fn_loadFunction
    };

});