"""
* 프로그램명
    - PY_MG_InventoryNodeNoCarry

* 내용
    - MP Engine 수행을 위한 ITEM, Location 기준 Inventory Parameter 정보 I/F
    - Plan 대상 Item Site Association (Measure Group : Item Site Asn) 에서
      실제 현재 PLAN 대상에 대한 Item - Location Association 만 반영
      ex) No Carry Buffer

* 변경이력
    - 2024.06.25 / 권태우 / Create
    - 2024.09.02 / 권태우 / 파일명 변경(PY_MG_InventoryNodeParameters -> PY_MG_InventoryNodeNoCarry), 로직변경
    - 2024.09.19 / 권태우 / input 추가(df_in_PlanningWeek), output 추가(df_out_QtyMaxTarget), SETP3 추가(No Carry Buffer 대상 df_out_QtyMaxTarget)

* Script Parameter
    - paramOutVersion : 기본값 : CWV_MP, 호출시에, 결과데이터를 Version Name을 별도로 지정하는데에 사용.

* Input Table
    - df_in_ItemSiteAsn   : Select (Version.[Version Name] * [Location].[Location] * [Item].[Item] ) on row, ({Measure.[Item Site Asn_Cur Status], Measure.[Item Site Asn_Engine Flag], Measure.[Item Site Asn_Item Grp], Measure.[Item Site Asn_Sales Prod Asn], Measure.[Item Site Asn_Stage]}) on column.filter(Measure.[Item Site Asn_Engine Flag]== true);
    - df_in_NoCarryBuffer : Select (&MPNoCarryBuffer);
    - df_in_NoCarryItem   : Select (&MPNoCarryItem);
    - df_in_PlanningWeek  : Select (&PlanningHorizon);

* Flow Summary
    - STEP1. Plan 대상 Item, Location(df_in_ItemSiteAsn) 정보 발췌
    - STEP2. No Carry Buffer 지정

* Output Table
    - df_out_log
    - df_out_logDetail

    - df_out_InventoryNodeParams
    - df_out_QtyMaxTarget

* 데이타 초기화
    - DELETE DATA FOR MODEL [001.011W Solver Inputs Inventory Node Parameters] where {Version.[Version Name].[CWV_MP]};

* RUN 스크립트
    - EXEC plugin instance [PY_MG_InventoryNodeNoCarry] for measures {[W No Carry Inventory]}
        using scope (&CWV)
        using arguments {
            (ExecutionMode, "MediumWeight"),
            ("IncludeNullRows", "False"),
            (paramOutVersion , "CWV_MP"),
            (MaxSliceTableCells, 200000000), (MaxConcurrency, 1),
            ([Param.o9_sys_log_level], "DEBUG")
        };

* Output Query
    - df_out_InventoryNodeParams / 001.011W Solver Inputs Inventory Node Parameters
        Select ([Version].[Version Name].[CWV_MP] * [Item].[Item] * [Location].[Location] ) on row,
        ({Measure.[W Alternate Material Node Group Priority],   // (LPS) 목적식 Minimize Alternate Flow의 priority
          Measure.[W Infinite Material Node],   // 무한자재 , Soft Constraints
          Measure.[W Infinite Material Supply Priority], // (LPS) 목적식 Minimize Infinite Material Supply의 priority
          Measure.[W Inventory Holding Priority],        // (LPS) 목적식 Minimize Inventory Hold의 priority
          Measure.[W Material Node Build Ahead Limit],  // 선행
          Measure.[W No Carry Inventory],  // NO Carry buffer 지정
          Measure.[W WIP Sweep Depth]
         }) on column;

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
# Local 개발 시에 필요한 공통 변수 선언
########################################################################################################################
# o9에 저장된 instanceName
str_instance = 'PY_MG_InventoryNodeNoCarry'
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
            df_in_ItemSiteAsn = read_csv_file("df_in_ItemSiteAsn")
            df_in_NoCarryBuffer = read_csv_file("df_in_NoCarryBuffer")
            df_in_NoCarryItem = read_csv_file("df_in_NoCarryItem")
            df_in_PlanningWeek = read_csv_file("df_in_PlanningWeek")
    
    
        print_df(df_in_ItemSiteAsn, 'input table load .... df_in_ItemSiteAsn')
        print_df(df_in_NoCarryBuffer, 'input table load .... df_in_NoCarryBuffer')
        print_df(df_in_NoCarryItem, 'input table load .... df_in_NoCarryItem')
        print_df(df_in_PlanningWeek, 'input table load .... df_in_PlanningWeek')
    
        step('=====> STEP1 End')


    
        ################################################################################################################
        # STEP 2 : DataFrame Column 변수 처리
        ################################################################################################################
        step('=====> STEP2 Start : DataFrame Column 변수 처리')
    
        VERSION_NAME_COLUMN = 'Version.[Version Name]'
        LOCATION_COLUMN = 'Location.[Location]'
        ITEM_COLUMN = 'Item.[Item]'
        ITEM_STAGE_COLUMN = 'Item.[Item Stage]'
    
        TIME_WEEK_COLUMN = 'Time.[Week]'
    
        ITEM_SITE_ASN_CUR_STATUS_COLUMN = "Item Site Asn_Cur Status"
        ITEM_SITE_ASN_ENGINE_FLAG_COLUMN = "Item Site Asn_Engine Flag"
        ITEM_SITE_ASN_ITEM_GRP_COLUMN = "Item Site Asn_Item Grp"
        ITEM_SITE_ASN_SALES_PROD_ASN_COLUMN = "Item Site Asn_Sales Prod Asn"
        ITEM_SITE_ASN_STAGE_COLUMN = "Item Site Asn_Stage"
    
        W_ALTERNATE_METERIAL_NODE_GROUP_PRIORITY_COLUMN = "W Alternate Material Node Group Priority"
        W_INFINITE_METERIAL_NODE_COLUMN = "W Infinite Material Node"
        W_INFINITE_METERIAL_SUPPLY_PRIORITY_COLUMN = "W Infinite Material Supply Priority"
        W_INVENTORY_HOLDING_PRIORITY_COLUMN = "W Inventory Holding Priority"
        W_METERIAL_NODE_BUILD_AHEAD_LIMIT_COLUMN = "W Material Node Build Ahead Limit"
        W_NO_CARRY_INVENTORY_COLUMN = "W No Carry Inventory"
        W_WIP_SWEEP_DEPTH_COLUMN = "W WIP Sweep Depth"
    
        W_QUANTIRY_MAX_TARGET_COLUMN = 'W Quantity Max Target'
        
        df_InventoryNodeParams_columns = [
            VERSION_NAME_COLUMN, ITEM_COLUMN, LOCATION_COLUMN, W_ALTERNATE_METERIAL_NODE_GROUP_PRIORITY_COLUMN, 
            W_INFINITE_METERIAL_NODE_COLUMN, W_INFINITE_METERIAL_SUPPLY_PRIORITY_COLUMN, W_INVENTORY_HOLDING_PRIORITY_COLUMN, 
            W_METERIAL_NODE_BUILD_AHEAD_LIMIT_COLUMN, W_NO_CARRY_INVENTORY_COLUMN, W_WIP_SWEEP_DEPTH_COLUMN
        ]
    
        df_QtyMaxTarget_columns = [
            VERSION_NAME_COLUMN, ITEM_COLUMN, LOCATION_COLUMN, TIME_WEEK_COLUMN, W_QUANTIRY_MAX_TARGET_COLUMN
        ]
    
        step('=====> STEP2 End')
        
        
    
        ################################################################################################################
        # STEP 3 :  데이터 선 가공
        ################################################################################################################
        step('=====> STEP3 Start : input data machining')
    
        # ====================> STEP3 by 1 : Plan 대상 Item, Location(df_in_ItemSiteAsn) 정보 발췌

        # 1.1 df_in_ItemSiteAsn remake
        drop_column = [col for col in list(df_in_ItemSiteAsn.columns) if col not in [VERSION_NAME_COLUMN,
                                                                                     LOCATION_COLUMN,
                                                                                     ITEM_COLUMN]]
        df_in_ItemSiteAsn = df_in_ItemSiteAsn.drop(labels=drop_column, axis=1, inplace=False).drop_duplicates(
            subset=[LOCATION_COLUMN], keep='first')

        # 1.2 df_in_PlanningWeek 에서 Time.[Week] 만 발췌
        df_in_PlanningWeek = df_in_PlanningWeek[[TIME_WEEK_COLUMN]].copy()
        df_in_PlanningWeek['key'] = 1

    
    
    
        # ====================> STEP3 by 2 : No Carry Inventory 지정 df_NoCarry Set 구성 df_InventoryNodeParams Insert

        # df_InventoryNodeParams create
        df_InventoryNodeParams = pd.merge(df_in_ItemSiteAsn, df_in_NoCarryBuffer, how='inner', on=[LOCATION_COLUMN])
        print_df(df_InventoryNodeParams, 'STEP3 by 2.1 ____ df_InventoryNodeParams .... create')



        # 값이 비어있거나 None이면 False로 하고 empty df 를 생성하고 종료
        if df_InventoryNodeParams.empty:
            raise CustomException(".... df_InventoryNodeParams 값이 없습니다.")


    
        # df_merged_location, df_in_NoCarryItem join
        df_InventoryNodeParams = pd.merge(df_InventoryNodeParams, df_in_NoCarryItem, how='inner', on=[ITEM_COLUMN])
        print_df(df_InventoryNodeParams, 'STEP3 by 2.2 ____ df_InventoryNodeParams .... merge[df_InventoryNodeParams, df_in_NoCarryItem]')
    
        # Selecting only required columns: item and location, and the constant column 'W No Carry Inventory'
        df_InventoryNodeParams = df_InventoryNodeParams[[ITEM_COLUMN, LOCATION_COLUMN]].copy().drop_duplicates()
        df_InventoryNodeParams[W_NO_CARRY_INVENTORY_COLUMN] = 1
        print_df(df_InventoryNodeParams, 'STEP3 by 2.3 ____ df_InventoryNodeParams .... select')
    
    
    
    
        # ====================> STEP3 by 3 : No Carry Buffer 대상 df_QtyMaxTarget (001.019W Solver Inputs Inventory Inputs) Insert

        # 3.1 df_InventoryNodeParams, df_in_PlanningWeek join (카테시안곱 처리)
        df_InventoryNodeParams['key'] = 1
        df_QtyMaxTarget = pd.merge(df_InventoryNodeParams, df_in_PlanningWeek, how='outer', on='key')

        # 3.2 key 삭제
        df_QtyMaxTarget.drop(columns=['key', W_NO_CARRY_INVENTORY_COLUMN], inplace=True)
        df_InventoryNodeParams.drop(columns=['key'], inplace=True)

        # 3.3 컬럼추가
        df_QtyMaxTarget[W_QUANTIRY_MAX_TARGET_COLUMN] = 0
        print_df(df_QtyMaxTarget, 'STEP3 by 3.3 ____ df_QtyMaxTarget .... create')
    
        step('=====> STEP3 End')
        
        
    
        ################################################################################################################
        # STEP 4 : output data machining
        ################################################################################################################
        step('=====> STEP4 Start : output data machining')

        # df_InventoryNodeParams 추가컬럼생성

        df_InventoryNodeParams[W_ALTERNATE_METERIAL_NODE_GROUP_PRIORITY_COLUMN] = np.nan
        df_InventoryNodeParams[W_INFINITE_METERIAL_NODE_COLUMN] = np.nan
        df_InventoryNodeParams[W_INFINITE_METERIAL_SUPPLY_PRIORITY_COLUMN] = np.nan
        df_InventoryNodeParams[W_INVENTORY_HOLDING_PRIORITY_COLUMN] = np.nan
        df_InventoryNodeParams[W_METERIAL_NODE_BUILD_AHEAD_LIMIT_COLUMN] = np.nan
        df_InventoryNodeParams[W_WIP_SWEEP_DEPTH_COLUMN] = np.nan

        # output create
        df_out_InventoryNodeParams = rename_and_delete_df(df_InventoryNodeParams)
        df_out_QtyMaxTarget = rename_and_delete_df(df_QtyMaxTarget)
        
        df_out_InventoryNodeParams[VERSION_NAME_COLUMN] = paramOutVersion
        df_out_QtyMaxTarget[VERSION_NAME_COLUMN] = paramOutVersion
    
        # 컬럼명 변경 및 순서 재정렬
        df_out_InventoryNodeParams = df_InventoryNodeParams[df_InventoryNodeParams_columns]
        df_out_QtyMaxTarget = df_QtyMaxTarget[df_QtyMaxTarget_columns]
        
        step('=====> STEP4 End')
        
        
    
        ################################################################################################################
        # STEP 5 : output table create
        ################################################################################################################
        step('=====> STEP 5(Start) : Final output table create')
    
        print_df(df_out_InventoryNodeParams, 'output table create .... df_out_InventoryNodeParams', True)
        print_df(df_out_QtyMaxTarget, 'output table create .... df_out_QtyMaxTarget', True)
        
        step('=====> STEP5 End')

        # 현재 메모리 사용량과 피크 메모리 사용량 체크 / 실행 시간 계산 (초 단위 -> 분 단위로 변환)
        current, peak = tracemalloc.get_traced_memory()

        step(f'=====> current: {format_size(current)}, peak: {format_size(peak)}, execution time: {run_time_minutes(start_time)}')
        step(f'===================== plugin Execution End ({get_formatted_time(time.time())}) =====================')
        tracemalloc.stop()

    except CustomException as e:
        step(f'=====> CustomException : {e}')
        df_out_InventoryNodeParams = pd.DataFrame(columns=df_InventoryNodeParams_columns)
        df_out_QtyMaxTarget = pd.DataFrame(columns=df_QtyMaxTarget_columns)

    except Exception as ex:
        step(f'=====> Exception : {traceback.format_exc()}')
        df_out_InventoryNodeParams = pd.DataFrame(columns=df_InventoryNodeParams_columns)
        df_out_QtyMaxTarget = pd.DataFrame(columns=df_QtyMaxTarget_columns)
        logger.Error()
        vdCommon.gfn_pyLog_error(traceback.format_exc())

    finally:
        vd_log_end()
        df_out_log = vdCommon.gfn_getLog()
        df_out_logDetail = vdCommon.gfn_getLogDetail()
        logger.Finish()
        step('=====> Batch end')
