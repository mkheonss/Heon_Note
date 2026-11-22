"""
############### Input ###############
// Where_Used : Not Used - 2025.03.13
Select (FROM.[Activity2].[Activity2] * FROM.[Location].[Location] * FROM.[Activity1].[Activity1] * FROM.[Item].[Item]
     * FROM.[Activity3].[Activity3] * TO.[Item].[Item] * TO.[Activity3].[Activity3] * TO.[Activity1].[Activity1]
     * TO.[Location].[Location] * TO.[Activity2].[Activity2]) on row
     , ({Edge.[013.006W Where Used Network Item SCS].[W Upstream Network Item Levels]}) on column
 where {RelationshipType.[013.006W Where Used Network Item SCS], Version.[Version Name]
     , Edge.[W Upstream Network Item Levels]==1}
;

// df :
Select (FROM.[Activity1].[Activity1] * FROM.[Activity2].[Activity Type2] * FROM.[Activity2].[Activity2] * FROM.[Activity3].[Activity3] 
     * FROM.[Item].[Item Stage].Filter(#.Name in {"SET","LCM","OPEN_CELL"}).relatedmembers([Item]) 
     * FROM.[Location].[Location] * FROM.[Time].[Week]
     * FROM.[Documents].[OrderlineID] * TO.[Activity1].[Activity1] * TO.[Activity2].[Activity Type2]
     * TO.[Activity2].[Activity2] * TO.[Activity3].[Activity3] * TO.[Demand].[DemandID] * TO.[Demand Type].[Demand Type]
     * TO.[Documents].[OrderlineID] * TO.[To Time].[To Week] * TO.[To Item].[To Item] * TO.[To Location].[To Location]
     * TO.[Item].[Item] 
     * TO.[Location].[Location Country].filter(#.Name in {"EUROPE"}).relatedmembers([Location])
     * TO.[Sales Domain].[Customer Group] * TO.[Time].[Week]) on row,
   (
    {
       Edge.[SOP Bottom Up Pegging Output Graph].[SOP BUP Consumer to Producer From Pegged]
     , Edge.[SOP Bottom Up Pegging Output Graph].[SOP BUP Producer to Consumer From Pegged]
    }
   *{
      Measure.[W Infinite Material Node]@(FROM.[Item].[Item],FROM.[Location].[Location])
    }
   ) on column
 where {RelationshipType.[SOP Bottom Up Pegging Output Graph], Version.[Version Name]}
;

// Activity_LeadTime :
Select ([Version].[Version Name] * [Activity1].[Activity1] * [Activity2].[Activity2] * [Activity3].[Activity3]) on row
     , ({Measure.[W Activity Lead Time]}) on column
;

// SalesStd2 :
select ([Sales Domain].[Sales Std2] * [Sales Domain].[Customer Group])
;

// MapOriginalDemandID :
Select ([Demand].[DemandID]) on row
     , ({Measure.[Map Original Demand ID]}) on column where {[Version].[Version Name]}
;

// MapOriginalOrderlineID :
Select ([Documents].[OrderlineID] * [Documents].[Document Type]) on row
     , ({Measure.[Map Original Orderline ID]}) on column
 where {[Version].[Version Name]}
;

// Week_Day :
Select ([Time].[Week]* [Time].[Day]) on row
     , ({Measure.[Assortment For Week to First Day]}) on column
 where {[Version].[Version Name]}
;

// MaterialConsumption
Select ([Version].[Version Name] * [Item].[Item Stage].Filter(#.Name in {"SET","LCM","OPEN_CELL"}).relatedmembers([Item]) *[Location].[Location] *
        [Activity1].[Activity1] * [Activity2].[Activity2] * [Activity3].[Activity3] ) on row, 
({Measure.[W Material Consumption Association]}) on column;

//MateralProduction
Select ([Version].[Version Name] * [Item].[Item Stage].Filter(#.Name in {"SET","LCM","OPEN_CELL"}).relatedmembers([Item]) * [Location].[Location]   * 
        [Activity1].[Activity1] * [Activity2].[Activity2] * [Activity3].[Activity3]  ) on row, 
({Measure.[W Material Production Association]}) on column ;


############### Exec ###############
# // 20min
exec plugin instance PluginforSOP BUP for measures {Measure.[Exp MPI_QTY]}
using scope ([Version].[Version Name])
using arguments {(DriverMemory,"2g")
              , ("IncludeNullRows", "False")
              , (ExecutionMode, "MediumWeight")
              ,([FailedExecutionCount], 1)
              ,([FailedExecutionPercent], 0.0)
              , ([ThrowExceptionOnFailure], true)
              , ([DateFormat], "d")
              , (MaxSliceTableCells,900000000)}
;
############### Output ###############
// DistPlan
Select ([Version].[Version Name].[EXP] * [Item].[Item] * [Location].[Location] * [Sequence].[Sequence]) on row
     , ({Measure.[Exp Dist Plan All_BODNAME] as Transient.BODNAME
     , Measure.[Exp Dist Plan All_DISTRIBUTIONORDERID] as Transient.DISTRIBUTIONORDERID
     , Measure.[Exp Dist Plan All_GBM] as Transient.GBM
     , Measure.[Exp Dist Plan All_Item] as Transient.Item
     , Measure.[Exp Dist Plan All_PLANNEDDELIVERYDATE] as Transient.PLANNEDDELIVERYDATE
     , Measure.[Exp Dist Plan All_PLANNEDSHIPMENTDATE] as Transient.PLANNEDSHIPMENTDATE
     , Measure.[Exp Dist Plan All_QTYPLANNED] as Transient.QTYPLANNED
     , Measure.[Exp Dist Plan All_RELEASEDPLAN] as Transient.RELEASEDPLAN
     , Measure.[Exp Dist Plan All_SALESID] as Transient.SALESID
     , Measure.[Exp Dist Plan All_TOSITEID] as Transient.TOSITEID}) on column
;

// DistPlan_SELL
Select ([Version].[Version Name].[EXP] * [Item].[Item] * [Location].[Location] * [Sequence].[Sequence]) on row
     , ({Measure.[Exp Dist Plan All_BODNAME] as Transient.BODNAME
     , Measure.[Exp Dist Plan All_DISTRIBUTIONORDERID] as Transient.DISTRIBUTIONORDERID
     , Measure.[Exp Dist Plan All_GBM] as Transient.GBM
     , Measure.[Exp Dist Plan All_Item] as Transient.Item
     , Measure.[Exp Dist Plan All_PLANNEDDELIVERYDATE] as Transient.PLANNEDDELIVERYDATE
     , Measure.[Exp Dist Plan All_PLANNEDSHIPMENTDATE] as Transient.PLANNEDSHIPMENTDATE
     , Measure.[Exp Dist Plan All_QTYPLANNED] as Transient.QTYPLANNED
     , Measure.[Exp Dist Plan All_RELEASEDPLAN] as Transient.RELEASEDPLAN
     , Measure.[Exp Dist Plan All_SALESID] as Transient.SALESID
     , Measure.[Exp Dist Plan All_TOSITEID] as Transient.TOSITEID}) on column
 where {~isnull(Measure.[Exp Dist Plan All_SALESID])}
;

// MPI
Select ([Version].[Version Name].[EXP] * [Item].[Item] * [Location].[Location] * [Sequence].[Sequence]) on row
     , ({Measure.[Exp MPI_CONSLOTNUMBER] as Transient.CONSLOTNUMBER
     , Measure.[Exp MPI_CONSROUTINGID] as Transient.CONSROUTINGID
     , Measure.[Exp MPI_CONSWORKORDERNUMBER] as Transient.CONSWORKORDERNUMBER
     , Measure.[Exp MPI_DEMANDSTARTDATE] as Transient.DEMANDSTARTDATE
     , Measure.[Exp MPI_GBM] as Transient.GBM
     , Measure.[Exp MPI_ORDERID] as Transient.ORDERID
     , Measure.[Exp MPI_PLANNEDCONSENDDATE] as Transient.PLANNEDCONSENDDATE
     , Measure.[Exp MPI_PLANNEDCONSSTARTDATE] as Transient.PLANNEDCONSSTARTDATE
     , Measure.[Exp MPI_PLANNEDPRODENDDATE] as Transient.PLANNEDPRODENDDATE
     , Measure.[Exp MPI_PLANNEDPRODSTARTDATE] as Transient.PLANNEDPRODSTARTDATE
     , Measure.[Exp MPI_PRODLOTNUMBER] as Transient.PRODLOTNUMBER
     , Measure.[Exp MPI_PRODROUTINGID] as Transient.PRODROUTINGID
     , Measure.[Exp MPI_PRODWORKORDERNUMBER] as Transient.PRODWORKORDERNUMBER
     , Measure.[Exp MPI_QTY] as Transient.QTY
     , Measure.[Exp MPI_SALESID] as Transient.SALESID
     , Measure.[Exp MPI_SALESLEVEL] as Transient.SALESLEVEL
     , Measure.[Exp MPI_SALESNAME] as Transient.SALESNAME
     , Measure.[Exp MPI_TOITEM] as Transient.TOITEM
     , Measure.[Exp MPI_TOSITEID] as Transient.TOSITEID}) on column
;

// SUPSTATUS
Select ([Version].[Version Name].[EXP] * [Sequence].[Sequence]) on row
     , ({Measure.[Exp Supply Status_GBM] as Transient.GBM
     , Measure.[Exp Supply Status_ROUTINGID] as Transient.ROUTINGID
     , Measure.[Exp Supply Status_STATUS] as Transient.STATUS
     , Measure.[Exp Supply Status_WORKORDERNUMBER] as Transient.WORKORDERNUMBER}) on column
;

############### Comments for Plugin Run Start from Here ###############
### After importing all the necessary libraries and input dataframes for the plugin,
    the plugin runs in the following steps --> ###
# Step 1: The Input Dataframes go through a process of Pre-Processing
          and Mapping the Where Used Graph to get the levels according to Activities
# Step 2: The Calculations begin for MPI Report by generating the data in the columns
          : ConsRoutingID, ProdRoutingID, ConsStartDate, ConsEndDate, ProdStartDate and ProdEndDate
# Step 3: The next columns that are generated are ConsWorkOrderNumber, ProdWorkOrderNumber and PeggingIDs
# Step 4: The cases where Inventory Demand exist in the SOP Bottom Up Peggings are handled
          and columns are renamed to the required names
# Step 5: The Calculations begin for Supplier Status Report by generating the columns
          : GBM, RoutingID, Status and WorkOrderNumber
# Step 6: The Calculations begin for Distribution Report by generating the columns
          : BODName, DistributionOrderID, GBM, All_Item, PlannedDeliveryDate, PlannedShipment Date, QtyPlanned,
            ReleasedPlan, SalesID, ToSiteID
# Step 7: The data in columns which contains date format as YYYYWW in MPI
          and Distribution Reports are changed to YYYY-MM-DD date format and this is the Monday of the Week
### The Plugin gets finished and Data is parsed into the Live Server ###
############### Comments for Plugin Run End Here ###############


"""

# Importing Libraries
import datetime
from o9_common_utils.O9DataLake import O9DataLake
import logging
from datetime import datetime,timedelta
import numpy as np
import pandas as pd
import time

pd.options.display.max_rows = 100
pd.options.display.max_columns = 150
pd.options.display.max_colwidth = 100
pd.set_option("display.width", 1000)
pd.options.display.precision = 3

# Get the o9_logger and storing it in a variable
logger = logging.getLogger('o9_logger')

logger.warn("@@@@@@@@@@@@@@@ PluginforSOP BUP01(Europe) execution Started @@@@@@@@@@@@@@@")

#Where_Used = O9DataLake.get("Where_Used")

df = O9DataLake.get("df")
Activity_LeadTime = O9DataLake.get("Activity_LeadTime")
SalesStd2 = O9DataLake.get("SalesStd2")
MapOriginalDemandID = O9DataLake.get("MapOriginalDemandID")
MapOriginalOrderlineID = O9DataLake.get("MapOriginalOrderlineID")
Week_Day = O9DataLake.get("Week_Day")

MaterialConsumption = O9DataLake.get("MaterialConsumption")
MaterialProduction = O9DataLake.get("MaterialProduction")

PlanConfig = O9DataLake.get("PlanConfig")

MPI_TYPE = "01"
Min_Seq = 0 

# 메모리사용 확인 함수
def memory_usage(message: str = 'info'):
    import psutil
    p = psutil.Process()
    rss = p.memory_info().rss / 2 ** 20  # byte to MB
    msg = f'{message} memory usage {rss: 10.5f} MB'
    return msg, rss

def fn_initialize_df(df_p_source: pd.DataFrame) -> pd.DataFrame:
    list_where_from_location_eq_to_to_location = (
            df_p_source['from.[Location].[Location]'] == df_p_source['to.[To Location].[To Location]'])
    list_where_from_item_eq_to_to_item = df_p_source['from.[Item].[Item]'] == df_p_source['to.[To Item].[To Item]']
    list_where_p_tp_c_more_then_one = (
            df_p_source['SOP Bottom Up Pegging Output Graph.[SOP BUP Producer to Consumer From Pegged]'] > 0)
    list_where_first = (list_where_from_location_eq_to_to_location & list_where_from_item_eq_to_to_item &
                        list_where_p_tp_c_more_then_one)

    list_where_from_location_neq_to_to_location = (
            df_p_source['from.[Location].[Location]'] != df_p_source['to.[To Location].[To Location]'])
    list_where_from_item_neq_to_to_item = df_p_source['from.[Item].[Item]'] != df_p_source['to.[To Item].[To Item]']
    list_where_c_to_p_more_then_one = (
            df_p_source['SOP Bottom Up Pegging Output Graph.[SOP BUP Consumer to Producer From Pegged]'] > 0)
    list_where_second = ((list_where_from_location_neq_to_to_location | list_where_from_item_neq_to_to_item) &
                         list_where_c_to_p_more_then_one)

    df_return = df_p_source.loc[list_where_first | list_where_second].copy(deep=True)

    return df_return

def fn_infinite_material_node_process(df_p_source: pd.DataFrame) -> pd.DataFrame:
    """
    SOP Bottom Up Pegging Output Graph.[W Infinite Material Node] 컬럼을 기준으로 데이터를 생성하여 input 테이블인 df에 추가
    :param df_p_source: df
    :return: Dataframe
    """
    # 최종 Return할 DataFrame
    df_return = pd.DataFrame(
        {'from.[Activity1].[Activity1]': [], 'from.[Activity2].[Activity Type2]': [],
         'from.[Activity2].[Activity2]': [], 'from.[Activity3].[Activity3]': [], 'from.[Item].[Item]': [],
         'from.[Location].[Location]': [], 'from.[Time].[Week]': [], 'from.[Documents].[OrderlineID]': [],
         'to.[Activity1].[Activity1]': [], 'to.[Activity2].[Activity Type2]': [], 'to.[Activity2].[Activity2]': [],
         'to.[Activity3].[Activity3]': [], 'to.[Demand].[DemandID]': [], 'to.[Demand Type].[Demand Type]': [],
         'to.[Documents].[OrderlineID]': [], 'to.[To Time].[To Week]': [], 'to.[To Item].[To Item]': [],
         'to.[To Location].[To Location]': [], 'to.[Item].[Item]': [], 'to.[Location].[Location]': [],
         'to.[Sales Domain].[Customer Group]': [], 'to.[Time].[Week]': [],
         'SOP Bottom Up Pegging Output Graph.[SOP BUP Consumer to Producer From Pegged]': [],
         'SOP Bottom Up Pegging Output Graph.[SOP BUP Producer to Consumer From Pegged]': [],
         'SOP Bottom Up Pegging Output Graph.[W Infinite Material Node]': [],
         'SOP Bottom Up Pegging Output Graph.[Preallocation Hub]': [],
         'SOP Bottom Up Pegging Output Graph.[Local the Real Owner]': [],
         'SOP Bottom Up Pegging Output Graph.[Local the Real Owner To Location]': []
         })
    # 입력 DF에 추가할 DataFrame
    df_add = df_return.copy(deep=True)

    # SOP Bottom Up Pegging Output Graph.[W Infinite Material Node] 컬럼값이 1인 경우
    list_where_infinite_material_node_eq_one = (
        df_p_source)['SOP Bottom Up Pegging Output Graph.[W Infinite Material Node]'] == 1
    # SOP Bottom Up Pegging Output Graph.[SOP BUP Consumer to Producer From Pegged] 컬럼값이 1 이상인 경우
    list_where_cons_to_prod_qty_more_then_one = (
        df_p_source)['SOP Bottom Up Pegging Output Graph.[SOP BUP Consumer to Producer From Pegged]'] > 0
    list_where = list_where_infinite_material_node_eq_one & list_where_cons_to_prod_qty_more_then_one
    df_tmp = df_p_source.loc[list_where].copy(deep=True)
    
    # from.[Item].[Item], from.[Location].[Location], from.[Time].[Week] => 기존 컬럼 유지
    # to.[Demand].[DemandID], to.[Demand Type].[Demand Type] => 기존 컬럼 유지
    # to.[Item].[Item], to.[Location].[Location], to.[Sales Domain].[Customer Group], to.[Time].[Week] => 기존 컬럼 유지
    df_add[['from.[Item].[Item]', 'from.[Location].[Location]', 'from.[Time].[Week]', 'to.[Demand].[DemandID]',
            'to.[Demand Type].[Demand Type]', 'to.[Item].[Item]', 'to.[Location].[Location]',
            'to.[Sales Domain].[Customer Group]', 'to.[Time].[Week]']] = (
        df_tmp)[['from.[Item].[Item]', 'from.[Location].[Location]', 'from.[Time].[Week]', 'to.[Demand].[DemandID]',
                 'to.[Demand Type].[Demand Type]', 'to.[Item].[Item]', 'to.[Location].[Location]',
                 'to.[Sales Domain].[Customer Group]', 'to.[Time].[Week]']]
                 
    # from.[Activity1].[Activity1] = 'ExpectedReceiptActivity', from.[Activity2].[Activity Type2] = 'Internal'
    # from.[Activity2].[Activity2] = 'ExpectedReceiptActivity', from.[Activity3].[Activity3] = 'ExpectedReceiptActivity'
    # from.[Documents].[OrderlineID] = '000SCS_LOT'
    df_add[
        ['from.[Activity1].[Activity1]', 'from.[Activity2].[Activity Type2]', 'from.[Activity2].[Activity2]',
         'from.[Activity3].[Activity3]', 'from.[Documents].[OrderlineID]']] = \
        ['ExpectedReceiptActivity', 'Internal', 'ExpectedReceiptActivity', 'ExpectedReceiptActivity', '000SCS_LOT']
        
    # SOP Bottom Up Pegging Output Graph.[SOP BUP Producer to Consumer From Pegged] 컬럼에 있던 값을
    # SOP Bottom Up Pegging Output Graph.[SOP BUP Consumer to Producer From Pegged] 컬럼으로 옮김
    df_add['SOP Bottom Up Pegging Output Graph.[SOP BUP Producer to Consumer From Pegged]'] = (
        df_tmp)['SOP Bottom Up Pegging Output Graph.[SOP BUP Consumer to Producer From Pegged]']
        
    # to.[Activity1].[Activity1] = from.[Activity1].[Activity1]
    # to.[Activity2].[Activity Type2] = from.[Activity2].[Activity Type2]
    # to.[Activity2].[Activity2] = from.[Activity2].[Activity2]
    # to.[Activity3].[Activity3] = from.[Activity3].[Activity3]
    # to.[Documents].[OrderlineID] = from.[Documents].[OrderlineID]
    # to.[To Time].[To Week] = from.[Time].[Week]
    # to.[To Item].[To Item] = from.[Item].[Item]
    # to.[To Location].[To Location] = from.[Location].[Location]
    df_add[['to.[Activity1].[Activity1]', 'to.[Activity2].[Activity Type2]', 'to.[Activity2].[Activity2]',
            'to.[Activity3].[Activity3]', 'to.[Documents].[OrderlineID]', 'to.[To Time].[To Week]',
            'to.[To Item].[To Item]', 'to.[To Location].[To Location]']] = (
        df_tmp)[['from.[Activity1].[Activity1]', 'from.[Activity2].[Activity Type2]', 'from.[Activity2].[Activity2]',
                 'from.[Activity3].[Activity3]', 'from.[Documents].[OrderlineID]', 'from.[Time].[Week]',
                 'from.[Item].[Item]', 'from.[Location].[Location]']]
    
    # 컬럼 순서 정리
    df_add = df_add[
        ['from.[Activity1].[Activity1]', 'from.[Activity2].[Activity Type2]', 'from.[Activity2].[Activity2]',
         'from.[Activity3].[Activity3]', 'from.[Item].[Item]', 'from.[Location].[Location]', 'from.[Time].[Week]',
         'from.[Documents].[OrderlineID]', 'to.[Activity1].[Activity1]', 'to.[Activity2].[Activity Type2]',
         'to.[Activity2].[Activity2]', 'to.[Activity3].[Activity3]', 'to.[Demand].[DemandID]',
         'to.[Demand Type].[Demand Type]', 'to.[Documents].[OrderlineID]', 'to.[To Time].[To Week]',
         'to.[To Item].[To Item]', 'to.[To Location].[To Location]', 'to.[Item].[Item]', 'to.[Location].[Location]',
         'to.[Sales Domain].[Customer Group]', 'to.[Time].[Week]',
         'SOP Bottom Up Pegging Output Graph.[SOP BUP Consumer to Producer From Pegged]',
         'SOP Bottom Up Pegging Output Graph.[SOP BUP Producer to Consumer From Pegged]',
         'SOP Bottom Up Pegging Output Graph.[W Infinite Material Node]'
         ]]

    # 입력 테이블과 추가 생성한 테이블을 concat
    df_return = pd.concat([df_p_source, df_add], ignore_index=True)

    # SOP Bottom Up Pegging Output Graph.[W Infinite Material Node] 컬럼 삭제
    df_return.drop(columns='SOP Bottom Up Pegging Output Graph.[W Infinite Material Node]', inplace=True)

    return df_return

def createUseMap():
    MaterialConsumption.drop("Version.[Version Name]", axis=1, inplace=True)
    MaterialConsumption.drop("W Material Consumption Association", axis=1, inplace=True)
    MaterialProduction.drop("Version.[Version Name]", axis=1, inplace=True)

    MaterialConsumption.rename(columns={
        'Item.[Item]' : 'from.[Item].[Item]',
        'Location.[Location]' : 'from.[Location].[Location]',		
        'Activity1.[Activity1]' : 'from.[Activity1].[Activity1]',
        'Activity2.[Activity2]' : 'from.[Activity2].[Activity2]',
        'Activity3.[Activity3]' : 'from.[Activity3].[Activity3]'
        }, inplace=True)
    
    MaterialProduction.rename(columns={
        'Activity1.[Activity1]' : 'to.[Activity1].[Activity1]',
        'Activity2.[Activity2]' : 'to.[Activity2].[Activity2]',
        'Activity3.[Activity3]' : 'to.[Activity3].[Activity3]',
        'Item.[Item]' : 'to.[Item].[Item]',
        'Location.[Location]' : 'to.[Location].[Location]',	
        'W Material Production Association' : 'whereUseLevel'		
        }, inplace=True)
    
    useMap = pd.merge(MaterialConsumption, MaterialProduction, 
                      left_on=['from.[Activity1].[Activity1]', 'from.[Activity2].[Activity2]','from.[Activity3].[Activity3]'], 
		      right_on=['to.[Activity1].[Activity1]', 'to.[Activity2].[Activity2]','to.[Activity3].[Activity3]'], how ='inner')
    
    useMap['concatenated_string'] = (
            useMap['from.[Activity1].[Activity1]'] + useMap['from.[Activity2].[Activity2]'] +
            useMap['from.[Activity3].[Activity3]'] + useMap['from.[Item].[Item]'] +
            useMap['from.[Location].[Location]'] + useMap['to.[Activity1].[Activity1]'] +
            useMap['to.[Activity2].[Activity2]'] + useMap['to.[Activity3].[Activity3]'] +
            useMap['to.[Item].[Item]'] + useMap['to.[Location].[Location]'])
    
    level = useMap.set_index('concatenated_string')['whereUseLevel'].to_dict()
    return level

 
# whereUse_map function that maps the Network Levels in Where Used Graph to a concatenated string in a dictionary
def whereUse_map():
    Where_Used['concatenated_string'] = (
            Where_Used['from.[Activity1].[Activity1]'] + Where_Used['from.[Activity2].[Activity2]'] +
            Where_Used['from.[Activity3].[Activity3]'] + Where_Used['from.[Item].[Item]'] +
            Where_Used['from.[Location].[Location]'] + Where_Used['to.[Activity1].[Activity1]'] +
            Where_Used['to.[Activity2].[Activity2]'] + Where_Used['to.[Activity3].[Activity3]'] +
            Where_Used['to.[Item].[Item]'] + Where_Used['to.[Location].[Location]'])

    level = Where_Used.set_index('concatenated_string')[
        '013.006W Where Used Network Item SCS.[W Upstream Network Item Levels]'].to_dict()
    return level


# preprocessing function that preprocesses, filters and cleans the data in the BUP_Input
def preprocessing(BUP_Input,concat_list):
    #@@20241120 BUP_Input.fillna(0, inplace=True)

    BUP_Input["SOP Bottom Up Pegging Output Graph.[SOP BUP Consumer to Producer From Pegged]"].fillna(0, inplace=True)
    BUP_Input["SOP Bottom Up Pegging Output Graph.[SOP BUP Producer to Consumer From Pegged]"].fillna(0, inplace=True)

    cond1 = BUP_Input["SOP Bottom Up Pegging Output Graph.[SOP BUP Consumer to Producer From Pegged]"] > 0
    cond2 = BUP_Input["SOP Bottom Up Pegging Output Graph.[SOP BUP Producer to Consumer From Pegged]"] > 0
    
    BUP_Input = BUP_Input[cond1 | cond2]

    BUP_Input['Concat'] = (
            BUP_Input['from.[Activity1].[Activity1]'] + BUP_Input['from.[Activity2].[Activity2]'] +
            BUP_Input['from.[Activity3].[Activity3]'] + BUP_Input['from.[Item].[Item]'] +
            BUP_Input['from.[Location].[Location]'] + BUP_Input['to.[Activity1].[Activity1]'] +
            BUP_Input['to.[Activity2].[Activity2]'] + BUP_Input['to.[Activity3].[Activity3]'] +
            BUP_Input['to.[To Item].[To Item]'] + BUP_Input['to.[To Location].[To Location]'])

    BUP_Input = BUP_Input[(BUP_Input['Concat'].isin(concat_list) & cond1) | cond2]

    BUP_Input.drop(['Concat'], axis=1, inplace=True)

    return BUP_Input


# data_PlannedCondEndDate function that calculates the PlannedConsEndDate based on the existing columns in the BUP_Input
def data_PlannedConsEndDate(BUP_Input):    
    CTOP_BUP_Input=pd.DataFrame()
    CTOP_BUP_Input=BUP_Input

    CTOP_BUP_Input['to.[Time].[Week]'] = CTOP_BUP_Input['to.[Time].[Week]'].astype(int)
    CTOP_BUP_Input['from.[Time].[Week]'] = CTOP_BUP_Input['from.[Time].[Week]'].astype(int)

    #@@ 20241120 CTOP_BUP_Input=CTOP_BUP_Input[CTOP_BUP_Input["SOP Bottom Up Pegging Output Graph.[BUP Cons to Prod Demand Pegged Qty]"]>0]
    
    #@@20241120
    CTOP_BUP_Input = CTOP_BUP_Input[
        CTOP_BUP_Input["SOP Bottom Up Pegging Output Graph.[SOP BUP Consumer to Producer From Pegged]"] > 0]

    CTOP_BUP_Input['toenddate'] = (
            CTOP_BUP_Input['to.[Item].[Item]'].astype(str) +
            CTOP_BUP_Input['to.[Location].[Location]'].astype(str) +
            CTOP_BUP_Input['to.[Time].[Week]'].astype(str) +
            CTOP_BUP_Input['to.[Demand].[DemandID]'].astype(str) +
            CTOP_BUP_Input['from.[Activity1].[Activity1]'].astype(str) +
            CTOP_BUP_Input['from.[Activity2].[Activity2]'].astype(str) +
            CTOP_BUP_Input['from.[Item].[Item]'].astype(str) +
            CTOP_BUP_Input['from.[Location].[Location]'].astype(str) +
            CTOP_BUP_Input['from.[Time].[Week]'].astype(str) +
            CTOP_BUP_Input['from.[Documents].[OrderlineID]'].astype(str))

    BUP_Input['to.[Time].[Week]'] = BUP_Input['to.[Time].[Week]'].astype(int)
    BUP_Input['to.[To Time].[To Week]'] = BUP_Input['to.[To Time].[To Week]'].astype(int)
    BUP_Input['fromenddate'] = (
            BUP_Input['to.[Item].[Item]'].astype(str) + BUP_Input['to.[Location].[Location]'].astype(str) +
            BUP_Input['to.[Time].[Week]'].astype(str) + BUP_Input['to.[Demand].[DemandID]'].astype(str) +
            BUP_Input['to.[Activity1].[Activity1]'].astype(str) + BUP_Input['to.[Activity2].[Activity2]'].astype(str) +
            BUP_Input['to.[To Item].[To Item]'].astype(str) + BUP_Input['to.[To Location].[To Location]'].astype(str) +
            BUP_Input['to.[To Time].[To Week]'].astype(str) + BUP_Input['to.[Documents].[OrderlineID]'].astype(str))

    from_dict = CTOP_BUP_Input.set_index('toenddate')['to.[To Time].[To Week]'].to_dict()

    BUP_Input['PlannedConsEndDate'] = BUP_Input['fromenddate'].map(from_dict)
    
    #2025.01.22
    from_dict = CTOP_BUP_Input.set_index('toenddate')['to.[To Location].[To Location]'].to_dict()

    BUP_Input['to_to_siteid'] = BUP_Input['fromenddate'].map(from_dict)
    
    BUP_Input.drop(['fromenddate'], axis=1, inplace=True)

    return BUP_Input

    
# Cons_RoutingID function
# that calculates the ConsRoutingID and ConsRoutingID_dist based on the existing columns in BUP_Input,
# the latter column will be used to generate the BODNAME column in Distribution Report
def Cons_RoutingID(BUP_Input):
   
    l=["Distribution"]
    il=["Internal"]

    ####2024.12.24
    BUP_Input.update(BUP_Input.loc[(BUP_Input['to.[Activity2].[Activity Type2]'].isin(l)),'to.[Activity1].[Activity1]'].fillna("").astype(str))

    BUP_Input['ConsRoutingID'] = (
        np.where(BUP_Input['to.[Activity2].[Activity Type2]'].isin(l),
                 "Transport-" + BUP_Input['from.[Item].[Item]'].astype(str) + "-" +
                 BUP_Input['to.[Activity1].[Activity1]'].astype(str),
                 np.where(BUP_Input['to.[Activity2].[Activity Type2]'].isin(il),
                          BUP_Input['to.[Activity2].[Activity2]'].astype(str) + "-" +
                          BUP_Input['from.[Item].[Item]'].astype(str),
                          BUP_Input['to.[Activity2].[Activity2]'])))
    BUP_Input['ConsRoutingID_dist'] = (
        np.where(BUP_Input['to.[Activity2].[Activity Type2]'].isin(l),
                 BUP_Input['to.[Activity1].[Activity1]'].astype(str),
                 np.where(BUP_Input['to.[Activity2].[Activity Type2]'].isin(il),
                          BUP_Input['to.[Activity2].[Activity2]'].astype(str) + "-" +
                          BUP_Input['from.[Item].[Item]'].astype(str),
                          BUP_Input['to.[Activity2].[Activity2]'])))
    
    return BUP_Input


# Prod_RoutingID function that calculates the ProdRoutingID column for BUP_Input based on concatenating the existing columns in BUP_Input
def Prod_RoutingID(BUP_Input):
    l=["Distribution"]
    il=["Internal"]

    ######2024.12.24
    BUP_Input.update(BUP_Input.loc[(BUP_Input['from.[Activity2].[Activity Type2]'].isin(l)),'from.[Activity1].[Activity1]'].astype(str).fillna(""))
    
    BUP_Input['ProdRoutingID'] = (
        np.where(BUP_Input['from.[Activity2].[Activity Type2]'].isin(l),
                 "Transport-" + BUP_Input['from.[Item].[Item]'].astype(str) + "-" +
                 BUP_Input['from.[Activity1].[Activity1]'].astype(str),
                 np.where(BUP_Input['from.[Activity2].[Activity Type2]'].isin(il),
                          BUP_Input['from.[Activity2].[Activity2]'].astype(str) + "-" +
                          BUP_Input['from.[Item].[Item]'].astype(str),
                          BUP_Input['from.[Activity2].[Activity2]'])))

# PlannedProdEndDate function that calculates the PlannedProdEndDate. This is the same value as 'from.[Time].[Week]' from BUP_Input
def PlannedProdEndDate(BUP_Input):
    BUP_Input['PlannedProdEndDate'] = BUP_Input['from.[Time].[Week]']


# parse_week_string function that returns the Week string in YYYYWW format to start of the week
def parse_week_string(week_string):
    week_start_date=week_string
    try:
       year = int(week_string[0:4])
       week = int(week_string[4:])
       start_of_year = datetime(year, 1, 1)
       FT = start_of_year -timedelta(days=start_of_year.weekday())
       week_start_date=FT+timedelta(weeks=week)
    except Exception as e:
       print(e)
    return week_start_date
        

# PlannedConsStartDate function that calculates the PlannedConsStartDate. This is the same value as to.[Time].[Week]' from BUP_Input
def PlannedConsStartDate(BUP_Input):
    BUP_Input['PlannedConsStartDate'] = BUP_Input['to.[To Time].[To Week]']


# PlannedProdStartDate function that calculates the PlannedProdStartDate based on the existing columns in the BUP_Input
def PlannedProdStartDate(BUP_Input):
    C_PBUP_Input = pd.DataFrame()
    C_PBUP_Input = BUP_Input
    C_PBUP_Input = (
        C_PBUP_Input)[C_PBUP_Input["SOP Bottom Up Pegging Output Graph.[SOP BUP Consumer to Producer From Pegged]"] > 0]
    C_PBUP_Input['to.[Time].[Week]'] = C_PBUP_Input['to.[Time].[Week]'].astype(int)
    C_PBUP_Input['to.[To Time].[To Week]'] = C_PBUP_Input['to.[To Time].[To Week]'].astype(int)
    C_PBUP_Input['toenddate'] = (
            C_PBUP_Input['to.[Item].[Item]'].astype(str) + C_PBUP_Input['to.[Location].[Location]'].astype(str) +
            C_PBUP_Input['to.[Time].[Week]'].astype(str) + C_PBUP_Input['to.[Demand].[DemandID]'].astype(str) +
            C_PBUP_Input['to.[Activity1].[Activity1]'].astype(str) +
            C_PBUP_Input['to.[Activity2].[Activity2]'].astype(str) +
            C_PBUP_Input['to.[To Item].[To Item]'].astype(str) +
            C_PBUP_Input['to.[To Location].[To Location]'].astype(str) +
            C_PBUP_Input['to.[To Time].[To Week]'].astype(str) +
            C_PBUP_Input['to.[Documents].[OrderlineID]'].astype(str))

    BUP_Input['to.[Time].[Week]'] = BUP_Input['to.[Time].[Week]'].astype(int)
    BUP_Input['from.[Time].[Week]'] = BUP_Input['from.[Time].[Week]'].astype(int)
    BUP_Input['fromenddate'] = (
            BUP_Input['to.[Item].[Item]'].astype(str) + BUP_Input['to.[Location].[Location]'].astype(str) +
            BUP_Input['to.[Time].[Week]'].astype(str) + BUP_Input['to.[Demand].[DemandID]'].astype(str) +
            BUP_Input['from.[Activity1].[Activity1]'].astype(str) +
            BUP_Input['from.[Activity2].[Activity2]'].astype(str) + BUP_Input['from.[Item].[Item]'].astype(str) +
            BUP_Input['from.[Location].[Location]'].astype(str) + BUP_Input['from.[Time].[Week]'].astype(str) +
            BUP_Input['from.[Documents].[OrderlineID]'].astype(str))

    to_dict = C_PBUP_Input.set_index('toenddate')['from.[Time].[Week]'].to_dict()

    BUP_Input['PlannedProdStartDate'] = BUP_Input['fromenddate'].map(to_dict)
    BUP_Input.drop(['fromenddate'], axis=1, inplace=True)

# WorkOrderNumber function that calculates the ConsWorkOrderNumber and ProdWorkOrderNumber from the existing columns in BUP_Input. Hash Maps are used in this function which are similar to dictionary
def WorkOrderNumber(BUP_Input):
    BUP_Input['PlannedProdStartDate'] = BUP_Input['PlannedProdStartDate'].fillna(0)
    BUP_Input['PlannedProdStartDate']=BUP_Input['PlannedProdStartDate'].astype(int)
    BUP_Input['from.[Time].[Week]'] = BUP_Input['from.[Time].[Week]'].fillna(0)
    BUP_Input['from.[Time].[Week]'] = BUP_Input['from.[Time].[Week]'].astype(int)
    BUP_Input['ProdRoutingID'] = BUP_Input['ProdRoutingID'].fillna('')

    BUP_Input['from.[Documents].[OrderlineID]'] = BUP_Input['from.[Documents].[OrderlineID]'].fillna('')

    BUP_Input['ProdWorkOrderstring'] = (
            BUP_Input['PlannedProdStartDate'].astype(str) + '_' + BUP_Input['from.[Time].[Week]'].astype(str) + '_' +
            BUP_Input['from.[Documents].[OrderlineID]'].astype(str) + '_' + BUP_Input['ProdRoutingID'].astype(str))
    #@@20241120 hash_string_to_num_dict = {}
    #@@20241120 hash_val = 0

    # Create a Series with unique ProdWorkOrderstrings
    unique_strings1 = BUP_Input.loc[~pd.isnull(BUP_Input['ProdWorkOrderstring']), 'ProdWorkOrderstring'].unique()

    BUP_Input['PlannedConsEndDate'] = BUP_Input['PlannedConsEndDate'].fillna('0')
    BUP_Input['PlannedConsEndDate'] = BUP_Input['PlannedConsEndDate'].astype(int)
    BUP_Input['to.[To Time].[To Week]'] = BUP_Input['to.[To Time].[To Week]'].fillna(0)
    BUP_Input['to.[To Time].[To Week]'] = BUP_Input['to.[To Time].[To Week]'].astype(int)
    BUP_Input['ConsRoutingID'] = BUP_Input['ConsRoutingID'].fillna('')
    BUP_Input['ConsRoutingID_dist'] = BUP_Input['ConsRoutingID_dist'].fillna('')
    BUP_Input['to.[Documents].[OrderlineID]'] = BUP_Input['to.[Documents].[OrderlineID]'].fillna('')

    #####2024.12.24
    #BUP_Input['to_to_siteid'] = BUP_Input['ConsRoutingID_dist'].fillna("")
    #BUP_Input['to_to_siteid'] = BUP_Input['to.[To Location].[To Location]']
    BUP_Input['Exp MPI_SALESID'] = BUP_Input['to.[Location].[Location]']
    BUP_Input['Exp MPI_TOSITEID'] = BUP_Input['to.[Location].[Location]']
    BUP_Input['To Site SALESID'] = ""
    BUP_Input.loc[BUP_Input['to_to_siteid']==BUP_Input['Exp MPI_TOSITEID'],'To Site SALESID'] = BUP_Input['Exp MPI_SALESID']
    BUP_Input['To Site SALESID'] = BUP_Input['To Site SALESID'].fillna("")	
	
    BUP_Input['ConsWorkOrderstring'] = (
            BUP_Input['to.[To Time].[To Week]'].astype(str) + '_' + BUP_Input['PlannedConsEndDate'].astype(str) + '_' +
            BUP_Input['to.[Documents].[OrderlineID]'].astype(str) + '_' + BUP_Input['ConsRoutingID'].astype(str) + '_' + BUP_Input['To Site SALESID'].astype(str))
    #######

    #@@20241120 hash_string_to_num_dict = {}
    #@@20241120 hash_val = 0

    # Creating ConsWorkOrderstrings
    unique_strings2 = BUP_Input.loc[~pd.isnull(BUP_Input['ConsWorkOrderstring']), 'ConsWorkOrderstring'].unique()

    # Generating hash values for unique ConsWorkOrderstrings
    unique_strings=unique_strings2
    unique_strings=np.append(unique_strings,unique_strings1)

    unique_strings=np.unique(unique_strings)

    hash_vals = np.arange(Min_Seq + 1, Min_Seq + len(unique_strings) + 1)

    # Creating a mapping of ConsWorkOrderstrings to hash values
    hash_string_to_num_dict = dict(zip(unique_strings, hash_vals))

    # Map the hash values to the ConsWorkOrderstrings in the dataframe
    BUP_Input['ProdWorkOrderNumber'] = BUP_Input['ProdWorkOrderstring'].map(hash_string_to_num_dict)
    BUP_Input['ConsWorkOrderNumber'] = BUP_Input['ConsWorkOrderstring'].map(hash_string_to_num_dict)


# PeggingIDs function that calculates the PeggingIDs based on the row index of BUP_Input dataframe
def PeggingIDs(BUP_Input):
    BUP_Input['EXP_Material_Pegging_Info_PEGGINGID']=BUP_Input.index
    

# rename function that renames the columns in BUP_Input dataframe
def rename(BUP_OUT):
    BUP_OUT.rename(columns={
        'PeggingIDs': 'EXP_Material_Pegging_Info_PEGGINGID',
        'from.[Location].[Location]': 'Location.[Location]',
        'from.[Item].[Item]': 'Item.[Item]',
        'SOP Bottom Up Pegging Output Graph.[SOP BUP Producer to Consumer From Pegged]': 'Exp MPI_QTY',
        'SOP Bottom Up Pegging Output Graph.[SOP BUP Consumer to Producer From Pegged]': 'EXP_Material_Pegging_Info_QTYC_P',
        'PlannedProdStartDate': 'Exp MPI_PLANNEDPRODSTARTDATE',
        'PlannedProdEndDate': 'Exp MPI_PLANNEDPRODENDDATE',
        'PlannedConsStartDate': 'Exp MPI_PLANNEDCONSSTARTDATE',
        'PlannedConsEndDate': 'Exp MPI_PLANNEDCONSENDDATE',
        'ProdWorkOrderNumber': 'Exp MPI_PRODWORKORDERNUMBER',
        'ConsWorkOrderNumber': 'Exp MPI_CONSWORKORDERNUMBER',
        'from.[Documents].[OrderlineID]': 'Exp MPI_PRODLOTNUMBER',
        'to.[Documents].[OrderlineID]': 'Exp MPI_CONSLOTNUMBER',
        'ProdRoutingID': 'Exp MPI_PRODROUTINGID',
        'ConsRoutingID': 'Exp MPI_CONSROUTINGID',
        'ConsRoutingID_dist': 'Exp MPI_CONSROUTINGID_DIST',
        'to.[Demand].[DemandID]': 'Exp MPI_ORDERID',
        'to.[Time].[Week]': 'Exp MPI_DEMANDSTARTDATE',
        'to.[Item].[Item]': 'Exp MPI_TOITEM',
        'to.[Sales Domain].[Customer Group]': 'Exp MPI_SALESLEVEL'}, inplace=True)


# out_df function that handles the cases of Inventory Demand and pass it as the last row for Item_Location combination. Additional columns such as TOSITEID and SALESID are also added in this function
def out_df(BUP_Input,headers_bool,InventoryDemand_req,Routing_LeadTime):   
    BUP_OUT=BUP_Input

    #BUP_OUT['to_to_siteid'] = BUP_OUT['to_to_siteid'].fillna('').astype(str)
    #BUP_OUT['Exp MPI_TOSITEID'] = BUP_OUT['to_to_siteid']
    #BUP_OUT.loc[BUP_OUT['Exp MPI_TOSITEID']=='', 'Exp MPI_TOSITEID'] = BUP_OUT['to.[Location].[Location]']
    #BUP_OUT['Exp MPI_SALESID'] = BUP_OUT['Exp MPI_TOSITEID']
    
    #@@20241120
    rename(BUP_OUT)
    
    # Copying the Version Name from Activity_LeadTime dataframe in the ActivityLeadTime variable
    # and inserting the value in BUP_OUT dataframe's column 'Version.[Version Name]'
    ActivityLeadTime = Activity_LeadTime['Version.[Version Name]'].values[0]
    BUP_OUT.insert(loc=0, column='Version.[Version Name]', value=ActivityLeadTime)
    
    # Inserting the values of Pegging IDs in '[Sequence].[Sequence]' column of BUP_OUT dataframe
    BUP_OUT.insert(loc=3, column='[Sequence].[Sequence]', value=BUP_OUT['EXP_Material_Pegging_Info_PEGGINGID'])
    
    # Repositioning the columns in BUP_OUT and filtering only the MPI_QTY which are positive in values
    l = ['Version.[Version Name]', 'Item.[Item]', 'Location.[Location]', '[Sequence].[Sequence]',
         'EXP_Material_Pegging_Info_PEGGINGID', 'Exp MPI_CONSLOTNUMBER', 'Exp MPI_CONSROUTINGID',
         'Exp MPI_CONSROUTINGID_DIST', 'Exp MPI_CONSWORKORDERNUMBER', 'Exp MPI_DEMANDSTARTDATE', 'Exp MPI_ORDERID',
         'Exp MPI_PLANNEDCONSENDDATE', 'Exp MPI_PLANNEDCONSSTARTDATE', 'Exp MPI_PLANNEDPRODENDDATE',
         'Exp MPI_PLANNEDPRODSTARTDATE', 'Exp MPI_PRODLOTNUMBER', 'Exp MPI_PRODROUTINGID',
         'Exp MPI_PRODWORKORDERNUMBER', 'Exp MPI_QTY', 'Exp MPI_SALESLEVEL', 'Exp MPI_TOITEM', 'Exp MPI_TOSITEID',
         'Exp MPI_SALESID', 'to.[Activity2].[Activity Type2]', 'Documents.[Document Type]_from',
         'Documents.[Document Type]_to', 'to_to_siteid', 'To Site SALESID']
    BUP_OUT = BUP_OUT[l]
    BUP_OUT = BUP_OUT[BUP_OUT['Exp MPI_QTY'] > 0]

    return BUP_OUT
    

# supstatus function that generates the entire Supplier Status Report
def supstatus(BUP_OUT_2):
    # Creating an empty dataframe
    BUP_Report1=pd.DataFrame()

    # Creating 2 dictionaries prod_dict and cons_dict that stores the respective WorkOrderNumbers as a key and combination of respective RoutingID and DocumentType
    prod_dict = BUP_OUT_2.set_index('Exp MPI_PRODWORKORDERNUMBER').apply(lambda row: (row['Exp MPI_PRODROUTINGID'], row['Documents.[Document Type]_from']), axis=1).to_dict()
    cons_dict = BUP_OUT_2.set_index('Exp MPI_CONSWORKORDERNUMBER').apply(lambda row: (row['Exp MPI_CONSROUTINGID'], row['Documents.[Document Type]_to']), axis=1).to_dict()

    # kwargs function to iterate over both the dictionaries 
    routing_workorder={**prod_dict,**cons_dict}

    # Creating 2 columns as WORKORDERNUMBER and Details that store the key and value of the above dictionaries
    BUP_Report1 = pd.DataFrame(list(routing_workorder.items()), columns=['WORKORDERNUMBER','Details'])

    # Copying the ROUTINGID and DocumentType from Details column in BUP_Report1
    BUP_Report1[['ROUTINGID', 'DocumentType']] = pd.DataFrame(BUP_Report1['Details'].tolist(), index=BUP_Report1.index)

    # Dropping the Details column and insertng values in necessary columns such as '[Sequence].[Sequence]', 'GBM' and 'Version.[Version Name]'
    BUP_Report1.drop(columns=['Details'], inplace=True)
    BUP_Report1['[Sequence].[Sequence]'] = BUP_Report1.index + Min_Seq
    BUP_Report1['GBM']="VD"
    BUP_Report1['Version.[Version Name]'] = BUP_OUT_2['Version.[Version Name]']
    BUP_Report1['TYPE']= MPI_TYPE
    BUP_Report1=BUP_Report1.drop_duplicates()

    # Modifying the statuses of DocumentType in Supply Status_STATUS column in BUP_Report1 
    OH=["On Hand"]
    CP=["Shipment Schedule"]
    FP=["Production Orders"] 
    IT=["Scheduled Receipts"]
    BUP_Report1['Exp Supply Status_STATUS'] = (
        np.where(BUP_Report1['DocumentType'].isin(OH), "OH",
                 np.where(BUP_Report1['DocumentType'].isin(CP), "CP",
                          np.where(BUP_Report1['DocumentType'].isin(FP), "FP",
                                   np.where(BUP_Report1['DocumentType'].isin(IT), "IT", "PP")))))
                                   
    # Repositioning the columns in BUP_Report1
    l = ['Version.[Version Name]', '[Sequence].[Sequence]', 'GBM', 'ROUTINGID', 'WORKORDERNUMBER',
         'Exp Supply Status_STATUS', 'TYPE']
    BUP_Report1=BUP_Report1[l]
    BUP_Report1=BUP_Report1[BUP_Report1['WORKORDERNUMBER']!='']
    BUP_Report1['WORKORDERNUMBER']=BUP_Report1['WORKORDERNUMBER'].astype(int)

    # Renaming columns in BUP_Report1
    BUP_Report1.rename(columns={
        'GBM':'Exp Supply Status_GBM',
        'TYPE':'Exp Supply Status_TYPE',
        'ROUTINGID':'Exp Supply Status_ROUTINGID',
        'WORKORDERNUMBER':'Exp Supply Status_WORKORDERNUMBER',},inplace=True)

    return BUP_Report1;


# DistributionPlan function that generates the entire Distribution Report
def DistributionPlan(BUPFULL_OUT):
    Distribution_df=pd.DataFrame()

    # Copying the values from necessary columns from BUPFULL_OUT column into Distribution_df in a vectorized manner 
    Distribution_df['Item.[Item]']=BUPFULL_OUT['Item.[Item]']   
    Distribution_df['Location.[Location]']=BUPFULL_OUT['Location.[Location]']
    Distribution_df['Exp Dist Plan All_GBM']='VD'
    Distribution_df['Exp Dist Plan All_TYPE']= MPI_TYPE
    Distribution_df['Exp Dist Plan All_DISTRIBUTIONORDERID']=BUPFULL_OUT['Exp MPI_CONSLOTNUMBER']
    Distribution_df['Exp Dist Plan All_BODNAME']=BUPFULL_OUT['Exp MPI_CONSROUTINGID_DIST']
    Distribution_df['Exp Dist Plan All_PLANNEDDELIVERYDATE']=BUPFULL_OUT['Exp MPI_PLANNEDCONSENDDATE']
    Distribution_df['Exp Dist Plan All_PLANNEDSHIPMENTDATE']=BUPFULL_OUT['Exp MPI_PLANNEDCONSSTARTDATE']
    Distribution_df['Exp Dist Plan All_QTYPLANNED']=BUPFULL_OUT['Exp MPI_QTY']

    Distribution_df['Exp Dist Plan All_Item']=BUPFULL_OUT['Exp MPI_TOITEM']

    ##2024.12.24. Distribution_df['Exp Dist Plan All_TOSITEID']=BUPFULL_OUT['Exp MPI_TOSITEID']
    Distribution_df['Exp Dist Plan All_TOSITEID'] = BUPFULL_OUT['to_to_siteid']
	
    ##2024.12.24 Distribution_df['Exp Dist Plan All_SALESID']=BUPFULL_OUT['Exp MPI_SALESID']
    Distribution_df['Exp Dist Plan All_SALESID'] = BUPFULL_OUT['To Site SALESID']
    
    Distribution_df['Consworkordernumber']=BUPFULL_OUT['Exp MPI_CONSWORKORDERNUMBER']
    Distribution_df['to.[Activity2].[Activity Type2]']=BUPFULL_OUT['to.[Activity2].[Activity Type2]']
    
    # Filtering the data such that Consworkordernumber is not null and 'to.[Activity2].[Activity Type2]' is only 'Distribution'
    Distribution_df=Distribution_df[Distribution_df['Consworkordernumber']!='']
    Distribution_df['Consworkordernumber']=Distribution_df['Consworkordernumber'].astype(int)
    act1_l=["Distribution"]
    Distribution_df = Distribution_df[Distribution_df['to.[Activity2].[Activity Type2]'].isin(act1_l)]
    
    # Populating the RELEASEDPLAN using the data in DISTRIBUTIONORDERID column in Distribution_df
    Distribution_df['Exp Dist Plan All_RELEASEDPLAN'] = np.where(Distribution_df['Exp Dist Plan All_DISTRIBUTIONORDERID'].str.startswith("000SCS_LOT"), 0, 
                                                             np.where(Distribution_df['Exp Dist Plan All_DISTRIBUTIONORDERID'].str.startswith("LPS_WIP"), 0, 1))

    # Updating the values in DISTRIBUTIONORDERID column
    Distribution_df['Exp Dist Plan All_DISTRIBUTIONORDERID'] = np.where(
        Distribution_df['Exp Dist Plan All_DISTRIBUTIONORDERID'].str.startswith("000SCS_LOT"),
        Distribution_df['Consworkordernumber'], Distribution_df['Exp Dist Plan All_DISTRIBUTIONORDERID']+'_'+Distribution_df['Consworkordernumber'].astype(str))

    Distribution_df['Exp Dist Plan All_DISTRIBUTIONORDERID'] = Distribution_df[
        'Exp Dist Plan All_DISTRIBUTIONORDERID'].astype(str)

    # Grouping the data in the dataframe based on the conditions which vary from 'first' to 'sum' to 'max'
    Distribution_df = Distribution_df.groupby(['Consworkordernumber', 'Exp Dist Plan All_SALESID']).agg(
        {'Location.[Location]':'first',
         'Item.[Item]': 'first',  
         'Exp Dist Plan All_GBM': 'first', 
         'Exp Dist Plan All_DISTRIBUTIONORDERID': 'first',  
         'Exp Dist Plan All_BODNAME': 'first', 
         'Exp Dist Plan All_PLANNEDDELIVERYDATE': 'first',  
         'Exp Dist Plan All_PLANNEDSHIPMENTDATE': 'first',  
         'Exp Dist Plan All_QTYPLANNED': 'sum', 
         #'Exp Dist Plan All_SALESID': 'first', 
         'Exp Dist Plan All_RELEASEDPLAN': 'max',
         'Exp Dist Plan All_Item': 'first',
         'Exp Dist Plan All_TOSITEID':'first',
         'Exp Dist Plan All_TYPE':'first', }).reset_index() 

    # Dropping the duplicates values in Consworkordernumber if found any and then dropping the column 'Consworkordernumber'
    Distribution_df = Distribution_df.drop_duplicates(subset=['Consworkordernumber', 'Exp Dist Plan All_SALESID'])
    Distribution_df.drop(columns=['Consworkordernumber'],inplace=True)

    Distribution_df.reset_index(drop=True,inplace=True)
    # Inserting the values in '[Sequence].[Sequence]' and 'Version.[Version Name]' columns in Distribution_df
    
    Distribution_df['[Sequence].[Sequence]']=Distribution_df.index.to_series() + Min_Seq
    
    # Repositioning the columns in Distribution_df
    # pos=['Version.[Version Name]','Item.[Item]','Location.[Location]','[Sequence].[Sequence]','Exp Dist Plan All_GBM','Exp Dist Plan All_DISTRIBUTIONORDERID','Exp Dist Plan All_BODNAME','Exp Dist Plan All_PLANNEDDELIVERYDATE','Exp Dist Plan All_PLANNEDSHIPMENTDATE','Exp Dist Plan All_QTYPLANNED','Exp Dist Plan All_SALESID','Exp Dist Plan All_RELEASEDPLAN','Exp Dist Plan All_Item','Exp Dist Plan All_TOSITEID']
    pos=['Item.[Item]','Location.[Location]','[Sequence].[Sequence]','Exp Dist Plan All_GBM','Exp Dist Plan All_DISTRIBUTIONORDERID','Exp Dist Plan All_BODNAME','Exp Dist Plan All_PLANNEDDELIVERYDATE','Exp Dist Plan All_PLANNEDSHIPMENTDATE','Exp Dist Plan All_QTYPLANNED','Exp Dist Plan All_SALESID','Exp Dist Plan All_RELEASEDPLAN','Exp Dist Plan All_Item','Exp Dist Plan All_TOSITEID', 'Exp Dist Plan All_TYPE']
    
    Distribution_df=Distribution_df[pos]    
    Distribution_df.reset_index(drop=True,inplace=True)
    
    return Distribution_df;

######################################################################

# Creating an empty dataframe by the name of BUPFULL_OUT
BUPFULL_OUT=pd.DataFrame()
count=1

# Logging Start time of Plugin
initTime = time.time()
logger.warning(f'START({initTime})')


PlanConfig.rename(columns={'MP Plan Configure.[Config Key Seq]': 'to.[Location].[Location Region]'},inplace=True)
df = pd.merge(df, PlanConfig, on = 'to.[Location].[Location Region]', how='inner')

df = fn_initialize_df(df)

# MapReplace Original OrderlineID and DemandID
MapOriginalDemandID.rename(columns={'Demand.[DemandID]': 'to.[Demand].[DemandID]'},inplace=True)
df = pd.merge(df, MapOriginalDemandID, on = 'to.[Demand].[DemandID]', how='left')
#MapID=["InventoryDemand"] 
df['to.[Demand].[DemandID]'] = df['Map Original Demand ID'].fillna(df['to.[Demand].[DemandID]'])

MapOriginalOrderlineID.rename(columns={'Documents.[OrderlineID]': 'to.[Documents].[OrderlineID]',
                                       'Documents.[Document Type]': 'Documents.[Document Type]_to',
                                       'Map Original Orderline ID': 'Map Original Orderline ID_to'}, inplace=True)
df = pd.merge(df, MapOriginalOrderlineID, on='to.[Documents].[OrderlineID]', how='left')

#MapLOT=["000SCS_LOT"] 
df['to.[Documents].[OrderlineID]'] = df['Map Original Orderline ID_to'].fillna(df['to.[Documents].[OrderlineID]'])

MapOriginalOrderlineID.rename(columns={'to.[Documents].[OrderlineID]': 'from.[Documents].[OrderlineID]',
                                       'Documents.[Document Type]_to': 'Documents.[Document Type]_from',
                                       'Map Original Orderline ID_to': 'Map Original Orderline ID_from'}, inplace=True)
df = pd.merge(df, MapOriginalOrderlineID, on = 'from.[Documents].[OrderlineID]', how='left')
df['from.[Documents].[OrderlineID]'] = df['Map Original Orderline ID_from'].fillna(df['from.[Documents].[OrderlineID]'])

df.drop(['Map Original Demand ID', 'Map Original Orderline ID_to', 'Map Original Orderline ID_from'],
        axis=1, inplace=True)

# Storing the input BUP Graph and other important inputs in a variable
BUP_FULL=df
ID=["InventoryDemand"]
InventoryDemand_req=df
InventoryDemand_req=InventoryDemand_req[InventoryDemand_req['to.[Demand].[DemandID]'].isin(ID)]

#createUseMap(MaterialConsumption, MaterialProduction)

#level=whereUse_map()
level = createUseMap()

logger.warn(f'level : {level}')

concat_list=list(level.keys())


# Calling the preprocessing function for df
df=preprocessing(df,concat_list)

df = fn_infinite_material_node_process(df)

logger.warning("Python Execution started for MPI Report Generation")

# Calling the preprocessing function for BUP_FULL
BUP_FULL=preprocessing(BUP_FULL,concat_list)

# Calling the Cons_RoutingID and data_PlannedConsEndDate functions for df
df=Cons_RoutingID(df)
df=data_PlannedConsEndDate(df)

BUP_Input=df

BUP_Input=data_PlannedConsEndDate(BUP_Input)

# Calling the Prod_RoutingID function for BUP_Input
Prod_RoutingID(BUP_Input)
    
# Calling the PlannedConsStartDate function for BUP_Input
PlannedConsStartDate(BUP_Input)

# Calling the PlannedProdStartDate function for BUP_Input
PlannedProdStartDate(BUP_Input)

# Calling the PlannedProdEndDate function for BUP_Input
PlannedProdEndDate(BUP_Input)


# Making necessary modifications in BUP_Input
#@@20241120 BUP_Input=BUP_Input[BUP_Input['from.[Item].[Item]']==BUP_Input['to.[To Item].[To Item]']]
#@@20241120 BUP_Input=BUP_Input[BUP_Input['from.[Location].[Location]']==BUP_Input['to.[To Location].[To Location]']]

# Calling the WorkOrderNumber function for BUP_Input
WorkOrderNumber(BUP_Input)

# Calling the PeggingIDs function for BUP_Input
PeggingIDs(BUP_Input)

# Calling the out_df function for BUP_Input
BUP_OUT=out_df(BUP_Input,0,InventoryDemand_req,Activity_LeadTime)

# Appending the results in BUP_OUT in the Empty dataframe BUPFULL_OUT
BUPFULL_OUT=pd.concat([BUPFULL_OUT,BUP_OUT],ignore_index=False)

# Adding Sequence Column in BUPFULL_OUT and dropping the PEGGINGID column in BUP_OUT
BUPFULL_OUT.reset_index(inplace=True)


BUPFULL_OUT['[Sequence].[Sequence]']=BUPFULL_OUT.index + Min_Seq + 1
BUP_OUT.drop('EXP_Material_Pegging_Info_PEGGINGID',axis=1,inplace=True)


# Repositioning the columns in BUPFULL_OUT
l = ['Version.[Version Name]', 'Location.[Location]', 'Item.[Item]', '[Sequence].[Sequence]', 'Exp MPI_CONSLOTNUMBER',
     'Exp MPI_CONSROUTINGID', 'Exp MPI_CONSROUTINGID_DIST', 'Exp MPI_CONSWORKORDERNUMBER', 'Exp MPI_DEMANDSTARTDATE',
     'Exp MPI_ORDERID', 'Exp MPI_PLANNEDCONSENDDATE', 'Exp MPI_PLANNEDCONSSTARTDATE', 'Exp MPI_PLANNEDPRODENDDATE',
     'Exp MPI_PLANNEDPRODSTARTDATE', 'Exp MPI_PRODLOTNUMBER', 'Exp MPI_PRODROUTINGID', 'Exp MPI_PRODWORKORDERNUMBER',
     'Exp MPI_QTY', 'Exp MPI_SALESLEVEL', 'Exp MPI_TOITEM', 'Exp MPI_TOSITEID', 'Exp MPI_SALESID',
     'to.[Activity2].[Activity Type2]', 'Documents.[Document Type]_from', 'Documents.[Document Type]_to',
     'to_to_siteid', 'To Site SALESID']
BUPFULL_OUT=BUPFULL_OUT[l]


# Changing string in MPI_CONSROUTINGID in BUPFULL_OUT
BUPFULL_OUT['Exp MPI_CONSROUTINGID'] = (
    BUPFULL_OUT['Exp MPI_CONSROUTINGID'].str.replace('DeliveryActivity', 'Deliver', regex=False))


# Changing string in MPI_PRODROUTINGID in BUPFULL_OUT
BUPFULL_OUT['Exp MPI_PRODROUTINGID'] = (
    BUPFULL_OUT['Exp MPI_PRODROUTINGID'].str.replace('BOHActivity', 'Add-to', regex=False))
BUPFULL_OUT['Exp MPI_PRODROUTINGID'] = (
    BUPFULL_OUT['Exp MPI_PRODROUTINGID'].str.replace('ExpectedReceiptActivity', 'Intransit', regex=False))



############### Week to First Day ###############
BUPFULL_OUT[['Exp MPI_PLANNEDCONSENDDATE', 'Exp MPI_PLANNEDCONSSTARTDATE', 'Exp MPI_PLANNEDPRODENDDATE',
             'Exp MPI_PLANNEDPRODSTARTDATE', 'Exp MPI_DEMANDSTARTDATE'
             ]] = (
    BUPFULL_OUT[['Exp MPI_PLANNEDCONSENDDATE', 'Exp MPI_PLANNEDCONSSTARTDATE', 'Exp MPI_PLANNEDPRODENDDATE',
                 'Exp MPI_PLANNEDPRODSTARTDATE', 'Exp MPI_DEMANDSTARTDATE']].fillna('0').astype(int))

BUPFULL_OUT[['Exp MPI_PLANNEDCONSENDDATE', 'Exp MPI_PLANNEDCONSSTARTDATE', 'Exp MPI_PLANNEDPRODENDDATE',
             'Exp MPI_PLANNEDPRODSTARTDATE', 'Exp MPI_DEMANDSTARTDATE']] = (
    BUPFULL_OUT[['Exp MPI_PLANNEDCONSENDDATE', 'Exp MPI_PLANNEDCONSSTARTDATE', 'Exp MPI_PLANNEDPRODENDDATE',
                 'Exp MPI_PLANNEDPRODSTARTDATE', 'Exp MPI_DEMANDSTARTDATE']].astype(str))

WeektoFirstDay = pd.Series(Week_Day['Time.[Day]'].values, index=Week_Day['Time.[Week]']).to_dict()

BUPFULL_OUT[['Exp MPI_PLANNEDCONSENDDATE', 'Exp MPI_PLANNEDCONSSTARTDATE', 'Exp MPI_PLANNEDPRODENDDATE',
             'Exp MPI_PLANNEDPRODSTARTDATE', 'Exp MPI_DEMANDSTARTDATE']] = (
    BUPFULL_OUT[['Exp MPI_PLANNEDCONSENDDATE', 'Exp MPI_PLANNEDCONSSTARTDATE', 'Exp MPI_PLANNEDPRODENDDATE',
                 'Exp MPI_PLANNEDPRODSTARTDATE', 'Exp MPI_DEMANDSTARTDATE']].replace(WeektoFirstDay))
 
# Updating the Exp MPI_PLANNEDPRODSTARTDATE in BUPFULL_OUT
# Add-to : BOH, Intransit : ER
mask_prod_start = (
    (BUPFULL_OUT['Exp MPI_PLANNEDPRODSTARTDATE']=="0") &
    (
        BUPFULL_OUT['Exp MPI_PRODROUTINGID'].str.startswith('Add-to') |
        BUPFULL_OUT['Exp MPI_PRODROUTINGID'].str.startswith('Intransit') |
        BUPFULL_OUT['Exp MPI_PRODROUTINGID'].str.startswith('RT_')
    )
)


# Updating the Exp MPI_PLANNEDCONSENDDATE in BUPFULL_OUT
mask_cons_end = (
    (BUPFULL_OUT['Exp MPI_PLANNEDCONSENDDATE']=="0") & 
    (
        BUPFULL_OUT['Exp MPI_CONSROUTINGID'].str.startswith('Deliver') |
        BUPFULL_OUT['Exp MPI_CONSROUTINGID'].str.startswith('RT_')
    )
)


# Apply the mask_prod_start function to update the 'Exp MPI_PLANNEDPRODSTARTDATE' column in BUPFULL_OUT
BUPFULL_OUT['Exp MPI_PLANNEDPRODSTARTDATE'] = (
    np.where(mask_prod_start, BUPFULL_OUT['Exp MPI_PLANNEDPRODENDDATE'], BUPFULL_OUT['Exp MPI_PLANNEDPRODSTARTDATE']))


# Apply the mask_cons_end function to update the 'Exp MPI_PLANNEDCONSENDDATE' column in BUPFULL_OUT
BUPFULL_OUT['Exp MPI_PLANNEDCONSENDDATE'] = (
    np.where(mask_cons_end, BUPFULL_OUT['Exp MPI_PLANNEDCONSSTARTDATE'], BUPFULL_OUT['Exp MPI_PLANNEDCONSENDDATE']))


# Adding the Exp MPI_SALESNAME column in Supplier Status report
SalesStd2.rename(columns={'Sales Domain.[Customer Group]': 'Exp MPI_SALESLEVEL'},inplace=True)
BUPFULL_OUT['Exp MPI_SALESLEVEL'] = BUPFULL_OUT['Exp MPI_SALESLEVEL'].astype(str)
SalesStd2['Exp MPI_SALESLEVEL'] = SalesStd2['Exp MPI_SALESLEVEL'].astype(str)
BUPFULL_OUT_new = pd.merge(BUPFULL_OUT, SalesStd2, on = 'Exp MPI_SALESLEVEL', how='left')
BUPFULL_OUT = BUPFULL_OUT_new
BUPFULL_OUT.rename(columns={'Sales Domain.[Sales Std2]': 'Exp MPI_SALESNAME'},inplace=True)
logger.warning("Python Execution ended for MPI Report Generation")

logger.warning("Python Execution started for Distribution Report Generation")

BUPFULL_OUT['ActivityType'] = BUPFULL_OUT['to.[Activity2].[Activity Type2]']

l = ['Version.[Version Name]', 'Location.[Location]', 'Item.[Item]', '[Sequence].[Sequence]', 'Exp MPI_CONSLOTNUMBER',
     'Exp MPI_CONSROUTINGID', 'Exp MPI_CONSROUTINGID_DIST', 'Exp MPI_CONSWORKORDERNUMBER', 'Exp MPI_DEMANDSTARTDATE',
     'Exp MPI_ORDERID', 'Exp MPI_PLANNEDCONSENDDATE', 'Exp MPI_PLANNEDCONSSTARTDATE', 'Exp MPI_PLANNEDPRODENDDATE',
     'Exp MPI_PLANNEDPRODSTARTDATE', 'Exp MPI_PRODLOTNUMBER', 'Exp MPI_PRODROUTINGID', 'Exp MPI_PRODWORKORDERNUMBER',
     'Exp MPI_QTY', 'Exp MPI_SALESLEVEL', 'Exp MPI_TOITEM', 'Exp MPI_TOSITEID', 'Exp MPI_SALESID', 'Exp MPI_SALESNAME',
     'ActivityType', 'to.[Activity2].[Activity Type2]', 'Documents.[Document Type]_from',
     'Documents.[Document Type]_to', 'to_to_siteid', 'To Site SALESID']
BUPFULL_OUT=BUPFULL_OUT[l]

# Adding Exp MPI_GBM column and dropping the unnecessary column from BUPFULL_OUT
# BUPFULL_OUT = pd.merge(BUPFULL_OUT, GBM, on = 'Item.[Item]', how = 'left')
# BUPFULL_OUT['Exp MPI_GBM']=BUPFULL_OUT['Item.[GBM]']
# BUPFULL_OUT.drop('Item.[GBM]', axis=1, inplace = True)

logger.warning("Python Execution started for Supplier Status Report Generation")

# Calling the supstatus function to BUPFULL_OUT to generate the Supplier Status Report and store the result in BUP_SUPSTATUS dataframe
BUP_SUPSTATUS=supstatus(BUPFULL_OUT)


# Renaming the columns in BUP_SUPSTATUS
rename(BUP_SUPSTATUS)

logger.warning("Python Execution ended for Supplier Status Report Generation")


BUPFULL_OUT.drop("Documents.[Document Type]_from",axis=1,inplace=True)
BUPFULL_OUT.drop("Documents.[Document Type]_to",axis=1,inplace=True)

#@@20241120 masking = BUPFULL_OUT['Exp MPI_ORDERID'] == 'InventoryDemand'

# BUPFULL_OUT = BUPFULL_OUT[~(masking & BUPFULL_OUT[['Item.[Item]', 'Location.[Location]', 'Exp MPI_CONSLOTNUMBER']].duplicated(keep = False))]
# BUPFULL_OUT = pd.concat([BUPFULL_OUT[masking].drop_duplicates(subset=['Item.[Item]', 'Location.[Location]', 'Exp MPI_CONSLOTNUMBER'],keep = 'first'), BUPFULL_OUT[~masking]])

#df_inv_demand = BUPFULL_OUT[masking].drop_duplicates(subset=['Item.[Item]', 'Location.[Location]', 'Exp MPI_CONSLOTNUMBER'],keep = 'first')
#df_filtered = BUPFULL_OUT[~(masking & BUPFULL_OUT[['Item.[Item]', 'Location.[Location]', 'Exp MPI_CONSLOTNUMBER']].duplicated(keep = False))]
#BUPFULL_OUT = pd.concat([df_inv_demand, df_filtered])

# Calling the DistributionPlan function that generates the Distribution Report
BUP_DISTRIBUTIONPLAN=DistributionPlan(BUPFULL_OUT)

BUP_DISTRIBUTIONPLAN['Version.[Version Name]'] = BUP_SUPSTATUS['Version.[Version Name]']
posit = ['Version.[Version Name]', 'Item.[Item]', 'Location.[Location]', '[Sequence].[Sequence]',
         'Exp Dist Plan All_GBM', 'Exp Dist Plan All_DISTRIBUTIONORDERID', 'Exp Dist Plan All_BODNAME',
         'Exp Dist Plan All_PLANNEDDELIVERYDATE', 'Exp Dist Plan All_PLANNEDSHIPMENTDATE',
         'Exp Dist Plan All_QTYPLANNED', 'Exp Dist Plan All_SALESID', 'Exp Dist Plan All_RELEASEDPLAN',
         'Exp Dist Plan All_Item', 'Exp Dist Plan All_TOSITEID', 'Exp Dist Plan All_TYPE']

BUP_DISTRIBUTIONPLAN=BUP_DISTRIBUTIONPLAN[posit]

logger.warning("Python Execution ended for Distribution Report Generation")

# Adding Exp MPI_GBM column and dropping the unnecessary column from BUPFULL_OUT
BUPFULL_OUT['Exp MPI_GBM']="VD"
BUPFULL_OUT['Exp MPI_TYPE']= MPI_TYPE
BUPFULL_OUT.drop("to.[Activity2].[Activity Type2]",axis=1,inplace=True)
BUPFULL_OUT.drop("Exp MPI_CONSROUTINGID_DIST",axis=1,inplace=True)
# BUPFULL_OUT.drop("Documents.[Document Type]_from",axis=1,inplace=True)
# BUPFULL_OUT.drop("Documents.[Document Type]_to",axis=1,inplace=True)
BUPFULL_OUT.drop("ActivityType",axis=1,inplace=True)

#####2024.12.24
BUPFULL_OUT.drop("to_to_siteid", axis=1, inplace=True)
BUPFULL_OUT.drop('To Site SALESID', axis=1, inplace=True)

BUPFULL_OUT['Exp MPI_PLANNEDPRODSTARTDATE'] = BUPFULL_OUT['Exp MPI_PLANNEDPRODSTARTDATE'].replace('0', np.nan)
BUPFULL_OUT['Exp MPI_PLANNEDCONSSTARTDATE'] = BUPFULL_OUT['Exp MPI_PLANNEDCONSSTARTDATE'].replace('0', np.nan)
BUPFULL_OUT['Exp MPI_DEMANDSTARTDATE'] = BUPFULL_OUT['Exp MPI_DEMANDSTARTDATE'].replace('0', np.nan)
BUPFULL_OUT['Exp MPI_PLANNEDCONSENDDATE'] = BUPFULL_OUT['Exp MPI_PLANNEDCONSENDDATE'].replace('0', np.nan)
BUPFULL_OUT['Exp MPI_PLANNEDCONSSTARTDATE'] = BUPFULL_OUT['Exp MPI_PLANNEDCONSSTARTDATE'].replace('0', np.nan)
BUP_DISTRIBUTIONPLAN['Exp Dist Plan All_PLANNEDDELIVERYDATE'] = (
    BUP_DISTRIBUTIONPLAN['Exp Dist Plan All_PLANNEDDELIVERYDATE'].replace('0', np.nan))

BUPFULL_OUT['Exp MPI_CONSLOTNUMBER'] = np.where(
        BUPFULL_OUT['Exp MPI_CONSLOTNUMBER'].str.startswith("000SCS_LOT"),
        BUPFULL_OUT['Exp MPI_CONSWORKORDERNUMBER'], BUPFULL_OUT['Exp MPI_CONSLOTNUMBER']+'_'+BUPFULL_OUT['Exp MPI_CONSWORKORDERNUMBER'].astype(str))


logger.debug("Started Nulling the Zeroes")    
# Logging the End time of Plugin
logger.warn(len(BUP_DISTRIBUTIONPLAN.index))
logger.warn("BUP_DISTRIBUTIONPLAN: {}".format(BUP_DISTRIBUTIONPLAN.head()))
logger.warn(len(BUP_SUPSTATUS.index))
logger.warn("BUP_SUPSTATUS: {}".format(BUP_SUPSTATUS.head()))
logger.warn(len(BUPFULL_OUT.index))
logger.warn(f'len org : {len(BUPFULL_OUT)}')
logger.warn("BUPFULL_OUT: {}".format(BUPFULL_OUT.head()))


# Parsing the output of the entire plugin in 3 different Measure Groups using the 3 different dataframes such as 'BUPFULL_OUT', 'BUP_DISTRIBUTIONPLAN' and 'BUP_SUPSTATUS'
O9DataLake.put("BUP_DISTRIBUTIONPLAN", BUP_DISTRIBUTIONPLAN)
O9DataLake.put("BUP_SUPSTATUS", BUP_SUPSTATUS)
O9DataLake.put("BUPFULL_OUT", BUPFULL_OUT)

import io
import boto3
import pyarrow as pa
import pyarrow.parquet as pq
from botocore.client import Config

Hub_S3_ACCESS_KEY = "6b2bd771fad4da6c2eaf"
Hub_S3_SECRET_KEY = "608fe10e82470ba519a27000"
hub_BASE_PATH = "VD/o9_in/mg/ui"
hub_bucket = "nscm-bdh-qa-obj-data"
S3Region = "skr-west-1"
S3Endpoint = "https://obj1.skr-west-1.samsungsdscloud.com:8443"


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

hub_s3 = get_s3_clients()

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

save_dataframe_to_s3(
    BUP_DISTRIBUTIONPLAN,
    hub_bucket,
    f"{hub_BASE_PATH}/BUP_DISTRIBUTIONPLAN1.parquet",
    hub_s3,
)
save_dataframe_to_s3(
    BUP_SUPSTATUS,
    hub_bucket,
    f"{hub_BASE_PATH}/BUP_SUPSTATUS1.parquet",
    hub_s3,
)
save_dataframe_to_s3(
    BUPFULL_OUT,
    hub_bucket,
    f"{hub_BASE_PATH}/BUPFULL_OUT1.parquet",
    hub_s3,
)

OutputCheck = InputCheck

logger.warn("OutputCheck : {}".format(OutputCheck.head()))

logger.info(memory_usage('@@@@@@@@@@@@@@@    Export MPI Data Memory')[0])
endTime = time.time()
logger.warning(f'END({endTime}): {endTime - initTime} secs')


