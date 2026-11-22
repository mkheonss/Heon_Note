define('o9.NSCM.JSAddSiteDetailValue', ['o9/data/query', 'o9/data/cellset', 'o9.NSCM.commonLib'], function () {
    const addBtn = function (props) {

        try {
            const queryModule = require('o9/data/query');
            const cellsetModule = require('o9/data/cellset');

            props = JSON.parse(props);

            const queryForUIData = `Select (&CWV* [Location].[Location].[${props.fbTo_Site}] * [Sub Location].[Sub Location].[${props.fbFrom_Site}] * [ERP Ship to].[ERP Ship to ID].[${props.fbShipToName}] * [ERP Sold to].[ERP Sold to ID].[${props.fbSoldToName}] * [Item].[Product Group].[${props.fbProductGroup}] ) on row,({Measure.[Site Detail_Priority], Measure.[Site Detail_Status]}) on column;`;

            const uiData = cellsetModule.createCellSet(queryModule.select(queryForUIData));


            if (uiData.rowCount > 0) {
                RuleOutputToUI = {
                    Status: 'Error',
                    Message: 'Duplicate data found'
                };
                return;
            }

            //--------------------------Add Command----------------------

            let addQuery = `
		cartesian scope: (&CWV* [Location].[Location].Filter( #.Name == "${props.fbTo_Site}") * [Sub Location].[Sub Location].Filter( #.Name == "${props.fbFrom_Site}") * [ERP Ship to].[ERP Ship to ID].Filter( #.Name == "${props.fbShipToName}") * [ERP Sold to].[ERP Sold to ID].Filter( #.Name == "${props.fbSoldToName}") * [Item].[Product Group].Filter( #.Name == "${props.fbProductGroup}"));
		Measure.[Site Detail_Priority]="${props.fbPriority}";
		Measure.[Site Detail_Status]="${props.fbStatus}";
		end scope;
		`;

        queryModule.update(addQuery);

        } catch (error) {
            RuleOutputToUI = { Status: 'Error', Message: "Js Logic Error : " + error.message };
            return;
        }

    };
    return {
        addBtn: addBtn
    };
});