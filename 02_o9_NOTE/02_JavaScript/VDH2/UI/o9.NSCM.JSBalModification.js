define('o9.NSCM.JSBalModification', ['o9/data/query', 'o9/data/cellset', 'o9.NSCM.commonLibVD'], function () {
	const programName = "o9.NSCM.JSBalModification";
    const commonLib = require('o9.NSCM.commonLib');
    const vdUtil = new commonLib.VdUtil();
    const log = new commonLib.VdCommon(programName);
    log.setLogLevel("Debug");

    var fn_cb_location = function(o9Params){
        const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
        vdCommon.setLogLevel("Debug");
        vdCommon.printParams(o9Params);

        try {
            // 파라메타 가져오기
            let parsedParams = JSON.parse(o9Params);

            var result = vdCommon.selectList(["[Location].[Location]"], ["Measure.[W Demand Quantity to SCS]"]
                                                ,"where { Version.[Version Name]" + vdUtil.fn_filterStr(parsedParams.fb_Version) +
                                                    ", Measure.[W Demand Quantity to SCS] > 0 } "
                                                ,"", "");
            var comboList = vdCommon.fn_makeCombo(result, {DimName : "Location", DimAttbName : "Location"
                                                            ,Sort : "DisplayName"
                                                            ,isDisplayNameWithCode : true
                                                            ,existAll : true});

            vdCommon.debug("ComboData : " + JSON.stringify(comboList.slice(0,3)));

            vdCommon.programEnd();

            return comboList;
        } catch ( e ) {
            RuleOutputToUI = { Status : 'Error', Message : "Js Logic Error : " + e.message };
            return;
        }
    };

    var fn_cb_scmType = function(o9Params){
        const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
        vdCommon.setLogLevel("Debug");
        vdCommon.printParams(o9Params);

        try {
            // 파라메타 가져오기
            let parsedParams = JSON.parse(o9Params);
            var fbSourceVersion = parsedParams.fb_Version;

            var result = vdCommon.selectList(["[Item].[SCM Type]"], []
                                                ,"where {[Version].[Version Name].[" + fbSourceVersion +
                                                    "], Measure.[W Demand Quantity to SCS] > 0 } "
                                                ,"", "");

            var comboList = vdCommon.fn_makeCombo(result, {DimName : "Item", DimAttbName : "SCM Type"
                                                            ,Sort : "DisplayName"
                                                            ,existAll : true});

            vdCommon.debug("ComboData : " + JSON.stringify(comboList.slice(0,3)));

            vdCommon.programEnd();

            return comboList;
        } catch ( e ) {
            RuleOutputToUI = { Status : 'Error', Message : "Js Logic Error : " + e.message };
            return;
        }
    };

    var fn_cb_productGroup = function(o9Params){
        const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
        vdCommon.setLogLevel("Debug");
        vdCommon.printParams(o9Params);

        try {
            // 파라메타 가져오기
            let parsedParams = JSON.parse(o9Params);
            var fbSourceVersion = parsedParams.fb_Version;

            var result = vdCommon.selectList(["[Item].[Product Group]"]
                                             ,[]
                                             ,"where {" +
                                                    ["[Item].[SCM Type]" + fn_localFilter(parsedParams.fb_ScmType)].join(",") +
                                                ", [Version].[Version Name].[" + fbSourceVersion + "], Measure.[W Demand Quantity to SCS] > 0 } "
                                             , "", "");
            var comboList = vdCommon.fn_makeCombo(result, {DimName : "Item", DimAttbName : "Product Group"
                                                            ,Sort : "DisplayName"
                                                            ,existAll : true});

            vdCommon.debug("ComboData : " + JSON.stringify(comboList.slice(0,3)));

            vdCommon.programEnd();

            return comboList;
        } catch ( e ) {
            RuleOutputToUI = { Status : 'Error', Message : "Js Logic Error : " + e.message };
            return;
        }
    };

    var fn_cb_product = function(o9Params){
        const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
        vdCommon.setLogLevel("Debug");
        vdCommon.printParams(o9Params);

        try {
            // 파라메타 가져오기
            let parsedParams = JSON.parse(o9Params);
            var fbSourceVersion = parsedParams.fb_Version;

            var result = vdCommon.selectList(["[Item].[Product]"]
                                             ,[]
                                             ,"where {" +
                                                    ["[Item].[SCM Type]" + fn_localFilter(parsedParams.fb_ScmType)
                                                        ,"[Item].[Product Group]" + fn_localFilter(parsedParams.fb_ProductGroup)].join(",") +
                                                ", [Version].[Version Name].[" + fbSourceVersion + "], Measure.[W Demand Quantity to SCS] > 0 } "
                                             , "", "");
            var comboList = vdCommon.fn_makeCombo(result, {DimName : "Item", DimAttbName : "Product"
                                                            ,Sort : "DisplayName"
                                                            ,existAll : true});

            vdCommon.debug("ComboData : " + JSON.stringify(comboList.slice(0,3)));

            vdCommon.programEnd();

            return comboList;
        } catch ( e ) {
            RuleOutputToUI = { Status : 'Error', Message : "Js Logic Error : " + e.message };
            return;
        }
    };

    var fn_cb_productType = function(o9Params){
        const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
        vdCommon.setLogLevel("Debug");
        vdCommon.printParams(o9Params);

        try {
            // 파라메타 가져오기
            let parsedParams = JSON.parse(o9Params);
            var fbSourceVersion = parsedParams.fb_Version;

            var result = vdCommon.selectList(["[Item].[ProductType]"]
                                             ,[]
                                             ,"where {" +
                                                    ["[Item].[SCM Type]" + fn_localFilter(parsedParams.fb_ScmType)
                                                        ,"[Item].[Product Group]" + fn_localFilter(parsedParams.fb_ProductGroup)
                                                        ,"[Item].[Product]" + fn_localFilter(parsedParams.fb_Product)].join(",") +
                                                ", [Version].[Version Name].[" + fbSourceVersion + "], Measure.[W Demand Quantity to SCS] > 0 } "
                                             , "", "");
            var comboList = vdCommon.fn_makeCombo(result, {DimName : "Item", DimAttbName : "ProductType"
                                                            ,Sort : "DisplayName"
                                                            ,existAll : true});

            vdCommon.debug("ComboData : " + JSON.stringify(comboList.slice(0,3)));

            vdCommon.programEnd();

            return comboList;
        } catch ( e ) {
            RuleOutputToUI = { Status : 'Error', Message : "Js Logic Error : " + e.message };
            return;
        }
    };

    var fn_cb_project = function(o9Params){
        const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
        vdCommon.setLogLevel("Debug");
        vdCommon.printParams(o9Params);

        try {
            // 파라메타 가져오기
            let parsedParams = JSON.parse(o9Params);
            var fbSourceVersion = parsedParams.fb_Version;

            var result = vdCommon.selectList(["[Item].[Project]"]
                                             ,[]
                                             ,"where {" +
                                                    ["[Item].[SCM Type]" + fn_localFilter(parsedParams.fb_ScmType)
                                                        ,"[Item].[Product Group]" + fn_localFilter(parsedParams.fb_ProductGroup)
                                                        ,"[Item].[Product]" + fn_localFilter(parsedParams.fb_Product)].join(",") +
                                                ", [Version].[Version Name].[" + fbSourceVersion + "], Measure.[W Demand Quantity to SCS] > 0 } "
                                             , "", "");
            var comboList = vdCommon.fn_makeCombo(result, {DimName : "Item", DimAttbName : "Project"
                                                            ,Sort : "DisplayName"
                                                            ,existAll : true});

            vdCommon.debug("ComboData : " + JSON.stringify(comboList.slice(0,3)));

            vdCommon.programEnd();

            return comboList;
        } catch ( e ) {
            RuleOutputToUI = { Status : 'Error', Message : "Js Logic Error : " + e.message };
            return;
        }
    };

    var fn_cb_a1 = function(o9Params){
        const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
        vdCommon.setLogLevel("Debug");
        vdCommon.printParams(o9Params);

        try {
            // 파라메타 가져오기
            let parsedParams = JSON.parse(o9Params);
            var fbSourceVersion = parsedParams.fb_Version;

            var result = vdCommon.selectList(["[Item].[A1]"]
                                             ,[]
                                             ,"where {" +
                                                    ["[Item].[SCM Type]" + fn_localFilter(parsedParams.fb_ScmType)
                                                        ,"[Item].[Product Group]" + fn_localFilter(parsedParams.fb_ProductGroup)
                                                        ,"[Item].[Product]" + fn_localFilter(parsedParams.fb_Product)
                                                        ,"[Item].[Project]" + fn_localFilter(parsedParams.fb_Project)].join(",") +
                                                ", [Version].[Version Name].[" + fbSourceVersion + "], Measure.[W Demand Quantity to SCS] > 0 } "
                                             , "", "");
            var comboList = vdCommon.fn_makeCombo(result, {DimName : "Item", DimAttbName : "A1"
                                                            ,Sort : "DisplayName"
                                                            ,existAll : true});

            vdCommon.debug("ComboData : " + JSON.stringify(comboList.slice(0,3)));

            vdCommon.programEnd();

            return comboList;
        } catch ( e ) {
            RuleOutputToUI = { Status : 'Error', Message : "Js Logic Error : " + e.message };
            return;
        }
    };

    var fn_cb_a2 = function(o9Params){
        const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
        vdCommon.setLogLevel("Debug");
        vdCommon.printParams(o9Params);

        try {
            // 파라메타 가져오기
            let parsedParams = JSON.parse(o9Params);
            var fbSourceVersion = parsedParams.fb_Version;

            var result = vdCommon.selectList(["[Item].[A2]"]
                                             ,[]
                                             ,"where {" +
                                                    ["[Item].[SCM Type]" + fn_localFilter(parsedParams.fb_ScmType)
                                                        ,"[Item].[Product Group]" + fn_localFilter(parsedParams.fb_ProductGroup)
                                                        ,"[Item].[Product]" + fn_localFilter(parsedParams.fb_Product)
                                                        ,"[Item].[Project]" + fn_localFilter(parsedParams.fb_Project)].join(",") +
                                                ", [Version].[Version Name].[" + fbSourceVersion + "], Measure.[W Demand Quantity to SCS] > 0 } "
                                             , "", "");
            var comboList = vdCommon.fn_makeCombo(result, {DimName : "Item", DimAttbName : "A2"
                                                            ,Sort : "DisplayName"
                                                            ,existAll : true});

            vdCommon.debug("ComboData : " + JSON.stringify(comboList.slice(0,3)));

            vdCommon.programEnd();

            return comboList;
        } catch ( e ) {
            RuleOutputToUI = { Status : 'Error', Message : "Js Logic Error : " + e.message };
            return;
        }
    };

    var fn_cb_a3 = function(o9Params){
        const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
        vdCommon.setLogLevel("Debug");
        vdCommon.printParams(o9Params);

        try {
            // 파라메타 가져오기
            let parsedParams = JSON.parse(o9Params);
            var fbSourceVersion = parsedParams.fb_Version;

            var result = vdCommon.selectList(["[Item].[A3]"]
                                             ,[]
                                             ,"where {" +
                                                    ["[Item].[SCM Type]" + fn_localFilter(parsedParams.fb_ScmType)
                                                        ,"[Item].[Product Group]" + fn_localFilter(parsedParams.fb_ProductGroup)
                                                        ,"[Item].[Product]" + fn_localFilter(parsedParams.fb_Product)
                                                        ,"[Item].[Project]" + fn_localFilter(parsedParams.fb_Project)].join(",") +
                                                ", [Version].[Version Name].[" + fbSourceVersion + "], Measure.[W Demand Quantity to SCS] > 0 } "
                                             , "", "");
            var comboList = vdCommon.fn_makeCombo(result, {DimName : "Item", DimAttbName : "A3"
                                                            ,Sort : "DisplayName"
                                                            ,existAll : true});

            vdCommon.debug("ComboData : " + JSON.stringify(comboList.slice(0,3)));

            vdCommon.programEnd();

            return comboList;
        } catch ( e ) {
            RuleOutputToUI = { Status : 'Error', Message : "Js Logic Error : " + e.message };
            return;
        }
    };

    var fn_cb_a4 = function(o9Params){
        const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
        vdCommon.setLogLevel("Debug");
        vdCommon.printParams(o9Params);

        try {
            // 파라메타 가져오기
            let parsedParams = JSON.parse(o9Params);
            var fbSourceVersion = parsedParams.fb_Version;

            var result = vdCommon.selectList(["[Item].[A4]"]
                                             ,[]
                                             ,"where {" +
                                                    ["[Item].[SCM Type]" + fn_localFilter(parsedParams.fb_ScmType)
                                                        ,"[Item].[Product Group]" + fn_localFilter(parsedParams.fb_ProductGroup)
                                                        ,"[Item].[Product]" + fn_localFilter(parsedParams.fb_Product)
                                                        ,"[Item].[Project]" + fn_localFilter(parsedParams.fb_Project)].join(",") +
                                                 ", [Version].[Version Name].[" + fbSourceVersion + "], Measure.[W Demand Quantity to SCS] > 0 } "
                                             , "", "");
            var comboList = vdCommon.fn_makeCombo(result, {DimName : "Item", DimAttbName : "A4"
                                                            ,Sort : "DisplayName"
                                                            ,existAll : true});

            vdCommon.debug("ComboData : " + JSON.stringify(comboList.slice(0,3)));

            vdCommon.programEnd();

            return comboList;
        } catch ( e ) {
            RuleOutputToUI = { Status : 'Error', Message : "Js Logic Error : " + e.message };
            return;
        }
    };

    var fn_cb_a5 = function(o9Params){
        const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
        vdCommon.setLogLevel("Debug");
        vdCommon.printParams(o9Params);

        try {
            // 파라메타 가져오기
            let parsedParams = JSON.parse(o9Params);
            var fbSourceVersion = parsedParams.fb_Version;

            var result = vdCommon.selectList(["[Item].[A5]"]
                                             ,[]
                                             ,"where {" +
                                                    ["[Item].[SCM Type]" + fn_localFilter(parsedParams.fb_ScmType)
                                                        ,"[Item].[Product Group]" + fn_localFilter(parsedParams.fb_ProductGroup)
                                                        ,"[Item].[Product]" + fn_localFilter(parsedParams.fb_Product)
                                                        ,"[Item].[Project]" + fn_localFilter(parsedParams.fb_Project)].join(",") +
                                                ", [Version].[Version Name].[" + fbSourceVersion + "], Measure.[W Demand Quantity to SCS] > 0 } "
                                             , "", "");
            var comboList = vdCommon.fn_makeCombo(result, {DimName : "Item", DimAttbName : "A5"
                                                            ,Sort : "DisplayName"
                                                            ,existAll : true});

            vdCommon.debug("ComboData : " + JSON.stringify(comboList.slice(0,3)));

            vdCommon.programEnd();

            return comboList;
        } catch ( e ) {
            RuleOutputToUI = { Status : 'Error', Message : "Js Logic Error : " + e.message };
            return;
        }
    };

    var fn_cb_a6 = function(o9Params){
        const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
        vdCommon.setLogLevel("Debug");
        vdCommon.printParams(o9Params);

        try {
            // 파라메타 가져오기
            let parsedParams = JSON.parse(o9Params);
            var fbSourceVersion = parsedParams.fb_Version;

            var result = vdCommon.selectList(["[Item].[A6]"]
                                             ,[]
                                             ,"where {" +
                                                    ["[Item].[SCM Type]" + fn_localFilter(parsedParams.fb_ScmType)
                                                        ,"[Item].[Product Group]" + fn_localFilter(parsedParams.fb_ProductGroup)
                                                        ,"[Item].[Product]" + fn_localFilter(parsedParams.fb_Product)
                                                        ,"[Item].[Project]" + fn_localFilter(parsedParams.fb_Project)].join(",") +
                                                ", [Version].[Version Name].[" + fbSourceVersion + "], Measure.[W Demand Quantity to SCS] > 0 } "
                                             , "", "");
            var comboList = vdCommon.fn_makeCombo(result, {DimName : "Item", DimAttbName : "A6"
                                                            ,Sort : "DisplayName"
                                                            ,existAll : true});

            vdCommon.debug("ComboData : " + JSON.stringify(comboList.slice(0,3)));

            vdCommon.programEnd();

            return comboList;
        } catch ( e ) {
            RuleOutputToUI = { Status : 'Error', Message : "Js Logic Error : " + e.message };
            return;
        }
    };

    var fn_cb_a7 = function(o9Params){
        const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
        vdCommon.setLogLevel("Debug");
        vdCommon.printParams(o9Params);

        try {
            // 파라메타 가져오기
            let parsedParams = JSON.parse(o9Params);
            var fbSourceVersion = parsedParams.fb_Version;

            var result = vdCommon.selectList(["[Item].[A7]"]
                                             ,[]
                                             ,"where {" +
                                                    ["[Item].[SCM Type]" + fn_localFilter(parsedParams.fb_ScmType)
                                                        ,"[Item].[Product Group]" + fn_localFilter(parsedParams.fb_ProductGroup)
                                                        ,"[Item].[Product]" + fn_localFilter(parsedParams.fb_Product)
                                                        ,"[Item].[Project]" + fn_localFilter(parsedParams.fb_Project)].join(",") +
                                                ", [Version].[Version Name].[" + fbSourceVersion + "], Measure.[W Demand Quantity to SCS] > 0 } "
                                             , "", "");
            var comboList = vdCommon.fn_makeCombo(result, {DimName : "Item", DimAttbName : "A7"
                                                            ,Sort : "DisplayName"
                                                            ,existAll : true});

            vdCommon.debug("ComboData : " + JSON.stringify(comboList.slice(0,3)));

            vdCommon.programEnd();

            return comboList;
        } catch ( e ) {
            RuleOutputToUI = { Status : 'Error', Message : "Js Logic Error : " + e.message };
            return;
        }
    };

    var fn_cb_a8 = function(o9Params){
        const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
        vdCommon.setLogLevel("Debug");
        vdCommon.printParams(o9Params);

        try {
            // 파라메타 가져오기
            let parsedParams = JSON.parse(o9Params);
            var fbSourceVersion = parsedParams.fb_Version;

            var result = vdCommon.selectList(["[Item].[A8]"]
                                             ,[]
                                             ,"where {" +
                                                    ["[Item].[SCM Type]" + fn_localFilter(parsedParams.fb_ScmType)
                                                        ,"[Item].[Product Group]" + fn_localFilter(parsedParams.fb_ProductGroup)
                                                        ,"[Item].[Product]" + fn_localFilter(parsedParams.fb_Product)
                                                        ,"[Item].[Project]" + fn_localFilter(parsedParams.fb_Project)].join(",") +
                                                ", [Version].[Version Name].[" + fbSourceVersion + "], Measure.[W Demand Quantity to SCS] > 0 } "
                                             , "", "");
            var comboList = vdCommon.fn_makeCombo(result, {DimName : "Item", DimAttbName : "A8"
                                                            ,Sort : "DisplayName"
                                                            ,existAll : true});

            vdCommon.debug("ComboData : " + JSON.stringify(comboList.slice(0,3)));

            vdCommon.programEnd();

            return comboList;
        } catch ( e ) {
            RuleOutputToUI = { Status : 'Error', Message : "Js Logic Error : " + e.message };
            return;
        }
    };

    var fn_cb_a9 = function(o9Params){
        const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
        vdCommon.setLogLevel("Debug");
        vdCommon.printParams(o9Params);

        try {
            // 파라메타 가져오기
            let parsedParams = JSON.parse(o9Params);
            var fbSourceVersion = parsedParams.fb_Version;

            var result = vdCommon.selectList(["[Item].[A9]"]
                                             ,[]
                                             ,"where {" +
                                                    ["[Item].[SCM Type]" + fn_localFilter(parsedParams.fb_ScmType)
                                                        ,"[Item].[Product Group]" + fn_localFilter(parsedParams.fb_ProductGroup)
                                                        ,"[Item].[Product]" + fn_localFilter(parsedParams.fb_Product)
                                                        ,"[Item].[Project]" + fn_localFilter(parsedParams.fb_Project)].join(",") +
                                                ", [Version].[Version Name].[" + fbSourceVersion + "], Measure.[W Demand Quantity to SCS] > 0 } "
                                             , "", "");
            var comboList = vdCommon.fn_makeCombo(result, {DimName : "Item", DimAttbName : "A9"
                                                            ,Sort : "DisplayName"
                                                            ,existAll : true});

            vdCommon.debug("ComboData : " + JSON.stringify(comboList.slice(0,3)));

            vdCommon.programEnd();

            return comboList;
        } catch ( e ) {
            RuleOutputToUI = { Status : 'Error', Message : "Js Logic Error : " + e.message };
            return;
        }
    };

    var fn_cb_a10 = function(o9Params){
        const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
        vdCommon.setLogLevel("Debug");
        vdCommon.printParams(o9Params);

        try {
            // 파라메타 가져오기
            let parsedParams = JSON.parse(o9Params);
            var fbSourceVersion = parsedParams.fb_Version;

            var result = vdCommon.selectList(["[Item].[A10]"]
                                             ,[]
                                             ,"where {" +
                                                    ["[Item].[SCM Type]" + fn_localFilter(parsedParams.fb_ScmType)
                                                        ,"[Item].[Product Group]" + fn_localFilter(parsedParams.fb_ProductGroup)
                                                        ,"[Item].[Product]" + fn_localFilter(parsedParams.fb_Product)
                                                        ,"[Item].[Project]" + fn_localFilter(parsedParams.fb_Project)].join(",") +
                                                ", [Version].[Version Name].[" + fbSourceVersion + "], Measure.[W Demand Quantity to SCS] > 0 } "
                                             , "", "");
            var comboList = vdCommon.fn_makeCombo(result, {DimName : "Item", DimAttbName : "A10"
                                                            ,Sort : "DisplayName"
                                                            ,existAll : true});

            vdCommon.debug("ComboData : " + JSON.stringify(comboList.slice(0,3)));

            vdCommon.programEnd();

            return comboList;
        } catch ( e ) {
            RuleOutputToUI = { Status : 'Error', Message : "Js Logic Error : " + e.message };
            return;
        }
    };

    var fn_cb_a11 = function(o9Params){
        const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
        vdCommon.setLogLevel("Debug");
        vdCommon.printParams(o9Params);

        try {
            // 파라메타 가져오기
            let parsedParams = JSON.parse(o9Params);
            var fbSourceVersion = parsedParams.fb_Version;

            var result = vdCommon.selectList(["[Item].[A11]"]
                                             ,[]
                                             ,"where {" +
                                                    ["[Item].[SCM Type]" + fn_localFilter(parsedParams.fb_ScmType)
                                                        ,"[Item].[Product Group]" + fn_localFilter(parsedParams.fb_ProductGroup)
                                                        ,"[Item].[Product]" + fn_localFilter(parsedParams.fb_Product)
                                                        ,"[Item].[Project]" + fn_localFilter(parsedParams.fb_Project)].join(",") +
                                                ", [Version].[Version Name].[" + fbSourceVersion + "], Measure.[W Demand Quantity to SCS] > 0 } "
                                             , "", "");
            var comboList = vdCommon.fn_makeCombo(result, {DimName : "Item", DimAttbName : "A11"
                                                            ,Sort : "DisplayName"
                                                            ,existAll : true});

            vdCommon.debug("ComboData : " + JSON.stringify(comboList.slice(0,3)));

            vdCommon.programEnd();

            return comboList;
        } catch ( e ) {
            RuleOutputToUI = { Status : 'Error', Message : "Js Logic Error : " + e.message };
            return;
        }
    };

    var fn_cb_a12 = function(o9Params){
        const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
        vdCommon.setLogLevel("Debug");
        vdCommon.printParams(o9Params);

        try {
            // 파라메타 가져오기
            let parsedParams = JSON.parse(o9Params);
            var fbSourceVersion = parsedParams.fb_Version;

            var result = vdCommon.selectList(["[Item].[A12]"]
                                             ,[]
                                             ,"where {" +
                                                    ["[Item].[SCM Type]" + fn_localFilter(parsedParams.fb_ScmType)
                                                        ,"[Item].[Product Group]" + fn_localFilter(parsedParams.fb_ProductGroup)
                                                        ,"[Item].[Product]" + fn_localFilter(parsedParams.fb_Product)
                                                        ,"[Item].[Project]" + fn_localFilter(parsedParams.fb_Project)].join(",") +
                                                ", [Version].[Version Name].[" + fbSourceVersion + "], Measure.[W Demand Quantity to SCS] > 0 } "
                                             , "", "");
            var comboList = vdCommon.fn_makeCombo(result, {DimName : "Item", DimAttbName : "A12"
                                                            ,Sort : "DisplayName"
                                                            ,existAll : true});

            vdCommon.debug("ComboData : " + JSON.stringify(comboList.slice(0,3)));

            vdCommon.programEnd();

            return comboList;
        } catch ( e ) {
            RuleOutputToUI = { Status : 'Error', Message : "Js Logic Error : " + e.message };
            return;
        }
    };

    var fn_cb_a13 = function(o9Params){
        const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
        vdCommon.setLogLevel("Debug");
        vdCommon.printParams(o9Params);

        try {
            // 파라메타 가져오기
            let parsedParams = JSON.parse(o9Params);
            var fbSourceVersion = parsedParams.fb_Version;

            var result = vdCommon.selectList(["[Item].[A13]"]
                                             ,[]
                                             ,"where {" +
                                                    ["[Item].[SCM Type]" + fn_localFilter(parsedParams.fb_ScmType)
                                                        ,"[Item].[Product Group]" + fn_localFilter(parsedParams.fb_ProductGroup)
                                                        ,"[Item].[Product]" + fn_localFilter(parsedParams.fb_Product)
                                                        ,"[Item].[Project]" + fn_localFilter(parsedParams.fb_Project)].join(",") +
                                                ", [Version].[Version Name].[" + fbSourceVersion + "], Measure.[W Demand Quantity to SCS] > 0 } "
                                             , "", "");
            var comboList = vdCommon.fn_makeCombo(result, {DimName : "Item", DimAttbName : "A13"
                                                            ,Sort : "DisplayName"
                                                            ,existAll : true});

            vdCommon.debug("ComboData : " + JSON.stringify(comboList.slice(0,3)));

            vdCommon.programEnd();

            return comboList;
        } catch ( e ) {
            RuleOutputToUI = { Status : 'Error', Message : "Js Logic Error : " + e.message };
            return;
        }
    };

    var fn_cb_a14 = function(o9Params){
        const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
        vdCommon.setLogLevel("Debug");
        vdCommon.printParams(o9Params);

        try {
            // 파라메타 가져오기
            let parsedParams = JSON.parse(o9Params);
            var fbSourceVersion = parsedParams.fb_Version;

            var result = vdCommon.selectList(["[Item].[A14]"]
                                             ,[]
                                             ,"where {" +
                                                    ["[Item].[SCM Type]" + fn_localFilter(parsedParams.fb_ScmType)
                                                        ,"[Item].[Product Group]" + fn_localFilter(parsedParams.fb_ProductGroup)
                                                        ,"[Item].[Product]" + fn_localFilter(parsedParams.fb_Product)
                                                        ,"[Item].[Project]" + fn_localFilter(parsedParams.fb_Project)].join(",") +
                                                ", [Version].[Version Name].[" + fbSourceVersion + "], Measure.[W Demand Quantity to SCS] > 0 } "
                                             , "", "");
            var comboList = vdCommon.fn_makeCombo(result, {DimName : "Item", DimAttbName : "A14"
                                                            ,Sort : "DisplayName"
                                                            ,existAll : true});

            vdCommon.debug("ComboData : " + JSON.stringify(comboList.slice(0,3)));

            vdCommon.programEnd();

            return comboList;
        } catch ( e ) {
            RuleOutputToUI = { Status : 'Error', Message : "Js Logic Error : " + e.message };
            return;
        }
    };

    var fn_cb_a15 = function(o9Params){
        const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
        vdCommon.setLogLevel("Debug");
        vdCommon.printParams(o9Params);

        try {
            // 파라메타 가져오기
            let parsedParams = JSON.parse(o9Params);
            var fbSourceVersion = parsedParams.fb_Version;

            var result = vdCommon.selectList(["[Item].[A15]"]
                                             ,[]
                                             ,"where {" +
                                                    ["[Item].[SCM Type]" + fn_localFilter(parsedParams.fb_ScmType)
                                                        ,"[Item].[Product Group]" + fn_localFilter(parsedParams.fb_ProductGroup)
                                                        ,"[Item].[Product]" + fn_localFilter(parsedParams.fb_Product)
                                                        ,"[Item].[Project]" + fn_localFilter(parsedParams.fb_Project)].join(",") +
                                                ", [Version].[Version Name].[" + fbSourceVersion + "], Measure.[W Demand Quantity to SCS] > 0 } "
                                             , "", "");
            var comboList = vdCommon.fn_makeCombo(result, {DimName : "Item", DimAttbName : "A15"
                                                            ,Sort : "DisplayName"
                                                            ,existAll : true});

            vdCommon.debug("ComboData : " + JSON.stringify(comboList.slice(0,3)));

            vdCommon.programEnd();

            return comboList;
        } catch ( e ) {
            RuleOutputToUI = { Status : 'Error', Message : "Js Logic Error : " + e.message };
            return;
        }
    };

    var fn_addIndex = function(o9Params){
        const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
        vdCommon.setLogLevel("Debug");
        vdCommon.printParams(o9Params);

        try{
            // 파라메타 가져오기
            let parsedParams = JSON.parse(o9Params);

            // Max 값을 구한다.
            var result = vdCommon.selectList(["[Version].[Version Name]" + vdUtil.fn_filterStr(parsedParams.fb_Version),
                                                '[Seq].[Seq]'],
                                             ["Measure.[Scenario BAL Mod_A1]"],
                                             "",
                                             "orderby [Seq].[Seq].Key desc",
                                             "limit 1");
            var seq = "A1";
            if ( result.cs.rowCount > 0 ) {
                seq = "A" + (parseInt(result.cs.row(0).cell(result.cs.memberColumnIndex("Seq", "Seq")).Name.substr(1)) + 1);
            }

            var dimensions = [];
            dimensions.push(vdUtil.fn_qDim(null, "[Version].[Version Name]", parsedParams.fb_Version));
            dimensions.push(vdUtil.fn_qDim(null, "[Seq].[Seq]", seq));

            var measures = [];
            measures.push(vdUtil.fn_qMeaStr(null, "Measure.[Scenario BAL Mod_Location]", fn_convertMultiValue(parsedParams.fb_Location)));
            measures.push(vdUtil.fn_qMeaStr(null, "Measure.[Scenario BAL Mod_SCM Type]", fn_convertMultiValue(parsedParams.fb_ScmType)));
            measures.push(vdUtil.fn_qMeaStr(null, "Measure.[Scenario BAL Mod_Product Group]", fn_convertMultiValue(parsedParams.fb_ProductGroup)));
            measures.push(vdUtil.fn_qMeaStr(null, "Measure.[Scenario BAL Mod_Product]", fn_convertMultiValue(parsedParams.fb_Product)));
            measures.push(vdUtil.fn_qMeaStr(null, "Measure.[Scenario BAL Mod_Product Type]", fn_convertMultiValue(parsedParams.fb_ProductType)));
            measures.push(vdUtil.fn_qMeaStr(null, "Measure.[Scenario BAL Mod_Project]", fn_convertMultiValue(parsedParams.fb_Project)));
            measures.push(vdUtil.fn_qMeaStr(null, "Measure.[Scenario BAL Mod_A1]", fn_convertMultiValue(parsedParams.fb_A1)));
            measures.push(vdUtil.fn_qMeaStr(null, "Measure.[Scenario BAL Mod_A2]", fn_convertMultiValue(parsedParams.fb_A2)));
            measures.push(vdUtil.fn_qMeaStr(null, "Measure.[Scenario BAL Mod_A3]", fn_convertMultiValue(parsedParams.fb_A3)));
            measures.push(vdUtil.fn_qMeaStr(null, "Measure.[Scenario BAL Mod_A4]", fn_convertMultiValue(parsedParams.fb_A4)));
            measures.push(vdUtil.fn_qMeaStr(null, "Measure.[Scenario BAL Mod_A5]", fn_convertMultiValue(parsedParams.fb_A5)));
            measures.push(vdUtil.fn_qMeaStr(null, "Measure.[Scenario BAL Mod_A6]", fn_convertMultiValue(parsedParams.fb_A6)));
            measures.push(vdUtil.fn_qMeaStr(null, "Measure.[Scenario BAL Mod_A7]", fn_convertMultiValue(parsedParams.fb_A7)));
            measures.push(vdUtil.fn_qMeaStr(null, "Measure.[Scenario BAL Mod_A8]", fn_convertMultiValue(parsedParams.fb_A8)));
            measures.push(vdUtil.fn_qMeaStr(null, "Measure.[Scenario BAL Mod_A9]", fn_convertMultiValue(parsedParams.fb_A9)));
            measures.push(vdUtil.fn_qMeaStr(null, "Measure.[Scenario BAL Mod_A10]", fn_convertMultiValue(parsedParams.fb_A10)));
            measures.push(vdUtil.fn_qMeaStr(null, "Measure.[Scenario BAL Mod_A11]", fn_convertMultiValue(parsedParams.fb_A11)));
            measures.push(vdUtil.fn_qMeaStr(null, "Measure.[Scenario BAL Mod_A12]", fn_convertMultiValue(parsedParams.fb_A12)));
            measures.push(vdUtil.fn_qMeaStr(null, "Measure.[Scenario BAL Mod_A13]", fn_convertMultiValue(parsedParams.fb_A13)));
            measures.push(vdUtil.fn_qMeaStr(null, "Measure.[Scenario BAL Mod_A14]", fn_convertMultiValue(parsedParams.fb_A14)));
            measures.push(vdUtil.fn_qMeaStr(null, "Measure.[Scenario BAL Mod_A15]", fn_convertMultiValue(parsedParams.fb_A15)));
            measures.push(vdUtil.fn_qMeaStr(null, "Measure.[Scenario BAL Mod_Item]", vdUtil.fn_getString(parsedParams.fb_Item)));
            measures.push('Measure.[Scenario BAL Mod_Override Seq] = 99;');
            measures.push(vdUtil.fn_qMeaUpdateUserName("Measure.[Scenario BAL Mod_Created By]"));
            measures.push(vdUtil.fn_qMeaUpdateUserName("Measure.[Scenario BAL Mod_Updated By]"));
            measures.push(vdUtil.fn_qMeaUpdateTime("Measure.[Scenario BAL Mod_Created Time]"));
            measures.push(vdUtil.fn_qMeaUpdateTime("Measure.[Scenario BAL Mod_Update Time]"));

            vdCommon.createMeasure(dimensions, measures);

            vdCommon.programEnd();
        }catch ( e ) {
            RuleOutputToUI = { Status : 'Error', Message : "Js Logic Error : " + e.message };
            return;
        }
    }

    var fn_editValidation = function(o9Params){
        const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
        vdCommon.setLogLevel("Debug");
        vdCommon.printParams(o9Params);

        var rtn = 0;

        try {
            // 파라미터 가져오기
            var parsedParams = JSON.parse(o9Params);

            vdCommon.debug(parsedParams.VersionSeq.length);
            if ( parsedParams.VersionSeq.length > 1 ) {
                RuleOutputToUI = { Status : 'Error', Message : "수정 할 row 하나만 선택 해주세요." };
                rtn = 1;
            } else{
                var CurrentWeek = vdCommon.selectResult('&CurrentWeek.element(0).DisplayName');
                vdCommon.debug("CurrentWeek : " + CurrentWeek);
                vdCommon.debug(parsedParams.VersionSeq[0]["Version"].Value.substr(0,6));
                // 당주인지 체크
                if ( CurrentWeek != parsedParams.VersionSeq[0]["Version"].Value.substr(0,6) ) {
                    RuleOutputToUI = { Status : 'Error', Message : "당주 Plan으로 다시 선택하세요." };
                    rtn = 1;
                }
            }

            vdCommon.programEnd();
        } catch ( e ) {
            RuleOutputToUI = { Status : 'Error', Message : "Js Logic Error : " + e.message };
            return 1;
        }

        return rtn;
    };

    var fn_copyValidation = function(o9Params){
        const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
        vdCommon.setLogLevel("Debug");
        vdCommon.printParams(o9Params);

        var rtn = 0;

        try {
            // 파라미터 가져오기
            var parsedParams = JSON.parse(o9Params);

            vdCommon.debug(parsedParams.VersionSeq.length);
            if ( parsedParams.VersionSeq.length > 1 ) {
                RuleOutputToUI = { Status : 'Error', Message : "복사 할 row 하나만 선택 해주세요." };
                rtn = 1;
            }

            vdCommon.programEnd();
        } catch ( e ) {
            RuleOutputToUI = { Status : 'Error', Message : "Js Logic Error : " + e.message };
            return 1;
        }

        return rtn;
    };

    var fn_applyValidation = function(o9Params){
        const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
        vdCommon.setLogLevel("Debug");
        vdCommon.printParams(o9Params);

        var rtn = 0;

        try {
            // 파라미터 가져오기
            var parsedParams = JSON.parse(o9Params);

            vdCommon.debug(parsedParams.Version.length);
            if ( parsedParams.Version.length > 1 ) {
                RuleOutputToUI = { Status : 'Error', Message : "Plan을 하나만 선택해주세요." };
                rtn = 1;
            } else {
                var CurrentWeek = vdCommon.selectResult('&CurrentWeek.element(0).DisplayName');
                vdCommon.debug("CurrentWeek : " + CurrentWeek);
                // 당주인지 체크
                if ( CurrentWeek != parsedParams.Version[0].substr(0,6) ) {
                    RuleOutputToUI = { Status : 'Error', Message : "당주 Plan으로 다시 선택하세요." };
                    rtn = 1;
                }
            }

            vdCommon.programEnd();
        } catch ( e ) {
            RuleOutputToUI = { Status : 'Error', Message : "Js Logic Error : " + e.message };
            return 1;
        }

        return rtn;
    };

    var fn_editIndex = function(o9Params){
        const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
        vdCommon.setLogLevel("Debug");
        vdCommon.printParams(o9Params);

        try{
            // 파라메타 가져오기
            let parsedParams = JSON.parse(o9Params);

            var dimensions = [];
            dimensions.push("[Version].[Version Name]" + vdUtil.fn_filterStr(parsedParams.fb_Version));
            dimensions.push("[Seq].[Seq]" + vdUtil.fn_filterStrForDN(parsedParams.fb_Seq));

            var measures = [];
            measures.push(vdUtil.fn_qMeaStr(null, "Measure.[Scenario BAL Mod_Location]", fn_convertMultiValue(parsedParams.fb_Location)));
            measures.push(vdUtil.fn_qMeaStr(null, "Measure.[Scenario BAL Mod_SCM Type]", fn_convertMultiValue(parsedParams.fb_ScmType)));
            measures.push(vdUtil.fn_qMeaStr(null, "Measure.[Scenario BAL Mod_Product Group]", fn_convertMultiValue(parsedParams.fb_ProductGroup)));
            measures.push(vdUtil.fn_qMeaStr(null, "Measure.[Scenario BAL Mod_Product]", fn_convertMultiValue(parsedParams.fb_Product)));
            measures.push(vdUtil.fn_qMeaStr(null, "Measure.[Scenario BAL Mod_Product Type]", fn_convertMultiValue(parsedParams.fb_ProductType)));
            measures.push(vdUtil.fn_qMeaStr(null, "Measure.[Scenario BAL Mod_Project]", fn_convertMultiValue(parsedParams.fb_Project)));
            measures.push(vdUtil.fn_qMeaStr(null, "Measure.[Scenario BAL Mod_A1]", fn_convertMultiValue(parsedParams.fb_A1)));
            measures.push(vdUtil.fn_qMeaStr(null, "Measure.[Scenario BAL Mod_A2]", fn_convertMultiValue(parsedParams.fb_A2)));
            measures.push(vdUtil.fn_qMeaStr(null, "Measure.[Scenario BAL Mod_A3]", fn_convertMultiValue(parsedParams.fb_A3)));
            measures.push(vdUtil.fn_qMeaStr(null, "Measure.[Scenario BAL Mod_A4]", fn_convertMultiValue(parsedParams.fb_A4)));
            measures.push(vdUtil.fn_qMeaStr(null, "Measure.[Scenario BAL Mod_A5]", fn_convertMultiValue(parsedParams.fb_A5)));
            measures.push(vdUtil.fn_qMeaStr(null, "Measure.[Scenario BAL Mod_A6]", fn_convertMultiValue(parsedParams.fb_A6)));
            measures.push(vdUtil.fn_qMeaStr(null, "Measure.[Scenario BAL Mod_A7]", fn_convertMultiValue(parsedParams.fb_A7)));
            measures.push(vdUtil.fn_qMeaStr(null, "Measure.[Scenario BAL Mod_A8]", fn_convertMultiValue(parsedParams.fb_A8)));
            measures.push(vdUtil.fn_qMeaStr(null, "Measure.[Scenario BAL Mod_A9]", fn_convertMultiValue(parsedParams.fb_A9)));
            measures.push(vdUtil.fn_qMeaStr(null, "Measure.[Scenario BAL Mod_A10]", fn_convertMultiValue(parsedParams.fb_A10)));
            measures.push(vdUtil.fn_qMeaStr(null, "Measure.[Scenario BAL Mod_A11]", fn_convertMultiValue(parsedParams.fb_A11)));
            measures.push(vdUtil.fn_qMeaStr(null, "Measure.[Scenario BAL Mod_A12]", fn_convertMultiValue(parsedParams.fb_A12)));
            measures.push(vdUtil.fn_qMeaStr(null, "Measure.[Scenario BAL Mod_A13]", fn_convertMultiValue(parsedParams.fb_A13)));
            measures.push(vdUtil.fn_qMeaStr(null, "Measure.[Scenario BAL Mod_A14]", fn_convertMultiValue(parsedParams.fb_A14)));
            measures.push(vdUtil.fn_qMeaStr(null, "Measure.[Scenario BAL Mod_A15]", fn_convertMultiValue(parsedParams.fb_A15)));
            measures.push(vdUtil.fn_qMeaStr(null, "Measure.[Scenario BAL Mod_Item]", vdUtil.fn_getString(parsedParams.fb_Item)));
            measures.push(vdUtil.fn_qMeaUpdateUserName("Measure.[Scenario BAL Mod_Updated By]"));
            measures.push(vdUtil.fn_qMeaUpdateTime("Measure.[Scenario BAL Mod_Update Time]"));

            vdCommon.updateMeasure(dimensions, measures);

            vdCommon.programEnd();
        }catch ( e ) {
            RuleOutputToUI = { Status : 'Error', Message : "Js Logic Error : " + e.message };
            return;
        }
    }

    var fn_copyIndex = function(o9Params){
        const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
        vdCommon.setLogLevel("Debug");
        vdCommon.printParams(o9Params);

        try{
            // 파라메타 가져오기
            let parsedParams = JSON.parse(o9Params);

            // Max 값을 구한다.
            var result = vdCommon.selectList(["[Version].[Version Name]" + vdUtil.fn_filterStr(parsedParams.fb_TargetVersion),
                                                '[Seq].[Seq]'],
                                             ["Measure.[Scenario BAL Mod_A1]"],
                                             "",
                                             "orderby [Seq].[Seq].Key desc",
                                             "limit 1");
            var seq = "A0";
            if ( result.cs.rowCount > 0 ) {
                seq = result.cs.row(0).cell(result.cs.memberColumnIndex("Seq", "Seq")).Name;
            }

            result = vdCommon.selectList(["[Version].[Version Name]" + vdUtil.fn_filterStr(parsedParams.fb_Version),
                                            '[Seq].[Seq]' + vdUtil.fn_filterStrForDN(parsedParams.fb_Seq)],
                                         ["Measure.[Scenario BAL Mod_Location]",
                                            "Measure.[Scenario BAL Mod_SCM Type]",
                                            "Measure.[Scenario BAL Mod_Product Group]",
                                            "Measure.[Scenario BAL Mod_Product]",
                                            "Measure.[Scenario BAL Mod_Product Type]",
                                            "Measure.[Scenario BAL Mod_Project]",
                                            "Measure.[Scenario BAL Mod_A1]",
                                            "Measure.[Scenario BAL Mod_A2]",
                                            "Measure.[Scenario BAL Mod_A3]",
                                            "Measure.[Scenario BAL Mod_A4]",
                                            "Measure.[Scenario BAL Mod_A5]",
                                            "Measure.[Scenario BAL Mod_A6]",
                                            "Measure.[Scenario BAL Mod_A7]",
                                            "Measure.[Scenario BAL Mod_A8]",
                                            "Measure.[Scenario BAL Mod_A9]",
                                            "Measure.[Scenario BAL Mod_A10]",
                                            "Measure.[Scenario BAL Mod_A11]",
                                            "Measure.[Scenario BAL Mod_A12]",
                                            "Measure.[Scenario BAL Mod_A13]",
                                            "Measure.[Scenario BAL Mod_A14]",
                                            "Measure.[Scenario BAL Mod_A15]",
                                            "Measure.[Scenario BAL Mod_Item]",
                                            "Measure.[Scenario BAL Mod_From Week]",
                                            "Measure.[Scenario BAL Mod_To Week]",
                                            "Measure.[Scenario BAL Mod_Add Period]",
				            "Measure.[Scenario BAL Mod_Description]"],
                                         "",
                                         "",
                                         "");
            for ( var i = 0; i < result.cs.rowCount; i++ ) {
                // seq 증가
                seq = "A" + (parseInt(seq.substr(1)) + 1);

                var dimensions = [];
                dimensions.push(vdUtil.fn_qDim(null, "[Version].[Version Name]", parsedParams.fb_TargetVersion));
                dimensions.push(vdUtil.fn_qDim(null, "[Seq].[Seq]", seq));

		value = vdUtil.fn_getString(result.cs.row(i).cell(result.cs.measureColumnIndex("Scenario BAL Mod_Description")));

		if ( value === "" ) {
		    RuleOutputToUI = { Status : 'Error', Message : "Please enter the description"};
                    return;
		}

		value1 = vdUtil.fn_getString(result.cs.row(i).cell(result.cs.measureColumnIndex("Scenario BAL Mod_From Week")));
		value2 = vdUtil.fn_getString(result.cs.row(i).cell(result.cs.measureColumnIndex("Scenario BAL Mod_To Week")));
		value3 = vdUtil.fn_getString(result.cs.row(i).cell(result.cs.measureColumnIndex("Scenario BAL Mod_Add Period")));

		if ( value1 === "" || value2 === "" || value3 === "" ) {
		    RuleOutputToUI = { Status : 'Error', Message : "Please enter From Week, To Week, and Add Period"};
                    return;
		}

                var measures = [];
                measures.push(vdUtil.fn_qMeaStr(null, "Measure.[Scenario BAL Mod_Location]", result.cs.row(i).cell(result.cs.measureColumnIndex("Scenario BAL Mod_Location"))));
                measures.push(vdUtil.fn_qMeaStr(null, "Measure.[Scenario BAL Mod_SCM Type]", result.cs.row(i).cell(result.cs.measureColumnIndex("Scenario BAL Mod_SCM Type"))));
                measures.push(vdUtil.fn_qMeaStr(null, "Measure.[Scenario BAL Mod_Product Group]", result.cs.row(i).cell(result.cs.measureColumnIndex("Scenario BAL Mod_Product Group"))));
                measures.push(vdUtil.fn_qMeaStr(null, "Measure.[Scenario BAL Mod_Product]", result.cs.row(i).cell(result.cs.measureColumnIndex("Scenario BAL Mod_Product"))));
                measures.push(vdUtil.fn_qMeaStr(null, "Measure.[Scenario BAL Mod_Product Type]", result.cs.row(i).cell(result.cs.measureColumnIndex("Scenario BAL Mod_Product Type"))));
                measures.push(vdUtil.fn_qMeaStr(null, "Measure.[Scenario BAL Mod_Project]", result.cs.row(i).cell(result.cs.measureColumnIndex("Scenario BAL Mod_Project"))));
                measures.push(vdUtil.fn_qMeaStr(null, "Measure.[Scenario BAL Mod_A1]", result.cs.row(i).cell(result.cs.measureColumnIndex("Scenario BAL Mod_A1"))));
                measures.push(vdUtil.fn_qMeaStr(null, "Measure.[Scenario BAL Mod_A2]", result.cs.row(i).cell(result.cs.measureColumnIndex("Scenario BAL Mod_A2"))));
                measures.push(vdUtil.fn_qMeaStr(null, "Measure.[Scenario BAL Mod_A3]", result.cs.row(i).cell(result.cs.measureColumnIndex("Scenario BAL Mod_A3"))));
                measures.push(vdUtil.fn_qMeaStr(null, "Measure.[Scenario BAL Mod_A4]", result.cs.row(i).cell(result.cs.measureColumnIndex("Scenario BAL Mod_A4"))));
                measures.push(vdUtil.fn_qMeaStr(null, "Measure.[Scenario BAL Mod_A5]", result.cs.row(i).cell(result.cs.measureColumnIndex("Scenario BAL Mod_A5"))));
                measures.push(vdUtil.fn_qMeaStr(null, "Measure.[Scenario BAL Mod_A6]", result.cs.row(i).cell(result.cs.measureColumnIndex("Scenario BAL Mod_A6"))));
                measures.push(vdUtil.fn_qMeaStr(null, "Measure.[Scenario BAL Mod_A7]", result.cs.row(i).cell(result.cs.measureColumnIndex("Scenario BAL Mod_A7"))));
                measures.push(vdUtil.fn_qMeaStr(null, "Measure.[Scenario BAL Mod_A8]", result.cs.row(i).cell(result.cs.measureColumnIndex("Scenario BAL Mod_A8"))));
                measures.push(vdUtil.fn_qMeaStr(null, "Measure.[Scenario BAL Mod_A9]", result.cs.row(i).cell(result.cs.measureColumnIndex("Scenario BAL Mod_A9"))));
                measures.push(vdUtil.fn_qMeaStr(null, "Measure.[Scenario BAL Mod_A10]", result.cs.row(i).cell(result.cs.measureColumnIndex("Scenario BAL Mod_A10"))));
                measures.push(vdUtil.fn_qMeaStr(null, "Measure.[Scenario BAL Mod_A11]", result.cs.row(i).cell(result.cs.measureColumnIndex("Scenario BAL Mod_A11"))));
                measures.push(vdUtil.fn_qMeaStr(null, "Measure.[Scenario BAL Mod_A12]", result.cs.row(i).cell(result.cs.measureColumnIndex("Scenario BAL Mod_A12"))));
                measures.push(vdUtil.fn_qMeaStr(null, "Measure.[Scenario BAL Mod_A13]", result.cs.row(i).cell(result.cs.measureColumnIndex("Scenario BAL Mod_A13"))));
                measures.push(vdUtil.fn_qMeaStr(null, "Measure.[Scenario BAL Mod_A14]", result.cs.row(i).cell(result.cs.measureColumnIndex("Scenario BAL Mod_A14"))));
                measures.push(vdUtil.fn_qMeaStr(null, "Measure.[Scenario BAL Mod_A15]", result.cs.row(i).cell(result.cs.measureColumnIndex("Scenario BAL Mod_A15"))));
                measures.push(vdUtil.fn_qMeaStr("", "Measure.[Scenario BAL Mod_Item]", result.cs.row(i).cell(result.cs.measureColumnIndex("Scenario BAL Mod_Item"))));
                measures.push('Measure.[Scenario BAL Mod_From Week] = ' + vdUtil.fn_getString(vdUtil.fn_getMeaValue(result, i, "Scenario BAL Mod_From Week")) + ';');
                measures.push('Measure.[Scenario BAL Mod_To Week] = ' + vdUtil.fn_getString(vdUtil.fn_getMeaValue(result, i, "Scenario BAL Mod_To Week")) + ';');
                measures.push('Measure.[Scenario BAL Mod_Add Period] = ' + vdUtil.fn_getString(vdUtil.fn_getMeaValue(result, i, "Scenario BAL Mod_Add Period")) + ';');
                measures.push('Measure.[Scenario BAL Mod_Override Seq] = 99;');
                measures.push(vdUtil.fn_qMeaUpdateUserName("Measure.[Scenario BAL Mod_Created By]"));
                measures.push(vdUtil.fn_qMeaUpdateUserName("Measure.[Scenario BAL Mod_Updated By]"));
                measures.push(vdUtil.fn_qMeaUpdateTime("Measure.[Scenario BAL Mod_Created Time]"));
                measures.push(vdUtil.fn_qMeaUpdateTime("Measure.[Scenario BAL Mod_Update Time]"));
                measures.push(vdUtil.fn_qMeaStr(null, "Measure.[Scenario BAL Mod_Description]", result.cs.row(i).cell(result.cs.measureColumnIndex("Scenario BAL Mod_Description"))));

                vdCommon.createMeasure(dimensions, measures);
            }

            vdCommon.programEnd();
        }catch ( e ) {
            RuleOutputToUI = { Status : 'Error', Message : "Js Logic Error : " + e.message };
            return;
        }
    }

    var fn_deleteIndex = function(o9Params){
        try {
            const commonLib = require('o9.NSCM.commonLib');
            const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
            const vdUtil = new commonLib.VdUtil();

            vdCommon.setLogLevel("Debug");

            vdCommon.printParams(o9Params);

            // 파라미터 가져오기
            var parsedParams = JSON.parse(o9Params);

            vdCommon.deleteMeasure(["[Version].[Version Name]" + vdUtil.fn_filterStr(parsedParams.fb_Version),
                                        "[Seq].[Seq]" + vdUtil.fn_filterStrForDN(parsedParams.fb_Seq)],
                                    "Scenario BAL Modification");

            vdCommon.programEnd();
        } catch ( e ) {
            RuleOutputToUI = { Status : 'Error', Message : "Js Logic Error : " + e.message };
            return;
        }
    };

    var fn_apply = function(o9Params){
        const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
        vdCommon.setLogLevel("Debug");
        vdCommon.printParams(o9Params);

        try{
            // 파라메타 가져오기
            let parsedParams = JSON.parse(o9Params);

            var value = "";
            var result = vdCommon.selectList(["[Version].[Version Name]" + vdUtil.fn_filterStr(parsedParams.fb_Version),
                                                '[Seq].[Seq]'],
                                             ["Measure.[Scenario BAL Mod_Location]",
                                                "Measure.[Scenario BAL Mod_SCM Type]", "Measure.[Scenario BAL Mod_Product Group]",
                                                "Measure.[Scenario BAL Mod_Product]", "Measure.[Scenario BAL Mod_Product Type]", "Measure.[Scenario BAL Mod_Project]",
                                                "Measure.[Scenario BAL Mod_A1]", "Measure.[Scenario BAL Mod_A2]",
                                                "Measure.[Scenario BAL Mod_A3]", "Measure.[Scenario BAL Mod_A4]",
                                                "Measure.[Scenario BAL Mod_A5]", "Measure.[Scenario BAL Mod_A6]",
                                                "Measure.[Scenario BAL Mod_A7]", "Measure.[Scenario BAL Mod_A8]",
                                                "Measure.[Scenario BAL Mod_A9]", "Measure.[Scenario BAL Mod_A10]",
                                                "Measure.[Scenario BAL Mod_A11]", "Measure.[Scenario BAL Mod_A12]",
                                                "Measure.[Scenario BAL Mod_A13]", "Measure.[Scenario BAL Mod_A14]",
                                                "Measure.[Scenario BAL Mod_A15]", "Measure.[Scenario BAL Mod_Item]",
                                                "Measure.[Scenario BAL Mod_From Week]", "Measure.[Scenario BAL Mod_To Week]",
                                                "Measure.[Scenario BAL Mod_Add Period]", "Measure.[Scenario BAL Mod_Override Seq]"],
                                             "",
                                             "orderby Measure.[Scenario BAL Mod_Override Seq] desc, Seq.Seq.Key desc",
                                             "");
            for ( var i = 0; i < result.cs.rowCount; i++ ) {
                value = vdUtil.fn_getString(vdUtil.fn_getMeaValue(result, i, "Scenario BAL Mod_Add Period"));

                if ( value === "" ) {
                    RuleOutputToUI = { Status : 'Error', Message : "Please check the Add Period value"};
                    return;
                }
            }

            vdCommon.updateMeasure(["[Version].[Version Name]" + vdUtil.fn_filterStr(parsedParams.fb_Version)]
                        ,['Measure.[W Demand Build Ahead Limit] = Measure.[W Demand Build Ahead Limit backup];'
                            ]);

            vdCommon.updateMeasure(["[Version].[Version Name]" + vdUtil.fn_filterStr(parsedParams.fb_Version)]
                        ,['Measure.[W Quantity Max Target] = 0;'
                            ]);

            for ( var i = 0; i < result.cs.rowCount; i++ ) {
                var dimensions = [];
                dimensions.push(vdUtil.fn_qDim(null, "[Version].[Version Name]", parsedParams.fb_Version));

                value = vdUtil.fn_getString(vdUtil.fn_getMeaValue(result, i, "Scenario BAL Mod_Location"));
                    dimensions.push("[Location].[Location]" + ( value == "All" ? "" : vdUtil.fn_filterStr(value.split("^"))));
                value = vdUtil.fn_getString(vdUtil.fn_getMeaValue(result, i, "Scenario BAL Mod_SCM Type"));
                    dimensions.push("[Item].[SCM Type]" + ( value == "All" ? "" : vdUtil.fn_filterStr(value.split("^"))));
                value = vdUtil.fn_getString(vdUtil.fn_getMeaValue(result, i, "Scenario BAL Mod_Product Group"));
                    dimensions.push("[Item].[Product Group]" + ( value == "All" ? "" : vdUtil.fn_filterStr(value.split("^"))));
                value = vdUtil.fn_getString(vdUtil.fn_getMeaValue(result, i, "Scenario BAL Mod_Product"));
                    dimensions.push("[Item].[Product]" + ( value == "All" ? "" : vdUtil.fn_filterStr(value.split("^"))));
                value = vdUtil.fn_getString(vdUtil.fn_getMeaValue(result, i, "Scenario BAL Mod_Product Type"));
                    dimensions.push("[Item].[ProductType]" + ( value == "All" ? "" : vdUtil.fn_filterStr(value.split("^"))));
                value = vdUtil.fn_getString(vdUtil.fn_getMeaValue(result, i, "Scenario BAL Mod_Project"));
                    dimensions.push("[Item].[Project]" + ( value == "All" ? "" : vdUtil.fn_filterStr(value.split("^"))));
                value = vdUtil.fn_getString(vdUtil.fn_getMeaValue(result, i, "Scenario BAL Mod_A1"));
                    dimensions.push("[Item].[A1]" + ( value == "All" ? "" : vdUtil.fn_filterStr(value.split("^"))));
                value = vdUtil.fn_getString(vdUtil.fn_getMeaValue(result, i, "Scenario BAL Mod_A2"));
                    dimensions.push("[Item].[A2]" + ( value == "All" ? "" : vdUtil.fn_filterStr(value.split("^"))));
                value = vdUtil.fn_getString(vdUtil.fn_getMeaValue(result, i, "Scenario BAL Mod_A3"));
                    dimensions.push("[Item].[A3]" + ( value == "All" ? "" : vdUtil.fn_filterStr(value.split("^"))));
                value = vdUtil.fn_getString(vdUtil.fn_getMeaValue(result, i, "Scenario BAL Mod_A4"));
                    dimensions.push("[Item].[A4]" + ( value == "All" ? "" : vdUtil.fn_filterStr(value.split("^"))));
                value = vdUtil.fn_getString(vdUtil.fn_getMeaValue(result, i, "Scenario BAL Mod_A5"));
                    dimensions.push("[Item].[A5]" + ( value == "All" ? "" : vdUtil.fn_filterStr(value.split("^"))));
                value = vdUtil.fn_getString(vdUtil.fn_getMeaValue(result, i, "Scenario BAL Mod_A6"));
                    dimensions.push("[Item].[A6]" + ( value == "All" ? "" : vdUtil.fn_filterStr(value.split("^"))));
                value = vdUtil.fn_getString(vdUtil.fn_getMeaValue(result, i, "Scenario BAL Mod_A7"));
                    dimensions.push("[Item].[A7]" + ( value == "All" ? "" : vdUtil.fn_filterStr(value.split("^"))));
                value = vdUtil.fn_getString(vdUtil.fn_getMeaValue(result, i, "Scenario BAL Mod_A8"));
                    dimensions.push("[Item].[A8]" + ( value == "All" ? "" : vdUtil.fn_filterStr(value.split("^"))));
                value = vdUtil.fn_getString(vdUtil.fn_getMeaValue(result, i, "Scenario BAL Mod_A9"));
                    dimensions.push("[Item].[A9]" + ( value == "All" ? "" : vdUtil.fn_filterStr(value.split("^"))));
                value = vdUtil.fn_getString(vdUtil.fn_getMeaValue(result, i, "Scenario BAL Mod_A10"));
                    dimensions.push("[Item].[A10]" + ( value == "All" ? "" : vdUtil.fn_filterStr(value.split("^"))));
                value = vdUtil.fn_getString(vdUtil.fn_getMeaValue(result, i, "Scenario BAL Mod_A11"));
                    dimensions.push("[Item].[A11]" + ( value == "All" ? "" : vdUtil.fn_filterStr(value.split("^"))));
                value = vdUtil.fn_getString(vdUtil.fn_getMeaValue(result, i, "Scenario BAL Mod_A12"));
                    dimensions.push("[Item].[A12]" + ( value == "All" ? "" : vdUtil.fn_filterStr(value.split("^"))));
                value = vdUtil.fn_getString(vdUtil.fn_getMeaValue(result, i, "Scenario BAL Mod_A13"));
                    dimensions.push("[Item].[A13]" + ( value == "All" ? "" : vdUtil.fn_filterStr(value.split("^"))));
                value = vdUtil.fn_getString(vdUtil.fn_getMeaValue(result, i, "Scenario BAL Mod_A14"));
                    dimensions.push("[Item].[A14]" + ( value == "All" ? "" : vdUtil.fn_filterStr(value.split("^"))));
                value = vdUtil.fn_getString(vdUtil.fn_getMeaValue(result, i, "Scenario BAL Mod_A15"));
                    dimensions.push("[Item].[A15]" + ( value == "All" ? "" : vdUtil.fn_filterStr(value.split("^"))));
                value = vdUtil.fn_getString(vdUtil.fn_getMeaValue(result, i, "Scenario BAL Mod_Item"));
                    dimensions.push("[Item].[Item]" + vdUtil.fn_filterStr(value));

                // 주차 설정
                var from = vdUtil.fn_getString(vdUtil.fn_getMeaValue(result, i, "Scenario BAL Mod_From Week"));
                var to = vdUtil.fn_getString(vdUtil.fn_getMeaValue(result, i, "Scenario BAL Mod_To Week"));

                // 주차 로직 걸기
                if ( from != "" && to != "" ) {
                    dimensions.push('[Time].[Week].filter(#.Name >= "' + from + '" && #.Name <= "' + to + '")');
                } else if ( from != "" && to == "" ) {
                    dimensions.push('[Time].[Week].filter(#.Name >= "' + from + '")');
                } else if ( from == "" && to != "" ) {
                    dimensions.push('[Time].[Week].filter(#.Name <= "' + to + '")');
                }

                var measures = [];
		value = vdUtil.fn_getMeaValue(result, i, "Scenario BAL Mod_Add Period");
                measures.push('Measure.[W Demand Build Ahead Limit] = ' +
                                ' if ( Measure.[W Demand Build Ahead Limit backup] + ' + value + ' > 0 )' +
                                ' then round(Measure.[W Demand Build Ahead Limit backup] + ' + value + ') ' +
                                ' else 0;');

                vdCommon.updateMeasure(dimensions, measures);
            }

            vdCommon.programEnd();
        }catch ( e ) {
            RuleOutputToUI = { Status : 'Error', Message : "Js Logic Error : " + e.message };
            return;
        }
    }

    var fn_convertMultiValue = function(val){
        if ( val === null ) {
            return "All";
        } else if ( typeof(val) == "string" ) {
            return val;
        } else {
            if ( val.includes("All") ) {
                return "All";
            } else {
                return val.join("^");
            }
        }
    }

    // All 과 다른것을 같이 멀티로 선택할 경우 공통을 타면 문제가 있어 따로 만듬
    var fn_localFilter = function(val) {
        if ( val.includes("All") ) {
            return "";
        } else {
            return vdUtil.fn_filterStr(val);
        }
    }

    return {
        fn_cb_location : fn_cb_location,
        fn_cb_scmType : fn_cb_scmType,
        fn_cb_productGroup : fn_cb_productGroup,
        fn_cb_product : fn_cb_product,
        fn_cb_productType : fn_cb_productType,
        fn_cb_project : fn_cb_project,
        fn_cb_a1 : fn_cb_a1,
        fn_cb_a2 : fn_cb_a2,
        fn_cb_a3 : fn_cb_a3,
        fn_cb_a4 : fn_cb_a4,
        fn_cb_a5 : fn_cb_a5,
        fn_cb_a6 : fn_cb_a6,
        fn_cb_a7 : fn_cb_a7,
        fn_cb_a8 : fn_cb_a8,
        fn_cb_a9 : fn_cb_a9,
        fn_cb_a10 : fn_cb_a10,
        fn_cb_a11 : fn_cb_a11,
        fn_cb_a12 : fn_cb_a12,
        fn_cb_a13 : fn_cb_a13,
        fn_cb_a14 : fn_cb_a14,
        fn_cb_a15 : fn_cb_a15,
        fn_addIndex : fn_addIndex,
        fn_editValidation : fn_editValidation,
        fn_copyValidation : fn_copyValidation,
        fn_applyValidation : fn_applyValidation,
        fn_editIndex : fn_editIndex,
        fn_copyIndex : fn_copyIndex,
        fn_deleteIndex : fn_deleteIndex,
        fn_apply : fn_apply
    };
});

/**************************************************************************************
프로그램명  : o9.NSCM.JSBalModification
화면명     : BAL Modification
개발자     : sungmin0.lim
최초생성   : 2025.09.30
**************************************************************************************/