"""
* 프로그램명
    - PY_MNG_ItemSiteAsn

* 내용
    - GSCM에서 Sales Product 및 BOM 기준 ITEM Site 전송 (당시 PLC Status 반영)
    - NSCM에서는 Info를 참고로한 Vendor - Mtrl Site Asn 구성

* 변경이력
    - 2024.06.18 / 권태우 / Create
    - 2024.10.08 / 권태우 / df_in_BOMMaster 삭제, df_out_RoutingID 삭제
    - 2024.11.18 / 권태우 / df_in_BODItemMtrl 추가(Step 7)
    - 2024.11.21 / 권태우 / 재개발
    - 2025.02.06 / 권태우 / 내용정리

* Script Parameter
    - paramOutVersion : 기본값 : CWV_MP, 호출시에, 결과데이터를 Version Name을 별도로 지정하는데에 사용.

* Input Table
    - df_in_Demand       : Select (Version.[Version Name] * [Demand Type].[Demand Type] * [Demand].[DemandID] * [Location].[Location] * [Sales Domain].[Ship To] * [Time].[Week] * [Item].[Item] ) on row, ({Measure.[Dmd W_Qty]}) on column.filter(Measure.[Dmd W_Qty] > 0);
    - df_in_INV          : Select (Version.[Version Name] * [Documents].[OrderlineID] * [Location].[Location] * [Time].[Week] * [Item].[Item] ) on row, ({Measure.[Inv_Qty], Measure.[Inv Shuffle_Qty], Measure.[Intr_Qty], Measure.[Intr Shuffle_Qty], Measure.[Mfg Plan_Qty] }) on column.filter(Measure.[Inv_Qty] > 0 || Measure.[Inv Shuffle_Qty] > 0 || Measure.[Intr_Qty] > 0 || Measure.[Intr Shuffle_Qty] > 0);
    - df_in_MfgPlan      : Select (Version.[Version Name] * [Documents].[OrderlineID] * [Location].[Location] * [Time].[Week] * [Item].[Item] ) on row, ({ Measure.[Mfg Plan_Qty]}) on column.filter(Measure.[Mfg Plan_Qty] > 0);
    - df_in_Distorders   : Select (Version.[Version Name] * [Item].[Item] * [Location].[Location] * [Documents].[OrderlineID] * [Sub Location].[Sub Location] * [Trans Mode].[Trans Mode]) on row, ({ Measure.[Dist Order_SS Qty], Measure.[Dist Order Shuffle_SS Qty] }) on column.filter( Measure.[Dist Order_SS Qty] > 0 || Measure.[Dist Order Shuffle_SS Qty] > 0);
    - df_in_VendorMtrl   : Select (Version.[Version Name] * [Location].[Location] * [Item Material].[Item Material] * [Vendor].[Vendor] * [Global Top].[GT Code] * [Partner Vendor].[Partner Vendor] ) on row, ({Measure.[Vendor Mtrl_GT Name], Measure.[Vendor Mtrl_Quota]}) on column;
    - df_in_BOMComp      : Select (Version.[Version Name] * [Item].[Item] * [Location].[Location] * [BOM Info].[BOM ID] ) on row, ({Measure.[BOM Comp_Consume Qty], Measure.[BOM Comp_Eff Enddate], Measure.[BOM Comp_Eff Startdate], Measure.[BOM Comp_Valid Flag]}) on column;
    - df_in_BOMMaster    : Select (Version.[Version Name] * [Location].[Location] * [BOM Info].[BOM ID] ) on row, ({Measure.[BOM Master_BOM ID], Measure.[BOM Master_Eff Enddate], Measure.[BOM Master_Eff Startdate], Measure.[BOM Master_Priority], Measure.[BOM Master_Prty], Measure.[BOM Master_Status]}) on column;
    - df_in_SalesItemAsn : Select (Version.[Version Name] * [Item].[Item] * [Location].[Location] * [Sales Domain].[AP2] ) on row, ({Measure.[Sales Item Asn_Valid Flag]}) on column;
    - df_in_ItemSiteAsn  : Select (Version.[Version Name] * [Item].[Item] * [Location].[Location] ) on row, ({Measure.[Item Site Asn_Dmd Flag], Measure.[Item Site Asn_Cur Status], Measure.[Item Site Asn_Inv Flag], Measure.[Item Site Asn_Intransit Flag], Measure.[Item Site Asn_Mfg Plan Flag], Measure.[Item Site Asn_DistOrders Flag], Measure.[Item Site Asn_Sales Prod Flag], Measure.[Item Site Asn_Stage], Measure.[Item Site Asn_Supply Plan Flag], Measure.[Item Site Asn_Engine Flag]}) on column;

* 주요 Logic ( Data 처리 )

* Output Table
    - df_out_log
    - df_out_logDetail
    
    - df_out_ItemSiteAsn

* 데이타 초기화
    - DELETE DATA FOR MODEL [Item Site Association] WHERE  {[Version].[Version Name].filter(#.Name in {"CWV_MP"})};

* RUN 스크립트
    - EXEC plugin instance [PY_MNG_ItemSiteAsn] for measures {[Item Site Asn_Engine Flag]} using scope (&MPV) using arguments {(ExecutionMode, "MediumWeight"), ("IncludeNullRows", "False"), (paramOutVersion , "CWV_MP"), (MaxSliceTableCells, 200000000), (MaxConcurrency, 1), ([Param.o9_sys_log_level], "DEBUG")};

* Output Query
    - Select ( &MPV * [Item].[Item] * [Location].[Location] ) on row, ({
        Measure.[Item Site Asn_Dmd Flag],   // Demand 있는 것
        Measure.[Item Site Asn_Cur Status],  // Status
        Measure.[Item Site Asn_Inv Flag],    // 재고 있는것
        Measure.[Item Site Asn_Intransit Flag], // Intransit 있는 것
        Measure.[Item Site Asn_WIP Flag], // 확정 생산계획 있는것
        Measure.[Item Site Asn_Sales Prod Flag], // sales product asn Y/N
        Measure.[Item Site Asn_Stage], // Site Stage
        Measure.[Item Site Asn_Supply Plan Flag], // 자재 가용 대상
        Measure.[Item Site Asn_Engine Flag] // 엔진 대상
        }) on column ;

"""
import gc
import traceback
import datetime
import numpy as np
import pandas as pd
import tracemalloc
import re
import time
import os
from NSCMCommon import NSCMCommon as common
from NSCMCommon import VDCommon as vdCommon

########################################################################################################################
# local 개발 시에 필요한 공통 변수 선언
########################################################################################################################
# o9에 저장된 instanceName
str_instance = 'PY_MNG_ItemSiteAsn'
is_local = common.gfn_get_isLocal()

# 공통 Liblary 버전
COMMON_SOURCE_VERSION = common.G_SourceVersion
VD_SOURCE_VERSION = vdCommon.G_VD_SourceVersion

# value 변수 선언
PARAM_OUTVERSION_VALUE = "CWV_MP"

# input variable 확인
paramOutVersion = (
    PARAM_OUTVERSION_VALUE
    if is_local or not paramOutVersion or not paramOutVersion.strip()
    else paramOutVersion
)


########################################################################################################################
# log 설정 : PROGRAM file_name
########################################################################################################################
logger = common.G_Logger(p_py_name=str_instance)
common.gfn_set_local_logfile()
LOG_LEVEL = common.G_log_level
log_level_info = LOG_LEVEL.info()
log_level_debug = LOG_LEVEL.debug()
logger.debug(f'[START] {str_instance}')
logger.Start()


########################################################################################################################
# local function
########################################################################################################################
class CustomException(Exception):
    pass


def read_csv_file(file_name):
    return pd.read_csv(f"{file_name}.csv", low_memory=False, encoding="UTF-8")


def save_csv_file(df, file_name):
    if is_local:
        df.to_csv(os.path.dirname(__file__) + "\\" + f"{file_name}.csv", index=False)


def print_df(df, df_name, _localFlag=False):
    vdCommon.gfn_saveDf(df, df_name, _localFlag)


def step(string):
    vdCommon.gfn_stepLog(string)


def note(string, p_log_level=LOG_LEVEL.debug()):
    logger.Note(p_note=f'{string}', p_log_level=p_log_level)



def vd_log_start():
    log_path = os.path.dirname(__file__) if is_local else ""
    vdCommon.gfn_pyLog_start(paramOutVersion, str_instance, logger, is_local, log_path)


def vd_log_end():
    vdCommon.gfn_pyLog_end()


def delete_dfs(*dfs):
    for df in dfs:
        del df
        gc.collect()


def rename_and_delete_df(target_df):
    new_df = target_df
    delete_dfs(target_df)
    return new_df


def get_first_value(df, column_name):
    if not df.empty and column_name in df.columns:
        return df[column_name].values[0]
    return None  # 기본값 반환


def get_formatted_time(timestamp):
    """타임스탬프를 사람이 읽을 수 있는 형식으로 변환"""
    return datetime.datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d %H:%M:%S")



def format_size(size_in_bytes):
    """바이트 단위를 적절히 MB 또는 GB로 변환하여 문자열 반환"""
    if size_in_bytes >= 1024 ** 3:  # 1GB 이상일 때
        return f"{size_in_bytes / 1024 ** 3:.1f} GB"
    else:
        return f"{size_in_bytes / 1024 ** 2:.1f} MB"


def run_time_minutes(start_time):
    """실행 시간을 계산하고, 소수점 2자리로 반환."""
    return str(round((time.time() - start_time) / 60, 2)) + " minutes"




########################################################################################################################
# logic start
########################################################################################################################
if __name__ == '__main__':
    # Batch 시작
    vd_log_start()

    # 현재 메모리 사용량과 피크 메모리 사용량 체크 시작
    tracemalloc.start()
    start_time = time.time()

    step(f'===================== plugin Execution Start ({get_formatted_time(start_time)}) =====================')
    step(f'=====> NSCMCommon Version check - {COMMON_SOURCE_VERSION}')
    step(f'=====> VDCommon Version check - {VD_SOURCE_VERSION}')
    step(f'=====> input value check - paramOutVersion : {paramOutVersion}')

    try:
        ################################################################################################################
        # STEP 1 : 전처리 - 모듈 내에서 사용될 input table load
        ################################################################################################################
        step('=====> STEP1 Start : 전처리 - 모듈 내에서 사용될 input table load')

        if is_local:
            df_in_Demand = read_csv_file("df_in_Demand")
            df_in_INV = read_csv_file("df_in_INV")
            df_in_MfgPlan = read_csv_file("df_in_MfgPlan")
            df_in_Distorders = read_csv_file("df_in_Distorders")
            df_in_VendorMtrl = read_csv_file("df_in_VendorMtrl")
            df_in_BOMComp = read_csv_file("df_in_BOMComp")
            df_in_BOMMaster = read_csv_file("df_in_BOMMaster")
            df_in_SalesItemAsn = read_csv_file("df_in_SalesItemAsn")
            df_in_ItemSiteAsn = read_csv_file("df_in_ItemSiteAsn")


        print_df(df_in_Demand, 'STEP 1 - Input table load .... df_in_Demand')
        print_df(df_in_INV, 'STEP 1 - Input table load .... df_in_INV')
        print_df(df_in_MfgPlan, 'STEP 1 - Input table load .... df_in_MfgPlan')
        print_df(df_in_Distorders, 'STEP 1 - Input table load .... df_in_Distorders')
        print_df(df_in_VendorMtrl, 'STEP 1 - Input table load .... df_in_VendorMtrl')
        print_df(df_in_BOMComp, 'STEP 1 - Input table load .... df_in_BOMComp')
        print_df(df_in_BOMMaster, 'STEP 1 - Input table load .... df_in_BOMMaster')
        print_df(df_in_SalesItemAsn, 'STEP 1 - Input table load .... df_in_SalesItemAsn')
        print_df(df_in_ItemSiteAsn, 'STEP 1 - Input table load .... df_in_ItemSiteAsn')

        step('=====> STEP1 End')
        
        

        ################################################################################################################
        # STEP 2 : DataFrame Column 변수 처리
        ################################################################################################################
        step('=====> STEP2 Start : DataFrame Column 변수 처리')

        VERSION_NAME_COLUMN = 'Version.[Version Name]'
        LOCATION_COLUMN = 'Location.[Location]'
        SUB_LOCATION_COLUMN = 'Sub Location.[Sub Location]'
        ITEM_COLUMN = 'Item.[Item]'
        TIME_WEEK_COLUMN = 'Time.[Week]'
        DOCUMENTS_ORDERLINEID_COLUMN = 'Documents.[OrderlineID]'

        INTER_FROM_SITE_ID_COLUMN = 'Intr_From Site ID'
        INTER_SHUFFLE_SITE_ID_COLUMN = 'Intr Shuffle_From Site ID'

        DIST_ORDER_FROM_SITE_ID_COLUMN = 'Dist Order_From Site ID'
        DIST_ORDER_TO_SITE_ID_COLUMN = 'Dist Order_To Site ID'
        DIST_ORDER_SHUFFLE_FROM_SITE_ID_COLUMN = 'Dist Order Shuffle_From Site ID'
        DIST_ORDER_SHUFFLE_TO_SITE_ID_COLUMN = 'Dist Order Shuffle_To Site ID'

        ITEM_SITE_ASN_CUR_STATUS_COLUMN = 'Item Site Asn_Cur Status'
        ITEM_SITE_ASN_ENGINE_FLAG_COLUMN = 'Item Site Asn_Engine Flag'
        ITEM_SITE_ASN_ITEM_GRP_COLUMN = 'Item Site Asn_Item Grp'
        ITEM_SITE_ASN_SALES_PROD_ASN_COLUMN = 'Item Site Asn_Sales Prod Asn'
        ITEM_SITE_ASN_STAGE_COLUMN = 'Item Site Asn_Stage'

        ITEM_METERIAL_COLUMN = 'Item Material.[Item Material]'
        TRANS_MODE_COLUMN = 'Trans Mode.[Trans Mode]'

        DMD_W_QRY_COLUMN = 'Dmd W_Qty'
        INTR_QTY_COLUMN = 'Intr_Qty'
        INTR_SHUFFLE_QTY_COLUMN = 'Intr Shuffle_Qty'
        INV_QTY_COLUMN = 'Inv_Qty'
        INV_SHUFFLE_QTY_COLUMN = 'Inv Shuffle_Qty'
        MFG_PLAN_QTY_COLUMN = 'Mfg Plan_Qty'
        QTY_COLUMN = 'Qty'
        DIST_ORDER_SS_QTY_COLUMN = 'Dist Order_SS Qty'
        DIST_ORDER_SHUFFLE_SS_QTY_COLUMN = 'Dist Order Shuffle_SS Qty'
        BOD_ITEM_MTRL_QTY_COLUMN = 'BODItemMtrl_Qty'

        BOM_ID_COLUMN = 'BOM Info.[BOM ID]'
        BOM_MASTER_ID_COLUMN = 'BOM Master_BOM ID'
        BOM_MASTER_EFF_ENDDATE_COLUMN = 'BOM Master_Eff Enddate'
        BOM_MASTER_EFF_STARTDATE_COLUMN = 'BOM Master_Eff Startdate'
        BOM_MASTER_PRIORITY_COLUMN = 'BOM Master_Priority'
        BOM_MASTER_STATUS_COLUMN = 'BOM Master_Status'

        BOM_COMP_CONSUME_QTY_COLUMN = 'BOM Comp_Consume Qty'
        BOM_COMP_EFF_ENDDATE_COLUMN = 'BOM Comp_Eff Enddate'
        BOM_COMP_EFF_STARTDATE_COLUMN = 'BOM Comp_Eff Startdate'
        BOM_COMP_VAILD_FLAG_COLUMN = 'BOM Comp_Valid Flag'
        BOM_MASTER_PRTY_COLUMN = 'BOM Master_Prty'
        SALES_DOMAIN_AP2_COLUMN = 'Sales Domain.[AP2]'
        SALES_ITEM_ASN_VAILD_FLAG_COLUMN = 'Sales Item Asn_Valid Flag'
        DEMAND_TYPE_COLUMN = 'Demand Type.[Demand Type]'
        DEMAND_ID_COLUMN = 'Demand.[DemandID]'
        SALES_DOMAIN_SHIP_TO_COLUMN = 'Sales Domain.[Ship To]'
        ITEM_SITE_ASN_DMD_FLAG_COLUMN = 'Item Site Asn_Dmd Flag'
        ITEM_SITE_ASN_INV_FLAG_COLUMN = 'Item Site Asn_Inv Flag'
        ITEM_SITE_ASN_INTRANSIT_FLAG_COLUMN = 'Item Site Asn_Intransit Flag'
        ITEM_SITE_ASN_MFG_PLAN_FLAG_COLUMN = 'Item Site Asn_Mfg Plan Flag'
        ITEM_SITE_ASN_DISTORDERS_FLAG_COLUMN = 'Item Site Asn_DistOrders Flag'
        ITEM_SITE_ASN_SALES_PROD_FLAG_COLUMN = 'Item Site Asn_Sales Prod Flag'
        ITEM_SITE_ASN_SUPPLY_PLAN_FLAG_COLUMN = 'Item Site Asn_Supply Plan Flag'
        VENDOR_COLUMN = 'Vendor.[Vendor]'
        GLOBAL_TOP_GT_CODE_COLUMN = 'Global Top.[GT Code]'
        PARTNER_VENDOR_COLUMN = 'Partner Vendor.[Partner Vendor]'
        VENDOR_MTRL_GT_NAME_COLUMN = 'Vendor Mtrl_GT Name'
        VENDOR_MTRL_QUOTA_COLUMN = 'Vendor Mtrl_Quota'
        
        df_ItemSiteAsn_columns = [
            VERSION_NAME_COLUMN,ITEM_COLUMN, LOCATION_COLUMN,
            ITEM_SITE_ASN_ENGINE_FLAG_COLUMN, ITEM_SITE_ASN_DMD_FLAG_COLUMN, ITEM_SITE_ASN_INV_FLAG_COLUMN,
            ITEM_SITE_ASN_MFG_PLAN_FLAG_COLUMN, ITEM_SITE_ASN_DISTORDERS_FLAG_COLUMN, ITEM_SITE_ASN_SUPPLY_PLAN_FLAG_COLUMN,
        ]

        step('=====> STEP2 End')




        ################################################################################################################
        # STEP 3 :  데이터 선 가공
        ################################################################################################################
        step('=====> STEP3 Start : input data machining')

        # ====================> STEP3 by 1 (Start) -> Item Site Asn_Dmd Flag Update

        drop_column = [col for col in list(df_in_Demand.columns) if col not in [ITEM_COLUMN, LOCATION_COLUMN]]
        df_Demand = df_in_Demand.drop(labels=drop_column, axis=1, inplace=False).drop_duplicates()
        df_Demand[ITEM_SITE_ASN_DMD_FLAG_COLUMN] = True
        df_Demand[ITEM_SITE_ASN_ENGINE_FLAG_COLUMN] = True
        print_df(df_Demand, 'STEP3 by 1.1 ____ df_Demand .... modify')

        # ====================> STEP3 by 1 (End)




        # ====================> STEP3 by 2 (Start) -> Item Site Asn_Inv Flag

        drop_column = [col for col in list(df_in_INV.columns) if col not in [ITEM_COLUMN, LOCATION_COLUMN]]
        df_INV = df_in_INV.drop(labels=drop_column, axis=1, inplace=False).drop_duplicates()
        df_INV[ITEM_SITE_ASN_INV_FLAG_COLUMN] = True
        df_INV[ITEM_SITE_ASN_ENGINE_FLAG_COLUMN] = True
        print_df(df_INV, 'STEP3 by 1.1 ____ df_INV .... modify')

        # ====================> STEP3 by 2 (End)




        # ====================> STEP3 by 3 (Start) -> Item Site Asn_Mfg Plan Flag

        drop_column = [col for col in list(df_in_MfgPlan.columns) if col not in [ITEM_COLUMN, LOCATION_COLUMN]]
        df_MfgPlan = df_in_MfgPlan.drop(labels=drop_column, axis=1, inplace=False).drop_duplicates()
        df_MfgPlan[ITEM_SITE_ASN_MFG_PLAN_FLAG_COLUMN] = True
        df_MfgPlan[ITEM_SITE_ASN_ENGINE_FLAG_COLUMN] = True
        print_df(df_MfgPlan, 'STEP3 by 1.1 ____ df_MfgPlan .... modify')

        # ====================> STEP3 by 3 (End)




        # ====================> STEP3 by 4 (Start) -> Item Site Asn_DistOrders Flag

        drop_column = [col for col in list(df_in_Distorders.columns) if col not in [ITEM_COLUMN, LOCATION_COLUMN]]
        df_Distorders = df_in_Distorders.drop(labels=drop_column, axis=1, inplace=False).drop_duplicates()
        df_Distorders[ITEM_SITE_ASN_DISTORDERS_FLAG_COLUMN] = True
        df_Distorders[ITEM_SITE_ASN_ENGINE_FLAG_COLUMN] = True
        print_df(df_Distorders, 'STEP3 by 1.1 ____ df_Distorders .... modify')

        # ====================> STEP3 by 4 (End)





        # ====================> STEP3 by 5 (Start) -> Vendor 입력

        drop_column = [col for col in list(df_in_VendorMtrl.columns) if col not in [ITEM_METERIAL_COLUMN, GLOBAL_TOP_GT_CODE_COLUMN]]
        df_VendorMtrl = df_in_VendorMtrl.drop(labels=drop_column, axis=1, inplace=False).drop_duplicates()
        df_VendorMtrl[ITEM_SITE_ASN_CUR_STATUS_COLUMN] = True
        df_VendorMtrl[ITEM_SITE_ASN_ENGINE_FLAG_COLUMN] = True
        print_df(df_VendorMtrl, 'STEP3 by 1.1 ____ df_VendorMtrl .... modify')

        # ====================> STEP3 by 5 (End)




        # ====================> STEP3 by 6 (Start) -> Item Site Asn_Supply Plan Flag

        drop_column = [col for col in list(df_in_SalesItemAsn.columns) if col not in [ITEM_COLUMN, LOCATION_COLUMN]]
        df_SalesItemAsn = df_in_SalesItemAsn.drop(labels=drop_column, axis=1, inplace=False).drop_duplicates()
        df_SalesItemAsn[ITEM_SITE_ASN_SUPPLY_PLAN_FLAG_COLUMN] = True
        df_SalesItemAsn[ITEM_SITE_ASN_ENGINE_FLAG_COLUMN] = True
        print_df(df_SalesItemAsn, 'STEP3 by 1.1 ____ df_SalesItemAsn .... modify')

        # ====================> STEP3 by 6 (End)




        # ====================> STEP3 by 7 (Start) -> PlanItemSet 구성

        drop_column = [col for col in list(df_in_BOMComp.columns) if col not in [ITEM_COLUMN]]
        df_BOMComp_item = df_in_BOMComp.drop(labels=drop_column, axis=1, inplace=False).drop_duplicates()
        print_df(df_BOMComp_item, 'STEP3 by 7.1 ____ df_BOMComp_item .... modify')

        drop_column = [col for col in list(df_in_BOMMaster.columns) if col not in [BOM_MASTER_ID_COLUMN]]
        df_BOMMaster_item = df_in_BOMMaster.drop(labels=drop_column, axis=1, inplace=False).drop_duplicates()
        df_BOMMaster_item.rename(columns={BOM_MASTER_ID_COLUMN: ITEM_COLUMN}, inplace=True)
        print_df(df_BOMMaster_item, 'STEP3 by 7.2 ____ df_BOMMaster_item .... modify')

        df_PlanItemSet = pd.concat([df_Demand, df_INV, df_MfgPlan, df_Distorders, df_VendorMtrl, df_SalesItemAsn,
                                    df_BOMComp_item, df_BOMMaster_item]).drop_duplicates()
        print_df(df_PlanItemSet, 'STEP3 by 7.3 ____ df_PlanItemSet .... modify final')

        # ====================> STEP3 by 7 (End)





        # ====================> STEP3 by 8 (Start) -> PlanItemSet 대상 Item engine flag  true 설정

        # 조인 수행
        df_in_ItemSiteAsn = df_in_ItemSiteAsn[df_in_ItemSiteAsn[ITEM_COLUMN].isin(df_PlanItemSet[ITEM_COLUMN])].copy()
        df_in_ItemSiteAsn[ITEM_SITE_ASN_ENGINE_FLAG_COLUMN] = True
        print_df(df_in_ItemSiteAsn, 'STEP3 by 8.1 ____ df_in_ItemSiteAsn .... final')

        # ====================> STEP3 by 8 (End)

        step('=====> STEP3 End')
        
        
        

        ################################################################################################################
        # STEP 4 : output data machining
        ################################################################################################################
        step('=====> STEP4 Start : output data machining')

        # 최종 아웃풋
        df_out_ItemSiteAsn = rename_and_delete_df(df_in_ItemSiteAsn)
        df_out_ItemSiteAsn[VERSION_NAME_COLUMN] = paramOutVersion

        # 필요한 칼럼 선택
        df_out_ItemSiteAsn = df_out_ItemSiteAsn[df_ItemSiteAsn_columns].drop_duplicates()

        # O9에서 Type 을 다르게 인식해서 오류나는 케이스 방지
        df_out_ItemSiteAsn = df_out_ItemSiteAsn.astype({
            ITEM_SITE_ASN_ENGINE_FLAG_COLUMN: bool,
            ITEM_SITE_ASN_DMD_FLAG_COLUMN: bool,
            ITEM_SITE_ASN_INV_FLAG_COLUMN: bool,
            ITEM_SITE_ASN_MFG_PLAN_FLAG_COLUMN: bool,
            ITEM_SITE_ASN_DISTORDERS_FLAG_COLUMN: bool,
            ITEM_SITE_ASN_SUPPLY_PLAN_FLAG_COLUMN: bool,
        }, copy=True)

        step('=====> STEP4 End')
        
        
        

        ################################################################################################################
        # STEP 5 : output table create
        ################################################################################################################
        step('=====> STEP5 Start : Final output table create')

        print_df(df_out_ItemSiteAsn, 'output table create .... df_out_ItemSiteAsn', True)

        step('=====> STEP5 End')

        # 현재 메모리 사용량과 피크 메모리 사용량 체크 / 실행 시간 계산 (초 단위 -> 분 단위로 변환)
        current, peak = tracemalloc.get_traced_memory()

        step(f'=====> current: {format_size(current)}, peak: {format_size(peak)}, execution time: {run_time_minutes(start_time)}')
        step(f'===================== plugin Execution End ({get_formatted_time(time.time())}) =====================')
        tracemalloc.stop()

    except CustomException as e:
        step(f'=====> CustomException : {e}')
        df_out_ItemSiteAsn = pd.DataFrame(columns=df_ItemSiteAsn_columns)

    except Exception as ex:
        step(f'=====> Exception : {traceback.format_exc()}')
        df_out_ItemSiteAsn = pd.DataFrame(columns=df_ItemSiteAsn_columns)
        logger.Error()
        vdCommon.gfn_pyLog_error(traceback.format_exc())

    finally:
        vd_log_end()
        df_out_log = vdCommon.gfn_getLog()
        df_out_logDetail = vdCommon.gfn_getLogDetail()
        logger.Finish()
        step('=====> Batch end')
