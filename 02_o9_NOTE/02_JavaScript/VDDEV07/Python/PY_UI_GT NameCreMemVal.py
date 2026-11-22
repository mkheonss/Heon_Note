import pandas as pd
from o9_common_utils.O9DataLake import O9DataLake
import collections
import logging

logger=logging.getLogger('o9_logger')

input_df = O9DataLake.get('input_df')

logger.info(input_df)

input_dfop=pd.DataFrame()

input_dfop=input_df[["Version.[Version Name]", "Global Top.[GT Code]", "GT_Fix Name", "GT_Priority","GT_Fix Name_Validation"]];

count_dict=input_dfop['GT_Fix Name'].value_counts().to_dict()
count_dict['']=1
logger.info(count_dict)

input_dfop['GT_Fix Name_Validation']=input_dfop['GT_Fix Name'].apply(lambda x: 'True' if count_dict[x]==1 else 'False')



output_df=input_dfop[["Version.[Version Name]", "Global Top.[GT Code]","GT_Fix Name_Validation"]];


logger.info(output_df)


O9DataLake.put('output_df', output_df)


input_dfpriority=O9DataLake.get('input_dfpriority')

input_dfpriorityop=pd.DataFrame()

input_dfpriorityop=input_dfpriority[["Version.[Version Name]", "Global Top.[GT Code]", "GT_Priority"]];
input_dfpriorityop['GT_Priority']=input_dfpriorityop['GT_Priority'].fillna(999)

output_dfpriority=input_dfpriorityop[["Version.[Version Name]", "Global Top.[GT Code]","GT_Priority"]];


logger.info(output_dfpriority)


O9DataLake.put('output_dfpriority', output_dfpriority)
