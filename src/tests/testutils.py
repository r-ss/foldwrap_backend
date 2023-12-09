import json
import os

import requests


async def dispatcher(client, method="get", url="/empty", data=None, headers=None, auth=None):
    url = f"/api/v1{url}"

    if auth and not headers:
        headers = {"authorization": "bearer " + auth}

    # fake ip headers for testing
    if method in ["post", "form"] and url in ["/api/v1/users", "/api/v1/token"]:
        headers = {"X-Real-IP": "88.88.88.100", "X-Forwarded-For": "88.88.88.200"}

    match method:
        case "post":
            if isinstance(data, dict):
                data = json.dumps(data)
            response = await client.post(url, data=data, headers=headers)
        case "put":
            data = json.dumps(data)
            response = await client.put(url, data=data, headers=headers)
        case "patch":
            data = json.dumps(data)
            response = await client.patch(url, data=data, headers=headers)
        case "delete":
            # data = json.dumps(data)
            response = await client.delete(url, headers=headers)
        case "form":
            response = await client.post(url, data=data, headers=headers)
        case "files":
            # in this case we assume that data variable contains list of files
            files = data
            # print(">>>>", files)
            if isinstance(files, str):
                stream = open(files, "rb")
                files_data = {"uploads": (os.path.basename(files), stream, "image/png")}

            elif isinstance(files, list):
                files_data = []
                for path in files:
                    stream = open(path, "rb")
                    item = ("uploads", (os.path.basename(path), stream, "image/png"))
                    files_data.append(item)

            response = await client.post(url, files=files_data, headers=headers)
        case _:  # default 'get'
            response = await client.get(url, headers=headers)

    try:
        dispatcher_resp = response.json()
    except requests.exceptions.JSONDecodeError:
        dispatcher_resp = response.text

    return response.status_code, dispatcher_resp


async def get(client, url, headers=None, auth=None):
    return await dispatcher(client, "get", url, None, headers, auth)


async def post(client, url, data, headers=None, auth=None):
    return await dispatcher(client, "post", url, data, headers, auth)


async def put(client, url, data, headers=None, auth=None):
    return await dispatcher(client, "put", url, data, headers, auth)


async def patch(client, url, data=None, headers=None, auth=None):
    return await dispatcher(client, "patch", url, data, headers, auth)


async def delete(client, url, headers=None, auth=None):
    return await dispatcher(client, "delete", url, None, headers, auth)


async def postForm(client, url, data, headers=None, auth=None):
    return await dispatcher(client, "form", url, data, headers, auth)


async def postFiles(client, url, files, headers=None, auth=None):
    return await dispatcher(client, "files", url, files, headers, auth)
