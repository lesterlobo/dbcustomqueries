
import getopt
import json
import sys
import requests


def usage():
    print(__doc__)

def retrieve_token(client_id, client_secret, controller_url):
    payload = 'grant_type=client_credentials&client_id=' + client_id + '&client_secret=' + client_secret
    tokenResponse = requests.post(controller_url + "/controller/api/oauth/access_token", data=payload)

    token = ''
    if tokenResponse.status_code == 200:
        token = json.loads(tokenResponse.content.decode('utf-8'))['access_token']
        return token
    else:
        raise Exception(f"API request failed with status code {tokenResponse.status_code}")


def main(argv):
    controller_url = ''
    client_id = ''
    client_secret = ""

    # Open the JSON file
    with open('db_input.json', 'r') as f:
        # Load the JSON data into a Python dictionary
        data = json.load(f)

    for i in data['dbqueries']:   
        query = (i['query'])
        name = i['name']
        dbcollector = i['dbcollector']
        dbtype = i['dbtype']
        frequency = i['frequency']

        # Get Collector id from name

        # retrieve api token
        token = retrieve_token(client_id, client_secret, controller_url)

        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json" 
        }   
        
        dbresp = requests.get(controller_url + "/controller/rest/databases/collectors",
                                    headers=headers)

        dbcollectorid = ''
        if (dbresp.ok):
            dbcollectors = json.loads(dbresp.content.decode('utf-8'))
            for collector in dbcollectors:
                if (dbcollector == collector['config']['name']):
                    dbcollectorid = collector['config']['id']
                    print(dbcollectorid)
                    break
        else:
            print("Error Occured in retrieving DB Collector. Please check the collector is active on the controller." + dbresp.status_code)

        proxies = {}
        verify = True
        session = requests.get(controller_url + "/controller/auth?action=login",
                                    headers=headers)
        
        cookies = session.cookies
        xsrf_cookie = cookies.get("X-CSRF-TOKEN")

        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "X-CSRF-TOKEN":  f"{xsrf_cookie}" 
        }   

        print("Creating custom query ")
        payload = {"name": name,"queryText": query,"timeIntervalInMin": frequency,"dbaemc":{"aemcType":"DB_SERVER_AFFECTED_EMC","type":"SPECIFIC_DB_SERVERS","dbServerType": dbtype,"dbServerIds":[dbcollectorid]},"isEvent": "false"}

        create_resp = requests.post(controller_url + '/controller/databasesui/dbCustomQueryMetrics/create', data=json.dumps(payload), headers=headers)

        print(create_resp.status_code)
        if create_resp.ok:
            print("Custom SQL Successfully created")
        else:
            print("error occurred while creating custom sql!. Error Code: " + create_resp.status_code)
        

if __name__ == "__main__":
    main(sys.argv[1:])
