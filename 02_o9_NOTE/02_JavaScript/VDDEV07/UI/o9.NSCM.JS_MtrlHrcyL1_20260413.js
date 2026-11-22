define('o9.NSCM.JS_MtrlHrcyL1', ['o9/data/query', 'o9/data/cellset', 'o9.NSCM.commonLib'], function () {
    var callJs = function(o9Params){
        var commonLib = require('o9.NSCM.commonLib');

        var programName = "o9.NSCM.JS_MtrlHrcy_ADD";
        vdCommon = new commonLib.VdCommon(programName);
        vdCommon.setLogLevel("Debug");

        vdCommon.printParams(o9Params);

        // 파라미터 가져오기
        var parsedParams = JSON.parse(o9Params);
        var fbMtrlHrcyType = parsedParams.fbMtrlHrcyType;

        vdCommon.printStep("[Mtrl Hrcy No].[Mtrl Hrcy No] Add");
        var result = vdCommon.selectList(["[Version].[Version Name].[CurrentWorkingView]",
                                            "[Mtrl Hrcy Type].[Mtrl Hrcy Type].[" + fbMtrlHrcyType + "]",
                                            "[Mtrl Hrcy Status].[Mtrl Hrcy Status]",
                                            "[Mtrl Hrcy No].[Mtrl Hrcy No]"],
                                         ["Measure.[Mtrl Hrcy_L1 Name]", "Measure.[Mtrl Hrcy_L1 Order]"],
                                         "orderby Measure.[Mtrl Hrcy_L1 Order] desc",
                                         "");
        vdCommon.printCsData(result, 3);

        var comboList = [];
        var validHashMap = {};
        for ( var i = 0; i < result.cs.rowCount; i++ ) {
            comboData = result.cs.row(i).cell(result.cs.measureColumnIndex("Mtrl Hrcy_L1 Name"));

            if ( validHashMap[comboData] == undefined )
                comboList.push({ Name : comboData, DisplayName : comboData});
        }
        
        vdCommon.programEnd();

        return comboList;
    };

    return {
        JS_MtrlHrcyL1 : callJs
    };
});