define('o9.NSCM.JSKnoxApprovalAllGroup', ['o9/data/query', 'o9/data/cellset', 'o9.NSCM.commonLibVD'], function () {

/**************************************************************************************
    프로그램명  : o9.NSCM.JSKnoxApprovalAllGroup
    화면명     : Knox 결재 그룹 관리(All)
    API 개발자 : sungmin0.lim
    최초생성   : 2026.03.20
**************************************************************************************/

    // fn_cLib 를 통해서 commonLib 를 생성
    var fn_cLib = function(name) {
        return new commonLib.VdCommon(name);
    }
    var fn_cUtil = function() {
        return new commonLib.VdUtil();
    }
    
    const programName = "o9.NSCM.JSKnoxApprovalAllGroup";
    const commonLib = require('o9.NSCM.commonLibVD');
    const cUtil = fn_cUtil();

    var fn_add = function(o9Params){
        const cLib = fn_cLib(programName + "." + arguments.callee.name);
        cLib.setLogLevel("Debug");

        try {
            cLib.printParams(o9Params);

            // 파라미터 가져오기
            var p = JSON.parse(o9Params);

            // Max 값을 구한다.
            var result = cLib.selectList(["[Version].[Version Name].[" + p.fbVersion + "]"
                                            ,"[Seq].[Seq]"]
                                         ,["Measure.[Knox Approval All Group_Code]"]
                                         ,""
                                         ,"orderby [Seq].[Seq].Key desc"
                                         ,"limit 1");
            var seq = 1;
            if ( result.cs.rowCount > 0 ) {
                seq = parseInt(cUtil.fn_getDimValue(result, 0, "Seq", "Seq")) + 1;
            }

            cLib.createMeasure(["[Version].[Version Name].[" + p.fbVersion + "]"
                                    ,"[Seq].[Seq].[" + seq + "]"]
                               ,['Measure.[Knox Approval All Group_Parent Code] = "' + p.fbParentCode + '";'
                                    ,'Measure.[Knox Approval All Group_Code] = "' + p.fbCode + '";'
                                    ,'Measure.[Knox Approval All Group_Name] = "' + p.fbName + '";']);

            cLib.programEnd();
        } catch ( e ) {
            cLib.error(e.message);
            RuleOutputToUI = { Status : 'Error', Message : "Js Logic Error : " + e.message };
            return;
        }
    };

    var fn_delete = function(o9Params){
        const cLib = fn_cLib(programName + "." + arguments.callee.name);
        cLib.setLogLevel("Debug");

        try {
            cLib.printParams(o9Params);

            // 파라미터 가져오기
            var p = JSON.parse(o9Params);

            for ( var i = 0; i < p.fbSelect.length; i++ ) {
                var row = p.fbSelect[i];

                cLib.deleteMeasure(["[Version].[Version Name].[" + p.fbVersion + "]"
                                            ,"[Seq].[Seq].[" + row.Seq.Value + "]"]
                                       ,"Knox Approval All Group");

                cLib.deleteMeasure(["[Version].[Version Name].[" + p.fbVersion + "]"
                                            ,"[Seq].[Seq].[" + row.Seq.Value + "]"]
                                       ,"Knox Approval All Group Line");
            }

            cLib.programEnd();
        } catch ( e ) {
            cLib.error(e.message);
            RuleOutputToUI = { Status : 'Error', Message : "Js Logic Error : " + e.message };
            return;
        }
    };

    var fn_lineAdd = function(o9Params){
        const cLib = fn_cLib(programName + "." + arguments.callee.name);
        cLib.setLogLevel("Debug");

        try {
            cLib.printParams(o9Params);

            // 파라미터 가져오기
            var p = JSON.parse(o9Params);

            // Max 값을 구한다.
            var result = cLib.selectList(["[Version].[Version Name].[" + p.fbVersion + "]"
                                            ,"[Seq].[Seq].[" + p.fbSeq + "]"
                                            ,"[Seq1].[Seq1]"]
                                         ,["Measure.[Knox Approval All Group Line_UserId]"]
                                         ,""
                                         ,"orderby [Seq1].[Seq1].Key desc"
                                         ,"limit 1");
            var seq1 = 1;
            if ( result.cs.rowCount > 0 ) {
                seq1 = parseInt(cUtil.fn_getDimValue(result, 0, "Seq1", "Seq1")) + 1;
            }

             var role = {"1" : "결재", "2" : "합의", "3" : "후결", "4" : "병렬합의", "7" : "병렬결재", "9" : "통보"};
            var order = {"1" : 1, "2" : 2, "3" : 3, "4" : 4, "7" : 7, "9" : 9};
            cLib.createMeasure(["[Version].[Version Name].[" + p.fbVersion + "]"
                                    ,"[Seq].[Seq].[" + p.fbSeq + "]"
                                    ,"[Seq1].[Seq1].[" + seq1 + "]"]
                               ,['Measure.[Knox Approval All Group Line_UserId] = "' + p.fbUserId + '";'
                                    ,'Measure.[Knox Approval All Group Line_Role] = "' + p.fbRole + '";'
                                    ,'Measure.[Knox Approval All Group Line_Role Name] = "' + role[p.fbRole] + '";'
                                    ,'Measure.[Knox Approval All Group Line_Order] = ' + order[p.fbRole] + ';']);

            cLib.programEnd();
        } catch ( e ) {
            cLib.error(e.message);
            RuleOutputToUI = { Status : 'Error', Message : "Js Logic Error : " + e.message };
            return;
        }
    };

    var fn_lineUpdate = function(o9Params){
        const cLib = fn_cLib(programName + "." + arguments.callee.name);
        cLib.setLogLevel("Debug");

        try {
            cLib.printParams(o9Params);

            // 파라미터 가져오기
            var p = JSON.parse(o9Params);

            var role = {"1" : "결재", "2" : "합의", "3" : "후결", "4" : "병렬합의", "7" : "병렬결재", "9" : "통보"};
            var order = {"1" : 1, "2" : 2, "3" : 3, "4" : 4, "7" : 7, "9" : 9};
            cLib.updateMeasure(["[Version].[Version Name].[" + p.fbVersion + "]"
                                    ,"[Seq].[Seq].[" + p.fbSeq + "]"
                                    ,"[Seq1].[Seq1].[" + p.fbSeq1 + "]"]
                               ,['Measure.[Knox Approval All Group Line_Role] = "' + p.fbRole + '";'
                                    ,'Measure.[Knox Approval All Group Line_Role Name] = "' + role[p.fbRole] + '";'
                                    ,'Measure.[Knox Approval All Group Line_Order] = ' + order[p.fbRole] + ';']);

            cLib.programEnd();
        } catch ( e ) {
            cLib.error(e.message);
            RuleOutputToUI = { Status : 'Error', Message : "Js Logic Error : " + e.message };
            return;
        }
    };

    var fn_lineDelete = function(o9Params){
        const cLib = fn_cLib(programName + "." + arguments.callee.name);
        cLib.setLogLevel("Debug");

        try {
            cLib.printParams(o9Params);

            // 파라미터 가져오기
            var p = JSON.parse(o9Params);

            for ( var i = 0; i < p.fbSelect.length; i++ ) {
                var row = p.fbSelect[i];

                cLib.deleteMeasure(["[Version].[Version Name].[" + p.fbVersion + "]"
                                            ,"[Seq].[Seq].[" + row.Seq.Value + "]"
                                            ,"[Seq1].[Seq1].[" + row.Seq1.Value + "]"]
                                       ,"Knox Approval All Group Line");
            }

            cLib.programEnd();
        } catch ( e ) {
            cLib.error(e.message);
            RuleOutputToUI = { Status : 'Error', Message : "Js Logic Error : " + e.message };
            return;
        }
    };

    var fn_roleCombo = function(o9Params){
        const cLib = fn_cLib(programName + "." + arguments.callee.name);
        cLib.setLogLevel("Debug");

        try {
            cLib.printParams(o9Params);

            var comboList = cLib.fn_makeCombo(null, {ComboCodes : ["1","2","3","4","7","9"]
                                                        ,ComboValues : ["결재","합의","후결","병렬합의","병렬결재","통보"]});
            cLib.debug("ComboData : " + JSON.stringify(comboList.slice(0,3)));

            cLib.programEnd();

            return comboList;
        } catch ( e ) {
            cLib.error(e.message);
            RuleOutputToUI = { Status : 'Error', Message : "Js Logic Error : " + e.message };
            return;
        }
    };

    var fn_parentCodeCombo = function(o9Params){
        const cLib = fn_cLib(programName + "." + arguments.callee.name);
        cLib.setLogLevel("Debug");

        try {
            cLib.printParams(o9Params);

            var p = JSON.parse(o9Params);

            var result = cLib.selectList(["[Version].[Version Name].[" + p.fbVersion + "]"
                                            ,"Seq.[Seq]"]
                                         ,["Measure.[Knox Approval All Group_Parent Code]"]
                                         ,""
                                         ,"orderby Measure.[Knox Approval All Group_Parent Code]"
                                         ,"");
            var comboList = cLib.fn_makeCombo(result, {MeasureName : "Knox Approval All Group_Parent Code"});
            cLib.debug("ComboData : " + JSON.stringify(comboList.slice(0,3)));

            cLib.programEnd();

            return comboList;
        } catch ( e ) {
            cLib.error(e.message);
            RuleOutputToUI = { Status : 'Error', Message : "Js Logic Error : " + e.message };
            return;
        }
    };

    var fn_blankCombo = function(o9Params){
        const cLib = fn_cLib(programName + "." + arguments.callee.name);
        cLib.setLogLevel("Debug");

        try {
            var comboList = cLib.fn_makeCombo(null, {ComboCodes : ["Enter characters to search"], ComboValues : ["Enter characters to search"]});
            cLib.debug("ComboData : " + JSON.stringify(comboList));

            cLib.programEnd();

            return comboList;
        } catch ( e ) {
            cLib.error(e.message);
            RuleOutputToUI = { Status : 'Error', Message : "Js Logic Error : " + e.message };
            return;
        }
    };

    var fn_userIdCombo = function(o9Params){
        const cLib = fn_cLib(programName + "." + arguments.callee.name);
        cLib.setLogLevel("Debug");

        try {
            cLib.printParams(o9Params);

            var p = JSON.parse(o9Params);

            var userName = cLib.selectResult('CurrentUser().Name');

            var comboList = [];
            if ( p.fbSearch != "Enter characters to search" ) {
                // 데이타 삭제
                cLib.deleteMeasure(["[Version].[Version Name].[" + p.fbVersion + "]", "[Personnel].[Email].[" + userName + "]"], 'Knox Employee');

                // Knox 파이썬 실행
                var execQuery = 'EXEC plugin instance [PY_Knox_Employees] ' +
                                'for measures {[Knox Employee_UserId]} ' +
                                'using scope ( [Version].[Version Name].[' + p.fbVersion + '] * [Personnel].[Email].[' + userName + '] ) ' +
                                'using arguments { (pVersionName, "' + p.fbVersion + '"), ' +
                                '                  (pEmail, "' + userName + '"), ' +
                                '                  (pField, "name"), ' +
                                '                  (pValue, "' + p.fbSearch + '"), ' +
                                '                  (ExecutionMode, "MediumWeight"), (MaxSliceTableCells, 200000000), (MaxConcurrency, 1 )};'
                cLib.executePython("PY_Knox_Employees", execQuery);

                // 싱글정보 가져오기
                var result = cLib.selectList(["[Version].[Version Name].[" + p.fbVersion + "]"
                                                    ,"[Personnel].[Email].[" + userName + "]"
                                                    ,"Seq.[Seq]"]
                                                 ,["Measure.[Knox Employee_UserId]"
                                                    ,"Measure.[Knox Employee_Email]"
                                                    ,"Measure.[Knox Employee_UserName]"
                                                    ,"Measure.[Knox Employee_CompanyName]"
                                                    ,"Measure.[Knox Employee_DepartmentName]"]
                                                 ,"", "", "");
                for ( var i = 0; i < result.cs.rowCount; i++ ) {
                    comboList.push({"Name" : cUtil.fn_getMeaValue(result, i, "Knox Employee_UserId")
                                        ,"DisplayName" : cUtil.fn_getMeaValue(result, i, "Knox Employee_UserName") +
                                                            " / " + cUtil.fn_getMeaValue(result, i, "Knox Employee_Email") +
                                                            " / " + cUtil.fn_getMeaValue(result, i, "Knox Employee_CompanyName") +
                                                            " / " + cUtil.fn_getMeaValue(result, i, "Knox Employee_DepartmentName")});
                }
                cLib.debug("ComboData : " + JSON.stringify(comboList.slice(0,3)));
            }

            cLib.programEnd();

            return comboList;
        } catch ( e ) {
            cLib.error(e.message);
            RuleOutputToUI = { Status : 'Error', Message : "Js Logic Error : " + e.message };
            return;
        }
    };

    return {
        fn_add : fn_add
        ,fn_delete : fn_delete
        ,fn_lineAdd : fn_lineAdd
        ,fn_lineUpdate : fn_lineUpdate
        ,fn_lineDelete : fn_lineDelete
        ,fn_roleCombo : fn_roleCombo
        ,fn_parentCodeCombo : fn_parentCodeCombo
        ,fn_blankCombo : fn_blankCombo
        ,fn_userIdCombo : fn_userIdCombo
    };
});

/*************************************************************************************************************

***************************************** o9.NSCM.JSKnoxApprovalAllGroup ****************************************/