define('o9.NSCM.JSQuotaMtrl', ['o9/data/query', 'o9/data/cellset', 'o9.NSCM.commonLib'], function () {
	const programName = "o9.NSCM.JSQuotaMtrl";

    var fn_dataCheck = function(o9Params){
        try{
            const commonLib = require('o9.NSCM.commonLib');
            const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
            vdCommon.setLogLevel("Debug");

            // 파라메타 가져오기
            vdCommon.printParams(o9Params);
            let parsedParams = JSON.parse(o9Params);
            var chkGroupID = parsedParams.chkGroupID;
            var chkToItem = parsedParams.chkToItem;
            var chkSubLocation = parsedParams.chkSubLocation;
            let rtnValue = 0;
            vdCommon.debug("["+chkGroupID.length+"]["+chkToItem.length+"]["+chkSubLocation.length+"]");

            if(chkGroupID.length > 1 || chkToItem.length > 1 || chkSubLocation.length > 1){
                rtnValue = 1;
                RuleOutputToUI = { Status : 'Error', Message : "You cannot select multiple rows." };
            }

            vdCommon.printStep(">>>>>>>>>>>  fn_dataCheck End");
            vdCommon.programEnd();

            return rtnValue;

        }catch ( e ) {
            RuleOutputToUI = { Status : 'Error', Message : "Js Logic Error : " + e.message };
            return;
        }
    }

    var fn_groupNamedataCheck = function(o9Params){
        try{
            /*Group ID Status 체크*/
            const commonLib = require('o9.NSCM.commonLib');
            const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
            vdCommon.setLogLevel("Debug");

            // 파라메타 가져오기
            vdCommon.printParams(o9Params);
            let parsedParams = JSON.parse(o9Params);
            var chkGroupID = parsedParams.chkGroupID;
            let rtnValue = 0;
            vdCommon.debug("["+chkGroupID.length+"]");


            if(chkGroupID.length > 1 ){
                rtnValue = 1;
                RuleOutputToUI = { Status : 'Error', Message : "You cannot select multiple rows." };
            }

            //Confirm 여부를 조회한다.
            let selectResult = vdCommon.selectList(["&CWVUI",
                                            "[Item Material].[Item Material]",
                                            "[Sub Location].[Sub Location]",
                                            "[Group].[Group ID].["+chkGroupID[0]+"]"],
                                            ["Measure.[Global Quota Mtrl_ASN]",
                                            "Measure.[Global Quota Mtrl_InterdepenF]",
                                            "Measure.[Global Quota Mtrl_Status]",
                                            "Measure.[Global Quota Mtrl_Validation]"
                                            ],
                                            "","","");
            let result = vdCommon.fn_makeCombo(selectResult, {MeasureName : "Global Quota Mtrl_Status", existAll : false, Sort : "DisplayName", isDisplayNameWithCode : false});

            let chkStatus = false;
            for(var k=0 ; k < result.length; k++){
                var sData = String(result[0].Name).toUpperCase();
                if(sData == "CONFIRM"){
                    chkStatus = true;
                }
            }

            if(chkStatus){
                rtnValue = 1;
                RuleOutputToUI = { Status : 'Error', Message : "Confirm status cannot be modified." };
            }

            vdCommon.programEnd();

            return rtnValue;

        }catch ( e ) {
            RuleOutputToUI = { Status : 'Error', Message : "Js Logic Error : " + e.message };
            return;
        }
    }

    var fn_groupIdCombo = function(o9Params){
        try{
            const commonLib = require('o9.NSCM.commonLib');
            const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
            vdCommon.setLogLevel("Debug");

            vdCommon.printParams(o9Params);
            // 파라미터 가져오기
            var parsedParams = JSON.parse(o9Params);
            var fbVersion = parsedParams.fbVersion;

            let selectQuery = 'Select ([Version].[Version Name].['+fbVersion+'] * [Group].[Group ID].filter(#.Name startswith "P") ) on row, ';
            selectQuery += "({Measure.[Global Quota Mtrl Sub_Group Name]}) on column orderby Measure.[Global Quota Mtrl Sub_Group Name];";

            let result = vdCommon.selectQueryList("fn_groupID Select", selectQuery);
            let comboList = [];
            for(var k=0; k < result.cs.rowCount; k++){
                let name =  result.cs.row(k).cell(result.cs.memberColumnIndex("Group", "Group ID")).Name;
                let displayName = result.cs.row(k).cell(result.cs.measureColumnIndex("Global Quota Mtrl Sub_Group Name"));

                if(displayName != undefined && displayName.length > 0){
                    displayName = displayName + " (" + name + ")";
                }else{
                    displayName = "(" + name + ")";
                }

                comboList.push({ Name : name, DisplayName : displayName});
            }

            vdCommon.programEnd();
            return comboList;

        }catch ( e ) {
            RuleOutputToUI = { Status : 'Error', Message : "Js Logic Error : " + e.message };
            return;
        }
    }

    var fn_chgGroupName = function(o9Params){
        try {

            const commonLib = require('o9.NSCM.commonLib');
            const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
            vdCommon.setLogLevel("Debug");

            vdCommon.printParams(o9Params);

            // 파라미터 가져오기
            var parsedParams = JSON.parse(o9Params);
            var fbVersion = parsedParams.fbVersion;
            var fbGroupID = parsedParams.fbGroupID;
            var fbGroupName = parsedParams.fbGroupName;

            var result = vdCommon.selectList(
                                ["[Version].[Version Name].["+fbVersion+"]",
                                 "[Group].[Group ID].[" + fbGroupID + "]"],
                                ["Measure.[Global Quota Mtrl Sub_Group Name]"],
                                 "", "", "");

            if ( result.cs.rowCount > 0 ) {
                vdCommon.updateMeasure(
                    ["[Version].[Version Name].["+fbVersion+"]",
                    "[Group].[Group ID].[" + fbGroupID + "]"],
                    ['Measure.[Global Quota Mtrl Sub_Group Name] = "'+fbGroupName+'";']);
            }else{
                vdCommon.createMeasure(
                    ["[Version].[Version Name].["+fbVersion+"]",
                    "[Group].[Group ID].[" + fbGroupID + "]"],
                    ['Measure.[Global Quota Mtrl Sub_Group Name] = "'+fbGroupName+'";']);
            }

            vdCommon.programEnd();

        } catch ( e ) {
            RuleOutputToUI = { Status : 'Error', Message : "Js Logic Error : " + e.message };
            return 1;
        }
    };

    var fn_plantAdd = function(o9Params){
        try {
            const commonLib = require('o9.NSCM.commonLib');
            const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
            vdCommon.setLogLevel("Debug");

            vdCommon.printParams(o9Params);
            // 파라미터 가져오기
            var parsedParams = JSON.parse(o9Params);
            var fbVersion = parsedParams.fbVersion;
            var fbGroupID = parsedParams.fbGroupID;
            var fbSubLocation = parsedParams.fbSubLocation;
            var fbToItem = parsedParams.fbToItem;
            var fbLocation = parsedParams.fbLocation;

            //Global Quota 데이타 조회
            let result = vdCommon.selectList(
                                            ["[Version].[Version Name].["+fbVersion+"]",
                                            "&MPHroizon",
                                            "[Item Material].[Item Material].["+fbToItem+"]",
                                            "[Sub Location].[Sub Location].["+fbSubLocation+"]",
                                            "[Group].[Group ID].[" + fbGroupID + "]"],
                                            ["Measure.[Global Quota Mtrl W_Portion]",
                                            "Measure.[Global Quota Mtrl W_Quota Sync]"],
                                            "", "", "");
            vdCommon.printCsData(result, 3);

            for ( var m = 0; m < fbLocation.length; m++ ) {
                let queryStr = "";
                vdCommon.debug("fbLocation : " + fbLocation[m]);
                for ( var q = 0; q < result.cs.rowCount; q++ ) {
                    let week = result.cs.row(q).cell(result.cs.memberColumnIndex("Time", "Week")).Name;
                    let item = result.cs.row(q).cell(result.cs.memberColumnIndex("Item Material", "Item Material")).Name;
                    let subLocation = result.cs.row(q).cell(result.cs.memberColumnIndex("Sub Location", "Sub Location")).Name;
                    let wPortionQty = result.cs.row(q).cell(result.cs.measureColumnIndex("Global Quota Mtrl W_Portion"));

                    //Plant Quota 데이타 생성
                    queryStr += vdCommon.createMeasureQuery(
                        ["[Version].[Version Name].["+fbVersion+"]",
                        "[Time].[Week].["+week+"]",
                        "[Location].[Location].[" + fbLocation[m] + "]",
                        "[Item Material].[Item Material].[" + item + "]",
                        "[Sub Location].[Sub Location].["+subLocation+"]",
                        "[Group].[Group ID].[" + fbGroupID + "]"
                        ],
                        ["Measure.[Plant Quota Mtrl W_Portion] = "+wPortionQty+";"]);
                }
                vdCommon.executeQuery("Batch Query" , queryStr);
            }

            vdCommon.programEnd();
        } catch ( e ) {
            RuleOutputToUI = { Status : 'Error', Message : "Js Logic Error : " + e.message };
            return;
        }
    };

    var fn_locationCombo = function(o9Params){
        try {
            const commonLib = require('o9.NSCM.commonLib');
            const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
            vdCommon.setLogLevel("Debug");

            vdCommon.printParams(o9Params);

            // 파라미터 가져오기
            var parsedParams = JSON.parse(o9Params);
            var fbVersion = parsedParams.fbVersion;
            var fbGroupID = parsedParams.fbGroupID;
            var fbSubLocation = parsedParams.fbSubLocation;
            var fbToItem = parsedParams.fbToItem;

            //선택한 GroupID의  Item 정보를 조회한다.
            //Global Quota Mtrl 메저그룹 조회
            /*var selectItemResult = vdCommon.selectList(
                                            ['[Version].[Version Name].['+fbVersion+']',
                                            '[Group].[Group ID].['+fbGroupID+']',
                                            '[Item Material].[Item Material]',
                                            '[Sub Location].[Sub Location]'],
                                             ["Measure.[Global Quota Mtrl_ASN]",
                                             "Measure.[Global Quota Mtrl_InterdepenF]",
                                             "Measure.[Global Quota Mtrl_Status]",
                                             "Measure.[Global Quota Mtrl_Validation]"],
                                             "",
                                             "",
                                             "");
            */
            //Global Quota Mtrl W 메져그룹 조회
            var selectItemResult = vdCommon.selectList(
                                        ['[Version].[Version Name].['+fbVersion+']',
                                        '[Item Material].[Item Material].['+fbToItem+']',
                                        '[Sub Location].[Sub Location]',
                                        '[Group].[Group ID].['+fbGroupID+']',],
                                        ["Measure.[Global Quota Mtrl W_Portion]",
                                        "Measure.[Global Quota Mtrl W_Quota Sync]"],
                                        "Where {&MPHroizon}",
                                        "",
                                        "");

            let selectItemCombo = vdCommon.fn_makeCombo(selectItemResult, {DimName : "Item Material", DimAttbName : "Item Material", existAll : false, Sort : "DisplayName", isDisplayNameWithCode : false});
            let itemList = '';
            let comboList = [];
            if(selectItemCombo.length > 0){
                for (var k = 0; k < selectItemCombo.length; k++){
                    if ((k + 1) < itemList.length){
                        itemList += ','
                    }
                    itemList += '"'+selectItemCombo[k].Name+'"';

                }
                //Location  조회함.
                //데이타 정비 후 NameSet 변경이 필요함.(25.02.11)
                //&MFLocation => &NSUISubLocationMFMtrlView
				//250224 JM. Sub Location가져오는게 아니라, Location 가져오는것이므로  &NSUISubLocationMFMtrlView -> &NSUILocationMFMtrlView
                let selectQuery = 'Select (&NSUILocationMFMtrlView) on row, () on column ';
                selectQuery += 'Where { [Version].[Version Name].['+fbVersion+']';
                selectQuery += ', Measure.[Item Mtrl Site Asn_Cur Status] in {"PLANNED", "ACTIVE"}' ;
                selectQuery += ', [Item Material].[Item Material].filter(#.Name in {'+itemList+'})';
                selectQuery += '} ;';

                let result = vdCommon.selectQueryList("fn_locationCombo(Plant)", selectQuery);
                let comboAll = vdCommon.fn_makeCombo(result, {DimName : "Location", DimAttbName : "Location", existAll : false, Sort : "DisplayName", isDisplayNameWithCode : true});

                //기존 등록된 Location은 제외함.
                let selectReq = vdCommon.selectList(['[Version].[Version Name].['+fbVersion+']',
                                                    '[Location].[Location]',
                                                    '[Time].[Week]',
                                                    '[Item Material].[Item Material].filter(#.Name in {'+itemList+'})',
                                                    '[Group].[Group ID].['+fbGroupID+']',
                                                    '[Sub Location].[Sub Location]'],
                                                    ['Measure.[Plant Quota Mtrl W_Portion]'],
                                                    "","","");
                let comboReg = vdCommon.fn_makeCombo(selectReq, {DimName : "Location", DimAttbName : "Location", existAll : false, Sort : "DisplayName", isDisplayNameWithCode : true});

                comboList = comboAll;
                if(comboReg.length > 0){
                    comboList = comboAll.filter(function(item1, idx1){
                        return comboReg.findIndex(function(item2, idx2){
                            console.log("[chkData]" +idx2 + "<"+item2.Name+">")
                            return item1.Name == item2.Name
                        }) < 0 ;
                    });
                }
            }
            vdCommon.programEnd();
            return comboList;
        } catch ( e ) {
            RuleOutputToUI = { Status : 'Error', Message : "Js Logic Error : " + e.message };
            return;
        }
    };

    var fn_locationCombo_V1 = function(o9Params){
        const commonLib = require('o9.NSCM.commonLib');
        const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
        const vdUtil = new commonLib.VdUtil();
        vdCommon.setLogLevel("Debug");

        try {
            vdCommon.printParams(o9Params);

            // 파라미터 가져오기
            var parsedParams = JSON.parse(o9Params);
            var fbVersion = parsedParams.fbVersion;
            var fbGroupID = parsedParams.fbGroupID;

            // Group ID 에 등록된 Item을 찾는다.
            var result = vdCommon.selectList(["[Item Material].[Item Material]"],
                                             ["Measure.[Global Quota Mtrl W_Portion]"],
                                             "Where {[Version].[Version Name].[" + fbVersion + "], &MPHroizon, [Sub Location].[Sub Location]" +
                                                ", [Group].[Group ID]" + vdUtil.fn_filterStr(fbGroupID) + "}",
                                             "",
                                             "");
            var items = "";
            for ( var i = 0; i < result.cs.rowCount; i++ ) {
                name = result.cs.row(i).cell(result.cs.memberColumnIndex("Item Material", "Item Material")).Name;
                items += ( items == "" ? "" : ",") + name;
            }
            vdCommon.debug("items : " + items);

            // Location 을 찾는다.
            result = vdCommon.selectList(["&NSUILocationMFMtrlView"],
                                         ["Measure.[Item Mtrl Site Asn_Cur Status]"],
                                         "Where { [Version].[Version Name].[" + fbVersion + "]" +
                                            "       ,[Item Material].[Item Material]" + vdUtil.fn_filterStr(items.split(",")) +
                                            '       ,Measure.[Item Mtrl Site Asn_Cur Status] in {"PLANNED", "ACTIVE"} }',
                                         "",
                                         "");

            var comboList = vdCommon.fn_makeCombo(result, {DimName : "Location", DimAttbName : "Location", isDisplayNameWithCode : true});
            vdCommon.debug("ComboData : " + JSON.stringify(comboList));

            vdCommon.programEnd();

            return comboList;
        } catch ( e ) {
            RuleOutputToUI = { Status : 'Error', Message : "Js Logic Error : " + e.message };
            return;
        }
    };

    var fn_plantAdd_V1 = function(o9Params){
        const commonLib = require('o9.NSCM.commonLib');
        const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
        const vdUtil = new commonLib.VdUtil();
        vdCommon.setLogLevel("Debug");

        try {
            vdCommon.printParams(o9Params);

            // 파라미터 가져오기
            var parsedParams = JSON.parse(o9Params);
            var fbVersion = parsedParams.fbVersion;
            var fbGroupID = parsedParams.fbGroupID;
            var fbLocation = parsedParams.fbLocation;

            for ( var i = 0; i < fbGroupID.length; i++ ) {
                var locations = "";

                // Group ID 에 있는 Item 별로....
                var resultItem = vdCommon.selectList(["[Item Material].[Item Material]",
                                                        "[Sub Location].[Sub Location]"],
                                                     ["Measure.[Global Quota Mtrl W_Portion]"],
                                                     "Where {[Version].[Version Name].[" + fbVersion + "], &MPHroizon" +
                                                        ", [Group].[Group ID].[" + fbGroupID[i] + "]}",
                                                     "",
                                                     "");
                for ( var m = 0; m < resultItem.cs.rowCount; m++ ) {
                    var item = resultItem.cs.row(m).cell(resultItem.cs.memberColumnIndex("Item Material", "Item Material")).Name;
                    var subLocation = resultItem.cs.row(m).cell(resultItem.cs.memberColumnIndex("Sub Location", "Sub Location")).Name;

                    // 선택한 Location 별로 "Item Mtrl Site Asn" 에 있는지 체크후에, 주차별 데이타가 없을때 신규로 생성을 한다.
                    for ( var o = 0; o < fbLocation.length; o++ ) {
                        var isExistA = vdCommon.existMeasure(["[Version].[Version Name].[" + fbVersion + "]",
                                                                "[Location].[Location].[" + fbLocation[o] + "]",
                                                                "[Item Material].[Item Material].[" + item + "]"],
                                                             ["Measure.[Item Mtrl Site Asn_Cur Status]"],
                                                             'where { Measure.[Item Mtrl Site Asn_Cur Status] in {"PLANNED", "ACTIVE"} }');

                        var isExistW = vdCommon.existMeasure(["[Version].[Version Name].[" + fbVersion + "]",
                                                                            //"[Time].[Week].[" + week + "]",
                                                                            "[Location].[Location].[" + fbLocation[o] + "]",
                                                                            "[Item Material].[Item Material].[" + item + "]",
                                                                            "[Sub Location].[Sub Location].[" + subLocation + "]",
                                                                            "[Group].[Group ID].[" + fbGroupID[i] + "]"],
                                                             ["Measure.[Plant Quota Mtrl W_Portion]"],
                                                             "");

                        vdCommon.debug("Flag Log =====> GroupID : " + fbGroupID[i] + " , subLocation : " + subLocation + " , item : " + item + " , fbLocation : " + fbLocation[o] +
                                " , item Asn : " + ( isExistA ? "Exist" : "Not Exist") + ", Plant Quota Mtrl W : " + ( isExistW ? "Exist" : "Not Exist"));

                        if ( isExistA && !isExistW ) {
                            var queryStr = "";
                            var resultW = vdCommon.selectList(["&MPHroizon"],
                                                             ["Measure.[Global Quota Mtrl W_Portion]"],
                                                             "Where { [Version].[Version Name].[" + fbVersion + "], [Group].[Group ID].[" + fbGroupID[i] + "] " +
                                                                "       ,[Item Material].[Item Material].[" + item + "] " +
                                                                "       ,[Sub Location].[Sub Location].[" + subLocation + "]}",
                                                             "",
                                                             "");
                            for ( var r = 0; r < resultW.cs.rowCount; r++ ) {
                                var week = resultW.cs.row(r).cell(resultW.cs.memberColumnIndex("Time", "Week")).Name;
                                var qty = resultW.cs.row(r).cell(resultW.cs.measureColumnIndex("Global Quota Mtrl W_Portion"));

                                queryStr += vdCommon.createMeasureQuery(["[Version].[Version Name].[" + fbVersion + "]",
                                                                            "[Time].[Week].[" + week + "]",
                                                                            "[Location].[Location].[" + fbLocation[o] + "]",
                                                                            "[Item Material].[Item Material].[" + item + "]",
                                                                            "[Sub Location].[Sub Location].[" + subLocation + "]",
                                                                            "[Group].[Group ID].[" + fbGroupID[i] + "]"],
                                                                        ["Measure.[Plant Quota Mtrl W_Portion] = " + qty + ";"]);
                            }
                            vdCommon.executeQuery("Batch Query" , queryStr);
                        }

                        if ( isExistA ) {
                            locations = vdUtil.fn_wordDistinctAppend(locations, fbLocation[o]);
                        }
                    }
                }

                // 신규 등록된 Location 이 있으면 추가를 해준다.
                vdCommon.createMeasure(["[Version].[Version Name].[" + fbVersion + "]",
                                            "[Group].[Group ID].[" + fbGroupID[i] + "]",
                                            "[Location].[Location]" + vdUtil.fn_filterStr(locations.split(","))],
                                        ["Measure.[Global Quota Mtrl Plant_ASN] = 1;"]);
            }

            vdCommon.programEnd();
        } catch ( e ) {
            RuleOutputToUI = { Status : 'Error', Message : "Js Logic Error : " + e.message };
            return;
        }
    };

    var fn_plantDelete = function(o9Params){
        const commonLib = require('o9.NSCM.commonLib');
        const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
        const vdUtil = new commonLib.VdUtil();
        vdCommon.setLogLevel("Debug");

        try {
            vdCommon.printParams(o9Params);

            // 파라미터 가져오기
            var parsedParams = JSON.parse(o9Params);
            var fbVersion = parsedParams.fbVersion;
            var fbSelect = parsedParams.fbSelect;

            for ( var i = 0; i < fbSelect.length; i++ ) {
                var row = fbSelect[i];

                vdCommon.deleteMeasure(["[Version].[Version Name].[" + fbVersion + "]",
                                            "[Location].[Location].[" + row.Location.Value + "]",
                                            "[Group].[Group ID].[" + row.GroupId.Value + "]"],
                                        "Plant Quota Mtrl W");

                vdCommon.deleteMeasure(["[Version].[Version Name].[" + fbVersion + "]",
                                            "[Group].[Group ID].[" + row.GroupId.Value + "]",
                                            "[Location].[Location].[" + row.Location.Value + "]"],
                                        "Global Quota Mtrl Plant");
            }

            vdCommon.programEnd();
        } catch ( e ) {
            RuleOutputToUI = { Status : 'Error', Message : "Js Logic Error : " + e.message };
            return;
        }
    };

    return {
        fn_groupNamedataCheck : fn_groupNamedataCheck,
        fn_chgGroupName : fn_chgGroupName,
        fn_dataCheck : fn_dataCheck,
        fn_groupIdCombo : fn_groupIdCombo,
        fn_plantAdd : fn_plantAdd,
        fn_locationCombo : fn_locationCombo,
        fn_locationCombo_V1 : fn_locationCombo_V1,
        fn_plantAdd_V1 : fn_plantAdd_V1,
        fn_plantDelete : fn_plantDelete
    };
});

/**************************** o9.NSCM.JSQuotaMtrl ****************************
    2025-04-18 : fn_locationCombo_V1, fn_plantAdd_V1, fn_plantDelete 기능 추가
*********************************************************************/