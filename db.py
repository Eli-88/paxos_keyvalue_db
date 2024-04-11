from abc import ABC, abstractmethod
import plyvel


class Db(ABC):
    @abstractmethod
    def get(self, key: str) -> str | None: ...

    @abstractmethod
    def put(self, key: str, value: str): ...

    @abstractmethod
    def remove(self, key: str): ...


class KvDb(Db):
    def __init__(self, db_path: str) -> None:
        self.db = plyvel.DB(db_path, create_if_missing=True)

    def close(self):
        self.db.close()

    def get(self, key: str) -> str | None:
        result = self.db.get(key.encode())
        if isinstance(result, bytes):
            return result.decode()
        return None

    def put(self, key: str, value: str):
        self.db.put(key.encode(), value.encode())

    def remove(self, key: str):
        self.db.remove(key.encode())
