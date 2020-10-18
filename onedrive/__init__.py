import logging

import azure.functions as func
from azure.data.tables import TableClient
import os

# This function provides interface to interact with OneDrive's API
# You must provide an auth code to trigger this function
# Only accept "GET" request, this will handle API calling into OneDrive.

# In url parameters, we need to specify the action needed(view, search, download...)

def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('HTTP trigger function processed a OneDrive request.')
    # get the token at first
    # connection_string = os.environ["AzureWebJobsStorage"]
    # client = TableClient.from_connection_string(conn_str=connection_string, table_name="tokens")
    # entity = client.get_entity(partition_key="pk", row_key="rk")
    # token = entity.access_token.value

    if req.method == "GET":
        action = req.params.get("action")
        if not action:
            return func.HttpResponse("You need to provide an action upon this perform.", status_code=400)
        return func.HttpResponse(
            "Haven't implemented for {} yet.".format(action),
            status_code=404
        )
    
    return func.HttpResponse("Method {} is not supported.".format(req.method), status_code=404)
