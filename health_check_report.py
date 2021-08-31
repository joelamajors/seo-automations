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


def get_service(api_name, api_version, scopes, key_file_location):
    credentials = ServiceAccountCredentials.from_json_keyfile_name(
            key_file_location, scopes=scopes)
    service = build(api_name, api_version, credentials=credentials)

    return service


def list_webproperties(request_id, response, exception):
    if exception is not None:
        print("webproperties failed")
        print(exception)
        pass
    else:
        webproperties.append(response)
        pass


def list_profiles(request_id, response, exception):
    if exception is not None:
        print("list profiles failed")
        print(exception)
        pass
    else:
        profile_list.append(response)
        pass


def get_profile_ids(service):
    # Gets view_ids for individual properties
    accounts = service.management().accounts().list().execute()
    webproperties_batch = service.new_batch_http_request()
    profiles_batch = service.new_batch_http_request()
    view_ids = []

    if accounts.get('items'):
        accounts_items = accounts.get('items')

        for account_item in accounts_items:
            account_id = account_item.get('id')
            webproperties_batch.add(service.management().webproperties().list(accountId=account_id), callback=list_webproperties)

    webproperties_batch.execute()

    for webproperty in webproperties:
        if webproperty.get('items'):
            property_items = webproperty.get('items')

            for prop_item in property_items:
                prop_id = prop_item.get('id')
                prop_account_id = prop_item.get('accountId')

                profiles_batch.add(service.management().profiles().list(accountId=prop_account_id, webPropertyId=prop_id), callback=list_profiles)

    profiles_batch.execute()

    for profile in profile_list:
        if profile.get('items'):
            view_ids.append(profile.get('id'))

    return view_ids


def list_profile_sessions(request_id, response, exception):
    if exception is not None:
        print("profile session borked")
        print(exception)
        pass
    else:
        profile_sessions.append(response)
        pass


def main():
    # Authenticate and construct service.
    service = get_service(
            api_name='analytics',
            api_version='v3',
            scopes=[scope],
            key_file_location=key_file_location)

    profile_id_batch = service.new_batch_http_request()

    zero_sessions = []

    profile_ids = get_profile_ids(service)

    for profile_id in profile_ids:
        profile_id_batch.add(service.data().ga().list(
            ids='ga:' + profile_id,
            start_date='yesterday',
            end_date='today',
            metrics='ga:sessions'
            ),
            callback=list_profile_sessions
        )

    profile_id_batch.execute()

    with open('profile_sessions_file.json', 'w') as profile_sessions_file:
        profile_sessions_file.write(json.dumps(profile_sessions))

    # takes zero results
    for session in profile_sessions:
        if session.get('totalsForAllResults').get('ga:sessions') == "0":
            zero_sessions.append(session.get('profileInfo'))

    with open('zero_sessions.json', 'w') as zero_sessions_file:
        zero_sessions_file.write(json.dumps(zero_sessions))


webproperties = []
profile_list = []
profile_sessions = []
get_secret()
scope = 'https://www.googleapis.com/auth/analytics.readonly'
key_file_location = './client_secret.json'

if __name__ == '__main__':
    main()
