define('o9.NSCM.JSMtrlConstraintType', ['o9.NSCM.commonLib'], function () {

    const programName = "o9.NSCM.JSMtrlConstraintType";

    const commonLib = require('o9.NSCM.commonLib');

    const vdCommon = new commonLib.VdCommon(programName);
    vdCommon.setLogLevel("Debug");

    const comboLevelArr = ["MSL1", "MSL2", "MSL3", "MSL4", "MSL5", "Item Material"];
    const levelKey = "Item Material";

    /**
     * Logs the given message.
     *
     * @param {string} msg - The message to be logged.
     * @returns {void}
     */
    let log = function(msg) {
        vdCommon.debug(msg);
    }

    /**
     * Prints the given parameters.
     *
     * @param {Array} params - The parameters to be printed.
     */
    let printParams = function(params) {
        vdCommon.printParams(params);
    }

    /**
     * Parses a JSON string or an object into a JavaScript object.
     *
     * @param {string | object} params - The JSON string or object to be parsed.
     * @returns {object} - The parsed JavaScript object.
     * @throws {SyntaxError} - If the JSON string is invalid and cannot be parsed.
     *
     * @example
     * const jsonString = '{"name": "John", "age": 25}';
     * const parsedObject = parse(jsonString);
     * // Returns: {name: "John", age: 25}
     *
     * const jsonObject = {name: "John", age: 25};
     * const parsedObject = parse(jsonObject);
     * // Returns: {name: "John", age: 25}
     */
    let parse = function(params) {
        try {
            return JSON.parse(params);
        } catch (e) {
            return JSON.stringify(params);
        }
    }

    /* ==============================================================================================================
                    Field Binding Function Start
       ============================================================================================================== */
    // Exception Mgmt By Group LV4 Combo
    let fn_InitCombobox = function(o9Params){
        printParams(o9Params);
        let parsedParams = parse(o9Params);
        parsedParams.version = parsedParams.fbVersion;
        parsedParams.comboLevel = parsedParams.levelValue;
        parsedParams.levelKey = levelKey;

        log(`JS_MtrlConstraintType > fn_InitCombobox : ${parse(parsedParams)}`);
        let queryResult;

        switch (parsedParams.levelValue) {
            case comboLevelArr[0]:
                queryResult = QueryCommon.selectMtrlConstMetrialLevel1List(parsedParams);
                break;

            case comboLevelArr[1]:
                queryResult = QueryCommon.selectMtrlConstMetrialLevel2List(parsedParams);
                break;

            case comboLevelArr[2]:
                queryResult = QueryCommon.selectMtrlConstMetrialLevel3List(parsedParams);
                break;

            case comboLevelArr[3]:
                queryResult = QueryCommon.selectMtrlConstMetrialLevel4List(parsedParams);
                break;

            case comboLevelArr[4]:
                queryResult = QueryCommon.selectMtrlConstMetrialLevel5List(parsedParams);
                break;

            case comboLevelArr[5]:
                queryResult = QueryCommon.selectMeterialCodeList(parsedParams);
                break;

            default:
                queryResult = QueryCommon.selectMtrlConstMetrialLevel1List(parsedParams);
        }

        return Common.fn_comboMake(queryResult, parsedParams);
    }


    let fn_addExcepMgmtLevel4 = function(o9Params){
        printParams(o9Params);
        let parsedParams = parse(o9Params);

        // 예외 건 생성 시, 상단 블록에서 설정한 Small Level 단위와 일치하는지 검증
        let selectResult = QueryCommon.selectExceptionMgmtLevel4(parsedParams);
        let selectResultCount = selectResult.rowCount;

        if (selectResultCount > 0) {
            // 동일등록 건은 없는지 검증
            let queryResult = QueryCommon.selectExceptionMgmtLevel4DuppleCheck(parsedParams);
            let selectResultCount = queryResult.rowCount;
            if (selectResultCount > 0) {
                RuleOutputToUI = { Status : 'Error', Message : "There is registered data." };

            } else {
                // LV4 예외 건 등록
                QueryCommon.executeExceptionMgmtLevel4AddStep1(parsedParams);
                QueryCommon.executeExceptionMgmtLevel4AddStep2(parsedParams);
                QueryCommon.executeExceptionMgmtLevel4AddStep3(parsedParams);
            }

        } else {
            // 상단 블록에서 설정한 Small Level 단위와 불일치 시 리턴
            RuleOutputToUI = { Status : 'Error', Message : "Small Level is inconsistent." };
        }

        vdCommon.programEnd();
    };

    let fn_addExcepMgmtLevel5 = function(o9Params){
        printParams(o9Params);
        let parsedParams = parse(o9Params);

        // 예외 건 생성 시, 상단 블록에서 설정한 Small Level 단위와 일치하는지 검증
        let queryResult = QueryCommon.selectExceptionMgmtLevel5(parsedParams);
        let selectResultCount = queryResult.rowCount;

        if (selectResultCount > 0) {
            // 동일등록 건은 없는지 검증
            let queryResult = QueryCommon.selectExceptionMgmtLevel5DuppleCheck(parsedParams);
            let selectResultCount = queryResult.rowCount;
            if (selectResultCount > 0) {
                RuleOutputToUI = { Status : 'Error', Message : "There is registered data." };

            } else {
                // LV5 예외 건 등록
                QueryCommon.executeExceptionMgmtLevel5AddStep1(parsedParams);
                QueryCommon.executeExceptionMgmtLevel5AddStep2(parsedParams);
                QueryCommon.executeExceptionMgmtLevel5AddStep3(parsedParams);
            }

        } else {
            // 상단 블록에서 설정한 Small Level 단위와 불일치 시 리턴
            RuleOutputToUI = { Status : 'Error', Message : "Small Level is inconsistent." };
        }

        vdCommon.programEnd();
    };

    let fn_addExcepMgmtByItem = function(o9Params){
        printParams(o9Params);
        let parsedParams = parse(o9Params);

        let allCheckVaild = false;

        // Field Binding Set
        let fbLV1 = parsedParams.fbLV1;
        let fbLV2 = parsedParams.fbLV2;
        let fbLV3 = parsedParams.fbLV3;
        let fbLV4 = parsedParams.fbLV4;
        let fbLV5 = parsedParams.fbLV5;

        if (fbLV1 === "ALL" && fbLV2 === "ALL" && fbLV3 === "ALL" && fbLV4 === "ALL" && fbLV5 === "ALL" ) {
            allCheckVaild = true;
        }

        // 예외 건 생성 시, 상단 블록에서 설정한 Small Level "-" 단위와 일치하는지, 동일등록 건은 없는지 검증
        let queryResult = QueryCommon.selectExceptionMgmtItems(parsedParams);
        let selectResultCount = queryResult.rowCount;

        if (allCheckVaild) {
            selectResultCount = 1;
        }

        if (selectResultCount > 0) {
            // 등록되어진 Meterial Code 인지 확인
            let queryResult = QueryCommon.selectMeterialCodeIsCheck(parsedParams);
            let selectResultCount = queryResult.rowCount;

            if (selectResultCount > 0) {
                if (allCheckVaild) {
                    // Meterial Codel 입력 시 LV관련 값이 ALL 일 경우 입력된 Meterial Code에 맞는 LV를 조회
                    let queryResult = QueryCommon.selectMeterialCodeLevelInfo(parsedParams);
                    let selectResult = queryResult.cs;

                    parsedParams.fbLV1 = selectResult.row(0).cell(selectResult.memberColumnIndex('Item Material', 'MSL1')).Name;
                    parsedParams.fbLV2 = selectResult.row(0).cell(selectResult.memberColumnIndex('Item Material', 'MSL2')).Name;
                    parsedParams.fbLV3 = selectResult.row(0).cell(selectResult.memberColumnIndex('Item Material', 'MSL3')).Name;
                    parsedParams.fbLV4 = selectResult.row(0).cell(selectResult.memberColumnIndex('Item Material', 'MSL4')).Name;
                    parsedParams.fbLV5 = selectResult.row(0).cell(selectResult.memberColumnIndex('Item Material', 'MSL5')).Name;
                }

                // Exception Mgmt by Item 예외 건 등록
                QueryCommon.executeExceptionMgmtItemsAddStep1(parsedParams);
                QueryCommon.executeExceptionMgmtItemsAddStep2(parsedParams);
                QueryCommon.executeExceptionMgmtItemsAddStep3(parsedParams);

            } else {
                RuleOutputToUI = { Status : 'Error', Message : "Unregistered Material Code." };
            }

        } else {
            // 상단 블록에서 설정한 Small Level 단위와 불일치 시 리턴
            RuleOutputToUI = { Status : 'Error', Message : "Small Level is inconsistent." };
        }

        vdCommon.programEnd();
    };

    let fn_isVaild = function(o9Params){
        printParams(o9Params);
        let parsedParams = parse(o9Params);
        parsedParams.limitCount = 5;
        parsedParams.fbItemSelectTupleSize = parsedParams.fbItemSelectTuple.length;
        log("fn_isVaild > parsedParams.fbItemSelectTuple : " + parsedParams.fbItemSelectTuple);
        log("fn_isVaild > parsedParams.fbItemSelectTupleSize : " + parsedParams.fbItemSelectTupleSize);

        if (!Common.fn_limitSelectCheckBoxCountCheck(parsedParams)) {
            RuleOutputToUI = { Status : 'Error', Message : "Please select less than 5." };
        }

        if (parsedParams.fbIsVaildType === "Y") {
            // executeQuery는 Designer IBPL 에 있음

        } else {
            let tupleItemList = parsedParams.fbItemSelectTuple;
            log("fn_isVaildN > tupleItemList : " + JSON.stringify(tupleItemList));

            for (let i=0; i < parsedParams.fbItemSelectTupleSize; i++) {
                const item = tupleItemList[i];

                switch (parsedParams.fbVaildBtnLv) {
                    case "LV3":
                        parsedParams.fbLV3 = item.LV3.Value;

                        QueryCommon.executeExceptionMgmtLV3VaildNProcStep1(parsedParams);
                        QueryCommon.executeExceptionMgmtLV3VaildNProcStep2(parsedParams);
                        QueryCommon.executeExceptionMgmtLV3VaildNProcStep3(parsedParams);
                        break;

                    case "LV4":
                        parsedParams.fbLV4 = item.LV4.Value;

                        QueryCommon.executeExceptionMgmtLV4VaildNProcStep1(parsedParams);
                        QueryCommon.executeExceptionMgmtLV4VaildNProcStep2(parsedParams);
                        QueryCommon.executeExceptionMgmtLV4VaildNProcStep3(parsedParams);
                        break;

                    case "LV5":
                        parsedParams.fbLV5 = item.LV5.Value;

                        QueryCommon.executeExceptionMgmtLV5VaildNProcStep1(parsedParams);
                        QueryCommon.executeExceptionMgmtLV5VaildNProcStep2(parsedParams);
                        QueryCommon.executeExceptionMgmtLV5VaildNProcStep3(parsedParams);
                        break;

                    case "ITEM":
                        parsedParams.fbLV5 = item.LV5.Value;
                        parsedParams.fbMeterial = item.Material.Value;
                        parsedParams.fbLocation = item.Plant.Value;

                        QueryCommon.executeExceptionMgmtItemVaildNProcStep1(parsedParams);
                        QueryCommon.executeExceptionMgmtItemVaildNProcStep2(parsedParams);
                        QueryCommon.executeExceptionMgmtItemVaildNProcStep3(parsedParams);
                        break;

                    default:
                }
            }
        }

        vdCommon.programEnd();
    };




    let fn_SmallLVSet = function(o9Params){
        printParams(o9Params);
        let parsedParams = parse(o9Params);
        parsedParams.limitCount = 5;
        parsedParams.fbItemSelectTupleSize = parsedParams.fbItemSelectTuple.length;
        log("fn_SmallLVSet > parsedParams.fbItemSelectTuple : " + parsedParams.fbItemSelectTuple);
        log("fn_SmallLVSet > parsedParams.fbItemSelectTupleSize : " + parsedParams.fbItemSelectTupleSize);

        if (!Common.fn_limitSelectCheckBoxCountCheck(parsedParams)) {
            RuleOutputToUI = { Status : 'Error', Message : "Please select less than 5." };

        } else {
            let tupleItemList = parsedParams.fbItemSelectTuple;
            log("fn_level3VaildIsN > tupleItemList : " + JSON.stringify(tupleItemList));

            for (let i=0; i < parsedParams.fbItemSelectTupleSize; i++) {
                const item = tupleItemList[i];
                parsedParams.fbLV1 = item.LV1.Value;
                parsedParams.fbLV2 = item.LV2.Value;
                parsedParams.fbLV3 = item.LV3.Value;


                let queryResult = QueryCommon.selectSmallLVLevel(parsedParams);
                let selectResultCount = queryResult.rowCount;
                if (selectResultCount > 0) {
                    let itemInfo = `(${parsedParams.fbLV1} | ${parsedParams.fbLV2} | ${parsedParams.fbLV3})It does not fit level.`;
                    RuleOutputToUI = { Status : 'Error', Message : itemInfo };
                    break;
                }
            }

            // executeQuery는 Designer IBPL 에 있음
        }
        vdCommon.programEnd();
    };

    let fn_selectCheckBoxCheck = function(o9Params){
        printParams(o9Params);
        let parsedParams = parse(o9Params);
        parsedParams.limitCount = 5;
        parsedParams.fbItemSelectTupleSize = parsedParams.fbItemSelectTuple.length;
        log("fn_selectCheckBoxCheck > parsedParams.fbItemSelectTuple : " + parsedParams.fbItemSelectTuple);
        log("fn_selectCheckBoxCheck > parsedParams.fbItemSelectTupleSize : " + parsedParams.fbItemSelectTupleSize);

        if (!Common.fn_limitSelectCheckBoxCountCheck(parsedParams)) {
            RuleOutputToUI = { Status : 'Error', Message : "Please select less than 5." };
        }

        vdCommon.programEnd();
    };
    /* ==============================================================================================================
                    Field Binding Function End
       ============================================================================================================== */





    /* ==============================================================================================================
                    내부 Common Function Start
       ============================================================================================================== */
    /**
     * Represents a Common utility class.
     */
    class Common {
        /**
         * Creates a combo list based on a query and parsed parameters.
         *
         * @param {object} queryResult - The query object containing the select results.
         * @param {object} parsedParams - The parsed parameters object.
         * @returns {array} - An array containing the combo list.
         */
        static fn_comboMake(queryResult, parsedParams) {
            let selectResult = queryResult.cs;
            let selectResultCount = queryResult.rowCount;

            let comboList = [];
            let validHashMap = new Map();
            let allCheck = parsedParams.allCheck;

            if (allCheck === "Y") {
                comboList.push({ ValueName: "ALL", DisplayName: "ALL" });
            }

            for (let i = 0; i < selectResultCount; i++) {
                const comboData = selectResult.row(i).cell(selectResult.memberColumnIndex(
                    parsedParams.levelKey, parsedParams.levelValue)).Name;

                if (!validHashMap.has(comboData)) {
                    let displayName = comboData;
                    let valueName = comboData;
                    if ( parsedParams.levelValue === "MSL4" || parsedParams.levelValue === "MSL5") {
                        let lastUnderscoreIndex = comboData.lastIndexOf("_");
                        displayName = comboData.substring(lastUnderscoreIndex + 1);
                    }
                    comboList.push({ ValueName: valueName, DisplayName: displayName });
                    validHashMap.set(comboData, comboData);
                }
            }

            return comboList;
        }

        /**
         * Checks if the number of selected checkboxes is within the specified limit.
         *
         * @param {object} parsedParams - The parsed parameters.
         * @param {number} parsedParams.fbItemSelectTupleSize - The number of selected checkboxes.
         * @param {number} parsedParams.limitCount - The limit count for selected checkboxes.
         *
         * @returns {boolean} - Returns true if the number of selected checkboxes is within the limit, otherwise false.
         */
        static fn_limitSelectCheckBoxCountCheck(parsedParams){
            let returnValue = true;
            if (parsedParams.fbItemSelectTupleSize > parsedParams.limitCount) {
                returnValue = false;
            }
            return returnValue;
        }
    }
    /* ==============================================================================================================
                    내부 Common Function End
       ============================================================================================================== */




    /* ==============================================================================================================
                    내부 Query Function Start
       ============================================================================================================== */
    class QueryCommon {
        static selectMtrlConstMetrialLevel1List(parsedParams) {
            let query = `
                select (
                    [Version].[Version Name].[CurrentWorkingView] * [Item Material].[MSL1] * [Item Material].[MSL2] * [Item Material].[MSL3]
                ) on row, ({Measure.[Mtrl Const Type L3_Sub Set]})
                on column.filter(Measure.[Mtrl Const Type L3_Sub Set] == "${parsedParams.smallLevel}");
            `;
            return vdCommon.selectQueryList('selectMtrlConstMetrialLevel1List', query);
        }

        static selectMtrlConstMetrialLevel2List(parsedParams) {
            let query = `
                select (
                    [Version].[Version Name].[CurrentWorkingView] * [Item Material].[MSL1] * [Item Material].[MSL2] * [Item Material].[MSL3]
                ) on row, ({Measure.[Mtrl Const Type L3_Sub Set]})
                on column where {
                      [Item Material].[MSL1].filter(#.Name == "${parsedParams.fbLV1}")
                    , Measure.[Mtrl Const Type L3_Sub Set] == "${parsedParams.smallLevel}"
                };
            `;
            return vdCommon.selectQueryList('selectMtrlConstMetrialLevel2List', query);
        }

        static selectMtrlConstMetrialLevel3List(parsedParams) {
            let query = `
                select (
                    [Version].[Version Name].[CurrentWorkingView] * [Item Material].[MSL1] * [Item Material].[MSL2] * [Item Material].[MSL3]
                ) on row, ({Measure.[Mtrl Const Type L3_Sub Set]})
                on column where {
                      [Item Material].[MSL1].filter(#.Name == "${parsedParams.fbLV1}")
                    , [Item Material].[MSL2].filter(#.Name == "${parsedParams.fbLV2}")
                    , Measure.[Mtrl Const Type L3_Sub Set] == "${parsedParams.smallLevel}"
                };
            `;
            return vdCommon.selectQueryList('selectMtrlConstMetrialLevel3List', query);
        }

        static selectMtrlConstMetrialLevel4List(parsedParams) {
            let query = `
                select (
                    [Item Material].[MSL4] * [Item Material].[MSL4 Name]
                ) on row, ()
                on column where {
                      [Item Material].[MSL1].filter(#.Name == "${parsedParams.fbLV1}")
                    , [Item Material].[MSL2].filter(#.Name == "${parsedParams.fbLV2}")
                    , [Item Material].[MSL3].filter(#.Name == "${parsedParams.fbLV3}")
                };
            `;
            return vdCommon.selectQueryList('selectMtrlConstMetrialLevel4List', query);
        }

        static selectMtrlConstMetrialLevel5List(parsedParams) {
            let query = `
                select (
                    [Item Material].[MSL5] * [Item Material].[MSL5 Name]
                ) on row, ()
                on column where {
                      [Item Material].[MSL1].filter(#.Name == "${parsedParams.fbLV1}")
                    , [Item Material].[MSL2].filter(#.Name == "${parsedParams.fbLV2}")
                    , [Item Material].[MSL3].filter(#.Name == "${parsedParams.fbLV3}")
                    , [Item Material].[MSL4].filter(#.Name == "${parsedParams.fbLV4}")
                };
            `;
            return vdCommon.selectQueryList('selectMtrlConstMetrialLevel5List', query);
        }

        static selectMeterialCodeList(parsedParams) {
            let query = `
                select (
                    [Item Material].[Item Material]
                ) on row, ()
                on column where {
                      [Item Material].[MSL1].filter(#.Name == "${parsedParams.fbLV1}")
                    , [Item Material].[MSL2].filter(#.Name == "${parsedParams.fbLV2}")
                    , [Item Material].[MSL3].filter(#.Name == "${parsedParams.fbLV3}")
                    , [Item Material].[MSL4].filter(#.Name == "${parsedParams.fbLV4}")
                    , [Item Material].[MSL5].filter(#.Name == "${parsedParams.fbLV5}")
                };
            `;
            return vdCommon.selectQueryList('selectMeterialCodeList', query);
        }

        static selectExceptionMgmtLevel4(parsedParams) {
            let query = `
                Select
                    (
                          [Version].[Version Name].[${parsedParams.fbVersion}]
                        * [Item Material].[MSL1].filter(#.Name == "${parsedParams.fbLV1}") 
                        * [Item Material].[MSL2].filter(#.Name == "${parsedParams.fbLV2}") 
                        * [Item Material].[MSL3].filter(#.Name == "${parsedParams.fbLV3}") 
                    ) on row, 
                    ({
                          Measure.[Mtrl Const Type L4_Valid Flag]
                        , Measure.[Mtrl Const Type L4_ETDETA]
                        , Measure.[Mtrl Const Type L3_Sub Set]
                    })
                    on column where {
                          Measure.[Mtrl Const Type L4 W_Type] == "${parsedParams.fbConstraintType}" 
                        , Measure.[Mtrl Const Type L3_Sub Set] == "LV4"
                    };
            `;
            return vdCommon.selectQueryList('selectExceptionMgmtLevel4', query);
        }

        static selectExceptionMgmtLevel4DuppleCheck(parsedParams) {
            let query = `
                Select
                    (
                          [Version].[Version Name].[${parsedParams.fbVersion}]
                        * [Item Material].[MSL1].filter(#.Name == "${parsedParams.fbLV1}") 
                        * [Item Material].[MSL2].filter(#.Name == "${parsedParams.fbLV2}") 
                        * [Item Material].[MSL3].filter(#.Name == "${parsedParams.fbLV3}") 
                        * [Item Material].[MSL4].filter(#.Name == "${parsedParams.fbLV4}")
                    ) on row,
                    ({
                          Measure.[Mtrl Const Type L4_Valid Flag]
                        , Measure.[Mtrl Const Type L4_ETDETA]
                        , Measure.[Mtrl Const Type L3_Sub Set]

                    })
                    on column where {
                        Measure.[Mtrl Const Type L3_Sub Set] == "LV4"
                    };
            `;
            return vdCommon.selectQueryList('selectExceptionMgmtLevel4DuppleCheck', query);
        }




        static executeExceptionMgmtLevel4AddStep1(parsedParams) {
            let query = `
                cartesian scope:
                    (
                          [Version].[Version Name].[${parsedParams.fbVersion}]
                        * [Item Material].[MSL3].[${parsedParams.fbLV3}] 
                        * [Item Material].[MSL4].[${parsedParams.fbLV4}]
                    );
                    Measure.[Mtrl Const Type L4_ETDETA] = "ETD";
                    Measure.[Mtrl Const Type L4_Valid Flag] = "Y";
                    Measure.[Mtrl Const Type L4_Updated By] = null;
                    Measure.[Mtrl Const Type L4_Update Time] = null;
                    Measure.[Mtrl Const Type L4_Created By] = Currentuser().Name;
                    Measure.[Mtrl Const Type L4_Creation Time] = Now();
                end scope;
            `;
            return vdCommon.executeQuery('executeExceptionMgmtLevel4AddStep1', query);
        }

        static executeExceptionMgmtLevel4AddStep2(parsedParams) {
            let query = `
                cartesian scope:
                    (
                          [Version].[Version Name].[${parsedParams.fbVersion}]
                        * [Item Material].[MSL3].[${parsedParams.fbLV3}] 
                    );
                    Measure.[Mtrl Const Type L3_Sub Set] = "LV4";
                end scope;
            `;
            return vdCommon.executeQuery('executeExceptionMgmtLevel4AddStep2', query);
        }

        static executeExceptionMgmtLevel4AddStep3(parsedParams) {
            let query = `
                cartesian scope:
                    (
                          [Version].[Version Name].[${parsedParams.fbVersion}]
                        * [Item Material].[MSL4].[${parsedParams.fbLV4}]
                        * [zzTime].[zzRelative_Week]
                    );
                    Measure.[Mtrl Const Type L4 W_Type] = "${parsedParams.fbConstraintType}";
                    Measure.[Mtrl Const Type L4 W_Lock Flag] = True;
                end scope;
            `;
            return vdCommon.executeQuery('executeExceptionMgmtLevel4AddStep3', query);
        }




        static selectExceptionMgmtLevel5(parsedParams) {
            let query = `
                Select
                (
                      [Version].[Version Name].[${parsedParams.fbVersion}]
                    * [Item Material].[MSL1].filter(#.Name == "${parsedParams.fbLV1}") 
                    * [Item Material].[MSL2].filter(#.Name == "${parsedParams.fbLV2}") 
                    * [Item Material].[MSL3].filter(#.Name == "${parsedParams.fbLV3}") 
                    * [Item Material].[MSL4].filter(#.Name == "${parsedParams.fbLV4}")
                ) on row, 
                ({
                      Measure.[Mtrl Const Type L5_Valid Flag]
                    , Measure.[Mtrl Const Type L5_ETDETA]
                    , Measure.[Mtrl Const Type L3_Sub Set]
                })
                on column where {
                      Measure.[Mtrl Const Type L5 W_Type] == "${parsedParams.fbConstraintType}" 
                    , Measure.[Mtrl Const Type L3_Sub Set] == "LV5"
                };
            `;
            return vdCommon.selectQueryList('selectExceptionMgmtLevel5', query);
        }

        static selectExceptionMgmtLevel5DuppleCheck(parsedParams) {
            let query = `
                Select
                    (
                          [Version].[Version Name].[${parsedParams.fbVersion}]
                        * [Item Material].[MSL1].filter(#.Name == "${parsedParams.fbLV1}") 
                        * [Item Material].[MSL2].filter(#.Name == "${parsedParams.fbLV2}") 
                        * [Item Material].[MSL3].filter(#.Name == "${parsedParams.fbLV3}") 
                        * [Item Material].[MSL4].filter(#.Name == "${parsedParams.fbLV4}")
                        * [Item Material].[MSL5].filter(#.Name == "${parsedParams.fbLV5}")
                    ) on row,
                    ({
                          Measure.[Mtrl Const Type L5_Valid Flag]
                        , Measure.[Mtrl Const Type L5_ETDETA]
                        , Measure.[Mtrl Const Type L3_Sub Set]

                    })
                    on column where {
                          Measure.[Mtrl Const Type L5 W_Type] == "${parsedParams.fbConstraintType}" 
                        , Measure.[Mtrl Const Type L3_Sub Set] == "LV5"
                    };
            `;
            return vdCommon.selectQueryList('selectExceptionMgmtLevel5DuppleCheck', query);
        }




        static executeExceptionMgmtLevel5AddStep1(parsedParams) {
            let query = `
                cartesian scope:
                    (
                          [Version].[Version Name].[${parsedParams.fbVersion}]
                        * [Item Material].[MSL3].[${parsedParams.fbLV3}] 
                        * [Item Material].[MSL4].[${parsedParams.fbLV4}]
                        * [Item Material].[MSL5].[${parsedParams.fbLV5}]
                    );
                    Measure.[Mtrl Const Type L5_ETDETA] = "ETD";
                    Measure.[Mtrl Const Type L5_Valid Flag] = "Y";
                    Measure.[Mtrl Const Type L5_Updated By] = null;
                    Measure.[Mtrl Const Type L5_Update Time] = null;
                    Measure.[Mtrl Const Type L5_Created By] = Currentuser().Name;
                    Measure.[Mtrl Const Type L5_Creation Time] = Now();
                end scope;
            `;
            return vdCommon.executeQuery('executeExceptionMgmtLevel5AddStep1', query);
        }

        static executeExceptionMgmtLevel5AddStep2(parsedParams) {
            let query = `
                cartesian scope:
                    (
                          [Version].[Version Name].[${parsedParams.fbVersion}]
                        * [Item Material].[MSL3].[${parsedParams.fbLV3}] 
                    );
                    Measure.[Mtrl Const Type L3_Sub Set] = "LV5";
                end scope;
            `;
            return vdCommon.executeQuery('executeExceptionMgmtLevel5AddStep2', query);
        }

        static executeExceptionMgmtLevel5AddStep3(parsedParams) {
            let query = `
                cartesian scope:
                    (
                          [Version].[Version Name].[${parsedParams.fbVersion}]
                        * [Item Material].[MSL3].[${parsedParams.fbLV3}]
                        * [Item Material].[MSL4].[${parsedParams.fbLV4}]
                        * [Item Material].[MSL5].[${parsedParams.fbLV5}]
                        * [zzTime].[zzRelative_Week]
                    );
                    Measure.[Mtrl Const Type L5 W_Type] = "${parsedParams.fbConstraintType}";
                    Measure.[Mtrl Const Type L5 W_Lock Flag] = True;
                end scope;
            `;
            return vdCommon.executeQuery('executeExceptionMgmtLevel5AddStep3', query);
        }




        static selectExceptionMgmtItems(parsedParams) {
            let query = `
                Select
                (
                      [Version].[Version Name].[${parsedParams.fbVersion}]
                    * [Item Material].[MSL1].filter(#.Name == "${parsedParams.fbLV1}") 
                    * [Item Material].[MSL2].filter(#.Name == "${parsedParams.fbLV2}") 
                    * [Item Material].[MSL3].filter(#.Name == "${parsedParams.fbLV3}") 
                ) on row, 
                ({
                      Measure.[Mtrl Const Type Item_Valid Flag]
                    , Measure.[Mtrl Const Type Item_ETDETA]
                    , Measure.[Mtrl Const Type L3_Sub Set]
                })
                on column where {
                      Measure.[Mtrl Const Type L3_Sub Set] == "-"
                };
            `;
            return vdCommon.selectQueryList('selectExceptionMgmtItems', query);
        }

        static selectMeterialCodeIsCheck(parsedParams) {
            let query = `
                Select (
                    [Item Material].[Item Material].filter(#.Name == "${parsedParams.fbMeterialCode}") 
                ) on row;
            `;
            return vdCommon.selectQueryList('selectMeterialCodeIsCheck', query);
        }

        static selectMeterialCodeLevelInfo(parsedParams) {
            let query = `
                select (
                      [Item Material].[MSL1] 
                    * [Item Material].[MSL2] 
                    * [Item Material].[MSL3] 
                    * [Item Material].[MSL4] 
                    * [Item Material].[MSL5]
                ) on row, ()
                on column where {
                      [Item Material].[Item Material].filter(#.Name == "${parsedParams.fbMeterialCode}")
                };
            `;
            return vdCommon.selectQueryList('selectMeterialCodeLevelInfo', query);
        }




        static executeExceptionMgmtItemsAddStep1(parsedParams) {
            let query = `
                cartesian scope:
                    (
                          [Version].[Version Name].[${parsedParams.fbVersion}]
                        * [Item Material].[MSL1].[${parsedParams.fbLV1}] 
                        * [Item Material].[MSL2].[${parsedParams.fbLV2}]
                        * [Item Material].[MSL3].[${parsedParams.fbLV3}] 
                        * [Item Material].[MSL4].[${parsedParams.fbLV4}]
                        * [Item Material].[MSL5].[${parsedParams.fbLV5}]
                        * [Item Material].[Item Material].[${parsedParams.fbMeterialCode}]
                        * [Location].[Location].[${parsedParams.fbPlant}]
                    );
                    Measure.[Mtrl Const Type Item_ETDETA] = "ETD";
                    Measure.[Mtrl Const Type Item_Lock Flag] = "Y";
                    Measure.[Mtrl Const Type Item_Valid Flag] = "Y";
                    Measure.[Mtrl Const Type Item_Created By] = Currentuser().Name;
                    Measure.[Mtrl Const Type Item_Creation Time] = Now();
                    Measure.[Mtrl Const Type Item_ASN] = 1;
                end scope;
            `;
            return vdCommon.executeQuery('executeExceptionMgmtItemsAddStep1', query);
        }

        static executeExceptionMgmtItemsAddStep2(parsedParams) {
            let query = `
                cartesian scope:
                    (
                          [Version].[Version Name].[${parsedParams.fbVersion}]
                        * [Item Material].[MSL1].[${parsedParams.fbLV1}] 
                        * [Item Material].[MSL2].[${parsedParams.fbLV2}]
                        * [Item Material].[MSL3].[${parsedParams.fbLV3}] 
                        * [Item Material].[MSL4].[${parsedParams.fbLV4}]
                        * [Item Material].[MSL5].[${parsedParams.fbLV5}]
                        * [Item Material].[Item Material].[${parsedParams.fbMeterialCode}]
                        * [Location].[Location].[${parsedParams.fbPlant}]
                        * [zzTime].[zzRelative_Week] 
                    );
                    Measure.[Mtrl Const Type Item W_Type] = "${parsedParams.fbConstraintType}";
                end scope;
            `;
            return vdCommon.executeQuery('executeExceptionMgmtItemsAddStep2', query);
        }

        static executeExceptionMgmtItemsAddStep3(parsedParams) {
            let query = `
                cartesian scope:
                    (
                          [Version].[Version Name].[${parsedParams.fbVersion}]
                        * [Item Material].[MSL3].[${parsedParams.fbLV3}]
                    );
                    Measure.[Mtrl Const Type L3_Sub Set] = "-";
                end scope;
            `;
            return vdCommon.executeQuery('executeExceptionMgmtItemsAddStep3', query);
        }




        static executeExceptionMgmtLV3VaildNProcStep1(parsedParams) {
            let query = `
                cartesian scope:
                    (
                          [Version].[Version Name].[${parsedParams.fbVersion}] 
                        * [Item Material].[MSL3].[${parsedParams.fbLV3}]
                    );
                    Measure.[Mtrl Const Type L3_Time Varying Flag] = "Y";
                end scope;
                
                cartesian scope:
                    (
                          [Version].[Version Name].[${parsedParams.fbVersion}] 
                        * zzTime.[zzRelative_Week]
                        * [Item Material].[MSL3].[${parsedParams.fbLV3}]
                    );
                    Measure.[Mtrl Const Type L3 W_Type.Lock] = False;
                end scope;
            `;
            return vdCommon.executeQuery('executeExceptionMgmtLV3VaildNProcStep1', query);
        }

        static executeExceptionMgmtLV3VaildNProcStep2(parsedParams) {
            let query = `
                cartesian scope:
                    (
                          [Version].[Version Name].[${parsedParams.fbVersion}] 
                        * [Item Material].[MSL3].[${parsedParams.fbLV3}]
                        * [zzTime].[zzRelative_Week].[W01]
                    );
                    Measure.[Mtrl Const Type L3 W_Type] = "Soft";
                end scope;
                
                cartesian scope:
                    (
                          [Version].[Version Name].[${parsedParams.fbVersion}] 
                        * [Item Material].[MSL3].[${parsedParams.fbLV3}]
                        * [zzTime].[zzRelative_Week].filter(#.Name != "W01")
                    );
                    
                    Measure.[Mtrl Const Type L3 W_Type] = "-";
                end scope;
            `;
            return vdCommon.executeQuery('executeExceptionMgmtLV3VaildNProcStep2', query);
        }

        static executeExceptionMgmtLV3VaildNProcStep3(parsedParams) {
            let query = `
                cartesian scope:
                    (
                          [Version].[Version Name].[${parsedParams.fbVersion}] 
                        * [Item Material].[MSL3].[${parsedParams.fbLV3}]
                    );
                    Measure.[Mtrl Const Type L3_Time Varying Flag] = "N";
                end scope;
                
                cartesian scope:
                    (
                          [Version].[Version Name].[${parsedParams.fbVersion}]
                        * [Item Material].[MSL3].[${parsedParams.fbLV3}]
                        * [zzTime].[zzRelative_Week].filter(#.Name != "W01")
                    );
                    Measure.[Mtrl Const Type L3 W_Type.Lock] = True;
                end scope;
            `;
            return vdCommon.executeQuery('executeExceptionMgmtLV3VaildNProcStep2', query);
        }






        static executeExceptionMgmtLV4VaildNProcStep1(parsedParams) {
            let query = `
                cartesian scope:
                    (
                          Version.[Version Name].[${parsedParams.fbVersion}] 
                        * [Item Material].[MSL4].[${parsedParams.fbLV4}]
                    );
                    Measure.[Mtrl Const Type L4_Valid Flag] = "Y";
                end scope;
                
                cartesian scope:
                    (
                          [Version].[Version Name].[${parsedParams.fbVersion}]
                        * zzTime.[zzRelative_Week] 
                        * [Item Material].[MSL4].[${parsedParams.fbLV4}]
                    );
                    Measure.[Mtrl Const Type L4 W_Type.Lock] = False;
                end scope;
            `;
            return vdCommon.executeQuery('executeExceptionMgmtLV4VaildNProcStep1', query);
        }

        static executeExceptionMgmtLV4VaildNProcStep2(parsedParams) {
            let query = `
                cartesian scope:
                    (
                          [Version].[Version Name].[${parsedParams.fbVersion}] 
                        * [Item Material].[MSL4].[${parsedParams.fbLV4}]
                        * [zzTime].[zzRelative_Week].[W01]
                    );
                    Measure.[Mtrl Const Type L4 W_Type] = "Soft";
                end scope;
                
                cartesian scope:
                    (
                          [Version].[Version Name].[${parsedParams.fbVersion}] 
                        * [Item Material].[MSL4].[${parsedParams.fbLV4}]
                        * [zzTime].[zzRelative_Week].filter(#.Name != "W01")
                    );
                    
                    Measure.[Mtrl Const Type L4 W_Type] = "-";
                end scope;
            `;
            return vdCommon.executeQuery('executeExceptionMgmtLV4VaildNProcStep2', query);
        }

        static executeExceptionMgmtLV4VaildNProcStep3(parsedParams) {
            let query = `
                cartesian scope:
                    (
                          Version.[Version Name].[${parsedParams.fbVersion}] 
                        * [Item Material].[MSL4].[${parsedParams.fbLV4}]
                    );
                    Measure.[Mtrl Const Type L4_Valid Flag] = "N";
                end scope;
                
                cartesian scope:
                    (
                          [Version].[Version Name].[${parsedParams.fbVersion}]
                        * zzTime.[zzRelative_Week] 
                        * [Item Material].[MSL4].[${parsedParams.fbLV4}]
                    );
                    Measure.[Mtrl Const Type L4 W_Type.Lock] = True;
                end scope;
            `;
            return vdCommon.executeQuery('executeExceptionMgmtLV4VaildNProcStep3', query);
        }






        static executeExceptionMgmtLV5VaildNProcStep1(parsedParams) {
            let query = `
                cartesian scope:
                    (
                          Version.[Version Name].[${parsedParams.fbVersion}] 
                        * [Item Material].[MSL5].[${parsedParams.fbLV5}]
                    );
                    Measure.[Mtrl Const Type L5_Valid Flag] = "Y";
                end scope;
                
                cartesian scope:
                    (
                          [Version].[Version Name].[${parsedParams.fbVersion}]
                        * zzTime.[zzRelative_Week] 
                        * [Item Material].[MSL5].[${parsedParams.fbLV5}]
                    );
                    Measure.[Mtrl Const Type L5 W_Type.Lock] = False;
                end scope;
            `;
            return vdCommon.executeQuery('executeExceptionMgmtLV5VaildNProcStep1', query);
        }

        static executeExceptionMgmtLV5VaildNProcStep2(parsedParams) {
            let query = `
                cartesian scope:
                    (
                          [Version].[Version Name].[${parsedParams.fbVersion}] 
                        * [Item Material].[MSL5].[${parsedParams.fbLV5}]
                        * [zzTime].[zzRelative_Week].[W01]
                    );
                    Measure.[Mtrl Const Type L5 W_Type] = "Soft";
                end scope;
                
                cartesian scope:
                    (
                          [Version].[Version Name].[${parsedParams.fbVersion}] 
                        * [Item Material].[MSL5].[${parsedParams.fbLV5}]
                        * [zzTime].[zzRelative_Week].filter(#.Name != "W01")
                    );
                    
                    Measure.[Mtrl Const Type L5 W_Type] = "-";
                end scope;
            `;
            return vdCommon.executeQuery('executeExceptionMgmtLV5VaildNProcStep2', query);
        }

        static executeExceptionMgmtLV5VaildNProcStep3(parsedParams) {
            let query = `
                cartesian scope:
                    (
                          Version.[Version Name].[${parsedParams.fbVersion}] 
                        * [Item Material].[MSL5].[${parsedParams.fbLV5}]
                    );
                    Measure.[Mtrl Const Type L5_Valid Flag] = "N";
                end scope;
                
                cartesian scope:
                    (
                          [Version].[Version Name].[${parsedParams.fbVersion}]
                        * zzTime.[zzRelative_Week] 
                        * [Item Material].[MSL5].[${parsedParams.fbLV5}]
                    );
                    Measure.[Mtrl Const Type L5 W_Type.Lock] = True;
                end scope;
            `;
            return vdCommon.executeQuery('executeExceptionMgmtLV5VaildNProcStep3', query);
        }






        static executeExceptionMgmtItemVaildNProcStep1(parsedParams) {
            let query = `
                cartesian scope:
                    (
                          Version.[Version Name].[${parsedParams.fbVersion}] 
                        * [Item Material].[Item Material].[${parsedParams.fbMeterial}]
                        * [Location].[Location].[${parsedParams.fbLocation}]
                    );
                    Measure.[Mtrl Const Type Item_Valid Flag] = "Y";
                end scope;
                
                cartesian scope:
                    (
                          [Version].[Version Name].[${parsedParams.fbVersion}]
                        * zzTime.[zzRelative_Week] 
                        * [Item Material].[Item Material].[${parsedParams.fbMeterial}]
                        * [Location].[Location].[${parsedParams.fbLocation}]
                    );
                    Measure.[Mtrl Const Type Item W_Type.Lock] = False;
                end scope;
            `;
            return vdCommon.executeQuery('executeExceptionMgmtItemVaildNProcStep1', query);
        }

        static executeExceptionMgmtItemVaildNProcStep2(parsedParams) {
            let query = `
                cartesian scope:
                    (
                          [Version].[Version Name].[${parsedParams.fbVersion}] 
                        * [Item Material].[Item Material].[${parsedParams.fbMeterial}]
                        * [Location].[Location].[${parsedParams.fbLocation}]
                        * [zzTime].[zzRelative_Week].[W01]
                    );
                    Measure.[Mtrl Const Type Item W_Type] = "Soft";
                end scope;
                
                cartesian scope:
                    (
                          [Version].[Version Name].[${parsedParams.fbVersion}] 
                        * [Item Material].[Item Material].[${parsedParams.fbMeterial}]
                        * [Location].[Location].[${parsedParams.fbLocation}]
                        * [zzTime].[zzRelative_Week].filter(#.Name != "W01")
                    );
                    
                    Measure.[Mtrl Const Type Item W_Type] = "-";
                end scope;
            `;
            return vdCommon.executeQuery('executeExceptionMgmtItemVaildNProcStep2', query);
        }

        static executeExceptionMgmtItemVaildNProcStep3(parsedParams) {
            let query = `
                cartesian scope:
                    (
                          Version.[Version Name].[${parsedParams.fbVersion}] 
                        * [Item Material].[Item Material].[${parsedParams.fbMeterial}]
                        * [Location].[Location].[${parsedParams.fbLocation}]
                    );
                    Measure.[Mtrl Const Type Item_Valid Flag] = "N";
                end scope;
                
                cartesian scope:
                    (
                          [Version].[Version Name].[${parsedParams.fbVersion}]
                        * zzTime.[zzRelative_Week] 
                        * [Item Material].[Item Material].[${parsedParams.fbMeterial}]
                        * [Location].[Location].[${parsedParams.fbLocation}]
                    );
                    Measure.[Mtrl Const Type Item W_Type.Lock] = True;
                end scope;
            `;
            return vdCommon.executeQuery('executeExceptionMgmtItemVaildNProcStep3', query);
        }





        static selectSmallLVLevel(parsedParams) {
            let query = `
                select (
                      [Version].[Version Name].[${parsedParams.fbVersion}]
                    * [Item Material].[MSL1].[${parsedParams.fbLV1}]
                    * [Item Material].[MSL2].[${parsedParams.fbLV2}]
                    * [Item Material].[MSL3].[${parsedParams.fbLV3}]
                ) on row, ()
                on column where {
                    Measure.[Mtrl Const Type L3_Sub Set] == "${parsedParams.fbLevelDepth}"
                };
            `;
            return vdCommon.selectQueryList('selectSmallLVLevel', query);
        }
    }
    /* ==============================================================================================================
                    내부 Query Function End
       ============================================================================================================== */


    return {
          fn_InitCombobox : fn_InitCombobox

        , fn_addExcepMgmtLevel4 : fn_addExcepMgmtLevel4
        , fn_addExcepMgmtLevel5 : fn_addExcepMgmtLevel5
        , fn_addExcepMgmtByItem : fn_addExcepMgmtByItem

        , fn_selectCheckBoxCheck : fn_selectCheckBoxCheck
        , fn_isVaild : fn_isVaild
        , fn_SmallLVSet : fn_SmallLVSet
    };
});