import pandas as pd
import traceback
from NSCMCommon import NSCMCommon as common

########################################################################################################################
# Local 개발 시에 필요한 공통 변수 선언
########################################################################################################################
# o9에 저장된 instanceName
str_instance = 'PY_UI_CopyPOPriceWeekly'
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
            
    ################################################################################################################
    # 전처리 : 모듈 내에서 사용될 input table load
    ################################################################################################################
    logger.Step(p_step_no=200, p_step_desc=f'=====> Input table load')
    
    
    
    # 데이터 파일 읽기
    if is_local:
                
        user_table= read_csv_file("user_table")
        data_table= read_csv_file("data_table")
          

    if user_table.empty:
        raise Exception("=====> raise Exception: user_table is empty")
    
    if data_table.empty:
        raise Exception("=====> raise Exception: data_table is empty")

          
    # DATA TYPE 설정
    
    # input dataframe 확인용 로그
    
    logger.PrintDF(p_df=user_table, p_df_name='user_table', p_log_level=common.G_log_level.debug(), p_format=1) 
    logger.PrintDF(p_df=data_table, p_df_name='data_table', p_log_level=common.G_log_level.debug(), p_format=1)
    logger.Step(p_step_no=290, p_step_desc=f'=====> Input table load End')
    
    ################################################################################################################
    # STEP 1 : Rename columns and Create a list of columns to process for comparision
    ################################################################################################################
    logger.Step(p_step_no=300, p_step_desc=f'=====> STEP 1 : Rename columns and Create a list of columns to process for comparision')
 

    # STEP1-1 - Rename columns
    user_table = user_table.rename(columns={'Product Price M_PO Price': 'PO','Product Price M_PO Price Week1': 'W1', 'Product Price M_PO Price Week2': 'W2', 'Product Price M_PO Price Week3': 'W3', 'Product Price M_PO Price Week4': 'W4', 'Product Price M_PO Price Week5': 'W5'})

    data_table = data_table.rename(columns={'Product Price M_PO Price Temp': 'PO', 'Product Price M_PO Price Week1 Temp': 'W1', 'Product Price M_PO Price Week2 Temp': 'W2', 'Product Price M_PO Price Week3 Temp': 'W3', 'Product Price M_PO Price Week4 Temp': 'W4', 'Product Price M_PO Price Week5 Temp': 'W5'})

    #Step 1-2: Create a list of columns to process
    delta_cols = ['PO', 'W1', 'W2', 'W3', 'W4','W5']
        
    logger.Step(p_step_no=310, p_step_desc=f'=====> STEP 1 : Rename columns and Create a list of columns to process for comparision End')
    
    
    ################################################################################################################
    # STEP 2 : Identify changes made by the user and create  a change_list
    ################################################################################################################
    logger.Step(p_step_no=400, p_step_desc=f'=====> STEP 2 :  Identify changes made by the user and create  a change_list create')
    
    #Step 2-1: Identify the changes made by the user
    change_list = []

    for idx, row in data_table.iterrows():
        for col in delta_cols:
            if user_table.loc[idx, col] != row[f'{col}']:
                change_list.append({
                'Index': idx,
                'Version.[Version Name]': row['Version.[Version Name]'],
                'Item.[Item]': row['Item.[Item]'],
                'Location.[Location]': row['Location.[Location]'],
                'Sub Location.[Sub Location]': row['Sub Location.[Sub Location]'],
                'Time.[Planning Month]': row['Time.[Planning Month]'],
                'Column': col,
                'Value': user_table.loc[idx, col]})

    #Step 2-2: Setting index for data table
    columns_index = list(set(user_table.columns) - set(delta_cols))
    data_table.set_index(columns_index, inplace=True)
        

    logger.PrintDF(p_df=data_table, p_df_name='data_table', p_log_level=common.G_log_level.debug(), p_format=1)
    logger.Step(p_step_no=410, p_step_desc=f'=====> STEP 2 : Identify changes made by the user and create  a change_list End')


    ################################################################################################################
    # STEP 3 : Loop through change_list and apply the changes based on the change_list
    ################################################################################################################
    logger.Step(p_step_no=500, p_step_desc=f'=====> STEP 3 : Loop through change_list and apply the changes based on the change_list Create')
    
    #Step 3-1: Filter out the specific combination of the 5 dimensions
    for change in change_list:
     filter_mask = ((user_table['Version.[Version Name]'] == change['Version.[Version Name]']) &
        (user_table['Item.[Item]'] == change['Item.[Item]']) &
        (user_table['Location.[Location]'] == change['Location.[Location]']) &
        (user_table['Sub Location.[Sub Location]'] == change['Sub Location.[Sub Location]']))

      # Get the index positions where the filter applies
     filtered_df = user_table[filter_mask].reset_index()
    
      # Get the row index based on the'Time.[Planning Month]' condition
     row_idx = filtered_df.loc[filtered_df['Time.[Planning Month]'] == change['Time.[Planning Month]']].index[0]
    
     #Step 3-2: Apply the changes to the specific cell and subsequent cells
     col_idx = filtered_df.columns.get_loc(change['Column'])
     col_idx_2 = filtered_df.columns.get_loc('PO') 


     filtered_df.iloc[row_idx:, col_idx+1:] = change['Value']
     filtered_df.iloc[row_idx+1:, col_idx_2:] = change['Value']

     #Step 3-3:Set index of filtered_df to columns_index and apply changes
     filtered_df.set_index(columns_index, inplace=True)
     data_table.loc[filtered_df.index,delta_cols ] = filtered_df[delta_cols]

    

    logger.PrintDF(p_df=data_table, p_df_name='data_table', p_log_level=common.G_log_level.debug(), p_format=1)
    logger.Step(p_step_no=510, p_step_desc=f'=====> STEP 3 : Loop through change_list and apply the changes based on the change_list End')
     
    ################################################################################################################
    # STEP 4 : Reset and rename of column for final output
    ################################################################################################################
    logger.Step(p_step_no=800, p_step_desc=f'=====> STEP 4 : Reset and rename of column for final output')

 
    #Step 4-1:Reset index of data_table for output
    Output_table = data_table.reset_index()
    Output_table_data = data_table.reset_index()

    #Step 4-2:Rename columns of output table
    Output_table = Output_table.rename(columns={'PO':'Product Price M_PO Price','W1' : 'Product Price M_PO Price Week1','W2' : 'Product Price M_PO Price Week2','W3' : 'Product Price M_PO Price Week3','W4' : 'Product Price M_PO Price Week4','W5' : 'Product Price M_PO Price Week5'})

    Output_table_data= Output_table_data.rename(columns={'PO':'Product Price M_PO Price Temp','W1' : 'Product Price M_PO Price Week1 Temp','W2' : 'Product Price M_PO Price Week2 Temp','W3' : 'Product Price M_PO Price Week3 Temp','W4' : 'Product Price M_PO Price Week4 Temp','W5' : 'Product Price M_PO Price Week5 Temp'})
 

    logger.PrintDF(p_df=Output_table  , p_df_name='Output_table ', p_log_level=common.G_log_level.debug(), p_format=1)
    logger.PrintDF(p_df=Output_table_data , p_df_name='Output_table_data', p_log_level=common.G_log_level.debug(), p_format=1)
    logger.Step(p_step_no=810, p_step_desc=f'=====> STEP 4 : Final output table create End')


    if is_local:
        logger.Step(p_step_no=821, p_step_desc=f'=====> Output csv create')
        save_csv_file(Output_table , 'Output_table ')
    
    row_count, col_count = Output_table.shape
    logger.Note(p_note=f'=====> Output_table rows : {row_count}, column : {col_count}', p_log_level=common.G_log_level.debug())
    
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