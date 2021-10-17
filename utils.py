import requests
import json

rpc_id = 0


def send_request(url, method, data=[]):
    global rpc_id
    rpc_id += 1
    responce = requests.post(url=url,
                             data=json.dumps({
                                 "jsonrpc": "2.0",
                                 "id": rpc_id,
                                 "method": method,
                                 "params": data}),
                             headers={'content-type': 'application/json'}).json()
    if 'result' in responce:
        return responce["result"]
    else:
        return responce