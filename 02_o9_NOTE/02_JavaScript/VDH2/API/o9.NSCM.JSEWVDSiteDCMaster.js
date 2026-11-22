define('o9.NSCM.JSEWVDSiteDCMaster', ['o9/data/query', 'o9/data/cellset', 'o9.NSCM.commonLibVD', 'o9.NSCM.JSEWCommonVD'], function() {    
    /*------------------------------------------------------------------------------------------------------------*/
    // 프로그램명 : o9.NSCM.JSEWVDSiteDCMaster
    // Action Button : EWVDSiteDCMaster
    // 화면명 : Site(DC)
    // 2026.04.09 최초 생성                                                                         / hnsk92.jeong */
    /*-----------------------------------------------------------------------------------------------------------*/

    const programName = "o9.NSCM.JSEWVDSiteDCMaster";
    const commonLib = require('o9.NSCM.commonLibVD');
    const commonUtil = new commonLib.VDUtil();
    
    // Define constants
    const DISPLAY_NAME = "DisplayName";
    const DEFAULT_LIMIT = 3000;
    const NO_LIMIT = -1;

    const AOP_FILTERSALESTYPE = "FilterSalesType";

    const DIM = Object.freeze({
        VERSION: 'Version',
        COUNTRY: 'Country',
        COMPANY: 'Company',
        LOCATION: 'Location',
        ITEM: 'Item',
        
    });
    
    const ATTR = Object.freeze({
        VERSIONNAME: 'Version Name',
        LOCATION: 'Location',
        COUNTRY: 'Country',
        COMPANY: 'Company',
        SITEGROUP1: 'Site Group1',
        SITEGROUP2: 'Site Group2',
        SITEGROUP3: 'Site Group3',
        SITEGROUP4: 'Site Group4',
        BIZTYPE: 'Biz Type',
        SHIPMENTTYPE: 'Shipment Type',
        ITEMSTD1: 'Item Std1',
        ITEMSTD2: 'Item Std2',
        ITEMSTD3: 'Item Std3',
        ITEMSTD4: 'Item Std4',
        SECTION: 'Section',
    });

    function dimAttr(dim, attr) {
        return `[${dim}].[${attr}]`;
    }

    const VERSION_VERSIONNAME = dimAttr(DIM.VERSION, ATTR.VERSIONNAME);
    const COUNTRY_COUNTRY = dimAttr(DIM.COUNTRY, ATTR.COUNTRY);
    const COMPANY_COMPANY = dimAttr(DIM.COMPANY, ATTR.COMPANY);
    const LOCATION_SITEGROUP1 = dimAttr(DIM.LOCATION, ATTR.SITEGROUP1);
    const LOCATION_SITEGROUP2 = dimAttr(DIM.LOCATION, ATTR.SITEGROUP2);
    const LOCATION_SITEGROUP3 = dimAttr(DIM.LOCATION, ATTR.SITEGROUP3);
    const LOCATION_SITEGROUP4 = dimAttr(DIM.LOCATION, ATTR.SITEGROUP4);
    const LOCATION_LOCATION = dimAttr(DIM.LOCATION, ATTR.LOCATION);
    const ITEM_ITEMSTD1 = dimAttr(DIM.ITEM, ATTR.ITEMSTD1);
    const ITEM_ITEMSTD2 = dimAttr(DIM.ITEM, ATTR.ITEMSTD2);
    const ITEM_ITEMSTD3 = dimAttr(DIM.ITEM, ATTR.ITEMSTD3);
    const ITEM_ITEMSTD4 = dimAttr(DIM.ITEM, ATTR.ITEMSTD4);
    const ITEM_SECTION = dimAttr(DIM.ITEM, ATTR.SECTION);

    const NS_DEF = {
        SITE_GROUP1_DC: 'NSUISiteGrp1DCView',
        SITE_GROUP2_DC: 'NSUISiteGrp2DCView',
        SITE_GROUP3_DC: 'NSUISiteGrp3DCView',
        LOCATION_DC: 'NSUILocationDC',
    };
    
    const NS = Object.freeze(
        Object.fromEntries(
            Object.entries(NS_DEF).map(([key, val]) => [key, `&${val}`])
        )
    );

    const Measure = Object.freeze({
        siteDcProdGroupAsnUseFlag: "Site DC Prod Group ASN_Use Flag",
    });

    const fullMeasureName = (_measure_name) => `Measure.[${_measure_name}]`;
    
    const makeSuccess = (rows, msg) => ({
        Code: 0,
        Msg: msg || '',
        Rows: rows || []
    });

    const makeError = (code, msg) => ({
        Code: code,
        Msg: msg
    });

    function _parseParams(o9Params) {
        const parsingParams = (typeof o9Params === 'string')
            ? JSON.parse(o9Params)
            : (o9Params || {});

        if (!parsingParams.fbFuncName) {
            throw new Error('fbFuncName is required.');
        }
        const fbParams = parsingParams.fbParams || {};
        const limitValue = fbParams.limit ?? DEFAULT_LIMIT;

        return {
            ...parsingParams,
            fbParams: {
                includeField: '',
                includeProperty: undefined,
                existAll: false,
                existBlank: false,
                existHyphen: false,
                where: {},
                filters: {},
                isDisplayNameWithCode: true,
                ...fbParams,
                limit: limitValue == NO_LIMIT ? '' : `limit ${limitValue}`
            }
        };
    }

    function fn_loadFunction(o9Params) {
        const pjtCommon = new commonLib.VDCommon(`${programName}.${arguments.callee.name}`);

        try {
            pjtCommon.debug(o9Params);
            const parsedParams = _parseParams(o9Params);
            const fn = functionMap[parsedParams?.fbFuncName];
            if (!fn) {
                return makeError(1, `Undefined function: ${fbFuncName}`);
            }
            
            // execute function
            const rtn = fn(parsedParams);
            return rtn;

        } catch ( e ) {
            pjtCommon.error(e.message);
            return makeError(-1, e.message);
        } finally {
            pjtCommon.programEnd();
        }
    };
    
/* [Define API funcs] ------------------------------------------------------------------------------------------------------------ */

    /*
{
    "fbFuncName": "fn_prefilter_Location",
    "fbParams": {
        "filters": {
            "[Item].[Item Std1]": {
                "SelectedMembers": [],
                "SelectedMembersAlias": [],
                "MemberFilter": "",
                "DimensionAliasName": "Prod"
            },
            "[Item].[Item Std2]": {
                "SelectedMembers": ["A/C_SAC_EHS"],
                "SelectedMembersAlias": [],
                "MemberFilter": "",
                "DimensionAliasName": "Prod"
            },
            "[Item].[Item Std3]": {
                "SelectedMembers": ["PC_NP_Chromebook"],
                "SelectedMembersAlias": [],
                "MemberFilter": "",
                "DimensionAliasName": "Prod"
            },
            "[Location].[Site Group1]": {
                "SelectedMembers": [],
                "SelectedMembersAlias": [],
                "MemberFilter": "&NSUISiteGrp1DCView",
                "DimensionAliasName": "Site (To)"
            },
            "[Location].[Site Group2]": {
                "SelectedMembers": [],
                "SelectedMembersAlias": [],
                "MemberFilter": "&NSUISiteGrp2DCView",
                "DimensionAliasName": "Site (To)"
            },
            "[Location].[Site Group3]": {
                "SelectedMembers": [],
                "SelectedMembersAlias": [],
                "MemberFilter": "&NSUISiteGrp3DCView",
                "DimensionAliasName": "Site (To)"
            },
            "[Version].[Version Name]": {
                "SelectedMembers": [
                    "CurrentWorkingView"
                ],
                "SelectedMembersAlias": [
                    null
                ],
                "MemberFilter": "&CWV",
                "DimensionAliasName": "Plan"
            },
            "[Filter].[Filter]": {
                "SelectedMembers": [],
                "SelectedMembersAlias": [],
                "MemberFilter": ""
            }
        }
    }
}
    [주요 동작]
    - 입력된 filter 기준으로 Location별 ASN 사용 flag를 조회.
    - flag가 Y 인 Location만 추려냄.
    - 추린 결과로 [Location].[Location].SelectedMembers overwrite.
    */
    function fn_prefilter_Location(parsedParams) {
        const pjtCommon = new commonLib.VDCommon(`${programName}.${arguments.callee.name}`);
        pjtCommon.setLogLevel("Debug");

        try {
            pjtCommon.printParams(parsedParams);            

            // Location별 ASN 사용 여부를 조회하기 위한 기본 select 구문 구성.
            const dims = [commonUtil.fn_getFilterQuery2(parsedParams, LOCATION_LOCATION) || LOCATION_LOCATION];
            const measures = [];
            
            const itemStdFilterKeys = [ITEM_ITEMSTD1, ITEM_ITEMSTD2, ITEM_ITEMSTD3, ITEM_ITEMSTD4];
            const itemSections = new Set();

            itemStdFilterKeys.forEach(filterKey => {
                const itemStdClause = commonUtil.fn_getFilterQuery2(parsedParams, filterKey);
                if (!itemStdClause) {
                    return;
                }

                const sectionResult = pjtCommon.selectList([`${itemStdClause}.relatedmembers([${ATTR.SECTION}])`], [], "", "", "");
                for (let i = 0; i < sectionResult.cs.rowCount; i++) {
                    const sectionName = sectionResult.cs.row(i).cell(sectionResult.cs.memberColumnIndex(DIM.ITEM, ATTR.SECTION)).Name;
                    if (sectionName) {
                        itemSections.add(sectionName);
                    }
                }
            });

            // 현재 들어온 filter를 그대로 where 절에 반영.
            const filters = parsedParams.fbParams.filters ??= {};
            filters[LOCATION_LOCATION] ??= { SelectedMembers: [], MemberFilter: "" };

            const whereParts = [];
            Object.keys(filters)
                .filter(filterKey => filterKey !== LOCATION_LOCATION && !itemStdFilterKeys.includes(filterKey))
                .map(filterKey => commonUtil.fn_getFilterQuery2(parsedParams, filterKey))
                .filter(Boolean)
                .forEach(clause => whereParts.push(clause));

            const itemSectionMembers = Array.from(itemSections);
            if (itemSectionMembers.length > 0) {
                whereParts.push(`${ITEM_SECTION}${commonUtil.fn_filterStr(itemSectionMembers)}`);
            }
            whereParts.push(`${fullMeasureName(Measure.siteDcProdGroupAsnUseFlag)}== "Y"`);
            const where = whereParts.length > 0 ? `where { ${whereParts.join(", ")} } ` : "";
            pjtCommon.debug("prefilter where: " + where);

            // filtering된 Section에 대해 Site DC Prod Group ASN == "Y" 인 Location들 조회
            const result = pjtCommon.selectList(dims, measures, where, "", parsedParams.fbParams.limit);
            pjtCommon.printCsData(result, 3);

            const filteredLocationSet = new Set();
            for (let i = 0; i < result.cs.rowCount; i++) {
                const locationName = result.cs.row(i).cell(result.cs.memberColumnIndex(DIM.LOCATION, ATTR.LOCATION)).Name;
                if (!locationName) {
                    continue;
                }
                filteredLocationSet.add(locationName);
            }
            filters[LOCATION_LOCATION].SelectedMembers = Array.from(new Set([
                ...(filters[LOCATION_LOCATION].SelectedMembers || []),
                ...filteredLocationSet
            ]));

            pjtCommon.info("Filtered Location count: " + filters[LOCATION_LOCATION].SelectedMembers.length);
            pjtCommon.debug("Filtered Locations sample: " + JSON.stringify(filters[LOCATION_LOCATION].SelectedMembers.slice(0, 10)));

            // 갱신된 filters 전체를 반환해서 후속 처리에서 그대로 재사용할 수 있게 한다.
            return makeSuccess(filters);
        } catch(e) {
            pjtCommon.error(e.message);
            return makeError(-1, e.message);
        }
    }

    function _fn_validation() {

    }

    //
    function fn_save(parsedParams) {
        const pjtCommon = new commonLib.VDCommon(`${programName}.${arguments.callee.name}`);
        pjtCommon.setLogLevel("Debug");
        try {
            // _fn_validation(); // TODO
        } catch(e) {
            pjtCommon.error(e.message);
            return makeError(-1, e.message);
        }
    }

    const functionMap = {
        fn_prefilter_Location,
        fn_save,
    };

    return {
        fn_loadFunction
    };
});