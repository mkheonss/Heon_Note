"""
* 프로그램명 
    - PY_MG_FullBOMUpdateEffective

* 내용
    - UI에서 관리한 BOM까지 Merge된 Fullbom에 UI에서 관리된 SRA/EOP 감안하여 Effectiveness를 갱신

* 변경이력
    - 2024.10.07 / 양희영 / Create
    - 2025.06.27 / 양희영 / Update

* Flow Summary
    STEP1.   SRA/EOP 정보를 가지고 와서 FULL BOM Update

* Execution 
* Script Parameter
    - paramOutVersion : CWV_MP : 사용안함.
* Input Tables
    - df_in_FullBOM : Measure Group : Full BOM
                      Select ([Version].[Version Name] * [Item].[Item] * [Location].[Location] * [To Location].[To Location] * [To Item].[To Item] * [Item Material].[Item Material] * 
                      [BOM Info].[BOM Version] * [BOM Type].[BOM Type] * [BOM Status].[BOM Status] * [Status].[Status] ) on row, 
                      ({Measure.[Full BOM_BOM Level], Measure.[Full BOM_Base Qty], Measure.[Full BOM_EOP Date], Measure.[Full BOM_Eff Enddate], Measure.[Full BOM_Eff Startdate], 
                      Measure.[Full BOM_Issue Date], Measure.[Full BOM_SRA Date], Measure.[Full BOM_Safety Date] }) on column;
    - df_in_PLCMfg : Measure Group : PLC Mfg
                     Select ([Version].[Version Name] * [Item].[Item] * [Location].[Location] ) on row, ({Measure.[PLC Mfg_SRA Com Date], Measure.[PLC Mfg_EOP Com Date]}) 
                     on column.filter ((~Isnull(Measure.[PLC Mfg_SRA Com Date])&&Measure.[PLC Mfg_SRA Com Date]  >= Measure.[W Plan Start Date]) || (~isnull(Measure.[PLC Mfg_EOP Com Date])&&Measure.[PLC Mfg_EOP Com Date]  >= Measure.[W Plan Start Date]));
* Output Tables
    - df_out_FullBOM : Measure Group : Full BOM
                       Select ([Version].[Version Name] * [Location].[Location] * [Item].[Item] * [To Location].[To Location] * [To Item].[To Item] * [Item Material].[Item Material] * [BOM Info].[BOM Version] * 
                       [Status].[Status] * [BOM Type].[BOM Type] * [BOM Status].[BOM Status] ) on row, 
                       ({Measure.[Full BOM_Acil Date], Measure.[Full BOM_Avail Qty], Measure.[Full BOM_BOM Date], Measure.[Full BOM_BOM Date_DateTime], Measure.[Full BOM_BOM Level], Measure.[Full BOM_Base Qty], 
                       Measure.[Full BOM_Consume Qty], Measure.[Full BOM_Consume UOM], Measure.[Full BOM_Creation Time], Measure.[Full BOM_EOP Date], Measure.[Full BOM_Eff Enddate], Measure.[Full BOM_Eff Startdate], 
                       Measure.[Full BOM_Flag], Measure.[Full BOM_HQ Dev Purchaser], Measure.[Full BOM_HQ Purchaser], Measure.[Full BOM_Issue Date], Measure.[Full BOM_MRP Controller], Measure.[Full BOM_Part Eff Enddate], 
                       Measure.[Full BOM_Part Eff Startdate], Measure.[Full BOM_Prty], Measure.[Full BOM_Purchaser], Measure.[Full BOM_SOP SET Qty], Measure.[Full BOM_SOP SET Qty_Exist Flag], 
                       Measure.[Full BOM_SOP Version Qty], Measure.[Full BOM_SRA Date], Measure.[Full BOM_Safety Date], Measure.[Full BOM_Unit], Measure.[Full BOM_Update Time], Measure.[Full BOM_Valid]}) on column;
    
* 테스트 스크립트
    EXEC plugin instance [PY_MG_FullBOMUpdateEffective] for measures {[Full BOM_Base Qty]} using scope (&MPV) 
    using arguments {(ExecutionMode, "MediumWeight"), ("IncludeNullRows", "False"), (paramOutVersion , "CWV_MP"), (MaxSliceTableCells, 200000000), (MaxConcurrency, 1)};
      
"""


from NSCMCommon import NSCMCommon as common
from NSCMCommon import VDCommon as vdCommon
import os
import pandas as pd
import numpy as np
import datetime as dt
import traceback
import gc
import tracemalloc
from datetime import datetime

########################################################################################################################
# Local 개발 시에 필요한 공통 변수 선언
########################################################################################################################
# o9에 저장된 instanceName
str_instance = 'PY_MG_FullBOMUpdateEffective'
is_local = common.gfn_get_isLocal()
COMMON_SOURCE_VERSION = common.G_SourceVersion

########################################################################################################################
# log 설정 : PROGRAM file_name
########################################################################################################################
logger = common.G_Logger(p_py_name=str_instance)
common.gfn_set_local_logfile()
LOG_LEVEL = common.G_log_level


########################################################################################################################
# logic start
########################################################################################################################
def read_csv_file(file_name):
    return pd.read_csv(f"{file_name}.csv", encoding="UTF-8", low_memory=False)
    #return pd.read_csv(f"{file_name}.csv", encoding="UTF-8", low_memory=False, keep_default_na=False)

def save_csv_file(df, file_name):
    df.to_csv(f"{file_name}.csv", index=False)

#def print_df(df, df_name, p_log_level=LOG_LEVEL.debug(), p_format=1):
#    logger.PrintDF(p_df=df, p_df_name=df_name, p_log_level=p_log_level, p_format=p_format)


def note(string, p_log_level=LOG_LEVEL.debug()):
    logger.Note(p_note=f'{string}', p_log_level=p_log_level)

#def step(no, string):
#    logger.Step(p_step_no=no, p_step_desc=f'{string}')


try:
    ################################################################################################################
    # Batch 시작
    ################################################################################################################
    vdCommon.gfn_pyLog_start("CWV_MP", str_instance, logger, common.gfn_get_isLocal(),
                             (os.path.dirname(__file__) if common.gfn_get_isLocal() else ""))
    
    vdCommon.gfn_stepLog("plugin Execution Start ")
    vdCommon.gfn_stepLog(common.G_SourceVersion)
    vdCommon.gfn_stepLog(vdCommon.G_VD_SourceVersion)
    
    ################################################################################################################
    # DataFrame Column : 변수 처리
    ################################################################################################################
    vdCommon.gfn_stepLog('=====> STEP 0 : DataFrame Column : 변수 처리')
    
    # Value 변수 선언
    #paramOutVersion_VALUE = "CWV_MP"
    
    # 컬럼 변수 선언
    versionVersionName       = 'Version.[Version Name]'
    itemItem                 = 'Item.[Item]'
    locationLocation         = 'Location.[Location]'
    toLocationToLocation     = 'To Location.[To Location]'
    toItemToItem             = 'To Item.[To Item]'
    itemMaterialItemMaterial = 'Item Material.[Item Material]'
    bOMInfoBOMVersion        = 'BOM Info.[BOM Version]'
    bOMTypeBOMType           = 'BOM Type.[BOM Type]'
    bOMStatusBOMStatus       = 'BOM Status.[BOM Status]'
    statusStatus             = 'Status.[Status]'
    
    fullBOM_EffStartdate = 'Full BOM_Eff Startdate'
    fullBOM_EffEnddate   = 'Full BOM_Eff Enddate'
    fullBOM_SafetyDate   = 'Full BOM_Safety Date'
    
    pLCMfg_SRAComDate = 'PLC Mfg_SRA Com Date'
    pLCMfg_EOPComDate = 'PLC Mfg_EOP Com Date'
    
    gtst_EffStartdate = 'Gtst_Eff Startdate'
    gtst_EffEnddate   = 'Gtst_Eff Enddate'
    tmp_Date1         = 'Tmp_Date1'
    
    vdCommon.gfn_stepLog('=====> STEP 0-1 : DataFrame Column : 변수 처리')
    ################################################################################################################
    # 전처리 : 모듈 내에서 사용될 input table load
    ################################################################################################################
    vdCommon.gfn_stepLog('=====> STEP 1 : Input table load')
    
    # 데이터 파일 읽기
    if is_local:
        # 로컬일 경우 버전 처리
        #paramOutVersion    = paramOutVersion_VALUE        
        
        df_in_FullBOM      = read_csv_file("df_in_FullBOM")
        df_in_PLCMfg       = read_csv_file("df_in_PLCMfg")
    
    #if df_in_FullBOM.empty:
    #    raise Exception("=====> raise Exception: df_in_FullBOM is empty")
    
    #if df_in_PLCMfg.empty:
    #    raise Exception("=====> raise Exception: df_in_PLCMfg is empty")
            
    # 입력 변수 확인
    #if paramOutVersion is None or paramOutVersion.strip() == '':
    #    paramOutVersion = paramOutVersion_VALUE
    
    # input dataframe 확인용 로그
    #note(f'=====> paramOutVersion : {paramOutVersion}')
    
    vdCommon.gfn_saveDf(df_in_FullBOM, 'df_in_FullBOM',False) 
    vdCommon.gfn_saveDf(df_in_PLCMfg, 'df_in_PLCMfg',False)
    
    vdCommon.gfn_stepLog('=====> STEP 1-1 : Input table load End')
    
    ################################################################################################################
    # STEP 2 : df_FullBOM 구성 
    ################################################################################################################
    vdCommon.gfn_stepLog('=====> STEP 2 : FullBOM Data create')
    
    # DATA TYPE 설정
    '''
    # PANDAS 지원되는 일자 : 1697년 9월 21일 ~ 2262년 4월 11일
    def replace_date(date_string, rtn_type):
        max_date = datetime.strptime("2262-04-11", '%Y-%m-%d')
        
        date_string = str(date_string)
        
        if date_string != 'nan':
            try:
                date_object = datetime.strptime(date_string, '%m/%d/%Y %I:%M:%S %p')
            except Exception as e1:
                try:
                    date_object = datetime.strptime(date_string, '%Y-%m-%d')
                except Exception as e2:
                    date_object = datetime.strptime(date_string, '%Y-%m-%d %H:%M:%S')
            
            if date_object > max_date:
                return_date = max_date
            else:
                return_date = date_object
            
            return return_date.strftime(rtn_type)
    '''
    
    # -------------------------------------------------------------------------------------
    if df_in_FullBOM[fullBOM_EffStartdate].dtype != 'datetime64[ns]':
        df_in_FullBOM[fullBOM_EffStartdate] = pd.to_datetime(df_in_FullBOM[fullBOM_EffStartdate], format='%Y-%m-%d')
    
    if df_in_FullBOM[fullBOM_EffEnddate].dtype != 'datetime64[ns]':
        # 2262년 4월 11일 보다 큰일자 2262년 4월 11일 로 치환
        df_in_FullBOM[fullBOM_EffEnddate] = np.where(df_in_FullBOM[fullBOM_EffEnddate] > "2262-04-11",
                                                     "2262-04-11",
                                                     df_in_FullBOM[fullBOM_EffEnddate])        
        df_in_FullBOM[fullBOM_EffEnddate] = pd.to_datetime(df_in_FullBOM[fullBOM_EffEnddate], format='%Y-%m-%d')
    
    if df_in_FullBOM[fullBOM_SafetyDate].dtype != 'datetime64[ns]':
        df_in_FullBOM[fullBOM_SafetyDate] = pd.to_datetime(df_in_FullBOM[fullBOM_SafetyDate], format='%Y-%m-%d')
    
    if df_in_PLCMfg[pLCMfg_SRAComDate].dtype != 'datetime64[ns]':
        df_in_PLCMfg[pLCMfg_SRAComDate] = pd.to_datetime(df_in_PLCMfg[pLCMfg_SRAComDate], format='%m/%d/%Y %I:%M:%S %p')
    
    if df_in_PLCMfg[pLCMfg_EOPComDate].dtype != 'datetime64[ns]':
        df_in_PLCMfg[pLCMfg_EOPComDate] = pd.to_datetime(df_in_PLCMfg[pLCMfg_EOPComDate], format='%m/%d/%Y %I:%M:%S %p')
    
    # df_FullBOM : Merge  df_in_FullBOM &  df_in_PLCMfg
    df_FullBOM = df_in_FullBOM.merge(df_in_PLCMfg, on=[versionVersionName, itemItem, locationLocation], how='left')
    del df_in_FullBOM; del df_in_PLCMfg
    
    # greatest(a.Full bom eff startdate, a.Full BOM_Safety Date, b.PLC Mfg_SRA Com Date ) 중 : "Full bom eff startdate" 와 "Full BOM_Safety Date" 비교
    df_FullBOM[tmp_Date1] = np.select([(df_FullBOM[fullBOM_SafetyDate].isna()),
                                        (df_FullBOM[fullBOM_EffStartdate].isna()),
                                        (df_FullBOM[fullBOM_EffStartdate] < df_FullBOM[fullBOM_SafetyDate]),
                                        True,],
                                       [df_FullBOM[fullBOM_EffStartdate].dt.date,
                                        df_FullBOM[fullBOM_SafetyDate].dt.date,
                                        df_FullBOM[fullBOM_SafetyDate].dt.date, 
                                        df_FullBOM[fullBOM_EffStartdate].dt.date])
    
    df_FullBOM[tmp_Date1] = pd.to_datetime(df_FullBOM[tmp_Date1], format='%Y-%m-%d')
    
    # greatest(a.Full bom eff startdate, a.Full BOM_Safety Date, b.PLC Mfg_SRA Com Date ) 중 : 위 결과값 과 "PLC Mfg_SRA Com Date" 비교
    df_FullBOM[gtst_EffStartdate] = np.select([(df_FullBOM[pLCMfg_SRAComDate].isna()),
                                         (df_FullBOM[tmp_Date1].isna()),
                                         (df_FullBOM[tmp_Date1] < df_FullBOM[pLCMfg_SRAComDate]),
                                         True, ],
                                        [df_FullBOM[tmp_Date1].dt.date,
                                         df_FullBOM[pLCMfg_SRAComDate].dt.date,
                                         df_FullBOM[pLCMfg_SRAComDate].dt.date,
                                         df_FullBOM[tmp_Date1].dt.date])
    
    # greatest(a.Full bom eff enddate, b.PLC Mfg_EOP Com Date ) 
    df_FullBOM[gtst_EffEnddate] = np.select([(df_FullBOM[pLCMfg_EOPComDate].isna()),
                                               (df_FullBOM[fullBOM_EffEnddate].isna()),
                                               (df_FullBOM[fullBOM_EffEnddate] < df_FullBOM[pLCMfg_EOPComDate]),
                                               True, ],
                                              [df_FullBOM[fullBOM_EffEnddate].dt.date,
                                               df_FullBOM[pLCMfg_EOPComDate].dt.date,
                                               df_FullBOM[pLCMfg_EOPComDate].dt.date,
                                               df_FullBOM[fullBOM_EffEnddate].dt.date])
    
    
    #save_csv_file(df_FullBOM, 'df_FullBOM')
    vdCommon.gfn_saveDf(df_FullBOM, 'df_FullBOM',False)
    vdCommon.gfn_stepLog('=====> STEP 2-1 : FullBOM Data create End')
    
    ################################################################################################################
    # STEP 3 : output table create
    ################################################################################################################
    vdCommon.gfn_stepLog('=====> STEP 3 : Final output table create')
    
    # out Data 생성    
    df_out_FullBOM  = df_FullBOM[[versionVersionName, itemItem, locationLocation, toLocationToLocation, toItemToItem,
                                  itemMaterialItemMaterial, bOMInfoBOMVersion, bOMTypeBOMType, bOMStatusBOMStatus, statusStatus,
                                  gtst_EffStartdate, gtst_EffEnddate]].copy()
    del df_FullBOM
    
    #칼럼명 변경
    df_out_FullBOM.rename(columns={gtst_EffStartdate: fullBOM_EffStartdate,
                                   gtst_EffEnddate: fullBOM_EffEnddate}, inplace=True)
        
    # fullBOM_EffStartdate , fullBOM_EffEnddate 모두 Null 제외 : Udate 의미없음(기존과 같은값)
    # greatest(a.Full bom eff startdate, a.Full BOM_Safety Date, b.PLC Mfg_SRA Com Date ) : 모두 Null
    # greatest(a.Full bom eff enddate, b.PLC Mfg_EOP Com Date ) : 모두 Null
    #df_out_FullBOM = df_out_FullBOM.loc[~(df_out_FullBOM[fullBOM_EffStartdate].isna() & df_out_FullBOM[fullBOM_EffEnddate].isna())].copy()
    
    
    # 버전 처리 :
    #df_out_FullBOM[versionVersionName]  = paramOutVersion
    
    vdCommon.gfn_saveDf(df_out_FullBOM, 'df_out_FullBOM',False)
    vdCommon.gfn_stepLog('=====> STEP 3-1 : Final output table create End')
    
    if is_local:
        vdCommon.gfn_stepLog('=====> Output csv create')
        save_csv_file(df_out_FullBOM, 'df_out_FullBOM')
    
    row_count, col_count = df_out_FullBOM.shape
    note(f'=====> df_out_FullBOM rows : {row_count}, column : {col_count}')
    
    vdCommon.gfn_stepLog('=====> STEP 3-2 : End')

except Exception as e:
    logger.Note(p_note=traceback.format_exc(), p_log_level=common.G_log_level.debug())
    logger.Error()
    vdCommon.gfn_pyLog_error(traceback.format_exc())
    
    df_out_FullBOM = pd.DataFrame([], columns=[])

finally:
    vdCommon.gfn_stepLog('plugin Execution End ')
    
    # Batch 종료
    vdCommon.gfn_pyLog_end()
    
    df_out_log = vdCommon.gfn_getLog()
    df_out_logDetail = vdCommon.gfn_getLogDetail()
    
    # logger.PrintDF(p_df=df_out_log, p_df_name="df_out_log", p_log_level=common.G_log_level.info(), p_format=1, p_row_num=10)
    # logger.PrintDF(p_df=df_out_logDetail, p_df_name="df_out_logDetail", p_log_level=common.G_log_level.info(), p_format=1, p_row_num=10)
    
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