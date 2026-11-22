define('o9.NSCM.JSEWProductionConst', ['o9/data/query', 'o9/data/cellset', 'o9.NSCM.commonLib'], function(){

    const programName = "o9.NSCM.JSEWProductionConst";
    const Horizon    = "&MPHorizon";
    const MFC_SET    = "MFC_S";
    const SRC_SET    = "SRC_S";
    
    const self = this;

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
//'where {&CWVUI, Measure.[BOD List_BOD Valid] == "Y", coalesce(Measure.[BOD List_Eff Startdate],DATEADD(Now(),-1,"Day")) < now(), coalesce(Measure.[BOD List_Eff Enddate],DATEADD(Now(),1,"Day")) > now()}',
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

    var fn_subLocationCombo = function(o9Params){
        try {
            const commonLib = require('o9.NSCM.commonLib');
            const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
            const vdUtil = new commonLib.VdUtil();

            vdCommon.setLogLevel("Debug");
            vdCommon.printParams(o9Params);
            // 파라메타 가져오기
            let parsedParams = JSON.parse(o9Params);
            //let fbLocation = parsedParams.fbLocation;
			
			let isFilter = false;
			let fbLocation = "All";
			if(parsedParams.fbLocation){
				fbLocation = parsedParams.fbLocation;
				isFilter = true;
			}
			

            var where = 'where {'
            where +=' &CWVUI'
            where +=', [Location].[Location]'+ vdUtil.fn_filterStr(fbLocation)
            where +=', Measure.[BOD List_BOD Valid] == "Y" '
            where +=', coalesce(Measure.[BOD List_Eff Startdate],DATEADD(Now(),-1,"Day")) < now() '
            where +=', coalesce(Measure.[BOD List_Eff Enddate],DATEADD(Now(),1,"Day")) > now() '
            where +='}';

			var result;
			if(isFilter){
				result = vdCommon.selectList(["&NSUISubLocationDC"],
															 ["Measure.[BOD List_BOD Valid]",
															  "Measure.[BOD List_Eff Enddate]",
															  "Measure.[BOD List_Eff Startdate]"],
															where,
															"",
															"");
			}else{
				result = vdCommon.selectList(["&MFStageSETLocation", "&NSUISubLocationDC"],
											 ["Measure.[BOD List_BOD Valid]",
											  "Measure.[BOD List_Eff Enddate]",
											  "Measure.[BOD List_Eff Startdate]"],
											where,
											"",
									"");
			}

            // var result = vdCommon.selectList(["&CWVUI",
            //                         "[Location].[Location].[" + fbLocation + "]",
            //                         "&NSUISubLocationDC",
            //                         "[Trans Mode].[Trans Mode]"],
            //                         ["Measure.[BOD List_BOD Valid]",
            //                         "Measure.[BOD List_Eff Enddate]",
            //                         "Measure.[BOD List_Eff Startdate]"],
            //                         'where {Measure.[BOD List_BOD Valid] == "Y", coalesce(Measure.[BOD List_Eff Startdate],DATEADD(Now(),-1,"Day")) < now(), coalesce(Measure.[BOD List_Eff Enddate],DATEADD(Now(),1,"Day")) > now()}',
            //                         "",
            //                         "");
            vdCommon.printCsData(result, 3);

			var comboList;
			if(isFilter){
				comboList = vdCommon.fn_makeCombo(result, {DimName : "Sub Location", DimAttbName : "Sub Location", Sort : "DisplayName", existAll : true, isDisplayNameWithCode : true});
			}else{
				comboList = fn_makeCombo(result, {ConditionName : "Location", ConditionAttbName : "Location", DimName : "Sub Location", DimAttbName : "Sub Location", Sort : "DisplayName", existAll : true, isDisplayNameWithCode : true});
			}
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
            var fbProductGroup = "All"; //parsedParams.fbProductGroup;

            var where = "where {"
                            +" &SETItem.relatedmembers([Product Group])" + vdUtil.fn_filterStr(fbProductGroup)
                            +"}";
							
			var result = vdCommon.selectList(["&SETItem.relatedmembers([Product Group])", "&SETItem.relatedmembers([Definition])"],
					 [],
					 "",
					 "",
					 "");
			/*
            var result = vdCommon.selectList(["&SETItem.relatedmembers([Definition])"],
                                             [],
                                             where,
                                             "",
                                             "");
			*/
            // var result = vdCommon.selectList(["&SETItem.relatedmembers([Product Group])" + vdUtil.fn_filterStr(fbProductGroup),
            //                                     "&SETItem.relatedmembers([Definition])"],
            //                                  [],
            //                                  "",
            //                                  "",
            //                                  "");
            vdCommon.printCsData(result, 3);

           // var comboList = vdCommon.fn_makeCombo(result, {DimName : "Item", DimAttbName : "Definition", Sort : "DisplayName", existAll : true});
		   var comboList = fn_makeCombo(result, {ConditionName : "Item", ConditionAttbName : "Product Group", DimName : "Item", DimAttbName : "Definition", Sort : "DisplayName", existAll : true});
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
            var fbProductGroup = "All"; //parsedParams.fbProductGroup;
            var fbDefinition = "All"; //parsedParams.fbDefinition;

            var where = "where {"
                            +" &SETItem.relatedmembers([Product Group])" + vdUtil.fn_filterStr(fbProductGroup)
                            +", &SETItem.relatedmembers([Definition])" + vdUtil.fn_filterStr(fbDefinition)
                            +"}";

            var result = vdCommon.selectList(["&SETItem.relatedmembers([Product Group])", "&SETItem.relatedmembers([Definition])", "&SETItem.relatedmembers([Project])"],
                                             [],
                                             "",
                                             "",
                                             "");
			/*								 
            var result = vdCommon.selectList(["&SETItem.relatedmembers([Project])"],
                                             [],
                                             where,
                                             "",
                                             "");
			*/
            // var result = vdCommon.selectList(["&SETItem.relatedmembers([Product Group])" + vdUtil.fn_filterStr(fbProductGroup),
            //                                   "&SETItem.relatedmembers([Definition])" + vdUtil.fn_filterStr(fbDefinition),
            //                                   "&SETItem.relatedmembers([Project])"],
            //                                  [],
            //                                  "",
            //                                  "",
            //                                  "");
            vdCommon.printCsData(result, 3);

           // var comboList = vdCommon.fn_makeCombo(result, {DimName : "Item", DimAttbName : "Project", Sort : "DisplayName", existAll : true});
		   var comboList = fn_makeCombo(result, {ConditionName : "Item^Item", ConditionAttbName : "Product Group^Definition", DimName : "Item", DimAttbName : "Project", Sort : "DisplayName", existAll : true});
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
            var fbProductGroup = "All"; //parsedParams.fbProductGroup;
            var fbDefinition = "All"; //parsedParams.fbDefinition;
            let fbProject = "All"; //parsedParams.fbProject;

            var where = "where {"
                            +" &SETItem.relatedmembers([Product Group])" + vdUtil.fn_filterStr(fbProductGroup)
                            +", &SETItem.relatedmembers([Definition])" + vdUtil.fn_filterStr(fbDefinition)
                            +", &SETItem.relatedmembers([Project])" + vdUtil.fn_filterStr(fbProject)
                            +"}";

			var result = vdCommon.selectList(["&SETItem.relatedmembers([Product Group])", "&SETItem.relatedmembers([Definition])", "&SETItem.relatedmembers([Project])", "&SETItem.relatedmembers([Marketing Name])"],
                                            [],
                                            "",
                                            "",
                                            "");
			/*
            var result = vdCommon.selectList(["&SETItem.relatedmembers([Marketing Name])"],
                                            [],
                                            where,
                                            "",
                                            "");
			*/
            // var result = vdCommon.selectList(["&SETItem.relatedmembers([Product Group])" + vdUtil.fn_filterStr(fbProductGroup),
            //                                     "&SETItem.relatedmembers([Definition])" + vdUtil.fn_filterStr(fbDefinition),
            //                                     "&SETItem.relatedmembers([Project])" + vdUtil.fn_filterStr(fbProject),
            //                                     "&SETItem.relatedmembers([Marketing Name])"],
            //                                 [],
            //                                 "",
            //                                 "",
            //                                 "");
            vdCommon.printCsData(result, 3);

            //var comboList = vdCommon.fn_makeCombo(result, {DimName : "Item", DimAttbName : "Marketing Name", Sort : "DisplayName", existAll : true});
			var comboList = fn_makeCombo(result, {ConditionName : "Item^Item^Item", ConditionAttbName : "Product Group^Definition^Project", DimName : "Item", DimAttbName : "Marketing Name", Sort : "DisplayName", existAll : true});
          
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
            var fbProductGroup = "All"; //parsedParams.fbProductGroup;
            var fbDefinition = "All"; //parsedParams.fbDefinition;
            let fbProject = "All"; //parsedParams.fbProject;
            let fbMKTName = "All"; //parsedParams.fbMKTName;

            var where = "where {"
                            +" &SETItem.relatedmembers([Product Group])" + vdUtil.fn_filterStr(fbProductGroup)
                            +", &SETItem.relatedmembers([Definition])" + vdUtil.fn_filterStr(fbDefinition)
                            +", &SETItem.relatedmembers([Project])" + vdUtil.fn_filterStr(fbProject)
                            +", &SETItem.relatedmembers([Marketing Name])" + vdUtil.fn_filterStr(fbMKTName)
                            +"}";

            var result = vdCommon.selectList(["&SETItem.relatedmembers([Product Group])", "&SETItem.relatedmembers([Definition])", "&SETItem.relatedmembers([Project])", " &SETItem.relatedmembers([Marketing Name])", "&SETItem.relatedmembers([Inch])"],
                                            [],
                                            "",
                                            "",
                                            "");
			/*								
            var result = vdCommon.selectList(["&SETItem.relatedmembers([Inch])"],
                                            [],
                                            where,
                                            "",
                                            "");
			*/
            // var result = vdCommon.selectList(["&SETItem.relatedmembers([Product Group])" + vdUtil.fn_filterStr(fbProductGroup),
            //                                     "&SETItem.relatedmembers([Definition])" + vdUtil.fn_filterStr(fbDefinition),
            //                                     "&SETItem.relatedmembers([Project])" + vdUtil.fn_filterStr(fbProject),
            //                                     "&SETItem.relatedmembers([Marketing Name])" + vdUtil.fn_filterStr(fbMKTName),
            //                                     "&SETItem.relatedmembers([Inch])"],
            //                                 [],
            //                                 "",
            //                                 "",
            //                                 "");
            vdCommon.printCsData(result, 3);

            //var comboList = vdCommon.fn_makeCombo(result, {DimName : "Item", DimAttbName : "Inch", Sort : "DisplayName", existAll : true});
			var comboList = fn_makeCombo(result, {ConditionName : "Item^Item^Item^Item", ConditionAttbName : "Product Group^Definition^Project^Marketing Name", DimName : "Item", DimAttbName : "Inch", Sort : "DisplayName", existAll : true});
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
            var fbProductGroup = "All"; parsedParams.fbProductGroup;
            var fbDefinition = "All"; parsedParams.fbDefinition;
            let fbProject = "All"; parsedParams.fbProject;
            let fbMKTName = "All"; parsedParams.fbMKTName;
            var fbInch = "All"; parsedParams.fbInch;

            // var result = vdCommon.selectList(["&SETItem.relatedmembers([Product Group])" + vdUtil.fn_filterStr(fbProductGroup),
            //                                     "&SETItem.relatedmembers([Definition])" + vdUtil.fn_filterStr(fbDefinition),
            //                                     "&SETItem.relatedmembers([Project])" + vdUtil.fn_filterStr(fbProject),
            //                                     "&SETItem.relatedmembers([Marketing Name])" + vdUtil.fn_filterStr(fbMKTName),
            //                                     "&SETItem.relatedmembers([Inch])" + vdUtil.fn_filterStr(fbInch),
            //                                     "&SETItem.relatedmembers([Year])"],
            //                                 [],
            //                                 "",
            //                                 "",
            //                                 "");

            var where = "where {"
                            +" &SETItem.relatedmembers([Product Group])" + vdUtil.fn_filterStr(fbProductGroup)
                            +", &SETItem.relatedmembers([Definition])" + vdUtil.fn_filterStr(fbDefinition)
                            +", &SETItem.relatedmembers([Project])" + vdUtil.fn_filterStr(fbProject)
                            +", &SETItem.relatedmembers([Marketing Name])" + vdUtil.fn_filterStr(fbMKTName)
                            +", &SETItem.relatedmembers([Inch])" + vdUtil.fn_filterStr(fbInch) 
                            +"}";
			var result = vdCommon.selectList(["&SETItem.relatedmembers([Product Group])", "&SETItem.relatedmembers([Definition])", "&SETItem.relatedmembers([Project])", "&SETItem.relatedmembers([Marketing Name])", " &SETItem.relatedmembers([Inch])", "&NSUIItemYearComboView"],       // &SETItem.relatedmembers([Year]) 수정 2025.03.10 임재민p요청
                                            [],
                                            "",
                                            "orderby [Item].[Year].[Name] desc",
                                            "");
			/*
            var result = vdCommon.selectList(["&NSUIItemYearComboView"],       // &SETItem.relatedmembers([Year]) 수정 2025.03.10 임재민p요청
                                            [],
                                            where,
                                            "orderby [Item].[Year].[Name] desc",
                                            "");
			*/
            vdCommon.printCsData(result, 3);

            // var comboList = vdCommon.fn_makeCombo(result, {DimName : "Item", DimAttbName : "Year", Sort : "DisplayName", existAll : true});
            //var comboList = vdCommon.fn_makeCombo(result, {DimName : "Item", DimAttbName : "Year", existAll : true});
            var comboList = fn_makeCombo(result, {ConditionName : "Item^Item^Item^Item^Item", ConditionAttbName : "Product Group^Definition^Project^Marketing Name^Inch", DimName : "Item", DimAttbName : "Year", Sort : "DisplayName", existAll : true});
            
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
            // where 조건으로 변경 함.. 2025.03.06
            // dims.push("&CWVUI");
            // dims.push("Location.[Location].[" + fbLocation + "]");
            // // All 을 제외한 Multi 조건으로 Filter
            // if( fbSubLocation != "All") dims.push("[Sub Location].[Sub Location]" + vdUtil.fn_filterStr(fbSubLocation));
            // if( fbProductGroup != "All") dims.push("Item.[Product Group]" + vdUtil.fn_filterStr(fbProductGroup));
            // if( fbDefinition != "All") dims.push("Item.[Definition]" + vdUtil.fn_filterStr(fbDefinition));
            // if( fbProject != "All") dims.push("Item.[Project]" + vdUtil.fn_filterStr(fbProject));
            // if( fbMKTName != "All") dims.push("Item.[Marketing Name]" + vdUtil.fn_filterStr(fbMKTName));
            // if( fbInch != "All") dims.push("Item.[Inch]" + vdUtil.fn_filterStr(fbInch));
            // if( fbYear != "All") dims.push("Item.[Year]" + vdUtil.fn_filterStr(fbYear));

            // dims.push("Item.[Item]");
            dims.push("&SETItem");
            // vdCommon.debug(" dims : "+dims);

            // All 을 제외한 Multi 조건으로 Filter
            var strWhere = "";
            if( fbSubLocation != "All") strWhere += ', [Sub Location].[Sub Location]'+ vdUtil.fn_filterStr(fbSubLocation);
            if( fbProductGroup != "All") strWhere += ', Item.[Product Group]'+ vdUtil.fn_filterStr(fbProductGroup);
            if( fbDefinition != "All") strWhere += ', Item.[Definition]'+ vdUtil.fn_filterStr(fbDefinition);
            if( fbProject != "All") strWhere += ', Item.[Project]'+ vdUtil.fn_filterStr(fbProject);
            if( fbMKTName != "All") strWhere += ', Item.[Marketing Name]'+ vdUtil.fn_filterStr(fbMKTName);
            if( fbInch != "All") strWhere += ', Item.[Inch]'+ vdUtil.fn_filterStr(fbInch);
            if( fbYear != "All") strWhere += ', Item.[Year]'+ vdUtil.fn_filterStr(fbYear);

            vdCommon.debug(" strWhere : "+strWhere);

            var where = 'where {'
            +' &CWVUI'
            +', [Location].[Location]'+ vdUtil.fn_filterStr(fbLocation)
            + strWhere
            +', coalesce(Measure.[BOD Item_Eff Startdate],DATEADD(Now(),-1,"Day")) < now() '
            +', coalesce(Measure.[BOD Item_Eff Enddate],DATEADD(Now(),1,"Day")) > now() '
            +'}';
            vdCommon.debug(" where : "+where);

            var result = vdCommon.selectList( dims, // &SETItem
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
            // let fbVersion = parsedParams.fbVersion;
			
			let parseTupleSize = parsedParams.fbConstGrpTuple.length;
            let tupleList = parsedParams.fbConstGrpTuple;
			let arrReturnData = [];
			for (let rowidx =0; rowidx < parseTupleSize; rowidx++) {
				const rowData = tupleList[rowidx];
			
				let fbLocation = rowData.fbLocation;
				let fbSubLocation_arry = rowData.fbSubLocation;
				let fbSubLocation = rowData.fbSubLocation ? rowData.fbSubLocation.toString().replace(/,/g, "^") : rowData.fbSubLocation;
				let fbProductGroup = rowData.fbProductGroup ? rowData.fbProductGroup.toString().replace(/,/g, "^") : rowData.fbProductGroup;
				let fbDefinition = rowData.fbDefinition ? rowData.fbDefinition.toString().replace(/,/g, "^") : rowData.fbDefinition;
				let fbProject = rowData.fbProject ? rowData.fbProject.toString().replace(/,/g, "^") : rowData.fbProject;
				let fbMKTName = rowData.fbMKTName ? rowData.fbMKTName.toString().replace(/,/g, "^") : rowData.fbMKTName;
				let fbInch = rowData.fbInch ? rowData.fbInch.toString().replace(/,/g, "^") : rowData.fbInch;
				let fbYear = rowData.fbYear ? rowData.fbYear.toString().replace(/,/g, "^") : rowData.fbYear;
				// let fbItem = rowData.fbItem ? rowData.fbItem.toString().replace(/,/g, "^") : rowData.fbItem;
				
				let argParam = {};

				// , 를 ^ 로 변환, All 제외한 대문자 변환
				let fbItem = rowData.fbItem ? rowData.fbItem.toString().split(",").map(item => (item === "All" ? item : item.toUpperCase())).join("^") : rowData.fbItem;
				vdCommon.debug("############# fbItem : "+fbItem);

				// let fbRefTime = rowData.fbRefTime;
				//==========================================================================================================//
				// Location ( To Site ) Name 가져오기
				//==========================================================================================================//
				let fbLocationName = vdCommon.selectResult("[Location].[Location].["+fbLocation+"].DisplayName");
				vdCommon.printStep("######################### Location ( To Site ) Name 가져오기 ---> Start");
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
				vdCommon.printStep("######################### Location ( To Site ) Name 가져오기 ---> End");
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
				vdCommon.printStep("######################### Measure Group 중복 체크 --> Start");
				// Measure Group 중복이 없을 경우, Group ID max 값을 가져와 'MFC' max+1, Sequence = 1
				let where = 'where {'+measureFilter+'}' ;
				if ( !vdCommon.existMeasure(["&CWVUI","[Sequence].[Sequence]","[Group].[Group ID]"], measures, where) ) {
					vdCommon.printStep("######################### 중복 없을 때 신규 --> Start");
					let newGroupID = "";
					let newSequence = 1;
					vdCommon.printStep("######################### Group ID 조회--> Start");
					let result = vdCommon.selectList(['&CWVUI','[Sequence].[Sequence]','[Group].[Group ID].filter(#.Name startswith "'+vGroupIdPreFix+'")'],  ['Measure.[Const Grp_From Site]'], '', "orderby [Group].[Group ID].Name desc", '');
					// let result = vdCommon.selectList(['&CWVUI','[Sequence].[Sequence].[1]','[Group].[Group ID].filter(#.Name startswith "'+vGroupIdPreFix+'")'],  ['Measure.[Const Grp_From Site]'], '', "orderby [Group].[Group ID].Name desc", '');
					
					// 해당 Group Type에 Measure 가 있는지 조회 : 없으면 초기값으로 세팅_
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
					vdCommon.printStep("######################### Group ID 조회--> End");
					argParam = {};
					argParam.paramGroupId = newGroupID;
					argParam.paramSeqId = newSequence;
					// argParam.paramVersion = fbVersion;
					argParam.paramGroupType = fbGroupType;
					argParam.paramLocationName = fbLocationName;
					argParam.paramSubLocationName = fbSubLocationName;

					//fn_ExecMemberMeasure(o9Params, argParam);
					fn_ExecMemberMeasure(rowData, argParam);
					vdCommon.printStep("######################### 중복 없을 때 신규 --> End");

				}else{
					vdCommon.printStep("######################### 중복 있을 때 신규 --> Start");
					// 중복인 경우
					// Measure Group 중복이 있을 경우, 해당 Group ID, seq + 1
					// Measure Group 에 해당하는 Member를 조회 ( Group ID,  Sequence)
					// 조회한 Group ID로 Sequence 의 Max 값 구하기 ( Sequence, 내림차순 정렬)
					let rtnMaxSequence = vdCommon.selectList(["&CWVUI","[Sequence].[Sequence]","[Group].[Group ID]"], [], "where {"+measureFilter+"}", "orderby [Sequence].[Sequence].Name desc", "");
					let getSeqId = parseInt(rtnMaxSequence.cs.row(0).cell(rtnMaxSequence.cs.memberColumnIndex("Sequence", "Sequence")).Name);

					// Group ID, Sequence 구하기 (Type String)
					let getGroupId = rtnMaxSequence.cs.row(0).cell(rtnMaxSequence.cs.memberColumnIndex("Group", "Group ID")).Name
					let makeSeq = getSeqId+1;

					argParam = {};
					argParam.paramGroupId = getGroupId;
					argParam.paramSeqId = makeSeq;
					// argParam.paramVersion = fbVersion;
					argParam.paramGroupType = fbGroupType;
					argParam.paramLocationName = fbLocationName;
					argParam.paramSubLocationName = fbSubLocationName;

					//fn_ExecMemberMeasure(o9Params, argParam);
					fn_ExecMemberMeasure(rowData, argParam);
					vdCommon.printStep("######################### 중복 있을 때 신규 --> End");
				}
				
				vdCommon.programEnd();
				let returnData = {};
				returnData.GroupID = argParam.paramGroupId;
				returnData.SeqId = argParam.paramSeqId;
				returnData.GroupType = argParam.paramGroupType;
				returnData.LocationName = argParam.paramLocationName;
				returnData.SubLocationName = argParam.paramSubLocationName;
				
				arrReturnData.push(returnData);
			}

			return arrReturnData
        } catch ( e ) {
            RuleOutputToUI = { Status : 'Error', Message : "Js Logic Error : " + e.message };
            return;
        }
    };

    // Member 체크 후 Member 생성, Measure Group 입력하는 함수
    //var fn_ExecMemberMeasure = function(o9Params, params){
	var fn_ExecMemberMeasure = function(rowData, params){
        try {            
            const commonLib = require('o9.NSCM.commonLib');
            const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
            const vdUtil = new commonLib.VdUtil();

            vdCommon.setLogLevel("Debug");
            vdCommon.programStart();
            //vdCommon.printParams(o9Params);

            vdCommon.printStep("######################### Member 체크 후 Member 생성, Measure Group 입력하는 함수 --> Start");

            // 파라미터 가져오기
            let parsedParams = rowData; //JSON.parse(o9Params);

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
			
			//EW에서는 이미 Validation을 선행 수행하므로 add에서 한번에 저장 처리
			 let fbStartdate = parsedParams.fbStartdate;
			 let fbEnddate = parsedParams.fbEnddate;
			 let fbReason = parsedParams.fbReason;
			 let fbProdQty = parsedParams.fbProdQty ? parsedParams.fbProdQty : 0;
			 let fbAheadLimit = parsedParams.fbAheadLimit;
			 //

            vdCommon.printStep("######################### Member 생성 --> Start");
            // vdCommon.debug(" 함수 생성  호출 ");
            // member 체크 후 생성 (Group ID)
            if ( !vdCommon.existMember('[Group].[Group ID]', params.paramGroupId) ) {
                vdCommon.createDimension(['[Group].[Group ID]','[Group].[Group Name]','[Group].[Group Type]'], [params.paramGroupId, params.paramGroupId, params.paramGroupType]);
            }

            // member 체크 후 생성 (Sequence ID)
            if ( !vdCommon.existMember('[Sequence].[Sequence]', params.paramSeqId) ) {
                vdCommon.createMember('[Sequence].[Sequence]', params.paramSeqId);
            }
            vdCommon.printStep("######################### Member 생성 --> End");
            // From Site Name + To Site Name + Product Group + Definition + Project + MKT Name + INch + Year + Item 의 조합
            let vDesc = "";
            // From/to Site Desc에 추가 2025.02.25 문지윤P 요청
            if ( fbLocation !== "All" ) vDesc += params.paramLocationName + " ";                // From Site name
            if ( fbSubLocation !== "All" ) vDesc += params.paramSubLocationName  + " ";         // To Site name
            // if ( fbLocation !== "All" ) vDesc += fbLocation + " ";                           // From Site Code
            // if ( fbSubLocation !== "All" ) vDesc += fbSubLocation  + " ";                    // To Site Code
            if ( fbProductGroup !== "All" ) vDesc += fbProductGroup + " ";
            if ( fbDefinition !== "All" ) vDesc += fbDefinition + " ";
            if ( fbProject !== "All" ) vDesc += fbProject + " ";
            if ( fbMKTName !== "All" ) vDesc += fbMKTName + " ";
            if ( fbInch !== "All" ) vDesc += fbInch + " ";
            if ( fbYear !== "All" ) vDesc += fbYear + " ";
            if ( fbItem !== "All" ) vDesc += fbItem;
            // 마지막 공백 제거
            vDesc = vDesc.trim();
            vdCommon.printStep("######################### Measure 생성 --> Start");
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
                            'Measure.[Const Grp_Enddate]            = "' + fbEnddate + '";', 	//null;',
                            'Measure.[Const Grp_Startdate]          = "' + fbStartdate + '";', 	//null;',
                            'Measure.[Const Grp_Need Check]         = null;',
                            'Measure.[Const Grp_Reason]             = "' + fbReason + '";', 	//null;',
                            'Measure.[Const Grp_Build Ahead]        = null;',
                            'Measure.[Const Grp_Prod Qty]           = ' + fbProdQty + ';', 		//0;',
							'Measure.[Const Grp_Build Ahead Limit]  = ' + fbAheadLimit + ';', 		//0;',
                            'Measure.[Const Grp_Update Time]        = dateadd(Now(),9,"hour");',
                            'Measure.[Const Grp_Updated By]         = CurrentUser().[User Name];'
                            ];
                vdCommon.createMeasure(dimension, ['Measure.[Const Grp_From Site]         = "' + fbLocation + '";']);
                vdCommon.updateMeasure(dimension,  measure);
            } else {
                RuleOutputToUI = { Status : 'Error', Message : "This Data has already been registered." };
                return;
            }
            vdCommon.printStep("######################### Measure 생성 --> End");
            vdCommon.printStep("######################### Member 체크 후 Member 생성, Measure Group 입력하는 함수 --> End");
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
            // let fbVersion = parsedParams.fbVersion;
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
                let rtnNeedCheck = rtnMeasureValue.cs.row(0).cell(rtnMeasureValue.cs.measureColumnIndex("Const Grp_Need Check"));
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
                // From/to Site Desc에 추가 2025.02.25 문지윤P 요청
                if ( fbLocation !== "All" ) vDesc += fbLocationName + " ";              // From Site Name
                if ( fbSubLocation !== "All" ) vDesc += fbSubLocationName  + " ";       // To Site Name
                // if ( fbLocation !== "All" ) vDesc += fbLocation + " ";               // From Site Code
                // if ( fbSubLocation !== "All" ) vDesc += fbSubLocation  + " ";        // To Site Code
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


		/*  기존 방식 대신 별도로 생성
           //Validation 호출 (PY_UI_ProductionConstValid)
            var execQuery = 'EXEC plugin instance [PY_UI_ProductionConstValid] ' +
                            'for measures {[Const Grp_From Site]} ' +
                            'using scope ( &CWVUI ) ' +
                            // 'using arguments {(ExecutionMode, "MediumWeight"), (MaxSliceTableCells, 200000000), (MaxConcurrency, 1), ([Param.o9_sys_log_level], "DEBUG") };  ';
                            'using arguments {(ExecutionMode, "MediumWeight"), ("IncludeNullRows", "False") , (MaxSliceTableCells, 200000000), (MaxConcurrency, 1), ([Param.o9_sys_log_level], "DEBUG") }; ';
            vdCommon.debug("execQuery: " + JSON.stringify(execQuery));
            vdCommon.executeQuery("fn_validation : PY_UI_ProductionConstValid Run", execQuery);
			vdCommon.programEnd();
		*/
			//[START]임시 개발형태로 추후 검증 로직이 맞는지 확인이 필요함.
			
			let parseTupleSize = parsedParams.fbConstGrpTuple.length;
            let tupleList = parsedParams.fbConstGrpTuple;
			
			/*
			var fbGroupID = parsedParams.fbGroupID;
            var fbSeq = parsedParams.fbSeq;
			
			var fbLocation = parsedParams.fbLocation;
            var fbSubLocation = parsedParams.fbSubLocation;
            var fbProductGroup = parsedParams.fbProductGroup;
            var fbDefinition = parsedParams.fbDefinition;
            var fbProject = parsedParams.fbProject;
            var fbMKTName = parsedParams.fbMKTName;
            var fbInch = parsedParams.fbInch;
            var fbYear = parsedParams.fbYear;
			var fbItem = parsedParams.fbItem;
			
			var fbStartdate = parsedParams.fbStartdate;
			var fbEnddate = parsedParams.fbEnddate;
			*/
			
			var fbGroupID = "";
            var fbSeq = "";
			var fbLocation = "";
            var fbSubLocation = "";
            var fbProductGroup = "";
            var fbDefinition  = "";
            var fbProject = "";
            var fbMKTName = "";
            var fbInch = "";
            var fbYear = "";
			var fbItem = "";
			
			var fbStartdate = "";
			var fbEnddate = "";
			
			var fbRow = "";
			
			let returnData = {};
			//배열로..
			for (let i=0; i < parseTupleSize; i++) {
                const row = tupleList[i];
				
		
				fbLocation = row.fbLocation;
				fbSubLocation = row.fbSubLocation;
				fbProductGroup = row.fbProductGroup;
				fbDefinition = row.fbDefinition;
				fbProject = row.fbProject;
				fbMKTName = row.fbMKTName;
				fbInch = row.fbInch;
				fbYear = row.fbYear;
				fbItem = row.fbItem;
				fbStartdate = row.fbStartdate;
				fbEnddate = row.fbEnddate;
				
				if(row.fbGroupID)
					fbGroupID = row.fbGroupID;
				
				if(row.fbGroupID)
					fbSeq = row.fbSeq;
				
				if(row.fbRow)
					fbRow = row.fbRow;
				
				
				if(fbStartdate == "" || fbEnddate == "") continue;
				
			
				let measureFilter =    'Measure.[Const Grp_From Site] == "'+fbLocation+'"'
											+' && Measure.[Const Grp_To Site] == "'+fbSubLocation+'"'
											+' && Measure.[Const Grp_Product Group] == "'+fbProductGroup+'"'
											+' && Measure.[Const Grp_Definition] == "'+fbDefinition+'"'
											+' && Measure.[Const Grp_Project] == "'+fbProject+'"'
											+' && Measure.[Const Grp_Mkt Name] == "'+fbMKTName+'"'
											+' && Measure.[Const Grp_Inch] == "'+fbInch+'"'
											+' && Measure.[Const Grp_Year] == "'+fbYear+'"'
											+' && Measure.[Const Grp_Item] == "'+fbItem+'"'
											;
				let where = 'where {'+measureFilter+'}' ;
				vdCommon.debug(" strWhere : "+where);

				
				//Select (&Sequence * [Group].[Group ID] ) on row,({Measure.[Const Grp_Startdate],Measure.[Const Grp_Enddate],Measure.[Const Grp_Need Check],Measure.[Const Grp_Refer Time]}) on column where { &CWVUI };
				let rtnMeasureValue = vdCommon.selectList(["&CWVUI","[Sequence].[Sequence]","[Group].[Group ID]"]
																, ["Measure.[Const Grp_Startdate], Measure.[Const Grp_Enddate]"]
																, where, "", "");  // where, orderby, limit

				fbStartdate = parseInt(fbStartdate, 10);
				fbEnddate = parseInt(fbEnddate, 10);
				
				let vGroupID = "";
				let vSeq = "";
				let vStartdate = "";
				let vEnddate = "";
				for (let j=0; j<rtnMeasureValue.cs.rowCount; j++){
					 
					vGroupID 	= rtnMeasureValue.cs.row(j).cell(rtnMeasureValue.cs.memberColumnIndex("Group", "Group ID")).Name
					vSeq 		= rtnMeasureValue.cs.row(j).cell(rtnMeasureValue.cs.memberColumnIndex("Sequence", "Sequence")).Name
					vStartdate	= rtnMeasureValue.cs.row(j).cell(rtnMeasureValue.cs.measureColumnIndex("Const Grp_Startdate"));
					vEnddate 	= rtnMeasureValue.cs.row(j).cell(rtnMeasureValue.cs.measureColumnIndex("Const Grp_Enddate"));
					
					if(vGroupID == fbGroupID && vSeq == fbSeq) continue;  //자기자신 제외
					
					vStartdate = parseInt(vStartdate, 10);
					vEnddate = parseInt(vEnddate, 10);
				
					if( fbStartdate <= vEnddate && fbEnddate >= vStartdate){ //겹치는 구간이 있는 경우
						
						let sTemp = "";
						if (fbGroupID == "") {
							sTemp = "[ New add row : " + fbRow + " ]";
						}else{
							sTemp = "[ Group ID :"+fbGroupID+" / Sequence : "+fbSeq+" ]";
						}
					
						//returnData.msg = "validation Check!! \n [ Group ID :"+vGroupID+" / Sequence : "+vSeq+" ] \n [ Group ID :"+fbGroupID+" / Sequence : "+fbSeq+" ]";
						returnData.msg = "validation Check!! \n [ Group ID :"+vGroupID+" / Sequence : "+vSeq+" ] \n " + sTemp;
						returnData.flag = false;
						returnData.row = fbRow;
						return returnData;
					}
				}
			}
			
			returnData.msg = "";
			returnData.flag = true;
			vdCommon.programEnd();
			return returnData;
			
			//[END]임시 개발형태로 추후 검증 로직이 맞는지 확인이 필요함.
			
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
            vdCommon.debug("fn_Apply=======>");
            vdCommon.printParams(o9Params);
            // 파라미터 가져오기
            let parsedParams = JSON.parse(o9Params);
			
			/*
            let rtnValid = fn_ValidationApply(o9Params);
            if ( !rtnValid.flag ){
                RuleOutputToUI = { Status : 'Error', Message : rtnValid.msg };
                return;
            }*/

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
            // vdCommon.debug("########### Measure 결과값 구하기 >>> 1");
            // Measure 의 Location 을 구한다
            let rtnMeasureValue = vdCommon.selectList(["&CWVUI","&Sequence"+vdUtil.fn_filterStr(fbSequence_filter),"[Group].[Group ID]"+vdUtil.fn_filterStr(fbGroupId_filter)]
            // let rtnMeasureValue = vdCommon.selectList(["&CWVUI","[Sequence].[Sequence].["+fbSequence_filter+"]","[Group].[Group ID].["+fbGroupId_filter+"]"]
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
            for (let j=0; j<rtnMeasureValue.cs.rowCount; j++){
               
                rtnLocation.push(rtnMeasureValue.cs.row(j).cell(rtnMeasureValue.cs.measureColumnIndex("Const Grp_From Site")));
                vSubLocation = rtnMeasureValue.cs.row(j).cell(rtnMeasureValue.cs.measureColumnIndex("Const Grp_To Site"));
                vProductGroup = rtnMeasureValue.cs.row(j).cell(rtnMeasureValue.cs.measureColumnIndex("Const Grp_Product Group")).replace(/\^/g,'","');
                vDefinition = rtnMeasureValue.cs.row(j).cell(rtnMeasureValue.cs.measureColumnIndex("Const Grp_Definition"));
                vProject = rtnMeasureValue.cs.row(j).cell(rtnMeasureValue.cs.measureColumnIndex("Const Grp_Project"));
                vMktName = rtnMeasureValue.cs.row(j).cell(rtnMeasureValue.cs.measureColumnIndex("Const Grp_Mkt Name"));
                vInch = rtnMeasureValue.cs.row(j).cell(rtnMeasureValue.cs.measureColumnIndex("Const Grp_Inch"));
                vYear = rtnMeasureValue.cs.row(j).cell(rtnMeasureValue.cs.measureColumnIndex("Const Grp_Year"));
                vItem = rtnMeasureValue.cs.row(j).cell(rtnMeasureValue.cs.measureColumnIndex("Const Grp_Item"));

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
            // var execQuery = 'EXEC plugin instance [PY_UI_ProductionConstApply] ' +
            var execQuery = 'EXEC plugin instance [PY_UI_ProductionConstApply] ' +     // 테스트중 2025.01.03
                            'for measures {[Const Grp Detail_From Site]} ' +
                            'using scope ( &CWVUI * [Group].[Group ID]' + vdUtil.fn_filterStr(fbGroupId_filter) + ' * ' +
                                         '[Location].[Location]' + vdUtil.fn_filterStr(rtnLocation) + ' * ' +
                                         '&SETItem '+ ') '+                                                                
                            'using arguments {(ExecutionMode, "MediumWeight"), (pDetailLogFlag, "N"), (MaxSliceTableCells, 200000000), (MaxConcurrency, 1), ([Param.o9_sys_log_level], "DEBUG") }; ';
                            // MediumWeight => LightWeight 변경 2024.12.30 , MediumWeight 변경 2025.01.02
            
            vdCommon.debug("execQuery: " + JSON.stringify(execQuery));
            vdCommon.executeQuery("PY Apply Run", execQuery);

            let measure = ['Measure.[Const Grp Detail Update Time] = dateadd(Now(),9,"hour");', 
                           'Measure.[Const Grp Detail Update User] = CurrentUser().[User Name];'];

            /* Update일자, 사용자 정보입력 */
            // Measure Group 존재하는지 체크후 생성 및 수정
			/* EW에서 별도 처리
            if ( !vdCommon.existMeasure(["&CWVUI"], ['Measure.[Const Grp Detail_From Site]'], "") ) {
                vdCommon.createMeasure(["&CWVUI"], measure);
            } else {                
                vdCommon.updateMeasure(["&CWVUI"],  measure);
            }
			*/

            vdCommon.programEnd();
        } catch ( e ) {
            RuleOutputToUI = { Status : 'Error', Message : "Js Logic Error : " + e.message };
            return;
        }
    };
	var fn_loadFunction = function(o9Params){
		let returnData = {};
		let obj = this;
		const functionmap = {
			 "fn_locationCombo"       : fn_locationCombo
			,"fn_subLocationCombo"    : fn_subLocationCombo
			,"fn_productGroupCombo"   : fn_productGroupCombo
			,"fn_definitionCombo"     : fn_definitionCombo
			,"fn_projectCombo"        : fn_projectCombo
			,"fn_mktNameCombo"        : fn_mktNameCombo
			,"fn_inchCombo"           : fn_inchCombo
			,"fn_yearCombo"           : fn_yearCombo
			,"fn_itemCombo"           : fn_itemCombo
			
			,"fn_Add"			      : fn_Add
			,"fn_Apply" 			  : fn_Apply
			,"fn_Delete"			  : fn_Delete
			,"fn_Copy"			      : fn_Copy
			,"fn_validation"		  : fn_validation
		};
		try {            
            const commonLib = require('o9.NSCM.commonLib');
            const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
    
            vdCommon.programStart();
            vdCommon.debug("fn_loadFunction=======>");
            vdCommon.printParams(o9Params);
            
            var parsedParams = JSON.parse(o9Params);
			var fbFuncName = parsedParams.fbFuncName;
			delete parsedParams.fbFuncName;
            //fbFuncName = "fn_locationCombo";
            //const {fbFuncName, ...newPrams } = parsedParams;

		//	if(typeof this[fbFuncName] === "function"){
				var comboList = functionmap[fbFuncName](JSON.stringify(parsedParams));
				//var comboList = fn_locationCombo(JSON.stringify(parsedParams));
				
				vdCommon.programEnd();
				return comboList;
		//	}else{
		//		returnData.msg = "미등록 함수";
		//		return returnData;
		//	}
        } catch ( e ) {
            RuleOutputToUI = { Status : 'Error', Message : "Js Logic Error : " + e.message };
            return;
        }
	};
	var fn_makeCombo  = function(result, param) {
		var comboList = [];
		var validHashMap = {};
		var name = "";
		var displayName = "";
		var _name = "";
		var _displayName = "";
		var _displayAlias = "";
		var condition = "";
		var conditionValue = "";

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

					// 25.2.25 : DisplayAlias 을 우선으로 반영한다.
					if ( _displayAlias != null && _displayAlias != "" ) {
						_displayName = _displayAlias
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
				
	

				if ( param["ConditionName"] != undefined ) {
					var arrConditionName = param["ConditionName"].split("^");
					var arrConditionAttbName = param["ConditionAttbName"].split("^");
					var arrConditionAttbValue = [];
					condition = "";
					for(var j = 0; j < arrConditionName.length; j++){
						conditionValue = result.cs.row(i).cell(result.cs.memberColumnIndex(arrConditionName[j], arrConditionAttbName[j])).Name;
						arrConditionAttbValue.push(conditionValue);
						
						if(condition != "") condition += "^";
						condition += conditionValue;
					}
					
					if ( validHashMap[condition+"^"+name] == undefined ) {
						var oValue = {};
						
						for(var k = 0; k < arrConditionAttbName.length; k++){
							var sAttbName = arrConditionAttbName[k];
							sAttbName = sAttbName.replace(/\s+/g, '');	//공백 제거
							oValue[sAttbName] = arrConditionAttbValue[k];
						}
						oValue.Name = name;
						oValue.DisplayName = displayName;
						comboList.push(oValue);
						validHashMap[condition+"^"+name] = name;
					}
				}else{
					if ( validHashMap[name] == undefined ) {
						comboList.push({ Name : name, DisplayName : displayName});
						validHashMap[name] = name;
					}
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
			comboList.unshift({ Name : "All", DisplayName : "All"});
		}

		return comboList;
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
        ,fn_loadFunction : fn_loadFunction
		,fn_makeCombo : fn_makeCombo
    };
});



/* 
 - EWProductionConst / Actionbutton
 - o9.NSCM.JSEWProductionConst : o9.NSCM.JSEWProductionConst
 - Function Name : Function Name
 - parsedParams : 
	fbFuncName
	fbLocation
	fbProductGroup
	fbDefinition
	fbProject
	fbMKTName
	fbInch
	fbYear
	fbSubLocation
	fbConstGrpTuple
	fbItem
	fbRefTime
	fbGroupID
	fbSeq
	fbStartdate
	fbEnddate
	fbRow
	fbProdQty
	fbReason
	fbGroupId
	fbSequence
*/
/*-------------------------------------------------------------------------------------------------*/
/* 2025.03.13 o9.NSCM.JSProductionConst copy                                                       */
/*-------------------------------------------------------------------------------------------------*/
/* 2025.03.21 update by dmin.oh                                                                    */
/* 2025.04.16 update by dmin.oh                                                                    */
/* 2025.08.21 update Const Grp_Build Ahead Limit                                                   */
/*-------------------------------------------------------------------------------------------------*/