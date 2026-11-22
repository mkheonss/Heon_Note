define('o9.NSCM.commonLibVD', ['o9.NSCM.commonLib'], function (commonLib) {
    // 사업부별 로직 추가 ( prefix : VD, DA, MX, DP, CO )
    class VDCommon extends commonLib.NSCMCommon{
        constructor(programName) {
            super(programName);
        }

        // 추가 기능을 정의 한다.
        fn_getUserName() {
            return this.selectResult("CurrentUser().[Name]");
        }

        // 2025-11-26 : 사업부 코드로 로직 분기를 위해 추가
        fn_getDivision() {
            return "VD";
        }

        // 2026-01-13 : [Version].[Version Name].[CWV_MP]
        /*
        fn_getVersion() {
            return "[Version].[Version Name].[CWV_MP]";
        }
        */

        // 2026-02-02 : CWV_MP
        /*
        fn_getVersionName() {
            return "CWV_MP";
        }
        */
    }

    // 사업부별 로직 추가 ( prefix : VD, DA, MX, DP, CO )
    class VDUtil extends commonLib.NSCMUtil{
        // 2026-02-03 : 사업부 코드로 로직 분기를 위해 추가 : Util 에서도 사용할 경우가 있어서 추가
        fn_getDivision() {
            return "VD";
        }

        // 2026-02-03 : [Version].[Version Name].[CWV_MP] : Util 에서도 사용할 경우가 있어서 추가
        /*
        fn_getVersion() {
            return "[Version].[Version Name].[CWV_MP]";
        }
        */

        // 2026-02-03 : CWV_MP : Util 에서도 사용할 경우가 있어서 추가
        /*
        fn_getVersionName() {
            return "CWV_MP";
        }
        */
    }

    var VdCommon = VDCommon;
    var VdUtil = VDUtil;

    // 사업부 코드는 대문자로 사용해야 하지만, vd 는 이미 Vd 로 많이 사용하고 있어서 VD, Vd 를 같이 넘겨줌.
    return {VDCommon, VDUtil, VdCommon, VdUtil};
});