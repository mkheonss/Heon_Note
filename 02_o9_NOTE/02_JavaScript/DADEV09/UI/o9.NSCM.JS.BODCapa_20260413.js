define('o9.NSCM.JS.BODCapa', ['o9.NSCM.commonLibDA'], function(commonLib)
{
    /**
     * o9.NSCM.JS.Simulation.
     *
     * Simulation 공용
     */
    /***********************************************************************/
    /******************* const 설정                  ************************/
    /***********************************************************************/
    /* Program Name */
    const programName = 'o9.NSCM.JS.BODCapa';
    /* jsErrorMsg   */
    const jsErrorMsg = 'An error occurred during the Simulation. \n Please contact the system administrator.';
    /* setting  */
    let daCommon = new commonLib.DACommon(programName);
    daCommon.setLogLevel("Debug");
    let daUtil = new commonLib.DAUtil();
    /**
     * Logs the given message.
     *
     * @param {string} msg - The message to be logged.
     * @returns {void}
     */
    let log = function(msg) {
        daCommon.debug(msg);
    }
    /**
     * Prints the given parameters.
     *
     * @param {Array} params - The parameters to be printed.
     */
    let printParams = function(params) {
        daCommon.printParams(params);
    }
/**********************************************************************************************************************/
/***************** TRANSACTION START *********************************************************************/
/**********************************************************************************************************************/
    let fn_SubmitBODCapaAdd = function(o9Params){
        /* parsed Param */
        const parsedParams = JSON.parse(o9Params);
        // User ID
        parsedParams.userId = daCommon.fn_getUserName();
        parsedParams.fb_Week = daUtil.fn_multiArr(parsedParams.fb_Week);
        /* [Capa Group].[Capa Group] member update*/

        let resultSet = QueryCommon.selectBODCapa(parsedParams);
        Log.Info("##########################resultSet:: "+resultSet.Result);
        if(resultSet.Result !== 0){
            RuleOutputToUI = {Status: 'Error', Message: "BOD Capa Group duplicate!"};
        }else {
            QueryCommon.executeCartesianBODCapaAdd(parsedParams);
        }
        
    }

    let fn_SubmitBODCapaGroupAdd = function(o9Params){
        /* parsed Param */
        const parsedParams = JSON.parse(o9Params);
        let resultSet;
        // User ID
        parsedParams.userId = daCommon.fn_getUserName();
        //[Capa Group].[Capa Group] Group ID의 Max값을 가져온다.
        parsedParams.useCapaGroupID = fn_createBODCapaGroupID();

        /* [Capa Group].[Capa Group] member update*/
        QueryCommon.updateCapaGroupID(parsedParams);
        //CapaGroup생성될때 Seq 1부터 생성
        parsedParams.Seq = 1;
        resultSet = QueryCommon.selectSubLocationName(parsedParams);
        if(resultSet.cs.rowCount !== 0){
            parsedParams.fromSiteName = daCommon.getMember(resultSet.cs, 0, 'Sub Location', 'Sub Location').DisplayName;
        }else {
            parsedParams.fromSiteName = "";
        }
        resultSet = QueryCommon.selectLocationName(parsedParams);
        if(resultSet.cs.rowCount !== 0){
            parsedParams.toSiteName = daCommon.getMember(resultSet.cs, 0, 'Location', 'Location').DisplayName;
        }else {
            parsedParams.toSiteName = "-";
        }

        QueryCommon.executeCartesianBODCapaGroupAdd(parsedParams);
    }

    let fn_createBODCapaGroupID = function(o9Params){
        /* parsed Param */
        // const parsedParams = JSON.parse(o9Params);
        let groupID = 'Group 1';
        // bod capa 전체 group을 select
        const resultSet = QueryCommon.selectMaxBODCapaGroupList(o9Params);
        if(resultSet.cs.rowCount !== 0){
            let groupSeq = [];
            for(let i=0; i<resultSet.cs.rowCount; i++){
                // Capa Group값이 Group 1~ 이런식이라 1을가져오기 위해 split하고 마지막 값을 가져와서 배열저장
                groupSeq.push(parseInt(daCommon.getMember(resultSet.cs, i, 'Capa Group', 'Capa Group').Name.split(' ').pop()));
                // 생성될 group의 seq를 가져오기 위한 함수 호출
                let useGroupSeq = findNextValue(groupSeq);
                let prefix = 'Group ';
                groupID = prefix + useGroupSeq;
            }
        }
       
        return groupID;
    }

    let fn_dsToSiteGroup3 = function(o9Params){
        /* parsed Param */
        const parsedParams = JSON.parse(o9Params);

        let resultSet
        let comboList = [];

        if(parsedParams.fb_Type === "From"){
            comboList.push({ Name : "-", DisplayName : "-"});
        }else{
            resultSet = QueryCommon.selectToSiteGroup3(parsedParams);
            comboList = daCommon.fn_makeCombo(resultSet, {DimName : "Location", DimAttbName : "Site Group3", Sort : "DisplayName", isDisplayNameWithCode : false});
        }
        return comboList;
    }

    let fn_dsToSite = function(o9Params){
        /* parsed Param */
        const parsedParams = JSON.parse(o9Params);

        let resultSet
        let comboList = [];

        if(parsedParams.fb_Type === "From"){
            comboList.push({ Name : "-", DisplayName : "-"});
        }else{
            parsedParams.fb_ToSiteGroup3 = daUtil.fn_multiArr(parsedParams.fb_ToSiteGroup3);
            resultSet = QueryCommon.selectToSite(parsedParams);
            // comboList.push({ Name : "-", DisplayName : "-"});
            comboList = daCommon.fn_makeCombo(resultSet, {DimName : "Location", DimAttbName : "Location", Sort : "Name", isDisplayNameWithCode : false});
        }
        return comboList;
    }

    let fn_SubmitBODCapaSiteAdd = function(o9Params){
        /* parsed Param */
        const parsedParams = JSON.parse(o9Params);
        // User ID
        parsedParams.userId = daCommon.fn_getUserName();
        // ibpl query row return을 받는 변수
        let resultSet;
        // site add시에 추가될 Seq번호를 받는 변수
        let useGroupSeq;

        // Site Add시 from Site, to Site 중복에서 들어가는것을 막기 위한 쿼리
        resultSet = QueryCommon.selectBODCapaGroupListForDupl(parsedParams);
        if(resultSet.cs.rowCount !== 0){
            RuleOutputToUI = {Status: 'Error', Message: "BOD Capa Group Site duplicate!"};
            return;
        }

        // check된 group에 대한 site seq를 가져오는 쿼리 실행
        resultSet = QueryCommon.selectMaxBODCapaSite(parsedParams);

        if(resultSet.cs.rowCount !== 0){
            let groupSeq = [];
            // check된 group에 대한 site seq를 배열 groupSeq에 저장 
            for(let i=0; i<resultSet.cs.rowCount; i++){
                groupSeq.push(parseInt(daCommon.getMember(resultSet.cs, i, 'Seq', 'Seq').Name));
            }
            // 생성될 seq번호를 가져오는 함수 실행
            useGroupSeq = findNextValue(groupSeq);
        }

        parsedParams.Seq = useGroupSeq;
        parsedParams.useCapaGroupID = parsedParams.fb_CapaGroup;
        //Sub Location, Location DisplayName구해서 measure에 넣기
        resultSet = QueryCommon.selectSubLocationName(parsedParams);
        if(resultSet.cs.rowCount !== 0){
            parsedParams.fromSiteName = daCommon.getMember(resultSet.cs, 0, 'Sub Location', 'Sub Location').DisplayName;
        }else {
            parsedParams.fromSiteName = "";
        }
        resultSet = QueryCommon.selectLocationName(parsedParams);
        if(resultSet.cs.rowCount !== 0){
            parsedParams.toSiteName = daCommon.getMember(resultSet.cs, 0, 'Location', 'Location').DisplayName;
        }else {
            parsedParams.toSiteName = "-";
        }
        QueryCommon.executeCartesianBODCapaGroupAdd(parsedParams);
    }

    let fn_SubmitBODCapaGroupDelete = function(o9Params){
        /* parsed Param */
        const parsedParams = JSON.parse(o9Params);
        let tupleList = parsedParams.fb_TupleList;
        // User ID
        parsedParams.userId = daCommon.fn_getUserName();
        // fb_GroupID별 count  
        const capaGroupCntObj = {};
        // check box에 선택된 capaGroup을 배열로 저장
        let capaGroupArr = tupleList.map(e => 
            e.fb_CapaGroup.Value
        );
        // 체크된 groupID 개수를 Object type의 groupIDCntObj 저장
        capaGroupArr.forEach(item => {
            capaGroupCntObj[item] = (capaGroupCntObj[item] || 0) + 1; 
        });
        // groupIDCntObj의 key만 가져온다.
        const capaGroupList = Object.keys(capaGroupCntObj);
        let param = {};
        capaGroupList.forEach(capaGroup => {
            param.fb_CapaGroup = capaGroup;
            param.fb_Version = parsedParams.fb_Version;
            let resultSetRowCount = QueryCommon.selectMaxBODCapaSite(param).cs.rowCount;
            if(resultSetRowCount == capaGroupCntObj[capaGroup]){
                QueryCommon.deleteBODCapa(param);
            }
        });

        //DeleteUseCaseIndex를 통해 Scenario Demand Modification 메져그룹 삭제
        tupleList.forEach(e => {
            e.fb_Version = parsedParams.fb_Version;
            QueryCommon.deleteBODCapaGroup(e);
        });
    }

    let fn_dsCapaGroup = function(o9Params){
        /* parsed Param */
        const parsedParams = JSON.parse(o9Params);
        let comboList = [];
        resultSet = QueryCommon.selectMaxBODCapaGroupList(parsedParams);
            // comboList.push({ Name : "-", DisplayName : "-"});
        comboList = daCommon.fn_makeCombo(resultSet, {DimName : "Capa Group", DimAttbName : "Capa Group", isDisplayNameWithCode : false});
        return comboList;
    }

    let findNextValue = function (excludes = []) {
        const excluded = new Set(excludes);
        let current = 1;

        while (excluded.has(current)) {
            current++;
        }
        return current++;
    }

    class QueryCommon {
        static deleteBODCapa(parsedParams){
            let query = `
                delete data for model [BOD Capacity]
                where {
                    [Version].[Version Name].[${parsedParams.fb_Version}]
                    , [Capa Group].[Capa Group].[${parsedParams.fb_CapaGroup}] 
                };

                delete data for model [BOD Capacity W]
                where {
                    [Version].[Version Name].[${parsedParams.fb_Version}]
                    , [Capa Group].[Capa Group].[${parsedParams.fb_CapaGroup}] 
                };
            `;
            // Log.Info("##########################deleteBODCapa:: "+query);
            return daCommon.executeQuery('deleteBODCapa', query);
        }

        static deleteBODCapaGroup(parsedParams){
            let query = `
                delete data for model [BOD Capacity Group]
                where {
                    [Version].[Version Name].[${parsedParams.fb_Version}]
                    , [Capa Group].[Capa Group].[${parsedParams.fb_CapaGroup.Value}]
                    , [Seq].[Seq].[${parsedParams.fb_Seq.Value}]
                };
            `;
            // Log.Info("##########################deleteBODCapaGroup:: "+query);
            return daCommon.executeQuery('deleteBODCapa', query);
        }

        static executeCartesianBODCapaAdd(parsedParams) {
            let query =`
                cartesian scope: (
                    [Version].[Version Name].[${parsedParams.fb_Version}] 
                    * [Capa Group].[Capa Group].[${parsedParams.fb_CapaGroup}]
                );
                    Measure.[BOD Capa_Created By] = "${parsedParams.userId}";
                    Measure.[BOD Capa_Creation Time] = Now();
                end scope;

                cartesian scope: (
                    [Version].[Version Name].[${parsedParams.fb_Version}] 
                    * [Capa Group].[Capa Group].[${parsedParams.fb_CapaGroup}]
                    * Time.Week.filter(#.Name in {${parsedParams.fb_Week}})
                );
                    Measure.[BOD Capa W_Capa] = null;
                end scope;
            `;
            // Log.Info("##########################executeCartesianBODCapaAdd:: "+query);
            return daCommon.executeQuery('executeCartesianBODCapaAdd', query);
        }
        static selectMaxBODCapaSite(parsedParams) {
            let query = `
                Select (
                    [Version].[Version Name].[${parsedParams.fb_Version}] 
                    * [Seq].[Seq] 
                    * [Capa Group].[Capa Group].[${parsedParams.fb_CapaGroup}] 
                ) on row, 
                ({
                    Measure.[BOD Capa Group_Creation Time]
                }) on column
                orderby [Seq].[Seq].Key asc;
            `;
            return daCommon.selectQueryList('selectSubLocationName', query);
        }

        static selectBODCapa(parsedParams) {
            let query = `
                (Select (
                    [Version].[Version Name].[${parsedParams.fb_Version}] 
                    * [Capa Group].[Capa Group].[${parsedParams.fb_CapaGroup}]
                    * Time.[Week]
                ) on row, 
                ({
                    Measure.[BOD Capa_Creation Time]
                    , Measure.[BOD Capa W_Capa]
                }) on column
                where {
                    isNull(Measure.[BOD Capa W_Capa])
                }).Count;
            `;
            return daCommon.selectQuery('selectSubLocationName', query);
        }
        
        static selectToSiteGroup3(parsedParams) {
            let query = `
                select ([Location].[Site Group3].filter(~(#.[DisplayName] == "-"))) on row,
                () on column
                where {
                    &NSLoadingDirToSite
                }
                orderby [Location].[Site Group3].DisplayName;
            `;
            return daCommon.selectQueryList('selectSubLocationName', query);
        }

        static selectToSite(parsedParams) {
            let query = `
                select (&NSToSiteDC) on row,
                () on column
                where {
                    [Location].[Site Group3].filter(#.Name in {${parsedParams.fb_ToSiteGroup3}})
                };
            `;
            return daCommon.selectQueryList('selectToSite', query);
        }

        static selectSubLocationName(parsedParams) {
            let query = `
                select ([Sub Location].[Sub Location].[${parsedParams.fb_FromSite}]) on row;
            `;
            return daCommon.selectQueryList('selectSubLocationName', query);
        };

        static selectLocationName(parsedParams) {
            let query = `
                select ([Location].[Location].[${parsedParams.fb_ToSite}]) on row;
            `;
            return daCommon.selectQueryList('selectLocationName', query);
        };

        static updateMemberDelayCase(parsedParams) {
            let query =`
                createmember(
                    Group.[Group ID] = {, "${parsedParams.useCaseID}"}, [Group].[Description] = {"${parsedParams.fb_UseCase}", }
                    , Group.[Group Type] = {, "Biz_DMD"}
                );
                `
            // Log.Info("##########################updateMemberGroupIDDescription:: "+query);
            return daCommon.executeQuery('updateMemberDelayCase', query);
        };

        static selectMaxBODCapaGroupList(parsedParams) {
            let query = `
                Select (
                    [Version].[Version Name].CWV_MP
                    * [Capa Group].[Capa Group]
                    * [Seq].[Seq]  
                ) on row, 
                ({
                    Measure.[BOD Capa Group_Created By]
                }) on column
                orderby [Capa Group].[Capa Group].Key Asc;
            `;
            return daCommon.selectQueryList('selectMaxBODCapaGroupList', query);
        };

        static updateCapaGroupID(parsedParams) {
            let query =`
                createmember(
                    [Capa Group].[Capa Group] = {, "${parsedParams.useCapaGroupID}"}
                    , [Capa Group].[Capa Group$DisplayName] = {"${parsedParams.useCapaGroupID}", }
                );
                `
            // Log.Info("##########################updateCapaGroupID:: "+query);
            return daCommon.executeQuery('updateCapaGroupID', query);
        };

        static executeCartesianBODCapaGroupAdd(parsedParams) {
            let query =`
                cartesian scope: (
                    [Version].[Version Name].[${parsedParams.fb_Version}] 
                    * [Seq].[Seq].[${parsedParams.Seq}]
                    * [Capa Group].[Capa Group].[${parsedParams.useCapaGroupID}]
                );
                    Measure.[BOD Capa Group_Type] = "${parsedParams.fb_Type}";
                    Measure.[BOD Capa Group_From Site] = "${parsedParams.fb_FromSite}";
                    Measure.[BOD Capa Group_From Site Name] = "${parsedParams.fromSiteName}";
                    Measure.[BOD Capa Group_To Site] = "${parsedParams.fb_ToSite}";
                    Measure.[BOD Capa Group_To Site Name] = "${parsedParams.toSiteName}";
                    Measure.[BOD Capa Group_Tranport Mode] = "${parsedParams.fb_TransportMode}";
                    Measure.[BOD Capa Group_Remark] = "${daUtil.fn_trim(parsedParams.fb_Remark)}";
                    Measure.[BOD Capa Group_Created By] = "${parsedParams.userId}";
                    Measure.[BOD Capa Group_Creation Time] = Now();
                end scope;

                createmember(
                    [Resource].[Resource] = {, "SR_${parsedParams.useCapaGroupID}_REF"}
                    , [Resource].[Resource All] = {,"All"}
                    , [Resource].[Resource Alternate Group1] = {,"LOAD"}
                    , [Resource].[Resource Alternate Group2] = {,"All"}
                    , [Resource].[Resource Type] = {,"${parsedParams.useCapaGroupID}"}
                    , [Resource].[Resource Solver Scope] = {,"REF"}
                );
                createmember(
                    [Resource].[Resource] = {, "SR_${parsedParams.useCapaGroupID}_WM"}
                    , [Resource].[Resource All] = {,"All"}
                    , [Resource].[Resource Alternate Group1] = {,"LOAD"}
                    , [Resource].[Resource Alternate Group2] = {,"All"}
                    , [Resource].[Resource Type] = {,"${parsedParams.useCapaGroupID}"}
                    , [Resource].[Resource Solver Scope] = {,"WM"}
                );
                createmember(
                    [Resource].[Resource] = {, "SR_${parsedParams.useCapaGroupID}_AC"}
                    , [Resource].[Resource All] = {,"All"}
                    , [Resource].[Resource Alternate Group1] = {,"LOAD"}
                    , [Resource].[Resource Alternate Group2] = {,"All"}
                    , [Resource].[Resource Type] = {,"${parsedParams.useCapaGroupID}"}
                    , [Resource].[Resource Solver Scope] = {,"AC"}
                );
                createmember(
                    [Resource].[Resource] = {, "SR_${parsedParams.useCapaGroupID}_Others"}
                    , [Resource].[Resource All] = {,"All"}
                    , [Resource].[Resource Alternate Group1] = {,"LOAD"}
                    , [Resource].[Resource Alternate Group2] = {,"All"}
                    , [Resource].[Resource Type] = {,"${parsedParams.useCapaGroupID}"}
                    , [Resource].[Resource Solver Scope] = {,"Others"}
                );
            `;
            // Log.Info("##########################executeCartesianBODCapaGroupAdd:: "+query);
            return daCommon.executeQuery('executeCartesianBODCapaGroupAdd', query);
        }

        static selectBODCapaGroupListForDupl(parsedParams) {
            let query = `
                Select (
                    [Version].[Version Name].[${parsedParams.fb_Version}] 
                    * [Seq].[Seq] 
                    * [Capa Group].[Capa Group].[${parsedParams.fb_CapaGroup}] 
                ) on row, 
                ({
                    Measure.[BOD Capa Group_Creation Time]
                }) on column
                where{
                    Measure.[BOD Capa Group_From Site] == "${parsedParams.fb_FromSite}"
                    , Measure.[BOD Capa Group_To Site] == "${parsedParams.fb_ToSite}"
                };
            `;
            return daCommon.selectQueryList('selectBODCapaGroupListForDupl', query);
        };
    }
    
    return {
        fn_SubmitBODCapaAdd : daCommon.fn_decorator(fn_SubmitBODCapaAdd)
        , fn_SubmitBODCapaGroupAdd : daCommon.fn_decorator(fn_SubmitBODCapaGroupAdd)
        , fn_SubmitBODCapaSiteAdd : daCommon.fn_decorator(fn_SubmitBODCapaSiteAdd)
        , fn_SubmitBODCapaGroupDelete : daCommon.fn_decorator(fn_SubmitBODCapaGroupDelete)
        , fn_dsToSiteGroup3 : daCommon.fn_decorator(fn_dsToSiteGroup3)
        , fn_dsToSite : daCommon.fn_decorator(fn_dsToSite)
        , fn_dsCapaGroup : daCommon.fn_decorator(fn_dsCapaGroup)
    };
});