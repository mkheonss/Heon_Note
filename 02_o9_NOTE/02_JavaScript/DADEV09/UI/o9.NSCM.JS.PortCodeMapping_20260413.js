define('o9.NSCM.JS.PortCodeMapping', ['o9.NSCM.commonLibDA'], function(commonLib)
{
    /**
     * o9.NSCM.JS.PortCodeMapping.
     *
     *  Master Data > Logistics > Port Code Mapping > Port Code Mapping
     */
/**********************************************************************************************************************/
/***************** CONST 설정 ****************************************************************************/
/**********************************************************************************************************************/
    /* Program Name */
    const programName = "o9.NSCM.JS.PortCodeMapping";

    /* jsErrorMsg   */
    const jsErrorMsg = "Please contact the system administrator.";

    /* setting  */
    let daCommon = new commonLib.DACommon(programName);
    daCommon.setLogLevel("Debug")
    let daUtil = new commonLib.DAUtil();

/**********************************************************************************************************************/
/***************** COMBO List START **********************************************************************/
/**********************************************************************************************************************/

/**********************************************************************************************************************/
/***************** COMBO List END ************************************************************************/
/**********************************************************************************************************************/

/**********************************************************************************************************************/
/***************** TRANSACTION START *********************************************************************/
/**********************************************************************************************************************/


    function validateFiveChars(context) {
        if (context) {
            if (context.Location.length !== 5) {
                throw "입력값은 정확히 5자리여야 합니다.";
            }
        }
        return context;
    }

    /** Loading Port       **/
    /* Loading Add Submit   */
    let fn_AddLoadingPortCode = function(o9Params){
        let parsedParams = JSON.parse(o9Params);
        // 사용자Id
        parsedParams.userId = daCommon.fn_getUserName();

        let sPortCode = parsedParams.fb_PortCode;
        let sNSCMPortCode = parsedParams.fb_NSCMPortCode;
        let sServiceRegionLv1 = parsedParams.fb_ServiceRegionLv1;
        let sServiceRegionLv2 = parsedParams.fb_ServiceRegionLv2;
        let sLogisticsPort = parsedParams.fb_LogisticsPort;

        //공백제거
        sPortCode = sPortCode.trim();
        sNSCMPortCode = sNSCMPortCode.trim();
        sServiceRegionLv1 = sServiceRegionLv1.trim();
        sServiceRegionLv2 = sServiceRegionLv2.trim();
        sLogisticsPort = sLogisticsPort.trim();

        //영문숫자만입력
        const regex = /^[A-Za-z0-9]*$/; // 영문숫자만 허용
        if ((!regex.test(sPortCode))) {
            RuleOutputToUI = {Status: 'Error', Message: "Please enter letters and numbers."};
            return;
        }

        // if (sPortCode.length !== 5) {
        //     RuleOutputToUI = {Status: 'Error', Message: "The input value must be exactly 5 digits long."};
        //     return;
        // }
        
        //코드 대문자화
        sPortCode = sPortCode.toUpperCase();
        sNSCMPortCode = sNSCMPortCode.toUpperCase();
        sServiceRegionLv1 = sServiceRegionLv1.toUpperCase();
        sServiceRegionLv2 = sServiceRegionLv2.toUpperCase();
        sLogisticsPort = sLogisticsPort.toUpperCase();

        // 1.중복 검사
        let countQuery = "[Loading Port].[Loading Port].["+sPortCode+"]";
        let iCountExist = daCommon.selectCount(countQuery);

        if(iCountExist > 0) {
            RuleOutputToUI = {Status: 'Error', Message: "Port Code [Origin] is duplicated."};
            return;
        }

        parsedParams.fb_PortCode = sPortCode;
        parsedParams.fb_NSCMPortCode = sNSCMPortCode;
        parsedParams.fb_ServiceRegionLv1 = sServiceRegionLv1;
        parsedParams.fb_ServiceRegionLv2 = sServiceRegionLv2;
        parsedParams.fb_LogisticsPort = sLogisticsPort;

        // 2.creatememberLoadingPortCode
        QueryCommon.creatememberLoadingPort(parsedParams);

        // 3.cartesian scope
        QueryCommon.insert_cartesianScopeLoadingPortMapping(parsedParams);

    };

    /* Loading Copy Submit   */
    let fn_CopyLoadingPortCode = function(o9Params){
        let parsedParams = JSON.parse(o9Params);
        // 사용자Id
        parsedParams.userId = daCommon.fn_getUserName();
        let sPortCode = parsedParams.fb_PortCode;
        let sNSCMPortCode = parsedParams.fb_NSCMPortCode;
        let sServiceRegionLv1 =parsedParams.fb_ServiceRegionLv1;
        let sServiceRegionLv2 =parsedParams.fb_ServiceRegionLv2;
        let sLogisticsPort =parsedParams.fb_LogisticsPort;

        //공백제거
        sPortCode = sPortCode.trim();
        sNSCMPortCode = sNSCMPortCode.trim();
        sServiceRegionLv1 = sServiceRegionLv1.trim();
        sServiceRegionLv2 = sServiceRegionLv2.trim();
        sLogisticsPort = sLogisticsPort.trim();

        //영문숫자만입력
        const regex = /^[A-Za-z0-9]*$/; // 영문숫자만 허용
        if ((!regex.test(sPortCode))) {
            RuleOutputToUI = {Status: 'Error', Message: "Please enter letters and numbers."};
            return;
        }

        //코드 대문자화
        sPortCode = sPortCode.toUpperCase();
        sNSCMPortCode = sNSCMPortCode.toUpperCase();
        sServiceRegionLv1 = sServiceRegionLv1.toUpperCase();
        sServiceRegionLv2 = sServiceRegionLv2.toUpperCase();
        sLogisticsPort = sLogisticsPort.toUpperCase();

        // 1.중복 검사
        let countQuery = "[Loading Port].[Loading Port].["+sPortCode+"]";
        let iCountExist = daCommon.selectCount(countQuery);

        if(iCountExist > 0) {
            RuleOutputToUI = {Status: 'Error', Message: "Port Code [Origin] is duplicated."};
            return;
        }

        parsedParams.fb_PortCode = sPortCode;
        parsedParams.fb_NSCMPortCode = sNSCMPortCode;
        parsedParams.fb_ServiceRegionLv1 = sServiceRegionLv1;
        parsedParams.fb_ServiceRegionLv2 = sServiceRegionLv2;
        parsedParams.fb_LogisticsPort = sLogisticsPort;

        if(iCountExist === 0) {
            // 2.creatememberLoadingPortCode
            QueryCommon.creatememberLoadingPort(parsedParams);
        }
        // 3.cartesian scope
        QueryCommon.insert_cartesianScopeLoadingPortMapping(parsedParams);

    };

    /* Loading Valid Submit */
    let fn_ValidLoadingPortCode = function(o9Params){
        let parsedParams = JSON.parse(o9Params);
        parsedParams.userId = daCommon.fn_getUserName();

        let tupleList = parsedParams.fb_TupleList;
        let confrmValid = '';

        //valid check start
        tupleList.forEach(element => {
            parsedParams.fb_LoadingPort = element.fb_LoadingPort.Value;
            let cntValidStatus = QueryCommon.selectCountLoadingValidFlagStatus2(parsedParams);
            if(cntValidStatus > 0) {
                confrmValid += parsedParams.fb_LoadingPort + ",";
            }
        });
        // Log.Info("##########################confrmValid:: "+confrmValid);

        if(confrmValid !== '' && parsedParams.fb_isValid === 'Y'){
            let arrConfirmLoadingPort = confrmValid.split(',');
            arrConfirmLoadingPort = arrConfirmLoadingPort.splice(0, arrConfirmLoadingPort.length-1);
            RuleOutputToUI = { Status : 'Error', Message : "(" + arrConfirmLoadingPort.join(", ") + ") The valid value for 'Loading Port Code' is already 'Y' in the Origin Port Code Mapping. "};
            Log.Info("##########################arrConfirmLoadingPort:: "+arrConfirmLoadingPort);
            return;
        }
        //valid check end

        tupleList.forEach(element => {

            parsedParams.fb_LoadingPort = element.fb_LoadingPort.Value;

            let query =
                `cartesian scope:(
                                    [Version].[Version Name].[${parsedParams.fb_Version}]
                                * [Loading Port].[Loading Port].[${parsedParams.fb_LoadingPort}]
                                );
                    Measure.[Loading Port Mapping_Updated By] = "${parsedParams.userId}";
                    Measure.[Loading Port Mapping_Update Time] = dateadd(Now(),0,"hour");
                    Measure.[Loading Port Mapping_Status] = "REQ";
                    Measure.[Loading Port Mapping_Valid Flag] = "${parsedParams.fb_isValid}";
                end scope;
                `;
            daCommon.executeQuery('valid_cartesianScopeLoadingPortMapping', query);

            // let query = `
            //     Select ([Loading Port].[Loading Port].[${parsedParams.fb_LoadingPort}] ) on row, 
            //         ({Measure.[Loading Port Mapping_Status],
            //         Measure.[Loading Port Mapping_Logistics Port],
            //         Measure.[Loading Port Mapping_SCM Port Code],
            //         Measure.[Loading Port Mapping_Service Region Lv1],
            //         Measure.[Loading Port Mapping_Service Region Lv2]
            //         }) on column
            //     where {
            //             [Version].[Version Name].[CWV_MP]
            //         };
            // `;
            // let resultSet =  daCommon.selectQueryList('fn_SelectLoadingPortMappingStatus', query);
            // let sStatus = daCommon.getMeasureValue(resultSet.cs, 0, 'Loading Port Mapping_Status');

            // //REQ 일경우만 
            // if(sStatus === "REQ") {

                // //delete model
                // QueryCommon.deleteModelLoadingPort(parsedParams);

                // daCommon.executeQuery('deletememberLoadingPort1', `deletemember ([Loading Port].[Loading Port] = {,"${parsedParams.fb_LoadingPort}"}) cascade;`);
                // daCommon.executeQuery('pergememberLoadingPort1', "purge members([Loading Port].[Loading Port]);");
            // }
        });

    };

    /* Loading Confirm Submit */
    let fn_ConfirmLoadingPortCode = function(o9Params){
        let parsedParams = JSON.parse(o9Params);
        // 사용자Id
        parsedParams.userId = daCommon.fn_getUserName();
        let tupleList = parsedParams.fb_TupleList;
        let confrmValid = '';


        //isValid check start
        tupleList.forEach(element => {
            parsedParams.fb_LoadingPort = element.fb_LoadingPort.Value;
            let cntValidStatus_isvalid = QueryCommon.selectCountLoadingValidFlagStatus(parsedParams);
            if(cntValidStatus_isvalid > 0) {
                confrmValid += parsedParams.fb_LoadingPort + ",";
            }
        });
        Log.Info("##########################confrmValid:: "+confrmValid);

        if(confrmValid !== ''){
            let arrConfirmLoadingPort = confrmValid.split(',');
            arrConfirmLoadingPort = arrConfirmLoadingPort.splice(0, arrConfirmLoadingPort.length-1);
            RuleOutputToUI = { Status : 'Error', Message : "(" + arrConfirmLoadingPort.join(", ") + ") The confirmation is unavailable because the Origin Port Code is invalid."};
            Log.Info("##########################arrConfirmLoadingPort:: "+arrConfirmLoadingPort);
            return;
        }
        //isValid check end
        
        confrmValid = '';

        //valid check start
        tupleList.forEach(element => {
            parsedParams.fb_LoadingPort = element.fb_LoadingPort.Value;
            let cntValidStatus = QueryCommon.selectCountLoadingValidStatus(parsedParams);
            if(cntValidStatus > 0) {
                confrmValid += parsedParams.fb_LoadingPort + ",";
            }
        });
        Log.Info("##########################confrmValid:: "+confrmValid);

        if(confrmValid !== ''){
            let arrConfirmLoadingPort = confrmValid.split(',');
            arrConfirmLoadingPort = arrConfirmLoadingPort.splice(0, arrConfirmLoadingPort.length-1);
            RuleOutputToUI = { Status : 'Error', Message : "(" + arrConfirmLoadingPort.join(", ") + ") Loading Port Code is confirmed in the Origin Port Code Mapping. "};
            Log.Info("##########################arrConfirmLoadingPort:: "+arrConfirmLoadingPort);
            // return;
        }
        //valid check end

        tupleList.forEach(element => {

            parsedParams.fb_LoadingPort = element.fb_LoadingPort.Value;
            let query = `
                Select ([Loading Port].[Loading Port].[${parsedParams.fb_LoadingPort}] ) on row, 
                    ({Measure.[Loading Port Mapping_Status],
                    Measure.[Loading Port Mapping_Logistics Port],
                    Measure.[Loading Port Mapping_SCM Port Code],
                    Measure.[Loading Port Mapping_Service Region Lv1],
                    Measure.[Loading Port Mapping_Service Region Lv2]
                    }) on column
                where {
                        [Version].[Version Name].[CWV_MP]
                    };
            `;
            let resultSet =  daCommon.selectQueryList('fn_SelectLoadingPortMappingStatus', query);
            let sStatus = daCommon.getMeasureValue(resultSet.cs, 0, 'Loading Port Mapping_Status');

            //REQ 일경우만 createmember 후 catesian
            if(sStatus === "REQ") {
                parsedParams.fb_LogisticsPort = daCommon.getMeasureValue(resultSet.cs, 0, 'Loading Port Mapping_Logistics Port');
                parsedParams.fb_SCMPortCode = daCommon.getMeasureValue(resultSet.cs, 0, 'Loading Port Mapping_SCM Port Code');
                parsedParams.fb_ServiceRegionLv1 = daCommon.getMeasureValue(resultSet.cs, 0, 'Loading Port Mapping_Service Region Lv1');
                parsedParams.fb_ServiceRegionLv2 = daCommon.getMeasureValue(resultSet.cs, 0, 'Loading Port Mapping_Service Region Lv2');

                let sNSCMPortCode = parsedParams.fb_SCMPortCode;
                let sServiceRegionLv1 =parsedParams.fb_ServiceRegionLv1;
                let sServiceRegionLv2 =parsedParams.fb_ServiceRegionLv2;
                let sLogisticsPort =parsedParams.fb_LogisticsPort;
        
                //공백제거
                sNSCMPortCode = sNSCMPortCode.trim();
                sServiceRegionLv1 = sServiceRegionLv1.trim();
                sServiceRegionLv2 = sServiceRegionLv2.trim();
                sLogisticsPort = sLogisticsPort.trim();

                //대문자화
                // sNSCMPortCode = sNSCMPortCode.toUpperCase();
                // sServiceRegionLv1 = sServiceRegionLv1.toUpperCase();
                // sServiceRegionLv2 = sServiceRegionLv2.toUpperCase();
                // sLogisticsPort = sLogisticsPort.toUpperCase();
        
                let query =
                    `createmember ( [Loading Port].[Loading Port] = {,"${parsedParams.fb_LoadingPort}"}
                                    ,[Loading Port].[Loading Logistics Port] = {,"${sLogisticsPort}"}
                                    ,[Loading Port].[Loading SCM Port] = {,"${sNSCMPortCode}"}
                                    ,[Loading Port].[Loading Service Region Level 1] = {,"${sServiceRegionLv1}"}
                                    ,[Loading Port].[Loading Service Region Level 2] = {,"${sServiceRegionLv2}"}
                                    );
                    `;
                    daCommon.executeQuery('confirmCreatememberLoadingPort', query);

                query =
                    `cartesian scope:(
                                        [Version].[Version Name].[${parsedParams.fb_Version}]
                                    * [Loading Port].[Loading Port].[${parsedParams.fb_LoadingPort}]
                                    );
                        Measure.[Loading Port Mapping_Updated By] = "${parsedParams.userId}";
                        Measure.[Loading Port Mapping_Update Time] = dateadd(Now(),0,"hour");
                        Measure.[Loading Port Mapping_Status] = "CON";
                    end scope;
                `;
                daCommon.executeQuery('confirm_cartesianScopeLoadingPortMapping', query);

            }
        });

    };

    /*  
        fn_ValidMultiSelect : Multirow check 후 copy 버튼 클릭 시 retrun 1
    */
    let fn_ValidMultiSelect =  function(o9Params){
        let parsedParams = JSON.parse(o9Params);
        let returnValue = 0;                            /* 0: 정상, 1: 오류메세지  */
        let tupleList = parsedParams.fb_TupleList;

        daUtil.fn_validationMultiRowCheck(tupleList);

    };
    
    let fn_ValidLoadingConfirm = function(o9Params){
        let parsedParams = JSON.parse(o9Params);
        let returnValue = 0;
        let confrmValid = '';
        let tupleList = parsedParams.fb_TupleList;


        tupleList.forEach(element => {
            parsedParams.fb_LoadingPort = element.fb_LoadingPort.Value;
            let cntValidStatus = QueryCommon.selectCountLoadingValidStatus(parsedParams);
            if(cntValidStatus > 0) {
                confrmValid += parsedParams.fb_LoadingPort + ",";
            }
        });

        if(confrmValid != ''){
            let arrConfirmLoadingPort = confrmValid.split(',');
            arrConfirmLoadingPort = arrConfirmLoadingPort.splice(0, arrConfirmLoadingPort.length-1);
            RuleOutputToUI = { Status : 'Warning', Message : "(" + arrConfirmLoadingPort.join(", ") + ") Loading Port Code is confirmed in the Origin Port Code Mapping. "};
            returnValue = 1;
        }

        return returnValue;
    };



    /** Discharge Port     **/
    /* Discharge Add Submit */
    let fn_AddDischargePortCode = function(o9Params){
        let parsedParams = JSON.parse(o9Params);
        // 사용자Id
        parsedParams.userId = daCommon.fn_getUserName();

        let sPortCode = parsedParams.fb_PortCode;
        let sNSCMPortCode = parsedParams.fb_NSCMPortCode;
        let sServiceRegionLv1 = parsedParams.fb_ServiceRegionLv1;
        let sServiceRegionLv2 = parsedParams.fb_ServiceRegionLv2;
        let sLogisticsPort = parsedParams.fb_LogisticsPort;

        //공백제거
        sPortCode = sPortCode.trim();
        sNSCMPortCode = sNSCMPortCode.trim();
        sServiceRegionLv1 = sServiceRegionLv1.trim();
        sServiceRegionLv2 = sServiceRegionLv2.trim();
        sLogisticsPort = sLogisticsPort.trim();

        //영문숫자만입력
        const regex = /^[A-Za-z0-9]*$/; // 영문숫자만 허용
        if ((!regex.test(sPortCode))) {
            RuleOutputToUI = {Status: 'Error', Message: "Please enter letters and numbers."};
            return;
        }


        //코드 대문자화
        sPortCode = sPortCode.toUpperCase();
        sNSCMPortCode = sNSCMPortCode.toUpperCase();
        sServiceRegionLv1 = sServiceRegionLv1.toUpperCase();
        sServiceRegionLv2 = sServiceRegionLv2.toUpperCase();
        sLogisticsPort = sLogisticsPort.toUpperCase();

        // 1.중복 검사
        let countQuery = "[Discharge Port].[Discharge Port].["+sPortCode+"]";
        let iCountExist = daCommon.selectCount(countQuery);

        if(iCountExist > 0) {
            RuleOutputToUI = {Status: 'Error', Message: "Port Code [Discharge] is duplicated."};
            return;
        }

        parsedParams.fb_PortCode = sPortCode;
        parsedParams.fb_NSCMPortCode = sNSCMPortCode;
        parsedParams.fb_ServiceRegionLv1 = sServiceRegionLv1;
        parsedParams.fb_ServiceRegionLv2 = sServiceRegionLv2;
        parsedParams.fb_LogisticsPort = sLogisticsPort;

        // 2.creatememberDischargePortCode
        QueryCommon.creatememberDischargePort(parsedParams);

        // 3.cartesian scope
        QueryCommon.insert_cartesianScopeDischargePortMapping(parsedParams);

    };

    /* Discharge Copy Submit   */
    let fn_CopyDischargePortCode = function(o9Params){
        let parsedParams = JSON.parse(o9Params);
        // 사용자Id
        parsedParams.userId = daCommon.fn_getUserName();
        let sPortCode = parsedParams.fb_PortCode;
        let sNSCMPortCode = parsedParams.fb_NSCMPortCode;
        let sServiceRegionLv1 =parsedParams.fb_ServiceRegionLv1;
        let sServiceRegionLv2 =parsedParams.fb_ServiceRegionLv2;
        let sLogisticsPort =parsedParams.fb_LogisticsPort;

        //공백제거
        sPortCode = sPortCode.trim();
        sNSCMPortCode = sNSCMPortCode.trim();
        sServiceRegionLv1 = sServiceRegionLv1.trim();
        sServiceRegionLv2 = sServiceRegionLv2.trim();
        sLogisticsPort = sLogisticsPort.trim();

        //영문숫자만입력
        const regex = /^[A-Za-z0-9]*$/; // 영문숫자만 허용
        if ((!regex.test(sPortCode))) {
            RuleOutputToUI = {Status: 'Error', Message: "Please enter letters and numbers."};
            return;
        }

        //코드 대문자화
        sPortCode = sPortCode.toUpperCase();
        sNSCMPortCode = sNSCMPortCode.toUpperCase();
        sServiceRegionLv1 = sServiceRegionLv1.toUpperCase();
        sServiceRegionLv2 = sServiceRegionLv2.toUpperCase();
        sLogisticsPort = sLogisticsPort.toUpperCase();
        

        // 1.중복 검사
        let countQuery = "[Discharge Port].[Discharge Port].["+sPortCode+"]";
        let iCountExist = daCommon.selectCount(countQuery);

        if(iCountExist > 0) {
            RuleOutputToUI = {Status: 'Error', Message: "Port Code [Discharge] is duplicated."};
            // return;
        }

        parsedParams.fb_PortCode = sPortCode;
        parsedParams.fb_NSCMPortCode = sNSCMPortCode;
        parsedParams.fb_ServiceRegionLv1 = sServiceRegionLv1;
        parsedParams.fb_ServiceRegionLv2 = sServiceRegionLv2;
        parsedParams.fb_LogisticsPort = sLogisticsPort;

        if(iCountExist === 0) {
            // 2.creatememberDischargePortCode
            QueryCommon.creatememberDischargePort(parsedParams);
        }
        // 3.cartesian scope
        QueryCommon.insert_cartesianScopeDischargePortMapping(parsedParams);

    };

    /* Discharge Valid Submit */
    let fn_ValidDischargePortCode = function(o9Params){
        let parsedParams = JSON.parse(o9Params);
        parsedParams.userId = daCommon.fn_getUserName();

        let tupleList = parsedParams.fb_TupleList;
        let confrmValid = '';

        //valid check start
        tupleList.forEach(element => {
            parsedParams.fb_DischargePort = element.fb_DischargePort.Value;
            let cntValidStatus = QueryCommon.selectCountDischargeValidFlagStatus2(parsedParams);
            if(cntValidStatus > 0) {
                confrmValid += parsedParams.fb_DischargePort + ",";
            }
        });
        // Log.Info("##########################confrmValid:: "+confrmValid);

        if(confrmValid !== '' && parsedParams.fb_isValid === 'Y'){
            let arrConfirmDischargePort = confrmValid.split(',');
            arrConfirmDischargePort = arrConfirmDischargePort.splice(0, arrConfirmDischargePort.length-1);
            RuleOutputToUI = { Status : 'Error', Message : "(" + arrConfirmDischargePort.join(", ") + ")  The valid value for 'Discharge Port Code' is already 'Y' in the Discharge Port Code Mapping. "};
            Log.Info("##########################arrConfirmDischargePort:: "+arrConfirmDischargePort);
            return;
        }
        //valid check end

        tupleList.forEach(element => {

            parsedParams.fb_DischargePort = element.fb_DischargePort.Value;
            let query =
                `cartesian scope:(
                                    [Version].[Version Name].[${parsedParams.fb_Version}]
                                * [Discharge Port].[Discharge Port].[${parsedParams.fb_DischargePort}]
                                );
                    Measure.[Discharge Port Mapping_Updated By] = "${parsedParams.userId}";
                    Measure.[Discharge Port Mapping_Update Time] = dateadd(Now(),0,"hour");
                    Measure.[Discharge Port Mapping_Status] = "REQ";
                    Measure.[Discharge Port Mapping_Valid Flag] = "${parsedParams.fb_isValid}";
                end scope;
                `;
            daCommon.executeQuery('valid_cartesianScopeDischargePortMapping', query);

            // let query = `
            //     Select ([Discharge Port].[Discharge Port].[${parsedParams.fb_DischargePort}] ) on row, 
            //         ({Measure.[Discharge Port Mapping_Status],
            //         Measure.[Discharge Port Mapping_Logistics Port],
            //         Measure.[Discharge Port Mapping_SCM Port Code],
            //         Measure.[Discharge Port Mapping_Service Region Lv1],
            //         Measure.[Discharge Port Mapping_Service Region Lv2]
            //         }) on column
            //     where {
            //             [Version].[Version Name].[CWV_MP]
            //         };
            // `;
            // let resultSet =  daCommon.selectQueryList('fn_SelectDischargePortMappingStatus', query);
            // let sStatus = daCommon.getMeasureValue(resultSet.cs, 0, 'Discharge Port Mapping_Status');

            // //REQ 일경우만 
            // if(sStatus === "REQ") {

            //     //delete model
            //     QueryCommon.deleteModelDischargePort(parsedParams);


            //     daCommon.executeQuery('deletememberDischargePort1', `deletemember ([Discharge Port].[Discharge Port] = {,"${parsedParams.fb_DischargePort}"}) cascade;`);
            //     daCommon.executeQuery('pergememberDischargePort1', "purge members([Discharge Port].[Discharge Port]);");
            // }
        });

    };

    /* Discharge Confirm Submit */
    let fn_ConfirmDischargePortCode = function(o9Params){
        let parsedParams = JSON.parse(o9Params);
        // 사용자Id
        parsedParams.userId = daCommon.fn_getUserName();
        let tupleList = parsedParams.fb_TupleList;
        let confrmValid = '';

        //valid check start
        tupleList.forEach(element => {
            parsedParams.fb_DischargePort = element.fb_DischargePort.Value;
            let cntValidStatus_isvalid = QueryCommon.selectCountDischargeValidFlagStatus(parsedParams);
            if(cntValidStatus_isvalid > 0) {
                confrmValid += parsedParams.fb_DischargePort + ",";
            }
        });
        Log.Info("##########################confrmValid:: "+confrmValid);

        if(confrmValid !== ''){
            let arrConfirmDischargePort = confrmValid.split(',');
            arrConfirmDischargePort = arrConfirmDischargePort.splice(0, arrConfirmDischargePort.length-1);
            RuleOutputToUI = { Status : 'Error', Message : "(" + arrConfirmDischargePort.join(", ") + ") The confirmation is unavailable because the Discharge Port Code is invalid. "};
            Log.Info("##########################arrConfirmDischargePort:: "+arrConfirmDischargePort);
            return;
        }
        //valid check end
        
        confrmValid = '';

        //valid check start
        tupleList.forEach(element => {
            parsedParams.fb_DischargePort = element.fb_DischargePort.Value;
            let cntValidStatus = QueryCommon.selectCountDischargeValidStatus(parsedParams);
            if(cntValidStatus > 0) {
                confrmValid += parsedParams.fb_DischargePort + ",";
            }
        });
        Log.Info("##########################confrmValid:: "+confrmValid);

        if(confrmValid !== ''){
            let arrConfirmDischargePort = confrmValid.split(',');
            arrConfirmDischargePort = arrConfirmDischargePort.splice(0, arrConfirmDischargePort.length-1);
            RuleOutputToUI = { Status : 'Error', Message : "(" + arrConfirmDischargePort.join(", ") + ") Discharge Port Code is confirmed in the Discharge Port Code Mapping. "};
            Log.Info("##########################arrConfirmDischargePort:: "+arrConfirmDischargePort);
            // return;
        }
        //valid check end

        tupleList.forEach(element => {

            parsedParams.fb_DischargePort = element.fb_DischargePort.Value;
            let query = `
                Select ([Discharge Port].[Discharge Port].[${parsedParams.fb_DischargePort}] ) on row, 
                    ({Measure.[Discharge Port Mapping_Status],
                    Measure.[Discharge Port Mapping_Logistics Port],
                    Measure.[Discharge Port Mapping_SCM Port Code],
                    Measure.[Discharge Port Mapping_Service Region Lv1],
                    Measure.[Discharge Port Mapping_Service Region Lv2]
                    }) on column
                where {
                        [Version].[Version Name].[CWV_MP]
                    };
            `;
            let resultSet =  daCommon.selectQueryList('fn_SelectDischargePortMappingStatus', query);
            let sStatus = daCommon.getMeasureValue(resultSet.cs, 0, 'Discharge Port Mapping_Status');

            //REQ 일경우만 createmember 후 catesian
            if(sStatus === "REQ") {
                parsedParams.fb_LogisticsPort = daCommon.getMeasureValue(resultSet.cs, 0, 'Discharge Port Mapping_Logistics Port');
                parsedParams.fb_SCMPortCode = daCommon.getMeasureValue(resultSet.cs, 0, 'Discharge Port Mapping_SCM Port Code');
                parsedParams.fb_ServiceRegionLv1 = daCommon.getMeasureValue(resultSet.cs, 0, 'Discharge Port Mapping_Service Region Lv1');
                parsedParams.fb_ServiceRegionLv2 = daCommon.getMeasureValue(resultSet.cs, 0, 'Discharge Port Mapping_Service Region Lv2');

                let sNSCMPortCode = parsedParams.fb_SCMPortCode;
                let sServiceRegionLv1 =parsedParams.fb_ServiceRegionLv1;
                let sServiceRegionLv2 =parsedParams.fb_ServiceRegionLv2;
                let sLogisticsPort =parsedParams.fb_LogisticsPort;
        
                //공백제거
                sNSCMPortCode = sNSCMPortCode.trim();
                sServiceRegionLv1 = sServiceRegionLv1.trim();
                sServiceRegionLv2 = sServiceRegionLv2.trim();
                sLogisticsPort = sLogisticsPort.trim();

                //대문자화
                // sNSCMPortCode = sNSCMPortCode.toUpperCase();
                // sServiceRegionLv1 = sServiceRegionLv1.toUpperCase();
                // sServiceRegionLv2 = sServiceRegionLv2.toUpperCase();
                // sLogisticsPort = sLogisticsPort.toUpperCase();
                
                let query =
                    `createmember ( [Discharge Port].[Discharge Port] = {,"${parsedParams.fb_DischargePort}"}
                                    ,[Discharge Port].[Discharge Logistics Port] = {,"${sLogisticsPort}"}
                                    ,[Discharge Port].[Discharge SCM Port] = {,"${sNSCMPortCode}"}
                                    ,[Discharge Port].[Discharge Service Region Level 1] = {,"${sServiceRegionLv1}"}
                                    ,[Discharge Port].[Discharge Service Region Level 2] = {,"${sServiceRegionLv2}"}
                                    );
                    `;
                    daCommon.executeQuery('confirmCreatememberDischargePort', query);

                query =
                    `cartesian scope:(
                                        [Version].[Version Name].[${parsedParams.fb_Version}]
                                    * [Discharge Port].[Discharge Port].[${parsedParams.fb_DischargePort}]
                                    );
                        Measure.[Discharge Port Mapping_Updated By] = "${parsedParams.userId}";
                        Measure.[Discharge Port Mapping_Update Time] = dateadd(Now(),0,"hour");
                        Measure.[Discharge Port Mapping_Status] = "CON";
                    end scope;
                `;
                daCommon.executeQuery('confirm_cartesianScopeDischargePortMapping', query);

            }
        });

    };

    /** Dest Port     **/
    /* Dest Add Submit */
    let fn_AddDestPortCode = function(o9Params){
        let parsedParams = JSON.parse(o9Params);
        // 사용자Id
        parsedParams.userId = daCommon.fn_getUserName();

        let sPortCode = parsedParams.fb_PortCode;
        let sNSCMPortCode = parsedParams.fb_NSCMPortCode;
        let sServiceRegionLv1 = parsedParams.fb_ServiceRegionLv1;
        let sServiceRegionLv2 = parsedParams.fb_ServiceRegionLv2;
        let sLogisticsPort = parsedParams.fb_LogisticsPort;

        //공백제거
        sPortCode = sPortCode.trim();
        sNSCMPortCode = sNSCMPortCode.trim();
        sServiceRegionLv1 = sServiceRegionLv1.trim();
        sServiceRegionLv2 = sServiceRegionLv2.trim();
        sLogisticsPort = sLogisticsPort.trim();

        //영문숫자만입력
        const regex = /^[A-Za-z0-9]*$/; // 영문숫자만 허용
        if ((!regex.test(sPortCode))) {
            RuleOutputToUI = {Status: 'Error', Message: "Please enter letters and numbers."};
            return;
        }

        //코드 대문자화
        sPortCode = sPortCode.toUpperCase();
        sNSCMPortCode = sNSCMPortCode.toUpperCase();
        sServiceRegionLv1 = sServiceRegionLv1.toUpperCase();
        sServiceRegionLv2 = sServiceRegionLv2.toUpperCase();
        sLogisticsPort = sLogisticsPort.toUpperCase();

        // 1.중복 검사
        let countQuery = "[Dest Port].[Dest Port].["+sPortCode+"]";
        let iCountExist = daCommon.selectCount(countQuery);

        if(iCountExist > 0) {
            RuleOutputToUI = {Status: 'Error', Message: "Port Code [Destination] is duplicated."};
            return;
        }

        parsedParams.fb_PortCode = sPortCode;
        parsedParams.fb_NSCMPortCode = sNSCMPortCode;
        parsedParams.fb_ServiceRegionLv1 = sServiceRegionLv1;
        parsedParams.fb_ServiceRegionLv2 = sServiceRegionLv2;
        parsedParams.fb_LogisticsPort = sLogisticsPort;

        if(iCountExist === 0) {
            // 2.creatememberDestPortCode
            QueryCommon.creatememberDestPort(parsedParams);
        }
        // 3.cartesian scope
        QueryCommon.insert_cartesianScopeDestPortMapping(parsedParams);

    };

    /* Dest Copy Submit   */
    let fn_CopyDestPortCode = function(o9Params){
        let parsedParams = JSON.parse(o9Params);
        // 사용자Id
        parsedParams.userId = daCommon.fn_getUserName();

        let sPortCode = parsedParams.fb_PortCode;
        let sNSCMPortCode = parsedParams.fb_NSCMPortCode;
        let sServiceRegionLv1 =parsedParams.fb_ServiceRegionLv1;
        let sServiceRegionLv2 =parsedParams.fb_ServiceRegionLv2;
        let sLogisticsPort =parsedParams.fb_LogisticsPort;

		//공백제거
        sPortCode = sPortCode.trim();
        sNSCMPortCode = sNSCMPortCode.trim();
        sServiceRegionLv1 = sServiceRegionLv1.trim();
        sServiceRegionLv2 = sServiceRegionLv2.trim();
        sLogisticsPort = sLogisticsPort.trim();

        //영문숫자만입력
        const regex = /^[A-Za-z0-9]*$/; // 영문숫자만 허용
        if ((!regex.test(sPortCode))) {
            RuleOutputToUI = {Status: 'Error', Message: "Please enter letters and numbers."};
            return;
        }

        //대문자화
        sPortCode = sPortCode.toUpperCase();
        sNSCMPortCode = sNSCMPortCode.toUpperCase();
        sServiceRegionLv1 = sServiceRegionLv1.toUpperCase();
        sServiceRegionLv2 = sServiceRegionLv2.toUpperCase();
        sLogisticsPort = sLogisticsPort.toUpperCase();

        // 1.중복 검사
        let countQuery = "[Dest Port].[Dest Port].["+sPortCode+"]";
        let iCountExist = daCommon.selectCount(countQuery);

        if(iCountExist > 0) {
            RuleOutputToUI = {Status: 'Error', Message: "Port Code [Destination] is duplicated."};
            // return;
        }

        parsedParams.fb_PortCode = sPortCode;
        parsedParams.fb_NSCMPortCode = sNSCMPortCode;
        parsedParams.fb_ServiceRegionLv1 = sServiceRegionLv1;
        parsedParams.fb_ServiceRegionLv2 = sServiceRegionLv2;
        parsedParams.fb_LogisticsPort = sLogisticsPort;

        if(iCountExist === 0) {
            // 2.creatememberDestPortCode
            QueryCommon.creatememberDestPort(parsedParams);
        }
        // 3.cartesian scope
        QueryCommon.insert_cartesianScopeDestPortMapping(parsedParams);

    };

    /* Dest Valid Submit */
    let fn_ValidDestPortCode = function(o9Params){
        let parsedParams = JSON.parse(o9Params);
        parsedParams.userId = daCommon.fn_getUserName();

        let tupleList = parsedParams.fb_TupleList;
        let confrmValid = '';

        //valid check start
        tupleList.forEach(element => {
            parsedParams.fb_DestPort = element.fb_DestPort.Value;
            let cntValidStatus = QueryCommon.selectCountDestValidFlagStatus2(parsedParams);
            if(cntValidStatus > 0) {
                confrmValid += parsedParams.fb_DestPort + ",";
            }
        });
        // Log.Info("##########################confrmValid:: "+confrmValid);

        if(confrmValid !== '' && parsedParams.fb_isValid === 'Y'){
            let arrConfirmDestPort = confrmValid.split(',');
            arrConfirmDestPort = arrConfirmDestPort.splice(0, arrConfirmDestPort.length-1);
            RuleOutputToUI = { Status : 'Error', Message : "(" + arrConfirmDestPort.join(", ") + ") The valid value for 'Dest Port Code' is already 'Y' in the Dest Port Code Mapping. "};
            Log.Info("##########################arrConfirmDestPort:: "+arrConfirmDestPort);
            return;
        }
        //valid check end

        tupleList.forEach(element => {

            parsedParams.fb_DestPort = element.fb_DestPort.Value;
            let query =
                `cartesian scope:(
                    [Version].[Version Name].[${parsedParams.fb_Version}]
                    * [Dest Port].[Dest Port].[${parsedParams.fb_DestPort}]
                    );
                    Measure.[Dest Port Mapping_Updated By] = "${parsedParams.userId}";
                    Measure.[Dest Port Mapping_Update Time] = dateadd(Now(),0,"hour");
                    Measure.[Dest Port Mapping_Status] = "REQ";
                    Measure.[Dest Port Mapping_Valid Flag] = "${parsedParams.fb_isValid}";
                    end scope;
                `;
            daCommon.executeQuery('valid_cartesianScopeDestPortMapping', query);

            // let query = `
            //     Select ([Dest Port].[Dest Port].[${parsedParams.fb_DestPort}] ) on row, 
            //         ({Measure.[Dest Port Mapping_Status],
            //         Measure.[Dest Port Mapping_Logistics Port],
            //         Measure.[Dest Port Mapping_SCM Port Code],
            //         Measure.[Dest Port Mapping_Service Region Lv1],
            //         Measure.[Dest Port Mapping_Service Region Lv2]
            //         }) on column
            //     where {
            //             [Version].[Version Name].[CWV_MP]
            //         };
            // `;
            // let resultSet =  daCommon.selectQueryList('fn_SelectDestPortMappingStatus', query);
            // let sStatus = daCommon.getMeasureValue(resultSet.cs, 0, 'Dest Port Mapping_Status');

            // //REQ 일경우만 
            // if(sStatus === "REQ") {

            //     //delete model
            //     QueryCommon.deleteModelDestPort(parsedParams);

            //     daCommon.executeQuery('deletememberDestPort1', `deletemember ([Dest Port].[Dest Port] = {,"${parsedParams.fb_DestPort}"}) cascade;`);
            //     daCommon.executeQuery('pergememberDestPort1', "purge members([Dest Port].[Dest Port]);");
            // }
        });

    };

    /* Dest Confirm Submit */
    let fn_ConfirmDestPortCode = function(o9Params){
        let parsedParams = JSON.parse(o9Params);
        // 사용자Id
        parsedParams.userId = daCommon.fn_getUserName();
        let tupleList = parsedParams.fb_TupleList;
        let confrmValid = '';

        //valid check start
        tupleList.forEach(element => {
            parsedParams.fb_DestPort = element.fb_DestPort.Value;
            let cntValidStatus_isvalid = QueryCommon.selectCountDestValidFlagStatus(parsedParams);
            if(cntValidStatus_isvalid > 0) {
                confrmValid += parsedParams.fb_DestPort + ",";
            }
        });
        Log.Info("##########################confrmValid:: "+confrmValid);

        if(confrmValid !== ''){
            let arrConfirmDestPort = confrmValid.split(',');
            arrConfirmDestPort = arrConfirmDestPort.splice(0, arrConfirmDestPort.length-1);
            RuleOutputToUI = { Status : 'Error', Message : "(" + arrConfirmDestPort.join(", ") + ") The confirmation is unavailable because the Destination Port Code is invalid. "};
            Log.Info("##########################arrConfirmDestPort:: "+arrConfirmDestPort);
            return;
        }
        //valid check end

        confrmValid = '';
        
        //valid check start
        tupleList.forEach(element => {
            parsedParams.fb_DestPort = element.fb_DestPort.Value;
            let cntValidStatus = QueryCommon.selectCountDestValidStatus(parsedParams);
            if(cntValidStatus > 0) {
                confrmValid += parsedParams.fb_DestPort + ",";
            }
        });
        Log.Info("##########################confrmValid:: "+confrmValid);

        if(confrmValid !== ''){
            let arrConfirmDestPort = confrmValid.split(',');
            arrConfirmDestPort = arrConfirmDestPort.splice(0, arrConfirmDestPort.length-1);
            RuleOutputToUI = { Status : 'Error', Message : "(" + arrConfirmDestPort.join(", ") + ") Dest Port Code is confirmed in the Destination Port Code Mapping. "};
            Log.Info("##########################arrConfirmDestPort:: "+arrConfirmDestPort);
            // return;
        }
        //valid check end

        tupleList.forEach(element => {

            parsedParams.fb_DestPort = element.fb_DestPort.Value;
            let query = `
                Select ([Dest Port].[Dest Port].[${parsedParams.fb_DestPort}] ) on row, 
                    ({Measure.[Dest Port Mapping_Status],
                    Measure.[Dest Port Mapping_Logistics Port],
                    Measure.[Dest Port Mapping_SCM Port Code],
                    Measure.[Dest Port Mapping_Service Region Lv1],
                    Measure.[Dest Port Mapping_Service Region Lv2]
                    }) on column
                where {
                        [Version].[Version Name].[CWV_MP]
                    };
            `;
            let resultSet =  daCommon.selectQueryList('fn_SelectDestPortMappingStatus', query);
            let sStatus = daCommon.getMeasureValue(resultSet.cs, 0, 'Dest Port Mapping_Status');

            //REQ 일경우만 createmember 후 catesian
            if(sStatus === "REQ") {
                parsedParams.fb_LogisticsPort = daCommon.getMeasureValue(resultSet.cs, 0, 'Dest Port Mapping_Logistics Port');
                parsedParams.fb_SCMPortCode = daCommon.getMeasureValue(resultSet.cs, 0, 'Dest Port Mapping_SCM Port Code');
                parsedParams.fb_ServiceRegionLv1 = daCommon.getMeasureValue(resultSet.cs, 0, 'Dest Port Mapping_Service Region Lv1');
                parsedParams.fb_ServiceRegionLv2 = daCommon.getMeasureValue(resultSet.cs, 0, 'Dest Port Mapping_Service Region Lv2');

                let sNSCMPortCode = parsedParams.fb_SCMPortCode;
                let sServiceRegionLv1 =parsedParams.fb_ServiceRegionLv1;
                let sServiceRegionLv2 =parsedParams.fb_ServiceRegionLv2;
                let sLogisticsPort =parsedParams.fb_LogisticsPort;
        
                //공백제거
                sNSCMPortCode = sNSCMPortCode.trim();
                sServiceRegionLv1 = sServiceRegionLv1.trim();
                sServiceRegionLv2 = sServiceRegionLv2.trim();
                sLogisticsPort = sLogisticsPort.trim();

                //대문자화
                // sNSCMPortCode = sNSCMPortCode.toUpperCase();
                // sServiceRegionLv1 = sServiceRegionLv1.toUpperCase();
                // sServiceRegionLv2 = sServiceRegionLv2.toUpperCase();
                // sLogisticsPort = sLogisticsPort.toUpperCase();

                let query =
                    `createmember ( [Dest Port].[Dest Port] = {,"${parsedParams.fb_DestPort}"}
                                    ,[Dest Port].[Dest Logistics Port] = {,"${sLogisticsPort}"}
                                    ,[Dest Port].[Dest SCM Port] = {,"${sNSCMPortCode}"}
                                    ,[Dest Port].[Dest Service Region Level 1] = {,"${sServiceRegionLv1}"}
                                    ,[Dest Port].[Dest Service Region Level 2] = {,"${sServiceRegionLv2}"}
                                    );
                    `;
                    daCommon.executeQuery('confirmCreatememberDestPort', query);

                query =
                    `cartesian scope:(
                                        [Version].[Version Name].[${parsedParams.fb_Version}]
                                    * [Dest Port].[Dest Port].[${parsedParams.fb_DestPort}]
                                    );
                        Measure.[Dest Port Mapping_Updated By] = "${parsedParams.userId}";
                        Measure.[Dest Port Mapping_Update Time] = dateadd(Now(),0,"hour");
                        Measure.[Dest Port Mapping_Status] = "CON";
                    end scope;
                `;
                daCommon.executeQuery('confirm_cartesianScopeDestPortMapping', query);

            }
        });

    };


/**********************************************************************************************************************/
/***************** TRANSACTION END ***********************************************************************/
/**********************************************************************************************************************/

/**********************************************************************************************************************/
/***************** QUERY COMMON START  *******************************************************************/
/**********************************************************************************************************************/
    class QueryCommon {

        /** Loading Port     **/

        static creatememberLoadingPort(params){

            let query =
                `createmember ( [Loading Port].[Loading Port] = {,"${params.fb_PortCode}"}
                );
            `;

            // `createmember ( [Loading Port].[Loading Port] = {,"${params.fb_PortCode}"}
                //                 ,[Loading Port].[Loading Logistics Port] = {,"${params.fb_LogisticsPort}"}
                //                 ,[Loading Port].[Loading SCM Port] = {,"${params.fb_NSCMPortCode}"}
                //                 ,[Loading Port].[Loading Service Region Level 1] = {,"${params.fb_ServiceRegionLv1}"}
                //                 ,[Loading Port].[Loading Service Region Level 2] = {,"${params.fb_ServiceRegionLv2}"}
                //                 );
                //             `;
            daCommon.executeQuery('creatememberLoadingPort', query);
        };

        static insert_cartesianScopeLoadingPortMapping(params){
            let query=
                `cartesian scope:(
                                    [Version].[Version Name].[${params.fb_Version}]
                                  * [Loading Port].[Loading Port].[${params.fb_PortCode}]
                                );
                    Measure.[Loading Port Mapping_SCM Port Code] = "${params.fb_NSCMPortCode}";
                    Measure.[Loading Port Mapping_Service Region Lv1] = "${params.fb_ServiceRegionLv1}";
                    Measure.[Loading Port Mapping_Service Region Lv2] = "${params.fb_ServiceRegionLv2}";
                    Measure.[Loading Port Mapping_Logistics Port] = "${params.fb_LogisticsPort}";
                    Measure.[Loading Port Mapping_Created By] = "${params.userId}";
                    Measure.[Loading Port Mapping_Creation Time] = dateadd(Now(),0,"hour");
                    Measure.[Loading Port Mapping_Status] = "REQ";
                    Measure.[Loading Port Mapping_Valid Flag]= "Y";
                end scope;
            `;
            daCommon.executeQuery('insert_cartesianScopeLoadingPortMapping', query);
        };

        /*  
            selectCountLoadingValidStatus : Status 'CON' 체크 Validation
        */
        static selectCountLoadingValidStatus(parsedParams) {

            let lstDimension = [
                `[Version].[Version Name].[CWV_MP]`
                ,`[Loading Port].[Loading Port].[${parsedParams.fb_LoadingPort}]`
            ]
            let sMeasure = '';
            let sWhere = `where {Measure.[Loading Port Mapping_Status] == "CON"}`;
            return daCommon.selectListCount(lstDimension, sMeasure, sWhere);
        };

        /*  
            selectCountLoadingValidFlagStatus : isValid 'N' 체크 Validation
        */
        static selectCountLoadingValidFlagStatus(parsedParams) {

            let lstDimension = [
                `[Version].[Version Name].[CWV_MP]`
                ,`[Loading Port].[Loading Port].[${parsedParams.fb_LoadingPort}]`
            ]
            let sMeasure = '';
            let sWhere = `where {Measure.[Loading Port Mapping_Valid Flag] == "N"}`;
            return daCommon.selectListCount(lstDimension, sMeasure, sWhere);
        };

        /*  
            selectCountLoadingValidFlagStatus2 : confirm 'CON', isValid 'Y' 체크 Validation
        */
        static selectCountLoadingValidFlagStatus2(parsedParams) {

            let lstDimension = [
                `[Version].[Version Name].[CWV_MP]`
                ,`[Loading Port].[Loading Port].[${parsedParams.fb_LoadingPort}]`
            ]
            let sMeasure = ['Measure.[Loading Port Mapping_Valid Flag]'];
            let sWhere = `where {Measure.[Loading Port Mapping_Valid Flag] == "Y",
                                Measure.[Loading Port Mapping_Status] == "CON"}`;
            return daCommon.selectListCount(lstDimension, sMeasure, sWhere);
        };
    

        static deleteModelLoadingPort(parsedParams) {
            let query = `
                delete data for model [Loading Port Mapping]
                where {
                    [Version].[Version Name].[CWV_MP],
                    [Loading Port].[Loading Port].[${parsedParams.fb_LoadingPort}]
                };
            `;
            // infLog("##########################deleteModelLoadingPort:: "+query);
            return daCommon.executeQuery('deleteModelLoadingPort', query);
        };

            

        /** Discharge Port     **/
    
        static creatememberDischargePort(params){
            let query =
                `createmember ( [Discharge Port].[Discharge Port] = {,"${params.fb_PortCode}"}
                );
            `;

            // `createmember ( [Discharge Port].[Discharge Port] = {,"${params.fb_PortCode}"}
                //                 ,[Discharge Port].[Discharge Logistics Port] = {,"${params.fb_LogisticsPort}"}
                //                 ,[Discharge Port].[Discharge SCM Port] = {,"${params.fb_NSCMPortCode}"}
                //                 ,[Discharge Port].[Discharge Service Region Level 1] = {,"${params.fb_ServiceRegionLv1}"}
                //                 ,[Discharge Port].[Discharge Service Region Level 2] = {,"${params.fb_ServiceRegionLv2}"}
                //                 );
                //             `;
            daCommon.executeQuery('creatememberDischargePort', query);
        };

        static insert_cartesianScopeDischargePortMapping(params){
            let query=
                `cartesian scope:(
                                    [Version].[Version Name].[${params.fb_Version}]
                                    * [Discharge Port].[Discharge Port].[${params.fb_PortCode}]
                                );
                    Measure.[Discharge Port Mapping_SCM Port Code] = "${params.fb_NSCMPortCode}";
                    Measure.[Discharge Port Mapping_Service Region Lv1] = "${params.fb_ServiceRegionLv1}";
                    Measure.[Discharge Port Mapping_Service Region Lv2] = "${params.fb_ServiceRegionLv2}";
                    Measure.[Discharge Port Mapping_Logistics Port] = "${params.fb_LogisticsPort}";
                    Measure.[Discharge Port Mapping_Created By] = "${params.userId}";
                    Measure.[Discharge Port Mapping_Creation Time] = dateadd(Now(),0,"hour");
                    Measure.[Discharge Port Mapping_Status] = "REQ";
                    Measure.[Discharge Port Mapping_Valid Flag]= "Y";
                end scope;
            `;
            daCommon.executeQuery('insert_cartesianScopeDischargePortMapping', query);
        };

        static deleteModelDischargePort(parsedParams) {
            let query = `
                delete data for model [Discharge Port Mapping]
                where {
                    [Version].[Version Name].[CWV_MP],
                    [Discharge Port].[Discharge Port].[${parsedParams.fb_DischargePort}]
                };
            `;
            // infLog("##########################deleteModelDischargePort:: "+query);
            return daCommon.executeQuery('deleteModelDischargePort', query);
        };

        /*  
            selectCountDischargeValidStatus : Status 'CON' 체크 Validation
        */
        static selectCountDischargeValidStatus(parsedParams) {

            let lstDimension = [
                `[Version].[Version Name].[CWV_MP]`
                ,`[Discharge Port].[Discharge Port].[${parsedParams.fb_DischargePort}]`
            ]
            let sMeasure = '';
            let sWhere = `where {Measure.[Discharge Port Mapping_Status] == "CON"}`;
            return daCommon.selectListCount(lstDimension, sMeasure, sWhere);
        };
        
        /*  
            selectCountDischargeValidFlagStatus : isValid 'N' 체크 Validation
        */
        static selectCountDischargeValidFlagStatus(parsedParams) {

            let lstDimension = [
                `[Version].[Version Name].[CWV_MP]`
                ,`[Discharge Port].[Discharge Port].[${parsedParams.fb_DischargePort}]`
            ]
            let sMeasure = '';
            let sWhere = `where {Measure.[Discharge Port Mapping_Valid Flag] == "N"}`;
            return daCommon.selectListCount(lstDimension, sMeasure, sWhere);
        };
                    
        /*  
            selectCountDischargeValidFlagStatus2 : confirm 'CON', isValid 'Y' 체크 Validation
        */
        static selectCountDischargeValidFlagStatus2(parsedParams) {

            let lstDimension = [
                `[Version].[Version Name].[CWV_MP]`
                ,`[Discharge Port].[Discharge Port].[${parsedParams.fb_DischargePort}]`
            ]
            let sMeasure = ['Measure.[Discharge Port Mapping_Valid Flag]'];
            let sWhere = `where {Measure.[Discharge Port Mapping_Valid Flag] == "Y",
                                Measure.[Discharge Port Mapping_Status] == "CON"}`;
            return daCommon.selectListCount(lstDimension, sMeasure, sWhere);
        };
            

        /** Dest Port     **/
    
        static creatememberDestPort(params){
            let query =
                `createmember ( [Dest Port].[Dest Port] = {,"${params.fb_PortCode}"}
                );
            `;

            // `createmember ( [Dest Port].[Dest Port] = {,"${params.fb_PortCode}"}
                //                 ,[Dest Port].[Dest Logistics Port] = {,"${params.fb_LogisticsPort}"}
                //                 ,[Dest Port].[Dest SCM Port] = {,"${params.fb_NSCMPortCode}"}
                //                 ,[Dest Port].[Dest Service Region Level 1] = {,"${params.fb_ServiceRegionLv1}"}
                //                 ,[Dest Port].[Dest Service Region Level 2] = {,"${params.fb_ServiceRegionLv2}"}
                //                 );
                //             `;
            daCommon.executeQuery('creatememberDestPort', query);
        };

        static insert_cartesianScopeDestPortMapping(params){
            let query=
                `cartesian scope:(
                                    [Version].[Version Name].[${params.fb_Version}]
                                    * [Dest Port].[Dest Port].[${params.fb_PortCode}]
                                );
                    Measure.[Dest Port Mapping_SCM Port Code] = "${params.fb_NSCMPortCode}";
                    Measure.[Dest Port Mapping_Service Region Lv1] = "${params.fb_ServiceRegionLv1}";
                    Measure.[Dest Port Mapping_Service Region Lv2] = "${params.fb_ServiceRegionLv2}";
                    Measure.[Dest Port Mapping_Logistics Port] = "${params.fb_LogisticsPort}";
                    Measure.[Dest Port Mapping_Created By] = "${params.userId}";
                    Measure.[Dest Port Mapping_Creation Time] = dateadd(Now(),0,"hour");
                    Measure.[Dest Port Mapping_Status] = "REQ";
                    Measure.[Dest Port Mapping_Valid Flag]= "Y";
                end scope;
            `;
            daCommon.executeQuery('insert_cartesianScopeDestPortMapping', query);
        };

        static deleteModelDestPort(parsedParams) {
            let query = `
                delete data for model [Dest Port Mapping]
                where {
                    [Version].[Version Name].[CWV_MP],
                    [Dest Port].[Dest Port].[${parsedParams.fb_DestPort}]
                };
            `;
            // infLog("##########################deleteModelDestPort:: "+query);
            return daCommon.executeQuery('deleteModelDestPort', query);
        };

        /*  
            selectCountDestValidStatus : Status 'CON' 체크 Validation
        */
        static selectCountDestValidStatus(parsedParams) {

            let lstDimension = [
                `[Version].[Version Name].[CWV_MP]`
                ,`[Dest Port].[Dest Port].[${parsedParams.fb_DestPort}]`
            ]
            let sMeasure = '';
            let sWhere = `where {Measure.[Dest Port Mapping_Status] == "CON"}`;
            return daCommon.selectListCount(lstDimension, sMeasure, sWhere);
        };

        /*  
            selectCountDestValidFlagStatus : isValid 'N' 체크 Validation
        */
        static selectCountDestValidFlagStatus(parsedParams) {

            let lstDimension = [
                `[Version].[Version Name].[CWV_MP]`
                ,`[Dest Port].[Dest Port].[${parsedParams.fb_DestPort}]`
            ]
            let sMeasure = '';
            let sWhere = `where {Measure.[Dest Port Mapping_Valid Flag] == "N"}`;
            return daCommon.selectListCount(lstDimension, sMeasure, sWhere);
        };

        /*  
            selectCountDestValidFlagStatus2 : confirm 'CON', isValid 'Y' 체크 Validation
        */
        static selectCountDestValidFlagStatus2(parsedParams) {

            let lstDimension = [
                `[Version].[Version Name].[CWV_MP]`
                ,`[Dest Port].[Dest Port].[${parsedParams.fb_DestPort}]`
            ]
            let sMeasure = ['Measure.[Dest Port Mapping_Valid Flag]'];
            let sWhere = `where {Measure.[Dest Port Mapping_Valid Flag] == "Y",
                                Measure.[Dest Port Mapping_Status] == "CON"}`;
            
            return daCommon.selectListCount(lstDimension, sMeasure, sWhere);
        };
    

    }

/**********************************************************************************************************************/
/***************** QUERY COMMON END  *********************************************************************/
/**********************************************************************************************************************/

    return {
        //add LoadingPort
        fn_AddLoadingPortCode : daCommon.fn_decorator(fn_AddLoadingPortCode),
        //confirm LoadingPort
        fn_ConfirmLoadingPortCode : daCommon.fn_decorator(fn_ConfirmLoadingPortCode),
        //copy LoadingPort
        fn_CopyLoadingPortCode : daCommon.fn_decorator(fn_CopyLoadingPortCode),
        //delete LoadingPort
        fn_ValidLoadingPortCode : daCommon.fn_decorator(fn_ValidLoadingPortCode),

        //add DischargePort
        fn_AddDischargePortCode : daCommon.fn_decorator(fn_AddDischargePortCode),
        //confirm DischargePort
        fn_ConfirmDischargePortCode : daCommon.fn_decorator(fn_ConfirmDischargePortCode),
        //copy DischargePort
        fn_CopyDischargePortCode : daCommon.fn_decorator(fn_CopyDischargePortCode),
        //delete DischargePort
        fn_ValidDischargePortCode : daCommon.fn_decorator(fn_ValidDischargePortCode),


        //add DestPort
        fn_AddDestPortCode : daCommon.fn_decorator(fn_AddDestPortCode),
        //confirm DestPort
        fn_ConfirmDestPortCode : daCommon.fn_decorator(fn_ConfirmDestPortCode),
        //copy DestPort
        fn_CopyDestPortCode : daCommon.fn_decorator(fn_CopyDestPortCode),
        //delete DestPort
        fn_ValidDestPortCode : daCommon.fn_decorator(fn_ValidDestPortCode),

        //fn_ValidMultiSelect
        fn_ValidMultiSelect : daCommon.fn_decorator(fn_ValidMultiSelect),
        //fn_ValidLoadingConfirm
        fn_ValidLoadingConfirm : daCommon.fn_decorator(fn_ValidLoadingConfirm),

    };

});