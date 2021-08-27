from googleapiclient.discovery import build
from oauth2client.service_account import ServiceAccountCredentials
import json


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
            ga_id = account_item.get('id')

            properties = service.management().webproperties().list(
                    accountId=ga_id).execute()

            if properties.get('items'):
                property_items = properties.get('items')

                for prop_item in property_items:
                    prop_id = prop_item.get('id')

                    profiles = service.management().profiles().list(
                            accountId=ga_id,
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
    # Define the auth scopes to request.
    scope = 'https://www.googleapis.com/auth/analytics.readonly'
    key_file_location = './client_secrets.json'

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
