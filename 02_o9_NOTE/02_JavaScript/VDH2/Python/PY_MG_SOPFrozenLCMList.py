"""
* 프로그램명
    - PY_MG_SOPFrozenLCMList

* 내용
    - LCM SOP Frozen List 구성을 위한 프로그램

* 변경이력
    - 2024.08.29 / 권태우 / Create

* Script Parameter
    - paramOutVersion : 기본값 : CurrentWorkingView, 호출시에, 결과데이터를 Version Name을 별도로 지정하는데에 사용.

* Input Table
    - df_in_ItemSiteAsn     : Select (Version.[Version Name] * &LCMItem * &LocationCategoryLCMLocation * [Item].[Product Group] * [Item].[SCM Type]) on row, ({Measure.[Item Site Asn_Engine Flag]}) on column.filter(Measure.[Item Site Asn_Engine Flag] == true);
    - df_in_SOPFrozenPeriod : Select (Version.[Version Name] * [Item].[SCM Type] * &MFLocation * [Product].[Product Group] ) on row, ({Measure.[SOP Frozen Period_Smry Copy], Measure.[SOP Frozen Period_Smry Exnd] }) on column;
    - df_in_SOPFrozen1      : Select (Version.[Version Name]  * [Group].[Group ID] ) on row, ({Measure.[SOP Frozen_From Site], Measure.[SOP Frozen_Frz], Measure.[SOP Frozen_Frz Enddate], Measure.[SOP Frozen_Frz Startdate], Measure.[SOP Frozen_Item], Measure.[SOP Frozen_Prod Grp], Measure.[SOP Frozen_Prty], Measure.[SOP Frozen_To Site]}) on column where {Measure.[SOP Frozen_Valid Flag] == "Y"};

* Flow Summary
    - STEP1. df_in_SOPFrozenPeriod와  df_in_ItemSiteAsn와 join 하고,  SOP Frozen Period_Smry Copy값을 df_out_SopFrozenList의  SOP Fix LCM List_Frozen 로 update
    - STEP2. df_in_SOPFrozen우선순위 순으로 df_out_SopFrozenList에  update

* Output Table
    - df_out_SopFrozenList

* 데이타 초기화
    - DELETE DATA FOR MODEL [SOP Frozen List] where {Version.[Version Name].filter(#.Name in {"CWV_MP","CurrentWorkingView"})};

* RUN 스크립트
    - EXEC plugin instance [PY_MG_SOPFrozenLCMList] for Measures {[SOP Frozen List_FP Period]}
        using scope (&MPV)
        using arguments {
            (ExecutionMode, "MediumWeight"),
            ("IncludeNullRows", "False"),
            (paramOutVersion , "CWV_MP"),
            (MaxSliceTableCells, 200000000), (MaxConcurrency, 1 ),
            ([Param.o9_sys_log_level], "DEBUG")
        };

* Output Query
    - Select (&CWV * [Item].[Item] * [Location].[Location] * [Sub Location].[Sub Location] ) on row,
        ({Measure.[SOP Frozen List_FP Period], Measure.[SOP Frozen List_Frz Enddate], Measure.[SOP Frozen List_Frz Startdate], Measure.[SOP Frozen List_Group ID]}) on column;

"""
import gc
import traceback
import time
import numpy as np
import pandas as pd
import tracemalloc
from NSCMCommon import NSCMCommon as common

########################################################################################################################
# Local 개발 시에 필요한 공통 변수 선언
########################################################################################################################
# o9에 저장된 instanceName
str_instance = 'PY_MG_SOPFrozenLCMList'
is_local = common.gfn_get_isLocal()

########################################################################################################################
# log 설정 : PROGRAM file_name
########################################################################################################################
logger = common.G_Logger(p_py_name=str_instance)
common.gfn_set_local_logfile()
LOG_LEVEL = common.G_log_level
COMMON_SOURCE_VERSION = common.G_SourceVersion


########################################################################################################################
# 내부함수
########################################################################################################################
def read_csv_file(file_name):
    return pd.read_csv(f"{file_name}.csv", encoding="UTF-8")


def save_csv_file(df, file_name):
    if is_local:
        df.to_csv(f"{file_name}.csv", index=False)


def delete_dfs(*dfs):
    for df in dfs:
        del df
        gc.collect()


def print_df(df, df_name, p_log_level=LOG_LEVEL.debug(), p_format=1):
    empty_status = "is empty" if df.empty else ""
    df_name = f"{df_name} {empty_status}"
    logger.PrintDF(p_df=df, p_df_name=df_name, p_log_level=p_log_level, p_format=p_format)


def note(string, p_log_level=LOG_LEVEL.debug()):
    logger.Note(p_note=f'{string}', p_log_level=p_log_level)


def step(no, string):
    logger.Step(p_step_no=no, p_step_desc=f'{string}')



########################################################################################################################
# logic start
########################################################################################################################
# 현재 메모리 사용량과 피크 메모리 사용량 체크 시작
tracemalloc.start()
start_time = time.time()

logger.debug(f'[START] {str_instance}')
logger.Start()
note(f'=====> Common SourceVersion : {COMMON_SOURCE_VERSION}')
step(0, '===================== plugin Execution Start =====================')

try:
    ################################################################################################################
    # STEP 1 : 전처리 - 모듈 내에서 사용될 input table load
    ################################################################################################################
    step(100, '=====> STEP 1(Start) : 전처리 - 모듈 내에서 사용될 input table load')

    # Value 변수 선언
    PARAM_OUTVERSION_VALUE = "CWV_MP"

    # csv 파일 이름과 변수명을 매핑한 딕셔너리 생성
    if is_local:
        # 로컬일 경우 버전 처리
        paramOutVersion = PARAM_OUTVERSION_VALUE

        df_in_ItemSiteAsn = read_csv_file("df_in_ItemSiteAsn")
        df_in_SOPFrozenPeriod = read_csv_file("df_in_SOPFrozenPeriod")
        df_in_SOPFrozen1 = read_csv_file("df_in_SOPFrozen1")


    print_df(df_in_ItemSiteAsn, 'STEP 1 - Input table load .....> df_in_ItemSiteAsn')
    print_df(df_in_SOPFrozenPeriod, 'STEP 1 - Input table load .....> df_in_SOPFrozenPeriod')
    print_df(df_in_SOPFrozen1, 'STEP 1 - Input table load .....> df_in_SOPFrozen1')


    # 입력 변수 확인
    if paramOutVersion is None or paramOutVersion.strip() == '':
        paramOutVersion = PARAM_OUTVERSION_VALUE

    # input dataframe 확인용 로그
    note(f'=====> paramOutVersion : {paramOutVersion}')

    step(100, '=====> STEP 1(End) : Check memory usage & runtime')

    ################################################################################################################
    # STEP 2 : DataFrame Column 변수 처리
    ################################################################################################################
    step(200, '=====> STEP 2(Start) : DataFrame Column 변수 처리')

    # 컬럼 변수 선언
    VERSION_NAME_COLUMN = 'Version.[Version Name]'

    LOCATION_COLUMN = 'Location.[Location]'
    SUB_LOCATION_COLUMN = '[Sub Location].[Sub Location]'
    TO_LOCATION_COLUMN = '[To Location].[To Location]'

    ITEM_COLUMN = 'Item.[Item]'
    ITEM_TYPE_COLUMN = 'Item.[Item Type]'
    ITEM_PRODUCT_GROUPL_COLUMN = 'Item.[Product Group]'
    ITEM_PRODUCT_COLUMN = 'Item.[Product]'
    ITEM_SCM_TYPE_COLUMN = 'Item.[SCM Type]'
    ITEM_SCM_TYPE_X_COLUMN = 'Item.[SCM Type]_y'
    ITEM_SCM_TYPE_Y_COLUMN = 'Item.[SCM Type]_x'
    ITEM_SITE_ASN_ENGINE_FLAG_COLUMN = 'Item Site Asn_Engine Flag'

    PRODUCT_GROUP_PRODUCT_GROUP_COLUMN = 'Product Group.[Product Group]'
    PRODUCT_PRODUCT_GROUP_COLUMN = 'Product.[Product Group]'
    CATEGORY_COLUMN = 'Category.[Category]'
    GROUP_ID_COLUMN = 'Group.[Group ID]'

    SOP_FROZEN_FORM_SITE_COLUMN = 'SOP Frozen_From Site'
    SOP_FROZEN_FRZ_COLUMN = 'SOP Frozen_Frz'
    SOP_FROZEN_FRZ_ENDDATE_COLUMN = 'SOP Frozen_Frz Enddate'
    SOP_FROZEN_FRZ_STARTDATE_COLUMN = 'SOP Frozen_Frz Startdate'
    SOP_FROZEN_ITEM_COLUMN = 'SOP Frozen_Item'
    SOP_FROZEN_PROD_GRP_COLUMN = 'SOP Frozen_Prod Grp'
    SOP_FROZEN_PRTY_COLUMN = 'SOP Frozen_Prty'
    SOP_FROZEN_TO_SITE_COLUMN = 'SOP Frozen_To Site'

    SOP_FROZEN_PERIOD_SMRY_COPY_COLUMN = 'SOP Frozen Period_Smry Copy'

    SOP_FROZEN_LIST_FP_PERIOD_COLUMN = 'SOP Frozen List_FP Period'
    SOP_FROZEN_LIST_FRZ_ENDDATE_COLUMN = 'SOP Frozen List_Frz Enddate'
    SOP_FROZEN_LIST_FRZ_STARTDATE_COLUMN = 'SOP Frozen List_Frz Startdate'
    SOP_FROZEN_LIST_GROUP_ID_COLUMN = 'SOP Frozen List_Group ID'

    step(200, '=====> STEP 2(End) : Check memory usage & runtime')

    ################################################################################################################
    # STEP 3 :  데이터 선 가공
    ################################################################################################################
    step(300, '=====> STEP 3(Start) : input data machining')

    # ====================> Step 1 (Start) > df_in_SOPFrozenPeriod와  df_in_ItemSiteAsn와 join 하고,
    #                                        SOP Frozen Period_Smry Copy값을 df_out_SopFrozenList에 의 SOP Fix LCM List_Frozen 로 update
    # 1.1 df_SopFrozenList create
    df_buf_step1 = pd.merge(df_in_SOPFrozenPeriod, df_in_ItemSiteAsn, how='inner',
                            left_on=[VERSION_NAME_COLUMN, LOCATION_COLUMN, PRODUCT_PRODUCT_GROUP_COLUMN],
                            right_on=[VERSION_NAME_COLUMN, LOCATION_COLUMN, ITEM_PRODUCT_GROUPL_COLUMN])
    print_df(df_buf_step1, 'STEP4 by 1.1 ____ df_buf_step1 ..... merge')


    # 1.2 SCM_TYPE 설정
    df_buf_step1[ITEM_SCM_TYPE_COLUMN] = np.where(
        df_buf_step1[ITEM_SCM_TYPE_X_COLUMN] == '-',
        df_buf_step1[ITEM_SCM_TYPE_Y_COLUMN],
        df_buf_step1[ITEM_SCM_TYPE_X_COLUMN]
    )

    # 1.3 SCM_TYPE이 같은건만 복사
    df_buf_SopFrozenList = df_buf_step1[
        (df_buf_step1[ITEM_SCM_TYPE_COLUMN] == df_buf_step1[ITEM_SCM_TYPE_Y_COLUMN])
    ].copy().drop_duplicates()

    # 1.4 사용된 df 삭제
    delete_dfs(df_buf_step1, df_in_SOPFrozenPeriod, df_in_ItemSiteAsn)

    # 1.5 컬럼설정, 변경, 삭제
    df_buf_SopFrozenList[SUB_LOCATION_COLUMN] = '-'
    df_buf_SopFrozenList.rename(columns={SOP_FROZEN_PERIOD_SMRY_COPY_COLUMN: SOP_FROZEN_LIST_FP_PERIOD_COLUMN}, inplace=True)
    df_buf_SopFrozenList = df_buf_SopFrozenList.drop(labels=[ITEM_SCM_TYPE_X_COLUMN, ITEM_SCM_TYPE_Y_COLUMN,
                                                             ITEM_SITE_ASN_ENGINE_FLAG_COLUMN],
                                                     axis=1)
    print_df(df_buf_SopFrozenList, 'STEP4 by 1 ____ df_buf_SopFrozenList ..... final')
    # ====================> Step 1 (End)




    # ====================> Step 2 (Start) > df_in_SOPFrozen우선순위 순으로 df_out_SopFrozenList 에 update
    # 2.1 df_in_SOPFrozen1 > 'SOP Frozen_Prty' 기준으로 desc 설정
    df_in_SOPFrozen1 = df_in_SOPFrozen1.sort_values(by=[SOP_FROZEN_PRTY_COLUMN], ascending=[False])

    # 2.2
    #   2.2.1 qeual join
    df_equal_SOPFrozen = pd.merge(df_in_SOPFrozen1, df_buf_SopFrozenList, how='inner',
                                  left_on=[VERSION_NAME_COLUMN, SOP_FROZEN_FORM_SITE_COLUMN,
                                           SOP_FROZEN_TO_SITE_COLUMN, SOP_FROZEN_ITEM_COLUMN],
                                  right_on=[VERSION_NAME_COLUMN, LOCATION_COLUMN,SUB_LOCATION_COLUMN, ITEM_COLUMN])
    print_df(df_equal_SOPFrozen, 'STEP4 by 2.2 ____ df_equal_SOPFrozen ..... equal merge')

    #       2.2.1.1 컬럼설정
    df_equal_SOPFrozen[SOP_FROZEN_LIST_GROUP_ID_COLUMN] = df_equal_SOPFrozen[GROUP_ID_COLUMN]
    df_equal_SOPFrozen[SOP_FROZEN_LIST_FRZ_STARTDATE_COLUMN] = df_equal_SOPFrozen[SOP_FROZEN_FRZ_STARTDATE_COLUMN]
    df_equal_SOPFrozen[SOP_FROZEN_LIST_FRZ_ENDDATE_COLUMN] = df_equal_SOPFrozen[SOP_FROZEN_FRZ_ENDDATE_COLUMN]
    df_equal_SOPFrozen[SOP_FROZEN_LIST_FP_PERIOD_COLUMN] = np.nanmax(
        df_equal_SOPFrozen[[SOP_FROZEN_LIST_FP_PERIOD_COLUMN, SOP_FROZEN_FRZ_COLUMN]].values, axis=1) # 큰 값으로만 UPDATE

    #       2.2.1.2 필요컬럼 발췌
    df_equal_SOPFrozen = df_equal_SOPFrozen[
        [VERSION_NAME_COLUMN, ITEM_COLUMN, LOCATION_COLUMN, SUB_LOCATION_COLUMN, SOP_FROZEN_LIST_FP_PERIOD_COLUMN,
         SOP_FROZEN_LIST_FRZ_STARTDATE_COLUMN, SOP_FROZEN_LIST_FRZ_ENDDATE_COLUMN, SOP_FROZEN_LIST_GROUP_ID_COLUMN,
         ]]
    print_df(df_equal_SOPFrozen, 'STEP4 by 2.2 ____ df_equal_SOPFrozen ..... equal merge final')


    #   2.2.2 not equla join
    df_not_equal_SOPFrozen = pd.merge(df_in_SOPFrozen1, df_buf_SopFrozenList, how='outer', indicator=True,
                                      left_on=[VERSION_NAME_COLUMN, SOP_FROZEN_FORM_SITE_COLUMN,
                                               SOP_FROZEN_TO_SITE_COLUMN, SOP_FROZEN_ITEM_COLUMN],
                                      right_on=[VERSION_NAME_COLUMN, LOCATION_COLUMN,SUB_LOCATION_COLUMN, ITEM_COLUMN])
    print_df(df_not_equal_SOPFrozen, 'STEP4 by 2.2 ____ df_not_equal_SOPFrozen ..... not equal merge')

    #       2.2.2.1 조건이 다른 데이터 추출
    df_not_equal_SOPFrozen = df_not_equal_SOPFrozen[df_not_equal_SOPFrozen['_merge'] != 'both']
    print_df(df_not_equal_SOPFrozen, 'STEP4 by 2.2 ____ df_not_equal_SOPFrozen ..... not equal(!=both) merge')

    #       2.2.2.2 컬럼설정
    df_not_equal_SOPFrozen[ITEM_COLUMN] = df_not_equal_SOPFrozen[SOP_FROZEN_ITEM_COLUMN]
    df_not_equal_SOPFrozen[LOCATION_COLUMN] = df_not_equal_SOPFrozen[SOP_FROZEN_FORM_SITE_COLUMN]
    df_not_equal_SOPFrozen[SUB_LOCATION_COLUMN] = df_not_equal_SOPFrozen[SOP_FROZEN_TO_SITE_COLUMN]
    df_not_equal_SOPFrozen[SOP_FROZEN_LIST_FP_PERIOD_COLUMN] = df_not_equal_SOPFrozen[SOP_FROZEN_FRZ_COLUMN]
    df_not_equal_SOPFrozen[SOP_FROZEN_LIST_FRZ_ENDDATE_COLUMN] = df_not_equal_SOPFrozen[SOP_FROZEN_FRZ_ENDDATE_COLUMN]
    df_not_equal_SOPFrozen[SOP_FROZEN_LIST_FRZ_STARTDATE_COLUMN] = df_not_equal_SOPFrozen[SOP_FROZEN_FRZ_STARTDATE_COLUMN]
    df_not_equal_SOPFrozen[SOP_FROZEN_LIST_GROUP_ID_COLUMN] = df_not_equal_SOPFrozen[GROUP_ID_COLUMN]

    #       2.2.2.2 필요컬럼 발췌
    df_not_equal_SOPFrozen = df_not_equal_SOPFrozen[
        [VERSION_NAME_COLUMN, ITEM_COLUMN, LOCATION_COLUMN, SUB_LOCATION_COLUMN, SOP_FROZEN_LIST_FP_PERIOD_COLUMN,
         SOP_FROZEN_LIST_FRZ_STARTDATE_COLUMN, SOP_FROZEN_LIST_FRZ_ENDDATE_COLUMN, SOP_FROZEN_LIST_GROUP_ID_COLUMN,
         ]]
    print_df(df_not_equal_SOPFrozen, 'STEP4 by 2.2 ____ df_not_equal_SOPFrozen ..... not equal merge final')

    # 2.3 사용된 df 삭제
    delete_dfs(df_in_SOPFrozen1, df_buf_SopFrozenList)

    # ====================> Step 2 (End)



    step(300, '=====> STEP 3(End) : Check memory usage & runtime')

    ################################################################################################################
    # STEP 4 : output data machining
    ################################################################################################################
    step(400, '=====> STEP 4(Start) : output data machining')

    df_SopFrozenList = pd.concat([df_equal_SOPFrozen, df_not_equal_SOPFrozen]).drop_duplicates()
    print_df(df_SopFrozenList, 'STEP4 by 4 ____ df_SopFrozenList ..... concat final')

    # 버전 처리
    df_SopFrozenList[VERSION_NAME_COLUMN] = paramOutVersion

    step(400, '=====> STEP 4(End) : Check memory usage & runtime')

    ################################################################################################################
    # STEP 5 : output table create
    ################################################################################################################
    step(500, '=====> STEP 5(Start) : Final output table create')

    df_out_SopFrozenList = df_SopFrozenList.copy()

    print_df(df_out_SopFrozenList, 'STEP 5 - Final output table create .....> df_out_SopFrozenList')
    row_count, col_count = df_out_SopFrozenList.shape
    note(f'=====> Final df_out_SopFrozenList rows : {row_count}, column : {col_count}')

    save_csv_file(df_out_SopFrozenList, 'df_out_SopFrozenList')

    step(500, '=====> STEP 5(End) : Check memory usage & runtime')

except Exception as ex:
    note(f'An exception occurred: {ex}')
    note(f'=====> try exception : {traceback.format_exc()}')
    logger.Error()

else:
    # 현재 메모리 사용량과 피크 메모리 사용량 체크
    current, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    # 실행 시간 계산 (초 단위 -> 분 단위로 변환)
    end_time = time.time()
    run_time_seconds = end_time - start_time
    run_time_minutes = run_time_seconds / 60

    note(f'=====> Current memory usage is {current / 10 ** 6}MB, Peak was {peak / 10 ** 6}MB, Execution time: {run_time_minutes:.4f} minutes')
    step(600, '===================== plugin Execution End =====================')

finally:
    logger.Finish()
