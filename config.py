from peer import Peer
import json
from typing import List


class Config:
    def __init__(self, file: str) -> None:

        with open(file, "rb") as f:
            config: dict = json.load(f)

            self.peer_conns = [
                Peer(host=peer["host"], port=int(peer["port"]))
                for peer in config["peers"]
            ]

            self.local_conn = Peer(
                host=config["local"]["host"], port=int(config["local"]["port"])
            )

    @property
    def PeerConns(self) -> List[Peer]:
        return self.peer_conns

    @property
    def LocalConn(self) -> Peer:
        return self.local_conn
