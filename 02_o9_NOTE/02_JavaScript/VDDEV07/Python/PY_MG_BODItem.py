"""
* 프로그램명
    - PY_MG_BODItem

* 내용
    - BOD Item Measure Group 생성을 위한 Program

* 변경이력
    - 2024.07.29 / 권태우 / Create
    - 2025.08.04 / 권태우 / Step2, Step3 ItemAsn 참조 오류 수정

* Script Parameter
    - paramOutVersion : 기본값 : CWV_MP, 호출시에, 결과데이터를 Version Name을 별도로 지정하는데에 사용.

* Input Table
    - df_in_BODList     : Select (&MFlocation * &SubLocationDC * &NSUITransModeView) on row, ({Measure.[BOD List_BOD Frozen], Measure.[BOD List_BOD LT], Measure.[BOD List_BOD Valid], Measure.[BOD List_Priority], Measure.[BOD List_Shipment LT] }) on column where {[Version].[Version Name], (Measure.[BOD List_BOD Valid] == "Y")};
    - df_in_BODListMF   : Select (&MFlocation * &SubLocationMF * &NSUITransModeView) on row, ({Measure.[BOD List_BOD Frozen], Measure.[BOD List_BOD LT], Measure.[BOD List_BOD Valid], Measure.[BOD List_Priority], Measure.[BOD List_Shipment LT] }) on column where {[Version].[Version Name], (Measure.[BOD List_BOD Valid] == "Y")};
    - df_in_BODListDC   : Select (&DClocation * &SubLocationDC * &NSUITransModeView) on row, ({Measure.[BOD List_BOD Frozen], Measure.[BOD List_BOD LT], Measure.[BOD List_BOD Valid], Measure.[BOD List_Priority], Measure.[BOD List_Shipment LT] }) on column where {[Version].[Version Name], (Measure.[BOD List_BOD Valid] == "Y")};
    - df_in_BODProdSET  : Select ([Item].[Product] * [Location].[Location] * [Sub Location].[Sub Location] * [Trans Mode].[Trans Mode] ) on row, ({Measure.[BOD Prod SET_BOD LT], Measure.[BOD Prod SET_BOD Valid], Measure.[BOD Prod SET_Priority], Measure.[BOD Prod SET_Shipment LT]}) on column where {[Version].[Version Name], (Measure.[BOD Prod SET_BOD Valid] == "Y")};
    - df_in_ItemSiteAsn1: Select ([Item].[Item] * [Item].[Product] * &MFlocation) on row, ({Measure.[Item Site Asn_Cur Status]}) on column where{[Version].[Version Name], &ProductTypeList, &FinishedGoods, Measure.[Item Site Asn_Cur Status] in {"PLANNED","ACTIVE"}, Measure.[Item Site Asn_Daily Change Flag_Interact Explosion]==true};
    - df_in_ItemSiteAsn2: Select ([Item].[Item] * [Item].[Product] * &DClocation) on row, ({Measure.[Item Site Asn_Cur Status]}) on column where{[Version].[Version Name], &ProductTypeList, &FinishedGoods, Measure.[Item Site Asn_Daily Change Flag_Interact Explosion]==true};

* Flow Summary
    - STEP1. BOD List 발췌 기준으로 Item Site Asn 조합하여  BOD Item 을 구성한다.
    - STEP2. BOD Prod Set 발췌 기준으로 Item Site Asn 조합하여 BOD Item 을 구성한다.

* Output Table
    - df_out_log
    - df_out_logDetail
    
    - df_out_BODItem
    - df_out_NewBODLocation

* 데이타 초기화
    -

* RUN 스크립트
    - EXEC plugin instance [PY_MG_BODItem] for Measures {[BOD Item_Cur Status]} using scope (&MPV)
        using arguments {(ExecutionMode, "MediumWeight"), (paramOutVersion , "CWV_MP"), (MaxSliceTableCells, 200000000), (MaxConcurrency, 1 )};

* Output Query
    - Select (&MPV * [Item].[Item] * [Location].[Location] * [Sub Location].[Sub Location] * [Trans Mode].[Trans Mode] ) on row, ({ Measure.[BOD Item_Cur Status]}) on column;

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
str_instance = 'PY_MG_BODItem'
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
            df_in_BODList = read_csv_file("df_in_BODList")
            df_in_BODListMF = read_csv_file("df_in_BODListMF")
            df_in_BODListDC = read_csv_file("df_in_BODListDC")
            df_in_BODProdSET = read_csv_file("df_in_BODProdSET")
            df_in_ItemSiteAsn1 = read_csv_file("df_in_ItemSiteAsn1")
            df_in_ItemSiteAsn2 = read_csv_file("df_in_ItemSiteAsn2")


        dataframes = {
            'df_in_BODList': df_in_BODList,
            'df_in_BODListMF': df_in_BODListMF,
            'df_in_BODListDC': df_in_BODListDC,
            'df_in_BODProdSET': df_in_BODProdSET,
            'df_in_ItemSiteAsn1': df_in_ItemSiteAsn1,
            'df_in_ItemSiteAsn2': df_in_ItemSiteAsn2,
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
        ITEM_TYPE_COLUMN = 'Item.[Item Type]'
        ITEM_PRODUCT_COLUMN = 'Item.[Product]'
        ITEM_PRODUCT_GROUP_COLUMN = 'Item.[Product Group]'
        ITEM_PRODUCT_TYPE_COLUMN = 'Item.[ProductType]'
        TRANS_MODE_COLUMN = 'Trans Mode.[Trans Mode]'
        ITEM_SITE_ASN_CUR_STATUS_COLUMN = 'Item Site Asn_Cur Status'
    
        BOD_LIST_BOD_FROZEN_COLUMN = 'BOD List_BOD Frozen'
        BOD_LIST_BOD_LT_COLUMN = 'BOD List_BOD LT'
        BOD_LIST_BOD_VAILD_COLUMN = 'BOD List_BOD Valid'
        BOD_LIST_EFF_ENDDATE_COLUMN = 'BOD List_Eff Enddate'
        BOD_LIST_EFF_STARTDATE_COLUMN = 'BOD List_Eff Startdate'
        BOD_LIST_PRIORITY_COLUMN = 'BOD List_Priority'
        BOD_LIST_SHIPMENT_LT_COLUMN = 'BOD List_Shipment LT'
    
        BOD_PROD_SET_BOD_LT_COLUMN = 'BOD Prod SET_BOD LT'
        BOD_PROD_SET_BOD_VAILD_COLUMN = 'BOD Prod SET_BOD Valid'
        BOD_PROD_SET_EFF_ENDDATE_COLUMN = 'BOD Prod SET_Eff Enddate'
        BOD_PROD_SET_EFF_STARTDATE_COLUMN = 'BOD Prod SET_Eff Startdate'
        BOD_PROD_SET_PRIORITY_COLUMN = 'BOD Prod SET_Priority'
        BOD_PROD_SET_SHIPMENT_LT_COLUMN = 'BOD Prod SET_Shipment LT'
    
        BOD_ITEM_BOD_FROZEN_COLUMN = 'BOD Item_BOD Frozen'
        BOD_ITEM_BOD_LT_COLUMN = 'BOD Item_BOD LT'
        BOD_ITEM_EFF_ENDDATE_COLUMN = 'BOD Item_Eff Enddate'
        BOD_ITEM_EFF_STARTDATE_COLUMN = 'BOD Item_Eff Startdate'
        BOD_ITEM_PRIORITY_COLUMN = 'BOD Item_Priority'
        BOD_ITEM_SHIPMENT_LT_COLUMN = 'BOD Item_Shipment LT'
        BOD_ITEM_CUR_STATUS_COLUMN = 'BOD Item_Cur Status'
        BOD_ITEM_ASN_COLUMN = 'BOD Item_Asn'

        LOCATION_BOD_LIST_IS_NEW_FLAG_COLUMN = 'Location_BOD List_is New Flag'
    
        ####################### Column add 2025.02.21 lsy ######################
        BOD_ITEM_LOCK_FLAG_COLUMN = 'BOD Item_Lock Flag'
        BOD_ITEM_BOD_LT_INHERIT_COLUMN = 'BOD Item_BOD LT_Inherit'
        BOD_ITEM_PRIORITY_INHERIT_COLUMN = 'BOD Item_Priority_Inherit'
        BOD_ITEM_SHIPMENT_LT_INHERIT_COLUMN = 'BOD Item_Shipment LT_Inherit'
        ########################################################################

        version_columns = [VERSION_NAME_COLUMN]

        df_BODList_columns = [
            ITEM_COLUMN, LOCATION_COLUMN, SUB_LOCATION_COLUMN, TRANS_MODE_COLUMN,
            BOD_ITEM_BOD_LT_COLUMN, BOD_ITEM_PRIORITY_COLUMN, BOD_ITEM_SHIPMENT_LT_COLUMN,
            BOD_ITEM_CUR_STATUS_COLUMN,
        ]

        df_BODItem_columns = [
            ITEM_COLUMN, LOCATION_COLUMN, SUB_LOCATION_COLUMN, TRANS_MODE_COLUMN,
            BOD_ITEM_BOD_LT_COLUMN, BOD_ITEM_PRIORITY_COLUMN, BOD_ITEM_SHIPMENT_LT_COLUMN,
            BOD_ITEM_CUR_STATUS_COLUMN, BOD_ITEM_ASN_COLUMN, BOD_ITEM_LOCK_FLAG_COLUMN,
        ]

        step('=====> STEP2 End')



    
        ################################################################################################################
        # STEP 3 :  데이터 선 가공
        ################################################################################################################
        step('=====> STEP3 Start : input data machining')


        # ====================> STEP3 by 0 (Start) -> BOD Item에 있는 Item만 처리
        # 불필요 컬럼 삭제
        df_in_BODList = df_in_BODList.drop(labels=[BOD_LIST_BOD_VAILD_COLUMN], axis=1)
        df_in_BODProdSET = df_in_BODProdSET.drop(labels=[BOD_PROD_SET_BOD_VAILD_COLUMN], axis=1)
        # df_in_BODItem = df_in_BODItem.drop(labels=[BOD_ITEM_BOD_FROZEN_COLUMN], axis=1)

        # columns_drop = [ITEM_PRODUCT_GROUP_COLUMN, ITEM_PRODUCT_TYPE_COLUMN, ITEM_TYPE_COLUMN]
        # df_in_ItemSiteAsn1 = df_in_ItemSiteAsn1.drop(labels=columns_drop, axis=1).drop_duplicates()
        # df_in_ItemSiteAsn2 = df_in_ItemSiteAsn2.drop(labels=columns_drop, axis=1).drop_duplicates()
        # ====================> STEP3 by 0 (End)

        step('=====> STEP3 End')
        
        
    
        ################################################################################################################
        # STEP 4 : output data machining
        ################################################################################################################
        step('=====> STEP4 Start : output data machining')

        def get_str_value(seq):
            str_map = {
                '1': 'df_BODList',
                '2': 'df_BODListMF',
                '3': 'df_BODListDC'
            }
            return str_map.get(seq, '')


        def process_bod_list_optimized(df_BODList, df_in_ItemSiteAsn1, df_in_ItemSiteAsn2, seq):
            df_name_str = get_str_value(seq)

            # 첫 번째 병합 (공통 키 기준 필터링)
            df_BODList_a = pd.merge(
                df_BODList,
                df_in_ItemSiteAsn1,
                how='inner',
                on=[LOCATION_COLUMN]
            )
            print_df(df_BODList_a, f'SETP3 by {seq}.1 _____ {df_name_str}_a .... merge[df_in_BODList, df_in_ItemSiteAsn1]')

            # 두 번째 병합 (위 병합과 별도 키 조건 사용)
            df_BODList_b = pd.merge(
                df_BODList,
                df_in_ItemSiteAsn2,
                how='inner',
                left_on=[SUB_LOCATION_COLUMN],
                right_on=[LOCATION_COLUMN]
            )
            print_df(df_BODList_b, f'SETP3 by {seq}.2 _____ {df_name_str}_b .... merge[df_in_BODList, df_in_ItemSiteAsn2]')

            # 불필요한 중복 컬럼 삭제 및 병렬 컬럼 이름 정리
            df_BODList_b = df_BODList_b.drop(columns=[LOCATION_COLUMN + '_y']).rename(
                columns={LOCATION_COLUMN + '_x': LOCATION_COLUMN}
            )

            # 최종 병합 (모든 공통 키 기준)
            merged_df = pd.merge(
                df_BODList_a,
                df_BODList_b,
                how='inner',
                on=[LOCATION_COLUMN, SUB_LOCATION_COLUMN, TRANS_MODE_COLUMN, ITEM_COLUMN]
            )
            print_df(df_BODList, f'SETP3 by {seq}.3 _____ {df_name_str} .... merge[df_BODList_a, df_BODList_b]')

            # 컬럼 매핑 (rename 처리)
            column_mapping = {
                BOD_LIST_BOD_LT_COLUMN + '_x': BOD_ITEM_BOD_LT_COLUMN,
                BOD_LIST_PRIORITY_COLUMN + '_x': BOD_ITEM_PRIORITY_COLUMN,
                BOD_LIST_SHIPMENT_LT_COLUMN + '_x': BOD_ITEM_SHIPMENT_LT_COLUMN,
                ITEM_SITE_ASN_CUR_STATUS_COLUMN + '_x': BOD_ITEM_CUR_STATUS_COLUMN
            }
            merged_df.rename(columns=column_mapping, inplace=True)

            # 필요한 필드만 선택하여 반환
            return merged_df[df_BODList_columns]

        # ====================> STEP4 by 1 (Start) -> BOD List 발췌 기준으로 Item Site Asn 조합하여 BOD Item 을 구성한다.

        df_BODList = process_bod_list_optimized(df_in_BODList, df_in_ItemSiteAsn1, df_in_ItemSiteAsn2, '1')
        print_df(df_BODList, 'STEP4 by 1 _____ df_BODList .... final')

        # ====================> STEP4 by 1 (End)



        # ====================> STEP4 by 2 (Start) -> BOD List MF 발췌 기준으로 Item Site Asn 조합하여 BOD Item 을 구성한다.

        df_BODListMF = process_bod_list_optimized(df_in_BODListMF, df_in_ItemSiteAsn1, df_in_ItemSiteAsn1, '2')
        print_df(df_BODListMF, 'STEP4 by 2 _____ df_BODListMF .... final')

        # ====================> STEP4 by 2 (End)




        # ====================> STEP4 by 3 (Start) -> BOD List DC 발췌 기준으로 Item Site Asn 조합하여 BOD Item 을 구성한다.

        df_BODListDC = process_bod_list_optimized(df_in_BODListDC, df_in_ItemSiteAsn2, df_in_ItemSiteAsn2, '3')
        print_df(df_BODListDC, 'STEP4 by 3 _____ df_BODListDC .... final')

        # ====================> STEP4 by 3 (End)



        def process_bod_prod_set_optimized(df_BODProdSET, df_in_ItemSiteAsn1, df_in_ItemSiteAsn2):
            # 첫 번째 병합 (공통 키 기준 필터링)
            df_BODProdSET_a = pd.merge(
                df_BODProdSET,
                df_in_ItemSiteAsn1,
                how='inner',
                on=[LOCATION_COLUMN, ITEM_PRODUCT_COLUMN]
            )
            print_df(df_BODProdSET_a, 'SETP3 by 4.1 _____ df_BODProdSET_a .... merge[df_in_BODProdSET, df_in_ItemSiteAsn1]')

            # 두 번째 병합 (위 병합과 별도 키 조건 사용)
            df_BODProdSET_b = pd.merge(
                df_BODProdSET,
                df_in_ItemSiteAsn2,
                how='inner',
                left_on=[SUB_LOCATION_COLUMN, ITEM_PRODUCT_COLUMN],
                right_on=[LOCATION_COLUMN, ITEM_PRODUCT_COLUMN]
            )
            print_df(df_BODProdSET_b, 'SETP3 by 4.2 _____ df_BODProdSET_b .... merge[df_in_BODProdSET, df_in_ItemSiteAsn2]')

            # 불필요한 중복 컬럼 삭제 및 병렬 컬럼 이름 정리
            df_BODProdSET_b = df_BODProdSET_b.drop(columns=[LOCATION_COLUMN + '_y']).rename(
                columns={LOCATION_COLUMN + '_x': LOCATION_COLUMN}
            )

            # 최종 병합 (모든 공통 키 기준)
            merged_df = pd.merge(
                df_BODProdSET_a,
                df_BODProdSET_b,
                how='inner',
                on=[LOCATION_COLUMN, SUB_LOCATION_COLUMN, TRANS_MODE_COLUMN, ITEM_COLUMN]
            )
            print_df(df_BODProdSET, 'SETP3 by 4.3 _____ df_BODProdSET .... merge[df_BODProdSET_a, df_BODProdSET_b]')

            # 컬럼 매핑 (rename 처리)
            column_mapping = {
                BOD_PROD_SET_BOD_LT_COLUMN+'_x': BOD_ITEM_BOD_LT_COLUMN,
                BOD_PROD_SET_PRIORITY_COLUMN+'_x': BOD_ITEM_PRIORITY_COLUMN,
                BOD_PROD_SET_SHIPMENT_LT_COLUMN+'_x': BOD_ITEM_SHIPMENT_LT_COLUMN,
                ITEM_SITE_ASN_CUR_STATUS_COLUMN+'_x': BOD_ITEM_CUR_STATUS_COLUMN,
            }
            merged_df.rename(columns=column_mapping, inplace=True)

            # 필요한 필드만 선택하여 반환
            return merged_df[df_BODList_columns]

        # ====================> STEP4 by 4 (Start) -> BOD Prod Set 발췌 기준으로 Item Site Asn 조합하여 BOD Item 을 구성한다.

        df_BODProdSET = process_bod_prod_set_optimized(df_in_BODProdSET, df_in_ItemSiteAsn1, df_in_ItemSiteAsn2)
        print_df(df_BODProdSET, 'STEP4 by 4 _____ df_BODProdSET .... final')

        # ====================> STEP4 by 4 (End)



        # ====================> STEP4 by 5 (Start) -> BOD Prod Set 발췌 기준으로 Item Site Asn 조합하여 BOD Item 을 구성한다.

        df_out_BODItem = pd.concat([df_BODList, df_BODListMF, df_BODListDC, df_BODProdSET]).drop_duplicates()
        print_df(df_out_BODItem, 'SETP4 by 5 _____ df_out_BODItem .... df concat')

        df_out_BODItem[BOD_ITEM_ASN_COLUMN] = 1
        df_out_BODItem[BOD_ITEM_LOCK_FLAG_COLUMN] = False    # add 2025.02.21 lsy
        df_out_BODItem[VERSION_NAME_COLUMN] = paramOutVersion

        colunms = version_columns + df_BODItem_columns
        df_out_BODItem = df_out_BODItem[colunms]

        ############################ add 2025.02.21 lsy ########################################
        df_out_BODItem[BOD_ITEM_BOD_LT_INHERIT_COLUMN] = df_out_BODItem[BOD_ITEM_BOD_LT_COLUMN]
        df_out_BODItem[BOD_ITEM_PRIORITY_INHERIT_COLUMN] = df_out_BODItem[BOD_ITEM_PRIORITY_COLUMN]
        df_out_BODItem[BOD_ITEM_SHIPMENT_LT_INHERIT_COLUMN] = df_out_BODItem[BOD_ITEM_SHIPMENT_LT_COLUMN]
        ########################################################################################

        # ====================> STEP4 by 5 (End)

        step('=====> STEP4 End')



    
        ################################################################################################################
        # STEP 5 : output table create
        ################################################################################################################
        step('=====> STEP5 Start : Final output table create')
    
        dataframes = {
            'df_out_BODItem': df_out_BODItem,
        }

        for name, df in dataframes.items():
            print_df(df, f'output table create .... {name}')

        step('=====> STEP5 End')

    except CustomException as e:
        step(f'=====> CustomException : {e}')
        df_out_BODItem = pd.DataFrame(columns=df_BODItem_columns)


    except Exception as ex:
        step(f'=====> Exception : {traceback.format_exc()}')
        df_out_BODItem = pd.DataFrame(columns=df_BODItem_columns)
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
