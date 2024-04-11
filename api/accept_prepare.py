from aiohttp.web import Request, Response
from aiohttp import web
from state import State


async def handle(request: Request, state: State) -> Response:
    try:
        msg = await request.json()

        num: int = int(msg["number"])

        success: bool = state.prepare(num)

        response_json = {}
        response_json["number"] = num
        response_json["approve"] = "true" if success else "false"

        return web.json_response(response_json)
    except:
        return web.json_response("invalid")
