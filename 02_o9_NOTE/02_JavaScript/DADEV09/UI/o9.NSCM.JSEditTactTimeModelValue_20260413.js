define('o9.NSCM.JSEditTactTimeModelValue', ['o9/data/query', 'o9/data/cellset', 'o9.NSCM.commonLib'], function () {
    const editBtn = function (props) {

        try {
            const queryModule = require('o9/data/query');
            const cellsetModule = require('o9/data/cellset');

            props = JSON.parse(props);

        
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

            let editQuery = `
		 scope: (&CWV* [Sub Location].[Sub Location].Filter( #.Name == "${props.fbFrom_Site}")*[Item].[Item].Filter( #.Name == "${props.fbItem}")*[Line].[Line].Filter( #.Name == "${props.fbLineName}"));
                Measure.[Tact Time Model_Target Tact Time]="${props.fbTargetTactTime}";
	        	Measure.[Tact Time Model_Priority]="${props.fbPriority}";

	   	end scope;
		`;

        queryModule.update(editQuery);

        } catch (error) {
            RuleOutputToUI = { Status: 'Error', Message: "Js Logic Error : " + error.message };
            return;
        }

    };
    return {
        editBtn: editBtn
    };
});