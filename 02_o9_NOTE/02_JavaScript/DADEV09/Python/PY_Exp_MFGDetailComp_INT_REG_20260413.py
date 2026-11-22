"""
* 프로그램명
    - PY_Exp_MFGDetailComp_INT_REG.py

* 내용
    -

* 변경이력
    - 2025.03.26 / Yuntaeun / Create
* Script Params
    - Param_OUT_VERSION : 기본값 : CWV_SP, 호출시에, 결과데이터를 Version Name을 별도로 지정하는데에 사용.

* Input Tables
    - EXP_PSI_SP_MGFDETAIL_INPUT :
        (
            Select (
                        FROM.[Item].[Item]
                        * FROM.[Location].[Location]
                        * FROM.[Time].[Week]
                        * FROM.[Documents].[Document Type]
                        * TO.[To Item].[To Item]
                        * TO.[To Location].[To Location]
                        * TO.[To Time].[To Week]
                        * TO.[Activity1].[Activity1]
                    ) on row
                    ,
                    (
                        {
                            Edge.[Bottom Up Pegging Output Graph].[BUP Producer to Consumer To Pegged]
                            , Measure.[Item Location Stage]@(FROM.[Item].[Item]
                            , FROM.[Location].[Location])
                        }
                    ) on column
                    where {
                                RelationshipType.[Bottom Up Pegging Output Graph]
                                , Version.[Version Name].[CWV_SP]
                            }
        ).filter(
                    Measure.[Item Location Stage] == "M_PSI"
                );
    - Week_Day
        Select (
                    [Version].[Version Name]
                    * &CurrentAndFuturePlanningWeeks
                    * [Time].[Day]
                ) on row
                ,
                (
                    {
                        Measure.[Assortment For Week to First Day]
                    }
                ) on column;
    - in_Version
    Select (
        [Version].[Version Name]
    ) on row
    , () on column
    include memberproperties {[Version].[Version Name], DisplayName};

* Output Tables
    - PSI_OUTPUT:
    # Exp_MFG_PSI_Detail :
        SELECT (
                        [Version].[Version Name]
                        * [Sequence].[Sequence]
                        * [Item].[Item]
                        * [Location].[Location]
                        * [Time].[Day]
                ) on row
                ,
                (
                    {
                        Measure.[Exp Mfg PSI Detail_To Site ID]
                        , Measure.[Exp Mfg PSI Detail_GBM]
                        , Measure.[Exp Mfg PSI Detail_BOH Qty]
                        , Measure.[Exp Mfg PSI Detail_Prod Qty]
                        , Measure.[Exp Mfg PSI Detail_Ship Qty]
                        , Measure.[Exp Mfg PSI Detail_EOH Qty]
                        , Measure.[Exp Mfg PSI Detail_Safety Stock Target]
                        , Measure.[Exp Mfg PSI Detail_Prod Dep]
                        , Measure.[Exp Mfg PSI Detail_Ship Dep]
                    }
                ) on column
    # Week_Day :
        Select (
                    [Version].[Version Name].CWV_SP
                    * &CurrentAndFuturePlanningWeeks
                    * [Time].[Day] ) on row
                    ,
                    (
                        {
                            Measure.[Assortment For Week to First Day]
                        }
                    ) on column;

* Flow Summary
    STEP1. Set1) --> 도착지 구분 없이 주별 Sum
        STEP 1-1. 'On Hand' - from.Time.Week에 합산 > [Exp Mfg PSI Detail_BOH Qty]
        STEP 1-2. 'On Hand'가 아닌 것은 해당 from.Time.Week에 합산 > [Exp Mfg PSI Detail_Prod Qty]
        STEP 1-3. 구분 없이 모든 수량을 to.Time.Week에 합산 > [Exp Mfg PSI Detail_Ship Qty]
        STEP 1-4. EOHQTY = BOHQTY + [Exp Mfg PSI Detail_Prod Qty] - [Exp Mfg PSI Detail_Ship Qty]
        STEP 1-5. BOHQTY(첫째 주) = On Hand 합
        STEP 1-6. BOHQTY(둘째 주 이후) = 이전 주(Bucket)의 EOHQTY
        STEP 1-7. [Exp Mfg PSI Detail_Ship Dep] = [Exp Mfg PSI Detail_Ship Qty]
        STEP 1-8. Time.[Day] = 해당 주차(Time.[Week])의 월요일 날자
        STEP 1-9. [Exp Mfg PSI Detail_Safety Stock Target] = ..
        STEP 1-10. Exp Mfg PSI Detail_GBM = "SHA"

    STEP2. Set2) --> 도착지별 구분하여 분류
        STEP2-1. [Exp Mfg PSI Detail_To Site ID]는 to.Activity1.Activity1(BOD)에서 첫째 '_'와 둘째 '_' 사이 값을 잘라 넣음
        STEP2-2. 'On Hand' - from.Time.Week에 도착지별로 분리 > [Exp Mfg PSI Detail_BOH Qty]
        STEP2-3. 'On Hand'가 아닌 것은 해당 from.Time.Week에 도착별로 분리 > [Exp Mfg PSI Detail_Prod Qty]
        STEP2-4. 구분 없이 모든 수량을 to.Time.Week에 도착별로 분리 > [Exp Mfg PSI Detail_Ship Qty]
        STEP2-5. EOHQTY = BOHQTY + [Exp Mfg PSI Detail_Prod Qty] - [Exp Mfg PSI Detail_Ship Qty]
        STEP2-6. BOHQTY(첫째 주) = On Hand 합
        STEP2-7. BOHQTY(둘째 주 이후) = 이전 주(Bucket)의 EOHQTY
        STEP2-8. [Exp Mfg PSI Detail_Prod Dep] = [Exp Mfg PSI Detail_Prod Qty]
        STEP2-9. Time.[Day] = 해당 주차(Time.[Week])의 월요일 날자
        STEP2-10. [Exp Mfg PSI Detail_Safety Stock Target] = ..
        STEP2-11. [Exp Mfg PSI Detail_GBM] = "SHA"

* Validation :
    존재하지 않으면 Raise Exception

* Execution :
    1. 기존 메저 데이터 삭제(nullify)
    Scope: ([Version].[Version Name].[CWV_SP]);
    Measure.[Exp Mfg PSI Detail_To Site ID]=null;
    Measure.[Exp Mfg PSI Detail_GBM]=null;
    Measure.[Exp Mfg PSI Detail_BOH Qty]=null;
    Measure.[Exp Mfg PSI Detail_Prod Qty]=null;
    Measure.[Exp Mfg PSI Detail_Ship Qty]=null;
    Measure.[Exp Mfg PSI Detail_EOH Qty]=null;
    Measure.[Exp Mfg PSI Detail_Safety Stock Target]=null;
    Measure.[Exp Mfg PSI Detail_Prod Dep]=null;
    Measure.[Exp Mfg PSI Detail_Ship Dep]=null;
    end scope;

    2. Plugin Call하여 신규 MG 생성
    EXEC plugin instance [PY_Exp_MFGDetailComp_REG]
        for measures {
                          Measure.[Exp Mfg PSI Detail_To Site ID]
                        , Measure.[Exp Mfg PSI Detail_GBM]
                        , Measure.[Exp Mfg PSI Detail_BOH Qty]
                        , Measure.[Exp Mfg PSI Detail_Prod Qty]
                        , Measure.[Exp Mfg PSI Detail_Ship Qty]
                        , Measure.[Exp Mfg PSI Detail_EOH Qty]
                        , Measure.[Exp Mfg PSI Detail_Safety Stock Target]
                        , Measure.[Exp Mfg PSI Detail_Prod Dep]
                        , Measure.[Exp Mfg PSI Detail_Ship Dep]
                        }
    using scope ([Version].[Version Name].[CWV_SP] * &CurrentAndFuturePlanningWeeks)
    using arguments {(ExecutionMode, "MediumWeight")
                  , (Param_OUT_VERSION, "CWV_SP")
                  , (MaxSliceTableCells, 200000000)
                  , (MaxConcurrency, 1 )
                  , (IncludeNullRows, False)
                  , ([Param.o9_sys_log_level], "DEBUG")
                  }
    ;
    3. OUT TABLE
    select (
            Version.[Version Name]
            * Item.[Item]
            * Location.[Location]
            * Time.[Day]
            * Sequence.[Sequence]
        ) on row
        ,
        (
            {
                Measure.[Exp Mfg PSI Detail_To Site ID]
                , Measure.[Exp Mfg PSI Detail_GBM]
                , Measure.[Exp Mfg PSI Detail_BOH Qty]
                , Measure.[Exp Mfg PSI Detail_Prod Qty]
                , Measure.[Exp Mfg PSI Detail_Ship Qty]
                , Measure.[Exp Mfg PSI Detail_EOH Qty]
                , Measure.[Exp Mfg PSI Detail_Safety Stock Target]
                , Measure.[Exp Mfg PSI Detail_Prod Dep]
                , Measure.[Exp Mfg PSI Detail_Ship Dep]
            }
        ) on column;

"""
import os.path
import pandas as pd
import numpy as np
import traceback
import datetime
import time
from NSCMCommon import NSCMCommon as common
import io
import boto3
import pyarrow as pa
import pyarrow.parquet as pq
from botocore.client import Config

########################################################################################################################
# Local 개발 시에 필요한 공통 변수 선언
########################################################################################################################
# o9에 저장된 instanceName
str_instance = "PY_Exp_MFGDetailComp_REG"
str_input_dir = "Input/EXP_MFG_PSI_DTL_REG"
str_output_dir = "Output/EXP_MFG_PSI_DTL_REG"
is_local = common.gfn_get_isLocal()
flag_exception = True

########################################################################################################################
# log 설정 : PROGRAM file_name
########################################################################################################################
logger = common.G_Logger(p_py_name=str_instance)
common.gfn_set_local_logfile()
LOG_LEVEL = common.G_log_level

########################################################################################################################
# S3 설정 :
########################################################################################################################
def get_s3_clients():
    s3_config = dict(
        service_name="s3",
        region_name=S3Region,
        endpoint_url=S3Endpoint,
        config=Config(s3={"addressing_style": "path"}, signature_version="s3v4"),
    )

    hub_s3 = boto3.client(
        **s3_config,
        aws_access_key_id=Hub_S3_ACCESS_KEY,
        aws_secret_access_key=Hub_S3_SECRET_KEY,
    )
    return hub_s3


def save_dataframe_to_s3(df, bucket: str, s3_path: str, hub_s3):
    if df is None or df.empty:
        print(f"저장할 데이터가 없습니다: {s3_path}")
        return

    table = pa.Table.from_pandas(df, preserve_index=False)
    buffer = io.BytesIO()
    pq.write_table(table, buffer)
    buffer.seek(0)
    hub_s3.put_object(Bucket=bucket, Key=s3_path, Body=buffer.getvalue())
    print(f"DataFrame이 S3에 저장되었습니다: s3://{bucket}/{s3_path}")


def fn_check_input_table(df_p_source: pd.DataFrame, str_p_source_name: str, str_p_cond: str) -> None:
    """
    Input Table을 체크한 결과를 로그 또는 Exception으로 표시한다.
    :param df_p_source: Input table
    :param str_p_source_name: Name of Input table
    :param str_p_cond: '0' - Exception, '1' - Warning Log
    :return: None
    """
    # Input Table 로그 출력
    logger.PrintDF(p_df=df_p_source, p_df_name=str_p_source_name, p_log_level=LOG_LEVEL.debug(), p_format=1)

    if df_p_source.empty:
        if str_p_cond == '0':
            # 테이블이 비어 있는 경우 raise Exception
            raise Exception(f'[Exception] Input table({str_p_source_name}) is empty.')
        else:
            # 테이블이 비어 있는 경우 Warning log
            logger.Note(p_note=f'Input table({str_p_source_name}) is empty.', p_log_level=LOG_LEVEL.warning())


def fn_set_bomqty(df_p_source: pd.DataFrame) -> pd.DataFrame:
    """
    'from.[Item].[Item]', 'from.[Location].[Location]', 'Exp Mfg PSI Detail_To Site ID'별 eoh qty계산된 값을
    다음주차에 boh로 넣는 함수
    :param df_p_source:
    :return: group by 별 row DataFrame
    """
    df_return = df_p_source.copy()
    eoh_qty = 0
    sequence = 0
    for i in np.arange(len(df_return)):
        eoh_qty = (
                    df_return.loc[df_return.index[i], 'Exp Mfg PSI Detail_BOH Qty'] +
                    df_return.loc[df_return.index[i], 'Exp Mfg PSI Detail_Prod Qty'] -
                    df_return.loc[df_return.index[i], 'Exp Mfg PSI Detail_Ship Qty']
        )
        df_return.loc[df_return.index[i], 'Exp Mfg PSI Detail_EOH Qty'] = eoh_qty

        if i == len(df_return)-1:
            break
        else:
            df_return.loc[df_return.index[i + 1], 'Exp Mfg PSI Detail_BOH Qty'] = eoh_qty

    return df_return


def get_week_month_day(sr_p_timeweek: int) -> datetime:
    """
    Time.[Day] = 해당 주차(Time.[Week])의 월요일 날자
    :param sr_p_timeweek: Time.Week컬럼 주차값
    :return: Time.Week컬럼 주차에 대한 월요일 날짜 %Y-%m-%d
    """
    yyyymm = sr_p_timeweek
    yyyymmstr = str(yyyymm)
    year = yyyymmstr[:4]
    week = int(yyyymmstr[4:])
    first_day_of_year = pd.to_datetime(f'{year}-01-01')
    first_day_of_week = first_day_of_year + pd.offsets.Week(week - 1)
    return first_day_of_week


def fn_set_header() -> pd.DataFrame:
    """
    MediumWeight로 실행 시 발생할 수 있는 Live Server에서의 오류를 방지하기 위해 Header만 있는 Output 테이블을 만든다.
    :return: DataFrame
    """
    df_return = pd.DataFrame(
        {
            'Version.[Version Name]': [], 'Item.[Item]': [], 'Location.[Location]': [],
            'Time.[Day]': [], 'Sequence.[Sequence]': [],
            'Exp Mfg PSI Detail_To Site ID': [], 'Exp Mfg PSI Detail_GBM': [],
            'Exp Mfg PSI Detail_BOH Qty': [], 'Exp Mfg PSI Detail_Prod Qty': [],
            'Exp Mfg PSI Detail_Ship Qty': [], 'Exp Mfg PSI Detail_EOH Qty': [],
            'Exp Mfg PSI Detail_Safety Stock Target': [], 'Exp Mfg PSI Detail_Prod Dep': [],
            'Exp Mfg PSI Detail_Ship Dep': []
        }
    )
    return df_return


if __name__ == '__main__':
    logger.debug(f'[START] {str_instance}')
    logger.Start()

    # Output 테이블 선언
    OUT_EXP_MFGDTL = pd.DataFrame()
    try:
        if is_local:
            # 로컬인 경우 Output 폴더를 정리한다.
            for file in os.scandir(str_output_dir):
                os.remove(file.path)

            # 로컬인 경우 파일을 읽어 입력 변수를 정의한다.
            Param_OUT_VERSION = 'CWV_SP'
            Param_Exception_Flag = ''
            Hub_S3_ACCESS_KEY = ''
            Hub_S3_SECRET_KEY = ''
            hub_BASE_PATH = ''
            hub_bucket = ''
            S3Region = ''
            S3Endpoint = ''
            EXP_MGFDETAIL_INPUT = pd.read_csv(str_input_dir + "/EXP_PSI_SP_MGFDETAIL_INPUT.csv", encoding="UTF8")
            Week_Day = pd.read_csv(str_input_dir + "/Week_Day.csv", encoding="UTF8")
            in_Version = pd.read_csv(str_input_dir + "/in_Version.csv", encoding="UTF8")

        # 입력 변수 확인
        if Param_OUT_VERSION is None or Param_OUT_VERSION.strip() == '':
            Param_OUT_VERSION = 'CWV_SP'

        if Param_Exception_Flag is None or Param_Exception_Flag.strip() == '':
            flag_exception = True
        elif Param_Exception_Flag == 'S':
            flag_exception = False

        logger.Note(p_note=f'Param_OUT_VERSION : {Param_OUT_VERSION}')
        # 입력 변수 확인용 로그
        logger.Note(p_note=f'Hub_S3_ACCESS_KEY : {Hub_S3_ACCESS_KEY}', p_log_level=LOG_LEVEL.debug())
        logger.Note(p_note=f'Hub_S3_SECRET_KEY : {Hub_S3_SECRET_KEY}', p_log_level=LOG_LEVEL.debug())
        logger.Note(p_note=f'hub_BASE_PATH : {hub_BASE_PATH}', p_log_level=LOG_LEVEL.debug())
        logger.Note(p_note=f'hub_bucket : {hub_bucket}', p_log_level=LOG_LEVEL.debug())
        logger.Note(p_note=f'S3Region : {S3Region}', p_log_level=LOG_LEVEL.debug())
        logger.Note(p_note=f'S3Endpoint : {S3Endpoint}', p_log_level=LOG_LEVEL.debug())

        if Hub_S3_ACCESS_KEY == 'F':
            raise Exception(f'[Exception] Hub_S3_ACCESS_KEY is "F"')
        if Hub_S3_SECRET_KEY == 'F':
            raise Exception(f'[Exception] Hub_S3_SECRET_KEY is "F"')
        if hub_BASE_PATH == 'F':
            raise Exception(f'[Exception] hub_BASE_PATH is "F"')
        if hub_bucket == 'F':
            raise Exception(f'[Exception] hub_bucket is "F"')
        if S3Region == 'F':
            raise Exception(f'[Exception] S3Region is "F"')
        if S3Endpoint == 'F':
            raise Exception(f'[Exception] S3Endpoint is "F"')

        # get_s3_clients 호출
        hub_s3 = get_s3_clients()

        # 입력 변수 확인용 로그
        logger.Note(p_note=f'Param_Exception_Flag : {Param_Exception_Flag}', p_log_level=LOG_LEVEL.debug())

        # 입력 테이블 점검 및 로그
        fn_check_input_table(EXP_MGFDETAIL_INPUT, 'EXP_MGFDETAIL_INPUT', '0')
        fn_check_input_table(Week_Day, 'Week_Day', '0')
        ################################################################################################################
        # ON HAND와 ON HAND가 아닌 데이타 선별
        ################################################################################################################
        DF_EXP_MGFDTL = EXP_MGFDETAIL_INPUT.copy()
        # Step Log
        logger.Step(p_step_no=101,
                    p_step_desc='from.[Location].[Location] == to.[To Item].[To Item] 선적지가 같은것만'
                    )
        # from.[Location].[Location] == to.[To Item].[To Item] 선적지가 같은것만
        DF_EXP_MGFDTL = DF_EXP_MGFDTL.query(
            '`from.[Location].[Location]` == `to.[To Location].[To Location]`'
        )
        # to.[Activity1].[Activity1]컬럼에서 목적지 '_' 잘라 리스트 index 1값을 가져와 ToSiteID컬럼을 만든다.
        DF_EXP_MGFDTL['Exp Mfg PSI Detail_To Site ID'] = DF_EXP_MGFDTL[
            'to.[Activity1].[Activity1]'
        ].str.split('_').str[1].fillna(DF_EXP_MGFDTL['to.[Activity1].[Activity1]'])
        # output Log
        logger.PrintDF(p_df=DF_EXP_MGFDTL, p_df_name='DF_EXP_MGFDTL', p_log_level=LOG_LEVEL.debug(), p_format=1)
        # 로컬 Debugging 시 csv 파일 출력
        if is_local and not DF_EXP_MGFDTL.empty:
            DF_EXP_MGFDTL.to_csv(str_output_dir + '/DF_EXP_MGFDTL.csv', encoding='UTF8')

        # Step Log
        logger.Step(p_step_no=102,
                    p_step_desc='DF_EXP_MGFDTL 테이블에서 from.[Documents].[Document Type]가 On Hand인 row만 가져오고'
                                ' 필요컬럼만 SETTING하고'
                                ' Bottom Up Pegging Output Graph.[BUP Producer to Consumer To Pegged]를'
                                ' Exp Mfg PSI Detail_BOH Qty RENAME'
                    )
        # DF_EXP_MGFDTL 테이블에서 from.[Documents].[Document Type]가 On Hand인 row만 가져온다.
        DF_ON_HAND_EXP_MGFDT = DF_EXP_MGFDTL.query(
            '`from.[Documents].[Document Type]` == "On Hand"'
        )[
            ['from.[Item].[Item]', 'from.[Location].[Location]', 'from.[Time].[Week]', 'Exp Mfg PSI Detail_To Site ID',
             'Bottom Up Pegging Output Graph.[BUP Producer to Consumer To Pegged]'
            ]
        ]
        # ON_HAND_EXP_MGFDTL_BY_DEST rename
        DF_ON_HAND_EXP_MGFDT.rename(columns={
            'Bottom Up Pegging Output Graph.[BUP Producer to Consumer To Pegged]':
                'Exp Mfg PSI Detail_BOH Qty'
        }, inplace=True)
        # output Log
        logger.PrintDF(p_df=DF_ON_HAND_EXP_MGFDT, p_df_name='DF_ON_HAND_EXP_MGFDT', p_log_level=LOG_LEVEL.debug(),
                       p_format=1)
        # 로컬 Debugging 시 csv 파일 출력
        if is_local and not DF_ON_HAND_EXP_MGFDT.empty:
            DF_ON_HAND_EXP_MGFDT.to_csv(str_output_dir + '/DF_ON_HAND_EXP_MGFDT.csv', encoding='UTF8')

        # Step Log
        logger.Step(p_step_no=103,
                    p_step_desc='DF_EXP_MGFDTL 테이블에서 from.[Documents].[Document Type]가 ON HAND가 아닌 row만 '
                                ' 가져오고 필요컬럼만 SETTING하고'
                                ' Bottom Up Pegging Output Graph.[BUP Producer to Consumer To Pegged]를'
                                ' Exp Mfg PSI Detail_Prod Qty RENAME'
                    )
        # DF_EXP_MGFDTL 테이블에서 from.[Documents].[Document Type]가 ON HAND가 아닌 row만 가져온다.
        DF_NOT_ON_HAND_EXP_MGFDT = DF_EXP_MGFDTL.query(
            '`from.[Documents].[Document Type]` != "On Hand"'
        )[
            ['from.[Item].[Item]', 'from.[Location].[Location]', 'from.[Time].[Week]', 'Exp Mfg PSI Detail_To Site ID',
             'Bottom Up Pegging Output Graph.[BUP Producer to Consumer To Pegged]'
            ]
        ]
        # DF_NOT_ON_HAND_EXP_MGFDT rename
        DF_NOT_ON_HAND_EXP_MGFDT.rename(columns={
            'Bottom Up Pegging Output Graph.[BUP Producer to Consumer To Pegged]':
                'Exp Mfg PSI Detail_Prod Qty'
        }, inplace=True)
        # output Log
        logger.PrintDF(p_df=DF_NOT_ON_HAND_EXP_MGFDT, p_df_name='DF_NOT_ON_HAND_EXP_MGFDT',
                       p_log_level=LOG_LEVEL.debug(), p_format=1)
        # 로컬 Debugging 시 csv 파일 출력
        if is_local and not DF_NOT_ON_HAND_EXP_MGFDT.empty:
            DF_NOT_ON_HAND_EXP_MGFDT.to_csv(str_output_dir + '/DF_NOT_ON_HAND_EXP_MGFDT.csv', encoding='UTF8')

        ################################################################################################################
        # STEP1. Set1) --> 도착지 구분 없이 주별 Sum
        #         STEP 1-1. 'On Hand' - from.Time.Week에 합산 > [Exp Mfg PSI Detail_BOH Qty]
        #         STEP 1-2. 'On Hand'가 아닌 것은 해당 from.Time.Week에 합산 > [Exp Mfg PSI Detail_Prod Qty]
        #         STEP 1-3. 구분 없이 모든 수량을 to.Time.Week에 합산 > [Exp Mfg PSI Detail_Ship Qty]
        #         STEP 1-4. EOHQTY = BOHQTY + [Exp Mfg PSI Detail_Prod Qty] - [Exp Mfg PSI Detail_Ship Qty]
        #         STEP 1-5. BOHQTY(첫째 주) = On Hand 합
        #         STEP 1-6. BOHQTY(둘째 주 이후) = 이전 주(Bucket)의 EOHQTY
        #         STEP 1-7. [Exp Mfg PSI Detail_Ship Dep] = [Exp Mfg PSI Detail_Ship Qty]
        #         STEP 1-8. Time.[Day] = 해당 주차(Time.[Week])의 월요일 날자
        #         STEP 1-9. [Exp Mfg PSI Detail_Safety Stock Target] = ..
        #         STEP 1-10. Exp Mfg PSI Detail_GBM = "SHA"
        ################################################################################################################
        # Step Log
        logger.Step(p_step_no=100,
                    p_step_desc='STEP1 도착지 구분 없이 주별 Exp Mfg PSI Detail_BOH Qty,'
                                ' Exp Mfg PSI Detail_Prod Qty DataFrame')
        # ON_HAND_EXP_MGFDTL_BY_DEST 도착지 구분없이 group by
        DF_ON_HAND_EXP_MGFDT_STP1_GRP = DF_ON_HAND_EXP_MGFDT.groupby(
            [
                'from.[Item].[Item]', 'from.[Location].[Location]', 'from.[Time].[Week]'
            ]
        ).agg(
            {
                'Exp Mfg PSI Detail_BOH Qty': 'sum'
            }
        ).reset_index()
        # DF_NOT_ON_HAND_EXP_MGFDT 도착지 구분없이 group by
        DF_NOT_ON_HAND_EXP_MGFDT_STP1_GRP = DF_NOT_ON_HAND_EXP_MGFDT.groupby(
            [
                'from.[Item].[Item]', 'from.[Location].[Location]', 'from.[Time].[Week]'
            ]
        ).agg(
            {
                'Exp Mfg PSI Detail_Prod Qty': 'sum'
            }
        ).reset_index()
        # merge columns
        list_merge_col = [
            'from.[Item].[Item]', 'from.[Location].[Location]', 'from.[Time].[Week]'
        ]
        # outer join
        EXP_MGFDTL_from_WEEK_SUM_STP1 = pd.merge(
            DF_ON_HAND_EXP_MGFDT_STP1_GRP, DF_NOT_ON_HAND_EXP_MGFDT_STP1_GRP,
            how='outer', on=list_merge_col
        )
        # from.[Time].[Week]를 향후 merge를 위해 [Time].[Week] rename
        EXP_MGFDTL_from_WEEK_SUM_STP1.rename(columns={
            'from.[Time].[Week]': '[Time].[Week]',
        }, inplace=True)
        # output Log
        logger.PrintDF(p_df=EXP_MGFDTL_from_WEEK_SUM_STP1, p_df_name='EXP_MGFDTL_from_WEEK_SUM_STP1',
                       p_log_level=LOG_LEVEL.debug(), p_format=1)
        # 로컬 Debugging 시 csv 파일 출력
        if is_local and not EXP_MGFDTL_from_WEEK_SUM_STP1.empty:
            EXP_MGFDTL_from_WEEK_SUM_STP1.to_csv(str_output_dir + '/EXP_MGFDTL_from_WEEK_SUM_STP1.csv',
                                                 encoding='UTF8')

        # Step Log
        logger.Step(p_step_no=101,
                    p_step_desc='STEP1 도착지 구분 없이 주별 Exp Mfg PSI Detail_Ship Qty DataFrame')
        # to.[To Time].[To Week] group by하여 주차별 Exp Mfg PSI Detail_Ship Qty 구한다.
        EXP_MGFDTL_to_WEEK_SUM_STP1 = DF_EXP_MGFDTL.groupby(
            [
                'from.[Item].[Item]',
                'from.[Location].[Location]',
                'to.[To Time].[To Week]',  # 주의
            ]
        ).agg(
            {
                'Bottom Up Pegging Output Graph.[BUP Producer to Consumer To Pegged]': 'sum'
            }
        ).reset_index()
        # Exp Mfg PSI Detail_Ship Qty 컬럼명 변경
        EXP_MGFDTL_to_WEEK_SUM_STP1.rename(columns={
            'to.[To Time].[To Week]': '[Time].[Week]',
            'Bottom Up Pegging Output Graph.[BUP Producer to Consumer To Pegged]':
                'Exp Mfg PSI Detail_Ship Qty'
        }, inplace=True)
        # output Log
        logger.PrintDF(p_df=EXP_MGFDTL_to_WEEK_SUM_STP1, p_df_name='EXP_MGFDTL_to_WEEK_SUM_STP1',
                       p_log_level=LOG_LEVEL.debug(), p_format=1)
        # 로컬 Debugging 시 csv 파일 출력
        if is_local and not EXP_MGFDTL_to_WEEK_SUM_STP1.empty:
            EXP_MGFDTL_to_WEEK_SUM_STP1.to_csv(str_output_dir + '/EXP_MGFDTL_BY_DEST_to_WEEK_SUM_STP1.csv',
                                               encoding='UTF8')

        # Step Log
        logger.Step(p_step_no=102,
                    p_step_desc='STEP1 도착지 구분 없이 주별 Exp Mfg PSI Detail_BOH Qty,'
                                ' EXP MFG PSI Detail Production, Exp Mfg PSI Detail_Ship Qty '
                                ' 를 위해 merge, fillna, sorting DataFrame')
        # merge columns
        list_merge_col = [
            'from.[Item].[Item]', 'from.[Location].[Location]', '[Time].[Week]'
        ]
        EXP_MGFDTL_WITHOUT_DEST_WEEK_SUM = pd.merge(
            left=EXP_MGFDTL_from_WEEK_SUM_STP1,
            right=EXP_MGFDTL_to_WEEK_SUM_STP1,
            how='outer',
            on=list_merge_col
        )
        # EXP_MGFDTL_BY_DEST_WEEK_SUM 아래 컬럼 nan 0처리
        list_columns_fillna = ['Exp Mfg PSI Detail_BOH Qty', 'Exp Mfg PSI Detail_Prod Qty',
                               'Exp Mfg PSI Detail_Ship Qty']
        EXP_MGFDTL_WITHOUT_DEST_WEEK_SUM[list_columns_fillna] = (
            EXP_MGFDTL_WITHOUT_DEST_WEEK_SUM[list_columns_fillna].replace(r'^\s*$', np.nan, regex=True).fillna(0)
        )
        # sort 컬럼 list
        list_sort_col = [
            'from.[Item].[Item]', 'from.[Location].[Location]', '[Time].[Week]'
        ]
        # item, location, week로 오름차순 정렬
        EXP_MGFDTL_WITHOUT_DEST_WEEK_SUM = EXP_MGFDTL_WITHOUT_DEST_WEEK_SUM.sort_values(axis=0, by=list_sort_col,
                                                                                        ascending=True)
        # EXP_MGFDTL_WITHOUT_DEST_WEEK_SUM 필요 컬럼 생성
        # item, location별 BOH Qty, Production Qty, Shipping Qty, EOH QTY, Sequence를 위한 함수 호출
        EXP_MGFDTL_WITHOUT_DEST_WEEK_SUM = EXP_MGFDTL_WITHOUT_DEST_WEEK_SUM.groupby(
            [
                'from.[Item].[Item]', 'from.[Location].[Location]'
            ]
        ).apply(
            fn_set_bomqty  # 해당 함수
        ).reset_index(drop=True)
        # 해당 주차(Time.[Week])의 월요일 날짜를 위한 함수 호출
        # EXP_MGFDTL_WITHOUT_DEST_WEEK_SUM['Time.[Day]'] = EXP_MGFDTL_WITHOUT_DEST_WEEK_SUM['[Time].[Week]'].apply(
        #     lambda x: get_week_month_day(x)  # 해당 함수
        # )
        # Exp Mfg PSI Detail_To Site ID
        EXP_MGFDTL_WITHOUT_DEST_WEEK_SUM['Exp Mfg PSI Detail_To Site ID'] = ''
        # Exp Mfg PSI Detail_GBM = "SHA"
        EXP_MGFDTL_WITHOUT_DEST_WEEK_SUM['Exp Mfg PSI Detail_GBM'] = 'SHA'
        # [Exp Mfg PSI Detail_Safety Stock Target] = ..
        EXP_MGFDTL_WITHOUT_DEST_WEEK_SUM['Exp Mfg PSI Detail_Safety Stock Target'] = ''
        # Exp Mfg PSI Detail_Prod Dep
        EXP_MGFDTL_WITHOUT_DEST_WEEK_SUM['Exp Mfg PSI Detail_Prod Dep'] = ''
        # [Exp Mfg PSI Detail_Ship Dep] = [Exp Mfg PSI Detail_Ship Qty]
        EXP_MGFDTL_WITHOUT_DEST_WEEK_SUM['Exp Mfg PSI Detail_Ship Dep'] = EXP_MGFDTL_WITHOUT_DEST_WEEK_SUM[
            'Exp Mfg PSI Detail_Ship Qty']
        # Version.[Version Name]
        EXP_MGFDTL_WITHOUT_DEST_WEEK_SUM['Version.[Version Name]'] = Param_OUT_VERSION
        # from 컬럼 rename
        EXP_MGFDTL_WITHOUT_DEST_WEEK_SUM.rename(
            columns={
                'from.[Item].[Item]': 'Item.[Item]',
                'from.[Location].[Location]': 'Location.[Location]',
                '[Time].[Week]': 'Time.[Week]'
            }, inplace=True
        )
        # 컬럼 순서변경
        EXP_MGFDTL_WITHOUT_DEST_WEEK_SUM = EXP_MGFDTL_WITHOUT_DEST_WEEK_SUM[
            [
                'Version.[Version Name]', 'Item.[Item]', 'Location.[Location]', 'Exp Mfg PSI Detail_To Site ID',
                'Time.[Week]', 'Exp Mfg PSI Detail_GBM',
                'Exp Mfg PSI Detail_BOH Qty', 'Exp Mfg PSI Detail_Prod Qty', 'Exp Mfg PSI Detail_Ship Qty',
                'Exp Mfg PSI Detail_EOH Qty', 'Exp Mfg PSI Detail_Safety Stock Target',
                'Exp Mfg PSI Detail_Prod Dep', 'Exp Mfg PSI Detail_Ship Dep'
            ]
        ]
        # output Log
        logger.PrintDF(p_df=EXP_MGFDTL_WITHOUT_DEST_WEEK_SUM, p_df_name='EXP_MGFDTL_WITHOUT_DEST_WEEK_SUM',
                       p_log_level=LOG_LEVEL.debug(), p_format=1)
        # 로컬 Debugging 시 csv 파일 출력
        if is_local and not EXP_MGFDTL_WITHOUT_DEST_WEEK_SUM.empty:
            EXP_MGFDTL_WITHOUT_DEST_WEEK_SUM.to_csv(str_output_dir + '/EXP_MGFDTL_WITHOUT_DEST_WEEK_SUM.csv',
                                                    encoding='UTF8')
        ################################################################################################################
        # STEP2. Set2) --> 도착지별 구분하여 분류
        # STEP2-1. [Exp Mfg PSI Detail_To Site ID]는 to.Activity1.Activity1(BOD)에서 첫째 '_'와 둘째 '_' 사이 값을 잘라 넣음
        # STEP2-2. 'On Hand' - from.Time.Week에 도착지별로 분리 > [Exp Mfg PSI Detail_BOH Qty]
        # STEP2-3. 'On Hand'가 아닌 것은 해당 from.Time.Week에 도착별로 분리 > [Exp Mfg PSI Detail_Prod Qty]
        # STEP2-4. 구분 없이 모든 수량을 to.Time.Week에 도착별로 분리 > [Exp Mfg PSI Detail_Ship Qty]
        # STEP2-5. EOHQTY = BOHQTY + [Exp Mfg PSI Detail_Prod Qty] - [Exp Mfg PSI Detail_Ship Qty]
        # STEP2-6. BOHQTY(첫째 주) = On Hand 합
        # STEP2-7. BOHQTY(둘째 주 이후) = 이전 주(Bucket)의 EOHQTY
        # STEP2-8. [Exp Mfg PSI Detail_Prod Dep] = [Exp Mfg PSI Detail_Prod Qty]
        # STEP2-9. Time.[Day] = 해당 주차(Time.[Week])의 월요일 날자
        # STEP2-10. [Exp Mfg PSI Detail_Safety Stock Target] = ..
        # STEP2-11. [Exp Mfg PSI Detail_GBM] = "SHA"
        ################################################################################################################
        # Step Log
        logger.Step(p_step_no=200,
                    p_step_desc='STEP2 도착지별 구분하여 분류 주별 Exp Mfg PSI Detail_BOH Qty,'
                                ' Exp Mfg PSI Detail_Prod Qty DataFrame')
        # ON HAND 도착지별 구분하여 분류 group by
        DF_ON_HAND_EXP_MGFDT_STP2_GRP = DF_ON_HAND_EXP_MGFDT.groupby(
            [
                'from.[Item].[Item]', 'from.[Location].[Location]', 'from.[Time].[Week]',
                'Exp Mfg PSI Detail_To Site ID'  # 주의
            ]
        ).agg(
            {
                'Exp Mfg PSI Detail_BOH Qty': 'sum'
            }
        ).reset_index()
        # NOT ON HAND 도착지별 구분하여 분류 group by
        DF_NOT_ON_HAND_EXP_MGFDT_STP2_GRP = DF_NOT_ON_HAND_EXP_MGFDT.groupby(
            [
                'from.[Item].[Item]', 'from.[Location].[Location]', 'from.[Time].[Week]',
                'Exp Mfg PSI Detail_To Site ID'  # 주의
            ]
        ).agg(
            {
                'Exp Mfg PSI Detail_Prod Qty': 'sum'
            }
        ).reset_index()
        # merge columns
        list_merge_col = [
            'from.[Item].[Item]', 'from.[Location].[Location]', 'from.[Time].[Week]', 'Exp Mfg PSI Detail_To Site ID'
        ]
        # outer join
        EXP_MGFDTL_from_WEEK_SUM_STP2 = pd.merge(
            DF_ON_HAND_EXP_MGFDT_STP2_GRP, DF_NOT_ON_HAND_EXP_MGFDT_STP2_GRP,
            how='outer', on=list_merge_col
        )
        # from.[Time].[Week]를 향후 merge를 위해 [Time].[Week] rename
        EXP_MGFDTL_from_WEEK_SUM_STP2.rename(columns={
            'from.[Time].[Week]': '[Time].[Week]',
        }, inplace=True)
        # output Log
        logger.PrintDF(p_df=EXP_MGFDTL_from_WEEK_SUM_STP2, p_df_name='EXP_MGFDTL_from_WEEK_SUM_STP2',
                       p_log_level=LOG_LEVEL.debug(), p_format=1)
        # 로컬 Debugging 시 csv 파일 출력
        if is_local and not EXP_MGFDTL_from_WEEK_SUM_STP2.empty:
            EXP_MGFDTL_from_WEEK_SUM_STP2.to_csv(str_output_dir + '/EXP_MGFDTL_from_WEEK_SUM_STP2.csv',
                                                 encoding='UTF8')

        # Step Log
        logger.Step(p_step_no=201,
                    p_step_desc='STEP2 도착지 구분하여 분류 주별 Exp Mfg PSI Detail_Ship Qty DataFrame')
        # to.[To Time].[To Week] group by하여 주차별 Exp Mfg PSI Detail_Ship Qty 구한다.
        EXP_MGFDTL_to_WEEK_SUM_STP2 = DF_EXP_MGFDTL.groupby(
            [
                'from.[Item].[Item]',
                'from.[Location].[Location]',
                'to.[To Time].[To Week]',  # 주의
                'Exp Mfg PSI Detail_To Site ID'
            ]
        ).agg(
            {
                'Bottom Up Pegging Output Graph.[BUP Producer to Consumer To Pegged]': 'sum'
            }
        ).reset_index()
        # Exp Mfg PSI Detail_Ship Qty 컬럼명 변경
        EXP_MGFDTL_to_WEEK_SUM_STP2.rename(columns={
            'to.[To Time].[To Week]': '[Time].[Week]',
            'Bottom Up Pegging Output Graph.[BUP Producer to Consumer To Pegged]': 'Exp Mfg PSI Detail_Ship Qty'
        }, inplace=True)
        # output Log
        logger.PrintDF(p_df=EXP_MGFDTL_to_WEEK_SUM_STP2, p_df_name='EXP_MGFDTL_to_WEEK_SUM_STP2',
                       p_log_level=LOG_LEVEL.debug(), p_format=1)
        # 로컬 Debugging 시 csv 파일 출력
        if is_local and not EXP_MGFDTL_to_WEEK_SUM_STP2.empty:
            EXP_MGFDTL_to_WEEK_SUM_STP2.to_csv(str_output_dir + '/EXP_MGFDTL_to_WEEK_SUM_STP2.csv',
                                               encoding='UTF8')

        # Step Log
        logger.Step(p_step_no=202,
                    p_step_desc='STEP2 도착지 구분 없이 주별 Exp Mfg PSI Detail_BOH Qty,'
                                ' EXP MFG PSI Detail Production, Exp Mfg PSI Detail_Ship Qty '
                                ' 를 위해 merge, fillna, sorting DataFrame')
        # merge columns
        list_merge_col = [
            'from.[Item].[Item]', 'from.[Location].[Location]', '[Time].[Week]', 'Exp Mfg PSI Detail_To Site ID'
        ]
        EXP_MGFDTL_BY_DEST_WEEK_SUM = pd.merge(
            left=EXP_MGFDTL_from_WEEK_SUM_STP2,
            right=EXP_MGFDTL_to_WEEK_SUM_STP2,
            how='outer',
            on=list_merge_col
        )
        # EXP_MGFDTL_BY_DEST_WEEK_SUM 아래 컬럼 nan 0처리
        list_columns_fillna = ['Exp Mfg PSI Detail_BOH Qty', 'Exp Mfg PSI Detail_Prod Qty',
                               'Exp Mfg PSI Detail_Ship Qty']
        EXP_MGFDTL_BY_DEST_WEEK_SUM[list_columns_fillna] = (
            EXP_MGFDTL_BY_DEST_WEEK_SUM[list_columns_fillna].replace(r'^\s*$', np.nan, regex=True).fillna(0)
        )
        # sort 컬럼 list
        list_sort_col = [
            'from.[Item].[Item]', 'from.[Location].[Location]', 'Exp Mfg PSI Detail_To Site ID', '[Time].[Week]'
        ]
        # item, location, week로 오름차순 정렬
        EXP_MGFDTL_BY_DEST_WEEK_SUM = EXP_MGFDTL_BY_DEST_WEEK_SUM.sort_values(axis=0, by=list_sort_col,
                                                                              ascending=True)
        # output Log
        logger.PrintDF(p_df=EXP_MGFDTL_BY_DEST_WEEK_SUM, p_df_name='EXP_MGFDTL_BY_DEST_WEEK_SUM',
                       p_log_level=LOG_LEVEL.debug(), p_format=1)
        # 로컬 Debugging 시 csv 파일 출력
        if is_local and not EXP_MGFDTL_BY_DEST_WEEK_SUM.empty:
            EXP_MGFDTL_BY_DEST_WEEK_SUM.to_csv(str_output_dir + '/EXP_MGFDTL_BY_DEST_WEEK_SUM.csv', encoding='UTF8')

        # Step Log
        logger.Step(p_step_no=203,
                    p_step_desc='STEP2 from.[Item].[Item], from.[Location].[Location], Exp Mfg PSI Detail_To Site ID별 '
                                ' eoh qty계산된 값을 다음주차에 boh로 넣는 함수 & (Time.[Week])의 월요일 날짜 함수호출'
                                ' 및 그밖에 컬럼 구성')
        # item, location별 BOH Qty, Production Qty, Shipping Qty, EOH QTY, Sequence를 위한 함수 호출
        EXP_MGFDTL_BY_DEST_WEEK_SUM = EXP_MGFDTL_BY_DEST_WEEK_SUM.groupby(
            [
                'from.[Item].[Item]', 'from.[Location].[Location]', 'Exp Mfg PSI Detail_To Site ID'
            ]
        ).apply(
            fn_set_bomqty  # 해당 함수
        ).reset_index(drop=True)
        # 해당 주차(Time.[Week])의 월요일 날짜를 위한 함수 호출
        # EXP_MGFDTL_BY_DEST_WEEK_SUM['Time.[Day]'] = EXP_MGFDTL_BY_DEST_WEEK_SUM['[Time].[Week]'].apply(
        #     lambda x: get_week_month_day(x)  # 해당 함수
        # )
        # Exp Mfg PSI Detail_Safety Stock Target
        EXP_MGFDTL_BY_DEST_WEEK_SUM['Exp Mfg PSI Detail_Safety Stock Target'] = ''
        # Exp Mfg PSI Detail_Prod Dep
        EXP_MGFDTL_BY_DEST_WEEK_SUM['Exp Mfg PSI Detail_Prod Dep'] = EXP_MGFDTL_BY_DEST_WEEK_SUM[
            'Exp Mfg PSI Detail_Prod Qty']
        # [Exp Mfg PSI Detail_Safety Stock Target] = ..
        EXP_MGFDTL_BY_DEST_WEEK_SUM['Exp Mfg PSI Detail_Safety Stock Target'] = ''
        # Exp Mfg PSI Detail_GBM = "SHA"
        EXP_MGFDTL_BY_DEST_WEEK_SUM['Exp Mfg PSI Detail_GBM'] = 'SHA'
        # Version.[Version Name]
        EXP_MGFDTL_BY_DEST_WEEK_SUM['Version.[Version Name]'] = Param_OUT_VERSION
        # Exp Mfg PSI Detail_Ship Dep
        EXP_MGFDTL_BY_DEST_WEEK_SUM['Exp Mfg PSI Detail_Ship Dep'] = ''
        # from 컬럼 rename
        EXP_MGFDTL_BY_DEST_WEEK_SUM.rename(
            columns={
                'from.[Item].[Item]': 'Item.[Item]',
                'from.[Location].[Location]': 'Location.[Location]',
                '[Time].[Week]': 'Time.[Week]'
            }, inplace=True
        )
        # 컬럼 순서변경
        EXP_MGFDTL_BY_DEST_WEEK_SUM = EXP_MGFDTL_BY_DEST_WEEK_SUM[
            [
                'Version.[Version Name]', 'Item.[Item]', 'Location.[Location]', 'Exp Mfg PSI Detail_To Site ID',
                'Time.[Week]', 'Exp Mfg PSI Detail_GBM',
                'Exp Mfg PSI Detail_BOH Qty', 'Exp Mfg PSI Detail_Prod Qty',
                'Exp Mfg PSI Detail_Ship Qty',
                'Exp Mfg PSI Detail_EOH Qty', 'Exp Mfg PSI Detail_Safety Stock Target',
                'Exp Mfg PSI Detail_Prod Dep', 'Exp Mfg PSI Detail_Ship Dep'
            ]
        ]
        # output Log
        logger.PrintDF(p_df=EXP_MGFDTL_BY_DEST_WEEK_SUM, p_df_name='EXP_MGFDTL_BY_DEST_WEEK_SUM',
                       p_log_level=LOG_LEVEL.debug(), p_format=1)
        # 로컬 Debugging 시 csv 파일 출력
        if is_local and not EXP_MGFDTL_BY_DEST_WEEK_SUM.empty:
            EXP_MGFDTL_BY_DEST_WEEK_SUM.to_csv(str_output_dir + '/EXP_MGFDTL_BY_DEST_WEEK_SUM.csv',
                                               encoding='UTF8')

        ################################################################################################################
        # STEP1, STEP2 CONCAT이후 Sequence생성, 컬럼순서변경, sort'
        ################################################################################################################
        # Step Log
        logger.Step(p_step_no=300,
                    p_step_desc='STEP1, STEP2 CONCAT이후 Sequence생성, 컬럼순서변경, sort')
        # STEP1, STEP2 concat
        OUT_EXP_MFGDTL = pd.concat([EXP_MGFDTL_WITHOUT_DEST_WEEK_SUM, EXP_MGFDTL_BY_DEST_WEEK_SUM],
                                   ignore_index=True)
        #
        Week_Day.drop(
            columns=[
                "Version.[Version Name]",
            ],
            inplace=True,
        )
        OUT_EXP_MFGDTL = pd.merge(OUT_EXP_MFGDTL, Week_Day, on='Time.[Week]', how='left')
        # 'Sequence.[Sequence] 컬럼
        OUT_EXP_MFGDTL['Sequence.[Sequence]'] = OUT_EXP_MFGDTL.groupby(
            ['Version.[Version Name]', 'Item.[Item]', 'Location.[Location]']
        ).cumcount() + 1
        # 컬럼 순서변경
        OUT_EXP_MFGDTL = OUT_EXP_MFGDTL[
            [
                'Version.[Version Name]', 'Item.[Item]', 'Location.[Location]', 'Time.[Day]', 'Sequence.[Sequence]',
                'Exp Mfg PSI Detail_To Site ID', 'Exp Mfg PSI Detail_GBM',
                'Exp Mfg PSI Detail_BOH Qty', 'Exp Mfg PSI Detail_Prod Qty',
                'Exp Mfg PSI Detail_Ship Qty',
                'Exp Mfg PSI Detail_EOH Qty', 'Exp Mfg PSI Detail_Safety Stock Target',
                'Exp Mfg PSI Detail_Prod Dep', 'Exp Mfg PSI Detail_Ship Dep'
            ]
        ]
        # OUT_MFG_DTL sort
        OUT_EXP_MFGDTL = OUT_EXP_MFGDTL.sort_values(
            axis=0, by=['Item.[Item]', 'Location.[Location]', 'Sequence.[Sequence]'],
            ascending=True
        ).reset_index(drop=True)
        # o9 데이타 타입과 맞게 형변환
        OUT_EXP_MFGDTL['Exp Mfg PSI Detail_Safety Stock Target'] = np.where(
            OUT_EXP_MFGDTL['Exp Mfg PSI Detail_Safety Stock Target'] == ''
            , 0
            , OUT_EXP_MFGDTL['Exp Mfg PSI Detail_Safety Stock Target']
        ).astype('float64')
        OUT_EXP_MFGDTL['Exp Mfg PSI Detail_Prod Dep'] = np.where(
            OUT_EXP_MFGDTL['Exp Mfg PSI Detail_Prod Dep'] == ''
            , 0
            , OUT_EXP_MFGDTL['Exp Mfg PSI Detail_Prod Dep']
        ).astype('float64')
        OUT_EXP_MFGDTL['Exp Mfg PSI Detail_Ship Dep'] = np.where(
            OUT_EXP_MFGDTL['Exp Mfg PSI Detail_Ship Dep'] == ''
            , 0
            , OUT_EXP_MFGDTL['Exp Mfg PSI Detail_Ship Dep']
        ).astype('float64')
        # Version Display
        Param_DisplayName = in_Version['Version.[Version Name$DisplayName]'].values[0]
        OUT_EXP_MFGDTL['Version.[DisplayName]'] = Param_DisplayName
        # output Log
        logger.PrintDF(p_df=OUT_EXP_MFGDTL, p_df_name='OUT_EXP_MFGDTL',
                       p_log_level=LOG_LEVEL.debug(), p_format=1)
        if is_local and not OUT_EXP_MFGDTL.empty:
            OUT_EXP_MFGDTL.to_csv(str_output_dir + "/OUT_EXP_MFGDTL.csv", encoding="UTF8")
        # S3저장하는 부분
        save_dataframe_to_s3(
            OUT_EXP_MFGDTL,
            hub_bucket,
            f"{hub_BASE_PATH}/MG_EXP_MFGPSIDTL_COMP/OUT_EXP_MFGDTL.parquet",
            hub_s3,
        )

    except Exception as e:
        trace_msg = traceback.format_exc()
        logger.Note(p_note=trace_msg, p_log_level=LOG_LEVEL.debug())
        logger.Error()
        if flag_exception:
            out_Check = None
            raise Exception(e)
        else:
            # out_Check
            out_Check = pd.DataFrame(
                {
                    'Version.[Version Name]': [Param_OUT_VERSION]
                    , 'Sequence.[Sequence]': [9]
                    , 'EXP Finish Flag': [True]
                }
            )
            logger.info(f'{str_instance} exit - {time.strftime("%Y-%m-%d - %H:%M:%S")}')

    else:
        # out_Check
        out_Check = pd.DataFrame(
            {
                'Version.[Version Name]': [Param_OUT_VERSION]
                , 'Sequence.[Sequence]': [9]
                , 'EXP Finish Flag': [True]
            }
        )
        logger.Finish()

    finally:
        logger.info(f'{str_instance} {time.strftime("%Y-%m-%d - %H:%M:%S")}::: Finish :::')