from abc import ABC, abstractmethod


class State(ABC):
    @abstractmethod
    def propose(self) -> int: ...

    @abstractmethod
    def prepare(self, number: int) -> bool: ...

    @abstractmethod
    def accept(self, number: int) -> bool: ...


class PaxosState(State):
    def __init__(self) -> None:
        self.proposed_number = -1
        self.next_promised_number = -1
        self.next_proposed_number = -1

    def propose(self) -> int:
        self.proposed_number += 1
        return self.proposed_number

    def prepare(self, number: int) -> bool:
        if number < self.next_promised_number:
            return False

        self.next_promised_number += 1
        return True

    def accept(self, number: int) -> bool:
        if number < self.next_proposed_number:
            return False

        self.next_proposed_number = number + 1
        return True
