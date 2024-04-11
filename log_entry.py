from abc import ABC, abstractmethod
from typing import List
import numpy as np


class LogEntry(ABC):
    @abstractmethod
    def add(self, number: int, entry: str) -> bool: ...

    @abstractmethod
    def retrieve_range(self, start_number: int) -> List[str] | None: ...

    @abstractmethod
    def latest_accepted_num(self) -> int: ...


class InMemoryLogEntry(LogEntry):
    def __init__(self) -> None:
        self.next_accepted_number = 0

        # TODO: flush this file when reach a certain size
        self.entries: List[str] = []

    def add(self, number: int, entry: str) -> bool:
        if number != self.next_accepted_number:
            return False

        self.entries.append(entry)
        self.next_accepted_number += 1
        return True

    def retrieve_range(self, start_number: int) -> List[str] | None:
        if start_number >= len(self.entries):
            return None

        return self.entries[start_number:]

    def latest_accepted_num(self) -> int:
        return self.next_accepted_number - 1
