define('o9.NSCM.JSObjectivePriorityDefinition', ['o9/data/query', 'o9/data/cellset', 'o9.NSCM.commonLib'], function () {
	const programName = "o9.NSCM.JSObjectivePriorityDefinition";
    const commonLib = require('o9.NSCM.commonLib');
    const vdUtil = new commonLib.VdUtil();

    var fn_groupAdd = function(o9Params){
        const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
        vdCommon.setLogLevel("Debug");
        vdCommon.printParams(o9Params);

        try{
            // 파라메타 가져오기
            let parsedParams = JSON.parse(o9Params);
            var version = parsedParams.Version;
            var planType = parsedParams.PlanType;
            var newGroupIDDescription = parsedParams.NewGroupIDDescription;

            // Max 값을 구한다.
            var result = vdCommon.selectList(["[Version].[Version Name]" + vdUtil.fn_filterStr(version),
                                                '[Group].[Group ID].filter(#.Name != "Regular Plan")'],
                                             [],
                                             "where { [Group].[Group Type].[OBJ_Group], Measure.[SDX Biz Case Span Association] > 0 }",
                                             "orderby [Group].[Group ID].Name desc",
                                             "limit 1");
            var groupId = "OBJ_00001";
            if ( result.cs.rowCount > 0 ) {
                groupId = "OBJ_" + vdUtil.fn_lpad((parseInt(result.cs.row(0).cell(result.cs.memberColumnIndex("Group", "Group ID")).Name.substr(4)) + 1) + "", 5, "0");
            }
            // Dimension 을 생성시 존재여부를 체크해야 하나 Property 인 Description의 수정이 있어서 생성한다.
            vdCommon.createDimension(['[Group].[Group Type]','[Group].[Description]','[Group].[Group ID]'], ["OBJ_Group", "P " + newGroupIDDescription, groupId]);

            // Picklist 생성
            var ddl = 'ddl { ' +
                        '  "Action": "Create", ' +
                        '  "ModelType": "PicklistValue", ' +
                        '  "Payload": { ' +
                        '    "PicklistName": "SDXCreateGroup", ' +
                        '    "DisplayName": "' + groupId + '", ' +
                        '    "Value": "' + groupId + '", ' +
                        '    "DisplayPosition": 0, ' +
                        '    "Icon": null, ' +
                        '    "Color": null, ' +
                        '    "Image": null, ' +
                        '    "CrudAction": 0, ' +
                        '    "ModuleId": "13acb48d-e6bb-4865-a625-202c58b204e8" ' +
                        '  } ' +
                        '}; ';
            vdCommon.executeQuery("DDL 실행", ddl);

            // 데이타 생성
            vdCommon.createMeasure(["[Version].[Version Name]" + vdUtil.fn_filterStr(version),
                                        "[Plan Type].[Plan Type]" + vdUtil.fn_filterStr(planType),
                                        "[Group].[Group ID]" + vdUtil.fn_filterStr(groupId),
                                        "[GraphCubeDim_Sequence].[GraphCubeAttr_Sequence].[1]",
                                        "[SDX_ObjectiveSequence].[SDX Biz Case Span].[1]"],
                                    ['Measure.[SDX Biz Case Span Association] = 1;']);

            vdCommon.programEnd();
        }catch ( e ) {
            RuleOutputToUI = { Status : 'Error', Message : "Js Logic Error : " + e.message };
            return;
        }
    }

    var fn_groupCopy = function(o9Params){
        const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
        vdCommon.setLogLevel("Debug");
        vdCommon.printParams(o9Params);

        try{
            // 파라메타 가져오기
            let parsedParams = JSON.parse(o9Params);
            var version = parsedParams.Version;
            var planType = parsedParams.PlanType;
            var sourceGroupID = parsedParams.SourceGroupID;
            var newGroupIDDescription = parsedParams.NewGroupIDDescription;

            // Max 값을 구한다.
            var result = vdCommon.selectList(["[Version].[Version Name]" + vdUtil.fn_filterStr(version),
                                                '[Group].[Group ID].filter(#.Name != "Regular Plan")'],
                                             [],
                                             "where { [Group].[Group Type].[OBJ_Group], Measure.[SDX Biz Case Span Association] > 0 }",
                                             "orderby [Group].[Group ID].Name desc",
                                             "limit 1");
            var groupId = "OBJ_00001";
            if ( result.cs.rowCount > 0 ) {
                groupId = "OBJ_" + vdUtil.fn_lpad((parseInt(result.cs.row(0).cell(result.cs.memberColumnIndex("Group", "Group ID")).Name.substr(4)) + 1) + "", 5, "0");
            }
            // Dimension 을 생성시 존재여부를 체크해야 하나 Property 인 Description의 수정이 있어서 생성한다.
            vdCommon.createDimension(['[Group].[Group Type]','[Group].[Description]','[Group].[Group ID]'], ["OBJ_Group", "P " + newGroupIDDescription, groupId]);

            // Picklist 생성
            var ddl = 'ddl { ' +
                        '  "Action": "Create", ' +
                        '  "ModelType": "PicklistValue", ' +
                        '  "Payload": { ' +
                        '    "PicklistName": "SDXCreateGroup", ' +
                        '    "DisplayName": "' + groupId + '", ' +
                        '    "Value": "' + groupId + '", ' +
                        '    "DisplayPosition": 0, ' +
                        '    "Icon": null, ' +
                        '    "Color": null, ' +
                        '    "Image": null, ' +
                        '    "CrudAction": 0, ' +
                        '    "ModuleId": "13acb48d-e6bb-4865-a625-202c58b204e8" ' +
                        '  } ' +
                        '}; ';
            vdCommon.executeQuery("DDL 실행", ddl);

            // 데이타 생성
            vdCommon.createMeasure(["[Version].[Version Name]" + vdUtil.fn_filterStr(version),
                                        "[Plan Type].[Plan Type]" + vdUtil.fn_filterStr(planType),
                                        "[Group].[Group ID]" + vdUtil.fn_filterStr(groupId),
                                        "[GraphCubeDim_Sequence].[GraphCubeAttr_Sequence].[1]",
                                        "[SDX_ObjectiveSequence].[SDX Biz Case Span].[1]"],
                                    ['Measure.[SDX Biz Case Span Association] = 1;']);

            // Measure 복사
            var query = 'COPYMEASURE( ' +
                        '  [Group].[Group ID] = {{"' + sourceGroupID + '","' + groupId + '"}} ' +
                        '  ,{ Measure.[SDX Biz Case Definition], Measure.[SDX Biz Case Span Association] } ' +
                        '  ,rollbackonconflict : false  ' +
                        '  ,nullifytargetintersections : true ) ' +
                        'WHERE { Version.[Version Name].[' + version + '], [Plan Type].[Plan Type].[' + planType + '] }; ';
//            var query = `COPYMEASURE(  +
//                          [Group].[Group ID] = {{"${sourceGroupID}","${groupId}"}}
//                          ,{ Measure.[SDX Biz Case Definition], Measure.[SDX Biz Case Span Association] }
//                          ,rollbackonconflict : false
//                          ,nullifytargetintersections : true )
//                        WHERE { Version.[Version Name].[${version}], [Plan Type].[Plan Type].[${planType}] }; `;

            vdCommon.executeQuery("Query 실행", query);

            vdCommon.programEnd();
        }catch ( e ) {
            RuleOutputToUI = { Status : 'Error', Message : "Js Logic Error : " + e.message };
            return;
        }
    }

    var fn_groupDelete = function(o9Params){
        const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
        vdCommon.setLogLevel("Debug");
        vdCommon.printParams(o9Params);

        try{
            // 파라메타 가져오기
            let parsedParams = JSON.parse(o9Params);
            var version = parsedParams.Version;
            var planType = parsedParams.PlanType;
            var groupID = parsedParams.GroupID;

            for ( var i = 0; i < groupID.length; i++ ) {
                vdCommon.deleteMeasure(["[Version].[Version Name]" + vdUtil.fn_filterStr(version),
                                            "[Plan Type].[Plan Type]" + vdUtil.fn_filterStr(planType),
                                            "[Group].[Group ID]" + vdUtil.fn_filterStr(groupID[i])],
                                        "110.005 SDX LPS Priority");

                // Picklist 삭제
                var ddl = 'ddl { ' +
                            '  "Action": "Delete", ' +
                            '  "ModelType": "PicklistValue", ' +
                            '  "Payload": { ' +
                            '    "PicklistName": "SDXCreateGroup", ' +
                            '    "Value": "' + groupID[i] + '", ' +
                            '    "ModuleId": "13acb48d-e6bb-4865-a625-202c58b204e8", ' +
                            '    "CrudAction": 0 ' +
                            '  } ' +
                            '}; ';
                vdCommon.executeQuery("DDL 실행", ddl);
            }

            vdCommon.programEnd();
        }catch ( e ) {
            RuleOutputToUI = { Status : 'Error', Message : "Js Logic Error : " + e.message };
            return;
        }
    }

    var fn_sequenceAdd = function(o9Params){
        const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
        vdCommon.setLogLevel("Debug");
        vdCommon.printParams(o9Params);

        try{
            // 파라메타 가져오기
            let parsedParams = JSON.parse(o9Params);
            var version = parsedParams.Version;
            var planType = parsedParams.PlanType;
            var groupID = parsedParams.GroupID;
            var sequence = parsedParams.AddSequence;

            // 마지막 추가인지 중간 추가 인지를 비교
            if ( sequence == "Last" ) {
                // Max 값을 구한다.
                var result = vdCommon.selectList(["[GraphCubeDim_Sequence].[GraphCubeAttr_Sequence]"],
                                                 ["Measure.[SDX Biz Case Span Association]"],
                                                 "where { [Version].[Version Name]" + vdUtil.fn_filterStr(version) +
                                                    ", [Plan Type].[Plan Type]" + vdUtil.fn_filterStr(planType) +
                                                    ", [Group].[Group ID]" + vdUtil.fn_filterStr(groupID) +
                                                    " }",
                                                 "orderby [GraphCubeDim_Sequence].[GraphCubeAttr_Sequence].Key desc",
                                                 "limit 1");

                var lastSequence = "1";
                if ( result.cs.rowCount > 0 ) {
                    lastSequence = (parseInt(result.cs.row(0).cell(result.cs.memberColumnIndex("GraphCubeDim_Sequence", "GraphCubeAttr_Sequence")).Name) + 1) + "";
                }

                // 데이타 생성
                vdCommon.createMeasure(["[Version].[Version Name]" + vdUtil.fn_filterStr(version),
                                            "[Plan Type].[Plan Type]" + vdUtil.fn_filterStr(planType),
                                            "[Group].[Group ID]" + vdUtil.fn_filterStr(groupID),
                                            "[GraphCubeDim_Sequence].[GraphCubeAttr_Sequence]" + vdUtil.fn_filterStr(lastSequence),
                                            "[SDX_ObjectiveSequence].[SDX Biz Case Span].[1]"],
                                        ['Measure.[SDX Biz Case Span Association] = 1;']);
            } else {
                // sequence 이후의 GraphCubeAttr_Sequence 를 조정한다.
                var result = vdCommon.selectList(["[GraphCubeDim_Sequence].[GraphCubeAttr_Sequence].filter(#.Key >= [GraphCubeDim_Sequence].[GraphCubeAttr_Sequence].[" + sequence + "].Key)"],
                                                 ["Measure.[SDX Biz Case Span Association]"],
                                                 "where { [Version].[Version Name]" + vdUtil.fn_filterStr(version) +
                                                    ", [Plan Type].[Plan Type]" + vdUtil.fn_filterStr(planType) +
                                                    ", [Group].[Group ID]" + vdUtil.fn_filterStr(groupID) +
                                                    " }",
                                                 "orderby [GraphCubeDim_Sequence].[GraphCubeAttr_Sequence].Key desc",
                                                 "");
                for ( var i = 0; i < result.cs.rowCount; i++ ) {
                    var rowSequence = parseInt(result.cs.row(i).cell(result.cs.memberColumnIndex("GraphCubeDim_Sequence", "GraphCubeAttr_Sequence")).Name);

                    // Measure 복사
                    var query = 'COPYMEASURE( ' +
                                '  [GraphCubeDim_Sequence].[GraphCubeAttr_Sequence] = {{"' + rowSequence + '","' + (rowSequence + 1) + '"}} ' +
                                '  ,{ Measure.[SDX Biz Case Definition], Measure.[SDX Biz Case Span Association] } ' +
                                '  ,false ) ' +
                                'WHERE { Version.[Version Name].[' + version + '], [Plan Type].[Plan Type].[' + planType + '], [Group].[Group ID].[' + groupID + '] }; ';
                    vdCommon.executeQuery("Copymeasure 실행", query);
                }

                // 데이타 생성
                vdCommon.updateMeasure(["[Version].[Version Name]" + vdUtil.fn_filterStr(version),
                                            "[Plan Type].[Plan Type]" + vdUtil.fn_filterStr(planType),
                                            "[Group].[Group ID]" + vdUtil.fn_filterStr(groupID),
                                            "[GraphCubeDim_Sequence].[GraphCubeAttr_Sequence]" + vdUtil.fn_filterStr(sequence),
                                            "[SDX_ObjectiveSequence].[SDX Biz Case Span].[1]"],
                                        ['Measure.[SDX Biz Case Span Association] = 1;',
                                            'Measure.[SDX Biz Case Definition] = "";']);
            }

            vdCommon.programEnd();
        }catch ( e ) {
            RuleOutputToUI = { Status : 'Error', Message : "Js Logic Error : " + e.message };
            return;
        }
    }

    var fn_sequenceDelete = function(o9Params){
        const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
        vdCommon.setLogLevel("Debug");
        vdCommon.printParams(o9Params);

        try{
            // 파라메타 가져오기
            let parsedParams = JSON.parse(o9Params);
            var version = parsedParams.Version;
            var planType = parsedParams.PlanType;
            var groupID = parsedParams.GroupID;
            var sequence = parsedParams.Sequence;

            // 삭제
            vdCommon.deleteMeasure(["[Version].[Version Name]" + vdUtil.fn_filterStr(version),
                                        "[Plan Type].[Plan Type]" + vdUtil.fn_filterStr(planType),
                                        "[Group].[Group ID]" + vdUtil.fn_filterStr(groupID),
                                        "[GraphCubeDim_Sequence].[GraphCubeAttr_Sequence]" + vdUtil.fn_filterStr(sequence)],
                                    "110.005 SDX LPS Priority");

            // 삭제후에 GraphCubeAttr_Sequence 를 조정한다.
            var result = vdCommon.selectList(["[GraphCubeDim_Sequence].[GraphCubeAttr_Sequence]"],
                                             ["Measure.[SDX Biz Case Span Association]"],
                                             "where { [Version].[Version Name]" + vdUtil.fn_filterStr(version) +
                                                ", [Plan Type].[Plan Type]" + vdUtil.fn_filterStr(planType) +
                                                ", [Group].[Group ID]" + vdUtil.fn_filterStr(groupID) +
                                                " }",
                                             "orderby [GraphCubeDim_Sequence].[GraphCubeAttr_Sequence].Key",
                                             "");
            var maxSequence = result.cs.rowCount;
            for ( var i = 0; i < result.cs.rowCount; i++ ) {
                var rowSequence = parseInt(result.cs.row(i).cell(result.cs.memberColumnIndex("GraphCubeDim_Sequence", "GraphCubeAttr_Sequence")).Name);

                if ( rowSequence != i + 1 ) {
                    // Measure 복사
                    var query = 'COPYMEASURE( ' +
                                '  [GraphCubeDim_Sequence].[GraphCubeAttr_Sequence] = {{"' + rowSequence + '","' + (i + 1) + '"}} ' +
                                '  ,{ Measure.[SDX Biz Case Definition], Measure.[SDX Biz Case Span Association] } ' +
                                '  ,false ) ' +
                                'WHERE { Version.[Version Name].[' + version + '], [Plan Type].[Plan Type].[' + planType + '], [Group].[Group ID].[' + groupID + '] }; ';
                    vdCommon.executeQuery("Copymeasure 실행", query);
                }
            }

            // GraphCubeAttr_Sequence 를 조정하고 이후 데이타 삭제
            vdCommon.deleteMeasure(["[Version].[Version Name]" + vdUtil.fn_filterStr(version),
                                        "[Plan Type].[Plan Type]" + vdUtil.fn_filterStr(planType),
                                        "[Group].[Group ID]" + vdUtil.fn_filterStr(groupID),
                                        "[GraphCubeDim_Sequence].[GraphCubeAttr_Sequence].filter(#.Key > [GraphCubeDim_Sequence].[GraphCubeAttr_Sequence].[" + maxSequence + "].Key)"],
                                    "110.005 SDX LPS Priority");
            vdCommon.programEnd();
        }catch ( e ) {
            RuleOutputToUI = { Status : 'Error', Message : "Js Logic Error : " + e.message };
            return;
        }
    }

    var fn_sequenceCombo = function(o9Params){
        const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
        vdCommon.setLogLevel("Debug");
        vdCommon.printParams(o9Params);

        try {
            // 파라메타 가져오기
            let parsedParams = JSON.parse(o9Params);
            var version = parsedParams.Version;
            var planType = parsedParams.PlanType;
            var groupID = parsedParams.GroupID;

            var result = vdCommon.selectList(["[GraphCubeDim_Sequence].[GraphCubeAttr_Sequence]"],
                                             ["Measure.[SDX Biz Case Span Association]"],
                                             "where { [Version].[Version Name]" + vdUtil.fn_filterStr(version) +
                                                ", [Plan Type].[Plan Type]" + vdUtil.fn_filterStr(planType) +
                                                ", [Group].[Group ID]" + vdUtil.fn_filterStr(groupID) +
                                                " }",
                                             "orderby [GraphCubeDim_Sequence].[GraphCubeAttr_Sequence].Key",
                                             "");

            var comboList = vdCommon.fn_makeCombo(result, {DimName : "GraphCubeDim_Sequence", DimAttbName : "GraphCubeAttr_Sequence"});

            // 마지막 데이타를 처음에 추가
            comboList.unshift({Name : "Last", DisplayName : parseInt(comboList[comboList.length - 1].Name) + 1});

            vdCommon.debug("ComboData : " + JSON.stringify(comboList.slice(0,3)));

            vdCommon.programEnd();

            return comboList;
        } catch ( e ) {
            RuleOutputToUI = { Status : 'Error', Message : "Js Logic Error : " + e.message };
            return;
        }
    };

    return {
        fn_groupAdd : fn_groupAdd,
        fn_groupCopy : fn_groupCopy,
        fn_groupDelete : fn_groupDelete,
        fn_sequenceAdd : fn_sequenceAdd,
        fn_sequenceDelete : fn_sequenceDelete,
        fn_sequenceCombo : fn_sequenceCombo
    };
});


//    var fn_sequenceInsert = function(o9Params){
//        const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
//        vdCommon.setLogLevel("Debug");
//        vdCommon.printParams(o9Params);
//
//        try{
//            // 파라메타 가져오기
//            let parsedParams = JSON.parse(o9Params);
//            var version = parsedParams.Version;
//            var planType = parsedParams.PlanType;
//            var groupID = parsedParams.GroupID;
//            var sequence = parsedParams.Sequence;
//
//            // sequence 이후의 GraphCubeAttr_Sequence 를 조정한다.
//            var result = vdCommon.selectList(["[GraphCubeDim_Sequence].[GraphCubeAttr_Sequence].filter(#.Key >= [GraphCubeDim_Sequence].[GraphCubeAttr_Sequence].[" + sequence + "].Key)"],
//                                             ["Measure.[SDX Biz Case Span Association]"],
//                                             "where { [Version].[Version Name]" + vdUtil.fn_filterStr(version) +
//                                                ", [Plan Type].[Plan Type]" + vdUtil.fn_filterStr(planType) +
//                                                ", [Group].[Group ID]" + vdUtil.fn_filterStr(groupID) +
//                                                " }",
//                                             "orderby [GraphCubeDim_Sequence].[GraphCubeAttr_Sequence].Key desc",
//                                             "");
//            for ( var i = 0; i < result.cs.rowCount; i++ ) {
//                var rowSequence = parseInt(result.cs.row(0).cell(result.cs.memberColumnIndex("GraphCubeDim_Sequence", "GraphCubeAttr_Sequence")).Name);
//
//                // Measure 복사
//                var query = 'COPYMEASURE( ' +
//                            '  [GraphCubeDim_Sequence].[GraphCubeAttr_Sequence] = {{"' + rowSequence + '","' + (rowSequence + 1) + '"}} ' +
//                            '  ,{ Measure.[SDX Biz Case Definition], Measure.[SDX Biz Case Span Association] } ' +
//                            '  ,false ) ' +
//                            'WHERE { Version.[Version Name].[' + version + '], [Plan Type].[Plan Type].[' + planType + '], [Group].[Group ID].[' + groupID + '] }; ';
//                vdCommon.executeQuery("Copymeasure 실행", query);
//            }
//
//            // 데이타 생성
//            vdCommon.updateMeasure(["[Version].[Version Name]" + vdUtil.fn_filterStr(version),
//                                        "[Plan Type].[Plan Type]" + vdUtil.fn_filterStr(planType),
//                                        "[Group].[Group ID]" + vdUtil.fn_filterStr(groupId),
//                                        "[GraphCubeDim_Sequence].[GraphCubeAttr_Sequence]" + vdUtil.fn_filterStr(sequence),
//                                        "[SDX_ObjectiveSequence].[SDX Biz Case Span].[1]"],
//                                    ['Measure.[SDX Biz Case Span Association] = 1;']);
//
//            vdCommon.programEnd();
//        }catch ( e ) {
//            RuleOutputToUI = { Status : 'Error', Message : "Js Logic Error : " + e.message };
//            return;
//        }
//    }



/*
    1. ABAddOBJGroup (Action Button)
    - NewGroupID_DS (DataSource)의 아래 ibpl을 js로 변환 필요
    ibpl : select ([Group].[Group ID].filter(#.Name != "Regular Plan")) on row,() on column where {[Version].[Version Name].[{{Version}}], [Group].[Group Type].[OBJ_Goup] , Measure.[SDX Biz Case Span Association] > 0 } orderby [Group].[Group ID].Name desc limit 1;
    js : 위 ibpl을 select하면 하나의 멤버가 나오게 됨. 해당 멤버가 max 멤버이고, NewGroupID_DS는 select된 max 멤버보다 숫자가 하나 더 큰 멤버를 표시해 주어야 함.
    * 멤버 예시 : OBJ_00001    즉, OBJ_00001 가 select 된다면, OBJ_00002 를 표시해 주어야 함.

    3. ABCopyOBJGroup (Action Button)
    - AddOBJGroup과 동일하게 NewGroupID_DS 바꾸어 주어야 함.

4. ABAddOBJGroupSequence (Action Button)
내용 : 마지막 라인에 줄을 추가하면 마지막 라인 줄 보이게 intersaction 추가, 중간에 추가하면 중간에 intersaction 만들고 copymeasure로 한 줄씩 다음 sequence로 copy 해주고, 추가한 라인을 null처리 한다면,
- (js 만든 것 VD에 맞게 변경 및 optimize 필요)
- js 추가 사항 - AddSequenceDS : MaxSequence 가 50 이라면 51 부터 1까지 보이게 해야함. 큰 숫자가 가장 첫번째로 보이게.

5. ABDeleteOBJGroupSequence (Action Button)
내용 : 마지막 라인 줄 삭제하면, 마지막 라인 null 처리, 중간에 삭제하면 중간에 null처리하고, copymeasure로 한줄씩 copy 한 후에 마지막 라인 null처리. 두줄 이상 삭제 할 경우에도 working 해야함
- (js 필요)
- Sequence FieldBinding이 하나이면서 MaxSequence FieldBinding과 동일하면 아래만 실행
delete data for model [110.005 SDX LPS Priority]
where {
    [Version].[Version Name].[{{Version}}],
    [Plan Type].[Plan Type].[{{PlanType}}],
    [SDX_ObjectiveSequence].[SDX Biz Case Span].[1],
    [Group].[Group ID].[{{GroupID}}],
   [GraphCubeDim_Sequence].[GraphCubeAttr_Sequence].filter(#.Name in {{#ibplList Sequence}})
};

- 아니라면 아래 {{Sequence}} 안에 ,로 여러개 넣고 실행 후에 빈칸을 땡겨주는 작업 필요 (재정렬은 ABAddOBJGroupSequence 에 있는   구문 사용)
delete data for model [110.005 SDX LPS Priority]
where {
    [Version].[Version Name].[{{Version}}],
    [Plan Type].[Plan Type].[{{PlanType}}],
    [SDX_ObjectiveSequence].[SDX Biz Case Span].[1],
    [Group].[Group ID].[{{GroupID}}],
    [GraphCubeDim_Sequence].[GraphCubeAttr_Sequence].filter(#.Name in {{#ibplList Sequence}})
};


=============================== add ====================================
Createmember
( [Group].[Group ID] = {,"{{NewGroupID}}"}
, [Group].[Group Type] = {,"OBJ_Group"}
, [Group].[Description]={"{{NewGroupIDDescription}}",}
);

ddl {
  "Action": "Create",
  "ModelType": "PicklistValue",
  "Payload": {
    "PicklistName": "SDXCreateGroup",
    "DisplayName": "{{NewGroupID}}",
    "Value": "{{NewGroupID}}",
    "DisplayPosition": 0,
    "Icon": null,
    "Color": null,
    "Image": null,
    "CrudAction": 0,
    "ModuleId": "13acb48d-e6bb-4865-a625-202c58b204e8"
  }
};

cartesian scope:
( [Version].[Version Name].[{{Version}}]
* [Plan Type].[Plan Type].[{{PlanType}}]
* [Group].[Group ID].[{{NewGroupID}}]
* [GraphCubeDim_Sequence].[GraphCubeAttr_Sequence].[1]
* [SDX_ObjectiveSequence].[SDX Biz Case Span].[1]
);
Measure.[SDX Biz Case Span Association] = 1;
end scope;

================================ delete ===========================
{{#each GroupID}}
delete data for model [110.005 SDX LPS Priority]
where {
    [Version].[Version Name].[{{Version}}],
    [Plan Type].[Plan Type].[{{Version}}],
    [Group].[Group ID].[{{this}}]
};

ddl {
  "Action": "Delete",
  "ModelType": "PicklistValue",
  "Payload": {
    "PicklistName": "SDXCreateGroup",
    "Value": "{{this}}",
    "ModuleId": "13acb48d-e6bb-4865-a625-202c58b204e8",
    "CrudAction": 0
  }
};
{{/each}}

============================= copy ======================
Createmember
( [Group].[Group ID] = {,"{{NewGroupID}}"}
, [Group].[Group Type] = {,"OBJ_Group"}
, [Group].[Description]={"{{NewGroupIDDescription}}",}
);

ddl {
  "Action": "Create",
  "ModelType": "PicklistValue",
  "Payload": {
    "PicklistName": "SDXCreateGroup",
    "DisplayName": "{{NewGroupID}}",
    "Value": "{{NewGroupID}}",
    "DisplayPosition": 0,
    "Icon": null,
    "Color": null,
    "Image": null,
    "CrudAction": 0,
    "ModuleId": "13acb48d-e6bb-4865-a625-202c58b204e8"
  }
};

cartesian scope:
( [Version].[Version Name].[{{Version}}]
* [Plan Type].[Plan Type].[{{PlanType}}]
* [Group].[Group ID].[{{NewGroupID}}]
* [GraphCubeDim_Sequence].[GraphCubeAttr_Sequence].[1]
* [SDX_ObjectiveSequence].[SDX Biz Case Span].[1]
);
Measure.[SDX Biz Case Span Association] = 1;
end scope;


COPYMEASURE(
[Group].[Group ID] = {{"{{SourceGroupID}}","{{NewGroupID}}"}},
{
Measure.[SDX Biz Case Definition],
Measure.[SDX Biz Case Span Association]},
 rollbackonconflict: false, nullifytargetintersections: true
)
WHERE {
Version.[Version Name].[{{Version}}],
[Plan Type].[Plan Type].[{{PlanType}}]
};

================== delete ====================
delete data for model [110.005 SDX LPS Priority]
where {
    [Version].[Version Name].[{{Version}}],
    [Plan Type].[Plan Type].[{{PlanType}}],
    [SDX_ObjectiveSequence].[SDX Biz Case Span].[1],
    [Group].[Group ID].[{{GroupID}}],
    [GraphCubeDim_Sequence].[GraphCubeAttr_Sequence].filter(#.Name in {{#ibplList Sequence}})
};
*/


/**************************************************************************************
프로그램명  : o9.NSCM.JSObjectivePriorityDefinition
화면명     : Objective Priority Definition
개발자     : sungmin0.lim
최초생성   : 2025.09.18
**************************************************************************************/