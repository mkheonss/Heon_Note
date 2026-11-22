"""
* 프로그램명
    - PY_UI_MtrlPSISub

* 내용
    - Material PSI 화면의 Measure값(Sub) 생성


* 변경이력
    - 2025.03.27 / 권태우 / Create

* Script Parameter
    - paramOutVersion : 기본값 : CWV_MP, 호출시에, 결과데이터를 Version Name을 별도로 지정하는데에 사용.

* Input Table
    - df_in_BODItemMtrlFull : Select ([Version].[Version Name] * [Location].[Location] * [Item Material].[Item Material] * [Sub Location].[Sub Location] * [Trans Mode].[Trans Mode] ) on row, ({Measure.[BOD Item MTrl Full_LT2], Measure.[BOD Item Mtrl Full_EFF Enddate], Measure.[BOD Item Mtrl Full_EFF Startdate], Measure.[BOD Item Mtrl Full_Flag], Measure.[BOD Item Mtrl Full_Intransit LT], Measure.[BOD Item Mtrl Full_Lot Size], Measure.[BOD Item Mtrl Full_MSL3], Measure.[BOD Item Mtrl Full_Supply LT], Measure.[BOD Item Mtrl Full_Transit Time]}) on column;
    - df_in_ItemMtrlSiteAssociation : Select ([Version].[Version Name] * [Location].[Location] * [Item Material].[Item Material] ) on row, ({Measure.[Item Mtrl Site Asn_Cur Status], Measure.[Item Mtrl Site Asn_Engine Flag], Measure.[Item Mtrl Site Asn_SS Time]}) on column;
    - df_in_MtrlPSI         : Select ([Version].[Version Name] * [Location].[Location] * [Item Material].[Item Material] * [Sub Location].[Sub Location] * [Trans Mode].[Trans Mode] ) on row, ({Measure.[Dummy], Measure.[Mtrl PSI_REQ_Demand]}) on column;

* Flow Summary
    -
* Output Table
    - df_out_log
    - df_out_logDetail

    - df_out_MtrlPSISub


* 데이타 초기화
    - DELETE DATA FOR MODEL [Mtrl PSI Sub] WHERE {[Version].[Version Name].filter(#.Name in {"CWV_MP"})};

* RUN 스크립트
    - EXEC plugin instance [PY_UI_MtrlPSISub] for Measures {[Mtrl PSI Sub_LT]} using scope (&MPV)
        using arguments {(ExecutionMode, "MediumWeight"), ("IncludeNullRows", "False"), (paramOutVersion , "CWV_MP"), (MaxSliceTableCells, 200000000), (MaxConcurrency, 1), ([Param.o9_sys_log_level], "DEBUG")};

* Output Query
    - df_out_MtrlPSISub / MG:  Mtrl PSI Sub
        Select (&MPV * [Location].[Location] * [Item Material].[Item Material] * [Sub Location].[Sub Location] * [Trans Mode].[Trans Mode] ) on row,
            ({Measure.[Mtrl PSI Sub_LT], Measure.[Mtrl PSI Sub_SS Time], Measure.[Mtrl PSI Sub_Supply LT], Measure.[Mtrl PSI Sub_Transit Time]}) on column limit 100;
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
str_instance = 'PY_UI_MtrlPSISub'
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
        # STEP 1 : input table load
        ################################################################################################################
        step('=====> STEP1 Start : input table load')

        if is_local:
            df_in_BODItemMtrlFull = read_csv_file("df_in_BODItemMtrlFull")
            df_in_ItemMtrlSiteAssociation = read_csv_file("df_in_ItemMtrlSiteAssociation")
            df_in_MtrlPSI = read_csv_file("df_in_MtrlPSI")


        dataframes = {
            'df_in_BODItemMtrlFull': df_in_BODItemMtrlFull,
            'df_in_ItemMtrlSiteAssociation': df_in_ItemMtrlSiteAssociation,
            'df_in_MtrlPSI': df_in_MtrlPSI,
        }

        for name, df in dataframes.items():
            print_df(df, f'input table load .... {name}')

        step('=====> STEP1 End')



        ################################################################################################################
        # STEP 2 : DataFrame Column 변수 처리
        ################################################################################################################
        step('=====> STEP2 Start : DataFrame Column 변수 처리')

        VERSION_NAME_COLUMN = 'Version.[Version Name]'
        LOCATION_COLUMN = 'Location.[Location]'
        SUB_LOCATION_COLUMN = 'Sub Location.[Sub Location]'
        ITEM_METERIAL_COLUMN = 'Item Material.[Item Material]'
        TRANS_MODE_COLUMN = 'Trans Mode.[Trans Mode]'

        BOD_ITEM_MTRL_FULL_LT_COLUMN = 'BOD Item Mtrl Full_LT'
        BOD_ITEM_MTRL_FULL_LT2_COLUMN = 'BOD Item MTrl Full_LT2'
        BOD_ITEM_MTRL_FULL_SUPPLY_LT_COLUMN = 'BOD Item Mtrl Full_Supply LT'
        BOD_ITEM_MTRL_FULL_TRANSIT_TIME_COLUMN = 'BOD Item Mtrl Full_Transit Time'
        ITEM_MTRL_SITE_ASN_SS_TIME_COLUMN = 'Item Mtrl Site Asn_SS Time'

        MTRL_PSI_SUB_LT_COLUMN = 'Mtrl PSI Sub_LT'
        MTRL_PSI_SUB_SUPPLY_LT_COLUMN = 'Mtrl PSI Sub_Supply LT'
        MTRL_PSI_SUB_TRANSIT_TIME_COLUMN = 'Mtrl PSI Sub_Transit Time'
        MTRL_PSI_SUB_SS_TIME_COLUMN = 'Mtrl PSI Sub_SS Time'

        TP_ORDER_COLUMN = 'TP_Order'

        TP_ORDER_Mapping = {
            'TRUCK': '1',
            'VESSEL': '2',
            'AIR': '3',
            'VSLEXP': '4',
            'AIREX': '5'
        }

        df_MtrlPSISub1_columns = [
            VERSION_NAME_COLUMN, LOCATION_COLUMN, ITEM_METERIAL_COLUMN, SUB_LOCATION_COLUMN, TRANS_MODE_COLUMN,
            MTRL_PSI_SUB_LT_COLUMN, MTRL_PSI_SUB_SUPPLY_LT_COLUMN, MTRL_PSI_SUB_TRANSIT_TIME_COLUMN
        ]

        df_MtrlPSISub_columns = df_MtrlPSISub1_columns + [MTRL_PSI_SUB_SS_TIME_COLUMN]

        step('=====> STEP2 End')



        ################################################################################################################
        # STEP 3 :  데이터 선 가공
        ################################################################################################################
        step('=====> STEP3 Start : input data machining')

        # ------------------ 테스트 디버깅용 ------------------ start
        # df_in_MtrlPSI = df_in_MtrlPSI[df_in_MtrlPSI[ITEM_METERIAL_COLUMN] == 'DMD_0000407284']
        # ------------------ 테스트 디버깅용 ------------------ end



        # 값이 비어있거나 None이면 False로 하고 empty df 를 생성하고 종료
        if df_in_MtrlPSI.empty:
            raise CustomException("STEP3 by 0.0 ____ df_in_MtrlPSI 값이 없습니다.")



        # ====================> STEP3 by 0 (Start)

        df_in_MtrlPSI = df_in_MtrlPSI[[
            VERSION_NAME_COLUMN, LOCATION_COLUMN, ITEM_METERIAL_COLUMN, SUB_LOCATION_COLUMN, TRANS_MODE_COLUMN
        ]].drop_duplicates()
        print_df(df_in_MtrlPSI, 'STEP3 by 0.1  ____ df_in_MtrlPSI .... uniqe')


        df_in_BODItemMtrlFull = df_in_BODItemMtrlFull[[
            VERSION_NAME_COLUMN, LOCATION_COLUMN, ITEM_METERIAL_COLUMN, SUB_LOCATION_COLUMN, TRANS_MODE_COLUMN,
            BOD_ITEM_MTRL_FULL_LT2_COLUMN, BOD_ITEM_MTRL_FULL_SUPPLY_LT_COLUMN, BOD_ITEM_MTRL_FULL_TRANSIT_TIME_COLUMN,
        ]].drop_duplicates()
        print_df(df_in_BODItemMtrlFull, 'STEP3 by 0.2  ____ df_in_BODItemMtrlFull .... uniqe')


        df_in_ItemMtrlSiteAssociation = df_in_ItemMtrlSiteAssociation[[
            VERSION_NAME_COLUMN, LOCATION_COLUMN, ITEM_METERIAL_COLUMN, ITEM_MTRL_SITE_ASN_SS_TIME_COLUMN
        ]].drop_duplicates()

        df_in_ItemMtrlSiteAssociation[ITEM_MTRL_SITE_ASN_SS_TIME_COLUMN] = (
            df_in_ItemMtrlSiteAssociation[ITEM_MTRL_SITE_ASN_SS_TIME_COLUMN].fillna(0).astype(int)
        )
        print_df(df_in_ItemMtrlSiteAssociation, 'STEP3 by 0.3  ____ df_in_ItemMtrlSiteAssociation .... uniqe')

        # ====================> STEP3 by 0 (End)






        step('=====> STEP3 End')




        # ################################################################################################################
        # # STEP 4 : output data machining
        # ################################################################################################################
        step('=====> STEP4 Start : output data machining')

        step('=====> STEP4 by 1 Start : df_in_MtrlPSI + df_in_BODItemMtrlFull modify')
        # 1.1 df_in_MtrlPSI, df_in_BODItemMtrlFull merge
        df_MtrlPSISubFull1 = pd.merge(df_in_MtrlPSI, df_in_BODItemMtrlFull, how='left',
                                      left_on=[VERSION_NAME_COLUMN, SUB_LOCATION_COLUMN, ITEM_METERIAL_COLUMN, LOCATION_COLUMN, TRANS_MODE_COLUMN],
                                      right_on=[VERSION_NAME_COLUMN, LOCATION_COLUMN, ITEM_METERIAL_COLUMN, SUB_LOCATION_COLUMN, TRANS_MODE_COLUMN]
                                      ).drop_duplicates()
        print_df(df_MtrlPSISubFull1, 'STEP4 by 1.1.1 ____ df_MtrlPSISubFull1 .... merge[df_in_MtrlPSI, df_in_BODItemMtrlFull]')

        df_MtrlPSISubFull1.rename(columns={
            SUB_LOCATION_COLUMN+'_x': SUB_LOCATION_COLUMN,
            LOCATION_COLUMN+'_x': LOCATION_COLUMN,
            BOD_ITEM_MTRL_FULL_LT2_COLUMN: MTRL_PSI_SUB_LT_COLUMN,
            BOD_ITEM_MTRL_FULL_SUPPLY_LT_COLUMN: MTRL_PSI_SUB_SUPPLY_LT_COLUMN,
            BOD_ITEM_MTRL_FULL_TRANSIT_TIME_COLUMN: MTRL_PSI_SUB_TRANSIT_TIME_COLUMN,
        }, inplace=True)

        df_MtrlPSISubFull1 = df_MtrlPSISubFull1[df_MtrlPSISub1_columns]

        int_columns = [MTRL_PSI_SUB_LT_COLUMN, MTRL_PSI_SUB_SUPPLY_LT_COLUMN, MTRL_PSI_SUB_TRANSIT_TIME_COLUMN]
        for col in int_columns:
            df_MtrlPSISubFull1[col] = df_MtrlPSISubFull1[col].fillna(0).astype(int)


        print_df(df_MtrlPSISubFull1, 'STEP4 by 1.1.2 ____ df_MtrlPSISubFull1 .... column rename')



        # 1.2 TP Order 설정
        #   'Trans Mode.[Trans Mode]' Mapping 처리
        df_in_BODItemMtrlFull[TP_ORDER_COLUMN] = df_in_BODItemMtrlFull[TRANS_MODE_COLUMN].map(TP_ORDER_Mapping)
        print_df(df_in_BODItemMtrlFull, 'STEP4 by 1.2.1 ____ df_in_BODItemMtrlFull .... Trans Mode mapping')

        df_MtrlPSISubFull2 = pd.merge(df_in_MtrlPSI, df_in_BODItemMtrlFull, how='left',
                                      left_on=[VERSION_NAME_COLUMN, LOCATION_COLUMN, ITEM_METERIAL_COLUMN],
                                      right_on=[VERSION_NAME_COLUMN, SUB_LOCATION_COLUMN, ITEM_METERIAL_COLUMN]).drop_duplicates()
        print_df(df_MtrlPSISubFull2, 'STEP4 by 1.2.2 ____ df_MtrlPSISubFull2 .... merge[df_in_MtrlPSI, df_in_BODItemMtrlFull]')

        df_MtrlPSISubFull2.rename(columns={
            LOCATION_COLUMN+'_x': LOCATION_COLUMN,
            SUB_LOCATION_COLUMN+'_y': SUB_LOCATION_COLUMN,
            TRANS_MODE_COLUMN+'_y': TRANS_MODE_COLUMN,
            BOD_ITEM_MTRL_FULL_LT2_COLUMN: MTRL_PSI_SUB_LT_COLUMN,
            BOD_ITEM_MTRL_FULL_SUPPLY_LT_COLUMN: MTRL_PSI_SUB_SUPPLY_LT_COLUMN,
            BOD_ITEM_MTRL_FULL_TRANSIT_TIME_COLUMN: MTRL_PSI_SUB_TRANSIT_TIME_COLUMN,
        }, inplace=True)

        columns = df_MtrlPSISub1_columns + [TP_ORDER_COLUMN]
        df_MtrlPSISubFull2 = df_MtrlPSISubFull2[columns]

        if not df_in_BODItemMtrlFull.empty:
            df_MtrlPSISubFull2 = df_MtrlPSISubFull2.sort_values(by=[LOCATION_COLUMN, TP_ORDER_COLUMN], ascending=[True, False])
            print_df(df_MtrlPSISubFull2, 'STEP4 by 1.2.2 ____ df_MtrlPSISubFull2 .... merge[df_in_MtrlPSI, df_in_BODItemMtrlFull]')

            groupby_columns = [VERSION_NAME_COLUMN, LOCATION_COLUMN, ITEM_METERIAL_COLUMN, SUB_LOCATION_COLUMN, TRANS_MODE_COLUMN, TP_ORDER_COLUMN]
            df_MtrlPSISubFull2 = df_MtrlPSISubFull2.groupby(groupby_columns, as_index=False).first()
            print_df(df_MtrlPSISubFull2, 'STEP4 by 1.2.4 ____ df_MtrlPSISubFull2 .... groupby first')


        df_MtrlPSISub1 = pd.concat([df_MtrlPSISubFull1, df_MtrlPSISubFull2], axis=0, ignore_index=True)
        df_MtrlPSISub1 = df_MtrlPSISub1[df_MtrlPSISub1_columns]
        print_df(df_MtrlPSISub1, 'STEP4 by 1.2.5 ____ df_MtrlPSISub1 .... df concat')
        step('=====> STEP4 by 1 End')




        step('=====> STEP4 by 2 Start : df_in_MtrlPSI + df_in_ItemMtrlSiteAssociation modify')
        df_MtrlPSISub2 = pd.merge(df_MtrlPSISubFull1, df_in_ItemMtrlSiteAssociation, how='left',
                                  left_on=[VERSION_NAME_COLUMN, LOCATION_COLUMN, ITEM_METERIAL_COLUMN],
                                  right_on=[VERSION_NAME_COLUMN, LOCATION_COLUMN, ITEM_METERIAL_COLUMN]).drop_duplicates()
        print_df(df_MtrlPSISub2, 'STEP4 by 2.1.1 ____ df_MtrlPSISub2 .... merge[df_in_MtrlPSI, df_in_ItemMtrlSiteAssociation]')

        df_MtrlPSISub2.rename(columns={
            ITEM_MTRL_SITE_ASN_SS_TIME_COLUMN: MTRL_PSI_SUB_SS_TIME_COLUMN,
        }, inplace=True)
        print_df(df_MtrlPSISub2, 'STEP4 by 2.1.2 ____ df_MtrlPSISub2 .... column rename')
        step('=====> STEP4 by 2 End')



        step('=====> STEP4 by 3 Start : df_MtrlPSISub1, df_MtrlPSISub2 concat')
        df_out_MtrlPSISub = pd.concat([df_MtrlPSISub1, df_MtrlPSISub2], axis=0, ignore_index=True)
        print_df(df_out_MtrlPSISub, 'STEP4 by 3 ____ df_out_MtrlPSISub .... df concat')

        df_out_MtrlPSISub = df_out_MtrlPSISub[df_MtrlPSISub_columns]
        df_out_MtrlPSISub[MTRL_PSI_SUB_SS_TIME_COLUMN] = df_out_MtrlPSISub[MTRL_PSI_SUB_SS_TIME_COLUMN].fillna(0).astype(int)
        df_out_MtrlPSISub[VERSION_NAME_COLUMN] = paramOutVersion
        step('=====> STEP4 by 3 End')

        step('=====> STEP4 End')


        ################################################################################################################
        # STEP 5 : output table create
        ################################################################################################################
        step('=====> STEP5 Start : output table create')

        dataframes = {
            'df_out_MtrlPSISub': df_out_MtrlPSISub,
        }

        for name, df in dataframes.items():
            print_df(df, f'output table create .... {name}')

        step('=====> STEP5 End')

    except CustomException as e:
        step(f'=====> CustomException : {e}')
        df_out_MtrlPSISub = pd.DataFrame(columns=df_MtrlPSISub_columns)


    except Exception as ex:
        step(f'=====> Exception : {traceback.format_exc()}')
        df_out_MtrlPSISub = pd.DataFrame(columns=df_MtrlPSISub_columns)
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


