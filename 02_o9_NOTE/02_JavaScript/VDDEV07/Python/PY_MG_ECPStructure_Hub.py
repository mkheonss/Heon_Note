# Importing Libraries
import datetime
from o9_common_utils.O9DataLake import O9DataLake
import logging
from datetime import datetime,timedelta
import numpy as np
import pandas as pd
import time



df_ECPStructure = O9DataLake.get("df_in_ECPStructure")
if (SavePoint == "DataLake"):
    df_ECPStructure.loc[0] = [paramOutVersion, 'P306', 'QE55LST7DATXXN', 'BN96-51825A', 'P306', 100, 'AA01',
                              'Test_Demand']
    O9DataLake.put("df_ECPStructure", df_ECPStructure)

elif (SavePoint == "Hub"):
    df_ECPStructure.loc[0] = [paramOutVersion, 'P306', 'QE55LST7DATXXN', 'BN96-51825A', 'P306', 100, 'AA01',
                              'Test_Demand']
    import io
    import boto3
    import pyarrow as pa
    import pyarrow.parquet as pq
    from botocore.client import Config

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

    Hub_s3 = get_s3_clients()

    def save_dataframe_to_s3(df, bucket: str, s3_path: str, Hub_s3):
        if df is None or df.empty:
            print(f"저장할 데이터가 없습니다: {s3_path}")
            return

        table = pa.Table.from_pandas(df, preserve_index=False)
        buffer = io.BytesIO()
        pq.write_table(table, buffer)
        buffer.seek(0)
        Hub_s3.put_object(Bucket=bucket, Key=s3_path, Body=buffer.getvalue())
        print(f"DataFrame이 S3에 저장되었습니다: s3://{bucket}/{s3_path}")

    save_dataframe_to_s3(
        df_ECPStructure,
        Hub_BUCKET,
        f"{Hub_BASE_PATH}/Fact.o9_out_mg_ecp_structure.parquet",
        Hub_s3,
    )
else:
    O9DataLake.put("df_ECPStructure", df_ECPStructure)