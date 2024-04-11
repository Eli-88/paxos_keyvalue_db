from aiohttp.web import Request, Response
from aiohttp import web
from log_entry import LogEntry
from typing import List


async def handle(request: Request, log_entry: LogEntry) -> Response:
    try:
        msg = await request.json()

        num: int = int(msg["number"])
        statement: List[str] | None = log_entry.retrieve_range(num)

        response_json = {}

        if statement:
            response_json["statement"] = statement
            response_json["result"] = "ok"
        else:
            response_json["statement"] = ""
            response_json["result"] = "error"

        return web.json_response(response_json)

    except:
        return web.json_response({"result": "error"})
