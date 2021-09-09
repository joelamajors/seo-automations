from googleapiclient.discovery import build
from oauth2client.service_account import ServiceAccountCredentials
import json
import boto3
from botocore.exceptions import ClientError
import base64
from datetime import datetime
import time


def get_secret():
    secret_name = "GoogleAnalyticsAPI"
    region_name = "us-east-1"

    # Create a Secrets Manager client
    session = boto3.session.Session()
    client = session.client(
        service_name='secretsmanager',
        region_name=region_name)

    try:
        get_secret_value_response = client.get_secret_value(
            SecretId=secret_name)
    except ClientError as e:
        if e.response['Error']['Code'] == 'DecryptionFailureException':
            raise e
        elif e.response['Error']['Code'] == 'InternalServiceErrorException':
            raise e
        elif e.response['Error']['Code'] == 'InvalidParameterException':
            raise e
        elif e.response['Error']['Code'] == 'InvalidRequestException':
            raise e
        elif e.response['Error']['Code'] == 'ResourceNotFoundException':
            raise e
    else:
        if 'SecretString' in get_secret_value_response:
            secret = get_secret_value_response['SecretString']
            secret_json = json.loads(secret)
            with open('client_secret.json', 'w') as client_secret:
                client_secret.write(json.dumps(secret_json))


def get_service(api_name, api_version, scopes, key_file_location):
    credentials = ServiceAccountCredentials.from_json_keyfile_name(
            key_file_location, scopes=scopes)
    service = build(api_name, api_version, credentials=credentials)

    return service


def get_profile_ids(service):
    # Gets view_ids for individual properties
    accounts = service.management().accounts().list().execute()

    view_ids = []

    if accounts.get('items'):
        accounts_items = accounts.get('items')

        for account_item in accounts_items:
            account_id = account_item.get('id')

            webproperty = service.management().webproperties().list(
                    accountId=account_id).execute()

            webproperties.append(webproperty)

            time.sleep(.5)

    for webproperty in webproperties:
        if webproperty.get('items'):
            property_items = webproperty.get('items')

            for prop_item in property_items:
                prop_id = prop_item.get('id')
                prop_account_id = prop_item.get('accountId')

                get_profile= service.management().profiles().list(
                        accountId=prop_account_id,
                        webPropertyId=prop_id).execute()

                profile_list.append(get_profile)

                time.sleep(.5)

    for profile in profile_list:
        if profile.get('items'):
            for profile_item in profile.get('items'):
                view_ids.append(profile_item.get('id'))

    return view_ids


def get_results(service, profile_id, start, end, metrics):
    # Calls Anayltics Reports API for session data
    return service.data().ga().get(
            ids='ga:' + profile_id,
            start_date=start,
            end_date='today',
            metrics=f'ga:{metrics}').execute()


def main():
    service = get_service(
            api_name='analytics',
            api_version='v3',
            scopes=[scope],
            key_file_location=key_file_location)

    completions_dict = []
    zero_completions = []

    profile_ids = get_profile_ids(service)

    for profile_id in profile_ids:
        result = get_results(service, profile_id, '30daysAgo', 'yesterday', 'goalCompletionsAll')
        completions_dict.append(result)

    with open('completions_file.json', 'w') as completions_file:
        completions_file.write(json.dumps(completions_dict))

    # makes file of zero results
    for comp in completions_dict:
        if comp.get('totalsForAllResults').get('ga:goalCompletionsAll') == "0":
            zero_completions.append(comp.get('profileInfo'))

    with open('zero_completions.json', 'w') as zero_completions_file:
        zero_completions_file.write(json.dumps(zero_completions))

webproperties = []
profile_list = []
get_secret()
scope = 'https://www.googleapis.com/auth/analytics.readonly'
key_file_location = './client_secret.json'

if __name__ == '__main__':
    main()
