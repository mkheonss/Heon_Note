define('o9.JSConstraintGroupComboList', ['o9/data/query', 'o9/data/cellset', 'o9.NSCM.commonLib'], function(){

    const programName = "o9.JSConstraintGroupComboList";
    const queryModule = require('o9/data/query');
    const cellsetModule = require('o9/data/cellset');
    const commonLib = require('o9.NSCM.commonLib');
    const vdCommon = new commonLib.VdCommon(programName);

    vdCommon.setLogLevel("Debug");

    const allCheckN = "N";
    const allCheckY = "Y";
    let dimParams = {};

    // 콤보 생성
    function fn_comboMake(query, dimParams) {
        let selectResult = cellsetModule.createCellSet(queryModule.select(query));
        let selectResultCount = selectResult.rowCount;
        vdCommon.debug("fn_comboMake > selectResult : " + JSON.stringify(selectResult));
        vdCommon.debug("fn_comboMake > selectResultCount : " + selectResultCount);

        let comboList = [];
        let validHashMap = new Map();
        let allCheck = dimParams.allCheck;

        if (allCheck === "Y") {
            comboList.push({ Name: "ALL", DisplayName: "ALL" });
        }

        for (let i = 0; i < selectResultCount; i++) {
            const comboData = selectResult.row(i).cell(selectResult.memberColumnIndex(
                dimParams.levelKey, dimParams.levelValue)).Name;

            if (!validHashMap.has(comboData)) {
                comboList.push({ Name: comboData, DisplayName: comboData });
                validHashMap.set(comboData, comboData);
            }
        }
        vdCommon.debug("fn_comboMake > ComboData : " + JSON.stringify(validHashMap));

        return comboList;
    }
    // 콤보리스트에 ALL 추가
    function GetToSiteAllSelectList(o9Params){
        vdCommon.programStart();
        vdCommon.printStep(">>>>>>>>>>>  Site To Combo List");
        vdCommon.printParams(o9Params);

        // 파라메타 가져오기
        let parsedParams = JSON.parse(o9Params);

        // FieldBind 변수 세팅하기
        let fbVersion = parsedParams.fbVersion;
        let fbSiteFrom = parsedParams.fbSiteFrom;

        dimParams.levelKey = "BOD";
        dimParams.levelValue = "To Site ID";
        dimParams.allCheck = allCheckY;

        let query = `
                    select (
                        [BOD].[To Site ID]
                    ) on row where {
                          Version.[Version Name].filter(#.Name == "${fbVersion}")
                        , [BOD].[From Site ID].filter(#.Name == "${fbSiteFrom}")
                     // , (Measure.[BOD Lane_EFF Enddate]>now() && Measure.[BOD Lane_EFF Startdate]<Now())
                    };
        `;
        vdCommon.debug("GetToSiteAllSelectList > select query : " + query);
        let comboList = fn_comboMake(query, dimParams);
        vdCommon.programEnd();

        return comboList;
    }
    function GetProductGroupList(o9Params){
        vdCommon.programStart();
        vdCommon.printStep(">>>>>>>>>>>  Product Group Combo List");
        vdCommon.printParams(o9Params);

        // 파라메타 가져오기
        let parsedParams = JSON.parse(o9Params);

        // FieldBind 변수 세팅하기
        let fbVersion = parsedParams.fbVersion;
        let fbSiteFrom = parsedParams.fbSiteFrom;

        dimParams.levelKey = "Item";
        dimParams.levelValue = "Product Group";
        dimParams.allCheck = allCheckY;

        let query = `
                    select (
                        [Item].[Product Group]
                    ) on row where {
                          Version.[Version Name].filter(#.Name == "${fbVersion}")
                     // ,~isnull(Measure.[BOD Lane Item_EFF Enddate])
                    };
        `;
        vdCommon.debug("GetProductGroupList > select query : " + query);
        let comboList = fn_comboMake(query, dimParams);
        vdCommon.programEnd();

        return comboList;
    }
    function GetDefinitionSelectList(o9Params){

        vdCommon.programStart();
        vdCommon.printStep(">>>>>>>>>>>  Definition Combo List");
        vdCommon.printParams(o9Params);

        // 파라메타 가져오기
        let parsedParams = JSON.parse(o9Params);

        // FieldBind 변수 세팅하기
        let fbVersion = parsedParams.fbVersion;
        let fbSiteFrom = parsedParams.fbSiteFrom;
        let fbSiteTo = parsedParams.fbSiteTo;
        let fbProductGroup = parsedParams.fbProductGroup;

        dimParams.levelKey = "Item";
        dimParams.levelValue = "A8";
        dimParams.allCheck = allCheckY;

        let query = `
                    select (
                        [Item].[A8]
                    ) on row where {
                          Version.[Version Name].filter(#.Name == "${fbVersion}")
                        , [BOD].[From Site ID].filter(#.Name == "${fbSiteFrom}")
                     // , [BOD].[To Site ID].filter(#.Name == "${fbSiteTo}")
                     // , [Item].[Product Group].filter(#.Name == "${fbProductGroup}")
                     // , ~isnull(Measure.[BOD Lane Item_EFF Enddate])
                    };
        `;
        vdCommon.debug("GetDefinitionSelectList > select query : " + query);
        let comboList = fn_comboMake(query, dimParams);
        vdCommon.programEnd();

        return comboList;
    }
    function GetProjectSelectList(o9Params){

        vdCommon.programStart();
        vdCommon.printStep(">>>>>>>>>>>  Project Combo List");
        vdCommon.printParams(o9Params);

        // 파라메타 가져오기
        let parsedParams = JSON.parse(o9Params);

        // FieldBind 변수 세팅하기
        let fbVersion = parsedParams.fbVersion;
        let fbSiteFrom = parsedParams.fbSiteFrom;
        let fbSiteTo = parsedParams.fbSiteTo;
        let fbProductGroup = parsedParams.fbProductGroup;

        dimParams.levelKey = "Item";
        dimParams.levelValue = "Project";
        dimParams.allCheck = allCheckY;

        let query = `
                    select (
                        [Item].[Project]
                    ) on row where {
                          Version.[Version Name].filter(#.Name == "${fbVersion}")
                        , [BOD].[From Site ID].filter(#.Name == "${fbSiteFrom}")
                     // , [BOD].[To Site ID].filter(#.Name == "${fbSiteTo}")
                     // , [Item].[Product Group].filter(#.Name == "${fbProductGroup}")
                     // , ~isnull(Measure.[BOD Lane Item_EFF Enddate])
                    };
        `;
        vdCommon.debug("GetProjectSelectList > select query : " + query);
        let comboList = fn_comboMake(query, dimParams);
        vdCommon.programEnd();

        return comboList;
    }
    function GetMKTNameSelectList(o9Params){
        vdCommon.programStart();
        vdCommon.printStep(">>>>>>>>>>>  MKT Name Combo List");
        vdCommon.printParams(o9Params);

        // 파라메타 가져오기
        let parsedParams = JSON.parse(o9Params);

        // FieldBind 변수 세팅하기
        let fbVersion = parsedParams.fbVersion;
        let fbSiteFrom = parsedParams.fbSiteFrom;
        let fbSiteTo = parsedParams.fbSiteTo;
        let fbProductGroup = parsedParams.fbProductGroup;

        dimParams.levelKey = "Item";
        dimParams.levelValue = "A15";
        dimParams.allCheck = allCheckY;

        let query = `
                    select (
                        [Item].[A15]
                    ) on row where {
                          Version.[Version Name].filter(#.Name == "${fbVersion}")
                        , [BOD].[From Site ID].filter(#.Name == "${fbSiteFrom}")
                     // , [BOD].[To Site ID].filter(#.Name == "${fbSiteTo}")
                     // , [Item].[Product Group].filter(#.Name == "${fbProductGroup}")
                     // , ~isnull(Measure.[BOD Lane Item_EFF Enddate])
                    };
        `;
        vdCommon.debug("GetMKTNameSelectList > select query : " + query);
        let comboList = fn_comboMake(query, dimParams);
        vdCommon.programEnd();

        return comboList;
    }
    function GetInchSelectList(o9Params){
        vdCommon.programStart();
        vdCommon.printStep(">>>>>>>>>>>  Inch Combo List");
        vdCommon.printParams(o9Params);

        // 파라메타 가져오기
        let parsedParams = JSON.parse(o9Params);

        // FieldBind 변수 세팅하기
        let fbVersion = parsedParams.fbVersion;
        let fbSiteFrom = parsedParams.fbSiteFrom;
        let fbSiteTo = parsedParams.fbSiteTo;
        let fbProductGroup = parsedParams.fbProductGroup;

        dimParams.levelKey = "Item";
        dimParams.levelValue = "A2";
        dimParams.allCheck = allCheckY;

        let query = `
                    select (
                        [Item].[A2]
                    ) on row where {
                          Version.[Version Name].filter(#.Name == "${fbVersion}")
                        , [BOD].[From Site ID].filter(#.Name == "${fbSiteFrom}")
                     // , [BOD].[To Site ID].filter(#.Name == "${fbSiteTo}")
                     // , [Item].[Product Group].filter(#.Name == "${fbProductGroup}")
                     // , ~isnull(Measure.[BOD Lane Item_EFF Enddate])
                    };
        `;
        vdCommon.debug("GetInchSelectList > select query : " + query);
        let comboList = fn_comboMake(query, dimParams);
        vdCommon.programEnd();

        return comboList;
    }
    function GetYearSelectList(o9Params){
        vdCommon.programStart();
        vdCommon.printStep(">>>>>>>>>>>  Year Combo List");
        vdCommon.printParams(o9Params);

        // 파라메타 가져오기
        let parsedParams = JSON.parse(o9Params);

        // FieldBind 변수 세팅하기
        let fbVersion = parsedParams.fbVersion;
        let fbSiteFrom = parsedParams.fbSiteFrom;
        let fbSiteTo = parsedParams.fbSiteTo;
        let fbProductGroup = parsedParams.fbProductGroup;

        dimParams.levelKey = "Item";
        dimParams.levelValue = "A13";
        dimParams.allCheck = allCheckY;

        let query = `
                    select (
                        [Item].[A13]
                    ) on row where {
                          Version.[Version Name].filter(#.Name == "${fbVersion}")
                        , [BOD].[From Site ID].filter(#.Name == "${fbSiteFrom}")
                     // , [BOD].[To Site ID].filter(#.Name == "${fbSiteTo}")
                     // , [Item].[Product Group].filter(#.Name == "${fbProductGroup}")
                     // , ~isnull(Measure.[BOD Lane Item_EFF Enddate])
                    };
        `;
        vdCommon.debug("GetYearSelectList > select query : " + query);
        let comboList = fn_comboMake(query, dimParams);
        vdCommon.programEnd();

        return comboList;
    }
    function GetItemSelectList(o9Params){
        vdCommon.programStart();
        vdCommon.printStep(">>>>>>>>>>>  Item Combo List");
        vdCommon.printParams(o9Params);

        // 파라메타 가져오기
        let parsedParams = JSON.parse(o9Params);

        // FieldBind 변수 세팅하기
        let fbVersion = parsedParams.fbVersion;
        let fbSiteFrom = parsedParams.fbSiteFrom;
        let fbSiteTo = parsedParams.fbSiteTo;
        let fbProductGroup = parsedParams.fbProductGroup;

        dimParams.levelKey = "Item";
        dimParams.levelValue = "Item";
        dimParams.allCheck = allCheckY;

        let query = `
                    select (
                        [Item].[Item]
                    ) on row where {
                          Version.[Version Name].filter(#.Name == "${fbVersion}")
                        , [BOD].[From Site ID].filter(#.Name == "${fbSiteFrom}")
                     // , [BOD].[To Site ID].filter(#.Name == "${fbSiteTo}")
                     // , [Item].[Product Group].filter(#.Name == "${fbProductGroup}")
                     // , ~isnull(Measure.[BOD Lane Item_EFF Enddate])
                    } limit 20 ;
        `;
        vdCommon.debug("GetItemSelectList > select query : " + query);
        let comboList = fn_comboMake(query, dimParams);
        vdCommon.programEnd();

        return comboList;
    }
    return{
        GetToSiteAllSelectList  : GetToSiteAllSelectList,
        GetDefinitionSelectList : GetDefinitionSelectList,
        GetProjectSelectList    : GetProjectSelectList,
        GetMKTNameSelectList    : GetMKTNameSelectList,
        GetInchSelectList       : GetInchSelectList,
        GetYearSelectList		: GetYearSelectList,
        GetItemSelectList		: GetItemSelectList,
        GetProductGroupList		: GetProductGroupList
    };
});