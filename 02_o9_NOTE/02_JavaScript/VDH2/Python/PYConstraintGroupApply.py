"""

* 프로그램명
    - PYConstraintGroupApply

* 내용
    - Production Constraint : Apply 액션버튼 수행
    - 상단 입력 row기준 Apply > 하단 report Week별 data분기

* Input
    - df_in_week : select ([Time].[Week] * Time.[Day] );
    - df_in_constGroup : Constraint Group
    - df_in_constGroupDetailW_lockInfo : Constraint Group Detail W (Qty Lock)

* Flow Summary
    Step1. Constraint Group Detail(Measure Group) 생성
    Step2. Constraint Group Detail W (Measure Group) 생성

* Input
    - in_ = pd.read_csv(' .csv')

* 변경이력
    - 2024.06.03 / syif1380.lee / Create

* Script Parameter
    - param_outVersion : 기본값 :

* Input Table
  - df_in_week : select ([Time].[Week]);

  - df_in_constGroup :
    Select ([Version].[Version Name] * [Sequence].[Sequence] * [Group].[Group ID] ) on row,
            ({Measure.[Const Grp_Build Ahead],
              Measure.[Const Grp_Definition],
              Measure.[Const Grp_Desc],
              Measure.[Const Grp_Enddate],
              Measure.[Const Grp_From Site],
              Measure.[Const Grp_Inch],
              Measure.[Const Grp_Item],
              Measure.[Const Grp_Mkt Name],
              Measure.[Const Grp_Need Check],
              Measure.[Const Grp_Prod Qty],
              Measure.[Const Grp_Product Group],
              Measure.[Const Grp_Project],
              Measure.[Const Grp_Reason],
              Measure.[Const Grp_Refer Time],
              Measure.[Const Grp_Startdate],
              Measure.[Const Grp_To Site],
              Measure.[Const Grp_Update Time],
              Measure.[Const Grp_Updated By],
              Measure.[Const Grp_Year]}) on column;

  - df_in_constGroupDetailW_lockInfo : UI 에서 Lock 이 있는 경우 Qty를 배정하지 않는다.
      - Measure.[Const Grp Detail W_Qty.Lock] 같이 Measure 의 속성을 input select 할때는 파이썬 실행 구문에서 "LightWeight" => "MediumWeight" 로 사용해야 함.
      Select ([Version].[Version Name] * [Group].[Group ID] * [Time].[Week] ) on row,
            ({Measure.[Const Grp Detail W_Lock Flag]
            , Measure.[Const Grp Detail W_Qty.Lock]
            }) on column;

            -- LightWeight 로 구성
        Select ([Version].[Version Name] * [Group].[Group ID] * [Time].[Week] ) on row,  ({
            // Measure.[Const Grp Detail W_Qty],
            Measure.[Const Grp Detail W_Lock Flag],
        (if (~isnull(Measure.[Const Grp Detail W_Qty.Lock]) && Measure.[Const Grp Detail W_Qty.Lock] ) then "Y"  else if (~isnull(Measure.[Const Grp Detail W_Qty.Lock]) && ~Measure.[Const Grp Detail W_Qty.Lock] ) then "N" else "N")  as transient.[Model Store Path]}) on column;


* Output Table :
   - df_out_constGroupDetail :
   - df_out_constGroupDetail_W :

* 테스트 스크립트
    EXEC plugin instance [PYConstraintGroupApply] for measures {[Constraint Group Detail} using scope ( Version.[Version Name].[CurrentWorkingView] ) using arguments {(ExecutionMode, "LightWeight"), (MaxSliceTableCells, 200000000), (MaxConcurrency, 1 )};

    * 실행되는지 테스트 필요 {fbVersion}}
    EXEC plugin instance [PYConstraintGroupApply] for measures {[Constraint Group Detail} using scope ( &CWV ) using arguments {(ExecutionMode, "LightWeight"), (MaxSliceTableCells, 200000000), (MaxConcurrency, 1 )};

    * /* APPLY 호출 (PYConstraintGroupApply) */
    EXEC plugin instance [PYConstraintGroupApply] for measures {[Const Grp Detail_From Site]} using scope ( Version.[Version Name]"{{fbVersion}}" * [Group].[Group ID].filter(#.[Name]=="{{fbGroupId}}")) using arguments {(ExecutionMode, "LightWeight"), (MaxSliceTableCells, 200000000), (MaxConcurrency, 1 )};
    EXEC plugin instance [PYConstraintGroupApply] for measures {[Const Grp Detail_From Site]} using scope ( Version.[Version Name].[CurrentWorkingView] * [Group].[Group ID].filter(#.[Name]=="G1")) using arguments {(ExecutionMode, "LightWeight"), (MaxSliceTableCells, 200000000), (MaxConcurrency, 1 )};

    /* APPLY 호출 (PYConstraintGroupApply) */
    // group id 여러개 실행 (delete 버튼시 여러건 삭제) {{#filter fbGroupId}}  => .filter(#.[Name] in{"Group1","Group2","Group3"}
    - Measure.[Const Grp Detail W_Qty.Lock] 같이 Measure 의 속성을 input select 할때는 파이썬 실행 구문에서 "LightWeight" => "MediumWeight" 로 사용해야 함.
    EXEC plugin instance [PYConstraintGroupApply] for measures {[Const Grp Detail_From Site]} using scope ( Version.[Version Name].[CurrentWorkingView] * [Group].[Group ID]{{#filter fbGroupId}}) using arguments {(ExecutionMode, "LightWeight"), (MaxSliceTableCells, 200000000), (MaxConcurrency, 1 )};


"""
import pandas as pd
import numpy as np
import logging
import datetime
import platform
import os
import tabulate
import traceback
import time


################################# 나중에 라이브러리로 빼야함 ##############################################
# 로거 세팅
logging.basicConfig(level=logging.DEBUG)
comm_logger = logging.getLogger("o9_logger")
startTime = datetime.datetime.now()

# Log 포맷 함수
def getLogger(_pluginName, _log_level=logging.DEBUG, _log_fileName="log"):
    global pluginName
    pluginName = _pluginName

    # 로컬이면 파일로 저장
    if platform.system() == 'Windows':
        comm_logger.setLevel(_log_level)
        # 일반 핸들러, 포매터 세팅
        formatter = logging.Formatter("%(asctime)s %(levelname)s : %(message)s")
        handler = logging.FileHandler(os.path.dirname(__file__) + "\\" + _log_fileName + ".log", encoding="UTF8")
        handler.setLevel(_log_level)
        handler.setFormatter(formatter)
        # 각 핸들러를 로거에 추가
        comm_logger.addHandler(handler)

    return comm_logger

def logPrefix():
    elapsed = datetime.datetime.now() - startTime
    return f"{pluginName} : {elapsed} sec : "

def log(_func, _msg, _dfName=""):
    if isinstance(_msg, pd.DataFrame):
        if platform.system() == 'Windows':
            head_row = 3
            if "__Fix" in _dfName:   # df name 에 '__Fix' 이름이 포함될 경우 head row 20로 정함
                head_row = 20
                # print('%%%%%%%%%%%%%%%   head_row' + str(head_row) + ' :: _dfName : ' + _dfName)

            _func(logPrefix() + "*" * 30 + f" {_dfName} : {len(_msg.columns)} Column, {str(len(_msg.index))} Rows " + "*" * 30 +
                f"\n" + tabulate.tabulate(_msg.head(head_row), headers="keys", tablefmt="fancy_grid"))
            _func(_msg.dtypes)
        else:
            _func(logPrefix() + "*"*30 + f" {_dfName} : {len(_msg.columns)} Column, {str(len(_msg.index))} Rows " + "*"*30)
            _func(logPrefix() + "Columns ==> " + "\t".join(_msg.columns))

            maxCnt = 3 if len(_msg.index) > 3 else len(_msg.index)
            for i in range(0,maxCnt):
                # _func(logPrefix() + str(i) + " ==> " + _msg.to_string(header=False, index=False, index_names=False).split('\n')[i])
                _func(logPrefix() + str(i) + " ==> " + ', '.join(_msg.iloc[i].astype(str)))
            # 컬럼 및 Type 출력
            colInfo = "Column Info ==> "
            for i in _msg.dtypes.keys():
                colInfo = colInfo + f"{i} ({_msg.dtypes[i]})\t*\t"
            _func(logPrefix() + colInfo)
    else:
        _func(logPrefix() + _msg)

def isLocal():
    if platform.system() == 'Windows':
        return True
    else:
        return False

def saveDf(_df, _csvName):
    if isLocal():
        _df.to_csv(os.path.dirname(__file__) + "\\" + f"{programName}_out_{_csvName}.csv", index=False)

def convert_date_string(date_string):
    # 24-Mar-24 포맷형식을 yyyy-mm-dd 형식으로 리턴
    return datetime.strptime(date_string, '%d-%b-%y').strftime('%Y-%m-%d')
    # return datetime.strptime(pd.to_datetime(date_string, format='%d-%b-%y'), '%d-%b-%y').strftime('%Y-%m-%d')
######################################### 서버 반영시 주석 처리 ########################################
# Version Name 세팅
# param_outVersion = "CWV_MP"
######################################################################################################
programName = "PYConstraintGroupApply"
logger = getLogger(programName)

log(logger.info, 'plugin Execution Start')

# 변수 선언
versionName = 'Version.[Version Name]'

# 데이터 파일 읽기
if isLocal():
    # df_in_constGroup = pd.read_csv(os.path.dirname(__file__) + "\\" + "df_in_constGroup.csv", encoding="UTF-8") # scope로 필터링된 데이타 Group ID 1개,seq n개
    # df_in_constGroup = pd.read_csv(os.path.dirname(__file__) + "\\" + "df_in_constGroup_PC_00002.csv", encoding="UTF-8")  # PC_00002 Data ( 테스트용 )
    # df_in_constGroup = pd.read_csv(os.path.dirname(__file__) + "\\" + "df_in_constGroup_2cnt.csv", encoding="UTF-8")  # PC_00001, PC_00002 Data ( 테스트용 )
    df_in_constGroup = pd.read_csv(os.path.dirname(__file__) + "\\" + "df_in_constGroupAll.csv", encoding="UTF-8") # All Data ( 테스트용 )
    df_in_week = pd.read_csv(os.path.dirname(__file__) + "\\" + "df_in_week.csv", encoding="UTF-8")
    df_in_constGroupDetailW_lockInfo = pd.read_csv(os.path.dirname(__file__) + "\\" + "df_in_constGroupDetailW_lockInfo.csv", encoding="UTF-8")

tm_StartMain = time.time()

try:
    if df_in_constGroup.empty:
        raise Exception("df_in_constGroup No Data")
    if df_in_week.empty:
        raise Exception("df_in_week No Data")
    if df_in_constGroupDetailW_lockInfo.empty:
        raise Exception("df_in_week No Data")
    log(logger.info, '==-> input Table ------------------------------------------------------------')
    log(logger.info, df_in_constGroup, _dfName="df_in_constGroup")
    log(logger.info, df_in_week, _dfName="df_in_week")
    log(logger.info, df_in_constGroupDetailW_lockInfo, _dfName="df_in_constGroupDetailW_lockInfo")

    # -------------------------------------------------------------------------------------------------------------#
    # STEP 1 :  Constraint Group Detail : Measure Group 을 생성
    #           - Constraint Group : Measure Group 을 가져와 Start/End Date 에 값이 있는것만 Filtering
    #           - Group ID 의 첫번째 행 기준으로 Distinct
    # ------------------------------------------------------------------------------------------------------------#
    # start/end Date 컬럼을 object 로 변경
    df_in_constGroup['Const Grp_Startdate'] = df_in_constGroup['Const Grp_Startdate'].astype(object)
    df_in_constGroup['Const Grp_Enddate'] = df_in_constGroup['Const Grp_Enddate'].astype(object)

    # start/end Date 컬럼이 null 이 아니고 공백이 아닌지를 체크하는 로직
    mask = ((df_in_constGroup['Const Grp_Startdate'].notnull()) & (df_in_constGroup['Const Grp_Startdate'].astype(str).str.strip() != '') &
            (df_in_constGroup['Const Grp_Enddate'].notnull()) & (df_in_constGroup['Const Grp_Enddate'].astype(str).str.strip() != ''))

    # 체크한 데이터만 남기기
    filtered_df = df_in_constGroup[mask].copy()
    log(logger.info, filtered_df, _dfName="filtered_df__1")

    # start/end Date 컬럼을 int 로 변경할 수 있는 경우 int로 변경
    filtered_df['Const Grp_Startdate'] = pd.to_numeric(filtered_df['Const Grp_Startdate'], errors='coerce')
    filtered_df['Const Grp_Enddate'] = pd.to_numeric(filtered_df['Const Grp_Enddate'], errors='coerce')

    # <NA> 값 필터링 ( string 형태의 문자가 있을 경우 )
    filtered_df = filtered_df[filtered_df['Const Grp_Startdate'].notnull()]
    filtered_df = filtered_df[filtered_df['Const Grp_Enddate'].notnull()]

    # int로 변경한 후 다시 str로 변경 : str 로 바로 변경시 202401 이 Float 으로 인식해서 202401.0 으로 변환됨, 소숫점자리 제거하기 위해 int 형변환
    # input data (202401.0) => int로 변환 (202401) => str로 변환 (202401)
    filtered_df['Const Grp_Startdate'] = filtered_df['Const Grp_Startdate'].astype(int).astype(str)
    filtered_df['Const Grp_Enddate'] = filtered_df['Const Grp_Enddate'].astype(int).astype(str)
    log(logger.info, filtered_df, _dfName="filtered_df__2")

    df_in_constGroup_copy = filtered_df.copy()

    log(logger.info, df_in_constGroup_copy, _dfName="df_in_constGroup_copy")
    # saveDf(df_in_constGroup_copy, 'df_in_constGroup_copy')

    # 중복행 제거
    df_out_constGroupDetail = df_in_constGroup_copy.drop_duplicates(subset=['Group.[Group ID]', 'Version.[Version Name]'], keep='first', inplace=False).copy()

    # 컬럼명 재정의
    df_out_constGroupDetail.rename(
        columns={'Const Grp_Desc': 'Const Grp Detail_Desc', 'Const Grp_From Site': 'Const Grp Detail_From Site', 'Const Grp_Item': 'Const Grp Detail_Item',
                 'Const Grp_Product Group': 'Const Grp Detail_Product Group', 'Const Grp_To Site' : 'Const Grp Detail_To Site'},
        inplace=True)

    # output : df_out_constGroupDetail 필요 컬럼 정의
    df_out_constGroupDetail = df_out_constGroupDetail[['Group.[Group ID]', 'Version.[Version Name]', 'Const Grp Detail_Desc', 'Const Grp Detail_From Site',
                                                       'Const Grp Detail_Item', 'Const Grp Detail_Product Group', 'Const Grp Detail_To Site'
                                                       ]]
    log(logger.info, df_out_constGroupDetail, _dfName="df_out_constGroupDetail")
    saveDf(df_out_constGroupDetail, 'df_out_constGroupDetail')

    # -------------------------------------------------------------------------------------------------------------#
    # STEP 2 :  Constraint Group Detail W (Measure Group) 생성
    #           - Group ID 별 주차를 만든다. (Constraint Group Detail(Measure Group)과 Time.[Week] 를 merge
    #           - Start/End Date 볌위의 Time.[Week] Filtering
    #           - Constraint Group Detail W 의 Model Store Path(Const Grp Detail W_Qty.Lock) 속성 컬럼을 가져와 N(False) 인 주차의 Qty 만 Filtering
    # ------------------------------------------------------------------------------------------------------------#
    # 주차 문자열로 형 변환
    df_in_week['Time.[Week]'] = df_in_week['Time.[Week]'].astype(object).astype(str)

    # main df 와 week df key를 만들어 merge 한다.
    df_merge = pd.merge(df_in_constGroup_copy.assign(temp_key=1), df_in_week.assign(temp_key=1), on='temp_key').drop('temp_key', axis=1)

    # start, end date 의 주차만큼 Time.Week 범위를 만든다.
    df_mergeQuery = df_merge.loc[(df_merge['Const Grp_Startdate'] <= df_merge['Time.[Week]']) & (df_merge['Const Grp_Enddate'] >= df_merge['Time.[Week]'])]
    log(logger.info, df_mergeQuery, _dfName="df_mergeQuery")

    df_Detail_W = df_mergeQuery.copy()

    # 컬럼명 재정의 (Const Qty => Detail W_Qty 로 변경)
    df_Detail_W.rename(columns={'Const Grp_Prod Qty': 'Const Grp Detail W_Qty'}, inplace=True)
    # log(logger.info, df_out_constGroupDetail_W, _dfName="df_out_constGroupDetail_W")

    # output : df_out_constGroupDetail_W 필요 컬럼 정의
    # df_Detail_W['Const Grp Detail W_Lock Flag'] = False
    df_Detail_W = df_Detail_W[['Group.[Group ID]', 'Version.[Version Name]', 'Time.[Week]', 'Const Grp Detail W_Qty']]

    log(logger.info, df_Detail_W, _dfName="df_Detail_W")
    saveDf(df_Detail_W, 'df_Detail_W')

    # 비교하기 위한 형변환
    df_in_constGroupDetailW_lockInfo['Time.[Week]'] = df_in_constGroupDetailW_lockInfo['Time.[Week]'].astype(object).astype(str)
    saveDf(df_in_constGroupDetailW_lockInfo, 'df_in_constGroupDetailW_lockInfo_형변환')

    # Detail_W 와 lock 정보를 merge
    df_mergeW = df_Detail_W.merge(df_in_constGroupDetailW_lockInfo, how='left', on=['Group.[Group ID]','Version.[Version Name]','Time.[Week]'])

    # NaN 이나 '' 일때 astype(bool) 로 변환시 True로 변환되어. Nan 일때 False 로 변환후 bool 로 변환해야 함.
    # df_mergeW['W_Qty_Lock'] = df_mergeW['Const Grp Detail W_Qty.Lock']
    # df_mergeW['W_Qty_Lock'] = df_mergeW['W_Qty_Lock'].fillna(False)
    # df_mergeW['W_Qty_Lock'] = df_mergeW['W_Qty_Lock'].astype(bool)

    df_mergeW['W_Qty_Lock'] = df_mergeW['Model Store Path'].astype(str)

    saveDf(df_mergeW, 'df_mergeW')

    # Lock = True 는 제외하고 Data 구성한다.
    # df_mergeWFilter =  df_mergeW.loc[(df_mergeW['W_Qty_Lock'] != True)]
    df_mergeWFilter = df_mergeW.loc[(df_mergeW['W_Qty_Lock'] == 'N')]
    saveDf(df_mergeWFilter, 'df_mergeWFilter')

    df_out_constGroupDetail_W = df_mergeWFilter.copy()

    df_out_constGroupDetail_W['Const Grp Detail W_Lock Flag'] = False
    df_out_constGroupDetail_W = df_out_constGroupDetail_W[['Group.[Group ID]', 'Version.[Version Name]', 'Time.[Week]', 'Const Grp Detail W_Lock Flag', 'Const Grp Detail W_Qty']]

    log(logger.info, df_out_constGroupDetail_W, _dfName="df_out_constGroupDetail_W")
    saveDf(df_out_constGroupDetail_W, 'df_out_constGroupDetail_W')

    # 데이터 파일 저장
    if isLocal():
        log(logger.info, '3. csv save')
        df_out_constGroupDetail.to_csv(os.path.dirname(__file__) + "\\" + f"{programName}_detail_out.csv", index=False)
        df_out_constGroupDetail_W.to_csv(os.path.dirname(__file__) + "\\" + f"{programName}_detail_W_out.csv", index=False)
except Exception as e:
    log(logger.error, traceback.format_exc())
    #raise Exception(e)
finally:
    tm_EndMain = time.time()
    log(logger.info, f'END : Total time is {tm_EndMain - tm_StartMain:5f} sec.')
    log(logger.info, 'plugin Execution End')
