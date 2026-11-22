############################################################################################################################################
# plugin : PY_UI_MatlBODApply

# Input Query :
# 1. bod_top :
"""
Select ([Version].[Version Name].[CWV_MP] * [Item Material].[MSL1].[Panel] *&NSUILocVendorBODView * &MDMHorizon *&NSUIMtrlMSL3View  * &NSUISubLocationMFMtrlView * &NSUITransModeMtrlView ) on row,  ({Measure.[BOD List Mtrl W_Factory Out], Measure.[BOD List Mtrl W_GR LT], Measure.[BOD List Mtrl W_Intransit LT], Measure.[BOD List Mtrl W_Port To Port], Measure.[BOD List Mtrl_EFF Startdate], Measure.[BOD List Mtrl_EFF Enddate],Measure.[BOD List Mtrl_Lot Type] }) on column ;"""

# 2. bod_bottom :
"""
Select ([Version].[Version Name].[CWV_MP] *&NSUILocVendorBODView *&NSUIMtrlMSL3View  *&NSUISubLocationMFMtrlView * &NSUITransModeMtrlView * &NSUIMtrlItemView * {Measure.[BOD Item Mtrl_Lock Flag],Measure.[BOD Item Mtrl W_Factory Out],Measure.[BOD Item Mtrl W_GR LT], Measure.[BOD Item Mtrl W_Intransit LT],Measure.[BOD Item Mtrl W_Port To Port], Measure.[BOD Item Mtrl W_Supplier]});
"""
# 3. vendor :
"""
Select ([Version].[Version Name].[CWV_MP] * [Location].[Location] * [Item Material].[MSL1].[Panel]  * [Item Material].[MSL3]* &NSUIMtrlItemView  * [Global Top].[GT Code]  ) on row, 
({Measure.[Vendor Mtrl_GT Name], Measure.[Vendor Mtrl_Master Ecp Flag], Measure.[Vendor Mtrl_Master Flag], Measure.[Vendor Mtrl_Quota], Measure.[Vendor Mtrl_Result Ecp Flag], Measure.[Vendor Mtrl_Result Flag]}) on column;
"""
# 4. lock : 
"""
Select ([Item Material].[MSL1].[Panel]* [Location].[Location]  * [Item Material].[MSL3]  * [Sub Location].[Sub Location] * [Trans Mode].[Trans Mode] * [Item Material].[Item Material] ) on row,       ({Measure.[BOD Item Mtrl_Lock Flag]}) on column where {[Version].[Version Name].[CWV_MP] , [Location].[Location],Measure.[BOD Item Mtrl_Lock Flag] in {"Y"}};
"""
# 5. lotsize
"""
Select ([Version].[Version Name].[CWV_MP]  * [Item Material].[Item Material] ) on row, ({Measure.[Mtrl Attr_20FT], Measure.[Mtrl Attr_40FT], Measure.[Mtrl Attr_40FT HC], Measure.[Mtrl Attr_Pallet]}) on column;
"""

# Plugin Execution :
"""
EXEC plugin instance [PY_UI_MatlBODApply] 
        for measures {[BOD Item Mtrl W_Factory Out],[BOD Item Mtrl W_GR LT],[BOD Item Mtrl W_Port To Port],[BOD Item Mtrl_EFF Startdate],[BOD Item Mtrl_EFF Enddate],[BOD Item Mtrl_Lock Flag],[BOD Item Mtrl_Lot Type],[BOD Item Mtrl_Lot Size]}
        using scope ([Version].[Version Name].[CWV_MP]) 
        using arguments {(ExecutionMode, "MediumWeight"), (MaxSliceTableCells, 2000000), (MaxConcurrency, 1 ), ([Param.o9_sys_log_level], "DEBUG")};
        
"""

###########################################################################################################################################

import os
import pandas as pd
import numpy as np
from o9_common_utils.O9DataLake import O9DataLake
import logging
logger = logging.getLogger('o9_logger')
pd.set_option('display.max_columns', 500)
pd.set_option('display.max_rows', 500)
pd.set_option('display.width', 170)
pd.set_option('display.float_format', lambda x: '{:,.3f}'.format(x))

logger.info("####################################### PY_UI_MatlBODApply plugin : Execution START ##############################################")

try:

    # ---------------- INPUT DATA ----------------
    bod_top_data = O9DataLake.get('bod_top')
    bod_bottom_data = O9DataLake.get('bod_bottom')
    vendor_data = O9DataLake.get('vendor')
    lock_data = O9DataLake.get('lock')
    lotsize_data = O9DataLake.get('lotsize')

    bod_top_df = pd.DataFrame(bod_top_data)
    bod_bottom_df = pd.DataFrame(bod_bottom_data)
    vendor_df = pd.DataFrame(vendor_data)
    lock_df = pd.DataFrame(lock_data)
    lotsize_df = pd.DataFrame(lotsize_data)

    logger.info('###########-------------------------------------STEP 1.1 : INPUT 1 : bod_top_df---------------------------------------------------')
    logger.info(bod_top_df)
    logger.info(bod_top_df.shape)
    logger.info('###########-------------------------------------STEP 1.2 : INPUT 2 : bod_bottom_df------------------------------------------------')
    logger.info(bod_bottom_df)
    logger.info(bod_bottom_df.shape)
    logger.info('###########-------------------------------------STEP 1.3 : INPUT 3 : vendor_df---------------------------------------------------')
    logger.info(vendor_df)
    logger.info(vendor_df.shape)
    logger.info('###########-------------------------------------STEP 1.4 : INPUT 4 : lock_df---------------------------------------------------')
    logger.info(lock_df)
    logger.info(lock_df.shape)
    logger.info('###########-------------------------------------STEP 1.5 : INPUT 5 : lotsize_df---------------------------------------------------')
    logger.info(lotsize_df)
    logger.info(lotsize_df.shape)

    # Early exit for empty DataFrames
    if bod_top_df.empty:
        logger.warning("###########---------------------------- bod_top_df is empty. No processing will be done.-----------------------------")
        raise ValueError("###########-------------------------  bod_top_df is empty ---------------------------------------------------------")

    if vendor_df.empty:
        logger.warning("###########------------------------ vendor_df is empty : No processing will be done.-----------------------------")
        raise ValueError("###########------------------------- vendor_df is empty ---------------------------------------------------------")

    if lotsize_df.empty:
        logger.warning("###########------------------------ lotsize_df is empty : No processing will be done.-----------------------------")
        raise ValueError("###########------------------------- lotsize_df is empty ---------------------------------------------------------")

    if bod_bottom_df.empty:
        logger.info("#############----------- bod_bottom_df is initially empty and will be created from bod_top_df-------------##########")

    # ---------------- COLUMN MAPPING ----------------
    top_column_mapping = {
        'Version.[Version Name]': 'Version Name',
        'Location.[Location]': 'GTCode',
        'Time.[Week]': 'Week',
        'Item Material.[MSL3]': 'MSL3',
        'Item Material.[MSL1]' : 'MSL1',
        'Sub Location.[Sub Location]': 'Location',
        'Trans Mode.[Trans Mode]': 'Trans Mode',
        'BOD List Mtrl W_Factory Out': 'BOD Item Mtrl W_Factory Out',
        'BOD List Mtrl W_GR LT': 'BOD Item Mtrl W_GR LT',
        'BOD List Mtrl W_Port To Port': 'BOD Item Mtrl W_Port To Port',
        'BOD List Mtrl_EFF Startdate' : 'BOD Item Mtrl_EFF Startdate',
        'BOD List Mtrl_EFF Enddate' : 'BOD Item Mtrl_EFF Enddate',
        'BOD List Mtrl_Lot Type' : 'BOD Item Mtrl_Lot Type'
    }

    bottom_column_mapping = {
        'Version.[Version Name]': 'Version Name',
        'Location.[Location]': 'Location',
        'Item Material.[Item Material]': 'Item Material',
        'Item Material.[MSL3]': 'MSL3',
        'Time.[Week]': 'Week',
        'Sub Location.[Sub Location]': 'Sub Location',
        'Trans Mode.[Trans Mode]': 'Trans Mode',
        'BOD Item Mtrl_Lock Flag' : 'BOD Item Mtrl_Lock Flag',
        'BOD Item Mtrl W_Factory Out': 'BOD Item Mtrl W_Factory Out',
        'BOD Item Mtrl W_GR LT': 'BOD Item Mtrl W_GR LT',
        'BOD Item Mtrl W_Port To Port': 'BOD Item Mtrl W_Port To Port'
    }

    vendor_column_mapping = {
        'Item Material.[MSL3]': 'MSL3',
        'Location.[Location]': 'Location',
        'Global Top.[GT Code]' : 'GTCode',
        'Item Material.[Item Material]': 'Item Material'
    }

    lock_column_mapping = {
        'Item Material.[MSL3]': 'MSL3',
        'Item Material.[MSL1]' : 'MSL1',
        'Item Material.[Item Material]': 'Item Material',
        'Sub Location.[Sub Location]': 'Location',
        'Trans Mode.[Trans Mode]': 'Trans Mode',
        'Location.[Location]': 'GTCode',
        'BOD Item Mtrl_Lock Flag' : 'BOD Item Mtrl_Lock Flag',
        
    }

    lotsize_column_mapping = {
        'Version.[Version Name]': 'Version Name',
        'Item Material.[Item Material]': 'Item Material',
        'Mtrl Attr_20FT' : '20FT',
        'Mtrl Attr_40FT' : '40FT',
        'Mtrl Attr_40FT HC' : '40FT HC',
        'Mtrl Attr_Pallet' : 'Pallet'
    }
    # ---------------- COLUMN RENAMING ----------------
    bod_top_df.rename(columns=top_column_mapping, inplace=True)
    bod_bottom_df.rename(columns=bottom_column_mapping, inplace=True)
    vendor_df.rename(columns=vendor_column_mapping, inplace=True)
    lock_df.rename(columns=lock_column_mapping, inplace=True)
    lotsize_df.rename(columns=lotsize_column_mapping, inplace=True)

    logger.info('###########-------------------------------------STEP 2.1 : Renaming column ---------------------------------------------------')
    logger.info(bod_top_df.head())
    logger.info(vendor_df.head())
    logger.info(lotsize_df.head())

    # Required columns
    vendor_df = vendor_df[['MSL3','Location','GTCode','Item Material']]
    lock_row_df = lock_df.drop(columns=['BOD Item Mtrl_Lock Flag','MSL1'])
    bod_top_df['BOD Item Mtrl_Lot Size'] = '-'
    bod_top_df = bod_top_df[['Version Name','GTCode','Week','MSL3','MSL1','Location','Trans Mode','BOD Item Mtrl W_Factory Out','BOD Item Mtrl W_GR LT','BOD Item Mtrl W_Port To Port','BOD Item Mtrl_EFF Startdate','BOD Item Mtrl_EFF Enddate','BOD Item Mtrl_Lot Type','BOD Item Mtrl_Lot Size']]
    lotsize_df = lotsize_df[['Item Material','20FT','40FT','40FT HC','Pallet']]

    # remove duplicates
    vendor_df.drop_duplicates()
    lock_row_df.drop_duplicates()
    bod_top_df.drop_duplicates()
    lotsize_df.drop_duplicates()
    
    bod_top_df.dropna(subset=['Version Name','Location','GTCode','Trans Mode','Week'], inplace=True)

    logger.info('###########-------------------------------------STEP 2.2 : Renaming completed ---------------------------------------------------')
    logger.info(bod_top_df.head())
    logger.info(vendor_df.head())
    logger.info(lotsize_df.head())

    # Merge using batching
    batch_size = 500
    num_batches = int(np.ceil(len(bod_top_df) / batch_size))

    merged_chunks = []

    for i in range(num_batches):
        # Slice the DataFrame into a batch
        top_batch = bod_top_df.iloc[i * batch_size:(i + 1) * batch_size]
        
        # Merge the batch with the vendor DataFrame
        merged_batch = top_batch.merge(vendor_df, on=["MSL3", "Location",'GTCode'], how="left")
 
        # Append the merged batch to the list
        merged_chunks.append(merged_batch)

    # Concatenate the merged batches into a single DataFrame
    merged_df = pd.concat(merged_chunks, ignore_index=True)
    merged_df.drop_duplicates()
    logger.info('###########----------------------------------STEP 3 : Merging Complete : merged_df (bod_top_df,vendor,left) ---------------------------------------')
    logger.info(merged_df)
    logger.info(merged_df.shape)

    # adding Lot Size wrt. Item material
    # Create a dictionary mapping
    lot_size_map = {
        '20FT': lotsize_df.set_index('Item Material')['20FT'].to_dict(),
        '40FT': lotsize_df.set_index('Item Material')['40FT'].to_dict(),
        '40FT HC': lotsize_df.set_index('Item Material')['40FT HC'].to_dict(),
        'Pallet': lotsize_df.set_index('Item Material')['Pallet'].to_dict()
    }

    # Update merged_df using the map
    def get_lot_size(row):
        item_material = row['Item Material']
        lot_type = row['BOD Item Mtrl_Lot Type']
        
        try:
            lot_size = lot_size_map[lot_type].get(item_material)
        except KeyError:
            lot_size = np.nan  # or any default value
        
        return lot_size

    merged_df['BOD Item Mtrl_Lot Size'] = merged_df.apply(get_lot_size, axis=1)
    merged_df['BOD Item Mtrl_Lot Size'] = merged_df['BOD Item Mtrl_Lot Size'].replace(np.nan, '-')
    logger.info('###########----------------------------------STEP 4 : Updated Lot Size wrt. Item Material : merged_df  ---------------------------------------')
    logger.info(merged_df.head())
    logger.info(merged_df.shape)


    if not bod_bottom_df.empty:
        logger.info('###########----------------------------------STEP 5 : Updating unlock rows  ------------------------------------')
        # Updating unlock rows
        key_cols = ['GTCode','Location','Trans Mode','MSL3','Item Material']

        lock_keys = set(tuple(row) for row in lock_row_df[key_cols].to_records(index=False))
        chunk_size = 1000
        chunks =[]

        for i in range(0, len(merged_df), chunk_size):
            chunk = merged_df.iloc[i:i + chunk_size].copy()
            chunk['key'] = list(zip(*[chunk[col] for col in key_cols]))
            filtered_chunk = chunk[~chunk['key'].isin(lock_keys)].drop(columns=['key'])
            chunks.append(filtered_chunk)
        
        updated_bod_bottom_df = pd.concat(chunks, ignore_index=True)
        updated_bod_bottom_df = updated_bod_bottom_df.copy()
        logger.info('###########----------------------------------STEP 6 : updated_bod_bottom_df  ------------------------------------')
        logger.info(updated_bod_bottom_df)

        # No processing when all rows are locked
        if updated_bod_bottom_df.empty:
            logger.warning("------------------------ All rows are Locked : No processing will be done.-----------------------------")
            raise ValueError("------------------------- All rows are Locked : No processing will be done ---------------------------------------------------------")

    else:
        logger.info('###########----------------------------------STEP 5 : bod_bottom_df is empty : Merging top + vendor ------------------------------')
        logger.info(merged_df.head())
        updated_bod_bottom_df = merged_df
        
        updated_bod_bottom_df = updated_bod_bottom_df.copy()

        logger.info('###########----------------------------------STEP 6 : updated_bod_bottom_df  ------------------------------------')
        logger.info(updated_bod_bottom_df)

    updated_bod_bottom_df.dropna(subset=['Version Name','Location','GTCode','Item Material','Trans Mode','Week'], inplace=True)

    # Renaming updated_bod_bottom_df
    updated_bod_bottom_df.rename(columns={
        'Version Name': '[Version].[Version Name]',
        'Location': '[Sub Location].[Sub Location]',
        'GTCode': '[Location].[Location]',
        'Item Material': '[Item Material].[Item Material]',
        'Trans Mode': '[Trans Mode].[Trans Mode]',
        'Week': '[Time].[Week]',
        'BOD Item Mtrl W_Factory Out' : 'BOD Item Mtrl W_Factory Out',
        'BOD Item Mtrl W_GR LT' : 'BOD Item Mtrl W_GR LT',
        'BOD Item Mtrl W_Port To Port' : 'BOD Item Mtrl W_Port To Port',
        'BOD Item Mtrl_EFF Startdate' : 'BOD Item Mtrl_EFF Startdate',
        'BOD Item Mtrl_EFF Enddate' : 'BOD Item Mtrl_EFF Enddate',
        'BOD Item Mtrl_Lot Type' : 'BOD Item Mtrl_Lot Type',
        'BOD Item Mtrl_Lot Size' : 'BOD Item Mtrl_Lot Size'
    }, inplace=True)

    # Set Flag default to "N"
    updated_bod_bottom_df['BOD Item Mtrl_Lock Flag'] = pd.Categorical(['N'] *  len(updated_bod_bottom_df), categories=['N'])
    
    logger.info('###########----------------------------------STEP 7 : Final Output updated_bod_bottom : renamed ---------------------------------------------------')
    logger.info(updated_bod_bottom_df)
    logger.info(updated_bod_bottom_df.shape)

    output_df = updated_bod_bottom_df[[
        '[Version].[Version Name]', 
        '[Sub Location].[Sub Location]', 
        '[Location].[Location]',
        '[Item Material].[Item Material]', 
        '[Trans Mode].[Trans Mode]', 
        '[Time].[Week]',
        'BOD Item Mtrl W_Factory Out',
        'BOD Item Mtrl W_GR LT', 
        'BOD Item Mtrl W_Port To Port',
        'BOD Item Mtrl_EFF Startdate',
        'BOD Item Mtrl_EFF Enddate',
        'BOD Item Mtrl_Lock Flag',
        'BOD Item Mtrl_Lot Type',
        'BOD Item Mtrl_Lot Size'
    ]]

    output_df.drop_duplicates()
    logger.info('-------------------------------------STEP 8 : Final bod_output_df ---------------------------------------------------')
    logger.info(output_df)
    logger.info(output_df.shape)

    bod_output_df = output_df.copy()



except Exception as e:
    logger.error("An error occurred: %s", str(e), exc_info=True)
finally:
    logger.info("####################################### PY_UI_MatlBODApply plugin : Execution END ##############################################")
