define('o9.NSCM.commonLib', ['o9/data/query', 'o9/data/cellset'], function () {
    const queryModule = require('o9/data/query');
    const cellsetModule = require('o9/data/cellset');

    class VdCommon {
        constructor(_programName) {
            this.programName = _programName;
            this.preFix = "[NSCM-Javascript-LOG]";
            this.errorPreFix = "[NSCM-Javascript-LOG-ERROR]";
            this.setLogLevel("Info");

            this.startTime = new Date();
            this.stepTime = this.startTime;

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
            this.debug("O9 Params : " + JSON.stringify(JSON.parse(params)));
        }
        printStep(msg) {
            this.info("Step : " + msg);
        }
        programStart() {
            if ( this.programName.indexOf("fn_loadFunction") == -1 ) {
                this.info("============== Javasrcipt Start ( Version : 2025-07-18 ) ==============");
            }
        }
        programEnd() {
            if ( this.programName.indexOf("fn_loadFunction") == -1 ) {
                this.info("============================ Javasrcipt End ============================");
            }
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
                        query += ' ' + dimension[i] + ' = {' + value[i].substr(2) + ',}' + (i < dimension.length - 1 ? "," : "");
                    } else {
                        query += ' ' + dimension[i] + ' = {,' + value[i] + '}' + (i < dimension.length - 1 ? "," : "");
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
         *
         * @returns {object} - An object containing two properties:
         *                    - cs: The cell set obtained from executing the query.
         *                    - columns: An object containing arrays of selected dimensions and measures.
         *                                The dimensions are stored in the "dimension" property of "columns".
         *                                The measures are stored in the "measure" property of "columns".
         */
        selectList(dimension, measure, where, orderby, limit) {
            try {
                var query = '';
                var measureQuery = "";

                if ( measure.length > 0 )
                    measureQuery = '{' + measure.join(',') + '}';
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
                if ( !this.existMember('[Python Batch].[Python Name]', pythonName) ) {
                    this.createMember('[Python Batch].[Python Name]', pythonName);
                }

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
                        if ( param["DimName"] == "Location" && param["DimAttbName"] == "Location" ) {
                            _displayAlias = this.getPropertyValue(result.cs, i, param["DimName"], param["DimAttbName"], "Location Site ID");
                        }
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
                return val;
        }
        fn_nvl(val1, val2) {
            if ( val1 != null && val1 != "" )
                return val1;
            else
                return val2;
        }
        fn_isInt(val) {
            if ( val == null || val == "" || val == undefined )
                return false;
            else
                return !isNaN(val);
        }
        fn_filterStr(val) {
            if ( val == "All" ) {
                return "";
            } else if ( Array.isArray(val) && val.length > 0 ) {
                return '.filter(#.Name in {' + val.map(item => `"${item}"`).join(",") + '})';
            } else if ( val != "" && val.indexOf("%") == -1 ) {
                return '.filter(#.Name == "' + val + '")';
            } else if ( val != "" && val.indexOf("%") == 0 && val.lastIndexOf("%") == val.length - 1 ) {
                return '.filter(#.Name contains "' + val.replace(/%/g,"") + '")';
            } else if ( val != "" && val.indexOf("%") == 0 ) {
                return '.filter(#.Name endswith "' + val.replace("%","") + '")';
            } else if ( val != "" && val.indexOf("%") == val.length - 1 ) {
                return '.filter(#.Name startswith "' + val.replace("%","") + '")';
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
            else    ``
                return val1 + "," + val2;
        }
        /* val1 에 val2 가 없다면 "," 를 사용해서 val2 를 붙인다. */
        fn_wordDistinctAppend(val1, val2) {
            if ( (val1 + ",").indexOf(val2 + ",") == -1 )
                return val1 + ( val1 == "" ? "" : "," ) + val2;
            else
                return val1;
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
*********************************************************************/