from log_entry import LogEntry
import asyncio
import aiohttp
from peer import Peer
from typing import List, Any, Tuple, Dict
from db import Db
import json


async def run(log_entry: LogEntry, db: Db, peers: List[Peer], interval_in_seconds: int):
    while True:
        await asyncio.sleep(interval_in_seconds)

        current_largest_num = await _request_largest_num(peers)

        latest_accepted_num = log_entry.latest_accepted_num()
        if latest_accepted_num < current_largest_num:
            num_statement_pair: List[Tuple[int, str]] = (
                await _request_log_starting_from(latest_accepted_num + 1, peers)
            )

            for num, statement in num_statement_pair:
                if log_entry.add(num, statement):

                    decoded: Dict = json.loads(statement)

                    ops = decoded["ops"]

                    if ops == "put":
                        key = decoded["key"]
                        value = decoded["value"]
                        db.put(key=key, value=value)
                    elif ops == "remove":
                        db.remove(key=decoded["key"])


async def _request_log_starting_from(
    number: int, peers: List[Peer]
) -> List[Tuple[int, str]]:
    req = {}
    req["number"] = number

    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                url=f"http://{peers[0].host}:{peers[0].port}/learn_retrieve", json=req
            ) as response:

                resp = await response.json()

                if resp["result"] == "ok":
                    return [
                        (number + index, statement)
                        for index, statement in enumerate(resp["statement"])
                    ]
                else:
                    return []
    except Exception:
        return []


async def _request_largest_num(peers) -> int:
    async with aiohttp.ClientSession() as session:
        all_responses: List[aiohttp.ClientResponse | BaseException] = (
            await asyncio.gather(
                *[
                    session.post(
                        url=f"http://{peer.host}:{peer.port}/check_lastest_number",
                        json={},
                    )
                    for peer in peers
                ],
                return_exceptions=True,
            )
        )

        filtered_responses: List[aiohttp.ClientResponse] = [
            resp for resp in all_responses if isinstance(resp, aiohttp.ClientResponse)
        ]

        all_json_responses = await asyncio.gather(
            *[(r.json()) for r in filtered_responses], return_exceptions=True
        )

        all_json_responses: List[Any] = [
            r for r in all_json_responses if r is not Exception
        ]

        largest_num = -1

        for resp in all_json_responses:
            try:
                largest_num = max(largest_num, int(resp["number"]))
            except:
                pass

        return largest_num
