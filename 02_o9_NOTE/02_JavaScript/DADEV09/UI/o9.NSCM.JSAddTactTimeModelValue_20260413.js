define('o9.NSCM.JSAddTactTimeModelValue', ['o9/data/query', 'o9/data/cellset', 'o9.NSCM.commonLib'], function () {
    const programName = "o9.NSCM.JSAddTactTimeModelValue";
    const commonLib = require('o9.NSCM.commonLib');
    const queryModule = require('o9/data/query');
    const cellsetModule = require('o9/data/cellset');
    nscmCommon = new commonLib.NSCMCommon(programName);
    
    const addBtn = function (props) {
        try {
            const queryModule = require('o9/data/query');
            const cellsetModule = require('o9/data/cellset');

            props = JSON.parse(props);

            const queryForUIData = `Select (&CWV_MP * [Sub Location].[Sub Location].[${props.fbFrom_Site}]  * [Item].[Item].[${props.fbItem}]*[Line].[Line].[${props.fbLineName}]) on row,({Measure.[Tact Time Model_Target Tact Time], Measure.[Tact Time Model_Priority]}) on column;`;

            const uiData = cellsetModule.createCellSet(queryModule.select(queryForUIData));

            if (uiData.rowCount > 0) {
                RuleOutputToUI = {
                    Status: 'Error',
                    Message: 'Duplicate data found'
                };
                return;
            }
             //--------Check Validation ---------
             var TargetTactTime=props.fbTargetTactTime;
              if ( TargetTactTime<=0 || TargetTactTime>=10000) {
                RuleOutputToUI = {
                    Status: 'Error',
                    Message: 'Target Tact time shall be in greater than 0 and less than 10000'
                };
                return;
            }
             var Priority=props.fbPriority;
       
            if ( Priority<=0||Priority>=10000) {
                RuleOutputToUI = {
                    Status: 'Error',
                    Message: 'Priority should be in greater than 0 and less than 10000'
                };
                return;
            }
            
            //Item Check 2026.01.23
            if (props.fbItem == "NA") {
                RuleOutputToUI = {
                    Status: 'Error',
                    Message: 'Please select a valid From Site before choosing an Item.'
                };
                return;
            }            
            //--------------------------Add Command----------------------

            let addQuery = `
		cartesian scope: (&CWV_MP * [Sub Location].[Sub Location].Filter( #.Name == "${props.fbFrom_Site}")*[Item].[Item].Filter( #.Name == "${props.fbItem}")*[Line].[Line].Filter( #.Name == "${props.fbLineName}"));
                Measure.[Tact Time Model_Target Tact Time]="${props.fbTargetTactTime}";
		        Measure.[Tact Time Model_Priority]="${props.fbPriority}";

		end scope;
		`;

        queryModule.update(addQuery);

        } catch (error) {
            RuleOutputToUI = { Status: 'Error', Message: "Js Logic Error : " + error.message };
            return;
        }

    };
    
    var fn_ItemSiteMFASN_Asn = function (o9Params) {
        try {
            nscmUtil = new commonLib.NSCMUtil();
            nscmCommon.setLogLevel("Debug");
            nscmCommon.printParams(o9Params);
            let parsedParams = JSON.parse(o9Params);

            nscmCommon.debug("props" + JSON.stringify(parsedParams));            

            const queryForItemSiteMFASN_Asn = `select(&CWV_MP*[Sub Location]. [Sub Location].[${parsedParams.fbFrom_Site}]*[Item].[Item]) on row,({Measure.[Item Site MF ASN_Asn]}) on column where {Measure.[Item Site MF ASN_Asn]==1};`;
            Log.Info('---------queryForItemSiteMFASN_Asn------------' + JSON.stringify(queryForItemSiteMFASN_Asn));
            var comboList = [];

            let selectResult = nscmCommon.selectQueryList("[fn_ItemSiteMFASN_Asn]" ,queryForItemSiteMFASN_Asn );
            if(selectResult.cs.rowCount <= 0){
                comboList.push({ Name: "NA", DisplayName: "No Data" });
            }else{
                comboList = nscmCommon.fn_makeCombo(selectResult, {DimName : "Item", 
                                                                    DimAttbName : "Item", 
                                                                    Sort :"DisplayName", 
                                                                    existAll : false, 
                                                                    isDisplayNameWithCode : false});  
            }

            nscmCommon.debug("["+selectResult.cs.rowCount+"]["+ JSON.stringify(comboList)+"]");
            
            return comboList;


        } catch (e) {
            RuleOutputToUI = { Status: 'Error', Message: "Js Logic Error : " + e.message };
            return;
        }
    };    
    return {
        addBtn: addBtn
        ,fn_ItemSiteMFASN_Asn : fn_ItemSiteMFASN_Asn
    };
});