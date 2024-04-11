from aiohttp import web
from aiohttp.web import Request, Response
from state import State


async def handle(request: Request, state: State) -> Response:
    try:
        msg = await request.json()
        number: int = int(msg["number"])

        success: bool = state.accept(number)

        response_json = {}
        response_json["number"] = number
        response_json["approve"] = "true" if success else "false"

        return web.json_response(response_json)

    except:
        return web.json_response({"result": "invalid"})
