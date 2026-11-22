define('o9.AddSequence', ['o9/data/query', 'o9/data/cellset'], function() {

    var AddSequence = function(o9Params) {
        var queryModule = require('o9/data/query');
        var cellsetModule = require('o9/data/cellset');
        var parsedParams = JSON.parse(o9Params);

        Log.Info('// count ' + JSON.stringify(parsedParams));

		var Version = parsedParams.Version;
        var PlanType = parsedParams.PlanType;
		var GroupID = parsedParams.GroupID;
        var AddSequence = parsedParams.AddSequence;
        var MaxSequence = parsedParams.MaxSequence;  

        MaxSequence = Number(MaxSequence);
        AddSequence = Number(AddSequence);
        AddSequence = Math.max(AddSequence,1);

        if (AddSequence <= MaxSequence) {
            for (let i = MaxSequence; i > AddSequence-1; i--) {
                var CopySequence = `COPYMEASURE([GraphCubeDim_Sequence].[GraphCubeAttr_Sequence] = {{"${i}","${i+1}"}}, {Measure.[SDX Biz Case Definition],Measure.[SDX Biz Case Span Association]},false) WHERE {Version.[Version Name].[${Version}], [Plan Type].[Plan Type].[${PlanType}], [Group].[Group ID].[${GroupID}], [SDX_ObjectiveSequence].[SDX Biz Case Span].[1]};`;
                queryModule.update(CopySequence);
            }
            var UpdateSequence = `scope: (Version.[Version Name].[${Version}] * [Plan Type].[Plan Type].[${PlanType}] * [Group].[Group ID].[${GroupID}] * [GraphCubeDim_Sequence].[GraphCubeAttr_Sequence].[${AddSequence}] * [SDX_ObjectiveSequence].[SDX Biz Case Span].[1]); Measure.[SDX Biz Case Definition] = null; end scope;`;
            queryModule.update(UpdateSequence);
        } else {
            var UpdateNewSequence = `cartesian scope: (Version.[Version Name].[${Version}] * [Plan Type].[Plan Type].[${PlanType}] * [Group].[Group ID].[${GroupID}] * [GraphCubeDim_Sequence].[GraphCubeAttr_Sequence].[${AddSequence}] * [SDX_ObjectiveSequence].[SDX Biz Case Span].[1]); Measure.[SDX Biz Case Span Association] = 1; end scope;`;
            queryModule.update(UpdateNewSequence);
        }
        
        return {};
    };

    return {
        AddSequence,
    };

});