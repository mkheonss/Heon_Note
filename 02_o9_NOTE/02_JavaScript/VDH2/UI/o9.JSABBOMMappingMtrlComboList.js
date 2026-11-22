define('o9.JSABBOMMappingMtrlComboList',['o9/data/query', 'o9/data/cellset', 'o9.NSCM.commonLib'], function () {


    const programName = 'o9.JSABBOMMappingMtrlComboList';
    const queryModule = require('o9/data/query');
    const cellsetModule = require('o9/data/cellset');
    const commonLib = require('o9.NSCM.commonLib');
    const vdCommon = new commonLib.VdCommon(programName);

    vdCommon.setLogLevel('Debug');

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
    function GetMSL2AllList(o9Params){
        vdCommon.programStart();
        vdCommon.printStep(">>>>>>>>>>>  Site To Combo List");
        vdCommon.printParams(o9Params);

        // 파라메타 가져오기
        let parsedParams = JSON.parse(o9Params);

        // FieldBind 변수 세팅하기
        let fbVersion = parsedParams.fbVersion;
        let fbMSL1 = parsedParams.fbMSL1;

        dimParams.levelKey = "Item Material";
        dimParams.levelValue = "MSL2";
        dimParams.allCheck = allCheckY;

        let query = `
                    select (
                        [Item Material].[MSL2]
                    ) on row where {
                          [Version].[Version Name].filter(#.Name == "${fbVersion}")
                        , [Item Material].[MSL1].filter(#.Name == "${fbMSL1}")
                    };
        `;
        vdCommon.debug("GetMSL2AllList > select query : " + query);
        let comboList = fn_comboMake(query, dimParams);
        vdCommon.programEnd();

        return comboList;
    }


    function GetMSL3SelectList(o9Params) {
        vdCommon.programStart();
        vdCommon.printStep(">>>>>>>>>>>  Product Group Combo List");
        vdCommon.printParams(o9Params);

        // 파라메타 가져오기
        let parsedParams = JSON.parse(o9Params);

        // FieldBind 변수 세팅하기
        let fbVersion = parsedParams.fbVersion;
        let fbMSL1 = parsedParams.fbMSL1;
        let fbMSL2 = parsedParams.fbMSL2;


        dimParams.levelKey = "Item Material";
        dimParams.levelValue = "MSL3";
        dimParams.allCheck = allCheckY;

        let query = `
                    select (
                        [Item Material].[MSL3]
                    ) on row where {
                          Version.[Version Name].filter(#.Name == "${fbVersion}")
                          , [Item Material].[MSL1].filter(#.Name == "${fbMSL1}")
                          , [Item Material].[MSL2].filter(#.Name == "${fbMSL2}")
                    };
        `;
        vdCommon.debug("GetMSL3SelectList > select query : " + query);
        let comboList = fn_comboMake(query, dimParams);
        vdCommon.programEnd();

        return comboList;
    }

    function GetItemSelect (o9Params) {
        vdCommon.programStart();
        vdCommon.printStep(">>>>>>>>>>>  Product Group Combo List");
        vdCommon.printParams(o9Params);

        // 파라메타 가져오기
        let parsedParams = JSON.parse(o9Params);

        // FieldBind 변수 세팅하기
        let fbVersion = parsedParams.fbVersion;
        let fbMSL1 = parsedParams.fbMSL1;
        let fbMSL2 = parsedParams.fbMSL2;
        let fbMSL3 = parsedParams.fbMSL3;


        dimParams.levelKey = "Item Material";
        dimParams.levelValue = "Item Material";
        dimParams.allCheck = allCheckY;

        let query = `
                    select (
                        [Item Material].[Item Material]
                    ) on row where {
                          Version.[Version Name].filter(#.Name == "${fbVersion}")
                          , [Item Material].[MSL1].filter(#.Name == "${fbMSL1}")
                          , [Item Material].[MSL2].filter(#.Name == "${fbMSL2}")
                          , [Item Material].[MSL3].filter(#.Name == "${fbMSL3}")
                    };
        `;
        vdCommon.debug("GetMSL3SelectList > select query : " + query);
        let comboList = fn_comboMake(query, dimParams);
        vdCommon.programEnd();

        return comboList;
    }
    return{
        GetMSL2AllList : GetMSL2AllList,
        GetMSL3SelectList : GetMSL3SelectList,
        GetItemSelect : GetItemSelect

    };

});