import ast
import pandas as pd
import boto3
from envyaml import EnvYAML

config = EnvYAML('.env.yaml')

accounts = config['accounts']
regions = config['regions']
properties = config['properties']

writer = pd.ExcelWriter("report.xlsx",engine="xlsxwriter")

def structureResults(response):
    results = []
    for r in response['Results']:
        result = ast.literal_eval(r)

        keys = result.keys()
        for k in properties:
            if k not in keys:
                result[k] = 'N/A'

        results.append(result)
    return results

def writeResults(df, account_name):
    df = pd.DataFrame.from_dict(results)
    df_ordered = df[properties]

    df_ordered.to_excel(writer, sheet_name=account_name, header=True, index=True)

    (max_row, max_col) = df.shape
    worksheet = writer.sheets[account_name]
    worksheet.autofilter(0, 0, max_row, max_col - 1)

for account in accounts:
    results = []

    for region in regions:
        nextPage = ''

        client = boto3.client(
            service_name='config', 
            region_name=region,
            aws_access_key_id=account['key'],  
            aws_secret_access_key=account['secret'],
            aws_session_token=account['session']
        )


        while nextPage is not None:
            response = client.select_resource_config(
                NextToken=nextPage,
                Limit=100,
                Expression="SELECT {0}".format(",".join(properties)),
            )

            results = results + structureResults(response)

            if 'NextToken' in response.keys():
                nextPage = response['NextToken']
            else:
                nextPage = None
    
    df = pd.DataFrame.from_dict(results)
    writeResults(df, account['name'])
    
writer.save()
