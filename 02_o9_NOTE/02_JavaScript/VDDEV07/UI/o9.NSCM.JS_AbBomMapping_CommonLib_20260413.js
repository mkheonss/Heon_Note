define('o9.NSCM.JS_AbBomMapping_CommonLib', ['o9/data/query', 'o9/data/cellset', 'o9.NSCM.commonLib'], function () {

    const programName = "o9.NSCM.JS_AbBomMapping_CommonLib";

    const queryModule = require('o9/data/query');
    const cellsetModule = require('o9/data/cellset');
    const commonLib = require('o9.NSCM.commonLib');
    const vdCommon = new commonLib.VdCommon(programName);

    class BomMappingCommonLib {
        constructor(_programName) {
            this.programName = _programName;
            vdCommon.setLogLevel("Debug");
        }

        fn_AddfbProject(o9Params) {
            vdCommon.programStart();
            vdCommon.printParams(o9Params);

            // 파라미터 가져오기
            let parsedParams = JSON.parse(o9Params);

            // Field Binding Set
            let fbVersion = parsedParams.fbVersion;
            let fbMarketingName = parsedParams.fbMarketingName;
            let fbProject = parsedParams.fbProject;
            vdCommon.debug("fn_AddfbProject > parsedParams > fbVersion : " + fbVersion);
            vdCommon.debug("fn_AddfbProject >  parsedParams > fbMarktingName : " + fbMarketingName);
            vdCommon.debug("fn_AddfbProject >  parsedParams > fbProject : " + fbProject);

            let query = `
                select (
                    [Item].[Project]
                ) on row, ()
                on column where {
                    [Item].[A14].filter(#.Name == "${fbMarketingName}")
                };
            `;
            vdCommon.debug("fn_AddProject > > select query : " + query);

            let comboList = this.fn_comboMake(query, "Project");
            vdCommon.programEnd();

            return comboList;
        }

        fn_AddfbBasicName(o9Params) {
            vdCommon.programStart();
            vdCommon.printParams(o9Params);

            // 파라미터 가져오기
            let parsedParams = JSON.parse(o9Params);

            // Field Binding Set
            let fbVersion = parsedParams.fbVersion;
            let fbMarketingName = parsedParams.fbMarketingName;
            let fbProject = parsedParams.fbProject;
            let fbBasic = parsedParams.fbBasic;
            vdCommon.debug("fn_AddfbBasic > parsedParams > fbVersion : " + fbVersion);
            vdCommon.debug("fn_AddfbBasic >  parsedParams > fbMarketingName : " + fbMarketingName);
            vdCommon.debug("fn_AddfbBasic >  parsedParams > fbProject : " + fbProject);
            vdCommon.debug("fn_AddfbBasic >  parsedParams > fbBasic : " + fbBasic);

            let query = `
                select (
                    [Item].[Basic Name]
                ) on row, ()
                on column where {
                    [Item].[A14].filter(#.Name == "${fbMarketingName}")
                    , [Item].[Project].filter(#.Name == "${fbProject}")
                };
            `;
            vdCommon.debug("fn_AddfbBasic > > select query : " + query);

            let comboList = this.fn_comboMake(query, "Basic");
            vdCommon.programEnd();

            return comboList;
        }

        fn_AddfbInch(o9Params) {
            vdCommon.programStart();
            vdCommon.printParams(o9Params);

            // 파라미터 가져오기
            let parsedParams = JSON.parse(o9Params);

            // Field Binding Set
            let fbVersion = parsedParams.fbVersion;
            let fbMarketingName = parsedParams.fbMarketingName;
            let fbProject = parsedParams.fbProject;
            let fbBasic = parsedParams.fbBasic;
            let fbInch = parsedParams.fbInch
            vdCommon.debug("fn_AddfbInch > parsedParams > fbVersion : " + fbVersion);
            vdCommon.debug("fn_AddfbInch>  parsedParams > fbMarketingName : " + fbMarketingName);
            vdCommon.debug("fn_AddfbInch >  parsedParams > fbProject : " + fbProject);
            vdCommon.debug("fn_AddfbInch >  parsedParams > fbBasic : " + fbBasic);
            vdCommon.debug("fn_AddfbInch >  parsedParams > fbInch : " + fbInch);

            let query = `
                select (
                    [Item].[A2]
                ) on row, ()
                on column where {
                    [Item].[A14].filter(#.Name == "${fbMarketingName}")
                    , [Item].[Project].filter(#.Name == "${fbProject}")
                    , [Item].[Basic].filter(#.Name == "${fbBasic}")
                };
            `;
            vdCommon.debug("fn_AddfbInch > > select query : " + query);

            let comboList = this.fn_comboMake(query, "Inch");
            vdCommon.programEnd();

            return comboList;
        }

        fn_AddfbModel(o9Params) {
            vdCommon.programStart();
            vdCommon.printParams(o9Params);

            // 파라미터 가져오기
            let parsedParams = JSON.parse(o9Params);

            // Field Binding Set
            let fbVersion = parsedParams.fbVersion;
            let fbMarketing = parsedParams.fbMarketingName;
            let fbProject = parsedParams.fbProject;
            let fbBasic = parsedParams.fbBasic;
            let fbInch = parsedParams.fbInch;
            let fbModel = parsedParams.fbModel;
            vdCommon.debug("fn_AddfbModel> parsedParams > fbVersion : " + fbVersion);
            vdCommon.debug("fn_AddfbModel>  parsedParams > fbMarketingName : " + fbMarketingName);
            vdCommon.debug("fn_AddfbModel >  parsedParams > fbProject : " + fbProject);
            vdCommon.debug("fn_AddfbModel>  parsedParams > fbBasic : " + fbBasic);
            vdCommon.debug("fn_AddfbModel >  parsedParams > fbInch : " + fbInch);
            vdCommon.debug("fn_AddfbModel >  parsedParams > fbModel : " + fbModel);

            let query = `
                select (
                    [Item].[Item]
                ) on row, ()
                on column where {
                    [Item].[A14].filter(#.Name == "${fbMarketingName}")
                    , [Item].[Project].filter(#.Name == "${fbProject}")
                    , [Item].[Basic].filter(#.Name == "${fbBasic}")
                    , [Item].[A2].filter(#.Name == "${fbInch}")
                };
            `;
            vdCommon.debug("fn_AddfbModel > > select query : " + query);

            let comboList = this.fn_comboMake(query, "Model");
            vdCommon.programEnd();

            return comboList;
        }

        fn_AddfbBuyer(o9Params) {
            vdCommon.programStart();
            vdCommon.printParams(o9Params);

            // 파라미터 가져오기
            let parsedParams = JSON.parse(o9Params);

            // Field Binding Set
            let fbVersion = parsedParams.fbVersion;
            let fbMarktingName = parsedParams.fbMarketingName;
            let fbProject = parsedParams.fbProject;
            let fbBasic = parsedParams.fbBasic;
            let fbInch = parsedParams.fbInch
            let fbModel = parsedParams.fbModel;
            let fbBuyer = parsedParams.fbBuyer;
            vdCommon.debug("fn_AddfbBuyer > parsedParams > fbVersion : " + fbVersion);
            vdCommon.debug("fn_AddfbBuyer >  parsedParams > fbMarketingName : " + fbMarketingName);
            vdCommon.debug("fn_AddfbBuyer >  parsedParams > fbProject : " + fbProject);
            vdCommon.debug("fn_AddfbBuyer >  parsedParams > fbBasic : " + fbBasic);
            vdCommon.debug("fn_AddfbBuyer >  parsedParams > fbInch : " + fbInch);
            vdCommon.debug("fn_AddfbBuyer >  parsedParams > fbModel : " + fbModel);
            vdCommon.debug("fn_AddfbBuyer >  parsedParams > fbBuyer : " + fbBuyer);

            let query = `
                select (
                    [Item].[Buyer]
                ) on row, ()
                on column where {
                    [Item].[A14].filter(#.Name == "${fbMarketingName}")
                    , [Item].[Project].filter(#.Name == "${fbProject}")
                    , [Item].[Basic].filter(#.Name == "${fbBasic}")
                    , [Item].[A2].filter(#.Name == "${fbInch}")
                    ' [Item].[Item].filter(#.Name == "${fbModel}")
                };
            `;
            vdCommon.debug("fn_AddfbModel > > select query : " + query);

            let comboList = this.fn_comboMake(query, "Buyer");
            vdCommon.programEnd();

            return comboList;
        }

        fn_comboMake(query, levelStr) {
            let selectResult = cellsetModule.createCellSet(queryModule.select(query));
            let selectResultCount = selectResult.RowCount;
            vdCommon.debug("selectResult : " + JSON.stringify(selectResult));
            vdCommon.debug("selectResultCount : " + JSON.stringify(selectResultCount));

            let comboList = [];
            let validHashMap = new Map();

            for (let i = 0; i < selectResultCount; i++) {
                const comboData = selectResult.row(i).cell(selectResult.membersColumnIndex('BOM ADD', levelStr)).Name;

                if (!validHashMap.has(comboData)) {
                    comboList.push({Name :comboData, DisplayName :comboData});
                    validHashMap.set(comboData, comboData);
                }
            }
            vdCommon.debug("fn_comboMake : " + JSON.stringify(validHashMap));
            return comboList;
        }
    }

    return {BomMappingCommonLib}
});