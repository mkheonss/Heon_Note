// ###############################
// o9 개발시 참고
// ###############################

// ###############################
// EW 개발시 참고
// ###############################

    // 26.3.11 : { "fbFuncName" : "fn_cb_siteDCwithKD" }
    var fn_cb_siteDCwithKD = function(parsedParams){
        const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);     // Parameter 전달
        vdCommon.setLogLevel("Debug");


        try {
            vdCommon.printParams(parsedParams);

		    var dims = ['&NSUIToLocationDC.unionwith(&NSUIToLocationwithKD)'];

            // filter를 적용할 Dimension 설정
            if ( parsedParams.fbParams["filterDimension"] == undefined ) {
                parsedParams.fbParams["filterDimension"] = ["[To Location]"];
            }

		    // Casecade 를 위해서 Dimension 추가
		    dims = vdUtil.fn_addIncludeField(dims, parsedParams);

            var result = vdCommon.selectList(dims, [], vdUtil.fn_makeWhere(parsedParams), "", parsedParams.fbParams.limit);
            //vdCommon.printCsData(result, 3);
            var comboList = vdCommon.fn_makeCombo(result, {DimName : "To Location", DimAttbName : "To Location", Sort : "DisplayName",
                                                    includeField : parsedParams.fbParams.includeField,
                                                    includeProperty : parsedParams.fbParams.includeProperty,
                                                    existAll : parsedParams.fbParams.existAll,
                                                    existBlank : parsedParams.fbParams.existBlank,
                                                    existHyphen : parsedParams.fbParams.existHyphen});
            vdCommon.debug("ComboData : " + JSON.stringify(comboList.slice(0,3)));

            vdCommon.programEnd();

            return { "Code" : 0, "Msg" : "", "Rows" : comboList };
        } catch ( e ) {
            vdCommon.error(e.message);
            return { "Code" : -1, "Msg" : e.message };
        }

    };
