define('o9.NSCM.JSProductionConst', ['o9/data/query', 'o9/data/cellset', 'o9.NSCM.commonLib'], function(){

    const programName = "o9.NSCM.JSProductionConst";
    const Horizon    = "&MPHorizon";
    const MFC_SET    = "MFC_S";
    const SRC_SET    = "SRC_S";

    var fn_locationCombo = function(o9Params){
        try {            
            const commonLib = require('o9.NSCM.commonLib');
            const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
            const vdUtil = new commonLib.VdUtil();

            vdCommon.setLogLevel("Debug");
            var parsedParams = JSON.parse(o9Params);

            var where = 'where {'
            +' &CWVUI'
            +', Measure.[BOD List_BOD Valid] == "Y" '
            +', coalesce(Measure.[BOD List_Eff Startdate],DATEADD(Now(),-1,"Day")) < now() '
            +', coalesce(Measure.[BOD List_Eff Enddate],DATEADD(Now(),1,"Day")) > now() '
            +'}';
            var result = vdCommon.selectList(["&MFStageSETLocation"],
                                             ["Measure.[BOD List_BOD Valid]",
                                              "Measure.[BOD List_Eff Enddate]",
                                              "Measure.[BOD List_Eff Startdate]"],
                                             where,
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

    // GC  add 2025.04.23 노보람p 요청
    function fn_salesGCCombo(o9Params){
        try{
            const commonLib = require('o9.NSCM.commonLib');
            const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
            const vdUtil = new commonLib.VdUtil();
            vdCommon.setLogLevel("Debug");
            vdCommon.printParams(o9Params);
            // 파라메타 가져오기
            let parsedParams = JSON.parse(o9Params); 
            let fbLocation = parsedParams.fbLocation;

            var where = 'where {'
            +' &CWVUI'
            +', [Location].[Location]'+ vdUtil.fn_filterStr(fbLocation)
            +', &NSUISubLocationDC'     // Sub Location
            +', (Measure.[BOD Item_Asn] >-1)'
            +'}';

            let selectResult = vdCommon.selectList(['[Sub Location].[Sub Location GC].filter(~(#.Name in {"All", "-"}))'],
                                                    [], 
                                                    where,
                                                    "","");
            let comboList = vdCommon.fn_makeCombo(selectResult, {DimName : "Sub Location", DimAttbName : "Sub Location GC", existAll : true, Sort : "DisplayName", isDisplayNameWithCode : false});
            var dateGC = comboList.map((value) => value.Name);

            let result = vdCommon.selectList(["[Sales Domain].[GC]" +vdUtil.fn_filterStr(dateGC)]
                                            ,[],"","","");
            comboList = vdCommon.fn_makeCombo(result, {DimName : "Sales Domain", DimAttbName : "GC", Sort :"DisplayName", existAll : false, isDisplayNameWithCode : true});
            comboList.unshift({ Name : "All", DisplayName : "All"});
    
            vdCommon.programEnd();

            return comboList;

        }catch ( e ) {
            RuleOutputToUI = { Status : 'Error', Message : "Js Logic Error : " + e.message };
            return;
        }
    }

    // AP2  add 2025.04.23 노보람p 요청
    function fn_salesAP2Combo(o9Params){
        try{
            const commonLib = require('o9.NSCM.commonLib');
            const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
            const vdUtil = new commonLib.VdUtil();
            vdCommon.setLogLevel("Debug");

            // 파라메타 가져오기
            let parsedParams = JSON.parse(o9Params); 
            let fbLocation = parsedParams.fbLocation;
            let fbGC = parsedParams.fbGC;

            var where = 'where {'
            +' &CWVUI'
            +', [Location].[Location]'+ vdUtil.fn_filterStr(fbLocation)
            +', &NSUISubLocationDC'     // Sub Location
            +', [Sub Location].[Sub Location GC]'+vdUtil.fn_filterStr(fbGC)
            +', (Measure.[BOD Item_Asn] >-1)'
            +'}';
            
            let selectResult = vdCommon.selectList(['[Sub Location].[Sub Location Rep AP2].filter(~(#.Name in {"All", "-"}))'], 
                                                    [], 
                                                    where,
                                                    "","");
            let comboList = vdCommon.fn_makeCombo(selectResult, {DimName : "Sub Location", DimAttbName : "Sub Location Rep AP2", existAll : false, Sort : "DisplayName", isDisplayNameWithCode : false});
            var dateAP2 = comboList.map((value) => value.Name);
            vdCommon.debug("[comboList]"+JSON.stringify(dateAP2));
            let result = vdCommon.selectList(["[Sales Domain].[AP2]" +vdUtil.fn_filterStr(dateAP2)],[],"","","");
            comboList = vdCommon.fn_makeCombo(result, {DimName : "Sales Domain", DimAttbName : "AP2", Sort :"DisplayName", existAll : false, isDisplayNameWithCode : true});   
            //comboList.unshift({ Name : "All", DisplayName : "All"});
    
            vdCommon.programEnd();

            return comboList; 
        }catch ( e ) {
            RuleOutputToUI = { Status : 'Error', Message : "Js Logic Error : " + e.message };
            return;
        }    
    } 

    // GC, AP2 사용 2025.04.23 syif1380.lee 수정
    var fn_subLocationCombo = function(o9Params){
        try {
            const commonLib = require('o9.NSCM.commonLib');
            const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
            const vdUtil = new commonLib.VdUtil();

            vdCommon.setLogLevel("Debug");
            vdCommon.printParams(o9Params);
            // 파라메타 가져오기
            let parsedParams = JSON.parse(o9Params);
            let fbLocation = parsedParams.fbLocation;
            let fbGC = parsedParams.fbGC;
            let fbAP2 = parsedParams.fbAP2;

            var where = 'where {'
            +' &CWVUI'
            +', [Location].[Location]'+ vdUtil.fn_filterStr(fbLocation)
            +', [Sub Location].[Sub Location GC]'+vdUtil.fn_filterStr(fbGC)
            +', [Sub Location].[Sub Location Rep AP2]'+vdUtil.fn_filterStr(fbAP2)
            +', (Measure.[BOD Item_Asn] >-1)'
            +'}';

            var result = vdCommon.selectList(["&NSUISubLocationDC"], [],  where, "","");
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
            const vdUtil = new commonLib.VdUtil();

            vdCommon.setLogLevel("Debug");
            vdCommon.printParams(o9Params);
            // 파라미터 가져오기
            var parsedParams = JSON.parse(o9Params);

            var result = vdCommon.selectList(["&SETItem.relatedmembers([Product Group])"],
                                             [],
                                             "",
                                             "",
                                             "");
            vdCommon.printCsData(result, 3);

            var comboList = vdCommon.fn_makeCombo(result, {DimName : "Item", DimAttbName : "Product Group", Sort : "DisplayName", existAll : true, isDisplayNameWithCode : false}); // All 보이게 수정 2025.04.16 노보람p요청
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

            var where = "where {"
                            +" &SETItem.relatedmembers([Product Group])" + vdUtil.fn_filterStr(fbProductGroup)
                            +"}";

            var result = vdCommon.selectList(["&SETItem.relatedmembers([Definition])"],
                                             [],
                                             where,
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

            var where = "where {"
                            +" &SETItem.relatedmembers([Product Group])" + vdUtil.fn_filterStr(fbProductGroup)
                            +", &SETItem.relatedmembers([Definition])" + vdUtil.fn_filterStr(fbDefinition)
                            +"}";

            var result = vdCommon.selectList(["&SETItem.relatedmembers([Project])"],
                                             [],
                                             where,
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

            var where = "where {"
                            +" &SETItem.relatedmembers([Product Group])" + vdUtil.fn_filterStr(fbProductGroup)
                            +", &SETItem.relatedmembers([Definition])" + vdUtil.fn_filterStr(fbDefinition)
                            +", &SETItem.relatedmembers([Project])" + vdUtil.fn_filterStr(fbProject)
                            +"}";

            var result = vdCommon.selectList(["&SETItem.relatedmembers([Marketing Name])"],
                                            [],
                                            where,
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

            var where = "where {"
                            +" &SETItem.relatedmembers([Product Group])" + vdUtil.fn_filterStr(fbProductGroup)
                            +", &SETItem.relatedmembers([Definition])" + vdUtil.fn_filterStr(fbDefinition)
                            +", &SETItem.relatedmembers([Project])" + vdUtil.fn_filterStr(fbProject)
                            +", &SETItem.relatedmembers([Marketing Name])" + vdUtil.fn_filterStr(fbMKTName)
                            +"}";

            var result = vdCommon.selectList(["&SETItem.relatedmembers([Inch])"],
                                            [],
                                            where,
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

            var where = "where {"
                            +" &SETItem.relatedmembers([Product Group])" + vdUtil.fn_filterStr(fbProductGroup)
                            +", &SETItem.relatedmembers([Definition])" + vdUtil.fn_filterStr(fbDefinition)
                            +", &SETItem.relatedmembers([Project])" + vdUtil.fn_filterStr(fbProject)
                            +", &SETItem.relatedmembers([Marketing Name])" + vdUtil.fn_filterStr(fbMKTName)
                            +", &SETItem.relatedmembers([Inch])" + vdUtil.fn_filterStr(fbInch) 
                            +"}";

            var result = vdCommon.selectList(["&NSUIItemYearComboView"],       // &SETItem.relatedmembers([Year]) 수정 2025.03.10 임재민p요청
                                            [],
                                            where,
                                            "orderby [Item].[Year].[Name] desc",
                                            "");
            vdCommon.printCsData(result, 3);

            // var comboList = vdCommon.fn_makeCombo(result, {DimName : "Item", DimAttbName : "Year", Sort : "DisplayName", existAll : true});
            var comboList = vdCommon.fn_makeCombo(result, {DimName : "Item", DimAttbName : "Year", existAll : true});
            
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

            var where = 'where {'
            +' &CWVUI'
            +', [Location].[Location]'+ vdUtil.fn_filterStr(fbLocation)
            +', &NSUISubLocationDC'+ (fbSubLocation ? vdUtil.fn_filterStr(fbSubLocation) : "")
            +', Item.[Product Group]'+ vdUtil.fn_filterStr(fbProductGroup)
            +', Item.[Definition]'+ vdUtil.fn_filterStr(fbDefinition)
            +', Item.[Project]'+ vdUtil.fn_filterStr(fbProject)
            +', Item.[Marketing Name]'+ vdUtil.fn_filterStr(fbMKTName)
            +', Item.[Inch]'+ vdUtil.fn_filterStr(fbInch)
            +', Item.[Year]'+ vdUtil.fn_filterStr(fbYear)
            +', Measure.[BOD Item_Asn] >-1'
            +', Measure.[BOD Item_Cur Status] in {"PLANNED", "ACTIVE"}'
            +'}';
            vdCommon.debug(" where : "+where);

            var result = vdCommon.selectList(["&SETItem"],
                                             ["Measure.[BOD Item_Asn]"],
                                             where,
                                             "",
                                             "");
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
    
    // Member 체크 후 Member 생성, Measure Group 입력하는 함수
    // var fn_ExecMemberMeasure = function(parsedParams, params){
    function fn_ExecMemberMeasure(parsedParams, params){
        try {            
            const commonLib = require('o9.NSCM.commonLib');
            const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
            const vdUtil = new commonLib.VdUtil();

            vdCommon.setLogLevel("Debug");
            vdCommon.programStart();

            vdCommon.debug("###############  fn_ExecMemberMeasure 함수 호출 ");
            // vdCommon.debug("###############  fn_ExecMemberMeasure parsedParams --> "+ JSON.stringify(parsedParams, null, 2));

            // member 체크 후 생성 (Group ID)
            if ( !vdCommon.existMember('[Group].[Group ID]', params.paramGroupId) ) {
                vdCommon.createDimension(['[Group].[Group ID]','[Group].[Group Name]','[Group].[Group Type]'], [params.paramGroupId, params.paramGroupId, params.paramGroupType]);
            }

            // member 체크 후 생성 (Sequence ID)
            if ( !vdCommon.existMember('[Sequence].[Sequence]', params.paramSeqId) ) {
                vdCommon.createMember('[Sequence].[Sequence]', params.paramSeqId);
            }
            let bWhere = 'where {Measure.[Const Grp_From Site] == "' + parsedParams.fbLocation + '", Measure.[Const Grp_To Site] == "' + params.paramSubLocation + '", Measure.[Const Grp_Product Group] == "' + parsedParams.fbProductGroup + '"}';
            let dimension = ["&CWVUI","[Sequence].[Sequence].[" + params.paramSeqId + "]", "[Group].[Group ID].[" + params.paramGroupId + "]"];
            if ( !vdCommon.existMeasure(dimension, ['Measure.[Const Grp_From Site]'], bWhere) ) {
                let measure = ['Measure.[Const Grp_From Site]       = "' + parsedParams.fbLocation + '";',
                            'Measure.[Const Grp_From Site Name]     = "' + params.paramLocationName + '";',
                            'Measure.[Const Grp_To Site]            = "' + params.paramSubLocation + '";',
                            'Measure.[Const Grp_To Site Name]       = "' + params.paramSubLocationName + '";',                                            
                            'Measure.[Const Grp_Product Group]      = "' + parsedParams.fbProductGroup + '";',
                            'Measure.[Const Grp_Definition]         = "' + parsedParams.fbDefinition + '";',
                            'Measure.[Const Grp_Project]            = "' + parsedParams.fbProject + '";',
                            'Measure.[Const Grp_Mkt Name]           = "' + parsedParams.fbMKTName + '";',
                            'Measure.[Const Grp_Inch]               = "' + parsedParams.fbInch + '";',
                            'Measure.[Const Grp_Year]               = "' + parsedParams.fbYear + '";',
                            'Measure.[Const Grp_Item]               = "' + params.paramItemText + '";',             // add 팝업에서 Item 멀티선택 + 입력하는 String 으로 변경 (문지윤p 요청, 2025.04.28)
                            'Measure.[Const Grp_Desc]               = "' + parsedParams.fbDesc + '";',              // add 팝업에서 입력하는 String 으로 변경 (문지윤p 요청, 2025.04.28)
                            'Measure.[Const Grp_Refer Time]         = "' + parsedParams.fbRefTime + '";',
                            'Measure.[Const Grp_Reason]             = "' + parsedParams.fbReason + '";',              // add 팝업에서 입력하는 String 으로 변경 (문지윤p 요청, 2025.05.08)
                            'Measure.[Const Grp_Enddate]            = null;',
                            'Measure.[Const Grp_Startdate]          = null;',
                            'Measure.[Const Grp_Need Check]         = null;',
                            'Measure.[Const Grp_Build Ahead]        = null;',
                            'Measure.[Const Grp_Prod Qty]           = 0;',
                            'Measure.[Const Grp_Update Time]        = dateadd(Now(),9,"hour");',
                            'Measure.[Const Grp_Updated By]         = CurrentUser().[User Name];'
                            ];
                vdCommon.createMeasure(dimension, ['Measure.[Const Grp_From Site]         = "' + parsedParams.fbLocation + '";']);
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
            let fbLocation = parsedParams.fbLocation;
            vdCommon.debug("########### fn_Add");
            
            let fbSubLocation_arry = parsedParams.fbSubLocation ? parsedParams.fbSubLocation : "All";
            parsedParams.fbSubLocation = parsedParams.fbSubLocation ? parsedParams.fbSubLocation.toString().replace(/,/g, "^") : "All";
            parsedParams.fbProductGroup = parsedParams.fbProductGroup ? parsedParams.fbProductGroup.toString().replace(/,/g, "^") : "All";
            parsedParams.fbDefinition = parsedParams.fbDefinition ? parsedParams.fbDefinition.toString().replace(/,/g, "^") : "All";
            parsedParams.fbProject = parsedParams.fbProject ? parsedParams.fbProject.toString().replace(/,/g, "^") : "All";
            parsedParams.fbMKTName = parsedParams.fbMKTName ? parsedParams.fbMKTName.toString().replace(/,/g, "^") : "All";
            parsedParams.fbInch = parsedParams.fbInch ? parsedParams.fbInch.toString().replace(/,/g, "^") : "All";
            parsedParams.fbYear = parsedParams.fbYear ? parsedParams.fbYear.toString().replace(/,/g, "^") : "All";
            parsedParams.fbDesc = parsedParams.fbDesc ? parsedParams.fbDesc : "";
            parsedParams.fbReason = parsedParams.fbReason ? parsedParams.fbReason : "";

            //----------------- 2025.05.07 테스트로 주석처리 -------//
            // // , 를 ^ 로 변환, All 제외한 대문자 변환
            // let fbItem = parsedParams.fbItem ? parsedParams.fbItem.toString().split(",").map(item => (item === "All" ? item : item.toUpperCase())).join("^") : parsedParams.fbItem;
            // // Item multi-select + Item Text // add 2025.04.28 문지윤p요청
            // // let fbItemText = parsedParams.fbItemText ? parsedParams.fbItemText.toString.trim() : parsedParams.fbItemText;
            // let fbItemText = parsedParams.fbItemText ? parsedParams.fbItemText.trim().toUpperCase() : vdUtil.fn_getString(parsedParams.fbItemText);

            // fbItemText = fbItem ? fbItem+"^"+fbItemText : fbItemText;                       // add 2025.04.28 문지윤p요청
            // fbItemText = fbItemText.toString().replace(/^(\^)+|(\^)+$/g,'');                // 문자열 앞 뒤에 "^" 있으면 지움
            // fbItemText = (fbItemText == null || fbItemText === "") ? "All" : fbItemText;    // Item (Multi-select) , Item (Wildcard) 둘다 값이 없을 경우 Item = All 입력
            //----------------- 2025.05.07 테스트로 주석처리 -------//

            //////////////////////////////////////////05.07//////////////////////////////////////////////////////////////////////
            let fbItem = parsedParams.fbItem;
            let fbItemText = parsedParams.fbItemText ? parsedParams.fbItemText.trim().toUpperCase() : parsedParams.fbItemText;

            if(fbItem == null && fbItemText == ""){
                vdCommon.debug("둘다 값이 없을 때");
                RuleOutputToUI = { Status : 'Error', Message : "One of the fields Item(Multi) and Item(WildCard) is required." };
                return 1;
            }else if (fbItem && !fbItemText){

                if( fbItem == "All"){
                    fbItemText = "All";
                } else {
                    fbItemText = fbItem.filter(v => v != "All").join("^");
                }
                // vdCommon.debug("fbItem && !fbItemText : fbItem 만 있을때 >> #################  fbItemText >> "+fbItemText);

            }else if (!fbItem && fbItemText){
                // fbItemText = fbItemText;
                vdCommon.debug("!fbItem && fbItemText : fbItemText 만 있을때 >> #################  fbItemText >> "+fbItemText);

            }else if (fbItem && fbItemText){
                vdCommon.debug("fbItem && fbItemText : 둘다 있을때 >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>");
                let ItemTextTmp ="";
                if( fbItem == "All"){
                    ItemTextTmp = "All";
                } else {
                    ItemTextTmp = fbItem.filter(v => v != "All");
                    const itemPattern = fbItemText.replace("%","");
                    let match;
                    let matchList = [];
                    if( fbItemText.includes("%") ){
                        if( fbItemText.endsWith("%") ){
                            match = fbItem.some(item => item.startsWith(itemPattern));
                            matchList = fbItem.filter(item => item.startsWith(itemPattern));
                        }else if( fbItemText.startsWith("%") ){
                            match = fbItem.some(item => item.endsWith(itemPattern));
                            matchList = fbItem.filter(item => item.endsWith(itemPattern));
                        }else{
                            match = fbItem.some(item => item.includes(itemPattern));
                            matchList = fbItem.filter(item => item.includes(itemPattern));
                        }
                    }else{
                        // equal
                        match = fbItem.includes(fbItemText);
                        matchList = fbItem.filter(item => item.includes(fbItemText));
                    }
                    vdCommon.debug("########### match ::  "+match);
                    // fbItemText = match ? fbItem.toString().split(",").map(item => item.toUpperCase()).join("^")  : fbItemText;
                    fbItemText = match ? matchList.join("^")  : ItemTextTmp.join("^");
                }
                
                vdCommon.debug("fbItem && fbItemText : 둘다 있을때 >> #################  fbItemText >> "+fbItemText);
            }
            ///////////////////////////////////////////////////////////////////////////////////////////////
            // RuleOutputToUI = { Status : 'Error', Message : "Test---------------------" };
            // return 1;   // 테스트로 브레이크
            ////////////////////////////////////////////////////////////////////////////////////////////////////////////////



            //==========================================================================================================//
            // Location ( From Site ) Name 가져오기
            //==========================================================================================================//
            let fbLocationName = vdCommon.selectResult("[Location].[Location].["+fbLocation+"].DisplayName");

            //==========================================================================================================//
            // Sub Location ( To Site ) Name 가져오기
            //==========================================================================================================//
            // Sub Location = 'All' or All,P54A,P54B 이면 All 빼고
            let fbSubLocationName = "";
            let fbGroupType = "";   // Group Type : MFC_S (SET), MFC_L (LCM)
            if( fbSubLocation_arry == "All" || fbSubLocation_arry == "-"){
                fbGroupType    = MFC_SET;   // MFC_S
                fbSubLocationName = fbSubLocation_arry;
            }else{
                fbGroupType    = SRC_SET;   // SRC_S

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

            // fbSubLocation = fbSubLocation ? fbSubLocation.toString().replace(/,/g, "^") : fbSubLocation;
            let vGroupIdPreFix = fbGroupType+"_";   // SET : MFC_S_00000 , LCM : MFC_L_00000 
            let fullPadLenth = 5;   // Group ID 만들때 MFC숫자 (숫자에 들어갈 길이)

            let argParam = {};
            argParam.paramGroupType = fbGroupType;
            argParam.paramLocationName = fbLocationName;
            argParam.paramSubLocationName = fbSubLocationName;
            argParam.paramItemText = fbItemText;
            argParam.paramSubLocation = parsedParams.fbSubLocation;

            var where = 'where {'
                        +' &CWVUI'
                        +', Measure.[Const Grp_From Site] == "'+fbLocation+'"'
                        +' && Measure.[Const Grp_To Site] == "'+parsedParams.fbSubLocation+'"'
                        +' && Measure.[Const Grp_Product Group] == "'+parsedParams.fbProductGroup+'"'
                        +' && Measure.[Const Grp_Definition] == "'+parsedParams.fbDefinition+'"'
                        +' && Measure.[Const Grp_Project] == "'+parsedParams.fbProject+'"'
                        +' && Measure.[Const Grp_Mkt Name] == "'+parsedParams.fbMKTName+'"'
                        +' && Measure.[Const Grp_Inch] == "'+parsedParams.fbInch+'"'
                        +' && Measure.[Const Grp_Year] == "'+parsedParams.fbYear+'"'
                        +' && Measure.[Const Grp_Item] == "'+fbItemText+'"'
                        +'}';

            //--------------------------------------------------------------------------------------------------------//
            // 중복이 아닌 경우
            // Const Grp : From Site ~ Item Measure 값 일치하지 않을 경우 
            // Group ID, Sequence 생성
            //--------------------------------------------------------------------------------------------------------//
            if ( !vdCommon.existMeasure(["&Sequence","[Group].[Group ID]"], ["Measure.[Const Grp_From Site]"], where) ) {   // Sequence 속도가 느려서 Namedset 사용2025.03.13 (임재민p요청)
                let newGroupID = "";
                let newSequence = 1;
                let result = vdCommon.selectList(['&CWVUI','&Sequence','[Group].[Group ID].filter(#.Name startswith "'+vGroupIdPreFix+'")'],  ['Measure.[Const Grp_From Site]'], '', "orderby [Group].[Group ID].Name desc", '');
                
                // 해당 Group Type에 Measure 가 있는지 조회 : 없으면 초기값으로 세팅
                if ( result.cs.rowCount == 0 ){
                    newGroupID = vGroupIdPreFix + vdUtil.fn_lpad("1", fullPadLenth, "0");
                } else {
                    let rtnGroupID = result.cs.row(0).cell(result.cs.memberColumnIndex("Group", "Group ID")).Name;
                    vdCommon.debug("########### GroupID생성 >> rtnGroupID : "+rtnGroupID);
                    // 두번째 배열의 숫자 + 1 ( ex: MFC_00001 )
                    newGroupID = vGroupIdPreFix + vdUtil.fn_lpad((parseInt(rtnGroupID.split("_").pop()) + 1).toString(), fullPadLenth, "0");
                    vdCommon.debug("########### GroupID생성 >> newGroupID : "+newGroupID);
                    
                }
                argParam.paramGroupId = newGroupID;
                argParam.paramSeqId = newSequence;
                
            }else{
            //--------------------------------------------------------------------------------------------------------//
            // 중복인 경우
            // Measure Group 중복이 있을 경우, 해당 Group ID, seq + 1
            // Measure Group 에 해당하는 Member를 조회 ( Group ID,  Sequence)
            // 조회한 Group ID로 Sequence 의 Max 값 구하기 ( Sequence, 내림차순 정렬)
            //--------------------------------------------------------------------------------------------------------//
                let rtnMaxSequence = vdCommon.selectList(["&Sequence","[Group].[Group ID]"], [], where, "orderby [Sequence].[Sequence].Name desc", "");
                let getSeqId = parseInt(rtnMaxSequence.cs.row(0).cell(rtnMaxSequence.cs.memberColumnIndex("Sequence", "Sequence")).Name);

                // Group ID, Sequence 구하기 (Type String)
                let getGroupId = rtnMaxSequence.cs.row(0).cell(rtnMaxSequence.cs.memberColumnIndex("Group", "Group ID")).Name;
                let makeSeq = getSeqId+1;

                argParam.paramGroupId = getGroupId;
                argParam.paramSeqId = makeSeq;
                
            }

            fn_ExecMemberMeasure(parsedParams, argParam);       // Member 체크 후 Member 생성, Measure Group 입력하는 함수 호출
            
            vdCommon.programEnd();
        } catch ( e ) {
            RuleOutputToUI = { Status : 'Error', Message : "Js Logic Error : " + e.message };
            return;
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
            vdCommon.programStart();
            vdCommon.printParams(o9Params);
            // 파라미터 가져오기
            let parsedParams = JSON.parse(o9Params);

            // Tuple 
            let parseTupleSize = parsedParams.fbConstGrpTuple.length;

            let tupleList = parsedParams.fbConstGrpTuple;
            // let fbGroupID = "", fbSeq = "", sql = "", sqlResult = "", rtnsqlResult = "", rtnNeedCheck = "", rtnStartDate = "", rtnEndDate = "", rtnRefTime = "";
            let fbGroupID = "", fbSeq = "", rtnMeasureValue = "", rtnNeedCheck = "", rtnRefTime = "";
            let returnData = {};
            // 점검필요 항목에 data 존재 여부 체크
            for (let i=0; i < parseTupleSize; i++) {
                const group = tupleList[i];
                fbGroupID = group.Group_ID.Value;
                fbSeq     = group.Seq.Value;

                //  점검필요를 조회한다.
                rtnMeasureValue = vdCommon.selectList(["&CWVUI"
                                                        ,"[Sequence].[Sequence].["+fbSeq+"]"
                                                        ,"[Group].[Group ID].["+fbGroupID+"]"]
                                                        , ["Measure.[Const Grp_From Site], Measure.[Const Grp_Startdate], Measure.[Const Grp_Enddate], Measure.[Const Grp_Need Check], Measure.[Const Grp_Refer Time], Measure.[Const Grp_Prod Qty]"]
                                                        , "", "", "");  // where, orderby, limit

                rtnNeedCheck = (rtnMeasureValue.cs.row(0).cell(rtnMeasureValue.cs.measureColumnIndex("Const Grp_Need Check")) !== null) ? rtnMeasureValue.cs.row(0).cell(rtnMeasureValue.cs.measureColumnIndex("Const Grp_Need Check")).toString() : null;
                rtnRefTime = (rtnMeasureValue.cs.row(0).cell(rtnMeasureValue.cs.measureColumnIndex("Const Grp_Refer Time")) !== null) ? rtnMeasureValue.cs.row(0).cell(rtnMeasureValue.cs.measureColumnIndex("Const Grp_Refer Time")).toString() : null;

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
     * fn_Delete - 현재 사용중 (2024.11.13 syif1380.lee)
     * UI 화면의 Delete
     * 삭제 후 Group ID 의 Seq 가 남아 있는 경우 Apply 기능 수행 -> PY 호출 2025.04.18 추가 (임재민p 요청)
     * @param {*} o9Params 
     */
    var fn_Delete = function(o9Params){
        try {
            const commonLib = require('o9.NSCM.commonLib');
            const vdCommon = new commonLib.VdCommon(programName);
            const vdUtil = new commonLib.VdUtil();
        
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

            //---------------삭제 후 Group ID 의 Sequence 가 남아 있는지 체크 후 PY 호출 -------------------//
            // Group ID 로 건수 확인
            let paramfbGroupId = parsedParams.fbGroupId;        // 2025.04.18 add
            // let paramfbLocation = parsedParams.fbLocation;      // 2025.04.18 add - FieldBindings 추가
            
            var tmpGroupIdList = [];
            var tmpLocationList = [];
            
            for ( var i=0; i<paramfbGroupId.length; i++){
                let result = vdCommon.selectList(['&CWVUI','&Sequence','[Group].[Group ID]'+vdUtil.fn_filterStr(paramfbGroupId[i])]
                                                , ['Measure.[Const Grp_From Site]']
                                                ,''
                                                ,''
                                                ,'');
                if ( result.cs.rowCount > 0 ){
                    tmpGroupIdList.push(paramfbGroupId[i]);
                    tmpLocationList.push(result.cs.row(0).cell(result.cs.measureColumnIndex("Const Grp_From Site")));
                }
            }

            // PY 호출 추가 - 2025.04.18
            if( tmpGroupIdList.length > 0 ){
                fn_PY_UI_ProductionConstApply(o9Params, tmpGroupIdList, tmpLocationList);
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
            const vdUtil = new commonLib.VdUtil();
        
            vdCommon.setLogLevel("Debug");
            vdCommon.programStart();
            vdCommon.printParams(o9Params);
            
            // 파라미터 가져오기
            let parsedParams = JSON.parse(o9Params);

            // Tuple 테스트.. 
            let parseTupleSize = parsedParams.fbConstGrpTuple.length;
            let tupleList = parsedParams.fbConstGrpTuple;
            let fbDesc = parsedParams.fbDesc ? parsedParams.fbDesc : "";       // 화면에서 입력 받음 2025.04.29
            let fbReason = parsedParams.fbReason ? parsedParams.fbReason : ""; // 화면에서 입력 받음 2025.05.08
            
            let fbRefTime = parsedParams.fbRefTime;

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
                let rtnMeasureValue = vdCommon.selectList(["&CWVUI"
                                                        ,"&Sequence"+vdUtil.fn_filterStr(fbSeq)
                                                        ,"[Group].[Group ID].["+fbGroupID+"]"]
                                                        , ["Measure.[Const Grp_Build Ahead]", "Measure.[Const Grp_Definition]", "Measure.[Const Grp_Desc]"
                                                         ,"Measure.[Const Grp_Enddate]", "Measure.[Const Grp_From Site]", "Measure.[Const Grp_From Site Name]"
                                                         ,"Measure.[Const Grp_Inch]", "Measure.[Const Grp_Item]", "Measure.[Const Grp_Mkt Name]"
                                                         ,"Measure.[Const Grp_Need Check]", "Measure.[Const Grp_Prod Qty]", "Measure.[Const Grp_Product Group]"
                                                         ,"Measure.[Const Grp_Project]", "Measure.[Const Grp_Reason]", "Measure.[Const Grp_Refer Time]"
                                                         ,"Measure.[Const Grp_Startdate]", "Measure.[Const Grp_To Site]", "Measure.[Const Grp_To Site Name]"
                                                         ,"Measure.[Const Grp_Update Time]", "Measure.[Const Grp_Updated By]", "Measure.[Const Grp_Year]"]
                                                        , "", "", "");  // where, orderby, limit

                let fbLocation = rtnMeasureValue.cs.row(0).cell(rtnMeasureValue.cs.measureColumnIndex("Const Grp_From Site"));
                let fbLocationName = rtnMeasureValue.cs.row(0).cell(rtnMeasureValue.cs.measureColumnIndex("Const Grp_From Site Name"));
                let fbInch = rtnMeasureValue.cs.row(0).cell(rtnMeasureValue.cs.measureColumnIndex("Const Grp_Inch"));
                let fbItem = rtnMeasureValue.cs.row(0).cell(rtnMeasureValue.cs.measureColumnIndex("Const Grp_Item"));                
                let fbMKTName = rtnMeasureValue.cs.row(0).cell(rtnMeasureValue.cs.measureColumnIndex("Const Grp_Mkt Name"));
                let fbProductGroup = rtnMeasureValue.cs.row(0).cell(rtnMeasureValue.cs.measureColumnIndex("Const Grp_Product Group"));
                let fbProject = rtnMeasureValue.cs.row(0).cell(rtnMeasureValue.cs.measureColumnIndex("Const Grp_Project"));                
                let fbSubLocation = rtnMeasureValue.cs.row(0).cell(rtnMeasureValue.cs.measureColumnIndex("Const Grp_To Site"));
                let fbSubLocationName = rtnMeasureValue.cs.row(0).cell(rtnMeasureValue.cs.measureColumnIndex("Const Grp_To Site Name"));
                let fbYear = rtnMeasureValue.cs.row(0).cell(rtnMeasureValue.cs.measureColumnIndex("Const Grp_Year"));
                let fbDefinition = rtnMeasureValue.cs.row(0).cell(rtnMeasureValue.cs.measureColumnIndex("Const Grp_Definition"));

                let rtnCs = vdCommon.selectList(["&CWVUI","&Sequence","[Group].[Group ID].["+fbGroupID+"]"]
                                                        , ["Measure.[Const Grp_From Site]","Measure.[Const Grp_To Site]"]
                                                        , "", "orderby [Sequence].[Sequence].Name desc", "");
                // Group ID, Sequence 구하기 (Type String)
                let getSeqId = parseInt(rtnCs.cs.row(0).cell(rtnCs.cs.memberColumnIndex('Sequence','Sequence')).Name);
                let makeSeq = getSeqId+1;   // Group ID 의 Seq + Max
                let bWhere = 'where {Measure.[Const Grp_From Site] == "' + fbLocation + '", Measure.[Const Grp_To Site] == "' + fbSubLocation + '", Measure.[Const Grp_Product Group] == "' + fbProductGroup + '"}';

                let dimension = ["&CWVUI"
                                ,"[Sequence].[Sequence].[" + makeSeq + "]"
                                , "[Group].[Group ID].[" + fbGroupID + "]"];
                if ( !vdCommon.existMeasure(dimension, ['Measure.[Const Grp_From Site]'], bWhere) ) {
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
                                    'Measure.[Const Grp_Desc]               = "' + fbDesc + '";',
                                    'Measure.[Const Grp_Refer Time]         = "' + fbRefTime + '";',
                                    'Measure.[Const Grp_Reason]             = "' + fbReason + '";',
                                    'Measure.[Const Grp_Enddate]            = null;',
                                    'Measure.[Const Grp_Startdate]          = null;',
                                    'Measure.[Const Grp_Need Check]         = null;',
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
                            'using arguments {(ExecutionMode, "MediumWeight"), (pDetailLogFlag, "N") , (MaxSliceTableCells, 200000000), (MaxConcurrency, 1), ([Param.o9_sys_log_level], "DEBUG") }; ';
            vdCommon.debug("execQuery: " + JSON.stringify(execQuery));
            vdCommon.executeQuery("fn_validation : PY_UI_ProductionConstValid Run", execQuery);

            vdCommon.programEnd();
        } catch ( e ) {
            RuleOutputToUI = { Status : 'Error', Message : "Js Logic Error : " + e.message };
            return;
        }
    };
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
                dimGrpEcp.push("&SETItem");
                vdCommon.deleteMeasure(dimGrpEcp, "Constraint Group Ecp");
            }
            // Measure 의 Location 을 구한다
            let rtnMeasureValue = vdCommon.selectList(["&CWVUI","&Sequence"+vdUtil.fn_filterStr(fbSequence_filter),"[Group].[Group ID]"+vdUtil.fn_filterStr(fbGroupId_filter)]
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

            // PY 호출 - 변경 2025.04.18
            fn_PY_UI_ProductionConstApply(o9Params, fbGroupId_filter, rtnLocation);

            vdCommon.programEnd();
        } catch ( e ) {
            RuleOutputToUI = { Status : 'Error', Message : "Js Logic Error : " + e.message };
            return;
        }
    };

    
    /** PY 호출 부분만 만들기 - 2025.04.18
        APPLY 호출 (PY_UI_ProdConstSETApply)  
    */
    var fn_PY_UI_ProductionConstApply = function(o9Params, arrGroupID, arrLocation){

        try {
            const commonLib = require('o9.NSCM.commonLib');
            const vdCommon = new commonLib.VdCommon(programName);
            const vdUtil = new commonLib.VdUtil();
        
            vdCommon.setLogLevel("Debug");

            vdCommon.programStart();
            vdCommon.printParams(o9Params);
            // 파라미터 가져오기
            let parsedParams = JSON.parse(o9Params);
            //--------------------------------------------------------------------------------------------------------//
            /* APPLY 호출 (PY_UI_ProdConstSETApply) - Detail W 재생성 */
            // Scope 에 Location 을 추가하여 BOD Item Data를 줄인다.
            //--------------------------------------------------------------------------------------------------------//
            var execQuery = 'EXEC plugin instance [PY_UI_ProductionConstApply] ' +
                            'for measures {[Const Grp Detail_From Site]} ' +
                            'using scope ( &CWVUI * [Group].[Group ID]' + vdUtil.fn_filterStr(arrGroupID) + ' * ' +
                                         '[Location].[Location]' + vdUtil.fn_filterStr(arrLocation) + ' * ' +   // input : BOD Item 의 건수를 줄이기 위한  Location 정보 
                                         '&SETItem '+ ') '+                                                                
                            'using arguments {(ExecutionMode, "MediumWeight"), (pDetailLogFlag, "N"), (MaxSliceTableCells, 200000000), (MaxConcurrency, 1), ([Param.o9_sys_log_level], "DEBUG") }; ';
            
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
        ,fn_salesGCCombo : fn_salesGCCombo          // GC combo 추가 2025.04.23
        ,fn_salesAP2Combo : fn_salesAP2Combo        // AP2 combo 추가 2025.04.23

    };
});
/*-------------------------------------------------------------------------------------------------*/
/* o9.NSCM.JSProductionConst */
/* 2024.12.30 fn_Apply LightWeight 수정*/
/* 2025.01.02 fn_Apply MediumWeight 수정*/
/* 2025.02.06 Filter version 삭제 */
/* 2025.02.25 fn_Add fn_Copy 에 From/to Site 를 Desc에 추가 (문지윤P요청) */
/* 2025.03.06 Year desc적용, 콤보 쿼리 수정 */
/* 2025.03.10 Year , NamedSet 변경 &NSUIItemYearComboView (임재민p요청) */
/* 2025.03.13 select 할때 [Sequence].[Sequence] 를 &Sequence  Namedset  변경 (임재민p요청) */
/* 2025.04.16 fn_productGroupCombo - Product Group : All 설정할수 있게 변경 */
/* 2025.04.18 fn_Delete - 삭제 후 GroupID 가 남아있는 경우 PY_UI_ProductionConstApply 실행 */
/* 2025.04.24 fn_Add : GC, AP2 필드 추가 및 Sub Location 연계 (노보람p요청) */
/* 2025.04.28 fn_Add : Description - 팝업에서 Ken-in 입력값 저장, Item 멀티입력 & Item Key in 으로 변경 (문지윤p요청) */
/* 2025.04.29 fn_Copy : 수정 */
/* 2025.05.08 fn_Add : item(multi-select), itemText 로직 추가 , Measure.[Const Grp_Reason] 필수입력 추가 (문지윤p요청) */
/*-------------------------------------------------------------------------------------------------*/