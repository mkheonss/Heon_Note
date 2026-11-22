define('o9.NSCM.JSEWLCMBODProductCopy', ['o9/data/query', 'o9/data/cellset', 'o9.NSCM.commonLibVD'], function(){

    /*--------------------------------------------------------------------------------------------------*/
    // 프로그램명 : o9.NSCM.JSEWLCMBODProductCopy
    // 화면명 : LCM BOD Product Copy (EW)
    // Action Button : EWLCMBODProductCopy
    // 최초생성 : 2025.08.07 / syif1380.lee
    /*--------------------------------------------------------------------------------------------------*/

    // fn_cLib 를 통해서 commonLib 를 생성 // 2026.03.26 공통적용변경
    var fn_cLib = function(name) {
        return new commonLib.VdCommon(name);
    }
    var fn_cUtil = function() {
        return new commonLib.VdUtil();
    }

    const programName = "o9.NSCM.JSEWLCMBODProductCopy";
    const commonLib = require('o9.NSCM.commonLibVD');   // 2026.03.26 공통적용변경
    const cUtil = fn_cUtil();                           // 2026.03.26 공통적용변경

    //================================= 공통 콤보 사용 ===============================//
    // Action Button : EWCommonVD
    // From Site : Location     : 
    // To Site   : Sub Location  : 
    //================================================================================//

	var fn_loadFunction = function(o9Params){
        const cLib = fn_cLib(programName + "." + arguments.callee.name);
        cLib.setLogLevel("Debug");

		try {
            let returnData = {};
            let obj = this;

            cLib.printParams(o9Params);

            // 파라메타 가져오기
            var parsedParams = JSON.parse(o9Params);
			var fbFuncName = parsedParams.fbFuncName;

            if ( functionMap[fbFuncName] == undefined ) {
                return { "Code" : 1, "Msg" : "No Function" };
            }

            var rtn = functionMap[fbFuncName](parsedParams);

            cLib.programEnd();
            return rtn;
        } catch ( e ) {
            cLib.error(e.message);
            return { "Code" : -1, "Msg" : e.message };
        }
	};

    /**
     * From Site콤보
     * Actiion Button : EWLCMBODProductCopy
     * {"fbFuncName":"fn_cb_location","fbParams":{"filters":{"[Location].[Site Group1]":{"SelectedMembers":[],"SelectedMembersAlias":[],"MemberFilter":"&NSUISiteGrp1LCMView","DimensionAliasName":"<MF>"},"[Location].[Site Group2]":{"SelectedMembers":[],"SelectedMembersAlias":[],"MemberFilter":"&NSUISiteGrp2LCMView","DimensionAliasName":"<MF>"},"[Location].[Site Group4]":{"SelectedMembers":[],"SelectedMembersAlias":[],"MemberFilter":"&NSUISiteGrp4LCMView","DimensionAliasName":"<MF>"},"[Item].[Item Std1]":{"SelectedMembers":[],"SelectedMembersAlias":[],"MemberFilter":"&NSUIItemStd1LCMView","DimensionAliasName":"<LCM>"},"[Item].[Item Std2]":{"SelectedMembers":[],"SelectedMembersAlias":[],"MemberFilter":"&NSUIItemStd2LCMView","DimensionAliasName":"<LCM>"},"[Sub Location].[Sub Location Group3]":{"SelectedMembers":[],"SelectedMembersAlias":[],"MemberFilter":"&NSUISubSiteGrp3SETView.unionwith(&NSUISubSiteGrp3KDView)","DimensionAliasName":"< MF >"},"[Sub Location].[Sub Location Group4]":{"SelectedMembers":[],"SelectedMembersAlias":[],"MemberFilter":"&NSUISubSiteGrp4SETView.unionwith(&NSUISubSiteGrp4KDView)","DimensionAliasName":"< MF >"},"[Version].[Version Name]":{"SelectedMembers":["CWV_MP"],"SelectedMembersAlias":["202547"],"MemberFilter":"&CWVUI","DimensionAliasName":"Plan ID"}}}}
     * 
     * @param {*} parsedParams 
     * @returns 
     */
    var fn_cb_location = function(parsedParams){
        const cLib = fn_cLib(programName + "." + arguments.callee.name);
        cLib.setLogLevel("Debug");

        try {
            cLib.debug("parsedParams :: "+JSON.stringify(parsedParams));

            // 2025.08.11
            // var where = "where { &CWVUI }";
            // var result = cLib.selectList(["&NSUISiteGrp4LCMView.relatedmembers([Location])"],
            //                                  ["Measure.[LCM BOD List_Value]","Measure.[Dummy]"],    // measure
            //                                  where,    // where
            //                                  "",    // orderby
            //                                  "");   // limit
            // var where = "where { &CWVUI }";

            let conditions = [];
            conditions.push("&CWVUI");
            conditions.push(cUtil.fn_getFilterQuery(parsedParams,"[Location].[Site Group1]"));
            conditions.push(cUtil.fn_getFilterQuery(parsedParams,"[Location].[Site Group2]"));
            conditions.push(cUtil.fn_getFilterQuery(parsedParams,"[Location].[Site Group4]"));
            cLib.debug(" fn_cb_location >> conditions : "+JSON.stringify(conditions));

            let where = conditions.length ? `where { ${conditions.join(',')} } ` : '' ;

            var result = cLib.selectList(["&NSUISiteGrp4LCMView.relatedmembers([Location])"],
                                             ["Measure.[LCM BOD List_Value]","Measure.[Dummy]"],    // measure
                                             where,    // where
                                             "",    // orderby
                                             "");   // limit

            cLib.printCsData(result, 3);

            var comboList = cLib.fn_makeCombo(result, {DimName : "Location", DimAttbName : "Location", Sort : "DisplayName", existAll : false, isDisplayNameWithCode : true});
            comboList.unshift({ Name : "", DisplayName : "임시 data"});
            cLib.debug("ComboData : " + JSON.stringify(comboList));

            cLib.programEnd();

            return { "Code" : 0, "Msg" : "", "Rows" : comboList };
        } catch ( e ) {
            cLib.error(e.message);
            return { "Code" : -1, "Msg" : e.message };
        }
    };

    /**
     * To Site 콤보
     * Actiion Button : EWLCMBODProductCopy
     * {"fbFuncName":"fn_cb_subLocation","fbParams":{"[Location].[Location]":"P82A","filters":{"[Location].[Site Group1]":{"SelectedMembers":[],"SelectedMembersAlias":[],"MemberFilter":"&NSUISiteGrp1LCMView","DimensionAliasName":"<MF>"},"[Location].[Site Group2]":{"SelectedMembers":["MF_NORTH_AMERICA"],"SelectedMembersAlias":["NORTH_AMERICA"],"MemberFilter":"&NSUISiteGrp2LCMView","DimensionAliasName":"<MF>"},"[Location].[Site Group4]":{"SelectedMembers":[],"SelectedMembersAlias":[],"MemberFilter":"&NSUISiteGrp4LCMView","DimensionAliasName":"<MF>"},"[Item].[Item Std1]":{"SelectedMembers":[],"SelectedMembersAlias":[],"MemberFilter":"&NSUIItemStd1LCMView","DimensionAliasName":"<LCM>"},"[Item].[Item Std2]":{"SelectedMembers":["LCD_TV","LCD_MONITOR"],"SelectedMembersAlias":["TV","MONITOR"],"MemberFilter":"&NSUIItemStd2LCMView","DimensionAliasName":"<LCM>"},"[Sub Location].[Sub Location Group3]":{"SelectedMembers":["MF_NORTH_AMERICA_SAMEX","MF_EUROPE_SEH"],"SelectedMembersAlias":["SAMEX","SEH"],"MemberFilter":"&NSUISubSiteGrp3SETView.unionwith(&NSUISubSiteGrp3KDView)","DimensionAliasName":"< MF >"},"[Sub Location].[Sub Location Group4]":{"SelectedMembers":[],"SelectedMembersAlias":[],"MemberFilter":"&NSUISubSiteGrp4SETView.unionwith(&NSUISubSiteGrp4KDView)","DimensionAliasName":"< MF >"},"[Version].[Version Name]":{"SelectedMembers":["CWV_MP"],"SelectedMembersAlias":["202547"],"MemberFilter":"&CWVUI","DimensionAliasName":"Plan ID"}}}}
     * 
     * @param {*} parsedParams 
     * @returns 
     */
    var fn_cb_subLocation = function(parsedParams){
        const cLib = fn_cLib(programName + "." + arguments.callee.name);
        cLib.setLogLevel("Debug");

        try {
            cLib.debug("parsedParams :: "+JSON.stringify(parsedParams));
            cLib.debug("parsedParams.fbParams :: "+JSON.stringify(parsedParams.fbParams));
            let fbLocation = parsedParams.fbParams["[Location].[Location]"];

            // // 2025.08.11
            // var where = "where {"
            //                    +"&CWVUI"
            //                    +",[Location].[Location].["+fbLocation+"]"
            //                    +"}";

            let conditions = [];
            conditions.push("&CWVUI");
            conditions.push("[Location].[Location]"+ cUtil.fn_filterStr(fbLocation));
            conditions.push(cUtil.fn_getFilterQuery(parsedParams,"[Sub Location].[Sub Location Group3]"));
            conditions.push(cUtil.fn_getFilterQuery(parsedParams,"[Sub Location].[Sub Location Group4]"));
            cLib.debug(" fn_cb_subLocation >> conditions : "+JSON.stringify(conditions));

            let where = conditions.length ? `where { ${conditions.join(',')} } ` : '' ;

            var result = cLib.selectList(["&NSUISubSiteGrp4SETView.unionwith(&NSUISubSiteGrp4KDView).relatedmembers([Sub Location])"],
                                             ["Measure.[LCM BOD List_Value]","Measure.[Dummy]"],    // measure
                                             where,    // where
                                             "",    // orderby
                                             "");   // limit
            cLib.printCsData(result, 3);

            var comboList = cLib.fn_makeCombo(result, {DimName : "Sub Location", DimAttbName : "Sub Location", Sort : "DisplayName", existAll : false, isDisplayNameWithCode : true});
            comboList.unshift({ Name : "", DisplayName : "임시 data"});

            cLib.debug("ComboData : " + JSON.stringify(comboList));

            cLib.programEnd();

            return { "Code" : 0, "Msg" : "", "Rows" : comboList };
        } catch ( e ) {
            cLib.error(e.message);
            return { "Code" : -1, "Msg" : e.message };
        }
    };

    // /**
    //  * Item (PO Item) 콤보
    //  * Actiion Button : EWLCMBODProductCopy
    //  * { "fbFuncName" : "fn_cb_poItem", "fbParams" : {"[Location].[Location]":"P306LCD"} }
    //  * 
    //  * @param {*} parsedParams 
    //  * @returns 
    //  */
    // var fn_cb_poItem = function(parsedParams){
    //     const cLib = new commonLib.CLib(programName + "." + arguments.callee.name);
    //     cLib.setLogLevel("Debug");

    //     try {
    //         cLib.debug("parsedParams :: "+JSON.stringify(parsedParams));
    //         cLib.debug("parsedParams.fbParams :: "+JSON.stringify(parsedParams.fbParams));
    //         let fbLocation = parsedParams.fbParams["[Location].[Location]"];
    //         // var itemStartswith = "BN95%";   // add 2025.05.02 (임재민p요청), data 없어서 주석처리(2025.08.11)
    //         var itemStartswith = "";

    //         var where = 'where {'
    //         +' &CWVUI'
    //         +', [Location].[Location]'+ cUtil.fn_filterStr(fbLocation)
    //         +', Measure.[LCM Code MAP_Status] != "COM" '
    //         +', [Item].[Item]'+cUtil.fn_filterStr(itemStartswith)
    //         +'}';
    //         // Select ([To Item].[To Item]) on row, () on column where { &CWVUI, [Location].[Location].filter(#.Name == "P551LCD"), Measure.[LCM Code MAP_Status] != "COM" }  ;
    //         var result = cLib.selectList(["[To Item].[To Item]"],
    //                                         "",
    //                                         where, // where
    //                                         "", // orderby
    //                                         "");  // limit 1000

    //         cLib.printCsData(result, 3);

    //         var comboList = cLib.fn_makeCombo(result, {DimName : "To Item", DimAttbName : "To Item", Sort : "DisplayName", existAll : false});
    //         comboList.unshift({ Name : "", DisplayName : "임시 data"});
    //         cLib.debug("ComboData : " + JSON.stringify(comboList));

    //         cLib.programEnd();

    //         return { "Code" : 0, "Msg" : "", "Rows" : comboList };
    //     } catch ( e ) {
    //         cLib.error(e.message);
    //         return { "Code" : -1, "Msg" : e.message };
    //     }
    // };

    /**
     * Item (PO Item) 콤보 : 2026.03.18 변경
     * Actiion Button : EWLCMBODProductCopy
     * {"fbFuncName" : "fn_cb_poItem", "fbParams" : {"filters":{"[Version].[Version Name]":{"SelectedMembers":["CWV_MP"],"MemberFilter":"&CWVUI"}}}}
     * 
     * @param {*} parsedParams 
     * @returns 
     */
    var fn_cb_poItem = function(parsedParams){
        const cLib = fn_cLib(programName + "." + arguments.callee.name);
        cLib.setLogLevel("Debug");

        try {
            cLib.debug("parsedParams :: "+JSON.stringify(parsedParams));

            var fbVersion = cUtil.fn_getFilterValue(parsedParams, "[Version].[Version Name]"); 

            let col03List = fn_AdhocCol03(parsedParams, "1");   // 배열로 리턴

            cLib.debug("########### col03List : "+col03List);

            where = 'where {'
                        +' [Item].[Class Category]'+cUtil.fn_filterStr(col03List)  // 위에서 조회한 ADHOC_Col03 값
                        +',[Item].[Description].filter(~(#.Name == "FAKE") )'
                        +'}';

            result = cLib.selectList(["[Item].[Item]"], "", where, "", "Limit 1000");   // 전체 row : 31,370
            // result = cLib.selectList(["[Item].[Item]"], "", where, "", "");  // 전체 조회시 오류 발생

            cLib.printCsData(result, 3);

            var comboList = cLib.fn_makeCombo(result, {DimName : "Item", DimAttbName : "Item", Sort : "DisplayName", existAll : false});
            cLib.debug("ComboData : " + JSON.stringify(comboList));

            cLib.programEnd();

            return { "Code" : 0, "Msg" : "", "Rows" : comboList };
        } catch ( e ) {
            cLib.error(e.message);
            return { "Code" : -1, "Msg" : e.message };
        }
    };

    /**
     * Item (Prod Item)콤보 : 2026.03.18 완전 다른 버전 생성 (이상엽p요청)
     * Actiion Button : EWLCMBODProductCopy
     * 
     * {"fbFuncName" : "fn_cb_prodItem", 
        "fbParams" : {
        "[Location].[Location]":"P306LCD"
        ,"[Sub Location].[Sub Location]":"P306"
        ,"[Item].[Item]":"BN95-12465C"
        ,"filters":{"[Version].[Version Name]":{"SelectedMembers":["CWV_MP"],"MemberFilter":"&CWVUI"}}}}
     * @param {*} parsedParams 
     * @returns 
     */
    var fn_cb_prodItem = function(parsedParams){
        const cLib = fn_cLib(programName + "." + arguments.callee.name);
        cLib.setLogLevel("Debug");

        try {
            cLib.debug("parsedParams :: "+JSON.stringify(parsedParams));

            let comboList = [];
            
            let fbLocation = parsedParams.fbParams["[Location].[Location]"];
            let fbSubLocation = parsedParams.fbParams["[Sub Location].[Sub Location]"];
            let fbPOItem = parsedParams.fbParams["[Item].[Item]"];

            // let result = cLib.selectList(["[Item].[Item]"+ cUtil.fn_filterStr(fbPOItem),"[Item].[Class Category]"], [], "", "", "");
            // var fbItemClassCategory = result.cs.row(0).cell(result.cs.memberColumnIndex("Item", "Class Category")).Name;
            // cLib.debug("## fbItemClassCategory : "+fbItemClassCategory);

            // Case 확인
            let vCase = fn_caseType(parsedParams, "1");

            cLib.debug("### vCase : "+vCase);

            if( vCase == "caseX"){
                return { "Code" : 1, "Msg" : "Case 구분 데이터 없음.", "Rows" : "" };
            }

            //----------------------------------------------------------------------------------------------------------------------//
            // Case 2
            //----------------------------------------------------------------------------------------------------------------------//
            if( vCase == "case2"){
                cLib.debug("################### vCase ===> 2");

                let col03List = fn_AdhocCol03(parsedParams, "2");   // 배열로 리턴
                let case2Where = 'where { [Item].[Class Category]'+ cUtil.fn_filterStr(col03List) +'}';                           
                let case2result = cLib.selectList(["[Item].[Item]"], "", case2Where, "", "limit 100");

                for (let i = 0; i < case2result.cs.rowCount; i++) {
                    let itemName = case2result.cs.row(i).cell(case2result.cs.memberColumnIndex("Item","Item")).Name;
                    comboList.push({ Name: itemName, DisplayName: itemName, Flag: "0" });
                }
            
            }else{
                cLib.debug("################### vCase ===> 기타");

                //-------------------- comboList1
                let col03List = fn_AdhocCol03(parsedParams, "1");   // 배열로 리턴
                let case3Where = 'where { [Item].[Class Category]'+ cUtil.fn_filterStr(col03List) +' ,[Item].[Description].filter(~(#.Name == "FAKE") ) }';    
                let case3result = cLib.selectList(["[Item].[Item]"], "", case3Where, "", "limit 100");  // 전체 row : 31,370

                if( case3result.cs.rowCount == 0){
                    return { "Code" : 1, "Msg" : "There are No CY code", "Rows" : "" };
                }

                let comboList1 = [];
                for (let i = 0; i < case3result.cs.rowCount; i++) {
                    let itemName = case3result.cs.row(i).cell(case3result.cs.memberColumnIndex("Item","Item")).Name;
                    comboList1.push({ Name: itemName, DisplayName: itemName, Flag: "0" });
                }

                cLib.debug("comboList1 --> 1 : " + JSON.stringify(comboList1));

                //-------------------- comboList2
                let where1 = 'where {'
                                + cUtil.fn_getFilterQuery(parsedParams, "[Version].[Version Name]")
                                +',[Location].[Location].[P105]'    // default 값
                                +',[Category].[Category].[MODEL] '  // default 값
                                // +',[To Item].[To Item].filter(#.Name startswith "CY-")' // default 값
                                +',Measure.[LCM Code MAP_Status] == "COM"'  // default 값
                                +',[Item].[Item]'+ cUtil.fn_filterStr(fbPOItem)
                                +'}';
                let result1 = cLib.selectList(['[To Item].[To Item].filter(#.Name startswith "CY-")'],  // "CY-"  default 값
                // let result1 = cLib.selectList(['[To Item].[To Item]'],
                                                ["Measure.[LCM Code MAP_Status]"],
                                                where1,
                                                "",
                                                "limit 100");
                let getToItem = [];
                for (let i = 0; i < result1.cs.rowCount; i++) {
                    getToItem.push(result1.cs.row(i).cell(result1.cs.memberColumnIndex("To Item","To Item")).Name);
                }

                // LCD Item
                let where2 = 'where { [Item].[Item Stage].[LCD] }';
                let result2 = cLib.selectList(["[Item].[Item]"+ cUtil.fn_filterStr(getToItem)], "", where2, "", "limit 100");
                let comboList2 = [];
                for (let i = 0; i < result2.cs.rowCount; i++) {
                    let itemName = result2.cs.row(i).cell(result2.cs.memberColumnIndex("Item","Item")).Name;
                    comboList2.push({ Name: itemName, DisplayName: itemName, Flag: "0" });
                }
                cLib.debug("comboList --> 2 : " + JSON.stringify(comboList2));

                comboList = [...(comboList1 || []), ...(comboList2 || [])];
            }

            cLib.debug("################### fn_cb_prodItem_test ===> finish");

            // var comboList = cLib.fn_makeCombo(result, {DimName : "Item", DimAttbName : "Item", Sort : "DisplayName", existAll : false});
            cLib.debug("ComboData : " + JSON.stringify(comboList));

            cLib.programEnd();

            return { "Code" : 0, "Msg" : "", "Rows" : comboList };
        } catch ( e ) {
            cLib.error(e.message);
            return { "Code" : -1, "Msg" : e.message };
        }
    };

    /**
     * Item (Prod Item)콤보 : 2026.03.18 완전 다른 버전 생성 (이상엽p요청)
     * Actiion Button : EWLCMBODProductCopy
     * 
     * {"fbFuncName" : "fn_cb_prodItem", 
        "fbParams" : {
        "[Location].[Location]":"P306LCD"
        ,"[Sub Location].[Sub Location]":"P306"
        ,"[Item].[Item]":"BN95-12465C"
        ,"filters":{"[Version].[Version Name]":{"SelectedMembers":["CWV_MP"],"MemberFilter":"&CWVUI"}}}}
     * @param {*} parsedParams 
     * @returns 
     */
    var fn_cb_prodItem_value = function(parsedParams){
        const cLib = fn_cLib(programName + "." + arguments.callee.name);
        cLib.setLogLevel("Debug");

        try {
            cLib.debug("parsedParams :: "+JSON.stringify(parsedParams));

            let comboList = [];
            
            let fbLocation = parsedParams.fbParams["[Location].[Location]"];
            let fbSubLocation = parsedParams.fbParams["[Sub Location].[Sub Location]"];
            let fbPOItem = parsedParams.fbParams["[Item].[Item]"];

            // let result = cLib.selectList(["[Item].[Item]"+ cUtil.fn_filterStr(fbPOItem),"[Item].[Class Category]"], [], "", "", "");
            // var fbItemClassCategory = result.cs.row(0).cell(result.cs.memberColumnIndex("Item", "Class Category")).Name;
            // cLib.debug("## fbItemClassCategory : "+fbItemClassCategory);

            // Case 확인
            let vCase = fn_caseType(parsedParams, "2");

            if( vCase == "caseX"){
                return { "Code" : 1, "Msg" : "Case 구분 데이터 없음.", "Rows" : "" };
            }

            cLib.debug("### vCase : "+vCase);

            //----------------------------------------------------------------------------------------------------------------------//
            // Case 2
            //----------------------------------------------------------------------------------------------------------------------//
            if( vCase == "case1"){
                cLib.debug("################### vCase ===> 1");

                let case1_Result= fn_getLcmCodeMap_toItem(parsedParams);

                cLib.debug("################### vCase ===> 1 : case1_Result > "+JSON.stringify(case1_Result));

                // code 0
                if( case1_Result.code == "0"){
                    comboList.push({ Name: case1_Result.name, DisplayName: case1_Result.name });

                // code 1 , code 2
                }else if( case1_Result.code == "1" || case1_Result.code == "2" ){
                    comboList.push({ Name: "-1", DisplayName: case1_Result.name });
                }
            }else if( vCase == "case2"){
                cLib.debug("################### vCase ===> 2 > Default Value Setting ");

                let case2Where = 'where {'
                                + cUtil.fn_getFilterQuery(parsedParams, "[Version].[Version Name]")
                                +',[Location].[Location]'+cUtil.fn_filterStr(fbLocation)
                                +',[Sub Location].[Sub Location].filter(#.Name endswith "KD")'
                                +'}';
                let case2result = cLib.selectList(["[Item].[Item]"+ cUtil.fn_filterStr(fbPOItem)], ["Measure.[Vendor Map Item_PO Flag]","Measure.[Vendor Map Item_Prod Flag]"], case2Where, "", "limit 100");

                for (let i = 0; i < case2result.cs.rowCount; i++) {
                    let itemName = case2result.cs.row(i).cell(case2result.cs.memberColumnIndex("Item","Item")).Name;
                    comboList.push({ Name: itemName, DisplayName: itemName });
                }
            }else if( vCase == "case3"){

                let col03List = fn_AdhocCol03(parsedParams, "2");   // 배열로 리턴

                cLib.debug("################### vCase ===> 3 : col03List :: "+col03List);

                let case3Where = 'where {'
                            + cUtil.fn_getFilterQuery(parsedParams, "[Version].[Version Name]")
                            +', [Location].[Location].[P105]'   // P105 고정
                            +', [Item].[Item]'+cUtil.fn_filterStr(fbPOItem)
                            +'}';
                let case3result = cLib.selectList(['[To Item].[To Item].filter(#.Name endswith "'+col03List[0]+'")'],
                                            ["Measure.[LCM Code MAP_Creation Time]","Measure.[LCM Code MAP_Status]"],
                                            case3Where,
                                            "",
                                            "limit 100");
                

                if( case3result.cs.rowCount == 0){
                    // return { "Code" : 1, "Msg" : "There are No CY code", "Rows" : "" };
                    comboList.push({ Name: "-1", DisplayName: "There are No CY code" });
                }

                for (let i = 0; i < case3result.cs.rowCount; i++) {
                    let itemName = case3result.cs.row(i).cell(case3result.cs.memberColumnIndex("To Item","To Item")).Name;
                    comboList.push({ Name: itemName, DisplayName: itemName });
                }
            }

            cLib.debug("################### fn_cb_prodItem_test ===> finish");

            cLib.debug("ComboData : " + JSON.stringify(comboList));

            cLib.programEnd();

            return { "Code" : 0, "Msg" : "", "Rows" : comboList };   // ui 에서 호출할 경우
        } catch ( e ) {
            cLib.error(e.message);
            return { "Code" : -1, "Msg" : e.message };
        }
    };

    /**
     * code 0, code 1, code 2 return
     * code 0 : To Item 값 리턴
     * code 1 or code 2 : message 리턴
     * return { code:0 , name: To Item 값}
     * return { code:1 , name: "[From Item]' is already exist.'"}
     * return { code:2 , name: "There are No CY Code"}
     * 
     * @param {*} o9Params 
     * @returns 
     */
    var fn_getLcmCodeMap_toItem = function(parsedParams){
        const cLib = fn_cLib(programName + "." + arguments.callee.name);
        cLib.setLogLevel("Debug");

        try {
            cLib.debug("==========================> fn_getLcmCodeMap_toItem ");
            cLib.debug("parsedParams :: "+JSON.stringify(parsedParams));

            
            let fbLocation = parsedParams.fbParams["[Location].[Location]"];
            let fbSubLocation = parsedParams.fbParams["[Sub Location].[Sub Location]"];
            let fbPOItem = parsedParams.fbParams["[Item].[Item]"];

            let col03List = fn_AdhocCol03(parsedParams, "3");   // 배열로 리턴 V or H 
            cLib.debug("============ fn_getLcmCodeMap_toItem > col03List.length : "+col03List.length);

            // 기준 데이터 없으면 
            if( col03List.length == 0 ){
                return {code:"2", name:"ADHOC_Col03 Data 없음."};
            }

            // Code 0 : 1 쿼리 (A)
            let whereA = 'where {'
                        + cUtil.fn_getFilterQuery(parsedParams, "[Version].[Version Name]")
                        +', [Location].[Location].[P105]'
                        +', [Category].[Category].[MODEL]'
                        +', Measure.[LCM Code MAP_Status] == "COM"'
                        +', [Item].[Item]'+ cUtil.fn_filterStr(fbPOItem)
                        +'}';

            let resultA = cLib.selectList(['[To Item].[To Item].filter(#.Name startswith "CY-").filter(#.Name endswith "'+col03List[0]+'")'],
                                            ["Measure.[LCM Code MAP_Status]"],
                                            whereA, // where
                                            "",
                                            "limit 100");
            cLib.printCsData(resultA, 3);

            let toItemA = [];
            for (let i = 0; i < resultA.cs.rowCount; i++) {
                let itemName = resultA.cs.row(i).cell(resultA.cs.memberColumnIndex("To Item","To Item")).Name;
                // toItemA.push({ Name: itemName });
                toItemA.push(itemName);
            }

            // Code 0 : 1 쿼리 (B) > 이미 등록된 데이터
            let whereB = 'where {'
                        + cUtil.fn_getFilterQuery(parsedParams, "[Version].[Version Name]")
                        +',[Location].[Location]'+cUtil.fn_filterStr(fbLocation)
                        +',[Item].[Item]'+cUtil.fn_filterStr(fbPOItem)
                        +',[Category].[Category].[MODEL]'
                        +'}';

            let resultB = cLib.selectList(['[To Item].[To Item]'],
                                            ["Measure.[LCM Code MAP_Status]"],
                                            whereB, // where
                                            "",
                                            "limit 100");
            cLib.printCsData(resultB, 3);

            let toItemB = [];
            for (let i = 0; i < resultB.cs.rowCount; i++) {
                let itemNameB = resultB.cs.row(i).cell(resultB.cs.memberColumnIndex("To Item","To Item")).Name;
                // toItemB.push({ Name: itemName });
                toItemB.push(itemNameB);
            }

            // 기준 데이터 없으면 
            if( toItemA.length == 0 ){
                return {code:"2", name:"There are No CY Code."};
            }

            // ( toItemA - toItemdB ) 결과 : toItemB 에 없는 Item
            let setB = new Set(toItemB);
            let selectableItems = toItemA.filter( a => !setB.has(a));
            cLib.debug("### toItemA - toItemB = selectableItems > selectableItems" + selectableItems);

            // ( toItemA - toItemdB ) = 0 일 경우 이미 모두 등록된 상태임
            // CY 코드가 이미 존재하여  [From Item]' is already exist.'
            if( selectableItems.length == 0 ){
                return {code:"1", name:"CY 코드 이미 존재 함."};
            }else{
                return {code:"0", name:selectableItems[0]};
            }

        } catch ( e ) {
            cLib.error(e.message);
            return { "Code" : -1, "Msg" : e.message };
        }
    };

    /**
     * ADHOC_Col03 구하기
     * 
     * @param {*} o9Params 
     * @returns 
     */
    var fn_AdhocCol03 = function(parsedParams, paramType){
        const cLib = fn_cLib(programName + "." + arguments.callee.name);
        cLib.setLogLevel("Debug");

        try {
            cLib.debug("==========================> fn_AdhocCol03 ");
            cLib.debug("parsedParams :: "+JSON.stringify(parsedParams));

            var fbVersion = cUtil.fn_getFilterValue(parsedParams, "[Version].[Version Name]");

            let result = "";

            if( paramType == "1"){

                cLib.debug("==========================> fn_AdhocCol03 : paramType => "+paramType);

                let where = 'where {'
                            + '[Version].[Version Name].['+fbVersion+']'
                            +',[Adhoc].[Adhoc].[MTA_VENDORMAP_COMP]'
                            +',Measure.[ADHOC_Col04] == "Y"'
                            +'}';

                result = cLib.selectList(["[Item].[Item]"],
                                                ["Measure.[ADHOC_Col03]"],
                                                where, // where
                                                "", // orderby
                                                "");  // limit 1000

                cLib.printCsData(result, 3);

            }else if( paramType == "2"){
                cLib.debug("==========================> fn_AdhocCol03 : paramType => "+paramType);

                let fbLocation = parsedParams.fbParams["[Location].[Location]"];
                let fbSubLocation = parsedParams.fbParams["[Sub Location].[Sub Location]"];
                let fbPOItem = parsedParams.fbParams["[Item].[Item]"];

                let resultCategory = cLib.selectList(["[Item].[Item]"+ cUtil.fn_filterStr(fbPOItem),"[Item].[Class Category]"], [], "", "", "");
                var fbItemClassCategory = resultCategory.cs.row(0).cell(resultCategory.cs.memberColumnIndex("Item", "Class Category")).Name;

                let where = 'where {'
                            + '[Version].[Version Name].['+fbVersion+']'
                            +',[Adhoc].[Adhoc].[MTA_VENDORMAP_COMP]'
                            +',Measure.[ADHOC_Col04] == "Y"'
                            +',[Location].[Location]'+cUtil.fn_filterStr(fbLocation)
                            +',[Sub Location].[Sub Location]'+cUtil.fn_filterStr(fbSubLocation)
                            +',Measure.[ADHOC_Col02] == "'+fbItemClassCategory+'"' // (Item.Class Category)
                            +'}';

                result = cLib.selectList(["[Item].[Item]"],
                                                ["Measure.[ADHOC_Col03]"],
                                                where, // where
                                                "", // orderby
                                                "");  // limit 1000

                cLib.printCsData(result, 3);

            }else if( paramType == "3"){
                cLib.debug("==========================> fn_AdhocCol03 : paramType => "+paramType);
                // ( SELECT ADHOC_Col03 FROM [Adhoc].[Adhoc].[MTA_CODE_COMP] 
                //     WHERE ADHOC_Col01 = 'COMP' 
                //       AND ADHOC_Col02 = 'DOM_CY_ADD'
                //       AND ADHOC_Col04 = 'Y'
                //       AND [Location].[Location] = :paramMap.fromsiteid -- FROMSITEID
                //       AND [Sub Location].[Sub Location] = :paramMap.tositeid -- TOSITEID
                //  )

                let fbLocation = parsedParams.fbParams["[Location].[Location]"];
                let fbSubLocation = parsedParams.fbParams["[Sub Location].[Sub Location]"];
                let fbPOItem = parsedParams.fbParams["[Item].[Item]"];

                let resultCategory = cLib.selectList(["[Item].[Item]"+ cUtil.fn_filterStr(fbPOItem),"[Item].[Class Category]"], [], "", "", "");
                var fbItemClassCategory = resultCategory.cs.row(0).cell(resultCategory.cs.memberColumnIndex("Item", "Class Category")).Name;

                let where = 'where {'
                            + '[Version].[Version Name].['+fbVersion+']'
                            +',[Adhoc].[Adhoc].[MTA_CODE_COMP]'
                            +',Measure.[ADHOC_Col01] == "COMP"'
                            +',Measure.[ADHOC_Col02] == "DOM_CY_ADD"'
                            +',Measure.[ADHOC_Col04] == "Y"'
                            +',[Location].[Location]'+cUtil.fn_filterStr(fbLocation)
                            +',[Sub Location].[Sub Location]'+cUtil.fn_filterStr(fbSubLocation)
                            +'}';

                result = cLib.selectList(["[Item].[Item]"],
                                                ["Measure.[ADHOC_Col03]"],
                                                where, // where
                                                "", // orderby
                                                "");  // limit 1000

                cLib.printCsData(result, 3);

            }

            if( result.cs.rowCount == 0){
                cLib.debug("######### fn_AdhocCol03 : ADHOC_Col03 해당 값이 없습니다 ");
                // return { "Code" : 1, "Msg" : "ADHOC_Col03 해당 값이 없습니다.", "Rows" : "" };
            }

            let adhocCol03List = [];
            for (let i = 0; i < result.cs.rowCount; i++) {
                adhocCol03List.push(result.cs.row(i).cell(result.cs.measureColumnIndex("ADHOC_Col03")));
            }
            
            let col03List = [...new Set(
                adhocCol03List
                    .filter(v => v)
                    .flatMap(v => v.split(',').map(s => s.trim()))
                    .filter(v => v !== "")
            )];

            return col03List;   // AHDOC_Col03 배열로 리턴
            

        } catch ( e ) {
            cLib.error(e.message);
            return { "Code" : -1, "Msg" : e.message };
        }
    };

    /**
     * Case 확인
     * 
     * @param {*} o9Params 
     * @returns 
     */
    var fn_caseType = function(parsedParams, paramType){
        const cLib = fn_cLib(programName + "." + arguments.callee.name);
        cLib.setLogLevel("Debug");

        try {
            cLib.debug("==========================> fn_caseType ");
            cLib.debug("parsedParams :: "+JSON.stringify(parsedParams));

            let fbLocation = parsedParams.fbParams["[Location].[Location]"];
            let fbSubLocation = parsedParams.fbParams["[Sub Location].[Sub Location]"];
            let fbPOItem = parsedParams.fbParams["[Item].[Item]"];

            let resultCategory = cLib.selectList(["[Item].[Item]"+ cUtil.fn_filterStr(fbPOItem),"[Item].[Class Category]"], [], "", "", "");
            let fbItemClassCategory = resultCategory.cs.row(0).cell(resultCategory.cs.memberColumnIndex("Item", "Class Category")).Name;
            
            let result = "";

            cLib.debug("## fbItemClassCategory : "+fbItemClassCategory);

            // -- CASE 확인
            // SELECT CASE WHEN Measure.[ADHOC_Col02] = Measure.[ADHOC_Col03] AND Measure.[ADHOC_Col01] = 'CLASSCATEGORY' THEN 'CASE1'
            //                          WHEN Measure.[ADHOC_Col02] <> Measure.[ADHOC_Col03] AND Measure.[ADHOC_Col01] =  'CLASSCATEGORY' THEN 'CASE2'
            //                          WHEN Measure.[ADHOC_Col02] <> Measure.[ADHOC_Col03] AND Measure.[ADHOC_Col01] IN ('ALL', 'IOT', 'MKD') THEN 'CASE3'
            //                 ELSE 'CASE4'
            //                 END CHK
            // FROM [Adhoc].[Adhoc].[MTA_VENDORMAP_COMP]
            //  WHERE [Sub Location].[Sub Location] = :parammap.tositeid (Sub Location)
            // AND Measure.[ADHOC_Col02] = :parammap.classcategory (Item.Class Category)
            // AND [Location].[Location] = :parammap.fromsiteid (Location)
            // AND Measure.[ADHOC_Col04] = 'Y' 

            let where = "";
            if( paramType == "1"){
                // -- CASE 확인
                where = 'where {'
                                + cUtil.fn_getFilterQuery(parsedParams, "[Version].[Version Name]")
                                +', [Location].[Location]'+ cUtil.fn_filterStr(fbLocation)
                                +', [Sub Location].[Sub Location]'+ cUtil.fn_filterStr(fbSubLocation)
                                +', [Adhoc].[Adhoc].[MTA_VENDORMAP_COMP] '  // default
                                +', Measure.[ADHOC_Col02] == "'+fbItemClassCategory+'"' // (Item.Class Category)
                                +'}';
            }else if( paramType == "2"){
                where = 'where {'
                                + cUtil.fn_getFilterQuery(parsedParams, "[Version].[Version Name]")
                                +', [Location].[Location]'+ cUtil.fn_filterStr(fbLocation)
                                +', [Sub Location].[Sub Location]'+ cUtil.fn_filterStr(fbSubLocation)
                                +', [Adhoc].[Adhoc].[MTA_VENDORMAP_COMP] '  // default
                                +', Measure.[ADHOC_Col02] == "'+fbItemClassCategory+'"' // (Item.Class Category)
                                +', Measure.[ADHOC_Col04] == "Y" '
                                +'}';
            }
            result = cLib.selectList(["[Item].[Item]"],
                                            ["Measure.[ADHOC_Col01]","Measure.[ADHOC_Col02]","Measure.[ADHOC_Col03]"],
                                            where, // where
                                            "",
                                            "limit 100");
            cLib.printCsData(result, 3);

            let vCase = "caseX";
            if( result.cs.rowCount == 0 ){
                cLib.debug("############################ rowCount = 0 , Case 해당 없음");
                return vCase;
            }
            
            let ADHOC_Col01 = result.cs.row(0).cell(result.cs.measureColumnIndex("ADHOC_Col01"));
            let ADHOC_Col02 = result.cs.row(0).cell(result.cs.measureColumnIndex("ADHOC_Col02"));
            let ADHOC_Col03 = result.cs.row(0).cell(result.cs.measureColumnIndex("ADHOC_Col03"));

            // cLib.debug("## ADHOC_Col01 : ["+ADHOC_Col01+"]");

            cLib.debug(`ADHOC_Col01:[${ADHOC_Col01}] , ADHOC_Col02:[${ADHOC_Col02}] , ADHOC_Col03:[${ADHOC_Col03}]`);

            //----------------------------------------------------------------------------------------------------------------------//
            // Case 1
            //Measure.[ADHOC_Col02] = Measure.[ADHOC_Col03] AND Measure.[ADHOC_Col01] = 'CLASSCATEGORY'
            // Case 2
            // Measure.[ADHOC_Col02] <> Measure.[ADHOC_Col03] AND Measure.[ADHOC_Col01] =  'CLASSCATEGORY'
            // Case 3
            // Measure.[ADHOC_Col02] <> Measure.[ADHOC_Col03] AND Measure.[ADHOC_Col01] IN ('ALL', 'IOT', 'MKD')
            //----------------------------------------------------------------------------------------------------------------------//
            // Case 1


            if ( ADHOC_Col01 === "CLASSCATEGORY" && (ADHOC_Col02 == ADHOC_Col03)){
                vCase = "case1";
            } else if ( ADHOC_Col01 === "CLASSCATEGORY" && (ADHOC_Col02 != ADHOC_Col03)){
                if(paramType == "1"){
                    vCase = "case2";
                }else if(paramType == "2"){
                    if ( fbSubLocation.toUpperCase().endsWith("KD")){
                        vCase = "case2";
                    }else{
                        vCase = "case1";
                    }
                }
            }else{
                // Case 3 : (ADHOC_Col01 == "ALL" || ADHOC_Col01 == "IOT" || ADHOC_Col01 == "MKD") && (ADHOC_Col02 != ADHOC_Col03))
                let caseArr = ["ALL","IOT","MKD"];
                let bArr = (ADHOC_Col01 || "")
                        .split(',')
                        .map(v => v.trim())
                        .filter(v => v);

                // ADHOC_Col01 == "ALL" || ADHOC_Col01 == "IOT" || ADHOC_Col01 == "MKD")
                let col01 = caseArr.some(v => bArr.includes(v)) ? true : false;

                if( col01 && (ADHOC_Col02 != ADHOC_Col03) ){    // (ADHOC_Col01 == "ALL" || ADHOC_Col01 == "IOT" || ADHOC_Col01 == "MKD") && (ADHOC_Col02 != ADHOC_Col03))
                    vCase = "case3";
                }else{
                    vCase = "case4";
                }

            }

            cLib.debug("################### vCase ===> "+ vCase);
            return vCase;

        } catch ( e ) {
            cLib.error(e.message);
            return { "Code" : -1, "Msg" : e.message };
        }
    };

    /**
     * Create BOD 재생성 2026.03.24
     * {"fbFuncName":"fn_createBOD"
        ,"fbGridRows":[{"rowstatus":"U","rowindex":0,"[Version].[Version Name]":"CWV_MP","[Location].[Location]":"P105LCD","[Sub Location].[Sub Location]":"P105","[Item].[Item]":"BN90-12360A","[To Item].[To Item]":"BN90-12360A"}
        ,{"rowstatus":"U","rowindex":1,"[Version].[Version Name]":"CWV_MP","[Location].[Location]":"P105LCD","[Sub Location].[Sub Location]":"P105","[Item].[Item]":"BN90-12360C","[To Item].[To Item]":"BN90-12360C"}]
        ,"fbParams":{"filters":{"[Version].[Version Name]":{"SelectedMembers":["CWV_MP"],"SelectedMembersAlias":["202608_P"],"MemberFilter":"&CWVUI","DimensionAliasName":"Plan ID"}}} }

     * @param {*} o9Params 
     * @returns 
     */
    var fn_createBOD = function(parsedParams){
        const cLib = fn_cLib(programName + "." + arguments.callee.name);
        cLib.setLogLevel("Debug");

        try {
            cLib.debug("==========================> fn_createBOD ");
            cLib.debug("parsedParams :: "+JSON.stringify(parsedParams));

            // createBOD 실행중인지 체크
            let result = cLib.selectList(["&CWVUI"]
                                            , ["Measure.[VersionInfo_RunningFlag_LCMProductCopyCreateBOD]"]
                                            , "where {Measure.[VersionInfo_RunningFlag_LCMProductCopyCreateBOD] == true }"
                                            , "", "");

            if ( result.cs.rowCount > 0 ){
                return { "Code" : 1, "Msg" : "실행중입니다"};
            }

            for ( var i=0; i<parsedParams.fbGridRows.length; i++){

                let row = parsedParams.fbGridRows[i];

                let dimension = [];
                dimension.push(cUtil.fn_qDimVersionName(parsedParams));
                dimension.push(cUtil.fn_qDim(row, "[Location].[Location]"));
                dimension.push(cUtil.fn_qDim(row, "[Sub Location].[Sub Location]"));
                dimension.push(cUtil.fn_qDim(row, "[Item].[Item]"));
                dimension.push(cUtil.fn_qDim(row, "[To Item].[To Item]")); // 2026.03.16 Measure -> grain 으로 변경 (이상엽p요청)

                let measure = [];
                /* Update일자, 사용자 정보입력 */
                measure.push(cUtil.fn_qMeaUpdateUserName("Measure.[Code Map LCM_Updated By]"));
                measure.push(cUtil.fn_qMeaUpdateTime("Measure.[Code Map LCM_Update Time]"));

                cLib.updateMeasure(dimension, measure);

                // 3. 선택한 row 들 intersection에 Flag 처리
                cLib.updateMeasure(dimension, ['Measure.[Code Map LCM_Create BOD_Target Flag]  = true;']);

            }

            fn_py_createBOD(parsedParams);   // Python 호출 (PY_UI_CodeMapLCMCreateBOD)

            // PY 종료 후 Flag 원복 - createBOD 실행 종료
            cLib.updateMeasure(["&CWVUI"], ['Measure.[VersionInfo_RunningFlag_LCMProductCopyCreateBOD]  = false;']);
            cLib.updateMeasure(["&CWVUI"], ['Measure.[Code Map LCM_Create BOD_Target Flag]  = null;']);

            cLib.programEnd();

            //  정상 저장 후 리턴 값?? Warn 종류는 저장은 되고, 화면으로 메세지 리턴해줘야 함
            return { "Code" : 0, "Msg" : "", "Rows" : parsedParams.fbGridRows };  // 오류 dataset Return

        } catch ( e ) {
            cLib.error(e.message);
            return { "Code" : -1, "Msg" : e.message };
        }
    };

    /**
     * code Map LCM 의 데이타로 BOD List의 TP mode 만큼 확장 row 생성, 생성 data 와 BOD Item 에 없는  data 생성 하는 로직 (insert O, update X)
     * @param {*} parsedParams 
     * @returns 
     */
    var fn_py_createBOD = function(parsedParams){
        const cLib = fn_cLib(programName + "." + arguments.callee.name);
        cLib.setLogLevel("Debug");

        try {
            cLib.debug(" fn_py_createBOD 실행 :: parsedParams :: "+JSON.stringify(parsedParams));
            // cLib.debug("cUtil.fn_getFilterVersion :: "+ cUtil.fn_getFilterVersion(parsedParams));
            let fbLocation = [...new Set(parsedParams.fbGridRows.map(row => row["[Location].[Location]"]))];
            let fbSubLocation = [...new Set(parsedParams.fbGridRows.map(row => row["[Sub Location].[Sub Location]"]))];
            let fbPOItem = [...new Set(parsedParams.fbGridRows.map(row => row["[Item].[Item]"]))];
            let fbProdItem = [...new Set(parsedParams.fbGridRows.map(row => row["[To Item].[To Item]"]))];

            /* PY 호출 (PY_UI_CodeMapLCMCreateBOD) */
            var execQuery = 'EXEC plugin instance [PY_UI_CodeMapLCMCreateBOD] ' +
                            'for measures {[Code Map LCM_Create BOD_Target Flag]} ' +
                            'using scope ( ' +
                                // '&CWVUI '+ ' * ' +
                                cUtil.fn_getFilterVersion(parsedParams) + ' * ' +      // [Version].[Version Name].[CWV_MP]
                                '[Location].[Location]' + cUtil.fn_filterStr(fbLocation) + ' * ' +
                                '[Sub Location].[Sub Location]'+ cUtil.fn_filterStr(fbSubLocation) + ' * ' +
                                '[Item].[Item]'+ cUtil.fn_filterStr(fbPOItem) + ' * ' +
                                '[To Item].[To Item]'+ cUtil.fn_filterStr(fbProdItem) + 
                                ' )'+
                            'using arguments {(ExecutionMode, "MediumWeight"), (MaxSliceTableCells, 200000000), (MaxConcurrency, 1), ([Param.o9_sys_log_level], "DEBUG")}; ';

            cLib.debug("execQuery: " + JSON.stringify(execQuery));
            cLib.executeQuery("fn_createBOD : PY_UI_CodeMapLCMCreateBOD Run", execQuery);

            cLib.programEnd();

            return { "Code" : 0, "Msg" : "", "Rows" : "" };

        } catch ( e ) {
            cLib.error(e.message);
            return { "Code" : -1, "Msg" : e.message };
        }
    };

    /**
     * fn_save
     * 
     * @param {*} o9Params 
     * @returns 
     */
    var fn_save = function(parsedParams){
        const cLib = fn_cLib(programName + "." + arguments.callee.name);
        cLib.setLogLevel("Debug");

        try {
            cLib.debug("==========================> LCM BOD Product Copy >> fn_save ");
            cLib.debug("parsedParams :: "+JSON.stringify(parsedParams));

            for ( var i=0; i<parsedParams.fbGridRows.length; i++){

                let row = parsedParams.fbGridRows[i];
                let rowstatus = row["rowstatus"];
                row["rowmsg"] = null;
                cLib.debug("rowstatus :: "+rowstatus);

                let dimension = [];
                dimension.push(cUtil.fn_qDimVersionName(parsedParams));
                dimension.push(cUtil.fn_qDim(row, "[Location].[Location]"));
                dimension.push(cUtil.fn_qDim(row, "[Sub Location].[Sub Location]"));
                dimension.push(cUtil.fn_qDim(row, "[Item].[Item]"));
                dimension.push(cUtil.fn_qDim(row, "[To Item].[To Item]")); // 2026.03.16 Measure -> grain 으로 변경 (이상엽p요청)

                // 기존 data 중복여부에 대한 체크
                if( rowstatus == "C") {

                    // 중복체크
                    if ( !cLib.existMeasure(dimension
                                                ,["Measure.[Code Map LCM_Valid Flag]", "Measure.[Code Map LCM_Map Status]","Measure.[Code Map LCM_Create BOD_Target Flag]"]
                                                , "") ) {
                        // Main MG 생성
                        cLib.createMeasure(dimension, ['Measure.[Code Map LCM_Valid Flag]     = "Y";']);
                        cLib.updateMeasure(dimension, ['Measure.[Code Map LCM_Map Status]     = "COM";'
                                                        , cUtil.fn_qMeaUpdateUserName('Measure.[Code Map LCM_Created By]')
                                                        , cUtil.fn_qMeaUpdateUserName('Measure.[Code Map LCM_Updated By]')
                                                        , cUtil.fn_qMeaUpdateTime('Measure.[Code Map LCM_Creation Time]')
                                                        , cUtil.fn_qMeaUpdateTime('Measure.[Code Map LCM_Update Time]')
                                                        ]);
                    }else{
                        // 중복 일 경우 리턴 메세지
                        return { "Code" : 1, "Msg" : "The Item had duplicated", "Rows" : "" };
                    }

                } else if( rowstatus == "U") {

                    let measure = [];
                    measure.push(cUtil.fn_qMeaStr(row, "Measure.[Code Map LCM_Valid Flag]"));
                    measure.push(cUtil.fn_qMeaUpdateUserName("Measure.[Code Map LCM_Updated By]"));
                    measure.push(cUtil.fn_qMeaUpdateTime("Measure.[Code Map LCM_Update Time]"));

                    cLib.updateMeasure(dimension, measure);
                }

            } // end for

            cLib.programEnd();

            return { "Code" : 0, "Msg" : "", "Rows" : "" };

        } catch ( e ) {
            cLib.error(e.message);
            return { "Code" : -1, "Msg" : e.message };
        }
    };

    /**
     *  Confirm 로직
     *   {"fbFuncName" : "fn_confirm", 
        "fbParams" : {"filters":{"[Version].[Version Name]":{"SelectedMembers":["CWV_MP"],"MemberFilter":"&CWVUI"}}}
        ,"fbGridRows":[
        {"rowstatus":"U"
        ,"groupkey":"0,0,0,0,0"
        ,"[Version].[Version Name]":"CWV_MP"
        ,"[Location].[Location]":"-"
        ,"[Item].[Item]":"BN95-07132A"
        ,"[To Item].[To Item]":"CY-PT340KGHV1V"
        } ]
        }
     * @param {*} parsedParams 
     * @returns 
     */
    var fn_confirm = function(parsedParams){
        const cLib = fn_cLib(programName + "." + arguments.callee.name);
        cLib.setLogLevel("Debug");
        cLib.debug("Confirm >>  fn_confirm ==========================================================>");
        try {
            cLib.debug("parsedParams :: "+JSON.stringify(parsedParams));

            for ( var i=0; i<parsedParams.fbGridRows.length; i++){
                let row = parsedParams.fbGridRows[i];

                // FromSite
                if( row["[Location].[Location]"] == "-" ){
                    cLib.debug("########## From Site Check!! ");
                    return { "Code" : 1, "Msg" : "From Site Check!!", "Rows" : "" };
                }

                // Prod Item
                if( row["[To Item].[To Item]"] == "-" ){
                    cLib.debug("########## Item(From) Check!");
                    return { "Code" : 1, "Msg" : "Item(From) Check!!", "Rows" : "" };
                }

                let dimension = [];
                dimension.push(cUtil.fn_qDimVersionName(parsedParams));
                dimension.push(cUtil.fn_qDim(row, "[Location].[Location]"));
                dimension.push(cUtil.fn_qDim(row, "[Sub Location].[Sub Location]"));
                dimension.push(cUtil.fn_qDim(row, "[Item].[Item]"));
                dimension.push(cUtil.fn_qDim(row, "[To Item].[To Item]")); // 2026.03.16 Measure -> grain 으로 변경 (이상엽p요청)

                let measure = [];
                measure.push('Measure.[Code Map LCM_Map Status]  = "COM";');
                measure.push(cUtil.fn_qMeaUpdateUserName("Measure.[Code Map LCM_Updated By]"));
                measure.push(cUtil.fn_qMeaUpdateTime("Measure.[Code Map LCM_Update Time]"));

                cLib.updateMeasure(dimension, measure);

            } // end for

            cLib.programEnd();

        } catch ( e ) {
            cLib.error(e.message);
            return { "Code" : -1, "Msg" : e.message };
        }
    };

    // Mapping 함수 정의, 마지막에 선언을 해야 함수를 정상적으로 인식함
    const functionMap = {
        "fn_cb_location"        : fn_cb_location
       ,"fn_cb_subLocation"     : fn_cb_subLocation
       ,"fn_cb_poItem"          : fn_cb_poItem
       ,"fn_cb_prodItem"        : fn_cb_prodItem
       ,"fn_createBOD"          : fn_createBOD
       ,"fn_save"               : fn_save
       ,"fn_confirm"            : fn_confirm
       ,"fn_cb_prodItem_value"  : fn_cb_prodItem_value
    };

    return {
        fn_loadFunction : fn_loadFunction
    };

});

/*--------------------------------------------------------------------------------------------------*/
/* 
    프로그램명 : o9.NSCM.JSEWLCMBODProductCopy
    화면명 : LCM BOD Product & Copy (EW)
    Action Button : EWLCMBODProductCopy
    [history]
    2025.10.29 : 공통소스 반영
    2025.11.05 : syif1380.lee : n_qMeaUpdateUser() => fn_qMeaUpdateUserName() 로 변경
    2025.12.29 : 콤보에 filter 적용
    2026.03.16 : Code Map LCM_Prod Item -> [To Item].[To Item] 으로 변경
    2026.03.18 : fn_save : Code Map LCM_Prod Item -> 저장시 메저 삭제
    2026.03.18 : fn_confirm : validation, grain 변경
    2026.03.19 : fn_cb_poItem 콤보 로직 변경
                fn_cb_prodItem 콤보 로직 변경
                fn_cb_prodItem_value : Prod Item 디폴트 값 세팅 함수 추가
    2026.03.23 : fn_cb_prodItem, fn_cb_prodItem_value 수정
    2026.03.26 : fn_createBOD 수정, fn_py_createBOD 별도 함수 생성
    2026.03.26 : commonLib 선언 부분 변경 및 공통함수 이름 변경
*/
/*--------------------------------------------------------------------------------------------------*/