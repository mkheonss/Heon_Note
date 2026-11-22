define('o9.NSCM.JSCopyTactTimeModelValue', ['o9/data/query', 'o9/data/cellset', 'o9.NSCM.commonLib'], function () {
    const addBtn = function (props) {

        try {
            const queryModule = require('o9/data/query');
            const cellsetModule = require('o9/data/cellset');

            props = JSON.parse(props);

            const queryForUIData = `Select (&CWV * [Sub Location].[Sub Location].[${props.fbFrom_Site}]  * [Item].[Item].[${props.fbItem}]*[Line].[Line].[${props.fbLineName}]) on row,({Measure.[Tact Time Model_Target Tact Time], Measure.[Tact Time Model_Priority]}) on column;`;

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

            //--------------------------Add Command----------------------

            let addQuery = `
		cartesian scope: (&CWV* [Sub Location].[Sub Location].Filter( #.Name == "${props.fbFrom_Site}")*[Item].[Item].Filter( #.Name == "${props.fbItem}")*[Line].[Line].Filter( #.Name == "${props.fbLineName}"));
		
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
    return {
        addBtn: addBtn
    };
});