define('o9.NSCM.JSEditPriority', ['o9/data/query', 'o9/data/cellset', 'o9.NSCM.commonLib'], function () {

    const editButton = function (props) {

    try{

        const queryModule = require('o9/data/query');
        const cellsetModule = require('o9/data/cellset');

        props = JSON.parse(props);

       // Log.Info("-------------props-----------------------" + JSON.stringify(props));
        //Log.Info("Tuple "+props.fbPriority);
            var Priority=props.fbPriority;
       
            if ( Priority<=0||Priority>=10000) {
                RuleOutputToUI = {
                    Status: 'Error',
                    Message: 'Priority should be in greater than 0 and less than 10000'
                };
                return;
            }

        for (var i = 0; i < props.fbEditPriority.length; i++){
                var curr = props.fbEditPriority[i];
                let updateQuery=`
                                scope:(&CWV* [Sub Location].[Sub Location].Filter( #.Name == "${curr.fbFromSite.Value}")*[Item].[Item].Filter( #.Name == "${curr.fbItem.Value}")*[Line].[Line].Filter( #.Name == "${curr.fbLineName.Value}"));
                                  Measure.[Tact Time Model_Priority]="${props.fbPriority}";
                                end scope;
                   
                  `;
               queryModule.update(updateQuery);

              }



      }

    catch (e) {
        RuleOutputToUI = { Status: 'Error', Message: "Js Logic Error : " + e.message };
        return;
    }
    };

   

    return {
        editButton: editButton
    };
});