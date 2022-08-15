import ast
import pandas as pd
import boto3
import logging
from envyaml import EnvYAML

config = EnvYAML('.env.yaml')

accounts = config['accounts']
regions = config['regions']
properties = config['properties']

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

def writeResults(writer, df, account_name, ordered = False, addFilter = False):
    if ordered:
        df = df[properties]

    df.to_excel(writer, sheet_name=account_name, header=True, index=True)

    if addFilter:
        (max_row, max_col) = df.shape
        worksheet = writer.sheets[account_name]
        worksheet.autofilter(0, 0, max_row, max_col - 1)

def fetchData(account):
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
                Expression="SELECT {0} WHERE resourceType not like 'AWS::EC2::%' ".format(",".join(properties)),
            )

            results = results + structureResults(response)

            if 'NextToken' in response.keys():
                nextPage = response['NextToken']
            else:
                nextPage = None

    return results


if __name__ == '__main__':
    writer_summary = pd.ExcelWriter("summary.xlsx",engine="xlsxwriter")
    writer_raw = pd.ExcelWriter("report.xlsx",engine="xlsxwriter")

    for account in accounts:
        try: 
            logging.info('Starting fetch data from account ' + account['name'])
            results = fetchData(account)

            df_summary = pd.DataFrame.from_dict(results).groupby('resourceType')['resourceType'].count()
            df_raw = pd.DataFrame.from_dict(results)

            writeResults(writer_summary, df_summary, account['name'])
            writeResults(writer_raw, df_raw, account['name'], True, True)
            logging.info('Fetching complete.')
        except Exception as e:
            logging.error(e)
            logging.error('Error trying to fetch data from account ' + account['name'])
    writer_summary.save()
    writer_raw.save()
