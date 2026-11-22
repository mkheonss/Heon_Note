define('o9.NSCM.JSLCMProductionConst', ['o9/data/query', 'o9/data/cellset', 'o9.NSCM.commonLib'], function(){

    const programName = "o9.NSCM.JSLCMProductionConst";
    const Horizon    = "&MPHorizon";
    const MFC_LCM    = "MFC_L";
    const SRC_LCM    = "SRC_L";

    var fn_locationCombo = function(o9Params){
        try {            
            const commonLib = require('o9.NSCM.commonLib');
            const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);

            vdCommon.setLogLevel("Debug");
            var parsedParams = JSON.parse(o9Params);
            // Location : LCM Namedset 확인 필요 2024.11.27 > BOD List LCM 의 Location
            var result = vdCommon.selectList(["&CWVUI", "&MFStageLCMLocation", "[Sub Location].[Sub Location]", "[Trans Mode].[Trans Mode]"],
                                             ["Measure.[BOD List_BOD Valid]",
                                                "Measure.[BOD List_Eff Enddate]",
                                                "Measure.[BOD List_Eff Startdate]"],
                                             'where {Measure.[BOD List_BOD Valid] == "Y", coalesce(Measure.[BOD List_Eff Startdate],DATEADD(Now(),-1,"Day")) < now(), coalesce(Measure.[BOD List_Eff Enddate],DATEADD(Now(),1,"Day")) > now()}',
                                             "",
                                             "");
            vdCommon.printCsData(result, 3);

            var comboList = vdCommon.fn_makeCombo(result, {DimName : "Location", DimAttbName : "Location", Sort : "DisplayName", existAll : false, isDisplayNameWithCode : true});
            vdCommon.debug("ComboData : " + JSON.stringify(comboList));

            vdCommon.programEnd();

            return comboList;
        } catch ( e ) {
            RuleOutputToUI = { Status : 'Error', Message : "Js Logic Error : " + e.message };
            return;
        }
    };

    var fn_subLocationCombo = function(o9Params){
        try {
            const commonLib = require('o9.NSCM.commonLib');
            const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
            vdCommon.setLogLevel("Debug");
            vdCommon.printParams(o9Params);
            // 파라메타 가져오기
            let parsedParams = JSON.parse(o9Params);
            let fbLocation = parsedParams.fbLocation;
            // Sub Location : LCM Namedset 확인 필요 2024.11.27 > BOD List LCM 의 SubLocation
            var result = vdCommon.selectList(["&CWVUI",
                                    "[Location].[Location].[" + fbLocation + "]",
                                    "&MFStageSETSubLocation.unionwith(&MFStageKDSubLocation)",
                                    "[Trans Mode].[Trans Mode]"],
                                    ["Measure.[BOD List_BOD Valid]",
                                    "Measure.[BOD List_Eff Enddate]",
                                    "Measure.[BOD List_Eff Startdate]"],
                                    'where {Measure.[BOD List_BOD Valid] == "Y", coalesce(Measure.[BOD List_Eff Startdate],DATEADD(Now(),-1,"Day")) < now(), coalesce(Measure.[BOD List_Eff Enddate],DATEADD(Now(),1,"Day")) > now()}',
                                    "",
                                    "");
            vdCommon.printCsData(result, 3);

            var comboList = vdCommon.fn_makeCombo(result, {DimName : "Sub Location", DimAttbName : "Sub Location", Sort : "DisplayName", existAll : true, isDisplayNameWithCode : true});
            vdCommon.debug("ComboData : " + JSON.stringify(comboList));

            vdCommon.programEnd();

            return comboList;
        } catch ( e ) {
            RuleOutputToUI = { Status : 'Error', Message : "Js Logic Error : " + e.message };
            return;
        }
    };

    var fn_productGroupCombo = function(o9Params){
        try {
            const commonLib = require('o9.NSCM.commonLib');
            const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
            vdCommon.setLogLevel("Debug");
            vdCommon.printParams(o9Params);
            // 파라미터 가져오기
            var parsedParams = JSON.parse(o9Params);

            var result = vdCommon.selectList(["&LCMItem.relatedmembers([Product Group])"],
                                             [],
                                             "",
                                             "",
                                             "");
            vdCommon.printCsData(result, 3);

            var comboList = vdCommon.fn_makeCombo(result, {DimName : "Item", DimAttbName : "Product Group", Sort : "DisplayName", existAll : false, isDisplayNameWithCode : false});
            vdCommon.debug("ComboData : " + JSON.stringify(comboList));

            vdCommon.programEnd();

            return comboList;
        } catch ( e ) {
            RuleOutputToUI = { Status : 'Error', Message : "Js Logic Error : " + e.message };
            return;
        }
    };
    
    var fn_definitionCombo = function(o9Params){
        try {
            const commonLib = require('o9.NSCM.commonLib');
            const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
            const vdUtil = new commonLib.VdUtil();
            vdCommon.setLogLevel("Debug");

            vdCommon.printParams(o9Params);

            // 파라미터 가져오기
            var parsedParams = JSON.parse(o9Params);
            var fbProductGroup = parsedParams.fbProductGroup;
            var result = vdCommon.selectList(["&LCMItem.relatedmembers([Product Group])" + vdUtil.fn_filterStr(fbProductGroup),
                                                "&LCMItem.relatedmembers([Definition])"],
                                             [],
                                             "",
                                             "",
                                             "");
            vdCommon.printCsData(result, 3);

            var comboList = vdCommon.fn_makeCombo(result, {DimName : "Item", DimAttbName : "Definition", Sort : "DisplayName", existAll : true});
            vdCommon.debug("ComboData : " + JSON.stringify(comboList));

            vdCommon.programEnd();

            return comboList;
        } catch ( e ) {
            RuleOutputToUI = { Status : 'Error', Message : "Js Logic Error : " + e.message };
            return;
        }
    };

    var fn_projectCombo = function(o9Params){
        try {
            const commonLib = require('o9.NSCM.commonLib');
            const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
            const vdUtil = new commonLib.VdUtil();
            vdCommon.setLogLevel("Debug");
            vdCommon.printParams(o9Params);

            // 파라미터 가져오기
            var parsedParams = JSON.parse(o9Params);
            var fbProductGroup = parsedParams.fbProductGroup;
            var fbDefinition = parsedParams.fbDefinition;

            var result = vdCommon.selectList(["&LCMItem.relatedmembers([Product Group])" + vdUtil.fn_filterStr(fbProductGroup),
                                              "&LCMItem.relatedmembers([Definition])" + vdUtil.fn_filterStr(fbDefinition),
                                              "&LCMItem.relatedmembers([Project])"],
                                             [],
                                             "",
                                             "",
                                             "");
            vdCommon.printCsData(result, 3);

            var comboList = vdCommon.fn_makeCombo(result, {DimName : "Item", DimAttbName : "Project", Sort : "DisplayName", existAll : true});
            vdCommon.debug("ComboData : " + JSON.stringify(comboList));

            vdCommon.programEnd();

            return comboList;
        } catch ( e ) {
            RuleOutputToUI = { Status : 'Error', Message : "Js Logic Error : " + e.message };
            return;
        }
    };

    var fn_mktNameCombo = function(o9Params){
        try {
            const commonLib = require('o9.NSCM.commonLib');
            const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
            const vdUtil = new commonLib.VdUtil();
            vdCommon.setLogLevel("Debug");

            vdCommon.printParams(o9Params);

            // 파라미터 가져오기
            var parsedParams = JSON.parse(o9Params);
            var fbProductGroup = parsedParams.fbProductGroup;
            var fbDefinition = parsedParams.fbDefinition;
            let fbProject = parsedParams.fbProject;

            var result = vdCommon.selectList(["&LCMItem.relatedmembers([Product Group])" + vdUtil.fn_filterStr(fbProductGroup),
                                                "&LCMItem.relatedmembers([Definition])" + vdUtil.fn_filterStr(fbDefinition),
                                                "&LCMItem.relatedmembers([Project])" + vdUtil.fn_filterStr(fbProject),
                                                "&LCMItem.relatedmembers([Marketing Name])"],
                                            [],
                                            "",
                                            "",
                                            "");
            vdCommon.printCsData(result, 3);

            var comboList = vdCommon.fn_makeCombo(result, {DimName : "Item", DimAttbName : "Marketing Name", Sort : "DisplayName", existAll : true});
            vdCommon.debug("ComboData : " + JSON.stringify(comboList));

            vdCommon.programEnd();

            return comboList;
        } catch ( e ) {
            RuleOutputToUI = { Status : 'Error', Message : "Js Logic Error : " + e.message };
            return;
        }
    };

    var fn_inchCombo = function(o9Params){
        try {
            const commonLib = require('o9.NSCM.commonLib');
            const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
            const vdUtil = new commonLib.VdUtil();
            vdCommon.setLogLevel("Debug");

            vdCommon.printParams(o9Params);

            // 파라미터 가져오기
            var parsedParams = JSON.parse(o9Params);
            var fbProductGroup = parsedParams.fbProductGroup;
            var fbDefinition = parsedParams.fbDefinition;
            let fbProject = parsedParams.fbProject;
            let fbMKTName = parsedParams.fbMKTName;

            var result = vdCommon.selectList(["&LCMItem.relatedmembers([Product Group])" + vdUtil.fn_filterStr(fbProductGroup),
                                                "&LCMItem.relatedmembers([Definition])" + vdUtil.fn_filterStr(fbDefinition),
                                                "&LCMItem.relatedmembers([Project])" + vdUtil.fn_filterStr(fbProject),
                                                "&LCMItem.relatedmembers([Marketing Name])" + vdUtil.fn_filterStr(fbMKTName),
                                                "&LCMItem.relatedmembers([Inch])"],
                                            [],
                                            "",
                                            "",
                                            "");
            vdCommon.printCsData(result, 3);

            var comboList = vdCommon.fn_makeCombo(result, {DimName : "Item", DimAttbName : "Inch", Sort : "DisplayName", existAll : true});
            vdCommon.debug("ComboData : " + JSON.stringify(comboList));

            vdCommon.programEnd();

            return comboList;
        } catch ( e ) {
            RuleOutputToUI = { Status : 'Error', Message : "Js Logic Error : " + e.message };
            return;
        }
    };

    var fn_yearCombo = function(o9Params){
        try {
            const commonLib = require('o9.NSCM.commonLib');
            const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
            const vdUtil = new commonLib.VdUtil();
            vdCommon.setLogLevel("Debug");

            vdCommon.printParams(o9Params);

            // 파라미터 가져오기
            var parsedParams = JSON.parse(o9Params);
            var fbProductGroup = parsedParams.fbProductGroup;
            var fbDefinition = parsedParams.fbDefinition;
            let fbProject = parsedParams.fbProject;
            let fbMKTName = parsedParams.fbMKTName;
            var fbInch = parsedParams.fbInch;

            var result = vdCommon.selectList(["&LCMItem.relatedmembers([Product Group])" + vdUtil.fn_filterStr(fbProductGroup),
                                                "&LCMItem.relatedmembers([Definition])" + vdUtil.fn_filterStr(fbDefinition),
                                                "&LCMItem.relatedmembers([Project])" + vdUtil.fn_filterStr(fbProject),
                                                "&LCMItem.relatedmembers([Marketing Name])" + vdUtil.fn_filterStr(fbMKTName),
                                                "&LCMItem.relatedmembers([Inch])" + vdUtil.fn_filterStr(fbInch),
                                                "&LCMItem.relatedmembers([Year])"],
                                            [],
                                            "",
                                            "",
                                            "");
            vdCommon.printCsData(result, 3);

            var comboList = vdCommon.fn_makeCombo(result, {DimName : "Item", DimAttbName : "Year", Sort : "DisplayName", existAll : true});
            vdCommon.debug("ComboData : " + JSON.stringify(comboList));

            vdCommon.programEnd();

            return comboList;
        } catch ( e ) {
            RuleOutputToUI = { Status : 'Error', Message : "Js Logic Error : " + e.message };
            return;
        }
    };

    var fn_itemCombo = function(o9Params){
        try {
            const commonLib = require('o9.NSCM.commonLib');
            const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
            const vdUtil = new commonLib.VdUtil();
            vdCommon.setLogLevel("Debug");

            vdCommon.printParams(o9Params);

            // 파라미터 가져오기
            var parsedParams = JSON.parse(o9Params);
            var fbLocation = parsedParams.fbLocation;
            var fbSubLocation = parsedParams.fbSubLocation;
            var fbProductGroup = parsedParams.fbProductGroup;
            var fbDefinition = parsedParams.fbDefinition;
            var fbProject = parsedParams.fbProject;
            var fbMKTName = parsedParams.fbMKTName;
            var fbInch = parsedParams.fbInch;
            var fbYear = parsedParams.fbYear;

            var dims = [];
            dims.push("&CWVUI");
            dims.push("Location.[Location].[" + fbLocation + "]");

            // All 을 제외한 Multi 조건으로 Filter
            if( fbSubLocation != "All") dims.push("[Sub Location].[Sub Location]" + vdUtil.fn_filterStr(fbSubLocation));
            if( fbProductGroup != "All") dims.push("Item.[Product Group]" + vdUtil.fn_filterStr(fbProductGroup));
            if( fbDefinition != "All") dims.push("Item.[Definition]" + vdUtil.fn_filterStr(fbDefinition));
            if( fbProject != "All") dims.push("Item.[Project]" + vdUtil.fn_filterStr(fbProject));
            if( fbMKTName != "All") dims.push("Item.[Marketing Name]" + vdUtil.fn_filterStr(fbMKTName));
            if( fbInch != "All") dims.push("Item.[Inch]" + vdUtil.fn_filterStr(fbInch));
            if( fbYear != "All") dims.push("Item.[Year]" + vdUtil.fn_filterStr(fbYear));

            // dims.push("Item.[Item]");
            dims.push("&LCMItem");
            vdCommon.debug(" dims : "+dims);

            var result = vdCommon.selectList( dims,
                                             ["Measure.[BOD Item_BOD Frozen]",
                                                "Measure.[BOD Item_BOD LT]",
                                                "Measure.[BOD Item_BOD LT_Inherit]",
                                                "Measure.[BOD Item_Cur Status]",
                                                "Measure.[BOD Item_Eff Enddate]",
                                                "Measure.[BOD Item_Eff Startdate]",
                                                "Measure.[BOD Item_Lock Flag]",
                                                "Measure.[BOD Item_Min Lot Qty]",
                                                "Measure.[BOD Item_Multi Lot Qty]",
                                                "Measure.[BOD Item_Need Check]",
                                                "Measure.[BOD Item_Period SET Detail]",
                                                "Measure.[BOD Item_Period1]",
                                                "Measure.[BOD Item_Period2]",
                                                "Measure.[BOD Item_Period3]",
                                                "Measure.[BOD Item_Priority]",
                                                "Measure.[BOD Item_Priority_Inherit]",
                                                "Measure.[BOD Item_Prod Item]",
                                                "Measure.[BOD Item_Shipment LT]",
                                                "Measure.[BOD Item_Shipment LT_Inherit]",
                                                "Measure.[BOD Item_Time Phased BOD]",
                                                "Measure.[BOD Item_Time Phased Prty]",
                                                "Measure.[BOD Item_Time Phased Shipment]",
                                                "Measure.[BOD Item_To Item]"],
                                             'where {coalesce(Measure.[BOD Item_Eff Startdate],DATEADD(Now(),-1,"Day")) < now(), coalesce(Measure.[BOD Item_Eff Enddate],DATEADD(Now(),1,"Day")) > now()}',
                                             "",
                                             "limit 1000");
            vdCommon.printCsData(result, 3);

            var comboList = vdCommon.fn_makeCombo(result, {DimName : "Item", DimAttbName : "Item", Sort : "DisplayName", existAll : true});
            vdCommon.debug("ComboData : " + JSON.stringify(comboList));

            vdCommon.programEnd();

            return comboList;
        } catch ( e ) {
            RuleOutputToUI = { Status : 'Error', Message : "Js Logic Error : " + e.message };
            return;
        }
    };
    
    /**
     * Constraint Group Add 
     * Group ID, Sequence 생성
     * @param {*} o9Params 
     */
    var fn_Add = function(o9Params){
        try {
            const commonLib = require('o9.NSCM.commonLib');
            const cellsetModule = require('o9/data/cellset');
            const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
            const vdUtil = new commonLib.VdUtil();

            vdCommon.setLogLevel("Debug");
            vdCommon.programStart();
            vdCommon.printParams(o9Params);

            // 파라미터 가져오기
            let parsedParams = JSON.parse(o9Params);
            let fbVersion = parsedParams.fbVersion;
            let fbLocation = parsedParams.fbLocation;
            let fbSubLocation_arry = parsedParams.fbSubLocation;
            let fbSubLocation = parsedParams.fbSubLocation ? parsedParams.fbSubLocation.toString().replace(/,/g, "^") : parsedParams.fbSubLocation;
            let fbProductGroup = parsedParams.fbProductGroup ? parsedParams.fbProductGroup.toString().replace(/,/g, "^") : parsedParams.fbProductGroup;
            let fbDefinition = parsedParams.fbDefinition ? parsedParams.fbDefinition.toString().replace(/,/g, "^") : parsedParams.fbDefinition;
            let fbProject = parsedParams.fbProject ? parsedParams.fbProject.toString().replace(/,/g, "^") : parsedParams.fbProject;
            let fbMKTName = parsedParams.fbMKTName ? parsedParams.fbMKTName.toString().replace(/,/g, "^") : parsedParams.fbMKTName;
            let fbInch = parsedParams.fbInch ? parsedParams.fbInch.toString().replace(/,/g, "^") : parsedParams.fbInch;
            let fbYear = parsedParams.fbYear ? parsedParams.fbYear.toString().replace(/,/g, "^") : parsedParams.fbYear;
            // let fbItem = parsedParams.fbItem ? parsedParams.fbItem.toString().replace(/,/g, "^") : parsedParams.fbItem;

            // , 를 ^ 로 변환, All 제외한 대문자 변환
            let fbItem = parsedParams.fbItem ? parsedParams.fbItem.toString().split(",").map(item => (item === "All" ? item : item.toUpperCase())).join("^") : parsedParams.fbItem;
            vdCommon.debug("############# fbItem : "+fbItem);

            // let fbRefTime = parsedParams.fbRefTime;
            //==========================================================================================================//
            // Location ( To Site ) Name 가져오기
            //==========================================================================================================//
            let fbLocationName = vdCommon.selectResult("[Location].[Location].["+fbLocation+"].DisplayName");
            
            //==========================================================================================================//
            // Sub Location ( To Site ) Name 가져오기
            //==========================================================================================================//
            // Sub Location = 'All' or All,P54A,P54B 이면 All 빼고
            let fbSubLocationName = "";
            let fbGroupType = "";   // Group Type : MFC_S (SET), MFC_L (LCM)
            if( fbSubLocation_arry == "All" || fbSubLocation_arry == "-"){
                fbGroupType    = MFC_LCM;   // MFC_L
                fbSubLocationName = fbSubLocation_arry;
            }else{
                fbGroupType    = SRC_LCM;   // SRC_L

                // Sub Location ( To Site ) Name 가져오기
                let resultSubLocation = vdCommon.selectList(["[Sub Location].[Sub Location]" + vdUtil.fn_filterStr(fbSubLocation_arry)], [], "", "", "");
                let resultSubLocationCnt = resultSubLocation.cs.rowCount;
                let validHashMap2 = new Map();
                for (let i = 0; i < resultSubLocationCnt; i++) {
                    const name2 = resultSubLocation.cs.row(i).cell(resultSubLocation.cs.memberColumnIndex("Sub Location", "Sub Location")).DisplayName;
                    const formatName2 = (i === resultSubLocationCnt-1) ? name2 : name2 + "^";
                    validHashMap2.set(name2, formatName2);
                }
                
                for( let formatName2 of validHashMap2.values() ){
                    fbSubLocationName += formatName2;
                }
            }

            fbSubLocation = fbSubLocation ? fbSubLocation.toString().replace(/,/g, "^") : fbSubLocation;
            let vGroupIdPreFix = fbGroupType+"_";   // SET : MFC_S_00000 , LCM : MFC_L_00000 
            let fullPadLenth = 5;   // Group ID 만들때 MFC숫자 (숫자에 들어갈 길이)

            // Measure Group 정의
            let measures =  ['Measure.[Const Grp_Build Ahead]',
                            'Measure.[Const Grp_Definition]', 
                            'Measure.[Const Grp_Desc]',
                            'Measure.[Const Grp_Enddate]', 
                            'Measure.[Const Grp_From Site]',
                            'Measure.[Const Grp_Inch]',
                            'Measure.[Const Grp_Item]',
                            'Measure.[Const Grp_Mkt Name]', 
                            'Measure.[Const Grp_Need Check]', 
                            'Measure.[Const Grp_Prod Qty]', 
                            'Measure.[Const Grp_Product Group]',
                            'Measure.[Const Grp_Project]', 
                            'Measure.[Const Grp_Reason]', 
                            'Measure.[Const Grp_Refer Time]',
                            'Measure.[Const Grp_Startdate]', 
                            'Measure.[Const Grp_To Site]', 
                            'Measure.[Const Grp_Update Time]', 
                            'Measure.[Const Grp_Updated By]',
                            'Measure.[Const Grp_Year]'];

            // Measure Group 중복이 있는지 체크
            let measureFilter =    'Measure.[Const Grp_From Site] == "'+fbLocation+'"'
                                +' && Measure.[Const Grp_To Site] == "'+fbSubLocation+'"'
                                // +' && Measure.[Const Grp_To Site] in {'+fbSubLocation_arr+'}'           // Multi
                                +' && Measure.[Const Grp_Product Group] == "'+fbProductGroup+'"'
                                +' && Measure.[Const Grp_Definition] == "'+fbDefinition+'"'
                                +' && Measure.[Const Grp_Project] == "'+fbProject+'"'
                                +' && Measure.[Const Grp_Mkt Name] == "'+fbMKTName+'"'
                                +' && Measure.[Const Grp_Inch] == "'+fbInch+'"'
                                +' && Measure.[Const Grp_Year] == "'+fbYear+'"'
                                +' && Measure.[Const Grp_Item] == "'+fbItem+'"'
                                ;

            // Measure Group 중복이 없을 경우, Group ID max 값을 가져와 'MFC' max+1, Sequence = 1
            let where = 'where {'+measureFilter+'}' ;
            if ( !vdCommon.existMeasure(["&CWVUI","[Sequence].[Sequence]","[Group].[Group ID]"], measures, where) ) {
                // vdCommon.debug("-----> Measure Group 중복이 없을 경우 ");
                let newGroupID = "";
                let newSequence = 1;
                
                let result = vdCommon.selectList(['&CWVUI','[Sequence].[Sequence]','[Group].[Group ID].filter(#.Name startswith "'+vGroupIdPreFix+'")'],  ['Measure.[Const Grp_From Site]'], '', "orderby [Group].[Group ID].Name desc", '');
                
                // 해당 Group Type에 Measure 가 있는지 조회 : 없으면 초기값으로 세팅
                if ( result.cs.rowCount == 0 ){
                    newGroupID = vGroupIdPreFix + vdUtil.fn_lpad("1", fullPadLenth, "0");
                } else {
                    let rtnGroupID = result.cs.row(0).cell(result.cs.memberColumnIndex("Group", "Group ID")).Name;
                    // vdCommon.debug(" ######## rtnGroupID >> "+ rtnGroupID);
                    // vdCommon.debug(" ######## rtnGroupID split[1] >> "+ rtnGroupID.split("_")[1]);
                    // vdCommon.debug(" ######## rtnGroupID split pop >> "+ rtnGroupID.split("_").pop());
                    // 두번째 배열의 숫자 + 1 ( ex: MFC_00001 )
                    newGroupID = vGroupIdPreFix + vdUtil.fn_lpad((parseInt(rtnGroupID.split("_").pop()) + 1).toString(), fullPadLenth, "0");
                }

                let argParam = {};
                argParam.paramGroupId = newGroupID;
                argParam.paramSeqId = newSequence;
                argParam.paramVersion = fbVersion;
                argParam.paramGroupType = fbGroupType;
                argParam.paramLocationName = fbLocationName;
                argParam.paramSubLocationName = fbSubLocationName;

                fn_ExecMemberMeasure(o9Params, argParam);

            }else{
                // 중복인 경우
                // Measure Group 중복이 있을 경우, 해당 Group ID, seq + 1
                // Measure Group 에 해당하는 Member를 조회 ( Group ID,  Sequence)
                // 조회한 Group ID로 Sequence 의 Max 값 구하기 ( Sequence, 내림차순 정렬)
                let rtnMaxSequence = vdCommon.selectList(["&CWVUI","[Sequence].[Sequence]","[Group].[Group ID]"], [], "where {"+measureFilter+"}", "orderby [Sequence].[Sequence].Name desc", "");
                let getSeqId = parseInt(rtnMaxSequence.cs.row(0).cell(rtnMaxSequence.cs.memberColumnIndex("Sequence", "Sequence")).Name);

                // Group ID, Sequence 구하기 (Type String)
                let getGroupId = rtnMaxSequence.cs.row(0).cell(rtnMaxSequence.cs.memberColumnIndex("Group", "Group ID")).Name
                let makeSeq = getSeqId+1;

                let argParam = {};
                argParam.paramGroupId = getGroupId;
                argParam.paramSeqId = makeSeq;
                argParam.paramVersion = fbVersion;
                argParam.paramGroupType = fbGroupType;
                argParam.paramLocationName = fbLocationName;
                argParam.paramSubLocationName = fbSubLocationName;

                fn_ExecMemberMeasure(o9Params, argParam);
            }
            
            vdCommon.programEnd();
        } catch ( e ) {
            RuleOutputToUI = { Status : 'Error', Message : "Js Logic Error : " + e.message };
            return;
        }
    };

    // Member 체크 후 Member 생성, Measure Group 입력하는 함수
    var fn_ExecMemberMeasure = function(o9Params, params){
        try {
            const commonLib = require('o9.NSCM.commonLib');
            const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
            const vdUtil = new commonLib.VdUtil();        

            vdCommon.setLogLevel("Debug");
            vdCommon.programStart();
            vdCommon.printParams(o9Params);

            // 파라미터 가져오기
            let parsedParams = JSON.parse(o9Params);

            // let fbVersion = parsedParams.fbVersion;
            let fbLocation = parsedParams.fbLocation;
            let fbSubLocation = parsedParams.fbSubLocation ? parsedParams.fbSubLocation.toString().replace(/,/g, "^") : parsedParams.fbSubLocation;
            let fbProductGroup = parsedParams.fbProductGroup ? parsedParams.fbProductGroup.toString().replace(/,/g, "^") : parsedParams.fbProductGroup;
            let fbDefinition = parsedParams.fbDefinition ? parsedParams.fbDefinition.toString().replace(/,/g, "^") : parsedParams.fbDefinition;
            let fbProject = parsedParams.fbProject ? parsedParams.fbProject.toString().replace(/,/g, "^") : parsedParams.fbProject;
            let fbMKTName = parsedParams.fbMKTName ? parsedParams.fbMKTName.toString().replace(/,/g, "^") : parsedParams.fbMKTName;
            let fbInch = parsedParams.fbInch ? parsedParams.fbInch.toString().replace(/,/g, "^") : parsedParams.fbInch;
            let fbYear = parsedParams.fbYear ? parsedParams.fbYear.toString().replace(/,/g, "^") : parsedParams.fbYear;
            // let fbItem = parsedParams.fbItem ? parsedParams.fbItem.toString().replace(/,/g, "^") : parsedParams.fbItem;
            // , 를 ^ 로 변환, All 제외한 대문자 변환
            let fbItem = parsedParams.fbItem ? parsedParams.fbItem.toString().split(",").map(item => (item === "All" ? item : item.toUpperCase())).join("^") : parsedParams.fbItem;

            let fbRefTime = parsedParams.fbRefTime;

            // vdCommon.debug(" 함수 생성  호출 ");
            // vdCommon.debug("paramGroupId : "+params.paramGroupId + " | paramSeqId : "+ params.paramSeqId.toString() + " | paramVersion : "+ params.paramVersion);
            // member 체크 후 생성 (Group ID)
            if ( !vdCommon.existMember('[Group].[Group ID]', params.paramGroupId) ) {
                vdCommon.createDimension(['[Group].[Group ID]','[Group].[Group Name]','[Group].[Group Type]'], [params.paramGroupId, params.paramGroupId, params.paramGroupType]);
            }

            // member 체크 후 생성 (Sequence ID)
            if ( !vdCommon.existMember('[Sequence].[Sequence]', params.paramSeqId) ) {
                vdCommon.createMember('[Sequence].[Sequence]', params.paramSeqId);
            }

            // Product Group + Definition + Project + MKT Name + INch + Year + Item 의 조합
            // let vDesc = fbProductGroup +" " + fbDefinition + " " + fbProject + " " + fbMKTName + " " + fbInch + " " + fbYear  + " " + fbItem;
            let vDesc = "";
            if ( fbProductGroup !== "All" ) vDesc += fbProductGroup + " ";
            if ( fbDefinition !== "All" ) vDesc += fbDefinition + " ";
            if ( fbProject !== "All" ) vDesc += fbProject + " ";
            if ( fbMKTName !== "All" ) vDesc += fbMKTName + " ";
            if ( fbInch !== "All" ) vDesc += fbInch + " ";
            if ( fbYear !== "All" ) vDesc += fbYear + " ";
            if ( fbItem !== "All" ) vDesc += fbItem;
            // 마지막 공백 제거
            vDesc = vDesc.trim();

            let bWhere = 'where {Measure.[Const Grp_From Site] == "' + fbLocation + '", Measure.[Const Grp_To Site] == "' + fbSubLocation + '", Measure.[Const Grp_Product Group] == "' + fbProductGroup + '"}';
            let dimension = ["&CWVUI","[Sequence].[Sequence].[" + params.paramSeqId + "]", "[Group].[Group ID].[" + params.paramGroupId + "]"];
            if ( !vdCommon.existMeasure(dimension, ['Measure.[Const Grp_From Site]'], bWhere) ) {
                let measure = ['Measure.[Const Grp_From Site]       = "' + fbLocation + '";',
                            'Measure.[Const Grp_From Site Name]     = "' + params.paramLocationName + '";',
                            'Measure.[Const Grp_To Site]            = "' + fbSubLocation + '";',
                            'Measure.[Const Grp_To Site Name]       = "' + params.paramSubLocationName + '";',                                            
                            'Measure.[Const Grp_Product Group]      = "' + fbProductGroup + '";',
                            'Measure.[Const Grp_Definition]         = "' + fbDefinition + '";',
                            'Measure.[Const Grp_Project]            = "' + fbProject + '";',
                            'Measure.[Const Grp_Mkt Name]           = "' + fbMKTName + '";',
                            'Measure.[Const Grp_Inch]               = "' + fbInch + '";',
                            'Measure.[Const Grp_Year]               = "' + fbYear + '";',
                            'Measure.[Const Grp_Item]               = "' + fbItem + '";',
                            'Measure.[Const Grp_Desc]               = "' + vDesc + '";',
                            'Measure.[Const Grp_Refer Time]         = "' + fbRefTime + '";',
                            'Measure.[Const Grp_Enddate]            = null;',
                            'Measure.[Const Grp_Startdate]          = null;',
                            'Measure.[Const Grp_Need Check]         = null;',
                            'Measure.[Const Grp_Reason]             = null;',
                            'Measure.[Const Grp_Build Ahead]        = null;',
                            'Measure.[Const Grp_Prod Qty]           = 0;',
                            'Measure.[Const Grp_Update Time]        = dateadd(Now(),9,"hour");',
                            'Measure.[Const Grp_Updated By]         = CurrentUser().[User Name];'
                            ];
                vdCommon.createMeasure(dimension, ['Measure.[Const Grp_From Site]         = "' + fbLocation + '";']);
                vdCommon.updateMeasure(dimension,  measure);
            } else {
                RuleOutputToUI = { Status : 'Error', Message : "This Data has already been registered." };
                return;
            }

        } catch ( e ) {
            this.error(e.message);
            throw e;
        }
    };

    /**
     * fn_ValidationApply
     * UI 화면의 Apply - Validation Check  -- 테스트 중
     * 선택 Row 중 점검 필요 항목(Measure.[Const Grp_Need Check])이 null 이 아니면 오류메세지 리턴
     * @param {*} o9Params 
     */
    var fn_ValidationApply = function(o9Params){
        try {
            const commonLib = require('o9.NSCM.commonLib');
            const cellsetModule = require('o9/data/cellset');
            const vdCommon = new commonLib.VdCommon(programName);
            const VdUtil = new commonLib.VdUtil();   // 2024.08.14 add
        
            vdCommon.setLogLevel("Debug");
            vdCommon.debug("fn_ValidationApply=======>");
            vdCommon.setLogLevel("Debug");
            vdCommon.programStart();
            vdCommon.printParams(o9Params);
            // 파라미터 가져오기
            let parsedParams = JSON.parse(o9Params);

            // Tuple 테스트.. 
            let parseTuple = parsedParams.fbConstGrpTuple;
            let parseTupleSize = parsedParams.fbConstGrpTuple.length;
            let fbVersion = parsedParams.fbVersion;
            // vdCommon.debug("parseTuple size =======>"+ parseTuple.length);

            let tupleList = parsedParams.fbConstGrpTuple;
            let fbGroupID = "", fbSeq = "", sql = "", sqlResult = "", rtnsqlResult = "", rtnNeedCheck = "", rtnStartDate = "", rtnEndDate = "", rtnRefTime = "";
            let rtnProdQty = 0;
            let returnData = {};
            // 점검필요 항목에 data 존재 여부 체크
            for (let i=0; i < parseTupleSize; i++) {
                const group = tupleList[i];
                fbGroupID = group.Group_ID.Value;
                // fbVersion = group.version.Value;
                fbSeq     = group.Seq.Value;

                //  점검필요를 조회한다.
                let rtnMeasureValue = vdCommon.selectList(["&CWVUI","[Sequence].[Sequence].["+fbSeq+"]","[Group].[Group ID].["+fbGroupID+"]"]
                                                        , ["Measure.[Const Grp_From Site], Measure.[Const Grp_Startdate], Measure.[Const Grp_Enddate], Measure.[Const Grp_Need Check], Measure.[Const Grp_Refer Time], Measure.[Const Grp_Prod Qty]"]
                                                        , "", "", "");  // where, orderby, limit

                let rtnNeedCheck = (rtnMeasureValue.cs.row(0).cell(rtnMeasureValue.cs.measureColumnIndex("Const Grp_Need Check")) !== null) ? rtnMeasureValue.cs.row(0).cell(rtnMeasureValue.cs.measureColumnIndex("Const Grp_Need Check")).toString() : null;
                let rtnRefTime = (rtnMeasureValue.cs.row(0).cell(rtnMeasureValue.cs.measureColumnIndex("Const Grp_Refer Time")) !== null) ? rtnMeasureValue.cs.row(0).cell(rtnMeasureValue.cs.measureColumnIndex("Const Grp_Refer Time")).toString() : null;

                // vdCommon.debug("점검필요=======>Group ID : "+ fbGroupID +" / "+ rtnNeedCheck);

                // 점검필요가 Not Null 일 경우 체크
                if( rtnNeedCheck !== null && rtnNeedCheck !== "" ){
                    returnData.msg = "validation 수행후 Apply을 실행하세요. [ Group ID :"+fbGroupID+" / Sequence : "+fbSeq+" ]";
                    returnData.flag = false;
                    return returnData;
                }

                // Ref.Time 체크
                if( rtnRefTime == null || rtnRefTime === ""){
                    returnData.msg = "Ref.Time을 입력 후 Apply을 실행하세요. [ Group ID :"+fbGroupID+" / Sequence : "+fbSeq+" ]";
                    returnData.flag = false;
                    return returnData;
                }

            }
            returnData.msg = "";
            returnData.flag = true;

            vdCommon.programEnd();

            return returnData;

        } catch ( e ) {
            RuleOutputToUI = { Status : 'Error', Message : "Js Logic Error : " + e.message };
            return;
        }
    }
    /**
     * fn_Apply
     * UI 화면의 Apply -- 테스트 중
     * @param {*} o9Params 
     */
    var fn_Apply = function(o9Params){
        try {
            const commonLib = require('o9.NSCM.commonLib');
            const vdCommon = new commonLib.VdCommon(programName);
            const vdUtil = new commonLib.VdUtil();   // 2024.08.14 add
        
            vdCommon.setLogLevel("Debug");

            vdCommon.programStart();
            vdCommon.debug("fn_Apply=======>");
            vdCommon.printParams(o9Params);
            // 파라미터 가져오기
            let parsedParams = JSON.parse(o9Params);

            let rtnValid = fn_ValidationApply(o9Params);
            if ( !rtnValid.flag ){
                RuleOutputToUI = { Status : 'Error', Message : rtnValid.msg };
                return;
            }

            // Row 선택 변수
            let fbGroupId_filter = parsedParams.fbGroupId;
            let fbSequence_filter = parsedParams.fbSequence;

            // Tuple List 변수 
            let parseTupleSize = parsedParams.fbConstGrpTuple.length;
            let tupleList = parsedParams.fbConstGrpTuple;
            let fbGroupID = "";

            let dimGrpDetail = [];
            let dimGrpDetailW = [];
            let dimGrpEcp = [];

            for (let i=0; i < parseTupleSize; i++) {
                const row = tupleList[i];
                fbGroupID = row.Group_ID.Value;
                // Constraint Group 은 삭제하면 안됨.
                // 1.Constraint Group Detail 삭제
                dimGrpDetail = ["&CWVUI","[Group].[Group ID].[" + fbGroupID + "]"];
                vdCommon.deleteMeasure(dimGrpDetail, "Constraint Group Detail");

                // 2.Constraint Group Detail W 삭제
                dimGrpDetailW = [...dimGrpDetail];
                dimGrpDetailW.push(Horizon);
                vdCommon.deleteMeasure(dimGrpDetailW, "Constraint Group Detail W");

                // 3.Constraint Group Ecp 삭제
                dimGrpEcp = [...dimGrpDetail];
                dimGrpEcp.push("&LCMItem");
                vdCommon.deleteMeasure(dimGrpEcp, "Constraint Group Ecp");
            }
            // vdCommon.debug("########### Measure 결과값 구하기 >>> 1");
            // Measure 의 Location 을 구한다
            let rtnMeasureValue = vdCommon.selectList(["&CWVUI","[Sequence].[Sequence]"+vdUtil.fn_filterStr(fbSequence_filter),"[Group].[Group ID]"+vdUtil.fn_filterStr(fbGroupId_filter)]
                                                        , [
                                                            'Measure.[Const Grp_From Site]'
                                                            ,'Measure.[Const Grp_To Site]'
                                                            ,'Measure.[Const Grp_Product Group]'
                                                            ,'Measure.[Const Grp_Definition]'
                                                            ,'Measure.[Const Grp_Project]'
                                                            ,'Measure.[Const Grp_Mkt Name]'
                                                            ,'Measure.[Const Grp_Inch]'
                                                            ,'Measure.[Const Grp_Year]'
                                                            ,'Measure.[Const Grp_Item]'
                                                        ]
                                                        , "", "", "");  // where, orderby, limit
            // vdCommon.debug("########### Measure 결과값 구하기 >>> 2");
            let rtnLocation = [], rtnSubLocation = [], rtnProductGroup = [], rtnDefinition = [], rtnProject = [], rtnMktName = [], rtnInch = [], rtnYear = [], rtnItem = [];
            let vSubLocation ="", vProductGroup = "", vDefinition = "", vProject="", vMktName = "", vInch = "", vYear = "", vItem = "";
            for ( i=0; i<rtnMeasureValue.cs.rowCount; i++){
               
                rtnLocation.push(rtnMeasureValue.cs.row(i).cell(rtnMeasureValue.cs.measureColumnIndex("Const Grp_From Site")));
                vSubLocation = rtnMeasureValue.cs.row(i).cell(rtnMeasureValue.cs.measureColumnIndex("Const Grp_To Site"));
                vProductGroup = rtnMeasureValue.cs.row(i).cell(rtnMeasureValue.cs.measureColumnIndex("Const Grp_Product Group")).replace(/\^/g,'","');
                vDefinition = rtnMeasureValue.cs.row(i).cell(rtnMeasureValue.cs.measureColumnIndex("Const Grp_Definition"));
                vProject = rtnMeasureValue.cs.row(i).cell(rtnMeasureValue.cs.measureColumnIndex("Const Grp_Project"));
                vMktName = rtnMeasureValue.cs.row(i).cell(rtnMeasureValue.cs.measureColumnIndex("Const Grp_Mkt Name"));
                vInch = rtnMeasureValue.cs.row(i).cell(rtnMeasureValue.cs.measureColumnIndex("Const Grp_Inch"));
                vYear = rtnMeasureValue.cs.row(i).cell(rtnMeasureValue.cs.measureColumnIndex("Const Grp_Year"));
                vItem = rtnMeasureValue.cs.row(i).cell(rtnMeasureValue.cs.measureColumnIndex("Const Grp_Item"));

                if ( vSubLocation != "All") rtnSubLocation.push(vSubLocation);
                if ( vProductGroup != "All") rtnProductGroup.push(vProductGroup);
                if ( vDefinition != "All") rtnDefinition.push(vDefinition);
                if ( vProject != "All") rtnProject.push(vProject);
                if ( vMktName != "All") rtnMktName.push(vMktName);
                if ( vInch != "All") rtnInch.push(vInch);
                if ( vYear != "All") rtnYear.push(vYear);
                if ( vItem != "All") rtnItem.push(vItem);

            }

            /* APPLY 호출 (PY_UI_ProdConstSETApply) - Detail W 재생성 */
            // Scope 에 Location 을 추가하여 BOD Item Data를 줄인다.
            var execQuery = 'EXEC plugin instance [PY_UI_ProductionConstApply] ' +
                            'for measures {[Const Grp Detail_From Site]} ' +
                            'using scope ( &CWVUI * [Group].[Group ID]' + vdUtil.fn_filterStr(fbGroupId_filter) + ' * ' +
                                         '[Location].[Location]' + vdUtil.fn_filterStr(rtnLocation) + ' * ' +
                                         '&LCMItem '+ ') '+                                                                
                            'using arguments {(ExecutionMode, "MediumWeight"), ("IncludeNullRows", "False") , (MaxSliceTableCells, 200000000), (MaxConcurrency, 1), ([Param.o9_sys_log_level], "DEBUG") }; ';
            
            vdCommon.debug("execQuery: " + JSON.stringify(execQuery));
            vdCommon.executeQuery("PY Apply Run", execQuery);

            let measure = ['Measure.[Const Grp Detail Update Time] = dateadd(Now(),9,"hour");', 
                           'Measure.[Const Grp Detail Update User] = CurrentUser().[User Name];'];

            /* Update일자, 사용자 정보입력 */
            // Measure Group 존재하는지 체크후 생성 및 수정
            if ( !vdCommon.existMeasure(["&CWVUI"], ['Measure.[Const Grp Detail_From Site]'], "") ) {
                vdCommon.createMeasure(["&CWVUI"], measure);
            } else {                
                vdCommon.updateMeasure(["&CWVUI"],  measure);
            }

            vdCommon.programEnd();
        } catch ( e ) {
            RuleOutputToUI = { Status : 'Error', Message : "Js Logic Error : " + e.message };
            return;
        }
    };

    /**
     * fn_Delete
     * UI 화면의 Delete Measure = Null 세팅용 Delete
     * 차후 Measure =Null 로 할 경우 사용 2024.11.13 syif1380.lee
     * @param {*} o9Params 
     */
    var fn_Delete_Null = function(o9Params){
        try {
            const commonLib = require('o9.NSCM.commonLib');
            const vdCommon = new commonLib.VdCommon(programName);
            const VdUtil = new commonLib.VdUtil();   // 2024.08.14 add
        
            vdCommon.setLogLevel("Debug");

            vdCommon.debug("fn_Delete=======>1");
            vdCommon.setLogLevel("Debug");
            vdCommon.programStart();
            vdCommon.printParams(o9Params);
            // 파라미터 가져오기
            let parsedParams = JSON.parse(o9Params);      
            
            // Row 선택 변수
            let fbGroupId_filter = parsedParams.fbGroupId;
            let fbVersion_filter = parsedParams.fbVersion;

            // Tuple List 변수 
            let parseTupleSize = parsedParams.fbConstGrpTuple.length;
            let tupleList = parsedParams.fbConstGrpTuple;
            let fbGroupID = "", fbSeq = "";
            let fbVersion = fbVersion_filter;

            let queryStrGroup = "", queryStrDetail = "", queryStrDetail_W = "", queryStrEcp = "";

            for (let i=0; i < parseTupleSize; i++) {
                const group = tupleList[i];
                fbGroupID = group.Group_ID.Value;
                fbSeq     = group.Seq.Value;
                //----------------------------------------------------------------------------------//
                // 1.Constraint Group 삭제
                //----------------------------------------------------------------------------------//
                var dimensionGroup = [];
                dimensionGroup.push("Version.[Version Name].["+fbVersion +"]");
                dimensionGroup.push("[Group].[Group ID].[" + fbGroupID + "]");
                dimensionGroup.push("[Sequence].[Sequence].[" + fbSeq + "]");

                var measureGroup = [];
                measureGroup.push('Measure.[Const Grp_Build Ahead]= null;');
                measureGroup.push(' Measure.[Const Grp_Definition]= null;');
                measureGroup.push(' Measure.[Const Grp_Desc]= null;');
                measureGroup.push(' Measure.[Const Grp_Enddate]= null;');
                measureGroup.push(' Measure.[Const Grp_From Site]= null;');
                measureGroup.push(' Measure.[Const Grp_From Site Name]= null;');
                measureGroup.push(' Measure.[Const Grp_Inch]= null;');
                measureGroup.push(' Measure.[Const Grp_Item]= null;');
                measureGroup.push(' Measure.[Const Grp_Mkt Name]= null;');
                measureGroup.push(' Measure.[Const Grp_Need Check]= null;');
                measureGroup.push(' Measure.[Const Grp_Prod Qty]= null;');
                measureGroup.push(' Measure.[Const Grp_Product Group]= null;');
                measureGroup.push(' Measure.[Const Grp_Project]= null;');
                measureGroup.push(' Measure.[Const Grp_Reason]= null;');
                measureGroup.push(' Measure.[Const Grp_Refer Time]= null;');
                measureGroup.push(' Measure.[Const Grp_Startdate]= null;');
                measureGroup.push(' Measure.[Const Grp_To Site]= null;');
                measureGroup.push(' Measure.[Const Grp_To Site Name]= null;');
                measureGroup.push(' Measure.[Const Grp_Update Time]= null;');
                measureGroup.push(' Measure.[Const Grp_Updated By]= null;');
                measureGroup.push(' Measure.[Const Grp_Year]= null;');

                // Measure Group 존재하는지 체크후 삭제
                if ( vdCommon.existMeasure(dimensionGroup, ['Measure.[Const Grp_From Site]'], "") ) {
                    queryStrGroup += vdCommon.updateMeasureQuery(dimensionGroup, measureGroup);
                }

                //----------------------------------------------------------------------------------//
                // 2.Constraint Group Detail 삭제
                //----------------------------------------------------------------------------------//
                var dimensionDetail = [];
                dimensionDetail.push("Version.[Version Name].["+fbVersion +"]");
                dimensionDetail.push("[Group].[Group ID].[" + fbGroupID + "]");

                var measureDetail = [];
                measureDetail.push('Measure.[Const Grp Detail_Desc]= null;');
                measureDetail.push(' Measure.[Const Grp Detail_From Site]= null;');
                measureDetail.push(' Measure.[Const Grp Detail_From Site Name]= null;');
                measureDetail.push(' Measure.[Const Grp Detail_Item]= null;');
                measureDetail.push(' Measure.[Const Grp Detail_Product Group]= null;');
                measureDetail.push(' Measure.[Const Grp Detail_To Site]= null;');
                measureDetail.push(' Measure.[Const Grp Detail_To Site Name]= null;');

                // Measure Group 존재하는지 체크후 삭제
                if ( vdCommon.existMeasure(dimensionDetail, ['Measure.[Const Grp Detail_From Site]'], "") ) {
                    queryStrDetail += vdCommon.updateMeasureQuery(dimensionDetail, measureDetail);
                }
                
                //----------------------------------------------------------------------------------//
                // 3.Constraint Group Detail W 삭제
                //----------------------------------------------------------------------------------//
                var dimensionDetail_W = [];
                dimensionDetail_W.push("Version.[Version Name].["+fbVersion +"]");
                dimensionDetail_W.push("[Group].[Group ID].[" + fbGroupID + "]");
                dimensionDetail_W.push("[Time].[Week]");

                var measureDetail_W = [];
                measureDetail_W.push('Measure.[Const Grp Detail W_Lock Flag] = null;');
                measureDetail_W.push(' Measure.[Const Grp Detail W_Qty]       = null;');

                // Measure Group 존재하는지 체크후 삭제, 정확한 메저 갯수 체크시에는 Grain 모두 있어야 함
                if ( vdCommon.existMeasure(dimensionDetail_W, ['Measure.[Const Grp Detail W_Qty]'], "") ) {
                    queryStrDetail_W += vdCommon.updateMeasureQuery(dimensionDetail, measureDetail_W);  // update시에는 Time.Week 제외 하고 처리
                }
                
                //----------------------------------------------------------------------------------//
                // 4.Constraint Group Ecp 삭제
                //----------------------------------------------------------------------------------//
                vdCommon.debug("************ 4.Constraint Group Ecp 삭제 *********************");
                var dimensionEcp = [];
                dimensionEcp.push("Version.[Version Name].["+fbVersion +"]");
                dimensionEcp.push("[Group].[Group ID].[" + fbGroupID + "]");
                dimensionEcp.push("[Item].[Item]");

                var measureGroupEcp = [];
                measureGroupEcp.push('Measure.[Const Grp Ecp_Flag] = null;');
                
                // Measure Group 존재하는지 체크후 삭제
                if ( vdCommon.existMeasure(dimensionEcp, ['Measure.[Const Grp Ecp_Flag]'], "") ) {
                    queryStrEcp += vdCommon.updateMeasureQuery(dimensionDetail, measureGroupEcp);
                }                
                
            }   // end for

            // 실행구문 ( != null > null, undefiend  동시 체크)
            if( queryStrGroup != null && queryStrGroup !== "" ){
                vdCommon.executeQuery("Batch Query-1.Constraint Group" , queryStrGroup);
            }
            if( queryStrDetail != null && queryStrDetail !== "" ){
                vdCommon.executeQuery("Batch Query-2.Constraint Group Detail" , queryStrDetail);
            }
            if( queryStrDetail_W != null && queryStrDetail_W !== "" ){
                vdCommon.executeQuery("Batch Query-3.Constraint Group Detail W" , queryStrDetail_W);
            }            
            if( queryStrEcp != null && queryStrEcp !== "" ){
                vdCommon.executeQuery("Batch Query-4.Constraint Group Ecp 삭제" , queryStrEcp);
            }
            // 단일 값 : "MFC0001", 여러값일 경우 : "MFC00001","MFC00002"  형태로 만들어 준다.
            let fbGroupId_arr = (fbGroupId_filter !=null && fbGroupId_filter.length === 1) ? `"${fbGroupId_filter[0]}"` : `"${fbGroupId_filter.join('","')}"`;

            /* APPLY 호출 (PY_UI_ProdConstSETApply) - Detail W 재생성 */
            var execQuery = '/*----------실행 PY_UI_ProductionConstApply-------------*/' +
                            'EXEC plugin instance [PY_UI_ProductionConstApply] ' +
                            'for measures {[Const Grp Detail_From Site]} ' +
                            'using scope ( Version.[Version Name].Filter(#.Name in { "'+ fbVersion +'" }) * [Group].[Group ID].Filter(#.Name in { '+ fbGroupId_arr +' }) ) ' +
                            'using arguments {(ExecutionMode, "MediumWeight"), ("IncludeNullRows", "False") , (MaxSliceTableCells, 200000000), (MaxConcurrency, 1), ([Param.o9_sys_log_level], "DEBUG") };  ';
            
            vdCommon.debug("execQuery: " + JSON.stringify(execQuery));
            vdCommon.executeQuery("PY Apply Run", execQuery);

            // 사용자 Update 정보
            let granularity = [];
            granularity.push("[Version].[Version Name]");

            let granularityValues = [];
            granularityValues.push(fbVersion_filter);
            
            let dimension = ["[Version].[Version Name].[" + fbVersion_filter + "]"];
            let measure = ['Measure.[Const Grp Detail Update Time] = now();', 
                            'Measure.[Const Grp Detail Update User] = CurrentUser().[User Name];'];

            /* Update일자, 사용자 정보입력 */
            // Measure Group 존재하는지 체크후 생성 및 수정
            if ( !vdCommon.existMeasure(dimension, ['Measure.[Const Grp Detail Update Time]'], "") ) {
                vdCommon.createMeasure(vdCommon.makeDimension(granularity, granularityValues), measure);
            } else {                
                vdCommon.updateMeasure(dimension,  measure);
            }            
        
            vdCommon.programEnd();
        } catch ( e ) {
            RuleOutputToUI = { Status : 'Error', Message : "Js Logic Error : " + e.message };
            return;
        }
    };

    /**
     * fn_Delete - 현재 사용중 (2024.11.13 syif1380.lee)
     * UI 화면의 Delete
     * @param {*} o9Params 
     */
    var fn_Delete = function(o9Params){
        try {
            const commonLib = require('o9.NSCM.commonLib');
            const vdCommon = new commonLib.VdCommon(programName);
            const VdUtil = new commonLib.VdUtil();   // 2024.08.14 add
        
            vdCommon.setLogLevel("Debug");

            vdCommon.debug("fn_Delete=======>1");
            vdCommon.setLogLevel("Debug");
            vdCommon.programStart();
            vdCommon.printParams(o9Params);
            // 파라미터 가져오기
            let parsedParams = JSON.parse(o9Params);      
            
            // Tuple List 변수 
            let parseTupleSize = parsedParams.fbConstGrpTuple.length;
            let tupleList = parsedParams.fbConstGrpTuple;
            let fbGroupID = "", fbSeq = "";

            let dimGrp = [];
            let dimGrpDetail = [];
            let dimGrpDetailW = [];

            for (let i=0; i < parseTupleSize; i++) {
                const row = tupleList[i];
                fbGroupID = row.Group_ID.Value;
                fbSeq     = row.Seq.Value;

                // 1.Constraint Group 삭제
                dimGrp = ["&CWVUI","[Group].[Group ID].[" + fbGroupID + "]","[Sequence].[Sequence].[" + fbSeq + "]"];                
                vdCommon.deleteMeasure(dimGrp, "Constraint Group");

                // 1.Constraint Group Detail 삭제
                dimGrpDetail = ["&CWVUI","[Group].[Group ID].[" + fbGroupID + "]"];
                vdCommon.deleteMeasure(dimGrpDetail, "Constraint Group Detail");

                // 1.Constraint Group Detail W 삭제
                dimGrpDetailW = [...dimGrpDetail];
                dimGrpDetailW.push(Horizon);    // 상단에 상수로 정의 됨 &MPHorizon
                vdCommon.deleteMeasure(dimGrpDetailW, "Constraint Group Detail W");

                // 1.Constraint Group Ecp 삭제
                vdCommon.deleteMeasure(dimGrpDetail, "Constraint Group Ecp");
            }        
            vdCommon.programEnd();
        } catch ( e ) {
            RuleOutputToUI = { Status : 'Error', Message : "Js Logic Error : " + e.message };
            return;
        }
    };
    /**
     * fn_Copy
     * UI 화면의 fn_Copy
     * 
     * @param {*} o9Params 
     */
    var fn_Copy = function(o9Params){
        try {
            const commonLib = require('o9.NSCM.commonLib');
            const cellsetModule = require('o9/data/cellset');
            const vdCommon = new commonLib.VdCommon(programName);
            const VdUtil = new commonLib.VdUtil();
        
            vdCommon.setLogLevel("Debug");

            // vdCommon.debug("fn_Copy=======>1");
            vdCommon.setLogLevel("Debug");
            vdCommon.programStart();
            vdCommon.printParams(o9Params);
            
            // 파라미터 가져오기
            let parsedParams = JSON.parse(o9Params);
            // let fbVersion = parsedParams.fbVersion;

            // Tuple 테스트.. 
            let parseTupleSize = parsedParams.fbConstGrpTuple.length;
            let tupleList = parsedParams.fbConstGrpTuple;

            let returnValue = 0;    // 0: 정상, 1: 오류메세지
            if( parseTupleSize > 1 ){
                returnString = "1건만 선택해 주세요.";
                RuleOutputToUI = { Status : 'Error', Message : returnString };
                returnValue = 1;    // 오류                    
                return returnValue;
            }

            for (let i=0; i < parseTupleSize; i++) {
                const row = tupleList[i];
                fbGroupID = row.Group_ID.Value;
                fbSeq     = row.Seq.Value;
                //----------------------------------------------------------------------------------//
                // 1.Constraint Group 추가
                //----------------------------------------------------------------------------------//
                vdCommon.printStep("--1");
                let rtnMeasureValue = vdCommon.selectList(["&CWVUI","[Sequence].[Sequence].["+fbSeq+"]","[Group].[Group ID].["+fbGroupID+"]"]
                                                        , ["Measure.[Const Grp_Build Ahead]", "Measure.[Const Grp_Definition]", "Measure.[Const Grp_Desc]"
                                                         ,"Measure.[Const Grp_Enddate]", "Measure.[Const Grp_From Site]", "Measure.[Const Grp_From Site Name]"
                                                         ,"Measure.[Const Grp_Inch]", "Measure.[Const Grp_Item]", "Measure.[Const Grp_Mkt Name]"
                                                         ,"Measure.[Const Grp_Need Check]", "Measure.[Const Grp_Prod Qty]", "Measure.[Const Grp_Product Group]"
                                                         ,"Measure.[Const Grp_Project]", "Measure.[Const Grp_Reason]", "Measure.[Const Grp_Refer Time]"
                                                         ,"Measure.[Const Grp_Startdate]", "Measure.[Const Grp_To Site]", "Measure.[Const Grp_To Site Name]"
                                                         ,"Measure.[Const Grp_Update Time]", "Measure.[Const Grp_Updated By]", "Measure.[Const Grp_Year]"]
                                                        , "", "", "");  // where, orderby, limit
                vdCommon.printStep("--2");
                let fbLocation = rtnMeasureValue.cs.row(0).cell(rtnMeasureValue.cs.measureColumnIndex("Const Grp_From Site"));
                let fbLocationName = rtnMeasureValue.cs.row(0).cell(rtnMeasureValue.cs.measureColumnIndex("Const Grp_From Site Name"));
                let fbInch = rtnMeasureValue.cs.row(0).cell(rtnMeasureValue.cs.measureColumnIndex("Const Grp_Inch"));
                let fbItem = rtnMeasureValue.cs.row(0).cell(rtnMeasureValue.cs.measureColumnIndex("Const Grp_Item"));
                let rtnNeedCheck = rtnMeasureValue.cs.row(0).cell(rtnMeasureValue.cs.measureColumnIndex("Const Grp_From Site"));
                let fbMKTName = rtnMeasureValue.cs.row(0).cell(rtnMeasureValue.cs.measureColumnIndex("Const Grp_Mkt Name"));
                let fbProductGroup = rtnMeasureValue.cs.row(0).cell(rtnMeasureValue.cs.measureColumnIndex("Const Grp_Product Group"));
                let fbProject = rtnMeasureValue.cs.row(0).cell(rtnMeasureValue.cs.measureColumnIndex("Const Grp_Project"));
                let fbRefTime = rtnMeasureValue.cs.row(0).cell(rtnMeasureValue.cs.measureColumnIndex("Const Grp_Refer Time"));
                let fbSubLocation = rtnMeasureValue.cs.row(0).cell(rtnMeasureValue.cs.measureColumnIndex("Const Grp_To Site"));
                let fbSubLocationName = rtnMeasureValue.cs.row(0).cell(rtnMeasureValue.cs.measureColumnIndex("Const Grp_To Site Name"));
                let fbYear = rtnMeasureValue.cs.row(0).cell(rtnMeasureValue.cs.measureColumnIndex("Const Grp_Year"));
                let fbDefinition = rtnMeasureValue.cs.row(0).cell(rtnMeasureValue.cs.measureColumnIndex("Const Grp_Definition"));
                vdCommon.printStep("--3");
                let rtnCs = vdCommon.selectList(["&CWVUI","[Sequence].[Sequence]","[Group].[Group ID].["+fbGroupID+"]"]
                                                        , ["Measure.[Const Grp_From Site]","Measure.[Const Grp_To Site]"]
                                                        , "", "orderby [Sequence].[Sequence].Name desc", "");
                vdCommon.printStep("--4");
                // Group ID, Sequence 구하기 (Type String)
                let getSeqId = parseInt(rtnCs.cs.row(0).cell(rtnCs.cs.memberColumnIndex('Sequence','Sequence')).Name);
                let makeSeq = getSeqId+1;   // Group ID 의 Seq + Max
                let bWhere = 'where {Measure.[Const Grp_From Site] == "' + fbLocation + '", Measure.[Const Grp_To Site] == "' + fbSubLocation + '", Measure.[Const Grp_Product Group] == "' + fbProductGroup + '"}';
                let vDesc = "";
                if ( fbProductGroup !== "All" ) vDesc += fbProductGroup + " ";
                if ( fbDefinition !== "All" ) vDesc += fbDefinition + " ";
                if ( fbProject !== "All" ) vDesc += fbProject + " ";
                if ( fbMKTName !== "All" ) vDesc += fbMKTName + " ";
                if ( fbInch !== "All" ) vDesc += fbInch + " ";
                if ( fbYear !== "All" ) vDesc += fbYear + " ";
                if ( fbItem !== "All" ) vDesc += fbItem;
                // 마지막 공백 제거
                vDesc = vDesc.trim();
                vdCommon.printStep("--5");
                let dimension = ["&CWVUI","[Sequence].[Sequence].[" + makeSeq + "]", "[Group].[Group ID].[" + fbGroupID + "]"];
                if ( !vdCommon.existMeasure(dimension, ['Measure.[Const Grp_From Site]'], bWhere) ) {
                    vdCommon.printStep("--6");
                    // cartesian scope 아래 메저 모두 등록시.. 시간이 1분 소요 됨.
                    let measure = ['Measure.[Const Grp_From Site]           = "' + fbLocation + '";',
                                    'Measure.[Const Grp_From Site Name]     = "' + fbLocationName + '";',
                                    'Measure.[Const Grp_To Site]            = "' + fbSubLocation + '";',
                                    'Measure.[Const Grp_To Site Name]       = "' + fbSubLocationName + '";',                                            
                                    'Measure.[Const Grp_Product Group]      = "' + fbProductGroup + '";',
                                    'Measure.[Const Grp_Definition]         = "' + fbDefinition + '";',
                                    'Measure.[Const Grp_Project]            = "' + fbProject + '";',
                                    'Measure.[Const Grp_Mkt Name]           = "' + fbMKTName + '";',
                                    'Measure.[Const Grp_Inch]               = "' + fbInch + '";',
                                    'Measure.[Const Grp_Year]               = "' + fbYear + '";',
                                    'Measure.[Const Grp_Item]               = "' + fbItem + '";',
                                    'Measure.[Const Grp_Desc]               = "' + vDesc + '";',
                                    'Measure.[Const Grp_Refer Time]         = "' + fbRefTime + '";',
                                    'Measure.[Const Grp_Enddate]            = null;',
                                    'Measure.[Const Grp_Startdate]          = null;',
                                    'Measure.[Const Grp_Need Check]         = null;',
                                    'Measure.[Const Grp_Reason]             = null;',
                                    'Measure.[Const Grp_Build Ahead]        = null;',
                                    'Measure.[Const Grp_Prod Qty]           = 0;',
                                    'Measure.[Const Grp_Update Time]        = dateadd(Now(),9,"hour");',
                                    'Measure.[Const Grp_Updated By]         = CurrentUser().[User Name];'
                                    ];
                    vdCommon.createMeasure(dimension, ['Measure.[Const Grp_From Site]         = "' + fbLocation + '";']);
                    vdCommon.updateMeasure(dimension,  measure);

                    vdCommon.debug("-----> Measure Group 생성 -- 종료 ");
                } else {
                    RuleOutputToUI = { Status : 'Error', Message : "This Data has already been registered." };
                    return;
                }
            }
            vdCommon.programEnd();
        } catch ( e ) {
            RuleOutputToUI = { Status : 'Error', Message : "Js Logic Error : " + e.message };
            return;
        }
    };

    /**
     * Validation
     * @param {*} o9Params 
     * @returns 
     */
    var fn_validation = function(o9Params){
        try {
            const commonLib = require('o9.NSCM.commonLib');
            const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
            const vdUtil = new commonLib.VdUtil();
            
            vdCommon.setLogLevel("Debug");
            vdCommon.printParams(o9Params);

            // 파라미터 가져오기
            var parsedParams = JSON.parse(o9Params);

            /* Validation 호출 (PY_UI_ProductionConstValid) */
            var execQuery = 'EXEC plugin instance [PY_UI_ProductionConstValid] ' +
                            'for measures {[Const Grp_From Site]} ' +
                            'using scope ( &CWVUI ) ' +
                            // 'using arguments {(ExecutionMode, "MediumWeight"), (MaxSliceTableCells, 200000000), (MaxConcurrency, 1), ([Param.o9_sys_log_level], "DEBUG") };  ';
                            'using arguments {(ExecutionMode, "MediumWeight"), ("IncludeNullRows", "False") , (MaxSliceTableCells, 200000000), (MaxConcurrency, 1), ([Param.o9_sys_log_level], "DEBUG") }; ';
            vdCommon.debug("execQuery: " + JSON.stringify(execQuery));
            vdCommon.executeQuery("fn_validation : PY_UI_ProductionConstValid Run", execQuery);

            vdCommon.programEnd();
        } catch ( e ) {
            RuleOutputToUI = { Status : 'Error', Message : "Js Logic Error : " + e.message };
            return;
        }
    };

    return{
         fn_locationCombo       : fn_locationCombo
        ,fn_subLocationCombo    : fn_subLocationCombo
        ,fn_productGroupCombo   : fn_productGroupCombo
        ,fn_definitionCombo     : fn_definitionCombo
        ,fn_projectCombo        : fn_projectCombo
        ,fn_mktNameCombo        : fn_mktNameCombo
        ,fn_inchCombo           : fn_inchCombo
        ,fn_yearCombo           : fn_yearCombo
        ,fn_itemCombo           : fn_itemCombo
        ,fn_Add     : fn_Add
        ,fn_Apply   : fn_Apply
        ,fn_Delete  : fn_Delete
        ,fn_Copy    : fn_Copy
        ,fn_validation : fn_validation
        /* 2024.11.27 ProductionConst LCM Create*/
    };
});