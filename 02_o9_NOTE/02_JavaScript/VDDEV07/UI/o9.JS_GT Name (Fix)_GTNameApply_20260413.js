define('o9.JS_GT Name (Fix)_GTNameApply', ['o9/data/query', 'o9/data/cellset', 'o9.ap.webservice.cliet'], function () {
    //gets all dimensions defined
    var Validate = function () {
    
        var queryModule = require('o9/data/query');
        var cellsetModule = require('o9/data/cellset');

        //Python Plugin
        Log.Info('----------------------Start Python Plugin -----------------------');
        var pythonplugin='Exec plugin instance [PY_UI_GT NameCreMemVal] for measures {[GT_Priority],[GT_Fix Name_Validation]} using scope ([Version].[Version Name].[CWV_MP] * [Global Top].[GT Code])  using arguments {(ExecutionMode, "LightWeight"),(MaxSliceTableCells, 200000000), ([Param.o9_sys_log_level], "DEBUG") };';
        queryModule.update(pythonplugin);
        Log.Info('----------------------Finish Python Plugin -----------------------');

        //Global Top Query
        var queryForCoverage = 'Select ([Version].[Version Name].[CWV_MP] * &NSUIGlobalTopView * [Global Top].[GT Name] * {Measure.[GT_Fix Name], Measure.[GT_Priority]});';
        var dataCellSet = cellsetModule.createCellSet(queryModule.select(queryForCoverage));
        
        Log.Info('Global Top Data ---' + JSON.stringify(dataCellSet));

        
        let coverage = [];


        const map1 = new Map();
        
        var coder1 = "";
        var errorVal = [];
        for (i = 0; i < dataCellSet.rowCount; i++) {
            var covVal = dataCellSet.row(i).cell(dataCellSet.measureColumnIndex('GT_Fix Name'));
            
            if(covVal == null || covVal == ""){
                covVal = dataCellSet.row(i).cell(dataCellSet.memberColumnIndex('Global Top', 'GT Name')).Name;
            }else{
                errorVal.push(covVal);
            }
            
            let store = dataCellSet.row(i).cell(dataCellSet.memberColumnIndex('Global Top', 'GT Code')).Name;
            coder1 = coder1 + '[' + store + ']';
            if (i < dataCellSet.rowCount - 1){
                coder1 = coder1 + ',';
            }
            map1.set(dataCellSet.row(i).cell(dataCellSet.memberColumnIndex('Global Top', 'GT Code')).Name, covVal.replace(/"/g, '\\"'));
        }

        ///// Check Dublicate Function
        const check_dublicate = (input_array) => {
            const dub = input_array.filter((item, index) => input_array.indexOf(item) !== index);
            return Array.from(new Set(dub));
        };
        Log.Info('Before Dublicate Array ...  ' + JSON.stringify(errorVal));
        let dub_Arr = check_dublicate(errorVal);
        Log.Info('Dublicate Array ...  ' + JSON.stringify(dub_Arr));

        let err = 1;
        var code1 = [];
        let ErrorOutput = "";
        for (i = 0; i < errorVal.length; i++) {
            for (j = 0; j < dub_Arr.length; j++) {
                if (errorVal[i] === dub_Arr[j]) {
                    code1.push(errorVal[i]);
                    err = 0;
                }
            }
            
        }
        dub_Arr = check_dublicate(code1);

        // Storing Error Data in Formate
        for(i = 0; i < dub_Arr.length; i++){
            if(i == dub_Arr.length-1){
                ErrorOutput = ErrorOutput +"["+ dub_Arr[i] + "]";
            }else{
                ErrorOutput = ErrorOutput +"["+ dub_Arr[i] + "], ";
            }
        }
        Log.Info(' -------------------Showing ERROR  --------------------------------------  ' + code1);
        
        if (err === 0) {
            RuleOutputToUI = {
                Status: 'Error',
                Message: 'There are ' + dub_Arr.length + ' duplicate Vendor(HQ), Please correct Vendor(HQ): ' + ErrorOutput + ''
            };
            return;
        }
        Log.Info('Error Not Found...');


        var VendorQuery = 'select([Location].[Location].Filter(#. Name in {'+ coder1 +'}));';
        // var VendorQuery = 'select ([Location].[Location].filter(#.Name Startswith"G"));';

        var VendorCode = cellsetModule.createCellSet(queryModule.select(VendorQuery));
        Log.Info('VendorCode Array ...  ' + JSON.stringify(VendorCode));
        Log.Info('Map Size...' + map1.size);
        for(let k =0; k <VendorCode.rowCount;k++){
            let vd = VendorCode.row(k).cell(VendorCode.memberColumnIndex('Location', 'Location')).Name;
            Log.Info('Code...' + vd);
            let mainCode = map1.get(vd);
            

            var CreateSO = 'Createmember([Global Top].[GT Code]={,"' + vd + '"}, [Global Top].[GT Name Fix] = {, "' + mainCode + '" });';
            Log.Info('CreateSO...' + CreateSO);

            var meas = 'scope:([Version].[Version Name].[CWV_MP] * [Location].[Location] * [Vendor].[Vendor] * [Global Top].[GT Code].['+ vd+'] * [Partner Vendor].[Partner Vendor] * [Item Material].[Item Material] );Measure.[Vendor Mtrl_GT Name] = "' + mainCode + '"; end scope;';
            Log.Info('code3...' + meas);
            queryModule.update(meas);
        }
    };
    return {
        Validate: Validate
    };
});