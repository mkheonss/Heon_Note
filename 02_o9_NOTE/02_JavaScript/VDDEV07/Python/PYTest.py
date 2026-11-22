'''
Exec plugin instance [PYTest]
for measures {Measure.[Model Store Path]}
using scope ( &CWV )
using arguments {
    (ExecutionMode, "LightWeight"),
    ([Param.o9_sys_log_level], "DEBUG")};
'''
import datetime
import pandas as pd
from NSCMCommon import NSCMCommon as common
logger = common.G_Logger(p_py_name='PYTest')
common.gfn_set_local_logfile()
LOG_LEVEL=common.G_log_level

logger.Start()
logger.Note(f'{common.G_SourceVersion}')

# dummy 
df_in['Algorithm.[Algorithm Instance]']='o9Model'
df_in['Model Store Path']=1
df_out=df_in
logger.Step(p_step_no=100,p_step_desc=f'desc1')


# call gfn
logger.Note(common.gfn_get_df_mst_week_from_date('2024-01-01',30))
logger.Step(p_step_no=200,p_step_desc=f'desc2')

# PrintDF
logger.PrintDF(p_df=df_in, p_df_name='df_in', p_log_level=LOG_LEVEL.debug(), p_format=1)
logger.PrintDF(p_df=df_in, p_df_name='df_in', p_log_level=LOG_LEVEL.debug(), p_format=2)
logger.Step(p_step_no=300,p_step_desc=f'desc3')


# conv
now = datetime.datetime.now()
str = '한글 內 abc 123'
df_test = pd.DataFrame(columns=['time','string'])
df_test['time']   = now
df_test['string'] = str
#logger.PrintDF(p_df=df_test, p_df_name='df_test', p_log_level=LOG_LEVEL.debug(), p_format=1)
logger.Note(f'{now}')
logger.Note(f'{str}')
logger.Step(p_step_no=400,p_step_desc=f'desc4')

logger.Finish()