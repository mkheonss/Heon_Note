define('o9.NSCM.JSAbBomMapping_Add', ['o9/data/query', 'o9/data/cellset', 'o9.NSCM.commonLib'], function () {

    const programName = 'o9.NSCM.JSAbBomMapping_Add';
    const queryModule = require('o9/data/query');
    const cellsetModule = require('o9/data/cellset');
    const commonLib = require('o9.NSCM.commonLib');
    const vdCommon = new commonLib.VdCommon(programName);
    vdCommon.setLogLevel("Debug");

    // Widget 추가

    function BomAddList(o9Params) {
        Log.info(">>>@ BomAddList Call");
        vdCommon.programStart();
        vdCommon.printParams(o9Params);

        let parsedParams = JSON.parse(o9Params);
        let querModule = require('o9/data/query');
        let cellsetModule = require('o9/data/cellset')

        let fbVersion = parsedParams.fbVersion;
        let fbMarketingName = parsedParams.fbMarketingName;
        Log.info(">>>fbVersion @" + fbVersion + "@");
        Log.info(">>>fbMarketingName @" + fbMarketingName + "@");

        let IBPLSelectMktName = '';
        IBPLSelectMktName += 'Select ([Item].[A14] ) on row, () on column where ';
        IBPLSelectMktName += `{[Version].[Version Name].filter(#.Name == ${fbVersion} )};`;
        Log.info(">>>Query");
        Log.info(IBPLSelectMktName);

        let ListSelectMktName = cellsetModule.createCellSet(querModule.select(IBPLSelectMktName));

        let result = [];
        Log.info('>>> count' + ListSelectMktName.rowCount);

        if (ListSelectMktName && ListSelectMktName.rowCount > 0) {
            let idx_MktNameID = ListSelectMktName.memberColumnIdex("Item", 'A14');
            Log.info(">>> idx_MktNameID :" + idx_MktNameID);

            let all = {Name: "ALL", DisplayName: 'ALL'};
            result.push(all);

            for (let i = 0; i < ListSelectMktName.rowCount; i++) {
                let MktNameID = ListSelectMktName.row(i).cell(idx_MktNameID).Name;
                let r = {
                    Name: MktNameID,
                    DisplayName: MktNameID
                };

                result.push(r)
            }
        } else {
            Log.Info(">>> non Data : 결과가 없으면 -라도 보여주자");
            let r = {
                Name: 'ALL',
                DisplayName: 'ALL'
            }
            result.push(r)
        }
        Log.info("---- Result -----");
        Log.Info(result);
        return result;
    }

    function ProjectAddList(o9Params) {
        Log.info(">>>@ Project List Call");
        let parsedParams = JSON.parse(o9Params);
        let queryModule = require('o9/data/query');
        let cellsetModule = require('o9/data/cellset');

        let fbVersion = parsedParams.fbVersion;
        let fbMarketingName = parsedParams.fbMarketingName;
        let fbProject = parsedParams.fbProject;
        Log.info(">>>fbVersion @" + fbVersion + "@");
        Log.info(">>>fbMarketingName @" + fbMarketingName + '@');
        Log.info(">>>fbProject @" + fbProject + '@');

        let IBPSelectProject = '';
        IBPSelectProject += 'Select ([Item].[Project]) on row, () on column where';
        IBPSelectProject += `{[Version].[Version Name].filter(#.Name == ${fbVersion}, [Item].[A14].filter(#.Name == ${fbMarketingName})};`;
        Log.info(">>>Query");
        Log.info(IBPSelectProject);

        let ListSelectProject = cellsetModule.createCellSet(queryModule.select(IBPSelectProject));

        let result = [];
        Log.Info(">>> Count" + ListSelectProject.rowCount);

        if (ListSelectProject && ListSelectProject.rowCount > 0) {
            let idx_ProjectID = ListSelectProject.memberColumnIndex("Item", "Project");
            Log.info(">>> idx_ProjectID :" + idx_ProjectID);

            let all = {Name: "ALL", DisplayName: 'ALL'};
            result.push(all);

            for (let i = 0; i < ListSelectProject.rowCount; i++) {
                let ProjectID = ListSelectProject.row(i).cell(idx_ProjectID).Name;
                let r = {
                    Name: ProjectID,
                    DisplayName: ProjectID
                };
                result.push(r)
            }
        } else {
            Log.Info(">>>> Non Date : 결과가 없으면 -라도 보여주자");
            let r = {
                Name: 'ALL',
                DisplayName: 'ALL'
            }
            result.push(r)
        }
        Log.Info("----- Result -----");
        Log.Info(result);
        return result;
    }

    return {
        BomAddList : BomAddList,
        ProjectAddList : ProjectAddList
    };
});