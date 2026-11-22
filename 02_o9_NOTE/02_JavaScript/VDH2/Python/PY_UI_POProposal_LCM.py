"""

* 프로그램명
    - PY_UI_POProposal_LCM

*  변경이력
- 2026.04.14 / ybest7.park (박병훈) / Create

* Input Table
    - df_in_DIMItem = Select (Item.[Item Stage].[LCM].relatedmembers([Item]) * Item.[Class Category] * Item.[Product] * Item.[Product Group]);
    - df_in_SOPAdjLCM = Select ([Version].[Version Name] * [Location].[Location] * [To Item].[To Item] * [Item Material].[Item Material] * [Item Component].[Item Component] * [Sub Location].[Sub Location] * [Week1].[Week1] * [To Trans Mode].[To Trans Mode] ) on row,  ({Measure.[SOP Adjust LCM W_Before Adj Qty], Measure.[SOP Adjust LCM W_Chg Qty], Measure.[SOP Adjust LCM W_Chg Qty SOPW], Measure.[SOP Adjust LCM W_Chg Reason], Measure.[SOP Adjust LCM W_Create Time], Measure.[SOP Adjust LCM W_Created By], Measure.[SOP Adjust LCM W_DSR], Measure.[SOP Adjust LCM W_SOP Adj Qty], Measure.[SOP Adjust LCM W_SOP Adj Qty SOPW], Measure.[SOP Adjust LCM W_SOP Qty], Measure.[SOP Adjust LCM W_SOP Qty SOPW], Measure.[SOP Adjust LCM W_Update Time], Measure.[SOP Adjust LCM W_Updated By] , Measure.[Dummy]}) on column;
    - df_in_POProposalMgmt  = Select ([Version].[Version Name] * [Location].[Location] * [Item].[Class Category] * [Trans Mode].[Trans Mode] * [Sub Location].[Sub Location] * [Vendor].[Vendor] * [Product].[Product Group] ) on row, ({Measure.[Purchasing Proposal Master_FCST Week], Measure.[Purchasing Proposal Master_Lot Size], Measure.[Purchasing Proposal Master_POP Week], Measure.[Purchasing Proposal Master_POPSTL], Measure.[Purchasing Proposal Master_STATUS], Measure.[Dummy]}) on column;
    - df_in_POProposalNCOTERMS = Select ([Version].[Version Name] * [Location].[Location] * [Sub Location].[Sub Location] * [Vendor].[Vendor] * [Product].[Product Group] ) on row, ({Measure.[Purchasing Proposal Vendor_INCO1],  Measure.[Dummy]}) on column;
    - df_in_LCMPOPSend =   Select ([Version].[Version Name]* [Location].[Location] * [To Item].[To Item] * [Item].[Item] * [Time].[Week] * [Sequence].[Sequence] * [Trans Mode].[Trans Mode] * [Sub Location].[Sub Location] ) on row, ({Measure.[LCM PO Send_ETA Week],Measure.[LCM PO Send_Incoterms2],Measure.[LCM PO Send_POP ID],Measure.[LCM PO Send_Org Vendor],Measure.[Dummy]}) on column;
    - df_in_LCMBODW =  Select ([Version].[Version Name] * [Location].[Location] * [Time].[Week] *  [Item].[Item Stage].[LCM].relatedmembers([Item]) * [Sub Location].[Sub Location] * [Trans Mode].[Trans Mode] ) on row, ({Measure.[BOD Item W_BOD LT], Measure.[BOD Item W_Shipment LT], Measure.[Dummy]}) on column where {(Measure.[BOD Item W_BOD LT]>0) || (Measure.[BOD Item W_Shipment LT]>0)} ;
    - df_in_DOBList = Select ([Version].[Version Name] * [Location].[Location] * [Item].[Item Stage].[LCM].relatedmembers([Item]) * [Sub Location].[Sub Location] * [Trans Mode].[Trans Mode] ) on row, ({Measure.[BOD Item_Shipment LT], Measure.[BOD Item_BOD LT],Measure.[BOD Item_Multi Lot Qty],Measure.[Dummy]}) on column where {(Measure.[BOD Item_Shipment LT] >0) || (Measure.[BOD Item_BOD LT] > 0)};
    - df_in_MTRLINFORECORD = Select ([Version].[Version Name] * [Location].[Location] * [Item].[Item] * [Sequence].[Sequence] * [Vendor].[Vendor] * [Partner Vendor].[Partner Vendor] ) on row, ({ Measure.[Mtrl Info Record_Currency],   Measure.[Mtrl Info Record_Price],Measure.[Dummy]}) on column;
    - df_in_lastMonth  = select([Time].[Day] * [Time].[Week] * [Time].[Month].filter(#.Key >= &CurrentMonth.element(0).LeadOffset(-6).Key && #.Key <= &CurrentMonth.element(0).LeadOffset(-6).Key));
    - df_in_MPCurrWeek = Select ([Time].[Week].filter(#.Key >= &CurrentWeek.element(0).Key && #.Key <= &CurrentWeek.element(0).LeadOffset(52).Key) * [Time].[Day]) where {[Time].[Day of Week].[MON]};
    - df_in_CurrentWeek : Select (&CurrentWeek * [Time].[Day]) where {[Time].[Day of Week].[MON]};
    - df_in_Adhoc1POPFlag = Select ([Version].[Version Name] * [Location].[Location] * [Sequence].[Sequence] ) on row, ({Measure.[PO Proposal Flag_PurORG],Measure.[PO Proposal Flag_CY Flag],Measure.[PO Proposal Flag_DE Flag],Measure.[PO Proposal Flag_Description], Measure.[PO Proposal Flag_Status]}) on column;
    - df_in_Adhoc2Purch_grp = Select ([Version].[Version Name] * [Location].[Location] * [Item Material].[Item Material] ) on row, ({Measure.[Item Material Spec Plant_Procurement Type],Measure.[Item Material Spec Plant_Purchase Group],Measure.[Item Material Spec Plant_Storage Location]}) on column;
    - df_in_Adhoc3Purch_SLOC = Select ([Version].[Version Name] * [Location].[Location] * [Sequence].[Sequence] ) on row, ({Measure.[PO Proposal SLoc_PurORG], Measure.[PO Proposal SLoc_StorageLocation]}) on column;

* Out Put Table
     df_out_LCMPOSend = Select ([Version].[Version Name].[CWV_MP] * [Location].[Location] * [To Item].[To Item] * [Item].[Item] * [Time].[Week] * [Sequence].[Sequence] * [Trans Mode].[Trans Mode] * [Sub Location].[Sub Location] ) on row, ({Measure.[LCM PO Send_MFG Week], Measure.[LCM PO Send_CY Flag], Measure.[LCM PO Send_Class Category], Measure.[LCM PO Send_Confirm POP QTY], Measure.[LCM PO Send_Currency], Measure.[LCM PO Send_DE Flag], Measure.[LCM PO Send_DOMEXP], Measure.[LCM PO Send_ETA Week], Measure.[LCM PO Send_ETD Week], Measure.[LCM PO Send_GERP Send], Measure.[LCM PO Send_Incoterms1], Measure.[LCM PO Send_Incoterms2], Measure.[LCM PO Send_Lot Size], Measure.[LCM PO Send_MFG Week], Measure.[LCM PO Send_Mst Check], Measure.[LCM PO Send_Org Vendor], Measure.[LCM PO Send_PO Item], Measure.[LCM PO Send_PO No], Measure.[LCM PO Send_PO Status], Measure.[LCM PO Send_POP ID], Measure.[LCM PO Send_POP Qty], Measure.[LCM PO Send_POP Reason], Measure.[LCM PO Send_POP Reason Detail], Measure.[LCM PO Send_POPSTL], Measure.[LCM PO Send_Plant], Measure.[LCM PO Send_Price], Measure.[LCM PO Send_Pur Grp], Measure.[LCM PO Send_Pur Org], Measure.[LCM PO Send_Qty], Measure.[LCM PO Send_Receive Time], Measure.[LCM PO Send_Received By], Measure.[LCM PO Send_Reject Reason], Measure.[LCM PO Send_SLoc], Measure.[LCM PO Send_SOP Qty], Measure.[LCM PO Send_Send Date], Measure.[LCM PO Send_Send User], Measure.[LCM PO Send_Status], Measure.[LCM PO Send_Update Time], Measure.[LCM PO Send_Updated By], Measure.[LCM PO Send_Vendor]}) on column;

 * 테스트 스크립트
    EXEC plugin instance [PY_UI_POProposal_LCM] for measures {[LCM PO Send_CY Flag]} using scope (&MPV) using arguments {(ExecutionMode, "MediumWeight"), ("IncludeNullRows", "False"),(MaxSliceTableCells, 200000000), (MaxConcurrency, 1 ), ([Param.o9_sys_log_level], "DEBUG"), (ParamOutVersion, "CWV_MP")} ;
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
import pytz
from dateutil.relativedelta import relativedelta

########################################################################################################################
# local 개발 시에 필요한 공통 변수 선언
########################################################################################################################
# o9에 저장된 instanceName
str_instance = 'PY_UI_POProposal_LCM'
is_local = common.gfn_get_isLocal()

# 공통 Liblary 버전
COMMON_SOURCE_VERSION = common.G_SourceVersion
VD_SOURCE_VERSION = vdCommon.G_VD_SourceVersion

# input variable 확인
paramOutVersion = (
    "CWV_MP"
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
    try:
        file_path = f"{file_name}.csv"
        if not os.path.exists(file_path):
            step(f"=====> 파일이 존재하지 않습니다: {file_path}")
            return pd.DataFrame()  # 빈 DataFrame 반환
        return pd.read_csv(file_path, low_memory=False, encoding="UTF-8")

    except Exception as e:
        step(f"=====> CSV 파일 읽기 실패: {file_name}, 오류: {str(e)}")
        return pd.DataFrame()  # 에러 발생시 빈 DataFrame 반환


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


def vd_log_end() -> tuple:
    """
    로그 처리를 종료하고 로그 데이터프레임들을 반환하는 공통 함수

    Returns:
        tuple: (df_out_log, df_out_logDetail) 형태의 튜플
    """
    try:
        # 로그 종료 처리
        vdCommon.gfn_pyLog_end()

        # 로그 데이터프레임 가져오기
        df_out_log = vdCommon.gfn_getLog()
        df_out_logDetail = vdCommon.gfn_getLogDetail()

        return df_out_log, df_out_logDetail

    except Exception as e:
        step(f"=====> 로그 처리 중 오류 발생: {str(e)}")
        return None, None


def delete_dfs(*dfs):
    for df in dfs:
        del df
        gc.collect()


def rename_and_delete_df(df):
    """데이터프레임 최적화 및 메모리 사용량 감소"""
    if df is None:
        return None

    # 데이터프레임 복사 및 메모리 최적화
    result = df.copy()

    # 숫자형 컬럼의 데이터 타입 최적화
    for col in result.select_dtypes(include=['int', 'float']).columns:
        result[col] = pd.to_numeric(result[col], downcast='integer')

    # # 범주형 데이터 최적화
    # for col in result.select_dtypes(include=['object']).columns:
    #     if result[col].nunique() / len(result) < 0.5:  # 고유값이 50% 미만일 경우
    #         result[col] = result[col].astype('category')

    delete_dfs(df)
    return result


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
    """실행 시간을 계산하고, 분 또는 초 단위로 반환.
    초 단위가 0일 경우 초로 표시하고, 그 외에는 분으로 표시."""
    elapsed = time.time() - start_time
    if elapsed < 60:  # 1분 미만일 경우
        return str(round(elapsed, 2)) + " seconds"
    else:
        return str(round(elapsed / 60, 2)) + " minutes"


########################################################################################################################
# logic start
########################################################################################################################
if __name__ == '__main__':
    # 현재 메모리 사용량과 피크 메모리 사용량 체크 시작
    tracemalloc.start()
    start_time = time.time()

    # Batch 시작
    vd_log_start()
    step(f'===================== plugin Execution Start ({get_formatted_time(start_time)}) =====================')
    step(f'=====> NSCMCommon Version check - {COMMON_SOURCE_VERSION}')
    step(f'=====> VDCommon Version check - {VD_SOURCE_VERSION}')
    step(f'=====> input value check - paramOutVersion : {paramOutVersion}')

    try:
        ################################################################################################################
        # STEP 1 : 전처리 - 모듈 내에서 사용될 input table load
        ################################################################################################################
        step('=====> STEP 1 Start : 전처리 - 모듈 내에서 사용될 input table load')

        if is_local:
            df_in_DIMItem            = read_csv_file('df_in_DIMItem_VD17')
            df_in_SOPAdjLCM          = read_csv_file('df_in_SOPAdjLCM_VD17')
            df_in_POProposalMgmt     = read_csv_file('df_in_POProposalMgmt_VD17')
            df_in_POProposalNCOTERMS = read_csv_file('df_in_POProposalNCOTERMS_VD17')
            df_in_LCMPOPSend         = read_csv_file('df_in_LCMPOPSend_VD17')
            df_in_LCMBODW            = read_csv_file('df_in_LCMBODW_VD17')
            df_in_DOBList            = read_csv_file('df_in_DOBList_VD17')
            df_in_MTRLINFORECORD     = read_csv_file('df_in_MTRLINFORECORD_VD17')
            df_in_lastMonth          = read_csv_file('df_in_lastMonth_VD17')
            df_in_MPCurrWeek         = read_csv_file('df_in_MPCurrWeek_VD17')
            df_in_CurrentWeek        = read_csv_file('df_in_CurrentWeek_VD17')
            df_in_Adhoc1POPFlag      = read_csv_file('df_in_Adhoc1POPFlag_VD17')
            df_in_Adhoc2Purch_grp    = read_csv_file('df_in_Adhoc2Purch_grp_VD17')
            df_in_Adhoc3Purch_SLOC  = read_csv_file('df_in_Adhoc3Purch_SLOC_VD17')


        dataframes = {
            'df_in_DIMItem'                :          df_in_DIMItem,
            'df_in_SOPAdjLCM'              :          df_in_SOPAdjLCM,
            'df_in_POProposalMgmt'         :          df_in_POProposalMgmt,
            'df_in_POProposalNCOTERMS'     :          df_in_POProposalNCOTERMS,
            'df_in_LCMPOPSend'             :          df_in_LCMPOPSend,
            'df_in_LCMBODW'                :          df_in_LCMBODW,
            'df_in_DOBList'                :          df_in_DOBList,
            'df_in_MTRLINFORECORD'         :          df_in_MTRLINFORECORD,
            'df_in_lastMonth'              :          df_in_lastMonth,
            'df_in_MPCurrWeek'             :          df_in_MPCurrWeek,
            'df_in_CurrentWeek'            :          df_in_CurrentWeek,
            'df_in_Adhoc1POPFlag'          :          df_in_Adhoc1POPFlag,
            'df_in_Adhoc2Purch_grp'        :          df_in_Adhoc2Purch_grp,
            'df_in_Adhoc3Purch_SLOC'       :          df_in_Adhoc3Purch_SLOC }

        for name, df in dataframes.items():
            print_df(df, f'input table load .... {name}')

        step('=====> STEP 1 End')
        ################################################################################################################
        # STEP 2 : DataFrame Column 변수 처리
        ################################################################################################################
        step('=====> STEP 2 Start : DataFrame Column 변수 처리')

        Version_Name_COLUMN = 'Version.[Version Name]'
        Item_COLUMN = 'Item.[Item]'
        Item_Class_Category_COLUMN = 'Item.[Class Category]'
        Item_Product_COLUMN = 'Item.[Product]'
        Item_Product_Group_COLUMN = 'Item.[Product Group]'
        Item_Material_COLUMNS = 'Item Material.[Item Material]'
        Item_Component_COLUMN = 'Item Component.[Item Component]'

        Time_Week_COLUMN = 'Time.[Week]'
        Time_Day_COLUMN = 'Time.[Day]'
        Time_Month_COLUMN = 'Time.[Month]'
        To_Item_COLUMN = 'To Item.[To Item]'
        Week1_COLUMN = 'Week1.[Week1]'

        Location_COLUMN = 'Location.[Location]'
        Sub_Location_COLUMN = 'Sub Location.[Sub Location]'
        Trans_Mode_COLUMN = 'Trans Mode.[Trans Mode]'
        To_Trans_Mode_COLUMN = 'To Trans Mode.[To Trans Mode]'

        Vendor_COLUMN = 'Vendor.[Vendor]'
        Product_Group_COLUMN = 'Product.[Product Group]'
        Sequence_COLUMN = 'Sequence.[Sequence]'
        Partner_Vendor_COLUMN = 'Partner Vendor.[Partner Vendor]'

        SOP_Adjust_LCM_W_Before_Adj_Qty = 'SOP Adjust LCM W_Before Adj Qty'
        SOP_Adjust_LCM_W_Chg_Qty = 'SOP Adjust LCM W_Chg Qty'
        SOP_Adjust_LCM_W_Chg_Qty_SOPW = 'SOP Adjust LCM W_Chg Qty SOPW'
        SOP_Adjust_LCM_W_Chg_Reason = 'SOP Adjust LCM W_Chg Reason'
        SOP_Adjust_LCM_W_Create_Time = 'SOP Adjust LCM W_Create Time'
        SOP_Adjust_LCM_W_Created_By = 'SOP Adjust LCM W_Created By'
        SOP_Adjust_LCM_W_DSR = 'SOP Adjust LCM W_DSR'
        SOP_Adjust_LCM_W_SOP_Adj_Qty = 'SOP Adjust LCM W_SOP Adj Qty'
        SOP_Adjust_LCM_W_SOP_Adj_Qty_SOPW = 'SOP Adjust LCM W_SOP Adj Qty SOPW'
        SOP_Adjust_LCM_W_SOP_Qty = 'SOP Adjust LCM W_SOP Qty'
        SOP_Adjust_LCM_W_SOP_Qty_SOPW = 'SOP Adjust LCM W_SOP Qty SOPW'
        SOP_Adjust_LCM_W_Update_Time = 'SOP Adjust LCM W_Update Time'
        SOP_Adjust_LCM_W_Updated_By = 'SOP Adjust LCM W_Updated By'
        Dummy = 'Dummy'

        Purchasing_Proposal_Master_FCST_Week = 'Purchasing Proposal Master_FCST Week'
        Purchasing_Proposal_Master_Lot_Size = 'Purchasing Proposal Master_Lot Size'
        Purchasing_Proposal_Master_POP_Week = 'Purchasing Proposal Master_POP Week'
        Purchasing_Proposal_Master_POPSTL = 'Purchasing Proposal Master_POPSTL'
        Purchasing_Proposal_Master_STATUS = 'Purchasing Proposal Master_STATUS'
        Purchasing_Proposal_Vendor_INCO1 = 'Purchasing Proposal Vendor_INCO1'

        LCM_PO_Send_Currency = 'LCM PO Send_Currency'
        LCM_PO_Send_DOMEXP = 'LCM PO Send_DOMEXP'
        LCM_PO_Send_ETA_Week = 'LCM PO Send_ETA Week'
        LCM_PO_Send_ETD_Week = 'LCM PO Send_ETD Week'
        LCM_PO_Send_Incoterms1 = 'LCM PO Send_Incoterms1'
        LCM_PO_Send_Incoterms2 = 'LCM PO Send_Incoterms2'
        LCM_PO_Send_Lot_Size = 'LCM PO Send_Lot Size'
        LCM_PO_Send_MFG_Week = 'LCM PO Send_MFG Week'
        LCM_PO_Send_Mst_Check = 'LCM PO Send_Mst Check'
        LCM_PO_Send_Org_Vendor = 'LCM PO Send_Org Vendor'
        LCM_PO_Send_PO_Item = 'LCM PO Send_PO Item'
        LCM_PO_Send_PO_No = 'LCM PO Send_PO No'
        LCM_PO_Send_PO_Status = 'LCM PO Send_PO Status'
        LCM_PO_Send_POP_ID = 'LCM PO Send_POP ID'
        LCM_PO_Send_POP_Qty = 'LCM PO Send_POP Qty'
        LCM_PO_Send_Plant = 'LCM PO Send_Plant'
        LCM_PO_Send_Price = 'LCM PO Send_Price'
        LCM_PO_Send_Pur_Grp = 'LCM PO Send_Pur Grp'
        LCM_PO_Send_Pur_Org = 'LCM PO Send_Pur Org'
        LCM_PO_Send_SLoc = 'LCM PO Send_SLoc'
        LCM_PO_Send_SOP_Qty = 'LCM PO Send_SOP Qty'
        LCM_PO_Send_Status = 'LCM PO Send_Status'
        LCM_PO_Send_POPSTL = 'LCM PO Send_POPSTL'
        LCM_PO_Send_CY_Flag = 'LCM PO Send_CY Flag'
        LCM_PO_Send_DE_Flag = 'LCM PO Send_DE Flag'
        LCM_PO_Send_Class_Category = 'LCM PO Send_Class Category'
        LCM_PO_Send_Vendor = 'LCM PO Send_Vendor'

        BOD_Item_W_BOD_LT = 'BOD Item W_BOD LT'
        BOD_Item_W_Shipment_LT = 'BOD Item W_Shipment LT'
        BOD_Item_BOD_LT = 'BOD Item_BOD LT'
        BOD_Item_Multi_Lot_Qty = 'BOD Item_Multi Lot Qty'
        BOD_Item_Shipment_LT = 'BOD Item_Shipment LT'

        Mtrl_Info_Record_Category = 'Mtrl Info Record_Category'
        Mtrl_Info_Record_Country = 'Mtrl Info Record_Country'
        Mtrl_Info_Record_Currency = 'Mtrl Info Record_Currency'
        Mtrl_Info_Record_Description = 'Mtrl Info Record_Description'
        Mtrl_Info_Record_Exchange_Rate = 'Mtrl Info Record_Exchange Rate'
        Mtrl_Info_Record_GT_Code = 'Mtrl Info Record_GT Code'
        Mtrl_Info_Record_Info_Price_USD = 'Mtrl Info Record_Info Price USD'
        Mtrl_Info_Record_Intransit_LT = 'Mtrl Info Record_Intransit LT'
        Mtrl_Info_Record_Plan_Del_Time = 'Mtrl Info Record_Plan Del Time'
        Mtrl_Info_Record_Price = 'Mtrl Info Record_Price'
        Mtrl_Info_Record_Price_Unit = 'Mtrl Info Record_Price Unit'
        Mtrl_Info_Record_Purchase_Org = 'Mtrl Info Record_Purchase Org'
        Mtrl_Info_Record_Quota = 'Mtrl Info Record_Quota'
        Mtrl_Info_Record_Ship_Instructions = 'Mtrl Info Record_Ship Instructions'
        Mtrl_Info_Record_Supplier_LT = 'Mtrl Info Record_Supplier LT'
        Mtrl_Info_Record_Valid_From = 'Mtrl Info Record_Valid From'
        Mtrl_Info_Record_Valid_From_Week = 'Mtrl Info Record_Valid From Week'
        Mtrl_Info_Record_Valid_To = 'Mtrl Info Record_Valid To'
        Mtrl_Info_Record_Valid_To_Week = 'Mtrl Info Record_Valid To Week'
        Mtrl_Info_Record_Valuation_Type = 'Mtrl Info Record_Valuation Type'
        Mtrl_Info_Record_Vendor_Schema_Grp = 'Mtrl Info Record_Vendor Schema Grp'

        PO_Proposal_Flag_PurORG = 'PO Proposal Flag_PurORG'
        PO_Proposal_Flag_CY_Flag = 'PO Proposal Flag_CY Flag'
        PO_Proposal_Flag_DE_Flag = 'PO Proposal Flag_DE Flag'
        PO_Proposal_Flag_Description = 'PO Proposal Flag_Description'
        PO_Proposal_Flag_Status = 'PO Proposal Flag_Status'

        Item_Material_Spec_Plant_Procurement_Type = 'Item Material Spec Plant_Procurement Type'
        Item_Material_Spec_Plant_Purchase_Group = 'Item Material Spec Plant_Purchase Group'
        Item_Material_Spec_Plant_Storage_Location = 'Item Material Spec Plant_Storage Location'

        PO_Proposal_SLoc_PurORG = 'PO Proposal SLoc_PurORG'
        PO_Proposal_SLoc_StorageLocation = 'PO Proposal SLoc_StorageLocation'

        Sequence = 'Sequence'
        Sequence_W = 'Sequence_W'

        step('=====> STEP 2 End')

        ################################################################################################################
        # STEP 3 :  input data machining
        ################################################################################################################
        step('=====> STEP 3 Start : input data machining')

        # Step 1 df_in_SOPAdjLCM 과 df_in_DIMItem 기준 연결 (key = To Item & Item )
        # Step 1 - 1 df_in_SOPAdjLCM 필요한 컬럼 선택
        # Step 1 - 2 merge 를 위해 컬럼 명 변경
        # Step 1 - 3 df_in_DIMItem 과 머지
        # Step 1 - 4 LCM_PO_Send_POP_Qty 값을 LCM_PO_Send_SOP_Qty 로 값 복사
        df_in_SOPAdjLCM_temp = df_in_SOPAdjLCM[df_in_SOPAdjLCM[To_Item_COLUMN] != '-'].rename(columns={
            Location_COLUMN: Sub_Location_COLUMN, To_Item_COLUMN: Item_COLUMN,
            Sub_Location_COLUMN: Location_COLUMN, To_Trans_Mode_COLUMN: Trans_Mode_COLUMN,
            Item_Component_COLUMN: To_Item_COLUMN, SOP_Adjust_LCM_W_SOP_Adj_Qty: LCM_PO_Send_POP_Qty,
            Week1_COLUMN: LCM_PO_Send_MFG_Week}).merge(
            df_in_DIMItem, on=Item_COLUMN, how='left').rename(columns={
            Sub_Location_COLUMN: Location_COLUMN, Location_COLUMN: Sub_Location_COLUMN}).drop(
            columns=Item_Material_COLUMNS)

        # LCM_PO_Send_POP_Qty 값을 합치기
        df_in_SOPAdjLCM_temp = df_in_SOPAdjLCM_temp.groupby([
            Version_Name_COLUMN, Location_COLUMN, Item_COLUMN, To_Item_COLUMN,
            Sub_Location_COLUMN, LCM_PO_Send_MFG_Week, Trans_Mode_COLUMN,
            Item_Class_Category_COLUMN, Item_Product_COLUMN, Item_Product_Group_COLUMN])[
            LCM_PO_Send_POP_Qty].sum().reset_index()

        # LCM_PO_Send_SOP_Qty 값 설정 (LCM_PO_Send_POP_Qty 복사하기
        df_in_SOPAdjLCM_temp[LCM_PO_Send_SOP_Qty] = df_in_SOPAdjLCM_temp[LCM_PO_Send_POP_Qty].copy()

        # Step 2 df_in_SOPAdjLCM_temp & df_in_POProposalMgmt 데이터 merge
        # Step 2-1 df_in_SOPAdjLCM_temp 의 정제 (Item_Product_COLUMN 정체 ----> 필요 시 주석 처리 필요)
        # Step 2-2 df_in_POProposalMgmt 컬럼명 변경 후 df_in_SOPAdjLCM_temp 와 merge
        df_in_SOPAdjLCM_temp[Item_Product_COLUMN] = df_in_SOPAdjLCM_temp[Item_Product_COLUMN].str.split('-').str[1]
        df_in_SOPAdjLCM_temp = df_in_SOPAdjLCM_temp.merge(
            df_in_POProposalMgmt.rename(columns={
                Location_COLUMN: Sub_Location_COLUMN, Sub_Location_COLUMN: Location_COLUMN,
                Product_Group_COLUMN: Item_Product_COLUMN}),
            on=[Version_Name_COLUMN, Location_COLUMN, Sub_Location_COLUMN, Trans_Mode_COLUMN,
                Item_Class_Category_COLUMN, Item_Product_COLUMN], how='left')

        # Step 2-3 주차 데이터 프레임 만들기
        df_currentWeek = df_in_MPCurrWeek[[Time_Week_COLUMN]].drop_duplicates().reset_index(drop=True)
        df_currentWeek[Sequence] = df_currentWeek.index + 1  # 현재주차부터 Sequence 설정
        #  map 설정을 위해 데이터 타입 변경
        df_in_SOPAdjLCM_temp[LCM_PO_Send_MFG_Week] = df_in_SOPAdjLCM_temp[LCM_PO_Send_MFG_Week].astype(str)
        df_currentWeek[Time_Week_COLUMN] = df_currentWeek[Time_Week_COLUMN].astype(str)
        # 현 주차를 기준으로 LCM_PO_Send_MFG_Week 주차 기준 찾기 위한 Sequence 설정
        df_in_SOPAdjLCM_temp[Sequence] = df_in_SOPAdjLCM_temp[LCM_PO_Send_MFG_Week].map(
            df_currentWeek.set_index(Time_Week_COLUMN)[Sequence])
        # Sequence 가 없는 데이터 프레임 필터 즉 CurrentWeek 보다 과거 데이터 삭제
        df_in_SOPAdjLCM_temp = df_in_SOPAdjLCM_temp.loc[df_in_SOPAdjLCM_temp[Sequence].notna()]
        # 필털를 위한 데이터 타입 변경
        df_in_SOPAdjLCM_temp[Purchasing_Proposal_Master_POP_Week] = df_in_SOPAdjLCM_temp[
            Purchasing_Proposal_Master_POP_Week].fillna(0).astype(int).astype(str)
        df_in_SOPAdjLCM_temp[Sequence] = df_in_SOPAdjLCM_temp[Sequence].astype(int).astype(str)
        # 필터를 위한 mask 설정  및 필터
        mask = df_in_SOPAdjLCM_temp[Purchasing_Proposal_Master_POP_Week].eq(df_in_SOPAdjLCM_temp[Sequence])
        df_in_SOPAdjLCM_temp = df_in_SOPAdjLCM_temp.loc[mask]

        # LCM_PO_Send_ETA_Week 값 가져 오기
        df_currentWeek[Sequence] = df_currentWeek[Sequence].astype(str)
        df_in_SOPAdjLCM_temp[LCM_PO_Send_ETA_Week] = df_in_SOPAdjLCM_temp[Sequence].map(
            df_currentWeek.set_index(Sequence)[Time_Week_COLUMN])

        # Step 3 df_in_Adhoc1POPFlag 정보 가지고 오기
        # df_in_Adhoc1POPFlag max 값 구하기 Version_Name_COLUMN, Sub_Location_COLUMN 기준으로 Max 구하기
        df_in_Adhoc1POPFlag_temp = df_in_Adhoc1POPFlag.groupby([
            Version_Name_COLUMN, Location_COLUMN], as_index=False)[
            [PO_Proposal_Flag_PurORG, PO_Proposal_Flag_CY_Flag, PO_Proposal_Flag_DE_Flag,
             PO_Proposal_Flag_Description, PO_Proposal_Flag_Status]].max()
        df_in_SOPAdjLCM_temp = df_in_SOPAdjLCM_temp.merge(
            df_in_Adhoc1POPFlag_temp.rename(
                columns={Location_COLUMN: Sub_Location_COLUMN}),
            on=[Version_Name_COLUMN, Sub_Location_COLUMN], how='left').rename(
            columns={
                PO_Proposal_Flag_PurORG: LCM_PO_Send_Pur_Org,
                PO_Proposal_Flag_CY_Flag: LCM_PO_Send_CY_Flag,
                PO_Proposal_Flag_DE_Flag: LCM_PO_Send_DE_Flag})

        # Step 4 df_in_Adhoc2Purch_grp 기준 정보 가져 오기 (Versio, Item, Location 기준)
        df_in_SOPAdjLCM_temp = df_in_SOPAdjLCM_temp.merge(
            df_in_Adhoc2Purch_grp.rename(
                columns={Item_Material_COLUMNS: Item_COLUMN}),
            on=[Version_Name_COLUMN, Item_COLUMN, Location_COLUMN],
            how='left').rename(columns={
            Item_Material_Spec_Plant_Purchase_Group: LCM_PO_Send_Pur_Grp,
            Item_Material_Spec_Plant_Storage_Location: LCM_PO_Send_SLoc})

        df_in_SOPAdjLCM_temp[LCM_PO_Send_Plant] = df_in_SOPAdjLCM_temp[Location_COLUMN].copy()

        # Step 5 df_in_Adhoc3Purch_SLOC 기준으로 정보 가지고 오기
        # df_in_Adhoc3Purch_SLOC 정보 변경
        df_in_Adhoc3Purch_SLOC_temp = df_in_Adhoc3Purch_SLOC.rename(
            columns={PO_Proposal_SLoc_PurORG: LCM_PO_Send_Pur_Grp}).drop_duplicates().astype(str)

        # Step 5-2 df_in_SOPAdjLCM_temp 기준으로 merge
        df_in_SOPAdjLCM_temp = df_in_SOPAdjLCM_temp.merge(
            df_in_Adhoc3Purch_SLOC_temp, on=[Version_Name_COLUMN, Location_COLUMN, LCM_PO_Send_Pur_Grp], how='left')

        # # Step 5-3  LCM_PO_Send_SLoc 값 설정
        df_in_SOPAdjLCM_temp[LCM_PO_Send_SLoc] = np.where(
            df_in_SOPAdjLCM_temp[LCM_PO_Send_SLoc].isnull(),
            df_in_SOPAdjLCM_temp[PO_Proposal_SLoc_StorageLocation],
            df_in_SOPAdjLCM_temp[LCM_PO_Send_SLoc])

        # Step 5-4 불필요한 컬럼 삭제
        df_in_SOPAdjLCM_temp = df_in_SOPAdjLCM_temp.drop(columns=[PO_Proposal_SLoc_StorageLocation], axis=1)

        print_df(df_in_SOPAdjLCM_temp , 'Step 5 단계 확인', False)

        step('=====> STEP 3 End')
        ################################################################################################################
        # Step 4. Actual 설정 및 정리
        ################################################################################################################
        step('=====> STEP 4 Start : input data machining')

        # Step 6 df_in_LCMPOPSend 내에서 6개월 인 데이터를 가지고 LCM PO Send_POP ID 정보 만들기 LCM_PO_Send_Org_Vendor -> LCM_PO_Send_Pur_Org 만들기
        # Step 6-1 CurrentWeek 현 주차의 날짜를 가지고 6개월 날짜 설정하기
        # Step 6-1-1 데이터 타입 변경
        df_in_CurrentWeek = df_in_CurrentWeek.astype({Time_Day_COLUMN: 'str'}, copy=True)
        df_in_CurrentWeek[Time_Day_COLUMN] = pd.to_datetime(df_in_CurrentWeek[Time_Day_COLUMN], format='%Y-%m-%d')
        # Step 6-1-2 6개월 이후 날짜 찾기
        df_in_CurrentWeek['Last6M_Day'] = (
            df_in_CurrentWeek[Time_Day_COLUMN].apply(lambda x: x - relativedelta(months=6)))
        # Step 6-1-3 df_in_lastMonth의 데이터 타입 변경 및 통일
        df_in_lastMonth[Time_Day_COLUMN] = pd.to_datetime(df_in_lastMonth[Time_Day_COLUMN], format='%Y-%m-%d')
        # Step 6-1-4 6개월 후 날짜를 시리즈로 만들기
        Last6M_Day_S = df_in_CurrentWeek['Last6M_Day'].dropna()
        # Step 6-1-5 df_in_lastMonth 에서 해당 주차를 찾기
        df_in_lastMonth = df_in_lastMonth[df_in_lastMonth[Time_Day_COLUMN].isin(Last6M_Day_S)].copy()
        # Step 6-1-6 df_in_lastMonth 에서 주차를 시리즈로 만들기
        Last6M_Week_S = df_in_lastMonth[Time_Week_COLUMN].dropna()
        Last6M_Week_S = int(Last6M_Week_S.iloc[0])
        # Step 6-2 df_in_LCMPOPSend 에서 필터링 최근 6개월 내 데이터만 데이터 프레임 만들기
        df_in_LCMPOPSend[LCM_PO_Send_ETA_Week] = pd.to_numeric(
            df_in_LCMPOPSend[LCM_PO_Send_ETA_Week], errors='coerce').fillna(0).astype(int)
        df_in_LCMPOPSend_temp = df_in_LCMPOPSend.loc[df_in_LCMPOPSend[
            LCM_PO_Send_ETA_Week].astype(int).ge(Last6M_Week_S)].copy()

        # Step 6-3 현재 주차를 변수로 설정
        current_week_s = df_in_CurrentWeek[Time_Week_COLUMN].dropna().drop_duplicates().iloc[0]
        current_week_s = str(current_week_s)
        # Step 6-4 df_in_LCMPOPSend_temp 의 컬럼명 변경
        df_in_LCMPOPSend_temp = df_in_LCMPOPSend_temp.rename(
            columns={Sub_Location_COLUMN: Location_COLUMN,
                     Location_COLUMN: Sub_Location_COLUMN})

        # Step 6-4-1 가장 최근 데이터 찾기
        df_in_LCMPOPSend_temp = df_in_LCMPOPSend_temp.loc[
            df_in_LCMPOPSend_temp[LCM_PO_Send_Org_Vendor].notna()].copy()
        df_in_LCMPOPSend_temp[Time_Week_COLUMN] = pd.to_numeric(
            df_in_LCMPOPSend_temp[Time_Week_COLUMN], errors='coerce').fillna(0).astype(int)
        df_in_LCMPOPSend_temp['max_week'] = df_in_LCMPOPSend_temp.groupby(
            [Version_Name_COLUMN, Sub_Location_COLUMN, Location_COLUMN, Item_COLUMN,
             To_Item_COLUMN, Trans_Mode_COLUMN])[Time_Week_COLUMN].transform('max')
        df_in_LCMPOPSend_temp = df_in_LCMPOPSend_temp[
            df_in_LCMPOPSend_temp[Time_Week_COLUMN].eq(df_in_LCMPOPSend_temp['max_week'])]
        # Step 6-5 merge 전 reset_index
        df_in_LCMPOPSend_temp = df_in_LCMPOPSend_temp.reset_index(drop=True)

        # Step 6-6 LCM_PO_Send_Pur_Org 정보 찾기
        df_in_SOPAdjLCM_temp = df_in_SOPAdjLCM_temp.merge(
            df_in_LCMPOPSend_temp[
                [Version_Name_COLUMN, Location_COLUMN, Sub_Location_COLUMN,
                 Item_COLUMN, To_Item_COLUMN, Trans_Mode_COLUMN, LCM_PO_Send_Org_Vendor]],
            on=[Version_Name_COLUMN, Location_COLUMN, Sub_Location_COLUMN,
                Item_COLUMN, To_Item_COLUMN, Trans_Mode_COLUMN],
            how='left').rename(columns={
            LCM_PO_Send_Org_Vendor: LCM_PO_Send_Pur_Org}).drop(columns=Dummy)

        print_df(df_in_SOPAdjLCM_temp, 'df_in_SOPAdjLCM_temp  확인', False)

        step('=====> STEP 4 End')
        ################################################################################################################
        # Step 5. Actual 설정 및 정리
        ################################################################################################################
        step('=====> STEP 5 Start : input data machining')

        # Step 7 df_in_POProposalNCOTERMS merge를 통해 LCM PO Send_Incoterms1 정보 더하기
        # Step 7-1 merge를 위한 Column 명 변경
        df_in_POProposalNCOTERMS_temp = df_in_POProposalNCOTERMS.rename(columns=
                                                                        {Sub_Location_COLUMN: Location_COLUMN,
                                                                         Location_COLUMN: Sub_Location_COLUMN,
                                                                         Product_Group_COLUMN: Item_Product_COLUMN})

        df_in_SOPAdjLCM_temp = df_in_SOPAdjLCM_temp.merge(
            df_in_POProposalNCOTERMS_temp,
            on=[Version_Name_COLUMN, Location_COLUMN, Sub_Location_COLUMN, Item_Product_COLUMN, Vendor_COLUMN],
            how='left').rename(
            columns={Purchasing_Proposal_Vendor_INCO1: LCM_PO_Send_Incoterms1})
        # Step 7-2 LCM_PO_Send_Org_Vendor 값 설정
        df_in_SOPAdjLCM_temp[LCM_PO_Send_Org_Vendor] = np.nan

        # Step 8-5-1 데이터 타입 변경
        df_in_LCMPOPSend_temp[LCM_PO_Send_POP_ID] = df_in_LCMPOPSend_temp[
            LCM_PO_Send_POP_ID].fillna(0).astype(int)
        df_in_LCMPOPSend_temp[LCM_PO_Send_POP_ID] = pd.to_numeric(
            df_in_LCMPOPSend_temp[LCM_PO_Send_POP_ID], errors='coerce')

        # Step 8-5 max 값 설정을 위한 key가 되는 컬럼 설정
        groupby_cols = [
            Version_Name_COLUMN, Sub_Location_COLUMN, To_Item_COLUMN, Item_COLUMN,
            Location_COLUMN, Trans_Mode_COLUMN]
        # Step 8-5-1 데이터 타입 변경
        df_in_LCMPOPSend_temp[LCM_PO_Send_POP_ID] = df_in_LCMPOPSend_temp[LCM_PO_Send_POP_ID].fillna(0).astype(int)
        df_in_LCMPOPSend_temp[LCM_PO_Send_POP_ID] = pd.to_numeric(
            df_in_LCMPOPSend_temp[LCM_PO_Send_POP_ID], errors='coerce')
        # Max LCM_PO_Send_PO_No 찾기
        df_in_LCMPOPSend_temp['LCM_PO_Send_PO_No_max'] = df_in_LCMPOPSend_temp.groupby(groupby_cols)[
            LCM_PO_Send_POP_ID].transform('max')
        # LCM_PO_Send_PO_No 와 LCM_PO_Send_PO_No_max 가 같은 것 필터링
        df_in_LCMPOPSend_temp = df_in_LCMPOPSend_temp[
            df_in_LCMPOPSend_temp[LCM_PO_Send_POP_ID].eq(df_in_LCMPOPSend_temp['LCM_PO_Send_PO_No_max'])]
        # PO No가 없는 것 중복을 제거하기 위한 중복제거
        df_in_LCMPOPSend_temp = df_in_LCMPOPSend_temp.drop_duplicates(subset=groupby_cols).reset_index(drop=True)
        # Step 8 번 한번에 처리
        last_POPID_MAX_S = (
            pd.to_numeric(df_in_LCMPOPSend_temp[LCM_PO_Send_POP_ID], errors='coerce')
            .fillna(0)
            .astype(int)
            .astype(str))

        last_POPID_MAX = pd.to_numeric(last_POPID_MAX_S.str[-8:], errors='coerce')
        last_POPID_MAX = last_POPID_MAX.max()

        # Step 8-5 df_in_SOPAdjLCM_temp 와 df_in_LCMPOPSend_temp merge
        df_in_SOPAdjLCM_temp = df_in_SOPAdjLCM_temp.drop(
            columns=[Dummy, LCM_PO_Send_Org_Vendor]).merge(
            df_in_LCMPOPSend_temp.drop(
                columns=[
                    Time_Week_COLUMN, Sequence_COLUMN,
                    LCM_PO_Send_ETA_Week, LCM_PO_Send_POP_ID, Dummy]),
            on=[Version_Name_COLUMN, Location_COLUMN, Item_COLUMN,
                To_Item_COLUMN, Sub_Location_COLUMN, Trans_Mode_COLUMN],
            how='left')

        # current_week_s 년도 제거
        current_week_s = current_week_s[2:]
        # start 번호 설정
        start_seq = 1 if pd.isna(last_POPID_MAX) else int(last_POPID_MAX) + 1
        # LCM_PO_Send_POP_ID 설정
        df_in_SOPAdjLCM_temp[LCM_PO_Send_POP_ID] = (
                current_week_s
                + pd.Series(
            np.arange(start_seq, start_seq + len(df_in_SOPAdjLCM_temp)),
            index=df_in_SOPAdjLCM_temp.index).astype(str).str.zfill(8))

        print_df(df_in_SOPAdjLCM_temp, 'df_in_SOPAdjLCM_temp step 8까지', True)

        # Step 9  ds_in_inforecord Left Out Join 하여,  Currency / Price 값을 가져온다
        # Step 9-1 df_in_MTRLINFORECORD 필요한 컬럼 설정
        df_in_MTRLINFORECORD_temp = df_in_MTRLINFORECORD[
            [Version_Name_COLUMN, Location_COLUMN, Item_COLUMN,
             Vendor_COLUMN, Mtrl_Info_Record_Currency, Mtrl_Info_Record_Price]]
        # Step 9-2 df_in_SOPAdjLCM_temp 와 df_in_MTRLINFORECORD_temp merge
        df_in_SOPAdjLCM_temp = df_in_SOPAdjLCM_temp.merge(
            df_in_MTRLINFORECORD_temp,
            on=[Version_Name_COLUMN, Location_COLUMN, Item_COLUMN, Vendor_COLUMN],
            how='left')

        # Step 10 df_in_LCMBODW & df_in_DOBList 에서 Shipment LT 와 BOD LT 정보 설정하기
        # df_in_LCMBODW 와 df_in_DOBList merge
        df_in_LCMBODW_temp = df_in_LCMBODW.drop(
            columns=Dummy).merge(
            df_in_DOBList.drop(
                columns=Dummy),
            on=[Version_Name_COLUMN, Location_COLUMN, Item_COLUMN,
                Sub_Location_COLUMN, Trans_Mode_COLUMN],
            how='left')

        df_in_LCMBODW_temp[Time_Week_COLUMN] = df_in_LCMBODW_temp[Time_Week_COLUMN].astype(str)

        # Step 10-2 df_in_SOPAdjLCM_temp 와 df_in_LCMBODW_temp merge
        df_in_SOPAdjLCM_temp = df_in_SOPAdjLCM_temp.merge(
            df_in_LCMBODW_temp.rename(
                columns={Time_Week_COLUMN: LCM_PO_Send_MFG_Week,
                         Location_COLUMN: Sub_Location_COLUMN,
                         Sub_Location_COLUMN: Location_COLUMN}),
            on=[Version_Name_COLUMN, Location_COLUMN, Item_COLUMN,
                Sub_Location_COLUMN, Trans_Mode_COLUMN, LCM_PO_Send_MFG_Week],
            how='left')

        # df_in_MPCurrWeek 의 Time_Week_COLUMN 타입 변경
        df_in_MPCurrWeek[Time_Week_COLUMN] = df_in_MPCurrWeek[Time_Week_COLUMN].astype(str)
        df_in_SOPAdjLCM_temp['LCM_PO_Send_MFG_Day'] = df_in_SOPAdjLCM_temp[LCM_PO_Send_MFG_Week].map(
            df_in_MPCurrWeek.set_index(Time_Week_COLUMN)[Time_Day_COLUMN])

        Shipment_LT_S = df_in_SOPAdjLCM_temp[BOD_Item_W_Shipment_LT].fillna(df_in_SOPAdjLCM_temp[BOD_Item_Shipment_LT])
        BOD_LT_S = df_in_SOPAdjLCM_temp[BOD_Item_W_BOD_LT].fillna(df_in_SOPAdjLCM_temp[BOD_Item_BOD_LT])

        # Shipmnet LT 주차 계산을 위한 날짜 계산
        df_in_SOPAdjLCM_temp['LCM_PO_Send_ETD_Day'] = pd.to_datetime(
            df_in_SOPAdjLCM_temp['LCM_PO_Send_MFG_Day']) + pd.to_timedelta(
            Shipment_LT_S, unit='D')
        # 매주 월요일로 날짜 수정
        df_in_SOPAdjLCM_temp['LCM_PO_Send_ETD_Day'] = (df_in_SOPAdjLCM_temp['LCM_PO_Send_ETD_Day']
                                                       - pd.to_timedelta(
                    df_in_SOPAdjLCM_temp['LCM_PO_Send_ETD_Day'].dt.weekday, unit='D'))
        # BOD LT 주차 계산을 위한 날짜 계산
        df_in_SOPAdjLCM_temp['LCM_PO_Send_ETA_Day'] = pd.to_datetime(
            df_in_SOPAdjLCM_temp['LCM_PO_Send_MFG_Day']) + pd.to_timedelta(BOD_LT_S, unit='D')
        # 매주 월요일로 날짜 수정
        df_in_SOPAdjLCM_temp['LCM_PO_Send_ETA_Day'] = df_in_SOPAdjLCM_temp['LCM_PO_Send_ETA_Day'] - pd.to_timedelta(
            df_in_SOPAdjLCM_temp['LCM_PO_Send_ETA_Day'].dt.weekday, unit='D')
        # 주차를 가지고 오기 위한 Time_Day_COLUMN 컬럼 데이터 타입 변경
        df_in_MPCurrWeek[Time_Day_COLUMN] = pd.to_datetime(
            df_in_MPCurrWeek[Time_Day_COLUMN])
        df_in_SOPAdjLCM_temp[LCM_PO_Send_ETD_Week] = df_in_SOPAdjLCM_temp['LCM_PO_Send_ETD_Day'].map(
            df_in_MPCurrWeek.set_index(Time_Day_COLUMN)[Time_Week_COLUMN])
        df_in_SOPAdjLCM_temp[LCM_PO_Send_ETA_Week] = df_in_SOPAdjLCM_temp['LCM_PO_Send_ETA_Day'].map(
            df_in_MPCurrWeek.set_index(Time_Day_COLUMN)[Time_Week_COLUMN])
        # 컬럼명 변경
        df_in_SOPAdjLCM_temp = df_in_SOPAdjLCM_temp.rename(
            columns={
                Mtrl_Info_Record_Price: LCM_PO_Send_Price,
                Mtrl_Info_Record_Currency: LCM_PO_Send_Currency,
                BOD_Item_Multi_Lot_Qty: LCM_PO_Send_Lot_Size,
                Purchasing_Proposal_Master_POPSTL: LCM_PO_Send_POPSTL,
                Item_Class_Category_COLUMN: LCM_PO_Send_Class_Category,
                Vendor_COLUMN: LCM_PO_Send_Vendor,
                Location_COLUMN : Sub_Location_COLUMN,
                Sub_Location_COLUMN : Location_COLUMN
            }
        )
        current_week_s = df_in_CurrentWeek[Time_Week_COLUMN].dropna().drop_duplicates().iloc[0]
        current_week_s = str(current_week_s)

        # 상수 값 설정
        df_in_SOPAdjLCM_temp[LCM_PO_Send_DOMEXP] = 'DOM'
        df_in_SOPAdjLCM_temp[LCM_PO_Send_Status] = 'INI'
        df_in_SOPAdjLCM_temp[LCM_PO_Send_POPSTL] = df_in_SOPAdjLCM_temp[LCM_PO_Send_POPSTL].fillna('Y')
        df_in_SOPAdjLCM_temp[Time_Week_COLUMN] = current_week_s
        # df_in_SOPAdjLCM_temp[LCM_PO_Send_MFG_Week] = current_week_s
        df_in_SOPAdjLCM_temp[Sequence_COLUMN] = df_in_SOPAdjLCM_temp.groupby(Time_Week_COLUMN).cumcount() + 1
        df_in_SOPAdjLCM_temp[LCM_PO_Send_POP_ID] = df_in_SOPAdjLCM_temp[LCM_PO_Send_POP_ID].astype(str)
        # df_in_SOPAdjLCM_temp[LCM_PO_Send_Org_Vendor] = df_in_SOPAdjLCM_temp[LCM_PO_Send_Pur_Org].copy()
        # 불필요한 컬럼 삭제
        df_in_SOPAdjLCM_temp = df_in_SOPAdjLCM_temp.loc[:,
                               ~df_in_SOPAdjLCM_temp.columns.str.endswith(('_Day', 'LT', '_max'))]
        df_in_SOPAdjLCM_temp = df_in_SOPAdjLCM_temp.loc[:,
                               ~df_in_SOPAdjLCM_temp.columns.str.startswith(('Purchasing', 'PO Proposal', 'Item Material'))]

        out_put_cols = [
            Version_Name_COLUMN, Location_COLUMN, To_Item_COLUMN, Item_COLUMN, Time_Week_COLUMN, Sequence_COLUMN,
            Trans_Mode_COLUMN, Sub_Location_COLUMN, LCM_PO_Send_MFG_Week, LCM_PO_Send_CY_Flag,
            LCM_PO_Send_Class_Category, LCM_PO_Send_Currency,LCM_PO_Send_DE_Flag, LCM_PO_Send_DOMEXP,
            LCM_PO_Send_ETA_Week, LCM_PO_Send_ETD_Week, LCM_PO_Send_Incoterms1,LCM_PO_Send_Incoterms2,
            LCM_PO_Send_Org_Vendor, LCM_PO_Send_POP_ID, LCM_PO_Send_POP_Qty, LCM_PO_Send_Plant,LCM_PO_Send_Price,
            LCM_PO_Send_Pur_Grp, LCM_PO_Send_Pur_Org, LCM_PO_Send_SLoc, LCM_PO_Send_SOP_Qty,
            LCM_PO_Send_Status, LCM_PO_Send_Vendor, LCM_PO_Send_POPSTL]

        df_out_LCMPOSend = df_in_SOPAdjLCM_temp[out_put_cols]

        print_df(df_out_LCMPOSend, 'df_out_LCMPOSend step 11까지', True)
        step('=====> STEP5  End')

        ################################################################################################################
        # STEP 6 :  input data machining
        ################################################################################################################
        step('=====> STEP 6 Start : input data machining')

        if is_local:
            note(f'=====> Final output table create')
            print_df(df_out_LCMPOSend, 'df_out_LCMPOSend', True)

        print_df(df_out_LCMPOSend, 'df_out_LCMPOSend', True)
        row_count, col_count = df_out_LCMPOSend.shape
        note(f'=====> Final df_out_LCMPOSend rows : {row_count} , Columns : {col_count}')

        step('=====> STEP 6 End')

    # except CustomException as e:
    #     step(f'=====> CustomException : {e}')
    #     df_out_LCMPOSend = pd.DataFrame([], columns=[])

    except Exception as ex:
        step(f'=====> Exception : {traceback.format_exc()}')
        logger.Error()
        vdCommon.gfn_pyLog_error(traceback.format_exc())
        df_out_LCMPOSend = pd.DataFrame([], columns=[])


    finally:
        # 현재 메모리 사용량과 피크 메모리 사용량 체크 / 실행 시간 계산 (초 단위 -> 분 단위로 변환)
        current, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()

        step(
            f'=====> current: {format_size(current)}, peak: {format_size(peak)}, execution time: {run_time_minutes(start_time)}')
        step(f'===================== plugin Execution End ({get_formatted_time(time.time())}) =====================')

        df_out_log, df_out_logDetail = vd_log_end()
        logger.Finish()
        logger.Step(p_step_desc=f'plugin Execution End')
        logger.Step(p_step_desc=f'plugin Execution End')
        logger.Step(p_step_desc=f'plugin Execution End')
        logger.Step(p_step_desc=f'plugin Execution End')
        logger.Step(p_step_desc=f'plugin Execution End')
        logger.Step(p_step_desc=f'plugin Execution End')
        logger.Step(p_step_desc=f'plugin Execution End')
        logger.Step(p_step_desc=f'plugin Execution End')
        logger.Step(p_step_desc=f'plugin Execution End')
        logger.Step(p_step_desc=f'plugin Execution End')

