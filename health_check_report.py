from googleapiclient.discovery import build
from oauth2client.service_account import ServiceAccountCredentials
import json
import boto3
from botocore.exceptions import ClientError
from datetime import datetime
# import concurrent

now = datetime.now().strftime("%m/%d/%Y, %H:%M:%S")

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
        else:
            secret = base64.b64decode(get_secret_value_response['SecretBinary'])

    secret_json = json.loads(secret)

    with open('client_secret.json', 'w') as client_secret:
        client_secret.write(json.dumps(secret_json))

get_secret()
scope = 'https://www.googleapis.com/auth/analytics.readonly'
key_file_location = './client_secret.json'


def get_service(api_name, api_version, scopes, key_file_location):
    credentials = ServiceAccountCredentials.from_json_keyfile_name(
            key_file_location, scopes=scopes)
    # Build the service object.
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

            properties = service.management().webproperties().list(
                    accountId=account_id).execute()

            if properties.get('items'):
                property_items = properties.get('items')

                for prop_item in property_items:
                    prop_id = prop_item.get('id')

                    profiles = service.management().profiles().list(
                            accountId=account_id,
                            webPropertyId=prop_id).execute()

                    if profiles.get('items'):
                        profile_items = profiles.get('items')

                        for prof_item in profile_items:
                            view_ids.append(prof_item.get('id'))

    return view_ids


def get_results(service, profile_id):
    # Calls Anayltics Reports API for session data
    return service.data().ga().get(
            ids='ga:' + profile_id,
            start_date='yesterday',
            end_date='today',
            metrics='ga:sessions').execute()


def main():
    # Authenticate and construct service.
    service = get_service(
            api_name='analytics',
            api_version='v3',
            scopes=[scope],
            key_file_location=key_file_location)

    results_dict = []
    zero_sessions = []

    profile_ids = get_profile_ids(service)

    for profile_id in profile_ids:
        result = get_results(service, profile_id)
        results_dict.append(result)

    with open('results_file.json', 'w') as results_file:
        results_file.write(json.dumps(results_dict))

    # takes zero results
    for result in results_dict:
        if result.get('totalsForAllResults').get('ga:sessions') == "0":
            zero_sessions.append(result.get('profileInfo'))

    with open('zero_sessions.json', 'w') as zero_sessions_file:
        zero_sessions_file.write(json.dumps(zero_sessions))

if __name__ == '__main__':
    main()
