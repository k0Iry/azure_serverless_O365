import datetime
import logging

import azure.functions as func
import os, json, urllib.request
from azure.data.tables import TableServiceClient, TableClient, UpdateMode
from azure.core.exceptions import ResourceExistsError, HttpResponseError
from urllib.parse import urlencode, quote_plus


def main(mytimer: func.TimerRequest) -> None:
    utc_timestamp = datetime.datetime.utcnow().replace(tzinfo=datetime.timezone.utc).isoformat()

    # if mytimer.past_due:
    logging.info('Now we are starting to refresh tokens!')
    refresh_token = os.environ["host"] + "token"
    request = urllib.request.Request(refresh_token)
    request.add_header("Content-Type", "application/x-www-form-urlencoded")
        
    # get refresh token from table
    connection_string = os.environ["AzureWebJobsStorage"]
    client = TableClient.from_connection_string(conn_str=connection_string, table_name="tokens")
    entity = client.get_entity(partition_key="pk", row_key="rk")

    # the request body should include refresh token
    body = {"client_id": os.environ["client_id"], "scope": "User.ReadBasic.All", "refresh_token": entity.refresh_token.value, "redirect_uri": os.environ["redirect_uri"], 
            "grant_type": "refresh_token", "client_secret": os.environ["client_secret"]}
    response = urllib.request.urlopen(request,  data=urlencode(body, quote_via=quote_plus).encode("utf-8"))
    res_body = json.loads(response.read().decode())

    # update tokens in the table
    entity.access_token = res_body["access_token"]
    entity.refresh_token = res_body["refresh_token"]
    client.update_entity(mode=UpdateMode.REPLACE, entity=entity)
#     print(entity.access_token)

    logging.info('tokens were refreshed at %s', utc_timestamp)
