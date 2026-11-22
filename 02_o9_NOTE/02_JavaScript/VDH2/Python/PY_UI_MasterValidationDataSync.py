import pandas as pd
import numpy as np
import datetime
import traceback
from NSCMCommon import NSCMCommon as common

########################################################################################################################
# Local 개발 시에 필요한 공통 변수 선언
########################################################################################################################
# o9에 저장된 instanceName
str_instance = 'PY_UI_MtrlConstraintType'
is_local = common.gfn_get_isLocal()

########################################################################################################################
# log 설정 : PROGRAM file_name
########################################################################################################################
logger = common.G_Logger(p_py_name=str_instance)
common.gfn_set_local_logfile()


########################################################################################################################
# logic start
########################################################################################################################
def read_csv_file(file_name):
    return pd.read_csv(f"{file_name}.csv", encoding="UTF-8")


def save_csv_file(df, file_name):
    df.to_csv(f"{file_name}.csv", index=False)


logger.debug(f'[START] {str_instance}')
logger.Start()
logger.Step(p_step_no=0, p_step_desc=f'===================== plugin Execution Start =====================')

try:
    ################################################################################################################
    # DataFrame Column : 변수 처리
    ################################################################################################################
    logger.Step(p_step_no=100, p_step_desc=f'=====> DataFrame Column : 변수 처리')
    
    # 컬럼 변수 선언
    versionVersionName         = 'Version.[Version Name]'
    zzTimezzRelative_Week      = 'zzTime.[zzRelative_Week]'
    locationLocation           = 'Location.[Location]'
        
    ################################################################################################################
    # 전처리 : 모듈 내에서 사용될 input table load
    ################################################################################################################
    logger.Step(p_step_no=200, p_step_desc=f'=====> Input table load')
    
    
    
    # 데이터 파일 읽기
    if is_local:
                
        Attribute= read_csv_file("Attribute")
        ConstraintTV_1= read_csv_file("ConstraintTV_1")
        #ConstraintTV_2= read_csv_file("ConstraintTV_2")
        ConstraintTV_3= read_csv_file("ConstraintTV_3")
        ConstraintTV_4= read_csv_file("ConstraintTV_4")
        SupplyPlan_1= read_csv_file("SupplyPlan_1")
        SupplyPlan_2= read_csv_file("SupplyPlan_2")
        Current_1= read_csv_file("Current_1")
        Current_2= read_csv_file("Current_2")
        Current_3= read_csv_file("Current_3")
        Current_4= read_csv_file("Current_4")   

    if Attribute.empty:
        raise Exception("=====> raise Exception: Attribute is empty")
    
    if ConstraintTV_1.empty:
        raise Exception("=====> raise Exception: ConstraintTV_1 is empty")

    #if ConstraintTV_2.empty:
        #raise Exception("=====> raise Exception: ConstraintTV_2 is empty")
    
    if ConstraintTV_3.empty:
        raise Exception("=====> raise Exception: ConstraintTV_3 is empty")
     
    if ConstraintTV_4.empty:
        raise Exception("=====> raise Exception: ConstraintTV_4 is empty")
     
    if SupplyPlan_1.empty:
        raise Exception("=====> raise Exception: SupplyPlan_1 is empty") 

    if SupplyPlan_2.empty:
        raise Exception("=====> raise Exception: SupplyPlan_2 is empty")

    if Current_1.empty:
        raise Exception("=====> raise Exception: Current_1 is empty")

    if Current_2.empty:
        raise Exception("=====> raise Exception: Current_2 is empty")

    if Current_3.empty:
        raise Exception("=====> raise Exception: Current_3 is empty")

    if Current_4.empty:
        raise Exception("=====> raise Exception: Current_4 is empty")
       
      
    # DATA TYPE 설정
    
    # input dataframe 확인용 로그
    
    logger.PrintDF(p_df=Attribute, p_df_name='Attribute', p_log_level=common.G_log_level.debug(), p_format=1) 
    logger.PrintDF(p_df=ConstraintTV_1, p_df_name='ConstraintTV_1', p_log_level=common.G_log_level.debug(), p_format=1)
    #logger.PrintDF(p_df=ConstraintTV_2, p_df_name='ConstraintTV_2', p_log_level=common.G_log_level.debug(), p_format=1)
    logger.PrintDF(p_df=ConstraintTV_3, p_df_name='ConstraintTV_3', p_log_level=common.G_log_level.debug(), p_format=1)
    logger.PrintDF(p_df=ConstraintTV_4, p_df_name='ConstraintTV_4', p_log_level=common.G_log_level.debug(), p_format=1)
    logger.PrintDF(p_df=SupplyPlan_1, p_df_name='SupplyPlan_1', p_log_level=common.G_log_level.debug(), p_format=1)
    logger.PrintDF(p_df=SupplyPlan_2, p_df_name='SupplyPlan_2', p_log_level=common.G_log_level.debug(), p_format=1)
    logger.PrintDF(p_df=Current_1, p_df_name='Current_1', p_log_level=common.G_log_level.debug(), p_format=1)
    logger.PrintDF(p_df=Current_2, p_df_name='Current_2', p_log_level=common.G_log_level.debug(), p_format=1)
    logger.PrintDF(p_df=Current_3, p_df_name='Current_3', p_log_level=common.G_log_level.debug(), p_format=1)
    logger.PrintDF(p_df=Current_4, p_df_name='Current_4', p_log_level=common.G_log_level.debug(), p_format=1)
    logger.Step(p_step_no=290, p_step_desc=f'=====> Input table load End')
    
    ################################################################################################################
    # STEP 1 : Constraint Type - Time Varying Column
    ################################################################################################################
    logger.Step(p_step_no=300, p_step_desc=f'=====> STEP 1 : Create Time Varying column')
 

    # STEP1-1 - Find Time Varyinf data from the 4 measures
    ConstraintTV=pd.merge(ConstraintTV_1, ConstraintTV_3, on= ['Version.[Version Name]','Item Material.[Item Material]'], how='outer')
    ConstraintTV= ConstraintTV.reset_index(drop=True)

    ConstraintTV=pd.merge(ConstraintTV, ConstraintTV_4, on= ['Version.[Version Name]','Item Material.[Item Material]'], how='outer')
    ConstraintTV = ConstraintTV.reset_index(drop=True)
    

    #ConstraintTV=pd.merge(ConstraintTV, ConstraintTV_4, on= ['Version.[Version Name]','Item Material.[Item Material]'], how='outer')
    #ConstraintTV = ConstraintTV.reset_index(drop=True)


    cols_to_check = [col for col in ConstraintTV.columns if col not in ['Version.[Version Name]','Item Material.[Item Material]']]
    


    ConstraintTV[cols_to_check ]= ConstraintTV[cols_to_check ].replace('',pd.NA)
    ConstraintTV['Time varying']= ConstraintTV[cols_to_check].bfill(axis=1).iloc[:,0]
 
    ConstraintTV = ConstraintTV[['Version.[Version Name]','Item Material.[Item Material]','Time varying']]
       
        
    logger.PrintDF(p_df=ConstraintTV, p_df_name='ConstraintTV', p_log_level=common.G_log_level.debug(), p_format=1)
    logger.Step(p_step_no=310, p_step_desc=f'=====> STEP 1 : Constraint Type Time Varying create End')
    
    
    ################################################################################################################
    # STEP 2 : Supply Plan - Source Column
    ################################################################################################################
    logger.Step(p_step_no=400, p_step_desc=f'=====> STEP 2 : Supply Plan - Source Column create')
  
    SupplyPlan =SupplyPlan_1[['Version.[Version Name]','Item Material.[Item Material]','Supply Plan Source Map Ecp_Source']].drop_duplicates().groupby(['Version.[Version Name]','Item Material.[Item Material]'],as_index=False).first()
    SupplyPlan_2 = SupplyPlan_2[SupplyPlan_2['Supply Plan Source Map_Source'].notna() & (SupplyPlan_2['Supply Plan Source Map_Source'] !='')]

    SupplyPlan =pd.merge(SupplyPlan,SupplyPlan_2, on=['Version.[Version Name]','Item Material.[Item Material]'], how='outer')
 
    SupplyPlan['Source']= SupplyPlan['Supply Plan Source Map Ecp_Source'].combine_first(SupplyPlan['Supply Plan Source Map_Source'])

    SupplyPlan= SupplyPlan[['Version.[Version Name]','Item Material.[Item Material]','Source']]
 

    SupplyPlan= SupplyPlan[SupplyPlan['Source'].notna() & (SupplyPlan['Source'] !='')]
    logger.PrintDF(p_df=SupplyPlan, p_df_name='SupplyPlan', p_log_level=common.G_log_level.debug(), p_format=1)
    logger.Step(p_step_no=410, p_step_desc=f'=====> STEP 2 : Supply Plan - Source Column Create End')


    ################################################################################################################
    # STEP 3 : Constraint Current Column Create
    ################################################################################################################
    logger.Step(p_step_no=500, p_step_desc=f'=====> STEP 3 : Constraint Current Column Create')
    
    def determine_current(group):
     if 'Hard' in group.values:
         return 'Hard'
     elif 'Soft' in group.values:
         return 'Soft'
     else:
         return 'Un'
    

    Current_1_Grouped = Current_1.groupby(['Version.[Version Name]','Item Material.[Item Material]'], as_index=False).agg(Current=('Mtrl Const Type Item W_Type', determine_current))
    logger.PrintDF(p_df=Current_1_Grouped , p_df_name='Current_1_Grouped ', p_log_level=common.G_log_level.debug(), p_format=1)
    Current_2_Grouped = Current_2.groupby(['Version.[Version Name]','Item Material.[Item Material]'], as_index=False).agg(Current=('Mtrl Const Type L5 W_Type', determine_current))
    logger.PrintDF(p_df=Current_2_Grouped , p_df_name='Current_2_Grouped ', p_log_level=common.G_log_level.debug(), p_format=1)

    Current_4_Grouped = Current_4.groupby(['Version.[Version Name]','Item Material.[Item Material]'], as_index=False).agg(Current=('Mtrl Const Type L3 W_Type', determine_current))
    logger.PrintDF(p_df=Current_4_Grouped , p_df_name='Current_4_Grouped ', p_log_level=common.G_log_level.debug(), p_format=1)

    merged_df = pd.merge(Current_1_Grouped ,Current_2_Grouped ,on=['Version.[Version Name]','Item Material.[Item Material]'], how='outer', suffixes =('_df1','_df2'))
    merged_df['Current'] = merged_df['Current_df1'].combine_first(merged_df['Current_df2'])
    merged_df = merged_df[['Version.[Version Name]','Item Material.[Item Material]','Current']]
    logger.PrintDF(p_df=merged_df, p_df_name='merged_df', p_log_level=common.G_log_level.debug(), p_format=1)

    final_df= pd.merge(merged_df ,Current_3[['Version.[Version Name]','Item Material.[Item Material]','Mtrl Const Type L4 W_Type']] ,on=['Version.[Version Name]','Item Material.[Item Material]'], how='outer')
    final_df['Current'] = final_df['Current'].combine_first(final_df['Mtrl Const Type L4 W_Type'])
    final_df= final_df[['Version.[Version Name]','Item Material.[Item Material]','Current']]
    logger.PrintDF(p_df=final_df, p_df_name='final_df', p_log_level=common.G_log_level.debug(), p_format=1)

    final_df= pd.merge(final_df,Current_4_Grouped,on=['Version.[Version Name]','Item Material.[Item Material]'], how='outer', suffixes =('','_df4'))
    final_df['Current'] = final_df['Current'].combine_first(final_df['Current_df4'])
    final_df= final_df[['Version.[Version Name]','Item Material.[Item Material]','Current']]
     

    logger.PrintDF(p_df=final_df, p_df_name='final_df', p_log_level=common.G_log_level.debug(), p_format=1)
    
    ConstraintTV= pd.merge(ConstraintTV,final_df, on=['Version.[Version Name]','Item Material.[Item Material]'], how='outer')
    ConstraintTV['Current'] =  ConstraintTV['Current'].replace('', 'Un')
    ConstraintTV['Const Exception'] = "Y"
    
    logger.PrintDF(p_df=ConstraintTV, p_df_name='ConstraintTV', p_log_level=common.G_log_level.debug(), p_format=1)
    logger.Step(p_step_no=510, p_step_desc=f'=====> STEP 3 : Constraint Table create End')
     
    ################################################################################################################
    # STEP 9 : Output table Create
    ################################################################################################################
    logger.Step(p_step_no=800, p_step_desc=f'=====> STEP 9 : Final output table create')

 
    Output_Attributes = pd.DataFrame(Attribute)
 
    Output_Attributes  = Output_Attributes.rename(columns={'Mtrl Attr_CA3':'Valid Mtrl Item_CAttb03 Value','Mtrl Attr_CA2':'Valid Mtrl Item_CAttb02 Value','Mtrl Attr_CA1':'Valid Mtrl Item_CAttb01 Value','Mtrl Attr_SA1':'Valid Mtrl Item_SAttb01 Value','Mtrl Attr_SA2':'Valid Mtrl Item_SAttb02 Value','Mtrl Attr_SA3':'Valid Mtrl Item_SAttb03 Value','Mtrl Attr_SA4':'Valid Mtrl Item_SAttb04 Value','Mtrl Attr_SA5':'Valid Mtrl Item_SAttb05 Value','Mtrl Attr_SA6':'Valid Mtrl Item_SAttb06 Value','Mtrl Attr_SA7':'Valid Mtrl Item_SAttb07 Value','Mtrl Attr_CA4':'Valid Mtrl Item_CAttb04 Value','Mtrl Attr_Pallet':'Valid Mtrl Item_PALLET','Mtrl Attr_20FT':'Valid Mtrl Item_20 FT','Mtrl Attr_40FT':'Valid Mtrl Item_40 FT','Mtrl Attr_40FT HC':'Valid Mtrl Item_40 FTHC'})   

    Output_Constraint = pd.DataFrame(ConstraintTV)
    Output_Constraint = Output_Constraint.dropna()
    Output_Constraint = Output_Constraint.rename(columns={'Time varying':'Valid Mtrl Item_Const Time Varying','Const Exception':'Valid Mtrl Item_Const Exception','Current':'Valid Mtrl Item_Const Current'})   
    
    Output_SupplyPlan = pd.DataFrame(SupplyPlan)
    Output_SupplyPlan = Output_SupplyPlan.rename(columns={'Source':'Valid Mtrl Item_Supply Plan Source'}) 

    logger.PrintDF(p_df=Output_Attributes , p_df_name='Output_Attributes', p_log_level=common.G_log_level.debug(), p_format=1)
    logger.PrintDF(p_df=Output_Constraint , p_df_name='Output_Constraint', p_log_level=common.G_log_level.debug(), p_format=1)
    logger.PrintDF(p_df=Output_SupplyPlan , p_df_name='Output_SupplyPlan ', p_log_level=common.G_log_level.debug(), p_format=1)
    logger.Step(p_step_no=810, p_step_desc=f'=====> STEP 9 : Final output table create End')


    if is_local:
        logger.Step(p_step_no=821, p_step_desc=f'=====> Output csv create')
        save_csv_file(Output_Attributes, 'Output_Attributes')
    
    row_count, col_count = Output_Attributes.shape
    logger.Note(p_note=f'=====> Output_Attributes rows : {row_count}, column : {col_count}', p_log_level=common.G_log_level.debug())
    
    logger.Step(p_step_no=890, p_step_desc=f'=====> STEP 9-2 : End')
    
except Exception as e:
    trace_msg = traceback.format_exc()
    logger.Note(p_note=f'=====> try Exception : {trace_msg}', p_log_level=common.G_log_level.info())
    logger.Error()
    raise Exception(e)

else:
    logger.Step(p_step_no=900, p_step_desc=f'===================== plugin Execution End =====================')

finally:
    logger.Finish()