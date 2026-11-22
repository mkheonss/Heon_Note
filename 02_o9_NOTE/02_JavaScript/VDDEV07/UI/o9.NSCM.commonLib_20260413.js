define('o9.NSCM.commonLib', ['o9/data/query', 'o9/data/cellset'], function () {
    const queryModule = require('o9/data/query');
    const cellsetModule = require('o9/data/cellset');
    const sourceVersion = "2026-03-19";

    class VdCommon {
        constructor(_programName) {
            this.programName = _programName;
            this.preFix = "[NSCM-Javascript-LOG]";
            this.errorPreFix = "[NSCM-Javascript-LOG-ERROR]";
            this.setLogLevel("Info");

            this.startTime = new Date();
            this.stepTime = this.startTime;

            this.vdUtil = new VdUtil();

            // 26.1.13 Javascript 로그를 남기는 로직 추가. EW Api 의 fn_loadFunction 호출시만 남긴다.
            this.logParams;
            var pos = _programName.lastIndexOf(".");
            this.logProgram = _programName.substring(0, pos);
            this.logFunction = _programName.substring(pos + 1);
            this.logParams = "";
            this.logEwFuncName = "";
            this.logEwParams = "";
            this.logEwFilters = "";
            this.logEwGridRows = "";
            this.logEwReportName = "";
            this.logEwMenuName = "";

            // 지워야함....
            this.division = "";

            this.programStart();
        }
        logLevelToInt(logLevel) {
            var levelMap = {"Debug" : 1, "Info" : 2, "Warn" : 3, "Error" : 4};
            return levelMap[logLevel];
        }
        setLogLevel(logLevel) {
            this.logLevel = this.logLevelToInt(logLevel);
        }
        debug(msg) {
            this.print(msg, "Debug");
        }
        info(msg) {
            this.print(msg, "Info");
        }
        warn(msg) {
            this.print(msg, "Warn");
        }
        error(msg) {
            this.createJavascriptLog(msg);

            this.print(msg, "Error");
        }
        timeLog() {
            this.print("Time Log", "Debug");
        }
        print(msg, logLevel) {
            // 시간 로그를 남김
            var nowTime = new Date();
            var timeStr = Math.floor((nowTime - this.stepTime) / 1000) + " s, " + Math.floor((nowTime - this.startTime) / 1000) + " s";
            this.stepTime = nowTime;

            if ( this.logLevelToInt(logLevel) >= this.logLevel) {
                if ( this.logLevelToInt(logLevel) == 4 ) {
                    Log.Error(this.errorPreFix + "[" + this.programName + "]" + "[" + logLevel + "]" + "[" + timeStr + "]" + " ===> " + msg);
                } else {
                    Log.Info(this.preFix + "[" + this.programName + "]" + "[" + logLevel + "]" + "[" + timeStr + "]" + " ===> " + msg);
                }
            }
        }
        printParams(params) {
            var p;
            if ( typeof(params) == "string" ) {
                p = JSON.parse(params);
            } else {
                p = params;
            }

            this.debug("O9 Params : " + JSON.stringify(p));

            // 복사를 한다.
            var wParams = JSON.parse(JSON.stringify(p));

            // 26.1.13 로그를 남길 데이타 생성
            // 필요없는 변수 삭제
            delete wParams["RuleOutputToUI"];

            // limit 는 숫자를 문자로 변환하기 때문에 로그를 복사해서 넘길경우 에러가 발생해서 삭제함
            if ( wParams["fbParams"] != undefined ) {
                if ( wParams.fbParams["limit"] != undefined ) {
                    delete wParams.fbParams["limit"];
                }
            }

            // 전체 파라미터를 남김
            this.logParams = JSON.stringify(wParams);

            if ( wParams["fbFuncName"] != undefined )
                this.logEwFuncName = wParams["fbFuncName"];
            if ( wParams["fbParams"] != undefined ) {
                if ( wParams.fbParams["filters"] != undefined ) {
                    this.logEwFilters = JSON.stringify(wParams.fbParams["filters"]);
                    delete wParams.fbParams["filters"];
                }

                if ( wParams.fbParams["menuName"] != undefined ) {
                    this.logEwMenuName = wParams.fbParams["menuName"];
                    delete wParams.fbParams["menuName"];
                }
                if ( wParams.fbParams["reportName"] != undefined ) {
                    this.logEwReportName = wParams.fbParams["reportName"];
                    delete wParams.fbParams["reportName"];
                }

                this.logEwParams = JSON.stringify(wParams["fbParams"]);
            }
            if ( wParams["fbGridRows"] != undefined ) {
                // 26.3.11 여러개의 그리드일 경우 object 로 넘어오기에 배열인지 판단 필요
                if ( Array.isArray(wParams["fbGridRows"]) ) {
                    this.logEwGridRows = JSON.stringify(wParams["fbGridRows"].slice(0,10));
                }
            }
        }
        printStep(msg) {
            this.info("Step : " + msg);
        }
        programStart() {
            if ( this.programName.indexOf("fn_loadFunction") == -1 ) {
                this.info("============== Javasrcipt Start ( Version : " + sourceVersion + " ) ==============");
            }
        }
        programEnd() {
            if ( this.programName.indexOf("fn_loadFunction") == -1 ) {
                this.info("============================ Javasrcipt End ============================");
            }

            this.createJavascriptLog("");
        }

        // 26.1.13 Javascript 로그를 남긴다.
        createJavascriptLog(errorMsg) {
            try {
                var splitStr = "^J:S:L^"

                var division = this.fn_division();
                /*
                if ( this.fn_getDivision != undefined ) {
                    division = this.fn_getDivision();
                }
                // commonLib 를 사용할 경우 개별적으로 지정한 division 을 사용한다. Knox 때문에
                if ( division == "" ) {
                    division = this.division;
                }
                */

                // MG 스키마가 있으면 등록을 한다.  -> 이 로직을 바꾼게 맞을까?
                // var mgCnt = queryModule.select("(SELECT (_SchemaPlan._Plan * _SchemaPlan.[_MeasureGroup].[Javascript Run Log] * _SchemaPlan.[_Measure]) on row, () on column).count;").Result;

                if ( "VD".split(",").includes(division) ) {
                    // commonLib를 상속받은 경우 함수가 없을 수 있어서 체크함
                    var versionName = "[Version].[Version Name].[CurrentWorkingView]";

                    var userName = queryModule.select("SELECT CurrentUser().Name;").Result;

                    var nowTime = new Date();
                    var runTimeStr = Math.floor((nowTime - this.startTime) / 1000);

                    nowTime.setHours(nowTime.getHours() + 9);

                    var day = nowTime.getFullYear() + "-"
                                + this.vdUtil.fn_lpad((nowTime.getMonth() + 1) + "", 2, "0") + "-"
                                + this.vdUtil.fn_lpad(nowTime.getDate() + "", 2, "0");
                    var sequence = nowTime.getHours()
                                        + this.vdUtil.fn_lpad(nowTime.getMinutes() + "", 2, "0")
                                        + this.vdUtil.fn_lpad(nowTime.getSeconds() + "", 2, "0");
                    var sequenceId = nowTime.getMilliseconds();

                    /*
                    this.debug("logProgram : " + this.logProgram);
                    this.debug("logFunction : " + this.logFunction);
                    this.debug("logEwFuncName : " + this.logEwFuncName);
                    this.debug("logEwParams : " + this.logEwParams);
                    this.debug("logEwFilters : " + this.logEwFilters);
                    this.debug("logEwGridRows : " + this.logEwGridRows);
                    this.debug("logParams : " + this.logParams);
                    this.debug("runTimeStr : " + runTimeStr);
                    this.debug("userName : " + userName);
                    this.debug("sequence : " + sequence);
                    this.debug("sequenceId : " + sequenceId);
                    */

                    if ( errorMsg == "" ) {
                        var dimension = [versionName
                                            ,"[Personnel].[Email].[" + userName + "]"
                                            ,"[Time].[Day].[" + day + "]"
                                            ,"[Sequence].[Sequence].[" + sequence + "]"
                                            ,"[Sequence ID].[Sequence ID].[" + sequenceId + "]"];
                        var measureStr = this.vdUtil.fn_getDimensionValue(versionName) + splitStr +
                                        userName + splitStr +
                                        day + splitStr +
                                        sequence + splitStr +
                                        sequenceId + splitStr +
                                        this.logEwMenuName + splitStr +
                                        this.logEwReportName + splitStr +
                                        this.logProgram + splitStr +
                                        this.logFunction + splitStr +
                                        this.logEwFuncName + splitStr +
                                        this.logEwParams.replace(/\"/g, '\\\"') + splitStr +
                                        this.logEwFilters.replace(/\"/g, '\\\"') + splitStr +
                                        this.logEwGridRows.replace(/\"/g, '\\\"') + splitStr +
                                        this.logParams.replace(/\"/g, '\\\"') + splitStr +
                                        runTimeStr;
                        var measure = ['Measure.[Javascript Run Log_Full] = "' + measureStr + '";'];

                        var query = 'cartesian scope:(' + dimension.join('*') + ');' + measure.join(' ') + ' end scope;';
                        //this.debug("Javascript Run Log : " + query);
                        queryModule.update(query);
                    } else {
                        var dimension = [versionName
                                            ,"[Personnel].[Email].[" + userName + "]"
                                            ,"[Time].[Day].[" + day + "]"
                                            ,"[Sequence].[Sequence].[" + sequence + "]"
                                            ,"[Sequence ID].[Sequence ID].[" + sequenceId + "]"];
                        var measureStr = this.vdUtil.fn_getDimensionValue(versionName) + splitStr +
                                        userName + splitStr +
                                        day + splitStr +
                                        sequence + splitStr +
                                        sequenceId + splitStr +
                                        this.logEwMenuName + splitStr +
                                        this.logEwReportName + splitStr +
                                        this.logProgram + splitStr +
                                        this.logFunction + splitStr +
                                        this.logEwFuncName + splitStr +
                                        this.logEwParams.replace(/\"/g, '\\\"') + splitStr +
                                        this.logEwFilters.replace(/\"/g, '\\\"') + splitStr +
                                        this.logEwGridRows.replace(/\"/g, '\\\"') + splitStr +
                                        this.logParams.replace(/\"/g, '\\\"') + splitStr +
                                        runTimeStr + splitStr +
                                        errorMsg;
                        var measure = ['Measure.[Javascript Error Log_Full] = "' + measureStr + '";'];

                        var query = 'cartesian scope:(' + dimension.join('*') + ');' + measure.join(' ') + ' end scope;';
                        //this.debug("Javascript Error Log : " + query);
                        queryModule.update(query);
                    }
                }
            } catch ( e ) {
                this.debug("Error");
            }
        }

        /**
        * 함수 처리 시간를 리턴한다.
        */
        processingTime() {
            var nowTime = new Date();
            var timeStr = Math.floor((nowTime - this.startTime) / 1000);
            return timeStr;
        }

        /**
         * Checks if a member exists in a given dimension.
         *
         * @param {string} dimension - The dimension to search for the member.
         * @param {string} member - The name of the member to check existence for.
         * @returns {boolean} - Returns true if the member exists, false otherwise.
         */
        existMember(dimension, member) {
            try {
                var query = 'Select (' + dimension + '.filter(#.Name=="' + member + '").count);';
                this.debug("Select Query : " + query);
                var returnJson = queryModule.select(query);
                this.debug("Return Json : " + JSON.stringify(returnJson));
                if ( returnJson.Result == 0 ) {
                    return false;
                } else {
                    return true;
                }
            } catch ( e ) {
                this.error(e.message);
                throw e;
            }
        }

        /**
         * Creates a member in a given dimension.
         *
         * @param {string} dimension - The dimension in which the member will be created.
         * @param {string} member - The name of the member to be created.
         *
         * @throws {Error} If an error occurs during the creation of the member.
         */
        createMember(dimension, member) {
            try {
                var query = 'Createmember (' + dimension + ' = {,"' + member + '" } );';
                this.debug("CreateMember Query : " + query);
                queryModule.update(query);
            } catch ( e ) {
                this.error(e.message);
                throw e;
            }
        }

        /**
         * Deletes a member from a given dimension.
         *
         * @param {string} dimension - The dimension from which to delete the member.
         * @param {string} member - The member to be deleted.
         *
         * @return {void}
         */
        deleteMember(dimension, member) {
            try {
                var query = 'DELETEMEMBER (' + dimension + ' = {,"' + member + '" } );';
                this.debug("deleteMember Query : " + query);
                queryModule.update(query);
            } catch ( e ) {
                this.error(e.message);
                throw e;
            }
        }

        /**
         * Check if the given dimension exists.
         *
         * @param {Array} dimension - An array representing the dimensions to be checked.
         * @returns {boolean} - True if the dimension exists, false otherwise.
         * @throws {Error} - If an error occurs during the process.
         */
        existDimension(dimension) {
            try {
                var query = '(Select (' + dimension.join('*') + ') on row).count;';
                this.debug("Select Query : " + query);
                var returnJson = queryModule.select(query);
                this.debug("Return Json : " + JSON.stringify(returnJson));
                if ( returnJson.Result == 0 ) {
                    return false;
                } else {
                    return true;
                }
            } catch ( e ) {
                this.error(e.message);
                throw e;
            }
        }

        /**
         * Creates a dimension member with the given dimension and value.
         *
         * @param {Array} dimension - The dimension of the member to be created.
         * @param {Array} value - The value of the member to be created.
         */
        createDimension(dimension, value, scope, where) {
            try {
                var query = 'Createmember (';
                for ( var i = 0; i < dimension.length; i++ ) {
                    if ( value[i].substr(0, 2) == "P ") {
                        // attribute 의 property 를 반영
                        query += ' ' + dimension[i] + ' = {"' + value[i].substr(2) + '",}' + (i < dimension.length - 1 ? "," : "");
                    } else {
                        // attribute 를 반영
                        query += ' ' + dimension[i] + ' = {,"' + value[i] + '"}' + (i < dimension.length - 1 ? "," : "");
                    }
                }
                query += ')';
                if ( scope != undefined ) {
                    query += ' ' + scope;
                }
                if ( where != undefined ) {
                    query += ' ' + where;
                }
                query += ';';
                this.debug("CreateMember Query : " + query);
                queryModule.update(query);
            } catch ( e ) {
                this.error(e.message);
                throw e;
            }
        }

        /**
         * Check if the given granularity exists.   필요없어 보임 - granularuty는 Measure 생성시 자동으로 생성이 된다.
         *
         * @param {Array} granularity - granularity.
         */
//        existGranularity(granularity) {
//            try {
//                var query = '(Select (' + granularity.join('*') + ') on row, () on column).count;';
//                this.debug("Select Query : " + query);
//                var returnJson = queryModule.select(query);
//                this.debug("Return Json : " + JSON.stringify(returnJson));
//                if ( returnJson.Result == 0 ) {
//                    return false;
//                } else {
//                    return true;
//                }
//            } catch ( e ) {
//                this.error(e.message);
//                throw e;
//            }
//        }

        /**
         * Creates a Granularity. 필요없어 보임 - granularuty는 Measure 생성시 자동으로 생성이 된다.
         *
         * @param {Array} granularity - granularity.
         * @param {Array} value - The value of the member to be created.
         */
//        createGranularity(granularity, value) {
//            try {
//                var query = 'Createmember (';
//                for ( var i = 0; i < granularity.length; i++ ) {
//                     query += ' ' + granularity[i] + ' = {,[' + value[i] + ']}' + (i < granularity.length - 1 ? "," : "");
//                }
//                query += ');';
//                this.debug("CreateMember Query : " + query);
//                queryModule.update(query);
//            } catch ( e ) {
//                this.error(e.message);
//                throw e;
//            }
//        }

        /**
         * Checks if a measure exists for a given dimension and condition.
         *
         * @param {Array} dimension - The array of dimensions to select.
         * @param {Array} measure - The array of measures to select.
         * @param {string} where - The condition to filter the data.
         * @returns {boolean} - Returns true if the measure exists, false otherwise.
         * @throws {Error} - Throws an error if there is an exception during the execution.
         */
        existMeasure(dimension, measure, where) {
            try {
                var query = '(Select (' + dimension.join('*') + ') on row, ({' + measure.join(',') + '}) on column ' + ( where != undefined ? where : "" ) + ').count;';
                this.debug("Select Query : " + query);
                var returnJson = queryModule.select(query);
                this.debug("Return Json : " + JSON.stringify(returnJson));
                if ( returnJson.Result == 0 ) {
                    return false;
                } else {
                    return true;
                }
            } catch ( e ) {
                this.error(e.message);
                throw e;
            }
        }

        /**
         * Creates a measure using the provided dimension and measure values.
         *
         * @param {Array} dimension - An array of dimension values.
         * @param {Array} measure - An array of measure values.
         *
         * @return {undefined}
         */
        createMeasure(dimension, measure) {
            try {
                var query = this.createMeasureQuery(dimension, measure);
                this.debug("createMeasure Query : " + query);
                queryModule.update(query);
            } catch ( e ) {
                this.error(e.message);
                throw e;
            }
        }

        createMeasureQuery(dimension, measure) {
            var query = 'cartesian scope:(' + dimension.join('*') + ');' + measure.join(' ') + ' end scope;';
            return query;
        }

        /**
         * Update a measure using the provided dimension and measure values.
         *
         * @param {Array} dimension - An array of dimension values.
         * @param {Array} measure - An array of measure values.
         *
         * @return {undefined}
         */
        updateMeasure(dimension, measure) {
            try {
                var query = this.updateMeasureQuery(dimension, measure);
                this.debug("updateMeasure Query : " + query);
                queryModule.update(query);
            } catch ( e ) {
                this.error(e.message);
                throw e;
            }
        }

        updateMeasureQuery(dimension, measure) {
            var query = 'scope:(' + dimension.join('*') + ');' + measure.join(' ') + ' end scope;';
            return query;
        }

        updateBlockMeasure(dimension, measure) {
            try {
                var query = this.updateBlockMeasureQuery(dimension, measure);
                this.debug("updateBlockMeasure Query : " + query);
                queryModule.update(query);
            } catch ( e ) {
                this.error(e.message);
                throw e;
            }
        }

        updateBlockMeasureQuery(dimension, measure) {
            var query = 'block scope:(' + dimension.join('*') + ');' + measure.join(' ') + ' end scope;';
            return query;
        }


        /**
         * Deletes data for the given dimension and measure group.
         *
         * @param {string} where - where qeury.
         * @param {string} measureGroup - The measure group to delete data from.
         *
         * @throws {Error} If an error occurs during the deletion process.
         */
        deleteMeasure(where, measureGroup) {
            try {
                var query = this.deleteMeasureQuery(where, measureGroup);
                this.debug("deleteMeasure Query : " + query);
                queryModule.update(query);
            } catch ( e ) {
                this.error(e.message);
                throw e;
            }
        }

        deleteMeasureQuery(where, measureGroup) {
            var query = 'delete data for model [' + measureGroup + '] where {' + where.join(",") + '};';
            return query;
        }

        /**
         * Retrieves a list of selected dimensions and measures based on provided parameters.
         *
         * @param {array} dimension - An array containing the dimensions to select.
         * @param {array} measure - An array containing the measures to select.
         * @param {string} where - The condition to apply to the query.
         * @param {string} orderby - The order to apply to the query results.
         * @param {string} limit - The maximum number of rows to return in the query results.
         * @param {string} _whereFilter - MG 가 다른 조건을 걸 경우 : where 절 다음에 filter 를 걸어서 사용해야함
         *
         * @returns {object} - An object containing two properties:
         *                    - cs: The cell set obtained from executing the query.
         *                    - columns: An object containing arrays of selected dimensions and measures.
         *                                The dimensions are stored in the "dimension" property of "columns".
         *                                The measures are stored in the "measure" property of "columns".
         */
        selectList(dimension, measure, where, orderby, limit, _whereFilter) {
            try {
                var query = '';
                var measureQuery = "";

                if ( measure.length > 0 )
                    measureQuery = '{' + measure.join(',') + '}';

                // 26.1.20 where 절 다음에 필터를 거는 로직 추가
                if ( _whereFilter != undefined ) {
                    where += ".filter ( " + _whereFilter + " )"
                }
                query = 'Select (' + dimension.join('*') + ') on row, (' + measureQuery + ') on column ' + where + ' ' + orderby + ' ' + limit + ";";

                this.debug("selectList Query : " + query);
                var lsResult = queryModule.select(query);

                var cs = cellsetModule.createCellSet(lsResult);
                this.debug("selectList Count : " + cs.rowCount);

                return { cs : cs, columns : this.getCsColumns(lsResult.Meta) };
            } catch ( e ) {
                this.error(e.message);
                throw e;
            }
        }

        /**
            var CurrentWeek = vdCommon.selectResult('&CurrentWeek.element(0).DisplayName');
            var SourceKey = vdCommon.selectResult('Version.[Version Name].[CWV_MP].Key');
            var SourceKey = vdCommon.selectResult('Version.[Version Name].[CWV_MP].DisplayName');
            var UserId = vdCommon.selectResult('CurrentUser().[User Name]');
        */
        selectResult(oneField) {
            try {
                var query = "SELECT " + oneField + ";";
                this.debug("selectResult Query : " + query);

                if ( queryModule.select(query) == null ) {
                    return null;
                } else {
                    return queryModule.select(query).Result;
                }
            } catch ( e ) {
                this.error(e.message);
                throw e;
            }
        }

        /**
            var Seq = vdCommon.selectCount('Version.[Version Name].filter(#.[Version Created By] == CurrentUSer().Name)') + 1;
        */
        selectCount(query) {
            try {
                var query = "( SELECT ( " + query + " ) ).count;";
                this.debug("selectCount Query : " + query);

                if ( queryModule.select(query) == null ) {
                    return 0;
                } else {
                    return parseInt(queryModule.select(query).Result);
                }
            } catch ( e ) {
                this.error(e.message);
                throw e;
            }
        }

        /**
            var Seq = vdCommon.selectListCount(["&VD"], ["Measure.[Validation]"], 'Version.[Version Name].filter(#.[Version Created By] == CurrentUSer().Name)');
        */
        selectListCount(dimension, measure, where) {
            try {
                var query = '';
                var measureQuery = "";

                if ( measure.length > 0 )
                    measureQuery = '{' + measure.join(',') + '}';
                query = 'Select (' + dimension.join('*') + ') on row, (' + measureQuery + ') on column ' + where;

                var query = "( " + query + " ).count;";
                this.debug("selectCount Query : " + query);

                if ( queryModule.select(query) == null ) {
                    return 0;
                } else {
                    return parseInt(queryModule.select(query).Result);
                }
            } catch ( e ) {
                this.error(e.message);
                throw e;
            }
        }

        /**
         * Retrieves a list of results from a select query.
         *
         * @param {string} fName - The name of the function.
         * @param {string} query - The select query.
         * @returns {object} An object containing the select list, column information, and the row count.
         *                   - rowCount: The number of rows in the select result.
         *                   - selectList: The select result.
         *                   - columns: An object containing the measures and dimensions of the select result.
         */
        selectQueryList(fName, query) {
            try {
                this.debug(`${fName} > query : ${query}`);
                let lsResult = queryModule.select(query);
                let selectResult = cellsetModule.createCellSet(lsResult);
                let selectResultCount = selectResult.rowCount;
                //this.debug(`${fName} > selectResult : ${JSON.stringify(selectResult)}`);
                this.debug(`${fName} > selectResultCount : ${selectResultCount}`);
                return {rowCount : selectResultCount, cs : selectResult, columns : this.getCsColumns(lsResult.Meta)}
            } catch ( e ) {
                this.error(e.message);
                throw e;
            }
        }

        /**
         * Executes a query and updates the query module.
         *
         * @param {string} fName - The name of the function executing the query.
         * @param {string} query - The query to be executed.
         *
         * @throws {Error} If an error occurs during execution.
         */
        executeQuery(fName, query) {
            try {
                this.debug(`${fName} > executeResult > query : ${query}`);
                queryModule.update(query);

            } catch ( e ) {
                this.error(e.message);
                throw e;
            }
        }

        /**
         * Executes a query for python.
         *
         * @param {string} pythonName - The name of the python.
         * @param {string} query - The query to be executed.
         *
         * @throws {Error} If an error occurs during execution.
         */
        executePython(pythonName, query) {
            try {
                /* 26.2.25 파이썬 멤버 확인 로직 제거
                if ( ["VD"].includes(this.fn_division()) ) {
                    if ( !this.existMember('[Python Batch].[Python Name]', pythonName) ) {
                        this.createMember('[Python Batch].[Python Name]', pythonName);
                    }
                }
                */

                this.debug(`Python Call > executeResult > query : ${query}`);
                queryModule.update(query);
            } catch ( e ) {
                this.error(e.message);
                throw e;
            }
        }

        /**
         * Retrieves the dimension and measure columns from the specified metadata.
         *
         * @param {Array} meta - The metadata to retrieve columns from.
         * @returns {Object} An object containing two arrays: dimension and measure.
         *                   The dimension array contains strings in the format "DimensionName.AttributeName",
         *                   while the measure array contains strings representing the names of the measures.
         */
        getCsColumns(meta) {
            var dimension = [];
            var measure = [];
            if (meta != undefined) {
                for ( var i = 0; i < meta.length; i++ ) {
                    if ( meta[i].DimensionName != undefined ) {
                        dimension.push(meta[i].DimensionName + "." + meta[i].AttributeName);
                    } else {
                        measure.push(meta[i].Name);
                    }
                }
            }

            return {dimension : dimension, measure : measure};
        }

        /**
         * Prints data from a given result set.
         *
         * @param {object} result - The result set containing the data to print.
         * @param {number} printRow - The number of rows to print. If set to 0, all rows will be printed. If a value greater than the total number of rows in the result set is specified, only the available rows will be printed.
         *
         * @return {void}
         */
        printCsData(result, printRow) {
            var dimension = result.columns.dimension;
            var measure = result.columns.measure;

            if ( printRow == 0 ) {
                printRow = result.cs.rowCount;
            } else if ( printRow > result.cs.rowCount ) {
                printRow = result.cs.rowCount;
            }

            for ( var i = 0; i < printRow; i++ ) {
                var row = {};
                for ( var idx = 0; idx < dimension.length; idx++ ) {
                    row[dimension[idx]] = result.cs.row(i).cell(result.cs.memberColumnIndex(dimension[idx].split(".")[0], dimension[idx].split(".")[1])).Name;
                }
                for ( var idx = 0; idx < measure.length; idx++ ) {
                    row[measure[idx]] = result.cs.row(i).cell(result.cs.measureColumnIndex(measure[idx]));
                }
                this.debug((i + 1) + " Row : " + JSON.stringify(row));
            }
        }

        /**
         * Creates a dimension based on the given granularity and granularityValues.
         *
         * @param {string[]} granularity - An array of strings representing the levels of granularity for the dimension.
         * @param {string[]} granularityValues - An array of strings representing the values corresponding to each level of granularity.
         *
         * @returns {string[]} - An array of strings representing the dimensions created based on the given granularity and granularityValues.
         */
        makeDimension(granularity, granularityValues) {
            var dimensions = [];

            for ( var i = 0; i < granularity.length; i++ ) {
                dimensions.push(granularity[i] + ".[" + granularityValues[i] + "]");
            }

            return dimensions;
        }

        /*
             Member 를 가져온다
        */
        getMember(cs, rowIdx, dimensionName, attributeName) {
            if ( rowIdx < cs.rowCount ) {
                return cs.row(rowIdx).cell(cs.memberColumnIndex(dimensionName, attributeName));
            } else {
                return {Name : ""};
            }
        }

        /*
            Measure 를 가져온다
        */
        getMeasureValue(cs, rowIdx, MeasureName) {
            if ( rowIdx < cs.rowCount ) {
                return cs.row(rowIdx).cell(cs.measureColumnIndex(MeasureName));
            } else {
                return "";
            }
        }

        /*
            멤버의 Properties 를 가져온다
        */
        getPropertyValue(cs, rowIdx, dimensionName, attributeName, propertyName) {
            if ( rowIdx < cs.rowCount ) {
                var memberObject = cs.row(rowIdx).cell(cs.memberColumnIndex(dimensionName, attributeName));

                if ( memberObject.MemberProperties && Array.isArray(memberObject.MemberProperties) ) {
                    for ( var k = 0; k < memberObject.MemberProperties.length; k++ ) {
                        var propertyItem = memberObject.MemberProperties[k];
                        if ( propertyItem.PropertyName && propertyItem.PropertyName === propertyName ) {
                            return propertyItem.PropertyValue;
                        }
                    }
                }
            } else {
                return "";
            }
        }

        /*
            콤보 데이타 구성
            파라미터
                1. Dimension 으로 콤보 구성 => DimName : "Location", DimAttbName : "Location"
                2. Measure 로 콤보 구성 => MeasureName : "Global Quota Mtrl_Status"
                3. 배열로 콤보 구성 => ComboCodes : ["A","B"], ComboValues : ["A","B"]
                4. 기타 옵션
                    DimDisplayAttbName => DisplayName 을 다른 Attribute 를 사용할때
                    DimDisplayPropertyName => DisplayName 을 Property 를 사용할때
                    DimDescAttbName => 코드로만 구성된 Member 의 경우 DisplayName 에 다른 설명을 붙일 Attribute 이름 => P306 (SAMEX)
                    isDisplayNameWithCode => DisplayName (Name) 으로 보고 싶을때
                    isNameWithDisplayName => Name:DisplayName 으로 보고 싶을때
                    isOnlyName => Name, Display를 Name으로 보여준다.
                    includeField => 추가로 필요한 컬럼 정의 => Location:Site Group1:SiteGroup,...
                    includeProperty => Property 를 포함 할때 => "To Location Site ID,To Location Site Location"
                    Sort : Name / DisplayName / 그외 Property 이름(IBPL 의 정렬에 들어가면 되기 때문에 사용할 일이 없어보임)
                    existAll : true => All 을 상단에 추가
                    existALL : true => ALL 을 상단에 추가
                    existBlank : true => "" 을 상단에 추가
                    existHyphen : true => - 을 상단에 추가
                    includeOtherProperty => 여러 Dimension의 Property 를 추가할때 Location:Location:Key/Name/DisplayName/DisplayAlias/그외:변수명, ..... : 26.1.20 추가
            예제
                var comboList = vdCommon.fn_makeCombo(result, {DimName : "Location", DimAttbName : "Location", Sort : "DisplayName", isDisplayNameWithCode : true});
                var comboList = vdCommon.fn_makeCombo(result, {DimName : "Sub Location", DimAttbName : "Sub Location", existAll : true, Sort : "DisplayName", isDisplayNameWithCode : true});
                var comboList = vdCommon.fn_makeCombo(null, {ComboCodes : ["ERP","NSCM"], ComboValues : ["ERP","NSCM"]});
        */
        fn_makeCombo(result, param) {
            var comboList = [];
            var validHashMap = {};
            var name = "";
            var displayName = "";
            var _name = "";
            var _displayName = "";
            var _displayAlias = "";

            // 2025-11-26 : 사업부 코드를 가져온다. Default 는 VD 임.
            var division = this.fn_division();
            // this.debug("division : " + division);

            if ( param["ComboCodes"] != undefined ) {
                var codes = param["ComboCodes"];
                var values = param["ComboValues"];
                for ( var i = 0; i < codes.length; i++ ) {
                    comboList.push({ Name : codes[i], DisplayName : values[i]});
                }
            } else {
                for ( var i = 0; i < result.cs.rowCount; i++ ) {
                    var propertySort = -1;

                    if ( param["DimName"] != undefined ) {
                        // this.debug(JSON.stringify(result.cs.row(i).cell(result.cs.memberColumnIndex(param["DimName"], param["DimAttbName"]))));
                        _name = result.cs.row(i).cell(result.cs.memberColumnIndex(param["DimName"], param["DimAttbName"])).Name;
                        _displayName = result.cs.row(i).cell(result.cs.memberColumnIndex(param["DimName"], param["DimAttbName"])).DisplayName;
                        _displayAlias = result.cs.row(i).cell(result.cs.memberColumnIndex(param["DimName"], param["DimAttbName"])).DisplayAlias;

                        // 25.8.22 : DisplayName 을 다른 Attribute, Property 를 볼때
                        if ( param["DimDisplayAttbName"] != undefined && param["DimDisplayAttbName"] ) {
                            // 25.8.22 : DisplayName을 다른 Attribute의 Property에서 조회 할 경우
                            _displayName = result.cs.row(i).cell(result.cs.memberColumnIndex(param["DimName"], param["DimDisplayAttbName"])).DisplayName;
                            _displayAlias = result.cs.row(i).cell(result.cs.memberColumnIndex(param["DimName"], param["DimDisplayAttbName"])).DisplayAlias;
                        } else if ( param["DimDisplayPropertyName"] != undefined && param["DimDisplayPropertyName"] ) {
                            // 25.8.22 : DisplayName을 Property에서 조회 할 경우
                            _displayName = this.getPropertyValue(result.cs, i, param["DimName"], param["DimAttbName"], param["DimDisplayPropertyName"]);
                            _displayAlias = this.getPropertyValue(result.cs, i, param["DimName"], param["DimAttbName"], param["DimDisplayPropertyName"]);
                        }

                        // 25.6.27 : 사업부 특화 로직 : Location.[Location], To Location.[To Location], Sub Location.[Sub Location] 경우에는
                        if ( division == "VD" ) {
                            // _displayAlias 을 다른 곳에서 가져온다. ( 예외 케이스 )
                            if ( param["DimName"] == "Location" && param["DimAttbName"] == "Location" ) {
                                _displayAlias = this.getPropertyValue(result.cs, i, param["DimName"], param["DimAttbName"], "Location Site ID");
                            }
                            if ( param["DimName"] == "Sub Location" && param["DimAttbName"] == "Sub Location" ) {
                                _displayAlias = this.getPropertyValue(result.cs, i, param["DimName"], param["DimAttbName"], "Sub Location ID");
                            }
                            if ( param["DimName"] == "To Location" && param["DimAttbName"] == "To Location" ) {
                                _displayAlias = this.getPropertyValue(result.cs, i, param["DimName"], param["DimAttbName"], "To Location Site ID");
                            }
                        }

                        // 25.2.25 : DisplayAlias 을 우선으로 반영한다.
                        if ( _displayAlias != null && _displayAlias != "" ) {
                            _displayName = _displayAlias;
                        }
                        // 25.7.1 : DisplayName 에 Desc 를 붙인다.
                        if ( param["DimDescAttbName"] != undefined ) {
                            _displayName = _displayName + " (" + result.cs.row(i).cell(result.cs.memberColumnIndex(param["DimName"], param["DimDescAttbName"])).Name + ")";
                        }
                        // 25.9.11 : propertySort 기능 추가 : null 이면 0으로 바꾼다.
                        if ( param["Sort"] != undefined && param["Sort"] != "Name" && param["Sort"] != "DisplayName" ) {
                            propertySort = this.getPropertyValue(result.cs, i, param["DimName"], param["DimAttbName"], param.Sort);
                            if ( propertySort == null ) {
                                propertySort = 0;
                            }
                        }

                        name = _name;
                        displayName = _displayName;

                        // - 일 경우는 무시
                        if ( name == "-" ) {
                            continue;
                        }

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

                    // Lookup 기능을 위해 includeField 가 있으면 중복 허용
                    var allowDuplicate = false;
                    if ( param["includeField"] != undefined && param["includeField"] != "" ) {
                        allowDuplicate = true;
                    }

                    if ( (allowDuplicate == false && validHashMap[name] == undefined) || allowDuplicate == true ) {
                        var rows = { Name : name, DisplayName : displayName};

                        // 2025-12-09 해당 Dimension 의 Property 를 가져온다.
                        if ( param["includeProperty"] != undefined && param["includeProperty"] != "" ) {
                            var includeProperty = param["includeProperty"].split(",");
                            for ( var m = 0; m < includeProperty.length; m++ ) {
                                rows[includeProperty[m]] = this.getPropertyValue(result.cs, i, param["DimName"], param["DimAttbName"], includeProperty[m]);
                            }
                        }

                        // Casecade를 위한 컬럼 추가 => otherColumns=Item:Product Group:UI Product Group,Item:Product:UI Product
                        if ( param["includeField"] != undefined && param["includeField"] != "" ) {
                            var includeField = param["includeField"].split(",");
                            for ( var m = 0; m < includeField.length; m++ ) {
                                var dims = includeField[m].split(":");
                                // 2025-11-24 : attribute 에 attribute^property 형태로 넣을 수 있게 수정
                                if ( dims[1].indexOf("^") < 0 ) {
                                    rows[dims[2]] = result.cs.row(i).cell(result.cs.memberColumnIndex(dims[0], dims[1])).Name;
                                    rows[dims[2] + "_DisplayName"] = result.cs.row(i).cell(result.cs.memberColumnIndex(dims[0], dims[1])).DisplayName;
                                    rows[dims[2] + "_DisplayAlias"] = result.cs.row(i).cell(result.cs.memberColumnIndex(dims[0], dims[1])).DisplayAlias;
                                } else {
                                    var attrSplit = dims[1].split("^");

                                    var propertyValue = this.getPropertyValue(result.cs, i, dims[0], attrSplit[0], attrSplit[1]);
                                    rows[dims[2]] = propertyValue;
                                    rows[dims[2] + "_DisplayName"] = propertyValue;
                                    rows[dims[2] + "_DisplayAlias"] = propertyValue;
                                }
                            }
                        }

                        // 정렬값이 있으면 추가
                        if ( propertySort > -1 ) {
                            rows["propertySort"] = propertySort;
                        }

                        // 26.1.20 : includeOtherProperty 로직 추가 : Location:Location:Key/Name/DisplayName/DisplayAlias/그외:변수명, .....
                        if ( param["includeOtherProperty"] != undefined && param["includeOtherProperty"] != "" ) {
                            var includeOtherProperty = param["includeOtherProperty"].split(",");
                            for ( var m = 0; m < includeOtherProperty.length; m++ ) {
                                var dims = includeOtherProperty[m].split(":");
                                if ( ["Key","Name","DisplayName","DisplayAlias"].includes(dims[2]) ) {
                                    rows[dims[3]] = result.cs.row(i).cell(result.cs.memberColumnIndex(dims[0], dims[1]))[dims[2]];
                                } else {
                                    rows[dims[3]] = this.getPropertyValue(result.cs, i, dims[0], dims[1], includeProperty[dims[2]]);
                                }
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
                } else if ( param["Sort"] == "DisplayName" ) {
                    comboList.sort((a, b) => {
                            if ( a.DisplayName < b.DisplayName ) return -1;
                            if ( a.DisplayName > b.DisplayName ) return 1;
                            return 0;
                        });
                } else {
                    // 25.9.11 : propertySort 기능 추가
                    comboList.sort((a, b) => {
                            if ( a.propertySort < b.propertySort ) return -1;
                            if ( a.propertySort > b.propertySort ) return 1;
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
                        all[dims[2] + "_DisplayName"] = "All";
                        all[dims[2] + "_DisplayAlias"] = "All";
                    }
                }

                comboList.unshift(all);
            }

            // 2025-11-26 : CO 의 경우 All 대신에 ALL 을 사용해서 옵션 추가
            if ( param["existALL"] != undefined && param["existALL"] ) {
                var all = { Name : "ALL", DisplayName : "ALL" };

                // includeField 에 All 넣기
                if ( param["includeField"] != undefined && param["includeField"] != "" ) {
                    var includeField = param["includeField"].split(",");
                    for ( var m = 0; m < includeField.length; m++ ) {
                        var dims = includeField[m].split(":");
                        all[dims[2]] = "ALL";
                        all[dims[2] + "_DisplayName"] = "ALL";
                        all[dims[2] + "_DisplayAlias"] = "ALL";
                    }
                }

                comboList.unshift(all);
            }

            if ( param["existBlank"] != undefined && param["existBlank"] ) {
                var blank = { Name : "", DisplayName : "" };

                // includeField 에 All 넣기
                if ( param["includeField"] != undefined && param["includeField"] != "" ) {
                    var includeField = param["includeField"].split(",");
                    for ( var m = 0; m < includeField.length; m++ ) {
                        var dims = includeField[m].split(":");
                        blank[dims[2]] = "";
                        blank[dims[2] + "_DisplayName"] = "";
                        blank[dims[2] + "_DisplayAlias"] = "";
                    }
                }

                comboList.unshift(blank);
            }

            // 2025-11-25 : existHyphen 옵션 추가
            if ( param["existHyphen"] != undefined && param["existHyphen"] ) {
                var all = { Name : "-", DisplayName : "-" };

                // includeField 에 All 넣기
                if ( param["includeField"] != undefined && param["includeField"] != "" ) {
                    var includeField = param["includeField"].split(",");
                    for ( var m = 0; m < includeField.length; m++ ) {
                        var dims = includeField[m].split(":");
                        all[dims[2]] = "-";
                        all[dims[2] + "_DisplayName"] = "-";
                        all[dims[2] + "_DisplayAlias"] = "-";
                    }
                }

                comboList.unshift(all);
            }

            return comboList;
        }

        /**
         * Dimension 의 DisplayName을 가져온다.
         *
         * @param dimension - Dimension 구분자
         * @param value - Dimension Member 값
         *
         * @returns - DisplayName
         */
        fn_getCodeName(dimension, value) {
            if ( dimension == "Location" ) {
                var result = this.selectList(["Location.[Location].[" + value + "]"], [], "", "", "");
                if ( result.cs.rowCount == 1 ) {
                    return result.cs.row(0).cell(result.cs.memberColumnIndex("Location", "Location")).DisplayName;
                }
            } else {
                var result = this.selectList([dimension + ".[" + value + "]"], [], "", "", "");
                if ( result.cs.rowCount == 1 ) {
                    var dim = dimension.split(".");

                    return result.cs.row(0).cell(result.cs.memberColumnIndex(dim[0].replace("[","").replace("]",""), dim[1].replace("[","").replace("]",""))).DisplayName;
                }
            }

            return "";
        }

        /**
            주("202501,202502,202503")를 주면 주별 첫 월요일을 넘겨주는 함수
        */
        fn_getMondayForWeek(weeks) {
            try {
                var result = this.selectList(["Time.[Day]", "Time.[Week]" + '.filter(#.Name in {' + weeks.split(",").map(item => `"${item}"`).join(",") + '})'],
                                                [], "where { Time.[Day of Week].[MON] }", "", "");

                var rtn = {};
                for ( var i = 0; i < result.cs.rowCount; i++ ) {
                    var week = result.cs.row(i).cell(result.cs.memberColumnIndex("Time", "Week")).Name;
                    var day = result.cs.row(i).cell(result.cs.memberColumnIndex("Time", "Day")).Name;
                    rtn[week] = day;
                }

                return rtn;
            } catch ( e ) {
                this.error(e.message);
                throw e;
            }
        }

        /**
            주를 나타내는 NamedSet 을 주면 주별 첫 월요일을 넘겨주는 함수
        */
        fn_getMondayForNS(weekNamedSet) {
            try {
                var result = this.selectList(["Time.[Day]", "&" + weekNamedSet],
                                                [], "where { Time.[Day of Week].[MON] }", "", "");

                var rtn = {};
                for ( var i = 0; i < result.cs.rowCount; i++ ) {
                    var week = result.cs.row(i).cell(result.cs.memberColumnIndex("Time", "Week")).Name;
                    var day = result.cs.row(i).cell(result.cs.memberColumnIndex("Time", "Day")).Name;
                    rtn[week] = day;
                }

                return rtn;
            } catch ( e ) {
                this.error(e.message);
                throw e;
            }
        }

        /**
        * Retrieves the number of rows from a select query.
        *
        * @param {string} fName - The name of the function.
        * @param {string} query - The select query.
        * @returns {object} An object containing the row count.
        * - Result: The number of rows in the select result.
        */
        selectQuery(fName, query) {
            try {
                this.debug(`${fName} > query : ${query}`);
                let selectResult = queryModule.select(query);
                //this.debug(`${fName} > selectResult : ${JSON.stringify(selectResult)}`);
                return selectResult;
            } catch ( e ) {
                this.error(e.message);
                throw e;
            }
        }

        /** Indicates the start and end of the function.
        *
        * @param function
        **/
        fn_decorator(fn) {
            let programName = this.programName;

            return function(...args) {
                let o9Params = args[0];

                if(typeof o9Params === "object"){
                    o9Params = JSON.stringify(o9Params)
                }

                let parsedParams = JSON.parse(o9Params);
                Log.Info(`[${programName}][${fn.name}] : START > ${o9Params}`);
                const result = fn(...args);
                Log.Info(`[${programName}][${fn.name}] : END`);
                return result;
            }
        }

        /**
        * Get KnoxId
        * @returns {*}
        */
        fn_getUserId() {
            let query = `select CurrentUser().[Name];`;
            let result = this.selectQuery('selectCurrentUserInfo', query).Result;
            return result.split("@")[0];
        }

        /*
            2026-01-12 : 데이타 업로드를 위한 공통 함수
        */
        fn_dataUpload(versionName, dimension, measure, dataArray) {
            this.debug("DataUpload - versionName : " + versionName);
            this.debug("DataUpload - dimension : " + dimension);
            this.debug("DataUpload - measure : " + measure);
            this.debug("DataUpload - data count : " + dataArray.length);

            var userName = this.selectResult('CurrentUser().Name');

            // 과거 데이타 삭제 ( 5일 이후 )
            var result = this.selectList([versionName, "[Personnel].[Email].[" + userName + "]", "[Seq1].[Seq1]"],
                                         ["Measure.[Upload Header_Creation Time]"],
                                         'where { Measure.[Upload Header_Creation Time] < DATEADD(Now(),-5,"Day")}', "", "");
            var seq1s = [];
            for ( var i = 0; i < result.cs.rowCount; i++ ) {
                seq1s.push(result.cs.row(i).cell(result.cs.memberColumnIndex("Seq1", "Seq1")).Name);
            }
            if ( seq1s.length > 0 ) {
                this.deleteMeasure([versionName,
                                            "[Personnel].[Email].[" + userName + "]",
                                            "[Seq1].[Seq1]" + this.vdUtil.fn_filterStr(seq1s)],
                                        "Upload Header");
                this.deleteMeasure([versionName,
                                            "[Personnel].[Email].[" + userName + "]",
                                            "[Seq1].[Seq1]" + this.vdUtil.fn_filterStr(seq1s)],
                                        "Upload Data");
            }

            // Max 값을 구한다.
            var seq1 = 1;
            result = this.selectList([versionName, "[Personnel].[Email].[" + userName + "]", "[Seq1].[Seq1]"],
                                     ["Measure.[Upload Header_Creation Time]"],
                                     "", "orderby [Seq1].[Seq1].Key desc", "limit 1");
            if ( result.cs.rowCount > 0 ) {
                seq1 = parseInt(result.cs.row(0).cell(result.cs.memberColumnIndex("Seq1", "Seq1")).Name) + 1;
            }

            // 실 데이타를 넣을 seq 배열을 구한다.
            var seq = [];
            for ( var i = 0; i < Math.ceil(dataArray.length / 20); i++ ) {
                seq.push((i + 1) + "");
            }

            // Upload Header 등록
            this.createMeasure([versionName, "[Personnel].[Email].[" + userName + "]"
                                        ,"[Seq1].[Seq1].[" + seq1 + "]"],
                               ['Measure.[Upload Header_Dimension] = "' + dimension + '";'
                                    ,'Measure.[Upload Header_Measure] = "' + measure + '";'
                                    ,this.vdUtil.fn_qMeaUpdateTime("Measure.[Upload Header_Creation Time]")]);

            // Upload Data 를 한번에 생성 - 속도 개선을 위핸 한방에 생성을 하고 다음에 block scope 로 수정을 한다.
            this.createMeasure([versionName
                                    ,"[Personnel].[Email].[" + userName + "]"
                                    ,"[Seq1].[Seq1].[" + seq1 + "]"
                                    ,"[Seq].[Seq]" + this.vdUtil.fn_filterStr(seq)],
                               ['Measure.[Upload Data_Data1] = "-";'
                                    ,'Measure.[Upload Data_Data2] = "-";'
                                    ,'Measure.[Upload Data_Data3] = "-";'
                                    ,'Measure.[Upload Data_Data4] = "-";'
                                    ,'Measure.[Upload Data_Data5] = "-";'
                                    ,'Measure.[Upload Data_Data6] = "-";'
                                    ,'Measure.[Upload Data_Data7] = "-";'
                                    ,'Measure.[Upload Data_Data8] = "-";'
                                    ,'Measure.[Upload Data_Data9] = "-";'
                                    ,'Measure.[Upload Data_Data10] = "-";'
                                    ,'Measure.[Upload Data_Data11] = "-";'
                                    ,'Measure.[Upload Data_Data12] = "-";'
                                    ,'Measure.[Upload Data_Data13] = "-";'
                                    ,'Measure.[Upload Data_Data14] = "-";'
                                    ,'Measure.[Upload Data_Data15] = "-";'
                                    ,'Measure.[Upload Data_Data16] = "-";'
                                    ,'Measure.[Upload Data_Data17] = "-";'
                                    ,'Measure.[Upload Data_Data18] = "-";'
                                    ,'Measure.[Upload Data_Data19] = "-";'
                                    ,'Measure.[Upload Data_Data20] = "-";']);

            var queryStr = "";
            for ( var i = 0; i < Math.ceil(dataArray.length / 20); i++ ) {
                var data = ["", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", ""];

                // 데이타 생성
                for ( var m = 0; m < 20; m++ ) {
                    if ( i * 20 + m < dataArray.length )     data[m] = dataArray[i * 20 + m];
                }

                // Upload Data 수정 쿼리를 만든다.
                queryStr += this.updateBlockMeasureQuery([versionName,
                                                                "[Personnel].[Email].[" + userName + "]",
                                                                "[Seq1].[Seq1].[" + seq1 + "]",
                                                                "[Seq].[Seq].[" + (i + 1) + "]"],
                                                            ['Measure.[Upload Data_Data1] = "' + data[0] + '";'
                                                                ,'Measure.[Upload Data_Data2] = "' + data[1] + '";'
                                                                ,'Measure.[Upload Data_Data3] = "' + data[2] + '";'
                                                                ,'Measure.[Upload Data_Data4] = "' + data[3] + '";'
                                                                ,'Measure.[Upload Data_Data5] = "' + data[4] + '";'
                                                                ,'Measure.[Upload Data_Data6] = "' + data[5] + '";'
                                                                ,'Measure.[Upload Data_Data7] = "' + data[6] + '";'
                                                                ,'Measure.[Upload Data_Data8] = "' + data[7] + '";'
                                                                ,'Measure.[Upload Data_Data9] = "' + data[8] + '";'
                                                                ,'Measure.[Upload Data_Data10] = "' + data[9] + '";'
                                                                ,'Measure.[Upload Data_Data11] = "' + data[10] + '";'
                                                                ,'Measure.[Upload Data_Data12] = "' + data[11] + '";'
                                                                ,'Measure.[Upload Data_Data13] = "' + data[12] + '";'
                                                                ,'Measure.[Upload Data_Data14] = "' + data[13] + '";'
                                                                ,'Measure.[Upload Data_Data15] = "' + data[14] + '";'
                                                                ,'Measure.[Upload Data_Data16] = "' + data[15] + '";'
                                                                ,'Measure.[Upload Data_Data17] = "' + data[16] + '";'
                                                                ,'Measure.[Upload Data_Data18] = "' + data[17] + '";'
                                                                ,'Measure.[Upload Data_Data19] = "' + data[18] + '";'
                                                                ,'Measure.[Upload Data_Data20] = "' + data[19] + '";']);

                // 부분 배치 쿼리 실행
                if ( i > 0 && i % 10 == 0 ) {
                    this.executeQuery("Batch Query : " + parseInt((i * 100) / Math.ceil(dataArray.length / 20)) + " %" , queryStr);
                    queryStr = "";
                }
            }
            // 나머지 배치 쿼리 실행
            if ( queryStr != "" ) {
                this.executeQuery("Batch Query" , queryStr);
            }

            // 엑셀 업로드 후에 파이썬 호출
            var execQuery = 'EXEC plugin instance [PY_UI_UploadMultiDataSplit] ' +
                            'for measures {[Upload Data_Data1]} ' +
                            'using scope ( ' + versionName + ' * [Personnel].[Email].[' + userName + '] * [Seq1].[Seq1].[' + seq1 + '] ) ' +
                            'using arguments {(ExecutionMode, "MediumWeight"), (MaxSliceTableCells, 200000000), (MaxConcurrency, 1 )};'
            this.executePython("PY_UI_UploadMultiDataSplit", execQuery);
        }

        // 26.2.3 : division 을 [Version].[Version Name].[GBM] 에서 가져오도록 변경. 로그를 안남기기 위해서 공통함수를 사용 안함
        fn_division() {
            var division = "";

            try {
                /*
                var result = queryModule.select(["[Version].[Version Name].[CurrentWorkingView]"], [], "", "", "");
                division = this.vdUtil.fn_getDimPropertyValue(result, 0, "Version", "Version Name", "GBM");
                */
                var lsResult = queryModule.select("Select ([Version].[Version Name].[CurrentWorkingView]) on row, () on column;");
                var cs = cellsetModule.createCellSet(lsResult);

                // GBM Property 찾기
                var memberObject = cs.row(0).cell(cs.memberColumnIndex("Version", "Version Name"));
                for ( var k = 0; k < memberObject.MemberProperties.length; k++ ) {
                    var propertyItem = memberObject.MemberProperties[k];
                    if ( propertyItem.PropertyName && propertyItem.PropertyName === "GBM" ) {
                        division = propertyItem.PropertyValue;
                        break;
                    }
                }

                //this.debug("division : " + division);
            } catch ( e ) {
                this.error(e.message);
            }

            return division;
        }

        /*
            2026.2.25 Append
            Merge 에 사용할 수정자 쿼리 구성
        */
        fn_mergeUser(measure, version) {
            return measure + ' = CurrentUser().Name + " (' + version + ')";';
        }

        // 2026.3.5 : JS 별 division 세팅
        // 2026.3.19 : DB 에서 가져오도록 변경해서 사용 안해서 주석처리 해야하는데 몰라서 막지는 않음
        fn_setDivision(division) {
            this.division = division;
        }

        // 2026.3.6 : 시나리오일 경우의 메세지를 가져온다.
        fn_scenarioInfo(version) {
            var planType = "";
            var description = "";

            var result = this.selectList(["[Version].[Version Name].[" + version + "]"], [], "", "", "");
            if ( result.cs.rowCount > 0 ) {
                planType = this.vdUtil.fn_getDimPropertyValue(result, 0, "Version", "Version Name", "Plan Type");
                description = this.vdUtil.fn_getDimPropertyValue(result, 0, "Version", "Version Name", "Description");
            }

            return { "IsScenario" : ( planType == "What-If" ? "Y" : "N")
                        ,"VersionInfo" : ( planType == "What-If" ? "This data is currently being edited in the scenario version. (" + description + ")" : "")
                   };
        }

        // 2026.3.19 : 결재 Role 정보. 안쓰일것 같음
        fn_approvalRole() {
            return { "roleCodes" : ["0","1","2","3","4","7","9"]
                        ,"roleValues" : ["Draft","Approval","Agreement","Conclusion","Parallel Consensus","Parallel Approvals","Notification"]
                        ,"roleHanValues" : ["기안","결재","합의","후결","병렬합의","병렬결재","통보"]};
        }

        // 2026.3.19 : 전체 결재라인 정보
        fn_aplns(parsedParams) {
            var aplns = [];

            try {
                if ( parsedParams.fbParams["Knox Approval All Group_Code"] != "" ) {
                    var version = this.vdUtil.fn_getFilterVersion(parsedParams);
                    var versionName = this.vdUtil.fn_getFilterVersionName(parsedParams);

                    var result = this.selectList([version
                                                        ,"[Seq].[Seq]"]
                                                     ,["Measure.[Knox Approval All Group_Name]"]
                                                     ,'where { Measure.[Knox Approval All Group_Parent Code] == "' + parsedParams.fbParams["Measure.[Knox Approval All Group_Parent Code]"] + '" '
                                                            + ', Measure.[Knox Approval All Group_Code] == "' + parsedParams.fbParams["Measure.[Knox Approval All Group_Code]"] + '" }'
                                                     ,""
                                                     ,"");
                    if ( result.cs.rowCount > 0 ) {
                        var seq = this.vdUtil.fn_getDimValue(result, 0, "Seq", "Seq");

                        // 결재 정보를 가져온다.
                        result = this.selectList([version
                                                        ,"[Seq].[Seq].[" + seq + "]"
                                                        ,"[Seq1].[Seq1]"]
                                                     ,["Measure.[Knox Approval All Group Line_UserId]"
                                                        ,"Measure.[Knox Approval All Group Line_Role]"
                                                        ,"Measure.[Knox Approval All Group Line_Order]"]
                                                     ,""
                                                     ,"orderby Measure.[Knox Approval All Group Line_Order]"
                                                     ,"");
                        for ( var i = 0; i < result.cs.rowCount; i++ ) {
                            var aplnsInfo = {"userId" : this.vdUtil.fn_getMeaValue(result, i, "Knox Approval All Group Line_UserId")
                                            ,"role" : this.vdUtil.fn_getMeaValue(result, i, "Knox Approval All Group Line_Role") //기안(0), 결재(1), 합의(2), 후결(3), 병렬합의(4), 병렬결재(7), 통보(9)(후결자는 최대 1명, 병렬결재 & 병렬합의자는 최소 2명 이상)
                                            ,"seq" : i + ""
                                            ,"aplnStatsCode" : "0"          //처리구분 미결(0), 결재(1), 반려(2), 전결(3), 자동결재(5)
                                            ,"aplnMdfyPmtYn" : "Y"          //경로변경권한여부
                                            ,"arbPmtYn" : "Y"               //전결권한여부
                                            ,"contentsMdfyPmtYn" : "Y"      //본문수정권한여부
                                         };
                            aplns.push(aplnsInfo);
                        }
                    }
                }
            } catch ( e ) {
                this.error(e.message);
            }

            return aplns;
        };

        // 2026.3.19 : 개인결 결재라인 정보
        fn_aplnsForUser(parsedParams) {
            var aplns = { groupCombo : [] };

            try {
                var version = this.vdUtil.fn_getFilterVersion(parsedParams);
                var versionName = this.vdUtil.fn_getFilterVersionName(parsedParams);
                var email = this.selectResult('CurrentUser().Name');

                var result = this.selectList([version
                                                ,"[Personnel].[Email].[" + email + "]"
                                                ,"[Seq].[Seq]"]
                                             ,["Measure.[Knox Approval Group_Name]"
                                                ,"Measure.[Knox Approval Group_Code]"]
                                             ,""
                                             ,"orderby Measure.[Knox Approval Group_Name]"
                                             ,"");
                for ( var i = 0; i < result.cs.rowCount; i++ ) {
                    var seq = this.vdUtil.fn_getDimValue(result, i, "Seq", "Seq");

                    // 결재 그룹 추가
                    var groupName = this.vdUtil.fn_getMeaValue(result, i, "Knox Approval Group_Name");
                    var groupCode = this.vdUtil.fn_getMeaValue(result, i, "Knox Approval Group_Code");
                    aplns.groupCombo.push({ "Name" : groupCode, "DisplayName" : groupName });
                    aplns[groupCode] = [];

                    // 결재 정보를 가져온다.
                    var sResult = this.selectList([version
                                                    ,"[Personnel].[Email].[" + email + "]"
                                                    ,"[Seq].[Seq].[" + seq + "]"
                                                    ,"[Seq1].[Seq1]"]
                                                 ,["Measure.[Knox Approval Group Line_UserId]"
                                                    ,"Measure.[Knox Approval Group Line_Role]"
                                                    ,"Measure.[Knox Approval Group Line_Order]"]
                                                 ,""
                                                 ,"orderby Measure.[Knox Approval Group Line_Order]"
                                                 ,"");
                    for ( var m = 0; m < sResult.cs.rowCount; m++ ) {
                        var aplnsInfo = {"userId" : this.vdUtil.fn_getMeaValue(sResult, m, "Knox Approval Group Line_UserId")
                                        ,"role" : this.vdUtil.fn_getMeaValue(sResult, m, "Knox Approval Group Line_Role") //기안(0), 결재(1), 합의(2), 후결(3), 병렬합의(4), 병렬결재(7), 통보(9)(후결자는 최대 1명, 병렬결재 & 병렬합의자는 최소 2명 이상)
                                        ,"seq" : m + ""
                                        ,"aplnStatsCode" : "0"          //처리구분 미결(0), 결재(1), 반려(2), 전결(3), 자동결재(5)
                                        ,"aplnMdfyPmtYn" : "Y"          //경로변경권한여부
                                        ,"arbPmtYn" : "Y"               //전결권한여부
                                        ,"contentsMdfyPmtYn" : "Y"      //본문수정권한여부
                                     };
                        aplns[groupCode].push(aplnsInfo);
                    }
                }
            } catch ( e ) {
                this.error(e.message);
            }

            return aplns;
        };

        // 2026.3.23 : 메일 수신자 정보
        fn_recipients(parsedParams) {
            var recipient = [];

            try {
                if ( parsedParams.fbParams["Knox Mail All Group_Code"] != "" ) {
                    var version = this.vdUtil.fn_getFilterVersion(parsedParams);
                    var versionName = this.vdUtil.fn_getFilterVersionName(parsedParams);

                    var result = this.selectList([version
                                                        ,"[Seq].[Seq]"]
                                                     ,["Measure.[Knox Mail All Group_Name]"]
                                                     ,'where { Measure.[Knox Mail All Group_Parent Code] == "' + parsedParams.fbParams["Measure.[Knox Mail All Group_Parent Code]"] + '" '
                                                            + ', Measure.[Knox Mail All Group_Code] == "' + parsedParams.fbParams["Measure.[Knox Mail All Group_Code]"] + '" }'
                                                     ,""
                                                     ,"");
                    if ( result.cs.rowCount > 0 ) {
                        var seq = this.vdUtil.fn_getDimValue(result, 0, "Seq", "Seq");

                        // 결재 정보를 가져온다.
                        result = this.selectList([version
                                                        ,"[Seq].[Seq].[" + seq + "]"
                                                        ,"[Seq1].[Seq1]"]
                                                     ,["Measure.[Knox Mail All Group Line_UserId]"
                                                        ,"Measure.[Knox Mail All Group Line_RecipientType]"]
                                                     ,""
                                                     ,""
                                                     ,"");
                        for ( var i = 0; i < result.cs.rowCount; i++ ) {
                            var recipientInfo = {"userId" : this.vdUtil.fn_getMeaValue(result, i, "Knox Mail All Group Line_UserId")
                                            ,"recipientType" : this.vdUtil.fn_getMeaValue(result, i, "Knox Mail All Group Line_RecipientType") //참조(CC), 비밀참조(BCC)
                                         };
                            recipient.push(recipientInfo);
                        }
                    }
                }
            } catch ( e ) {
                this.error(e.message);
            }

            return recipient;
        };


    }

    class VdUtil {
        fn_lpad(val, width, fillchar) {
            return val.padStart(width, fillchar);
        }
        fn_rpad(val, width, fillchar) {
            return val.padEnd(width, fillchar);
        }
        fn_getString(val) {
            if ( val == undefined || val == null )
                return "";
            else
                return val + "";
        }
        fn_nvl(val1, val2) {
            if ( val1 != null && val1 != "" )
                return val1;
            else
                return val2;
        }
        fn_isInt(val) {
            if ( val === null || val === "" || val === undefined )
                return false;
            else
                return !isNaN(val);
        }
        fn_filterStr(val) {
            // 데이타중에 " 이 있는 케이스가 있어서 변환
            if ( Array.isArray(val) ) {
                if ( val.length > 0 ) {
                    val = val.map(item => `${item}`.replace(/"/g,'\\"'));
                }
            } else {
                val = val.replace(/"/g,'\\"');
            }

            if ( Array.isArray(val) ) {
                if ( val.length > 0 ) {
                    return '.filter(#.Name in {' + val.map(item => `"${item}"`).join(",") + '})';
                } else {
                    return "";
                }
            } else if ( val != "" && val.indexOf("%") == -1 ) {
                return '.filter(#.Name == "' + val + '")';
            } else if ( (val.match(/%/g) || []).length > 0 ) {
                // 26.1.26 : % 가 들어간 경우는 정규식을 활용하도록 로직 추가
                var prefix = "";
                var postfix = "";
                if ( val.indexOf("%") == 0 && val.lastIndexOf("%") == val.length - 1 ) {
                    val = val.substr(1, val.length - 2);
                }
                if ( val.indexOf("%") == 0 ) {
                    postfix = "$";
                    val = val.substr(1);
                }
                if ( val.lastIndexOf("%") == val.length - 1 ) {
                    prefix = "^";
                    val = val.substr(0, val.length - 1);
                }

                return '.filter(#.Name containsregexp "' + prefix + val.replace(/%/g,".*") + postfix + '")';
            } else if ( val != "" && val.indexOf("%") == 0 && val.lastIndexOf("%") == val.length - 1 ) {
                // 26.1.26 : 위 로직으로 사용안함
                return '.filter(#.Name contains "' + val.replace(/%/g,"") + '")';
            } else if ( val != "" && val.indexOf("%") == 0 ) {
                // 26.1.26 : 위 로직으로 사용안함
                return '.filter(#.Name endswith "' + val.replace("%","") + '")';
            } else if ( val != "" && val.indexOf("%") == val.length - 1 ) {
                // 26.1.26 : 위 로직으로 사용안함
                return '.filter(#.Name startswith "' + val.replace("%","") + '")';
            } else {
                return "";
            }
        }
        // 2025.9.26 추가. 필터를 DisplayName 으로 사용
        fn_filterStrForDN(val) {
            // 데이타중에 " 이 있는 케이스가 있어서 변환
            if ( Array.isArray(val) ) {
                if ( val.length > 0 ) {
                    val = val.map(item => `${item}`.replace(/"/g,'\\"'));
                }
            } else {
                val = val.replace(/"/g,'\\"');
            }

            if ( Array.isArray(val) ) {
                if ( val.length > 0 ) {
                    return '.filter(#.DisplayName in {' + val.map(item => `"${item}"`).join(",") + '})';
                } else {
                    return "";
                }
            } else if ( val != "" && val.indexOf("%") == -1 ) {
                return '.filter(#.DisplayName == "' + val + '")';
            } else if ( (val.match(/%/g) || []).length > 0 ) {
                // 26.1.26 : % 가 들어간 경우는 정규식을 활용하도록 로직 추가
                var prefix = "";
                var postfix = "";
                if ( val.indexOf("%") == 0 && val.lastIndexOf("%") == val.length - 1 ) {
                    val = val.substr(1, val.length - 2);
                }
                if ( val.indexOf("%") == 0 ) {
                    postfix = "$";
                    val = val.substr(1);
                }
                if ( val.lastIndexOf("%") == val.length - 1 ) {
                    prefix = "^";
                    val = val.substr(0, val.length - 1);
                }

                return '.filter(#.DisplayName containsregexp "' + prefix + val.replace(/%/g,".*") + postfix + '")';
            } else if ( val != "" && val.indexOf("%") == 0 && val.lastIndexOf("%") == val.length - 1 ) {
                // 26.1.26 : 위 로직으로 사용안함
                return '.filter(#.DisplayName contains "' + val.replace(/%/g,"") + '")';
            } else if ( val != "" && val.indexOf("%") == 0 ) {
                // 26.1.26 : 위 로직으로 사용안함
                return '.filter(#.DisplayName endswith "' + val.replace("%","") + '")';
            } else if ( val != "" && val.indexOf("%") == val.length - 1 ) {
                // 26.1.26 : 위 로직으로 사용안함
                return '.filter(#.DisplayName startswith "' + val.replace("%","") + '")';
            } else {
                return "";
            }
        }
        // 2025.9.24 추가. 필터에 ~ 추가
        fn_notFilterStr(val) {
            // 데이타중에 " 이 있는 케이스가 있어서 변환
            if ( Array.isArray(val) ) {
                if ( val.length > 0 ) {
                    val = val.map(item => `${item}`.replace(/"/g,'\\"'));
                }
            } else {
                val = val.replace(/"/g,'\\"');
            }

            if ( Array.isArray(val) ) {
                if ( val.length > 0 ) {
                    return '.filter(~(#.Name in {' + val.map(item => `"${item}"`).join(",") + '}))';
                } else {
                    return "";
                }
            } else if ( val != "" && val.indexOf("%") == -1 ) {
                return '.filter(~(#.Name == "' + val + '"))';
            } else if ( (val.match(/%/g) || []).length > 0 ) {
                // 26.1.26 : % 가 들어간 경우는 정규식을 활용하도록 로직 추가
                var prefix = "";
                var postfix = "";
                if ( val.indexOf("%") == 0 && val.lastIndexOf("%") == val.length - 1 ) {
                    val = val.substr(1, val.length - 2);
                }
                if ( val.indexOf("%") == 0 ) {
                    postfix = "$";
                    val = val.substr(1);
                }
                if ( val.lastIndexOf("%") == val.length - 1 ) {
                    prefix = "^";
                    val = val.substr(0, val.length - 1);
                }

                return '.filter(~(#.Name containsregexp "' + prefix + val.replace(/%/g,".*") + postfix + '"))';
            } else if ( val != "" && val.indexOf("%") == 0 && val.lastIndexOf("%") == val.length - 1 ) {
                // 26.1.26 : 위 로직으로 사용안함
                return '.filter(~(#.Name contains "' + val.replace(/%/g,"") + '"))';
            } else if ( val != "" && val.indexOf("%") == 0 ) {
                // 26.1.26 : 위 로직으로 사용안함
                return '.filter(~(#.Name endswith "' + val.replace("%","") + '"))';
            } else if ( val != "" && val.indexOf("%") == val.length - 1 ) {
                // 26.1.26 : 위 로직으로 사용안함
                return '.filter(~(#.Name startswith "' + val.replace("%","") + '"))';
            } else {
                return "";
            }
        }

        /*
            var WeeklyMPEndDate = vdUtil.fn_dateAdd("2024-11-11", "week", 24);
        */
        fn_dateAdd(date, interval, units) {
            var ret = new Date(date);
            switch ( interval.toLowerCase() ) {
                case 'year'   :  ret.setFullYear(ret.getFullYear() + units);  break;
                case 'quarter':  ret.setMonth(ret.getMonth() + 3*units);  break;
                case 'month'  :  ret.setMonth(ret.getMonth() + units);  break;
                case 'week'   :  ret.setDate(ret.getDate() + 7*units);  break;
                case 'day'    :  ret.setDate(ret.getDate() + units);  break;
                case 'hour'   :  ret.setTime(ret.getTime() + units*3600000);  break;
                case 'minute' :  ret.setTime(ret.getTime() + units*60000);  break;
                case 'second' :  ret.setTime(ret.getTime() + units*1000);  break;
                default       :  ret = undefined;  break;
            }
            ret = ret.toJSON().substring(0,10);
            return ret;
        }
        fn_getDateString(dt) {
            var year = dt.getFullYear(); // 년도
            var month = dt.getMonth() + 1;  // 월
            var date = dt.getDate();  // 날짜

            return year + "-" + (month < 10 ? "0" : "" ) + month + "-" + (date < 10 ? "0" : "" ) + date;
        }
        /* val1 에 "," 를 사용해서 val2 를 붙인다. */
        fn_wordAppend(val1, val2) {
            if ( val1 == "" )
                return val2;
            else
                return val1 + "," + val2;
        }
        /* val1 에 val2 가 없다면 "," 를 사용해서 val2 를 붙인다. */
        fn_wordDistinctAppend(val1, val2) {
            if ( (val1 + ",").indexOf(val2 + ",") == -1 )
                return val1 + ( val1 == "" ? "" : "," ) + val2;
            else
                return val1;
        }

        /*
            2025.8.26 Append
            Dimension 쿼리 구성 : "[Location].[Location].[" + row["[Location].[Location]"] + "]"
        */
        fn_qDim(row, name, value) {
            if ( row === null ) {
                return name + this.fn_filterStr(value);
            } else if ( row[name] === undefined ) {
                return "";
            } else {
                return name + ( value === undefined ? this.fn_filterStr(row[name]) : this.fn_filterStr(value));
            }
        }
        /*
            2026.3.26 Append
            Dimension 쿼리 구성 : "[Location].[Location].[" + row["[Location].[Location]"] + "]"
        */
        fn_qDimWithDN(row, name, value) {
            if ( row === null ) {
                return name + this.fn_filterStrForDN(value);
            } else if ( row[name] === undefined ) {
                return "";
            } else {
                return name + ( value === undefined ? this.fn_filterStrForDN(row[name]) : this.fn_filterStrForDN(value));
            }
        }
        /*
            2025.8.26 Append
            String Measure 쿼리 구성 : 'Measure.[SET Frozen Period_PreFPSOP] = "' + row["Measure.[SET Frozen Period_PreFPSOP]"] + '";'
        */
        fn_qMeaStr(row, name, value) {
            // 데이타중에 " 이 있는 케이스가 있어서 변환
            if ( value != null ) {
                value = value.replace(/"/g,'\\"');
            }

            if ( row === null ) {
                if ( value === null ) {
                    return name + ' = Null;';
                } else {
                    return name + ' = "' + value + '";';
                }
            } else if ( row[name] === undefined ) {
                return "";
            } else {
                //return name + ' = "' + ( value == undefined ? row[name] : value ) + '";';
                return name + ' = ' + ( value === undefined ? ( row[name] === null ? 'Null' : '"' + row[name] + '"' ) : '"' + value + '"') + ';';
            }
        }
        /*
            2025.8.26 Append
            String Measure 쿼리 구성 : 'Measure.[SET Frozen Period_PreFPSOP] = ' + row["Measure.[SET Frozen Period_PreFPSOP]"] + ';'
        */
        fn_qMeaNotStr(row, name, value) {
            if ( row === null ) {
                if ( value === null ) {
                    return name + ' = Null;';
                } else {
                    return name + ' = ' + this.fn_blankNull(value) + ';';
                }
            } else if ( row[name] === undefined ) {
                return "";
            } else {
                //return name + ' = ' + ( value == undefined ? this.fn_undefinedNull(row[name]) : this.fn_undefinedNull(value) ) + ';';
                return name + ' = ' + ( value === undefined ? ( row[name] === null ? 'Null' : this.fn_blankNull(row[name]) ) : this.fn_blankNull(value) ) + ';';
            }
        }
        /*
            2025.8.26 Append
            Int Measure 쿼리 구성 : 'Measure.[SET Frozen Period_PreFPSOP] = ' + row["Measure.[SET Frozen Period_PreFPSOP]"] + ';'
        */
        fn_qMeaInt(row, name, value) {
            if ( row === null ) {
                if ( value === null ) {
                    return name + ' = Null;';
                } else {
                    return name + ' = ' + this.fn_blankNull(value) + ';';
                }
            } else if ( row[name] === undefined ) {
                return "";
            } else {
                //return name + ' = ' + ( value == undefined ? row[name] : value ) + ';';
                return name + ' = ' + ( value === undefined ? ( row[name] === null ? 'Null' : this.fn_blankNull(row[name]) ) : this.fn_blankNull(value) ) + ';';
            }
        }
        /*
            2025.8.26 Append : Name 을 넣는 함수
            수정자 Measure 쿼리 구성 : 'Measure.[SET Frozen Period_Init By] = CurrentUser().Name;'
        */
        fn_qMeaUpdateUser(name) {
            return name + ' = CurrentUser().Name;';
        }
        /*
            2025.9.26 Append : User Name 을 넣는 함수
            수정자 Measure 쿼리 구성 : 'Measure.[SET Frozen Period_Init By] = CurrentUser().[User Name];'
        */
        fn_qMeaUpdateUserName(name) {
            return name + ' = CurrentUser().[User Name];';
        }
        /*
            2025.8.26 Append
            수정일자 Measure 쿼리 구성 : 'Measure.[SET Frozen Period_Init Time] = dateadd(Now(),9,"hour");'
        */
        fn_qMeaUpdateTime(name) {
            //return name + ' = dateadd(Now(),9,"hour");';
            return name + ' = Now();';
        }
        /*
            2026.2.26 Append
            Version 에서 복사하는 Measure 구문을 생성
        */
        fn_qMeaForMerge(name, version) {
            return name + ' = ' + name + '@([Version].[Version Name].[' + version + ']);';
        }
        /*
            2025.8.26 Append
            Version 정보 가져오기 : fbParams 를 보고 없으면 필터를 본다.
        */
        fn_qDimVersionName(parsedParams) {
            /*
            if ( parsedParams["fbParams"] == undefined ) {
                var version = "[Version].[Version Name].[CWV_MP]";
                if ( this.fn_getVersion != undefined ) {
                    version = this.fn_getVersion();
                }

                return version;
            } else {
                if ( parsedParams.fbParams["[Version].[Version Name]"] == undefined ) {
                    var version = "[Version].[Version Name].[CWV_MP]";
                    if ( this.fn_getVersion != undefined ) {
                        version = this.fn_getVersion();
                    }

                    return version;
                } else {
                    return "[Version].[Version Name].[" + parsedParams.fbParams["[Version].[Version Name]"] + "]";
                }
            }
            */
            // 파라미터에서 Version 을 가져온다.
            var versionName = this.fn_getParamVersion(parsedParams);
            // 필터에서 Version 을 가져온다.
            if ( versionName == "" ) {
                versionName = this.fn_getFilterVersion(parsedParams);
            }

            return versionName;
        }
        /*
            2025.8.26 Append
            파라미터 가져오기. 없으면 빈 문자열을 넘긴다.
        */
        fn_getParam(parsedParams, param) {
            if ( parsedParams["fbParams"] == undefined ) {
                return "";
            } else {
                if ( parsedParams.fbParams[param] == undefined ) {
                    return "";
                } else {
                    return parsedParams.fbParams[param];
                }
            }
        }
        /*
            2026.1.21 Append
            파라미터 값을 가지고 Query를 만든다.
            결과 : [Version].[Version Name].[CWV_MP]
        */
        fn_getParamQuery(parsedParams, param) {
            if ( parsedParams["fbParams"] == undefined ) {
                return "";
            } else {
                if ( parsedParams.fbParams[param] == undefined ) {
                    return "";
                } else {
                    return param + ".[" + parsedParams.fbParams[param] + "]";
                }
            }
        }
        /*
            2026.1.21 : 파라미터 값을 가지고 Query를 만든다. 단 값이 없으면 빈 물자열을 넘긴다.
        */
        fn_getParamQuery2(parsedParams, param) {
            if ( parsedParams["fbParams"] == undefined ) {
                return "";
            } else {
                if ( parsedParams.fbParams[param] == undefined ) {
                    return "";
                } else {
                    if ( parsedParams.fbParams[param] == "" ) {
                        return "";
                    } else {
                        return param + ".[" + parsedParams.fbParams[param] + "]";
                    }
                }
            }
        }
        /*
            2025.8.27 Append
            값이 undefined 이면 Null 을 넘기는 함수(int, float 타입일때)
        */
        fn_undefinedNull(val) {
            if ( val == "undefined" || val === "" ) {
                return "null";
            } else {
                return val;
            }
        }
        /*
            2025.9.5 Append
            값이 "" 이면 Null 을 넘기는 함수(int, float 타입일때)
        */
        fn_blankNull(val) {
            if ( val === "" ) {
                return "Null";
            } else {
                return val;
            }
        }
        /*
            2025.8.27 Append
            필터값을 가져온다.
        */
        fn_getFilter(parsedParams, filterStr) {
            if ( parsedParams["fbParams"] == undefined ) {
                return "";
            } else {
                if ( parsedParams.fbParams["filters"] == undefined ) {
                    return "";
                } else {
                    if ( parsedParams.fbParams.filters[filterStr] == undefined ) {
                        return "";
                    } else {
                        return parsedParams.fbParams.filters[filterStr];
                    }
                }
            }
        }
        /*
            2025.8.27 Append
            필터의 선택한 값을 가져온다.
        */
        fn_getFilterValue(parsedParams, filterStr) {
            var filterInfo = this.fn_getFilter(parsedParams, filterStr);

            if ( filterInfo == "" ) {
                return [];
            } else {
                return filterInfo["SelectedMembers"];
            }
        }
        /*
            2025.8.27 Append
            필터의 NamedSet 을 가져온다.
        */
        fn_getFilterNs(parsedParams, filterStr) {
             var filterInfo = this.fn_getFilter(parsedParams, filterStr);

            if ( filterInfo == "" ) {
                return [];
            } else {
                return filterInfo["MemberFilter"];
            }
        }
        /*
            2025.8.27 Append
            필터의 Query 구문을 가져온다. 값이 없어도 Dimension 은 구성해줌
        */
        fn_getFilterQuery(parsedParams, filterStr) {
             var filterInfo = this.fn_getFilter(parsedParams, filterStr);

            if ( filterInfo == "" ) {
                return "";
            } else {
                if ( filterInfo["MemberFilter"] == "" ) {
                    return filterStr + this.fn_filterStr(filterInfo["SelectedMembers"]);
                } else {
                    return filterInfo["MemberFilter"] + this.fn_filterStr(filterInfo["SelectedMembers"]);
                }
            }
        }
        /*
            2025.9.19 Append
            필터의 Query 구문을 가져온다.
            - MemberFilter, SelectedMembers 에 값이 없으면 빈 문자열을 넘긴다.
            - 추가할 필요가 없을 때 사용
        */
        fn_getFilterQuery2(parsedParams, filterStr) {
            var filterInfo = this.fn_getFilter(parsedParams, filterStr);

            if ( filterInfo == "" ) {
                return "";
            } else {
                if ( filterInfo["MemberFilter"] == "" && filterInfo["SelectedMembers"].length == 0 ) {
                    return "";
                } else {
                    if ( filterInfo["MemberFilter"] == "" ) {
                        return filterStr + this.fn_filterStr(filterInfo["SelectedMembers"]);
                    } else {
                        return filterInfo["MemberFilter"] + this.fn_filterStr(filterInfo["SelectedMembers"]);
                    }
                }
            }
        }
        /*
            2026.2.23 Append
            필터에 있는 첫번째 [Version].[Version Name].[CWV_MP] 을 가져온다.
        */
        fn_getFilterVersion(parsedParams) {
            var values = this.fn_getFilterValue(parsedParams, "[Version].[Version Name]");

            if ( values.length > 0 ) {
                return "[Version].[Version Name].[" + values[0] + "]";
            } else {
                return "";
            }
        }
        /*
            2026.2.23 Append
            필터에 있는 첫번째 CWV_MP 을 가져온다.
        */
        fn_getFilterVersionName(parsedParams) {
            var values = this.fn_getFilterValue(parsedParams, "[Version].[Version Name]");

            if ( values.length > 0 ) {
                return values[0];
            } else {
                return "";
            }
        }
        /*
            2025.9.25 Append
            result 에 Dimension의 Name 을 가져오기
        */
        fn_getDimValue(result, idx, dimension, attribute) {
            return result.cs.row(idx).cell(result.cs.memberColumnIndex(dimension, attribute)).Name;
        }
        /*
            2026.1.7 Append
            result 에 Dimension 의 DisplayName 을 가져오기
            기본은 DisplayAlias 를 먼저 체크해서 넘겨준다.
        */
        fn_getDimDisplayName(result, idx, dimension, attribute, isUseDisplayAlias) {
            var displayName = result.cs.row(idx).cell(result.cs.memberColumnIndex(dimension, attribute)).DisplayName;
            var displayAlias = result.cs.row(idx).cell(result.cs.memberColumnIndex(dimension, attribute)).DisplayAlias;

            if ( isUseDisplayAlias == undefined || isUseDisplayAlias == true ) {
                if ( displayAlias != null && displayAlias != "" ) {
                    return displayAlias;
                } else {
                    return displayName;
                }
            } else {
                return displayName;
            }
        }
        /*
            2026.1.7 Append
            result 에 Dimension 의 DisplayAlias 을 가져오기
        */
        fn_getDimDisplayAlias(result, idx, dimension, attribute) {
            return result.cs.row(idx).cell(result.cs.memberColumnIndex(dimension, attribute)).DisplayAlias;
        }
        /*
            2025.9.25 Append
            result 에 Measure 가져오기
        */
        fn_getMeaValue(result, idx, measure) {
            return result.cs.row(idx).cell(result.cs.measureColumnIndex(measure));
        }
        /*
            2025.11.18 Append
            result 에 Dimension 의 Property 가져오기
        */
        fn_getDimPropertyValue(result, idx, dimension, attribute, property) {
            if ( idx < result.cs.rowCount ) {
                var memberObject = result.cs.row(idx).cell(result.cs.memberColumnIndex(dimension, attribute));

                if ( memberObject.MemberProperties && Array.isArray(memberObject.MemberProperties) ) {
                    for ( var k = 0; k < memberObject.MemberProperties.length; k++ ) {
                        var propertyItem = memberObject.MemberProperties[k];
                        if ( propertyItem.PropertyName && propertyItem.PropertyName === property ) {
                            return propertyItem.PropertyValue;
                        }
                    }
                }
            } else {
                return "";
            }
        }

        // 26.01.05 JSEWCommonVD 함수를 공통으로 뺌 : Dimension 에 includeField의 정보를 추가한다.
        fn_addIncludeField(dims, parsedParams) {
            if ( parsedParams.fbParams["includeField"] != "" ) {
                // 필터에 where 에서 뺄 대상을 추가할 배열
                parsedParams.fbParams["filterExistGrain"] = [];

                var includeField = parsedParams.fbParams.includeField.split(",");
                for ( var i = 0; i < includeField.length; i++ ) {
                    var tSplit = includeField[i].split(":");

                    // 2025-11-24 : attribute 에 attribute^property 형태로 넣은 경우 로직 추가
                    var attrSplit = tSplit[1].split("^");

                    if ( parsedParams.fbParams["filters"] != undefined &&
                            parsedParams.fbParams["filterDimension"] != undefined &&
                            parsedParams.fbParams["filterDimension"].length > 0 &&
                            parsedParams.fbParams.filters["[" + tSplit[0] + "].[" + attrSplit[0] + "]"] != undefined ) {
                        // 필터를 반영한 로직
                        var filter = this.fn_getFilterQuery(parsedParams, "[" + tSplit[0] + "].[" + attrSplit[0] + "]");

                        // 파라미터를 반영
                        if ( parsedParams.fbParams["[" + tSplit[0] + "].[" + attrSplit[0] + "]"] != undefined ) {
                            filter += this.fn_filterStr(parsedParams.fbParams["[" + tSplit[0] + "].[" + attrSplit[0] + "]"]);
                        }

                        dims.push(filter);
                    } else {
                        // 필터를 반영 안하는 로직
                        var value = "";

                        // 파라미터를 반영
                        if ( parsedParams.fbParams["[" + tSplit[0] + "].[" + attrSplit[0] + "]"] != undefined ) {
                            value += this.fn_filterStr(parsedParams.fbParams["[" + tSplit[0] + "].[" + attrSplit[0] + "]"]);
                        }

                        dims.push("[" + tSplit[0] + "].[" + attrSplit[0] + "]" + value);
                    }

                    // 필터에 where 에서 뺄 대상을 추가한다.
                    parsedParams.fbParams.filterExistGrain.push("[" + tSplit[0] + "].[" + attrSplit[0] + "]");
                }
            }

            return dims;
        }

        // 26.01.05 JSEWCommonVD 함수를 공통으로 뺌 : Measure.[ABC] 에서 ABC 만 가져오는 함수
        fn_getMeasureName(measure) {
            var measureSplit = measure.split(".");
            return measureSplit[1].replace("[", "").replace("]", "")
        }

        // 26.01.05 JSEWCommonVD 함수를 공통으로 뺌 : where 절 생성
        fn_makeWhere(parsedParams, otherWhere) {
            var whereStr = "";

            // 로직에 있는 where 조건 반영
            if ( otherWhere != undefined ) {
                //for ( var i = 0; i < otherWhere.length; i++ ) {
                //    whereStr += ( whereStr == "" ? "" : ", " ) + otherWhere[i];
                //}
                whereStr = otherWhere.join(", ");
            }

            // filter를 위한 where 절 생성
            var filterWhere = this.fn_makeFilterWhere(parsedParams);
            if ( filterWhere.length > 0 ) {
                whereStr += ( whereStr == "" ? "" : ", " ) + filterWhere.join(", ");
            }

            // 파라미터에 있는 where 조건 반영
            var where = parsedParams.fbParams["where"];
            for ( let key in where ) {
                whereStr += ( whereStr == "" ? "" : ", " ) + key + this.fn_filterStr(where[key]);
            }

            if ( whereStr == "" ) {
                return "";
            } else {
                return "where { " + whereStr + " } ";
            }
        }

        // 26.01.05 JSEWCommonVD 함수를 공통으로 뺌 : filter를 위한 where 절 생성
        fn_makeFilterWhere(parsedParams) {
            var filtersArr = [];

            // filters 가 있어야 하고, filterDimension 에 필터를 적용할 Dimension 이 있어야함.
            if ( parsedParams.fbParams["filters"] != undefined && parsedParams.fbParams["filterDimension"] != undefined) {
                var filterDimension = parsedParams.fbParams.filterDimension;
                var filterExistGrain = [];
                if ( parsedParams.fbParams["filterExistGrain"] != undefined ) {
                    filterExistGrain = parsedParams.fbParams.filterExistGrain;
                }

                var filters = parsedParams.fbParams["filters"];
                for ( let key in filters ) {
                    if ( filterDimension.includes(key.split(".")[0]) && !filterExistGrain.includes(key) ) {
                        filtersArr.push(this.fn_getFilterQuery(parsedParams, key));
                    }
                }
            }

            return filtersArr;
        }

        /*
            2026.1.8 Append
            스트링을 Float로 변경. 오류가 나면 0을 리턴
        */
        fn_stringToFloat(val) {
            var rtn = 0;

            try {
                rtn = parseFloat(val);
            } catch ( e ) {
            }

            return rtn;
        }

        // 2026.03.03 : Dimension 쿼리에서 값만 가져온다.
        fn_getDimensionValue(dimension) {
            var split = dimension.split(".");

            if ( split.length == 3 ) {
                return split[2].replace("[", "").replace("]", "");
            } else {
                return "";
            }
        }

        // 2026.03.03 : Dimension 쿼리에서 Dimension만 가져온다.
        fn_getDimensionName(dimension) {
            var split = dimension.split(".");

            return split[0] + "." + split[1];
        }

        /*
            2026.3.3 Append : Param 에 있는 Version 을 가져온다.
        */
        fn_getParamVersion(parsedParams) {
            var value = this.fn_getParam(parsedParams, "[Version].[Version Name]");

            if ( value != "" ) {
                return "[Version].[Version Name].[" + value + "]";
            } else {
                return "";
            }
        }
    }

    var NSCMCommon = VdCommon;
    var NSCMUtil = VdUtil;

    return {VdCommon, VdUtil, NSCMCommon, NSCMUtil};
});

/**************************** o9.NSCM.commonLib ****************************
    2024-11-13 : 콤보 구성시 - 데이타 제거
    2025-03-17 : fn_getDateString 함수 추가
    2025-04-18 : VdUtil.fn_wordAppend, VdUtil.fn_wordDistinctAppend 추가
    2025-07-11 : updateBlockMeasure, updateBlockMeasureQuery 추가 - 대량 데이타 생성시 기본 값(1건)으로 Measure를 생성하고 나머지는 Block Scope 로 생성
    2025-07-18 : 소스 전사 사용을 위한 NSCMCommon, NSCMUtil 변수 생성
    2025-07-22 : fn_loadFunction 관련 로그는 남기지 않도록 변경
                 로그를 print 할때 Info, Error 로 분리함
                 selectQuery, fn_decorator, fn_getUserId 추가
                 fn_makeCombo 에서 includeField 가 있으면 중복이 허용 되도록 수정
    2025-08-20 : fn_makeCombo 에서
                    existBlank 추가
                    includeField 가 있을때 조건값이 들어가면 Filer 가 되도록 수정
                    includeField 가 있을때 DisplayName, DisplayAlias 도 추가해줌
    2025-08-22 : Dimension, Measure 구문을 생성하는 함수 생성
    2025-09-24 : fn_notFilterStr 추가
    2025-09-25 : fn_getDimValue, fn_getDimValue 추가
    2025-09-30 : fn_filterStr 에서 val 중에 " 이 들어간 케이스에 대한 변경 작업 추가.
                    " 를 \" 로 변경
    2025-11-07 : fn_notFilterStr 에서 배열로 넘어올때 비어 있을 경우 오류가 나서 수정
    2025-11-12 : fn_getString 에서 스트링이 아닌경우에 "" 를 붙여서 스트링으로 변경하도록 수정
    2025-11-18 : fn_getDimPropertyValue 추가
    2025-11-24 : fn_makeCombo 에서 : attribute 에 attribute^property 형태로 넣을 수 있게 수정
                    { "fbFuncName" : "fn_cb_siteMFMtrl","fbParams" : {"includeField" : "Location:Company:Company,Location:Region^Region Sorting Order:RegionOrder" ,"where" : { "Location.[All Location]" : "All" }, "limit" : 10 ,"existAll" : true} }
    2025-11-25 : fn_makeCombo 에서 : existHyphen 옵션 기능 추가
    2025-11-26 : fn_makeCombo 에서 : CO 의 경우 All 대신에 ALL 을 사용해서 옵션 추가
                 fn_makeCombo 에서 : 사업부별 분기 로직을 반영하도록 로직 추가
    2025-12-09 : fn_makeCombo 에서 : 해당 Dimension 의 Property 를 가져오는 파라미터 추가
    2026-01-05 : JSEWCommonVD 에 있는 함수를 공통으로 옮김
                    fn_addIncludeField, fn_getMeasureName, fn_makeWhere, fn_makeFilterWhere
    2026-01-07 : fn_getDimDisplayName, fn_getDimDisplayAlias 추가
    2026-01-08 : fn_stringToFloat 추가
    2026-01-12 : fn_dataUpload 추가
    2026-01-21 : fn_getParamQuery 추가
    2026-01-26 : fn_filterStr 에서 정규식 검색이 되도록 수정
    2026-02-23 : fn_getFilterVersion 추가
    2026-02-26 : fn_mergeUser 추가
    2026-03-03 : fn_getDimensionValue, fn_getDimensionName 추가
    2026-03-17 : fn_division - division 을 소스가 아닌 o9 에서 가져와서 사용하도록 변경, 쿼리 로그를 안남기기 위해서 공통함수를 사용 안함
    2026-03-19 : fn_aplns, fn_aplnsForUser, fn_recipients 추가
    2026-03-26 : fn_qDimWithDN 추가
**************************** o9.NSCM.commonLib ****************************/