from aiohttp.web import Request, Response
from aiohttp import web
from log_entry import LogEntry
from db import Db


async def handle_put(request: Request, log_entry: LogEntry, db: Db) -> Response:
    try:
        msg = await request.json()
        num: int = int(msg["number"])
        statement: str = msg["statement"]
        key: str = msg["key"]
        value: str = msg["value"]

        success: bool = log_entry.add(num, statement)
        if success:
            db.put(key=key, value=value)

        response_json = {}
        response_json["number"] = num
        response_json["approve"] = "true" if success else "false"

        return web.json_response(response_json)

    except:
        return web.json_response({"error", "invalid"})


async def handle_get(request: Request, log_entry: LogEntry) -> Response:
    try:
        msg = await request.json()
        num: int = int(msg["number"])
        statement: str = msg["statement"]

        success: bool = log_entry.add(num, statement)

        response_json = {}
        response_json["number"] = num
        response_json["approve"] = "true" if success else "false"

        return web.json_response(response_json)

    except:
        return web.json_response({"error": "invalid"})


# async def handle_remove(request: Request, log_entry: LogEntry, db: Db) -> Response:
#     try:
#         msg = await request.json()
#         num: int = int(msg["number"])
#         statement: str = msg["statement"]
#         key: str = msg["key"]

#         success: bool = log_entry.add(num, statement)
#         if success:
#             db.remove(key=key)

#         response_json = {}
#         response_json["number"] = num
#         response_json["approve"] = "true" if success else "false"

#         return web.json_response(response_json)

#     except:
#         return web.json_response({"error": "invalid"})
