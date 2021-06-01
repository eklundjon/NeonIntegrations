########### ATXHS NeonCRM & Discourse API Integrations ############
#      Neon API docs - https://developer.neoncrm.com/api-v2/     #
#################################################################
#################################################################
#  This helper script assists in making bulk updates to events  #
#  in Neon.  If event details have changed and need to be       #
#  updated for a large number of events, change one the way     #
#  you want it in the UI, then use this script to pull the      #
#  changes and PATCH it to all other events.                    #
#################################################################

from pprint import pprint
import requests
import json
import base64
import time
import datetime

from config import N_APIkey, N_APIuser


# Neon Account Info
N_auth = f'{N_APIuser}:{N_APIkey}'
N_baseURL = 'https://api.neoncrm.com/v2'
N_signature = base64.b64encode(bytearray(N_auth.encode())).decode()
N_headers = {'Content-Type':'application/json','Authorization': f'Basic {N_signature}', 'NEON-API-VERSION': '2.1'}


## Helper function for API calls
def apiCall(httpVerb, url, data, headers):
    # Make request
    if httpVerb == 'GET':
        response = requests.get(url, data=data, headers=headers)
    elif httpVerb == 'POST':
        response = requests.post(url, data=data, headers=headers)
    elif httpVerb == 'PUT':
        response = requests.put(url, data=data, headers=headers)
    elif httpVerb == 'PATCH':
        response = requests.patch(url, data=data, headers=headers)
    elif httpVerb == 'DELETE':
        response = requests.delete(url, data=data, headers=headers)
    else:
        print(f"HTTP verb {httpVerb} not recognized")

    # These lines break the code for PATCH requests
    # response = response.json()
    # pprint(response)

    return response


# ##### NEON #####
# # Get list of custom fields for events
# httpVerb = 'GET'
# resourcePath = '/customFields'
# queryParams = '?category=Events'
# data = ''

# url = N_baseURL + resourcePath + queryParams
# print("### CUSTOM FIELDS ###\n")
# responseFields = apiCall(httpVerb, url, data, N_headers)


# ##### NEON #####
# # Get possible search fields for POST to /events/search
# httpVerb = 'GET'
# resourcePath = '/events/search/searchFields'
# queryParams = ''
# data = ''
# # Event Category

# url = N_baseURL + resourcePath + queryParams
# print("### SEARCH FIELDS ###\n")
# responseSearchFields = apiCall(httpVerb, url, data, N_headers)

# response = responseSearchFields.json()
# pprint(response)


# ##### NEON #####
# # Get possible output fields for POST to /events/search
# httpVerb = 'GET'
# resourcePath = '/events/search/outputFields'
# queryParams = ''
# data = ''

# url = N_baseURL + resourcePath + queryParams
# print("### OUTPUT FIELDS ###\n")
# responseOutputFields = apiCall(httpVerb, url, data, N_headers)

# response = responseOutputFields.json()
# pprint(response)


##### NEON #####
# Get event with correct details
# today = datetime.date.today()
# print(f"TODAY IS {today}")

httpVerb = 'POST'
resourcePath = '/events/search'
queryParams = ''
data = f'''
{{
    "searchFields": [
        {{
            "field": "Event Name",
            "operator": "CONTAIN",
            "value": "Orientation"
        }},
        {{
            "field": "Event Start Date",
            "operator": "EQUAL",
            "value": "2021-05-11"
        }}
    ],
    "outputFields": [
        "Event Summary",
        "Event Description"
    ],
    "pagination": {{
    "currentPage": 0,
    "pageSize": 200
    }}
}}
'''

url = N_baseURL + resourcePath + queryParams
print("### CORRECT EVENT ###\n")
responseEvents = apiCall(httpVerb, url, data, N_headers).json()

pprint(responseEvents)

newSumm = responseEvents['searchResults'][0]['Event Summary']
newDesc = responseEvents['searchResults'][0]['Event Description']

print(newSumm)
print(newDesc)


### NEON #####
# Get events that need this new info
today = datetime.date.today()
print(f"TODAY IS {today}")

httpVerb = 'POST'
resourcePath = '/events/search'
queryParams = ''
data = f'''
{{
    "searchFields": [
        {{
            "field": "Event End Date",
            "operator": "GREATER_THAN",
            "value": "{today}"
        }},
        {{
            "field": "Event Name",
            "operator": "CONTAIN",
            "value": "Orientation"
        }}
    ],
    "outputFields": [
        "Event Name", 
        "Event ID",
        "Event Summary",
        "Event Description"
    ],
    "pagination": {{
    "currentPage": 0,
    "pageSize": 200
    }}
}}
'''

url = N_baseURL + resourcePath + queryParams
print("### EVENTS TO UPDATE ###\n")
responseEvents = apiCall(httpVerb, url, data, N_headers).json()

# Iterate over response to archive each event
for event in responseEvents["searchResults"]:
    httpVerb = 'PATCH'
    resourcePath = f'/events/{event["Event ID"]}'
    queryParams = ''
    data = f'''
    {{
        "Event Summary": "{newSumm}",
        "Event Description": "{newDesc}"
    }}
    '''

    url = N_baseURL + resourcePath + queryParams
    responseEvents = apiCall(httpVerb, url, data, N_headers)

    print(f'Response for event {event["Event ID"]}: {responseEvents}')