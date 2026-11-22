define('o9.NSCM.JSEditSiteGroupValid', ['o9/data/query', 'o9/data/cellset', 'o9.NSCM.commonLib'], function () {

    const editButton = function (props) {

    try{

        const queryModule = require('o9/data/query');
        const cellsetModule = require('o9/data/cellset');

        props = JSON.parse(props);

        Log.Info("-------------props-----------------------" + JSON.stringify(props));
       // Log.Info("Version "+props.fb_Version);

        for (var i = 0; i < props.fbEdit.length; i++){
                var curr = props.fbEdit[i];
                let updateQuery;
                if(props.fbSiteGroupValid!==null){
                 updateQuery=`
                                scope:([Version].[Version Name].Filter( #.Name == "${props.fb_Version}")* [Location].[Location].Filter( #.Name == "${curr.fbSiteID.Value}"));
                                  Measure.[Site DC Master_Site Group Valid Flag]="${props.fbSiteGroupValid}";
                                end scope; `;
                      }
                else{
                      updateQuery=`
                                scope:([Version].[Version Name].Filter( #.Name == "${props.fb_Version}")* [Location].[Location].Filter( #.Name == "${curr.fbSiteID.Value}"));
                                  Measure.[Site DC Master_Site Group Valid Flag]=null;
                                end scope; `;
                      }

                   
                 
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