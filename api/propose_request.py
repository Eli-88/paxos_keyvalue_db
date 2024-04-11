from aiohttp.web import Request, Response
from aiohttp import web
from state import State
from log_entry import LogEntry
from peer import Peer
from typing import List, Dict, Tuple
import asyncio
import aiohttp
import json
from db import Db


async def handle_put(
    request: Request,
    state: State,
    log_entry: LogEntry,
    peers: List[Peer],
    minimum_votes: int,
    db: Db,
) -> Response:
    try:
        msg = await request.json()
        key: str = msg["key"]
        value: str = msg["value"]

        async with aiohttp.ClientSession() as session:
            approved, num = await _validate(
                state=state,
                peers=peers,
                minimum_votes=minimum_votes,
                session=session,
            )

            if approved:
                statement = {}
                statement["ops"] = "put"
                statement["key"] = key
                statement["value"] = value

                statement_str: str = json.dumps(statement)

                success = log_entry.add(num, statement_str)
                if success:
                    db.put(key, value)

                req = {}
                req["number"] = num
                req["statement"] = statement_str
                req["key"] = key
                req["value"] = value

                all_requests = (
                    session.post(url=f"http://{host}:{port}/learn_accept_put", json=req)
                    for host, port in peers
                )
                await asyncio.gather(*all_requests, return_exceptions=True)

                response_json = {}
                response_json["result"] = "ok" if approved else "error"

                return web.json_response(response_json)
            else:
                return web.json_response({"error": "invalid"})

    except:
        return web.json_response({"error": "invalid"})


async def handle_get(
    request: Request,
    state: State,
    log_entry: LogEntry,
    peers: List[Peer],
    minimum_votes: int,
    db: Db,
) -> Response:
    try:
        msg = await request.json()
        key: str = msg["key"]

        async with aiohttp.ClientSession() as session:
            approved, num = await _validate(
                state=state,
                peers=peers,
                minimum_votes=minimum_votes,
                session=session,
            )

            if approved:
                statement = {}
                statement["ops"] = "get"
                statement["key"] = key

                statement_str = json.dumps(statement)

                success = log_entry.add(num, statement_str)

                db_value = None
                if success:
                    db_value = db.get(key)

                req = {}
                req["number"] = num
                req["statement"] = statement_str

                all_requests = (
                    session.post(url=f"http://{host}:{port}/learn_accept_get", json=req)
                    for host, port in peers
                )
                await asyncio.gather(*all_requests, return_exceptions=True)

                response_json = {}
                response_json["result"] = "ok" if db_value else "error"
                response_json["value"] = db_value

                return web.json_response(response_json)
            else:
                return web.json_response({"error": "invalid"})

    except Exception as e:
        print(e)
        return web.json_response({"error": "invalid"})


async def _validate(
    state: State,
    peers: List[Peer],
    minimum_votes: int,
    session: aiohttp.ClientSession,
) -> Tuple[bool, int]:
    approved: bool = False
    max_tries: int = 10

    while not approved and max_tries > 0:
        max_tries -= 1

        num: int = state.propose()

        if not await _post_and_validate_votes(
            session, num, "/accept_prepare", peers, minimum_votes
        ):
            continue

        if not await _post_and_validate_votes(
            session, num, "/accept_propose", peers, minimum_votes
        ):
            continue

        return True, num

    return False, -1


async def _post_and_validate_votes(
    session: aiohttp.ClientSession,
    num: int,
    target: str,
    peers: List[Peer],
    minimum_votes: int,
) -> bool:
    req = {}
    req["number"] = num

    all_requests = [_send(session, host, port, target, req) for host, port in peers]

    all_responses: List[Dict | BaseException] = await asyncio.gather(
        *all_requests, return_exceptions=True
    )

    approvals: List[bool] = [
        response["approve"] == "true"
        for response in all_responses
        if not isinstance(response, BaseException)
    ]

    return sum(1 for x in approvals if x) >= minimum_votes


async def _send(
    session: aiohttp.ClientSession, host: str, port: int, target: str, req: Dict
):
    response = await session.post(url=f"http://{host}:{port}{target}", json=req)
    return await response.json()
