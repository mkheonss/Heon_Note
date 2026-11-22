define('o9.NSCM.commonLibDA', ['o9.NSCM.commonLib'], function (commonLib) {
/*----------------------------------------------------------------------------------------------------------
    VERSION     HISTORY
   ========================
    20250721    CREATED

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
        };

    }

    return {DACommon, DAUtil};
});