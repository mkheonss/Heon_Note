"""
* 프로그램명 
    - PY_UI_SOPAdjustSETSub

* 내용
    - 

* 변경이력
    - 2025.10.13 / 양희영 / Create
    - 2026.03.27 / 양희영 / Update

* Flow Summary
    

* Execution 

* Script Parameter
    - 

* Input Tables
    - df_in_SOPW : Select ([Version].[Version Name] * [Location].[Location] * [Item].[Item] * [Time].[Week] * [To Location].[To Location] * [To Item].[To Item] * [To Time].[To Week] * 
                   [Sequence].[Sequence] * [Week1].[Week1] * [Item Material].[Item Material] * [Sub Location].[Sub Location] * [Item Component].[Item Component] * [BOM Info].[BOM Version] * 
                   [Week2].[Week2] * [To Trans Mode].[To Trans Mode] * [Trans Mode].[Trans Mode] ) on row, 
                   ({Measure.[SOP W_BOD Name], Measure.[Dummy]}) on column;

    - df_in_PLCMfg : Select ([Version].[Version Name] * [Location].[Location] * [Item].[Item] ) on row, ({Measure.[PLC Mfg_SRA Actual Date], Measure.[PLC Mfg_EOP Cur Date]}) on column;

    - df_in_FullBOM : Select ([Version].[Version Name] * [Location].[Location] * [Item].[Item] * [To Location].[To Location] * [To Item].[To Item] * [Item Material].[Item Material] * 
                      [BOM Info].[BOM Version] * [Status].[Status] * [BOM Type].[BOM Type] * [BOM Status].[BOM Status] ) on row, 
                      ({Measure.[Full BOM_Eff Startdate], Measure.[Full BOM_Eff Enddate], Measure.[Full BOM_BOM Date]}) on column;

    - df_in_LCMFrznPrdDtl : Select ([Version].[Version Name] * [Location].[Location] * [Item].[Item] * [Sub Location].[Sub Location] ) on row, 
                            ({Measure.[LCM Frozen Period Detail_Frz Startdate], Measure.[LCM Frozen Period Detail_Frz Enddate]}) on column;

    - df_in_TimeWeek : Select ([Time].[Day] * [Time].[Week]);

* Output Tables
    - df_out_SOPAdjustSETSub : Select ([Version].[Version Name].[CWV_MP] * [Location].[Location] * [Item].[Item] ) on row, 
                               ({Measure.[SOP Adjust SET Sub_BOM Eff End], Measure.[SOP Adjust SET Sub_BOM Eff Start], Measure.[SOP Adjust SET Sub_BOM Issue], Measure.[SOP Adjust SET Sub_BOM Status], 
                               Measure.[SOP Adjust SET Sub_EOP], Measure.[SOP Adjust SET Sub_Panel Block End], Measure.[SOP Adjust SET Sub_Panel Block Start], Measure.[SOP Adjust SET Sub_QtyItem], 
                               Measure.[SOP Adjust SET Sub_SRA]}) on column;
    
* 테스트 스크립트
    EXEC plugin instance [PY_UI_SOPAdjustSETSub] for measures {[SOP Adjust SET Sub_SRA]} using scope (&MPV) 
     using arguments {("IncludeNullRows", "False"), (ExecutionMode, "MediumWeight"), (MaxSliceTableCells, 200000000), (MaxConcurrency, 1 )};

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
import warnings

warnings.filterwarnings("ignore")

########################################################################################################################
# Local 개발 시에 필요한 공통 변수 선언
########################################################################################################################
# o9에 저장된 instanceName
str_instance = 'PY_UI_SOPAdjustSETSub'
is_local = common.gfn_get_isLocal()

# 공통 Liblary 버전
COMMON_SOURCE_VERSION = common.G_SourceVersion
VD_SOURCE_VERSION = vdCommon.G_VD_SourceVersion

# input variable 확인
paramOutVersion = "CWV_MP"
#paramOutVersion = (
#    "CWV_MP"
#    if is_local or not paramOutVersion or not paramOutVersion.strip()
#    else paramOutVersion
#)

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
    return pd.read_csv(f"{file_name}.csv", encoding="UTF-8", low_memory=False)


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
        setp(f"=====> 로그 처리 중 오류 발생: {str(e)}")
        return None, None


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
    # STEP 0 : DataFrame Column : 변수 처리
    ################################################################################################################
    step('=====>STEP 0-1 DataFrame Column : 변수 처리')

    # 컬럼 변수 선언
    col_VersionName = 'Version.[Version Name]'
    col_Location = 'Location.[Location]'
    col_SubLocation = 'Sub Location.[Sub Location]'
    col_Item = 'Item.[Item]'
    col_ToItem = 'To Item.[To Item]'
    col_TimeWeek = 'Time.[Week]'
    col_TimeDay = 'Time.[Day]'
    
    col_SRA_Date = 'PLC Mfg_SRA Actual Date'
    col_EOP_Date = 'PLC Mfg_EOP Cur Date'
    
    col_FullBOM_EffStartdate = 'Full BOM_Eff Startdate'
    col_FullBOM_EffEnddate = 'Full BOM_Eff Enddate'
    col_FullBOM_BOMDate = 'Full BOM_BOM Date'
    
    col_Frz_Startdate = 'LCM Frozen Period Detail_Frz Startdate'
    col_Frz_Enddate   = 'LCM Frozen Period Detail_Frz Enddate'
    #----------------------------------------------------------
    col_SETSub_SRA = 'SOP Adjust SET Sub_SRA'
    col_SETSub_EOP = 'SOP Adjust SET Sub_EOP'
    
    col_SETSub_BOMEffStart = 'SOP Adjust SET Sub_BOM Eff Start'
    col_SETSub_BOMEffEnd   = 'SOP Adjust SET Sub_BOM Eff End'
    col_SETSub_BOMIssue    = 'SOP Adjust SET Sub_BOM Issue'
    
    col_SETSub_PanelBlockStart = 'SOP Adjust SET Sub_Panel Block Start'
    col_SETSub_PanelBlockEnd = 'SOP Adjust SET Sub_Panel Block End'
    
    col_SETSub_QtyItem = 'SOP Adjust SET Sub_QtyItem'
    
    # 칼럼 List 설정
    cList_V_L_I = [col_VersionName, col_Location, col_Item]
    
    ################################################################################################################
    # STEP 0 : 전처리 : 모듈 내에서 사용될 input table load
    ################################################################################################################
    step('=====> STEP 0-2 : Input table load')
    
    # Value 변수 선언
    
    # 데이터 파일 읽기
    if is_local:
        df_in_SOPW = read_csv_file("df_in_SOPW")
        df_in_PLCMfg = read_csv_file("df_in_PLCMfg")
        df_in_FullBOM = read_csv_file("df_in_FullBOM")
        df_in_LCMFrznPrdDtl = read_csv_file("df_in_LCMFrznPrdDtl")
        df_in_TimeWeek = read_csv_file("df_in_TimeWeek")
    
    print_df(df_in_SOPW, 'df_in_SOPW', False)
    print_df(df_in_PLCMfg, 'df_in_PLCMfg', False)
    print_df(df_in_FullBOM, 'df_in_FullBOM', False)
    print_df(df_in_LCMFrznPrdDtl, 'df_in_LCMFrznPrdDtl', False)
    print_df(df_in_TimeWeek, 'df_in_TimeWeek', False)
    
    step('=====> STEP 0-3 : Input table load End')
    
    # DATA TYPE 설정
    def cnvt_mixed_date(x):
        try:
            if len(x) == 8:
                # note(f'=====check x1 len: {x} ========')
                return pd.to_datetime(x, format='%Y%m%d', errors='coerce')
            elif '-' in x:
                # note(f'=====check x2: {x} ========')
                return pd.to_datetime(x, format='%Y-%m-%d', errors='coerce')
            elif '.' in x:
                # note(f'=====check x3: {x} ========')
                return pd.to_datetime(x, format='%Y.%m.%d', errors='coerce')
            else:
                # note(f'=====check x4: {x} ========')
                return pd.to_datetime(x, format='%Y%m%d', errors='coerce')
        except:
            return pd.NaT
    # --------------------------------------------------------------------------------
    
    df_SOPW = df_in_SOPW[[col_VersionName,col_Location,col_Item]].copy()
    df_SOPW.drop_duplicates(inplace=True)
    print_df(df_SOPW, 'df_SOPW', False)
    
    df_in_TimeWeek = df_in_TimeWeek[[col_TimeDay, col_TimeWeek]].copy()
    df_in_TimeWeek[col_TimeDay] = pd.to_datetime(df_in_TimeWeek[col_TimeDay], format='%Y-%m-%d')
    df_in_TimeWeek[col_TimeWeek] = df_in_TimeWeek[col_TimeWeek].astype('str')
    print_df(df_in_TimeWeek, 'df_in_TimeWeek -2', False)
    
    ################################################################################################################
    # STEP 1 : SOP Adjust SET Sub_SRA,  SOP Adjust SET Sub_EOP
    ################################################################################################################
    step('=====> STEP 1 : SRA - EOP create')
    df_SETSub_PLC = df_SOPW.merge(df_in_PLCMfg, on=cList_V_L_I, how='inner')
    del df_in_PLCMfg
    
    if df_SETSub_PLC[col_SRA_Date].dtype != 'datetime64[ns]':
        df_SETSub_PLC[col_SRA_Date] = pd.to_datetime(df_SETSub_PLC[col_SRA_Date], format='%m/%d/%Y %I:%M:%S %p')
    
    if df_SETSub_PLC[col_EOP_Date].dtype != 'datetime64[ns]':
        df_SETSub_PLC[col_EOP_Date] = pd.to_datetime(df_SETSub_PLC[col_EOP_Date], format='%m/%d/%Y %I:%M:%S %p')
    
    # PLC의 SRA WEEK
    df_SETSub_PLC = df_SETSub_PLC.merge(df_in_TimeWeek, left_on=[col_SRA_Date], right_on=[col_TimeDay], how='left')
    df_SETSub_PLC[col_SETSub_SRA] = df_SETSub_PLC[col_TimeWeek]
    df_SETSub_PLC.drop(columns=[col_SRA_Date, col_TimeDay, col_TimeWeek], inplace=True)
    
    # PLC의 EOP WEEK
    df_SETSub_PLC = df_SETSub_PLC.merge(df_in_TimeWeek, left_on=[col_EOP_Date], right_on=[col_TimeDay], how='left')
    del df_in_TimeWeek
    df_SETSub_PLC[col_SETSub_EOP] = df_SETSub_PLC[col_TimeWeek]
    df_SETSub_PLC.drop(columns=[col_EOP_Date, col_TimeDay, col_TimeWeek], inplace=True)
    
    print_df(df_SETSub_PLC, 'df_SETSub_PLC', False)
    
    ################################################################################################################
    # STEP 2 : SOP Adjust SET Sub_BOM Eff Start, SOP Adjust SET Sub_BOM Eff End, SOP Adjust SET Sub_BOM Issue
    ################################################################################################################
    step('=====> STEP 2 : BOM Eff Start - BOM Eff End - BOM Issue create')
    df_SETSub_BOM = df_SOPW.merge(df_in_FullBOM, on=cList_V_L_I, how='inner')
    del [df_SOPW, df_in_FullBOM]
    
    df_SETSub_BOM.drop(columns=['To Location.[To Location]','To Item.[To Item]','Item Material.[Item Material]',
                                'BOM Info.[BOM Version]','Status.[Status]','BOM Type.[BOM Type]',
                                'BOM Status.[BOM Status]'], inplace=True)
    
    df_SETSub_BOM.drop_duplicates(inplace=True)
    
    print_df(df_SETSub_BOM, 'df_SETSub_BOM DIST', False)
    
    # float --> str 변환때 붙는 .0 제거 -------------------------------------------------------------------
    if df_SETSub_BOM[col_FullBOM_EffStartdate].dtype == 'float64':
        df_SETSub_BOM[col_FullBOM_EffStartdate] = df_SETSub_BOM[col_FullBOM_EffStartdate].astype('str').str.replace('.0', '')
    
    if df_SETSub_BOM[col_FullBOM_EffStartdate].dtype != 'datetime64[ns]':
        df_SETSub_BOM[col_FullBOM_EffStartdate] = df_SETSub_BOM[col_FullBOM_EffStartdate].apply(cnvt_mixed_date)
    
    # float --> str 변환때 붙는 .0 제거 -------------------------------------------------------------------
    if df_SETSub_BOM[col_FullBOM_EffEnddate].dtype == 'float64':
        df_SETSub_BOM[col_FullBOM_EffEnddate] = df_SETSub_BOM[col_FullBOM_EffEnddate].astype('str').str.replace('.0', '')
    
    if df_SETSub_BOM[col_FullBOM_EffEnddate].dtype != 'datetime64[ns]':
        df_SETSub_BOM[col_FullBOM_EffEnddate] = df_SETSub_BOM[col_FullBOM_EffEnddate].apply(cnvt_mixed_date)
    
    # float --> str 변환때 붙는 .0 제거 -------------------------------------------------------------------
    if df_SETSub_BOM[col_FullBOM_BOMDate].dtype == 'float64':
        df_SETSub_BOM[col_FullBOM_BOMDate] = df_SETSub_BOM[col_FullBOM_BOMDate].astype('str').str.replace('.0', '')
    
    if df_SETSub_BOM[col_FullBOM_BOMDate].dtype != 'datetime64[ns]':
        df_SETSub_BOM[col_FullBOM_BOMDate] = df_SETSub_BOM[col_FullBOM_BOMDate].apply(cnvt_mixed_date)
        
    df_SETSub_BOM = df_SETSub_BOM.groupby(cList_V_L_I, as_index=False).agg(Startdate=(col_FullBOM_EffStartdate, 'min'),
                                                                           Enddate=(col_FullBOM_EffEnddate, 'max'),
                                                                           Issue=(col_FullBOM_BOMDate, 'max') 
                                                                          )
    
    df_SETSub_BOM.rename(columns={'Startdate':col_SETSub_BOMEffStart,
                                  'Enddate':col_SETSub_BOMEffEnd,
                                  'Issue':col_SETSub_BOMIssue}, inplace=True)
    
    df_SETSub_BOM[col_SETSub_BOMEffStart] = np.where(df_SETSub_BOM[col_SETSub_BOMEffStart].notna(),
                                                     df_SETSub_BOM[col_SETSub_BOMEffStart].dt.date.astype('str'),np.nan)
    
    df_SETSub_BOM[col_SETSub_BOMEffEnd] = np.where(df_SETSub_BOM[col_SETSub_BOMEffEnd].notna(),
                                                   df_SETSub_BOM[col_SETSub_BOMEffEnd].dt.date.astype('str'),np.nan)
    
    df_SETSub_BOM[col_SETSub_BOMIssue] = np.where(df_SETSub_BOM[col_SETSub_BOMIssue].notna(),
                                                  df_SETSub_BOM[col_SETSub_BOMIssue].dt.date.astype('str'),np.nan)
    
    print_df(df_SETSub_BOM, 'df_SETSub_BOM', False)
    
    ################################################################################################################
    # STEP 3 : SOP Adjust SET Sub_Panel Block Start, SOP Adjust SET Sub_Panel Block End
    ################################################################################################################
    step('=====> STEP 3 : Panel Block Start - Panel Block End create')
    # WEEK 가 float64 로 자동 변환되는 현상이 있어, Start, End 정보를 각각 null 제거후 min/max 값 구한 후 취합
    
    df_SOPW_LCM = df_in_SOPW[[col_VersionName,col_Location,col_Item, col_ToItem, col_SubLocation]].copy()
    df_SOPW_LCM.drop_duplicates(inplace=True)
    print_df(df_SOPW_LCM, 'df_SOPW_LCM', True)
    
    #  SOP Adjust SET Sub_Panel Block Start ---------------------------------------------------------
    df_LCMFrznPrdDtl_Start = df_in_LCMFrznPrdDtl[df_in_LCMFrznPrdDtl[col_Frz_Startdate].notna()].copy()
    #df_LCMFrznPrdDtl_Start.drop(columns=['Sub Location.[Sub Location]', col_Frz_Enddate],inplace=True)
    df_LCMFrznPrdDtl_Start.drop(columns=[col_Frz_Enddate], inplace=True)
    df_LCMFrznPrdDtl_Start.drop_duplicates(inplace=True)
    
    if df_LCMFrznPrdDtl_Start[col_Frz_Startdate].dtype != 'int64':
        df_LCMFrznPrdDtl_Start[col_Frz_Startdate] = df_LCMFrznPrdDtl_Start[col_Frz_Startdate].astype('int64')
        
    df_LCMFrznPrdDtl_Start.rename(columns={col_Frz_Startdate: col_SETSub_PanelBlockStart}, inplace=True)
    print_df(df_LCMFrznPrdDtl_Start, 'df_LCMFrznPrdDtl_Start', True)
    
    # Merge : df_SOPW_LCM & df_LCMFrznPrdDtl_Start
    
    cList_Left = [col_VersionName,col_SubLocation,col_ToItem,col_Location]
    cList_Right = [col_VersionName,col_Location,col_Item,col_SubLocation]
    #df_SETSub_PnlBlckStart = df_SOPW.merge(df_LCMFrznPrdDtl_Start, on=cList_V_L_I, how='inner')
    df_SETSub_PnlBlckStart = df_SOPW_LCM.merge(df_LCMFrznPrdDtl_Start, left_on=cList_Left, right_on=cList_Right,
                                               how='inner', suffixes=('', '_y'))
    
    print_df(df_SETSub_PnlBlckStart, 'df_SETSub_PnlBlckStart Merge ', False)
    del df_LCMFrznPrdDtl_Start
    
    df_SETSub_PnlBlckStart = df_SETSub_PnlBlckStart.groupby(cList_V_L_I,
                                                            as_index=False)[col_SETSub_PanelBlockStart].min() # MIN
    
    df_SETSub_PnlBlckStart[col_SETSub_PanelBlockStart] =df_SETSub_PnlBlckStart[col_SETSub_PanelBlockStart].astype('str')
    print_df(df_SETSub_PnlBlckStart, 'df_SETSub_PnlBlckStart', False)
    
    #  SOP Adjust SET Sub_Panel Block End ------------------------------------------------------------
    df_LCMFrznPrdDtl_End = df_in_LCMFrznPrdDtl[df_in_LCMFrznPrdDtl[col_Frz_Enddate].notna()].copy()
    del df_in_LCMFrznPrdDtl
    
    #df_LCMFrznPrdDtl_End.drop(columns=['Sub Location.[Sub Location]', col_Frz_Startdate],inplace=True)
    df_LCMFrznPrdDtl_End.drop(columns=[col_Frz_Startdate], inplace=True)
    df_LCMFrznPrdDtl_End.drop_duplicates(inplace=True)
    
    if df_LCMFrznPrdDtl_End[col_Frz_Enddate].dtype != 'int64':
        df_LCMFrznPrdDtl_End[col_Frz_Enddate] = df_LCMFrznPrdDtl_End[col_Frz_Enddate].astype('int64')
        
    df_LCMFrznPrdDtl_End.rename(columns={col_Frz_Enddate: col_SETSub_PanelBlockEnd}, inplace=True)
    print_df(df_LCMFrznPrdDtl_End, 'df_LCMFrznPrdDtl_End', True)
    
    # Merge : df_SOPW_LCM & df_LCMFrznPrdDtl_End
    cList_Left = [col_VersionName, col_SubLocation, col_ToItem, col_Location]
    cList_Right = [col_VersionName, col_Location, col_Item, col_SubLocation]
    #df_SETSub_PnlBlckEnd = df_SOPW.merge(df_LCMFrznPrdDtl_End, on=cList_V_L_I, how='inner')
    df_SETSub_PnlBlckEnd = df_SOPW_LCM.merge(df_LCMFrznPrdDtl_End, left_on=cList_Left, right_on=cList_Right, 
                                             how='inner', suffixes=('', '_y'))
    print_df(df_SETSub_PnlBlckEnd, 'df_SETSub_PnlBlckEnd Merge', False)
    del [df_SOPW_LCM, df_LCMFrznPrdDtl_End]
    df_SETSub_PnlBlckEnd = df_SETSub_PnlBlckEnd.groupby(cList_V_L_I, 
                                                        as_index=False)[col_SETSub_PanelBlockEnd].max() # MAX
    
    df_SETSub_PnlBlckEnd[col_SETSub_PanelBlockEnd] = df_SETSub_PnlBlckEnd[col_SETSub_PanelBlockEnd].astype('str')
    print_df(df_SETSub_PnlBlckEnd, 'df_SETSub_PnlBlckEnd', False)
    
    # 취합 : df_SETSub_PnlBlckStart, df_SETSub_PnlBlckEnd
    df_SETSub_PnlBlck = df_SETSub_PnlBlckStart.merge(df_SETSub_PnlBlckEnd, on=cList_V_L_I, how='outer')
    del [df_SETSub_PnlBlckStart, df_SETSub_PnlBlckEnd]
    print_df(df_SETSub_PnlBlck, 'df_SETSub_PnlBlck', False)
    
    ################################################################################################################
    # STEP 4 : output table create
    ################ ################################################################################################
    step('=====> STEP 4-1 : Final output table create')
    # 취합 : df_SETSub_PLC, df_SETSub_BOM, df_SETSub_PnlBlck
    df_SETSub = df_SETSub_PLC.merge(df_SETSub_BOM, on=cList_V_L_I, how='outer')
    df_SETSub = df_SETSub.merge(df_SETSub_PnlBlck, on=cList_V_L_I, how='outer')
    del [df_SETSub_PLC, df_SETSub_BOM, df_SETSub_PnlBlck]
    #print_df(df_SETSub, 'df_SETSub', True)
    
    df_out_SOPAdjustSETSub = df_SETSub.copy()
    del df_SETSub
    
    # 버전 처리
    # df_out_SOPAdjustSETSub[col_VersionVersionName] = paramOutVersion
    
    row_count, col_count = df_out_SOPAdjustSETSub.shape
    note(f'=====> Final df_out_SOPAdjustSETSub rows : {row_count}, column : {col_count}')
    print_df(df_out_SOPAdjustSETSub, 'df_out_SOPAdjustSETSub', False)
    
    if is_local:
        step('=====> Output csv create')
        save_csv_file(df_out_SOPAdjustSETSub, 'df_out_SOPAdjustSETSub')
    
    step('=====> STEP 4-2 : Final output table create End')
    step('==============================================')
    step('==============================================')
    step('==============================================')
    
except Exception as e:
    step(f'=====> Exception : {traceback.format_exc()}')
    logger.Error()
    vdCommon.gfn_pyLog_error(traceback.format_exc())
    
    df_out_SOPAdjustSETSub = pd.DataFrame([], columns=[])

finally:
    # 현재 메모리 사용량과 피크 메모리 사용량 체크 / 실행 시간 계산 (초 단위 -> 분 단위로 변환)
    current, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    
    step(f'=====> current: {format_size(current)}, peak: {format_size(peak)}, execution time: {run_time_minutes(start_time)}')
    step(f'===================== plugin Execution End ({get_formatted_time(time.time())}) =====================')
    
    df_out_log, df_out_logDetail = vd_log_end()
    logger.Finish()