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

    /**
     * Item (PO Item) Key 값 조회 : 2026.04.16 변경
     * UI 에서 PO Item 코드 입력 후 Enter key 입력시 호출
     * Actiion Button : EWLCMBODProductCopy
     * {"fbFuncName" : "fn_cb_poItem", "fbParams" : {"[Item].[Item]":"BN95-0694"}}
     *
     * @param {*} parsedParams
     * @returns
     */
    var fn_cb_poItem = function(parsedParams){
        const cLib = fn_cLib(programName + "." + arguments.callee.name);
        cLib.setLogLevel("Debug");

        try {
            let fbItem = parsedParams.fbParams["[Item].[Item]"];

            // SELECT &LCMProdCopyItem.filter(#.Name contains "bn95") limit 50;
            let result = cLib.selectList(['&LCMProdCopyItem.filter(#.Name contains "'+fbItem+'")'], "", "", "", "Limit 1000");   // 전체 row : 31,370

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

            cLib.debug("######################################### fn_cb_prodItem ===> start");

            let comboList = [];
            
            let fbLocation = parsedParams.fbParams["[Location].[Location]"];
            let fbSubLocation = parsedParams.fbParams["[Sub Location].[Sub Location]"];
            let fbPOItem = parsedParams.fbParams["[Item].[Item]"];
            let fbProdItem = parsedParams.fbParams["[To Item].[To Item]"];  // Prod Item 입력 데이터 (key in)

            // .filter(#.Name contains "'+fbProdItem+'")'
            // let fbProdItemCond = fbProdItem ? '.filter(#.Name contains "'+fbProdItem+'")' : '';
            let fbProdItemCond = (fbProdItem != null && fbProdItem !== "") ? '.filter(#.Name contains "'+fbProdItem+'")' : '';

            let result = cLib.selectList(["[Item].[Item]"+ cUtil.fn_filterStr(fbPOItem),"[Item].[Class Category]"], [], "", "", "");
            var fbItemClassCategory = result.cs.row(0).cell(result.cs.memberColumnIndex("Item", "Class Category")).Name;
            cLib.debug("## fbItemClassCategory : "+fbItemClassCategory);

            // Case 확인
            let vCase = fn_caseType(parsedParams, "");

            cLib.debug("### vCase : "+vCase);

            if( vCase == "caseX"){
                return { "Code" : 1, "Msg" : ""};
            }

            //----------------------------------------------------------------------------------------------------------------------//
            // CASE 2
            //----------------------------------------------------------------------------------------------------------------------//
            if( vCase == "case2"){
                cLib.debug("################### vCase ===> 2");

                //----------------------------------------------------------------------------------------------------//
                // 1. Vendor Map_Prod Map 구하기
                //----------------------------------------------------------------------------------------------------//
                //where {[Location].[Location].[P306LCD], [Sub Location].[Sub Location].[P306], [Item].[Class Category].[95DZ], Measure.[Vendor Map_Valid] == "Y"}
                let case2Where = 'where {'
                                + cUtil.fn_getFilterQuery(parsedParams, "[Version].[Version Name]")
                                +',[Location].[Location]'+ cUtil.fn_filterStr(fbLocation)
                                +',[Sub Location].[Sub Location]'+ cUtil.fn_filterStr(fbSubLocation)
                                +',[Item].[Class Category]'+ cUtil.fn_filterStr(fbItemClassCategory)
                                +',Measure.[Vendor Map_Valid] == "Y"'
                                +'}';
                let case2result = cLib.selectList(["[Category].[Category]"], ["Measure.[Vendor Map_Prod Map]"], case2Where, "", "limit 1000");

                let vendorProdMapList = [];
                for (let i = 0; i < case2result.cs.rowCount; i++) {
                    vendorProdMapList.push(case2result.cs.row(i).cell(case2result.cs.measureColumnIndex("Vendor Map_Prod Map")));
                }
                
                //----------------------------------------------------------------------------------------------------//
                // 2. 최종 Item 구하기 (combo Data)
                //----------------------------------------------------------------------------------------------------//
                let resultItem = [];
                if( vendorProdMapList.length > 0){
                    // let resultItem = cLib.selectList(["[Item].[Item]"], [], "where { "+'[Item].[Class Category]'+ cUtil.fn_filterStr(vendorProdMapList)+"}", "", "");
                    // Prod Item 입력 데이터 (key in)
                    resultItem = cLib.selectList(['[Item].[Item]'+fbProdItemCond], [], "where { "+'[Item].[Class Category]'+ cUtil.fn_filterStr(vendorProdMapList)+"}", "", "limit 1000");
                }
                for (let i = 0; i < resultItem.cs.rowCount; i++) {
                    let itemName = resultItem.cs.row(i).cell(resultItem.cs.memberColumnIndex("Item","Item")).Name;
                    let itemDisplayName = resultItem.cs.row(i).cell(resultItem.cs.memberColumnIndex("Item","Item")).DisplayName;
                    comboList.push({ Name: itemName, DisplayName: itemDisplayName, Flag: "0" });
                }

            //----------------------------------------------------------------------------------------------------------------------//
            // CASE 2 이외
            //----------------------------------------------------------------------------------------------------------------------//
            }else{
                cLib.debug("################### vCase2 가 아닐 경우 로직");

                //----------------------------------------------------------------------------------------------------//
                // 1. comboList1 : &LCMProdCopyItem
                //----------------------------------------------------------------------------------------------------//
                cLib.debug("################### 1. comboList1 : &LCMProdCopyItem ");
                let result1 = cLib.selectList(["&LCMProdCopyItem"+fbProdItemCond], "", "", "", "limit 1000");

                let comboList1 = [];
                for (let i = 0; i < result1.cs.rowCount; i++) {
                    let itemName = result1.cs.row(i).cell(result1.cs.memberColumnIndex("Item","Item")).Name;
                    let itemDisplayName = result1.cs.row(i).cell(result1.cs.memberColumnIndex("Item","Item")).DisplayName;
                    comboList1.push({ Name: itemName, DisplayName: itemDisplayName, Flag: "0" });
                }

                cLib.debug("comboList1 --> 1 : " + JSON.stringify(comboList1));
                //----------------------------------------------------------------------------------------------------//

                //----------------------------------------------------------------------------------------------------//
                // 2.1 LCM Code MAP  : To Item 가져오기
                //----------------------------------------------------------------------------------------------------//
                cLib.debug("################### 2.1 LCM Code MAP  : To Item 가져오기 ");
                let where1 = 'where {'
                                + cUtil.fn_getFilterQuery(parsedParams, "[Version].[Version Name]")
                                +',[Location].[Location].[P105]'    // default 값 (하드코딩)
                                +',[Category].[Category].[MODEL] '  // default 값 (하드코딩)
                                +',Measure.[LCM Code MAP_Status] == "COM"'  // default 값 (하드코딩)
                                +',[Item].[Item]'+ cUtil.fn_filterStr(fbPOItem)
                                +'}';
                let result2 = cLib.selectList(['[To Item].[To Item].filter(#.Name startswith "CY-")'+fbProdItemCond],  // "CY-"  default 값 (하드코딩)
                                                ["Measure.[LCM Code MAP_Status]"],
                                                where1,
                                                "",
                                                "limit 1000");
                let getToItem = [];
                for (let i = 0; i < result2.cs.rowCount; i++) {
                    getToItem.push(result2.cs.row(i).cell(result2.cs.memberColumnIndex("To Item","To Item")).Name);
                }

                // 2.1 의 데이타가 있는 경우에만 조회 함 subquery in 조건
                let comboList2 = [];
                if( getToItem.length > 0){
                    //----------------------------------------------------------------------------------------------------//
                    // 2.2 comboList2 : LCM Code MAP 의 To Item == Item (Item Stage : LCD) -> LCM ?
                    //----------------------------------------------------------------------------------------------------//
                    // LCD Item
                    cLib.debug("################### 2.2 [Item].[Item Stage].[LCM] : comboList2 ");
                    let where2 = 'where { [Item].[Item Stage].[LCM] }';
                    let result3 = cLib.selectList(["[Item].[Item]"+ cUtil.fn_filterStr(getToItem)], "", where2, "", "limit 1000");

                    for (let i = 0; i < result3.cs.rowCount; i++) {
                        let itemName = result3.cs.row(i).cell(result3.cs.memberColumnIndex("Item","Item")).Name;
                        let itemDisplayName = result3.cs.row(i).cell(result3.cs.memberColumnIndex("Item","Item")).DisplayName;
                        comboList2.push({ Name: itemName, DisplayName: itemDisplayName, Flag: "0" });
                    }

                }else{
                    cLib.debug("################### 2.1 LCM Code MAP  : To Item 가져오기 => 0 row");
                }
                cLib.debug("comboList --> 2 : " + JSON.stringify(comboList2));

                //----------------------------------------------------------------------------------------------------//
                // 3. comboList = comboList1 + comboList2
                //----------------------------------------------------------------------------------------------------//
                comboList = [...(comboList1 || []), ...(comboList2 || [])];
            }

            cLib.debug("최종 >>>>>> ComboData : " + JSON.stringify(comboList));

            cLib.debug("################### fn_cb_prodItem_test ===> finish");

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
     * {"fbFuncName" : "fn_cb_prodItem_value",
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
            let vCase = fn_caseType(parsedParams, 'fn_cb_prodItem_value');

            if( vCase == "caseX"){
                return { "Code" : 1, "Msg" : "" };
            }

            cLib.debug("### vCase : "+vCase);

            //----------------------------------------------------------------------------------------------------------------------//
            // Case 1
            //----------------------------------------------------------------------------------------------------------------------//
            if( vCase == "case1"){
                cLib.debug("################### vCase ===> 1");

                let case1_Result= fn_getLcmCodeMap_toItem(parsedParams);    // CODE별 Logic 분기

                cLib.debug("################### vCase ===> 1 : case1_Result > "+JSON.stringify(case1_Result));

                // code 0
                if( case1_Result.code == "0"){
                    comboList.push({ Name: case1_Result.name, DisplayName: case1_Result.name });

                // code 1 , code 2
                }else if( case1_Result.code == "1" || case1_Result.code == "2" ){
                    comboList.push({ Name: "-1", DisplayName: case1_Result.name });
                }

                // case1 일때 , code 값 상관없이 입력 Item.Item(Po Item) 값을 그대로 추가 넘김 2026.04.02 이상엽 프로 요청
                comboList.push({ Name: fbPOItem, DisplayName: fbPOItem });

            //----------------------------------------------------------------------------------------------------------------------//
            // Case 2
            //----------------------------------------------------------------------------------------------------------------------//
            }else if( vCase == "case2"){
                // Vendor Map Item => Code Map LCM (MG변경) (2026.03.27 이상엽p)
                cLib.debug("################### vCase ===> 2 > Default Value Setting ");

                let case2Where = 'where {'
                                + cUtil.fn_getFilterQuery(parsedParams, "[Version].[Version Name]")
                                +',[Location].[Location]'+cUtil.fn_filterStr(fbLocation)
                                +',[Sub Location].[Sub Location].filter(#.Name endswith "KD")'
                                +'}';
                let case2result = cLib.selectList(["[Item].[Item]"+ cUtil.fn_filterStr(fbPOItem)], ["Measure.[Code Map LCM_Valid Flag]","Measure.[Code Map LCM_Map Status]"], case2Where, "", "limit 1000");

                for (let i = 0; i < case2result.cs.rowCount; i++) {
                    let itemName = case2result.cs.row(i).cell(case2result.cs.memberColumnIndex("Item","Item")).Name;
                    comboList.push({ Name: itemName, DisplayName: itemName });
                }

            //----------------------------------------------------------------------------------------------------------------------//
            // Case 3 ===> 로직 검토 요청 중 이상엽 프로 04.16 ***********************************
            //----------------------------------------------------------------------------------------------------------------------//
            }else if( vCase == "case3"){

                // ( SELECT Vendor Map_Prod Map
                // FROM Vendor Map
                // WHERE [Sub Location].[Sub Location]  = :parammap.tositeid -- TOSITEID
                //  AND [Item].[Class Category]  = :parammap.classcategory -- CLASSCATEGORY
                //  AND [Location].[Location]  = :parammap.fromsiteid -- FROMSITEID
                //  AND Vendor Map_Valid  = 'Y' )

                //----------------------------------------------------------------------------------------------------//
                // 1. Vendor Map_Prod Map 구하기
                //----------------------------------------------------------------------------------------------------//
                //where {[Location].[Location].[P306LCD], [Sub Location].[Sub Location].[P306], [Item].[Class Category].[95DZ], Measure.[Vendor Map_Valid] == "Y"}
                let case2Where = 'where {'
                                + cUtil.fn_getFilterQuery(parsedParams, "[Version].[Version Name]")
                                +',[Location].[Location]'+ cUtil.fn_filterStr(fbLocation)
                                +',[Sub Location].[Sub Location]'+ cUtil.fn_filterStr(fbSubLocation)
                                +',[Item].[Class Category]'+ cUtil.fn_filterStr(fbItemClassCategory)
                                +',Measure.[Vendor Map_Valid] == "Y"'
                                +'}';
                let case2result = cLib.selectList(["[Category].[Category]"], ["Measure.[Vendor Map_Prod Map]"], case2Where, "", "limit 1000");

                let vendorProdMapList = [];
                for (let i = 0; i < case2result.cs.rowCount; i++) {
                    vendorProdMapList.push(case2result.cs.row(i).cell(case2result.cs.measureColumnIndex("Vendor Map_Prod Map")));
                }

                //----------------------------------------------------------------------------------------------------//
                // 2. 최종 Item 구하기 (combo Data)
                //----------------------------------------------------------------------------------------------------//
                let resultItem = [];
                if( vendorProdMapList.length > 0){

                    let case3Where = 'where {'
                        + cUtil.fn_getFilterQuery(parsedParams, "[Version].[Version Name]")
                        + ', [Location].[Location].[P105]'   // P105 고정
                        + ', [Item].[Item]' + cUtil.fn_filterStr(fbPOItem)
                        + '}';
                    let case3result = cLib.selectList(['[To Item].[To Item].filter(#.Name endswith "' + vendorProdMapList[0] + '")'],
                        ["Measure.[LCM Code MAP_Creation Time]", "Measure.[LCM Code MAP_Status]"],
                        case3Where,
                        "",
                        "limit 1000");

                    if (case3result.cs.rowCount == 0) {
                        comboList.push({Name: "-1", DisplayName: "There are No CY code"});
                    }

                    for (let i = 0; i < case3result.cs.rowCount; i++) {
                        let itemName = case3result.cs.row(i).cell(case3result.cs.memberColumnIndex("To Item", "To Item")).Name;
                        comboList.push({Name: itemName, DisplayName: itemName});
                    }
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
     * CY Flag 를 참조한 To Item (CY 코드) 1건을 조회 한다.
     *
     * @param {*} parsedParams
     * @returns
     */
    var fn_getToItem_CYCode = function(parsedParams){
        const cLib = fn_cLib(programName + "." + arguments.callee.name);
        cLib.setLogLevel("Debug");

        try {
            let fbItem = parsedParams.fbParams["[Item].[Item]"];
            let fbLocation = parsedParams.fbParams["[Location].[Location]"];
            let fbSubLocation = parsedParams.fbParams["[Sub Location].[Sub Location]"];
            let fbPOItem = parsedParams.fbParams["[Item].[Item]"];

            // CY Flag 가져오기
            let cyFlagList = fn_CY_Flag(parsedParams);   // 배열로 리턴 V or H

            // CY를 포함한 To Item 가져온다. (1건)
            let whereA = 'where {'
                        + cUtil.fn_getFilterQuery(parsedParams, "[Version].[Version Name]")
                        +', [Location].[Location].[P105]'
                        +', [Category].[Category].[MODEL]'
                        +', Measure.[LCM Code MAP_Status] == "COM"'
                        +', [Item].[Item]'+ cUtil.fn_filterStr(fbPOItem)
                        +'}';

            let result = cLib.selectList(['[To Item].[To Item].filter(#.Name startswith "CY-").filter(#.Name endswith "'+cyFlagList[0]+'")'],
                                            ["Measure.[LCM Code MAP_Status]"],
                                            whereA, // where
                                            "",
                                            "limit 1000");
            cLib.printCsData(result, 3);

            let toItem = [];
            for (let i = 0; i < result.cs.rowCount; i++) {
                let itemName = result.cs.row(i).cell(result.cs.memberColumnIndex("To Item","To Item")).Name;
                toItem.push(itemName);
            }
            cLib.programEnd();

            return toItem;

        } catch ( e ) {
            cLib.error(e.message);
            return { "Code" : -1, "Msg" : e.message };
        }
    };

    /**
     * fn_cb_prodItem_value >> 디폴트세팅에서 사용
     *
     * CODE별 Logic 분기
     *
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

            //--------------------------------------------------------------------------------------------------------//
            // Code 0 : 1 쿼리 (A)
            // CY Flag 포함한 To Item 가져오기 : [To Item].[To Item].filter(#.Name startswith "CY-")
            //--------------------------------------------------------------------------------------------------------//
            let ToItemCYCode = fn_getToItem_CYCode(parsedParams);   // 배열로 리턴
            cLib.debug("============ CY Flag 포함한 To Item 가져오기 > ToItemCYCode.length : "+ToItemCYCode.length);

            //--------------------------------------------------------------------------------------------------------//
            // Code 0 : 1 쿼리 (B) > 이미 등록된 데이터 (TO Item) 가져오기.
            // AND NOT EXISTS (
            // SELECT 'X' FROM LCM Code MAP B
            // WHERE [Location].[Location] = :paramMap.fromsiteid -- FROMSITEID
            // AND B.[Item].[Item] = :paramMap.poItem -- PO ITEM
            // AND B.[Category].[Category] = 'MODEL'
            // AND B.[To Item].[To Item] = A.FROMITEM // ==> (A 에서 구한 To Item)
            // )
            //--------------------------------------------------------------------------------------------------------//
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
                                            "limit 1000");
            cLib.printCsData(resultB, 3);

            // toItemB -> toItemExists 로 명칭 변경
            let toItemExists = [];
            for (let i = 0; i < resultB.cs.rowCount; i++) {
                let itemNameB = resultB.cs.row(i).cell(resultB.cs.memberColumnIndex("To Item","To Item")).Name;
                toItemExists.push(itemNameB);
            }
            //--------------------------------------------------------------------------------------------------------//

            // 최종 : A-B => A에 있고 B 에 없는 것만 남기
            // 기준 데이터 없으면 (A 자체가 없을 경우)
            if( ToItemCYCode.length == 0 ){
                return {code:"2", name:"There are No CY Code."};
            }

            // ( ToItemCYCode - toItemExists ) 결과 : toItemExists 에 없는 Item
            let setB = new Set(toItemExists);
            let selectableItems = ToItemCYCode.filter( a => !setB.has(a));
            cLib.debug("### ToItemCYCode - toItemExists = selectableItems > selectableItems" + selectableItems);

            // ( ToItemCYCode - toItemExists ) = 0 일 경우 이미 모두 등록된 상태임
            // CY 코드가 이미 존재하여  [From Item]' is already exist.'
            if( selectableItems.length == 0 ){
                return {code:"1", name:"CY 코드 이미 존재 함."};
            }else{
                return {code:"0", name:selectableItems[0], name2:fbPOItem};     // code, To Item(Prod Item), Item(Po Item)
            }

        } catch ( e ) {
            cLib.error(e.message);
            return { "Code" : -1, "Msg" : e.message };
        }
    };

    /**
     * CY Flag 구하기 (이전 ADHOC_Col03 )
     *
     * @param {*} o9Params
     * @returns
     */
    var fn_CY_Flag = function(parsedParams){
        const cLib = fn_cLib(programName + "." + arguments.callee.name);
        cLib.setLogLevel("Debug");

        try {
            cLib.debug("==========================> fn_CY_Flag ");
            cLib.debug("parsedParams :: "+JSON.stringify(parsedParams));

            var fbVersion = cUtil.fn_getFilterValue(parsedParams, "[Version].[Version Name]");
            let result = "";
            let fbLocation = parsedParams.fbParams["[Location].[Location]"];
            let fbSubLocation = parsedParams.fbParams["[Sub Location].[Sub Location]"];
            let fbPOItem = parsedParams.fbParams["[Item].[Item]"];

            let resultCategory = cLib.selectList(["[Item].[Item]"+ cUtil.fn_filterStr(fbPOItem),"[Item].[Class Category]"], [], "", "", "");
            var fbItemClassCategory = resultCategory.cs.row(0).cell(resultCategory.cs.memberColumnIndex("Item", "Class Category")).Name;

            let where = 'where {'
                        // + '[Version].[Version Name].['+fbVersion+']'
                        +' [Location].[Location]'+cUtil.fn_filterStr(fbLocation)
                        +',[Sub Location].[Sub Location]'+cUtil.fn_filterStr(fbSubLocation)
                        +',Measure.[Code Map LCM CY Flag_Valid] == "Y"'
                        +'}';

            result = cLib.selectList(['[Version].[Version Name].['+fbVersion+']'],  ["Measure.[Code Map LCM CY Flag_CY Flag]"], where, "", "");

            cLib.printCsData(result, 3);

            if( result.cs.rowCount == 0){
                cLib.debug("######### fn_CY_Flag : CY Flag 해당 값이 없습니다 ");
            }

            let cyFlagList = [];
            for (let i = 0; i < result.cs.rowCount; i++) {
                cyFlagList.push(result.cs.row(i).cell(result.cs.measureColumnIndex("Code Map LCM CY Flag_CY Flag")));
            }

            return cyFlagList;   // CY Flag 배열로 리턴

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
    var fn_caseType = function(parsedParams, paramName){
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

            let where = "";
            where = 'where {'
                                + cUtil.fn_getFilterQuery(parsedParams, "[Version].[Version Name]")
                                +', [Location].[Location]'+ cUtil.fn_filterStr(fbLocation)
                                +', [Sub Location].[Sub Location]'+ cUtil.fn_filterStr(fbSubLocation)
                                // +', [Item].[Class Category]'+ cUtil.fn_filterStr(fbItemClassCategory)
                                +', Measure.[Vendor Map_Valid] == "Y" '
                                +'}';
            // result = cLib.selectList(["[Location].[Location]","[Sub Location].[Sub Location]","[Item].[Class Category]","[Category].[Category]"],
            result = cLib.selectList(["[Item].[Class Category]"+ cUtil.fn_filterStr(fbItemClassCategory),"[Category].[Category]"],
                                            ["Measure.[Vendor Map_Prod Map]"],
                                            where, // where
                                            "",
                                            "limit 1000");
            cLib.printCsData(result, 3);

            let vCase = "caseX";
            if( result.cs.rowCount == 0 ){
                cLib.debug("############################ rowCount = 0 , Measure.[Vendor Map_Prod Map] 데이터 존재하지 않음.");
                return vCase;
            }
            
            //----------------------------------------------------------------------------------------------------------------------//
            // CASE 확인 : 변경 2026.04.16
            // Case 1
            // [Item].[Class Category] = Vendor Map_Prod Map AND [Category].[Category] = 'CLASSCATEGORY'
            // Case 2
            // [Item].[Class Category] <> Vendor Map_Prod Map AND [Category].[Category] =  'CLASSCATEGORY'
            // Case 3
            // [Item].[Class Category] <> Vendor Map_Prod Map AND [Category].[Category]] IN ('ALL', 'IOT', 'MKD')
            //----------------------------------------------------------------------------------------------------------------------//
            let itemClassCategory = result.cs.row(0).cell(result.cs.memberColumnIndex("Item", "Class Category")).Name;
            let category = result.cs.row(0).cell(result.cs.memberColumnIndex("Category", "Category")).Name;
            let vendorProdMap = result.cs.row(0).cell(result.cs.measureColumnIndex("Vendor Map_Prod Map"));

            cLib.debug(`itemClassCategory:[${itemClassCategory}] , category:[${category}] , vendorProdMap:[${vendorProdMap}] , endsWith(KD) >> fbSubLocation:[${fbSubLocation}]`);
            if( itemClassCategory == vendorProdMap && category == "CLASSCATEGORY" ){
                vCase = "case1";
            }else if( itemClassCategory != vendorProdMap && category == "CLASSCATEGORY" ){
                vCase = "case2";

                if(paramName != null && paramName !== ""){
                    if ( !fbSubLocation.toUpperCase().endsWith("KD")) {
                        vCase = "case1";
                        cLib.debug("############################ fbSubLocation.endsWith('KD') 아닐 경우 ");
                    }
                }
                // if ( !fbSubLocation.toUpperCase().endsWith("KD")){
                //     vCase = "case1";
                //     cLib.debug("############################ fbSubLocation.endsWith('KD') 아닐 경우 ");
                // }
                // if(paramName == "1"){
                //     vCase = "case2";
                // }else if(paramName == "2"){
                //     if ( fbSubLocation.toUpperCase().endsWith("KD")){
                //         vCase = "case2";
                //     }else{
                //        vCase = "case1";
                //     }
                // }

            }else{
                let caseArr = ["ALL","IOT","MKD"];
                let bArr = (category || "")
                        .split(',')
                        .map(v => v.trim())
                        .filter(v => v);

                // category == "ALL" || category == "IOT" || category == "MKD")
                let col01 = caseArr.some(v => bArr.includes(v)) ? true : false;

                if( col01 && (itemClassCategory != vendorProdMap) ){    // (category == "ALL" || category == "IOT" || category == "MKD") && (itemClassCategory != vendorProdMap))
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
                return { "Code" : 1, "Msg" : "Create BOD 실행중입니다"};
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
                measure.push('Measure.[Code Map LCM_Create BOD_Target Flag]  = true;'); // 3. 선택한 row 들 intersection에 Flag 처리

                cLib.updateMeasure(dimension, measure);

                // 3. 선택한 row 들 intersection에 Flag 처리
                // cLib.updateMeasure(dimension, ['Measure.[Code Map LCM_Create BOD_Target Flag]  = true;']);

            }

            fn_py_createBOD(parsedParams);   // Python 호출 (PY_UI_CodeMapLCMCreateBOD)

            // PY 종료 후 Flag 원복 - createBOD 실행 종료
            cLib.updateMeasure(["&CWVUI"], ['Measure.[VersionInfo_RunningFlag_LCMProductCopyCreateBOD]  = false;']);
            cLib.updateMeasure(["&CWVUI"], ['Measure.[Code Map LCM_Create BOD_Target Flag]  = null;']);

            cLib.programEnd();

            //  정상 저장 후 리턴 값?? Warn 종류는 저장은 되고, 화면으로 메세지 리턴해줘야 함
            return { "Code" : 0, "Msg" : "", "Rows" : "" };  // 오류 dataset Return

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
     * 저장 전 Validation Check 2026.04.16 생성
     *
     * @param parsedParams
     * @returns {{errCnt: number, Rows: {rowindex: *, rowvalid: *|null, rowmsg: *|null}[]}|{Code: number, Msg: *}}
     */
    var fn_validation = function(parsedParams){
        const cLib = fn_cLib(programName + "." + arguments.callee.name);
        cLib.setLogLevel("Debug");

        try {
            let box = {};
            let errCnt = 0;     // 오류건수

            for ( var i=0; i<parsedParams.fbGridRows.length; i++){

                let row = parsedParams.fbGridRows[i];

                rowstatus = row["rowstatus"];
                rowindex = row["rowindex"];
                row["rowmsg"] = null;

                let gk = row.rowindex;
                if ( !box[gk] ) box[gk] = {rowindex: gk, rowvalid:[], rowmsg:[]};

                let dimension = [];
                dimension.push(cUtil.fn_qDimVersionName(parsedParams));
                dimension.push(cUtil.fn_qDim(row, "[Location].[Location]"));
                dimension.push(cUtil.fn_qDim(row, "[Sub Location].[Sub Location]"));
                dimension.push(cUtil.fn_qDim(row, "[Item].[Item]"));        // PO Item(To Item) > Item.Item
                dimension.push(cUtil.fn_qDim(row, "[To Item].[To Item]"));

                // dimension
                let fbLocation = row["[Location].[Location]"];
                let fbSubLocation = row["[Sub Location].[Sub Location]"];
                let fbPoItem = row["[Item].[Item]"];
                let fbProdItem = row["[To Item].[To Item]"];

                // measure
                let fbValidFlag = row["Measure.[Code Map LCM_Valid Flag]"];

                // 기존 data 중복여부에 대한 체크
                if( rowstatus == "C") {
                    // 중복체크
                    if ( cLib.existMeasure(dimension,["Measure.[Code Map LCM_Valid Flag]","Measure.[Code Map LCM_Map Status]"],"") ) {
                        errCnt++;
                        box[gk].rowvalid.push("Error");
                        box[gk].rowmsg.push("The Item had duplicated");
                    }
                }

                // 필수 입력값 체크
                if( rowstatus == "C" || rowstatus == "U") {

                    if( fbLocation === null || fbLocation === undefined || fbLocation === "" ){
                        errCnt++;
                        box[gk].rowvalid.push("Error");
                        box[gk].rowmsg.push("From Site 필수 입력 값이 없습니다.");
                    }

                    if( fbSubLocation === null || fbSubLocation === undefined || fbSubLocation === "" ){
                        errCnt++;
                        box[gk].rowvalid.push("Error");
                        box[gk].rowmsg.push("To Site 필수 입력 값이 없습니다.");
                    }

                    if( fbPoItem === null || fbPoItem === undefined || fbPoItem === "" ){
                        errCnt++;
                        box[gk].rowvalid.push("Error");
                        box[gk].rowmsg.push("PO Item(To Item) 필수 입력 값이 없습니다.");
                    }

                    if( fbProdItem === null || fbProdItem === undefined || fbProdItem === "" ){
                        errCnt++;
                        box[gk].rowvalid.push("Error");
                        box[gk].rowmsg.push("Prod Item(From Item) 필수 입력 값이 없습니다.");
                    }

                    if( fbValidFlag === null || fbValidFlag === undefined || fbValidFlag === "" ){
                        errCnt++;
                        box[gk].rowvalid.push("Error");
                        box[gk].rowmsg.push("Valid 필수 입력 값이 없습니다.");
                    }
                }

            } // end for

            let result = Object.values(box).map(r => ({
                rowindex : r.rowindex,
                rowvalid : r.rowvalid.length ? r.rowvalid.join("^") : null,
                rowmsg   : r.rowmsg.length ? r.rowmsg.join("^") : null
            }));

            return { errCnt, "Rows": result};

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

            //--------------------------------------------------------------------------------------------------------//
            // validation Check 로직 수행 리턴 값 (2026.04.16)
            //--------------------------------------------------------------------------------------------------------//
            let resutlValid = fn_validation(parsedParams);
            cLib.debug("#### resutlValid : "+JSON.stringify(resutlValid));

            if ( resutlValid.errCnt > 0){
                return { "Code" : 1, "Msg" : "valid", "ErrorCount":resutlValid.errCnt, "Rows" : resutlValid.Rows};  // return { "Code" : 1, "Msg" : resutlValid.Msg, "Rows" : resutlValid.Rows};   // 오류 리턴
            }
            //--------------------------------------------------------------------------------------------------------//

            for ( var i=0; i<parsedParams.fbGridRows.length; i++){

                let row = parsedParams.fbGridRows[i];
                let rowstatus = row["rowstatus"];
                row["rowmsg"] = null;
                cLib.debug("rowstatus :: "+rowstatus);

                let dimension = [];
                dimension.push(cUtil.fn_qDimVersionName(parsedParams));
                dimension.push(cUtil.fn_qDim(row, "[Location].[Location]"));
                dimension.push(cUtil.fn_qDim(row, "[Sub Location].[Sub Location]"));
                dimension.push(cUtil.fn_qDim(row, "[Item].[Item]"));        // PO Item(To Item) > Item.Item
                dimension.push(cUtil.fn_qDim(row, "[To Item].[To Item]"));  // Prod Item(From Item) > To Item.To Item - 2026.03.16 Measure -> grain 으로 변경 (이상엽p요청)

                let deleteWhere = [];
                deleteWhere.push(cUtil.fn_qDimVersionName(parsedParams));
                // deleteWhere.push(cUtil.fn_qDim(row, "[Location].[LocationOld]"));          // Location old
                deleteWhere.push(cUtil.fn_qDim(null, "[Location].[Location]", row["[Location].[LocationOld]"]));          // Location old
                deleteWhere.push(cUtil.fn_qDim(row, "[Sub Location].[Sub Location]"));
                deleteWhere.push(cUtil.fn_qDim(row, "[Item].[Item]"));
                // deleteWhere.push(cUtil.fn_qDim(row, "[To Item].[To ItemOld]"));            // To Item old
                deleteWhere.push(cUtil.fn_qDim(null, "[To Item].[To Item]", row["[To Item].[To ItemOld]"]));            // To Item old

                let measure = [];
                measure.push(cUtil.fn_qMeaStr(row, "Measure.[Code Map LCM_Valid Flag]"));
                measure.push(cUtil.fn_qMeaUpdateUserName("Measure.[Code Map LCM_Updated By]"));
                measure.push(cUtil.fn_qMeaUpdateTime("Measure.[Code Map LCM_Update Time]"));

                let measureCreate = [];
                // 입력 key값 바탕으로 Code Map LCM_Map Status = If {[Location].[Location] = "-" OR [To Item].[To Item]  = "-"} Then "REQ" ELSE "CON" (기존 fn_confrim 대체)
                // 2026.04.16 변경 이상엽p요청
                if( row["[Location].[Location]"] == "-" || row["[To Item].[To Item]"] == "-" ){
                    measureCreate.push(cUtil.fn_qMeaStr(null, "Measure.[Code Map LCM_Map Status]", "REQ"));
                }else{
                    measureCreate.push(cUtil.fn_qMeaStr(null, "Measure.[Code Map LCM_Map Status]", "CON"));
                }
                // measureCreate.push(cUtil.fn_qMeaStr(row, "Measure.[Code Map LCM_Map Status]")); // UI 받아서 처리 , 2026.04.07 이상엽p요청

                // 기존 data 중복여부에 대한 체크
                if( rowstatus == "C") {

                    // 중복체크
                    if ( !cLib.existMeasure(dimension
                                                ,["Measure.[Code Map LCM_Valid Flag]", "Measure.[Code Map LCM_Map Status]","Measure.[Code Map LCM_Create BOD_Target Flag]"]
                                                , "") ) {
                        // Main MG 생성
                        // cLib.createMeasure(dimension, ['Measure.[Code Map LCM_Map Status] = "CON";']);  // COM -> CON 변경 2026.04.02 이상엽p요청
                        cLib.createMeasure(dimension, measureCreate);

                        measure.push(cUtil.fn_qMeaUpdateUserName('Measure.[Code Map LCM_Created By]'));
                        measure.push(cUtil.fn_qMeaUpdateTime('Measure.[Code Map LCM_Creation Time]'));
                        cLib.updateMeasure(dimension, measure);

                    // }else{
                    //     // 중복 일 경우 리턴 메세지
                    //     return { "Code" : 1, "Msg" : "The Item had duplicated", "Rows" : "" };
                    }

                } else if( rowstatus == "U") {
                    // UI 에서 key 값을 변경 할 수 있음.
                    // Key 값이 변경이 없을 경우에만 update
                    if( (row["[Location].[Location]"] == row["[Location].[LocationOld]"]) && (row["[To Item].[To Item]"] == row["[To Item].[To ItemOld]"]) ){
                        cLib.updateMeasure(dimension, measure);

                    // Key 값 변경이 있을 경우 삭제 후 생성
                    }else{
                        cLib.deleteMeasure(deleteWhere, "Code Map LCM");

                        cLib.createMeasure(dimension, measureCreate);

                    }
                }

                // fn_itemSiteAsnSet(row);  // PY 로 변경 2026.04.16

            } // end for

            fn_py_itemSiteAsnSet(parsedParams);

            cLib.programEnd();

            return { "Code" : 0, "Msg" : "", "Rows" : "" };

        } catch ( e ) {
            cLib.error(e.message);
            return { "Code" : -1, "Msg" : e.message };
        }
    };

    /**
     * LCM BOD Product Copy 화면에서 데이터셋 변경 후 저장시 Item Site Asn을 Create/Update
     * PY_UI_LCMProdCopy_ItemSiteAsnSet 호출
     * @param {*} parsedParams
     * @returns
     */
    var fn_py_itemSiteAsnSet = function(parsedParams){
        const cLib = fn_cLib(programName + "." + arguments.callee.name);
        cLib.setLogLevel("Debug");

        try {
            cLib.debug(" fn_py_createBOD 실행 :: parsedParams :: "+JSON.stringify(parsedParams));

            /* PY 호출 (PY_UI_LCMProdCopy_ItemSiteAsnSet) */
            var execQuery = 'EXEC plugin instance [PY_UI_LCMProdCopy_ItemSiteAsnSet] ' +
                            'for measures {[Item Site Asn_Cur Status]} ' +
                            'using scope ( ' +
                                // '&CWVUI '+ ' * ' +
                                cUtil.fn_getFilterVersion(parsedParams) + ' * ' +      // [Version].[Version Name].[CWV_MP]
                                ' )'+
                            'using arguments {(ExecutionMode, "MediumWeight"), (MaxSliceTableCells, 200000000), (MaxConcurrency, 1), ([Param.o9_sys_log_level], "DEBUG")}; ';

            cLib.debug("execQuery: " + JSON.stringify(execQuery));
            cLib.executeQuery("fn_py_itemSiteAsnSet : PY_UI_LCMProdCopy_ItemSiteAsnSet Run", execQuery);

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
    2026.03.27 : fn_itemSiteAsnSet 생성, fn_save 시 Item Site Asn (MG) 데이터 생성 로직 추가 (이상엽p요청)
    2026.03.31 : fn_itemSiteAsnSet 수정, valid =N 은 update 만 처리
    2026.04.02 : Code Map LCM_Map Status // COM -> CON 변경 2026.04.02 이상엽p요청
    2026.04.02 : fn_cb_prodItem_value : case1 일때, code 값 상관없이 입력 Item.Item(Po Item) 값을 그대로 추가 넘김 2026.04.02 이상엽 프로 요청
    2026.04.07 : fn_itemSiteAsnSet : 수정, fn_save 수정
    2026.04.16 : -fn_cb_poItem 로직 변경, PO Item key in 으로 값 찾기(이상엽p요청)
                 -fn_cb_prodItem 로직변경
                 -fn_save 변경 : key 값이 변경될수 있는 부분 수정, key 변경시 delete 후 create, key 변경 없을 경우 update
                 -fn_confirm 삭제
                 -fn_py_itemSiteAsnSet 추가 (fn_itemSiteAsnSet(삭제) -> PY 호출로 변경)
                 -fn_cb_prodItem_value 로직 변경
*/
/*--------------------------------------------------------------------------------------------------*/