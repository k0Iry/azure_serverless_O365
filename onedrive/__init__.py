import logging

import azure.functions as func
from azure.data.tables import TableClient
import os, json, urllib.request, urllib.parse, mimetypes
from urllib.error import URLError, HTTPError

api_endpoint = os.environ["GraphAPI_endpoint"]

def onedrv_upload(token):
    """This function upload a file to a directory

    Args:
        token: The access token.

    Returns:
        return a upload link for the server.

    """
    pass

def get_onedrv_id(token):
    if not get_onedrv_id.id:
        request = urllib.request.Request(api_endpoint + "/me/drive")
        request.add_header("Authorization", "Bearer {}".format(token))
        try:
            response = urllib.request.urlopen(request)
            res_body = json.loads(response.read().decode())
            if "id" in res_body:
                get_onedrv_id.id = res_body["id"]
        except HTTPError as e:
            print('Error code: ', e.code)
        except URLError as e:
            print('Reason: ', e.reason)

    return get_onedrv_id.id

def access(token, path, dir) -> func.HttpResponse:
    """Access folder with 'path' in onedrive.

    Args:
        token: The access token.
        path:  The path to be accessed, if not given, root.
        dir:   If path is a file(False) or a directory(True)

    Returns:
        Return the meta data for files under this path

    """
    concat = "/drives/{}/root:/{}:/children" if dir else "/drives/{}/root:/{}"
    full_path = "/me/drive/root/children" if not path else concat.format(get_onedrv_id(token), path)
    request = urllib.request.Request(api_endpoint + full_path)
    request.add_header("Authorization", "Bearer {}".format(token))
    try:
        response = urllib.request.urlopen(request)
    except HTTPError as e:
        return func.HttpResponse("Error msg: {}".format(e.msg), status_code=e.code)
    except URLError as e:
        return func.HttpResponse("URL error: {}".format(e.reason), status_code=404)

    return func.HttpResponse(body=response.read(), status_code=response.status)

def is_dir(path) -> bool:
    type, _ = mimetypes.guess_type(path, True)
    return (not type)

def main(req: func.HttpRequest) -> func.HttpResponse:
    """Main function, maintain a connection to the database."""

    logging.info('HTTP trigger function processed a OneDrive request.')
    if not main.client:
        main.client = TableClient.from_connection_string(conn_str=os.environ["AzureWebJobsStorage"], table_name="tokens")

    entity = main.client.get_entity(partition_key="pk", row_key="rk")
    token = entity.access_token.value

    if req.method == "GET":
        path_encoded = urllib.parse.quote(req.params.get("access")) if req.params.get("access") else None
        dir = True if not path_encoded else is_dir(path_encoded)
        return access(token, path_encoded, dir)
    
    return func.HttpResponse("choose an action")

"""
functional scope variables
"""
main.client = None
get_onedrv_id.id = ""