define('o9.NSCM.commonLibCO', ['o9.NSCM.commonLib'], function (commonLib) {
    // 사업부별 로직 추가 ( prefix : VD, DA, MX, DP, CO )
    class COCommon extends commonLib.NSCMCommon{
        constructor(programName) {
            super(programName);
        }

        // 추가 기능을 정의 한다.
        fn_getUserName() {
            return this.selectResult("CurrentUser().[Name]");
        }

        // 2025-11-26 : 사업부 코드로 로직 분기를 위해 추가
        fn_getDivision() {
            return "CO";
        }

        // 추가 기능을 정의 한다.
        //fn_function() {
            //.......
        //}
				
				
				/*
					@Override	Location Display 표시 내용에 따라 다르게 표시 되서 확인이 필요
				
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
        fn_makeCombo_deprecated(result, param) {
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

                        // 25.8.22 : DisplayName을 다른 Attribute에서 조회 할 경우
                        if ( param["DimDisplayAttbName"] != undefined && param["DimDisplayAttbName"] ) {
                            // 25.8.22 : DisplayName을 다른 Attribute의 Property에서 조회 할 경우
                            if ( param["DimDisplayPropertyName"] != undefined && param["DimDisplayPropertyName"] ) {
                                _displayName = this.getPropertyValue(result.cs, i, param["DimName"], param["DimDisplayAttbName"], param["DimDisplayPropertyName"]);
                                _displayAlias = this.getPropertyValue(result.cs, i, param["DimName"], param["DimDisplayAttbName"], param["DimDisplayPropertyName"]);
                            } else {
                                _displayName = result.cs.row(i).cell(result.cs.memberColumnIndex(param["DimName"], param["DimDisplayAttbName"])).DisplayName;
                                _displayAlias = result.cs.row(i).cell(result.cs.memberColumnIndex(param["DimName"], param["DimDisplayAttbName"])).DisplayAlias;
                            }
                        } else {
                            // 25.8.22 : DisplayName을 Property에서 조회 할 경우
                            if ( param["DimDisplayPropertyName"] != undefined && param["DimDisplayPropertyName"] ) {
                                _displayName = this.getPropertyValue(result.cs, i, param["DimName"], param["DimAttbName"], param["DimDisplayPropertyName"]);
                                _displayAlias = this.getPropertyValue(result.cs, i, param["DimName"], param["DimAttbName"], param["DimDisplayPropertyName"]);
                            } else {
                                _displayName = result.cs.row(i).cell(result.cs.memberColumnIndex(param["DimName"], param["DimAttbName"])).DisplayName;
                                _displayAlias = result.cs.row(i).cell(result.cs.memberColumnIndex(param["DimName"], param["DimAttbName"])).DisplayAlias;
                            }
                        }

                        // 25.6.27 Location.[Location], To Location.[To Location], Sub Location.[Sub Location] 경우에는
                        // _displayAlias 을 다른 곳에서 가져온다. ( 예외 케이스 )
                        //if ( param["DimName"] == "Location" && param["DimAttbName"] == "Location" ) {
                        //    _displayAlias = this.getPropertyValue(result.cs, i, param["DimName"], param["DimAttbName"], "Location Site ID");
                        //}
                        if ( param["DimName"] == "Sub Location" && param["DimAttbName"] == "Sub Location" ) {
                            _displayAlias = this.getPropertyValue(result.cs, i, param["DimName"], param["DimAttbName"], "Sub Location Name");
                        }
												//if ( param["DimName"] == "EOL Group" && param["DimAttbName"] == "EOL Group ID" ) {
                        //    //_displayAlias = this.getPropertyValue(result.cs, i, param["DimName"], param["DimAttbName"], "EOL Group Description");
												//		_displayAlias = result.cs.row(i).cell(result.cs.memberColumnIndex("EOL Group", "EOL Group Description")).Name;
                        //}
                        //if ( param["DimName"] == "To Location" && param["DimAttbName"] == "To Location" ) {
                        //    _displayAlias = this.getPropertyValue(result.cs, i, param["DimName"], param["DimAttbName"], "To Location Site ID");
                        //}
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

                    // Lookup 기능을 위해 includeField 가 있으면 중복 허용
                    var allowDuplicate = false;
                    if ( param["includeField"] != undefined && param["includeField"] != "" ) {
                        allowDuplicate = true;
                    }

                    if ( (allowDuplicate == false && validHashMap[name] == undefined) || allowDuplicate == true ) {
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

    // 사업부별 로직 추가 ( prefix : VD, DA, MX, DP, CO )
    class COUtil extends commonLib.NSCMUtil {
        // Dimension 에 includeField의 정보를 추가한다.
        fn_addincludeField(dims, parsedParams) {
            if ( parsedParams.fbParams["includeField"] != "" ) {
                var includeField = parsedParams.fbParams.includeField.split(",");
                for ( var i = 0; i < includeField.length; i++ ) {
                    var tSplit = includeField[i].split(":");
                    dims.push("[" + tSplit[0] + "].[" + tSplit[1] + "]");
                }
            }

            return dims;
        }

        // where 정 생성
        fn_makeWhere(parsedParams, whereStr = "") {
            const where = parsedParams.fbParams["where"];
            for ( let key in where ) {
                whereStr += ( whereStr == "" ? "" : ", " ) + key + this.fn_filterStr(where[key]);
            }

            if ( whereStr == "" ) {
                return "";
            } else {
                return "where { " + whereStr + " } ";
            }
        }

        fn_makeClauseWithFilter(dimension, param, isSelect = false) {
            if (param.fbParams.filters === undefined || param.fbParams.filters.length === 0) {
                return "";
            }

            const filters = Object.entries(param.fbParams.filters)
                            .filter(([key, _]) => key.startsWith(`[${dimension}]`))
                            .reduce((obj, [key, value]) => {
                                obj[key] = value;
                                return obj;
                            }, {});

            const clause = [];
            Object.entries(filters).forEach(([key, value]) => {
                if (value.MemberFilter !== "") {
                    clause.push(`${value.MemberFilter}${value.SelectedMembers.length > 0 ? `.filter(#.Name in {${value.SelectedMembers.map(v => `"${v}"`).join()}})` : ""}`)
                } else if (key.startsWith("[Time]")) {
                    clause.push(`${key}${value.SelectedMembers.length > 0 ? `.filter(#.Name in {${value.SelectedMembers.map(v => `"${v}"`).join()}})` : ""}`)
                }
            });

            return isSelect ? clause : clause.join();
        }
    }

    return {COCommon, COUtil};
});