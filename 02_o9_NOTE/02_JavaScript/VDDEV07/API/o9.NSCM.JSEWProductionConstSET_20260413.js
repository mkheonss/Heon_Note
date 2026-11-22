define('o9.NSCM.JSEWProductionConstSET', ['o9/data/query', 'o9/data/cellset', 'o9.NSCM.commonLibVD'], function(){

    /*--------------------------------------------------------------------------------------------------*/
    // 프로그램명 : o9.NSCM.JSEWProductionConstSET
    // 화면명 : Production Constraint (EW) - SET
    // EW 개발자 : 정형철P
    // API 개발자 : 이숙영B
    // Action Button : EWProductionConstSET
    // 최초생성 : 2025.09.09 / syif1380.lee
    /*--------------------------------------------------------------------------------------------------*/

    // fn_cLib 를 통해서 commonLib 를 생성 // 2026.03.26 공통적용변경
    var fn_cLib = function(name) {
        return new commonLib.VdCommon(name);
    }
    var fn_cUtil = function() {
        return new commonLib.VdUtil();
    }

    const programName = "o9.NSCM.JSEWProductionConstSET";
    const commonLib = require('o9.NSCM.commonLibVD');   // 2026.03.26 공통적용변경
    const cUtil = fn_cUtil();                           // 2026.03.26 공통적용변경
    
    const queryModule = require('o9/data/query');
    const Horizon    = "&MPHorizon";        // Const Grp Detail W 생성 주차 기준
    const AheadHorizon = "&MDMHorizon";     // Build Ahead 생성 주차 기준
    const MFC_SET    = "MFC_S";
    const SRC_SET    = "SRC_S";

    let MakeWeekOrg     = {};           // MPHorizon 범위의 전체 주차
    let MakeWeekRough   = {};           // MPHorizon (-4 ~ 4) 범주의 주차

    //================================================== -[Combo Data] ==========================================//
    /*------------------------------------------------------------------------------------------------------------
    From Site           > EWCommonVD           >  { "fbFuncName" : "fn_cb_siteMF", "fbParams" : {} }
    To Site             > EWCommonVD           >  { "fbFuncName" : "fn_cb_siteDC", "fbParams" : {} }
    Product Group       > EWCommonVD           >  { "fbFuncName" : "fn_cb_setProductGroup", "fbParams" : {} }
    Definition          > EWCommonVD           >  { "fbFuncName" : "fn_cb_setDefinition", "fbParams" : { } }
    Project             > EWCommonVD           >  { "fbFuncName" : "fn_cb_setProject", "fbParams" : { } }
    MktName             > EWCommonVD           >  { "fbFuncName" : "fn_cb_setMarketingName", "fbParams" : { } }
    Inch                > EWCommonVD           >  { "fbFuncName" : "fn_cb_setInch", "fbParams" : { } }
    Year                > EWCommonVD           >  { "fbFuncName" : "fn_cb_setYear", "fbParams" : { } }
    -------------------------------------------------------------------------------------------------------------*/
	var fn_loadFunction = function(o9Params){
        const cLib = fn_cLib(programName + "." + arguments.callee.name);
        cLib.setLogLevel("Debug");

		try {
            let returnData = {};
            let obj = this;

            cLib.printParams(o9Params);

            // 파라메타 가져오기
            var parsedParams = JSON.parse(o9Params);
			var fbFuncName = parsedParams.fbFuncName;

            if ( functionMap[fbFuncName] == undefined ) {
                return { "Code" : 1, "Msg" : "No Function" };
            }

            var rtn = functionMap[fbFuncName](parsedParams);

            cLib.programEnd();
            return rtn;
        } catch ( e ) {
            cLib.error(e.message);
            return { "Code" : -1, "Msg" : e.message };
        }
	};

    // ################################################################################################################
    // #          :  Ref.Time ( Const Grp_Refer Time ) 에 따른 Qty 세팅
    // #           무한대 null 로 변경 2025.04.25 (노보람p 요청)
    // #           - Even W  (Even Week)  : 짝수주차에만 Production QTY 값 입력. 나머지는 0으로 입력. 엔진은 무한대로 해석
    // #           - Odd W   (Odd Week)   : 홀수주차에만 Production QTY 값 입력. 나머지는 0으로 입력. 엔진은 무한대로 해석
    // #           - Every W (every week) : start~end 사이 모든주차에 qty 입력
    // #           - Last W  (last Week)  : 1st 와 동일. 월별 마지막주차.
    // #           - 1st W   (1st Week)   : 월별 1주차에만 Production QTY 값 입력. start 가 월중 이면, start의 월은 0, 차월의 첫주부터 값~
    // #           - 2st W   (2st Week)   : 월별 2주차
    // #           - 3st W   (3st Week)   : 월별 3주차
    // #           - 4st W   (4st Week)   : 월별 4주차
    // #           - null       : 사용자 정의 안함 ( 차후 정의 필요 )
    // #           ** 월별의 첫주차, 마지막 주차가 겹칠 경우는??  6월의 마지막주차가 7월에 첫주차가 될수 있음 ( Partial )
    // ################################################################################################################
    // YYYYWW -> 끝 두 자리 주차로 짝/홀
    var refEvenOdd = function(weekStr){
        const ww = Number(String(weekStr).slice(-2));
        return ww %2 === 0 ? "even" : "odd";
    };

    // 월별 1주차, 2주차, 3주차, 4주차, .. last 주차 정의
    var makeWeekRowsISO = function(map){
        // 1.기본 rows + ref(even/odd)
        const rows = Object.entries(map).map(([week, day]) => ({
            week, day,
            ref: refEvenOdd(week),
        }));

        // 2. 월별 그룹핑
        const byMonth = new Map();
        for ( const r of rows ){
            const month = r.day.slice(0,7); // "YYYY-MM"
            if ( !byMonth.has(month) ) byMonth.set(month, []);
            byMonth.get(month).push(r);
        }

        // 3. 각 월에서 가장 이른/늦은 날짜에 ref_day 부여
        for (const list of byMonth.values()) {
            list.sort((a,b) => a.day.localeCompare(b.day)); // ISO 문자열 비교 == 시간순
            if(list.length){
                list[0].ref_day = "1st";
                list[list.length - 1].ref_day = "last";

                // ref_week (1주차, 2주차, ...)
                list.forEach((r, idx) => {
                    r.ref_week = `${idx + 1}st`;
                });
            }
        }
        return rows;
    }

    // MPHorizon 주차 조회 및 세팅
    var fn_getHorizon = function(){
        const cLib = fn_cLib(programName + "." + arguments.callee.name);
        cLib.setLogLevel("Debug");

        let MPHorizonMapOrg = cLib.fn_getMondayForNS("MPHorizon");    // &MPHorizon Data

        // &MPHorizon.first 전 4주차 ~ &MPHorizon.last 후 4주차 (넉넉히 가져와서 1st,2st 계산 목적)
        // select ( Time.[Day] * Time.Week.filter(#.Key <= &MPHorizon.last.LeadOffset(5).Key && #.Key > &MPHorizon.first.LeadOffset(-5).Key))  on row, () on column where { Time.[Day of Week].[MON] }  ;
        var result = cLib.selectList(["Time.[Day]", "Time.Week.filter(#.Key <= &MPHorizon.last.LeadOffset(5).Key && #.Key > &MPHorizon.first.LeadOffset(-5).Key)"],
                                    [], "where { Time.[Day of Week].[MON] }", "", "");

        var MPHorizonMapRough = {};
        for ( var i = 0; i < result.cs.rowCount; i++ ) {
            var week = result.cs.row(i).cell(result.cs.memberColumnIndex("Time", "Week")).Name;
            var day = result.cs.row(i).cell(result.cs.memberColumnIndex("Time", "Day")).Name;
            MPHorizonMapRough[week] = day;
        }

        // 상단 변수에 정의 됨.
        MakeWeekOrg = makeWeekRowsISO(MPHorizonMapOrg);           // MPHorizon 범위의 전체 주차
        MakeWeekRough = makeWeekRowsISO(MPHorizonMapRough);       // MPHorizon (-4 ~ 4) 범주의 주차
    };

    // 저장 전 Validation Check
    var fn_validation = function(parsedParams){
        const cLib = fn_cLib(programName + "." + arguments.callee.name);
        cLib.setLogLevel("Debug");

        try {
            let box = {};
            let errCnt = 0;     // 오류건수

            for ( var i=0; i<parsedParams.fbGridRows.length; i++){

                let row = parsedParams.fbGridRows[i];

                rowstatus = row["rowstatus"];
                rowindex = row["rowindex"];
                row["rowmsg"] = null;
                let versionName = cUtil.fn_qDimVersionName(parsedParams);
                cLib.debug("### fn_validation >> versionName : "+versionName);

                let gk = row.rowindex;
                if ( !box[gk] ) box[gk] = {rowindex: gk, rowvalid:[], rowmsg:[]};

                // measure
                let fbLocation = row["Measure.[Const Grp_From Site]"];
                let fbSubLocation = row["Measure.[Const Grp_To Site]"];
                let fbProductGroup = row["Measure.[Const Grp_Product Group]"];
                let fbDefinition = row["Measure.[Const Grp_Definition]"];
                let fbProject = row["Measure.[Const Grp_Project]"];
                let fbMKTName = row["Measure.[Const Grp_Mkt Name]"];
                let fbInch = row["Measure.[Const Grp_Inch]"];
                let fbYear = row["Measure.[Const Grp_Year]"];
                let fbItem = row["Measure.[Const Grp_Item]"];

                let fb_Reason = row["Measure.[Const Grp_Reason]"];
                let fbEnddate = row["Measure.[Const Grp_Enddate]"];          // edit
                let fbStartdate = row["Measure.[Const Grp_Startdate]"];      // edit

                let measureFilter =  ' Measure.[Const Grp_From Site] == "'+fbLocation+'"'
                                    +', Measure.[Const Grp_To Site] == "'+fbSubLocation+'"'
                                    +', Measure.[Const Grp_Product Group] == "'+fbProductGroup+'"'
                                    +', Measure.[Const Grp_Definition] == "'+fbDefinition+'"'
                                    +', Measure.[Const Grp_Project] == "'+fbProject+'"'
                                    +', Measure.[Const Grp_Mkt Name] == "'+fbMKTName+'"'
                                    +', Measure.[Const Grp_Inch] == "'+fbInch+'"'
                                    +', Measure.[Const Grp_Year] == "'+fbYear+'"'
                                    +', Measure.[Const Grp_Item] == "'+fbItem+'"'
                                    ;
                let where = 'where {'+measureFilter+'}' ;

                // 기존 data 중복여부에 대한 체크
                if( rowstatus == "C") {
                    let rtnMeasureValue = cLib.selectList([versionName]
                                                            , ["Measure.[Const Grp_Exists Flag]"]
                                                            , where, "", "");  // where, orderby, limit

                    // From Site ~ Item 까지 동일할 경우 동일 Group ID 로 생성 불가
                    if( rtnMeasureValue.cs.rowCount > 0 ){
                        errCnt++;
                        box[gk].rowvalid.push("Error");
                        box[gk].rowmsg.push("Please check whether the same group is exist!");
                    }
                }

                // validation Check
                if( rowstatus == "C" || rowstatus == "U") {
                    
                    if( fbLocation === null || fbLocation === undefined || fbLocation === "" ){
                        // return { "errCnt" : 1, "Msg" : "Please input From Site!", "Rows" : row};   // 오류 리턴
                        errCnt++;
                        box[gk].rowvalid.push("Error");
                        box[gk].rowmsg.push("Please input From Site!");
                    }

                    if( fb_Reason === null || fb_Reason === undefined || fb_Reason === "" ){
                        // return { "errCnt" : 1, "Msg" : "Please input reason!", "Rows" : row};   // 오류 리턴
                        errCnt++;
                        box[gk].rowvalid.push("Error");
                        box[gk].rowmsg.push("Please input reason!");
                    }

                    if( fbStartdate != null && fbStartdate !== "" && fbEnddate != null && fbEnddate !== ""){
                        if ( !Number.isNaN(fbStartdate) && !Number.isNaN(fbEnddate)){
                            if ( fbStartdate > fbEnddate){
                                // return { "errCnt" : 1, "Msg" : "Start Week 가 End Week 보다 클 수 없음.", "Rows" : row};   // 오류 리턴
                                errCnt++;
                                box[gk].rowvalid.push("Error");
                                box[gk].rowmsg.push("Start Week 가 End Week 보다 클 수 없음.");
                            }
                        }
                    }
                }

            } // end for

            let result = Object.values(box).map(r => ({
                rowindex : r.rowindex,
                rowvalid : r.rowvalid.length ? r.rowvalid.join("^") : null, 
                rowmsg   : r.rowmsg.length ? r.rowmsg.join("^") : null
            }));

            return { errCnt, "Rows": result};

            // return { "errCnt" : 0, "Msg" : "", "Rows" : ""};   // 오류 리턴

        } catch ( e ) {
            cLib.error(e.message);
            return { "Code" : -1, "Msg" : e.message };
        }
    };

    /**
     * 저장 로직
     * validation Check
     * 저장 로직 수행
     * 
     * @param {*} parsedParams 
     * @returns 
     */
    var fn_save = function(parsedParams){
        const cLib = fn_cLib(programName + "." + arguments.callee.name);
        cLib.setLogLevel("Debug");

        try {
            // cLib.debug("parsedParams :: "+JSON.stringify(parsedParams));
            cLib.printParams(parsedParams);

            // validation Check 로직 수행 리턴 값
            let resutlValid = fn_validation(parsedParams);
            cLib.debug("#### resutlValid : "+JSON.stringify(resutlValid));

            if ( resutlValid.errCnt > 0){
                return { "Code" : 1, "Msg" : "valid", "ErrorCount":resutlValid.errCnt, "Rows" : resutlValid.Rows};  // return { "Code" : 1, "Msg" : resutlValid.Msg, "Rows" : resutlValid.Rows};   // 오류 리턴
            }

            fn_getHorizon();   // 계산용 MPHorizon 세팅

            for ( var i=0; i<parsedParams.fbGridRows.length; i++){
                let row = parsedParams.fbGridRows[i];
                let rowstatus = row["rowstatus"];
                
                // measure
                let fbSubLocation = row["Measure.[Const Grp_To Site]"];
                let fbAheadLimit = row["Measure.[Const Grp_Build Ahead Limit]"];

                if( rowstatus == "C") {
                    // Group ID 신규 생성
                    cLib.debug("신규생성 => Group ID 생성");

                    if( fbSubLocation == "All" || fbSubLocation == "-"){
                        fbGroupType    = MFC_SET;   // MFC_S
                    }else{
                        fbGroupType    = SRC_SET;   // SRC_S
                    }
                    row["[Group].[Group Type]"] = fbGroupType;
                    let newGroupID = fn_newGroupId(parsedParams, row);
                    row["[Group].[Group ID]"] = newGroupID;
                    row["[Sequence].[Sequence]"] = "1";
                }

                // 신규 생성
                if( rowstatus == "C" || rowstatus == "U") {

                    // Const Grp 생성 (그리드 상단)
                    fn_constGroup(parsedParams, row);

                    // Const Grp Detail 생성 / Const Grp Detail W 생성
                    fn_constGroupDetail(parsedParams, row);

                    // Const Grp Detail W 수정 (qty, sequence 업데이트)
                    fn_updateConstGroupDetail_W(parsedParams, row);

                    if( rowstatus == "C" ){
                        // Const Grp Ecp 생성 (Item 생성)
                        fn_constGroupEcp(parsedParams, row);

                        // Const Grp Asn 생성 (AOP 검색 용)
                        fn_constGroupAsn(parsedParams, row);

                        // Build Ahead 생성
                        if( fbAheadLimit !== null && fbAheadLimit !== undefined && fbAheadLimit !== "" ){
                            fn_buildAhead(parsedParams, row);
                        }
                    }

                    // Build Ahead 수정
                    fn_buildAhead(parsedParams, row);

                } else if( rowstatus == "D") {

                    // 1.Constraint Group 삭제
                    let dimGrp = [];
                    dimGrp.push(cUtil.fn_qDimVersionName(parsedParams));
                    dimGrp.push(cUtil.fn_qDim(row, "[Group].[Group ID]"));
                    dimGrp.push(cUtil.fn_qDim(row, "[Sequence].[Sequence]"));
                    cLib.deleteMeasure(dimGrp, "Constraint Group");

                    // 2-1.Constraint Group Detail 삭제
                    let dimGrpDetail = [];
                    dimGrpDetail.push(cUtil.fn_qDimVersionName(parsedParams));
                    dimGrpDetail.push(cUtil.fn_qDim(row, "[Group].[Group ID]"));
                    cLib.deleteMeasure(dimGrpDetail, "Constraint Group Detail");

                    // 2-2.Constraint Group Detail W 삭제
                    let dimGrpDetailW = [...dimGrpDetail];
                    dimGrpDetailW.push(Horizon);
                    cLib.deleteMeasure(dimGrpDetailW, "Constraint Group Detail W");

                    // 3.Constraint Group Ecp 삭제
                    let dimGrpItem = [...dimGrpDetail];
                    dimGrpItem.push("[Item].[Item]");
                    cLib.deleteMeasure(dimGrpItem, "Constraint Group Ecp");

                    // 4.Const Grp Asn 삭제 (AOP 검색 용)
                    cLib.deleteMeasure(dimGrpDetail, "Constraint Group Asn");

                    // 5.Build Ahead 삭제
                    fn_buildAhead(parsedParams, row);
                }
            } // for

            cLib.programEnd();

            return { "Code" : 0, "Msg" : "", "Rows" : "" };

        } catch ( e ) {
            cLib.error(e.message);
            return { "Code" : -1, "Msg" : e.message };
        }
    };

    /**
     * Group ID 신규 생성
     * 
     * @param {*} parsedParams 
     * @param {*} row 
     * @returns 
     */
    var fn_newGroupId = function(parsedParams, row){
        const cLib = fn_cLib(programName + "." + arguments.callee.name);
        cLib.setLogLevel("Debug");

        try {
            cLib.debug("## fn_newGroupId : Group ID 신규 생성 ");

            // let versionName = row["[Version].[Version Name]"];
            let versionName = cUtil.fn_qDimVersionName(parsedParams);
            let fbGroupType = row["[Group].[Group Type]"];

            let fullPadLenth = 5;   // Group ID 만들때 MFC숫자 (숫자에 들어갈 길이)
            let vGroupIdPreFix = fbGroupType+"_";   // SET : MFC_S_00000 , LCM : MFC_L_00000 

            let newGroupID = "";
            let result = cLib.selectList([versionName,'[Group].[Group ID].filter(#.Name startswith "'+vGroupIdPreFix+'")']
                                            ,['Measure.[Const Grp_Exists Flag]']
                                            , ''
                                            , "orderby [Group].[Group ID].Name desc", '');  // 역순으로 max 값 가져오기

            if ( result.cs.rowCount == 0 ){
                newGroupID = vGroupIdPreFix + cUtil.fn_lpad("1", fullPadLenth, "0");
            } else {
                let rtnGroupID = result.cs.row(0).cell(result.cs.memberColumnIndex("Group", "Group ID")).Name;
                // 두번째 배열의 숫자 + 1 ( ex: MFC_00001 )
                newGroupID = vGroupIdPreFix + cUtil.fn_lpad((parseInt(rtnGroupID.split("_").pop()) + 1).toString(), fullPadLenth, "0");
            }

            return newGroupID;

        } catch ( e ) {
            cLib.error(e.message);
            return { "Code" : -1, "Msg" : e.message };
        }
    };

    /**
     * member 체크 후 생성 (Group ID)
     * @param {*} row 
     * @returns 
     */
    var fn_makeMember = function(row){
        const cLib = fn_cLib(programName + "." + arguments.callee.name);
        cLib.setLogLevel("Debug");

        try {
            // member 체크 후 생성 (Group ID)
            let fbGroupID = row["[Group].[Group ID]"];
            cLib.debug(" fn_makeMember :: fbGroupID > " + fbGroupID);
            
            let fbGroupType = row["[Group].[Group Type]"];
            cLib.debug(" fn_makeMember :: fbGroupType > " + fbGroupType);

            if ( !cLib.existMember('[Group].[Group ID]', fbGroupID) ) {
                cLib.createDimension(['[Group].[Group ID]','[Group].[Group Name]','[Group].[Group Type]']
                                         , [fbGroupID, fbGroupID, fbGroupType]);
            }
            
        } catch ( e ) {
            cLib.error(e.message);
            return { "Code" : -1, "Msg" : e.message };
        }
    };

    /**
     * Const Grp 생성 로직
     * @param {*} rparsedParams 
     * @param {*} row 
     * @returns 
     */
    var fn_constGroup = function(parsedParams, row){
        const cLib = fn_cLib(programName + "." + arguments.callee.name);
        cLib.setLogLevel("Debug");

        try {
            cLib.debug("fn_constGroup :: row >>>>>> "+JSON.stringify(row));
            cLib.debug("########## fn_constGroup :: Start");
            
            let rowstatus = row["rowstatus"];
            // let fbVersion = cUtil.fn_qDimVersionName(parsedParams);
            // let fbVersion = row["[Version].[Version Name]"];

            let fbGroupID = row["[Group].[Group ID]"];
            let fbSequence = row["[Sequence].[Sequence]"];

            let dimension = [];
            // dimension.push(cUtil.fn_qDim(row, "[Version].[Version Name]"));
            dimension.push(cUtil.fn_qDimVersionName(parsedParams));
            dimension.push(cUtil.fn_qDim(row, "[Group].[Group ID]"));
            dimension.push(cUtil.fn_qDim(row, "[Sequence].[Sequence]"));
            cLib.debug("fn_constGroup :: dimension >>>>>> "+JSON.stringify(dimension));

            let measureUpdate = [];
            measureUpdate.push(cUtil.fn_qMeaStr(row, "Measure.[Const Grp_Refer Time]", row["Measure.[Const Grp_Refer Time]"]));  // string
            measureUpdate.push(cUtil.fn_qMeaStr(row, "Measure.[Const Grp_Enddate]", row["Measure.[Const Grp_Enddate]"]));
            measureUpdate.push(cUtil.fn_qMeaStr(row, "Measure.[Const Grp_Startdate]", row["Measure.[Const Grp_Startdate]"]));
            measureUpdate.push(cUtil.fn_qMeaStr(row, "Measure.[Const Grp_Reason]", row["Measure.[Const Grp_Reason]"]));
            measureUpdate.push(cUtil.fn_qMeaInt(row, "Measure.[Const Grp_Prod Qty]", row["Measure.[Const Grp_Prod Qty]"]));
            measureUpdate.push(cUtil.fn_qMeaInt(row, "Measure.[Const Grp_Build Ahead Limit]", row["Measure.[Const Grp_Build Ahead Limit]"]));
            measureUpdate.push(cUtil.fn_qMeaUpdateUserName("Measure.[Const Grp_Updated By]"));
            measureUpdate.push(cUtil.fn_qMeaUpdateTime("Measure.[Const Grp_Update Time]"));

            let measureInsert = [...measureUpdate];
            measureInsert.push(cUtil.fn_qMeaStr(row, "Measure.[Const Grp_From Site]", row["Measure.[Const Grp_From Site]"]));
            measureInsert.push(cUtil.fn_qMeaStr(row, "Measure.[Const Grp_From Site Name]", row["Measure.[Const Grp_From Site Name]"]));
            measureInsert.push(cUtil.fn_qMeaStr(row, "Measure.[Const Grp_To Site]", row["Measure.[Const Grp_To Site]"]));
            measureInsert.push(cUtil.fn_qMeaStr(row, "Measure.[Const Grp_To Site Name]", row["Measure.[Const Grp_To Site Name]"]));
            measureInsert.push(cUtil.fn_qMeaStr(row, "Measure.[Const Grp_Product Group]", row["Measure.[Const Grp_Product Group]"]));
            measureInsert.push(cUtil.fn_qMeaStr(row, "Measure.[Const Grp_Definition]", row["Measure.[Const Grp_Definition]"]));
            measureInsert.push(cUtil.fn_qMeaStr(row, "Measure.[Const Grp_Project]", row["Measure.[Const Grp_Project]"]));
            measureInsert.push(cUtil.fn_qMeaStr(row, "Measure.[Const Grp_Mkt Name]", row["Measure.[Const Grp_Mkt Name]"]));
            measureInsert.push(cUtil.fn_qMeaStr(row, "Measure.[Const Grp_Inch]", row["Measure.[Const Grp_Inch]"]));
            measureInsert.push(cUtil.fn_qMeaStr(row, "Measure.[Const Grp_Year]", row["Measure.[Const Grp_Year]"]));
            measureInsert.push(cUtil.fn_qMeaStr(row, "Measure.[Const Grp_Item]", row["Measure.[Const Grp_Item]"]));
            measureInsert.push(cUtil.fn_qMeaStr(row, "Measure.[Const Grp_Desc]", row["Measure.[Const Grp_Desc]"]));

            if( rowstatus == "C"){
                // member 체크 후 생성 (Group ID, Sequence)
                fn_makeMember(row);
            }

            let where = 'where { '
                                +' [Group].[Group ID]'+ cUtil.fn_filterStr(fbGroupID)
                                +',[Sequence].[Sequence]'+ cUtil.fn_filterStr(fbSequence)
                                +',Measure.[Const Grp_Exists Flag] > 0 '
                                +' } ';

            // 생생 로직
            if ( !cLib.existMeasure([dimension[0]], ["Measure.[Const Grp_Exists Flag]"], where) ) {
                cLib.createMeasure(dimension, ['Measure.[Const Grp_Exists Flag] = 1 ;']);
                cLib.updateMeasure(dimension,  measureInsert);
            }else{
                cLib.updateMeasure(dimension,  measureUpdate);
            }

            cLib.debug("########## fn_constGroup :: End");

        } catch ( e ) {
            cLib.error(e.message);
            return { "Code" : -1, "Msg" : e.message };
        }
    };

    /**
     * Detail 생성 (하단 그리드 MDP 영역)
     * 
     * 
     * @param {*} parsedParams 
     * @param {*} row 
     * @returns 
     */
    var fn_constGroupDetail = function(parsedParams, row){
        const cLib = fn_cLib(programName + "." + arguments.callee.name);
        cLib.setLogLevel("Debug");
        cLib.debug("############# fn_constGroupDetail : Start ");
        try {
            
            let fbGroupID = row["[Group].[Group ID]"];

            let dimension = [];
            // dimension.push(cUtil.fn_qDim(row, "[Version].[Version Name]"));
            dimension.push(cUtil.fn_qDimVersionName(parsedParams));
            dimension.push(cUtil.fn_qDim(row, "[Group].[Group ID]"));

            cLib.debug("fn_constGroupDetail :: dimension >>>>>> "+JSON.stringify(dimension));
            
            let where = 'where { '
                                + '[Group].[Group ID]'+cUtil.fn_filterStr(fbGroupID)
                                +', Measure.[Const Grp Detail_Exists Flag] > 0 '
                                +' } ';
            if ( !cLib.existMeasure([dimension[0]], ["Measure.[Const Grp Detail_Exists Flag]"], where) ) {
                cLib.createMeasure(dimension, ['Measure.[Const Grp Detail_Exists Flag] = 1 ;']);

                let measure = [];
                measure.push(cUtil.fn_qMeaStr(null, "Measure.[Const Grp Detail_From Site]", row["Measure.[Const Grp_From Site]"]));
                measure.push(cUtil.fn_qMeaStr(null, "Measure.[Const Grp Detail_From Site Name]", row["Measure.[Const Grp_From Site Name]"]));
                measure.push(cUtil.fn_qMeaStr(null, "Measure.[Const Grp Detail_To Site]", row["Measure.[Const Grp_To Site]"]));
                measure.push(cUtil.fn_qMeaStr(null, "Measure.[Const Grp Detail_To Site Name]", row["Measure.[Const Grp_To Site Name]"]));
                measure.push(cUtil.fn_qMeaStr(null, "Measure.[Const Grp Detail_Product Group]", row["Measure.[Const Grp_Product Group]"]));
                measure.push(cUtil.fn_qMeaStr(null, "Measure.[Const Grp Detail_Item]", row["Measure.[Const Grp_Item]"]));
                measure.push(cUtil.fn_qMeaStr(null, "Measure.[Const Grp Detail_Desc]", row["Measure.[Const Grp_Desc]"]));
                cLib.updateMeasure(dimension, measure);
            }else{
                // From Site ~ Item 까지는 수정사항이 없음
                cLib.updateMeasure(dimension, ['Measure.[Const Grp Detail_Exists Flag] = 1 ;']);
            }

            cLib.debug("############# fn_constGroupDetail : End ");

        } catch ( e ) {
            cLib.error(e.message);
            return { "Code" : -1, "Msg" : e.message };
        }
    };

    //########################################################################################
    /**
     *  Detail W  =========================> seq 가 다른 정보들을 지워줌.. 문제가 있음.. 2026.01.09 검토 및 수정 해야 함...
     * 
     * @param {*} parsedParams
     * @param {*} params 
     * @returns 
     */
    var fn_updateConstGroupDetail_W = function(parsedParams, row){
        const cLib = fn_cLib(programName + "." + arguments.callee.name);
        cLib.setLogLevel("Debug");

        try {
            // Group id : MFC_S_00001 , Sequence : 1 , start week : 202601 , end week : 202605 , time ref : every , qty : 10
            // Group id : MFC_S_00001 , Sequence : 2 , start week : 202607 , end week : 202609 , time ref : even , qty : 20
            // 202601 ~ 202605 : qty 10
            // 202607 ~ 202609 : qty 20

            let rowstatus = row["rowstatus"];
            let fbGroupID = row["[Group].[Group ID]"];

            let dimension = [];
            // dimension.push(cUtil.fn_qDim(row, "[Version].[Version Name]"));
            dimension.push(cUtil.fn_qDimVersionName(parsedParams));
            dimension.push(cUtil.fn_qDim(row, "[Group].[Group ID]"));

            let dimensionW = [...dimension];
            dimensionW.push(Horizon);
            
            //---------------------------- Const Grp Detail W 생성 : Horizon 의 모든 주차 디폴트 생성 ----------------------------//
            if( rowstatus == "C"){
                

                let whereW = 'where { '
                                    + '[Group].[Group ID]'+cUtil.fn_filterStr(fbGroupID)
                                    +',' + Horizon  // Horizon
                                    +', Measure.[Const Grp Detail W_Exists Flag] > 0 '
                                    +' } ';
                if ( !cLib.existMeasure([dimension[0]], ["Measure.[Const Grp Detail W_Exists Flag]"], whereW) ) {
                    cLib.createMeasure(dimensionW, ['Measure.[Const Grp Detail W_Exists Flag] = 1 ;']);
                    // cLib.updateMeasure(dimensionW, ['Measure.[Const Grp Detail W_Lock Flag] = false ;']);   // lock flag 사용안함
                }
            }else if( rowstatus == "U"){
                // 해당 seq의 기존 데이터 null 초기화
                cLib.updateMeasure(dimensionW, ["Measure.[Const Grp Detail W_Qty] = null ;"]);
            }
            //--------------------------------------------------------------------------------------------------------------------//

            let fbStartdate = row["Measure.[Const Grp_Startdate]"];
            let fbEnddate = row["Measure.[Const Grp_Enddate]"];
            let fbProdQty = row["Measure.[Const Grp_Prod Qty]"];
            let fbReferTime = row["Measure.[Const Grp_Refer Time]"];

            // return { week : { weekEvery, weekEven, weekOdd, weekLast, week1st, week2st, week3st, week4st, weekAll } };
            // ReferTime 계산하기 위한 주차 계산 함수
            const { week } = fn_getWeeks(fbStartdate, fbEnddate);

            let dimWeekMake = [...dimension];  // version, group ID

            if( fbReferTime == "Every W"){
                dimWeekMake.push("[Time].[Week]"+ cUtil.fn_filterStr(week.weekEvery));
            }else if( fbReferTime == "Even W"){
                dimWeekMake.push("[Time].[Week]"+ cUtil.fn_filterStr(week.weekEven));
            }else if( fbReferTime == "Odd W"){
                dimWeekMake.push("[Time].[Week]"+ cUtil.fn_filterStr(week.weekOdd));
            }else if( fbReferTime == "Last W"){
                dimWeekMake.push("[Time].[Week]"+ cUtil.fn_filterStr(week.weekLast));
            }else if( fbReferTime == "1st W"){
                dimWeekMake.push("[Time].[Week]"+ cUtil.fn_filterStr(week.week1st));
            }else if( fbReferTime == "2st W"){
                dimWeekMake.push("[Time].[Week]"+ cUtil.fn_filterStr(week.week2st));
            }else if( fbReferTime == "3st W"){
                dimWeekMake.push("[Time].[Week]"+ cUtil.fn_filterStr(week.week3st));
            }else if( fbReferTime == "4st W"){
                dimWeekMake.push("[Time].[Week]"+ cUtil.fn_filterStr(week.week4st));
            }

            // ReferTime 에 해당하는 주차에  Qty 세팅
            if ( dimWeekMake.length > 0){

                // // 해당 seq의 기존 데이터 null 초기화
                // if( rowstatus == "U"){
                //     let dimHorizon = [...dimension];
                //     dimHorizon.push(Horizon);
                //     cLib.updateMeasure(dimHorizon, ["Measure.[Const Grp Detail W_Qty] = null ;"]);
                // }

                // 주차별, refTime 에 따른 세팅
                let measureAdd = [];
                measureAdd.push(cUtil.fn_qMeaInt(null, "Measure.[Const Grp Detail W_Qty]", fbProdQty));
                cLib.updateMeasure(dimWeekMake, measureAdd);
            }

        } catch ( e ) {
            cLib.error(e.message);
            return { "Code" : -1, "Msg" : e.message };
        }
    };

    // MPHorizon, week 의 특성별로 필터링한 json 정의
    // ref_day == "1st" , "2st", "3st", "4st", "5st", "last"
    // ref == "even", "odd"
    var fn_getWeeks = function(paramStartdate, paramEnddate){
        const cLib = fn_cLib(programName + "." + arguments.callee.name);
        cLib.setLogLevel("Debug");

        let weekAll = MakeWeekOrg.map(r => r.week); 

        // MPHorizon 의 첫주차, 마지막 주차
        let firstWeek = weekAll[0];
        let lastWeek = weekAll[weekAll.length - 1];

        if( paramStartdate === null || paramStartdate === undefined || paramStartdate === ""){
            paramStartdate = firstWeek;
        }

        if( paramEnddate === null || paramEnddate === undefined || paramEnddate === ""){
            paramEnddate = lastWeek;
        }

        let startdate = paramStartdate;
        let enddate = paramEnddate;

        // MPHorizon 범위 만큼 담기
        const weekHorizon = MakeWeekRough.filter( r => {
            const num = Number(r.week);
            return !Number.isNaN(num) && num >= Number(firstWeek) && num <= Number(lastWeek);  // MPHorizon 시작주차~마지막주차
        });

        // MPHorizon 범위에서 start week ~ end week 만큼 담기
        const weekLimit = weekHorizon.filter( r => {
            const num = Number(r.week);
            return !Number.isNaN(num) && num >= Number(startdate) && num <= Number(enddate);
        });

        let week1st = weekLimit.filter( r => r.ref_day === "1st").map(r => r.week);  // ref_day == "1st"인 것만, 원하는 항목만 추출 (예: week), 콤마로 연결
        let week2st = weekLimit.filter( r => r.ref_day === "2st").map(r => r.week);  // ref_day == "2st"인 것만, 원하는 항목만 추출 (예: week), 콤마로 연결
        let week3st = weekLimit.filter( r => r.ref_day === "3st").map(r => r.week);  // ref_day == "3st"인 것만, 원하는 항목만 추출 (예: week), 콤마로 연결
        let week4st = weekLimit.filter( r => r.ref_day === "4st").map(r => r.week);  // ref_day == "4st"인 것만, 원하는 항목만 추출 (예: week), 콤마로 연결
        let weekLast = weekLimit.filter( r => r.ref_day === "last").map(r => r.week);  // ref_day == "last"인 것만, 원하는 항목만 추출 (예: week), 콤마로 연결
        let weekEven = weekLimit.filter( r => r.ref === "even").map(r => r.week);  // ref == "even"인 것만, 원하는 항목만 추출 (예: week), 콤마로 연결
        let weekOdd = weekLimit.filter( r => r.ref === "odd").map(r => r.week);  // ref == "odd"인 것만, 원하는 항목만 추출 (예: week), 콤마로 연결
        let weekEvery = weekLimit.map(r => r.week);

        return { week : { weekEvery, weekEven, weekOdd, weekLast, week1st, week2st, week3st, week4st, weekAll , weekLimit} }; // weekAll : Horizon 전체 주차
    };

    /**
     * ECP (Item) 생성
     * @param {*} parsedParams 
     * @param {*} row 
     * @returns 
     */
    var fn_constGroupEcp = function(parsedParams, row){
        const cLib = fn_cLib(programName + "." + arguments.callee.name);
        cLib.setLogLevel("Debug");

        try {
            let fbGroupID = row["[Group].[Group ID]"];

            let dimension = [];
            // dimension.push(cUtil.fn_qDim(row, "[Version].[Version Name]"));
            dimension.push(cUtil.fn_qDimVersionName(parsedParams));
            dimension.push(cUtil.fn_qDim(row, "[Group].[Group ID]"));

            let fbLocation = row["Measure.[Const Grp_From Site]"];
            let fbProductGroup = row["Measure.[Const Grp_Product Group]"];
            let fbDefinition = row["Measure.[Const Grp_Definition]"];
            let fbProject = row["Measure.[Const Grp_Project]"];
            let fbMKTName = row["Measure.[Const Grp_Mkt Name]"];
            let fbInch = row["Measure.[Const Grp_Inch]"];
            let fbYear = row["Measure.[Const Grp_Year]"];
            let fbItem = row["Measure.[Const Grp_Item]"];

            fbProductGroup = (fbProductGroup === "All") ? "" : (fbProductGroup || "").split("^").map(item => item.trim());
            fbDefinition = (fbDefinition === "All") ? "" : (fbDefinition || "").split("^").map(item => item.trim());
            fbProject = (fbProject === "All") ? "" : (fbProject || "").split("^").map(item => item.trim());
            fbMKTName = (fbMKTName === "All") ? "" : (fbMKTName || "").split("^").map(item => item.trim());
            fbInch = (fbInch === "All") ? "" : (fbInch || "").split("^").map(item => item.trim());
            fbYear = (fbYear === "All") ? "" : (fbYear || "").split("^").map(item => item.trim());
            fbItem = (fbItem === "All") ? "" : (fbItem || "").split("^").map(item => item.trim());
            
            let whereChk = 'where { '
                                + '[Group].[Group ID]'+cUtil.fn_filterStr(fbGroupID)
                                +', [Item].[Item]'
                                +', Measure.[Const Grp Ecp_Exists Flag] > 0 '
                                +' } ';
            // Const Grp Ecp 에 Group ID 별 데이터가 없을 경우에만 생성
            if ( !cLib.existMeasure([dimension[0]], ["Measure.[Const Grp Ecp_Exists Flag]"], whereChk) ) {

                let where = 'where { ' + dimension[0]   // version
                            + ',[Location].[Location]' + cUtil.fn_filterStr(fbLocation)
                            + ',[Item].[Product Group]' + cUtil.fn_filterStr(fbProductGroup)
                            + ',[Item].[Definition]' + cUtil.fn_filterStr(fbDefinition)
                            + ',[Item].[Project]' + cUtil.fn_filterStr(fbProject)
                            + ',[Item].[Marketing Name]' + cUtil.fn_filterStr(fbMKTName)
                            + ',[Item].[Inch]' + cUtil.fn_filterStr(fbInch)
                            + ',[Item].[Year]' + cUtil.fn_filterStr(fbYear)
                            + ',[Sub Location].[Sub Location] ,[Trans Mode].[Trans Mode] '
                            + ',Measure.[BOD Item_Asn] == 1 '
                            // + ',(Measure.[BOD Item_Cur Status] in {"PLANNED","ACTIVE","INACTIVE"})'
                            + ',(Measure.[BOD Item_Cur Status] in {"PLANNED","ACTIVE"})' // "INACTIVE" 제외 2026.01.27 이상엽p요청
                            + ',(coalesce(Measure.[BOD Item_Eff Startdate],DATEADD(Now(),-1,"Day")) < now() && coalesce(Measure.[BOD Item_Eff Enddate],DATEADD(Now(),1,"Day")) > now()) '
                            + ' }';

                // &SETItem -> SETItemExcludeOPT Named Set 변경 2026.01.27 (이상엽p)
                let result = cLib.selectList(['&SETItemExcludeOPT' + cUtil.fn_filterStr(fbItem)]
                                                ,['Measure.[BOD Item_Asn]']
                                                , where
                                                , '', '');

                // 대상 Item 을 조회한다.
                let getItemList = [];
                for ( k=0; k<result.cs.rowCount; k++){

                    let getItem = result.cs.row(k).cell(result.cs.memberColumnIndex("Item", "Item")).Name;
                    getItemList.push(getItem);
                }

                let dimensionEtc = [...dimension];
                if( getItemList.length > 0){
                    dimensionEtc.push("[Item].[Item]"+cUtil.fn_filterStr(getItemList));
                    cLib.createMeasure(dimensionEtc, ['Measure.[Const Grp Ecp_Exists Flag] = 1 ;']);
                    cLib.updateMeasure(dimensionEtc, ['Measure.[Const Grp Ecp_Flag] = "N" ;']);  // Boolean -> String (Y/N) 변경, 2025.10.28 (이상엽P요청)
                }else{
                    cLib.debug("####### BOD Item 에 조회된 Item 이 없어 생성하지 못함. getItemList.length : "+ getItemList.length);
                }
            }

        } catch ( e ) {
            cLib.error(e.message);
            return { "Code" : -1, "Msg" : e.message };
        }
    };

    /**
     * To Site, Item.Product Group : 멀티데이터로 변환
     * ex) Item.Product Group = All > TV,AV,MONITOR 로 변환
     *     To Site (Sub Location) = All > 쿼리 조회로 모든 Sub Location 배열로 변환
     * @param {*} parsedParams 
     * @param {*} row 
     * @returns 
     */
    var fn_getItemProdGrpAndToSiteArr = function(parsedParams, row){
        const cLib = fn_cLib(programName + "." + arguments.callee.name);
        cLib.setLogLevel("Debug");
        cLib.debug("############# fn_getItemProdGrpAndToSiteArr : Start ");
        // cLib.debug("############# fn_getItemProdGrpAndToSiteArr : parsedParams :: "+JSON.stringify(parsedParams));
        cLib.printParams(parsedParams);
        try {

            var fbVersion = cUtil.fn_getFilterValue(parsedParams, "[Version].[Version Name]");
            let fbLocation = row["Measure.[Const Grp_From Site]"];
            let fbToSite = row["Measure.[Const Grp_To Site]"];
            let fbProductGroup = row["Measure.[Const Grp_Product Group]"];

            //###############################################################################################################//
            // Item.Product Group 세팅 : commonVD : fn_cb_setProductGroup
            //###############################################################################################################//
            let fbAopItemStd1 = [];
            let itemStd1 =  cUtil.fn_getFilterQuery(parsedParams,"[Item].[Item Std1]");
            if( itemStd1 != null && itemStd1 != "" ){
                fbAopItemStd1.push(cUtil.fn_getFilterQuery(parsedParams,"[Item].[Item Std1]"));
            }

            let fbProductGroupArray = [];
            if( fbProductGroup ==="All" ){
                var dims = [];
                let where = "";

                dims = ['[Item].[Product Group].filter(#.Name != "-").relatedmembers([Product Group])'];
                // dims = ['&NSUIItemStd1View'];   // product group
                where = 'where { [Item].[Item Stage].[SET] } ';

                // // AOP Filter 사용시 적용 및 테스트 필요 (현재 넘어오지 않음)
                // if ( fbAopItemStd1.length > 0 ){
                //     dims = fbAopItemStd1;
                // }else{
                //     dims = ['[Item].[Product Group].filter(#.Name != "-").relatedmembers([Product Group])'];
                //     // dims = ['&NSUIItemStd1View'];   // product group
                //     where = 'where { [Item].[Item Stage].[SET] } ';
                // }

                let result = cLib.selectList(dims, [], where, "", "");
                for ( var i = 0; i < result.cs.rowCount; i++ ) {
                    var resultProductGroup = result.cs.row(i).cell(result.cs.memberColumnIndex("Item", "Product Group")).Name;
                    fbProductGroupArray.push(resultProductGroup);
                }
            }else{
                fbProductGroupArray = fbProductGroup.split("^");                      // row data : TV^MONITOR  or All
            }
            
            //###############################################################################################################//
            // To Site (Sub Location) 세팅 : commonVD : fn_cb_siteTo
            //###############################################################################################################//
            
            // // AOP Filter 사용시 적용 및 테스트 필요 (현재 넘어오지 않음)
            // let subLocationGroup1 =  cUtil.fn_getFilterQuery(parsedParams,"[Sub Location].[Sub Location Group1]");
            // let subLocationGroup2 =  cUtil.fn_getFilterQuery(parsedParams,"[Sub Location].[Sub Location Group2]");
            // let subLocationGroup3 =  cUtil.fn_getFilterQuery(parsedParams,"[Sub Location].[Sub Location Group3]");
            // let subLocationGroup4 =  cUtil.fn_getFilterQuery(parsedParams,"[Sub Location].[Sub Location Group4]");

            // let conditions = [];
            // if( subLocationGroup1 != null && subLocationGroup1 != "" ){
            //     conditions.push(cUtil.fn_getFilterQuery(parsedParams,"[Sub Location].[Sub Location Group1]"));
            // }
            // if( subLocationGroup2 != null && subLocationGroup2 != "" ){
            //     conditions.push(cUtil.fn_getFilterQuery(parsedParams,"[Sub Location].[Sub Location Group2]"));
            // }
            // if( subLocationGroup3 != null && subLocationGroup3 != "" ){
            //     conditions.push(cUtil.fn_getFilterQuery(parsedParams,"[Sub Location].[Sub Location Group3]"));
            // }
            // if( subLocationGroup4 != null && subLocationGroup4 != "" ){
            //     conditions.push(cUtil.fn_getFilterQuery(parsedParams,"[Sub Location].[Sub Location Group4]"));
            // }

            // cLib.debug("############# fn_getItemProdGrpAndToSiteArr : conditions :: "+JSON.stringify(conditions));
            // let conditionsStr = conditions.length ? `, ${conditions.join(',')} ` : '';
            // cLib.debug("### conditionsStr :: "+ conditionsStr);
            
            let fbToSiteArray = [];
            if( fbToSite ==="All" ){
                var dims = ['&NSUISubLocationDC'];
                //+cUtil.fn_getFilterQuery(parsedParams, "[Version].[Version Name]")
                // let where = 'where { [Version].[Version Name].['+fbVersion+']'
                let where = 'where { '+cUtil.fn_getFilterQuery(parsedParams, "[Version].[Version Name]")
                            + ', [Location].[Location]' + cUtil.fn_filterStr(fbLocation) 
                            + ', [Trans Mode].[Trans Mode]' 
                            + ', Measure.[BOD List_BOD Valid] == "Y" '
                            + ', coalesce(Measure.[BOD List_Eff Startdate],DATEADD(Now(),-1,"Day")) < now() '
                            + ', coalesce(Measure.[BOD List_Eff Enddate],DATEADD(Now(),1,"Day")) > now() '
                            // + ( conditions.length ? conditionsStr : '' )
                            + '} ';

                // let where = 'where { &CWVUI, [Location].[Location]' + cUtil.fn_filterStr(fbLocation) 
                //             + ', [Trans Mode].[Trans Mode]' 
                //             + ', Measure.[BOD List_BOD Valid] == "Y" '
                //             + ', coalesce(Measure.[BOD List_Eff Startdate],DATEADD(Now(),-1,"Day")) < now() '
                //             + ', coalesce(Measure.[BOD List_Eff Enddate],DATEADD(Now(),1,"Day")) > now() '
                //             // + ( conditions.length ? conditionsStr : '' )
                //             + '} ';
                cLib.debug("############# fn_getItemProdGrpAndToSiteArr : where >> " + where);

                let result = cLib.selectList(dims, ["Measure.[BOD List_BOD Valid]"], where, "", "");
                for ( var i = 0; i < result.cs.rowCount; i++ ) {
                    var SubLocation = result.cs.row(i).cell(result.cs.memberColumnIndex("Sub Location", "Sub Location")).Name;
                    fbToSiteArray.push(SubLocation);
                }
            }else{
                fbToSiteArray = fbToSite.split("^");                      // row data : S602^L5N0
            }
                

            cLib.debug("############# fn_getItemProdGrpAndToSiteArr : End ");

            return {fbProductGroupArray, fbToSiteArray};

        } catch ( e ) {
            cLib.error(e.message);
            return { "Code" : -1, "Msg" : e.message };
        }
    };

    /**
     * Const Group Asn 생성
     * Group ID 생성 이후에 로직 호출
     * 추가, 삭제
     * Grain : ver, group id, location, sub location, [Item].[Product Group]
     * @param {*} parsedParams 
     * @param {*} row 
     * @returns 
     */
    var fn_constGroupAsn = function(parsedParams, row){
        const cLib = fn_cLib(programName + "." + arguments.callee.name);
        cLib.setLogLevel("Debug");
        cLib.debug("############# fn_constGroupAsn : Start ");
        // cLib.debug("############# fn_constGroupAsn : parsedParams :: "+JSON.stringify(parsedParams));
        cLib.printParams(parsedParams);
        try {

            let dimension = [];
            // dimension.push(cUtil.fn_qDim(row, "[Version].[Version Name]"));
            dimension.push(cUtil.fn_qDimVersionName(parsedParams));
            dimension.push(cUtil.fn_qDim(row, "[Group].[Group ID]"));

            let fbLocation = row["Measure.[Const Grp_From Site]"];
            let {fbProductGroupArray, fbToSiteArray} = fn_getItemProdGrpAndToSiteArr(parsedParams, row);    // Product Group Array, To Site Array

            //###############################################################################################################//
            // Const Grp Asn 생성 / 삭제
            //###############################################################################################################//
            let makeAsnDim = [...dimension];    // versionName, Group ID
            makeAsnDim.push(cUtil.fn_qDim(null, "[Location].[Location]", fbLocation));
            makeAsnDim.push(cUtil.fn_qDim(null, "[Sub Location].[Sub Location]", fbToSiteArray));       // multi data
            makeAsnDim.push(cUtil.fn_qDim(null, "[Item].[Product Group]", fbProductGroupArray));        // multi data

            cLib.debug("############# fn_constGroupAsn : makeAsnDim >> "+JSON.stringify(makeAsnDim));

            cLib.createMeasure(makeAsnDim, ["Measure.[Const Grp Asn_Asn] = 1 ;"]);

            cLib.debug("############# fn_constGroupAsn : End ");

        } catch ( e ) {
            cLib.error(e.message);
            return { "Code" : -1, "Msg" : e.message };
        }
    };

    /**
     * Build Ahead Item (MG) , Build Ahead Item W (MG) : Data 입력
     * Build Ahead Item (MG) 로직 추가 : 신승호P요청 (2025.11.04)
     * dimension : [Version].[Version Name] * [Group].[Group ID]
     * Measure Group 변경 : Build Ahead Item => Build Ahead Group (2025.11.20) 신승호p 요청
     * 
     * @param {*} parsedParams 
     * @param {*} row 
     * @returns 
     */
    var fn_buildAhead = function(parsedParams, row){
        const cLib = fn_cLib(programName + "." + arguments.callee.name);
        cLib.setLogLevel("Debug");
        cLib.debug("############# fn_buildAhead : Start ");
        try {
            
            // let fbVersion = row["[Version].[Version Name]"];
            let fbGroupID = row["[Group].[Group ID]"];

            let dimension = [];
            // dimension.push(cUtil.fn_qDim(row, "[Version].[Version Name]"));
            dimension.push(cUtil.fn_qDimVersionName(parsedParams));
            dimension.push(cUtil.fn_qDim(row, "[Group].[Group ID]"));

            // Build Ahead Group : Grain
            let dimHorizonAll = [...dimension];
            dimHorizonAll.push(AheadHorizon);  // &MDMHorizon 전체

            let rowstatus = row["rowstatus"];

            if ( rowstatus == "C" || rowstatus == "U") {
                let fbFromSite = row["Measure.[Const Grp_From Site]"];
                let fbToSite = row["Measure.[Const Grp_To Site]"];
                let fbProductGroup = row["Measure.[Const Grp_Product Group]"];
                let fbStartdate = row["Measure.[Const Grp_Startdate]"];
                let fbEnddate = row["Measure.[Const Grp_Enddate]"];

                var result = cLib.selectList([AheadHorizon],[], "", "", "");

                let firstWeek = result.cs.row(0).cell(result.cs.memberColumnIndex("Time", "Week")).Name;
                let lastWeek = result.cs.row(result.cs.rowCount-1).cell(result.cs.memberColumnIndex("Time", "Week")).Name;

                if ( fbStartdate === null || fbStartdate === ""){
                    fbStartdate = firstWeek.toString();
                }

                if ( fbEnddate === null || fbEnddate === ""){
                    fbEnddate = lastWeek.toString();
                }

                //----------------------------------------- Grain 정의 ----------------------------------------//
                // Build Ahead Group W : Grain
                let dimensionW = [...dimension];
                dimensionW.push(AheadHorizon+`.filter(#.Name >= ${fbStartdate} && #.Name <= ${fbEnddate} )`);   // &MDMHorizon 기간내의 start/end date

                // Build Ahead Group : Grain
                // let fbToSiteArray = fbToSite.split("^");
                // let fbProductGroupArray = fbProductGroup.split("^");

                let {fbProductGroupArray, fbToSiteArray} = fn_getItemProdGrpAndToSiteArr(parsedParams, row);    // Product Group Array, To Site Array

                let dimensionAheadAsn = [...dimension];
                dimensionAheadAsn.push(cUtil.fn_qDim(null, "[Location].[Location]", fbFromSite));
                dimensionAheadAsn.push(cUtil.fn_qDim(null, "[Sub Location].[Sub Location]", fbToSiteArray));       // multi data
                dimensionAheadAsn.push(cUtil.fn_qDim(null, "[Item].[Product Group]", fbProductGroupArray));        // multi data
                //---------------------------------------------------------------------------------------------//

                // Measure.[Build Ahead Item_Shipment Type] : 쿼리 조회 후 세팅 , "All" 은 제외
                // Select ([Sub Location].[Sub Location].{To Site} * [Sub Location].[Sub Location Shipment Type]);
                let subLocationType = [];
                if( fbToSite != "All" ){
                    let fbToSiteList = fbToSite.split("^");
                    var resultType = cLib.selectList(["[Sub Location].[Sub Location]"+cUtil.fn_filterStr(fbToSiteList),"[Sub Location].[Sub Location Shipment Type]"]
                                                        ,[], "", "", "");
                    for ( var i = 0; i < resultType.cs.rowCount; i++ ) {
                        subLocationType.push(resultType.cs.row(i).cell(resultType.cs.memberColumnIndex("Sub Location", "Sub Location Shipment Type")).Name);
                    }
                }

                let shipmentType = "";
                if( subLocationType.length > 0 ){
                    shipmentType = subLocationType.join("^");
                }

                let measureUpdate = [];
                measureUpdate.push(cUtil.fn_qMeaUpdateUserName("Measure.[Build Ahead Group_Updated By]"));
                measureUpdate.push(cUtil.fn_qMeaUpdateTime("Measure.[Build Ahead Group_Update Time]"));

                let measureInsert = [...measureUpdate];
                measureInsert.push(cUtil.fn_qMeaUpdateUserName("Measure.[Build Ahead Group_Created By]"));
                measureInsert.push(cUtil.fn_qMeaUpdateTime("Measure.[Build Ahead Group_Creation Time]"));
                measureInsert.push(cUtil.fn_qMeaStr(null, "Measure.[Build Ahead Group_Category]", "Production Constraint"));   // default 세팅 : Production Constraint
                measureInsert.push(cUtil.fn_qMeaStr(null, "Measure.[Build Ahead Group_ALL]", "Default"));   // default 세팅 : Default
                measureInsert.push(cUtil.fn_qMeaStr(null, "Measure.[Build Ahead Group_From Site]", row["Measure.[Const Grp_From Site]"]));
                measureInsert.push(cUtil.fn_qMeaStr(null, "Measure.[Build Ahead Group_To Site]", row["Measure.[Const Grp_To Site]"]));
                measureInsert.push(cUtil.fn_qMeaStr(null, "Measure.[Build Ahead Group_Product Group]", row["Measure.[Const Grp_Product Group]"]));
                measureInsert.push(cUtil.fn_qMeaStr(null, "Measure.[Build Ahead Group_Definition]", row["Measure.[Const Grp_Definition]"]));
                measureInsert.push(cUtil.fn_qMeaStr(null, "Measure.[Build Ahead Group_Project]", row["Measure.[Const Grp_Project]"]));
                measureInsert.push(cUtil.fn_qMeaStr(null, "Measure.[Build Ahead Group_MKT Name]", row["Measure.[Const Grp_Mkt Name]"]));
                measureInsert.push(cUtil.fn_qMeaStr(null, "Measure.[Build Ahead Group_Inch]", row["Measure.[Const Grp_Inch]"]));
                measureInsert.push(cUtil.fn_qMeaStr(null, "Measure.[Build Ahead Group_Year]", row["Measure.[Const Grp_Year]"]));
                measureInsert.push(cUtil.fn_qMeaStr(null, "Measure.[Build Ahead Group_Item]", row["Measure.[Const Grp_Item]"]));
                measureInsert.push(cUtil.fn_qMeaStr(null, "Measure.[Build Ahead Group_Description]", row["Measure.[Const Grp_Desc]"]));
                measureInsert.push(cUtil.fn_qMeaStr(null, "Measure.[Build Ahead Group_Shipment Type]", shipmentType));

                // MDP : Build Ahead Group
                let where = 'where { '
                                +' [Group].[Group ID]'+ cUtil.fn_filterStr(fbGroupID)
                                +', (~isnull(Measure.[Build Ahead Group_Valid]) || ~isnull(Measure.[Build Ahead Group_Item])) '
                                +' } ';
                if ( !cLib.existMeasure([dimension[0]], ["Measure.[Build Ahead Group_Valid]"], where) ) {
                    cLib.createMeasure(dimension, ['Measure.[Build Ahead Group_Valid] = "Y" ;']);
                    cLib.updateBlockMeasure(dimension, measureInsert);
                }else{
                    cLib.updateBlockMeasure(dimension, measureUpdate);
                }

                // 주차 : Build Ahead Group W (삭제 후 재 생성)
                cLib.deleteMeasure(dimHorizonAll, "Build Ahead Group W");
                cLib.createMeasure(dimensionW, [cUtil.fn_qMeaInt(null, "Measure.[Build Ahead Group W_Period]", row["Measure.[Const Grp_Build Ahead Limit]"])]);

                // Build Ahead Asn 생성 : AOP 조회용 Data 생성 
                let whereAsn = 'where { '
                                +' [Group].[Group ID]'+ cUtil.fn_filterStr(fbGroupID)
                                +', Measure.[Build Ahead Asn_Asn] > 0 '
                                +' } ';

                if ( !cLib.existMeasure([dimension[0]], ["Measure.[Build Ahead Asn_Asn]"], whereAsn) ) {
                    cLib.createMeasure(dimensionAheadAsn, ['Measure.[Build Ahead Asn_Asn] = 1 ;']);
                }else{
                    cLib.updateBlockMeasure(dimensionAheadAsn, ['Measure.[Build Ahead Asn_Asn] = 1 ;']);
                }

            } else if ( rowstatus == "D") {
                cLib.deleteMeasure(dimension, "Build Ahead Group");
                cLib.deleteMeasure(dimHorizonAll, "Build Ahead Group W");
                cLib.deleteMeasure(dimension, "Build Ahead Asn");   // version, Group ID 로만 삭제 ( 동일 Group ID 없음 )
                // cLib.deleteMeasure(dimensionAheadAsn, "Build Ahead Asn");
            }

            cLib.debug("############# fn_buildAhead : End ");

        } catch ( e ) {
            cLib.error(e.message);
            return { "Code" : -1, "Msg" : e.message };
        }
    };

    /**
     * fn_merge : Scenario Plan >> 테스트 필요..
     * 2026.03.04 생성
     * fbGridRows > Grain + 아래 메저 함께 넘겨줘야 함.
     * Measure.[Const Grp_From Site]
     * Measure.[Const Grp_To Site]
     * Measure.[Const Grp_Product Group]
     * @param {*} parsedParams 
     * @returns 
     */
    var fn_merge = function(parsedParams){
        const cLib = fn_cLib(programName + "." + arguments.callee.name);
        cLib.setLogLevel("Debug");

        try {
            cLib.debug("fn_merge call ==========================================================>");
            cLib.debug("parsedParams :: "+JSON.stringify(parsedParams));

            // 시나리오버전 테스트 : 202608_M_WI_05
            cLib.debug("fn_getFilterValue >>"+cUtil.fn_getFilterValue(parsedParams, "[Version].[Version Name]"));
            var fbVersion = cUtil.fn_getFilterValue(parsedParams, "[Version].[Version Name]");  // ew에서 버전이 어떻게 넘어 오는지??? (시나리오 버전)
            var toVersion = "[Version].[Version Name].[CWV_MP]";

            cLib.debug("####### mergeType : "+parsedParams.fbParams["mergeType"]);
            cLib.debug(""+parsedParams.fbGridRows.master.length);

            if( parsedParams.fbParams["mergeType"] == "1"){

                let query = 'UpdateScenario( '
                    + toVersion         // To 버전
                    + ',' + "[Version].[Version Name].["+fbVersion+"]"   // 시나리오 버전(from 버전)
                    + ',false'
                    + ',for model [Constraint Group] '
                    + ',for model [Constraint Group Asn] '
                    + ',for model [Constraint Group Detail] '
                    + ',for model [Constraint Group Detail W] '
                    + ',for model [Constraint Group Ecp] '
                    + ',for model [Build Ahead Group] '
                    + ',for model [Build Ahead Group W] '
                    + ',for model [Build Ahead Asn] '
                    +'); ';

                    cLib.debug("UpdateScenario >> "+query);
                    queryModule.update(query);

            }else if( parsedParams.fbParams["mergeType"] == "0"){

                //// cLib.debug("fn_getFilterValue >>"+cUtil.fn_getFilterValue(parsedParams, "[Version].[Version Name]"));

                //// // var fbVersion = parsedParams.fbParams["[Version].[Version Name]"];  // ew에서 버전이 어떻게 넘어 오는지??? (시나리오 버전)
                //// var fbVersion = cUtil.fn_getFilterValue(parsedParams, "[Version].[Version Name]");  // ew에서 버전이 어떻게 넘어 오는지??? (시나리오 버전)
                //// var toVersion = "[Version].[Version Name].[CWV_MP]";
                
                //// parsedParams.fbGridRows.master
                for ( var i=0; i<parsedParams.fbGridRows.master.length; i++){
                // for ( var i=0; i<parsedParams.fbGridRows.length; i++){

                    var row = parsedParams.fbGridRows.master[i];

                    let dimension = [];
                    dimension.push(cUtil.fn_qDim(row, "[Group].[Group ID]"));

                    let dimGrp = [];
                    dimGrp.push(cUtil.fn_qDim(row, "[Group].[Group ID]"));
                    // dimGrp.push(cUtil.fn_qDim(row, "[Sequence].[Sequence].[1]"));
                    dimGrp.push("[Sequence].[Sequence].[1]");

                    // let dimGrpAsn = [];
                    // dimGrpAsn.push(cUtil.fn_qDim(row, "[Group].[Group ID]"));
                    // dimGrpAsn.push(cUtil.fn_qDim(null, "[Location].[Location]", row["Measure.[Const Grp_From Site]"]));
                    // dimGrpAsn.push(cUtil.fn_qDim(null, "[Sub Location].[Sub Location]", row["Measure.[Const Grp_To Site]"]));
                    // dimGrpAsn.push(cUtil.fn_qDim(null, "[Item].[Product Group]", row["Measure.[Const Grp_Product Group]"]));

                    let dimGrpDetailW = [];
                    dimGrpDetailW.push(cUtil.fn_qDim(row, "[Group].[Group ID]"));
                    dimGrpDetailW.push(Horizon);

                    let dimGrpEcp = [];
                    dimGrpEcp.push(cUtil.fn_qDim(row, "[Group].[Group ID]"));
                    dimGrpEcp.push("[Item].[Item]");

                    // let dimAheadGrp = [];
                    // dimAheadGrp.push(cUtil.fn_qDim(row, "[Group].[Group ID]"));

                    let dimAheadGrpW = [];
                    dimAheadGrpW.push(cUtil.fn_qDim(row, "[Group].[Group ID]"));
                    dimAheadGrpW.push(AheadHorizon);

                    // let dimAheadAsn = [];
                    // dimAheadAsn.push(cUtil.fn_qDim(row, "[Group].[Group ID]"));
                    // dimAheadAsn.push(cUtil.fn_qDim(null, "[Location].[Location]", row["Measure.[Const Grp_From Site]"]));
                    // dimAheadAsn.push(cUtil.fn_qDim(null, "[Sub Location].[Sub Location]", row["Measure.[Const Grp_To Site]"]));
                    // dimAheadAsn.push(cUtil.fn_qDim(null, "[Item].[Product Group]", row["Measure.[Const Grp_Product Group]"]));

                    //-------------------------------------------------------------------------------------
                    // 시나리오 버전 Copy ( fbVersion => toVersion (CWP_MP) 로 copy )
                    // 각 MG 의 시나리오 버전 데이터가 없는 경우 copy 안됨
                    //-------------------------------------------------------------------------------------
                    let query = 'UpdateScenario( '
                    + toVersion         // To 버전
                    + ',' + "[Version].[Version Name].["+fbVersion+"]"   // 시나리오 버전(from 버전)
                    + ',false'
                    + ',for model [Constraint Group] using scope (' + dimGrp.join('*') + ')'
                    + ',for model [Constraint Group Asn] using scope (' + dimension.join('*') + ')'
                    + ',for model [Constraint Group Detail] using scope (' + dimension.join('*') + ')'
                    + ',for model [Constraint Group Detail W] using scope (' + dimGrpDetailW.join('*') + ')'
                    + ',for model [Constraint Group Ecp] using scope (' + dimGrpEcp.join('*') + ')'
                    + ',for model [Build Ahead Group] using scope (' + dimension.join('*') + ')'
                    + ',for model [Build Ahead Group W] using scope (' + dimAheadGrpW.join('*') + ')'
                    + ',for model [Build Ahead Asn] using scope (' + dimension.join('*') + ')'
                    +'); ';

                    cLib.debug("UpdateScenario >> "+query);
                    queryModule.update(query);

                    //-------------------------------------------------------------------------------------
                    // Constraint Group : 사용자 Update > 시나리오 버전 Data 가 존재할 때만 update
                    //-------------------------------------------------------------------------------------
                    let dimGrpChk = [...dimGrp];
                    dimGrpChk.push("[Version].[Version Name].["+fbVersion+"]"); // 시나리오 버전
                    if( cLib.existMeasure(dimGrpChk, ["Measure.[Const Grp_From Site]"], "") ){

                        dimGrp.push(toVersion);

                        let measure = [];
                        measure.push(cLib.fn_mergeUser("Measure.[Const Grp_Updated By]", fbVersion));
                        measure.push(cUtil.fn_qMeaUpdateTime("Measure.[Const Grp_Update Time]"));
                        cLib.updateMeasure(dimGrp, measure);
                    }

                    //-------------------------------------------------------------------------------------
                    // 사용자 Update > Measure 없음 (skip)
                    // Constraint Group Asn
                    // Constraint Group Detail
                    // Constraint Group Detail W
                    // Constraint Group Ecp
                    // Build Ahead Group W
                    // Build Ahead Asn
                    //-------------------------------------------------------------------------------------

                    //-------------------------------------------------------------------------------------
                    // Build Ahead Group : 사용자 Update > 시나리오 버전 Data 가 존재할 때만 update
                    //-------------------------------------------------------------------------------------
                    let dimAheadGrpChk = [...dimension];
                    dimAheadGrpChk.push("[Version].[Version Name].["+fbVersion+"]"); // 시나리오 버전
                    if( cLib.existMeasure(dimAheadGrpChk, ["Measure.[Build Ahead Group_From Site]"], "") ){

                        dimension.push(toVersion);

                        let measure = [];
                        measure.push(cLib.fn_mergeUser("Measure.[Build Ahead Group_Updated By]", fbVersion));
                        measure.push(cUtil.fn_qMeaUpdateTime("Measure.[Build Ahead Group_Update Time]"));
                        cLib.updateMeasure(dimension, measure);
                    }
                    
                }

            }

            cLib.programEnd();

            //  정상 저장 후 리턴
            return { "Code" : 0, "Msg" : "It was saved successfully." };

        } catch ( e ) {
            cLib.error(e.message);
            return { "Code" : -1, "Msg" : e.message };
        }
    };

    // Mapping 함수 정의, 마지막에 선언을 해야 함수를 정상적으로 인식함
    const functionMap = {
        "fn_save"        : fn_save
       ,"fn_merge"       : fn_merge
    };

    return {
        fn_loadFunction : fn_loadFunction
    };
});

/*--------------------------------------------------------------------------------------------------*/
/* 프로그램명 : o9.NSCM.JSEWProductionConstSET
    화면명 : Production Constraint (EW) - SET
    Action Button : EWProductionConstSET
    [history]
    2025.09.11 | syif1380.lee | fn_save : 전체 수정
                                - fn_validation
                                - PY 호출 실행 => JS 로 구현 (속도.. Item 건수가 많아서 생김 - 테스트 필요)

    2025.10.28 | syif1380.lee | Measure.[Const Grp Ecp_Flag]  // Boolean -> String (Y/N) 변경 (이상엽P요청)
    2025.11.04 | syif1380.lee | fn_buildAhead 함수 변경, Build Ahead Item(MG) 데이터 생성 (신승호P요청)
    2025.11.05 | syif1380.lee : fn_buildAhead 함수 로직 추가, Measure.[Build Ahead Group_Asn] 등록 (신승호P요청)
    2025.11.20 | syif1380.lee : fn_buildAhead - Measure Group 전체 변경 (신승호P요청)
                                - Build Ahead Item    => Build Ahead Group
                                - Build Ahead Item W  => Build Ahead Group W
                                - Build Ahead Group   => Build Ahead Asn
    2026.01.08 | syif1380.lee : 데이터 생성시 Measure.[Const Grp_Sequence Index] : Sequence값을 메저에 입력 , aggregation=max
                                - 체크 메저 (Const Grp_Exists Flag, Const Grp Detail_Exists Flag, Const Grp Detail W_Exists Flag, Const Grp Ecp_Exists Flag)
                                - 메저 검색용 추가 (Const Grp_Search Key)
                                - &CWVUI : 버전 정보 제거, param 값 정의
    2026.01.09 | syif1380.lee : 테스트, 소스 점검 수정
    2026.01.13 | syif1380.lee : Const Grp Asn 생성/삭제 : fn_constGroupAsn() 추가, 이상엽p 요청
    2026.01.14 | syif1380.lee : fn_constGroupAsn() 수정 : Product Group = All or Sub Location = All 일때, data 조회하여 모두 저장
    2026.01.15 | syif1380.lee : fn_constGroupAsn() 수정 : Product Group = All or Sub Location = All 일때, AOP Filter 참조하여 세팅
    2026.01.19 | syif1380.lee : fn_constGroupAsn() 수정 : 삭제시 Const Grp 에 Group ID 존재하면 삭제하지 않음(Sequence 여러개일 경우 sequence 1개 삭제시 skip )
    2026.01.20 | syif1380.lee : Sequence = 1로 통일 (Sequence +1 하지 않음), 전체 로직 변경
    2026.01.21 | syif1380.lee : Measure 삭제 : Const Grp_Sequence Index, Const Grp_Search Key, Const Grp Detail W_Sequence
                                - validation 추가 : From Site ~ Item 동일한 경우 validation 체크 로직 추가 (동일 Group ID 생성 불가)
    2026.01.27 | syif1380.lee : fn_constGroupEcp : BOD Item select 변경 , &SETItem -> &SETItemExcludeOPT , {"PLANNED","ACTIVE","INACTIVE"} -> "INACTIVE" 제외
    2026.03.03 : fn_merge() : Scenario Plan 정의 , combo > &cwvui 없음
    2026.03.04 : fn_merge() : Scenario Plan 정의 -> UpdateScenario 로 변경
    2026.03.16 : fn_merge() : fbParams.mergeType 추가
    2026.03.26 : commonLib 선언 부분 변경 및 공통함수 이름 변경
*/
/*--------------------------------------------------------------------------------------------------*/