"""
* 프로그램명
    - PY_UI_BODLoadingInfoApply

* 내용
    - Loading 정보를 BOD Item, SOP Adjust

* 변경이력
    - 2024.07.29 / 권태우 / Create
    - 2025.08.27 / 권태우 / 파일명 변경 및 input변경, output 삭제
        파일명 변경 : PY_UI_BOD_SOPAdjust_LoadingInfo_Apply -> PY_UI_BODLoadingInfoApply
        input 변경 : df_in_loadinginfo
        input 삭제 : df_in_loadingexception, df_in_sopadjustintersection
        output 삭제 : df_out_sopadjust
    - 2025.09.30 / 권태우 / process 변경, input 추가, 삭제
        input 추가 : df_in_loadinginfoall, df_in_loadinginfonotall
        input 삭제 : df_in_loadinginfo

* Script Parameter
    - paramOutVersion : 기본값 : CWV_MP, 호출시에, 결과데이터를 Version Name을 별도로 지정하는데에 사용.

* Input Table
    - df_in_loadinginfoall      : Select (&SETMFLocation * &SETItem * [Sub Location].[Sub Location].[All] * [Trans Mode].[Trans Mode].[VESSEL] ) on row, ({ Measure.[Loading Master To Site_Minimum Lot], Measure.[Loading Master To Site_Multiple Lot]}) on column where {Version.[Version Name]};
    - df_in_loadinginfonotall   : Select (&SETMFLocation * &SETItem * [Sub Location].[Sub Location].filter(#.Name != "All") * [Trans Mode].[Trans Mode].[VESSEL] ) on row, ({  Measure.[Loading Master To Site_Minimum Lot], Measure.[Loading Master To Site_Multiple Lot], Measure.[Loading Master To Site_Valid]}) on column  where {Version.[Version Name]};
    - df_in_boditemintersection : Select ([Location].[Location] * [Item].[Item] * [Sub Location].[Sub Location] * [Trans Mode].[Trans Mode].[VESSEL] ) on row, ({Measure.[BOD Item_Asn], Measure.[BOD Item_Min Lot Qty], Measure.[BOD Item_Multi Lot Qty], Measure.[BOD Item_Loading Lock Flag]}) on column where {Version.[Version Name]};

* Flow Summary
    - STEP1. Input1(df_in_loadinginfoall) 을 To Site, TP Mode Exposion. (TP ="VSL"고정 / To Site = BOD Item의 From,To,TP,Item)
    - STEP2. BOD Item Output 업데이트 및 생성 (Update, Insert)
    - STEP3. input2 추출
    - STEP4. BOD Item 메저에 반영 (BOD Item 데이터를 가져올 필요 없음.)

* Output Table
    - df_out_log
    - df_out_logDetail

    - df_out_boditem

* 데이타 초기화
    -

* RUN 스크립트
    - EXEC plugin instance [PY_UI_BODLoadingInfoApply] for Measures {[BOD Item_Min Lot Qty]} using scope (&MPV)
        using arguments {(ExecutionMode, "MediumWeight"), (paramOutVersion , "CWV_MP"), (MaxSliceTableCells, 200000000), (MaxConcurrency, 1 )};

* Output Query
    - df_out_boditem
        Select (&MPV * [Location].[Location] * [Item].[Item] * [Sub Location].[Sub Location] * [Trans Mode].[Trans Mode] ) on row, ({Measure.[BOD Item_20FT Min Lot Qty], Measure.[BOD Item_20FT Multi Lot Qty], Measure.[BOD Item_40HC Min Lot Qty], Measure.[BOD Item_40HC Multi Lot Qty, Measure.[BOD Item_Loading Lock Flag] }) on column limit 100;
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
str_instance = 'PY_UI_BODLoadingInfoApply'
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
        setp(f"=====> 로그 처리 중 오류 발생: {str(e)}")
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
        step('=====> STEP1 Start : 전처리 - 모듈 내에서 사용될 input table load')

        if is_local:
            df_in_loadinginfoall = read_csv_file("df_in_loadinginfoall")
            df_in_loadinginfonotall = read_csv_file("df_in_loadinginfonotall")
            df_in_boditemintersection = read_csv_file("df_in_boditemintersection")


        dataframes = {
            'df_in_loadinginfoall': df_in_loadinginfoall,
            'df_in_loadinginfonotall': df_in_loadinginfonotall,
            'df_in_boditemintersection': df_in_boditemintersection,
        }

        for name, df in dataframes.items():
            print_df(df, f'input table load .... {name}')


        step('=====> STEP1 End')




        ################################################################################################################
        # STEP 2 : DataFrame Column 변수 처리
        ################################################################################################################
        step('=====> STEP2 Start : DataFrame Column 변수 처리')

        # 컬럼 변수 선언
        VERSION_NAME_COLUMN = 'Version.[Version Name]'
        LOCATION_COLUMN = 'Location.[Location]'
        SUB_LOCATION_COLUMN = 'Sub Location.[Sub Location]'
        TRANS_MODE_COLUMN = 'Trans Mode.[Trans Mode]'
        ITEM_COLUMN = 'Item.[Item]'

        BOD_ITEM_ASN_COLUMN = 'BOD Item_Asn'
        DUMMY_COLUMN = 'Dummy'

        LOADING_MASTER_TO_SITE_MINIMUM_LOT_COLUMN = 'Loading Master To Site_Minimum Lot'
        LOADING_MASTER_TO_SITE_MULTIPLE_LOT_COLUMN = 'Loading Master To Site_Multiple Lot'
        LOADING_MASTER_TO_SITE_VAILD_COLUMN = 'Loading Master To Site_Valid'

        BOD_ITEM_MIN_LOT_QTY_COLUMN = 'BOD Item_Min Lot Qty'
        BOD_ITEM_MULTI_LOT_QTY_COLUMN = 'BOD Item_Multi Lot Qty'
        BOD_ITEM_LOADING_LOCK_FLAG_COLUMN = 'BOD Item_Loading Lock Flag'

        df_BODItem_columns = [
            VERSION_NAME_COLUMN,
            LOCATION_COLUMN, ITEM_COLUMN, SUB_LOCATION_COLUMN, TRANS_MODE_COLUMN,
            BOD_ITEM_MIN_LOT_QTY_COLUMN, BOD_ITEM_MULTI_LOT_QTY_COLUMN,
            BOD_ITEM_LOADING_LOCK_FLAG_COLUMN,
        ]

        step('=====> STEP2 End')




        ################################################################################################################
        # STEP 3 :  데이터 선 가공
        ################################################################################################################
        step('=====> STEP3 Start : input data machining')

        # ====================> STEP3 by 0 (Start) -> BOD Item에 있는 Item만 처리
        # 불필요 컬럼 삭제
        df_in_boditemintersection = df_in_boditemintersection.drop(labels=[BOD_ITEM_ASN_COLUMN], axis=1).drop_duplicates()
        # ====================> STEP3 by 0 (End)

        step('=====> STEP3 End')



        ################################################################################################################
        # STEP 4 : output data machining
        ################################################################################################################
        step('=====> STEP4 Start : output data machining')

        step('=====> STEP4 by 1 Start : df_in_loadinginfoall 을 To Site, TP Mode Exposion. (TP ="VSL"고정 / To Site = BOD Item의 From,To,TP,Item)')
        # => df_in_loadinginfoall의 Sub loation이 "all"로 존재하는 모든 데이터 기준, Input3의 From, Item, TP Mode 으로 Join하여 Input3에 존재하는 모든 Sub location으로 데이터 부풀리기
        df_boditem_all = pd.merge(df_in_boditemintersection, df_in_loadinginfoall, how='inner', on=[LOCATION_COLUMN, ITEM_COLUMN, TRANS_MODE_COLUMN])
        print_df(df_boditem_all, 'SETP4 by 1.1 _____ df_boditem_all .... pd.merge[df_in_boditemintersection, df_in_loadinginfoall]')

        drop_columns = [SUB_LOCATION_COLUMN+'_y']
        for col in drop_columns:
            df_boditem_all.drop(columns=[col], inplace=True, errors='ignore')

        df_boditem_all.rename(columns={
            SUB_LOCATION_COLUMN+'_x': SUB_LOCATION_COLUMN,
        }, inplace=True)
        print_df(df_boditem_all, 'SETP4 by 1.2 _____ df_boditem_all .... create')
        step('=====> STEP4 by 1 End')





        step('=====> STEP4 by 2 Start : BOD Item Output 업데이트 및 생성 (Update, Insert)')
        # Step1의 데이터형태가 곧 BOD Item이라 별도 로직 불필요.
        # Step4 by 4 에서 처리
        step('=====> STEP4 by 2 End')





        step('=====> STEP4 by 3 Start : df_in_loadinginfonotall 추출 (Sublocation이 All 아닌 데이터)')
        # => df_in_loadinginfonotall의 Sub loation이 "all"이 아닌 데이터 기준, Input3의 From, To, Item, TP Mode 으로 Inner Join
        df_boditem_notall = pd.merge(df_in_boditemintersection, df_in_loadinginfonotall, how='inner', on=[LOCATION_COLUMN, SUB_LOCATION_COLUMN, ITEM_COLUMN, TRANS_MODE_COLUMN])
        print_df(df_boditem_notall, 'SETP4 by 3.1 _____ df_boditem_notall .... pd.merge[df_in_boditemintersection, df_in_loadinginfonotall]')
        step('=====> STEP4 by 3 End')





        step('=====> STEP4 by 4 Start : 최종 Output 생성')
        df_boditem = pd.concat([df_boditem_all, df_boditem_notall]).drop_duplicates()
        print_df(df_boditem, 'SETP4 by 4.1 _____ df_boditem .... concat')

        df_boditem[BOD_ITEM_LOADING_LOCK_FLAG_COLUMN] = df_boditem[LOADING_MASTER_TO_SITE_VAILD_COLUMN]
        df_boditem[BOD_ITEM_MIN_LOT_QTY_COLUMN] = df_boditem[LOADING_MASTER_TO_SITE_MINIMUM_LOT_COLUMN]
        df_boditem[BOD_ITEM_MULTI_LOT_QTY_COLUMN] = df_boditem[LOADING_MASTER_TO_SITE_MULTIPLE_LOT_COLUMN]

        mask = pd.isna(df_boditem[BOD_ITEM_LOADING_LOCK_FLAG_COLUMN]) | (df_boditem[BOD_ITEM_LOADING_LOCK_FLAG_COLUMN] == '')
        df_boditem.loc[mask, BOD_ITEM_LOADING_LOCK_FLAG_COLUMN] = 'Y'

        int_columns = [
            BOD_ITEM_MIN_LOT_QTY_COLUMN, BOD_ITEM_MULTI_LOT_QTY_COLUMN,
        ]
        for col in int_columns:
            df_boditem[col] = df_boditem[col].fillna(0).astype(int)

        print_df(df_boditem, 'SETP4 by 4.2 _____ df_boditem .... create')
        step('=====> STEP4 by 4 End')


        df_out_boditem = rename_and_delete_df(df_boditem)
        df_out_boditem[VERSION_NAME_COLUMN] = paramOutVersion
        df_out_boditem = df_out_boditem[df_BODItem_columns]

        step('=====> STEP4 End')




        ################################################################################################################
        # STEP 5 : output table create
        ################################################################################################################
        step('=====> STEP5 Start : Final output table create')

        dataframes = {
            'df_out_boditem': df_out_boditem,
        }

        for name, df in dataframes.items():
            print_df(df, f'output table create .... {name}')

        step('=====> STEP5 End')

    except CustomException as e:
        step(f'=====> CustomException : {e}')
        df_out_boditem = pd.DataFrame(columns=df_BODItem_columns)


    except Exception as ex:
        step(f'=====> Exception : {traceback.format_exc()}')
        df_out_boditem = pd.DataFrame(columns=df_BODItem_columns)
        logger.Error()
        vdCommon.gfn_pyLog_error(traceback.format_exc())

    finally:
        # 현재 메모리 사용량과 피크 메모리 사용량 체크 / 실행 시간 계산 (초 단위 -> 분 단위로 변환)
        current, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()

        step(f'=====> current: {format_size(current)}, peak: {format_size(peak)}, execution time: {run_time_minutes(start_time)}')
        step(f'===================== plugin Execution End ({get_formatted_time(time.time())}) =====================')

        df_out_log, df_out_logDetail = vd_log_end()
        logger.Finish()
