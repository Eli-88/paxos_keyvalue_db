from aiohttp import web
from functools import partial
from state import PaxosState
from log_entry import InMemoryLogEntry
from api import (
    accept_prepare,
    accept_propose,
    learn_retrieve,
    learn_accept,
    propose_request,
    check_lastest_number,
)
import sync_task
import asyncio
from config import Config
import sys
from db import KvDb


async def main():
    if len(sys.argv) < 2:
        print("usage: python main.py <full file path>")
        exit(-1)

    config = Config(sys.argv[1])
    minimum_votes = len(config.PeerConns) // 2 + 1

    state = PaxosState()
    log_entry = InMemoryLogEntry()
    db = KvDb(db_path=f"./db_{config.LocalConn.port}")

    app = web.Application()

    routes = [
        web.post("/accept_prepare", partial(accept_prepare.handle, state=state)),
        web.post("/accept_propose", partial(accept_propose.handle, state=state)),
        web.post(
            "/learn_accept_put",
            partial(learn_accept.handle_put, log_entry=log_entry, db=db),
        ),
        web.post(
            "/learn_accept_get",
            partial(learn_accept.handle_get, log_entry=log_entry),
        ),
        web.post(
            "/learn_retrieve", partial(learn_retrieve.handle, log_entry=log_entry)
        ),
        web.post(
            "/propose_request_put",
            partial(
                propose_request.handle_put,
                state=state,
                log_entry=log_entry,
                peers=config.PeerConns,
                minimum_votes=minimum_votes,
                db=db,
            ),
        ),
        web.post(
            "/propose_request_get",
            partial(
                propose_request.handle_get,
                state=state,
                log_entry=log_entry,
                peers=config.PeerConns,
                minimum_votes=minimum_votes,
                db=db,
            ),
        ),
        web.post(
            "/check_lastest_number",
            partial(check_lastest_number.handle, log_entry=log_entry),
        ),
    ]
    app.add_routes(routes)

    asyncio.create_task(
        sync_task.run(
            log_entry=log_entry, db=db, peers=config.PeerConns, interval_in_seconds=5
        )
    )

    runner = web.AppRunner(app)
    await runner.setup()

    site = web.TCPSite(runner, config.LocalConn.host, config.LocalConn.port)
    await site.start()

    try:
        while True:
            await asyncio.sleep(10000)
    except KeyboardInterrupt:
        await runner.cleanup()
    except BaseException:
        pass


if __name__ == "__main__":
    asyncio.run(main())
