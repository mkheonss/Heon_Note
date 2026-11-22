define('o9.vd.zz1CommonLib', ['o9/data/query', 'o9/data/cellset'], function () {

    const queryModule = require('o9/data/query');
    const cellsetModule = require('o9/data/cellset');

    class VdCommon {
        constructor(_programName) {
            this.programName = _programName;
            this.preFix = "[NSCM-Javascript-LOG]";
            this.errorPreFix = "[NSCM-Javascript-LOG-ERROR]";
            this.setLogLevel("Info");

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
        print(msg, logLevel) {
            if ( this.logLevelToInt(logLevel) >= this.logLevel) {
                Log.Info((logLevel == "Error" ? this.errorPreFix : this.preFix) + "[" + this.programName + "]" + "[" + logLevel + "]" + " ===> " + msg);
            }
        }
        printParams(params) {
            this.debug("O9 Params : " + JSON.stringify(JSON.parse(params)));
        }
        printStep(msg) {
            this.info("Step : " + msg);
        }
        programStart() {
            this.info("============================================================");
            this.info("Javasrcipt Start");
        }
        programEnd() {
            this.info("Javasrcipt End");
            this.info("============================================================");
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
                    if ( value[i].substr(0, 1) == "P") {
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
                var query = '(Select (' + dimension.join('*') + ') on row, ({' + measure.join(',') + '}) on column ' + where + ').count;';
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
                var query = 'scope:(' + dimension.join('*') + ');' + measure.join(' ') + ' end scope;';
                this.debug("updateMeasure Query : " + query);
                queryModule.update(query);
            } catch ( e ) {
                this.error(e.message);
                throw e;
            }
        }

        /**
         * Deletes data for the given dimension and measure group.
         *
         * @param {Array<string>} dimension - The dimension(s) to delete data for.
         * @param {string} measureGroup - The measure group to delete data from.
         *
         * @throws {Error} If an error occurs during the deletion process.
         */
        deleteMeasure(where, measureGroup) {
            try {
                var query = 'delete data for model [' + measureGroup + '] where {' + where.join(",") + '};';
                this.debug("deleteMeasure Query : " + query);
                queryModule.update(query);
            } catch ( e ) {
                this.error(e.message);
                throw e;
            }
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
                if ( measure.length > 0 )
                    query = 'Select (' + dimension.join('*') + ') on row, ({' + measure.join(',') + '}) on column ' + where + ' ' + orderby + ' ' + limit + ";";
                else
                    query = 'Select (' + dimension.join('*') + ') on row, () on column ' + where + ' ' + orderby + ' ' + limit + ";";

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
                let selectResult = cellsetModule.createCellSet(queryModule.select(query));
                let selectResultCount = selectResult.rowCount;
                this.debug(`${fName} > selectResult : ${JSON.stringify(selectResult)}`);
                this.debug(`${fName} > selectResultCount : ${selectResultCount}`);
                return {rowCount : selectResultCount, cs : selectResult, columns : this.getCsColumns(selectResult.Meta)}

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
            for ( var i = 0; i < meta.length; i++ ) {
                if ( meta[i].DimensionName != undefined ) {
                    dimension.push(meta[i].DimensionName + "." + meta[i].AttributeName);
                } else {
                    measure.push(meta[i].Name);
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
        fn_nvl(val, replaceVal) {
            if ( val == null || val == "" )
                return replaceVal;
            else
                return val;
        }
    }

    return {VdCommon, VdUtil};
});