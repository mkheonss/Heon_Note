define('o9.NSCM.commonLibDA', ['o9.NSCM.commonLib'], function (commonLib) {
/*----------------------------------------------------------------------------------------------------------
    VERSION     HISTORY
   ========================
    20250721    CREATED
    20250825    fn_getUserName() 함수 추가
    20250926    fn_getCurrentWeek(), fn_getCurrentWeekAdd() 함수 추가
    20250929    fn_GetCurrentKRDatetime(), fn_GetWeekDay() 함수 추가

  ----------------------------------------------------------------------------------------------------------*/
    class DACommon extends commonLib.NSCMCommon{
        constructor(programName) {
            super(programName);
        }

        infLog(msg, printFlag) {
            if (printFlag) {
                let logMsg = `${this.preFix}[${this.programName}] ${msg}`;
                Log.Info(logMsg);
            }
        }

        errLog(msg, printFlag) {
            if (printFlag) {
                let logMsg = `${this.errorPreFix}[${this.programName}] ${msg}`;
                Log.Error(logMsg);
            }
        }

        /**
         *  property를 DisplayAlias 명으로 반환한다.
         * @param result
         * @param dimensionName
         * @param attributeName
         * @param propertyName
         * @returns {*}
         */
        fn_makeDisplayAlias(result, dimensionName, attributeName, propertyName) {
            let propertyValue;
            for(let i=0; i < result.cs.rowCount ; i++){
                propertyValue = this.getPropertyValue(result.cs, i, dimensionName, attributeName, propertyName);
                result.cs.row(i).cell(result.cs.memberColumnIndex(dimensionName, attributeName)).DisplayAlias = propertyValue;
            }
            return result;
        }

        /**
         * CurrentUSer().[User Name]을 반환한다.
         * @returns {*}
         */
        fn_getUserName() {
            let query = `select CurrentUser().[User Name];`;
            return this.selectQuery('selectCurrentUserName', query).Result;
        }

        /**
         * 현재 주차 정보의 property를 반환한다.
         * @param param
         * @returns {*}
         */
        fn_getCurrentWeek(param){
            let query = `select &CurrentWeek.element(0).${param};`;
            return this.selectQuery('getCurrentWeek', query).Result;
        }

        /**
         * 현재 주차에서 interval만큼 +, - 한 주의 월요일 날짜
         * @param interval
         * @returns {*}
         */
        fn_getCurrentWeekAdd(interval){
            let query = `select &CurrentWeek.element(0).LeadOffSet(${interval}).Key;`;
            return this.selectQuery('fn_getCurrentWeekAdd', query).Result;
        }

        /*
            콤보 데이타 구성
            param = {
                        DimName : "Location", DimAttbName : "Location"
                        ,MeasureName : ""
                        ,ComboCodes : ["A","B"], ComboValues : ["A","B"]
                        ,Sort : "Name" / DisplayName
                        ,existAll : true
                        ,isOnlyName : true => Name, DisplayName 을 Name으로 보여준다.
                        }
            var comboList = vdCommon.fn_makeCombo(result, {DimName : "Location", DimAttbName : "Location", Sort : "DisplayName", isDisplayNameWithCode : true});
            var comboList = vdCommon.fn_makeCombo(result, {DimName : "Sub Location", DimAttbName : "Sub Location", existAll : true, Sort : "DisplayName", isDisplayNameWithCode : true});
        */
        fn_makeCombo(result, param) {
            var comboList = [];
            var validHashMap = {};
            var name = "";
            var displayName = "";
            var _name = "";
            var _displayName = "";
            var _displayAlias = "";

            if ( param["ComboCodes"] != undefined ) {
                var codes = param["ComboCodes"];
                var values = param["ComboValues"];
                for ( var i = 0; i < codes.length; i++ ) {
                    comboList.push({ Name : codes[i], DisplayName : values[i]});
                }
            } else {
                for ( var i = 0; i < result.cs.rowCount; i++ ) {
                    if ( param["DimName"] != undefined ) {
                        // this.debug(JSON.stringify(result.cs.row(i).cell(result.cs.memberColumnIndex(param["DimName"], param["DimAttbName"]))));
                        _name = result.cs.row(i).cell(result.cs.memberColumnIndex(param["DimName"], param["DimAttbName"])).Name;
                        _displayName = result.cs.row(i).cell(result.cs.memberColumnIndex(param["DimName"], param["DimAttbName"])).DisplayName;
                        _displayAlias = result.cs.row(i).cell(result.cs.memberColumnIndex(param["DimName"], param["DimAttbName"])).DisplayAlias;

                        // 25.6.27 Location.[Location], To Location.[To Location], Sub Location.[Sub Location] 경우에는
                        // _displayAlias 을 다른 곳에서 가져온다. ( 예외 케이스 )
                        // if ( param["DimName"] == "Location" && param["DimAttbName"] == "Location" ) {
                        //     _displayAlias = this.getPropertyValue(result.cs, i, param["DimName"], param["DimAttbName"], "Location Site ID");
                        // }
                        if ( param["DimName"] == "Sub Location" && param["DimAttbName"] == "Sub Location" ) {
                            _displayAlias = this.getPropertyValue(result.cs, i, param["DimName"], param["DimAttbName"], "Sub Location ID");
                        }
                        if ( param["DimName"] == "To Location" && param["DimAttbName"] == "To Location" ) {
                            _displayAlias = this.getPropertyValue(result.cs, i, param["DimName"], param["DimAttbName"], "To Location Site ID");
                        }
                        // 25.2.25 : DisplayAlias 을 우선으로 반영한다.
                        if ( _displayAlias != null && _displayAlias != "" ) {
                            _displayName = _displayAlias
                        }
                        // 25.7.1 : DisplayName 에 Desc 를 붙인다.
                        if ( param["DimDescAttbName"] != undefined ) {
                            _displayName = _displayName + " (" + result.cs.row(i).cell(result.cs.memberColumnIndex(param["DimName"], param["DimDescAttbName"])).Name + ")";
                        }

                        name = _name;
                        displayName = _displayName;

                        // - 일 경우는 무시
                        // if ( name == "-" ) {
                        //     continue;
                        // }

                        // DisplayName 에 코드도 같이 보여줄지 여부
                        if ( param["isDisplayNameWithCode"] != undefined && param["isDisplayNameWithCode"] ) {
                            displayName = _displayName + " (" + _name + ")";
                        }
                        // Name 에 DisplayName 도 같이 보여줄지 여부
                        if ( param["isNameWithDisplayName"] != undefined && param["isNameWithDisplayName"] ) {
                            name = _name + ":" + _displayName;
                        }

                        // Name, Display를 Name으로 보여준다.
                        if ( param["isOnlyName"] != undefined && param["isOnlyName"] ) {
                            displayName = _name;
                        }
                    } else if ( param["MeasureName"] != undefined ) {
                        name = result.cs.row(i).cell(result.cs.measureColumnIndex(param["MeasureName"]));
                        displayName = name;
                    }

                    if ( validHashMap[name] == undefined ) {
                        var rows = { Name : name, DisplayName : displayName};

                        // Casecade를 위한 컬럼 추가 => otherColumns=Item:Product Group:UI Product Group,Item:Product:UI Product
                        if ( param["includeField"] != undefined && param["includeField"] != "" ) {
                            var includeField = param["includeField"].split(",");
                            for ( var m = 0; m < includeField.length; m++ ) {
                                var dims = includeField[m].split(":");
                                rows[dims[2]] = result.cs.row(i).cell(result.cs.memberColumnIndex(dims[0], dims[1])).Name;
                            }
                        }

                        comboList.push(rows);
                        validHashMap[name] = name;
                    }
                }
            }

            if ( param["Sort"] != undefined ) {
                if ( param["Sort"] == "Name" ) {
                    comboList.sort((a, b) => {
                            if ( a.Name < b.Name ) return -1;
                            if ( a.Name > b.Name ) return 1;
                            return 0;
                        });
                } else {
                    comboList.sort((a, b) => {
                            if ( a.DisplayName < b.DisplayName ) return -1;
                            if ( a.DisplayName > b.DisplayName ) return 1;
                            return 0;
                        });
                }
            }

            if ( param["existAll"] != undefined && param["existAll"] ) {
                var all = { Name : "All", DisplayName : "All" };

                // includeField 에 All 넣기
                if ( param["includeField"] != undefined && param["includeField"] != "" ) {
                    var includeField = param["includeField"].split(",");
                    for ( var m = 0; m < includeField.length; m++ ) {
                        var dims = includeField[m].split(":");
                        all[dims[2]] = "All";
                    }
                }

                comboList.unshift(all);
            }

            return comboList;
        }
    }

    class DAUtil extends commonLib.NSCMUtil{
        /**
         * 문자열이 빈 문자열인지 체크하여 결과값을 리턴한다.
         * @param str		: 체크할 문자열
         */
        fn_isEmpty(str) {
            return typeof str === "undefined" || str === null || str === "";
        }

        /**
         * 문자열이 빈 문자열인지 체크하여 기본 문자열로 리턴한다.
         * @param str			: 체크할 문자열
         * @param defaultStr	: 문자열이 비어있을경우 리턴할 기본 문자열
         */
	    fn_nvl(str, defaultStr){
            if(typeof str === "undefined" || str === null || str === "")
                str = defaultStr ;

            return str ;
	    }

        fn_max(arr){
            return Math.max(...arr);
        }
        fn_min(arr){
            return Math.min(...arr);
        }
        fn_multiArr(arr){
            return arr.map(i => '[' + i +']').join(',');
        }
        fn_trim(str){
            if(typeof str === "undefined" || str === null || str === "")
                return "" ;
            else
                return str.trim();
        }
        /**
         * grid의 grain 변경시 grain 을 모두 선택하라는 메세지 출력 validation
         * message : Select all granularities in the grid.
         * @param tupleList
         */
        fn_validationGrainCheck(tupleList){
            let returnValue = 0;                            /* 0: 정상, 1: 오류메세지  */

            let flag = false;
              //tupleList(grain key값 확인)
            loopKeys: for(let i = 0 ; i< tupleList.length ; i++){
                              /* tuple Value  */
                            let item = tupleList[i];
                            let keys = Object.keys(item);
                            for(let j = 0 ; j < keys.length ; j++){
                                // Grain key값이 빈값이면 Error Msg return
                                if(this.fn_isEmpty(item[keys[j]].Value)){
                                    flag = true;
                                    break loopKeys;
                                }
                            }
                      }

            if(flag) {
                RuleOutputToUI = { Status : 'Error', Message : "Select all granularities in the grid." };
                returnValue = 1;
            }

            return returnValue;
        }

        /**
         *  grid에서 Multi checkbox 선택시 1건만 선택하라는 메세지 출력 Validation
         *  message : Choose only one.
         * @param tupleList
         */
        fn_validationMultiRowCheck(tupleList){
            let returnValue = 0;                            /* 0: 정상, 1: 오류메세지  */

            if(tupleList.length > 1){
                RuleOutputToUI = { Status : 'Error', Message : "Choose only one." };
                returnValue = 1;
            }

            return returnValue;
        }

        fn_validationShipToCodeInput(inputShipToCode) {
            if (!inputShipToCode) return { returnShipToCode: inputShipToCode, checkMessage: 'ShipToCode is empty' };

            const isNumeric = /^[0-9]+$/.test(inputShipToCode);
            let firstThreeZeros = inputShipToCode.startsWith('000');
            let lengthIsTen = inputShipToCode.length === 10;

            let returnShipToCode = inputShipToCode;

            // 1. 숫자이고 길이 7이면 앞에 '000' 붙임
            if (isNumeric && inputShipToCode.length === 7) {
                returnShipToCode = '000' + inputShipToCode;
                lengthIsTen = true;
                firstThreeZeros = true;
            }

            if(isNumeric){
                if(!lengthIsTen || !firstThreeZeros){
                    return { returnShipToCode: returnShipToCode,
                        checkMessage: "The number-only Ship To Code is 10 digits starting with '000'. Please check again."};
                }
            }

            // 조건에 걸리지 않으면 null 반환
            return { returnShipToCode: returnShipToCode, checkMessage: null };
        }

        fn_GetCurrentKRDatetime() {
            const kstMillis = (new Date()).getTime() + (9 * 60 * 60 * 1000);
            return new Date(kstMillis);
        }

        fn_GetWeekDay(pDate) {
            const week = ['SUN', 'MON', 'TUE', 'WED', 'THU', 'FRI', 'SAT'];
            return week[pDate.getDay()];
        }
    }

    return {DACommon, DAUtil};
});