define('o9.NSCM.JSEWSiteMFMaster', ['o9/data/query', 'o9/data/cellset', 'o9.NSCM.commonLib'], function(){	
	const programName = "o9.NSCM.JSEWSiteMFMaster";
    const commonLib = require('o9.NSCM.commonLib');
    const vdUtil = new commonLib.VdUtil();
    /*--------------------------------------------------------------------------------------------------*/
    // 프로그램명 : o9.NSCM.JSEWSiteMFMaster
    // Action Button : EWSiteMFMaster
    // 화면명 : Site(MF) Master
    // 2025.08.19 수정 : Add 기능 추가하면서 재개발
    // 2025.08.21 : 디멘젼 Attribute, [Location].[Location] Property 재정의함.
    // 2025.09.02 : fn_cb_country 공통함수로 전환함. Region 입력시 예외처리로직 추가
    // 2025.09.03 : Location 속성 중 [Location].[JDM Flag]에 대해서 'Y'일때 true, '-'일때는 null 처리
    // 2025.09.03 : Location 멤버 속성 항목 추가함. [Location].[Location$DisplayName], [Location].[Location$DisplayAlias] 
    // 2025.09.03 : [Location].[Site Group4 View Flag] 추가
    // 2025.09.08 : Row Status "U" 추가함.
    // 2025.09.23 : update 일자 처리 수정
    // 2025.10.27 : location  member IBPL 수정 (DisplayName 변경)    
    // 2025.10.29 : Location Attribute [JDM Type] 추가함.
    // 2025.10.29 : Site Group4 관련 memberproperties 추가
    // 2025.11.03 : memberproperties 수정 (Sorting Order, Valid Flag 처리)
    // 2025.12.31 fn_loadFunction() 수정함. => parsedParams 값 체크 로직 추가
    /*--------------------------------------------------------------------------------------------------*/        

	var fn_loadFunction = function(o9Params){
        const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
        vdCommon.setLogLevel("Debug");

		try {
            let returnData = {};
            let obj = this;

            vdCommon.printParams(o9Params);

            // 파라메타 가져오기
            var parsedParams = JSON.parse(o9Params);
			var fbFuncName = parsedParams.fbFuncName;

            if ( functionMap[fbFuncName] == undefined ) {
                return { "Code" : 1, "Msg" : "No Function" };
            }

            if ( parsedParams["fbParams"] == undefined ) {
                parsedParams["fbParams"] = {};
            }
            if ( parsedParams.fbParams["includeField"] == undefined ) {
                parsedParams.fbParams["includeField"] = "";
            }
            if ( parsedParams.fbParams["includeProperty"] == undefined ) {
                parsedParams.fbParams["includeProperty"] = "";
            }
            // 조회시 기본 limit 지정( 3000개 )
            if ( parsedParams.fbParams["limit"] == undefined ) {
                parsedParams.fbParams["limit"] = "limit 3000";
            } else if ( parsedParams.fbParams["limit"] == -1 ) {
                parsedParams.fbParams["limit"] = "";
            } else {
                parsedParams.fbParams["limit"] = "limit " + parsedParams.fbParams.limit;
            }
            // 콤보에 All 추가
            if ( parsedParams.fbParams["existAll"] == undefined ) {
                parsedParams.fbParams["existAll"] = false;
            }
            // 콤보에 Blank 추가
            if ( parsedParams.fbParams["existBlank"] == undefined ) {
                parsedParams.fbParams["existBlank"] = false;
            }
            // 콤보에 - 추가
            if ( parsedParams.fbParams["existHyphen"] == undefined ) {
                parsedParams.fbParams["existHyphen"] = false;
            }
            // where 조건 추가
            if ( parsedParams.fbParams["where"] == undefined ) {
                parsedParams.fbParams["where"] = {};
            }
            if ( parsedParams.fbParams["isDisplayNameWithCode"] == undefined ) {
                parsedParams.fbParams["isDisplayNameWithCode"] = true;
            }
            // filters 조건 추가
            if ( parsedParams.fbParams["filters"] == undefined ) {
                parsedParams.fbParams["filters"] = {};
            }

            var rtn = functionMap[fbFuncName](parsedParams);

            vdCommon.programEnd();
            return rtn;
        } catch ( e ) {
            vdCommon.error(e.message);
            return { "Code" : -1, "Msg" : e.message };
        }
	};
	
    /* ********************************************************************************** */
    /* EWCommonVD 호출함.
    {"fbFuncName":"fn_cb_country",
    "fbParams":{"includeField":"Country:Region:Region",
    "filters":{"[Location].[Site Group1]":{"SelectedMembers":[],"MemberFilter":"&NSUISiteGrp1MFView"},
    "[Location].[Site Group2]":{"SelectedMembers":[],"MemberFilter":"&NSUISiteGrp2MFView.unionwith(Location.[Site Group2].filter(#.Name ==\"-\"))"},
    "[Location].[Site Group3]":{"SelectedMembers":[],"MemberFilter":"&NSUISiteGrp3MFView.unionwith(Location.[Site Group3].filter(#.Name ==\"-\"))"},
    "[Location].[Site Group4]":{"SelectedMembers":[],"MemberFilter":"[Location].[Site Group4].filter(#.[Site Group4 View Flag] == True).intersectwith(&NSUILocationPlant.relatedmembers([Site Group4])).unionwith(Location.[Site Group4].filter(#.Name ==\"-\"))"},
    "[Version].[Version Name]":{"SelectedMembers":["CWV_MP"],"MemberFilter":"&CWVUI"}}}}
    */
    /* ********************************************************************************** */
    /* EWCommonVD 호출함.
     {"fbFuncName":"fn_cb_company", "fbParams":{"includeField":"Company:Abbreviation:Abbreviation"}}
    */
    /* ********************************************************************************** */
    var fn_validation = function(parsedParams){
        const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
        vdCommon.setLogLevel("Debug"); 
        try{
            let errorCnt = 0;
            let errorMsg = "";
            let fbVersion = parsedParams.fbParams.version;

            for ( var i = 0; i < parsedParams.fbGridRows.length; i++ ) {
                let rowStatus = parsedParams.fbGridRows[i]["rowstatus"];
                let fbLocation = parsedParams.fbGridRows[i]["[Location].[Location]"];

                parsedParams.fbGridRows[i]["rowmsg"] = "";
                parsedParams.fbGridRows[i]["errorflag"] = "";

                if(rowStatus == "C"){
                     //validation 체크함.
                    //(1) 등록여부 확인 : Measure.[Alloc Pur_ETD Plan] 데이타 존재 여부를 체크함.
                    let sDimension = [];
                    sDimension.push("[Version].[Version Name].["+fbVersion+"]");
                    sDimension.push("[Location].[Location].["+fbLocation+"]");

                    let sMeasure = [];
                    sMeasure.push("Measure.[MF Site_Business Type]");

                    let chkFlag  = vdCommon.existMeasure(sDimension, sMeasure, "")
                    vdCommon.debug("[Site(MF) Master]" + chkFlag);
                   
                    if(chkFlag){
                        errorMsg = "This is a registered <MF Site> Data.";
                        errorCnt++;
                        parsedParams.fbGridRows[i]["rowmsg"] = errorMsg;
                        parsedParams.fbGridRows[i]["errorflag"] = "ERROR";
                    } 
                }                
            }

            if(errorCnt > 0 ){
                //Error Row만 Return 함.
                let checkGridRows = parsedParams.fbGridRows;
                const errorRows = checkGridRows.filter((checkGridRows)=>{return checkGridRows.errorflag === "ERROR"});
                parsedParams.fbGridRows = errorRows;
                return { "Code" : -1, "Msg" : "validation Error", "Rows" : parsedParams.fbGridRows };
            }

            return { "Code" : 0, "Msg" : "" };
        }catch(e){
            return { "Code" : -1, "Msg" : e.message };
        }  
    } ; 
    /* ********************************************************************************** */
    /*{"fbFuncName":"fn_save","fbParams":{"version":"CWV_MP"},
    "fbGridRows" : [
    {"rowstatus":"C", "rowindex":0
    ,"[Location].[Location Code]":"SITE_CODE" //Form Site   
    ,"[Location].[Location Name]": "SITE_Name" //Site Name(From)
    ,"[Location].[Description]":"SITEMF_TEST_002"
    ,"[Location].[Location Type]":"MF"
    ,"Measure.[MF Site_Country Name Override]":"UNITED STATES"
    ,"Measure.[MF Site_Country Code]":"US"
    ,"Measure.[MF Site_Region]":"NORTH_AMERICA"
    ,"Measure.[MF Site_Business Type]":"PLANT"
    ,"Measure.[MF Site_Sales Type]": "PLANT"
    ,"Measure.[MF Site_Company Name Override]": "B201"
    ,"Measure.[MF Site_Company Code]":"B201"
    ,"Measure.[MF Site_GBM]": "VD"
    ,"Measure.[MF Site_JDM Flag Override]": "Y"
    ,"Measure.[MF Site_KD Flag Override]": "Y"
    ,"Measure.[MF Site_MF SITE STAGE Override]": "SET"
    ,"Measure.[MF Site_Valid Flag Override]": "Y"
    ,"Measure.[MF Site_Group1]": "MF"
    ,"Measure.[MF Site_Group2]": "NORTH_AMERICA"
    ,"Measure.[MF Site_Group3 Override]": "AMERICA"
    ,"[Location].[Location Sorting Order]": 100
    }]}
    */
    var fn_save = function(parsedParams){
        const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
        vdCommon.setLogLevel("Debug"); 
        try{
            //Validation 체크
            let errorData = fn_validation(parsedParams);
            if(errorData.Code == -1){
                return errorData
            }
            //++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
            let fbVersion = parsedParams.fbParams.version;            
            //vdCommon.debug("[fs_save]" + fbVersion);
            for ( var i = 0; i < parsedParams.fbGridRows.length; i++ ) {
                let rowStatus = parsedParams.fbGridRows[i]["rowstatus"];
                let fbLocationCode = parsedParams.fbGridRows[i]["[Location].[Location Code]"]; //Location Code
                let fbLocationName = parsedParams.fbGridRows[i]["[Location].[Location Name]"]; // Location Name
 
                let fbLocationDescription = parsedParams.fbGridRows[i]["[Location].[Description]"];
                let fbLocatioinType = parsedParams.fbGridRows[i]["[Location].[Location Type]"];
                let fbCountryName = parsedParams.fbGridRows[i]["Measure.[MF Site_Country Name Override]"];
                let fbCountryCode = parsedParams.fbGridRows[i]["Measure.[MF Site_Country Code]"];
                let fbRegion = parsedParams.fbGridRows[i]["Measure.[MF Site_Region]"];
                let fbBusinessType = parsedParams.fbGridRows[i]["Measure.[MF Site_Business Type]"];
                let fbSalesType = parsedParams.fbGridRows[i]["Measure.[MF Site_Sales Type]"];
                let fbCompanyName = parsedParams.fbGridRows[i]["Measure.[MF Site_Company Name Override]"];
                let fbCompanyCode = parsedParams.fbGridRows[i]["Measure.[MF Site_Company Code]"];
                //let fbCompanyDesc = parsedParams.fbGridRows[i]["Measure.[MF Site_Company Desc Override]"];
                let fbGBM = parsedParams.fbGridRows[i]["Measure.[MF Site_GBM]"];
                let fbJDMFlag = parsedParams.fbGridRows[i]["Measure.[MF Site_JDM Flag Override]"];
                let fbKDFlag = parsedParams.fbGridRows[i]["Measure.[MF Site_KD Flag Override]"];
                let fbMFSiteStage = parsedParams.fbGridRows[i]["Measure.[MF Site_MF SITE STAGE Override]"];
                let fbValidFlag = parsedParams.fbGridRows[i]["Measure.[MF Site_Valid Flag Override]"];
                let fbSiteGroup1 = parsedParams.fbGridRows[i]["Measure.[MF Site_Group1]"];
                let fbSiteGroup2 = parsedParams.fbGridRows[i]["Measure.[MF Site_Group2]"];
                let fbSiteGroup3 = parsedParams.fbGridRows[i]["Measure.[MF Site_Group3 Override]"];
                let sortingOrder = parsedParams.fbGridRows[i]["[Location].[Location Sorting Order]"];

                let validFlag = (fbValidFlag == "Y" ? true: null);
                let jdmFlag = (fbJDMFlag == "Y" ? true : null);
                let jdmType = (fbJDMFlag == "-" ? null : (fbJDMFlag == "" ? null : fbJDMFlag) );
                let kdFlag = (fbKDFlag == "Y" ? true : null);

                if(sortingOrder == undefined){
                    sortingOrder = 999;
                }
                
                //++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
                //Dimension Member처리
                //++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
                let memberQuery = 'Createmember ( [Location].[Location] = {,"' + fbLocationCode + '" }';  //Hierarchy
                //+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
                //memberproperties 등록  
                memberQuery += ',[Location].[Location$DisplayName] = {"'+fbLocationCode+'",} '; 
                memberQuery += ',[Location].[Location$DisplayAlias] = {"'+fbLocationCode+'",} '; 
                memberQuery += ',[Location].[Location Site ID] = {"'+fbLocationName+'",} ';
                memberQuery += ',[Location].[Description] = {"'+fbLocationDescription+'",} ';
                memberQuery += ',[Location].[Country Code] = {"'+fbCountryCode+'",} ';
                memberQuery += ',[Location].[Business Type] = {"'+fbBusinessType+'",} ';
                memberQuery += ',[Location].[Location GBM] = {"'+fbGBM+'",} ';
                memberQuery += ',[Location].[JDM Flag] = {'+jdmFlag+',} ';
                memberQuery += ',[Location].[KD Flag] = {'+kdFlag+',} ';
                memberQuery += ',[Location].[Location Valid Flag] = {'+validFlag+',} '; 
                memberQuery += ',[Location].[Location Sorting Order] = {'+sortingOrder+',} '; //25.11.03 Sorting Order 추가
                //Location.Site Group4 속성
                memberQuery += ',[Location].[Site Group4$DisplayName] = {"'+fbLocationName+'",} ';
                memberQuery += ',[Location].[Site Group4$DisplayAlias] = {"'+fbLocationName+'",} ';
                // 2025.10.29 수정함.(Site Group4 관련 memberproperties 추가함.)
                memberQuery += ',[Location].[Site Group4 View Flag] = {true,} '; 
                memberQuery += ',[Location].[Site Group4 Valid Flag] = {'+validFlag+',} '; 
                memberQuery += ',[Location].[Site Group4 Sorting Order] = {'+sortingOrder+',} '; //25.11.03 Sorting Order 추가
                //+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++  
                // Attribute                      
                memberQuery += ',[Location].[Location Type] = {, "'+fbLocatioinType+'"} ';
                memberQuery += ',[Location].[Country Name] = {, "'+fbCountryName+'"} ';           
                memberQuery += ',[Location].[Sales Type] = {, "'+fbSalesType+'"} ';
                //2026.03.13 미입력 데이타 처리
                if(fbCompanyName != undefined && fbCompanyName != null && fbCompanyName != ""){
                    memberQuery += ',[Location].[Company Name] = {, "'+vdUtil.fn_getString(fbCompanyName)+'"} ';
                }
                if(fbCompanyCode != undefined && fbCompanyCode != null && fbCompanyCode != ""){
                    memberQuery += ',[Location].[Company] = {, "'+vdUtil.fn_getString(fbCompanyCode)+'"} ';
                }                
                    
                //memberQuery += ',[Location].[MF Site Stage] = {, "'+fbMFSiteStage+'"} '; // 2026.03.13 미사용함.(임재민프로 요청)
                memberQuery += ',[Location].[JDM Type] = {, "'+jdmType+'"} ';  // 2025.10.29 추가함.
                //+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
                // Region 예외처리 로직 
                if(fbRegion === "LATIN AMERICA"){
                    fbRegion = "LATIN_AMERICA";
                }
                if(fbRegion === "NORTH AMERICA"){
                    fbRegion = "NORTH_AMERICA";
                }
                memberQuery += ',[Location].[Region] = {, "'+fbRegion+'"} ';
                //+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++    

                //Hierarchy 선정한 것은 반드시 입력해야함
                memberQuery += ',[Location].[Site Group1] = {, "'+fbSiteGroup1+'"} '; //Hierarchy
                memberQuery += ',[Location].[Site Group2] = {, "'+fbSiteGroup1 +'_'+fbSiteGroup2+'"} '; //Hierarchy
                memberQuery += ',[Location].[Site Group3] = {, "'+fbSiteGroup1 +'_'+ fbSiteGroup2 +'_'+ fbSiteGroup3+'"} '; //Hierarchy
                memberQuery += ',[Location].[Site Group4] = {, "'+fbLocationCode+'"} '; //Hierarchy
                
                memberQuery += ',[Location].[All Location] = {, "All"} '; //Hierarchy
                memberQuery += ',[Location].[Location Country] = {, "-"} '; //Hierarchy
                memberQuery += ',[Location].[Location Region] = {, "-"} '; //Hierarchy 
                memberQuery += ',[Location].[Reporting Location] = {, "-"} '; //Hierarchy

               //Hierarchy
                memberQuery += ',[Location].[Site Org1] = {, "-"} '; //Hierarchy
                memberQuery += ',[Location].[Site Org2] = {, "-"} '; //Hierarchy
                memberQuery += ',[Location].[Site Org3] = {, "-"} '; //Hierarchy
                memberQuery += ');';
                vdCommon.debug("Create memberQuery::" + memberQuery);
                vdCommon.executeQuery("fn_save(MemberCreate)]", memberQuery);
                //++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

                let dimension = [];
                let measure = [];

                dimension.push('[Version].[Version Name].['+fbVersion+']');
                dimension.push('[Location].[Location].['+fbLocationCode+']');

                measure.push('Measure.[MF Site_Country Name Override] = "'+vdUtil.fn_getString(fbCountryName)+'";');
                //measure.push('Measure.[MF Site_Country Name] = "'+vdUtil.fn_getString(fbCountryName)+'";');
                measure.push('Measure.[MF Site_Country Code] = "'+vdUtil.fn_getString(fbCountryCode)+'";');
                measure.push('Measure.[MF Site_Region] = "'+vdUtil.fn_getString(fbRegion)+'";');
                measure.push('Measure.[MF Site_Business Type] = "'+vdUtil.fn_getString(fbBusinessType)+'";');
                measure.push('Measure.[MF Site_Sales Type] = "'+vdUtil.fn_getString(fbSalesType)+'";');
                measure.push('Measure.[MF Site_Company Name Override] = "'+ vdUtil.fn_getString(fbCompanyName)+'";');
                measure.push('Measure.[MF Site_Company Code] = "'+vdUtil.fn_getString(fbCompanyCode)+'";');
                measure.push('Measure.[MF Site_GBM] = "'+vdUtil.fn_getString(fbGBM)+'";');
                measure.push('Measure.[MF Site_JDM Flag Override] = "'+ vdUtil.fn_getString(fbJDMFlag)+'";');
                measure.push('Measure.[MF Site_KD Flag Override] = "'+ vdUtil.fn_getString(fbKDFlag)+'";');
                measure.push('Measure.[MF Site_MF SITE STAGE Override] = "'+ vdUtil.fn_getString(fbMFSiteStage)+'";');
                measure.push('Measure.[MF Site_Valid Flag Override] = "'+ vdUtil.fn_getString(fbValidFlag)+'";');
                measure.push('Measure.[MF Site_Group1] = "'+ vdUtil.fn_getString(fbSiteGroup1)+'";');
                measure.push('Measure.[MF Site_Group2] = "'+ vdUtil.fn_getString(fbSiteGroup2)+'";');
                measure.push('Measure.[MF Site_Group3 Override] = "'+ vdUtil.fn_getString(fbSiteGroup3)+'";');
                measure.push('Measure.[MF Site_Sorting Order] = ' + sortingOrder + ';');
                //measure.push('Measure.[MF Site_Group3] = "'+ vdUtil.fn_getString(fbSiteGroup3)+'";');
                
                if(rowStatus == "C"){
                    measure.push('Measure.[MF Site_Creation Time]= Now();');
                    measure.push('Measure.[MF Site_Created By]   = CurrentUser().[User Name];');
                    measure.push('Measure.[MF Site_Update Time]= Now();');
                    measure.push('Measure.[MF Site_Updated By]= CurrentUser().[User Name];') ;
                    vdCommon.createMeasure(dimension, measure);
                }else{
                    //Update
                    measure.push('Measure.[MF Site_Update Time]= Now();');
                    measure.push('Measure.[MF Site_Updated By]= CurrentUser().[User Name];') ;
                    vdCommon.updateMeasure(dimension, measure);
                }
            }
            return { "Code" : 0, "Msg" : "", "Rows" : "" };
            //

        }catch ( e ) {
            return { "Code" : -1, "Msg" : e.message };
        }
    }

/************************************************* Mapping logic *************************************************/
    // Mapping 함수 정의, 마지막에 선언을 해야 함수를 정상적으로 인식함
    const functionMap = {
        "fn_save" : fn_save
    };

    return {
        fn_loadFunction : fn_loadFunction
    };    
});