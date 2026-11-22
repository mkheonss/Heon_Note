define('o9.NSCM.JS.RepackPartMaster', ['o9.NSCM.commonLibDA'], function(commonLib){
    /**
     * o9.NSCM.JS.RepackPartMaster.
     *
     * RepackPartMaster 공용
     * 
     * Master Data > SOP > Spare Box > Repack Part Master
     */

    /*********************************************************************/
    /**************************** const 설정 *****************************/
    /*********************************************************************/

    /* programName */
    const programName = "o9.NSCM.JS.RepackPartMaster";

    /* setting  */
    // let commonLib = require('o9.NSCM.JScommon_DA');
    let daCommon = new commonLib.DACommon(programName);
    daCommon.setLogLevel("Debug")
    let daUtil = new commonLib.DAUtil();

    /* jsErrorMsg */
    const jsErrorMsg = "Please contact the system administrator.";

    /* set flag to print log */
    const infLogFlag = true;
    
    /**
     * Logs the given message.
     *
     * @param {string} msg - The message to be logged.
     * @returns {void}
     */
    let log = function(msg) {
        daCommon.debug(msg);
    };

    /* infLog */
    let infLog = function (msg, printFlag) {
        if (printFlag) {
            let logMsg = `${this.preFix}[${this.programName}] ${msg}`;
            Log.Info(logMsg);
        }
    };

    /* errLog */
    let errLog = function (msg, printFlag) {
        if (printFlag) {
            let logMsg = `${this.errorPreFix}[${this.programName}] ${msg}`;
            Log.Error(logMsg);
        }
    };

    /*******************************************************************************/
    /**************************** combo list 구성 함수 ******************************/
    /*******************************************************************************/

    /*******************************************************************************/
    /**************************** combo list END ***********************************/
    /*******************************************************************************/

    /*******************************************************************************/
    /**************************** TRANSACTION START ********************************/
    /*******************************************************************************/
    let fn_AddRepackPartMaster = function(o9Params){
        try {
            daCommon.printParams(o9Params);

            var parsedParams = JSON.parse(o9Params);

            var sConsumePart = parsedParams.fb_ConsumePart;
            //대문자화 및 공백제거
            parsedParams.fb_ConsumePart = sConsumePart.toUpperCase().trim();


            // 0.중복 검사
            let dimensionRepackPartMaster = [
                `[Version].[Version Name].[${parsedParams.fb_Version}]`
                , `[Sub Location].[Sub Location].[${parsedParams.fb_FromSite}]`
                , `[Item].[Item].[${parsedParams.fb_Item}]`
                , `[To Item].[To Item].[${parsedParams.fb_ConsumePart}]`
            ];

            let iCountExist = daCommon.selectListCount(dimensionRepackPartMaster, ["Measure.[Repack Part Master_Created by]"],"");

            if(iCountExist > 0) {
                RuleOutputToUI = {Status: 'Error', Message: "Input data is duplicated."};
                return;
            }

            // 0.Valid check

            let countToItem = `[To Item].[To Item].[${parsedParams.fb_ConsumePart}]`;
            let cntDimensionToItem = daCommon.selectCount(countToItem);

            if (cntDimensionToItem === 0) {
                RuleOutputToUI = {Status: 'Error', Message: "Consume Part does not exist."};
                return;

                //createmember
                // infLog(`##########################createmember 전 cntDimensionScenario:: ${cntDimensionScenario} `, infLogFlag);
                
                // let creatMemberToItem = `createmember(
                //     [To Item].[To Item] = {, "${parsedParams.fb_ConsumePart}"}
                //     , [To Item].[To Item$DisplayName] = {"${parsedParams.fb_ConsumePart}", }
                // );`;
                // daCommon.executeQuery('creatMemberToItem', creatMemberToItem);

                // infLog(`##########################createmember 후 cntDimensionScenario:: ${cntDimensionScenario} `, infLogFlag);
            }



            // 1.createMeasure
            let sUserName = daCommon.fn_getUserName();
            let measure = [
                `Measure.[Repack Part Master_Box YN] = "${parsedParams.fb_BOXYN}";`
                //, `Measure.[Repack Part Master_Apply Grade] = "${parsedParams.fb_ApplyGrade}";`
                // ,`Measure.[Repack Part Master_Category No] = "${parsedParams.fb_CategoryNo}";`
                ,`Measure.[Repack Part Master_Current Status] = "Active";`
                // ,`Measure.[Repack Part Master_Parent Part] = "${parsedParams.fb_ParentPart}";`
                // ,`Measure.[Repack Part Master_Part Description] = "${parsedParams.fb_PartDescription}";`
                // ,`Measure.[Repack Part Master_Special Specification] = "${parsedParams.fb_SpecialSpecification}";`
                ,`Measure.[Repack Part Master_Valid] = "${parsedParams.fb_Valid}";`
                ,`Measure.[Repack Part Master_Creation time] = dateadd(Now(),0,"hour");`
                ,`Measure.[Repack Part Master_Created by] = "${sUserName}";`
            ];

            // infLog(`##########################createMeasure 1번실행 fbBizCase:: ${fbBizCase} `, infLogFlag);
            daCommon.createMeasure(dimensionRepackPartMaster, measure);

        } catch ( e ) {
            RuleOutputToUI = { Status : 'Error', Message : "Js Logic Error : " + e.message };
            return;
        }
    };

    let fn_DeleteRepackPartMaster = function(o9Params){
        /* parsed Param */
        const parsedParams = JSON.parse(o9Params);
        let tupleList = parsedParams.fb_TupleList;
        let iErrCnt = 0;
        // User ID
        parsedParams.userId = daCommon.fn_getUserName();

        let sWhere = `where {Measure.[Repack Part Master_Category No] != ""
                            ,Measure.[Repack Part Master_Apply Grade] != ""
                            ,Measure.[Repack Part Master_Part Description] != ""
                            ,Measure.[Repack Part Master_Special Specification] != ""
                            ,Measure.[Repack Part Master_Parent Part] != ""
                            }`;

        tupleList.forEach(e => {
            let dimensionRepackPartMaster = [
                `[Version].[Version Name].[${parsedParams.fb_Version}]`
                , `[Sub Location].[Sub Location].[${e.fb_FromSite.Value}]`
                , `[Item].[Item].[${e.fb_Item.Value}]`
                , `[To Item].[To Item].[${e.fb_ConsumePart.Value}]`
            ];

            let iCountExist = daCommon.selectListCount(dimensionRepackPartMaster, ["Measure.[Repack Part Master_Created by]"],sWhere);

            if(iCountExist > 0) {
                iErrCnt++;
                RuleOutputToUI = {Status: 'Error', Message: "You can delete only data that users have added."};
                return;
            }
        });

        if(iErrCnt==0) {
            tupleList.forEach(e => {
                e.fb_Version = parsedParams.fb_Version;
                QueryCommon.deleteRepackPartMaster(e);
            });
        }

    }

    let fn_selectItemList  = function(o9Params){
        /* parsed Param */
        const parsedParams = JSON.parse(o9Params);

        parsedParams.fb_ProductGroup = daUtil.fn_multiArr(parsedParams.fb_ProductGroup);
        parsedParams.fb_Product = daUtil.fn_multiArr(parsedParams.fb_Product);
        parsedParams.fb_Project = daUtil.fn_multiArr(parsedParams.fb_Project);

        const resultSet = QueryCommon.selectItemList(parsedParams);

        /*  DisplayName(Code)  combo return */
        let comboList = daCommon.fn_makeCombo(resultSet, {DimName : "Item",
                DimAttbName : "Item",
                Sort : "DisplayName",
                isDisplayNameWithCode : false});

        return comboList;

    }

    let fn_selectProjectList  = function(o9Params){
        /* parsed Param */
        const parsedParams = JSON.parse(o9Params);

        parsedParams.fb_ProductGroup = daUtil.fn_multiArr(parsedParams.fb_ProductGroup);
        parsedParams.fb_Product = daUtil.fn_multiArr(parsedParams.fb_Product);

        const resultSet = QueryCommon.selectProjectList(parsedParams);
        var comboList = [];

        if(resultSet.cs.rowCount > 0){
        /*  DisplayName(Code)  combo return */
            comboList = daCommon.fn_makeCombo(resultSet, {DimName : "Item",
                DimAttbName : "Project",
                Sort : "DisplayName",
                isDisplayNameWithCode : false});
        } else {
            comboList.push({ Name : "-", DisplayName : "-" });
        }

        return comboList;

    }

    /*******************************************************************************/
    /**************************** QUERY COMMON START *******************************/
    /*******************************************************************************/
    class QueryCommon {


        /*  
            deleteRepackPartMaster : delete 함수
        */
        static deleteRepackPartMaster(parsedParams){
            let query = `
                delete data for model [Repack Part Master]
                where {
                    [Version].[Version Name].[${parsedParams.fb_Version}]
                    , [Sub Location].[Sub Location].[${parsedParams.fb_FromSite.Value}]
                    , [Item].[Item].[${parsedParams.fb_Item.Value}]
                    , [To Item].[To Item].[${parsedParams.fb_ConsumePart.Value}]
                };
            `;
            // Log.Info("##########################deleteRepackPartMaster:: "+query);
            return daCommon.executeQuery('deleteRepackPartMaster', query);
        }

        static selectItemList(parsedParams){

            let query = `
                //// ABRepackPartMasterAdd  // ds_Item2  // 상위 레벨 multiple 일때
                select (Item.[Item].filter(~(#.[Name] == "-" ) && #.[MP Item Flag] == true)) on row,
                () on column
                where {
                    Item.[Product Group].filter(#.Name in {${parsedParams.fb_ProductGroup}}),
                    Item.[Product].filter(#.Name in {${parsedParams.fb_Product}}),
                    `;

            if(parsedParams.fb_Project != "") {        
                query += `Item.[Project].Filter(#.Name in {${parsedParams.fb_Project}}),
                    `;
            } else {
                query += `Item.[Project].Filter(#.Name in {"-"}),`;
            }

            query += `[Version].[Version Name].[${parsedParams.fb_Version}],
                    [Location].[Location].[${parsedParams.fb_FromSite}],
                    Measure.[Item Site Asn_Current Status] in {"ACTIVE","PLANNED"}
                }
                orderby Item.[Item].DisplayName;
            `;
            return daCommon.selectQueryList('selectItemList', query);
        }

        static selectProjectList(parsedParams){

            let query = `
                //// ABRepackPartMasterAdd  // ds_Project2  // 상위 레벨 multiple 일때

                select (&NSMPProject.filter(~(#.[Name] == "-" ))) on row,
                () on column
                where {
                    Item.[Product Group].filter(#.Name in {${parsedParams.fb_ProductGroup}}),
                    Item.[Product].filter(#.Name in {${parsedParams.fb_Product}}),
                    [Version].[Version Name].[${parsedParams.fb_Version}],
                    [Location].[Location].[${parsedParams.fb_FromSite}],
                    Measure.[Item Site Asn_Current Status] in {"ACTIVE","PLANNED"}
                }
                orderby Item.[Project].DisplayName;
            `;
            return daCommon.selectQueryList('selectProjectList', query);
        }

    }
    /*******************************************************************************/
    /**************************** QUERY COMMON END *********************************/
    /*******************************************************************************/

    /*******************************************************************************/
    /****************** return start o9.NSCM.JS.RepackPartMaster *****************/
    /*******************************************************************************/
    return{
        fn_selectProjectList : daCommon.fn_decorator(fn_selectProjectList),
        fn_selectItemList : daCommon.fn_decorator(fn_selectItemList),
        fn_AddRepackPartMaster : daCommon.fn_decorator(fn_AddRepackPartMaster),
        fn_DeleteRepackPartMaster : daCommon.fn_decorator(fn_DeleteRepackPartMaster)

    };
    /*******************************************************************************/
    /****************** return end o9.NSCM.JS.RepackPartMaster *******************/
    /*******************************************************************************/
});