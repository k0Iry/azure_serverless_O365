import logging

import azure.functions as func
import json, os, urllib.request

from azure.data.tables import TableClient
from azure.core.exceptions import ResourceExistsError, HttpResponseError
from urllib.parse import urlencode, quote_plus
from urllib.error import URLError, HTTPError

def getToken(code) -> func.HttpResponse:
    connection_string = os.environ["AzureWebJobsStorage"]
    client = TableClient.from_connection_string(conn_str=connection_string, table_name="tokens")
    try:
        client.create_table()
    except HttpResponseError:
        print("Table already exists")

    try:
        client.get_entity(partition_key="pk", row_key="rk")
    except HttpResponseError:
        # we haven't built up our tokens yet, request the server for them
        gettoken = os.environ["host"] + "token"
        # send a POST request to endpoint for the access token & refresh token
        request = urllib.request.Request(gettoken)
        request.add_header("Content-Type", "application/x-www-form-urlencoded")
        body = {"client_id": os.environ["client_id"], "scope": "User.ReadBasic.All", "code": code, "redirect_uri": os.environ["redirect_uri"], 
                "grant_type": "authorization_code", "client_secret": os.environ["client_secret"]}
        try:
            response = urllib.request.urlopen(request,  data=urlencode(body, quote_via=quote_plus).encode("utf-8"))
            res_body = json.loads(response.read().decode())
            # save tokens in the table
            entity = {
                "PartitionKey": "pk",
                "RowKey": "rk",
                "token_type": res_body["token_type"],
                "access_token": res_body["access_token"],
                "refresh_token": res_body["refresh_token"],
                "scope": res_body["scope"],
                "expires_in": res_body["expires_in"]
            }
            client.create_entity(entity=entity)
        except HTTPError as e:
            return func.HttpResponse("Error msg: {}".format(e.msg), status_code=e.code)
        except URLError as e:
            return func.HttpResponse("URL error: {}".format(e.reason), status_code=404)

    logging.info('Tokens will be refreshed automatically')
    return func.HttpResponse(f"Authorized successfully! Token has been saved.")


# This function shouldn't be triggered manually
def main(req: func.HttpRequest) -> func.HttpResponse:
    # accept auth code from Microsoft
    code = req.params.get('code')
    if not code:
        return func.HttpResponse("400 Bad Request.\n\nWe need code passed from Microsoft.", status_code=400)

    return getToken(code)
