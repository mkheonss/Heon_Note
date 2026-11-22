######################################################################################################################################
### Plugin : 'PY_UI_PanelDual3IN1Date'

### Input :

# Report "Panel Dualization" data : 

"""
select([Version].[Version Name] *[Dash No].[Dash No]*[Dash No].[Project]*[Region].[Region]*[To Item].[To Item]*[Item].[Item]*[Item Material].[Item Material]*[Change Request].[CR No]) on row,({Measure.[Panel Dual Old_Open Cell], Measure.[Panel Dual New_Open Cell], Measure.[Panel Dual New_Intro Conference], Measure.[Panel Dual New_Get SET Sample], Measure.[Panel Dual New_Complete], Measure.[Panel Dual Progress_Complete HQ Plan], Measure.[Panel Dual Progress_Complete HQ Result], Measure.[Panel Dual Progress_Local BOM], Measure.[Panel Dual Progress_Plant], Measure.[Panel Dual Progress_3IN1 Exist], Measure.[Panel Dual Progress_Model code], Measure.[Panel Dual Progress_3IN1 New Code], Measure.[Panel Dual Progress_3IN1 Date System], Measure.[Panel Dual Progress_3IN1 Date], Measure.[Panel Dual Progress_3in1 Final], Measure.[Panel Dual Progress_Final Date]}) on column;
"""

# Week "LT_intransit" data  :

"""
Select ([Version].[Version Name] * [Location].[Location] ) on row, ({Measure.[Mtrl Plant LT_Intransit]}) on column;
"""

# Requirement :  

"""
1. Panel Dual Progress_Model code = Last 2 Digit of [To Item].[To Item]

2. For  : Panel Dual Progress_3IN1 Date System

        1. If [3IN1 Exist] = N, leave as Null
        2. If [3IN1 Exist] = Y, Add 4 Weeks as default to [Complete Date Result] and Add Weeks from Measure.[Mtrl Plant LT_Intransit ]
        → when find the weeks from Measure.[Mtrl Plant LT_Intransit], Please apply the Measure.[Panel Dual Progress_Plant] as Location.[Location] in Measure.[Mtrl Plant LT_Intransit]. If there are multi value in Measure.[Panel Dual Progress_Plant], please apply week(Intransit) which is Max. 

        2-1. In 2nd calculation, If [Complete Date Result] = null, apply [Complete Date Plan]
"""

# Plugin Execution : 

"""
EXEC plugin instance [PY_UI_PanelDual3IN1Date] for measures {[Panel Dual Progress_Model code],[Panel Dual Progress_3IN1 Date System]} using scope ([Version].[Version Name].[CWV_MP]) using arguments {(ExecutionMode, "MediumWeight"), (MaxSliceTableCells, 2000000), (MaxConcurrency, 1 ), ([Param.o9_sys_log_level], "DEBUG")};

"""

# Last update : 17-Jun-2025
# Reviewed By  : Amit Kumar  Date: 29th May-2025

######################################################################################################################################

import os
import pandas as pd
import numpy as np
from o9_common_utils.O9DataLake import O9DataLake
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('o9_logger')
pd.set_option('display.max_columns', 500)
pd.set_option('display.max_rows', 500)
pd.set_option('display.width', 170)
pd.set_option('display.float_format', lambda x: '{:,.3f}'.format(x))

logger.info("########################################## 'PY_UI_PanelDual3IN1Date' plugin : Execution START ##############################################")


try:
    # ---------------- INPUT DATA ----------------
    panel_data = O9DataLake.get('panel')
    intransit_data = O9DataLake.get('intransit')

    panel_df = pd.DataFrame(panel_data)
    intransit_df = pd.DataFrame(intransit_data)

    logger.info('###########-------------------------------------STEP 1.1 : INPUT 1 : panel_df---------------------------------------------------')
    logger.info(panel_df)
    logger.info(panel_df.shape)
    logger.info('###########-------------------------------------STEP 1.2 : INPUT 2 : intransit_df------------------------------------------------')
    logger.info(intransit_df)
    logger.info(intransit_df.shape)

    # ---------------- COLUMN MAPPING ----------------
    panel_column_mapping = {
        'Version.[Version Name]' : 'Version Name',
        'Dash No.[Dash No]' : 'Dash No',
        'Dash No.[Project]' : 'Project',
        'Region.[Region]' : 'Region',
        'To Item.[To Item]' : 'To Item',
        'Item.[Item]' : 'Item',
        'Item Material.[Item Material]' : 'Item Material',
        'Change Request.[CR No]' : 'CR No',
        'Panel Dual Progress_Complete HQ Plan' : 'Panel Dual Progress_Complete HQ Plan',
        'Panel Dual Progress_Complete HQ Result' : 'Panel Dual Progress_Complete HQ Result',
        'Panel Dual Progress_Plant' : 'Panel Dual Progress_Plant',
        'Panel Dual Progress_3IN1 Exist' : 'Panel Dual Progress_3IN1 Exist',
        'Panel Dual Progress_Model code' : 'Panel Dual Progress_Model code',
        'Panel Dual Progress_3IN1 Date System' : 'Panel Dual Progress_3IN1 Date System'
    } 

    intransit_column_mapping = {
        'Version.[Version Name]' : 'Version Name',
        'Location.[Location]' : 'Plant',
        'Mtrl Plant LT_Intransit' : 'Mtrl Plant LT_Intransit'
    }



    panel_df.rename(columns=panel_column_mapping, inplace=True)
    intransit_df.rename(columns=intransit_column_mapping, inplace=True)

    logger.info('###########-------------------------------------STEP 2.1 : Renaming column ---------------------------------------------------')
    logger.info(panel_df.head())
    logger.info(intransit_df.head())

    # remove duplicates
    panel_df.drop_duplicates()
    intransit_df.drop_duplicates()

    ###############################################################################################################################
    # Logic 1 : Panel Dual Progress_Model code = Last 2 Digit of [To Item].[To Item]
    ###############################################################################################################################

    panel_df['Panel Dual Progress_Model code'] = panel_df['To Item'].apply(lambda x: x[-2:])

    logger.info('###########-------------------------------------STEP 3 : Model Code : Last 2 Char ---------------------------------------------------')
    logger.info(panel_df.head())


    ###############################################################################################################################
    # Logic 2 : 'Panel Dual Progress_3IN1 Date System'
    ###############################################################################################################################


    # Create a mask for rows where 'Panel Dual Progress_3IN1 Exist' is 'Y'
    mask = panel_df['Panel Dual Progress_3IN1 Exist'] == 'Y'
    logger.info('###########-------------------------------------STEP 4.1 : Mask  ---------------------------------------------------')

    # Convert to datetime type
    panel_df['Panel Dual Progress_Complete HQ Result'] = pd.to_datetime(panel_df['Panel Dual Progress_Complete HQ Result'], errors='coerce')
    panel_df['Panel Dual Progress_Complete HQ Plan'] = pd.to_datetime(panel_df['Panel Dual Progress_Complete HQ Plan'], errors='coerce')

    logger.info('###########-------------------------------------STEP 4.2 : Date Time Converted  ---------------------------------------------------')
    
    # Priority Logic for date : 'Panel Dual Progress_Complete HQ Result' + 4 week
    panel_df.loc[mask, 'Panel Dual Progress_3IN1 Date System'] = panel_df.loc[mask].apply(lambda row: 
        np.nan if pd.isnull(row['Panel Dual Progress_Complete HQ Result']) and pd.isnull(row['Panel Dual Progress_Complete HQ Plan']) 
        else (row['Panel Dual Progress_Complete HQ Plan'] + pd.Timedelta(weeks=4)).date() if pd.isnull(row['Panel Dual Progress_Complete HQ Result']) 
        else (row['Panel Dual Progress_Complete HQ Result'] + pd.Timedelta(weeks=4)).date(), axis=1)

    # Set 'Panel Dual Progress_3IN1 Date System' to NaN where the condition is False
    panel_df.loc[~mask, 'Panel Dual Progress_3IN1 Date System'] = np.nan


    logger.info('###########-------------------------------------STEP 4.3 : Priority Logic : 4 week + (Result(P) or Plan)  ---------------------------------------------------')
    logger.info(panel_df.head())

    ##### Max from LT_intransit
    # Convert to datetime
    panel_df['Panel Dual Progress_3IN1 Date System'] = pd.to_datetime(panel_df['Panel Dual Progress_3IN1 Date System'])

    # Create a dictionary to map plants to their week_intransit
    plant_week_dict = intransit_df.set_index('Plant')['Mtrl Plant LT_Intransit'].to_dict()

    # Create a dictionary to map plants to their maximum week_intransit
    max_week_dict = {
        index: max([plant_week_dict.get(plant, 0) for plant in str(row['Panel Dual Progress_Plant']).split(',') if plant]) 
        if row['Panel Dual Progress_Plant'] is not None and str(row['Panel Dual Progress_Plant']) != '' 
        else 0 
        for index, row in panel_df.iterrows()
    }

    # Add 'week_intransit' to the 'date'
    panel_df['Panel Dual Progress_3IN1 Date System'] = panel_df.apply(lambda row: row['Panel Dual Progress_3IN1 Date System'] + pd.Timedelta(weeks=max_week_dict[row.name]), axis=1)

    logger.info('###########-------------------------------------STEP 5 : 3IN1 Date System + max(Mtrl Plant LT_Intransit) ---------------------------------------------------')
    logger.info(panel_df.head())


    # Rename the columns for output_df
    panel_df.rename(columns={
        'Version Name' : '[Version].[Version Name]',
        'Dash No' : '[Dash No].[Dash No]',
        'Project' : '[Dash No].[Project]',
        'Region' : '[Region].[Region]',
        'To Item' : '[To Item].[To Item]',
        'Item' : '[Item].[Item]',
        'Item Material' : '[Item Material].[Item Material]',
        'CR No' : '[Change Request].[CR No]',
        'Panel Dual Progress_Complete HQ Plan' : 'Panel Dual Progress_Complete HQ Plan',
        'Panel Dual Progress_Complete HQ Result' : 'Panel Dual Progress_Complete HQ Result',
        'Panel Dual Progress_Plant' : 'Panel Dual Progress_Plant',
        'Panel Dual Progress_3IN1 Exist' : 'Panel Dual Progress_3IN1 Exist',
        'Panel Dual Progress_Model code' : 'Panel Dual Progress_Model code',
        'Panel Dual Progress_3IN1 Date System' : 'Panel Dual Progress_3IN1 Date System'

    }, inplace=True) 

    final_panel_df =   panel_df.copy()

    logger.info("-------------------------------------STEP 6 : Final Output table renamed----------------------------------------------------")
    logger.info(final_panel_df)

    ###############################################################################################################################
    # Output
    ###############################################################################################################################

    output_df = final_panel_df[["[Version].[Version Name]",'[Dash No].[Dash No]','[Dash No].[Project]','[Region].[Region]','[To Item].[To Item]','[Item].[Item]','[Item Material].[Item Material]','[Change Request].[CR No]','Panel Dual Progress_Model code','Panel Dual Progress_3IN1 Date System']]
    logger.info("-------------------------------------STEP 7: Final Output table ----------------------------------------------------")
    logger.info(output_df.head())
    logger.info(output_df.columns)
    O9DataLake.put("output_df",output_df)

except KeyError as e:
    logger.error(f"Column not found: {e}")
except Exception as e:
    logger.error(f"An error occurred: {e}")
finally:
    logger.info("####################################### 'PY_UI_PanelDual3IN1Date' plugin : Execution END ##############################################")




