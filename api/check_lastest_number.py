from aiohttp.web import Request, Response
from aiohttp import web
from log_entry import LogEntry


async def handle(request: Request, log_entry: LogEntry) -> Response:
    try:
        lastest_number = log_entry.latest_accepted_num()
        return web.json_response({"number": lastest_number})
    except:
        return web.json_response({"result": "error"})
